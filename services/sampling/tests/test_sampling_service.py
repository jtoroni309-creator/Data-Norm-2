"""
Comprehensive Test Suite for Statistical Sampling Service

Tests MUS, Classical Variables, and Attribute sampling methods.
"""

import pytest
from decimal import Decimal
from typing import List, Dict

from app.sampling_service import (
    MonetaryUnitSampling,
    ClassicalVariablesSampling,
    AttributeSampling,
    SamplingService,
    SamplingMethod,
    RiskLevel,
)


# ============================================================================
# MONETARY UNIT SAMPLING (MUS/PPS) TESTS
# ============================================================================

class TestMonetaryUnitSampling:
    """Test MUS/PPS sampling calculations"""

    def test_sample_size_calculation_basic(self):
        """Test basic MUS sample size calculation"""
        result = MonetaryUnitSampling.calculate_sample_size(
            population_value=Decimal("1000000"),
            tolerable_misstatement=Decimal("50000"),
            expected_misstatement=Decimal("0"),
            risk_level=RiskLevel.MODERATE,
        )

        # Formula: n = (RF × BV) / TM
        # n = (2.31 × 1,000,000) / 50,000 = 46.2 → 47
        assert result["sample_size"] >= 46
        assert result["sample_size"] <= 50  # Some rounding tolerance
        assert result["reliability_factor"] == 2.31

    def test_sample_size_calculation_low_risk(self):
        """Test MUS sample size with low risk (RF=3.00)"""
        result = MonetaryUnitSampling.calculate_sample_size(
            population_value=Decimal("1000000"),
            tolerable_misstatement=Decimal("50000"),
            expected_misstatement=Decimal("0"),
            risk_level=RiskLevel.LOW,
        )

        # RF = 3.00 for 5% risk
        assert result["reliability_factor"] == 3.00
        # n = (3.00 × 1,000,000) / 50,000 = 60
        assert result["sample_size"] >= 60

    def test_sample_size_calculation_high_risk(self):
        """Test MUS sample size with high risk (RF=1.61)"""
        result = MonetaryUnitSampling.calculate_sample_size(
            population_value=Decimal("1000000"),
            tolerable_misstatement=Decimal("50000"),
            expected_misstatement=Decimal("0"),
            risk_level=RiskLevel.HIGH,
        )

        # RF = 1.61 for 20% risk
        assert result["reliability_factor"] == 1.61
        # n = (1.61 × 1,000,000) / 50,000 = 32.2 → 33
        assert result["sample_size"] >= 32
        assert result["sample_size"] <= 35

    def test_sample_size_minimum_30(self):
        """Test that minimum sample size is 30"""
        result = MonetaryUnitSampling.calculate_sample_size(
            population_value=Decimal("100000"),
            tolerable_misstatement=Decimal("50000"),  # High tolerable misstatement
            expected_misstatement=Decimal("0"),
            risk_level=RiskLevel.HIGH,
        )

        # Even with calculation yielding low number, minimum should be 30
        assert result["sample_size"] >= 30

    def test_sampling_interval_calculation(self):
        """Test sampling interval calculation"""
        result = MonetaryUnitSampling.calculate_sample_size(
            population_value=Decimal("1000000"),
            tolerable_misstatement=Decimal("50000"),
            expected_misstatement=Decimal("0"),
            risk_level=RiskLevel.MODERATE,
        )

        # Sampling interval = Population / Sample Size
        expected_interval = Decimal("1000000") / Decimal(result["sample_size"])
        assert abs(result["sampling_interval"] - expected_interval) < Decimal("1.0")

    def test_expected_misstatement_adjustment(self):
        """Test that expected misstatement increases sample size"""
        result_zero_expected = MonetaryUnitSampling.calculate_sample_size(
            population_value=Decimal("1000000"),
            tolerable_misstatement=Decimal("50000"),
            expected_misstatement=Decimal("0"),
            risk_level=RiskLevel.MODERATE,
        )

        result_with_expected = MonetaryUnitSampling.calculate_sample_size(
            population_value=Decimal("1000000"),
            tolerable_misstatement=Decimal("50000"),
            expected_misstatement=Decimal("10000"),  # Expected errors
            risk_level=RiskLevel.MODERATE,
        )

        # Sample size should increase when errors expected
        assert result_with_expected["sample_size"] > result_zero_expected["sample_size"]

    def test_select_sample_systematic_selection(self):
        """Test systematic sample selection with random start"""
        # Create simple population
        population = [
            {"id": 1, "amount": 1000},
            {"id": 2, "amount": 2000},
            {"id": 3, "amount": 3000},
            {"id": 4, "amount": 4000},
            {"id": 5, "amount": 5000},
            {"id": 6, "amount": 6000},
            {"id": 7, "amount": 7000},
            {"id": 8, "amount": 8000},
            {"id": 9, "amount": 9000},
            {"id": 10, "amount": 10000},
        ]

        sample = MonetaryUnitSampling.select_sample(
            population=population,
            sample_size=5,
            sampling_interval=Decimal("11000"),  # Total = 55000, interval = 11000
        )

        # Should select approximately 5 items
        assert len(sample) >= 4  # Allow some variance due to random start
        assert len(sample) <= 6

        # All selected items should be from population
        for item in sample:
            assert item in population

    def test_evaluate_sample_no_errors(self):
        """Test sample evaluation with no errors found"""
        sample_results = [
            {"book_value": "1000", "audit_value": "1000"},
            {"book_value": "2000", "audit_value": "2000"},
            {"book_value": "3000", "audit_value": "3000"},
        ]

        result = MonetaryUnitSampling.evaluate_sample(
            sample_results=sample_results,
            population_value=Decimal("1000000"),
            tolerable_misstatement=Decimal("50000"),
            risk_level=RiskLevel.MODERATE,
        )

        # No errors found
        assert result["actual_misstatements_found"] == 0
        assert result["total_known_misstatement"] == 0
        assert result["upper_misstatement_limit"] < result["tolerable_misstatement"]
        assert result["conclusion"] == "ACCEPT"

    def test_evaluate_sample_with_errors(self):
        """Test sample evaluation with errors found"""
        sample_results = [
            {"book_value": "10000", "audit_value": "9500"},  # $500 error, 5% tainting
            {"book_value": "20000", "audit_value": "19000"},  # $1000 error, 5% tainting
            {"book_value": "30000", "audit_value": "30000"},  # No error
        ]

        result = MonetaryUnitSampling.evaluate_sample(
            sample_results=sample_results,
            population_value=Decimal("1000000"),
            tolerable_misstatement=Decimal("50000"),
            risk_level=RiskLevel.MODERATE,
        )

        # Errors found
        assert result["actual_misstatements_found"] == 2
        assert result["total_known_misstatement"] == 1500.0
        assert result["projected_misstatement"] > 0

        # Check tainting calculation
        assert len(result["misstatement_details"]) == 2
        for detail in result["misstatement_details"]:
            assert "tainting" in detail
            assert detail["tainting"] == 0.05  # 5% tainting

    def test_evaluate_sample_exceed_tolerable(self):
        """Test sample evaluation when errors exceed tolerable misstatement"""
        sample_results = [
            {"book_value": "10000", "audit_value": "5000"},  # 50% tainting - significant
            {"book_value": "20000", "audit_value": "10000"},  # 50% tainting
            {"book_value": "30000", "audit_value": "20000"},  # 33% tainting
        ]

        result = MonetaryUnitSampling.evaluate_sample(
            sample_results=sample_results,
            population_value=Decimal("100000"),
            tolerable_misstatement=Decimal("5000"),  # Low tolerable
            risk_level=RiskLevel.MODERATE,
        )

        # UML should exceed tolerable misstatement
        assert result["upper_misstatement_limit"] > result["tolerable_misstatement"]
        assert result["conclusion"] == "REJECT"


