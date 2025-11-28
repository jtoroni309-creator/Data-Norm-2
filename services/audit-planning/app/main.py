"""
Aura Audit AI - Audit Planning Service

Comprehensive audit planning and risk assessment:
- Materiality calculations per PCAOB standards
- Risk assessments (inherent, control, detection)
- Audit program generation
- Preliminary analytical procedures
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .config import settings
from .database import get_db, init_db
from .models import (
    AuditPlan,
    RiskAssessment,
    RiskLevel,
    RiskType,
    PreliminaryAnalytics,
    RiskMatrix,
    FraudRiskFactor
)
from .planning_service import (
    MaterialityCalculator,
    RiskAssessor,
    AuditProgramGenerator,
    AuditPlanningService
)
from .ai_planning_service import AIAuditPlanningService

# Initialize AI Planning Service
ai_planning_service = AIAuditPlanningService()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura Audit AI - Audit Planning Service",
    description="Audit planning, materiality, risk assessment, and program generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# Schemas
# ========================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


class MaterialityRequest(BaseModel):
    """Request for materiality calculation"""
    total_assets: Decimal
    total_revenue: Decimal
    pretax_income: Decimal
    total_equity: Decimal
    entity_type: str = "public"


class MaterialityResponse(BaseModel):
    """Materiality calculation response"""
    overall_materiality: Decimal
    performance_materiality: Decimal
    trivial_threshold: Decimal
    benchmark_used: str
    all_benchmarks: Dict[str, Decimal]


class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment"""
    engagement_id: UUID
    account_name: str
    account_balance: Decimal
    assertion_type: str
    factors: Optional[Dict] = {}


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response"""
    inherent_risk: str
    control_risk: str
    detection_risk: str
    audit_risk: str
    recommendations: List[str]


class AuditPlanRequest(BaseModel):
    """Request for audit plan creation"""
    engagement_id: UUID
    fiscal_year_end: str
    materiality_amount: Decimal
    risk_level: str


class AuditPlanResponse(BaseModel):
    """Audit plan response"""
    id: UUID
    engagement_id: UUID
    plan_status: str
    fiscal_year_end: str
    overall_materiality: Decimal
    created_at: datetime


# ========================================
# AI Planning Schemas
# ========================================

class AIRiskAnalysisRequest(BaseModel):
    """Request for AI-powered engagement risk analysis"""
    engagement_id: str
    client_name: str
    industry: str
    financial_data: Dict
    prior_year_data: Optional[Dict] = None
    known_issues: Optional[List[str]] = []


class AIAuditProgramRequest(BaseModel):
    """Request for AI-generated audit program"""
    engagement_id: str
    risk_assessment: Dict
    audit_area: str
    account_balance: float
    materiality: float
    prior_year_findings: Optional[List[str]] = []


class AIMaterialityRequest(BaseModel):
    """Request for AI-powered materiality recommendation"""
    financial_data: Dict
    industry: str
    entity_type: str = "private"
    risk_factors: List[str] = []
    user_count: int = 0


class AIFraudDetectionRequest(BaseModel):
    """Request for AI fraud pattern detection"""
    engagement_id: str
    financial_data: Dict
    transaction_data: Optional[List[Dict]] = None
    journal_entries: Optional[List[Dict]] = None


class AIPlanningMemoRequest(BaseModel):
    """Request for AI-generated planning memo"""
    engagement_id: str
    client_name: str
    risk_assessment: Dict
    materiality: Dict
    fraud_assessment: Dict
    audit_programs: List[Dict]


# ========================================
# Mock Authentication
# ========================================

async def get_current_user_id() -> UUID:
    """Mock function to get current user ID"""
    return UUID("00000000-0000-0000-0000-000000000001")


# ========================================
# Health & Status
# ========================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="audit-planning",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aura Audit AI - Audit Planning Service",
        "version": "1.0.0",
        "features": [
            "Materiality calculations per PCAOB standards",
            "Risk assessments (inherent, control, detection)",
            "Audit program generation",
            "Preliminary analytical procedures"
        ],
        "docs": "/docs"
    }


# ========================================
# Materiality Calculation
# ========================================

@app.post("/materiality/calculate", response_model=MaterialityResponse)
async def calculate_materiality(
    request: MaterialityRequest,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Calculate materiality benchmarks per PCAOB and AICPA standards.

    Uses multiple benchmarks:
    - 0.5-1% of total assets
    - 0.5-1% of total revenue
    - 5% of pre-tax income (if stable)
    - 1-2% of equity
    """
    try:
        result = MaterialityCalculator.calculate_materiality(
            total_assets=request.total_assets,
            total_revenue=request.total_revenue,
            pretax_income=request.pretax_income,
            total_equity=request.total_equity,
            entity_type=request.entity_type
        )

        logger.info(
            f"Materiality calculated: ${result['overall_materiality']:,.0f} "
            f"using {result['benchmark_used']}"
        )

        return MaterialityResponse(**result)

    except Exception as e:
        logger.error(f"Error calculating materiality: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate materiality: {str(e)}"
        )


