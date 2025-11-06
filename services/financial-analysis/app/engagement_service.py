"""
Engagement Service for Audit, Review, and Compilation

Provides services for all three types of financial statement engagements
following GAAS (audits) and SSARS (reviews and compilations) standards.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from openai import AsyncOpenAI

from .config import settings
from .models import (
    EngagementType,
    AuditOpinion,
    ReviewConclusion,
    CompilationReport,
    RiskLevel,
)

logger = logging.getLogger(__name__)


class EngagementService:
    """
    Service for managing financial statement engagements.

    Supports:
    - Audit engagements (GAAS) - Reasonable assurance
    - Review engagements (SSARS AR-C 90) - Limited assurance
    - Compilation engagements (SSARS AR-C 80) - No assurance
    """

    def __init__(self):
        """Initialize engagement service."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("Engagement service initialized")

    async def create_engagement(
        self,
        engagement_type: EngagementType,
        company_name: str,
        company_id: str,
        engagement_partner_id: str,
        period_start: datetime,
        period_end: datetime,
        fiscal_year: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new engagement.

        Args:
            engagement_type: Type of engagement (audit/review/compilation)
            company_name: Client company name
            company_id: Company ID
            engagement_partner_id: Partner responsible for engagement
            period_start: Start of period
            period_end: End of period
            fiscal_year: Fiscal year
            **kwargs: Additional engagement parameters

        Returns:
            Engagement details
        """
        # Generate engagement number
        engagement_number = f"{engagement_type.value.upper()}-{fiscal_year}-{company_id[:8]}"

        # Determine required elements based on engagement type
        requirements = self._get_engagement_requirements(engagement_type)

        engagement = {
            "engagement_number": engagement_number,
            "engagement_name": f"{fiscal_year} {company_name} {engagement_type.value.title()}",
            "engagement_type": engagement_type.value,
            "company_id": company_id,
            "company_name": company_name,
            "engagement_partner_id": engagement_partner_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "fiscal_year": fiscal_year,
            "status": "planning",
            "requirements": requirements,
            "created_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Created {engagement_type.value} engagement {engagement_number} for {company_name}"
        )

        return engagement

    def _get_engagement_requirements(
        self, engagement_type: EngagementType
    ) -> Dict[str, Any]:
        """Get required elements for engagement type."""

        if engagement_type == EngagementType.AUDIT:
            return {
                "independence_required": True,
                "engagement_letter_required": True,
                "understanding_of_entity": True,
                "internal_control_understanding": True,
                "risk_assessment_required": True,
                "materiality_required": True,
                "representation_letter_required": True,
                "subsequent_events_review": True,
                "procedures": [
                    "Plan the audit",
                    "Understand entity and environment",
                    "Assess risks of material misstatement",
                    "Design and perform audit procedures",
                    "Obtain audit evidence",
                    "Evaluate audit findings",
                    "Form opinion on financial statements",
                ],
                "deliverables": ["Audit report with opinion", "Management letter"],
                "standards": ["GAAS", "PCAOB (if applicable)", "AICPA"],
            }

        elif engagement_type == EngagementType.REVIEW:
            return {
                "independence_required": True,
                "engagement_letter_required": True,
                "understanding_of_entity": True,
                "internal_control_understanding": False,
                "risk_assessment_required": False,
                "materiality_required": True,  # SSARS 25
                "representation_letter_required": True,
                "subsequent_events_review": True,
                "procedures": [
                    "Obtain engagement letter",
                    "Establish understanding with client",
                    "Understand the entity and industry",
                    "Perform analytical procedures",
                    "Make inquiries of management",
                    "Obtain representation letter",
                    "Review subsequent events",
                    "Form conclusion on financial statements",
                ],
                "deliverables": ["Review report with conclusion"],
                "standards": ["SSARS", "AR-C 90", "AICPA"],
            }

        elif engagement_type == EngagementType.COMPILATION:
            return {
                "independence_required": False,  # But must disclose if not independent
                "engagement_letter_required": True,
                "understanding_of_entity": True,
                "internal_control_understanding": False,
                "risk_assessment_required": False,
                "materiality_required": False,
                "representation_letter_required": False,
                "subsequent_events_review": False,
                "procedures": [
                    "Obtain engagement letter",
                    "Establish understanding with client",
                    "Understand accounting principles and practices",
                    "Read the compiled financial statements",
                    "Consider whether statements are appropriate",
                ],
                "deliverables": ["Compilation report (no assurance)"],
                "standards": ["SSARS", "AR-C 80", "AICPA"],
            }

        return {}

    async def perform_review_engagement(
        self,
        company_name: str,
        financial_statements: Dict[str, Any],
        prior_period_statements: Optional[Dict[str, Any]] = None,
        industry_data: Optional[Dict[str, Any]] = None,
        materiality: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Perform review engagement procedures (AR-C 90).

        Reviews consist primarily of:
        1. Analytical procedures
        2. Inquiries of management

        Args:
            company_name: Client name
            financial_statements: Current period financial statements
            prior_period_statements: Prior period for comparison
            industry_data: Industry benchmarks
            materiality: Overall materiality

        Returns:
            Review results with conclusion
        """
        logger.info(f"Performing review engagement for {company_name}")

        # Step 1: Perform analytical procedures
        analytical_results = await self._perform_analytical_procedures(
            financial_statements=financial_statements,
            prior_period_statements=prior_period_statements,
            industry_data=industry_data,
            materiality=materiality,
        )

        # Step 2: Develop inquiries based on analytical results
        inquiries = await self._develop_review_inquiries(
            analytical_results=analytical_results,
            financial_statements=financial_statements,
        )

        # Step 3: Form conclusion
        conclusion = await self._form_review_conclusion(
            analytical_results=analytical_results,
            inquiry_results=inquiries,
            materiality=materiality,
        )

        return {
            "engagement_type": "review",
            "company_name": company_name,
            "analytical_procedures": analytical_results,
            "inquiries": inquiries,
            "conclusion": conclusion,
            "standards_followed": ["SSARS AR-C 90", "AICPA", "GAAP"],
            "performed_at": datetime.utcnow().isoformat(),
        }

    async def _perform_analytical_procedures(
        self,
        financial_statements: Dict[str, Any],
        prior_period_statements: Optional[Dict[str, Any]],
        industry_data: Optional[Dict[str, Any]],
        materiality: Optional[float],
    ) -> Dict[str, Any]:
        """
        Perform analytical procedures for review.

        Analytical procedures involve:
        - Comparing current to prior period
        - Comparing to budget/forecast
        - Comparing to industry benchmarks
        - Analyzing trends and relationships
        """
        procedures = []

        # Get key figures
        current = financial_statements
        revenue = current.get("revenue", 0)
        net_income = current.get("net_income", 0)
        total_assets = current.get("total_assets", 0)
        total_liabilities = current.get("total_liabilities", 0)
        total_equity = current.get("total_equity", 0)

        # 1. Period-over-period comparison
        if prior_period_statements:
            prior = prior_period_statements
            prior_revenue = prior.get("revenue", 0)
            prior_net_income = prior.get("net_income", 0)

            if prior_revenue > 0:
                revenue_change = ((revenue - prior_revenue) / prior_revenue) * 100
                net_income_change = (
                    ((net_income - prior_net_income) / abs(prior_net_income)) * 100
                    if prior_net_income != 0
                    else 0
                )

                # Set expectation threshold (e.g., 10%)
                threshold = 10.0

                revenue_variance = {
                    "account": "Revenue",
                    "current": revenue,
                    "prior": prior_revenue,
                    "change_percent": revenue_change,
                    "threshold": threshold,
                    "variance_identified": abs(revenue_change) > threshold,
                    "explanation_required": abs(revenue_change) > threshold,
                }

                procedures.append(revenue_variance)

                net_income_variance = {
                    "account": "Net Income",
                    "current": net_income,
                    "prior": prior_net_income,
                    "change_percent": net_income_change,
                    "threshold": threshold,
                    "variance_identified": abs(net_income_change) > threshold,
                    "explanation_required": abs(net_income_change) > threshold,
                }

                procedures.append(net_income_variance)

        # 2. Ratio analysis
        ratios = {}
        if total_assets > 0:
            ratios["return_on_assets"] = (net_income / total_assets) * 100
        if total_equity > 0:
            ratios["return_on_equity"] = (net_income / total_equity) * 100
        if revenue > 0:
            ratios["profit_margin"] = (net_income / revenue) * 100
        if total_equity > 0 and total_liabilities > 0:
            ratios["debt_to_equity"] = total_liabilities / total_equity

        # 3. Reasonableness tests
        reasonableness = []

        # Check if balance sheet balances
        calculated_equity = total_assets - total_liabilities
        equity_difference = abs(total_equity - calculated_equity)

        if equity_difference > 1:  # Allow for rounding
            reasonableness.append({
                "test": "Balance sheet equation",
                "issue": f"Assets - Liabilities ≠ Equity (difference: ${equity_difference:,.2f})",
                "requires_modification": True,
            })

        # Check for negative equity
        if total_equity < 0:
            reasonableness.append({
                "test": "Equity position",
                "issue": "Company has negative equity (deficit)",
                "requires_inquiry": True,
                "going_concern_indicator": True,
            })

        return {
            "procedures_performed": len(procedures),
            "variances_identified": sum(
                1 for p in procedures if p.get("variance_identified")
            ),
            "procedures": procedures,
            "ratio_analysis": ratios,
            "reasonableness_tests": reasonableness,
            "overall_result": "satisfactory"
            if len(reasonableness) == 0
            else "exceptions_noted",
        }

    async def _develop_review_inquiries(
        self, analytical_results: Dict[str, Any], financial_statements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Develop inquiries based on analytical procedure results."""

        inquiries = []

        # Standard inquiries required by AR-C 90
        standard_inquiries = [
            {
                "inquiry_of": "Management",
                "question": "Are you aware of any fraud or suspected fraud affecting the entity?",
                "purpose": "Fraud risk assessment",
                "required": True,
            },
            {
                "inquiry_of": "Management",
                "question": "Are you aware of any significant unusual transactions?",
                "purpose": "Identify unusual items",
                "required": True,
            },
            {
                "inquiry_of": "Management",
                "question": "Have there been any significant changes in the entity's business activities?",
                "purpose": "Understand business changes",
                "required": True,
            },
            {
                "inquiry_of": "Management",
                "question": "Are there any events after the balance sheet date that would require adjustment or disclosure?",
                "purpose": "Subsequent events",
                "required": True,
            },
            {
                "inquiry_of": "Management",
                "question": "Are the financial statements prepared in accordance with the applicable financial reporting framework?",
                "purpose": "GAAP compliance",
                "required": True,
            },
        ]

        inquiries.extend(standard_inquiries)

        # Additional inquiries based on analytical results
        if analytical_results.get("variances_identified", 0) > 0:
            for procedure in analytical_results.get("procedures", []):
                if procedure.get("variance_identified"):
                    inquiries.append({
                        "inquiry_of": "Management",
                        "question": f"What explains the {procedure['change_percent']:.1f}% change in {procedure['account']}?",
                        "purpose": f"Explain variance in {procedure['account']}",
                        "required": True,
                        "triggered_by": "analytical_procedure",
                    })

        # Inquiries based on reasonableness tests
        for test in analytical_results.get("reasonableness_tests", []):
            if test.get("requires_inquiry"):
                inquiries.append({
                    "inquiry_of": "Management",
                    "question": f"Please explain: {test['issue']}",
                    "purpose": test["test"],
                    "required": True,
                    "triggered_by": "reasonableness_test",
                })

        return inquiries

    async def _form_review_conclusion(
        self,
        analytical_results: Dict[str, Any],
        inquiry_results: List[Dict[str, Any]],
        materiality: Optional[float],
    ) -> Dict[str, Any]:
        """
        Form review conclusion based on procedures performed.

        Review conclusion types (AR-C 90):
        - Unmodified: Not aware of material modifications needed
        - Modified: Material modifications are needed
        - Adverse: Departures from framework
        """
        # Analyze results
        exceptions_noted = analytical_results.get("overall_result") == "exceptions_noted"
        variances_count = analytical_results.get("variances_identified", 0)

        # Default to unmodified conclusion
        conclusion_type = ReviewConclusion.UNMODIFIED
        modifications_needed = []

        # Check for material issues
        for test in analytical_results.get("reasonableness_tests", []):
            if test.get("requires_modification"):
                conclusion_type = ReviewConclusion.MODIFIED
                modifications_needed.append({
                    "issue": test["issue"],
                    "materiality": "material",
                    "requires_adjustment": True,
                })

        # Form conclusion text
        if conclusion_type == ReviewConclusion.UNMODIFIED:
            conclusion_text = (
                "Based on our review, we are not aware of any material modifications "
                "that should be made to the accompanying financial statements in order "
                "for them to be in accordance with accounting principles generally "
                "accepted in the United States of America."
            )
        else:
            conclusion_text = (
                "Based on our review, with the exception of the matters described in "
                "the following paragraph, we are not aware of any material modifications "
                "that should be made to the accompanying financial statements in order "
                "for them to be in accordance with accounting principles generally "
                "accepted in the United States of America."
            )

        return {
            "conclusion_type": conclusion_type.value,
            "conclusion_text": conclusion_text,
            "modifications_needed": modifications_needed,
            "basis": {
                "analytical_procedures": analytical_results["procedures_performed"],
                "inquiries_made": len(inquiry_results),
                "exceptions_noted": exceptions_noted,
                "variances_investigated": variances_count,
            },
            "confidence": "limited_assurance",
            "standards_followed": ["SSARS AR-C 90"],
        }

    async def perform_compilation_engagement(
        self,
        company_name: str,
        financial_statements: Dict[str, Any],
        omit_disclosures: bool = False,
    ) -> Dict[str, Any]:
        """
        Perform compilation engagement (AR-C 80).

        Compilations provide NO ASSURANCE. The accountant simply
        presents management's financial information in financial
        statement format.

        Args:
            company_name: Client name
            financial_statements: Financial statement data
            omit_disclosures: Whether to omit substantially all disclosures

        Returns:
            Compilation results
        """
        logger.info(f"Performing compilation engagement for {company_name}")

        # Step 1: Read the financial statements
        reading_results = self._read_compiled_statements(financial_statements)

        # Step 2: Check for obvious material errors
        obvious_errors = self._check_obvious_errors(financial_statements)

        # Step 3: Determine compilation report type
        if omit_disclosures:
            report_type = CompilationReport.OMIT_DISCLOSURES
        else:
            report_type = CompilationReport.WITH_DISCLOSURES

        return {
            "engagement_type": "compilation",
            "company_name": company_name,
            "report_type": report_type.value,
            "disclosures_omitted": omit_disclosures,
            "reading_results": reading_results,
            "obvious_errors": obvious_errors,
            "assurance_provided": None,  # NO ASSURANCE
            "standards_followed": ["SSARS AR-C 80", "AICPA"],
            "performed_at": datetime.utcnow().isoformat(),
        }

    def _read_compiled_statements(
        self, financial_statements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Read compiled statements to ensure they appear appropriate in form."""

        checks = []

        # Check balance sheet equation
        total_assets = financial_statements.get("total_assets", 0)
        total_liabilities = financial_statements.get("total_liabilities", 0)
        total_equity = financial_statements.get("total_equity", 0)

        if abs((total_assets - total_liabilities) - total_equity) > 1:
            checks.append({
                "item": "Balance sheet equation",
                "status": "does_not_balance",
                "note": "Assets - Liabilities ≠ Equity",
            })
        else:
            checks.append({
                "item": "Balance sheet equation",
                "status": "balances",
            })

        # Check for required elements
        required_items = ["revenue", "net_income", "total_assets", "total_equity"]
        missing_items = [
            item for item in required_items if item not in financial_statements
        ]

        if missing_items:
            checks.append({
                "item": "Required financial statement elements",
                "status": "incomplete",
                "missing": missing_items,
            })

        return {
            "checks_performed": len(checks),
            "checks": checks,
            "overall_status": "appears_appropriate"
            if all(c.get("status") != "does_not_balance" for c in checks)
            else "requires_discussion",
        }

    def _check_obvious_errors(
        self, financial_statements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for obvious material errors that require discussion."""

        errors = []

        # Note: AR-C 80 doesn't require verification, but obvious errors
        # should be brought to management's attention

        total_assets = financial_statements.get("total_assets", 0)
        total_liabilities = financial_statements.get("total_liabilities", 0)
        total_equity = financial_statements.get("total_equity", 0)

        # Mathematical error
        if abs((total_assets - total_liabilities) - total_equity) > 1:
            errors.append({
                "type": "mathematical_error",
                "description": "Balance sheet does not balance",
                "severity": "material",
                "requires_discussion": True,
            })

        return errors

    async def generate_engagement_report(
        self,
        engagement_type: EngagementType,
        company_name: str,
        period_end: datetime,
        results: Dict[str, Any],
        accountant_firm: str,
        report_date: datetime,
        is_independent: bool = True,
    ) -> str:
        """
        Generate formal engagement report.

        Args:
            engagement_type: Type of engagement
            company_name: Client company name
            period_end: Period end date
            results: Engagement results
            accountant_firm: Accounting firm name
            report_date: Report date
            is_independent: Independence status

        Returns:
            Formatted report text
        """
        if engagement_type == EngagementType.AUDIT:
            return await self._generate_audit_report(
                company_name, period_end, results, accountant_firm, report_date
            )
        elif engagement_type == EngagementType.REVIEW:
            return self._generate_review_report(
                company_name, period_end, results, accountant_firm, report_date
            )
        elif engagement_type == EngagementType.COMPILATION:
            return self._generate_compilation_report(
                company_name,
                period_end,
                results,
                accountant_firm,
                report_date,
                is_independent,
            )

        return ""

    def _generate_review_report(
        self,
        company_name: str,
        period_end: datetime,
        results: Dict[str, Any],
        accountant_firm: str,
        report_date: datetime,
    ) -> str:
        """Generate review report following AR-C 90."""

        conclusion = results.get("conclusion", {})
        period_end_str = period_end.strftime("%B %d, %Y")
        report_date_str = report_date.strftime("%B %d, %Y")

        report = f"""
INDEPENDENT ACCOUNTANT'S REVIEW REPORT


To the Board of Directors
{company_name}


We have reviewed the accompanying financial statements of {company_name}, which comprise the balance sheet as of {period_end_str}, and the related statements of income, changes in stockholders' equity, and cash flows for the year then ended, and the related notes to the financial statements.


Management's Responsibility for the Financial Statements

Management is responsible for the preparation and fair presentation of these financial statements in accordance with accounting principles generally accepted in the United States of America; this includes the design, implementation, and maintenance of internal control relevant to the preparation and fair presentation of financial statements that are free from material misstatement whether due to fraud or error.


Accountant's Responsibility

Our responsibility is to conduct the review engagement in accordance with Statements on Standards for Accounting and Review Services promulgated by the Accounting and Review Services Committee of the AICPA. Those standards require that we perform procedures to obtain limited assurance as a basis for reporting whether we are aware of any material modifications that should be made to the financial statements for them to be in accordance with accounting principles generally accepted in the United States of America. We believe that the results of our procedures provide a reasonable basis for our conclusion.

A review consists principally of applying analytical procedures and making inquiries of management. A review is substantially less in scope than an audit, the objective of which is the expression of an opinion regarding the financial statements as a whole. Accordingly, we do not express such an opinion.


Accountant's Conclusion

{conclusion.get('conclusion_text', '')}


{accountant_firm}
{report_date_str}
"""

        return report.strip()

    def _generate_compilation_report(
        self,
        company_name: str,
        period_end: datetime,
        results: Dict[str, Any],
        accountant_firm: str,
        report_date: datetime,
        is_independent: bool,
    ) -> str:
        """Generate compilation report following AR-C 80."""

        period_end_str = period_end.strftime("%B %d, %Y")
        report_date_str = report_date.strftime("%B %d, %Y")
        omit_disclosures = results.get("disclosures_omitted", False)

        # Standard compilation report
        report = f"""
ACCOUNTANT'S COMPILATION REPORT


To the Board of Directors
{company_name}


Management's Responsibility for the Financial Statements

Management is responsible for the accompanying financial statements of {company_name}, which comprise the balance sheet as of {period_end_str}, and the related statements of income, changes in stockholders' equity, and cash flows for the year then ended, and the related notes to the financial statements in accordance with accounting principles generally accepted in the United States of America. Management is also responsible for the design, implementation, and maintenance of internal control relevant to the preparation and fair presentation of the financial statements.


Accountant's Responsibility

We have performed a compilation engagement in accordance with Statements on Standards for Accounting and Review Services promulgated by the Accounting and Review Services Committee of the AICPA. We did not audit or review the financial statements nor were we required to perform any procedures to verify the accuracy or completeness of the information provided by management. Accordingly, we do not express an opinion, a conclusion, nor provide any form of assurance on these financial statements.
"""

        # Add disclosure omission paragraph if applicable
        if omit_disclosures:
            report += f"""

Management has elected to omit substantially all of the disclosures ordinarily included in financial statements prepared in accordance with accounting principles generally accepted in the United States of America. If the omitted disclosures were included in the financial statements, they might influence the user's conclusions about the company's financial position, results of operations, and cash flows. Accordingly, the financial statements are not designed for those who are not informed about such matters.
"""

        # Add lack of independence paragraph if applicable
        if not is_independent:
            report += f"""

We are not independent with respect to {company_name}.
"""

        report += f"""

{accountant_firm}
{report_date_str}
"""

        return report.strip()

    async def _generate_audit_report(
        self,
        company_name: str,
        period_end: datetime,
        results: Dict[str, Any],
        accountant_firm: str,
        report_date: datetime,
    ) -> str:
        """Generate audit report (references existing audit functionality)."""

        # This would reference the existing financial analysis AI system
        # for audit engagements
        return "Audit report generation - see financial_analyzer.py"


# Singleton instance
engagement_service = EngagementService()