# ============================================================================
# CLASSICAL VARIABLES SAMPLING TESTS
# ============================================================================

class TestClassicalVariablesSampling:
    """Test classical variables sampling methods"""

    def test_mean_per_unit_sample_size(self):
        """Test mean-per-unit sample size calculation"""
        sample_size = ClassicalVariablesSampling.calculate_sample_size_mean_per_unit(
            population_size=1000,
            population_std_dev=Decimal("500"),
            tolerable_misstatement=Decimal("10000"),
            risk_level=RiskLevel.MODERATE,
        )

        # Sample size should be reasonable
        assert sample_size >= 30  # Minimum
        assert sample_size <= 1000  # Maximum (population size)

    def test_mean_per_unit_minimum_sample_size(self):
        """Test minimum sample size enforcement"""
        sample_size = ClassicalVariablesSampling.calculate_sample_size_mean_per_unit(
            population_size=1000,
            population_std_dev=Decimal("10"),  # Very low std dev
            tolerable_misstatement=Decimal("10000"),  # High tolerable
            risk_level=RiskLevel.HIGH,  # Low confidence
        )

        # Should enforce minimum of 30
        assert sample_size >= 30

    def test_mean_per_unit_risk_level_impact(self):
        """Test that risk level impacts sample size"""
        size_low_risk = ClassicalVariablesSampling.calculate_sample_size_mean_per_unit(
            population_size=1000,
            population_std_dev=Decimal("500"),
            tolerable_misstatement=Decimal("10000"),
            risk_level=RiskLevel.LOW,  # 5% risk, Z=1.96
        )

        size_high_risk = ClassicalVariablesSampling.calculate_sample_size_mean_per_unit(
            population_size=1000,
            population_std_dev=Decimal("500"),
            tolerable_misstatement=Decimal("10000"),
            risk_level=RiskLevel.HIGH,  # 20% risk, Z=1.28
        )

        # Lower risk should require larger sample
        assert size_low_risk > size_high_risk

    def test_evaluate_mean_per_unit(self):
        """Test mean-per-unit evaluation"""
        sample_values = [
            Decimal("1000"),
            Decimal("1500"),
            Decimal("2000"),
            Decimal("2500"),
            Decimal("3000"),
        ]

        result = ClassicalVariablesSampling.evaluate_mean_per_unit(
            sample_values=sample_values,
            population_size=100,
            tolerable_misstatement=Decimal("50000"),
            risk_level=RiskLevel.MODERATE,
        )

        # Check projected value
        expected_mean = sum(sample_values) / len(sample_values)
        expected_projected = expected_mean * Decimal("100")

        assert result["sample_mean"] == float(expected_mean)
        assert result["projected_value"] == float(expected_projected)

        # Check confidence interval
        assert "confidence_interval" in result
        assert result["confidence_interval"]["lower"] < result["projected_value"]
        assert result["confidence_interval"]["upper"] > result["projected_value"]

        # Check precision
        assert result["precision"] > 0


