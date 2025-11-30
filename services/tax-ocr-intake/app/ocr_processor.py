"""
OCR Processing Pipeline

Comprehensive document processing:
- Page splitting for multi-page PDFs
- Document classification using AI
- OCR using Azure Document Intelligence or similar
- Field extraction with confidence scoring
- Structured data output mapped to tax form fields
"""
import asyncio
import logging
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID, uuid4
import io
import base64

logger = logging.getLogger(__name__)


# ========================================
# Document Types
# ========================================

class DocumentType(str, Enum):
    """Supported tax document types"""
    W2 = "W-2"
    W2G = "W-2G"
    FORM_1099_INT = "1099-INT"
    FORM_1099_DIV = "1099-DIV"
    FORM_1099_B = "1099-B"
    FORM_1099_R = "1099-R"
    FORM_1099_MISC = "1099-MISC"
    FORM_1099_NEC = "1099-NEC"
    FORM_1099_G = "1099-G"
    FORM_1099_K = "1099-K"
    FORM_1099_S = "1099-S"
    FORM_1098 = "1098"
    FORM_1098_E = "1098-E"
    FORM_1098_T = "1098-T"
    SSA_1099 = "SSA-1099"
    RRB_1099 = "RRB-1099"
    K1_1065 = "K-1 (1065)"
    K1_1120S = "K-1 (1120-S)"
    K1_1041 = "K-1 (1041)"
    FORM_5498 = "5498"
    FORM_5498_SA = "5498-SA"
    UNKNOWN = "UNKNOWN"


# ========================================
# Data Structures
# ========================================

@dataclass
class BoundingBox:
    """Bounding box for extracted text region"""
    x: float
    y: float
    width: float
    height: float
    page: int = 1


@dataclass
class ExtractedField:
    """A single extracted field from OCR"""
    field_name: str
    field_label: str
    value: Any
    raw_text: str
    confidence: float
    bounding_box: Optional[BoundingBox] = None
    needs_review: bool = False
    review_reason: Optional[str] = None
    suggested_value: Optional[Any] = None


@dataclass
class DocumentPage:
    """A single page of a document"""
    page_number: int
    width: int
    height: int
    raw_text: str
    words: List[Dict[str, Any]] = field(default_factory=list)
    lines: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ClassificationResult:
    """Document classification result"""
    document_type: DocumentType
    confidence: float
    secondary_types: List[Tuple[DocumentType, float]] = field(default_factory=list)


@dataclass
class ExtractionResult:
    """Complete extraction result for a document"""
    document_id: UUID
    document_type: DocumentType
    classification_confidence: float
    fields: Dict[str, ExtractedField]
    pages: List[DocumentPage]
    raw_json: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ========================================
# Field Mappings for Each Document Type
# ========================================

