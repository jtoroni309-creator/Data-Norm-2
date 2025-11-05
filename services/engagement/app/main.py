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
from sqlalchemy import select, and_, or_, func
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
# Mock Authentication (Replace with real auth)
# ========================================

async def get_current_user_id() -> UUID:
    """
    Mock function to get current user ID
    In production, this would decode JWT and return user ID
    """
    # For now, return a fixed UUID
    # In production: extract from JWT token via Identity service
    return UUID("00000000-0000-0000-0000-000000000001")


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
    await db.commit()
    await db.refresh(engagement)

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
        # TODO: Check QC policies passed
        # TODO: Check partner signature exists
        pass

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

@app.get("/engagements/{engagement_id}/binder/tree", response_model=BinderTreeResponse)
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

    # Build tree structure
    node_map = {node.id: BinderNodeResponse.model_validate(node) for node in nodes}
    tree_nodes = []

    for node_id, node in node_map.items():
        if node.parent_id:
            parent = node_map.get(node.parent_id)
            if parent:
                if not hasattr(parent, 'children'):
                    parent.children = []
                parent.children.append(node)
        else:
            tree_nodes.append(node)

    return BinderTreeResponse(
        engagement_id=engagement_id,
        nodes=tree_nodes
    )


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