# ============================================================================
# ATTRIBUTE SAMPLING TESTS
# ============================================================================

class TestAttributeSampling:
    """Test attribute sampling for control testing"""

    def test_sample_size_zero_expected_deviations(self):
        """Test sample size with zero expected deviations"""
        sample_size = AttributeSampling.calculate_sample_size(
            population_size=5000,
            tolerable_deviation_rate=Decimal("0.05"),  # 5%
            expected_deviation_rate=Decimal("0.00"),
            risk_level=RiskLevel.MODERATE,
        )

        # Should be around 77 per statistical tables
        assert sample_size >= 75
        assert sample_size <= 80

    def test_sample_size_with_expected_deviations(self):
        """Test sample size increases with expected deviations"""
        size_zero_expected = AttributeSampling.calculate_sample_size(
            population_size=5000,
            tolerable_deviation_rate=Decimal("0.05"),
            expected_deviation_rate=Decimal("0.00"),
            risk_level=RiskLevel.MODERATE,
        )

        size_with_expected = AttributeSampling.calculate_sample_size(
            population_size=5000,
            tolerable_deviation_rate=Decimal("0.06"),
            expected_deviation_rate=Decimal("0.02"),  # 2% expected
            risk_level=RiskLevel.MODERATE,
        )

        # Sample size should increase with expected deviations
        assert size_with_expected > size_zero_expected

    def test_sample_size_minimum_25(self):
        """Test minimum sample size enforcement"""
        sample_size = AttributeSampling.calculate_sample_size(
            population_size=100,
            tolerable_deviation_rate=Decimal("0.20"),  # Very high tolerable
            expected_deviation_rate=Decimal("0.00"),
            risk_level=RiskLevel.HIGH,
        )

        # Minimum should be 25
        assert sample_size >= 25

    def test_sample_size_maximum_population(self):
        """Test sample size doesn't exceed population"""
        sample_size = AttributeSampling.calculate_sample_size(
            population_size=50,  # Small population
            tolerable_deviation_rate=Decimal("0.02"),  # Very low tolerable
            expected_deviation_rate=Decimal("0.00"),
            risk_level=RiskLevel.LOW,
        )

        # Should not exceed population
        assert sample_size <= 50

    def test_evaluate_sample_no_deviations(self):
        """Test evaluation with no deviations found"""
        result = AttributeSampling.evaluate_sample(
            sample_size=100,
            deviations_found=0,
            tolerable_deviation_rate=Decimal("0.05"),
            risk_level=RiskLevel.MODERATE,
        )

        # No deviations
        assert result["deviations_found"] == 0
        assert result["sample_deviation_rate"] == 0.0
        assert result["upper_deviation_limit"] < float(Decimal("0.05"))
        assert result["conclusion"] == "RELY"

    def test_evaluate_sample_with_deviations_can_rely(self):
        """Test evaluation with deviations but still can rely"""
        result = AttributeSampling.evaluate_sample(
            sample_size=100,
            deviations_found=2,  # 2% deviation rate
            tolerable_deviation_rate=Decimal("0.10"),  # 10% tolerable
            risk_level=RiskLevel.MODERATE,
        )

        # Some deviations but acceptable
        assert result["deviations_found"] == 2
        assert result["sample_deviation_rate"] == 0.02
        assert result["upper_deviation_limit"] < result["tolerable_deviation_rate"]
        assert result["conclusion"] == "RELY"

    def test_evaluate_sample_cannot_rely(self):
        """Test evaluation when cannot rely on controls"""
        result = AttributeSampling.evaluate_sample(
            sample_size=100,
            deviations_found=8,  # 8% deviation rate
            tolerable_deviation_rate=Decimal("0.05"),  # 5% tolerable
            risk_level=RiskLevel.MODERATE,
        )

        # Too many deviations
        assert result["deviations_found"] == 8
        assert result["sample_deviation_rate"] == 0.08
        assert result["upper_deviation_limit"] >= result["tolerable_deviation_rate"]
        assert result["conclusion"] == "DO_NOT_RELY"