W2_FIELD_MAPPING = {
    "employer_ein": {"label": "Employer EIN", "box": "b", "type": "ein"},
    "employer_name": {"label": "Employer Name", "box": "c", "type": "text"},
    "employer_address": {"label": "Employer Address", "box": "c", "type": "address"},
    "control_number": {"label": "Control Number", "box": "d", "type": "text"},
    "employee_ssn": {"label": "Employee SSN", "box": "a", "type": "ssn"},
    "employee_name": {"label": "Employee Name", "box": "e", "type": "text"},
    "employee_address": {"label": "Employee Address", "box": "f", "type": "address"},
    "wages": {"label": "Wages, tips, other compensation", "box": "1", "type": "currency"},
    "federal_tax_withheld": {"label": "Federal income tax withheld", "box": "2", "type": "currency"},
    "social_security_wages": {"label": "Social security wages", "box": "3", "type": "currency"},
    "social_security_tax": {"label": "Social security tax withheld", "box": "4", "type": "currency"},
    "medicare_wages": {"label": "Medicare wages and tips", "box": "5", "type": "currency"},
    "medicare_tax": {"label": "Medicare tax withheld", "box": "6", "type": "currency"},
    "social_security_tips": {"label": "Social security tips", "box": "7", "type": "currency"},
    "allocated_tips": {"label": "Allocated tips", "box": "8", "type": "currency"},
    "dependent_care_benefits": {"label": "Dependent care benefits", "box": "10", "type": "currency"},
    "nonqualified_plans": {"label": "Nonqualified plans", "box": "11", "type": "currency"},
    "box_12a_code": {"label": "Box 12a code", "box": "12a", "type": "code"},
    "box_12a_amount": {"label": "Box 12a amount", "box": "12a", "type": "currency"},
    "box_12b_code": {"label": "Box 12b code", "box": "12b", "type": "code"},
    "box_12b_amount": {"label": "Box 12b amount", "box": "12b", "type": "currency"},
    "box_12c_code": {"label": "Box 12c code", "box": "12c", "type": "code"},
    "box_12c_amount": {"label": "Box 12c amount", "box": "12c", "type": "currency"},
    "box_12d_code": {"label": "Box 12d code", "box": "12d", "type": "code"},
    "box_12d_amount": {"label": "Box 12d amount", "box": "12d", "type": "currency"},
    "statutory_employee": {"label": "Statutory employee", "box": "13", "type": "checkbox"},
    "retirement_plan": {"label": "Retirement plan", "box": "13", "type": "checkbox"},
    "third_party_sick_pay": {"label": "Third-party sick pay", "box": "13", "type": "checkbox"},
    "state_wages_1": {"label": "State wages (1)", "box": "16", "type": "currency"},
    "state_tax_1": {"label": "State income tax (1)", "box": "17", "type": "currency"},
    "local_wages_1": {"label": "Local wages (1)", "box": "18", "type": "currency"},
    "local_tax_1": {"label": "Local income tax (1)", "box": "19", "type": "currency"},
}

FORM_1099_INT_MAPPING = {
    "payer_name": {"label": "Payer Name", "type": "text"},
    "payer_tin": {"label": "Payer TIN", "type": "ein"},
    "recipient_tin": {"label": "Recipient TIN", "type": "ssn"},
    "recipient_name": {"label": "Recipient Name", "type": "text"},
    "interest_income": {"label": "Interest income", "box": "1", "type": "currency"},
    "early_withdrawal_penalty": {"label": "Early withdrawal penalty", "box": "2", "type": "currency"},
    "interest_on_us_savings_bonds": {"label": "Interest on U.S. Savings Bonds", "box": "3", "type": "currency"},
    "federal_tax_withheld": {"label": "Federal income tax withheld", "box": "4", "type": "currency"},
    "investment_expenses": {"label": "Investment expenses", "box": "5", "type": "currency"},
    "foreign_tax_paid": {"label": "Foreign tax paid", "box": "6", "type": "currency"},
    "tax_exempt_interest": {"label": "Tax-exempt interest", "box": "8", "type": "currency"},
    "private_activity_bond_interest": {"label": "Private activity bond interest", "box": "9", "type": "currency"},
    "market_discount": {"label": "Market discount", "box": "10", "type": "currency"},
    "bond_premium": {"label": "Bond premium", "box": "11", "type": "currency"},
    "state": {"label": "State", "box": "15", "type": "state"},
    "state_tax_withheld": {"label": "State tax withheld", "box": "17", "type": "currency"},
}

FORM_1099_DIV_MAPPING = {
    "payer_name": {"label": "Payer Name", "type": "text"},
    "payer_tin": {"label": "Payer TIN", "type": "ein"},
    "recipient_tin": {"label": "Recipient TIN", "type": "ssn"},
    "recipient_name": {"label": "Recipient Name", "type": "text"},
    "ordinary_dividends": {"label": "Total ordinary dividends", "box": "1a", "type": "currency"},
    "qualified_dividends": {"label": "Qualified dividends", "box": "1b", "type": "currency"},
    "total_capital_gain": {"label": "Total capital gain distributions", "box": "2a", "type": "currency"},
    "unrecap_sec_1250_gain": {"label": "Unrecap. Sec. 1250 gain", "box": "2b", "type": "currency"},
    "section_1202_gain": {"label": "Section 1202 gain", "box": "2c", "type": "currency"},
    "collectibles_gain": {"label": "Collectibles (28%) gain", "box": "2d", "type": "currency"},
    "section_897_ordinary": {"label": "Section 897 ordinary dividends", "box": "2e", "type": "currency"},
    "section_897_capital": {"label": "Section 897 capital gain", "box": "2f", "type": "currency"},
    "nondividend_distributions": {"label": "Nondividend distributions", "box": "3", "type": "currency"},
    "federal_tax_withheld": {"label": "Federal income tax withheld", "box": "4", "type": "currency"},
    "section_199a_dividends": {"label": "Section 199A dividends", "box": "5", "type": "currency"},
    "investment_expenses": {"label": "Investment expenses", "box": "6", "type": "currency"},
    "foreign_tax_paid": {"label": "Foreign tax paid", "box": "7", "type": "currency"},
    "cash_liquidation": {"label": "Cash liquidation distributions", "box": "9", "type": "currency"},
    "noncash_liquidation": {"label": "Noncash liquidation distributions", "box": "10", "type": "currency"},
    "exempt_interest_dividends": {"label": "Exempt-interest dividends", "box": "12", "type": "currency"},
    "state_tax_withheld": {"label": "State tax withheld", "box": "16", "type": "currency"},
}