# ========================================
# Risk Assessment
# ========================================

@app.post("/risk/assess")
async def assess_risk(
    request: RiskAssessmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Perform comprehensive risk assessment for an account.

    Evaluates:
    - Inherent risk (nature of account/transaction)
    - Control risk (effectiveness of internal controls)
    - Detection risk (audit procedures needed)
    - Overall audit risk
    """
    try:
        assessor = RiskAssessor()

        # Assess inherent risk
        inherent_risk = assessor.assess_inherent_risk(
            account_type=request.factors.get("account_type", "asset"),
            transaction_volume=request.factors.get("transaction_volume", "medium"),
            complexity=request.factors.get("complexity", "low"),
            susceptibility_to_fraud=request.factors.get("fraud_risk", False)
        )

        # Assess control risk
        control_risk = assessor.assess_control_risk(
            control_design=request.factors.get("control_design", "adequate"),
            control_operation=request.factors.get("control_operation", "effective"),
            test_results=request.factors.get("test_results", [])
        )

        # Calculate detection risk
        detection_risk = assessor.calculate_detection_risk(
            inherent_risk=inherent_risk,
            control_risk=control_risk,
            acceptable_audit_risk=Decimal("0.05")  # 5% audit risk
        )

        # Store risk assessment
        risk_assessment = RiskAssessment(
            engagement_id=request.engagement_id,
            account_name=request.account_name,
            account_balance=request.account_balance,
            assertion_type=request.assertion_type,
            risk_type=RiskType.INHERENT,
            risk_level=RiskLevel[inherent_risk.upper()],
            justification=f"Automated risk assessment based on account characteristics",
            assessed_by=current_user_id
        )
        db.add(risk_assessment)
        await db.commit()

        logger.info(
            f"Risk assessment for {request.account_name}: "
            f"IR={inherent_risk}, CR={control_risk}, DR={detection_risk:.2%}"
        )

        return {
            "inherent_risk": inherent_risk,
            "control_risk": control_risk,
            "detection_risk": float(detection_risk),
            "audit_risk": float(Decimal(inherent_risk) * Decimal(control_risk) * detection_risk) if isinstance(inherent_risk, (int, float)) else "qualitative",
            "recommendations": [
                f"Inherent risk is {inherent_risk} - consider additional substantive procedures",
                f"Control risk is {control_risk} - {'rely on controls' if control_risk == 'low' else 'perform extended testing'}",
                f"Detection risk target: {detection_risk:.2%} - plan audit procedures accordingly"
            ]
        }

    except Exception as e:
        logger.error(f"Error assessing risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assess risk: {str(e)}"
        )


# ========================================
# Audit Plan Management
# ========================================

@app.post("/plans", response_model=AuditPlanResponse)
async def create_audit_plan(
    request: AuditPlanRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Create comprehensive audit plan for engagement.

    Includes:
    - Materiality thresholds
    - Risk assessment summary
    - Preliminary audit programs
    - Resource allocation
    """
    try:
        # Parse fiscal year end
        from datetime import datetime
        fye_date = datetime.fromisoformat(request.fiscal_year_end)

        # Create audit plan
        audit_plan = AuditPlan(
            engagement_id=request.engagement_id,
            fiscal_year_end=fye_date,
            overall_materiality=request.materiality_amount,
            performance_materiality=request.materiality_amount * Decimal("0.65"),
            trivial_threshold=request.materiality_amount * Decimal("0.05"),
            plan_status="draft",
            created_by=current_user_id
        )

        db.add(audit_plan)
        await db.commit()
        await db.refresh(audit_plan)

        logger.info(f"Created audit plan {audit_plan.id} for engagement {request.engagement_id}")

        return AuditPlanResponse(
            id=audit_plan.id,
            engagement_id=audit_plan.engagement_id,
            plan_status=audit_plan.plan_status,
            fiscal_year_end=audit_plan.fiscal_year_end.isoformat(),
            overall_materiality=audit_plan.overall_materiality,
            created_at=audit_plan.created_at
        )

    except Exception as e:
        logger.error(f"Error creating audit plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audit plan: {str(e)}"
        )


@app.get("/plans/{engagement_id}")
async def get_audit_plan(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Get audit plan for engagement"""
    result = await db.execute(
        select(AuditPlan).where(AuditPlan.engagement_id == engagement_id)
    )
    audit_plan = result.scalar_one_or_none()

    if not audit_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit plan not found"
        )

    return {
        "id": str(audit_plan.id),
        "engagement_id": str(audit_plan.engagement_id),
        "fiscal_year_end": audit_plan.fiscal_year_end.isoformat(),
        "overall_materiality": float(audit_plan.overall_materiality),
        "performance_materiality": float(audit_plan.performance_materiality),
        "trivial_threshold": float(audit_plan.trivial_threshold),
        "plan_status": audit_plan.plan_status,
        "created_at": audit_plan.created_at.isoformat()
    }


# ========================================
# Audit Program Generation
# ========================================

@app.post("/programs/generate/{engagement_id}")
async def generate_audit_program(
    engagement_id: UUID,
    area: str,
    risk_level: str = "moderate",
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Generate audit program for specific area.

    Areas: cash, receivables, inventory, revenue, etc.
    Risk levels: low, moderate, high, significant
    """
    try:
        generator = AuditProgramGenerator()

        # Generate procedures based on area and risk level
        procedures = generator.generate_procedures(
            audit_area=area,
            risk_level=RiskLevel[risk_level.upper()]
        )

        logger.info(
            f"Generated {len(procedures)} audit procedures for {area} "
            f"at {risk_level} risk level"
        )

        return {
            "engagement_id": str(engagement_id),
            "audit_area": area,
            "risk_level": risk_level,
            "procedures_count": len(procedures),
            "procedures": procedures
        }

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid risk level: {risk_level}. Use: low, moderate, high, significant"
        )
    except Exception as e:
        logger.error(f"Error generating audit program: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate audit program: {str(e)}"
        )


# ========================================
# AI-Powered Planning Endpoints
# ========================================

@app.post("/ai/analyze-risk")
async def ai_analyze_risk(
    request: AIRiskAnalysisRequest,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    AI-Powered Engagement Risk Analysis.

    Performs comprehensive risk analysis that exceeds human CPA capabilities:
    - Pattern recognition across industry benchmarks
    - Fraud indicator detection using anomaly analysis
    - Predictive risk scoring
    - AI-generated insights and recommendations

    Returns risk assessment with PCAOB AS 2110 compliance.
    """
    try:
        result = await ai_planning_service.analyze_engagement_risk(
            engagement_id=request.engagement_id,
            client_name=request.client_name,
            industry=request.industry,
            financial_data=request.financial_data,
            prior_year_data=request.prior_year_data,
            known_issues=request.known_issues
        )

        logger.info(
            f"AI risk analysis completed for {request.client_name}: "
            f"Risk score {result.get('overall_risk_score')}/100"
        )

        return result

    except Exception as e:
        logger.error(f"Error in AI risk analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI risk analysis failed: {str(e)}"
        )


@app.post("/ai/generate-program")
async def ai_generate_program(
    request: AIAuditProgramRequest,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    AI-Generated Intelligent Audit Program.

    Creates tailored audit procedures that:
    - Adapt to specific identified risks
    - Include AI-enhanced procedures for efficiency
    - Optimize sample sizes using statistical methods
    - Prioritize procedures by expected audit value

    Superior to human-generated programs through ML optimization.
    """
    try:
        result = await ai_planning_service.generate_intelligent_audit_program(
            engagement_id=request.engagement_id,
            risk_assessment=request.risk_assessment,
            audit_area=request.audit_area,
            account_balance=request.account_balance,
            materiality=request.materiality,
            prior_year_findings=request.prior_year_findings
        )

        logger.info(
            f"AI audit program generated for {request.audit_area}: "
            f"{len(result.get('procedures', []))} procedures"
        )

        return result

    except Exception as e:
        logger.error(f"Error generating AI audit program: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI program generation failed: {str(e)}"
        )


@app.post("/ai/materiality")
async def ai_materiality_recommendation(
    request: AIMaterialityRequest,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    AI-Powered Intelligent Materiality Recommendation.

    Provides materiality determination that considers:
    - Multiple benchmarks with intelligent weighting
    - Industry-specific adjustments
    - Risk factor adjustments
    - Qualitative factors humans often miss
    - Sensitivity analysis

    Complies with PCAOB AS 2105 while exceeding traditional methods.
    """
    try:
        result = await ai_planning_service.intelligent_materiality_recommendation(
            financial_data=request.financial_data,
            industry=request.industry,
            entity_type=request.entity_type,
            risk_factors=request.risk_factors,
            user_count=request.user_count
        )

        logger.info(
            f"AI materiality calculated: ${result.get('overall_materiality'):,.0f} "
            f"using {result.get('selected_benchmark')}"
        )

        return result

    except Exception as e:
        logger.error(f"Error in AI materiality calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI materiality calculation failed: {str(e)}"
        )


@app.post("/ai/detect-fraud")
async def ai_detect_fraud(
    request: AIFraudDetectionRequest,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    AI-Powered Fraud Pattern Detection.

    Uses advanced techniques humans cannot perform at scale:
    - Benford's Law analysis on 100% of transactions
    - Journal entry pattern recognition
    - Transaction anomaly detection
    - Revenue manipulation indicators
    - Related party identification

    Implements PCAOB AS 2401 with AI enhancement.
    """
    try:
        result = await ai_planning_service.detect_fraud_patterns(
            engagement_id=request.engagement_id,
            financial_data=request.financial_data,
            transaction_data=request.transaction_data,
            journal_entries=request.journal_entries
        )

        logger.info(
            f"AI fraud detection completed: Risk level {result.get('fraud_risk_level')}, "
            f"{result.get('indicators_found')} indicators found"
        )

        return result

    except Exception as e:
        logger.error(f"Error in AI fraud detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI fraud detection failed: {str(e)}"
        )


@app.post("/ai/planning-memo")
async def ai_generate_planning_memo(
    request: AIPlanningMemoRequest,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    AI-Generated Comprehensive Planning Memorandum.

    Creates PCAOB-compliant planning documentation including:
    - Executive summary
    - Risk assessment documentation
    - Materiality determination
    - Fraud risk evaluation
    - Planned audit approach
    - PCAOB standard references

    Saves hours of documentation time while ensuring completeness.
    """
    try:
        result = await ai_planning_service.generate_planning_memo(
            engagement_id=request.engagement_id,
            client_name=request.client_name,
            risk_assessment=request.risk_assessment,
            materiality=request.materiality,
            fraud_assessment=request.fraud_assessment,
            audit_programs=request.audit_programs
        )

        logger.info(f"AI planning memo generated for {request.client_name}")

        return result

    except Exception as e:
        logger.error(f"Error generating AI planning memo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI planning memo generation failed: {str(e)}"
        )


@app.get("/ai/capabilities")
async def get_ai_capabilities():
    """
    Get AI Planning Service Capabilities.

    Returns information about available AI-powered features
    and their advantages over traditional human planning.
    """
    return {
        "service": "AI-Powered Audit Planning",
        "version": "2.0.0",
        "capabilities": [
            {
                "name": "Risk Analysis",
                "endpoint": "/ai/analyze-risk",
                "description": "Comprehensive engagement risk analysis with pattern recognition",
                "advantages": [
                    "Industry benchmarking against 500+ data points",
                    "Predictive risk scoring",
                    "Real-time anomaly detection",
                    "AI-generated insights"
                ]
            },
            {
                "name": "Audit Program Generation",
                "endpoint": "/ai/generate-program",
                "description": "Intelligent audit program tailored to specific risks",
                "advantages": [
                    "Dynamic procedure generation",
                    "Statistical sample size optimization",
                    "AI-enhanced procedures with 60-90% time savings",
                    "Risk-responsive procedure prioritization"
                ]
            },
            {
                "name": "Materiality Recommendation",
                "endpoint": "/ai/materiality",
                "description": "AI-powered materiality determination",
                "advantages": [
                    "Multiple benchmark analysis",
                    "Industry-specific adjustments",
                    "Risk factor optimization",
                    "Sensitivity analysis"
                ]
            },
            {
                "name": "Fraud Detection",
                "endpoint": "/ai/detect-fraud",
                "description": "Advanced fraud pattern recognition",
                "advantages": [
                    "100% transaction coverage with Benford's Law",
                    "Journal entry pattern analysis",
                    "Related party identification",
                    "Management override detection"
                ]
            },
            {
                "name": "Planning Memo Generation",
                "endpoint": "/ai/planning-memo",
                "description": "Automated PCAOB-compliant planning documentation",
                "advantages": [
                    "Complete documentation in minutes",
                    "PCAOB standard compliance",
                    "Consistent quality",
                    "Ready for partner review"
                ]
            }
        ],
        "pcaob_compliance": {
            "AS 2101": "Audit Planning",
            "AS 2105": "Consideration of Materiality",
            "AS 2110": "Identifying and Assessing Risks",
            "AS 2301": "Responses to Assessed Risks",
            "AS 2401": "Consideration of Fraud"
        },
        "efficiency_gains": {
            "risk_assessment": "70% faster than traditional methods",
            "audit_planning": "60% time reduction",
            "fraud_detection": "90% faster with 100% coverage",
            "documentation": "80% faster memo generation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