# ============================================================================
# SAMPLING SERVICE INTEGRATION TESTS
# ============================================================================

class TestSamplingService:
    """Test unified sampling service"""

    def test_recommend_method_controls(self):
        """Test method recommendation for control testing"""
        service = SamplingService()

        method = service.recommend_sampling_method(
            population_size=1000,
            population_value=Decimal("1000000"),
            test_objective="controls",
            expected_error_rate=Decimal("0.02"),
        )

        assert method == SamplingMethod.ATTRIBUTE

    def test_recommend_method_overstatement_low_errors(self):
        """Test method recommendation for overstatement with low errors"""
        service = SamplingService()

        method = service.recommend_sampling_method(
            population_size=5000,
            population_value=Decimal("10000000"),
            test_objective="overstatement",
            expected_error_rate=Decimal("0.01"),  # 1% - low
        )

        assert method == SamplingMethod.MUS

    def test_recommend_method_understatement(self):
        """Test method recommendation for understatement testing"""
        service = SamplingService()

        method = service.recommend_sampling_method(
            population_size=1000,
            population_value=Decimal("5000000"),
            test_objective="understatement",
            expected_error_rate=Decimal("0.02"),
        )

        assert method == SamplingMethod.MEAN_PER_UNIT

    def test_recommend_method_small_population(self):
        """Test method recommendation for small population"""
        service = SamplingService()

        method = service.recommend_sampling_method(
            population_size=50,  # Small
            population_value=Decimal("100000"),
            test_objective="overstatement",
            expected_error_rate=Decimal("0.01"),
        )

        assert method == SamplingMethod.MEAN_PER_UNIT

    def test_calculate_optimal_sample_size_mus(self):
        """Test optimal sample size calculation for MUS"""
        service = SamplingService()

        sample_size = service.calculate_optimal_sample_size(
            method=SamplingMethod.MUS,
            population_value=Decimal("1000000"),
            tolerable_misstatement=Decimal("50000"),
            expected_misstatement=Decimal("0"),
            risk_level=RiskLevel.MODERATE,
        )

        assert sample_size >= 30
        assert sample_size < 100  # Reasonable range

    def test_calculate_optimal_sample_size_mean_per_unit(self):
        """Test optimal sample size calculation for mean-per-unit"""
        service = SamplingService()

        sample_size = service.calculate_optimal_sample_size(
            method=SamplingMethod.MEAN_PER_UNIT,
            population_size=1000,
            population_std_dev=Decimal("500"),
            tolerable_misstatement=Decimal("10000"),
            risk_level=RiskLevel.MODERATE,
        )

        assert sample_size >= 30
        assert sample_size <= 1000

    def test_calculate_optimal_sample_size_attribute(self):
        """Test optimal sample size calculation for attribute"""
        service = SamplingService()

        sample_size = service.calculate_optimal_sample_size(
            method=SamplingMethod.ATTRIBUTE,
            population_size=5000,
            tolerable_deviation_rate=Decimal("0.05"),
            expected_deviation_rate=Decimal("0.00"),
            risk_level=RiskLevel.MODERATE,
        )

        assert sample_size >= 25
        assert sample_size <= 5000