FORM_1099_R_MAPPING = {
    "payer_name": {"label": "Payer Name", "type": "text"},
    "payer_tin": {"label": "Payer TIN", "type": "ein"},
    "recipient_tin": {"label": "Recipient TIN", "type": "ssn"},
    "recipient_name": {"label": "Recipient Name", "type": "text"},
    "gross_distribution": {"label": "Gross distribution", "box": "1", "type": "currency"},
    "taxable_amount": {"label": "Taxable amount", "box": "2a", "type": "currency"},
    "taxable_amount_not_determined": {"label": "Taxable amount not determined", "box": "2b", "type": "checkbox"},
    "total_distribution": {"label": "Total distribution", "box": "2b", "type": "checkbox"},
    "capital_gain": {"label": "Capital gain", "box": "3", "type": "currency"},
    "federal_tax_withheld": {"label": "Federal income tax withheld", "box": "4", "type": "currency"},
    "employee_contributions": {"label": "Employee contributions", "box": "5", "type": "currency"},
    "net_unrealized_appreciation": {"label": "Net unrealized appreciation", "box": "6", "type": "currency"},
    "distribution_code_1": {"label": "Distribution code(s)", "box": "7", "type": "code"},
    "distribution_code_2": {"label": "Distribution code 2", "box": "7", "type": "code"},
    "ira_sep_simple": {"label": "IRA/SEP/SIMPLE", "box": "7", "type": "checkbox"},
    "other_amount": {"label": "Other", "box": "8", "type": "currency"},
    "total_employee_contribution": {"label": "Total employee contributions", "box": "9b", "type": "currency"},
    "state_tax_withheld": {"label": "State tax withheld", "box": "14", "type": "currency"},
    "local_tax_withheld": {"label": "Local tax withheld", "box": "17", "type": "currency"},
}

DOCUMENT_FIELD_MAPPINGS = {
    DocumentType.W2: W2_FIELD_MAPPING,
    DocumentType.FORM_1099_INT: FORM_1099_INT_MAPPING,
    DocumentType.FORM_1099_DIV: FORM_1099_DIV_MAPPING,
    DocumentType.FORM_1099_R: FORM_1099_R_MAPPING,
    # Add more mappings...
}


# ========================================
# OCR Processor
# ========================================

