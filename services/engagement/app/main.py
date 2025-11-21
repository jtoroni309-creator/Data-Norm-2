"""
Aura Audit AI - Engagement Service

Core business entity management with:
- Engagement CRUD operations
- State machine (Draft → Planning → Fieldwork → Review → Finalized)
- Team member management
- RLS (Row-Level Security) enforcement
- Binder tree operations
- Workpaper management
"""
import logging
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload

from .config import settings
from .database import get_db, init_db, set_rls_context
from .models import (
    Engagement,
    EngagementTeamMember,
    BinderNode,
    Workpaper,
    ReviewNote,
    EngagementStatus,
    EngagementType,
    UserRole,
    BinderNodeType,
    WorkpaperStatus
)
from .schemas import (
    EngagementCreate,
    EngagementResponse,
    EngagementUpdate,
    TeamMemberAdd,
    TeamMemberResponse,
    BinderTreeResponse,
    BinderNodeResponse,
    WorkpaperResponse,
    ReviewNoteCreate,
    ReviewNoteResponse,
    HealthResponse
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura Audit AI - Engagement Service",
    description="Engagement management, binder, and workpapers",
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
# JWT Authentication
# ========================================

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> UUID:
    """
    Extract user ID from JWT token

    Args:
        credentials: JWT token from Authorization header

    Returns:
        User ID from token payload

    Raises:
        HTTPException: If token is invalid or expired
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

        return UUID(user_id)

    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise credentials_exception
    except ValueError as e:
        logger.error(f"Invalid user ID format in token: {e}")
        raise credentials_exception


# ========================================
# Health & Status
# ========================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="engagement",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aura Audit AI - Engagement Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ========================================
# Engagement CRUD
# ========================================

@app.post("/engagements", response_model=EngagementResponse, status_code=status.HTTP_201_CREATED)
async def create_engagement(
    engagement_data: EngagementCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Create a new engagement

    - Sets initial status to 'draft'
    - Assigns creator as team member
    - Enforces RLS (engagement-level isolation)
    """
    # Set RLS context
    await set_rls_context(db, current_user_id)

    # Create engagement
    new_engagement = Engagement(
        client_id=engagement_data.client_id,
        name=engagement_data.name,
        engagement_type=engagement_data.engagement_type,
        status=EngagementStatus.DRAFT,
        fiscal_year_end=engagement_data.fiscal_year_end,
        start_date=engagement_data.start_date,
        expected_completion_date=engagement_data.expected_completion_date,
        partner_id=engagement_data.partner_id,
        manager_id=engagement_data.manager_id,
        created_by=current_user_id
    )

    db.add(new_engagement)
    await db.flush()  # Get engagement ID

    # Add creator as team member
    team_member = EngagementTeamMember(
        engagement_id=new_engagement.id,
        user_id=current_user_id,
        role=UserRole.MANAGER,  # Default role
        assigned_by=current_user_id
    )
    db.add(team_member)

    # Create root binder node
    root_node = BinderNode(
        engagement_id=new_engagement.id,
        node_type=BinderNodeType.FOLDER,
        title="Audit Binder",
        node_code="ROOT",
        position=0,
        created_by=current_user_id
    )
    db.add(root_node)

    await db.commit()
    await db.refresh(new_engagement)

    logger.info(f"Created engagement: {new_engagement.name} (ID: {new_engagement.id})")

    return EngagementResponse.model_validate(new_engagement)


@app.get("/engagements", response_model=List[EngagementResponse])
async def list_engagements(
    status: Optional[EngagementStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    List engagements accessible to current user

    RLS: Only returns engagements where user is a team member
    """
    # Set RLS context
    await set_rls_context(db, current_user_id)

    # Build query
    query = select(Engagement)

    if status:
        query = query.where(Engagement.status == status)

    query = query.offset(skip).limit(limit).order_by(Engagement.created_at.desc())

    result = await db.execute(query)
    engagements = result.scalars().all()

    return [EngagementResponse.model_validate(eng) for eng in engagements]


@app.get("/engagements/{engagement_id}", response_model=EngagementResponse)
async def get_engagement(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Get engagement by ID

    RLS: Only accessible if user is team member
    """
    await set_rls_context(db, current_user_id)

    result = await db.execute(
        select(Engagement).where(Engagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()

    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found or access denied"
        )

    return EngagementResponse.model_validate(engagement)


@app.patch("/engagements/{engagement_id}", response_model=EngagementResponse)
async def update_engagement(
    engagement_id: UUID,
    update_data: EngagementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Update engagement

    Requires: Partner or Manager role
    """
    await set_rls_context(db, current_user_id)

    result = await db.execute(
        select(Engagement).where(Engagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()

    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found or access denied"
        )

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(engagement, field, value)

    engagement.updated_at = datetime.utcnow()

    try:
        await db.commit()
        await db.refresh(engagement)
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error updating engagement {engagement_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update engagement"
        )

    logger.info(f"Updated engagement: {engagement.id}")

    return EngagementResponse.model_validate(engagement)


# ========================================
# State Transitions
# ========================================

@app.post("/engagements/{engagement_id}/transition")
async def transition_engagement_status(
    engagement_id: UUID,
    new_status: EngagementStatus,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Transition engagement status

    Valid transitions:
    - Draft → Planning
    - Planning → Fieldwork
    - Fieldwork → Review
    - Review → Finalized (requires partner approval)
    """
    await set_rls_context(db, current_user_id)

    result = await db.execute(
        select(Engagement).where(Engagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()

    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )

    # Validate transition
    valid_transitions = {
        EngagementStatus.DRAFT: [EngagementStatus.PLANNING],
        EngagementStatus.PLANNING: [EngagementStatus.FIELDWORK, EngagementStatus.DRAFT],
        EngagementStatus.FIELDWORK: [EngagementStatus.REVIEW, EngagementStatus.PLANNING],
        EngagementStatus.REVIEW: [EngagementStatus.FINALIZED, EngagementStatus.FIELDWORK],
        EngagementStatus.FINALIZED: []  # Terminal state
    }

    if new_status not in valid_transitions.get(engagement.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from {engagement.status.value} to {new_status.value}"
        )

    # Finalized requires additional checks (partner approval, QC pass)
    if new_status == EngagementStatus.FINALIZED:
        # Check QC policies passed
        qc_check_query = text("""
            SELECT
                qc.id,
                qp.policy_name,
                qp.is_blocking,
                qc.status
            FROM atlas.qc_checks qc
            JOIN atlas.qc_policies qp ON qc.policy_id = qp.id
            WHERE qc.engagement_id = :engagement_id
              AND qp.is_blocking = TRUE
              AND qp.is_active = TRUE
              AND qc.status NOT IN ('passed', 'waived')
        """)
        qc_result = await db.execute(qc_check_query, {"engagement_id": engagement_id})
        failed_qc_checks = qc_result.fetchall()

        if failed_qc_checks:
            failed_policies = [row[1] for row in failed_qc_checks]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot finalize: blocking QC policies not passed: {', '.join(failed_policies)}"
            )

        # Check partner signature exists
        signature_check_query = text("""
            SELECT
                se.id,
                se.status,
                r.report_type
            FROM atlas.signature_envelopes se
            JOIN atlas.reports r ON se.report_id = r.id
            WHERE r.engagement_id = :engagement_id
              AND r.report_type IN ('audit_opinion', 'review_opinion', 'compilation_report')
              AND se.status = 'completed'
            ORDER BY se.created_at DESC
            LIMIT 1
        """)
        signature_result = await db.execute(signature_check_query, {"engagement_id": engagement_id})
        partner_signature = signature_result.fetchone()

        if not partner_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot finalize: partner signature not completed on engagement report"
            )

    engagement.status = new_status
    engagement.updated_at = datetime.utcnow()

    if new_status == EngagementStatus.FINALIZED:
        engagement.locked_at = datetime.utcnow()
        engagement.locked_by = current_user_id

    await db.commit()

    logger.info(f"Engagement {engagement_id} transitioned to {new_status.value}")

    return {"message": f"Status updated to {new_status.value}"}


# ========================================
# Team Members
# ========================================

@app.get("/engagements/{engagement_id}/team", response_model=List[TeamMemberResponse])
async def get_team_members(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Get engagement team members"""
    await set_rls_context(db, current_user_id)

    result = await db.execute(
        select(EngagementTeamMember)
        .where(EngagementTeamMember.engagement_id == engagement_id)
        .order_by(EngagementTeamMember.assigned_at.desc())
    )
    team_members = result.scalars().all()

    return [TeamMemberResponse.model_validate(tm) for tm in team_members]


@app.post("/engagements/{engagement_id}/team", response_model=TeamMemberResponse)
async def add_team_member(
    engagement_id: UUID,
    member_data: TeamMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Add team member to engagement

    Requires: Partner or Manager role
    """
    await set_rls_context(db, current_user_id)

    # Check if already exists
    result = await db.execute(
        select(EngagementTeamMember).where(
            and_(
                EngagementTeamMember.engagement_id == engagement_id,
                EngagementTeamMember.user_id == member_data.user_id
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a team member"
        )

    new_member = EngagementTeamMember(
        engagement_id=engagement_id,
        user_id=member_data.user_id,
        role=member_data.role,
        assigned_by=current_user_id
    )

    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)

    logger.info(f"Added team member {member_data.user_id} to engagement {engagement_id}")

    return TeamMemberResponse.model_validate(new_member)


# ========================================
# Binder Tree
# ========================================

@app.get("/engagements/{engagement_id}/binder/tree")
async def get_binder_tree(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Get complete binder tree structure

    Returns hierarchical tree of folders, workpapers, and evidence
    """
    await set_rls_context(db, current_user_id)

    result = await db.execute(
        select(BinderNode)
        .where(BinderNode.engagement_id == engagement_id)
        .order_by(BinderNode.position)
    )
    nodes = result.scalars().all()

    if not nodes:
        return []

    # Build tree structure
    node_map = {}
    for node in nodes:
        node_dict = BinderNodeResponse.model_validate(node).model_dump()
        node_dict['children'] = []
        node_map[node.id] = node_dict

    # Build hierarchy
    tree_nodes = []
    for node_id, node_data in node_map.items():
        parent_id = node_data.get('parent_id')
        if parent_id and parent_id in node_map:
            node_map[parent_id]['children'].append(node_data)
        else:
            tree_nodes.append(node_data)

    return tree_nodes


@app.post("/engagements/{engagement_id}/binder/nodes", response_model=BinderNodeResponse)
async def create_binder_node(
    engagement_id: UUID,
    node_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Create a new binder node (folder or workpaper)"""
    await set_rls_context(db, current_user_id)

    new_node = BinderNode(
        engagement_id=engagement_id,
        parent_id=node_data.get("parent_id"),
        node_type=node_data["node_type"],
        title=node_data["title"],
        node_code=node_data.get("node_code"),
        position=node_data.get("position", 0),
        created_by=current_user_id
    )

    db.add(new_node)
    await db.commit()
    await db.refresh(new_node)

    return BinderNodeResponse.model_validate(new_node)


# ========================================
# AI-Enhanced Materiality & Risk Assessment
# ========================================

from .ai_materiality_service import ai_materiality_service
from .ai_risk_service import ai_risk_service


class AIAnalysisRequest(BaseModel):
    """Request for AI-powered analysis"""
    financial_statements: Dict[str, Any]
    prior_period_statements: Optional[Dict[str, Any]] = None
    industry: Optional[str] = None
    entity_type: Optional[str] = None


@app.post("/engagements/{engagement_id}/ai/materiality")
async def calculate_ai_materiality(
    engagement_id: UUID,
    request: AIAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Calculate AI-enhanced materiality for engagement.

    Uses AI to dynamically adjust materiality based on:
    - Risk assessment results
    - Industry context
    - Financial trends and volatility
    - Engagement-specific factors

    Returns comprehensive materiality analysis with AI recommendations.
    """
    if not settings.ENABLE_AI_MATERIALITY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI materiality feature is currently disabled"
        )

    await set_rls_context(db, current_user_id)

    # Verify engagement exists and user has access
    result = await db.execute(
        select(Engagement).where(Engagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()

    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found or access denied"
        )

    try:
        # Calculate AI-enhanced materiality
        materiality_result = await ai_materiality_service.calculate_ai_enhanced_materiality(
            db=db,
            engagement_id=engagement_id,
            financial_statements=request.financial_statements,
            risk_assessment=None,  # Will be calculated separately
            industry=request.industry,
            prior_period_statements=request.prior_period_statements
        )

        logger.info(
            f"AI materiality calculated for engagement {engagement_id}: "
            f"${materiality_result['recommended_materiality']:,.0f}"
        )

        return materiality_result

    except Exception as e:
        logger.error(f"Error calculating AI materiality for engagement {engagement_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate AI materiality: {str(e)}"
        )


@app.post("/engagements/{engagement_id}/ai/risk-assessment")
async def perform_ai_risk_assessment(
    engagement_id: UUID,
    request: AIAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Perform AI-enhanced risk assessment for engagement.

    Uses AI to:
    - Detect complex risk patterns and correlations
    - Identify industry-specific risk factors
    - Assess going concern indicators
    - Generate key audit matters (KAMs)
    - Recommend audit strategy

    Returns comprehensive risk assessment with AI insights.
    """
    if not settings.ENABLE_AI_RISK_ASSESSMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI risk assessment feature is currently disabled"
        )

    await set_rls_context(db, current_user_id)

    # Verify engagement exists and user has access
    result = await db.execute(
        select(Engagement).where(Engagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()

    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found or access denied"
        )

    try:
        # Perform AI-enhanced risk assessment
        risk_result = await ai_risk_service.perform_comprehensive_risk_assessment(
            db=db,
            engagement_id=engagement_id,
            financial_statements=request.financial_statements,
            prior_period_statements=request.prior_period_statements,
            industry=request.industry,
            entity_type=request.entity_type,
            materiality=None  # Can be provided if already calculated
        )

        logger.info(
            f"AI risk assessment completed for engagement {engagement_id}: "
            f"Risk Level = {risk_result['overall_risk_assessment']['risk_level']}"
        )

        return risk_result

    except Exception as e:
        logger.error(f"Error performing AI risk assessment for engagement {engagement_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform AI risk assessment: {str(e)}"
        )


@app.post("/engagements/{engagement_id}/ai/comprehensive-analysis")
async def perform_comprehensive_ai_analysis(
    engagement_id: UUID,
    request: AIAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Perform comprehensive AI-powered analysis including both materiality and risk assessment.

    This endpoint:
    1. Calculates AI-enhanced risk assessment
    2. Uses risk results to inform materiality calculation
    3. Assesses alignment between risk and materiality
    4. Provides integrated recommendations

    Returns complete engagement analysis with AI-powered insights.
    """
    if not (settings.ENABLE_AI_MATERIALITY and settings.ENABLE_AI_RISK_ASSESSMENT):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI analysis features are currently disabled"
        )

    await set_rls_context(db, current_user_id)

    # Verify engagement exists and user has access
    result = await db.execute(
        select(Engagement).where(Engagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()

    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found or access denied"
        )

    try:
        # Step 1: Perform risk assessment first
        logger.info(f"Starting comprehensive AI analysis for engagement {engagement_id}")

        risk_result = await ai_risk_service.perform_comprehensive_risk_assessment(
            db=db,
            engagement_id=engagement_id,
            financial_statements=request.financial_statements,
            prior_period_statements=request.prior_period_statements,
            industry=request.industry,
            entity_type=request.entity_type,
            materiality=None
        )

        # Step 2: Calculate materiality using risk assessment results
        materiality_result = await ai_materiality_service.calculate_ai_enhanced_materiality(
            db=db,
            engagement_id=engagement_id,
            financial_statements=request.financial_statements,
            risk_assessment=risk_result["overall_risk_assessment"],
            industry=request.industry,
            prior_period_statements=request.prior_period_statements
        )

        # Step 3: Update risk assessment with materiality for final alignment check
        risk_result_with_materiality = await ai_risk_service.perform_comprehensive_risk_assessment(
            db=db,
            engagement_id=engagement_id,
            financial_statements=request.financial_statements,
            prior_period_statements=request.prior_period_statements,
            industry=request.industry,
            entity_type=request.entity_type,
            materiality=materiality_result
        )

        # Compile comprehensive result
        comprehensive_result = {
            "engagement_id": str(engagement_id),
            "analysis_date": datetime.utcnow().isoformat(),

            # Executive summary
            "executive_summary": {
                "overall_risk_level": risk_result_with_materiality["overall_risk_assessment"]["risk_level"],
                "risk_score": risk_result_with_materiality["overall_risk_assessment"]["risk_score"],
                "recommended_materiality": materiality_result["recommended_materiality"],
                "recommended_performance_materiality": materiality_result["recommended_performance_materiality"],
                "going_concern_risk": risk_result_with_materiality["going_concern_assessment"]["risk_level"],
                "key_audit_matters_count": len(risk_result_with_materiality.get("key_audit_matters", []))
            },

            # Detailed results
            "materiality_analysis": materiality_result,
            "risk_assessment": risk_result_with_materiality,

            # Integrated recommendations
            "integrated_recommendations": {
                "materiality_risk_alignment": risk_result_with_materiality.get("materiality_risk_alignment", {}),
                "audit_strategy": risk_result_with_materiality.get("recommended_audit_strategy", {}),
                "priority_areas": [
                    kam["matter"] for kam in risk_result_with_materiality.get("key_audit_matters", [])[:3]
                ]
            },

            # AI confidence metrics
            "ai_confidence": {
                "materiality_confidence": materiality_result["ai_adjusted_materiality"]["confidence_score"],
                "risk_assessment_confidence": risk_result_with_materiality["overall_risk_assessment"]["confidence_score"]
            }
        }

        logger.info(
            f"Comprehensive AI analysis completed for engagement {engagement_id}: "
            f"Risk={comprehensive_result['executive_summary']['overall_risk_level']}, "
            f"Materiality=${comprehensive_result['executive_summary']['recommended_materiality']:,.0f}"
        )

        return comprehensive_result

    except Exception as e:
        logger.error(f"Error performing comprehensive AI analysis for engagement {engagement_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform comprehensive AI analysis: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
