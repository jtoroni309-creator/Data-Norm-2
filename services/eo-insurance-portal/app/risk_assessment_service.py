"""
E&O Risk Assessment Service

Evaluates CPA firm risk profiles and platform effectiveness for reducing E&O liability.

Key Functions:
- Assess CPA firm risk based on historical data
- Calculate potential premium reductions with platform adoption
- Generate underwriting reports
- Track platform ROI for reducing claims
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk level classifications"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class FirmSize(str, Enum):
    """CPA firm size categories"""
    SOLE_PRACTITIONER = "sole_practitioner"
    SMALL = "small"  # 2-10 professionals
    MEDIUM = "medium"  # 11-50 professionals
    LARGE = "large"  # 51-200 professionals
    NATIONAL = "national"  # 200+ professionals


class RiskAssessmentService:
    """
    Comprehensive risk assessment for E&O underwriting.

    Evaluates:
    - Historical claims data
    - Platform detection accuracy
    - Potential premium reductions
    - Firm risk profiles
    """

    def __init__(self):
        # Industry benchmarks for E&O claims (per $1M revenue)
        self.industry_benchmarks = {
            "claim_frequency": {
                "sole_practitioner": 0.08,  # 8 claims per 100 firms
                "small": 0.06,
                "medium": 0.05,
                "large": 0.04,
                "national": 0.03,
            },
            "average_claim_amount": {
                "sole_practitioner": 150000,
                "small": 250000,
                "medium": 500000,
                "large": 1000000,
                "national": 2000000,
            },
            "base_premium_rate": {  # % of revenue
                "sole_practitioner": 0.04,  # 4%
                "small": 0.035,
                "medium": 0.03,
                "large": 0.025,
                "national": 0.02,
            }
        }

    def assess_firm_risk(
        self,
        firm_profile: Dict[str, Any],
        claims_history: List[Dict[str, Any]],
        platform_usage: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Assess CPA firm risk profile.

        Args:
            firm_profile: Firm information (size, revenue, specialties, etc.)
            claims_history: Historical E&O claims
            platform_usage: Platform adoption details (if using)

        Returns:
            Comprehensive risk assessment
        """
        firm_size = firm_profile.get("size", "small")
        annual_revenue = Decimal(str(firm_profile.get("annual_revenue", 1000000)))
        years_in_practice = firm_profile.get("years_in_practice", 5)

        # Calculate base risk score
        base_risk_score = self._calculate_base_risk(
            firm_size, annual_revenue, years_in_practice
        )

        # Adjust for claims history
        claims_adjustment = self._assess_claims_history(claims_history)

        # Adjust for platform usage
        platform_adjustment = 0
        if platform_usage and platform_usage.get("is_using_platform", False):
            platform_adjustment = self._calculate_platform_benefit(
                platform_usage
            )

        # Calculate final risk score
        final_risk_score = base_risk_score + claims_adjustment - platform_adjustment
        final_risk_score = max(0, min(100, final_risk_score))  # Clamp to 0-100

        # Determine risk level
        risk_level = self._determine_risk_level(final_risk_score)

        # Calculate recommended premium
        recommended_premium = self._calculate_premium(
            annual_revenue,
            firm_size,
            final_risk_score,
            platform_usage is not None
        )

        return {
            "firm_id": firm_profile.get("firm_id"),
            "assessment_date": datetime.utcnow().isoformat(),
            "risk_score": round(final_risk_score, 2),
            "risk_level": risk_level.value,
            "components": {
                "base_risk_score": round(base_risk_score, 2),
                "claims_adjustment": round(claims_adjustment, 2),
                "platform_adjustment": round(platform_adjustment, 2),
            },
            "recommended_premium": {
                "annual_premium": float(recommended_premium),
                "premium_rate": float((recommended_premium / annual_revenue) * 100),
            },
            "risk_factors": self._identify_risk_factors(
                firm_profile, claims_history, final_risk_score
            ),
            "recommendations": self._generate_recommendations(
                risk_level, platform_usage
            ),
        }

    def _calculate_base_risk(
        self,
        firm_size: str,
        annual_revenue: Decimal,
        years_in_practice: int
    ) -> float:
        """Calculate base risk score."""
        # Start with moderate risk
        base_score = 50

        # Adjust for firm size (smaller = higher risk)
        size_risk = {
            "sole_practitioner": 10,
            "small": 5,
            "medium": 0,
            "large": -5,
            "national": -10,
        }
        base_score += size_risk.get(firm_size, 0)

        # Adjust for experience (newer = higher risk)
        if years_in_practice < 3:
            base_score += 15
        elif years_in_practice < 5:
            base_score += 10
        elif years_in_practice < 10:
            base_score += 5
        elif years_in_practice > 20:
            base_score -= 5

        return base_score

    def _assess_claims_history(
        self,
        claims_history: List[Dict[str, Any]]
    ) -> float:
        """Assess risk adjustment from claims history."""
        if not claims_history:
            return 0  # No claims = no adjustment

        # Recent claims (last 5 years) matter more
        recent_cutoff = datetime.utcnow() - timedelta(days=365 * 5)
        recent_claims = [
            claim for claim in claims_history
            if datetime.fromisoformat(claim["claim_date"]) > recent_cutoff
        ]

        # Calculate adjustment
        adjustment = 0

        # Number of claims
        if len(recent_claims) == 0:
            adjustment -= 5  # No recent claims = lower risk
        elif len(recent_claims) == 1:
            adjustment += 5
        elif len(recent_claims) == 2:
            adjustment += 10
        else:
            adjustment += 15  # Multiple claims = much higher risk

        # Claim severity
        for claim in recent_claims:
            amount = Decimal(str(claim.get("settlement_amount", 0)))
            if amount > 1000000:
                adjustment += 10  # Large claim
            elif amount > 500000:
                adjustment += 5
            elif amount > 100000:
                adjustment += 2

        return adjustment

    def _calculate_platform_benefit(
        self,
        platform_usage: Dict[str, Any]
    ) -> float:
        """Calculate risk reduction from platform usage."""
        if not platform_usage.get("is_using_platform", False):
            return 0

        benefit = 0

        # Base benefit for platform adoption
        benefit += 15

        # Additional benefit for full adoption
        adoption_rate = platform_usage.get("adoption_rate", 0)  # 0-100%
        if adoption_rate >= 90:
            benefit += 10
        elif adoption_rate >= 75:
            benefit += 5

        # Benefit for platform accuracy
        platform_accuracy = platform_usage.get("platform_accuracy", 0)  # 0-100%
        if platform_accuracy >= 95:
            benefit += 10
        elif platform_accuracy >= 90:
            benefit += 5

        # Benefit for time using platform
        months_using = platform_usage.get("months_using_platform", 0)
        if months_using >= 24:
            benefit += 5
        elif months_using >= 12:
            benefit += 3

        return min(benefit, 40)  # Cap at 40% reduction

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score."""
        if risk_score < 20:
            return RiskLevel.VERY_LOW
        elif risk_score < 40:
            return RiskLevel.LOW
        elif risk_score < 60:
            return RiskLevel.MODERATE
        elif risk_score < 80:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    def _calculate_premium(
        self,
        annual_revenue: Decimal,
        firm_size: str,
        risk_score: float,
        using_platform: bool
    ) -> Decimal:
        """Calculate recommended E&O premium."""
        # Get base rate
        base_rate = Decimal(str(self.industry_benchmarks["base_premium_rate"].get(firm_size, 0.03)))

        # Adjust for risk score
        risk_multiplier = Decimal(str(risk_score / 50))  # 50 is baseline

        # Platform discount
        platform_discount = Decimal("0.20") if using_platform else Decimal("0")

        # Calculate premium
        premium = annual_revenue * base_rate * risk_multiplier
        premium = premium * (Decimal("1") - platform_discount)

        return premium

    def _identify_risk_factors(
        self,
        firm_profile: Dict[str, Any],
        claims_history: List[Dict[str, Any]],
        risk_score: float
    ) -> List[Dict[str, str]]:
        """Identify specific risk factors."""
        risk_factors = []

        # Check claims history
        if len(claims_history) > 0:
            risk_factors.append({
                "factor": "previous_claims",
                "severity": "high" if len(claims_history) > 2 else "moderate",
                "description": f"{len(claims_history)} previous E&O claim(s)",
            })

        # Check firm size
        if firm_profile.get("size") == "sole_practitioner":
            risk_factors.append({
                "factor": "sole_practitioner",
                "severity": "moderate",
                "description": "Sole practitioner - limited peer review",
            })

        # Check practice areas
        high_risk_areas = ["public_company_audits", "broker_dealer_audits", "sec_filings"]
        for area in high_risk_areas:
            if area in firm_profile.get("practice_areas", []):
                risk_factors.append({
                    "factor": "high_risk_practice_area",
                    "severity": "high",
                    "description": f"High-risk practice area: {area}",
                })

        return risk_factors

    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        platform_usage: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []

        # Platform adoption recommendation
        if not platform_usage or not platform_usage.get("is_using_platform"):
            recommendations.append(
                "Consider adopting Aura Audit AI platform for enhanced quality control "
                "and potential 20% premium reduction"
            )

        # Risk-specific recommendations
        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.append("Implement enhanced peer review procedures")
            recommendations.append("Consider additional CPE training in high-risk areas")
            recommendations.append("Strengthen client acceptance procedures")

        if risk_level == RiskLevel.VERY_HIGH:
            recommendations.append("Recommend risk management consultation")
            recommendations.append("Consider limiting high-risk engagements")

        return recommendations

    def calculate_roi(
        self,
        current_premium: Decimal,
        platform_cost: Decimal,
        expected_accuracy: float
    ) -> Dict[str, Any]:
        """
        Calculate ROI of platform adoption for reducing E&O premiums.

        Args:
            current_premium: Current annual E&O premium
            platform_cost: Annual platform subscription cost
            expected_accuracy: Expected platform detection accuracy (0-100)

        Returns:
            ROI analysis
        """
        # Estimate premium reduction based on platform adoption
        # Conservative estimate: 15-25% reduction for 90%+ accuracy
        if expected_accuracy >= 95:
            premium_reduction_pct = Decimal("0.25")
        elif expected_accuracy >= 90:
            premium_reduction_pct = Decimal("0.20")
        elif expected_accuracy >= 85:
            premium_reduction_pct = Decimal("0.15")
        else:
            premium_reduction_pct = Decimal("0.10")

        premium_savings = current_premium * premium_reduction_pct
        net_savings = premium_savings - platform_cost

        # Calculate payback period
        if net_savings > 0:
            roi_percentage = (net_savings / platform_cost) * 100
            payback_months = 12
        else:
            roi_percentage = ((premium_savings - platform_cost) / platform_cost) * 100
            payback_months = 0 if premium_savings == 0 else int((platform_cost / premium_savings) * 12)

        # Calculate 5-year savings
        five_year_savings = (premium_savings - platform_cost) * 5

        return {
            "current_annual_premium": float(current_premium),
            "platform_annual_cost": float(platform_cost),
            "premium_reduction_percentage": float(premium_reduction_pct * 100),
            "annual_premium_savings": float(premium_savings),
            "annual_net_savings": float(net_savings),
            "roi_percentage": float(roi_percentage),
            "payback_period_months": payback_months,
            "five_year_total_savings": float(five_year_savings),
            "recommendation": "Highly recommended" if net_savings > 0 else "Consider based on other benefits",
        }

    def generate_underwriting_report(
        self,
        firm_assessment: Dict[str, Any],
        platform_performance: Dict[str, Any],
        test_case_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive underwriting report for insurance company.

        Args:
            firm_assessment: Firm risk assessment
            platform_performance: Platform performance metrics
            test_case_results: Test case validation results

        Returns:
            Underwriting report
        """
        # Calculate platform effectiveness score
        platform_effectiveness = self._calculate_platform_effectiveness(
            platform_performance,
            test_case_results
        )

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            firm_assessment,
            platform_effectiveness
        )

        return {
            "report_id": str(uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "executive_summary": executive_summary,
            "firm_risk_assessment": firm_assessment,
            "platform_effectiveness": platform_effectiveness,
            "test_case_summary": self._summarize_test_cases(test_case_results),
            "premium_recommendation": {
                "current_risk_based_premium": firm_assessment["recommended_premium"],
                "with_platform_premium": self._calculate_with_platform_premium(
                    firm_assessment
                ),
                "estimated_savings": self._calculate_estimated_savings(
                    firm_assessment
                ),
            },
            "underwriting_decision": self._make_underwriting_decision(
                firm_assessment,
                platform_effectiveness
            ),
        }

    def _calculate_platform_effectiveness(
        self,
        platform_performance: Dict[str, Any],
        test_case_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate platform effectiveness score."""
        accuracy = platform_performance.get("overall_accuracy", 0)
        detection_rate = platform_performance.get("detection_rate", 0)
        false_negative_rate = platform_performance.get("false_negative_rate", 0)

        # Effectiveness score (0-100)
        # Heavily weight detection rate and penalize false negatives
        effectiveness_score = (
            (accuracy * 0.3) +
            (detection_rate * 0.5) +
            ((100 - false_negative_rate) * 0.2)
        )

        return {
            "effectiveness_score": round(effectiveness_score, 2),
            "accuracy": accuracy,
            "detection_rate": detection_rate,
            "false_negative_rate": false_negative_rate,
            "rating": self._rate_effectiveness(effectiveness_score),
        }

    def _rate_effectiveness(self, score: float) -> str:
        """Rate platform effectiveness."""
        if score >= 95:
            return "Exceptional"
        elif score >= 90:
            return "Excellent"
        elif score >= 85:
            return "Very Good"
        elif score >= 80:
            return "Good"
        else:
            return "Acceptable"

    def _generate_executive_summary(
        self,
        firm_assessment: Dict[str, Any],
        platform_effectiveness: Dict[str, Any]
    ) -> str:
        """Generate executive summary."""
        risk_level = firm_assessment["risk_level"]
        effectiveness_rating = platform_effectiveness["rating"]

        summary = f"Risk Assessment: {risk_level.upper()}. "
        summary += f"Platform Effectiveness: {effectiveness_rating}. "

        if platform_effectiveness["effectiveness_score"] >= 90:
            summary += "Platform demonstrates exceptional ability to detect audit failures. "
            summary += "Recommend 20-25% premium reduction for firms using platform."
        elif platform_effectiveness["effectiveness_score"] >= 85:
            summary += "Platform shows strong detection capabilities. "
            summary += "Recommend 15-20% premium reduction for firms using platform."

        return summary

    def _summarize_test_cases(
        self,
        test_case_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize test case results."""
        if not test_case_results:
            return {"total_cases": 0}

        total = len(test_case_results)
        detected = sum(1 for r in test_case_results if r.get("platform_detected", False))

        return {
            "total_test_cases": total,
            "correctly_detected": detected,
            "detection_rate": round((detected / total * 100) if total > 0 else 0, 2),
            "failure_types_tested": list(set(r.get("failure_type") for r in test_case_results)),
        }

    def _calculate_with_platform_premium(
        self,
        firm_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate premium with platform discount."""
        current_premium = Decimal(str(firm_assessment["recommended_premium"]["annual_premium"]))
        discount = Decimal("0.20")  # 20% discount

        with_platform = current_premium * (Decimal("1") - discount)

        return {
            "annual_premium": float(with_platform),
            "discount_applied": "20%",
        }

    def _calculate_estimated_savings(
        self,
        firm_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate estimated savings."""
        current = Decimal(str(firm_assessment["recommended_premium"]["annual_premium"]))
        with_platform = current * Decimal("0.80")  # 20% discount
        annual_savings = current - with_platform

        return {
            "annual_savings": float(annual_savings),
            "five_year_savings": float(annual_savings * 5),
        }

    def _make_underwriting_decision(
        self,
        firm_assessment: Dict[str, Any],
        platform_effectiveness: Dict[str, Any]
    ) -> Dict[str, str]:
        """Make underwriting decision."""
        risk_level = firm_assessment["risk_level"]
        effectiveness = platform_effectiveness["effectiveness_score"]

        if risk_level in ["very_high", "high"] and effectiveness < 85:
            decision = "DECLINE"
            reason = "High risk profile and insufficient platform effectiveness"
        elif risk_level == "very_high":
            decision = "CONDITIONAL_APPROVAL"
            reason = "Approve only if firm adopts platform with 90%+ accuracy"
        elif risk_level == "high":
            decision = "APPROVE_WITH_CONDITIONS"
            reason = "Approve with platform adoption requirement"
        else:
            decision = "APPROVE"
            reason = "Acceptable risk profile"

        return {
            "decision": decision,
            "reason": reason,
        }


class RiskAssessmentError(Exception):
    """Raised when risk assessment fails"""
    pass
