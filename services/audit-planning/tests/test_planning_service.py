"""
Comprehensive Test Suite for Audit Planning Service

Tests materiality calculations, risk assessments, and audit program generation.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from app.planning_service import (
    MaterialityCalculator,
    RiskAssessor,
    AuditProgramGenerator,
    AuditPlanningService,
)
from app.models import (
    AccountType,
    AssertionType,
    ControlEffectiveness,
    RiskLevel,
)


# ============================================================================
# MATERIALITY CALCULATOR TESTS
# ============================================================================

class TestMaterialityCalculator:
    """Test materiality calculation logic"""

    def test_asset_based_materiality(self):
        """Test materiality calculation using total assets benchmark"""
        calc = MaterialityCalculator()

        result = calc.calculate_materiality(
            total_assets=Decimal("10000000"),  # $10M
            total_revenue=Decimal("0"),
            pretax_income=Decimal("0"),
            total_equity=Decimal("0"),
            entity_type="public"
        )

        # Should use 1% of assets = $100,000
        assert result["overall_materiality"] == Decimal("100000.00")
        assert result["performance_materiality"] == Decimal("65000.00")  # 65%
        assert result["trivial_threshold"] == Decimal("4000.00")  # 4%
        assert result["benchmark_used"] == "total_assets_1.0%"

    def test_revenue_based_materiality(self):
        """Test materiality using revenue benchmark"""
        calc = MaterialityCalculator()

        result = calc.calculate_materiality(
            total_assets=Decimal("10000000"),
            total_revenue=Decimal("5000000"),  # $5M revenue
            pretax_income=Decimal("0"),
            total_equity=Decimal("0"),
            entity_type="public"
        )

        # Should prefer revenue benchmark: 0.5% = $25,000
        assert result["overall_materiality"] == Decimal("25000.00")
        assert result["benchmark_used"] == "total_revenue_0.5%"

    def test_income_based_materiality(self):
        """Test materiality using pre-tax income benchmark"""
        calc = MaterialityCalculator()

        result = calc.calculate_materiality(
            total_assets=Decimal("10000000"),
            total_revenue=Decimal("5000000"),
            pretax_income=Decimal("1500000"),  # $1.5M income (30% margin - stable)
            total_equity=Decimal("3000000"),
            entity_type="public"
        )

        # Should prefer income benchmark: 5% = $75,000
        assert result["overall_materiality"] == Decimal("75000.00")
        assert result["benchmark_used"] == "pretax_income_5%"

    def test_private_company_adjustment(self):
        """Test that private companies get 80% adjustment"""
        calc = MaterialityCalculator()

        public_result = calc.calculate_materiality(
            total_assets=Decimal("10000000"),
            total_revenue=Decimal("0"),
            pretax_income=Decimal("0"),
            total_equity=Decimal("0"),
            entity_type="public"
        )

        private_result = calc.calculate_materiality(
            total_assets=Decimal("10000000"),
            total_revenue=Decimal("0"),
            pretax_income=Decimal("0"),
            total_equity=Decimal("0"),
            entity_type="private"
        )

        # Private should be 80% of public
        assert private_result["overall_materiality"] == public_result["overall_materiality"] * Decimal("0.80")

    def test_performance_materiality_65_percent(self):
        """Test that performance materiality is 65% of overall"""
        calc = MaterialityCalculator()

        result = calc.calculate_materiality(
            total_assets=Decimal("10000000"),
            total_revenue=Decimal("0"),
            pretax_income=Decimal("0"),
            total_equity=Decimal("0"),
            entity_type="public"
        )

        expected_pm = result["overall_materiality"] * Decimal("0.65")
        assert result["performance_materiality"] == expected_pm

    def test_trivial_threshold_4_percent(self):
        """Test that trivial threshold is 4% of overall"""
        calc = MaterialityCalculator()

        result = calc.calculate_materiality(
            total_assets=Decimal("10000000"),
            total_revenue=Decimal("0"),
            pretax_income=Decimal("0"),
            total_equity=Decimal("0"),
            entity_type="public"
        )

        expected_trivial = result["overall_materiality"] * Decimal("0.04")
        assert result["trivial_threshold"] == expected_trivial

    def test_all_benchmarks_returned(self):
        """Test that all calculated benchmarks are returned"""
        calc = MaterialityCalculator()

        result = calc.calculate_materiality(
            total_assets=Decimal("10000000"),
            total_revenue=Decimal("5000000"),
            pretax_income=Decimal("1000000"),
            total_equity=Decimal("3000000"),
            entity_type="public"
        )

        assert "all_benchmarks" in result
        assert "total_assets_0.5%" in result["all_benchmarks"]
        assert "total_assets_1.0%" in result["all_benchmarks"]
        assert "total_revenue_0.5%" in result["all_benchmarks"]
        assert "total_revenue_1.0%" in result["all_benchmarks"]


# ============================================================================
# RISK ASSESSOR TESTS
# ============================================================================

class TestRiskAssessor:
    """Test risk assessment logic"""

    def test_low_risk_combination(self):
        """Test low inherent + low control = low RMM"""
        rmm, detection_risk, multiplier = RiskAssessor.assess_combined_risk(
            RiskLevel.LOW, RiskLevel.LOW
        )

        assert rmm == RiskLevel.LOW
        assert detection_risk == RiskLevel.MODERATE
        assert multiplier == Decimal("0.7")

    def test_high_risk_combination(self):
        """Test high inherent + high control = significant RMM"""
        rmm, detection_risk, multiplier = RiskAssessor.assess_combined_risk(
            RiskLevel.HIGH, RiskLevel.HIGH
        )

        assert rmm == RiskLevel.SIGNIFICANT
        assert detection_risk == RiskLevel.LOW
        assert multiplier == Decimal("1.5")

    def test_significant_risk_combination(self):
        """Test significant inherent + significant control = significant RMM"""
        rmm, detection_risk, multiplier = RiskAssessor.assess_combined_risk(
            RiskLevel.SIGNIFICANT, RiskLevel.SIGNIFICANT
        )

        assert rmm == RiskLevel.SIGNIFICANT
        assert detection_risk == RiskLevel.LOW
        assert multiplier == Decimal("2.5")  # Highest multiplier

    def test_moderate_risk_combination(self):
        """Test moderate inherent + moderate control = moderate RMM"""
        rmm, detection_risk, multiplier = RiskAssessor.assess_combined_risk(
            RiskLevel.MODERATE, RiskLevel.MODERATE
        )

        assert rmm == RiskLevel.MODERATE
        assert detection_risk == RiskLevel.MODERATE
        assert multiplier == Decimal("1.0")

    def test_fraud_risk_factors_liquidity(self):
        """Test fraud risk identification - liquidity pressure"""
        ratios = {
            "current_ratio": Decimal("0.8"),  # Below 1.0
            "debt_to_equity": Decimal("1.5"),
            "roe": Decimal("0.1"),
        }

        factors = RiskAssessor.identify_fraud_risk_factors(
            industry="technology",
            financial_ratios=ratios,
            management_changes=False,
            significant_transactions=False,
            complex_structure=False,
        )

        # Should identify liquidity pressure
        assert any("Liquidity pressure" in f["factor"] for f in factors)
        assert any(f["category"] == "incentive" for f in factors)

    def test_fraud_risk_factors_debt_covenant(self):
        """Test fraud risk identification - debt covenant pressure"""
        ratios = {
            "current_ratio": Decimal("2.0"),
            "debt_to_equity": Decimal("2.5"),  # Above 2.0
            "roe": Decimal("0.1"),
        }

        factors = RiskAssessor.identify_fraud_risk_factors(
            industry="manufacturing",
            financial_ratios=ratios,
            management_changes=False,
            significant_transactions=False,
            complex_structure=False,
        )

        # Should identify debt covenant pressure
        assert any("Debt covenant" in f["factor"] for f in factors)

    def test_fraud_risk_factors_management_changes(self):
        """Test fraud risk identification - management changes"""
        ratios = {
            "current_ratio": Decimal("2.0"),
            "debt_to_equity": Decimal("1.0"),
            "roe": Decimal("0.1"),
        }

        factors = RiskAssessor.identify_fraud_risk_factors(
            industry="retail",
            financial_ratios=ratios,
            management_changes=True,  # Risk factor
            significant_transactions=False,
            complex_structure=False,
        )

        # Should identify management changes as opportunity
        assert any("Management changes" in f["factor"] for f in factors)
        assert any(f["category"] == "opportunity" for f in factors)

    def test_fraud_risk_factors_complex_structure(self):
        """Test fraud risk identification - complex structure"""
        ratios = {
            "current_ratio": Decimal("2.0"),
            "debt_to_equity": Decimal("1.0"),
            "roe": Decimal("0.1"),
        }

        factors = RiskAssessor.identify_fraud_risk_factors(
            industry="financial",
            financial_ratios=ratios,
            management_changes=False,
            significant_transactions=False,
            complex_structure=True,  # Risk factor
        )

        # Should identify complex structure
        assert any("Complex structure" in f["factor"] for f in factors)


# ============================================================================
# AUDIT PROGRAM GENERATOR TESTS
# ============================================================================

class TestAuditProgramGenerator:
    """Test audit program generation"""

    def test_asset_existence_procedures(self):
        """Test procedures for asset existence assertion"""
        procedures = AuditProgramGenerator.generate_procedures(
            account_type=AccountType.ASSET,
            assertion=AssertionType.EXISTENCE,
            risk_level=RiskLevel.MODERATE,
            balance=Decimal("1000000"),
            materiality=Decimal("50000"),
        )

        assert len(procedures) > 0
        assert any("Confirm" in p["procedure"] for p in procedures)
        assert any("inspect" in p["procedure"].lower() for p in procedures)
        assert all(p["nature"] == "substantive" for p in procedures)

    def test_liability_completeness_procedures(self):
        """Test procedures for liability completeness assertion"""
        procedures = AuditProgramGenerator.generate_procedures(
            account_type=AccountType.LIABILITY,
            assertion=AssertionType.COMPLETENESS,
            risk_level=RiskLevel.HIGH,
            balance=Decimal("2000000"),
            materiality=Decimal("50000"),
        )

        assert len(procedures) > 0
        assert any("unrecorded" in p["procedure"].lower() for p in procedures)
        assert any("subsequent" in p["procedure"].lower() for p in procedures)

    def test_low_risk_extent(self):
        """Test that low risk results in minimal extent"""
        procedures = AuditProgramGenerator.generate_procedures(
            account_type=AccountType.ASSET,
            assertion=AssertionType.EXISTENCE,
            risk_level=RiskLevel.LOW,
            balance=Decimal("1000000"),
            materiality=Decimal("50000"),
        )

        assert all(p["extent"] == "minimal" for p in procedures)
        assert all("25%" in p["sample_size_guidance"] for p in procedures)

    def test_high_risk_extent(self):
        """Test that high risk results in extensive testing"""
        procedures = AuditProgramGenerator.generate_procedures(
            account_type=AccountType.ASSET,
            assertion=AssertionType.EXISTENCE,
            risk_level=RiskLevel.HIGH,
            balance=Decimal("1000000"),
            materiality=Decimal("50000"),
        )

        assert all(p["extent"] == "extensive" for p in procedures)
        assert all("75%" in p["sample_size_guidance"] for p in procedures)
        assert all(p["timing"] == "year_end" for p in procedures)

    def test_significant_risk_unpredictable_procedures(self):
        """Test that significant risk includes unpredictable procedures"""
        procedures = AuditProgramGenerator.generate_procedures(
            account_type=AccountType.REVENUE,
            assertion=AssertionType.OCCURRENCE,
            risk_level=RiskLevel.SIGNIFICANT,
            balance=Decimal("5000000"),
            materiality=Decimal("50000"),
        )

        # Should include unpredictable procedure
        assert any(p.get("fraud_procedure") == True for p in procedures)
        assert any("unpredictable" in p["procedure"].lower() for p in procedures)

    def test_procedure_sequencing(self):
        """Test that procedures are properly sequenced"""
        procedures = AuditProgramGenerator.generate_procedures(
            account_type=AccountType.ASSET,
            assertion=AssertionType.EXISTENCE,
            risk_level=RiskLevel.MODERATE,
            balance=Decimal("1000000"),
            materiality=Decimal("50000"),
        )

        # Check sequential numbering
        for i, proc in enumerate(procedures):
            assert proc["sequence"] == i + 1

    def test_material_item_flagging(self):
        """Test that items exceeding materiality are flagged"""
        materiality = Decimal("50000")

        # Balance exceeds materiality
        procedures = AuditProgramGenerator.generate_procedures(
            account_type=AccountType.ASSET,
            assertion=AssertionType.VALUATION_ALLOCATION,
            risk_level=RiskLevel.MODERATE,
            balance=Decimal("100000"),  # Exceeds materiality
            materiality=materiality,
        )

        assert all(p["is_material"] == True for p in procedures)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
class TestAuditPlanningServiceIntegration:
    """Integration tests for audit planning service"""

    @pytest.fixture
    async def db_session(self):
        """Create test database session"""
        # Mock async session for testing
        from unittest.mock import AsyncMock
        session = AsyncMock()
        yield session

    async def test_create_audit_plan_complete_workflow(self, db_session):
        """Test creating complete audit plan with materiality"""
        service = AuditPlanningService(db_session)

        financial_data = {
            "total_assets": Decimal("10000000"),
            "total_revenue": Decimal("5000000"),
            "pretax_income": Decimal("1000000"),
            "total_equity": Decimal("3000000"),
        }

        # Mock the database operations
        db_session.add = lambda x: None
        db_session.commit = AsyncMock()
        db_session.refresh = AsyncMock()

        plan = await service.create_audit_plan(
            engagement_id=uuid4(),
            tenant_id=uuid4(),
            planned_by_id=uuid4(),
            financial_data=financial_data,
            entity_type="public",
        )

        # Verify materiality was calculated
        assert plan.overall_materiality is not None
        assert plan.performance_materiality is not None
        assert plan.trivial_threshold is not None
        assert plan.overall_engagement_risk == RiskLevel.MODERATE

    async def test_assess_account_risk_complete_workflow(self, db_session):
        """Test complete risk assessment workflow"""
        service = AuditPlanningService(db_session)

        # Mock audit plan retrieval
        from app.models import AuditPlan
        mock_plan = AuditPlan(
            id=uuid4(),
            engagement_id=uuid4(),
            tenant_id=uuid4(),
            planned_by_id=uuid4(),
            overall_materiality=Decimal("100000"),
            performance_materiality=Decimal("65000"),
            trivial_threshold=Decimal("4000"),
        )

        from sqlalchemy.ext.asyncio import AsyncResult
        mock_result = AsyncMock(spec=AsyncResult)
        mock_result.scalar_one.return_value = mock_plan
        db_session.execute = AsyncMock(return_value=mock_result)
        db_session.add = lambda x: None
        db_session.commit = AsyncMock()
        db_session.refresh = AsyncMock()

        assessment = await service.assess_account_risk(
            audit_plan_id=mock_plan.id,
            tenant_id=uuid4(),
            assessed_by_id=uuid4(),
            account_name="Accounts Receivable",
            account_type=AccountType.ASSET,
            account_balance=Decimal("1000000"),
            assertion=AssertionType.EXISTENCE,
            inherent_risk=RiskLevel.MODERATE,
            control_effectiveness=ControlEffectiveness.EFFECTIVE,
        )

        # Verify risk assessment
        assert assessment.account_name == "Accounts Receivable"
        assert assessment.inherent_risk == RiskLevel.MODERATE
        assert assessment.control_risk == RiskLevel.LOW  # Effective controls
        assert assessment.risk_of_material_misstatement is not None
        assert assessment.planned_procedures is not None
        assert len(assessment.planned_procedures) > 0


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_zero_values(self):
        """Test materiality calculation with zero values"""
        calc = MaterialityCalculator()

        result = calc.calculate_materiality(
            total_assets=Decimal("0"),
            total_revenue=Decimal("0"),
            pretax_income=Decimal("0"),
            total_equity=Decimal("0"),
            entity_type="public"
        )

        # Should return default materiality
        assert result["overall_materiality"] == Decimal("100000.00")

    def test_negative_income(self):
        """Test materiality with negative income (loss)"""
        calc = MaterialityCalculator()

        result = calc.calculate_materiality(
            total_assets=Decimal("10000000"),
            total_revenue=Decimal("5000000"),
            pretax_income=Decimal("-500000"),  # Loss
            total_equity=Decimal("3000000"),
            entity_type="public"
        )

        # Should not use income benchmark
        assert "pretax_income" not in result["benchmark_used"]

    def test_very_large_values(self):
        """Test materiality with very large values"""
        calc = MaterialityCalculator()

        result = calc.calculate_materiality(
            total_assets=Decimal("1000000000000"),  # $1 trillion
            total_revenue=Decimal("500000000000"),
            pretax_income=Decimal("50000000000"),
            total_equity=Decimal("300000000000"),
            entity_type="public"
        )

        # Should calculate without errors
        assert result["overall_materiality"] > 0
        assert result["performance_materiality"] > 0

    def test_all_risk_matrix_combinations(self):
        """Test all 16 risk matrix combinations"""
        risk_levels = [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.SIGNIFICANT]

        for ir in risk_levels:
            for cr in risk_levels:
                rmm, dr, multiplier = RiskAssessor.assess_combined_risk(ir, cr)

                # Verify all return valid values
                assert rmm in risk_levels
                assert dr in risk_levels
                assert multiplier >= Decimal("0.7")
                assert multiplier <= Decimal("2.5")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
