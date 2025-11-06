"""
Accounting Estimates Evaluation Service

Implements PCAOB AS 2501: Auditing Accounting Estimates, Including Fair Value Measurements

Provides tools for evaluating management's:
- Valuation models and assumptions
- Fair value measurements
- Allowances and reserves
- Historical accuracy of estimates
- Potential management bias

Key Requirements (AS 2501):
- Understand management's process
- Evaluate reasonableness of assumptions
- Test methodology and data
- Develop independent expectation
- Evaluate historical accuracy
- Assess management bias
"""

import logging
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class EstimateType(str, Enum):
    """Types of accounting estimates"""
    FAIR_VALUE = "fair_value"  # Fair value measurements
    ALLOWANCE = "allowance"  # Allowance for credit losses, doubtful accounts
    RESERVE = "reserve"  # Warranty reserves, legal reserves
    DEPRECIATION = "depreciation"  # Useful life estimates
    IMPAIRMENT = "impairment"  # Impairment testing
    PROVISION = "provision"  # Provision for losses
    CONTINGENCY = "contingency"  # Contingent liabilities
    VALUATION_ALLOWANCE = "valuation_allowance"  # DTAs


class ComplexityLevel(str, Enum):
    """Estimate complexity assessment"""
    LOW = "low"  # Simple calculation, objective inputs
    MODERATE = "moderate"  # Some subjectivity
    HIGH = "high"  # Significant judgment, unobservable inputs
    VERY_HIGH = "very_high"  # Level 3 fair values, complex models


class BiasIndicator(str, Enum):
    """Direction of potential management bias"""
    OPTIMISTIC = "optimistic"  # Tends toward favorable outcomes
    PESSIMISTIC = "pessimistic"  # Tends toward conservative outcomes
    NEUTRAL = "neutral"  # No apparent bias
    INCONSISTENT = "inconsistent"  # Changes direction period to period


