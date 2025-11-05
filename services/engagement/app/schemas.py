"""Pydantic schemas for request/response validation"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .models import (
    EngagementStatus,
    EngagementType,
    UserRole,
    BinderNodeType,
    WorkpaperStatus
)


# ========================================
# Health & Status
# ========================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


# ========================================
# Engagement Schemas
# ========================================

class EngagementCreate(BaseModel):
    """Create new engagement"""
    client_id: UUID
    name: str = Field(..., min_length=1, max_length=500)
    engagement_type: EngagementType
    fiscal_year_end: date
    start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    partner_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class EngagementUpdate(BaseModel):
    """Update engagement"""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    partner_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class EngagementResponse(BaseModel):
    """Engagement response"""
    id: UUID
    client_id: UUID
    name: str
    engagement_type: EngagementType
    status: EngagementStatus
    fiscal_year_end: date
    start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    partner_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    locked_at: Optional[datetime] = None
    locked_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class EngagementListResponse(BaseModel):
    """List of engagements"""
    engagements: List[EngagementResponse]
    total: int
    page: int
    page_size: int


class StatusTransitionRequest(BaseModel):
    """Request to transition engagement status"""
    new_status: EngagementStatus
    notes: Optional[str] = None


class StatusTransitionResponse(BaseModel):
    """Response for status transition"""
    success: bool
    engagement_id: UUID
    old_status: EngagementStatus
    new_status: EngagementStatus
    message: str


# ========================================
# Team Member Schemas
# ========================================

class TeamMemberAdd(BaseModel):
    """Add team member to engagement"""
    user_id: UUID
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class TeamMemberResponse(BaseModel):
    """Team member response"""
    id: UUID
    engagement_id: UUID
    user_id: UUID
    role: UserRole
    assigned_at: datetime
    assigned_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class TeamMemberListResponse(BaseModel):
    """List of team members"""
    team_members: List[TeamMemberResponse]
    total: int


# ========================================
# Binder & Workpaper Schemas
# ========================================

class BinderNodeCreate(BaseModel):
    """Create binder node"""
    parent_id: Optional[UUID] = None
    node_type: BinderNodeType
    node_code: Optional[str] = Field(None, max_length=50)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    position: int = Field(default=0, ge=0)

    model_config = ConfigDict(from_attributes=True)


class BinderNodeUpdate(BaseModel):
    """Update binder node"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    position: Optional[int] = Field(None, ge=0)
    status: Optional[WorkpaperStatus] = None

    model_config = ConfigDict(from_attributes=True)


class BinderNodeResponse(BaseModel):
    """Binder node response"""
    id: UUID
    engagement_id: UUID
    parent_id: Optional[UUID] = None
    node_type: BinderNodeType
    node_code: Optional[str] = None
    title: str
    description: Optional[str] = None
    position: int
    status: Optional[WorkpaperStatus] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BinderTreeResponse(BaseModel):
    """Hierarchical binder tree"""
    node: BinderNodeResponse
    children: List["BinderTreeResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# Enable forward references for recursive model
BinderTreeResponse.model_rebuild()


class WorkpaperCreate(BaseModel):
    """Create workpaper"""
    binder_node_id: UUID
    content: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class WorkpaperUpdate(BaseModel):
    """Update workpaper"""
    content: Optional[dict] = None
    status: Optional[WorkpaperStatus] = None

    model_config = ConfigDict(from_attributes=True)


class WorkpaperResponse(BaseModel):
    """Workpaper response"""
    id: UUID
    binder_node_id: UUID
    content: Optional[dict] = None
    prepared_by: Optional[UUID] = None
    prepared_at: Optional[datetime] = None
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========================================
# Review Note Schemas
# ========================================

class ReviewNoteCreate(BaseModel):
    """Create review note"""
    workpaper_id: Optional[UUID] = None
    procedure_id: Optional[UUID] = None
    note_text: str = Field(..., min_length=1)
    is_blocking: bool = False

    model_config = ConfigDict(from_attributes=True)


class ReviewNoteUpdate(BaseModel):
    """Update review note"""
    note_text: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(open|addressed|cleared)$")

    model_config = ConfigDict(from_attributes=True)


class ReviewNoteResponse(BaseModel):
    """Review note response"""
    id: UUID
    workpaper_id: Optional[UUID] = None
    procedure_id: Optional[UUID] = None
    reviewer_id: UUID
    note_text: str
    is_blocking: bool
    status: str
    addressed_by: Optional[UUID] = None
    addressed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewNoteListResponse(BaseModel):
    """List of review notes"""
    review_notes: List[ReviewNoteResponse]
    total: int
    open_blocking_count: int
