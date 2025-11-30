"""
Database models for R&D Study Automation Service.

Comprehensive data model for Federal + State R&D tax credit studies
with full audit trail and evidence linking.
"""

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, Date, DateTime,
    ForeignKey, Index, CheckConstraint, UniqueConstraint, Numeric,
    Enum as SQLEnum, JSON, LargeBinary
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from uuid import uuid4
from enum import Enum
from decimal import Decimal

from .database import Base


# =============================================================================
# ENUMERATIONS
# =============================================================================

class StudyStatus(str, Enum):
    """Study workflow status."""
    DRAFT = "draft"
    INTAKE = "intake"
    DATA_COLLECTION = "data_collection"
    QUALIFICATION = "qualification"
    QRE_ANALYSIS = "qre_analysis"
    CALCULATION = "calculation"
    REVIEW = "review"
    CPA_APPROVAL = "cpa_approval"
    FINALIZED = "finalized"
    AMENDED = "amended"


class EntityType(str, Enum):
    """Tax entity type."""
    C_CORP = "c_corp"
    S_CORP = "s_corp"
    PARTNERSHIP = "partnership"
    LLC_CORP = "llc_corp"
    LLC_PARTNERSHIP = "llc_partnership"
    LLC_DISREGARDED = "llc_disregarded"
    SOLE_PROPRIETOR = "sole_proprietor"


class CreditMethod(str, Enum):
    """Federal R&D credit calculation method."""
    REGULAR = "regular"
    ASC = "asc"  # Alternative Simplified Credit


class QualificationStatus(str, Enum):
    """Project qualification status."""
    PENDING = "pending"
    QUALIFIED = "qualified"
    PARTIALLY_QUALIFIED = "partially_qualified"
    NOT_QUALIFIED = "not_qualified"
    NEEDS_REVIEW = "needs_review"
    CPA_OVERRIDE = "cpa_override"


class QRECategory(str, Enum):
    """Qualified Research Expense category."""
    WAGES = "wages"
    SUPPLIES = "supplies"
    CONTRACT_RESEARCH = "contract_research"
    BASIC_RESEARCH = "basic_research"
    ENERGY_RESEARCH = "energy_research"


class DocumentType(str, Enum):
    """Uploaded document type."""
    GENERAL_LEDGER = "general_ledger"
    TRIAL_BALANCE = "trial_balance"
    PAYROLL = "payroll"
    TIME_TRACKING = "time_tracking"
    JOB_COSTING = "job_costing"
    PROJECT_MANAGEMENT = "project_management"
    ENGINEERING_DOC = "engineering_doc"
    CONTRACT = "contract"
    INVOICE = "invoice"
    EMPLOYEE_LIST = "employee_list"
    ORGANIZATION_CHART = "organization_chart"
    GITHUB_EXPORT = "github_export"
    JIRA_EXPORT = "jira_export"
    INTERVIEW_TRANSCRIPT = "interview_transcript"
    OTHER = "other"


class ConfidenceLevel(str, Enum):
    """AI confidence level for assertions."""
    HIGH = "high"  # >= 85%
    MEDIUM = "medium"  # 70-84%
    LOW = "low"  # 60-69%
    INSUFFICIENT = "insufficient"  # < 60%


class RiskFlag(str, Enum):
    """Risk flags for review."""
    MISSING_EVIDENCE = "missing_evidence"
    LOW_CONFIDENCE = "low_confidence"
    OUTLIER_VALUE = "outlier_value"
    DOUBLE_COUNTING = "double_counting"
    INCONSISTENT_DATA = "inconsistent_data"
    WEAK_QUALIFICATION = "weak_qualification"
    AGGRESSIVE_POSITION = "aggressive_position"
    MISSING_DOCUMENTATION = "missing_documentation"
    INCOMPLETE_INTERVIEW = "incomplete_interview"


class UserRole(str, Enum):
    """User roles for R&D studies."""
    PARTNER = "partner"
    MANAGER = "manager"
    SENIOR = "senior"
    STAFF = "staff"
    ADMIN = "admin"
    CLIENT = "client"
    REVIEWER = "reviewer"


# =============================================================================
# CORE MODELS
# =============================================================================