class AccountingEstimatesService:
    """
    Service for evaluating accounting estimates per AS 2501.
    """

    def __init__(self):
        """Initialize estimates evaluation service"""
        pass

    def assess_estimate_complexity(
        self,
        estimate_type: EstimateType,
        involves_unobservable_inputs: bool,
        requires_specialist: bool,
        multiple_assumptions: bool,
        significant_judgment: bool,
    ) -> ComplexityLevel:
        """
        Assess the complexity of an accounting estimate.

        Higher complexity = higher audit risk and more procedures needed.

        Args:
            estimate_type: Type of estimate
            involves_unobservable_inputs: Uses Level 3 inputs (ASC 820)
            requires_specialist: Needs valuation specialist
            multiple_assumptions: Multiple interdependent assumptions
            significant_judgment: Requires significant management judgment

        Returns:
            ComplexityLevel assessment
        """
        complexity_score = 0

        # Base complexity by type
        type_complexity = {
            EstimateType.FAIR_VALUE: 2,
            EstimateType.IMPAIRMENT: 2,
            EstimateType.CONTINGENCY: 2,
            EstimateType.VALUATION_ALLOWANCE: 2,
            EstimateType.ALLOWANCE: 1,
            EstimateType.RESERVE: 1,
            EstimateType.PROVISION: 1,
            EstimateType.DEPRECIATION: 0,
        }
        complexity_score += type_complexity.get(estimate_type, 1)

        # Add points for complexity factors
        if involves_unobservable_inputs:
            complexity_score += 2  # Major complexity driver
        if requires_specialist:
            complexity_score += 1
        if multiple_assumptions:
            complexity_score += 1
        if significant_judgment:
            complexity_score += 1

        # Map score to complexity level
        if complexity_score >= 5:
            return ComplexityLevel.VERY_HIGH
        elif complexity_score >= 3:
            return ComplexityLevel.HIGH
        elif complexity_score >= 2:
            return ComplexityLevel.MODERATE
        else:
            return ComplexityLevel.LOW

    def evaluate_assumption_reasonableness(
        self,
        assumption_name: str,
        management_value: Decimal,
        auditor_range_low: Decimal,
        auditor_range_high: Decimal,
        industry_benchmark: Optional[Decimal] = None,
    ) -> Dict:
        """
        Evaluate reasonableness of a key assumption.

        Compares management's assumption to:
        - Auditor's independent range
        - Industry benchmarks
        - Historical company experience

        Args:
            assumption_name: Name of assumption (e.g., "discount_rate", "growth_rate")
            management_value: Management's assumed value
            auditor_range_low: Lower bound of reasonable range
            auditor_range_high: Upper bound of reasonable range
            industry_benchmark: Industry average/median if available

        Returns:
            Dictionary with reasonableness assessment
        """
        within_range = auditor_range_low <= management_value <= auditor_range_high

        # Calculate how far from midpoint
        range_midpoint = (auditor_range_low + auditor_range_high) / 2
        distance_from_midpoint = abs(management_value - range_midpoint)
        distance_as_percent = (distance_from_midpoint / range_midpoint) * 100 if range_midpoint != 0 else 0

        # Compare to industry if available
        industry_comparison = None
        if industry_benchmark:
            industry_diff = management_value - industry_benchmark
            industry_diff_percent = (industry_diff / industry_benchmark) * 100 if industry_benchmark != 0 else 0
            industry_comparison = {
                "benchmark": float(industry_benchmark),
                "difference": float(industry_diff),
                "difference_percent": round(float(industry_diff_percent), 2),
            }

        # Determine reasonableness conclusion
        if not within_range:
            conclusion = "UNREASONABLE"
            risk_level = "HIGH"
        elif distance_as_percent > 25:
            conclusion = "REASONABLE_BUT_AGGRESSIVE"
            risk_level = "MODERATE"
        elif distance_as_percent > 10:
            conclusion = "REASONABLE"
            risk_level = "LOW"
        else:
            conclusion = "REASONABLE_AND_NEUTRAL"
            risk_level = "LOW"

        return {
            "assumption_name": assumption_name,
            "management_value": float(management_value),
            "auditor_range": {
                "low": float(auditor_range_low),
                "high": float(auditor_range_high),
                "midpoint": float(range_midpoint),
            },
            "within_reasonable_range": within_range,
            "distance_from_midpoint_percent": round(float(distance_as_percent), 2),
            "industry_comparison": industry_comparison,
            "conclusion": conclusion,
            "risk_level": risk_level,
        }

    def perform_retrospective_review(
        self,
        historical_estimates: List[Dict],  # [{"period": "2024", "estimate": 100, "actual": 95}]
    ) -> Dict:
        """
        Perform retrospective review of prior period estimates.

        AS 2501.14: Auditor should evaluate how management's prior estimates
        turned out compared to actual results (management bias indicator).

        Args:
            historical_estimates: List of prior estimates with actual outcomes

        Returns:
            Analysis of historical accuracy and bias patterns
        """
        if not historical_estimates:
            return {
                "sufficient_history": False,
                "message": "No historical data available for retrospective review",
            }

        # Calculate variances
        variances = []
        optimistic_count = 0
        pessimistic_count = 0

        for item in historical_estimates:
            estimate = Decimal(str(item["estimate"]))
            actual = Decimal(str(item["actual"]))

            variance = actual - estimate
            variance_percent = (variance / estimate * 100) if estimate != 0 else 0

            variances.append({
                "period": item["period"],
                "estimate": float(estimate),
                "actual": float(actual),
                "variance": float(variance),
                "variance_percent": round(float(variance_percent), 2),
            })

            # Track bias direction
            if variance > 0:
                optimistic_count += 1  # Underestimated (too optimistic)
            elif variance < 0:
                pessimistic_count += 1  # Overestimated (too pessimistic)

        # Calculate statistics
        total_periods = len(historical_estimates)
        variance_amounts = [Decimal(str(v["variance"])) for v in variances]
        variance_percents = [Decimal(str(v["variance_percent"])) for v in variances]

        mean_variance = sum(variance_amounts) / len(variance_amounts)
        mean_variance_percent = sum(variance_percents) / len(variance_percents)

        # Assess bias
        if optimistic_count >= (total_periods * 0.75):
            bias = BiasIndicator.OPTIMISTIC
            bias_description = "Management consistently underestimates (too optimistic)"
        elif pessimistic_count >= (total_periods * 0.75):
            bias = BiasIndicator.PESSIMISTIC
            bias_description = "Management consistently overestimates (too conservative)"
        elif abs(optimistic_count - pessimistic_count) <= 1:
            bias = BiasIndicator.NEUTRAL
            bias_description = "No apparent directional bias"
        else:
            bias = BiasIndicator.INCONSISTENT
            bias_description = "Bias direction varies period to period"

        # Assess accuracy
        avg_absolute_variance = sum(abs(v) for v in variance_percents) / len(variance_percents)

        if avg_absolute_variance < 5:
            accuracy = "EXCELLENT"
        elif avg_absolute_variance < 10:
            accuracy = "GOOD"
        elif avg_absolute_variance < 20:
            accuracy = "MODERATE"
        else:
            accuracy = "POOR"

        return {
            "sufficient_history": True,
            "periods_analyzed": total_periods,
            "variances": variances,
            "mean_variance": round(float(mean_variance), 2),
            "mean_variance_percent": round(float(mean_variance_percent), 2),
            "average_absolute_variance_percent": round(float(avg_absolute_variance), 2),
            "optimistic_periods": optimistic_count,
            "pessimistic_periods": pessimistic_count,
            "bias_indicator": bias.value,
            "bias_description": bias_description,
            "historical_accuracy": accuracy,
            "audit_implication": self._get_bias_audit_implication(bias, accuracy),
        }

    def test_sensitivity_analysis(
        self,
        base_estimate: Decimal,
        key_assumptions: List[Dict],  # [{"name": "discount_rate", "base": 0.10, "sensitivity": 0.01}]
    ) -> Dict:
        """
        Perform sensitivity analysis on key assumptions.

        Tests how changes in assumptions affect the estimate.
        High sensitivity = higher risk and more audit focus needed.

        Args:
            base_estimate: Management's base case estimate
            key_assumptions: List of assumptions with sensitivity ranges

        Returns:
            Sensitivity analysis results
        """
        sensitivities = []

        for assumption in key_assumptions:
            name = assumption["name"]
            base_value = Decimal(str(assumption["base"]))
            sensitivity_range = Decimal(str(assumption["sensitivity"]))

            # Calculate +/- sensitivity
            # This is simplified - real analysis would recalculate estimate with assumption change
            # For demonstration, assume linear relationship
            estimated_impact_percent = sensitivity_range / base_value * 100 if base_value != 0 else 0

            # High/low scenarios
            high_scenario = base_estimate * (1 + estimated_impact_percent / 100)
            low_scenario = base_estimate * (1 - estimated_impact_percent / 100)
            total_range = high_scenario - low_scenario

            sensitivities.append({
                "assumption_name": name,
                "base_value": float(base_value),
                "sensitivity_range": float(sensitivity_range),
                "high_scenario_estimate": round(float(high_scenario), 2),
                "low_scenario_estimate": round(float(low_scenario), 2),
                "total_range": round(float(total_range), 2),
                "range_as_percent_of_base": round(float(total_range / base_estimate * 100), 2),
            })

        # Overall sensitivity assessment
        max_sensitivity = max(s["range_as_percent_of_base"] for s in sensitivities)

        if max_sensitivity > 50:
            sensitivity_level = "VERY_HIGH"
            risk_assessment = "HIGH"
            recommendation = "Estimate is very sensitive to key assumptions. Consider specialist involvement."
        elif max_sensitivity > 25:
            sensitivity_level = "HIGH"
            risk_assessment = "MODERATE_TO_HIGH"
            recommendation = "Significant sensitivity. Expand testing of key assumptions."
        elif max_sensitivity > 10:
            sensitivity_level = "MODERATE"
            risk_assessment = "MODERATE"
            recommendation = "Moderate sensitivity. Standard testing procedures appropriate."
        else:
            sensitivity_level = "LOW"
            risk_assessment = "LOW"
            recommendation = "Low sensitivity. Estimate is relatively robust to assumption changes."

        return {
            "base_estimate": float(base_estimate),
            "sensitivities": sensitivities,
            "max_sensitivity_percent": round(max_sensitivity, 2),
            "sensitivity_level": sensitivity_level,
            "risk_assessment": risk_assessment,
            "audit_recommendation": recommendation,
        }

    def evaluate_model_validation(
        self,
        model_type: str,
        has_independent_validation: bool,
        validation_frequency: str,  # "annual", "quarterly", "none"
        back_testing_results: Optional[str] = None,  # "passed", "failed", "not_performed"
        uses_market_data: bool = True,
        model_age_years: int = 0,
    ) -> Dict:
        """
        Evaluate the validation of management's valuation model.

        AS 2501.19: Auditor should evaluate company's process for
        validating models used in estimates.

        Args:
            model_type: Type of model (DCF, Monte Carlo, Black-Scholes, etc.)
            has_independent_validation: Independent party validates model
            validation_frequency: How often model is validated
            back_testing_results: Results of back-testing against actuals
            uses_market_data: Uses observable market data (vs unobservable)
            model_age_years: Years since model developed/updated

        Returns:
            Model validation assessment
        """
        risk_score = 0

        # Independent validation
        if not has_independent_validation:
            risk_score += 2
            validation_concerns = ["No independent validation"]
        else:
            validation_concerns = []

        # Validation frequency
        if validation_frequency == "none":
            risk_score += 3
            validation_concerns.append("Model not regularly validated")
        elif validation_frequency == "annual" and model_age_years > 3:
            risk_score += 1
            validation_concerns.append("Model validation may be stale")

        # Back-testing
        if back_testing_results == "failed":
            risk_score += 3
            validation_concerns.append("Back-testing shows poor predictive accuracy")
        elif back_testing_results == "not_performed":
            risk_score += 1
            validation_concerns.append("No back-testing performed")

        # Data sources
        if not uses_market_data:
            risk_score += 1
            validation_concerns.append("Relies on unobservable inputs")

        # Model age
        if model_age_years > 5:
            risk_score += 1
            validation_concerns.append("Model is outdated (>5 years old)")

        # Overall assessment
        if risk_score >= 6:
            overall_assessment = "HIGH_RISK"
            recommendation = "Engage valuation specialist to validate model"
        elif risk_score >= 3:
            overall_assessment = "MODERATE_RISK"
            recommendation = "Expand testing of model inputs and assumptions"
        else:
            overall_assessment = "LOW_RISK"
            recommendation = "Standard testing procedures appropriate"

        return {
            "model_type": model_type,
            "risk_score": risk_score,
            "risk_factors_identified": len(validation_concerns),
            "validation_concerns": validation_concerns if validation_concerns else ["None identified"],
            "overall_assessment": overall_assessment,
            "audit_recommendation": recommendation,
            "specialist_recommended": risk_score >= 6,
        }

    # Private helper methods

    def _get_bias_audit_implication(self, bias: BiasIndicator, accuracy: str) -> str:
        """Get audit implications based on bias and accuracy assessment"""
        if bias == BiasIndicator.OPTIMISTIC and accuracy in ["POOR", "MODERATE"]:
            return "High risk: Management consistently overestimates favorable outcomes. Increase skepticism and expand testing."
        elif bias == BiasIndicator.OPTIMISTIC:
            return "Moderate risk: Management tends toward optimistic assumptions. Review current period assumptions for continued bias."
        elif bias == BiasIndicator.PESSIMISTIC and accuracy in ["POOR", "MODERATE"]:
            return "Moderate risk: Management may be building 'cookie jar' reserves. Review reasonableness of conservative assumptions."
        elif bias == BiasIndicator.INCONSISTENT:
            return "Moderate risk: Inconsistent bias may indicate earnings management. Investigate reasons for variance pattern changes."
        elif accuracy == "POOR":
            return "Moderate risk: Poor historical accuracy indicates weak estimation process. Expand procedures and consider developing independent expectation."
        else:
            return "Low risk: No significant bias and good historical accuracy. Standard procedures appropriate."
