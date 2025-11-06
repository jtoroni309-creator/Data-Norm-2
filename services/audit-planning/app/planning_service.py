"""
Audit Planning Service

Provides audit planning and risk assessment functionality including:
- Materiality calculations per PCAOB standards
- Risk assessments (inherent, control, detection)
- Audit program generation
- Preliminary analytical procedures
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    AccountType,
    AssertionType,
    AuditArea,
    AuditPlan,
    ControlEffectiveness,
    FraudRiskFactor,
    PreliminaryAnalytics,
    RiskAssessment,
    RiskLevel,
    RiskMatrix,
    RiskType,
)

logger = logging.getLogger(__name__)


class MaterialityCalculator:
    """
    Calculate materiality benchmarks per PCAOB and AICPA standards.

    Typical benchmarks:
    - 0.5-1% of total assets (asset-based entities)
    - 0.5-1% of total revenue (revenue-based entities)
    - 5% of pre-tax income (income-based entities, if stable)
    - 1-2% of equity (if negative or volatile income)
    """

    @staticmethod
    def calculate_materiality(
        total_assets: Decimal,
        total_revenue: Decimal,
        pretax_income: Decimal,
        total_equity: Decimal,
        entity_type: str = "public"  # "public" or "private"
    ) -> Dict[str, Decimal]:
        """
        Calculate overall materiality using multiple benchmarks.

        Returns dictionary with:
        - overall_materiality: Recommended planning materiality
        - performance_materiality: Typically 65% of overall
        - trivial_threshold: Typically 3-5% of overall
        - benchmark_used: Which benchmark was selected
        - all_benchmarks: All calculated benchmarks for comparison
        """
        benchmarks = {}

        # Asset-based calculation
        if total_assets > 0:
            benchmarks["total_assets_0.5%"] = total_assets * Decimal("0.005")
            benchmarks["total_assets_1.0%"] = total_assets * Decimal("0.01")

        # Revenue-based calculation
        if total_revenue > 0:
            benchmarks["total_revenue_0.5%"] = total_revenue * Decimal("0.005")
            benchmarks["total_revenue_1.0%"] = total_revenue * Decimal("0.01")

        # Income-based calculation (if stable and positive)
        if pretax_income > 0:
            benchmarks["pretax_income_5%"] = pretax_income * Decimal("0.05")
            # Check volatility - if income is > 20% of revenue, consider stable
            if total_revenue > 0 and (pretax_income / total_revenue) > Decimal("0.20"):
                benchmarks["pretax_income_3%"] = pretax_income * Decimal("0.03")

        # Equity-based calculation
        if total_equity > 0:
            benchmarks["total_equity_1%"] = total_equity * Decimal("0.01")
            benchmarks["total_equity_2%"] = total_equity * Decimal("0.02")

        # Select most appropriate benchmark
        # Priority: Income (if stable) > Revenue > Assets > Equity
        benchmark_used = "total_assets_1.0%"
        overall_materiality = benchmarks.get("total_assets_1.0%", Decimal("100000"))

        if pretax_income > 0 and "pretax_income_5%" in benchmarks:
            benchmark_used = "pretax_income_5%"
            overall_materiality = benchmarks["pretax_income_5%"]
        elif total_revenue > 0:
            benchmark_used = "total_revenue_0.5%"
            overall_materiality = benchmarks["total_revenue_0.5%"]
        elif total_assets > 0:
            benchmark_used = "total_assets_1.0%"
            overall_materiality = benchmarks["total_assets_1.0%"]
        elif total_equity > 0:
            benchmark_used = "total_equity_1%"
            overall_materiality = benchmarks["total_equity_1%"]

        # Adjust for entity type (private companies often use lower percentages)
        if entity_type == "private":
            overall_materiality = overall_materiality * Decimal("0.80")

        # Calculate performance materiality (typically 50-75%, we use 65%)
        performance_materiality = overall_materiality * Decimal("0.65")

        # Calculate trivial threshold (typically 3-5%, we use 4%)
        trivial_threshold = overall_materiality * Decimal("0.04")

        return {
            "overall_materiality": round(overall_materiality, 2),
            "performance_materiality": round(performance_materiality, 2),
            "trivial_threshold": round(trivial_threshold, 2),
            "benchmark_used": benchmark_used,
            "all_benchmarks": {k: round(v, 2) for k, v in benchmarks.items()},
        }


class RiskAssessor:
    """
    Assess audit risks and determine appropriate audit response.

    Implements PCAOB AS 2110 risk assessment requirements.
    """

    # Risk matrix: Maps (Inherent Risk, Control Risk) → (RMM, Detection Risk, Sample Size Multiplier)
    RISK_MATRIX = {
        (RiskLevel.LOW, RiskLevel.LOW): (RiskLevel.LOW, RiskLevel.MODERATE, Decimal("0.7")),
        (RiskLevel.LOW, RiskLevel.MODERATE): (RiskLevel.LOW, RiskLevel.MODERATE, Decimal("0.8")),
        (RiskLevel.LOW, RiskLevel.HIGH): (RiskLevel.MODERATE, RiskLevel.MODERATE, Decimal("1.0")),
        (RiskLevel.LOW, RiskLevel.SIGNIFICANT): (RiskLevel.MODERATE, RiskLevel.LOW, Decimal("1.2")),
        (RiskLevel.MODERATE, RiskLevel.LOW): (RiskLevel.LOW, RiskLevel.MODERATE, Decimal("0.8")),
        (RiskLevel.MODERATE, RiskLevel.MODERATE): (RiskLevel.MODERATE, RiskLevel.MODERATE, Decimal("1.0")),
        (RiskLevel.MODERATE, RiskLevel.HIGH): (RiskLevel.HIGH, RiskLevel.LOW, Decimal("1.3")),
        (RiskLevel.MODERATE, RiskLevel.SIGNIFICANT): (RiskLevel.SIGNIFICANT, RiskLevel.LOW, Decimal("1.5")),
        (RiskLevel.HIGH, RiskLevel.LOW): (RiskLevel.MODERATE, RiskLevel.MODERATE, Decimal("1.0")),
        (RiskLevel.HIGH, RiskLevel.MODERATE): (RiskLevel.HIGH, RiskLevel.LOW, Decimal("1.3")),
        (RiskLevel.HIGH, RiskLevel.HIGH): (RiskLevel.SIGNIFICANT, RiskLevel.LOW, Decimal("1.5")),
        (RiskLevel.HIGH, RiskLevel.SIGNIFICANT): (RiskLevel.SIGNIFICANT, RiskLevel.LOW, Decimal("2.0")),
        (RiskLevel.SIGNIFICANT, RiskLevel.LOW): (RiskLevel.HIGH, RiskLevel.LOW, Decimal("1.3")),
        (RiskLevel.SIGNIFICANT, RiskLevel.MODERATE): (RiskLevel.SIGNIFICANT, RiskLevel.LOW, Decimal("1.5")),
        (RiskLevel.SIGNIFICANT, RiskLevel.HIGH): (RiskLevel.SIGNIFICANT, RiskLevel.LOW, Decimal("2.0")),
        (RiskLevel.SIGNIFICANT, RiskLevel.SIGNIFICANT): (RiskLevel.SIGNIFICANT, RiskLevel.LOW, Decimal("2.5")),
    }

    @classmethod
    def assess_combined_risk(
        cls,
        inherent_risk: RiskLevel,
        control_risk: RiskLevel,
    ) -> Tuple[RiskLevel, RiskLevel, Decimal]:
        """
        Determine risk of material misstatement, detection risk, and sample size multiplier.

        Returns:
            Tuple of (RMM, Detection Risk, Sample Size Multiplier)
        """
        return cls.RISK_MATRIX.get(
            (inherent_risk, control_risk),
            (RiskLevel.MODERATE, RiskLevel.MODERATE, Decimal("1.0"))
        )

    @staticmethod
    def identify_fraud_risk_factors(
        industry: str,
        financial_ratios: Dict[str, Decimal],
        management_changes: bool,
        significant_transactions: bool,
        complex_structure: bool,
    ) -> List[Dict[str, str]]:
        """
        Identify fraud risk factors based on AS 2401.

        Returns list of fraud risk factors categorized by fraud triangle.
        """
        risk_factors = []

        # Incentive/Pressure factors
        if financial_ratios.get("current_ratio", Decimal("2.0")) < Decimal("1.0"):
            risk_factors.append({
                "category": "incentive",
                "factor": "Liquidity pressure",
                "description": "Current ratio below 1.0 indicates potential liquidity issues"
            })

        if financial_ratios.get("debt_to_equity", Decimal("0.5")) > Decimal("2.0"):
            risk_factors.append({
                "category": "incentive",
                "factor": "Debt covenant pressure",
                "description": "High debt-to-equity ratio may indicate covenant compliance pressure"
            })

        # Opportunity factors
        if management_changes:
            risk_factors.append({
                "category": "opportunity",
                "factor": "Management changes",
                "description": "Significant management changes may indicate control weaknesses"
            })

        if complex_structure:
            risk_factors.append({
                "category": "opportunity",
                "factor": "Complex structure",
                "description": "Complex organizational structure provides opportunities for manipulation"
            })

        if significant_transactions:
            risk_factors.append({
                "category": "opportunity",
                "factor": "Significant unusual transactions",
                "description": "Significant or unusual transactions near year-end"
            })

        # Rationalization factors (harder to detect, often based on attitude)
        if financial_ratios.get("roe", Decimal("0.1")) < 0:
            risk_factors.append({
                "category": "rationalization",
                "factor": "Poor performance",
                "description": "Negative ROE may create pressure to manipulate results"
            })

        return risk_factors


class AuditProgramGenerator:
    """
    Generate audit programs based on risk assessments.

    Implements AS 2301 audit response to assessed risks.
    """

    # Standard procedures by assertion and account type
    PROCEDURES_TEMPLATES = {
        (AccountType.ASSET, AssertionType.EXISTENCE): [
            "Confirm account balances with third parties",
            "Physically inspect assets",
            "Review supporting documentation",
            "Test cutoff procedures",
        ],
        (AccountType.ASSET, AssertionType.COMPLETENESS): [
            "Analyze suspense accounts",
            "Review subsequent period transactions",
            "Test completeness of additions",
            "Perform analytical procedures",
        ],
        (AccountType.ASSET, AssertionType.VALUATION_ALLOCATION): [
            "Test impairment assessments",
            "Review depreciation calculations",
            "Evaluate fair value measurements",
            "Test allowance for uncollectible amounts",
        ],
        (AccountType.LIABILITY, AssertionType.COMPLETENESS): [
            "Search for unrecorded liabilities",
            "Review subsequent payments",
            "Confirm balances with creditors",
            "Analyze expense accounts for understatement",
        ],
        (AccountType.REVENUE, AssertionType.OCCURRENCE): [
            "Vouch revenue transactions to supporting documentation",
            "Confirm revenue with customers",
            "Test revenue recognition criteria",
            "Analyze unusual or significant transactions",
        ],
        (AccountType.EXPENSE, AssertionType.COMPLETENESS): [
            "Perform analytical procedures for reasonableness",
            "Test accruals and provisions",
            "Review subsequent period payments",
            "Analyze expense trends",
        ],
    }

    @classmethod
    def generate_procedures(
        cls,
        account_type: AccountType,
        assertion: AssertionType,
        risk_level: RiskLevel,
        balance: Decimal,
        materiality: Decimal,
    ) -> List[Dict[str, any]]:
        """
        Generate audit procedures based on risk and account type.

        Returns list of procedures with nature, timing, and extent details.
        """
        # Get base procedures from template
        base_procedures = cls.PROCEDURES_TEMPLATES.get(
            (account_type, assertion),
            ["Perform detailed testing of transactions and balances"]
        )

        procedures = []
        for i, proc in enumerate(base_procedures):
            # Determine extent (sample size guidance)
            if risk_level == RiskLevel.LOW:
                extent = "minimal"
                sample_guidance = "10-15 items or 25% of population"
            elif risk_level == RiskLevel.MODERATE:
                extent = "moderate"
                sample_guidance = "20-30 items or 50% of population"
            elif risk_level == RiskLevel.HIGH:
                extent = "extensive"
                sample_guidance = "40-60 items or 75% of population"
            else:  # SIGNIFICANT
                extent = "very_extensive"
                sample_guidance = "60+ items or 100% if material population"

            # Determine timing
            if risk_level in [RiskLevel.HIGH, RiskLevel.SIGNIFICANT]:
                timing = "year_end"  # Test at year-end for high risk
            else:
                timing = "interim_or_year_end"  # Can test at interim for lower risk

            procedures.append({
                "sequence": i + 1,
                "procedure": proc,
                "nature": "substantive",  # vs. "control" testing
                "timing": timing,
                "extent": extent,
                "sample_size_guidance": sample_guidance,
                "is_material": balance > materiality,
                "risk_responsive": risk_level in [RiskLevel.HIGH, RiskLevel.SIGNIFICANT],
            })

        # Add unpredictable procedures for fraud risk
        if risk_level == RiskLevel.SIGNIFICANT:
            procedures.append({
                "sequence": len(procedures) + 1,
                "procedure": "Perform unpredictable audit procedures",
                "nature": "substantive",
                "timing": "year_end",
                "extent": "as_needed",
                "sample_size_guidance": "Based on auditor judgment",
                "is_material": True,
                "risk_responsive": True,
                "fraud_procedure": True,
            })

        return procedures


class AuditPlanningService:
    """
    Main service for audit planning and risk assessment.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.materiality_calculator = MaterialityCalculator()
        self.risk_assessor = RiskAssessor()
        self.program_generator = AuditProgramGenerator()

    async def create_audit_plan(
        self,
        engagement_id: UUID,
        tenant_id: UUID,
        planned_by_id: UUID,
        financial_data: Dict[str, Decimal],
        entity_type: str = "public",
    ) -> AuditPlan:
        """
        Create a comprehensive audit plan with materiality and risk assessments.

        Args:
            engagement_id: Engagement this plan is for
            tenant_id: CPA firm tenant ID
            planned_by_id: User creating the plan
            financial_data: Dictionary with total_assets, total_revenue, pretax_income, total_equity
            entity_type: "public" or "private"

        Returns:
            Created AuditPlan with materiality calculations
        """
        # Calculate materiality
        materiality = self.materiality_calculator.calculate_materiality(
            total_assets=financial_data.get("total_assets", Decimal("0")),
            total_revenue=financial_data.get("total_revenue", Decimal("0")),
            pretax_income=financial_data.get("pretax_income", Decimal("0")),
            total_equity=financial_data.get("total_equity", Decimal("0")),
            entity_type=entity_type,
        )

        # Create audit plan
        audit_plan = AuditPlan(
            engagement_id=engagement_id,
            tenant_id=tenant_id,
            planned_by_id=planned_by_id,
            planning_date=datetime.utcnow(),
            overall_materiality=materiality["overall_materiality"],
            performance_materiality=materiality["performance_materiality"],
            trivial_threshold=materiality["trivial_threshold"],
            materiality_basis=materiality["benchmark_used"],
            overall_engagement_risk=RiskLevel.MODERATE,  # Initial assessment
        )

        self.db.add(audit_plan)
        await self.db.commit()
        await self.db.refresh(audit_plan)

        logger.info(f"Created audit plan {audit_plan.id} for engagement {engagement_id}")
        return audit_plan

    async def assess_account_risk(
        self,
        audit_plan_id: UUID,
        tenant_id: UUID,
        assessed_by_id: UUID,
        account_name: str,
        account_type: AccountType,
        account_balance: Decimal,
        assertion: AssertionType,
        inherent_risk: RiskLevel,
        control_effectiveness: ControlEffectiveness,
    ) -> RiskAssessment:
        """
        Perform risk assessment for specific account/assertion combination.

        Determines control risk based on control effectiveness, then calculates
        risk of material misstatement and generates audit response.

        Args:
            audit_plan_id: Audit plan this assessment belongs to
            tenant_id: CPA firm tenant ID
            assessed_by_id: User performing assessment
            account_name: Account being assessed
            account_type: Type of account (asset, liability, etc.)
            account_balance: Current balance
            assertion: Financial statement assertion being assessed
            inherent_risk: Assessed inherent risk
            control_effectiveness: Assessment of internal controls

        Returns:
            RiskAssessment with audit response
        """
        # Map control effectiveness to control risk
        control_risk_map = {
            ControlEffectiveness.EFFECTIVE: RiskLevel.LOW,
            ControlEffectiveness.PARTIALLY_EFFECTIVE: RiskLevel.MODERATE,
            ControlEffectiveness.INEFFECTIVE: RiskLevel.HIGH,
            ControlEffectiveness.NOT_TESTED: RiskLevel.HIGH,  # Assume high if not tested
        }
        control_risk = control_risk_map[control_effectiveness]

        # Calculate combined risk
        rmm, detection_risk, sample_multiplier = self.risk_assessor.assess_combined_risk(
            inherent_risk, control_risk
        )

        # Determine if significant risk (AS 2110.71)
        significant_risk = rmm == RiskLevel.SIGNIFICANT

        # Get audit plan for materiality
        result = await self.db.execute(
            select(AuditPlan).where(AuditPlan.id == audit_plan_id)
        )
        audit_plan = result.scalar_one()

        # Generate procedures
        procedures = self.program_generator.generate_procedures(
            account_type=account_type,
            assertion=assertion,
            risk_level=rmm,
            balance=account_balance,
            materiality=audit_plan.performance_materiality,
        )

        # Create risk assessment
        risk_assessment = RiskAssessment(
            audit_plan_id=audit_plan_id,
            tenant_id=tenant_id,
            assessed_by_id=assessed_by_id,
            account_name=account_name,
            account_type=account_type,
            account_balance=account_balance,
            assertion=assertion,
            inherent_risk=inherent_risk,
            control_risk=control_risk,
            detection_risk=detection_risk,
            risk_of_material_misstatement=rmm,
            significant_risk=significant_risk,
            control_effectiveness=control_effectiveness,
            control_testing_required=(control_risk != RiskLevel.HIGH),
            planned_procedures=procedures,
            testing_approach="substantive",  # Default approach
        )

        self.db.add(risk_assessment)
        await self.db.commit()
        await self.db.refresh(risk_assessment)

        logger.info(f"Created risk assessment for {account_name} - {assertion.value}")
        return risk_assessment

    async def perform_preliminary_analytics(
        self,
        audit_plan_id: UUID,
        tenant_id: UUID,
        performed_by_id: UUID,
        account_name: str,
        current_year_value: Decimal,
        prior_year_value: Decimal,
        expected_value: Optional[Decimal] = None,
        threshold_percentage: Decimal = Decimal("10.0"),  # 10% default threshold
    ) -> PreliminaryAnalytics:
        """
        Perform preliminary analytical procedures.

        Compares current year to prior year and expected values,
        identifies unusual fluctuations that require investigation.

        Args:
            audit_plan_id: Audit plan this analysis belongs to
            tenant_id: CPA firm tenant ID
            performed_by_id: User performing analysis
            account_name: Account being analyzed
            current_year_value: Current year balance
            prior_year_value: Prior year balance
            expected_value: Expected value (if calculated)
            threshold_percentage: Threshold for investigation (default 10%)

        Returns:
            PreliminaryAnalytics with results
        """
        # Calculate differences
        year_over_year_diff = current_year_value - prior_year_value
        year_over_year_pct = (
            (year_over_year_diff / prior_year_value * 100)
            if prior_year_value != 0
            else Decimal("0")
        )

        # Check against expected value if provided
        expected_diff = None
        expected_diff_pct = None
        if expected_value:
            expected_diff = current_year_value - expected_value
            expected_diff_pct = (
                (expected_diff / expected_value * 100)
                if expected_value != 0
                else Decimal("0")
            )

        # Determine if exceeds threshold
        exceeds_threshold = abs(year_over_year_pct) > threshold_percentage
        if expected_value:
            exceeds_threshold = exceeds_threshold or abs(expected_diff_pct) > threshold_percentage

        analytics = PreliminaryAnalytics(
            audit_plan_id=audit_plan_id,
            tenant_id=tenant_id,
            performed_by_id=performed_by_id,
            analysis_name=f"Preliminary Analysis - {account_name}",
            account_name=account_name,
            analysis_type="trend",
            current_year_value=current_year_value,
            prior_year_value=prior_year_value,
            expected_value=expected_value,
            difference=year_over_year_diff,
            difference_percentage=year_over_year_pct,
            threshold_percentage=threshold_percentage,
            exceeds_threshold=exceeds_threshold,
            requires_investigation=exceeds_threshold,
        )

        self.db.add(analytics)
        await self.db.commit()
        await self.db.refresh(analytics)

        logger.info(f"Performed preliminary analytics for {account_name}")
        return analytics
