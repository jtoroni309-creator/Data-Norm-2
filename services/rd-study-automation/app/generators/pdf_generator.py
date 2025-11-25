"""
PDF Study Report Generator

Generates audit-ready PDF R&D tax credit study reports.
"""

import io
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

logger = logging.getLogger(__name__)


class PDFStudyGenerator:
    """
    Generates comprehensive PDF R&D tax credit study reports.

    Report includes:
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

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.include_watermark = self.config.get("include_watermark", True)
        self.watermark_text = "DRAFT - NOT FOR FILING"

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
        # In production, use reportlab or weasyprint
        # This is a structure representation

        report_structure = self._build_report_structure(
            study_data,
            projects,
            employees,
            qre_summary,
            calculation_result,
            narratives,
            evidence_items,
            is_final
        )

        # Generate PDF content
        pdf_content = self._generate_pdf_content(report_structure, is_final)

        return pdf_content

    def _build_report_structure(
        self,
        study_data: Dict,
        projects: List[Dict],
        employees: List[Dict],
        qre_summary: Dict,
        calculation_result: Dict,
        narratives: Dict,
        evidence_items: List[Dict],
        is_final: bool
    ) -> Dict[str, Any]:
        """Build the report structure."""
        return {
            "metadata": {
                "title": f"R&D Tax Credit Study - {study_data.get('entity_name', 'Unknown')}",
                "tax_year": study_data.get("tax_year"),
                "generated_at": datetime.utcnow().isoformat(),
                "is_final": is_final,
                "version": "1.0"
            },
            "cover_page": {
                "title": "Research and Development Tax Credit Study",
                "subtitle": f"Tax Year {study_data.get('tax_year')}",
                "entity_name": study_data.get("entity_name"),
                "prepared_for": study_data.get("entity_name"),
                "prepared_by": "CPA Firm Name",  # Would come from firm data
                "date": datetime.utcnow().strftime("%B %d, %Y")
            },
            "table_of_contents": self._generate_toc(projects),
            "sections": [
                {
                    "id": "executive_summary",
                    "title": "Executive Summary",
                    "content": narratives.get("executive_summary", ""),
                    "page_break_after": True
                },
                {
                    "id": "methodology",
                    "title": "Study Methodology",
                    "content": self._generate_methodology_section(study_data),
                    "page_break_after": True
                },
                {
                    "id": "qualification_analysis",
                    "title": "Qualification Analysis",
                    "subsections": [
                        {
                            "title": "Federal 4-Part Test Overview",
                            "content": self._generate_four_part_test_overview()
                        },
                        {
                            "title": "Qualified Research Activities",
                            "content": self._generate_activities_summary(projects)
                        }
                    ],
                    "page_break_after": True
                },
                {
                    "id": "evidence_matrix",
                    "title": "Evidence Matrix",
                    "content": self._generate_evidence_matrix(projects, evidence_items),
                    "page_break_after": True
                },
                {
                    "id": "project_narratives",
                    "title": "Project Narratives",
                    "subsections": [
                        {
                            "title": p.get("name", f"Project {i+1}"),
                            "content": p.get("qualification_narrative", "")
                        }
                        for i, p in enumerate(projects)
                    ],
                    "page_break_after": True
                },
                {
                    "id": "employee_narratives",
                    "title": "Employee Role Narratives",
                    "subsections": [
                        {
                            "title": e.get("name", f"Employee {i+1}"),
                            "content": e.get("employee_narrative", "")
                        }
                        for i, e in enumerate(employees[:20])  # Limit for report
                    ],
                    "page_break_after": True
                },
                {
                    "id": "qre_schedules",
                    "title": "Qualified Research Expense Schedules",
                    "content": self._generate_qre_schedule_content(qre_summary),
                    "tables": [
                        self._generate_qre_summary_table(qre_summary),
                        self._generate_wage_qre_table(employees),
                    ],
                    "page_break_after": True
                },
                {
                    "id": "federal_calculation",
                    "title": "Federal Credit Calculation",
                    "content": self._generate_federal_calculation_content(calculation_result),
                    "tables": [
                        self._generate_calculation_table(calculation_result)
                    ],
                    "page_break_after": True
                },
                {
                    "id": "state_addenda",
                    "title": "State Credit Addenda",
                    "content": self._generate_state_addenda(study_data, calculation_result),
                    "page_break_after": True
                },
                {
                    "id": "assumptions",
                    "title": "Assumptions and Limitations",
                    "content": self._generate_assumptions_section(study_data),
                    "page_break_after": True
                },
                {
                    "id": "appendix",
                    "title": "Appendix",
                    "subsections": [
                        {
                            "title": "A. IRC Section 41 Citations",
                            "content": self._generate_irc_citations()
                        },
                        {
                            "title": "B. Treasury Regulation Citations",
                            "content": self._generate_treasury_citations()
                        },
                        {
                            "title": "C. Document Index",
                            "content": self._generate_document_index(evidence_items)
                        }
                    ]
                }
            ]
        }

    def _generate_toc(self, projects: List[Dict]) -> List[Dict]:
        """Generate table of contents."""
        toc = [
            {"title": "Executive Summary", "page": 1},
            {"title": "Study Methodology", "page": 3},
            {"title": "Qualification Analysis", "page": 5},
            {"title": "Evidence Matrix", "page": 8},
            {"title": "Project Narratives", "page": 10},
            {"title": "Employee Role Narratives", "page": 15 + len(projects)},
            {"title": "QRE Schedules", "page": 20 + len(projects)},
            {"title": "Federal Credit Calculation", "page": 25 + len(projects)},
            {"title": "State Credit Addenda", "page": 28 + len(projects)},
            {"title": "Assumptions and Limitations", "page": 30 + len(projects)},
            {"title": "Appendix", "page": 32 + len(projects)},
        ]
        return toc

    def _generate_methodology_section(self, study_data: Dict) -> str:
        """Generate methodology section content."""
        return f"""
