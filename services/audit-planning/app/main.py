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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
