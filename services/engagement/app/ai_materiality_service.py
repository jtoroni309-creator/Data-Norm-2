"""
AI-Enhanced Materiality Service

Provides intelligent, risk-adjusted materiality calculations using:
- AI-powered dynamic materiality adjustment based on risk profile
- Industry-specific benchmarking and context
- Integration with risk assessment results
- Historical pattern analysis
- Engagement-specific factors
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from openai import AsyncOpenAI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings

logger = logging.getLogger(__name__)


class AIMaterialityService:
    """
    AI-powered materiality calculation service that enhances traditional
    materiality thresholds with intelligent risk-based adjustments.
    """

    def __init__(self):
        """Initialize with OpenAI client for AI-powered analysis"""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = getattr(settings, 'OPENAI_CHAT_MODEL', 'gpt-4-turbo-preview')

        # Default thresholds (configurable)
        self.default_materiality_pct = Decimal(str(getattr(settings, 'DEFAULT_MATERIALITY_PERCENTAGE', 0.05)))
        self.performance_materiality_pct = Decimal(str(getattr(settings, 'PERFORMANCE_MATERIALITY_PERCENTAGE', 0.75)))
        self.trivial_threshold_pct = Decimal(str(getattr(settings, 'TRIVIAL_THRESHOLD_PERCENTAGE', 0.05)))

        logger.info("AI Materiality Service initialized")

    async def calculate_ai_enhanced_materiality(
        self,
        db: AsyncSession,
        engagement_id: UUID,
        financial_statements: Dict[str, Any],
        risk_assessment: Optional[Dict[str, Any]] = None,
        industry: Optional[str] = None,
        prior_period_statements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate AI-enhanced materiality with risk-based adjustments.

        Args:
            db: Database session
            engagement_id: Engagement ID
            financial_statements: Current period financial statements
            risk_assessment: Risk assessment results (if available)
            industry: Industry classification (e.g., 'Manufacturing', 'Technology')
            prior_period_statements: Prior period statements for trend analysis

        Returns:
            Comprehensive materiality analysis with AI recommendations
        """
        logger.info(f"Calculating AI-enhanced materiality for engagement {engagement_id}")

        # Step 1: Calculate base materiality using traditional methods
        base_materiality = self._calculate_base_materiality(financial_statements)

        # Step 2: Assess risk factors that influence materiality
        risk_factors = await self._assess_materiality_risk_factors(
            financial_statements,
            risk_assessment,
            industry,
            prior_period_statements
        )

        # Step 3: Use AI to determine appropriate materiality adjustments
        ai_adjustment = await self._ai_determine_materiality_adjustment(
            base_materiality,
            risk_factors,
            financial_statements,
            risk_assessment,
            industry
        )

        # Step 4: Calculate adjusted materiality levels
        adjusted_materiality = self._apply_adjustments(
            base_materiality,
            ai_adjustment
        )

        # Step 5: Get industry benchmarks for comparison
        industry_benchmarks = await self._get_industry_benchmarks(
            db,
            industry,
            financial_statements
        )

        # Step 6: Generate AI-powered insights and recommendations
        insights = await self._generate_materiality_insights(
            base_materiality,
            adjusted_materiality,
            risk_factors,
            ai_adjustment,
            industry_benchmarks
        )

        # Compile comprehensive result
        result = {
            "engagement_id": str(engagement_id),
            "calculation_date": datetime.utcnow().isoformat(),

            # Base calculations
            "base_materiality": {
                "basis": base_materiality["basis"],
                "base_amount": float(base_materiality["base_amount"]),
                "materiality": float(base_materiality["materiality"]),
                "performance_materiality": float(base_materiality["performance_materiality"]),
                "trivial_threshold": float(base_materiality["trivial_threshold"]),
                "percentage_used": float(base_materiality["percentage_used"])
            },

            # AI-enhanced calculations
            "ai_adjusted_materiality": {
                "materiality": float(adjusted_materiality["materiality"]),
                "performance_materiality": float(adjusted_materiality["performance_materiality"]),
                "trivial_threshold": float(adjusted_materiality["trivial_threshold"]),
                "adjustment_factor": ai_adjustment["adjustment_factor"],
                "adjustment_direction": ai_adjustment["adjustment_direction"],
                "confidence_score": ai_adjustment["confidence_score"]
            },

            # Risk factors influencing materiality
            "risk_factors": risk_factors,

            # AI reasoning
            "ai_analysis": {
                "recommendation": ai_adjustment["recommendation"],
                "reasoning": ai_adjustment["reasoning"],
                "key_considerations": ai_adjustment["key_considerations"],
                "industry_context": ai_adjustment.get("industry_context", "")
            },

            # Industry comparison
            "industry_benchmarks": industry_benchmarks,

            # Actionable insights
            "insights": insights,

            # Overall recommendation
            "recommended_materiality": float(adjusted_materiality["materiality"]),
            "recommended_performance_materiality": float(adjusted_materiality["performance_materiality"]),
            "recommended_trivial_threshold": float(adjusted_materiality["trivial_threshold"])
        }

        logger.info(
            f"AI materiality calculation complete: "
            f"Base ${base_materiality['materiality']:,.0f} → "
            f"Adjusted ${adjusted_materiality['materiality']:,.0f} "
            f"({ai_adjustment['adjustment_direction']} {abs(ai_adjustment['adjustment_factor'] - 1.0) * 100:.1f}%)"
        )

        return result

    def _calculate_base_materiality(
        self,
        statements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate traditional rule-based materiality.

        Uses standard benchmarks:
        - Net income > 0: 5% of net income
        - Revenue > 0: 0.5-1% of revenue
        - Otherwise: 1-2% of total assets
        """
        revenue = Decimal(str(statements.get("income_statement", {}).get("revenue", 0) or 0))
        total_assets = Decimal(str(statements.get("balance_sheet", {}).get("total_assets", 0) or 0))
        net_income = Decimal(str(statements.get("income_statement", {}).get("net_income", 0) or 0))

        # Determine best basis
        if net_income > 0:
            basis = "net_income"
            base_amount = net_income
            percentage = self.default_materiality_pct  # 5%
        elif revenue > 0:
            basis = "revenue"
            base_amount = revenue
            percentage = Decimal("0.01")  # 1% for revenue
        else:
            basis = "total_assets"
            base_amount = total_assets
            percentage = Decimal("0.015")  # 1.5% for assets

        materiality = base_amount * percentage
        performance_materiality = materiality * self.performance_materiality_pct
        trivial_threshold = materiality * self.trivial_threshold_pct

        return {
            "basis": basis,
            "base_amount": base_amount,
            "materiality": materiality,
            "performance_materiality": performance_materiality,
            "trivial_threshold": trivial_threshold,
            "percentage_used": percentage * 100
        }

    async def _assess_materiality_risk_factors(
        self,
        financial_statements: Dict[str, Any],
        risk_assessment: Optional[Dict[str, Any]],
        industry: Optional[str],
        prior_period_statements: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess risk factors that influence materiality judgment.

        Factors considered:
        - Financial volatility (earnings variability)
        - Liquidity concerns
        - Going concern indicators
        - Industry-specific risks
        - Trend deterioration
        - Complexity of operations
        """
        factors = {
            "overall_risk_level": "low",
            "factors": []
        }

        # Factor 1: Earnings volatility
        if prior_period_statements:
            current_ni = Decimal(str(financial_statements.get("income_statement", {}).get("net_income", 0) or 0))
            prior_ni = Decimal(str(prior_period_statements.get("income_statement", {}).get("net_income", 1) or 1))

            if prior_ni != 0:
                ni_change_pct = float((current_ni - prior_ni) / abs(prior_ni) * 100)
                if abs(ni_change_pct) > 20:
                    factors["factors"].append({
                        "type": "earnings_volatility",
                        "severity": "high" if abs(ni_change_pct) > 50 else "medium",
                        "description": f"Earnings volatility: {ni_change_pct:+.1f}% change",
                        "impact_on_materiality": "Lower materiality appropriate due to volatility"
                    })

        # Factor 2: Liquidity risk
        balance_sheet = financial_statements.get("balance_sheet", {})
        current_assets = Decimal(str(balance_sheet.get("current_assets", 0) or 0))
        current_liabilities = Decimal(str(balance_sheet.get("current_liabilities", 1) or 1))

        if current_liabilities > 0:
            current_ratio = float(current_assets / current_liabilities)
            if current_ratio < 1.0:
                factors["factors"].append({
                    "type": "liquidity_risk",
                    "severity": "high",
                    "description": f"Current ratio of {current_ratio:.2f} indicates liquidity concerns",
                    "impact_on_materiality": "Lower materiality to capture potential misstatements"
                })

        # Factor 3: Use risk assessment if provided
        if risk_assessment:
            overall_risk = risk_assessment.get("overall_risk_level", "low")
            risk_score = risk_assessment.get("risk_score", 0.0)

            factors["overall_risk_level"] = overall_risk

            if risk_score > 0.5:
                factors["factors"].append({
                    "type": "high_engagement_risk",
                    "severity": overall_risk,
                    "description": f"Overall engagement risk score: {risk_score:.2f}",
                    "impact_on_materiality": "Lower materiality appropriate for higher risk engagements"
                })

        # Factor 4: Industry-specific risks
        if industry:
            high_risk_industries = ["Technology", "Biotech", "Cryptocurrency", "Startups"]
            if any(high_risk in industry for high_risk in high_risk_industries):
                factors["factors"].append({
                    "type": "industry_risk",
                    "severity": "medium",
                    "description": f"Industry '{industry}' has inherent complexity and risk",
                    "impact_on_materiality": "May warrant lower materiality for complex transactions"
                })

        return factors

    async def _ai_determine_materiality_adjustment(
        self,
        base_materiality: Dict[str, Any],
        risk_factors: Dict[str, Any],
        financial_statements: Dict[str, Any],
        risk_assessment: Optional[Dict[str, Any]],
        industry: Optional[str]
    ) -> Dict[str, Any]:
        """
        Use AI to determine appropriate materiality adjustments based on risk profile.

        Returns:
            Adjustment factor, reasoning, and recommendations
        """
        prompt = f"""You are an experienced audit partner determining appropriate materiality for an audit engagement.

BASE MATERIALITY CALCULATION:
- Basis: {base_materiality['basis']}
- Base amount: ${base_materiality['base_amount']:,.0f}
- Calculated materiality: ${base_materiality['materiality']:,.0f}
- Percentage used: {base_materiality['percentage_used']:.2f}%

RISK FACTORS:
Overall Risk Level: {risk_factors.get('overall_risk_level', 'N/A')}

Identified Risk Factors:
{self._format_risk_factors(risk_factors['factors'])}

FINANCIAL CONTEXT:
Revenue: ${financial_statements.get('income_statement', {}).get('revenue', 0):,.0f}
Net Income: ${financial_statements.get('income_statement', {}).get('net_income', 0):,.0f}
Total Assets: ${financial_statements.get('balance_sheet', {}).get('total_assets', 0):,.0f}
Industry: {industry or 'Not specified'}

TASK:
Based on professional judgment and PCAOB/AICPA standards, determine if the base materiality should be adjusted.

Consider:
1. Does the risk profile warrant a more conservative (lower) materiality?
2. Are there user considerations (financial stability, low risk) that support higher materiality?
3. What is the appropriate adjustment factor (typically 0.7 to 1.3)?
4. What specific factors drive your recommendation?

Respond in JSON format:
{{
  "adjustment_factor": 0.XX (0.7 = 30% lower, 1.0 = no change, 1.3 = 30% higher),
  "adjustment_direction": "decrease|neutral|increase",
  "confidence_score": 0.XX (0.0 to 1.0),
  "recommendation": "Brief recommendation (1-2 sentences)",
  "reasoning": "Detailed reasoning for the adjustment (3-4 sentences)",
  "key_considerations": ["consideration 1", "consideration 2", "consideration 3"],
  "industry_context": "Industry-specific considerations affecting materiality"
}}

Professional standards guidance:
- Higher risk → Lower materiality (more items examined)
- Stable, low-risk entities → May support higher materiality within reason
- Adjustment factors typically range from 0.7x to 1.3x of base materiality
- Must maintain professional skepticism and audit quality"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert audit partner with deep knowledge of materiality determination per AU-C 320 and AS 2105. Provide professional, conservative recommendations that prioritize audit quality."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Low temperature for consistency
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)

            # Validate adjustment factor is reasonable
            adjustment_factor = result.get("adjustment_factor", 1.0)
            if adjustment_factor < 0.5 or adjustment_factor > 1.5:
                logger.warning(f"AI suggested extreme adjustment factor {adjustment_factor}, capping to reasonable range")
                adjustment_factor = max(0.7, min(1.3, adjustment_factor))
                result["adjustment_factor"] = adjustment_factor

            return result

        except Exception as e:
            logger.error(f"Error in AI materiality adjustment: {e}")
            # Fallback to rule-based adjustment
            return self._fallback_risk_adjustment(risk_factors)

    def _fallback_risk_adjustment(
        self,
        risk_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback rule-based adjustment if AI fails"""
        overall_risk = risk_factors.get("overall_risk_level", "low")
        num_high_risk_factors = len([f for f in risk_factors.get("factors", []) if f.get("severity") == "high"])

        if overall_risk in ["critical", "high"] or num_high_risk_factors >= 2:
            adjustment_factor = 0.8  # 20% lower
            direction = "decrease"
            recommendation = "Lower materiality recommended due to elevated risk factors"
        elif num_high_risk_factors == 1:
            adjustment_factor = 0.9  # 10% lower
            direction = "decrease"
            recommendation = "Slightly lower materiality due to identified risk factor"
        else:
            adjustment_factor = 1.0
            direction = "neutral"
            recommendation = "Base materiality appropriate given risk profile"

        return {
            "adjustment_factor": adjustment_factor,
            "adjustment_direction": direction,
            "confidence_score": 0.7,
            "recommendation": recommendation,
            "reasoning": "Rule-based adjustment applied based on risk factor count and severity",
            "key_considerations": ["Risk factor count", "Overall risk level", "Standard materiality guidelines"],
            "industry_context": ""
        }

    def _apply_adjustments(
        self,
        base_materiality: Dict[str, Any],
        ai_adjustment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply AI-recommended adjustments to base materiality"""
        adjustment_factor = Decimal(str(ai_adjustment["adjustment_factor"]))

        adjusted_materiality = base_materiality["materiality"] * adjustment_factor
        adjusted_performance = adjusted_materiality * self.performance_materiality_pct
        adjusted_trivial = adjusted_materiality * self.trivial_threshold_pct

        return {
            "materiality": adjusted_materiality,
            "performance_materiality": adjusted_performance,
            "trivial_threshold": adjusted_trivial,
            "adjustment_applied": adjustment_factor
        }

    async def _get_industry_benchmarks(
        self,
        db: AsyncSession,
        industry: Optional[str],
        financial_statements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Retrieve industry benchmarks for materiality comparison.

        In production, this would query a database of industry statistics.
        For now, we provide standard ranges.
        """
        # Standard materiality ranges by basis
        benchmarks = {
            "materiality_ranges": {
                "net_income_based": "3-7% of net income",
                "revenue_based": "0.5-2% of revenue",
                "asset_based": "1-3% of total assets"
            },
            "industry": industry or "General",
            "typical_adjustment_factors": {
                "low_risk": "1.0-1.2x base materiality",
                "moderate_risk": "0.9-1.0x base materiality",
                "high_risk": "0.7-0.9x base materiality"
            }
        }

        # In production: Query historical engagements in same industry
        # query = select(...).where(industry == industry).aggregate(...)

        return benchmarks

    async def _generate_materiality_insights(
        self,
        base_materiality: Dict[str, Any],
        adjusted_materiality: Dict[str, Any],
        risk_factors: Dict[str, Any],
        ai_adjustment: Dict[str, Any],
        industry_benchmarks: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable insights about materiality determination"""
        insights = []

        # Insight 1: Adjustment direction
        adj_factor = ai_adjustment["adjustment_factor"]
        if adj_factor < 1.0:
            pct_change = (1.0 - adj_factor) * 100
            insights.append({
                "type": "materiality_adjustment",
                "severity": "high",
                "title": f"Materiality Reduced by {pct_change:.0f}%",
                "description": f"AI analysis recommends lower materiality (${adjusted_materiality['materiality']:,.0f}) compared to base calculation (${base_materiality['materiality']:,.0f})",
                "rationale": ai_adjustment["reasoning"]
            })
        elif adj_factor > 1.0:
            pct_change = (adj_factor - 1.0) * 100
            insights.append({
                "type": "materiality_adjustment",
                "severity": "low",
                "title": f"Materiality Increased by {pct_change:.0f}%",
                "description": f"Low risk profile supports higher materiality threshold",
                "rationale": ai_adjustment["reasoning"]
            })

        # Insight 2: Performance materiality guidance
        insights.append({
            "type": "performance_materiality",
            "severity": "info",
            "title": "Performance Materiality Set",
            "description": f"Performance materiality of ${adjusted_materiality['performance_materiality']:,.0f} (75% of overall materiality) for testing individual transactions and balances",
            "rationale": "Standard 75% allocation balances efficiency with risk of aggregated misstatements"
        })

        # Insight 3: Risk factor summary
        if risk_factors.get("factors"):
            num_factors = len(risk_factors["factors"])
            insights.append({
                "type": "risk_factors",
                "severity": "medium",
                "title": f"{num_factors} Risk Factor(s) Identified",
                "description": f"Risk factors considered in materiality determination: {', '.join([f['type'] for f in risk_factors['factors'][:3]])}",
                "rationale": "These factors influenced the AI recommendation for materiality adjustment"
            })

        return insights

    def _format_risk_factors(self, risk_factors: List[Dict[str, Any]]) -> str:
        """Format risk factors for display"""
        if not risk_factors:
            return "- No significant risk factors identified"

        return "\n".join(
            f"- [{rf['severity'].upper()}] {rf['description']}"
            for rf in risk_factors
        )


# Singleton instance
ai_materiality_service = AIMaterialityService()
