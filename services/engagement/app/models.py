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
    draft = "draft"
    planning = "planning"
    fieldwork = "fieldwork"
    review = "review"
    finalized = "finalized"


class EngagementType(str, Enum):
    """Type of engagement"""
    audit = "audit"
    review = "review"
    compilation = "compilation"
    agreed_upon_procedures = "agreed_upon_procedures"


class UserRole(str, Enum):
    """User role on engagement team"""
    partner = "partner"
    manager = "manager"
    senior = "senior"
    staff = "staff"
    qc_reviewer = "qc_reviewer"
    client_contact = "client_contact"


class BinderNodeType(str, Enum):
    """Type of binder node"""
    folder = "folder"
    workpaper = "workpaper"
    evidence = "evidence"
    note = "note"


class WorkpaperStatus(str, Enum):
    """Workpaper review status"""
    draft = "draft"
    prepared = "prepared"
    reviewed = "reviewed"
    approved = "approved"


class ComponentSignificance(str, Enum):
    """Significance level of component entity"""
    significant = "significant"
    not_significant = "not_significant"
    material = "material"
    immaterial = "immaterial"


class ComponentAuditApproach(str, Enum):
    """Audit approach for component"""
    full_scope = "full_scope"
    specific_scope = "specific_scope"
    analytical_review = "analytical_review"
    desktop_review = "desktop_review"
    no_procedures = "no_procedures"


class ComponentAuditorType(str, Enum):
    """Type of component auditor"""
    group_team = "group_team"
    network_firm = "network_firm"
    non_network_firm = "non_network_firm"
    specialist = "specialist"


class EliminationEntryType(str, Enum):
    """Type of elimination entry"""
    intercompany_revenue = "intercompany_revenue"
    intercompany_payable_receivable = "intercompany_payable_receivable"
    intercompany_investment = "intercompany_investment"
    unrealized_profit = "unrealized_profit"
    dividend = "dividend"
    other = "other"


class ConsolidationMethod(str, Enum):
    """Consolidation method for component"""
    full_consolidation = "full_consolidation"
    proportionate = "proportionate"
    equity_method = "equity_method"
    cost_method = "cost_method"


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
        SQLEnum(EngagementType, name="engagement_type", create_type=False, schema="atlas"),
        nullable=False
    )
    status = Column(
        SQLEnum(EngagementStatus, name="engagement_status", create_type=False, schema="atlas"),
        nullable=False,
        default=EngagementStatus.draft,
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
        SQLEnum(UserRole, name="user_role", create_type=False, schema="atlas"),
        nullable=False
    )
    assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    assigned_by = Column(PGUUID(as_uuid=True))

    # Relationships
    engagement = relationship("Engagement", back_populates="team_members")


