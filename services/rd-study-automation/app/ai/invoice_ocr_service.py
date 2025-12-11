"""
Invoice OCR Service

AI-powered invoice processing using Azure Document Intelligence (Form Recognizer)
and OpenAI for intelligent expense categorization and R&D qualification.
"""

import logging
import json
import re
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, date
from enum import Enum
from uuid import UUID

logger = logging.getLogger(__name__)


class ExpenseCategory(str, Enum):
    """R&D expense categories for tax credit purposes."""
    SUPPLIES = "supplies"
    CONTRACT_RESEARCH = "contract_research"
    COMPUTER_RENTAL = "computer_rental"
    SOFTWARE = "software"
    EQUIPMENT_RENTAL = "equipment_rental"
    PROTOTYPE_MATERIALS = "prototype_materials"
    TESTING_MATERIALS = "testing_materials"
    LAB_SUPPLIES = "lab_supplies"
    OTHER = "other"


class StateRequirement(str, Enum):
    """States with specific documentation requirements."""
    PA = "PA"  # Pennsylvania requires W-2s, 1099s, and detailed invoices
    CA = "CA"  # California
    TX = "TX"  # Texas
    NY = "NY"  # New York
    MA = "MA"  # Massachusetts


@dataclass
class InvoiceLineItem:
    """Extracted invoice line item."""
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[Decimal] = None
    amount: Decimal = Decimal("0")
    gl_account: Optional[str] = None
    category: ExpenseCategory = ExpenseCategory.OTHER
    rd_qualified: bool = False
    qualification_reason: Optional[str] = None


@dataclass
class ExtractedInvoice:
    """Fully extracted and processed invoice."""
    document_id: Optional[UUID] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None

    # Vendor information
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_tax_id: Optional[str] = None
    vendor_state: Optional[str] = None

    # Buyer information
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None

    # Financial details
    subtotal: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    total_amount: Decimal = Decimal("0")

    # Line items
    line_items: List[InvoiceLineItem] = field(default_factory=list)

    # R&D qualification
    qualified_amount: Decimal = Decimal("0")
    qualification_percentage: Decimal = Decimal("0")
    primary_category: ExpenseCategory = ExpenseCategory.OTHER

    # Processing metadata
    ocr_confidence: float = 0.0
    ai_analysis_confidence: float = 0.0
    processing_notes: List[str] = field(default_factory=list)

    # State-specific fields
    pa_qualified: bool = False  # PA R&D credit eligibility


@dataclass
class W2Extract:
    """Extracted W-2 information for state R&D documentation."""
    employee_name: str
    ssn_last4: Optional[str] = None
    employer_name: Optional[str] = None
    employer_ein: Optional[str] = None
    employer_state: Optional[str] = None
    employer_address: Optional[str] = None

    # Wage boxes
    wages_box1: Decimal = Decimal("0")  # Wages, tips, other compensation
    federal_tax_withheld: Decimal = Decimal("0")  # Box 2
    social_security_wages: Decimal = Decimal("0")  # Box 3
    medicare_wages: Decimal = Decimal("0")  # Box 5

    # State wages
    state_wages: Dict[str, Decimal] = field(default_factory=dict)  # State code -> amount
    state_tax_withheld: Dict[str, Decimal] = field(default_factory=dict)

    # Processing metadata
    tax_year: int = 2024
    ocr_confidence: float = 0.0


@dataclass
class Form1099Extract:
    """Extracted 1099 information."""
    form_type: str  # 1099-NEC, 1099-MISC, etc.
    recipient_name: str
    recipient_tin_last4: Optional[str] = None
    payer_name: Optional[str] = None
    payer_tin: Optional[str] = None
    payer_state: Optional[str] = None

    # Amounts
    nonemployee_compensation: Decimal = Decimal("0")  # Box 1 for 1099-NEC
    other_income: Decimal = Decimal("0")
    state_income: Dict[str, Decimal] = field(default_factory=dict)

    tax_year: int = 2024
    ocr_confidence: float = 0.0