class OCRProcessor:
    """
    Main OCR processing pipeline.

    Integrates with:
    - Azure Document Intelligence (Form Recognizer)
    - AWS Textract
    - Google Document AI
    - OpenAI GPT-4 Vision for classification
    """

    def __init__(self, provider: str = "azure"):
        self.provider = provider
        self.confidence_threshold = 0.85  # Flag for review below this

    async def process_document(
        self,
        document_id: UUID,
        file_content: bytes,
        file_type: str,
        hint_document_type: Optional[DocumentType] = None
    ) -> ExtractionResult:
        """
        Process a document through the complete OCR pipeline.

        Steps:
        1. Split pages (if multi-page PDF)
        2. Classify document type
        3. Run OCR
        4. Extract structured fields
        5. Validate and flag low-confidence fields
        """
        logger.info(f"Processing document {document_id}")

        # Step 1: Split pages
        pages = await self._split_pages(file_content, file_type)

        # Step 2: Classify document
        if hint_document_type:
            classification = ClassificationResult(
                document_type=hint_document_type,
                confidence=1.0
            )
        else:
            classification = await self._classify_document(pages[0] if pages else None)

        # Step 3: Run OCR
        ocr_result = await self._run_ocr(file_content, file_type)

        # Step 4: Extract structured fields
        fields = await self._extract_fields(
            classification.document_type,
            ocr_result,
            pages
        )

        # Step 5: Build result
        result = ExtractionResult(
            document_id=document_id,
            document_type=classification.document_type,
            classification_confidence=classification.confidence,
            fields=fields,
            pages=pages,
            raw_json=ocr_result
        )

        # Flag low-confidence fields
        self._flag_low_confidence_fields(result)

        return result

    async def _split_pages(
        self,
        file_content: bytes,
        file_type: str
    ) -> List[DocumentPage]:
        """Split multi-page documents into individual pages"""
        pages = []

        if file_type in ["application/pdf", "pdf"]:
            # Would use PyPDF2 or similar to split pages
            # For now, create a single page placeholder
            pages.append(DocumentPage(
                page_number=1,
                width=612,  # Letter size
                height=792,
                raw_text=""
            ))
        else:
            # Single image
            pages.append(DocumentPage(
                page_number=1,
                width=0,
                height=0,
                raw_text=""
            ))

        return pages

    async def _classify_document(
        self,
        first_page: Optional[DocumentPage]
    ) -> ClassificationResult:
        """
        Classify document type using AI.

        Uses GPT-4 Vision or similar for intelligent classification.
        """
        # Would call AI service for classification
        # For demo, return W-2 with high confidence
        return ClassificationResult(
            document_type=DocumentType.W2,
            confidence=0.95,
            secondary_types=[
                (DocumentType.FORM_1099_INT, 0.03),
                (DocumentType.FORM_1099_DIV, 0.02)
            ]
        )

    async def _run_ocr(
        self,
        file_content: bytes,
        file_type: str
    ) -> Dict[str, Any]:
        """
        Run OCR on document.

        Would integrate with Azure Document Intelligence, AWS Textract,
        or Google Document AI.
        """
        if self.provider == "azure":
            return await self._run_azure_ocr(file_content, file_type)
        elif self.provider == "aws":
            return await self._run_aws_textract(file_content)
        elif self.provider == "google":
            return await self._run_google_document_ai(file_content)
        else:
            raise ValueError(f"Unknown OCR provider: {self.provider}")

    async def _run_azure_ocr(
        self,
        file_content: bytes,
        file_type: str
    ) -> Dict[str, Any]:
        """Run Azure Document Intelligence (Form Recognizer)"""
        # Would call Azure Document Intelligence API
        # Return demo data for now
        return {
            "status": "succeeded",
            "analyzeResult": {
                "content": "Sample W-2 content",
                "pages": [{"pageNumber": 1, "words": [], "lines": []}],
                "documents": [{
                    "docType": "tax.w2",
                    "fields": {
                        "Employee": {"content": "John Doe", "confidence": 0.98},
                        "Employer": {"content": "Acme Corporation", "confidence": 0.97},
                        "Wages": {"content": "75000.00", "confidence": 0.96},
                        "FederalTaxWithheld": {"content": "12500.00", "confidence": 0.95},
                        "SocialSecurityWages": {"content": "75000.00", "confidence": 0.94},
                        "SocialSecurityTax": {"content": "4650.00", "confidence": 0.93},
                        "MedicareWages": {"content": "75000.00", "confidence": 0.95},
                        "MedicareTax": {"content": "1087.50", "confidence": 0.94},
                    }
                }]
            }
        }

    async def _run_aws_textract(self, file_content: bytes) -> Dict[str, Any]:
        """Run AWS Textract"""
        # Would call AWS Textract API
        return {"status": "not_implemented"}

    async def _run_google_document_ai(self, file_content: bytes) -> Dict[str, Any]:
        """Run Google Document AI"""
        # Would call Google Document AI API
        return {"status": "not_implemented"}

    async def _extract_fields(
        self,
        document_type: DocumentType,
        ocr_result: Dict[str, Any],
        pages: List[DocumentPage]
    ) -> Dict[str, ExtractedField]:
        """Extract structured fields based on document type"""
        fields = {}

        # Get field mapping for document type
        field_mapping = DOCUMENT_FIELD_MAPPINGS.get(document_type, {})

        # Extract fields from OCR result
        if "analyzeResult" in ocr_result:
            documents = ocr_result["analyzeResult"].get("documents", [])
            if documents:
                doc_fields = documents[0].get("fields", {})

                # Map OCR fields to our schema
                fields = self._map_ocr_fields_to_schema(
                    document_type, doc_fields, field_mapping
                )

        return fields

    def _map_ocr_fields_to_schema(
        self,
        document_type: DocumentType,
        ocr_fields: Dict[str, Any],
        field_mapping: Dict[str, Dict]
    ) -> Dict[str, ExtractedField]:
        """Map OCR extracted fields to our standardized schema"""
        fields = {}

        # Example mapping for W-2
        if document_type == DocumentType.W2:
            # Wages
            if "Wages" in ocr_fields:
                field_data = ocr_fields["Wages"]
                fields["wages"] = ExtractedField(
                    field_name="wages",
                    field_label="Wages, tips, other compensation (Box 1)",
                    value=self._parse_currency(field_data.get("content", "0")),
                    raw_text=field_data.get("content", ""),
                    confidence=field_data.get("confidence", 0),
                    needs_review=field_data.get("confidence", 0) < self.confidence_threshold
                )

            # Federal tax withheld
            if "FederalTaxWithheld" in ocr_fields:
                field_data = ocr_fields["FederalTaxWithheld"]
                fields["federal_tax_withheld"] = ExtractedField(
                    field_name="federal_tax_withheld",
                    field_label="Federal income tax withheld (Box 2)",
                    value=self._parse_currency(field_data.get("content", "0")),
                    raw_text=field_data.get("content", ""),
                    confidence=field_data.get("confidence", 0),
                    needs_review=field_data.get("confidence", 0) < self.confidence_threshold
                )

            # Social Security wages
            if "SocialSecurityWages" in ocr_fields:
                field_data = ocr_fields["SocialSecurityWages"]
                fields["social_security_wages"] = ExtractedField(
                    field_name="social_security_wages",
                    field_label="Social security wages (Box 3)",
                    value=self._parse_currency(field_data.get("content", "0")),
                    raw_text=field_data.get("content", ""),
                    confidence=field_data.get("confidence", 0),
                    needs_review=field_data.get("confidence", 0) < self.confidence_threshold
                )

            # Employee name
            if "Employee" in ocr_fields:
                field_data = ocr_fields["Employee"]
                fields["employee_name"] = ExtractedField(
                    field_name="employee_name",
                    field_label="Employee name (Box e)",
                    value=field_data.get("content", ""),
                    raw_text=field_data.get("content", ""),
                    confidence=field_data.get("confidence", 0),
                    needs_review=field_data.get("confidence", 0) < self.confidence_threshold
                )

            # Employer name
            if "Employer" in ocr_fields:
                field_data = ocr_fields["Employer"]
                fields["employer_name"] = ExtractedField(
                    field_name="employer_name",
                    field_label="Employer name (Box c)",
                    value=field_data.get("content", ""),
                    raw_text=field_data.get("content", ""),
                    confidence=field_data.get("confidence", 0),
                    needs_review=field_data.get("confidence", 0) < self.confidence_threshold
                )

        return fields

    def _parse_currency(self, text: str) -> Decimal:
        """Parse currency string to Decimal"""
        try:
            # Remove currency symbols and commas
            cleaned = text.replace("$", "").replace(",", "").strip()
            return Decimal(cleaned)
        except:
            return Decimal("0")

    def _flag_low_confidence_fields(self, result: ExtractionResult) -> None:
        """Flag fields with low confidence for human review"""
        for field_name, field in result.fields.items():
            if field.confidence < self.confidence_threshold:
                field.needs_review = True
                field.review_reason = f"Low confidence ({field.confidence:.2%})"
                result.warnings.append(
                    f"Field '{field.field_label}' has low confidence ({field.confidence:.2%})"
                )


