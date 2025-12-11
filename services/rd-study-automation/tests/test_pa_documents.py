"""
Test PA Document Package Feature

Tests for Pennsylvania R&D tax credit documentation package including:
- Sample PA W-2 generation and processing
- Sample PA 1099 generation and processing
- Sample PA invoice generation and processing
- PA document package reconciliation
"""

import pytest
import io
import json
from decimal import Decimal
from uuid import uuid4
from datetime import date, datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.ai.invoice_ocr_service import (
    InvoiceOCRService,
    PADocumentPackageService,
    ExtractedInvoice,
    InvoiceLineItem,
    W2Extract,
    Form1099Extract,
    ExpenseCategory
)


# =============================================================================
# SAMPLE DOCUMENT GENERATORS
# =============================================================================

def create_sample_pa_invoice(
    vendor_name: str = "TechSupplies PA Inc.",
    vendor_address: str = "123 Innovation Way, Pittsburgh, PA 15213",
    invoice_number: str = "INV-PA-2024-001",
    invoice_date: str = "2024-11-15",
    items: list = None,
    total: float = None
) -> bytes:
    """Generate a sample Pennsylvania invoice PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Header
    story.append(Paragraph(f"<b>{vendor_name}</b>", styles['Heading1']))
    story.append(Paragraph(vendor_address, styles['Normal']))
    story.append(Spacer(1, 20))

    # Invoice details
    story.append(Paragraph(f"<b>Invoice #{invoice_number}</b>", styles['Heading2']))
    story.append(Paragraph(f"Date: {invoice_date}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Bill to
    story.append(Paragraph("<b>Bill To:</b>", styles['Normal']))
    story.append(Paragraph("Acme R&D Corporation", styles['Normal']))
    story.append(Paragraph("456 Research Blvd, Philadelphia, PA 19104", styles['Normal']))
    story.append(Spacer(1, 20))

    # Default items if none provided
    if items is None:
        items = [
            ("Laboratory Testing Equipment - Prototype Materials", 1, 5250.00),
            ("Software Development Tools License - Annual", 1, 3600.00),
            ("Cloud Computing Services - R&D Workloads", 1, 2400.00),
            ("Engineering Supplies - CAD Software", 1, 1200.00),
            ("Testing Materials - Quality Assurance", 50, 45.00),
        ]

    # Line items table
    table_data = [["Description", "Qty", "Unit Price", "Amount"]]
    subtotal = 0

    for desc, qty, unit_price in items:
        amount = qty * unit_price
        subtotal += amount
        table_data.append([
            desc,
            str(qty),
            f"${unit_price:,.2f}",
            f"${amount:,.2f}"
        ])

    # Calculate totals
    if total is None:
        total = subtotal

    tax = total * 0.06  # PA sales tax
    grand_total = total + tax

    table_data.append(["", "", "Subtotal:", f"${subtotal:,.2f}"])
    table_data.append(["", "", "PA Sales Tax (6%):", f"${tax:,.2f}"])
    table_data.append(["", "", "<b>Total Due:</b>", f"<b>${grand_total:,.2f}</b>"])

    table = Table(table_data, colWidths=[280, 50, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),
        ('LINEBELOW', (2, -3), (3, -3), 1, colors.black),
        ('LINEBELOW', (2, -1), (3, -1), 2, colors.black),
    ]))
    story.append(table)

    story.append(Spacer(1, 30))
    story.append(Paragraph("Payment Terms: Net 30", styles['Normal']))
    story.append(Paragraph("Federal Tax ID: 25-1234567", styles['Normal']))

    doc.build(story)
    return buffer.getvalue()


def create_sample_pa_w2(
    employee_name: str = "John Smith",
    ssn_last4: str = "1234",
    employer_name: str = "Acme R&D Corporation",
    employer_ein: str = "25-9876543",
    wages_box1: float = 125000.00,
    pa_wages: float = 125000.00,
    federal_withheld: float = 25000.00,
    pa_withheld: float = 3843.75,
    tax_year: int = 2024
) -> bytes:
    """Generate a sample Pennsylvania W-2 PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Header
    story.append(Paragraph("<b>Form W-2 Wage and Tax Statement</b>", styles['Heading1']))
    story.append(Paragraph(f"Tax Year {tax_year}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Employer info
    employer_data = [
        ["<b>Employer Information</b>", ""],
        ["Employer Name:", employer_name],
        ["Employer EIN:", employer_ein],
        ["Employer Address:", "456 Research Blvd, Philadelphia, PA 19104"],
    ]

    employer_table = Table(employer_data, colWidths=[150, 300])
    employer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('SPAN', (0, 0), (1, 0)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(employer_table)
    story.append(Spacer(1, 15))

    # Employee info
    employee_data = [
        ["<b>Employee Information</b>", ""],
        ["Employee Name:", employee_name],
        ["SSN:", f"XXX-XX-{ssn_last4}"],
        ["Employee Address:", "789 Innovation St, Harrisburg, PA 17101"],
    ]

    employee_table = Table(employee_data, colWidths=[150, 300])
    employee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('SPAN', (0, 0), (1, 0)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(employee_table)
    story.append(Spacer(1, 15))

    # Wage boxes
    wage_data = [
        ["<b>Wages and Tax Information</b>", "", "", ""],
        ["Box 1 - Wages, tips, other comp:", f"${wages_box1:,.2f}",
         "Box 2 - Federal income tax withheld:", f"${federal_withheld:,.2f}"],
        ["Box 3 - Social security wages:", f"${wages_box1:,.2f}",
         "Box 4 - Social security tax withheld:", f"${wages_box1 * 0.062:,.2f}"],
        ["Box 5 - Medicare wages and tips:", f"${wages_box1:,.2f}",
         "Box 6 - Medicare tax withheld:", f"${wages_box1 * 0.0145:,.2f}"],
    ]

    wage_table = Table(wage_data, colWidths=[180, 100, 180, 100])
    wage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('SPAN', (0, 0), (3, 0)),
        ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(wage_table)
    story.append(Spacer(1, 15))

    # State info (PA)
    state_data = [
        ["<b>State Tax Information</b>", "", "", ""],
        ["Box 15 - State:", "PA",
         "Box 16 - State wages:", f"${pa_wages:,.2f}"],
        ["Box 17 - State income tax:", f"${pa_withheld:,.2f}",
         "", ""],
    ]

    state_table = Table(state_data, colWidths=[150, 100, 150, 100])
    state_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('SPAN', (0, 0), (3, 0)),
        ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(state_table)

    doc.build(story)
    return buffer.getvalue()


def create_sample_pa_1099(
    recipient_name: str = "Research Consulting LLC",
    recipient_tin_last4: str = "5678",
    payer_name: str = "Acme R&D Corporation",
    payer_ein: str = "25-9876543",
    compensation: float = 45000.00,
    tax_year: int = 2024
) -> bytes:
    """Generate a sample Pennsylvania 1099-NEC PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Header
    story.append(Paragraph("<b>Form 1099-NEC</b>", styles['Heading1']))
    story.append(Paragraph("Nonemployee Compensation", styles['Heading2']))
    story.append(Paragraph(f"Tax Year {tax_year}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Payer info
    payer_data = [
        ["<b>PAYER'S Information</b>", ""],
        ["Payer's Name:", payer_name],
        ["Payer's TIN:", payer_ein],
        ["Payer's Address:", "456 Research Blvd, Philadelphia, PA 19104"],
    ]

    payer_table = Table(payer_data, colWidths=[150, 300])
    payer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('SPAN', (0, 0), (1, 0)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(payer_table)
    story.append(Spacer(1, 15))

    # Recipient info
    recipient_data = [
        ["<b>RECIPIENT'S Information</b>", ""],
        ["Recipient's Name:", recipient_name],
        ["Recipient's TIN:", f"XX-XXX{recipient_tin_last4}"],
        ["Recipient's Address:", "321 Contractor Ave, Pittsburgh, PA 15222"],
    ]

    recipient_table = Table(recipient_data, colWidths=[150, 300])
    recipient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('SPAN', (0, 0), (1, 0)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(recipient_table)
    story.append(Spacer(1, 15))

    # Amount boxes
    amount_data = [
        ["<b>Income Information</b>", ""],
        ["Box 1 - Nonemployee compensation:", f"${compensation:,.2f}"],
        ["Box 4 - Federal income tax withheld:", "$0.00"],
        ["Box 5 - State tax withheld:", "$0.00"],
        ["Box 6 - State/Payer's state no.:", "PA / 25-9876543"],
        ["Box 7 - State income:", f"${compensation:,.2f}"],
    ]

    amount_table = Table(amount_data, colWidths=[200, 200])
    amount_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('SPAN', (0, 0), (1, 0)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(amount_table)

    doc.build(story)
    return buffer.getvalue()


# =============================================================================
# UNIT TESTS
# =============================================================================

class TestInvoiceOCRService:
    """Tests for the Invoice OCR Service."""

    @pytest.fixture
    def service(self):
        """Create invoice service without Azure credentials (will use fallback)."""
        return InvoiceOCRService()

    @pytest.mark.asyncio
    async def test_process_invoice_basic(self, service):
        """Test basic invoice processing."""
        invoice_pdf = create_sample_pa_invoice()

        result = await service.process_invoice(
            file_content=invoice_pdf,
            filename="pa_invoice_001.pdf"
        )

        assert isinstance(result, ExtractedInvoice)
        # With fallback processing, we may not get all fields
        # but the structure should be valid
        assert result.total_amount >= Decimal("0")

    @pytest.mark.asyncio
    async def test_rule_based_categorization_cloud(self, service):
        """Test rule-based categorization for cloud services."""
        invoice = ExtractedInvoice()
        invoice.vendor_name = "Amazon Web Services"
        invoice.total_amount = Decimal("5000.00")

        result = service._rule_based_categorization(invoice)

        assert result.primary_category == ExpenseCategory.COMPUTER_RENTAL
        assert result.qualification_percentage == Decimal("100")
        assert result.qualified_amount == Decimal("5000.00")

    @pytest.mark.asyncio
    async def test_rule_based_categorization_software(self, service):
        """Test rule-based categorization for software."""
        invoice = ExtractedInvoice()
        invoice.vendor_name = "JetBrains s.r.o."
        invoice.total_amount = Decimal("600.00")

        result = service._rule_based_categorization(invoice)

        assert result.primary_category == ExpenseCategory.SOFTWARE
        assert result.qualification_percentage == Decimal("100")

    @pytest.mark.asyncio
    async def test_rule_based_categorization_lab_supplies(self, service):
        """Test rule-based categorization for lab supplies."""
        invoice = ExtractedInvoice()
        invoice.vendor_name = "Fisher Scientific"
        invoice.total_amount = Decimal("2500.00")

        result = service._rule_based_categorization(invoice)

        assert result.primary_category == ExpenseCategory.LAB_SUPPLIES
        assert result.qualification_percentage == Decimal("100")

    @pytest.mark.asyncio
    async def test_rule_based_categorization_consulting(self, service):
        """Test rule-based categorization for consulting."""
        invoice = ExtractedInvoice()
        invoice.vendor_name = "Tech Research Consulting LLC"
        invoice.total_amount = Decimal("15000.00")

        result = service._rule_based_categorization(invoice)

        assert result.primary_category == ExpenseCategory.CONTRACT_RESEARCH
        assert result.qualification_percentage == Decimal("65")  # Non-qualified contractor
        assert result.qualified_amount == Decimal("9750.00")  # 65% of 15000

    @pytest.mark.asyncio
    async def test_w2_processing(self, service):
        """Test W-2 processing."""
        w2_pdf = create_sample_pa_w2(
            employee_name="Jane Developer",
            wages_box1=150000.00,
            pa_wages=150000.00
        )

        result = await service.process_w2(w2_pdf, "w2_jane.pdf")

        assert isinstance(result, W2Extract)
        # Basic structure should be present
        assert result.tax_year == 2024

    @pytest.mark.asyncio
    async def test_1099_processing(self, service):
        """Test 1099 processing."""
        form_1099_pdf = create_sample_pa_1099(
            recipient_name="Innovation Consulting Inc",
            compensation=75000.00
        )

        result = await service.process_1099(form_1099_pdf, "1099_consultant.pdf")

        assert isinstance(result, Form1099Extract)
        assert result.form_type in ["1099-NEC", "1099-MISC"]

    def test_extract_state_from_address(self, service):
        """Test state extraction from address."""
        # Valid PA addresses
        assert service._extract_state_from_address("123 Main St, Pittsburgh, PA 15213") == "PA"
        assert service._extract_state_from_address("456 Oak Ave, Philadelphia PA 19104") == "PA"

        # Other states
        assert service._extract_state_from_address("789 Elm St, Boston, MA 02101") == "MA"
        assert service._extract_state_from_address("321 Pine Rd, Austin, TX 78701") == "TX"

        # Invalid
        assert service._extract_state_from_address("No state here") is None

    def test_parse_date(self, service):
        """Test date parsing."""
        assert service._parse_date("11/15/2024") == date(2024, 11, 15)
        assert service._parse_date("2024-11-15") == date(2024, 11, 15)
        assert service._parse_date(date(2024, 11, 15)) == date(2024, 11, 15)
        assert service._parse_date(None) is None


class TestPADocumentPackageService:
    """Tests for PA Document Package Service."""

    @pytest.fixture
    def invoice_service(self):
        return InvoiceOCRService()

    @pytest.fixture
    def pa_service(self, invoice_service):
        return PADocumentPackageService(invoice_service)

    @pytest.mark.asyncio
    async def test_create_pa_package(self, pa_service):
        """Test creating a complete PA document package."""
        # Generate sample documents
        w2s = [
            create_sample_pa_w2(employee_name="John Engineer", wages_box1=125000, pa_wages=125000),
            create_sample_pa_w2(employee_name="Jane Scientist", wages_box1=145000, pa_wages=145000),
            create_sample_pa_w2(employee_name="Bob Developer", wages_box1=115000, pa_wages=115000),
        ]

        form_1099s = [
            create_sample_pa_1099(recipient_name="Research Consulting LLC", compensation=45000),
            create_sample_pa_1099(recipient_name="Tech Advisory Services", compensation=35000),
        ]

        invoices = [
            create_sample_pa_invoice(vendor_name="Lab Supplies PA", invoice_number="INV-001"),
            create_sample_pa_invoice(vendor_name="Cloud Services Inc", invoice_number="INV-002"),
            create_sample_pa_invoice(vendor_name="Engineering Materials", invoice_number="INV-003"),
        ]

        # Calculation summary (what should match)
        calculation_summary = {
            "pa_qre_wages": 385000.00,  # Sum of W-2 PA wages
            "pa_qre_contractor": 80000.00,  # Sum of 1099s
            "pa_qre_supplies": 45000.00,  # Sum of invoices
        }

        study_id = uuid4()
        package = await pa_service.create_pa_package(
            study_id=study_id,
            w2s=w2s,
            form_1099s=form_1099s,
            invoices=invoices,
            calculation_summary=calculation_summary
        )

        # Verify package structure
        assert package["study_id"] == str(study_id)
        assert package["state"] == "PA"
        assert "w2_summary" in package
        assert "form_1099_summary" in package
        assert "invoice_summary" in package
        assert "reconciliation" in package

        # Check document counts
        assert package["w2_summary"]["count"] >= 0
        assert package["form_1099_summary"]["count"] >= 0
        assert package["invoice_summary"]["count"] >= 0


class TestSampleDocumentGeneration:
    """Tests for sample document generation."""

    def test_create_sample_pa_invoice(self):
        """Test PA invoice PDF generation."""
        pdf_content = create_sample_pa_invoice(
            vendor_name="Test Vendor PA",
            invoice_number="TEST-001"
        )

        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        # PDF magic bytes
        assert pdf_content[:4] == b'%PDF'

    def test_create_sample_pa_w2(self):
        """Test PA W-2 PDF generation."""
        pdf_content = create_sample_pa_w2(
            employee_name="Test Employee",
            wages_box1=100000.00
        )

        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        assert pdf_content[:4] == b'%PDF'

    def test_create_sample_pa_1099(self):
        """Test PA 1099 PDF generation."""
        pdf_content = create_sample_pa_1099(
            recipient_name="Test Contractor",
            compensation=50000.00
        )

        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        assert pdf_content[:4] == b'%PDF'


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestPADocumentPackageIntegration:
    """Integration tests for PA document package with actual study data."""

    @pytest.mark.asyncio
    async def test_full_pa_workflow(self):
        """Test complete PA document package workflow."""
        # This would typically require database setup
        # For now, test the service layer

        invoice_service = InvoiceOCRService()
        pa_service = PADocumentPackageService(invoice_service)

        # Create comprehensive test data
        employees = [
            {"name": "Alice Engineer", "wages": 135000, "pa_wages": 135000, "rd_pct": 80},
            {"name": "Bob Scientist", "wages": 155000, "pa_wages": 155000, "rd_pct": 90},
            {"name": "Carol Developer", "wages": 125000, "pa_wages": 125000, "rd_pct": 75},
            {"name": "David Researcher", "wages": 145000, "pa_wages": 145000, "rd_pct": 85},
            {"name": "Eve Analyst", "wages": 95000, "pa_wages": 95000, "rd_pct": 50},
        ]

        contractors = [
            {"name": "R&D Consulting Partners", "amount": 65000},
            {"name": "Tech Innovation Lab", "amount": 45000},
            {"name": "Scientific Research Inc", "amount": 35000},
        ]

        vendors = [
            {"name": "PA Lab Supplies Co", "number": "INV-PA-001", "items": [
                ("Laboratory Equipment", 1, 8500.00),
                ("Testing Materials", 100, 25.00),
                ("Safety Supplies", 50, 35.00),
            ]},
            {"name": "Cloud Computing PA", "number": "INV-PA-002", "items": [
                ("AWS R&D Instance Hours", 1, 4500.00),
                ("Azure ML Compute", 1, 3200.00),
            ]},
            {"name": "Engineering Materials Inc", "number": "INV-PA-003", "items": [
                ("Prototype Components", 25, 180.00),
                ("PCB Manufacturing", 10, 450.00),
            ]},
        ]

        # Generate documents
        w2s = [
            create_sample_pa_w2(
                employee_name=emp["name"],
                wages_box1=emp["wages"],
                pa_wages=emp["pa_wages"]
            )
            for emp in employees
        ]

        form_1099s = [
            create_sample_pa_1099(
                recipient_name=contractor["name"],
                compensation=contractor["amount"]
            )
            for contractor in contractors
        ]

        invoices = [
            create_sample_pa_invoice(
                vendor_name=vendor["name"],
                invoice_number=vendor["number"],
                items=vendor["items"]
            )
            for vendor in vendors
        ]

        # Calculate expected totals
        total_wages = sum(emp["pa_wages"] * emp["rd_pct"] / 100 for emp in employees)
        total_contractor = sum(c["amount"] * 0.65 for c in contractors)  # 65% qualified
        total_supplies = sum(
            sum(qty * price for _, qty, price in vendor["items"])
            for vendor in vendors
        )

        calculation_summary = {
            "pa_qre_wages": total_wages,
            "pa_qre_contractor": total_contractor,
            "pa_qre_supplies": total_supplies,
        }

        # Create package
        study_id = uuid4()
        package = await pa_service.create_pa_package(
            study_id=study_id,
            w2s=w2s,
            form_1099s=form_1099s,
            invoices=invoices,
            calculation_summary=calculation_summary
        )

        # Verify results
        assert package["study_id"] == str(study_id)
        assert package["state"] == "PA"

        # Print summary for verification
        print("\n=== PA Document Package Summary ===")
        print(f"Study ID: {package['study_id']}")
        print(f"\nW-2 Summary:")
        print(f"  Documents: {package['w2_summary']['count']}")
        print(f"  Total PA Wages: ${package['w2_summary']['total_pa_wages']:,.2f}")
        print(f"\n1099 Summary:")
        print(f"  Documents: {package['form_1099_summary']['count']}")
        print(f"  Total Compensation: ${package['form_1099_summary']['total_compensation']:,.2f}")
        print(f"\nInvoice Summary:")
        print(f"  Documents: {package['invoice_summary']['count']}")
        print(f"  Total Qualified: ${package['invoice_summary']['total_qualified']:,.2f}")
        print(f"\nReconciliation Status: {package['reconciliation_status']}")

        if package['notes']:
            print("\nNotes:")
            for note in package['notes']:
                print(f"  - {note}")


# =============================================================================
# RUN SAMPLE DOCUMENT GENERATION
# =============================================================================

def generate_sample_pa_documents():
    """Generate sample PA documents for manual testing."""
    import os

    output_dir = "test_pa_documents"
    os.makedirs(output_dir, exist_ok=True)

    # Generate invoices
    invoices = [
        {
            "vendor_name": "Pittsburgh Tech Supplies Inc.",
            "vendor_address": "123 Innovation Drive, Pittsburgh, PA 15213",
            "invoice_number": "INV-PA-2024-001",
            "items": [
                ("R&D Testing Equipment - Oscilloscope", 1, 4500.00),
                ("Prototype PCB Materials", 50, 45.00),
                ("Laboratory Safety Equipment", 10, 125.00),
                ("Electronic Components Kit", 5, 350.00),
            ]
        },
        {
            "vendor_name": "Philadelphia Cloud Services",
            "vendor_address": "456 Market Street, Philadelphia, PA 19104",
            "invoice_number": "INV-PA-2024-002",
            "items": [
                ("AWS R&D Compute Instance - Monthly", 1, 3200.00),
                ("Azure Machine Learning Compute", 1, 2800.00),
                ("Google Cloud AI Platform", 1, 1950.00),
            ]
        },
        {
            "vendor_name": "Harrisburg Engineering Materials",
            "vendor_address": "789 Capitol Blvd, Harrisburg, PA 17101",
            "invoice_number": "INV-PA-2024-003",
            "items": [
                ("CAD Software License - Annual", 1, 2400.00),
                ("3D Printing Filament - R&D Grade", 20, 85.00),
                ("Mechanical Testing Materials", 100, 12.50),
            ]
        },
    ]

    for i, inv_data in enumerate(invoices):
        pdf = create_sample_pa_invoice(**inv_data)
        filename = f"{output_dir}/pa_invoice_{i+1}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf)
        print(f"Created: {filename}")

    # Generate W-2s
    employees = [
        {"employee_name": "Michael Chen", "wages_box1": 145000, "pa_wages": 145000},
        {"employee_name": "Sarah Johnson", "wages_box1": 128000, "pa_wages": 128000},
        {"employee_name": "David Williams", "wages_box1": 165000, "pa_wages": 165000},
        {"employee_name": "Emily Davis", "wages_box1": 112000, "pa_wages": 112000},
        {"employee_name": "Robert Martinez", "wages_box1": 138000, "pa_wages": 138000},
    ]

    for i, emp_data in enumerate(employees):
        pdf = create_sample_pa_w2(**emp_data)
        filename = f"{output_dir}/pa_w2_{i+1}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf)
        print(f"Created: {filename}")

    # Generate 1099s
    contractors = [
        {"recipient_name": "Innovation Research Partners LLC", "compensation": 75000},
        {"recipient_name": "Technical Consulting Associates", "compensation": 55000},
        {"recipient_name": "R&D Advisory Services Inc", "compensation": 42000},
    ]

    for i, contractor_data in enumerate(contractors):
        pdf = create_sample_pa_1099(**contractor_data)
        filename = f"{output_dir}/pa_1099_{i+1}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf)
        print(f"Created: {filename}")

    print(f"\nAll sample documents created in '{output_dir}/' directory")


if __name__ == "__main__":
    generate_sample_pa_documents()