# ============================================================================
# EDGE CASE AND ERROR HANDLING TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_mus_with_very_small_population(self):
        """Test MUS with very small population value"""
        result = MonetaryUnitSampling.calculate_sample_size(
            population_value=Decimal("10000"),  # Small
            tolerable_misstatement=Decimal("1000"),
            expected_misstatement=Decimal("0"),
            risk_level=RiskLevel.MODERATE,
        )

        # Should still calculate valid sample size
        assert result["sample_size"] >= 30

    def test_classical_with_zero_std_dev(self):
        """Test classical sampling with zero standard deviation"""
        sample_size = ClassicalVariablesSampling.calculate_sample_size_mean_per_unit(
            population_size=1000,
            population_std_dev=Decimal("0"),  # No variation
            tolerable_misstatement=Decimal("10000"),
            risk_level=RiskLevel.MODERATE,
        )

        # Should return minimum sample size
        assert sample_size >= 30

    def test_attribute_with_100_percent_tolerable(self):
        """Test attribute sampling with very high tolerable rate"""
        result = AttributeSampling.evaluate_sample(
            sample_size=30,
            deviations_found=29,  # Almost all items have deviations
            tolerable_deviation_rate=Decimal("1.0"),  # 100% tolerable
            risk_level=RiskLevel.MODERATE,
        )

        # Should still evaluate (though controls are useless)
        assert result["conclusion"] == "RELY"  # Within 100% tolerable

    def test_all_risk_levels_produce_valid_results(self):
        """Test that all risk levels work correctly"""
        service = SamplingService()

        for risk in [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH]:
            sample_size = service.calculate_optimal_sample_size(
                method=SamplingMethod.MUS,
                population_value=Decimal("1000000"),
                tolerable_misstatement=Decimal("50000"),
                expected_misstatement=Decimal("0"),
                risk_level=risk,
            )

            assert sample_size >= 30
            assert sample_size <= 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
