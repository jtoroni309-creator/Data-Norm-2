"""
AI-Enhanced Risk Assessment Service

Provides intelligent, comprehensive risk assessment using:
- AI-powered pattern detection and predictive risk scoring
- Integration with materiality calculations
- Industry-specific risk factor analysis
- Historical data analysis and trend identification
- Real-time risk monitoring capabilities
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from openai import AsyncOpenAI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings

logger = logging.getLogger(__name__)


class AIRiskAssessmentService:
    """
    AI-powered risk assessment service that provides comprehensive
    risk analysis for audit engagements with materiality integration.
    """

    def __init__(self):
        """Initialize with OpenAI client for AI-powered analysis"""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = getattr(settings, 'OPENAI_CHAT_MODEL', 'gpt-4-turbo-preview')

        # Risk thresholds (configurable)
        self.high_risk_debt_to_equity = float(getattr(settings, 'HIGH_RISK_DEBT_TO_EQUITY', 2.0))
        self.low_liquidity_current_ratio = float(getattr(settings, 'LOW_LIQUIDITY_CURRENT_RATIO', 1.0))
        self.going_concern_risk_threshold = float(getattr(settings, 'GOING_CONCERN_RISK_THRESHOLD', 0.75))

        logger.info("AI Risk Assessment Service initialized")

    async def perform_comprehensive_risk_assessment(
        self,
        db: AsyncSession,
        engagement_id: UUID,
        financial_statements: Dict[str, Any],
        prior_period_statements: Optional[Dict[str, Any]] = None,
        industry: Optional[str] = None,
        entity_type: Optional[str] = None,
        materiality: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive AI-enhanced risk assessment.

        Args:
            db: Database session
            engagement_id: Engagement ID
            financial_statements: Current period financial statements
            prior_period_statements: Prior period for trend analysis
            industry: Industry classification
            entity_type: Entity type (public, private, nonprofit)
            materiality: Materiality thresholds (if already calculated)

        Returns:
            Comprehensive risk assessment with AI insights
        """
        logger.info(f"Performing AI-enhanced risk assessment for engagement {engagement_id}")

        # Step 1: Calculate financial ratios
        ratios = self._calculate_financial_ratios(financial_statements)

        # Step 2: Analyze trends (if prior period available)
        trends = None
        if prior_period_statements:
            trends = self._analyze_trends(financial_statements, prior_period_statements)

        # Step 3: Identify rule-based risk factors
        rule_based_risks = self._identify_rule_based_risks(ratios, trends, financial_statements)

        # Step 4: AI-powered risk pattern detection
        ai_risk_patterns = await self._ai_detect_risk_patterns(
            financial_statements,
            ratios,
            trends,
            industry,
            entity_type
        )

        # Step 5: Industry-specific risk assessment
        industry_risks = await self._assess_industry_specific_risks(
            db,
            industry,
            financial_statements,
            ratios
        )

        # Step 6: Integrate with materiality (if provided)
        materiality_risk_alignment = None
        if materiality:
            materiality_risk_alignment = self._assess_materiality_risk_alignment(
                rule_based_risks,
                ai_risk_patterns,
                materiality
            )

        # Step 7: Calculate overall risk score with AI weighting
        overall_risk = await self._calculate_ai_weighted_risk_score(
            rule_based_risks,
            ai_risk_patterns,
            industry_risks
        )

        # Step 8: Generate key audit matters (KAMs)
        key_audit_matters = await self._identify_key_audit_matters(
            financial_statements,
            ratios,
            overall_risk,
            industry
        )

        # Step 9: Going concern assessment
        going_concern = await self._assess_going_concern(
            financial_statements,
            ratios,
            trends,
            overall_risk
        )

        # Step 10: Generate audit strategy recommendations
        audit_strategy = await self._generate_audit_strategy_recommendations(
            overall_risk,
            key_audit_matters,
            going_concern,
            materiality
        )

        # Compile comprehensive result
        result = {
            "engagement_id": str(engagement_id),
            "assessment_date": datetime.utcnow().isoformat(),

            # Financial metrics
            "financial_ratios": ratios,
            "trends": trends,

            # Risk assessment
            "overall_risk_assessment": {
                "risk_level": overall_risk["risk_level"],
                "risk_score": overall_risk["risk_score"],
                "confidence_score": overall_risk["confidence_score"]
            },

            # Risk factors by category
            "risk_factors": {
                "rule_based": rule_based_risks,
                "ai_detected_patterns": ai_risk_patterns,
                "industry_specific": industry_risks
            },

            # Going concern
            "going_concern_assessment": going_concern,

            # Key audit matters
            "key_audit_matters": key_audit_matters,

            # Materiality alignment
            "materiality_risk_alignment": materiality_risk_alignment,

            # Audit strategy
            "recommended_audit_strategy": audit_strategy,

            # AI insights
            "ai_insights": overall_risk.get("ai_insights", [])
        }

        logger.info(
            f"Risk assessment complete: "
            f"Risk Level = {overall_risk['risk_level']}, "
            f"Score = {overall_risk['risk_score']:.2f}"
        )

        return result

    def _calculate_financial_ratios(
        self,
        statements: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate comprehensive financial ratios for risk assessment"""
        ratios = {}

        # Extract values
        balance_sheet = statements.get("balance_sheet", {})
        income_statement = statements.get("income_statement", {})
        cash_flow = statements.get("cash_flow", {})

        current_assets = Decimal(str(balance_sheet.get("current_assets", 0) or 0))
        current_liabilities = Decimal(str(balance_sheet.get("current_liabilities", 1) or 1))
        cash = Decimal(str(balance_sheet.get("cash_and_equivalents", 0) or 0))
        inventory = Decimal(str(balance_sheet.get("inventory", 0) or 0))
        total_assets = Decimal(str(balance_sheet.get("total_assets", 1) or 1))
        total_liabilities = Decimal(str(balance_sheet.get("total_liabilities", 0) or 0))
        total_equity = Decimal(str(balance_sheet.get("total_equity", 1) or 1))

        revenue = Decimal(str(income_statement.get("revenue", 1) or 1))
        gross_profit = Decimal(str(income_statement.get("gross_profit", 0) or 0))
        operating_income = Decimal(str(income_statement.get("operating_income", 0) or 0))
        net_income = Decimal(str(income_statement.get("net_income", 0) or 0))

        operating_cash_flow = Decimal(str(cash_flow.get("operating_cash_flow", 0) or 0))

        # Liquidity ratios
        if current_liabilities > 0:
            ratios["current_ratio"] = float(current_assets / current_liabilities)
            ratios["quick_ratio"] = float((current_assets - inventory) / current_liabilities)
            ratios["cash_ratio"] = float(cash / current_liabilities)

        ratios["working_capital"] = float(current_assets - current_liabilities)

        # Profitability ratios
        if revenue > 0:
            ratios["gross_profit_margin"] = float(gross_profit / revenue * 100)
            ratios["operating_profit_margin"] = float(operating_income / revenue * 100)
            ratios["net_profit_margin"] = float(net_income / revenue * 100)

        if total_assets > 0:
            ratios["return_on_assets"] = float(net_income / total_assets * 100)

        if total_equity > 0:
            ratios["return_on_equity"] = float(net_income / total_equity * 100)

        # Leverage ratios
        if total_equity > 0:
            ratios["debt_to_equity"] = float(total_liabilities / total_equity)

        if total_assets > 0:
            ratios["debt_to_assets"] = float(total_liabilities / total_assets * 100)

        # Cash flow ratios
        if current_liabilities > 0:
            ratios["operating_cash_flow_ratio"] = float(operating_cash_flow / current_liabilities)

        return ratios

    def _analyze_trends(
        self,
        current_period: Dict[str, Any],
        prior_period: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze year-over-year trends"""
        trends = {}

        # Revenue growth
        current_revenue = Decimal(str(current_period.get("income_statement", {}).get("revenue", 0) or 0))
        prior_revenue = Decimal(str(prior_period.get("income_statement", {}).get("revenue", 1) or 1))

        if prior_revenue > 0:
            trends["revenue_growth"] = float((current_revenue - prior_revenue) / prior_revenue * 100)

        # Earnings growth
        current_ni = Decimal(str(current_period.get("income_statement", {}).get("net_income", 0) or 0))
        prior_ni = Decimal(str(prior_period.get("income_statement", {}).get("net_income", 1) or 1))

        if prior_ni != 0:
            trends["earnings_growth"] = float((current_ni - prior_ni) / abs(prior_ni) * 100)

        # Asset growth
        current_assets = Decimal(str(current_period.get("balance_sheet", {}).get("total_assets", 0) or 0))
        prior_assets = Decimal(str(prior_period.get("balance_sheet", {}).get("total_assets", 1) or 1))

        if prior_assets > 0:
            trends["asset_growth"] = float((current_assets - prior_assets) / prior_assets * 100)

        return trends

    def _identify_rule_based_risks(
        self,
        ratios: Dict[str, float],
        trends: Optional[Dict[str, float]],
        statements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify risks using traditional rule-based criteria"""
        risks = []

        # Liquidity risk
        current_ratio = ratios.get("current_ratio", 10)
        if current_ratio < self.low_liquidity_current_ratio:
            risks.append({
                "category": "liquidity",
                "severity": "high",
                "description": f"Current ratio of {current_ratio:.2f} indicates liquidity concerns",
                "metric": "current_ratio",
                "value": current_ratio,
                "threshold": self.low_liquidity_current_ratio,
                "audit_implications": "Increased testing of cash flow projections and going concern assessment"
            })

        # Leverage risk
        debt_to_equity = ratios.get("debt_to_equity", 0)
        if debt_to_equity > self.high_risk_debt_to_equity:
            risks.append({
                "category": "leverage",
                "severity": "high",
                "description": f"High debt-to-equity ratio of {debt_to_equity:.2f}",
                "metric": "debt_to_equity",
                "value": debt_to_equity,
                "threshold": self.high_risk_debt_to_equity,
                "audit_implications": "Enhanced testing of debt covenants and related party transactions"
            })

        # Profitability risk
        net_margin = ratios.get("net_profit_margin", 0)
        if net_margin < 0:
            risks.append({
                "category": "profitability",
                "severity": "high",
                "description": f"Negative net profit margin of {net_margin:.1f}%",
                "metric": "net_profit_margin",
                "value": net_margin,
                "threshold": 0.0,
                "audit_implications": "Assess going concern and management's plans to return to profitability"
            })

        # Trend risks
        if trends:
            revenue_growth = trends.get("revenue_growth", 0)
            if revenue_growth < -10:
                risks.append({
                    "category": "revenue_decline",
                    "severity": "medium",
                    "description": f"Revenue declined by {abs(revenue_growth):.1f}%",
                    "metric": "revenue_growth",
                    "value": revenue_growth,
                    "threshold": -10.0,
                    "audit_implications": "Increased testing of revenue recognition and cut-off procedures"
                })

        return risks

    async def _ai_detect_risk_patterns(
        self,
        financial_statements: Dict[str, Any],
        ratios: Dict[str, float],
        trends: Optional[Dict[str, float]],
        industry: Optional[str],
        entity_type: Optional[str]
    ) -> Dict[str, Any]:
        """Use AI to detect complex risk patterns and relationships"""
        prompt = f"""You are an experienced audit risk assessment expert analyzing an engagement for potential risks.

FINANCIAL RATIOS:
{self._format_ratios(ratios)}

TRENDS:
{self._format_trends(trends) if trends else 'Not available'}

FINANCIAL POSITION:
Revenue: ${financial_statements.get('income_statement', {}).get('revenue', 0):,.0f}
Net Income: ${financial_statements.get('income_statement', {}).get('net_income', 0):,.0f}
Total Assets: ${financial_statements.get('balance_sheet', {}).get('total_assets', 0):,.0f}
Total Liabilities: ${financial_statements.get('balance_sheet', {}).get('total_liabilities', 0):,.0f}

CONTEXT:
Industry: {industry or 'Not specified'}
Entity Type: {entity_type or 'Not specified'}

TASK:
Identify complex risk patterns, correlations, and emerging risks that may not be obvious from individual metrics. Consider:

1. Unusual combinations of metrics that indicate hidden risks
2. Industry-specific warning signs
3. Patterns suggesting management pressure or incentives for misstatement
4. Early indicators of financial distress not yet obvious in individual ratios
5. Risks related to revenue recognition, estimates, or complex transactions

Respond in JSON format:
{{
  "detected_patterns": [
    {{
      "pattern_name": "Brief pattern name",
      "severity": "low|medium|high|critical",
      "description": "What the pattern indicates",
      "supporting_metrics": ["metric1", "metric2"],
      "audit_implications": "How this affects audit approach",
      "recommended_procedures": ["procedure 1", "procedure 2"]
    }}
  ],
  "overall_risk_indicators": {{
    "fraud_risk_indicators": ["indicator 1", "indicator 2"],
    "going_concern_indicators": ["indicator 1", "indicator 2"],
    "complex_estimate_areas": ["area 1", "area 2"]
  }},
  "ai_confidence": 0.XX (0.0 to 1.0),
  "summary": "Brief summary of key AI-detected risks"
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in audit risk assessment with deep knowledge of PCAOB AS 2110 (Risk Assessment), AS 2401 (Fraud), and AS 2415 (Going Concern). Identify patterns and risks that require enhanced audit procedures."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"Error in AI risk pattern detection: {e}")
            return {
                "detected_patterns": [],
                "overall_risk_indicators": {},
                "ai_confidence": 0.0,
                "summary": "AI analysis unavailable"
            }

    async def _assess_industry_specific_risks(
        self,
        db: AsyncSession,
        industry: Optional[str],
        financial_statements: Dict[str, Any],
        ratios: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Assess industry-specific risk factors"""
        if not industry:
            return []

        industry_risks = []

        # Technology industry
        if "Technology" in industry or "Software" in industry:
            # High R&D intensity
            revenue = financial_statements.get("income_statement", {}).get("revenue", 1)
            if revenue > 0:
                industry_risks.append({
                    "industry": industry,
                    "risk_area": "Revenue Recognition",
                    "description": "Complex revenue recognition for software and multi-element arrangements",
                    "severity": "high",
                    "audit_focus": "ASC 606 compliance, performance obligations, variable consideration"
                })

        # Manufacturing industry
        elif "Manufacturing" in industry:
            inventory_ratio = ratios.get("inventory_turnover", 0)
            if inventory_ratio < 4:
                industry_risks.append({
                    "industry": industry,
                    "risk_area": "Inventory Valuation",
                    "description": "Potential inventory obsolescence or overvaluation",
                    "severity": "medium",
                    "audit_focus": "Physical counts, NRV testing, obsolescence reserves"
                })

        # Financial services
        elif "Financial" in industry or "Banking" in industry:
            industry_risks.append({
                "industry": industry,
                "risk_area": "Credit Risk and Loan Loss Reserves",
                "description": "Complex estimates for loan loss allowances",
                "severity": "high",
                "audit_focus": "CECL model compliance, credit quality indicators, reserve adequacy"
            })

        return industry_risks

    def _assess_materiality_risk_alignment(
        self,
        rule_based_risks: List[Dict[str, Any]],
        ai_risk_patterns: Dict[str, Any],
        materiality: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess whether materiality levels are appropriate for identified risks"""
        high_severity_risks = len([r for r in rule_based_risks if r.get("severity") == "high"])
        ai_patterns = len(ai_risk_patterns.get("detected_patterns", []))

        total_risk_factors = high_severity_risks + ai_patterns

        # Get materiality adjustment if available
        materiality_adjustment = materiality.get("ai_adjusted_materiality", {}).get("adjustment_factor", 1.0)

        alignment_assessment = "appropriate"
        recommendation = "Materiality levels are appropriately aligned with identified risks"

        if total_risk_factors >= 3 and materiality_adjustment >= 1.0:
            alignment_assessment = "consider_lowering"
            recommendation = f"With {total_risk_factors} significant risk factors identified, consider lowering materiality for enhanced testing"
        elif total_risk_factors <= 1 and materiality_adjustment < 0.9:
            alignment_assessment = "possibly_conservative"
            recommendation = "Low risk profile may support slightly higher materiality within professional judgment"

        return {
            "alignment_assessment": alignment_assessment,
            "high_severity_risk_count": high_severity_risks,
            "ai_detected_pattern_count": ai_patterns,
            "current_materiality_adjustment": materiality_adjustment,
            "recommendation": recommendation
        }

    async def _calculate_ai_weighted_risk_score(
        self,
        rule_based_risks: List[Dict[str, Any]],
        ai_risk_patterns: Dict[str, Any],
        industry_risks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall risk score with AI weighting"""
        # Rule-based score
        rule_score = 0.0
        for risk in rule_based_risks:
            severity = risk.get("severity", "low")
            if severity == "critical":
                rule_score += 0.25
            elif severity == "high":
                rule_score += 0.20
            elif severity == "medium":
                rule_score += 0.10
            else:
                rule_score += 0.05

        # AI pattern score
        ai_score = 0.0
        for pattern in ai_risk_patterns.get("detected_patterns", []):
            severity = pattern.get("severity", "low")
            if severity == "critical":
                ai_score += 0.20
            elif severity == "high":
                ai_score += 0.15
            elif severity == "medium":
                ai_score += 0.08

        # Industry risk score
        industry_score = len(industry_risks) * 0.10

        # Weighted combination (rule-based 40%, AI 50%, industry 10%)
        total_score = min(1.0, (rule_score * 0.4) + (ai_score * 0.5) + (industry_score * 0.1))

        # Determine risk level
        if total_score >= 0.75:
            risk_level = "critical"
        elif total_score >= 0.50:
            risk_level = "high"
        elif total_score >= 0.25:
            risk_level = "moderate"
        else:
            risk_level = "low"

        ai_confidence = ai_risk_patterns.get("ai_confidence", 0.7)

        return {
            "risk_score": round(total_score, 2),
            "risk_level": risk_level,
            "confidence_score": ai_confidence,
            "score_breakdown": {
                "rule_based": round(rule_score, 2),
                "ai_patterns": round(ai_score, 2),
                "industry_specific": round(industry_score, 2)
            },
            "ai_insights": [
                f"Overall risk assessment: {risk_level.upper()}",
                f"Risk score: {total_score:.2f} (0.0 = low risk, 1.0 = critical risk)",
                ai_risk_patterns.get("summary", "")
            ]
        }

    async def _identify_key_audit_matters(
        self,
        financial_statements: Dict[str, Any],
        ratios: Dict[str, float],
        overall_risk: Dict[str, Any],
        industry: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Identify Key Audit Matters (KAMs) based on risk assessment"""
        kams = []

        # Revenue recognition (always a KAM for complex entities)
        revenue = financial_statements.get("income_statement", {}).get("revenue", 0)
        if revenue > 1000000:  # Material revenue
            kams.append({
                "matter": "Revenue Recognition",
                "why_kam": "Revenue is a key performance metric subject to management incentives and requires significant judgment",
                "audit_response": "Test revenue transactions, review contracts, perform cut-off procedures, assess ASC 606 compliance",
                "risk_level": "high"
            })

        # Going concern (if risk indicators present)
        if overall_risk["risk_level"] in ["high", "critical"]:
            kams.append({
                "matter": "Going Concern Assessment",
                "why_kam": "Identified risk indicators raise substantial doubt about entity's ability to continue as going concern",
                "audit_response": "Evaluate management's plans, test cash flow projections, assess covenant compliance",
                "risk_level": overall_risk["risk_level"]
            })

        return kams

    async def _assess_going_concern(
        self,
        financial_statements: Dict[str, Any],
        ratios: Dict[str, float],
        trends: Optional[Dict[str, float]],
        overall_risk: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess going concern risk"""
        indicators = []
        risk_score = 0.0

        # Negative working capital
        working_capital = ratios.get("working_capital", 0)
        if working_capital < 0:
            indicators.append("Negative working capital")
            risk_score += 0.20

        # Operating losses
        net_margin = ratios.get("net_profit_margin", 0)
        if net_margin < 0:
            indicators.append("Operating at a loss")
            risk_score += 0.20

        # Revenue decline
        if trends and trends.get("revenue_growth", 0) < -15:
            indicators.append("Significant revenue decline")
            risk_score += 0.20

        # High leverage
        debt_to_equity = ratios.get("debt_to_equity", 0)
        if debt_to_equity > 3.0:
            indicators.append("Very high debt levels")
            risk_score += 0.15

        # Overall risk contribution
        if overall_risk["risk_level"] in ["high", "critical"]:
            risk_score += 0.15

        # Determine risk level
        if risk_score >= self.going_concern_risk_threshold:
            risk_level = "critical"
            requires_disclosure = True
        elif risk_score >= 0.50:
            risk_level = "high"
            requires_disclosure = True
        elif risk_score >= 0.25:
            risk_level = "moderate"
            requires_disclosure = False
        else:
            risk_level = "low"
            requires_disclosure = False

        return {
            "risk_level": risk_level,
            "risk_score": min(risk_score, 1.0),
            "indicators": indicators,
            "requires_disclosure": requires_disclosure,
            "assessment": f"Going concern risk is {risk_level} based on {len(indicators)} indicator(s)"
        }

    async def _generate_audit_strategy_recommendations(
        self,
        overall_risk: Dict[str, Any],
        key_audit_matters: List[Dict[str, Any]],
        going_concern: Dict[str, Any],
        materiality: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate recommended audit strategy based on risk assessment"""
        recommendations = []

        risk_level = overall_risk["risk_level"]

        # Substantive vs controls testing
        if risk_level in ["high", "critical"]:
            recommendations.append({
                "area": "Audit Approach",
                "recommendation": "Primarily substantive approach with increased sample sizes",
                "rationale": "High risk profile warrants more extensive substantive testing"
            })
        else:
            recommendations.append({
                "area": "Audit Approach",
                "recommendation": "Balanced approach with controls testing where effective",
                "rationale": "Moderate risk allows for efficient controls reliance strategy"
            })

        # Specialist involvement
        if any(kam.get("matter") == "Going Concern Assessment" for kam in key_audit_matters):
            recommendations.append({
                "area": "Specialist Involvement",
                "recommendation": "Consider engaging valuation or industry specialist",
                "rationale": "Going concern assessment may require specialist expertise"
            })

        # Increased skepticism
        if risk_level == "critical":
            recommendations.append({
                "area": "Professional Skepticism",
                "recommendation": "Heightened professional skepticism required",
                "rationale": "Critical risk factors indicate potential for material misstatement"
            })

        return {
            "recommended_approach": "Primarily Substantive" if risk_level in ["high", "critical"] else "Balanced Controls and Substantive",
            "recommended_procedures": recommendations,
            "audit_hours_adjustment": "Increase 20-30%" if risk_level in ["high", "critical"] else "Standard allocation",
            "partner_involvement": "Enhanced" if risk_level in ["high", "critical"] else "Standard"
        }

    def _format_ratios(self, ratios: Dict[str, float]) -> str:
        """Format ratios for display"""
        if not ratios:
            return "No ratios available"
        return "\n".join(f"- {k.replace('_', ' ').title()}: {v:.2f}" for k, v in sorted(ratios.items()))

    def _format_trends(self, trends: Dict[str, float]) -> str:
        """Format trends for display"""
        if not trends:
            return "No trends available"
        return "\n".join(f"- {k.replace('_', ' ').title()}: {v:+.1f}%" for k, v in sorted(trends.items()))


# Singleton instance
ai_risk_service = AIRiskAssessmentService()
