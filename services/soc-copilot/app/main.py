"""
SOC Copilot - Main FastAPI Application
Production-grade SOC 1 & SOC 2 audit platform
"""
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text

from .config import settings
from .database import get_db, init_db, close_db, set_rls_context
from .models import (
    SOCEngagement, User, UserRole, EngagementType, ReportType, EngagementStatus,
    ControlObjective, Control, TestPlan, Evidence, TestResult, Deviation,
    ManagementAssertion, SystemDescription, Report, Signature, Approval,
    WorkflowTask, AuditTrail, TSCCategory, TestType, TestStatus
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# LIFESPAN & INITIALIZATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Starting SOC Copilot service...")
    logger.info(f"Firm: {settings.FIRM_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database (in production, use Alembic migrations)
    if settings.ENVIRONMENT == "development":
        await init_db()

    yield

    # Cleanup
    logger.info("Shutting down SOC Copilot service...")
    await close_db()


app = FastAPI(
    title="SOC Copilot",
    description="AI-Assisted SOC 1 & SOC 2 Audit Platform | " + settings.FIRM_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# AUTHENTICATION
# ============================================================================

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Validate JWT token and return current user

    Args:
        credentials: JWT token from Authorization header
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Get user from database
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        user = result.scalar_one_or_none()

        if user is None or not user.is_active:
            raise credentials_exception

        # Set RLS context for this user
        await set_rls_context(db, user.id)

        return user

    except (JWTError, ValueError) as e:
        logger.error(f"Authentication error: {e}")
        raise credentials_exception


def require_role(*allowed_roles: UserRole):
    """
    Dependency to enforce role-based access control

    Usage:
        @app.get("/admin", dependencies=[Depends(require_role(UserRole.CPA_PARTNER))])
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


# ============================================================================
# PYDANTIC SCHEMAS (API Request/Response)
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    firm: str


class EngagementCreate(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=500)
    service_description: str
    engagement_type: EngagementType
    report_type: ReportType
    tsc_categories: Optional[List[TSCCategory]] = [TSCCategory.SECURITY]
    review_period_start: Optional[date] = None
    review_period_end: Optional[date] = None
    point_in_time_date: Optional[date] = None
    partner_id: Optional[UUID] = None  # Made optional - defaults to current user if Partner
    manager_id: Optional[UUID] = None  # Made optional - defaults to current user if Manager
    fiscal_year_end: Optional[date] = None


class EngagementResponse(BaseModel):
    id: UUID
    client_name: str
    service_description: str
    engagement_type: EngagementType
    report_type: ReportType
    status: EngagementStatus
    tsc_categories: Optional[List[str]]
    review_period_start: Optional[date]
    review_period_end: Optional[date]
    point_in_time_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ControlObjectiveCreate(BaseModel):
    objective_code: str
    objective_name: str
    objective_description: str
    icfr_assertion: Optional[str] = None
    tsc_category: Optional[TSCCategory] = None
    tsc_criteria: Optional[str] = None
    points_of_focus_2022: Optional[List[str]] = None


class ControlCreate(BaseModel):
    objective_id: UUID
    control_code: str
    control_name: str
    control_description: str
    control_type: str
    control_owner: Optional[str] = None
    frequency: Optional[str] = None
    automation_level: Optional[str] = None


class TestPlanCreate(BaseModel):
    control_id: UUID
    test_type: TestType
    test_objective: str
    test_procedures: str
    sample_size: Optional[int] = None
    sampling_method: Optional[str] = None
    population_size: Optional[int] = None
    required_evidence_types: Optional[List[str]] = None


class TestResultCreate(BaseModel):
    test_plan_id: UUID
    evidence_id: Optional[UUID] = None
    test_date: date
    passed: Optional[bool] = None
    findings: Optional[str] = None
    conclusion: Optional[str] = None
    sample_item_identifier: Optional[str] = None


class DeviationCreate(BaseModel):
    test_result_id: UUID
    control_id: Optional[UUID] = None
    deviation_description: str
    root_cause: Optional[str] = None
    severity: str
    impact_on_objective: Optional[str] = None
    remediation_plan: Optional[str] = None


class ReportCreate(BaseModel):
    engagement_id: UUID
    report_title: str
    report_date: date


# ============================================================================
# HEALTH & STATUS
# ============================================================================

@app.get("/", tags=["Status"])
async def root():
    """Root endpoint"""
    return {
        "service": "SOC Copilot",
        "version": settings.APP_VERSION,
        "firm": settings.FIRM_NAME,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="soc-copilot",
        version=settings.APP_VERSION,
        firm=settings.FIRM_NAME
    )


# ============================================================================
# ENGAGEMENT MANAGEMENT
# ============================================================================

@app.post(
    "/engagements",
    response_model=EngagementResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Engagements"],
    dependencies=[Depends(require_role(UserRole.CPA_PARTNER, UserRole.AUDIT_MANAGER))]
)
async def create_engagement(
    engagement_data: EngagementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new SOC 1 or SOC 2 engagement

    - **Requires:** Partner or Manager role
    - **Validates:** Period requirements for Type 1/Type 2
    - **Initializes:** Engagement team, workflow tasks
    """
    # Validate period requirements
    if engagement_data.report_type == ReportType.TYPE1 and not engagement_data.point_in_time_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type 1 engagements require a point-in-time date"
        )

    if engagement_data.report_type == ReportType.TYPE2:
        if not engagement_data.review_period_start or not engagement_data.review_period_end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Type 2 engagements require review period start and end dates"
            )

    # Default partner_id and manager_id to current user if not provided
    partner_id = engagement_data.partner_id or current_user.id
    manager_id = engagement_data.manager_id or current_user.id

    # Create engagement
    new_engagement = SOCEngagement(
        client_name=engagement_data.client_name,
        service_description=engagement_data.service_description,
        engagement_type=engagement_data.engagement_type,
        report_type=engagement_data.report_type,
        status=EngagementStatus.DRAFT,
        tsc_categories=[cat.value for cat in engagement_data.tsc_categories] if engagement_data.tsc_categories else ["SECURITY"],
        review_period_start=engagement_data.review_period_start,
        review_period_end=engagement_data.review_period_end,
        point_in_time_date=engagement_data.point_in_time_date,
        partner_id=partner_id,
        manager_id=manager_id,
        created_by=current_user.id,
        fiscal_year_end=engagement_data.fiscal_year_end
    )

    db.add(new_engagement)
    await db.commit()
    await db.refresh(new_engagement)

    # Log to audit trail
    audit_entry = AuditTrail(
        engagement_id=new_engagement.id,
        event_type="ENGAGEMENT_CREATED",
        entity_type="SOCEngagement",
        entity_id=new_engagement.id,
        actor_id=current_user.id,
        action="CREATE",
        after_state={
            "client_name": new_engagement.client_name,
            "engagement_type": new_engagement.engagement_type.value,
            "report_type": new_engagement.report_type.value
        }
    )
    db.add(audit_entry)
    await db.commit()

    logger.info(f"Created {engagement_data.engagement_type.value} {engagement_data.report_type.value} engagement: {new_engagement.client_name} (ID: {new_engagement.id})")

    return EngagementResponse.model_validate(new_engagement)


@app.get("/engagements", response_model=List[EngagementResponse], tags=["Engagements"])
async def list_engagements(
    status_filter: Optional[EngagementStatus] = None,
    engagement_type: Optional[EngagementType] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all accessible engagements

    - **RLS enforced:** Only returns engagements where user is a team member
    - **Filters:** status, engagement type
    """
    query = select(SOCEngagement)

    if status_filter:
        query = query.where(SOCEngagement.status == status_filter)

    if engagement_type:
        query = query.where(SOCEngagement.engagement_type == engagement_type)

    query = query.offset(skip).limit(limit).order_by(SOCEngagement.created_at.desc())

    result = await db.execute(query)
    engagements = result.scalars().all()

    return [EngagementResponse.model_validate(eng) for eng in engagements]


@app.get("/engagements/{engagement_id}", response_model=EngagementResponse, tags=["Engagements"])
async def get_engagement(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get engagement by ID"""
    result = await db.execute(
        select(SOCEngagement).where(SOCEngagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()

    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found or access denied"
        )

    return EngagementResponse.model_validate(engagement)


@app.post("/engagements/{engagement_id}/transition", tags=["Engagements"])
async def transition_engagement_status(
    engagement_id: UUID,
    new_status: EngagementStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transition engagement status through workflow

    Valid transitions:
    - DRAFT → PLANNING
    - PLANNING → FIELDWORK
    - FIELDWORK → REVIEW
    - REVIEW → PARTNER_REVIEW
    - PARTNER_REVIEW → SIGNED (requires CPA Partner signature)
    - SIGNED → RELEASED (requires CPA Partner approval)
    """
    result = await db.execute(
        select(SOCEngagement).where(SOCEngagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()

    if not engagement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Engagement not found")

    # Define valid transitions
    valid_transitions = {
        EngagementStatus.DRAFT: [EngagementStatus.PLANNING],
        EngagementStatus.PLANNING: [EngagementStatus.FIELDWORK, EngagementStatus.DRAFT],
        EngagementStatus.FIELDWORK: [EngagementStatus.REVIEW, EngagementStatus.PLANNING],
        EngagementStatus.REVIEW: [EngagementStatus.PARTNER_REVIEW, EngagementStatus.FIELDWORK],
        EngagementStatus.PARTNER_REVIEW: [EngagementStatus.SIGNED, EngagementStatus.REVIEW],
        EngagementStatus.SIGNED: [EngagementStatus.RELEASED],
        EngagementStatus.RELEASED: [EngagementStatus.ARCHIVED]
    }

    if new_status not in valid_transitions.get(engagement.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from {engagement.status.value} to {new_status.value}"
        )

    # Special validations for critical transitions
    if new_status == EngagementStatus.SIGNED:
        # Require CPA Partner role
        if current_user.role != UserRole.CPA_PARTNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only CPA Partners can sign reports"
            )

        # Check if report exists and is approved
        report_result = await db.execute(
            select(Report).where(
                and_(
                    Report.engagement_id == engagement_id,
                    Report.is_draft == False
                )
            ).order_by(Report.created_at.desc()).limit(1)
        )
        report = report_result.scalar_one_or_none()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot sign: No finalized report found"
            )

    old_status = engagement.status
    engagement.status = new_status
    engagement.updated_at = datetime.utcnow()

    if new_status == EngagementStatus.RELEASED:
        engagement.locked_at = datetime.utcnow()
        engagement.locked_by = current_user.id

    await db.commit()

    # Audit trail
    audit_entry = AuditTrail(
        engagement_id=engagement_id,
        event_type="STATUS_TRANSITION",
        entity_type="SOCEngagement",
        entity_id=engagement_id,
        actor_id=current_user.id,
        action="UPDATE",
        before_state={"status": old_status.value},
        after_state={"status": new_status.value}
    )
    db.add(audit_entry)
    await db.commit()

    logger.info(f"Engagement {engagement_id} transitioned from {old_status.value} to {new_status.value} by {current_user.email}")

    return {
        "message": f"Status updated to {new_status.value}",
        "old_status": old_status.value,
        "new_status": new_status.value
    }


# ============================================================================
# CONTROL OBJECTIVES & CONTROLS
# ============================================================================

@app.post("/engagements/{engagement_id}/objectives", status_code=status.HTTP_201_CREATED, tags=["Controls"])
async def create_control_objective(
    engagement_id: UUID,
    objective_data: ControlObjectiveCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a control objective

    - **SOC 1:** Set icfr_assertion (existence, completeness, accuracy, etc.)
    - **SOC 2:** Set tsc_category and tsc_criteria (CC1.1, A1.1, etc.)
    """
    new_objective = ControlObjective(
        engagement_id=engagement_id,
        objective_code=objective_data.objective_code,
        objective_name=objective_data.objective_name,
        objective_description=objective_data.objective_description,
        icfr_assertion=objective_data.icfr_assertion,
        tsc_category=objective_data.tsc_category,
        tsc_criteria=objective_data.tsc_criteria,
        points_of_focus_2022=objective_data.points_of_focus_2022
    )

    db.add(new_objective)
    await db.commit()
    await db.refresh(new_objective)

    return new_objective


@app.post("/engagements/{engagement_id}/controls", status_code=status.HTTP_201_CREATED, tags=["Controls"])
async def create_control(
    engagement_id: UUID,
    control_data: ControlCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a control"""
    new_control = Control(
        engagement_id=engagement_id,
        objective_id=control_data.objective_id,
        control_code=control_data.control_code,
        control_name=control_data.control_name,
        control_description=control_data.control_description,
        control_type=control_data.control_type,
        control_owner=control_data.control_owner,
        frequency=control_data.frequency,
        automation_level=control_data.automation_level
    )

    db.add(new_control)
    await db.commit()
    await db.refresh(new_control)

    return new_control


# ============================================================================
# TESTING & EVIDENCE
# ============================================================================

@app.post("/engagements/{engagement_id}/test-plans", status_code=status.HTTP_201_CREATED, tags=["Testing"])
async def create_test_plan(
    engagement_id: UUID,
    test_plan_data: TestPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a test plan

    - **Walkthrough:** Interview process owners
    - **Design Evaluation:** Review policies, inspect configs
    - **Operating Effectiveness:** Test samples across period (Type 2)
    """
    new_plan = TestPlan(
        engagement_id=engagement_id,
        control_id=test_plan_data.control_id,
        test_type=test_plan_data.test_type,
        test_objective=test_plan_data.test_objective,
        test_procedures=test_plan_data.test_procedures,
        sample_size=test_plan_data.sample_size,
        sampling_method=test_plan_data.sampling_method,
        population_size=test_plan_data.population_size,
        required_evidence_types=test_plan_data.required_evidence_types
    )

    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)

    return new_plan


@app.post("/engagements/{engagement_id}/test-results", status_code=status.HTTP_201_CREATED, tags=["Testing"])
async def create_test_result(
    engagement_id: UUID,
    test_result_data: TestResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Document test result"""
    new_result = TestResult(
        test_plan_id=test_result_data.test_plan_id,
        evidence_id=test_result_data.evidence_id,
        test_date=test_result_data.test_date,
        tested_by=current_user.id,
        passed=test_result_data.passed,
        findings=test_result_data.findings,
        conclusion=test_result_data.conclusion,
        sample_item_identifier=test_result_data.sample_item_identifier,
        test_status=TestStatus.COMPLETED if test_result_data.passed is not None else TestStatus.IN_PROGRESS
    )

    db.add(new_result)
    await db.commit()
    await db.refresh(new_result)

    return new_result


# ============================================================================
# REPORTS
# ============================================================================

@app.post("/engagements/{engagement_id}/reports", status_code=status.HTTP_201_CREATED, tags=["Reports"])
async def create_report(
    engagement_id: UUID,
    report_data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new report draft

    - Generates report template based on engagement type (SOC 1/SOC 2)
    - Includes all required sections per AT-C 320 and TSC
    """
    new_report = Report(
        engagement_id=engagement_id,
        report_title=report_data.report_title,
        report_date=report_data.report_date,
        is_draft=True,
        restricted_distribution=settings.REPORT_RESTRICTED_DISTRIBUTION_DEFAULT,
        watermark_text=f"{settings.FIRM_NAME} - Restricted Distribution" if settings.REPORT_WATERMARK_ENABLED else None,
        drafted_by=current_user.id,
        drafted_at=datetime.utcnow()
    )

    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)

    return new_report


# ============================================================================
# AUDIT TRAIL
# ============================================================================

@app.get("/engagements/{engagement_id}/audit-trail", tags=["Audit Trail"])
async def get_audit_trail(
    engagement_id: UUID,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get immutable audit trail for engagement

    - Shows all actions with timestamps
    - Hash chain ensures tamper detection
    """
    result = await db.execute(
        select(AuditTrail)
        .where(AuditTrail.engagement_id == engagement_id)
        .order_by(AuditTrail.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    trail_entries = result.scalars().all()

    return [
        {
            "event_type": entry.event_type,
            "entity_type": entry.entity_type,
            "action": entry.action,
            "actor_id": str(entry.actor_id) if entry.actor_id else None,
            "created_at": entry.created_at,
            "event_hash": entry.event_hash[:16] + "...",  # Truncated for display
            "before_state": entry.before_state,
            "after_state": entry.after_state
        }
        for entry in trail_entries
    ]


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1
    )
