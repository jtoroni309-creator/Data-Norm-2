"""
SOC Copilot Data Models (SQLAlchemy ORM)
Implements schema from migrations/001_init_schema.sql
"""
import enum
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    String, Text, Integer, BigInteger, Boolean, Date, DECIMAL,
    ForeignKey, Index, CheckConstraint, UniqueConstraint,
    ARRAY, JSON as SQLJSON, Enum as SQLEnum, TIMESTAMP
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .database import Base


# ============================================================================
# ENUMS
# ============================================================================

class EngagementType(str, enum.Enum):
    SOC1 = "SOC1"
    SOC2 = "SOC2"


class ReportType(str, enum.Enum):
    TYPE1 = "TYPE1"
    TYPE2 = "TYPE2"


class EngagementStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    FIELDWORK = "FIELDWORK"
    REVIEW = "REVIEW"
    PARTNER_REVIEW = "PARTNER_REVIEW"
    SIGNED = "SIGNED"
    RELEASED = "RELEASED"
    ARCHIVED = "ARCHIVED"


class UserRole(str, enum.Enum):
    CPA_PARTNER = "CPA_PARTNER"
    AUDIT_MANAGER = "AUDIT_MANAGER"
    AUDITOR = "AUDITOR"
    CLIENT_MANAGEMENT = "CLIENT_MANAGEMENT"
    READ_ONLY = "READ_ONLY"


class TSCCategory(str, enum.Enum):
    SECURITY = "SECURITY"
    AVAILABILITY = "AVAILABILITY"
    PROCESSING_INTEGRITY = "PROCESSING_INTEGRITY"
    CONFIDENTIALITY = "CONFIDENTIALITY"
    PRIVACY = "PRIVACY"


class ControlType(str, enum.Enum):
    PREVENTIVE = "PREVENTIVE"
    DETECTIVE = "DETECTIVE"
    CORRECTIVE = "CORRECTIVE"


class TestType(str, enum.Enum):
    WALKTHROUGH = "WALKTHROUGH"
    DESIGN_EVALUATION = "DESIGN_EVALUATION"
    OPERATING_EFFECTIVENESS = "OPERATING_EFFECTIVENESS"


class TestStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PASSED = "PASSED"
    FAILED = "FAILED"
    DEVIATION = "DEVIATION"
    RETESTED = "RETESTED"


class EvidenceSourceType(str, enum.Enum):
    IAM = "IAM"
    SIEM = "SIEM"
    TICKETING = "TICKETING"
    CHANGE_MANAGEMENT = "CHANGE_MANAGEMENT"
    CI_CD = "CI_CD"
    CLOUD_PROVIDER = "CLOUD_PROVIDER"
    MANUAL_UPLOAD = "MANUAL_UPLOAD"
    SYSTEM_GENERATED = "SYSTEM_GENERATED"


class DeviationSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class SubserviceTreatment(str, enum.Enum):
    INCLUSIVE = "INCLUSIVE"
    CARVE_OUT = "CARVE_OUT"


# ============================================================================
# USER & RBAC
# ============================================================================

