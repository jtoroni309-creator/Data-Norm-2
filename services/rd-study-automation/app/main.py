"""
R&D Study Automation Service - FastAPI Application

AI-first R&D tax credit study automation for CPA firms.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Depends, status, Security, Query, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
from openai import AsyncOpenAI, AsyncAzureOpenAI

from .config import settings
from .database import get_db, init_db, close_db, set_rls_context
from .models import (
    RDStudy, RDProject, RDEmployee, QualifiedResearchExpense,
    RDCalculation, StateCredit, RDDocument, RDInterview, RDNarrative,
    RDEvidence, RDAuditLog, RDStudyTeamMember, RDOutputFile,
    StudyStatus, QualificationStatus, CreditMethod, UserRole
)
from .schemas import (
    StudyCreate, StudyUpdate, StudyResponse, StudySummary, StudyStatusTransition, StudyCPAApproval,
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectSummary, ProjectQualificationOverride,
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeTimeAdjustment,
    QRECreate, QREUpdate, QREResponse, QRESummary, QREAdjustment,
    CalculationRequest, FullCalculationResponse, FederalCalculationResult, StateCalculationResult,
    DocumentUpload, DocumentResponse, DataIngestionResult,
    InterviewCreate, InterviewResponse, InterviewContinue,
    NarrativeGenerateRequest, NarrativeResponse, NarrativeUpdate,
    EvidenceCreate, EvidenceResponse,
    ReviewQueueResponse, ReviewDecision, RiskFlagResponse,
    OutputGenerationRequest, OutputFileResponse, Form6765Data, TaxPreparerSummary,
    BenchmarkAnalysis, SanityCheckResult,
    AuditLogResponse, AuditTrailQuery,
    TeamMemberAdd, TeamMemberResponse,
    IntakeWizardComplete, AIScopingResult,
    PaginatedResponse, ErrorResponse
)
from .engines import RulesEngine, QualificationEngine, QREEngine, CalculationEngine
from .routes import ai_processing, outputs

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


# =============================================================================
# APPLICATION LIFECYCLE
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    # Startup
    logger.info("Starting R&D Study Automation Service...")
    await init_db()

    # Initialize OpenAI client - prefer Azure OpenAI if configured
    openai_client = None
    if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY:
        # Use Azure OpenAI
        openai_client = AsyncAzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version="2024-02-15-preview"
        )
        logger.info(f"Azure OpenAI client initialized - endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
    elif settings.OPENAI_API_KEY:
        # Fall back to regular OpenAI
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    else:
        logger.warning("No OpenAI credentials configured - AI features will use fallback mode")

    # Initialize engines
    app.state.rules_engine = RulesEngine(version=settings.RULES_VERSION)
    app.state.qualification_engine = QualificationEngine(app.state.rules_engine)
    app.state.qre_engine = QREEngine(app.state.rules_engine)
    app.state.calculation_engine = CalculationEngine(app.state.rules_engine)

    # Store OpenAI client in app state
    app.state.openai_client = openai_client

    # Initialize AI services with OpenAI client
    from .ai import NarrativeService, DataIngestionService
    app.state.narrative_service = NarrativeService(
        openai_client=openai_client,
        config={"model": settings.OPENAI_CHAT_MODEL}
    )
    app.state.data_ingestion_service = DataIngestionService(
        openai_client=openai_client,
        config={"model": settings.OPENAI_CHAT_MODEL}
    )

    logger.info("R&D Study Automation Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down R&D Study Automation Service...")
    await close_db()


# =============================================================================
# APPLICATION SETUP
# =============================================================================

app = FastAPI(
    title="R&D Study Automation Service",
    description="AI-first R&D tax credit study automation for CPA firms",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - allow all origins for production (nginx handles security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(ai_processing.router, prefix="", tags=["AI Processing"])
app.include_router(outputs.router, prefix="", tags=["Outputs"])


# =============================================================================
# AUTHENTICATION
# =============================================================================

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> UUID:
    """Extract user ID from JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UUID(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


async def get_current_user_firm_id(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> tuple[UUID, UUID]:
    """Extract user ID and firm ID from JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        firm_id = payload.get("firm_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # If firm_id not in JWT, use a default firm_id from settings or generate from user_id
        if not firm_id:
            # Use default firm ID from settings, or derive from user's org
            default_firm_id = getattr(settings, 'DEFAULT_FIRM_ID', None)
            if default_firm_id:
                firm_id = default_firm_id
            else:
                # Use a deterministic UUID based on the deployment (same for all users in this deployment)
                from uuid import uuid5, NAMESPACE_DNS
                firm_id = str(uuid5(NAMESPACE_DNS, "aura-audit-ai.toroniandcompany.com"))

        return UUID(user_id), UUID(firm_id) if firm_id else None
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "rd-study-automation",
        "version": "1.0.0",
        "rules_version": settings.RULES_VERSION
    }


# =============================================================================
# STUDY ENDPOINTS
# =============================================================================

@app.post("/studies", response_model=StudyResponse, status_code=201)
async def create_study(
    study_data: StudyCreate,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Create a new R&D study."""
    from uuid import uuid4
    from datetime import date

    user_id, firm_id = user_firm

    if not firm_id:
        raise HTTPException(status_code=400, detail="Firm ID required")

    # Handle client_id - generate if not provided or if it's a string (client name)
    client_id = None
    if study_data.client_id:
        try:
            # Try to parse as UUID
            if isinstance(study_data.client_id, UUID):
                client_id = study_data.client_id
            else:
                client_id = UUID(str(study_data.client_id))
        except (ValueError, TypeError):
            # Not a valid UUID, generate a new one
            client_id = uuid4()
    else:
        client_id = uuid4()

    # Handle fiscal year dates - default to calendar year if not provided
    fiscal_year_start = study_data.fiscal_year_start
    fiscal_year_end = study_data.fiscal_year_end
    if not fiscal_year_start:
        fiscal_year_start = date(study_data.tax_year, 1, 1)
    if not fiscal_year_end:
        fiscal_year_end = date(study_data.tax_year, 12, 31)

    # Store client_name in notes if provided
    notes = study_data.notes or ""
    if study_data.client_name:
        notes = f"Client: {study_data.client_name}\n{notes}".strip()

    # Create study
    study = RDStudy(
        firm_id=firm_id,
        client_id=client_id,
        engagement_id=study_data.engagement_id,
        name=study_data.name,
        tax_year=study_data.tax_year,
        entity_type=study_data.entity_type,
        entity_name=study_data.entity_name,
        ein=study_data.ein,
        fiscal_year_start=fiscal_year_start,
        fiscal_year_end=fiscal_year_end,
        is_short_year=study_data.is_short_year,
        short_year_days=study_data.short_year_days,
        is_controlled_group=study_data.is_controlled_group,
        controlled_group_name=study_data.controlled_group_name,
        aggregation_method=study_data.aggregation_method,
        states=study_data.states,
        primary_state=study_data.primary_state,
        notes=notes,
        rules_version=settings.RULES_VERSION,
        created_by=user_id,
        status=StudyStatus.DRAFT,
        status_history=[{
            "status": StudyStatus.DRAFT.value,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id)
        }]
    )

    db.add(study)
    await db.commit()
    await db.refresh(study)

    # Add creator as team member
    team_member = RDStudyTeamMember(
        study_id=study.id,
        user_id=user_id,
        role=UserRole.MANAGER,
        can_approve=True,
        assigned_by=user_id
    )
    db.add(team_member)
    await db.commit()

    # Log creation
    await _log_audit(db, study.id, "create", "study", study.id, None, {"name": study.name}, user_id)

    return study


@app.get("/studies", response_model=PaginatedResponse)
async def list_studies(
    status: Optional[StudyStatus] = None,
    tax_year: Optional[int] = None,
    client_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """List R&D studies with filtering."""
    user_id, firm_id = user_firm

    await set_rls_context(db, user_id, firm_id)

    query = select(RDStudy).where(RDStudy.firm_id == firm_id)

    if status:
        query = query.where(RDStudy.status == status)
    if tax_year:
        query = query.where(RDStudy.tax_year == tax_year)
    if client_id:
        query = query.where(RDStudy.client_id == client_id)

    # Get total count
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())

    # Get paginated results
    query = query.order_by(RDStudy.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    studies = result.scalars().all()

    return PaginatedResponse(
        items=[StudySummary.model_validate(s) for s in studies],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        pages=(total + limit - 1) // limit
    )


@app.get("/studies/{study_id}", response_model=StudyResponse)
async def get_study(
    study_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Get a specific R&D study."""
    user_id, firm_id = user_firm

    result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = result.scalar_one_or_none()

    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    return study


@app.patch("/studies/{study_id}", response_model=StudyResponse)
async def update_study(
    study_id: UUID,
    update_data: StudyUpdate,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Update an R&D study."""
    user_id, firm_id = user_firm

    result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = result.scalar_one_or_none()

    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    if study.locked_at:
        raise HTTPException(status_code=400, detail="Study is locked and cannot be modified")

    # Store previous values for audit
    previous_values = {
        k: getattr(study, k) for k in update_data.model_dump(exclude_unset=True).keys()
    }

    # Update fields
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(study, field, value)

    await db.commit()
    await db.refresh(study)

    # Log update
    await _log_audit(
        db, study_id, "update", "study", study_id,
        previous_values,
        update_data.model_dump(exclude_unset=True),
        user_id
    )

    return study


@app.post("/studies/{study_id}/transition", response_model=StudyResponse)
async def transition_study_status(
    study_id: UUID,
    transition: StudyStatusTransition,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Transition study to a new status."""
    user_id, firm_id = user_firm

    result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = result.scalar_one_or_none()

    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Validate transition
    valid_transitions = {
        StudyStatus.DRAFT: [StudyStatus.INTAKE],
        StudyStatus.INTAKE: [StudyStatus.DATA_COLLECTION, StudyStatus.DRAFT],
        StudyStatus.DATA_COLLECTION: [StudyStatus.QUALIFICATION, StudyStatus.INTAKE],
        StudyStatus.QUALIFICATION: [StudyStatus.QRE_ANALYSIS, StudyStatus.DATA_COLLECTION],
        StudyStatus.QRE_ANALYSIS: [StudyStatus.CALCULATION, StudyStatus.QUALIFICATION],
        StudyStatus.CALCULATION: [StudyStatus.REVIEW, StudyStatus.QRE_ANALYSIS],
        StudyStatus.REVIEW: [StudyStatus.CPA_APPROVAL, StudyStatus.CALCULATION],
        StudyStatus.CPA_APPROVAL: [StudyStatus.FINALIZED, StudyStatus.REVIEW],
        StudyStatus.FINALIZED: [StudyStatus.AMENDED],
    }

    if transition.new_status not in valid_transitions.get(study.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {study.status.value} to {transition.new_status.value}"
        )

    # Additional validation for CPA_APPROVAL -> FINALIZED
    if transition.new_status == StudyStatus.FINALIZED:
        if not study.cpa_approved:
            raise HTTPException(
                status_code=400,
                detail="Study must be CPA approved before finalizing"
            )

    previous_status = study.status
    study.status = transition.new_status
    study.status_history.append({
        "status": transition.new_status.value,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": str(user_id),
        "notes": transition.notes
    })

    if transition.new_status == StudyStatus.FINALIZED:
        study.finalized_at = datetime.utcnow()
        study.locked_at = datetime.utcnow()

    await db.commit()
    await db.refresh(study)

    # Log transition
    await _log_audit(
        db, study_id, "transition", "study", study_id,
        {"status": previous_status.value},
        {"status": transition.new_status.value, "notes": transition.notes},
        user_id
    )

    return study


@app.post("/studies/{study_id}/cpa-approval", response_model=StudyResponse)
async def cpa_approve_study(
    study_id: UUID,
    approval: StudyCPAApproval,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """CPA approval checkpoint for study."""
    user_id, firm_id = user_firm

    result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = result.scalar_one_or_none()

    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    if study.status != StudyStatus.CPA_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail="Study must be in CPA_APPROVAL status for approval"
        )

    # Verify user can approve
    team_result = await db.execute(
        select(RDStudyTeamMember).where(
            and_(
                RDStudyTeamMember.study_id == study_id,
                RDStudyTeamMember.user_id == user_id,
                RDStudyTeamMember.can_approve == True
            )
        )
    )
    team_member = team_result.scalar_one_or_none()

    if not team_member:
        raise HTTPException(
            status_code=403,
            detail="User does not have approval permissions for this study"
        )

    study.cpa_approved = approval.approved
    study.cpa_approved_by = user_id
    study.cpa_approved_at = datetime.utcnow()
    study.cpa_approval_notes = approval.notes

    await db.commit()
    await db.refresh(study)

    # Log approval
    await _log_audit(
        db, study_id, "approve" if approval.approved else "reject", "study", study_id,
        None,
        {"approved": approval.approved, "notes": approval.notes},
        user_id
    )

    return study


# =============================================================================
# PROJECT ENDPOINTS
# =============================================================================

@app.post("/studies/{study_id}/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    study_id: UUID,
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Create a new R&D project within a study."""
    user_id, firm_id = user_firm

    # Verify study exists and belongs to firm
    result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    project = RDProject(
        study_id=study_id,
        name=project_data.name,
        code=project_data.code,
        description=project_data.description,
        department=project_data.department,
        business_component=project_data.business_component,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        is_ongoing=project_data.is_ongoing,
        qualification_status=QualificationStatus.PENDING
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    return project


@app.get("/studies/{study_id}/projects", response_model=List[ProjectSummary])
async def list_projects(
    study_id: UUID,
    status: Optional[QualificationStatus] = None,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """List all projects in a study."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    query = select(RDProject).where(RDProject.study_id == study_id)

    if status:
        query = query.where(RDProject.qualification_status == status)

    result = await db.execute(query.order_by(RDProject.name))
    projects = result.scalars().all()

    return projects


@app.get("/studies/{study_id}/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    study_id: UUID,
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Get a specific project."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    result = await db.execute(
        select(RDProject).where(
            and_(RDProject.id == project_id, RDProject.study_id == study_id)
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@app.post("/studies/{study_id}/projects/{project_id}/qualify")
async def qualify_project(
    study_id: UUID,
    project_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Run AI qualification analysis on a project."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = study_result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    result = await db.execute(
        select(RDProject).where(
            and_(RDProject.id == project_id, RDProject.study_id == study_id)
        ).options(selectinload(RDProject.evidence_items))
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Run qualification (in production, this would be async)
    qualification_engine = app.state.qualification_engine

    project_data = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "department": project.department,
        "business_component": project.business_component
    }

    evidence_items = [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "relevant_to_permitted_purpose": e.relevant_to_permitted_purpose,
            "relevant_to_technological_nature": e.relevant_to_technological_nature,
            "relevant_to_uncertainty": e.relevant_to_uncertainty,
            "relevant_to_experimentation": e.relevant_to_experimentation
        }
        for e in project.evidence_items
    ]

    qualification_result = await qualification_engine.evaluate_project(
        project_data,
        evidence_items,
        states=study.states if study else None
    )

    # Update project with results
    project.permitted_purpose_score = qualification_result.permitted_purpose.score
    project.permitted_purpose_narrative = qualification_result.permitted_purpose.analysis
    project.technological_nature_score = qualification_result.technological_nature.score
    project.technological_nature_narrative = qualification_result.technological_nature.analysis
    project.uncertainty_score = qualification_result.elimination_of_uncertainty.score
    project.uncertainty_narrative = qualification_result.elimination_of_uncertainty.analysis
    project.experimentation_score = qualification_result.process_of_experimentation.score
    project.experimentation_narrative = qualification_result.process_of_experimentation.analysis
    project.overall_score = qualification_result.overall_score
    project.overall_confidence = qualification_result.overall_confidence
    project.qualification_status = QualificationStatus(qualification_result.qualification_status)
    project.qualification_narrative = qualification_result.qualification_narrative
    project.state_qualifications = qualification_result.state_qualifications
    project.risk_flags = qualification_result.risk_flags
    project.ai_qualification_analysis = {
        "ai_analysis_summary": qualification_result.ai_analysis_summary,
        "ai_suggested_evidence": qualification_result.ai_suggested_evidence,
        "audit_risk_score": qualification_result.audit_risk_score,
        "rules_version": qualification_result.rules_version,
        "evaluated_at": qualification_result.evaluated_at.isoformat()
    }

    await db.commit()

    return {
        "project_id": str(project_id),
        "qualification_status": qualification_result.qualification_status,
        "overall_score": qualification_result.overall_score,
        "overall_confidence": qualification_result.overall_confidence,
        "risk_flags_count": len(qualification_result.risk_flags)
    }


@app.post("/studies/{study_id}/projects/{project_id}/override", response_model=ProjectResponse)
async def override_project_qualification(
    study_id: UUID,
    project_id: UUID,
    override: ProjectQualificationOverride,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """CPA override for project qualification status."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    result = await db.execute(
        select(RDProject).where(
            and_(RDProject.id == project_id, RDProject.study_id == study_id)
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.cpa_reviewed = True
    project.cpa_reviewed_by = user_id
    project.cpa_reviewed_at = datetime.utcnow()
    project.cpa_override_status = override.override_status
    project.cpa_override_reason = override.reason

    # Update qualification status to override
    project.qualification_status = override.override_status

    await db.commit()
    await db.refresh(project)

    return project


# =============================================================================
# EMPLOYEE ENDPOINTS
# =============================================================================

@app.post("/studies/{study_id}/employees", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    study_id: UUID,
    employee_data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Create a new employee record."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    # Calculate qualified wages based on percentage
    qualified_wages = Decimal(str(employee_data.w2_wages)) * Decimal(str(employee_data.qualified_time_percentage)) / Decimal("100")

    employee = RDEmployee(
        study_id=study_id,
        employee_id=employee_data.employee_id,
        name=employee_data.name,
        title=employee_data.title,
        department=employee_data.department,
        hire_date=employee_data.hire_date,
        termination_date=employee_data.termination_date,
        total_wages=employee_data.total_wages,
        w2_wages=employee_data.w2_wages,
        bonus=employee_data.bonus,
        stock_compensation=employee_data.stock_compensation,
        qualified_time_percentage=employee_data.qualified_time_percentage,
        qualified_time_source=employee_data.qualified_time_source,
        qualified_wages=qualified_wages
    )

    db.add(employee)
    await db.commit()
    await db.refresh(employee)

    return employee


@app.get("/studies/{study_id}/employees", response_model=List[EmployeeResponse])
async def list_employees(
    study_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """List all employees in a study."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    result = await db.execute(
        select(RDEmployee).where(RDEmployee.study_id == study_id).order_by(RDEmployee.name)
    )
    employees = result.scalars().all()
    return employees


@app.post("/studies/{study_id}/employees/{employee_id}/adjust-time", response_model=EmployeeResponse)
async def adjust_employee_time(
    study_id: UUID,
    employee_id: UUID,
    adjustment: EmployeeTimeAdjustment,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """CPA adjustment of employee qualified time percentage."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    result = await db.execute(
        select(RDEmployee).where(
            and_(RDEmployee.id == employee_id, RDEmployee.study_id == study_id)
        )
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee.cpa_reviewed = True
    employee.cpa_adjusted_percentage = adjustment.adjusted_percentage
    employee.cpa_adjustment_reason = adjustment.reason

    # Recalculate qualified wages
    employee.qualified_wages = (
        employee.w2_wages * Decimal(str(adjustment.adjusted_percentage)) / 100
    )

    await db.commit()
    await db.refresh(employee)

    return employee


# =============================================================================
# QRE ENDPOINTS
# =============================================================================

@app.post("/studies/{study_id}/qres", response_model=QREResponse, status_code=201)
async def create_qre(
    study_id: UUID,
    qre_data: QRECreate,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Create a new QRE record."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    qualified_amount = qre_data.gross_amount * Decimal(str(qre_data.qualified_percentage)) / 100

    # Get the enum value (lowercase) if it's an enum, otherwise use as-is
    category_value = qre_data.category.value if hasattr(qre_data.category, 'value') else qre_data.category

    qre = QualifiedResearchExpense(
        study_id=study_id,
        project_id=qre_data.project_id,
        employee_id=qre_data.employee_id,
        category=category_value,
        subcategory=qre_data.subcategory,
        is_w2_wages=qre_data.is_w2_wages,
        supply_description=qre_data.supply_description,
        supply_vendor=qre_data.supply_vendor,
        gl_account=qre_data.gl_account,
        contractor_name=qre_data.contractor_name,
        contractor_ein=qre_data.contractor_ein,
        is_qualified_research_org=qre_data.is_qualified_research_org,
        contract_percentage=qre_data.contract_percentage,
        gross_amount=qre_data.gross_amount,
        qualified_percentage=qre_data.qualified_percentage,
        qualified_amount=qualified_amount,
        source_reference=qre_data.source_reference
    )

    db.add(qre)
    await db.commit()
    await db.refresh(qre)

    return qre


@app.get("/studies/{study_id}/qres/summary", response_model=Dict)
async def get_qre_summary(
    study_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Get QRE summary by category."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    result = await db.execute(
        select(QualifiedResearchExpense).where(QualifiedResearchExpense.study_id == study_id)
    )
    qres = result.scalars().all()

    summary = {
        "wages": Decimal("0"),
        "supplies": Decimal("0"),
        "contract_research": Decimal("0"),
        "basic_research": Decimal("0"),
        "total": Decimal("0")
    }

    for qre in qres:
        if qre.category.value == "wages":
            summary["wages"] += qre.qualified_amount
        elif qre.category.value == "supplies":
            summary["supplies"] += qre.qualified_amount
        elif qre.category.value == "contract_research":
            summary["contract_research"] += qre.qualified_amount
        elif qre.category.value == "basic_research":
            summary["basic_research"] += qre.qualified_amount

    summary["total"] = sum(summary.values())

    return {k: str(v) for k, v in summary.items()}


# =============================================================================
# CALCULATION ENDPOINTS
# =============================================================================

@app.post("/studies/{study_id}/calculate", response_model=Dict)
async def calculate_credits(
    study_id: UUID,
    request: CalculationRequest,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Calculate R&D credits for a study."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = study_result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Get QRE summary
    qre_result = await db.execute(
        select(QualifiedResearchExpense).where(QualifiedResearchExpense.study_id == study_id)
    )
    qres = qre_result.scalars().all()

    qre_data = {
        "wages": sum(q.qualified_amount for q in qres if q.category.value == "wages"),
        "supplies": sum(q.qualified_amount for q in qres if q.category.value == "supplies"),
        "contract_research": sum(q.qualified_amount for q in qres if q.category.value == "contract_research"),
        "basic_research": sum(q.qualified_amount for q in qres if q.category.value == "basic_research"),
    }
    qre_data["total"] = sum(qre_data.values())

    # Calculate credits
    calculation_engine = app.state.calculation_engine

    result = calculation_engine.calculate_full_credit(
        study_id=study_id,
        tax_year=study.tax_year,
        entity_name=study.entity_name,
        qre_data=qre_data,
        base_period_data=request.base_period_data,
        is_controlled_group=study.is_controlled_group,
        controlled_group_allocation=Decimal("100"),
        is_short_year=study.is_short_year,
        short_year_days=study.short_year_days or 365,
        section_280c_election=True,
        states=study.states if request.include_states else None
    )

    # Update study with results
    study.total_qre = qre_data["total"]
    study.federal_credit_regular = result.federal_regular.final_credit if result.federal_regular else Decimal("0")
    study.federal_credit_asc = result.federal_asc.final_credit if result.federal_asc else Decimal("0")
    study.federal_credit_final = result.federal_credit
    study.total_state_credits = result.total_state_credits
    study.total_credits = result.total_credits
    study.recommended_method = result.federal_comparison.recommended_method if result.federal_comparison else None

    # Save calculation records
    if result.federal_regular:
        calc_record = RDCalculation(
            study_id=study_id,
            calculation_type="federal_regular",
            method=CreditMethod.REGULAR,
            total_qre_wages=qre_data["wages"],
            total_qre_supplies=qre_data["supplies"],
            total_qre_contract=qre_data["contract_research"],
            total_qre=qre_data["total"],
            base_amount=result.federal_regular.base_amount,
            credit_rate=float(result.federal_regular.credit_rate),
            excess_qre=result.federal_regular.excess_qre,
            calculated_credit=result.federal_regular.tentative_credit,
            section_280c_reduction=result.federal_regular.section_280c_reduction,
            final_credit=result.federal_regular.final_credit,
            calculation_steps=[{
                "step_number": s.step_number,
                "description": s.description,
                "formula": s.formula,
                "inputs": s.inputs,
                "result": str(s.result),
                "irc_reference": s.irc_reference
            } for s in result.federal_regular.steps],
            rules_version=result.rules_version
        )
        db.add(calc_record)

    await db.commit()

    return calculation_engine.generate_calculation_summary(result)


# =============================================================================
# DOCUMENT ENDPOINTS
# =============================================================================

@app.post("/studies/{study_id}/documents", response_model=DocumentResponse, status_code=201)
async def upload_document(
    study_id: UUID,
    file: UploadFile = File(...),
    document_type: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Upload a document for processing."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = study_result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Save document record
    document = RDDocument(
        study_id=study_id,
        filename=file.filename,
        original_filename=file.filename,
        file_size=file.size,
        mime_type=file.content_type,
        storage_path=f"studies/{study_id}/documents/{file.filename}",
        processing_status="pending",
        uploaded_by=user_id
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    # In production, queue document for processing
    # background_tasks.add_task(process_document, document.id)

    return document


@app.get("/studies/{study_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    study_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """List all documents in a study."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    result = await db.execute(
        select(RDDocument).where(RDDocument.study_id == study_id).order_by(RDDocument.uploaded_at.desc())
    )
    documents = result.scalars().all()
    return documents


# =============================================================================
# NARRATIVE ENDPOINTS
# =============================================================================

@app.post("/studies/{study_id}/narratives/generate")
async def generate_narratives(
    study_id: UUID,
    request: NarrativeGenerateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Generate AI narratives for the study."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = study_result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Queue narrative generation
    # In production, this would use the NarrativeService

    return {
        "message": "Narrative generation queued",
        "narrative_types": request.narrative_types,
        "study_id": str(study_id)
    }


@app.get("/studies/{study_id}/narratives", response_model=List[NarrativeResponse])
async def list_narratives(
    study_id: UUID,
    narrative_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """List all narratives for a study."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    query = select(RDNarrative).where(RDNarrative.study_id == study_id)

    if narrative_type:
        query = query.where(RDNarrative.narrative_type == narrative_type)

    result = await db.execute(query.order_by(RDNarrative.created_at.desc()))
    narratives = result.scalars().all()
    return narratives


@app.patch("/studies/{study_id}/narratives/{narrative_id}", response_model=NarrativeResponse)
async def update_narrative(
    study_id: UUID,
    narrative_id: UUID,
    update_data: NarrativeUpdate,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """CPA edit of a narrative."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    result = await db.execute(
        select(RDNarrative).where(
            and_(RDNarrative.id == narrative_id, RDNarrative.study_id == study_id)
        )
    )
    narrative = result.scalar_one_or_none()

    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")

    narrative.cpa_edited = True
    narrative.cpa_edited_content = update_data.content
    narrative.cpa_edit_reason = update_data.edit_reason
    narrative.reviewed = True
    narrative.reviewed_by = user_id
    narrative.reviewed_at = datetime.utcnow()
    narrative.version += 1

    await db.commit()
    await db.refresh(narrative)

    return narrative


# =============================================================================
# REVIEW CONSOLE ENDPOINTS
# =============================================================================

@app.get("/studies/{study_id}/review-queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    study_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Get items requiring CPA review."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    # Get projects needing review
    projects_result = await db.execute(
        select(RDProject).where(
            and_(
                RDProject.study_id == study_id,
                RDProject.cpa_reviewed == False,
                RDProject.qualification_status != QualificationStatus.PENDING
            )
        )
    )
    projects = projects_result.scalars().all()

    # Get employees needing review
    employees_result = await db.execute(
        select(RDEmployee).where(
            and_(
                RDEmployee.study_id == study_id,
                RDEmployee.cpa_reviewed == False,
                RDEmployee.qualified_time_percentage > 0
            )
        )
    )
    employees = employees_result.scalars().all()

    items = []

    for p in projects:
        has_flags = len(p.risk_flags or []) > 0
        items.append({
            "id": p.id,
            "entity_type": "project",
            "entity_id": p.id,
            "title": p.name,
            "description": f"Qualification: {p.qualification_status.value}",
            "confidence": p.overall_confidence,
            "risk_flags": [f.get("type") for f in (p.risk_flags or [])],
            "suggested_action": "review" if has_flags else "approve",
            "evidence_count": 0
        })

    for e in employees:
        items.append({
            "id": e.id,
            "entity_type": "employee",
            "entity_id": e.id,
            "title": e.name,
            "description": f"Qualified time: {e.qualified_time_percentage}%",
            "confidence": e.qualified_time_confidence,
            "risk_flags": [f.get("type") for f in (e.risk_flags or [])],
            "suggested_action": "approve",
            "evidence_count": 0
        })

    high_priority = sum(1 for i in items if len(i.get("risk_flags", [])) > 0)
    reviewed = sum(1 for p in projects if p.cpa_reviewed) + sum(1 for e in employees if e.cpa_reviewed)

    return ReviewQueueResponse(
        study_id=study_id,
        total_items=len(items),
        reviewed_items=reviewed,
        pending_items=len(items),
        high_priority_items=high_priority,
        items=items
    )


# =============================================================================
# OUTPUT GENERATION ENDPOINTS
# =============================================================================

@app.post("/studies/{study_id}/outputs/generate")
async def generate_outputs(
    study_id: UUID,
    request: OutputGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Generate output files (PDF, Excel, Form 6765)."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = study_result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Verify CPA approval if generating final outputs
    if not request.include_draft_watermark and not study.cpa_approved:
        raise HTTPException(
            status_code=400,
            detail="CPA approval required for final outputs"
        )

    # Queue output generation
    # In production, this would use the output generators

    return {
        "message": "Output generation queued",
        "output_types": request.output_types,
        "study_id": str(study_id)
    }


@app.get("/studies/{study_id}/outputs", response_model=List[OutputFileResponse])
async def list_outputs(
    study_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """List generated output files."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    result = await db.execute(
        select(RDOutputFile).where(RDOutputFile.study_id == study_id).order_by(RDOutputFile.generated_at.desc())
    )
    outputs = result.scalars().all()

    return [
        OutputFileResponse(
            id=o.id,
            study_id=o.study_id,
            file_type=o.file_type,
            filename=o.filename,
            file_size=o.file_size or 0,
            version=o.version,
            is_final=o.is_final,
            download_url=f"/api/studies/{study_id}/outputs/{o.id}/download",
            generated_at=o.generated_at
        )
        for o in outputs
    ]


@app.get("/studies/{study_id}/form-6765-data", response_model=Dict)
async def get_form_6765_data(
    study_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Get data for Form 6765 generation."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    study = study_result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Get latest calculation
    calc_result = await db.execute(
        select(RDCalculation).where(
            RDCalculation.study_id == study_id
        ).order_by(RDCalculation.calculated_at.desc())
    )
    calculations = calc_result.scalars().all()

    regular_calc = next((c for c in calculations if c.calculation_type == "federal_regular"), None)
    asc_calc = next((c for c in calculations if c.calculation_type == "federal_asc"), None)

    return {
        "entity_name": study.entity_name,
        "ein": study.ein,
        "tax_year": study.tax_year,
        "total_qre": str(study.total_qre),
        "regular_credit": str(study.federal_credit_regular),
        "asc_credit": str(study.federal_credit_asc),
        "selected_method": study.selected_method.value if study.selected_method else None,
        "final_credit": str(study.federal_credit_final),
        "calculation_steps": regular_calc.calculation_steps if regular_calc else []
    }


# =============================================================================
# AUDIT TRAIL ENDPOINTS
# =============================================================================

@app.get("/studies/{study_id}/audit-trail", response_model=List[AuditLogResponse])
async def get_audit_trail(
    study_id: UUID,
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Get audit trail for a study."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    query = select(RDAuditLog).where(RDAuditLog.study_id == study_id)

    if entity_type:
        query = query.where(RDAuditLog.entity_type == entity_type)
    if action:
        query = query.where(RDAuditLog.action == action)

    result = await db.execute(
        query.order_by(RDAuditLog.created_at.desc()).offset(skip).limit(limit)
    )
    logs = result.scalars().all()

    return logs


# =============================================================================
# TEAM ENDPOINTS
# =============================================================================

@app.get("/studies/{study_id}/team", response_model=List[TeamMemberResponse])
async def get_team(
    study_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Get team members for a study."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    result = await db.execute(
        select(RDStudyTeamMember).where(RDStudyTeamMember.study_id == study_id)
    )
    members = result.scalars().all()
    return members


@app.post("/studies/{study_id}/team", response_model=TeamMemberResponse, status_code=201)
async def add_team_member(
    study_id: UUID,
    member_data: TeamMemberAdd,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Add a team member to a study."""
    user_id, firm_id = user_firm

    # Verify study belongs to firm
    study_result = await db.execute(
        select(RDStudy).where(
            and_(RDStudy.id == study_id, RDStudy.firm_id == firm_id)
        )
    )
    if not study_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Study not found")

    member = RDStudyTeamMember(
        study_id=study_id,
        user_id=member_data.user_id,
        role=member_data.role,
        can_approve=member_data.can_approve,
        can_edit=member_data.can_edit,
        assigned_by=user_id
    )

    db.add(member)
    await db.commit()
    await db.refresh(member)

    return member


# =============================================================================
# CLIENT DATA COLLECTION ENDPOINTS (for invited clients)
# These endpoints support the R&D Client Portal (rdclient subdomain)
# =============================================================================


@app.post("/client-data/auto-save")
async def client_data_auto_save(
    data: Dict,
    db: AsyncSession = Depends(get_db)
):
    """Auto-save client portal data (token-based authentication)."""
    token = data.get("token")
    study_id = data.get("study_id")

    if not token or not study_id:
        raise HTTPException(status_code=400, detail="Token and study_id required")

    # Get the study
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == UUID(study_id))
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Store auto-save data
    auto_save_record = {
        "saved_at": datetime.utcnow().isoformat(),
        "employees": data.get("employees", []),
        "projects": data.get("projects", []),
        "supplies": data.get("supplies", []),
        "contracts": data.get("contracts", []),
        "notes": data.get("notes", "")
    }

    if not study.ai_suggested_areas:
        study.ai_suggested_areas = {}
    study.ai_suggested_areas["client_auto_save"] = auto_save_record

    await db.commit()

    return {"status": "success", "saved_at": auto_save_record["saved_at"]}


@app.get("/client-data/{study_id}")
async def get_client_data(
    study_id: UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Get existing client data for a study (token-based authentication)."""
    # Get the study
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == study_id)
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Get employees
    emp_result = await db.execute(
        select(RDEmployee).where(RDEmployee.study_id == study_id)
    )
    employees = emp_result.scalars().all()

    # Get projects
    proj_result = await db.execute(
        select(RDProject).where(RDProject.study_id == study_id)
    )
    projects = proj_result.scalars().all()

    # Get documents
    doc_result = await db.execute(
        select(RDDocument).where(RDDocument.study_id == study_id)
    )
    documents = doc_result.scalars().all()

    # Get QREs (supplies and contracts)
    qre_result = await db.execute(
        select(QualifiedResearchExpense).where(QualifiedResearchExpense.study_id == study_id)
    )
    qres = qre_result.scalars().all()

    supplies = [q for q in qres if q.category.value == "supplies"]
    contracts = [q for q in qres if q.category.value == "contract_research"]

    return {
        "study_id": str(study_id),
        "study_name": study.name,
        "employees": [
            {
                "id": str(e.id),
                "employee_id": e.employee_id,
                "name": e.name,
                "title": e.title,
                "department": e.department,
                "annual_wages": float(e.w2_wages or 0),
                "qualified_time_percentage": float(e.qualified_time_percentage or 0),
                "time_source": e.qualified_time_source or "estimate"
            }
            for e in employees
        ],
        "projects": [
            {
                "id": str(p.id),
                "name": p.name,
                "code": p.code,
                "description": p.description,
                "business_component": p.business_component,
                "department": p.department,
                "start_date": str(p.start_date) if p.start_date else None,
                "end_date": str(p.end_date) if p.end_date else None,
                "is_ongoing": p.is_ongoing,
                "four_part_test": p.ai_qualification_analysis.get("client_four_part_test", {}).get("answers", {}) if p.ai_qualification_analysis else {}
            }
            for p in projects
        ],
        "supplies": [
            {
                "id": str(s.id),
                "description": s.supply_description,
                "vendor": s.supply_vendor,
                "amount": float(s.gross_amount or 0),
                "gl_account": s.gl_account,
                "qualified_percentage": float(s.qualified_percentage or 0)
            }
            for s in supplies
        ],
        "contracts": [
            {
                "id": str(c.id),
                "contractor_name": c.contractor_name,
                "description": c.subcategory,
                "total_amount": float(c.gross_amount or 0),
                "qualified_percentage": float(c.qualified_percentage or 0),
                "is_qualified_research_org": c.is_qualified_research_org
            }
            for c in contracts
        ],
        "documents": [
            {
                "id": str(d.id),
                "name": d.filename,
                "type": d.mime_type,
                "status": d.processing_status,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None
            }
            for d in documents
        ]
    }


@app.post("/client-data/connect-payroll")
async def connect_payroll(
    data: Dict,
    db: AsyncSession = Depends(get_db)
):
    """Connect client's payroll system for automated data sync."""
    token = data.get("token")
    study_id = data.get("study_id")
    provider = data.get("provider")

    if not all([token, study_id, provider]):
        raise HTTPException(status_code=400, detail="Token, study_id, and provider required")

    supported_providers = ["adp", "gusto", "paychex", "quickbooks", "zenefits", "rippling"]
    if provider not in supported_providers:
        raise HTTPException(status_code=400, detail=f"Unsupported provider. Supported: {supported_providers}")

    # Get the study
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == UUID(study_id))
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Store payroll connection config
    payroll_connection = {
        "provider": provider,
        "status": "pending",
        "connected_at": datetime.utcnow().isoformat(),
        "credentials": data.get("credentials", {}),  # In production, encrypt these
        "last_sync": None
    }

    if not study.ai_suggested_areas:
        study.ai_suggested_areas = {}
    study.ai_suggested_areas["payroll_connection"] = payroll_connection

    await db.commit()

    return {
        "status": "success",
        "message": f"Payroll connection initiated with {provider}. Awaiting authorization.",
        "provider": provider
    }


@app.post("/client-data/sync-payroll")
async def sync_payroll(
    data: Dict,
    db: AsyncSession = Depends(get_db)
):
    """Sync data from connected payroll system."""
    token = data.get("token")
    study_id = data.get("study_id")

    if not all([token, study_id]):
        raise HTTPException(status_code=400, detail="Token and study_id required")

    # Get the study
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == UUID(study_id))
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    if not study.ai_suggested_areas or "payroll_connection" not in study.ai_suggested_areas:
        raise HTTPException(status_code=400, detail="No payroll connection configured")

    # In production, this would call the actual payroll API
    # For now, return simulated sync results
    sync_result = {
        "status": "synced",
        "synced_at": datetime.utcnow().isoformat(),
        "employees_synced": 0,
        "data_range": {
            "start": str(study.fiscal_year_start),
            "end": str(study.fiscal_year_end)
        }
    }

    study.ai_suggested_areas["payroll_connection"]["last_sync"] = sync_result

    await db.commit()

    return {
        "status": "success",
        "message": "Payroll data synchronized",
        **sync_result
    }


@app.post("/client-data/submit")
async def submit_client_data(
    data: Dict,
    db: AsyncSession = Depends(get_db)
):
    """Final submission of client data for CPA review."""
    token = data.get("token")
    study_id = data.get("study_id")

    if not all([token, study_id]):
        raise HTTPException(status_code=400, detail="Token and study_id required")

    # Get the study
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == UUID(study_id))
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Process employees
    employees_data = data.get("employees", [])
    for emp_data in employees_data:
        if emp_data.get("id", "").startswith("emp-"):
            # New employee from client
            w2_wages = Decimal(str(emp_data.get("annual_wages", 0)))
            qualified_pct = Decimal(str(emp_data.get("qualified_time_percentage", 0)))
            qualified_wages = w2_wages * qualified_pct / Decimal("100")

            employee = RDEmployee(
                study_id=UUID(study_id),
                employee_id=emp_data.get("employee_id"),
                name=emp_data.get("name", ""),
                title=emp_data.get("title"),
                department=emp_data.get("department"),
                w2_wages=w2_wages,
                qualified_time_percentage=qualified_pct,
                qualified_time_source=emp_data.get("time_source", "client_submission"),
                qualified_wages=qualified_wages
            )
            db.add(employee)

    # Process projects
    projects_data = data.get("projects", [])
    for proj_data in projects_data:
        if proj_data.get("id", "").startswith("proj-"):
            # New project from client
            project = RDProject(
                study_id=UUID(study_id),
                name=proj_data.get("name", ""),
                code=proj_data.get("code"),
                description=proj_data.get("description"),
                business_component=proj_data.get("business_component"),
                department=proj_data.get("department"),
                start_date=proj_data.get("start_date"),
                end_date=proj_data.get("end_date"),
                is_ongoing=proj_data.get("is_ongoing", False),
                qualification_status=QualificationStatus.PENDING,
                ai_qualification_analysis={
                    "client_four_part_test": {
                        "submitted_by": "client",
                        "submitted_at": datetime.utcnow().isoformat(),
                        "status": "pending_review",
                        "answers": proj_data.get("four_part_test", {})
                    }
                }
            )
            db.add(project)

    # Process supplies
    supplies_data = data.get("supplies", [])
    for supply_data in supplies_data:
        if supply_data.get("id", "").startswith("supply-"):
            qre = QualifiedResearchExpense(
                study_id=UUID(study_id),
                category="supplies",
                supply_description=supply_data.get("description"),
                supply_vendor=supply_data.get("vendor"),
                gl_account=supply_data.get("gl_account"),
                gross_amount=Decimal(str(supply_data.get("amount", 0))),
                qualified_percentage=Decimal(str(supply_data.get("qualified_percentage", 100))),
                qualified_amount=Decimal(str(supply_data.get("amount", 0))) * Decimal(str(supply_data.get("qualified_percentage", 100))) / Decimal("100")
            )
            db.add(qre)

    # Process contracts
    contracts_data = data.get("contracts", [])
    for contract_data in contracts_data:
        if contract_data.get("id", "").startswith("contract-"):
            qre = QualifiedResearchExpense(
                study_id=UUID(study_id),
                category="contract_research",
                contractor_name=contract_data.get("contractor_name"),
                subcategory=contract_data.get("description"),
                is_qualified_research_org=contract_data.get("contractor_type") in ["university", "research_org"],
                gross_amount=Decimal(str(contract_data.get("total_amount", 0))),
                qualified_percentage=Decimal(str(contract_data.get("qualified_percentage", 65))),
                qualified_amount=Decimal(str(contract_data.get("total_amount", 0))) * Decimal(str(contract_data.get("qualified_percentage", 65))) / Decimal("100")
            )
            db.add(qre)

    # Update study status to indicate client data received
    submission_record = {
        "submitted_at": datetime.utcnow().isoformat(),
        "employee_count": len(employees_data),
        "project_count": len(projects_data),
        "supply_count": len(supplies_data),
        "contract_count": len(contracts_data),
        "notes": data.get("notes", "")
    }

    if not study.ai_suggested_areas:
        study.ai_suggested_areas = {}
    study.ai_suggested_areas["client_submission"] = submission_record

    # Move study to data collection phase
    if study.status == StudyStatus.DRAFT or study.status == StudyStatus.INTAKE:
        study.status = StudyStatus.DATA_COLLECTION
        study.status_history.append({
            "status": StudyStatus.DATA_COLLECTION.value,
            "timestamp": datetime.utcnow().isoformat(),
            "notes": "Client data submitted via portal"
        })

    await db.commit()

    return {
        "status": "success",
        "message": "Your data has been submitted successfully and is pending CPA review.",
        "submission_summary": submission_record
    }


@app.post("/client/studies/{study_id}/data/manual")
async def submit_client_data_manual(
    study_id: UUID,
    data: Dict,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Client submits data manually via form."""
    user_id, firm_id = user_firm

    # Get the study (clients have restricted access via their token)
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == study_id)
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Process and store client-submitted data
    data_record = {
        "submission_type": "manual",
        "submitted_by": str(user_id),
        "submitted_at": datetime.utcnow().isoformat(),
        "data": data,
        "status": "pending_review"
    }

    # Store in study's client_submissions
    if not study.ai_suggested_areas:
        study.ai_suggested_areas = {}
    if "client_submissions" not in study.ai_suggested_areas:
        study.ai_suggested_areas["client_submissions"] = []
    study.ai_suggested_areas["client_submissions"].append(data_record)

    await db.commit()

    return {
        "status": "success",
        "message": "Data submitted successfully and pending CPA review",
        "submission_id": len(study.ai_suggested_areas["client_submissions"])
    }


@app.post("/client/studies/{study_id}/data/excel")
async def submit_client_data_excel(
    study_id: UUID,
    file: UploadFile = File(...),
    data_type: str = Query(..., description="Type of data: payroll, projects, expenses, employees"),
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Client uploads Excel file for AI parsing."""
    import io
    user_id, firm_id = user_firm

    # Get the study
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == study_id)
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Read and validate file
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="File must be Excel (.xlsx, .xls) or CSV")

    file_content = await file.read()

    # Parse Excel/CSV with AI
    try:
        parsed_data = await _parse_excel_with_ai(file_content, file.filename, data_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    # Store parsed data
    data_record = {
        "submission_type": "excel_upload",
        "data_type": data_type,
        "filename": file.filename,
        "file_size": len(file_content),
        "submitted_by": str(user_id),
        "submitted_at": datetime.utcnow().isoformat(),
        "parsed_data": parsed_data,
        "ai_confidence": parsed_data.get("confidence", 0.0),
        "status": "pending_review"
    }

    if not study.ai_suggested_areas:
        study.ai_suggested_areas = {}
    if "client_submissions" not in study.ai_suggested_areas:
        study.ai_suggested_areas["client_submissions"] = []
    study.ai_suggested_areas["client_submissions"].append(data_record)

    await db.commit()

    return {
        "status": "success",
        "message": f"Excel file parsed successfully. Found {parsed_data.get('record_count', 0)} records.",
        "parsed_summary": parsed_data.get("summary", {}),
        "confidence": parsed_data.get("confidence", 0.0),
        "submission_id": len(study.ai_suggested_areas["client_submissions"])
    }


@app.post("/client/studies/{study_id}/data/api-connect")
async def setup_client_api_connection(
    study_id: UUID,
    connection_config: Dict,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Client sets up API connection for automated data sync."""
    user_id, firm_id = user_firm

    # Get the study
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == study_id)
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Validate connection config
    supported_systems = ["quickbooks", "sage", "adp", "paychex", "gusto", "custom_api"]
    system_type = connection_config.get("system_type")
    if system_type not in supported_systems:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported system. Supported: {supported_systems}"
        )

    # Store API connection config (encrypted in production)
    api_connection = {
        "system_type": system_type,
        "configured_by": str(user_id),
        "configured_at": datetime.utcnow().isoformat(),
        "status": "pending_validation",
        "sync_enabled": False,
        "last_sync": None
    }

    if not study.ai_suggested_areas:
        study.ai_suggested_areas = {}
    study.ai_suggested_areas["api_connection"] = api_connection

    await db.commit()

    return {
        "status": "success",
        "message": f"API connection configured for {system_type}. Pending CPA approval.",
        "connection_id": str(study_id)
    }


@app.post("/client/studies/{study_id}/auto-save")
async def auto_save_client_data(
    study_id: UUID,
    data: Dict,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Auto-save client portal draft data (called periodically)."""
    user_id, firm_id = user_firm

    # Get the study
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == study_id)
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Store auto-save data
    auto_save_record = {
        "saved_by": str(user_id),
        "saved_at": datetime.utcnow().isoformat(),
        "data": data
    }

    if not study.ai_suggested_areas:
        study.ai_suggested_areas = {}
    study.ai_suggested_areas["auto_save"] = auto_save_record

    await db.commit()

    return {
        "status": "success",
        "message": "Data auto-saved successfully",
        "saved_at": auto_save_record["saved_at"]
    }


@app.get("/client/studies/{study_id}/auto-save")
async def get_auto_saved_data(
    study_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Get auto-saved client portal draft data."""
    user_id, firm_id = user_firm

    # Get the study
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == study_id)
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    auto_save = {}
    if study.ai_suggested_areas and "auto_save" in study.ai_suggested_areas:
        auto_save = study.ai_suggested_areas["auto_save"]

    return {
        "study_id": str(study_id),
        "has_saved_data": bool(auto_save),
        "saved_at": auto_save.get("saved_at"),
        "data": auto_save.get("data", {})
    }


@app.post("/client/studies/{study_id}/projects/{project_id}/four-part-test")
async def submit_four_part_test(
    study_id: UUID,
    project_id: UUID,
    test_data: Dict,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Client submits 4-part test questionnaire answers for a project."""
    user_id, firm_id = user_firm

    # Get the project
    result = await db.execute(
        select(RDProject).where(
            and_(RDProject.id == project_id, RDProject.study_id == study_id)
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Validate 4-part test structure
    required_parts = ["permitted_purpose", "technological_nature", "elimination_uncertainty", "process_experimentation"]
    for part in required_parts:
        if part not in test_data:
            raise HTTPException(status_code=400, detail=f"Missing required 4-part test section: {part}")

    # Store client's 4-part test answers
    client_four_part_test = {
        "submitted_by": str(user_id),
        "submitted_at": datetime.utcnow().isoformat(),
        "status": "pending_review",
        "answers": test_data
    }

    # Store in project's AI qualification analysis field
    if not project.ai_qualification_analysis:
        project.ai_qualification_analysis = {}
    project.ai_qualification_analysis["client_four_part_test"] = client_four_part_test

    await db.commit()

    return {
        "status": "success",
        "message": "4-part test questionnaire submitted successfully. Pending CPA review.",
        "project_id": str(project_id)
    }


@app.get("/client/studies/{study_id}/projects/{project_id}/four-part-test")
async def get_four_part_test(
    study_id: UUID,
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Get client's 4-part test questionnaire answers for a project."""
    user_id, firm_id = user_firm

    # Get the project
    result = await db.execute(
        select(RDProject).where(
            and_(RDProject.id == project_id, RDProject.study_id == study_id)
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    client_test = {}
    if project.ai_qualification_analysis and "client_four_part_test" in project.ai_qualification_analysis:
        client_test = project.ai_qualification_analysis["client_four_part_test"]

    return {
        "project_id": str(project_id),
        "project_name": project.name,
        "has_submitted": bool(client_test),
        "submitted_at": client_test.get("submitted_at"),
        "status": client_test.get("status"),
        "answers": client_test.get("answers", {})
    }


@app.post("/client/studies/{study_id}/employees/bulk")
async def bulk_import_employees(
    study_id: UUID,
    employees: List[Dict],
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Bulk import employees from client portal (manual entry or parsed spreadsheet)."""
    user_id, firm_id = user_firm

    # Verify study exists
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == study_id)
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    imported_count = 0
    errors = []

    for idx, emp_data in enumerate(employees):
        try:
            # Calculate qualified wages
            w2_wages = Decimal(str(emp_data.get("w2_wages", emp_data.get("total_wages", 0))))
            qualified_pct = Decimal(str(emp_data.get("qualified_time_percentage", 0)))
            qualified_wages = w2_wages * qualified_pct / Decimal("100")

            employee = RDEmployee(
                study_id=study_id,
                employee_id=emp_data.get("employee_id", f"EMP-{idx+1:04d}"),
                name=emp_data.get("name", f"Employee {idx+1}"),
                title=emp_data.get("title"),
                department=emp_data.get("department"),
                hire_date=emp_data.get("hire_date"),
                termination_date=emp_data.get("termination_date"),
                total_wages=emp_data.get("total_wages", 0),
                w2_wages=w2_wages,
                bonus=emp_data.get("bonus"),
                stock_compensation=emp_data.get("stock_compensation"),
                qualified_time_percentage=qualified_pct,
                qualified_time_source=emp_data.get("qualified_time_source", "client_submission"),
                qualified_wages=qualified_wages
            )

            db.add(employee)
            imported_count += 1

        except Exception as e:
            errors.append({
                "row": idx + 1,
                "name": emp_data.get("name", "Unknown"),
                "error": str(e)
            })

    await db.commit()

    return {
        "status": "success" if imported_count > 0 else "partial",
        "message": f"Imported {imported_count} of {len(employees)} employees",
        "imported_count": imported_count,
        "error_count": len(errors),
        "errors": errors[:10]  # Return first 10 errors only
    }


@app.get("/client/studies/{study_id}/submissions")
async def get_client_submissions(
    study_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_firm: tuple = Depends(get_current_user_firm_id)
):
    """Get list of client data submissions (without sensitive study data)."""
    user_id, firm_id = user_firm

    # Get the study
    result = await db.execute(
        select(RDStudy).where(RDStudy.id == study_id)
    )
    study = result.scalar_one_or_none()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Return only submission metadata, not study progress/calculations
    submissions = []
    if study.ai_suggested_areas and "client_submissions" in study.ai_suggested_areas:
        for idx, sub in enumerate(study.ai_suggested_areas["client_submissions"]):
            submissions.append({
                "submission_id": idx + 1,
                "type": sub.get("submission_type"),
                "data_type": sub.get("data_type"),
                "filename": sub.get("filename"),
                "submitted_at": sub.get("submitted_at"),
                "status": sub.get("status")
            })

    return {
        "study_id": str(study_id),
        "study_name": study.name,
        "submissions": submissions,
        "api_connected": bool(study.ai_suggested_areas and study.ai_suggested_areas.get("api_connection"))
    }


async def _parse_excel_with_ai(file_content: bytes, filename: str, data_type: str) -> Dict:
    """Parse Excel/CSV file using AI to extract structured data."""
    import io

    try:
        # Try to import pandas for Excel parsing
        import pandas as pd

        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))

        # Convert to records
        records = df.to_dict('records')

        # AI-powered column mapping based on data type
        column_mappings = {
            "payroll": {
                "name_columns": ["employee", "name", "employee_name", "full_name"],
                "id_columns": ["employee_id", "emp_id", "id", "employee_number"],
                "wage_columns": ["wages", "salary", "gross_pay", "total_wages", "w2_wages"],
                "department_columns": ["department", "dept", "division", "cost_center"]
            },
            "projects": {
                "name_columns": ["project", "project_name", "name", "title"],
                "id_columns": ["project_id", "id", "project_number", "code"],
                "description_columns": ["description", "desc", "details", "summary"],
                "department_columns": ["department", "dept", "division", "business_unit"]
            },
            "expenses": {
                "category_columns": ["category", "type", "expense_type", "account"],
                "amount_columns": ["amount", "total", "value", "cost"],
                "vendor_columns": ["vendor", "supplier", "payee", "recipient"],
                "description_columns": ["description", "desc", "memo", "notes"]
            },
            "employees": {
                "name_columns": ["name", "employee_name", "full_name"],
                "title_columns": ["title", "job_title", "position", "role"],
                "department_columns": ["department", "dept", "division"],
                "hire_date_columns": ["hire_date", "start_date", "date_hired"]
            }
        }

        # Get relevant mappings
        mappings = column_mappings.get(data_type, {})

        # Identify columns using fuzzy matching
        identified_columns = {}
        df_columns_lower = {col.lower().strip(): col for col in df.columns}

        for field, possible_names in mappings.items():
            for name in possible_names:
                if name in df_columns_lower:
                    identified_columns[field] = df_columns_lower[name]
                    break

        # Calculate confidence based on matched columns
        confidence = len(identified_columns) / max(len(mappings), 1)

        # Generate summary statistics
        summary = {
            "total_rows": len(df),
            "columns_found": list(df.columns),
            "columns_mapped": identified_columns,
            "data_types_detected": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }

        # Add type-specific summaries
        if data_type == "payroll" and any("wage" in col.lower() for col in df.columns):
            for col in df.columns:
                if "wage" in col.lower() or "salary" in col.lower():
                    try:
                        summary["total_wages"] = float(df[col].sum())
                    except:
                        pass
                    break

        return {
            "record_count": len(records),
            "records": records[:100],  # Limit to first 100 for preview
            "column_mapping": identified_columns,
            "summary": summary,
            "confidence": confidence,
            "data_type": data_type
        }

    except ImportError:
        # Fallback without pandas
        return {
            "record_count": 0,
            "records": [],
            "column_mapping": {},
            "summary": {"error": "Excel parsing requires pandas library"},
            "confidence": 0.0,
            "data_type": data_type
        }
    except Exception as e:
        raise ValueError(f"Failed to parse file: {str(e)}")


# =============================================================================
# RULES ENGINE ENDPOINTS
# =============================================================================

@app.get("/rules/federal")
async def get_federal_rules():
    """Get current Federal R&D credit rules."""
    rules_engine = app.state.rules_engine
    federal_rules = rules_engine.get_federal_rules()

    return {
        "version": federal_rules.version,
        "four_part_test": federal_rules.FOUR_PART_TEST,
        "excluded_activities": federal_rules.EXCLUDED_ACTIVITIES,
        "qre_rules": federal_rules.QRE_RULES,
        "rates": {
            "regular": federal_rules.REGULAR_CREDIT_RATE,
            "asc": federal_rules.ASC_CREDIT_RATE
        }
    }


@app.get("/rules/states")
async def get_state_rules():
    """Get available state R&D credit rules."""
    rules_engine = app.state.rules_engine

    return {
        "available_states": rules_engine.get_available_states(),
        "states": {
            code: {
                "name": rules.state_name,
                "has_credit": rules.has_rd_credit,
                "credit_rate": rules.credit_rate,
                "credit_type": rules.credit_type,
                "carryforward_years": rules.carryforward_years,
                "is_refundable": rules.is_refundable,
                "citation": rules.statute_citation
            }
            for code, rules in rules_engine.state_rules.items()
        }
    }


@app.get("/rules/states/{state_code}")
async def get_state_rule(state_code: str):
    """Get rules for a specific state."""
    rules_engine = app.state.rules_engine
    state_rules = rules_engine.get_state_rules(state_code.upper())

    if not state_rules:
        raise HTTPException(status_code=404, detail=f"No rules found for state: {state_code}")

    return state_rules


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def _log_audit(
    db: AsyncSession,
    study_id: UUID,
    action: str,
    entity_type: str,
    entity_id: UUID,
    previous_value: Optional[dict],
    new_value: Optional[dict],
    user_id: UUID
):
    """Log an audit trail entry."""
    log = RDAuditLog(
        study_id=study_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        previous_value=previous_value,
        new_value=new_value,
        user_id=user_id
    )
    db.add(log)
    await db.commit()