This R&D Tax Credit Study was prepared in accordance with IRC Section 41 and applicable
Treasury Regulations. The study covers the tax year ending {study_data.get('fiscal_year_end', 'N/A')}.

**Scope of Study**

The scope of this study includes:
- Identification and documentation of qualified research activities
- Evaluation of activities against the Federal 4-part test
- Calculation of Qualified Research Expenses (QRE)
- Computation of Federal and state R&D tax credits

**Information Sources**

Information for this study was gathered from:
- General ledger and trial balance data
- Payroll records and W-2 data
- Time tracking and project management systems
- Employee interviews and questionnaires
- Technical documentation and engineering records
- Contracts and invoices

**Qualification Methodology**

Each research activity was evaluated against the IRC Section 41 4-part test:
1. Permitted Purpose (§41(d)(1)(B)(i))
2. Technological in Nature (§41(d)(1)(B)(ii))
3. Elimination of Uncertainty (§41(d)(1)(B)(iii))
4. Process of Experimentation (§41(d)(1)(B)(iv))

Activities meeting all four parts of the test were included in the QRE calculation.

**QRE Methodology**

Qualified Research Expenses were calculated for:
- Wages: Based on employee time allocations to qualified research activities
- Supplies: Tangible property consumed in qualified research
- Contract Research: 65% of amounts paid to non-qualified organizations (75% for qualified organizations)

**Credit Calculation**

The Federal R&D credit was calculated using both the Regular Credit method (IRC §41(a)(1))
and the Alternative Simplified Credit method (IRC §41(c)(4)). The method producing the
greater benefit is recommended.
"""

    def _generate_four_part_test_overview(self) -> str:
        """Generate 4-part test overview."""
        return """
**IRC Section 41(d) - Qualified Research**

To qualify for the R&D tax credit under IRC Section 41, research activities must satisfy
all four parts of the following test:

**Part 1: Permitted Purpose (IRC §41(d)(1)(B)(i))**
Research must be undertaken for the purpose of discovering information which is technological
in nature, and the application of which is intended to be useful in the development of a new
or improved business component of the taxpayer.

**Part 2: Technological in Nature (IRC §41(d)(1)(B)(ii))**
The research must fundamentally rely on principles of physical or biological sciences,
engineering, or computer science. This element is satisfied when the information sought
is based on the "hard sciences."

