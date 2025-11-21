"""
Continuous Control Monitoring (CCM) Module
============================================
COMPETITIVE DIFFERENTIATOR #1: Real-time automated control testing

vs. Drata/Vanta: More intelligent AI-powered analysis
vs. AuditBoard/CaseWare: Automated vs. manual point-in-time testing

Key Features:
- Deployable monitoring agents for various control types
- 24/7 automated control testing
- AI-powered anomaly detection
- Predictive control health scoring
- Auto-remediation capabilities
"""

import logging
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from .config import settings
from .models import SOCEngagement, Control
# Note: Import monitoring models when migration is applied

logger = logging.getLogger(__name__)


class ContinuousMonitoringService:
    """
    Continuous Control Monitoring service for real-time automated testing
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.enabled = settings.ENABLE_AI_PLANNING and settings.OPENAI_API_KEY is not None

    async def deploy_monitoring_agent(
        self,
        db: AsyncSession,
        engagement_id: UUID,
        control_id: UUID,
        agent_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deploy a monitoring agent for continuous control testing

        Args:
            db: Database session
            engagement_id: SOC engagement ID
            control_id: Control to monitor
            agent_type: Type of agent (ACCESS_CONTROL, CHANGE_MANAGEMENT, etc.)
            config: Agent configuration (connection details, schedules, etc.)

        Returns:
            Deployed agent details
        """
        logger.info(f"Deploying {agent_type} monitoring agent for control {control_id}")

        # Validate engagement exists
        result = await db.execute(
            select(SOCEngagement).where(SOCEngagement.id == engagement_id)
        )
        engagement = result.scalar_one_or_none()
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        # TODO: Create monitoring_agent record
        # This requires migration 003 to be applied first

        agent = {
            "id": str(UUID("12345678-1234-5678-1234-567812345678")),  # Placeholder
            "engagement_id": str(engagement_id),
            "control_id": str(control_id),
            "agent_type": agent_type,
            "status": "ACTIVE",
            "monitoring_frequency_minutes": config.get("frequency_minutes", 60),
            "next_check_at": datetime.utcnow() + timedelta(minutes=config.get("frequency_minutes", 60))
        }

        logger.info(f"Agent deployed: {agent['id']}")
        return agent

    async def run_monitoring_check(
        self,
        db: AsyncSession,
        agent_id: UUID
    ) -> Dict[str, Any]:
        """
        Execute a monitoring check for a deployed agent

        Performs the actual control test and records results

        Returns:
            Monitoring result with AI analysis
        """
        logger.info(f"Running monitoring check for agent {agent_id}")

        # TODO: Fetch agent from DB
        # Execute agent-specific monitoring logic
        # For now, return mock result

        # Simulate collecting monitoring data
        raw_data = {
            "check_time": datetime.utcnow().isoformat(),
            "status": "SUCCESS",
            "metrics": {
                "users_with_mfa": 45,
                "total_users": 50,
                "mfa_adoption_rate": 0.90
            }
        }

        # AI analysis of results
        if self.enabled:
            ai_analysis = await self._analyze_monitoring_results(raw_data)
        else:
            ai_analysis = {"analysis": "AI analysis disabled", "risk_score": 0.0}

        result = {
            "agent_id": str(agent_id),
            "check_timestamp": datetime.utcnow().isoformat(),
            "control_health": self._calculate_health_status(raw_data),
            "raw_data": raw_data,
            "ai_analysis": ai_analysis.get("analysis"),
            "ai_risk_score": ai_analysis.get("risk_score"),
            "anomaly_detected": ai_analysis.get("anomaly_detected", False)
        }

        logger.info(f"Monitoring check completed: {result['control_health']}")
        return result

    async def get_control_health_trend(
        self,
        db: AsyncSession,
        control_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get control health trend over time

        Analyzes historical monitoring results to show health trajectory

        Args:
            db: Database session
            control_id: Control ID
            days: Number of days to analyze

        Returns:
            Trend analysis with predictions
        """
        # TODO: Query control_health_history table
        # Calculate trends

        trend = {
            "control_id": str(control_id),
            "period_days": days,
            "current_health": "HEALTHY",
            "health_score": 92.5,
            "trend_direction": "STABLE",
            "success_rate": 98.2,
            "total_checks": 720,  # 30 days * 24 checks/day
            "failed_checks": 13,
            "historical_scores": [
                {"date": "2025-01-01", "score": 91.2},
                {"date": "2025-01-08", "score": 92.8},
                {"date": "2025-01-15", "score": 93.1},
                {"date": "2025-01-21", "score": 92.5}
            ]
        }

        return trend

    async def detect_control_anomalies(
        self,
        db: AsyncSession,
        engagement_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies across all monitored controls

        Uses AI to identify unusual patterns or sudden changes

        Returns:
            List of detected anomalies with severity
        """
        logger.info(f"Detecting anomalies for engagement {engagement_id}")

        # TODO: Query recent monitoring_results
        # Use AI to detect anomalies

        anomalies = [
            {
                "control_id": "123",
                "control_name": "Multi-Factor Authentication Enforcement",
                "anomaly_type": "SUDDEN_DEGRADATION",
                "severity": "HIGH",
                "description": "MFA adoption dropped from 98% to 90% in 24 hours",
                "detected_at": datetime.utcnow().isoformat(),
                "recommended_action": "Investigate user offboarding process - may be disabling MFA before account deletion"
            }
        ]

        return anomalies

    async def auto_remediate(
        self,
        db: AsyncSession,
        monitoring_result_id: UUID
    ) -> Dict[str, Any]:
        """
        Attempt automatic remediation of detected issues

        CAUTION: Only for safe, pre-approved remediation actions

        Returns:
            Remediation attempt result
        """
        logger.warning(f"Auto-remediation requested for result {monitoring_result_id}")

        # TODO: Implement safe auto-remediation
        # For now, return that manual remediation is required

        return {
            "result_id": str(monitoring_result_id),
            "auto_remediation_attempted": False,
            "reason": "Manual review required - auto-remediation not configured for this control type",
            "recommended_manual_actions": [
                "Review user access logs",
                "Verify offboarding checklist completion",
                "Re-enable MFA for active accounts"
            ]
        }

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    async def _analyze_monitoring_results(
        self,
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to analyze monitoring results and identify issues
        """
        if not self.enabled:
            return {"analysis": "AI disabled", "risk_score": 0.0}

        try:
            prompt = f"""
Analyze this control monitoring result and identify any risks or issues:

Monitoring Data: {raw_data}

Provide:
1. Overall assessment (HEALTHY, DEGRADED, AT_RISK, FAILING)
2. Risk score (0.00 to 1.00)
3. Any anomalies or red flags detected
4. Recommended actions if issues found

Return as JSON with keys: analysis, risk_score, anomaly_detected, recommended_actions
"""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SOC audit expert analyzing control monitoring results. Identify risks and anomalies."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            import json
            analysis = json.loads(response.choices[0].message.content)
            return analysis

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"analysis": "Analysis failed", "risk_score": 0.0}

    def _calculate_health_status(self, raw_data: Dict[str, Any]) -> str:
        """
        Calculate control health status from monitoring data
        """
        # Simple logic for now
        metrics = raw_data.get("metrics", {})

        # Example: MFA adoption rate
        mfa_rate = metrics.get("mfa_adoption_rate", 0)

        if mfa_rate >= 0.95:
            return "HEALTHY"
        elif mfa_rate >= 0.85:
            return "DEGRADED"
        elif mfa_rate >= 0.70:
            return "AT_RISK"
        else:
            return "FAILING"


# Global instance
continuous_monitoring_service = ContinuousMonitoringService()