class User(Base):
    """User model - reads from atlas.users (shared identity schema)"""
    __tablename__ = "users"
    __table_args__ = {"schema": "atlas"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    cpa_firm_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    client_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def full_name(self) -> str:
        """Computed full name property"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email

    @property
    def role(self) -> UserRole:
        """Default role for all authenticated users - CPA users get AUDIT_MANAGER access"""
        # Users with cpa_firm_id are CPA staff, give them manager access
        # Client users (with client_id) get CLIENT_MANAGEMENT access
        if self.cpa_firm_id:
            return UserRole.AUDIT_MANAGER
        elif self.client_id:
            return UserRole.CLIENT_MANAGEMENT
        return UserRole.READ_ONLY


# ============================================================================
# SOC ENGAGEMENT
# ============================================================================

class SOCEngagement(Base):
    __tablename__ = "soc_engagements"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    client_name: Mapped[str] = mapped_column(String(500), nullable=False)
    service_description: Mapped[str] = mapped_column(Text, nullable=False)
    engagement_type: Mapped[EngagementType] = mapped_column(SQLEnum(EngagementType, name='engagementtype', create_type=False), nullable=False)
    report_type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType, name='reporttype', create_type=False), nullable=False)
    status: Mapped[EngagementStatus] = mapped_column(SQLEnum(EngagementStatus, name='engagementstatus', create_type=False), default=EngagementStatus.DRAFT, index=True)

    # SOC 2 specific
    tsc_categories: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Period
    review_period_start: Mapped[Optional[date]] = mapped_column(Date)
    review_period_end: Mapped[Optional[date]] = mapped_column(Date)
    point_in_time_date: Mapped[Optional[date]] = mapped_column(Date)

    # Team
    partner_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), nullable=False, index=True)
    manager_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), nullable=False, index=True)
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), nullable=False)

    # Metadata
    fiscal_year_end: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    locked_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    locked_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))

    # Relationships
    team_members: Mapped[List["EngagementTeam"]] = relationship(back_populates="engagement", cascade="all, delete-orphan")
    system_components: Mapped[List["SystemComponent"]] = relationship(back_populates="engagement", cascade="all, delete-orphan")
    control_objectives: Mapped[List["ControlObjective"]] = relationship(back_populates="engagement", cascade="all, delete-orphan")


class EngagementTeam(Base):
    __tablename__ = "engagement_team"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), index=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name='userrole', create_type=False), nullable=False)
    assigned_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))
    assigned_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    removed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))

    # Relationships
    engagement: Mapped["SOCEngagement"] = relationship(back_populates="team_members")


# ============================================================================
# SYSTEM COMPONENTS
# ============================================================================

class SystemComponent(Base):
    __tablename__ = "system_components"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)
    component_name: Mapped[str] = mapped_column(String(255), nullable=False)
    component_type: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    in_scope: Mapped[bool] = mapped_column(Boolean, default=True)
    boundaries: Mapped[Optional[str]] = mapped_column(Text)
    data_flows: Mapped[Optional[dict]] = mapped_column(SQLJSON)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    engagement: Mapped["SOCEngagement"] = relationship(back_populates="system_components")


# ============================================================================
# SUBSERVICE ORGANIZATIONS
# ============================================================================

class SubserviceOrg(Base):
    __tablename__ = "subservice_orgs"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)
    org_name: Mapped[str] = mapped_column(String(255), nullable=False)
    service_description: Mapped[str] = mapped_column(Text, nullable=False)
    treatment: Mapped[SubserviceTreatment] = mapped_column(SQLEnum(SubserviceTreatment, name='subservicetreatment', create_type=False), nullable=False)
    has_soc_report: Mapped[bool] = mapped_column(Boolean, default=False)
    soc_report_period_start: Mapped[Optional[date]] = mapped_column(Date)
    soc_report_period_end: Mapped[Optional[date]] = mapped_column(Date)
    soc_report_opinion: Mapped[Optional[str]] = mapped_column(String(50))
    monitoring_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    csoc: Mapped[List["CSOC"]] = relationship(back_populates="subservice_org", cascade="all, delete-orphan")


# ============================================================================
# CONTROL OBJECTIVES
# ============================================================================

class ControlObjective(Base):
    __tablename__ = "control_objectives"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)
    objective_code: Mapped[str] = mapped_column(String(50), nullable=False)
    objective_name: Mapped[str] = mapped_column(String(500), nullable=False)
    objective_description: Mapped[str] = mapped_column(Text, nullable=False)

    # SOC 1: ICFR relevance
    icfr_assertion: Mapped[Optional[str]] = mapped_column(String(100))

    # SOC 2: TSC mapping
    tsc_category: Mapped[Optional[TSCCategory]] = mapped_column(SQLEnum(TSCCategory, name='tsccategory', create_type=False))
    tsc_criteria: Mapped[Optional[str]] = mapped_column(String(50))
    points_of_focus_2022: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    engagement: Mapped["SOCEngagement"] = relationship(back_populates="control_objectives")
    controls: Mapped[List["Control"]] = relationship(back_populates="objective", cascade="all, delete-orphan")


# ============================================================================
# CONTROLS
# ============================================================================

class Control(Base):
    __tablename__ = "controls"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)
    objective_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.control_objectives.id", ondelete="CASCADE"), index=True)
    control_code: Mapped[str] = mapped_column(String(50), nullable=False)
    control_name: Mapped[str] = mapped_column(String(500), nullable=False)
    control_description: Mapped[str] = mapped_column(Text, nullable=False)
    control_type: Mapped[ControlType] = mapped_column(SQLEnum(ControlType, name='controltype', create_type=False), nullable=False)
    control_owner: Mapped[Optional[str]] = mapped_column(String(255))
    frequency: Mapped[Optional[str]] = mapped_column(String(100))
    automation_level: Mapped[Optional[str]] = mapped_column(String(50))

    # Design assessment
    design_adequate: Mapped[Optional[bool]] = mapped_column(Boolean)
    design_notes: Mapped[Optional[str]] = mapped_column(Text)

    is_key_control: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    objective: Mapped["ControlObjective"] = relationship(back_populates="controls")
    test_plans: Mapped[List["TestPlan"]] = relationship(back_populates="control", cascade="all, delete-orphan")
    cuec: Mapped[List["CUEC"]] = relationship(back_populates="control", cascade="all, delete-orphan")


# ============================================================================
# CUEC & CSOC
# ============================================================================

class CUEC(Base):
    """Complementary User Entity Controls"""
    __tablename__ = "cuec"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)
    control_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.controls.id"))
    cuec_description: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[Optional[str]] = mapped_column(Text)
    disclosed_in_report: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    control: Mapped[Optional["Control"]] = relationship(back_populates="cuec")


class CSOC(Base):
    """Complementary Subservice Organization Controls"""
    __tablename__ = "csoc"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    subservice_org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.subservice_orgs.id", ondelete="CASCADE"), index=True)
    csoc_description: Mapped[str] = mapped_column(Text, nullable=False)
    monitoring_procedure: Mapped[Optional[str]] = mapped_column(Text)
    last_monitored_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    subservice_org: Mapped["SubserviceOrg"] = relationship(back_populates="csoc")


# ============================================================================
# TEST PLANS
# ============================================================================

class TestPlan(Base):
    __tablename__ = "test_plans"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)
    control_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.controls.id", ondelete="CASCADE"), index=True)
    test_type: Mapped[TestType] = mapped_column(SQLEnum(TestType, name='testtype', create_type=False), nullable=False)
    test_objective: Mapped[str] = mapped_column(Text, nullable=False)
    test_procedures: Mapped[str] = mapped_column(Text, nullable=False)

    # Type 2 specific
    sample_size: Mapped[Optional[int]] = mapped_column(Integer)
    sampling_method: Mapped[Optional[str]] = mapped_column(String(100))
    population_size: Mapped[Optional[int]] = mapped_column(Integer)

    # Evidence requirements
    required_evidence_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # AI suggestions
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_confidence_score: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))
    ai_rationale: Mapped[Optional[str]] = mapped_column(Text)

    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    control: Mapped["Control"] = relationship(back_populates="test_plans")
    test_results: Mapped[List["TestResult"]] = relationship(back_populates="test_plan", cascade="all, delete-orphan")
    evidence: Mapped[List["Evidence"]] = relationship(back_populates="test_plan")


# ============================================================================
# EVIDENCE
# ============================================================================

class EvidenceSource(Base):
    __tablename__ = "evidence_sources"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[EvidenceSourceType] = mapped_column(SQLEnum(EvidenceSourceType, name='evidencesourcetype', create_type=False), nullable=False)
    connection_config: Mapped[Optional[dict]] = mapped_column(SQLJSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    evidence: Mapped[List["Evidence"]] = relationship(back_populates="source")


class Evidence(Base):
    __tablename__ = "evidence"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.evidence_sources.id"))
    test_plan_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.test_plans.id"), index=True)

    # File metadata
    file_name: Mapped[Optional[str]] = mapped_column(String(500))
    file_path: Mapped[Optional[str]] = mapped_column(Text)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))

    # Chain of custody
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True, unique=True)
    collected_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    collected_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))

    # Classification
    evidence_type: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # AI quality scoring
    quality_score: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))
    relevance_score: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))
    completeness_score: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))
    ai_extracted_data: Mapped[Optional[dict]] = mapped_column(SQLJSON)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1)
    superseded_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.evidence.id"))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    source: Mapped[Optional["EvidenceSource"]] = relationship(back_populates="evidence")
    test_plan: Mapped[Optional["TestPlan"]] = relationship(back_populates="evidence")
    test_results: Mapped[List["TestResult"]] = relationship(back_populates="evidence")


# ============================================================================
# TEST RESULTS
# ============================================================================

class TestResult(Base):
    __tablename__ = "test_results"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    test_plan_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.test_plans.id", ondelete="CASCADE"), index=True)
    evidence_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.evidence.id"))

    test_status: Mapped[TestStatus] = mapped_column(SQLEnum(TestStatus, name='teststatus', create_type=False), nullable=False, default=TestStatus.PLANNED, index=True)
    test_date: Mapped[date] = mapped_column(Date, nullable=False)
    tested_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), nullable=False)

    # Results
    passed: Mapped[Optional[bool]] = mapped_column(Boolean)
    findings: Mapped[Optional[str]] = mapped_column(Text)
    conclusion: Mapped[Optional[str]] = mapped_column(Text)

    # Sampling details (Type 2)
    sample_item_identifier: Mapped[Optional[str]] = mapped_column(String(255))
    sample_selection_method: Mapped[Optional[str]] = mapped_column(String(100))

    reviewed_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    test_plan: Mapped["TestPlan"] = relationship(back_populates="test_results")
    evidence: Mapped[Optional["Evidence"]] = relationship(back_populates="test_results")
    deviations: Mapped[List["Deviation"]] = relationship(back_populates="test_result", cascade="all, delete-orphan")


# ============================================================================
# DEVIATIONS
# ============================================================================

class Deviation(Base):
    __tablename__ = "deviations"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    test_result_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.test_results.id", ondelete="CASCADE"), index=True)
    control_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.controls.id"))

    deviation_description: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[Optional[str]] = mapped_column(Text)
    severity: Mapped[DeviationSeverity] = mapped_column(SQLEnum(DeviationSeverity, name='deviationseverity', create_type=False), nullable=False, index=True)

    # Impact assessment
    impact_on_objective: Mapped[Optional[str]] = mapped_column(Text)
    impact_on_opinion: Mapped[Optional[str]] = mapped_column(Text)

    # Remediation
    remediation_plan: Mapped[Optional[str]] = mapped_column(Text)
    remediation_owner: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))
    remediation_deadline: Mapped[Optional[date]] = mapped_column(Date)
    remediation_completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))

    # Retesting
    retest_required: Mapped[bool] = mapped_column(Boolean, default=True)
    retest_plan_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.test_plans.id"))
    retest_passed: Mapped[Optional[bool]] = mapped_column(Boolean)

    identified_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))
    identified_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    test_result: Mapped["TestResult"] = relationship(back_populates="deviations")


# ============================================================================
# MANAGEMENT ASSERTION & SYSTEM DESCRIPTION
# ============================================================================

class ManagementAssertion(Base):
    __tablename__ = "management_assertions"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)

    assertion_text: Mapped[str] = mapped_column(Text, nullable=False)
    assertion_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Signatories
    signatory_name: Mapped[str] = mapped_column(String(255), nullable=False)
    signatory_title: Mapped[str] = mapped_column(String(255), nullable=False)
    signatory_signature_image: Mapped[Optional[str]] = mapped_column(Text)

    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class SystemDescription(Base):
    """SOC 2 System Description per DC 2018"""
    __tablename__ = "system_descriptions"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)

    # SOC 2 Description Criteria (DC) 2018
    overview: Mapped[Optional[str]] = mapped_column(Text)
    principal_service_commitments: Mapped[Optional[str]] = mapped_column(Text)
    system_components: Mapped[Optional[str]] = mapped_column(Text)
    system_boundaries: Mapped[Optional[str]] = mapped_column(Text)
    types_of_data_processed: Mapped[Optional[str]] = mapped_column(Text)
    principal_service_users: Mapped[Optional[str]] = mapped_column(Text)
    infrastructure: Mapped[Optional[str]] = mapped_column(Text)
    software: Mapped[Optional[str]] = mapped_column(Text)
    people: Mapped[Optional[str]] = mapped_column(Text)
    procedures: Mapped[Optional[str]] = mapped_column(Text)
    data_flows: Mapped[Optional[str]] = mapped_column(Text)

    # Complementary controls
    cuec_section: Mapped[Optional[str]] = mapped_column(Text)
    subservice_section: Mapped[Optional[str]] = mapped_column(Text)

    # AI generation
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_confidence_score: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))

    drafted_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))
    drafted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


# ============================================================================
# REPORTS & SIGNATURES
# ============================================================================

class Report(Base):
    __tablename__ = "reports"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)

    # Report metadata
    report_title: Mapped[str] = mapped_column(String(500), nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    report_version: Mapped[int] = mapped_column(Integer, default=1)

    # Content sections
    auditor_opinion: Mapped[Optional[str]] = mapped_column(Text)
    scope_section: Mapped[Optional[str]] = mapped_column(Text)
    control_objectives_section: Mapped[Optional[str]] = mapped_column(Text)
    tests_and_results_section: Mapped[Optional[str]] = mapped_column(Text)
    management_assertion_section: Mapped[Optional[str]] = mapped_column(Text)
    system_description_section: Mapped[Optional[str]] = mapped_column(Text)
    other_information_section: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True)
    is_signed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_released: Mapped[bool] = mapped_column(Boolean, default=False)

    # Distribution
    restricted_distribution: Mapped[bool] = mapped_column(Boolean, default=True)
    watermark_text: Mapped[Optional[str]] = mapped_column(String(500))

    # Files
    pdf_path: Mapped[Optional[str]] = mapped_column(Text)
    docx_path: Mapped[Optional[str]] = mapped_column(Text)

    drafted_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))
    drafted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    signatures: Mapped[List["Signature"]] = relationship(back_populates="report", cascade="all, delete-orphan")
    approvals: Mapped[List["Approval"]] = relationship(back_populates="report", cascade="all, delete-orphan")


class Signature(Base):
    __tablename__ = "signatures"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.reports.id", ondelete="CASCADE"), index=True)

    signer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), nullable=False, index=True)
    signer_role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name='userrole', create_type=False), nullable=False)

    signature_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    signature_image: Mapped[Optional[str]] = mapped_column(Text)
    digital_signature: Mapped[Optional[str]] = mapped_column(Text)

    # Attestation
    attestation_text: Mapped[str] = mapped_column(
        Text,
        default="I have reviewed this report and, based on my knowledge, the information is accurate and complete in all material respects."
    )

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    report: Mapped["Report"] = relationship(back_populates="signatures")


# ============================================================================
# WORKFLOW & APPROVALS
# ============================================================================

class WorkflowTask(Base):
    __tablename__ = "workflow_tasks"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)

    task_title: Mapped[str] = mapped_column(String(500), nullable=False)
    task_description: Mapped[Optional[str]] = mapped_column(Text)
    task_type: Mapped[Optional[str]] = mapped_column(String(100))

    assigned_to: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), index=True)
    assigned_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"))
    assigned_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    due_date: Mapped[Optional[date]] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(String(50), default="MEDIUM")

    status: Mapped[str] = mapped_column(String(50), default="TODO", index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))

    # Dependencies
    depends_on: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.workflow_tasks.id"))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class Approval(Base):
    __tablename__ = "approvals"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id", ondelete="CASCADE"), index=True)
    report_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.reports.id"))

    approval_type: Mapped[str] = mapped_column(String(100), nullable=False)
    approval_level: Mapped[int] = mapped_column(Integer, nullable=False)

    approver_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), nullable=False, index=True)
    approval_status: Mapped[ApprovalStatus] = mapped_column(SQLEnum(ApprovalStatus, name='approvalstatus', create_type=False), default=ApprovalStatus.PENDING, index=True)

    comments: Mapped[Optional[str]] = mapped_column(Text)

    approved_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    rejected_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    report: Mapped[Optional["Report"]] = relationship(back_populates="approvals")


# ============================================================================
# AUDIT TRAIL
# ============================================================================

class AuditTrail(Base):
    """Immutable audit trail with hash chain"""
    __tablename__ = "audit_trail"
    __table_args__ = {"schema": "soc_copilot"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("soc_copilot.soc_engagements.id"), index=True)

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)

    actor_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), index=True)
    actor_ip_address: Mapped[Optional[str]] = mapped_column(INET)

    action: Mapped[str] = mapped_column(String(100), nullable=False)

    # Event data
    before_state: Mapped[Optional[dict]] = mapped_column(SQLJSON)
    after_state: Mapped[Optional[dict]] = mapped_column(SQLJSON)

    # Hash chain (immutability)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_hash: Mapped[Optional[str]] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)