**Part 3: Elimination of Uncertainty (IRC §41(d)(1)(B)(iii))**
The research must be undertaken for the purpose of eliminating uncertainty concerning the
development or improvement of a business component. Uncertainty exists if the information
available to the taxpayer does not establish the capability or method for developing or
improving the business component, or the appropriate design of the business component.

**Part 4: Process of Experimentation (IRC §41(d)(1)(B)(iv))**
The research must involve a process of experimentation for a qualified purpose. This means
substantially all of the research activities must constitute elements of a process of
experimentation for a qualified purpose. A process of experimentation is one in which the
taxpayer evaluates one or more alternatives to achieve a result where the capability or
method of achieving that result, or the appropriate design of that result, is uncertain.
"""

    def _generate_activities_summary(self, projects: List[Dict]) -> str:
        """Generate activities summary."""
        qualified = [p for p in projects if p.get("qualification_status") == "qualified"]
        partial = [p for p in projects if p.get("qualification_status") == "partially_qualified"]

        content = f"""
**Summary of Research Activities**

Total projects analyzed: {len(projects)}
Fully qualified projects: {len(qualified)}
Partially qualified projects: {len(partial)}

**Qualified Research Areas**

The following research areas were identified as meeting the requirements of IRC Section 41:

"""
        for i, p in enumerate(qualified[:10], 1):
            content += f"{i}. {p.get('name', 'Unknown Project')}\n"
            content += f"   - Business Component: {p.get('business_component', 'N/A')}\n"
            content += f"   - Qualification Score: {p.get('overall_score', 0):.0f}/100\n\n"

        return content

    def _generate_evidence_matrix(
        self,
        projects: List[Dict],
        evidence_items: List[Dict]
    ) -> str:
        """Generate evidence matrix content."""
        content = """
**Evidence Matrix**

The following matrix summarizes the evidence supporting qualification for each research project:

| Project | Permitted Purpose | Technological | Uncertainty | Experimentation |
|---------|------------------|---------------|-------------|-----------------|
"""
        for p in projects[:15]:
            pp_score = "✓" if p.get("permitted_purpose_score", 0) >= 70 else "△" if p.get("permitted_purpose_score", 0) >= 50 else "✗"
            tn_score = "✓" if p.get("technological_nature_score", 0) >= 70 else "△" if p.get("technological_nature_score", 0) >= 50 else "✗"
            uc_score = "✓" if p.get("uncertainty_score", 0) >= 70 else "△" if p.get("uncertainty_score", 0) >= 50 else "✗"
            ex_score = "✓" if p.get("experimentation_score", 0) >= 70 else "△" if p.get("experimentation_score", 0) >= 50 else "✗"

            content += f"| {p.get('name', 'Unknown')[:30]} | {pp_score} | {tn_score} | {uc_score} | {ex_score} |\n"

        content += """
Legend: ✓ = Strong evidence (≥70), △ = Moderate evidence (50-69), ✗ = Weak evidence (<50)
"""
        return content

    def _generate_qre_schedule_content(self, qre_summary: Dict) -> str:
        """Generate QRE schedule content."""
        return f"""
**Qualified Research Expense Summary**

Total Qualified Research Expenses for the tax year:

- Wage QRE: ${qre_summary.get('total_wages', 0):,.2f}
- Supply QRE: ${qre_summary.get('total_supplies', 0):,.2f}
- Contract Research QRE: ${qre_summary.get('total_contract_research', 0):,.2f}
- Basic Research QRE: ${qre_summary.get('total_basic_research', 0):,.2f}

**Total QRE: ${qre_summary.get('total_qre', 0):,.2f}**

**Wage QRE Methodology**

Wage QRE was calculated based on W-2 wages paid to employees who performed, directly
supervised, or directly supported qualified research activities. Time allocations were
determined through:
- Analysis of time tracking records
- Employee interviews and questionnaires
- Management estimates based on project involvement

**Supply QRE Methodology**

Supply QRE includes tangible property (other than land or depreciable property) used in
the conduct of qualified research. Supplies were identified through general ledger analysis
and categorized based on their use in qualified research activities.