# ========================================
# AI Document Classifier
# ========================================

class AIDocumentClassifier:
    """
    AI-powered document classification using vision models.

    Uses GPT-4 Vision, Claude Vision, or similar for intelligent
    document type detection.
    """

    def __init__(self, model: str = "gpt-4-vision"):
        self.model = model

    async def classify(
        self,
        image_bytes: bytes,
        available_types: Optional[List[DocumentType]] = None
    ) -> ClassificationResult:
        """
        Classify document using AI vision model.

        Args:
            image_bytes: Image of document (first page)
            available_types: Limit classification to these types

        Returns:
            Classification result with confidence scores
        """
        # Would call AI API with image
        # For demo, return high-confidence W-2

        prompt = """
        Analyze this tax document image and identify the document type.

        Possible types:
        - W-2 (Wage and Tax Statement)
        - 1099-INT (Interest Income)
        - 1099-DIV (Dividend Income)
        - 1099-B (Brokerage Statement)
        - 1099-R (Retirement Distributions)
        - 1099-MISC (Miscellaneous Income)
        - 1099-NEC (Nonemployee Compensation)
        - 1098 (Mortgage Interest)
        - SSA-1099 (Social Security Benefits)
        - K-1 (Partnership/S-Corp income)

        Return JSON with:
        {
            "document_type": "type code",
            "confidence": 0.0-1.0,
            "reasoning": "explanation"
        }
        """

        # Simulate AI response
        return ClassificationResult(
            document_type=DocumentType.W2,
            confidence=0.95,
            secondary_types=[
                (DocumentType.FORM_1099_NEC, 0.03),
                (DocumentType.FORM_1099_MISC, 0.02)
            ]
        )


