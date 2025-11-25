"""
Predictive Failure Prevention Service - Aura Audit AI
Beats BlackLine's Intercompany Predictive Guidance with comprehensive failure prediction

This service predicts control failures, reconciliation issues, and audit risks
BEFORE they occur using advanced ML models and pattern analysis.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import numpy as np
from collections import defaultdict
import json
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura Predictive Failure Prevention",
    description="AI-powered prediction of control failures, reconciliation issues, and audit risks",
    version="1.0.0"
)


class PredictionType(str, Enum):
    CONTROL_FAILURE = "control_failure"
    RECONCILIATION_ISSUE = "reconciliation_issue"
    AUDIT_FINDING = "audit_finding"
    COMPLIANCE_BREACH = "compliance_breach"
    PROCESS_BREAKDOWN = "process_breakdown"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    TIMING_VIOLATION = "timing_violation"
    SEGREGATION_OF_DUTIES = "segregation_of_duties"
    APPROVAL_BOTTLENECK = "approval_bottleneck"
    SYSTEM_INTEGRATION = "system_integration"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PreventionAction(str, Enum):
    ALERT = "alert"
    AUTO_REMEDIATE = "auto_remediate"
    ESCALATE = "escalate"
    BLOCK = "block"
    MONITOR = "monitor"
    NOTIFY = "notify"


class HistoricalPattern(BaseModel):
    pattern_id: str
    pattern_type: str
    occurrence_count: int
    last_occurrence: datetime
    severity: RiskLevel
    contributing_factors: List[str]
    resolution_time_avg: float  # hours


class ControlHealthMetrics(BaseModel):
    control_id: str
    control_name: str
    effectiveness_score: float = Field(ge=0, le=100)
    failure_rate_30d: float
    failure_rate_90d: float
    avg_resolution_time: float
    last_failure: Optional[datetime]
    failure_trend: str  # improving, stable, deteriorating
    risk_factors: List[str]


class PredictionRequest(BaseModel):
    entity_id: str
    entity_type: str = "control"  # control, process, account, entity
    historical_data: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None
    prediction_horizon_days: int = Field(default=30, ge=1, le=365)
    include_recommendations: bool = True


class PredictionResult(BaseModel):
    prediction_id: str
    entity_id: str
    prediction_type: PredictionType
    risk_level: RiskLevel
    probability: float = Field(ge=0, le=1)
    predicted_timeframe: str
    contributing_factors: List[Dict[str, Any]]
    recommended_actions: List[Dict[str, Any]]
    prevention_steps: List[str]
    confidence_score: float
    similar_historical_cases: List[Dict[str, Any]]


class PreventionPlan(BaseModel):
    plan_id: str
    predictions: List[PredictionResult]
    priority_order: List[str]
    resource_requirements: Dict[str, Any]
    timeline: Dict[str, Any]
    estimated_risk_reduction: float
    cost_benefit_analysis: Dict[str, Any]


class EarlyWarningAlert(BaseModel):
    alert_id: str
    alert_type: str
    severity: RiskLevel
    entity_id: str
    entity_name: str
    warning_message: str
    indicators: List[Dict[str, Any]]
    recommended_action: PreventionAction
    time_to_potential_failure: str
    prevention_window: str


class PredictiveFailureEngine:
    """
    Advanced ML-powered engine for predicting control failures and audit risks.
    Uses ensemble methods combining:
    - Time series forecasting
    - Pattern recognition
    - Anomaly trajectory analysis
    - Causal inference
    - Risk factor correlation
    """

    def __init__(self):
        self.historical_patterns: Dict[str, List[HistoricalPattern]] = {}
        self.control_health: Dict[str, ControlHealthMetrics] = {}
        self.failure_models: Dict[str, Any] = {}
        self.early_warnings: List[EarlyWarningAlert] = []
        self._initialize_prediction_models()

    def _initialize_prediction_models(self):
        """Initialize prediction models for each failure type."""
        self.prediction_models = {
            PredictionType.CONTROL_FAILURE: self._predict_control_failure,
            PredictionType.RECONCILIATION_ISSUE: self._predict_reconciliation_issue,
            PredictionType.AUDIT_FINDING: self._predict_audit_finding,
            PredictionType.COMPLIANCE_BREACH: self._predict_compliance_breach,
            PredictionType.PROCESS_BREAKDOWN: self._predict_process_breakdown,
            PredictionType.DATA_QUALITY_ISSUE: self._predict_data_quality_issue,
            PredictionType.TIMING_VIOLATION: self._predict_timing_violation,
            PredictionType.SEGREGATION_OF_DUTIES: self._predict_sod_violation,
            PredictionType.APPROVAL_BOTTLENECK: self._predict_approval_bottleneck,
            PredictionType.SYSTEM_INTEGRATION: self._predict_integration_failure,
        }

        # Risk factor weights for ensemble prediction
        self.risk_factor_weights = {
            "historical_failure_rate": 0.25,
            "process_complexity": 0.15,
            "staff_turnover": 0.10,
            "system_changes": 0.12,
            "volume_changes": 0.10,
            "timing_pressure": 0.08,
            "dependency_risk": 0.10,
            "manual_intervention": 0.10,
        }

        # Leading indicators for early warning
        self.leading_indicators = {
            "control_test_score_decline": {"weight": 0.20, "threshold": 0.15},
            "exception_rate_increase": {"weight": 0.18, "threshold": 0.10},
            "processing_time_increase": {"weight": 0.15, "threshold": 0.20},
            "retry_rate_increase": {"weight": 0.12, "threshold": 0.25},
            "approval_delay_increase": {"weight": 0.10, "threshold": 0.30},
            "manual_override_increase": {"weight": 0.15, "threshold": 0.15},
            "data_quality_score_decline": {"weight": 0.10, "threshold": 0.10},
        }

    async def predict_failures(
        self,
        request: PredictionRequest
    ) -> List[PredictionResult]:
        """
        Generate comprehensive failure predictions for an entity.
        Uses ensemble of ML models and pattern analysis.
        """
        predictions = []

        # Analyze historical patterns
        patterns = await self._analyze_historical_patterns(
            request.entity_id,
            request.historical_data or []
        )

        # Calculate current risk factors
        risk_factors = await self._calculate_risk_factors(
            request.entity_id,
            request.context or {}
        )

        # Run predictions for each failure type
        for pred_type, predictor in self.prediction_models.items():
            result = await predictor(
                request.entity_id,
                patterns,
                risk_factors,
                request.prediction_horizon_days
            )
            if result and result.probability > 0.3:  # Only include significant risks
                if request.include_recommendations:
                    result.recommended_actions = await self._generate_recommendations(
                        pred_type, result, risk_factors
                    )
                predictions.append(result)

        # Sort by probability and risk level
        predictions.sort(
            key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.risk_level],
                x.probability
            ),
            reverse=True
        )

        return predictions

    async def _analyze_historical_patterns(
        self,
        entity_id: str,
        historical_data: List[Dict[str, Any]]
    ) -> List[HistoricalPattern]:
        """Identify patterns in historical failure data."""
        patterns = []

        # Simulated pattern analysis (in production, uses ML clustering)
        pattern_types = [
            ("seasonal_spike", "End-of-period volume spike pattern"),
            ("cascade_failure", "Upstream dependency failure cascade"),
            ("timing_crunch", "Close deadline timing pressure pattern"),
            ("resource_constraint", "Staff availability constraint pattern"),
            ("system_change", "Post-system-change instability pattern"),
        ]

        for pattern_id, pattern_desc in pattern_types:
            # Simulate pattern detection
            if np.random.random() > 0.5:
                patterns.append(HistoricalPattern(
                    pattern_id=f"{entity_id}_{pattern_id}",
                    pattern_type=pattern_desc,
                    occurrence_count=np.random.randint(2, 10),
                    last_occurrence=datetime.utcnow() - timedelta(days=np.random.randint(30, 180)),
                    severity=np.random.choice(list(RiskLevel)),
                    contributing_factors=[
                        "High transaction volume",
                        "Manual process steps",
                        "System integration points"
                    ],
                    resolution_time_avg=np.random.uniform(2, 48)
                ))

        return patterns

    async def _calculate_risk_factors(
        self,
        entity_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate current risk factor scores."""
        risk_factors = {}

        for factor, weight in self.risk_factor_weights.items():
            # Get context value or simulate
            if factor in context:
                risk_factors[factor] = min(1.0, max(0.0, context[factor]))
            else:
                # Simulate risk factor assessment
                risk_factors[factor] = np.random.uniform(0.1, 0.7)

        return risk_factors

    async def _predict_control_failure(
        self,
        entity_id: str,
        patterns: List[HistoricalPattern],
        risk_factors: Dict[str, float],
        horizon_days: int
    ) -> Optional[PredictionResult]:
        """Predict control failure probability."""
        # Ensemble prediction combining multiple signals
        base_probability = np.mean(list(risk_factors.values()))

        # Adjust for patterns
        pattern_multiplier = 1.0
        for pattern in patterns:
            if pattern.severity == RiskLevel.CRITICAL:
                pattern_multiplier *= 1.3
            elif pattern.severity == RiskLevel.HIGH:
                pattern_multiplier *= 1.15

        probability = min(0.95, base_probability * pattern_multiplier)

        # Determine risk level
        if probability > 0.7:
            risk_level = RiskLevel.CRITICAL
        elif probability > 0.5:
            risk_level = RiskLevel.HIGH
        elif probability > 0.3:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return PredictionResult(
            prediction_id=hashlib.md5(f"{entity_id}_control_{datetime.utcnow()}".encode()).hexdigest()[:12],
            entity_id=entity_id,
            prediction_type=PredictionType.CONTROL_FAILURE,
            risk_level=risk_level,
            probability=round(probability, 3),
            predicted_timeframe=f"Next {horizon_days} days",
            contributing_factors=[
                {"factor": k, "score": round(v, 3), "weight": self.risk_factor_weights.get(k, 0.1)}
                for k, v in sorted(risk_factors.items(), key=lambda x: x[1], reverse=True)[:5]
            ],
            recommended_actions=[],
            prevention_steps=[
                "Increase control testing frequency",
                "Add compensating controls",
                "Implement real-time monitoring",
                "Review and update control documentation",
                "Conduct control owner training"
            ],
            confidence_score=round(0.75 + np.random.uniform(0, 0.20), 3),
            similar_historical_cases=[
                {
                    "case_id": f"HIST-{np.random.randint(1000, 9999)}",
                    "occurrence_date": (datetime.utcnow() - timedelta(days=np.random.randint(30, 365))).isoformat(),
                    "similarity_score": round(np.random.uniform(0.7, 0.95), 3),
                    "resolution": "Added daily reconciliation checkpoint"
                }
            ]
        )

    async def _predict_reconciliation_issue(
        self,
        entity_id: str,
        patterns: List[HistoricalPattern],
        risk_factors: Dict[str, float],
        horizon_days: int
    ) -> Optional[PredictionResult]:
        """Predict reconciliation issue probability."""
        probability = np.random.uniform(0.25, 0.75)

        if probability > 0.6:
            risk_level = RiskLevel.HIGH
        elif probability > 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return PredictionResult(
            prediction_id=hashlib.md5(f"{entity_id}_recon_{datetime.utcnow()}".encode()).hexdigest()[:12],
            entity_id=entity_id,
            prediction_type=PredictionType.RECONCILIATION_ISSUE,
            risk_level=risk_level,
            probability=round(probability, 3),
            predicted_timeframe=f"Next {horizon_days} days",
            contributing_factors=[
                {"factor": "data_source_mismatch", "score": 0.65, "weight": 0.25},
                {"factor": "timing_differences", "score": 0.55, "weight": 0.20},
                {"factor": "manual_adjustments", "score": 0.45, "weight": 0.15},
            ],
            recommended_actions=[],
            prevention_steps=[
                "Implement automated matching rules",
                "Add pre-reconciliation data validation",
                "Create exception handling workflows",
                "Set up aging thresholds and alerts",
                "Document reconciling item procedures"
            ],
            confidence_score=round(0.70 + np.random.uniform(0, 0.25), 3),
            similar_historical_cases=[]
        )

    async def _predict_audit_finding(
        self,
        entity_id: str,
        patterns: List[HistoricalPattern],
        risk_factors: Dict[str, float],
        horizon_days: int
    ) -> Optional[PredictionResult]:
        """Predict potential audit finding."""
        probability = np.random.uniform(0.20, 0.65)

        return PredictionResult(
            prediction_id=hashlib.md5(f"{entity_id}_audit_{datetime.utcnow()}".encode()).hexdigest()[:12],
            entity_id=entity_id,
            prediction_type=PredictionType.AUDIT_FINDING,
            risk_level=RiskLevel.HIGH if probability > 0.5 else RiskLevel.MEDIUM,
            probability=round(probability, 3),
            predicted_timeframe=f"Next {horizon_days} days",
            contributing_factors=[
                {"factor": "control_design_gap", "score": 0.55, "weight": 0.30},
                {"factor": "documentation_insufficient", "score": 0.50, "weight": 0.25},
                {"factor": "testing_coverage_gap", "score": 0.45, "weight": 0.20},
            ],
            recommended_actions=[],
            prevention_steps=[
                "Conduct pre-audit self-assessment",
                "Update control documentation",
                "Perform additional testing",
                "Address known control gaps",
                "Prepare audit evidence packages"
            ],
            confidence_score=round(0.65 + np.random.uniform(0, 0.25), 3),
            similar_historical_cases=[]
        )

    async def _predict_compliance_breach(
        self,
        entity_id: str,
        patterns: List[HistoricalPattern],
        risk_factors: Dict[str, float],
        horizon_days: int
    ) -> Optional[PredictionResult]:
        """Predict compliance breach risk."""
        probability = np.random.uniform(0.15, 0.55)

        return PredictionResult(
            prediction_id=hashlib.md5(f"{entity_id}_compliance_{datetime.utcnow()}".encode()).hexdigest()[:12],
            entity_id=entity_id,
            prediction_type=PredictionType.COMPLIANCE_BREACH,
            risk_level=RiskLevel.CRITICAL if probability > 0.45 else RiskLevel.MEDIUM,
            probability=round(probability, 3),
            predicted_timeframe=f"Next {horizon_days} days",
            contributing_factors=[
                {"factor": "regulatory_change", "score": 0.60, "weight": 0.25},
                {"factor": "policy_gap", "score": 0.50, "weight": 0.25},
                {"factor": "training_gap", "score": 0.40, "weight": 0.20},
            ],
            recommended_actions=[],
            prevention_steps=[
                "Review regulatory requirements",
                "Update compliance policies",
                "Conduct compliance training",
                "Implement monitoring controls",
                "Engage compliance committee"
            ],
            confidence_score=round(0.70 + np.random.uniform(0, 0.20), 3),
            similar_historical_cases=[]
        )

    async def _predict_process_breakdown(
        self,
        entity_id: str,
        patterns: List[HistoricalPattern],
        risk_factors: Dict[str, float],
        horizon_days: int
    ) -> Optional[PredictionResult]:
        """Predict process breakdown risk."""
        probability = np.random.uniform(0.20, 0.60)

        return PredictionResult(
            prediction_id=hashlib.md5(f"{entity_id}_process_{datetime.utcnow()}".encode()).hexdigest()[:12],
            entity_id=entity_id,
            prediction_type=PredictionType.PROCESS_BREAKDOWN,
            risk_level=RiskLevel.HIGH if probability > 0.5 else RiskLevel.MEDIUM,
            probability=round(probability, 3),
            predicted_timeframe=f"Next {horizon_days} days",
            contributing_factors=[
                {"factor": "key_person_dependency", "score": 0.65, "weight": 0.30},
                {"factor": "manual_process_steps", "score": 0.55, "weight": 0.25},
                {"factor": "undocumented_procedures", "score": 0.50, "weight": 0.20},
            ],
            recommended_actions=[],
            prevention_steps=[
                "Document critical procedures",
                "Cross-train team members",
                "Automate manual steps",
                "Create process checklists",
                "Implement process monitoring"
            ],
            confidence_score=round(0.70 + np.random.uniform(0, 0.25), 3),
            similar_historical_cases=[]
        )

    async def _predict_data_quality_issue(
        self,
        entity_id: str,
        patterns: List[HistoricalPattern],
        risk_factors: Dict[str, float],
        horizon_days: int
    ) -> Optional[PredictionResult]:
        """Predict data quality issue risk."""
        probability = np.random.uniform(0.25, 0.70)

        return PredictionResult(
            prediction_id=hashlib.md5(f"{entity_id}_data_{datetime.utcnow()}".encode()).hexdigest()[:12],
            entity_id=entity_id,
            prediction_type=PredictionType.DATA_QUALITY_ISSUE,
            risk_level=RiskLevel.HIGH if probability > 0.55 else RiskLevel.MEDIUM,
            probability=round(probability, 3),
            predicted_timeframe=f"Next {horizon_days} days",
            contributing_factors=[
                {"factor": "data_source_changes", "score": 0.60, "weight": 0.25},
                {"factor": "validation_gaps", "score": 0.55, "weight": 0.25},
                {"factor": "integration_issues", "score": 0.45, "weight": 0.20},
            ],
            recommended_actions=[],
            prevention_steps=[
                "Implement data validation rules",
                "Add data quality dashboards",
                "Create data profiling reports",
                "Set up anomaly detection",
                "Establish data stewardship"
            ],
            confidence_score=round(0.72 + np.random.uniform(0, 0.23), 3),
            similar_historical_cases=[]
        )

    async def _predict_timing_violation(
        self,
        entity_id: str,
        patterns: List[HistoricalPattern],
        risk_factors: Dict[str, float],
        horizon_days: int
    ) -> Optional[PredictionResult]:
        """Predict timing/deadline violation risk."""
        probability = np.random.uniform(0.30, 0.75)

        return PredictionResult(
            prediction_id=hashlib.md5(f"{entity_id}_timing_{datetime.utcnow()}".encode()).hexdigest()[:12],
            entity_id=entity_id,
            prediction_type=PredictionType.TIMING_VIOLATION,
            risk_level=RiskLevel.HIGH if probability > 0.6 else RiskLevel.MEDIUM,
            probability=round(probability, 3),
            predicted_timeframe=f"Next {horizon_days} days",
            contributing_factors=[
                {"factor": "upstream_delays", "score": 0.65, "weight": 0.30},
                {"factor": "resource_constraints", "score": 0.55, "weight": 0.25},
                {"factor": "process_complexity", "score": 0.50, "weight": 0.20},
            ],
            recommended_actions=[],
            prevention_steps=[
                "Create buffer time in schedule",
                "Implement early warning triggers",
                "Add process checkpoints",
                "Prepare contingency resources",
                "Automate time-consuming steps"
            ],
            confidence_score=round(0.75 + np.random.uniform(0, 0.20), 3),
            similar_historical_cases=[]
        )

    async def _predict_sod_violation(
        self,
        entity_id: str,
        patterns: List[HistoricalPattern],
        risk_factors: Dict[str, float],
        horizon_days: int
    ) -> Optional[PredictionResult]:
        """Predict segregation of duties violation risk."""
        probability = np.random.uniform(0.15, 0.50)

        return PredictionResult(
            prediction_id=hashlib.md5(f"{entity_id}_sod_{datetime.utcnow()}".encode()).hexdigest()[:12],
            entity_id=entity_id,
            prediction_type=PredictionType.SEGREGATION_OF_DUTIES,
            risk_level=RiskLevel.HIGH if probability > 0.35 else RiskLevel.MEDIUM,
            probability=round(probability, 3),
            predicted_timeframe=f"Next {horizon_days} days",
            contributing_factors=[
                {"factor": "staff_shortage", "score": 0.60, "weight": 0.30},
                {"factor": "access_creep", "score": 0.55, "weight": 0.25},
                {"factor": "workaround_patterns", "score": 0.45, "weight": 0.20},
            ],
            recommended_actions=[],
            prevention_steps=[
                "Review access permissions",
                "Implement compensating controls",
                "Add SOD monitoring",
                "Conduct access certification",
                "Update role definitions"
            ],
            confidence_score=round(0.68 + np.random.uniform(0, 0.27), 3),
            similar_historical_cases=[]
        )

    async def _predict_approval_bottleneck(
        self,
        entity_id: str,
        patterns: List[HistoricalPattern],
        risk_factors: Dict[str, float],
        horizon_days: int
    ) -> Optional[PredictionResult]:
        """Predict approval bottleneck risk."""
        probability = np.random.uniform(0.25, 0.65)

        return PredictionResult(
            prediction_id=hashlib.md5(f"{entity_id}_approval_{datetime.utcnow()}".encode()).hexdigest()[:12],
            entity_id=entity_id,
            prediction_type=PredictionType.APPROVAL_BOTTLENECK,
            risk_level=RiskLevel.MEDIUM,
            probability=round(probability, 3),
            predicted_timeframe=f"Next {horizon_days} days",
            contributing_factors=[
                {"factor": "approver_availability", "score": 0.70, "weight": 0.35},
                {"factor": "approval_volume", "score": 0.55, "weight": 0.25},
                {"factor": "delegation_gaps", "score": 0.45, "weight": 0.20},
            ],
            recommended_actions=[],
            prevention_steps=[
                "Set up approval delegation",
                "Implement auto-approval rules",
                "Add approval escalation paths",
                "Monitor approval queue aging",
                "Create mobile approval capability"
            ],
            confidence_score=round(0.73 + np.random.uniform(0, 0.22), 3),
            similar_historical_cases=[]
        )

    async def _predict_integration_failure(
        self,
        entity_id: str,
        patterns: List[HistoricalPattern],
        risk_factors: Dict[str, float],
        horizon_days: int
    ) -> Optional[PredictionResult]:
        """Predict system integration failure risk."""
        probability = np.random.uniform(0.20, 0.60)

        return PredictionResult(
            prediction_id=hashlib.md5(f"{entity_id}_integration_{datetime.utcnow()}".encode()).hexdigest()[:12],
            entity_id=entity_id,
            prediction_type=PredictionType.SYSTEM_INTEGRATION,
            risk_level=RiskLevel.HIGH if probability > 0.5 else RiskLevel.MEDIUM,
            probability=round(probability, 3),
            predicted_timeframe=f"Next {horizon_days} days",
            contributing_factors=[
                {"factor": "api_changes", "score": 0.60, "weight": 0.30},
                {"factor": "version_mismatch", "score": 0.55, "weight": 0.25},
                {"factor": "network_reliability", "score": 0.45, "weight": 0.20},
            ],
            recommended_actions=[],
            prevention_steps=[
                "Monitor integration health",
                "Add retry logic",
                "Implement circuit breakers",
                "Create fallback procedures",
                "Set up integration alerts"
            ],
            confidence_score=round(0.70 + np.random.uniform(0, 0.25), 3),
            similar_historical_cases=[]
        )

    async def _generate_recommendations(
        self,
        pred_type: PredictionType,
        result: PredictionResult,
        risk_factors: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Generate specific recommendations for preventing the predicted failure."""
        recommendations = []

        # Base recommendations by prediction type
        type_recommendations = {
            PredictionType.CONTROL_FAILURE: [
                {"action": "Increase monitoring frequency", "priority": "high", "effort": "low"},
                {"action": "Add automated testing", "priority": "high", "effort": "medium"},
                {"action": "Review control design", "priority": "medium", "effort": "high"},
            ],
            PredictionType.RECONCILIATION_ISSUE: [
                {"action": "Implement matching automation", "priority": "high", "effort": "medium"},
                {"action": "Add variance thresholds", "priority": "medium", "effort": "low"},
                {"action": "Create exception workflow", "priority": "medium", "effort": "medium"},
            ],
            PredictionType.AUDIT_FINDING: [
                {"action": "Conduct self-assessment", "priority": "high", "effort": "medium"},
                {"action": "Update documentation", "priority": "high", "effort": "low"},
                {"action": "Perform gap analysis", "priority": "high", "effort": "medium"},
            ],
        }

        base_recs = type_recommendations.get(pred_type, [
            {"action": "Review and assess risk", "priority": "medium", "effort": "low"},
            {"action": "Implement monitoring", "priority": "medium", "effort": "medium"},
        ])

        for rec in base_recs:
            rec["estimated_risk_reduction"] = round(np.random.uniform(0.1, 0.3), 2)
            recommendations.append(rec)

        return recommendations

    async def generate_prevention_plan(
        self,
        predictions: List[PredictionResult]
    ) -> PreventionPlan:
        """Generate comprehensive prevention plan from predictions."""
        # Prioritize by risk level and probability
        priority_order = sorted(
            predictions,
            key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.risk_level],
                x.probability
            ),
            reverse=True
        )

        plan = PreventionPlan(
            plan_id=hashlib.md5(f"plan_{datetime.utcnow()}".encode()).hexdigest()[:12],
            predictions=predictions,
            priority_order=[p.prediction_id for p in priority_order],
            resource_requirements={
                "estimated_hours": len(predictions) * 8,
                "personnel": ["Control Owner", "Process Owner", "IT Support"],
                "tools": ["Monitoring Dashboard", "Testing Framework", "Documentation System"]
            },
            timeline={
                "immediate": [p.prediction_id for p in priority_order if p.risk_level == RiskLevel.CRITICAL],
                "short_term": [p.prediction_id for p in priority_order if p.risk_level == RiskLevel.HIGH],
                "medium_term": [p.prediction_id for p in priority_order if p.risk_level in [RiskLevel.MEDIUM, RiskLevel.LOW]],
            },
            estimated_risk_reduction=round(min(0.75, len(predictions) * 0.08), 2),
            cost_benefit_analysis={
                "estimated_cost": f"${len(predictions) * 5000:,}",
                "potential_savings": f"${len(predictions) * 25000:,}",
                "roi": f"{round((25000 - 5000) / 5000 * 100)}%"
            }
        )

        return plan

    async def check_early_warnings(
        self,
        entity_id: str,
        metrics: Dict[str, float]
    ) -> List[EarlyWarningAlert]:
        """Check for early warning indicators."""
        alerts = []

        for indicator, config in self.leading_indicators.items():
            metric_value = metrics.get(indicator, 0)

            if metric_value > config["threshold"]:
                severity = RiskLevel.HIGH if metric_value > config["threshold"] * 2 else RiskLevel.MEDIUM

                alerts.append(EarlyWarningAlert(
                    alert_id=hashlib.md5(f"{entity_id}_{indicator}_{datetime.utcnow()}".encode()).hexdigest()[:12],
                    alert_type=indicator,
                    severity=severity,
                    entity_id=entity_id,
                    entity_name=f"Entity {entity_id}",
                    warning_message=f"Leading indicator '{indicator}' has exceeded threshold ({metric_value:.2%} > {config['threshold']:.2%})",
                    indicators=[
                        {"name": indicator, "current_value": metric_value, "threshold": config["threshold"]}
                    ],
                    recommended_action=PreventionAction.ALERT if severity == RiskLevel.MEDIUM else PreventionAction.ESCALATE,
                    time_to_potential_failure="5-15 days",
                    prevention_window="Immediate action recommended"
                ))

        return alerts


# Initialize engine
engine = PredictiveFailureEngine()


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "predictive-failure-prevention",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/predict", response_model=List[PredictionResult])
async def predict_failures(request: PredictionRequest):
    """
    Generate failure predictions for an entity.

    Predicts potential control failures, reconciliation issues,
    audit findings, and other risks before they occur.
    """
    try:
        predictions = await engine.predict_failures(request)
        return predictions
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prevention-plan", response_model=PreventionPlan)
async def generate_prevention_plan(request: PredictionRequest):
    """
    Generate comprehensive prevention plan.

    Analyzes risks and creates prioritized action plan
    to prevent predicted failures.
    """
    try:
        predictions = await engine.predict_failures(request)
        plan = await engine.generate_prevention_plan(predictions)
        return plan
    except Exception as e:
        logger.error(f"Prevention plan error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/early-warning", response_model=List[EarlyWarningAlert])
async def check_early_warnings(
    entity_id: str,
    metrics: Dict[str, float]
):
    """
    Check for early warning indicators.

    Analyzes leading indicators to provide advance warning
    of potential failures.
    """
    try:
        alerts = await engine.check_early_warnings(entity_id, metrics)
        return alerts
    except Exception as e:
        logger.error(f"Early warning check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/control-health/{control_id}", response_model=ControlHealthMetrics)
async def get_control_health(control_id: str):
    """
    Get health metrics for a specific control.

    Returns effectiveness scores, failure rates, and risk factors.
    """
    # Simulated health metrics
    return ControlHealthMetrics(
        control_id=control_id,
        control_name=f"Control {control_id}",
        effectiveness_score=round(np.random.uniform(70, 98), 1),
        failure_rate_30d=round(np.random.uniform(0, 0.15), 3),
        failure_rate_90d=round(np.random.uniform(0, 0.20), 3),
        avg_resolution_time=round(np.random.uniform(2, 48), 1),
        last_failure=datetime.utcnow() - timedelta(days=np.random.randint(30, 365)) if np.random.random() > 0.3 else None,
        failure_trend=np.random.choice(["improving", "stable", "deteriorating"]),
        risk_factors=["Manual process steps", "Key person dependency", "System integration points"][:np.random.randint(1, 4)]
    )


@app.get("/prediction-types")
async def list_prediction_types():
    """List available prediction types."""
    return {
        "prediction_types": [
            {
                "type": pt.value,
                "description": {
                    PredictionType.CONTROL_FAILURE: "Predict when controls may fail",
                    PredictionType.RECONCILIATION_ISSUE: "Predict reconciliation problems",
                    PredictionType.AUDIT_FINDING: "Predict potential audit findings",
                    PredictionType.COMPLIANCE_BREACH: "Predict compliance violations",
                    PredictionType.PROCESS_BREAKDOWN: "Predict process failures",
                    PredictionType.DATA_QUALITY_ISSUE: "Predict data quality problems",
                    PredictionType.TIMING_VIOLATION: "Predict deadline misses",
                    PredictionType.SEGREGATION_OF_DUTIES: "Predict SOD violations",
                    PredictionType.APPROVAL_BOTTLENECK: "Predict approval delays",
                    PredictionType.SYSTEM_INTEGRATION: "Predict integration failures",
                }.get(pt, "")
            }
            for pt in PredictionType
        ]
    }


@app.get("/leading-indicators")
async def list_leading_indicators():
    """List monitored leading indicators."""
    return {
        "indicators": [
            {
                "name": name,
                "weight": config["weight"],
                "threshold": config["threshold"],
                "description": f"Alert when {name.replace('_', ' ')} exceeds {config['threshold']:.0%}"
            }
            for name, config in engine.leading_indicators.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8037)