**Contract Research Methodology**

Contract research expenses include 65% of amounts paid to non-qualified organizations
for qualified research performed on behalf of the taxpayer. Amounts paid to qualified
research organizations are included at 75%.
"""

    def _generate_qre_summary_table(self, qre_summary: Dict) -> Dict:
        """Generate QRE summary table."""
        return {
            "title": "QRE Summary",
            "headers": ["Category", "Gross Amount", "Qualified %", "QRE Amount"],
            "rows": [
                ["Wages", "N/A", "Various", f"${qre_summary.get('total_wages', 0):,.2f}"],
                ["Supplies", "N/A", "100%", f"${qre_summary.get('total_supplies', 0):,.2f}"],
                ["Contract Research", "N/A", "65%/75%", f"${qre_summary.get('total_contract_research', 0):,.2f}"],
                ["Basic Research", "N/A", "100%", f"${qre_summary.get('total_basic_research', 0):,.2f}"],
            ],
            "footer": ["Total QRE", "", "", f"${qre_summary.get('total_qre', 0):,.2f}"]
        }

    def _generate_wage_qre_table(self, employees: List[Dict]) -> Dict:
        """Generate wage QRE detail table."""
        return {
            "title": "Wage QRE Detail",
            "headers": ["Employee", "Title", "Total Wages", "Qualified %", "Wage QRE"],
            "rows": [
                [
                    e.get("name", "Unknown")[:25],
                    e.get("title", "")[:20],
                    f"${e.get('total_wages', 0):,.2f}",
                    f"{e.get('qualified_time_percentage', 0):.0f}%",
                    f"${e.get('qualified_wages', 0):,.2f}"
                ]
                for e in employees[:25]
            ]
        }

    def _generate_federal_calculation_content(self, calculation_result: Dict) -> str:
        """Generate federal calculation content."""
        return f"""
**Federal R&D Credit Calculation**

The Federal R&D credit was calculated using both available methods:

**Regular Credit Method (IRC §41(a)(1))**
Credit = 20% × (Current Year QRE - Base Amount)

Regular Credit: ${calculation_result.get('regular_credit', 0):,.2f}

**Alternative Simplified Credit (IRC §41(c)(4))**
Credit = 14% × (Current Year QRE - 50% of Average QRE for 3 Prior Years)

ASC Credit: ${calculation_result.get('asc_credit', 0):,.2f}

**Recommended Method: {calculation_result.get('selected_method', 'ASC').upper()}**

Based on the calculations above, the {calculation_result.get('selected_method', 'ASC').upper()} method
produces the greater credit and is recommended.

**Final Federal Credit: ${calculation_result.get('federal_credit', 0):,.2f}**

Note: The Section 280C(c) election has been made, resulting in a reduced credit in exchange
for the ability to claim a full deduction for research expenses.
"""

    def _generate_calculation_table(self, calculation_result: Dict) -> Dict:
        """Generate calculation comparison table."""
        return {
            "title": "Credit Calculation Comparison",
            "headers": ["Item", "Regular Credit", "ASC"],
            "rows": [
                ["Total QRE", f"${calculation_result.get('total_qre', 0):,.2f}", f"${calculation_result.get('total_qre', 0):,.2f}"],
                ["Base Amount", f"${calculation_result.get('regular_base', 0):,.2f}", f"${calculation_result.get('asc_base', 0):,.2f}"],
                ["Excess QRE", f"${calculation_result.get('regular_excess', 0):,.2f}", f"${calculation_result.get('asc_excess', 0):,.2f}"],
                ["Credit Rate", "20%", "14%"],
                ["Tentative Credit", f"${calculation_result.get('regular_tentative', 0):,.2f}", f"${calculation_result.get('asc_tentative', 0):,.2f}"],
                ["280C Reduction", f"${calculation_result.get('regular_280c', 0):,.2f}", f"${calculation_result.get('asc_280c', 0):,.2f}"],
                ["Final Credit", f"${calculation_result.get('regular_credit', 0):,.2f}", f"${calculation_result.get('asc_credit', 0):,.2f}"],
            ]
        }

    def _generate_state_addenda(self, study_data: Dict, calculation_result: Dict) -> str:
        """Generate state credit addenda."""
        states = study_data.get("states", [])
        state_results = calculation_result.get("state_results", {})

        if not states:
            return "No state R&D credits were calculated for this study."

        content = "**State R&D Credit Summary**\n\n"

        for state in states:
            state_data = state_results.get(state, {})
            content += f"**{state}**\n"
            content += f"- State Credit: ${state_data.get('final_credit', 0):,.2f}\n"
            content += f"- Credit Type: {state_data.get('credit_type', 'N/A')}\n"
            content += f"- Carryforward: {state_data.get('carryforward_years', 'N/A')} years\n\n"

        return content

    def _generate_assumptions_section(self, study_data: Dict) -> str:
        """Generate assumptions and limitations section."""
        return """