class InvoiceOCRService:
    """
    AI-powered invoice OCR and processing service.

    Uses Azure Document Intelligence for OCR and OpenAI for intelligent
    categorization and R&D qualification analysis.
    """

    def __init__(
        self,
        azure_endpoint: Optional[str] = None,
        azure_key: Optional[str] = None,
        openai_client: Optional[Any] = None,
        config: Optional[Dict] = None
    ):
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.azure_key = azure_key or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        self.openai_client = openai_client
        self.config = config or {}

        # Initialize Azure Document Intelligence client if credentials available
        self.document_client = None
        if self.azure_endpoint and self.azure_key:
            try:
                from azure.ai.formrecognizer import DocumentAnalysisClient
                from azure.core.credentials import AzureKeyCredential
                self.document_client = DocumentAnalysisClient(
                    endpoint=self.azure_endpoint,
                    credential=AzureKeyCredential(self.azure_key)
                )
                logger.info("Azure Document Intelligence client initialized")
            except ImportError:
                logger.warning("azure-ai-formrecognizer not installed")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Document Intelligence: {e}")

    async def process_invoice(
        self,
        file_content: bytes,
        filename: str,
        study_id: Optional[UUID] = None,
        existing_vendors: Optional[List[Dict]] = None
    ) -> ExtractedInvoice:
        """
        Process an invoice document using OCR and AI analysis.

        Args:
            file_content: Raw file bytes (PDF, image, etc.)
            filename: Original filename
            study_id: Associated R&D study ID
            existing_vendors: List of known vendors for matching

        Returns:
            ExtractedInvoice with all parsed data and R&D qualification
        """
        logger.info(f"Processing invoice: {filename}")

        result = ExtractedInvoice()

        # Step 1: OCR extraction
        if self.document_client:
            ocr_result = await self._azure_ocr_invoice(file_content)
            result = self._apply_azure_ocr_result(result, ocr_result)
        else:
            # Fallback to basic text extraction
            text = self._extract_text_basic(file_content, filename)
            result = self._parse_invoice_from_text(result, text)

        # Step 2: AI-powered categorization and R&D qualification
        result = await self._ai_analyze_invoice(result, study_id)

        # Step 3: Vendor matching
        if existing_vendors:
            result = self._match_vendor(result, existing_vendors)

        logger.info(f"Invoice processed: {result.invoice_number}, Total: ${result.total_amount}, R&D Qualified: ${result.qualified_amount}")

        return result

    async def _azure_ocr_invoice(self, file_content: bytes) -> Dict[str, Any]:
        """Use Azure Document Intelligence to extract invoice data."""
        try:
            from azure.ai.formrecognizer import AnalyzeResult

            poller = self.document_client.begin_analyze_document(
                "prebuilt-invoice",
                file_content
            )
            result: AnalyzeResult = poller.result()

            extracted = {
                "confidence": 0.0,
                "invoices": []
            }

            for invoice in result.documents:
                invoice_data = {
                    "confidence": invoice.confidence,
                    "fields": {}
                }

                # Extract common fields
                field_mapping = {
                    "VendorName": "vendor_name",
                    "VendorAddress": "vendor_address",
                    "VendorTaxId": "vendor_tax_id",
                    "CustomerName": "customer_name",
                    "CustomerAddress": "customer_address",
                    "InvoiceId": "invoice_number",
                    "InvoiceDate": "invoice_date",
                    "DueDate": "due_date",
                    "SubTotal": "subtotal",
                    "TotalTax": "tax_amount",
                    "InvoiceTotal": "total_amount",
                    "AmountDue": "amount_due",
                }

                for azure_field, our_field in field_mapping.items():
                    if azure_field in invoice.fields:
                        field = invoice.fields[azure_field]
                        invoice_data["fields"][our_field] = {
                            "value": field.value if hasattr(field, 'value') else field.content,
                            "confidence": field.confidence if hasattr(field, 'confidence') else 0.0
                        }

                # Extract line items
                if "Items" in invoice.fields:
                    items_field = invoice.fields["Items"]
                    invoice_data["line_items"] = []

                    for item in items_field.value:
                        line_item = {}
                        item_fields = {
                            "Description": "description",
                            "Quantity": "quantity",
                            "UnitPrice": "unit_price",
                            "Amount": "amount",
                        }

                        for azure_item, our_item in item_fields.items():
                            if azure_item in item.value:
                                line_item[our_item] = item.value[azure_item].value

                        invoice_data["line_items"].append(line_item)

                extracted["invoices"].append(invoice_data)
                extracted["confidence"] = max(extracted["confidence"], invoice.confidence)

            return extracted

        except Exception as e:
            logger.error(f"Azure OCR failed: {e}")
            return {"confidence": 0.0, "invoices": [], "error": str(e)}

    def _apply_azure_ocr_result(self, result: ExtractedInvoice, ocr_data: Dict) -> ExtractedInvoice:
        """Apply Azure OCR results to the invoice object."""
        if not ocr_data.get("invoices"):
            return result

        invoice_data = ocr_data["invoices"][0]
        fields = invoice_data.get("fields", {})

        result.ocr_confidence = ocr_data.get("confidence", 0.0)

        # Apply extracted fields
        if "vendor_name" in fields:
            result.vendor_name = fields["vendor_name"]["value"]
        if "vendor_address" in fields:
            result.vendor_address = fields["vendor_address"]["value"]
            result.vendor_state = self._extract_state_from_address(result.vendor_address)
        if "vendor_tax_id" in fields:
            result.vendor_tax_id = fields["vendor_tax_id"]["value"]
        if "customer_name" in fields:
            result.buyer_name = fields["customer_name"]["value"]
        if "customer_address" in fields:
            result.buyer_address = fields["customer_address"]["value"]
        if "invoice_number" in fields:
            result.invoice_number = fields["invoice_number"]["value"]
        if "invoice_date" in fields:
            result.invoice_date = self._parse_date(fields["invoice_date"]["value"])
        if "due_date" in fields:
            result.due_date = self._parse_date(fields["due_date"]["value"])
        if "subtotal" in fields:
            result.subtotal = Decimal(str(fields["subtotal"]["value"] or 0))
        if "tax_amount" in fields:
            result.tax_amount = Decimal(str(fields["tax_amount"]["value"] or 0))
        if "total_amount" in fields:
            result.total_amount = Decimal(str(fields["total_amount"]["value"] or 0))

        # Process line items
        for item in invoice_data.get("line_items", []):
            line_item = InvoiceLineItem(
                description=item.get("description", ""),
                quantity=item.get("quantity"),
                unit_price=Decimal(str(item.get("unit_price", 0))) if item.get("unit_price") else None,
                amount=Decimal(str(item.get("amount", 0)))
            )
            result.line_items.append(line_item)

        return result

    def _extract_text_basic(self, file_content: bytes, filename: str) -> str:
        """Basic text extraction fallback when Azure OCR is not available."""
        text = ""

        try:
            if filename.lower().endswith('.pdf'):
                try:
                    import PyPDF2
                    import io
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                except Exception as e:
                    logger.warning(f"PyPDF2 extraction failed: {e}")
            else:
                # Try as text
                try:
                    text = file_content.decode('utf-8')
                except:
                    text = file_content.decode('latin-1', errors='ignore')
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")

        return text

    def _parse_invoice_from_text(self, result: ExtractedInvoice, text: str) -> ExtractedInvoice:
        """Parse invoice data from extracted text using patterns."""
        result.ocr_confidence = 0.5  # Lower confidence for basic extraction

        # Invoice number patterns
        invoice_patterns = [
            r'Invoice\s*#?\s*:?\s*(\w+-?\d+)',
            r'INV[-\s]?(\d+)',
            r'Invoice\s+Number[:\s]+(\S+)',
        ]
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.invoice_number = match.group(1)
                break

        # Date patterns
        date_patterns = [
            r'Invoice\s+Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.invoice_date = self._parse_date(match.group(1))
                break

        # Amount patterns
        amount_patterns = [
            r'Total[:\s]+\$?([\d,]+\.?\d*)',
            r'Amount\s+Due[:\s]+\$?([\d,]+\.?\d*)',
            r'Grand\s+Total[:\s]+\$?([\d,]+\.?\d*)',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                result.total_amount = Decimal(amount_str)
                break

        # Vendor name (typically at top)
        lines = text.strip().split('\n')
        if lines:
            # First non-empty line is often vendor name
            for line in lines[:5]:
                line = line.strip()
                if line and len(line) > 3 and not re.match(r'^[\d\$]', line):
                    result.vendor_name = line
                    break

        return result

    async def _ai_analyze_invoice(
        self,
        invoice: ExtractedInvoice,
        study_id: Optional[UUID] = None
    ) -> ExtractedInvoice:
        """Use AI to analyze and categorize invoice for R&D qualification."""
        if not self.openai_client:
            # Fallback to rule-based categorization
            return self._rule_based_categorization(invoice)

        # Prepare invoice summary for AI
        line_items_summary = "\n".join([
            f"- {item.description}: ${item.amount}"
            for item in invoice.line_items
        ]) if invoice.line_items else "No line items extracted"

        prompt = f"""Analyze this invoice for R&D tax credit qualification under IRC Section 41.

INVOICE DETAILS:
- Vendor: {invoice.vendor_name or 'Unknown'}
- Invoice #: {invoice.invoice_number or 'Unknown'}
- Date: {invoice.invoice_date or 'Unknown'}
- Total Amount: ${invoice.total_amount}

LINE ITEMS:
{line_items_summary}

Determine:
1. Primary expense category for R&D (supplies, contract_research, computer_rental, software, equipment_rental, prototype_materials, testing_materials, lab_supplies, other)
2. What percentage of this invoice likely qualifies for R&D tax credit
3. Qualification reasoning

For contract research with qualified small businesses or universities: 65% qualifies
For supplies used in R&D: 100% qualifies
For computer rentals for R&D: 100% qualifies

Return JSON:
{{
    "primary_category": "<category>",
    "qualified_percentage": <0-100>,
    "qualification_reasoning": "<explanation>",
    "line_item_categories": [
        {{"description": "<item>", "category": "<category>", "qualified": true/false, "reason": "<why>"}}
    ],
    "confidence": <0.0-1.0>,
    "pa_qualified": true/false  // Pennsylvania R&D credit eligibility
}}"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an R&D tax credit specialist expert in expense categorization under IRC Section 41."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Apply AI analysis
            invoice.primary_category = ExpenseCategory(result.get("primary_category", "other"))
            invoice.qualification_percentage = Decimal(str(result.get("qualified_percentage", 0)))
            invoice.qualified_amount = invoice.total_amount * (invoice.qualification_percentage / 100)
            invoice.ai_analysis_confidence = result.get("confidence", 0.8)
            invoice.pa_qualified = result.get("pa_qualified", False)
            invoice.processing_notes.append(result.get("qualification_reasoning", ""))

            # Update line item categories
            for i, item_analysis in enumerate(result.get("line_item_categories", [])):
                if i < len(invoice.line_items):
                    invoice.line_items[i].category = ExpenseCategory(item_analysis.get("category", "other"))
                    invoice.line_items[i].rd_qualified = item_analysis.get("qualified", False)
                    invoice.line_items[i].qualification_reason = item_analysis.get("reason", "")

            logger.info(f"AI invoice analysis complete: {invoice.primary_category}, {invoice.qualification_percentage}% qualified")

        except Exception as e:
            logger.error(f"AI invoice analysis failed: {e}")
            invoice = self._rule_based_categorization(invoice)

        return invoice

    def _rule_based_categorization(self, invoice: ExtractedInvoice) -> ExtractedInvoice:
        """Rule-based categorization fallback when AI is unavailable."""
        vendor_lower = (invoice.vendor_name or "").lower()

        # Check for common R&D suppliers
        if any(kw in vendor_lower for kw in ["aws", "amazon web services", "azure", "google cloud", "microsoft"]):
            invoice.primary_category = ExpenseCategory.COMPUTER_RENTAL
            invoice.qualification_percentage = Decimal("100")
        elif any(kw in vendor_lower for kw in ["github", "atlassian", "jetbrains", "adobe", "autodesk"]):
            invoice.primary_category = ExpenseCategory.SOFTWARE
            invoice.qualification_percentage = Decimal("100")
        elif any(kw in vendor_lower for kw in ["lab", "scientific", "chemicals", "fisher", "sigma"]):
            invoice.primary_category = ExpenseCategory.LAB_SUPPLIES
            invoice.qualification_percentage = Decimal("100")
        elif any(kw in vendor_lower for kw in ["consulting", "research", "engineering"]):
            invoice.primary_category = ExpenseCategory.CONTRACT_RESEARCH
            invoice.qualification_percentage = Decimal("65")  # Non-qualified contractor rate
        else:
            # Check line items
            rd_keywords = ["prototype", "testing", "development", "research", "engineering", "software", "hardware"]
            qualified_amount = Decimal("0")

            for item in invoice.line_items:
                desc_lower = item.description.lower()
                if any(kw in desc_lower for kw in rd_keywords):
                    item.rd_qualified = True
                    item.category = ExpenseCategory.SUPPLIES
                    qualified_amount += item.amount

            if qualified_amount > 0:
                invoice.primary_category = ExpenseCategory.SUPPLIES
                invoice.qualification_percentage = (qualified_amount / invoice.total_amount * 100) if invoice.total_amount > 0 else Decimal("0")
            else:
                invoice.primary_category = ExpenseCategory.OTHER
                invoice.qualification_percentage = Decimal("0")

        invoice.qualified_amount = invoice.total_amount * (invoice.qualification_percentage / 100)
        invoice.ai_analysis_confidence = 0.6  # Lower confidence for rule-based

        return invoice

    def _match_vendor(self, invoice: ExtractedInvoice, existing_vendors: List[Dict]) -> ExtractedInvoice:
        """Match vendor to existing vendor records."""
        if not invoice.vendor_name:
            return invoice

        vendor_lower = invoice.vendor_name.lower().strip()

        for vendor in existing_vendors:
            existing_name = vendor.get("name", "").lower().strip()
            if vendor_lower == existing_name or vendor_lower in existing_name or existing_name in vendor_lower:
                invoice.processing_notes.append(f"Matched to existing vendor: {vendor.get('name')}")
                break

        return invoice

    async def process_w2(self, file_content: bytes, filename: str) -> W2Extract:
        """Process a W-2 document for state R&D documentation."""
        logger.info(f"Processing W-2: {filename}")

        result = W2Extract(employee_name="Unknown")

        if self.document_client:
            try:
                # Use W-2 model if available, otherwise general document
                poller = self.document_client.begin_analyze_document(
                    "prebuilt-tax.us.w2",
                    file_content
                )
                analysis_result = poller.result()

                for document in analysis_result.documents:
                    fields = document.fields

                    if "Employee" in fields:
                        emp = fields["Employee"].value
                        if "Name" in emp:
                            result.employee_name = emp["Name"].value
                        if "SocialSecurityNumber" in emp:
                            ssn = emp["SocialSecurityNumber"].value
                            result.ssn_last4 = ssn[-4:] if ssn else None

                    if "Employer" in fields:
                        emp = fields["Employer"].value
                        if "Name" in emp:
                            result.employer_name = emp["Name"].value
                        if "IdNumber" in emp:
                            result.employer_ein = emp["IdNumber"].value
                        if "Address" in emp:
                            addr = emp["Address"].value
                            result.employer_address = str(addr)
                            result.employer_state = self._extract_state_from_address(str(addr))

                    # Wage boxes
                    wage_fields = {
                        "WagesTipsAndOtherCompensation": "wages_box1",
                        "FederalIncomeTaxWithheld": "federal_tax_withheld",
                        "SocialSecurityWages": "social_security_wages",
                        "MedicareWagesAndTips": "medicare_wages",
                    }

                    for azure_field, our_field in wage_fields.items():
                        if azure_field in fields:
                            value = fields[azure_field].value
                            setattr(result, our_field, Decimal(str(value or 0)))

                    # State wages
                    if "StateTaxInfos" in fields:
                        for state_info in fields["StateTaxInfos"].value:
                            state = state_info.value.get("State", {}).value
                            wages = state_info.value.get("StateWages", {}).value
                            tax = state_info.value.get("StateTax", {}).value

                            if state:
                                result.state_wages[state] = Decimal(str(wages or 0))
                                result.state_tax_withheld[state] = Decimal(str(tax or 0))

                    result.ocr_confidence = document.confidence

            except Exception as e:
                logger.error(f"Azure W-2 OCR failed: {e}")
                # Fallback to text extraction
                text = self._extract_text_basic(file_content, filename)
                result = self._parse_w2_from_text(result, text)
        else:
            text = self._extract_text_basic(file_content, filename)
            result = self._parse_w2_from_text(result, text)

        return result

    def _parse_w2_from_text(self, result: W2Extract, text: str) -> W2Extract:
        """Parse W-2 data from text using patterns."""
        result.ocr_confidence = 0.4

        # Extract employee name
        name_patterns = [
            r'Employee.*?name[:\s]+([A-Za-z\s]+)',
            r'(?:1|a)\s+Employee.*?([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.employee_name = match.group(1).strip()
                break

        # Extract wages
        wage_patterns = [
            r'Wages.*?tips.*?\$?([\d,]+\.?\d*)',
            r'Box 1.*?\$?([\d,]+\.?\d*)',
        ]
        for pattern in wage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.wages_box1 = Decimal(match.group(1).replace(',', ''))
                break

        # Extract state
        state_pattern = r'([A-Z]{2})\s+State\s+wages'
        match = re.search(state_pattern, text)
        if match:
            state = match.group(1)
            result.employer_state = state
            # Try to find state wages
            state_wages_pattern = rf'{state}\s+.*?\$?([\d,]+\.?\d*)'
            wages_match = re.search(state_wages_pattern, text)
            if wages_match:
                result.state_wages[state] = Decimal(wages_match.group(1).replace(',', ''))

        return result

    async def process_1099(self, file_content: bytes, filename: str) -> Form1099Extract:
        """Process a 1099 document for contractor documentation."""
        logger.info(f"Processing 1099: {filename}")

        result = Form1099Extract(form_type="1099-NEC", recipient_name="Unknown")

        if self.document_client:
            try:
                # Use 1099 model
                poller = self.document_client.begin_analyze_document(
                    "prebuilt-tax.us.1099NEC",
                    file_content
                )
                analysis_result = poller.result()

                for document in analysis_result.documents:
                    fields = document.fields

                    if "Recipient" in fields:
                        recip = fields["Recipient"].value
                        if "Name" in recip:
                            result.recipient_name = recip["Name"].value
                        if "TIN" in recip:
                            tin = recip["TIN"].value
                            result.recipient_tin_last4 = tin[-4:] if tin else None

                    if "Payer" in fields:
                        payer = fields["Payer"].value
                        if "Name" in payer:
                            result.payer_name = payer["Name"].value
                        if "TIN" in payer:
                            result.payer_tin = payer["TIN"].value
                        if "Address" in payer:
                            result.payer_state = self._extract_state_from_address(str(payer["Address"].value))

                    if "NonemployeeCompensation" in fields:
                        result.nonemployee_compensation = Decimal(str(fields["NonemployeeCompensation"].value or 0))

                    result.ocr_confidence = document.confidence

            except Exception as e:
                logger.error(f"Azure 1099 OCR failed: {e}")
                text = self._extract_text_basic(file_content, filename)
                result = self._parse_1099_from_text(result, text)
        else:
            text = self._extract_text_basic(file_content, filename)
            result = self._parse_1099_from_text(result, text)

        return result

    def _parse_1099_from_text(self, result: Form1099Extract, text: str) -> Form1099Extract:
        """Parse 1099 data from text using patterns."""
        result.ocr_confidence = 0.4

        # Determine form type
        if "1099-NEC" in text:
            result.form_type = "1099-NEC"
        elif "1099-MISC" in text:
            result.form_type = "1099-MISC"

        # Extract nonemployee compensation
        comp_patterns = [
            r'Nonemployee\s+compensation.*?\$?([\d,]+\.?\d*)',
            r'Box 1.*?\$?([\d,]+\.?\d*)',
        ]
        for pattern in comp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.nonemployee_compensation = Decimal(match.group(1).replace(',', ''))
                break

        return result

    def _extract_state_from_address(self, address: str) -> Optional[str]:
        """Extract state code from address string."""
        if not address:
            return None

        # Common state patterns
        state_pattern = r'\b([A-Z]{2})\s+\d{5}'  # State before ZIP
        match = re.search(state_pattern, address)
        if match:
            state = match.group(1)
            if state in ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC']:
                return state

        return None

    def _parse_date(self, date_value: Any) -> Optional[date]:
        """Parse date from various formats."""
        if date_value is None:
            return None

        if isinstance(date_value, date):
            return date_value

        if isinstance(date_value, datetime):
            return date_value.date()

        date_str = str(date_value)

        patterns = [
            ("%m/%d/%Y", r'\d{1,2}/\d{1,2}/\d{4}'),
            ("%Y-%m-%d", r'\d{4}-\d{2}-\d{2}'),
            ("%m-%d-%Y", r'\d{1,2}-\d{1,2}-\d{4}'),
            ("%B %d, %Y", r'[A-Za-z]+\s+\d{1,2},?\s+\d{4}'),
        ]

        for fmt, pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    return datetime.strptime(match.group(), fmt).date()
                except:
                    continue

        return None


class PADocumentPackageService:
    """
    Service for creating Pennsylvania R&D tax credit documentation packages.

    PA requires specific documentation including:
    - PA W-2s for employee wages
    - PA 1099s for contractor payments
    - Invoices for supplies and other R&D expenses
    - Reconciliation to calculation
    """

    def __init__(self, invoice_service: InvoiceOCRService):
        self.invoice_service = invoice_service

    async def create_pa_package(
        self,
        study_id: UUID,
        w2s: List[bytes],
        form_1099s: List[bytes],
        invoices: List[bytes],
        calculation_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a complete PA R&D tax credit documentation package.

        Returns package summary with reconciliation.
        """
        logger.info(f"Creating PA documentation package for study {study_id}")

        # Process W-2s
        pa_w2s = []
        total_pa_wages = Decimal("0")
        for i, w2_content in enumerate(w2s):
            w2 = await self.invoice_service.process_w2(w2_content, f"w2_{i}.pdf")
            if "PA" in w2.state_wages:
                pa_w2s.append({
                    "employee_name": w2.employee_name,
                    "pa_wages": float(w2.state_wages.get("PA", 0)),
                    "federal_wages": float(w2.wages_box1),
                    "ocr_confidence": w2.ocr_confidence
                })
                total_pa_wages += w2.state_wages.get("PA", Decimal("0"))

        # Process 1099s
        pa_1099s = []
        total_pa_contractor = Decimal("0")
        for i, f1099_content in enumerate(form_1099s):
            f1099 = await self.invoice_service.process_1099(f1099_content, f"1099_{i}.pdf")
            if f1099.payer_state == "PA":
                pa_1099s.append({
                    "recipient_name": f1099.recipient_name,
                    "compensation": float(f1099.nonemployee_compensation),
                    "form_type": f1099.form_type,
                    "ocr_confidence": f1099.ocr_confidence
                })
                total_pa_contractor += f1099.nonemployee_compensation

        # Process invoices
        pa_invoices = []
        total_pa_supplies = Decimal("0")
        for i, inv_content in enumerate(invoices):
            invoice = await self.invoice_service.process_invoice(inv_content, f"invoice_{i}.pdf")
            if invoice.pa_qualified or invoice.vendor_state == "PA":
                pa_invoices.append({
                    "vendor": invoice.vendor_name,
                    "invoice_number": invoice.invoice_number,
                    "date": str(invoice.invoice_date) if invoice.invoice_date else None,
                    "total": float(invoice.total_amount),
                    "qualified_amount": float(invoice.qualified_amount),
                    "category": invoice.primary_category.value,
                    "ocr_confidence": invoice.ocr_confidence
                })
                total_pa_supplies += invoice.qualified_amount

        # Create reconciliation
        calc_wages = Decimal(str(calculation_summary.get("pa_qre_wages", 0)))
        calc_contractor = Decimal(str(calculation_summary.get("pa_qre_contractor", 0)))
        calc_supplies = Decimal(str(calculation_summary.get("pa_qre_supplies", 0)))

        reconciliation = {
            "wages": {
                "calculation": float(calc_wages),
                "documented": float(total_pa_wages),
                "variance": float(calc_wages - total_pa_wages),
                "variance_pct": float((calc_wages - total_pa_wages) / calc_wages * 100) if calc_wages > 0 else 0
            },
            "contractor": {
                "calculation": float(calc_contractor),
                "documented": float(total_pa_contractor),
                "variance": float(calc_contractor - total_pa_contractor),
                "variance_pct": float((calc_contractor - total_pa_contractor) / calc_contractor * 100) if calc_contractor > 0 else 0
            },
            "supplies": {
                "calculation": float(calc_supplies),
                "documented": float(total_pa_supplies),
                "variance": float(calc_supplies - total_pa_supplies),
                "variance_pct": float((calc_supplies - total_pa_supplies) / calc_supplies * 100) if calc_supplies > 0 else 0
            }
        }

        # Check reconciliation status
        all_reconciled = all(
            abs(cat["variance_pct"]) < 5  # Within 5% tolerance
            for cat in reconciliation.values()
        )

        package = {
            "study_id": str(study_id),
            "state": "PA",
            "package_date": datetime.utcnow().isoformat(),
            "w2_summary": {
                "count": len(pa_w2s),
                "total_pa_wages": float(total_pa_wages),
                "documents": pa_w2s
            },
            "form_1099_summary": {
                "count": len(pa_1099s),
                "total_compensation": float(total_pa_contractor),
                "documents": pa_1099s
            },
            "invoice_summary": {
                "count": len(pa_invoices),
                "total_qualified": float(total_pa_supplies),
                "documents": pa_invoices
            },
            "reconciliation": reconciliation,
            "reconciliation_status": "complete" if all_reconciled else "variance_detected",
            "notes": []
        }

        if not all_reconciled:
            for cat_name, cat_data in reconciliation.items():
                if abs(cat_data["variance_pct"]) >= 5:
                    package["notes"].append(
                        f"Variance detected in {cat_name}: ${cat_data['variance']:,.2f} ({cat_data['variance_pct']:.1f}%)"
                    )

        logger.info(f"PA package created: {len(pa_w2s)} W-2s, {len(pa_1099s)} 1099s, {len(pa_invoices)} invoices")

        return package