class RDStudy(Base):
    """
    Main R&D tax credit study entity.

    Represents a complete study for a tax year with all related
    projects, QREs, calculations, and outputs.
    """
    __tablename__ = "rd_studies"
    __table_args__ = (
        Index("ix_rd_studies_firm_client", "firm_id", "client_id"),
        Index("ix_rd_studies_status", "status"),
        Index("ix_rd_studies_tax_year", "tax_year"),
        {"schema": "atlas"}
    )

    # Primary key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Firm and client association
    firm_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    client_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=True, index=True)

    # Study identification
    name = Column(String(500), nullable=False)
    tax_year = Column(Integer, nullable=False)
    study_type = Column(String(50), default="standard")  # standard, amended, multi_year

    # Entity information
    entity_type = Column(SQLEnum(EntityType), nullable=False)
    entity_name = Column(String(500), nullable=False)
    ein = Column(String(20), nullable=True)  # Encrypted
    fiscal_year_start = Column(Date, nullable=False)
    fiscal_year_end = Column(Date, nullable=False)
    is_short_year = Column(Boolean, default=False)
    short_year_days = Column(Integer, nullable=True)

    # Controlled group information
    is_controlled_group = Column(Boolean, default=False)
    controlled_group_id = Column(PGUUID(as_uuid=True), nullable=True)
    controlled_group_name = Column(String(500), nullable=True)
    aggregation_method = Column(String(50), nullable=True)  # standalone, aggregated, allocated

    # Status and workflow
    status = Column(SQLEnum(StudyStatus), default=StudyStatus.DRAFT, nullable=False)
    status_history = Column(JSONB, default=list)

    # Credit method selection
    recommended_method = Column(SQLEnum(CreditMethod), nullable=True)
    selected_method = Column(SQLEnum(CreditMethod), nullable=True)
    method_selection_reason = Column(Text, nullable=True)

    # State nexus
    states = Column(ARRAY(String(2)), default=list)  # State codes
    primary_state = Column(String(2), nullable=True)

    # AI analysis results
    ai_risk_score = Column(Float, nullable=True)  # 0-100
    ai_opportunity_score = Column(Float, nullable=True)  # 0-100
    ai_suggested_areas = Column(JSONB, default=list)
    ai_analysis_summary = Column(Text, nullable=True)

    # Credit amounts (calculated)
    total_qre = Column(Numeric(15, 2), default=0)
    federal_credit_regular = Column(Numeric(15, 2), default=0)
    federal_credit_asc = Column(Numeric(15, 2), default=0)
    federal_credit_final = Column(Numeric(15, 2), default=0)
    total_state_credits = Column(Numeric(15, 2), default=0)
    total_credits = Column(Numeric(15, 2), default=0)

    # Carryforward/carryback
    prior_credit_carryforward = Column(Numeric(15, 2), default=0)
    credit_carryback_years = Column(Integer, default=0)
    credit_carryforward_years = Column(Integer, default=20)

    # CPA approval
    requires_cpa_approval = Column(Boolean, default=True)
    cpa_approved = Column(Boolean, default=False)
    cpa_approved_by = Column(PGUUID(as_uuid=True), nullable=True)
    cpa_approved_at = Column(DateTime(timezone=True), nullable=True)
    cpa_approval_notes = Column(Text, nullable=True)

    # Risk flags
    risk_flags = Column(JSONB, default=list)
    has_open_flags = Column(Boolean, default=False)

    # Rules version used
    rules_version = Column(String(20), nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    assumptions = Column(JSONB, default=list)
    limitations = Column(JSONB, default=list)

    # Audit trail
    created_by = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    locked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    projects = relationship("RDProject", back_populates="study", cascade="all, delete-orphan")
    employees = relationship("RDEmployee", back_populates="study", cascade="all, delete-orphan")
    qres = relationship("QualifiedResearchExpense", back_populates="study", cascade="all, delete-orphan")
    calculations = relationship("RDCalculation", back_populates="study", cascade="all, delete-orphan")
    state_credits = relationship("StateCredit", back_populates="study", cascade="all, delete-orphan")
    documents = relationship("RDDocument", back_populates="study", cascade="all, delete-orphan")
    interviews = relationship("RDInterview", back_populates="study", cascade="all, delete-orphan")
    narratives = relationship("RDNarrative", back_populates="study", cascade="all, delete-orphan")
    audit_logs = relationship("RDAuditLog", back_populates="study", cascade="all, delete-orphan")
    team_members = relationship("RDStudyTeamMember", back_populates="study", cascade="all, delete-orphan")


class RDProject(Base):
    """
    R&D project within a study.

    Represents a specific research activity being evaluated
    against the Federal 4-part test and state overlays.
    """
    __tablename__ = "rd_projects"
    __table_args__ = (
        Index("ix_rd_projects_study", "study_id"),
        Index("ix_rd_projects_qualification", "qualification_status"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)

    # Project identification
    name = Column(String(500), nullable=False)
    code = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    department = Column(String(200), nullable=True)
    business_component = Column(String(500), nullable=True)

    # Project dates
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_ongoing = Column(Boolean, default=True)

    # Qualification status
    qualification_status = Column(SQLEnum(QualificationStatus), default=QualificationStatus.PENDING)

    # Federal 4-part test evaluation
    permitted_purpose_score = Column(Float, nullable=True)  # 0-100
    permitted_purpose_evidence = Column(JSONB, default=list)
    permitted_purpose_narrative = Column(Text, nullable=True)

    technological_nature_score = Column(Float, nullable=True)
    technological_nature_evidence = Column(JSONB, default=list)
    technological_nature_narrative = Column(Text, nullable=True)

    uncertainty_score = Column(Float, nullable=True)
    uncertainty_evidence = Column(JSONB, default=list)
    uncertainty_narrative = Column(Text, nullable=True)

    experimentation_score = Column(Float, nullable=True)
    experimentation_evidence = Column(JSONB, default=list)
    experimentation_narrative = Column(Text, nullable=True)

    # Overall qualification
    overall_score = Column(Float, nullable=True)
    overall_confidence = Column(SQLEnum(ConfidenceLevel), nullable=True)
    qualification_narrative = Column(Text, nullable=True)

    # AI analysis
    ai_qualification_analysis = Column(JSONB, default=dict)
    ai_suggested_evidence = Column(JSONB, default=list)
    ai_risk_factors = Column(JSONB, default=list)

    # State-specific qualification
    state_qualifications = Column(JSONB, default=dict)  # {state_code: {qualified: bool, notes: str}}

    # CPA review
    cpa_reviewed = Column(Boolean, default=False)
    cpa_reviewed_by = Column(PGUUID(as_uuid=True), nullable=True)
    cpa_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    cpa_override_status = Column(SQLEnum(QualificationStatus), nullable=True)
    cpa_override_reason = Column(Text, nullable=True)

    # Risk flags
    risk_flags = Column(JSONB, default=list)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    study = relationship("RDStudy", back_populates="projects")
    qres = relationship("QualifiedResearchExpense", back_populates="project")
    evidence_items = relationship("RDEvidence", back_populates="project", cascade="all, delete-orphan")
    employee_allocations = relationship("ProjectEmployeeAllocation", back_populates="project", cascade="all, delete-orphan")


class RDEmployee(Base):
    """
    Employee involved in R&D activities.

    Tracks employee information, roles, and qualified time percentages.
    """
    __tablename__ = "rd_employees"
    __table_args__ = (
        Index("ix_rd_employees_study", "study_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)

    # Employee identification
    employee_id = Column(String(100), nullable=True)  # Client's internal ID
    name = Column(String(300), nullable=False)
    title = Column(String(200), nullable=True)
    department = Column(String(200), nullable=True)
    hire_date = Column(Date, nullable=True)
    termination_date = Column(Date, nullable=True)

    # Compensation
    total_wages = Column(Numeric(15, 2), default=0)
    w2_wages = Column(Numeric(15, 2), default=0)
    bonus = Column(Numeric(15, 2), default=0)
    stock_compensation = Column(Numeric(15, 2), default=0)  # Generally not QRE

    # Qualified time analysis
    qualified_time_percentage = Column(Float, default=0)  # 0-100
    qualified_time_source = Column(String(100), nullable=True)  # timesheet, estimate, interview
    qualified_time_confidence = Column(SQLEnum(ConfidenceLevel), nullable=True)

    # Qualified wages
    qualified_wages = Column(Numeric(15, 2), default=0)

    # Role categorization for narrative
    role_category = Column(String(100), nullable=True)  # engineer, scientist, technician, support, supervisor
    rd_role_description = Column(Text, nullable=True)  # AI-generated R&D-relevant role description

    # Employee narrative
    employee_narrative = Column(Text, nullable=True)  # AI-generated narrative
    narrative_confidence = Column(Float, nullable=True)

    # AI analysis
    ai_time_inference = Column(JSONB, default=dict)  # From timesheets, artifacts, interviews
    ai_role_analysis = Column(JSONB, default=dict)

    # Evidence links
    evidence_sources = Column(JSONB, default=list)  # Document IDs, interview IDs

    # CPA review
    cpa_reviewed = Column(Boolean, default=False)
    cpa_adjusted_percentage = Column(Float, nullable=True)
    cpa_adjustment_reason = Column(Text, nullable=True)

    # Risk flags
    risk_flags = Column(JSONB, default=list)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    study = relationship("RDStudy", back_populates="employees")
    project_allocations = relationship("ProjectEmployeeAllocation", back_populates="employee", cascade="all, delete-orphan")
    qres = relationship("QualifiedResearchExpense", back_populates="employee")


class ProjectEmployeeAllocation(Base):
    """
    Allocation of employee time to specific projects.
    """
    __tablename__ = "rd_project_employee_allocations"
    __table_args__ = (
        UniqueConstraint("project_id", "employee_id", name="uq_project_employee"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_projects.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_employees.id", ondelete="CASCADE"), nullable=False)

    # Allocation
    allocation_percentage = Column(Float, nullable=False)  # % of qualified time on this project
    allocated_wages = Column(Numeric(15, 2), default=0)

    # Evidence
    source = Column(String(100), nullable=True)  # timesheet, estimate, interview
    evidence_ids = Column(JSONB, default=list)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("RDProject", back_populates="employee_allocations")
    employee = relationship("RDEmployee", back_populates="project_allocations")


class QualifiedResearchExpense(Base):
    """
    Individual Qualified Research Expense (QRE) record.

    Represents a specific expense item that qualifies for the R&D credit.
    """
    __tablename__ = "rd_qres"
    __table_args__ = (
        Index("ix_rd_qres_study", "study_id"),
        Index("ix_rd_qres_project", "project_id"),
        Index("ix_rd_qres_category", "category"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_projects.id", ondelete="SET NULL"), nullable=True)
    employee_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_employees.id", ondelete="SET NULL"), nullable=True)

    # QRE category
    category = Column(SQLEnum(QRECategory), nullable=False)
    subcategory = Column(String(100), nullable=True)

    # For wages
    is_w2_wages = Column(Boolean, default=True)

    # For supplies
    supply_description = Column(String(500), nullable=True)
    supply_vendor = Column(String(300), nullable=True)
    gl_account = Column(String(100), nullable=True)

    # For contract research
    contractor_name = Column(String(300), nullable=True)
    contractor_ein = Column(String(20), nullable=True)
    is_qualified_research_org = Column(Boolean, default=False)
    contract_percentage = Column(Float, default=65)  # 65% or 75% for qualified orgs

    # Amounts
    gross_amount = Column(Numeric(15, 2), nullable=False)
    qualified_percentage = Column(Float, default=100)  # % that qualifies
    qualified_amount = Column(Numeric(15, 2), nullable=False)

    # State allocation
    state_allocation = Column(JSONB, default=dict)  # {state_code: amount}

    # Evidence and source
    source_document_id = Column(PGUUID(as_uuid=True), nullable=True)
    source_reference = Column(String(500), nullable=True)  # GL line, invoice #, etc.
    evidence_ids = Column(JSONB, default=list)

    # AI analysis
    ai_confidence = Column(Float, nullable=True)
    ai_classification_reason = Column(Text, nullable=True)

    # CPA review
    cpa_reviewed = Column(Boolean, default=False)
    cpa_adjusted_amount = Column(Numeric(15, 2), nullable=True)
    cpa_adjustment_reason = Column(Text, nullable=True)

    # Risk flags
    risk_flags = Column(JSONB, default=list)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    study = relationship("RDStudy", back_populates="qres")
    project = relationship("RDProject", back_populates="qres")
    employee = relationship("RDEmployee", back_populates="qres")


class RDCalculation(Base):
    """
    R&D credit calculation record.

    Stores detailed calculation results with full audit trail.
    """
    __tablename__ = "rd_calculations"
    __table_args__ = (
        Index("ix_rd_calculations_study", "study_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)

    # Calculation type
    calculation_type = Column(String(50), nullable=False)  # federal_regular, federal_asc, state_{code}
    method = Column(SQLEnum(CreditMethod), nullable=True)
    is_final = Column(Boolean, default=False)

    # Input values
    total_qre_wages = Column(Numeric(15, 2), default=0)
    total_qre_supplies = Column(Numeric(15, 2), default=0)
    total_qre_contract = Column(Numeric(15, 2), default=0)
    total_qre_basic_research = Column(Numeric(15, 2), default=0)
    total_qre = Column(Numeric(15, 2), default=0)

    # Base period data (for Regular method)
    base_period_data = Column(JSONB, default=dict)  # {year: {qre: amount, gross_receipts: amount}}
    base_amount = Column(Numeric(15, 2), default=0)
    fixed_base_percentage = Column(Float, nullable=True)
    average_annual_gross_receipts = Column(Numeric(15, 2), nullable=True)

    # Credit calculation
    credit_rate = Column(Float, nullable=False)
    excess_qre = Column(Numeric(15, 2), default=0)
    calculated_credit = Column(Numeric(15, 2), default=0)

    # Adjustments
    section_280c_reduction = Column(Numeric(15, 2), default=0)  # 280C(c) election
    controlled_group_allocation = Column(Float, default=100)  # % allocated to this entity
    final_credit = Column(Numeric(15, 2), default=0)

    # Payroll tax offset (for qualified small business)
    is_qualified_small_business = Column(Boolean, default=False)
    payroll_tax_offset_amount = Column(Numeric(15, 2), default=0)

    # Calculation steps (full audit trail)
    calculation_steps = Column(JSONB, default=list)  # [{step, formula, inputs, result}]

    # Comparison data
    alternative_credit = Column(Numeric(15, 2), nullable=True)  # Credit under alternative method
    credit_difference = Column(Numeric(15, 2), nullable=True)
    recommended_method = Column(SQLEnum(CreditMethod), nullable=True)

    # Metadata
    rules_version = Column(String(20), nullable=True)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    calculated_by = Column(PGUUID(as_uuid=True), nullable=True)

    # Relationships
    study = relationship("RDStudy", back_populates="calculations")


class StateCredit(Base):
    """
    State R&D credit calculation.

    Handles state-specific rules, rates, and calculations.
    """
    __tablename__ = "rd_state_credits"
    __table_args__ = (
        Index("ix_rd_state_credits_study", "study_id"),
        UniqueConstraint("study_id", "state_code", name="uq_study_state"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)

    # State identification
    state_code = Column(String(2), nullable=False)
    state_name = Column(String(100), nullable=False)

    # State rules applied
    rules_version = Column(String(20), nullable=True)
    rules_reference = Column(String(200), nullable=True)  # Citation

    # State-specific QRE
    state_qre_wages = Column(Numeric(15, 2), default=0)
    state_qre_supplies = Column(Numeric(15, 2), default=0)
    state_qre_contract = Column(Numeric(15, 2), default=0)
    state_qre_other = Column(Numeric(15, 2), default=0)  # State-specific categories
    state_total_qre = Column(Numeric(15, 2), default=0)

    # State calculation
    state_credit_rate = Column(Float, nullable=True)
    state_base_amount = Column(Numeric(15, 2), default=0)
    state_excess_qre = Column(Numeric(15, 2), default=0)
    calculated_credit = Column(Numeric(15, 2), default=0)

    # State-specific adjustments
    state_adjustments = Column(JSONB, default=dict)
    final_credit = Column(Numeric(15, 2), default=0)

    # Carryforward/limitations
    state_credit_cap = Column(Numeric(15, 2), nullable=True)
    carryforward_years = Column(Integer, nullable=True)
    prior_carryforward = Column(Numeric(15, 2), default=0)

    # Calculation details
    calculation_steps = Column(JSONB, default=list)
    state_specific_notes = Column(Text, nullable=True)

    # Metadata
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    study = relationship("RDStudy", back_populates="state_credits")


class RDDocument(Base):
    """
    Uploaded document for R&D study.

    Tracks all documents with OCR results, classification, and extraction.
    """
    __tablename__ = "rd_documents"
    __table_args__ = (
        Index("ix_rd_documents_study", "study_id"),
        Index("ix_rd_documents_type", "document_type"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)

    # Document info
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    document_type = Column(SQLEnum(DocumentType), nullable=True)

    # Storage
    storage_path = Column(String(1000), nullable=False)
    storage_bucket = Column(String(200), nullable=True)

    # Processing status
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)

    # OCR results
    ocr_completed = Column(Boolean, default=False)
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)

    # AI classification
    ai_document_type = Column(SQLEnum(DocumentType), nullable=True)
    ai_classification_confidence = Column(Float, nullable=True)
    ai_extracted_data = Column(JSONB, default=dict)

    # Table extraction
    extracted_tables = Column(JSONB, default=list)  # [{table_id, headers, rows}]

    # Entity resolution
    identified_employees = Column(JSONB, default=list)
    identified_projects = Column(JSONB, default=list)
    identified_vendors = Column(JSONB, default=list)

    # Normalization results
    normalized_data = Column(JSONB, default=dict)

    # Missing data detection
    missing_fields = Column(JSONB, default=list)
    follow_up_questions = Column(JSONB, default=list)

    # Metadata
    uploaded_by = Column(PGUUID(as_uuid=True), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    study = relationship("RDStudy", back_populates="documents")


class RDInterview(Base):
    """
    AI interview session for R&D study.

    Records interview transcripts and extracted information.
    """
    __tablename__ = "rd_interviews"
    __table_args__ = (
        Index("ix_rd_interviews_study", "study_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)

    # Interview info
    interview_type = Column(String(100), nullable=False)  # employee, project_lead, management, technical
    interviewee_name = Column(String(300), nullable=True)
    interviewee_title = Column(String(200), nullable=True)
    interviewee_employee_id = Column(PGUUID(as_uuid=True), nullable=True)

    # Interview status
    status = Column(String(50), default="scheduled")  # scheduled, in_progress, completed, cancelled
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # AI interview bot
    interview_mode = Column(String(50), default="ai_assisted")  # ai_assisted, manual
    ai_questions_generated = Column(JSONB, default=list)
    ai_follow_up_questions = Column(JSONB, default=list)

    # Transcript
    transcript = Column(JSONB, default=list)  # [{role, content, timestamp}]
    summary = Column(Text, nullable=True)

    # Extracted information
    extracted_projects = Column(JSONB, default=list)
    extracted_activities = Column(JSONB, default=list)
    extracted_time_allocations = Column(JSONB, default=list)
    extracted_uncertainties = Column(JSONB, default=list)
    extracted_experiments = Column(JSONB, default=list)

    # Confidence and flags
    overall_confidence = Column(Float, nullable=True)
    needs_follow_up = Column(Boolean, default=False)
    follow_up_topics = Column(JSONB, default=list)

    # Metadata
    conducted_by = Column(PGUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    study = relationship("RDStudy", back_populates="interviews")


class RDNarrative(Base):
    """
    Generated narrative for R&D study.

    AI-generated narratives with evidence citations.
    """
    __tablename__ = "rd_narratives"
    __table_args__ = (
        Index("ix_rd_narratives_study", "study_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)

    # Narrative type
    narrative_type = Column(String(100), nullable=False)  # executive_summary, project, employee, qualification, qre_schedule
    entity_id = Column(PGUUID(as_uuid=True), nullable=True)  # project_id or employee_id
    entity_type = Column(String(50), nullable=True)  # project, employee, study

    # Content
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)

    # Evidence links
    evidence_citations = Column(JSONB, default=list)  # [{citation_id, text, source_type, source_id}]
    supporting_documents = Column(JSONB, default=list)

    # AI generation
    ai_generated = Column(Boolean, default=True)
    ai_model = Column(String(100), nullable=True)
    ai_prompt_version = Column(String(50), nullable=True)
    ai_confidence = Column(Float, nullable=True)

    # Review status
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(PGUUID(as_uuid=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # CPA edits
    cpa_edited = Column(Boolean, default=False)
    cpa_edited_content = Column(Text, nullable=True)
    cpa_edit_reason = Column(Text, nullable=True)

    # Version control
    version = Column(Integer, default=1)
    previous_version_id = Column(PGUUID(as_uuid=True), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    study = relationship("RDStudy", back_populates="narratives")


class RDEvidence(Base):
    """
    Evidence item linked to qualification assertions.
    """
    __tablename__ = "rd_evidence"
    __table_args__ = (
        Index("ix_rd_evidence_project", "project_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_projects.id", ondelete="CASCADE"), nullable=False)

    # Evidence info
    evidence_type = Column(String(100), nullable=False)  # document, interview, artifact, external
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Source
    source_document_id = Column(PGUUID(as_uuid=True), nullable=True)
    source_interview_id = Column(PGUUID(as_uuid=True), nullable=True)
    external_url = Column(String(1000), nullable=True)

    # Location in source
    source_page = Column(Integer, nullable=True)
    source_section = Column(String(200), nullable=True)
    source_excerpt = Column(Text, nullable=True)

    # Relevance to 4-part test
    relevant_to_permitted_purpose = Column(Boolean, default=False)
    relevant_to_technological_nature = Column(Boolean, default=False)
    relevant_to_uncertainty = Column(Boolean, default=False)
    relevant_to_experimentation = Column(Boolean, default=False)

    # Strength
    evidence_strength = Column(SQLEnum(ConfidenceLevel), nullable=True)
    ai_relevance_score = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("RDProject", back_populates="evidence_items")


class RDAuditLog(Base):
    """
    Audit log for all study actions.

    Provides complete audit trail for compliance.
    """
    __tablename__ = "rd_audit_logs"
    __table_args__ = (
        Index("ix_rd_audit_logs_study", "study_id"),
        Index("ix_rd_audit_logs_timestamp", "created_at"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)

    # Action info
    action = Column(String(100), nullable=False)  # create, update, delete, approve, reject, calculate, generate
    entity_type = Column(String(100), nullable=False)  # study, project, employee, qre, calculation, document
    entity_id = Column(PGUUID(as_uuid=True), nullable=True)

    # Change details
    previous_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    change_summary = Column(Text, nullable=True)

    # User info
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    user_email = Column(String(300), nullable=True)
    user_role = Column(String(100), nullable=True)

    # Context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    study = relationship("RDStudy", back_populates="audit_logs")


class RDStudyTeamMember(Base):
    """
    Team member assigned to R&D study.
    """
    __tablename__ = "rd_study_team_members"
    __table_args__ = (
        UniqueConstraint("study_id", "user_id", name="uq_study_team_member"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Role
    role = Column(SQLEnum(UserRole), nullable=False)
    can_approve = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=True)
    can_view = Column(Boolean, default=True)

    # Assignment
    assigned_by = Column(PGUUID(as_uuid=True), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    study = relationship("RDStudy", back_populates="team_members")


class RDOutputFile(Base):
    """
    Generated output file (PDF, Excel, Form 6765).
    """
    __tablename__ = "rd_output_files"
    __table_args__ = (
        Index("ix_rd_output_files_study", "study_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    study_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.rd_studies.id", ondelete="CASCADE"), nullable=False)

    # File info
    file_type = Column(String(50), nullable=False)  # pdf_study, excel_workbook, form_6765, state_form
    filename = Column(String(500), nullable=False)
    storage_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=True)

    # Version
    version = Column(Integer, default=1)
    is_final = Column(Boolean, default=False)

    # Generation
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    generated_by = Column(PGUUID(as_uuid=True), nullable=True)
    generation_parameters = Column(JSONB, default=dict)

    # Content hash for integrity
    content_hash = Column(String(64), nullable=True)

    # File content (for demo/testing - in production use blob storage)
    file_content = Column(LargeBinary, nullable=True)


class RDRulesConfig(Base):
    """
    Versioned rules configuration for R&D credits.
    """
    __tablename__ = "rd_rules_config"
    __table_args__ = (
        UniqueConstraint("version", "jurisdiction", name="uq_rules_version_jurisdiction"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Version info
    version = Column(String(20), nullable=False)
    jurisdiction = Column(String(10), nullable=False)  # federal, CA, TX, etc.
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=True)

    # Rules content
    rules_json = Column(JSONB, nullable=False)
    rules_hash = Column(String(64), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    notes = Column(Text, nullable=True)
    citation = Column(Text, nullable=True)

    # Active flag
    is_active = Column(Boolean, default=True)