# ========================================
# Extraction Validators
# ========================================

class ExtractionValidator:
    """Validates extracted data for consistency and completeness"""

    @staticmethod
    def validate_w2(fields: Dict[str, ExtractedField]) -> List[str]:
        """Validate W-2 extraction"""
        errors = []

        # Check required fields
        required = ["wages", "federal_tax_withheld", "social_security_wages", "medicare_wages"]
        for field_name in required:
            if field_name not in fields or fields[field_name].value is None:
                errors.append(f"Missing required field: {field_name}")

        # Cross-validate: SS wages should not exceed SS wage base
        if "social_security_wages" in fields:
            ss_wages = fields["social_security_wages"].value
            if ss_wages and ss_wages > Decimal("168600"):  # 2024 limit
                errors.append("Social Security wages exceed annual limit")

        # SS tax should be ~6.2% of SS wages
        if "social_security_wages" in fields and "social_security_tax" in fields:
            ss_wages = fields["social_security_wages"].value or Decimal("0")
            ss_tax = fields.get("social_security_tax", ExtractedField("", "", Decimal("0"), "", 0)).value or Decimal("0")
            expected_tax = ss_wages * Decimal("0.062")
            if abs(ss_tax - expected_tax) > Decimal("1"):
                errors.append("Social Security tax does not match expected (6.2%)")

        # Medicare tax should be ~1.45% of Medicare wages
        if "medicare_wages" in fields and "medicare_tax" in fields:
            med_wages = fields["medicare_wages"].value or Decimal("0")
            med_tax = fields.get("medicare_tax", ExtractedField("", "", Decimal("0"), "", 0)).value or Decimal("0")
            expected_tax = med_wages * Decimal("0.0145")
            if abs(med_tax - expected_tax) > Decimal("1"):
                errors.append("Medicare tax does not match expected (1.45%)")

        return errors

    @staticmethod
    def validate_1099_int(fields: Dict[str, ExtractedField]) -> List[str]:
        """Validate 1099-INT extraction"""
        errors = []

        if "interest_income" not in fields:
            errors.append("Missing interest income field")

        return errors

    @staticmethod
    def validate_1099_div(fields: Dict[str, ExtractedField]) -> List[str]:
        """Validate 1099-DIV extraction"""
        errors = []

        if "ordinary_dividends" not in fields:
            errors.append("Missing ordinary dividends field")

        # Qualified dividends should not exceed ordinary dividends
        if "ordinary_dividends" in fields and "qualified_dividends" in fields:
            ordinary = fields["ordinary_dividends"].value or Decimal("0")
            qualified = fields["qualified_dividends"].value or Decimal("0")
            if qualified > ordinary:
                errors.append("Qualified dividends cannot exceed ordinary dividends")

        return errors
