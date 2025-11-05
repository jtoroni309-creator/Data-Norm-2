"""SQLAlchemy ORM models for Engagement Service"""
from datetime import datetime, date
from uuid import uuid4
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Date,
    Boolean,
    Integer,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from .database import Base


# ========================================
# Enums
# ========================================

class EngagementStatus(str, Enum):
    """Engagement lifecycle status"""
    DRAFT = "draft"
    PLANNING = "planning"
    FIELDWORK = "fieldwork"
    REVIEW = "review"
    FINALIZED = "finalized"


class EngagementType(str, Enum):
    """Type of engagement"""
    AUDIT = "audit"
    REVIEW = "review"
    COMPILATION = "compilation"
    AGREED_UPON_PROCEDURES = "agreed_upon_procedures"


class UserRole(str, Enum):
    """User role on engagement team"""
    PARTNER = "partner"
    MANAGER = "manager"
    SENIOR = "senior"
    STAFF = "staff"
    QC_REVIEWER = "qc_reviewer"
    CLIENT_CONTACT = "client_contact"


class BinderNodeType(str, Enum):
    """Type of binder node"""
    FOLDER = "folder"
    WORKPAPER = "workpaper"
    EVIDENCE = "evidence"
    NOTE = "note"


class WorkpaperStatus(str, Enum):
    """Workpaper review status"""
    DRAFT = "draft"
    PREPARED = "prepared"
    REVIEWED = "reviewed"
    APPROVED = "approved"


# ========================================
# ORM Models
# ========================================

class Engagement(Base):
    """
    Core engagement entity

    Represents an audit, review, compilation, or AUP engagement for a client.
    Includes state machine tracking (draft → planning → fieldwork → review → finalized).
    """
    __tablename__ = "engagements"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    name = Column(Text, nullable=False)
    engagement_type = Column(
        SQLEnum(EngagementType, name="engagement_type", create_type=False),
        nullable=False
    )
    status = Column(
        SQLEnum(EngagementStatus, name="engagement_status", create_type=False),
        nullable=False,
        default=EngagementStatus.DRAFT,
        index=True
    )
    fiscal_year_end = Column(Date, nullable=False)
    start_date = Column(Date)
    expected_completion_date = Column(Date)
    partner_id = Column(PGUUID(as_uuid=True), index=True)
    manager_id = Column(PGUUID(as_uuid=True))
    created_by = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    locked_at = Column(DateTime(timezone=True))
    locked_by = Column(PGUUID(as_uuid=True))

    # Relationships
    team_members = relationship("EngagementTeamMember", back_populates="engagement", cascade="all, delete-orphan")
    binder_nodes = relationship("BinderNode", back_populates="engagement", cascade="all, delete-orphan")


class EngagementTeamMember(Base):
    """
    Team member assignment to engagement

    Links users to engagements with their role (partner, manager, senior, staff, etc).
    Used for access control and RLS (Row-Level Security) filtering.
    """
    __tablename__ = "engagement_team_members"
    __table_args__ = (
        Index("idx_team_members_engagement", "engagement_id"),
        Index("idx_team_members_user", "user_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.engagements.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    role = Column(
        SQLEnum(UserRole, name="user_role", create_type=False),
        nullable=False
    )
    assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    assigned_by = Column(PGUUID(as_uuid=True))

    # Relationships
    engagement = relationship("Engagement", back_populates="team_members")


class BinderNode(Base):
    """
    Hierarchical binder structure

    Represents folders, workpapers, evidence, and notes in a tree structure.
    Each engagement has a binder with nested folders and workpapers (e.g., A-100, B-200).
    """
    __tablename__ = "binder_nodes"
    __table_args__ = (
        Index("idx_binder_nodes_engagement", "engagement_id"),
        Index("idx_binder_nodes_parent", "parent_id"),
        Index("idx_binder_nodes_position", "engagement_id", "parent_id", "position"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.engagements.id", ondelete="CASCADE"),
        nullable=False
    )
    parent_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.binder_nodes.id", ondelete="CASCADE")
    )
    node_type = Column(
        SQLEnum(BinderNodeType, name="binder_node_type", create_type=False),
        nullable=False
    )
    node_code = Column(String)  # e.g., 'A-100', 'B-200'
    title = Column(Text, nullable=False)
    description = Column(Text)
    position = Column(Integer, nullable=False, default=0)
    status = Column(
        SQLEnum(WorkpaperStatus, name="workpaper_status", create_type=False),
        default=WorkpaperStatus.DRAFT
    )
    created_by = Column(PGUUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    engagement = relationship("Engagement", back_populates="binder_nodes")
    parent = relationship("BinderNode", remote_side=[id], backref="children")
    workpapers = relationship("Workpaper", back_populates="binder_node", cascade="all, delete-orphan")


class Workpaper(Base):
    """
    Workpaper content and metadata

    Contains the actual content of a workpaper (JSONB for rich text/structured data).
    Tracks preparation, review, and approval workflow.
    """
    __tablename__ = "workpapers"
    __table_args__ = (
        Index("idx_workpapers_node", "binder_node_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    binder_node_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.binder_nodes.id", ondelete="CASCADE"),
        nullable=False
    )
    content = Column(JSONB)  # Rich text or structured content
    prepared_by = Column(PGUUID(as_uuid=True))
    prepared_at = Column(DateTime(timezone=True))
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    approved_by = Column(PGUUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    binder_node = relationship("BinderNode", back_populates="workpapers")
    review_notes = relationship("ReviewNote", back_populates="workpaper", cascade="all, delete-orphan")


class ReviewNote(Base):
    """
    Review comments on workpapers

    Reviewers can add blocking or non-blocking notes to workpapers.
    Blocking notes must be addressed before finalization.
    """
    __tablename__ = "review_notes"
    __table_args__ = (
        Index("idx_review_notes_workpaper", "workpaper_id"),
        Index("idx_review_notes_reviewer", "reviewer_id"),
        Index("idx_review_notes_status", "status"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workpaper_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.workpapers.id", ondelete="CASCADE")
    )
    procedure_id = Column(PGUUID(as_uuid=True))  # Optional link to procedure
    reviewer_id = Column(PGUUID(as_uuid=True), nullable=False)
    note_text = Column(Text, nullable=False)
    is_blocking = Column(Boolean, nullable=False, default=False)
    status = Column(String, nullable=False, default="open")  # 'open', 'addressed', 'cleared'
    addressed_by = Column(PGUUID(as_uuid=True))
    addressed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    workpaper = relationship("Workpaper", back_populates="review_notes")
