"""
PDF Study Report Generator

Generates audit-ready PDF R&D tax credit study reports using ReportLab.
"""

import io
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, ListFlowable, ListItem, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import Drawing, Line

logger = logging.getLogger(__name__)


class PDFStudyGenerator:
    """
    Generates comprehensive PDF R&D tax credit study reports.

    Report includes:
    - Cover Page
    - Table of Contents
    - Executive Summary
    - Qualification Analysis
    - Evidence Matrix
    - Project Narratives
    - Employee Role Narratives
    - QRE Schedules
    - Federal Calculation
    - State Addenda
    - Assumptions & Limitations
    - Appendix with Citations
    """

    # Color definitions
    PRIMARY_COLOR = colors.HexColor("#1F4E79")
    SECONDARY_COLOR = colors.HexColor("#2E7D32")
    WARNING_COLOR = colors.HexColor("#E65100")
    LIGHT_GRAY = colors.HexColor("#F5F5F5")
    BORDER_COLOR = colors.HexColor("#CCCCCC")

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.include_watermark = self.config.get("include_watermark", True)
        self.watermark_text = "DRAFT - NOT FOR FILING"
        self.styles = self._create_styles()

    def _create_styles(self) -> Dict:
        """Create custom paragraph styles."""
        styles = getSampleStyleSheet()

        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section heading
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.PRIMARY_COLOR,
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            borderPadding=(0, 0, 5, 0),
            borderWidth=2,
            borderColor=self.PRIMARY_COLOR
        ))

        # Subsection heading
        styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=self.PRIMARY_COLOR,
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))

        # Body text - use existing BodyText style but customize it
        # Don't add new 'BodyText' as it already exists in getSampleStyleSheet()
        body_style = styles['BodyText']
        body_style.fontSize = 10
        body_style.leading = 14
        body_style.alignment = TA_JUSTIFY
        body_style.spaceBefore = 6
        body_style.spaceAfter = 6

        # Caption
        styles.add(ParagraphStyle(
            name='Caption',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=12
        ))

        # Credit amount
        styles.add(ParagraphStyle(
            name='CreditAmount',
            parent=styles['Normal'],
            fontSize=14,
            textColor=self.SECONDARY_COLOR,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT
        ))

        # Citation
        styles.add(ParagraphStyle(
            name='Citation',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            fontName='Helvetica-Oblique'
        ))

        return styles

    def generate_study_report(
        self,
        study_data: Dict[str, Any],
        projects: List[Dict[str, Any]],
        employees: List[Dict[str, Any]],
        qre_summary: Dict[str, Any],
        calculation_result: Dict[str, Any],
        narratives: Dict[str, str],
        evidence_items: List[Dict[str, Any]],
        is_final: bool = False
    ) -> bytes:
        """
        Generate complete PDF study report.

        Returns PDF content as bytes.
        """
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
            title=f"R&D Tax Credit Study - {study_data.get('entity_name', 'Unknown')}",
            author="Aura Audit AI"
        )

        story = []

        # Build document sections
        story.extend(self._build_cover_page(study_data, calculation_result, is_final))
        story.append(PageBreak())

        story.extend(self._build_executive_summary(
            study_data, calculation_result, narratives, projects
        ))
        story.append(PageBreak())

        story.extend(self._build_methodology_section(study_data))
        story.append(PageBreak())

        story.extend(self._build_qualification_analysis(projects))
        story.append(PageBreak())

        story.extend(self._build_qre_schedules(qre_summary, employees))
        story.append(PageBreak())

        story.extend(self._build_federal_calculation(calculation_result))
        story.append(PageBreak())

        if study_data.get("states"):
            story.extend(self._build_state_addenda(study_data, calculation_result))
            story.append(PageBreak())

        story.extend(self._build_project_narratives(projects, narratives))
        story.append(PageBreak())

        story.extend(self._build_assumptions_section(study_data))
        story.append(PageBreak())

        story.extend(self._build_appendix(evidence_items))

        # Build PDF
        if is_final:
            doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        else:
            doc.build(story, onFirstPage=self._add_draft_watermark, onLaterPages=self._add_draft_watermark)

        buffer.seek(0)
        return buffer.getvalue()

    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()

        # Header line
        canvas.setStrokeColor(self.PRIMARY_COLOR)
        canvas.setLineWidth(1)
        canvas.line(0.75 * inch, 10.25 * inch, 7.75 * inch, 10.25 * inch)

        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)
        canvas.drawString(0.75 * inch, 0.5 * inch, f"Generated: {datetime.now().strftime('%B %d, %Y')}")
        canvas.drawRightString(7.75 * inch, 0.5 * inch, f"Page {doc.page}")

        # Confidential notice
        canvas.setFont('Helvetica-Oblique', 7)
        canvas.drawCentredString(4.25 * inch, 0.5 * inch, "CONFIDENTIAL - Prepared for client use only")

        canvas.restoreState()

    def _add_draft_watermark(self, canvas, doc):
        """Add draft watermark to each page."""
        canvas.saveState()

        # Header and footer
        self._add_header_footer(canvas, doc)

        # Watermark
        canvas.setFont('Helvetica-Bold', 60)
        canvas.setFillColor(colors.HexColor("#FFCCCC"))
        canvas.setFillAlpha(0.3)
        canvas.translate(4.25 * inch, 5.5 * inch)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "DRAFT")

        canvas.restoreState()

    def _build_cover_page(
        self,
        study_data: Dict,
        calculation_result: Dict,
        is_final: bool
    ) -> List:
        """Build professional cover page with branding and key metrics."""
        elements = []

        # Use firm colors if available
        firm_primary = study_data.get("firm_primary_color", "#1F4E79")
        firm_secondary = study_data.get("firm_secondary_color", "#2E7D32")
        primary_color = colors.HexColor(firm_primary) if firm_primary else self.PRIMARY_COLOR
        secondary_color = colors.HexColor(firm_secondary) if firm_secondary else self.SECONDARY_COLOR

        # Header bar with decorative line
        header_drawing = Drawing(6.5 * inch, 0.1 * inch)
        header_drawing.add(Line(0, 0, 6.5 * inch, 0, strokeColor=primary_color, strokeWidth=3))
        elements.append(header_drawing)

        elements.append(Spacer(1, 0.5 * inch))

        # Firm logo (if available)
        firm_logo_url = study_data.get("firm_logo_url")
        if firm_logo_url:
            try:
                import base64
                import io as py_io
                # Handle base64 encoded logo
                if firm_logo_url.startswith("data:image"):
                    # Extract base64 data
                    header, data = firm_logo_url.split(",", 1)
                    logo_data = base64.b64decode(data)
                    logo_img = Image(py_io.BytesIO(logo_data), width=1.5*inch, height=1.5*inch)
                    logo_img.hAlign = 'CENTER'
                    elements.append(logo_img)
                    elements.append(Spacer(1, 0.25 * inch))
            except Exception as e:
                logger.warning(f"Failed to add firm logo: {e}")

        # Prepared by section (top of cover)
        prepared_style = ParagraphStyle(
            name='PreparedBy',
            fontSize=10,
            textColor=colors.gray,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        firm_name = study_data.get("firm_name", "Aura Audit AI")
        elements.append(Paragraph(f"Prepared by {firm_name}", prepared_style))

        elements.append(Spacer(1, 1.0 * inch))

        # Main title with styled box
        title_box_style = ParagraphStyle(
            name='TitleBox',
            fontSize=28,
            textColor=primary_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=36
        )
        elements.append(Paragraph(
            "Research &amp; Development<br/>Tax Credit Study",
            title_box_style
        ))

        elements.append(Spacer(1, 0.3 * inch))

        # IRC Section subtitle
        subtitle_style = ParagraphStyle(
            name='Subtitle',
            fontSize=12,
            textColor=colors.gray,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        elements.append(Paragraph("Pursuant to IRC Section 41", subtitle_style))

        elements.append(Spacer(1, 0.75 * inch))

        # Decorative divider
        divider_drawing = Drawing(4 * inch, 0.05 * inch)
        divider_drawing.add(Line(0, 0, 4 * inch, 0, strokeColor=secondary_color, strokeWidth=2))
        elements.append(divider_drawing)

        elements.append(Spacer(1, 0.5 * inch))

        # Entity name (client)
        entity_style = ParagraphStyle(
            name='EntityName',
            fontSize=20,
            textColor=primary_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(study_data.get("entity_name", ""), entity_style))

        elements.append(Spacer(1, 0.15 * inch))

        # Entity type and EIN
        entity_details_style = ParagraphStyle(
            name='EntityDetails',
            fontSize=11,
            textColor=colors.gray,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        entity_type = study_data.get("entity_type", "").replace("_", " ").upper()
        ein = study_data.get("ein", "N/A")
        elements.append(Paragraph(f"{entity_type} | EIN: {ein}", entity_details_style))

        elements.append(Spacer(1, 0.4 * inch))

        # Tax year with period
        year_style = ParagraphStyle(
            name='TaxYear',
            fontSize=14,
            textColor=primary_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        fiscal_start = study_data.get("fiscal_year_start", "")
        fiscal_end = study_data.get("fiscal_year_end", "")
        if fiscal_start and fiscal_end:
            elements.append(Paragraph(f"Tax Year {study_data.get('tax_year', '')}", year_style))
            period_style = ParagraphStyle(
                name='Period',
                fontSize=10,
                textColor=colors.gray,
                alignment=TA_CENTER
            )
            elements.append(Paragraph(f"Period: {fiscal_start} through {fiscal_end}", period_style))
        else:
            elements.append(Paragraph(f"Tax Year {study_data.get('tax_year', '')}", year_style))

        elements.append(Spacer(1, 0.75 * inch))

        # Credit summary box - professional styling
        total_credit = calculation_result.get("total_credits", 0)
        federal_credit = calculation_result.get("federal_credit", 0)
        state_credits = calculation_result.get("total_state_credits", 0)
        total_qre = calculation_result.get("total_qre", 0)
        selected_method = calculation_result.get("selected_method", "ASC").upper()

        # Prominent total credit display
        credit_display_style = ParagraphStyle(
            name='CreditDisplay',
            fontSize=14,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            backColor=secondary_color,
            borderPadding=15
        )
        credit_amount_style = ParagraphStyle(
            name='CreditAmount',
            fontSize=32,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # Create summary table with enhanced styling
        summary_data = [
            ["TOTAL R&D TAX CREDIT", ""],
            ["", f"${total_credit:,.0f}"],
            ["", ""],
            ["Federal Credit", f"${federal_credit:,.0f}"],
            ["State Credits", f"${state_credits:,.0f}"],
            ["Total QRE", f"${total_qre:,.0f}"],
            ["Method Applied", selected_method],
        ]

        summary_table = Table(summary_data, colWidths=[2.75 * inch, 2.25 * inch])
        summary_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.SECONDARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Big credit amount row
            ('BACKGROUND', (0, 1), (-1, 1), self.SECONDARY_COLOR),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 28),
            ('SPAN', (0, 1), (-1, 1)),
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            # Spacer row
            ('BACKGROUND', (0, 2), (-1, 2), self.LIGHT_GRAY),
            ('SPAN', (0, 2), (-1, 2)),
            # Data rows
            ('BACKGROUND', (0, 3), (-1, -1), self.LIGHT_GRAY),
            ('TEXTCOLOR', (0, 3), (0, -1), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (1, 3), (1, -1), colors.black),
            ('FONTNAME', (0, 3), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 3), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 3), (-1, -1), 11),
            ('ALIGN', (0, 3), (0, -1), 'LEFT'),
            ('ALIGN', (1, 3), (1, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 2, self.PRIMARY_COLOR),
            ('LINEBELOW', (0, 2), (-1, 2), 1, self.BORDER_COLOR),
        ]))
        elements.append(summary_table)

        elements.append(Spacer(1, 1 * inch))

        # Footer with status and date
        footer_style = ParagraphStyle(
            name='CoverFooter',
            fontSize=10,
            textColor=colors.gray,
            alignment=TA_CENTER,
            leading=16
        )

        status = "FINAL REPORT" if is_final else "DRAFT - Subject to Review"
        status_color = self.SECONDARY_COLOR if is_final else self.WARNING_COLOR

        status_style = ParagraphStyle(
            name='Status',
            fontSize=12,
            textColor=status_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(status, status_style))
        elements.append(Spacer(1, 0.15 * inch))
        elements.append(Paragraph(
            f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            footer_style
        ))

        # Bottom decorative bar
        elements.append(Spacer(1, 0.5 * inch))
        footer_drawing = Drawing(6.5 * inch, 0.1 * inch)
        footer_drawing.add(Line(0, 0, 6.5 * inch, 0, strokeColor=self.PRIMARY_COLOR, strokeWidth=3))
        elements.append(footer_drawing)

        return elements

    def _build_executive_summary(
        self,
        study_data: Dict,
        calculation_result: Dict,
        narratives: Dict,
        projects: List[Dict]
    ) -> List:
        """Build executive summary section."""
        elements = []

        elements.append(Paragraph("Executive Summary", self.styles['SectionHeading']))

        # AI-generated or custom narrative
        summary_text = narratives.get("executive_summary", "")
        if not summary_text:
            total_credit = calculation_result.get("total_credits", 0)
            total_qre = calculation_result.get("total_qre", 0)
            qualified_projects = len([p for p in projects if p.get("qualification_status") == "qualified"])

            summary_text = f"""
            <b>{study_data.get('entity_name', 'The Company')}</b> has completed a comprehensive analysis of its
            research and development activities for tax year {study_data.get('tax_year', '')}. Based on our
            evaluation of {len(projects)} research projects, {qualified_projects} projects were found to meet
            the requirements of IRC Section 41 for the R&D tax credit.

            The total Qualified Research Expenses (QRE) amount to <b>${total_qre:,.0f}</b>, resulting in
            a total R&D tax credit of <b>${total_credit:,.0f}</b>.

            The credit calculation was performed using the {calculation_result.get('selected_method', 'ASC').upper()}
            method, which provided the most favorable outcome for the taxpayer.
            """

        elements.append(Paragraph(summary_text, self.styles['BodyText']))

        elements.append(Spacer(1, 0.25 * inch))

        # Key metrics table
        elements.append(Paragraph("Key Metrics", self.styles['SubsectionHeading']))

        metrics_data = [
            ["Metric", "Value"],
            ["Total Qualified Research Expenses", f"${calculation_result.get('total_qre', 0):,.0f}"],
            ["Federal R&D Credit", f"${calculation_result.get('federal_credit', 0):,.0f}"],
            ["Total State Credits", f"${calculation_result.get('total_state_credits', 0):,.0f}"],
            ["Total Credits", f"${calculation_result.get('total_credits', 0):,.0f}"],
            ["Credit Method", calculation_result.get('selected_method', 'ASC').upper()],
            ["Qualified Projects", str(len([p for p in projects if p.get("qualification_status") == "qualified"]))],
        ]

        metrics_table = Table(metrics_data, colWidths=[3.5 * inch, 2.5 * inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.LIGHT_GRAY]),
        ]))
        elements.append(metrics_table)

        return elements

    def _build_methodology_section(self, study_data: Dict) -> List:
        """Build methodology section."""
        elements = []

        elements.append(Paragraph("Study Methodology", self.styles['SectionHeading']))

        methodology_text = f"""
        This R&D Tax Credit Study was prepared in accordance with IRC Section 41 and applicable
        Treasury Regulations. The study covers the tax year ending {study_data.get('fiscal_year_end', 'N/A')}.
        """
        elements.append(Paragraph(methodology_text, self.styles['BodyText']))

        # Scope
        elements.append(Paragraph("Scope of Study", self.styles['SubsectionHeading']))
        scope_items = [
            "Identification and documentation of qualified research activities",
            "Evaluation of activities against the Federal 4-part test",
            "Calculation of Qualified Research Expenses (QRE)",
            "Computation of Federal and state R&D tax credits"
        ]
        elements.append(self._create_bullet_list(scope_items))

        # Information sources
        elements.append(Paragraph("Information Sources", self.styles['SubsectionHeading']))
        source_items = [
            "General ledger and trial balance data",
            "Payroll records and W-2 data",
            "Time tracking and project management systems",
            "Employee interviews and questionnaires",
            "Technical documentation and engineering records",
            "Contracts and invoices"
        ]
        elements.append(self._create_bullet_list(source_items))

        # 4-part test
        elements.append(Paragraph("Qualification Methodology", self.styles['SubsectionHeading']))
        test_text = """
        Each research activity was evaluated against the IRC Section 41 four-part test:
        """
        elements.append(Paragraph(test_text, self.styles['BodyText']))

        test_items = [
            "<b>Permitted Purpose (§41(d)(1)(B)(i))</b> - Research must be undertaken for developing new or improved business components",
            "<b>Technological in Nature (§41(d)(1)(B)(ii))</b> - Research must rely on principles of physical/biological sciences, engineering, or computer science",
            "<b>Elimination of Uncertainty (§41(d)(1)(B)(iii))</b> - Research must address uncertainty regarding capability, method, or design",
            "<b>Process of Experimentation (§41(d)(1)(B)(iv))</b> - Research must involve systematic evaluation of alternatives"
        ]
        elements.append(self._create_bullet_list(test_items))

        return elements

    def _build_qualification_analysis(self, projects: List[Dict]) -> List:
        """Build qualification analysis section."""
        elements = []

        elements.append(Paragraph("Qualification Analysis", self.styles['SectionHeading']))

        qualified = [p for p in projects if p.get("qualification_status") == "qualified"]
        partial = [p for p in projects if p.get("qualification_status") == "partially_qualified"]
        not_qualified = [p for p in projects if p.get("qualification_status") == "not_qualified"]

        summary_text = f"""
        A total of <b>{len(projects)}</b> research projects were analyzed for qualification under IRC Section 41.
        Of these, <b>{len(qualified)}</b> projects were found to be fully qualified, <b>{len(partial)}</b>
        partially qualified, and <b>{len(not_qualified)}</b> did not meet the qualification criteria.
        """
        elements.append(Paragraph(summary_text, self.styles['BodyText']))

        elements.append(Spacer(1, 0.25 * inch))

        # Project summary table
        if projects:
            elements.append(Paragraph("Project Summary", self.styles['SubsectionHeading']))

            project_data = [["Project Name", "Status", "4-Part Score", "QRE"]]
            for p in projects[:15]:  # Limit to 15 projects
                status = p.get("qualification_status", "pending").replace("_", " ").title()
                score = p.get("overall_score", 0)
                score_str = f"{score:.0f}%" if isinstance(score, (int, float)) else str(score)
                qre = p.get("total_qre", 0)
                project_data.append([
                    p.get("name", "")[:40],
                    status,
                    score_str,
                    f"${qre:,.0f}" if qre else "-"
                ])

            project_table = Table(project_data, colWidths=[2.5 * inch, 1.5 * inch, 1 * inch, 1.2 * inch])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.LIGHT_GRAY]),
            ]))
            elements.append(project_table)

        return elements

    def _build_qre_schedules(self, qre_summary: Dict, employees: List[Dict]) -> List:
        """Build QRE schedules section."""
        elements = []

        elements.append(Paragraph("Qualified Research Expenses", self.styles['SectionHeading']))

        total_wages = qre_summary.get("total_wages", 0)
        total_supplies = qre_summary.get("total_supplies", 0)
        total_contract = qre_summary.get("total_contract_research", 0)
        total_qre = qre_summary.get("total_qre", total_wages + total_supplies + total_contract)

        summary_text = f"""
        Total Qualified Research Expenses for the tax year amount to <b>${total_qre:,.0f}</b>,
        comprised of wage expenses, supply costs, and contract research payments.
        """
        elements.append(Paragraph(summary_text, self.styles['BodyText']))

        # QRE breakdown table
        elements.append(Paragraph("QRE by Category", self.styles['SubsectionHeading']))

        qre_data = [
            ["Category", "IRC Reference", "Amount", "% of Total"],
            ["Wages", "§41(b)(2)(A)", f"${total_wages:,.0f}", f"{total_wages/total_qre*100:.1f}%" if total_qre else "0%"],
            ["Supplies", "§41(b)(2)(C)", f"${total_supplies:,.0f}", f"{total_supplies/total_qre*100:.1f}%" if total_qre else "0%"],
            ["Contract Research", "§41(b)(3)", f"${total_contract:,.0f}", f"{total_contract/total_qre*100:.1f}%" if total_qre else "0%"],
            ["Total QRE", "", f"${total_qre:,.0f}", "100%"],
        ]

        qre_table = Table(qre_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
        qre_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), self.LIGHT_GRAY),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
        ]))
        elements.append(qre_table)

        # Top employees
        if employees:
            elements.append(Spacer(1, 0.25 * inch))
            elements.append(Paragraph("Top R&D Employees by Qualified Wages", self.styles['SubsectionHeading']))

            sorted_employees = sorted(employees, key=lambda x: x.get("qualified_wages", 0), reverse=True)[:10]

            emp_data = [["Employee", "Title", "Qualified %", "Qualified Wages"]]
            for emp in sorted_employees:
                emp_data.append([
                    emp.get("name", "")[:25],
                    emp.get("title", "")[:20],
                    f"{emp.get('qualified_time_percentage', 0):.0f}%",
                    f"${emp.get('qualified_wages', 0):,.0f}"
                ])

            emp_table = Table(emp_data, colWidths=[2 * inch, 2 * inch, 1 * inch, 1.5 * inch])
            emp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.LIGHT_GRAY]),
            ]))
            elements.append(emp_table)

        return elements

    def _build_federal_calculation(self, calculation_result: Dict) -> List:
        """Build federal calculation section."""
        elements = []

        elements.append(Paragraph("Federal R&D Credit Calculation", self.styles['SectionHeading']))

        regular = calculation_result.get("federal_regular", {})
        asc = calculation_result.get("federal_asc", {})
        selected_method = calculation_result.get("selected_method", "asc")

        intro_text = """
        The Federal R&D credit was calculated using both available methods: the Regular Credit
        method (IRC §41(a)(1)) and the Alternative Simplified Credit (ASC) method (IRC §41(c)(4)).
        """
        elements.append(Paragraph(intro_text, self.styles['BodyText']))

        # Comparison table
        elements.append(Paragraph("Method Comparison", self.styles['SubsectionHeading']))

        comparison_data = [
            ["Item", "Regular Credit", "ASC"],
            ["Total QRE", f"${regular.get('total_qre', 0):,.0f}", f"${asc.get('total_qre', 0):,.0f}"],
            ["Base Amount", f"${regular.get('base_amount', 0):,.0f}", f"${asc.get('base_amount', 0):,.0f}"],
            ["Excess QRE", f"${regular.get('excess_qre', 0):,.0f}", f"${asc.get('excess_qre', 0):,.0f}"],
            ["Credit Rate", "20%", "14%"],
            ["Tentative Credit", f"${regular.get('tentative_credit', 0):,.0f}", f"${asc.get('tentative_credit', 0):,.0f}"],
            ["280C Reduction", f"${regular.get('section_280c_reduction', 0):,.0f}", f"${asc.get('section_280c_reduction', 0):,.0f}"],
            ["Final Credit", f"${regular.get('final_credit', 0):,.0f}", f"${asc.get('final_credit', 0):,.0f}"],
        ]

        comp_table = Table(comparison_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), self.LIGHT_GRAY),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
        ]))
        elements.append(comp_table)

        elements.append(Spacer(1, 0.25 * inch))

        # Recommendation
        rec_style = ParagraphStyle(
            name='Recommendation',
            fontSize=11,
            textColor=self.SECONDARY_COLOR,
            fontName='Helvetica-Bold',
            backColor=self.LIGHT_GRAY,
            borderPadding=10
        )
        elements.append(Paragraph(
            f"Recommended Method: {selected_method.upper()} - "
            f"Final Federal Credit: ${calculation_result.get('federal_credit', 0):,.0f}",
            rec_style
        ))

        return elements

    def _build_state_addenda(self, study_data: Dict, calculation_result: Dict) -> List:
        """Build state credit addenda."""
        elements = []

        elements.append(Paragraph("State R&D Credits", self.styles['SectionHeading']))

        states = study_data.get("states", [])
        state_results = calculation_result.get("state_results", {})

        intro_text = f"""
        In addition to the Federal R&D credit, the company may be eligible for state R&D credits
        in the following {len(states)} state(s): {', '.join(states)}.
        """
        elements.append(Paragraph(intro_text, self.styles['BodyText']))

        if state_results:
            state_data = [["State", "Credit Type", "Credit Rate", "Credit Amount"]]
            for state_code, result in state_results.items():
                state_data.append([
                    result.get("state_name", state_code),
                    result.get("credit_type", "Incremental"),
                    f"{result.get('credit_rate', 0)*100:.1f}%",
                    f"${result.get('final_credit', 0):,.0f}"
                ])

            state_table = Table(state_data, colWidths=[2 * inch, 1.5 * inch, 1.2 * inch, 1.5 * inch])
            state_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
            ]))
            elements.append(state_table)

        return elements

    def _build_project_narratives(self, projects: List[Dict], narratives: Dict) -> List:
        """Build project narratives section."""
        elements = []

        elements.append(Paragraph("Project Qualification Narratives", self.styles['SectionHeading']))

        intro_text = """
        The following narratives describe the qualified research activities and how each project
        satisfies the four-part test under IRC Section 41.
        """
        elements.append(Paragraph(intro_text, self.styles['BodyText']))

        for i, project in enumerate(projects[:10], 1):  # Limit to 10 projects
            elements.append(Paragraph(
                f"{i}. {project.get('name', 'Unnamed Project')}",
                self.styles['SubsectionHeading']
            ))

            narrative = project.get("qualification_narrative", "")
            if not narrative:
                narrative = f"""
                <b>Business Component:</b> {project.get('business_component', 'N/A')}<br/>
                <b>Department:</b> {project.get('department', 'N/A')}<br/>
                <b>Qualification Status:</b> {project.get('qualification_status', 'pending').replace('_', ' ').title()}<br/>
                <b>Overall Score:</b> {project.get('overall_score', 0):.0f}/100<br/><br/>
                {project.get('description', 'No description available.')}
                """

            elements.append(Paragraph(narrative, self.styles['BodyText']))
            elements.append(Spacer(1, 0.15 * inch))

        return elements

    def _build_assumptions_section(self, study_data: Dict) -> List:
        """Build assumptions and limitations section."""
        elements = []

        elements.append(Paragraph("Assumptions and Limitations", self.styles['SectionHeading']))

        # Assumptions
        elements.append(Paragraph("Assumptions", self.styles['SubsectionHeading']))
        assumptions = [
            "All information provided by the taxpayer is accurate and complete.",
            "Time allocation estimates represent management's best estimate of time spent on qualified activities.",
            "Projects classified as qualified research meet all requirements of IRC Section 41.",
            "All research was conducted within the United States.",
            "The taxpayer had no funded research arrangements during the study period."
        ]
        elements.append(self._create_bullet_list(assumptions))

        # Limitations
        elements.append(Paragraph("Limitations", self.styles['SubsectionHeading']))
        limitations = [
            "The conclusions in this study are based on information available at the time of preparation.",
            "Changes in facts, circumstances, or law may affect the conclusions.",
            "The ultimate determination of qualification is subject to IRS review and interpretation.",
            "Time allocations based on estimates are inherently less precise than contemporaneous records.",
            "This study does not constitute legal or accounting advice."
        ]
        elements.append(self._create_bullet_list(limitations))

        # Reliance
        elements.append(Paragraph("Reliance", self.styles['SubsectionHeading']))
        reliance_text = """
        This study was prepared for the exclusive use of the taxpayer named herein and should not
        be relied upon by any third party without the express written consent of the preparer.
        """
        elements.append(Paragraph(reliance_text, self.styles['BodyText']))

        return elements

    def _build_appendix(self, evidence_items: List[Dict]) -> List:
        """Build appendix section."""
        elements = []

        elements.append(Paragraph("Appendix", self.styles['SectionHeading']))

        # IRC citations
        elements.append(Paragraph("A. IRC Section 41 Citations", self.styles['SubsectionHeading']))
        citations = [
            "§41(a) - General Rule",
            "§41(b) - Qualified Research Expenses",
            "§41(c) - Base Amount / Alternative Simplified Credit",
            "§41(d) - Qualified Research Defined",
            "§41(e) - Credit for Certain Payments to Qualified Organizations",
            "§41(f) - Special Rules",
            "§280C(c) - Certain Expenses for Which Credits Are Allowable"
        ]
        elements.append(self._create_bullet_list(citations))

        # Treasury regulations
        elements.append(Paragraph("B. Treasury Regulation Citations", self.styles['SubsectionHeading']))
        regs = [
            "§1.41-2 - Qualified Research Expenses",
            "§1.41-3 - Base Amount",
            "§1.41-4 - Qualified Research",
            "§1.41-5 - Basic Research",
            "§1.41-8 - Alternative Simplified Credit"
        ]
        elements.append(self._create_bullet_list(regs))

        # Document index
        if evidence_items:
            elements.append(Paragraph("C. Document Index", self.styles['SubsectionHeading']))
            doc_data = [["#", "Document", "Type", "Source"]]
            for i, item in enumerate(evidence_items[:30], 1):
                doc_data.append([
                    str(i),
                    item.get("title", "Unknown")[:35],
                    item.get("evidence_type", "N/A"),
                    item.get("source_reference", "N/A")[:20]
                ])

            doc_table = Table(doc_data, colWidths=[0.4 * inch, 2.5 * inch, 1.5 * inch, 1.5 * inch])
            doc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.LIGHT_GRAY]),
            ]))
            elements.append(doc_table)

        return elements

    def _create_bullet_list(self, items: List[str]) -> ListFlowable:
        """Create a bullet list from items."""
        list_items = []
        for item in items:
            list_items.append(ListItem(
                Paragraph(item, self.styles['BodyText']),
                leftIndent=20,
                bulletColor=self.PRIMARY_COLOR
            ))
        return ListFlowable(
            list_items,
            bulletType='bullet',
            start='circle'
        )

    def _format_currency(self, amount) -> str:
        """Format currency value."""
        if isinstance(amount, (int, float, Decimal)):
            return f"${amount:,.0f}"
        return str(amount)