**Assumptions**

The following assumptions were made in preparing this study:

1. All information provided by the taxpayer is accurate and complete.
2. Time allocation estimates represent management's best estimate of time spent on qualified activities.
3. Projects classified as qualified research meet all requirements of IRC Section 41.
4. All research was conducted within the United States.
5. The taxpayer had no funded research arrangements during the study period.

**Limitations**

This study is subject to the following limitations:

1. The conclusions in this study are based on information available at the time of preparation.
2. Changes in facts, circumstances, or law may affect the conclusions.
3. The ultimate determination of qualification is subject to IRS review and interpretation.
4. Time allocations based on estimates are inherently less precise than contemporaneous records.
5. This study does not constitute legal or accounting advice.

**Reliance**

This study was prepared for the exclusive use of the taxpayer named herein and should not
be relied upon by any third party without the express written consent of the preparer.
"""

    def _generate_irc_citations(self) -> str:
        """Generate IRC citation appendix."""
        return """
**IRC Section 41 - Credit for Increasing Research Activities**

- §41(a) - General Rule
- §41(b) - Qualified Research Expenses
- §41(c) - Base Amount / Alternative Simplified Credit
- §41(d) - Qualified Research Defined
- §41(e) - Credit Allowable with Respect to Certain Payments to Qualified Organizations
- §41(f) - Special Rules
- §41(h) - Termination

**IRC Section 280C - Certain Expenses for Which Credits Are Allowable**

- §280C(c) - Credit for Increasing Research Activities
"""

    def _generate_treasury_citations(self) -> str:
        """Generate Treasury Regulation citations."""
        return """
**Treasury Regulation §1.41-1 through §1.41-9**

- §1.41-2 - Qualified Research Expenses
- §1.41-3 - Base Amount for Taxable Years Beginning After December 31, 1989
- §1.41-4 - Qualified Research for Expenditures Paid or Incurred in Taxable Years Ending After December 31, 2003
- §1.41-5 - Basic Research for Taxable Years Beginning After December 31, 1986
- §1.41-6 - Aggregation of Expenditures
- §1.41-8 - Alternative Simplified Credit
"""

    def _generate_document_index(self, evidence_items: List[Dict]) -> str:
        """Generate document index."""
        content = "**Document Index**\n\n"

        for i, e in enumerate(evidence_items[:50], 1):
            content += f"{i}. {e.get('title', 'Unknown Document')}\n"
            content += f"   Type: {e.get('evidence_type', 'N/A')}\n"
            content += f"   Source: {e.get('source_reference', 'N/A')}\n\n"

        return content

    def _generate_pdf_content(self, report_structure: Dict, is_final: bool) -> bytes:
        """
        Generate actual PDF bytes.

        In production, this would use reportlab or weasyprint.
        """
        # Placeholder - returns empty PDF structure
        # In production, implement with reportlab:
        #
        # from reportlab.lib.pagesizes import letter
        # from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        # from reportlab.lib.styles import getSampleStyleSheet
        #
        # buffer = io.BytesIO()
        # doc = SimpleDocTemplate(buffer, pagesize=letter)
        # story = []
        # styles = getSampleStyleSheet()
        # ...build PDF...
        # doc.build(story)
        # return buffer.getvalue()

        import json
        return json.dumps(report_structure, indent=2, default=str).encode("utf-8")