class EngagementCustomer(Base):
    """
    Customer (client user) assignment to engagement

    Links customer users to specific engagements with granular permissions.
    Allows CPA firms to grant customers access to their own engagement data,
    upload documents, and connect integrations.
    """
    __tablename__ = "engagement_customers"
    __table_args__ = (
        Index("idx_engagement_customers_engagement", "engagement_id"),
        Index("idx_engagement_customers_user", "customer_user_id"),
        Index("idx_engagement_customers_active", "is_active"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.engagements.id", ondelete="CASCADE"),
        nullable=False
    )
    customer_user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)  # References user from identity service

    # Customer role on engagement
    role = Column(String(100), default="primary_contact")  # primary_contact, secondary_contact, authorized_signer

    # Granular permissions for this customer on this engagement
    can_view_reports = Column(Boolean, default=True)
    can_upload_documents = Column(Boolean, default=True)
    can_manage_integrations = Column(Boolean, default=True)
    can_view_financials = Column(Boolean, default=True)
    can_complete_questionnaires = Column(Boolean, default=True)
    can_approve_confirmations = Column(Boolean, default=False)

    # Access control
    is_active = Column(Boolean, default=True)
    access_expires_at = Column(DateTime(timezone=True))

    # Invitation tracking
    invited_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    invited_by = Column(PGUUID(as_uuid=True), nullable=False)  # CPA user who granted access
    access_granted_at = Column(DateTime(timezone=True))  # When customer accepted invitation
    last_accessed_at = Column(DateTime(timezone=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Additional context
    notes = Column(Text)  # Internal notes about this customer's access

    # Relationships
    engagement = relationship("Engagement", backref="customers")


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
        SQLEnum(BinderNodeType, name="binder_node_type", create_type=False, schema="atlas"),
        nullable=False
    )
    node_code = Column(String)  # e.g., 'A-100', 'B-200'
    title = Column(Text, nullable=False)
    description = Column(Text)
    position = Column(Integer, nullable=False, default=0)
    status = Column(
        SQLEnum(WorkpaperStatus, name="workpaper_status", create_type=False, schema="atlas"),
        default=WorkpaperStatus.draft
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


# ========================================
# Group Audit Models
# ========================================

class GroupEngagement(Base):
    """
    Group Audit Engagement - Parent entity for consolidated audits

    Represents the top-level group audit engagement that links multiple
    component entity engagements together for consolidated financial statement audits.
    """
    __tablename__ = "group_engagements"
    __table_args__ = (
        Index("idx_group_engagements_parent", "parent_engagement_id"),
        Index("idx_group_engagements_status", "status"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    parent_engagement_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.engagements.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    # Group information
    group_name = Column(Text, nullable=False)
    ultimate_parent_name = Column(Text)
    reporting_framework = Column(String(100), default="US GAAP")  # US GAAP, IFRS, etc.
    functional_currency = Column(String(10), default="USD")

    # Group-level materiality
    group_materiality = Column(Integer)  # Overall materiality for group
    group_performance_materiality = Column(Integer)  # Performance materiality
    component_materiality = Column(Integer)  # Threshold for components
    clearly_trivial_threshold = Column(Integer)

    # Risk assessment
    group_risk_level = Column(String(50), default="moderate")  # low, moderate, high
    risk_factors = Column(JSONB)  # JSON list of identified risk factors

    # Consolidation settings
    consolidation_date = Column(Date)
    reporting_period_end = Column(Date)

    # Status tracking
    status = Column(String(50), default="planning")  # planning, in_progress, component_review, consolidation, finalized

    # Metadata
    created_by = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    parent_engagement = relationship("Engagement", backref="group_engagement", foreign_keys=[parent_engagement_id])
    component_entities = relationship("ComponentEntity", back_populates="group_engagement", cascade="all, delete-orphan")
    elimination_entries = relationship("EliminationEntry", back_populates="group_engagement", cascade="all, delete-orphan")
    consolidated_statements = relationship("ConsolidatedStatement", back_populates="group_engagement", cascade="all, delete-orphan")


class ComponentEntity(Base):
    """
    Component Entity - Subsidiary or division within a group audit

    Represents a subsidiary, division, branch, or other component that is part of
    the consolidated group. Each component can have its own engagement and auditor.
    """
    __tablename__ = "component_entities"
    __table_args__ = (
        Index("idx_component_entities_group", "group_engagement_id"),
        Index("idx_component_entities_engagement", "component_engagement_id"),
        Index("idx_component_entities_significance", "significance"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    group_engagement_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.group_engagements.id", ondelete="CASCADE"),
        nullable=False
    )
    component_engagement_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.engagements.id", ondelete="SET NULL"),
        nullable=True
    )

    # Entity information
    entity_name = Column(Text, nullable=False)
    entity_code = Column(String(50))  # Short code for the entity (e.g., "US-001")
    legal_name = Column(Text)
    jurisdiction = Column(String(100))  # Country/state of incorporation
    functional_currency = Column(String(10), default="USD")

    # Ownership structure
    ownership_percentage = Column(Integer, default=100)  # Percentage owned by parent
    direct_parent_id = Column(PGUUID(as_uuid=True))  # For multi-tier structures
    consolidation_method = Column(
        SQLEnum(ConsolidationMethod, name="consolidation_method", create_type=False, schema="atlas"),
        default=ConsolidationMethod.full_consolidation
    )

    # Significance assessment
    significance = Column(
        SQLEnum(ComponentSignificance, name="component_significance", create_type=False, schema="atlas"),
        default=ComponentSignificance.not_significant
    )
    significance_factors = Column(JSONB)  # JSON with factors driving significance

    # Financial metrics
    total_assets = Column(Integer)
    total_revenue = Column(Integer)
    net_income = Column(Integer)
    percentage_of_group_assets = Column(Integer)  # Stored as basis points (100 = 1%)
    percentage_of_group_revenue = Column(Integer)

    # Audit approach
    audit_approach = Column(
        SQLEnum(ComponentAuditApproach, name="component_audit_approach", create_type=False, schema="atlas"),
        default=ComponentAuditApproach.analytical_review
    )
    scoped_accounts = Column(JSONB)  # List of accounts in scope for specific scope audits

    # Component-level materiality
    component_materiality = Column(Integer)
    component_performance_materiality = Column(Integer)

    # Risk assessment
    risk_level = Column(String(50), default="moderate")
    identified_risks = Column(JSONB)

    # Status
    status = Column(String(50), default="pending")  # pending, in_progress, completed, reviewed
    completion_percentage = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    group_engagement = relationship("GroupEngagement", back_populates="component_entities")
    component_engagement = relationship("Engagement", backref="as_component", foreign_keys=[component_engagement_id])
    component_auditors = relationship("ComponentAuditor", back_populates="component_entity", cascade="all, delete-orphan")


class ComponentAuditor(Base):
    """
    Component Auditor - Auditor responsible for a component entity

    Tracks which auditor (group team, network firm, or other firm) is responsible
    for auditing a specific component entity.
    """
    __tablename__ = "component_auditors"
    __table_args__ = (
        Index("idx_component_auditors_component", "component_entity_id"),
        Index("idx_component_auditors_type", "auditor_type"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    component_entity_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.component_entities.id", ondelete="CASCADE"),
        nullable=False
    )

    # Auditor information
    auditor_type = Column(
        SQLEnum(ComponentAuditorType, name="component_auditor_type", create_type=False, schema="atlas"),
        nullable=False
    )
    firm_name = Column(Text, nullable=False)
    firm_id = Column(PGUUID(as_uuid=True))  # Reference to firm if in system

    # Contact information
    lead_partner_name = Column(Text)
    lead_partner_email = Column(String(255))
    lead_partner_phone = Column(String(50))

    # Quality assessment
    competence_assessment = Column(String(50))  # satisfied, concerns, not_assessed
    independence_confirmed = Column(Boolean, default=False)
    independence_confirmation_date = Column(Date)

    # Instructions and communications
    instructions_sent_date = Column(Date)
    instructions_acknowledged_date = Column(Date)
    reporting_deadline = Column(Date)

    # Deliverables tracking
    deliverables = Column(JSONB)  # List of expected deliverables
    deliverables_received = Column(Boolean, default=False)
    deliverables_reviewed = Column(Boolean, default=False)

    # Issues and findings
    issues_identified = Column(JSONB)
    findings_summary = Column(Text)

    # Status
    status = Column(String(50), default="pending")  # pending, engaged, reporting, completed

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    component_entity = relationship("ComponentEntity", back_populates="component_auditors")


class EliminationEntry(Base):
    """
    Elimination Entry - Intercompany elimination for consolidation

    Tracks elimination entries required for consolidated financial statement preparation,
    including intercompany revenues, payables/receivables, investments, and unrealized profits.
    """
    __tablename__ = "elimination_entries"
    __table_args__ = (
        Index("idx_elimination_entries_group", "group_engagement_id"),
        Index("idx_elimination_entries_type", "entry_type"),
        Index("idx_elimination_entries_status", "status"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    group_engagement_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.group_engagements.id", ondelete="CASCADE"),
        nullable=False
    )

    # Entry details
    entry_number = Column(String(50))  # E.g., "ELIM-001"
    entry_type = Column(
        SQLEnum(EliminationEntryType, name="elimination_entry_type", create_type=False, schema="atlas"),
        nullable=False
    )
    description = Column(Text, nullable=False)

    # Entities involved
    from_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.component_entities.id"))
    to_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.component_entities.id"))

    # Financial details (stored in cents for precision)
    debit_account = Column(String(100))
    debit_amount = Column(Integer)  # Amount in cents
    credit_account = Column(String(100))
    credit_amount = Column(Integer)  # Amount in cents

    # Journal entry lines for complex entries
    journal_lines = Column(JSONB)  # Array of {account, debit, credit, description}

    # Supporting documentation
    supporting_workpaper_id = Column(PGUUID(as_uuid=True))
    documentation = Column(Text)

    # Recurrence
    is_recurring = Column(Boolean, default=False)
    prior_year_amount = Column(Integer)

    # Review status
    status = Column(String(50), default="draft")  # draft, prepared, reviewed, approved
    prepared_by = Column(PGUUID(as_uuid=True))
    prepared_at = Column(DateTime(timezone=True))
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    group_engagement = relationship("GroupEngagement", back_populates="elimination_entries")
    from_entity = relationship("ComponentEntity", foreign_keys=[from_entity_id])
    to_entity = relationship("ComponentEntity", foreign_keys=[to_entity_id])


class ConsolidatedStatement(Base):
    """
    Consolidated Financial Statement - Assembled consolidated financials

    Stores the consolidated financial statement data after applying all
    component entity financials and elimination entries.
    """
    __tablename__ = "consolidated_statements"
    __table_args__ = (
        Index("idx_consolidated_statements_group", "group_engagement_id"),
        Index("idx_consolidated_statements_type", "statement_type"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    group_engagement_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.group_engagements.id", ondelete="CASCADE"),
        nullable=False
    )

    # Statement details
    statement_type = Column(String(100), nullable=False)  # balance_sheet, income_statement, cash_flow, equity_changes
    period_end_date = Column(Date, nullable=False)
    comparative_period_end = Column(Date)

    # Consolidated data
    current_period_data = Column(JSONB)  # Full statement data in JSON
    prior_period_data = Column(JSONB)

    # Rollup tracking
    component_contributions = Column(JSONB)  # Breakdown by component
    elimination_adjustments = Column(JSONB)  # Applied eliminations

    # Variance analysis
    variance_to_prior = Column(JSONB)  # Line-by-line variances
    significant_variances = Column(JSONB)  # Flagged items requiring explanation

    # Review status
    status = Column(String(50), default="draft")  # draft, prepared, reviewed, approved
    prepared_by = Column(PGUUID(as_uuid=True))
    prepared_at = Column(DateTime(timezone=True))
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))

    # Version control
    version = Column(Integer, default=1)
    is_final = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    group_engagement = relationship("GroupEngagement", back_populates="consolidated_statements")


class GroupAuditRiskConsolidation(Base):
    """
    Group Audit Risk Consolidation - Cross-entity risk analysis

    Consolidates and analyzes risks across all component entities to identify
    group-level significant risks and allocate audit resources appropriately.
    """
    __tablename__ = "group_audit_risk_consolidations"
    __table_args__ = (
        Index("idx_group_risk_consolidation_group", "group_engagement_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    group_engagement_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.group_engagements.id", ondelete="CASCADE"),
        nullable=False
    )

    # Risk category
    risk_category = Column(String(100), nullable=False)  # fraud, going_concern, related_party, etc.
    risk_title = Column(Text, nullable=False)
    risk_description = Column(Text)

    # Assessment
    inherent_risk = Column(String(50), default="moderate")  # low, moderate, high, very_high
    control_risk = Column(String(50), default="moderate")
    combined_risk = Column(String(50), default="moderate")

    # Component impact
    affected_components = Column(JSONB)  # List of component_entity_ids
    pervasive = Column(Boolean, default=False)  # Affects group as a whole

    # Response
    planned_response = Column(Text)
    audit_procedures = Column(JSONB)  # Planned procedures to address risk

    # Status
    status = Column(String(50), default="identified")  # identified, assessed, responded, concluded
    conclusion = Column(Text)

    # Metadata
    created_by = Column(PGUUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    group_engagement = relationship("GroupEngagement", backref="risk_consolidations")
