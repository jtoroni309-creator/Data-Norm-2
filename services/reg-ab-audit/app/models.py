"""
SQLAlchemy Models for Regulation A/B Audit Service
"""

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SQLEnum, ForeignKey,
    Integer, Numeric, String, Text, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ========================================
# Enums
# ========================================

class RegABAuditStatus(str, enum.Enum):
    DRAFT = "draft"
    CLIENT_INPUT = "client_input"
    AI_PROCESSING = "ai_processing"
    WORKPAPER_GENERATION = "workpaper_generation"
    CPA_REVIEW = "cpa_review"
    REVISION_REQUIRED = "revision_required"
    CPA_APPROVED = "cpa_approved"
    FINALIZED = "finalized"


class CMBSDealStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_AUDIT = "pending_audit"
    AUDIT_COMPLETE = "audit_complete"


class WorkpaperStatus(str, enum.Enum):
    DRAFT = "draft"
    AI_GENERATED = "ai_generated"
    IN_REVIEW = "in_review"
    REVISION_REQUIRED = "revision_required"
    APPROVED = "approved"


class ComplianceStandard(str, enum.Enum):
    PCAOB = "PCAOB"
    GAAP = "GAAP"
    GAAS = "GAAS"
    SEC = "SEC"
    AICPA = "AICPA"


class ComplianceCheckStatus(str, enum.Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"


class SignoffStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"


# ========================================
# Feature Flag Model
# ========================================

class RegABFeatureFlag(Base):
    __tablename__ = "reg_ab_feature_flags"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(PGUUID(as_uuid=True), nullable=False, unique=True)

    # Feature toggles
    is_enabled = Column(Boolean, nullable=False, default=False)
    allow_client_portal = Column(Boolean, nullable=False, default=True)
    allow_cpa_portal = Column(Boolean, nullable=False, default=True)
    auto_workpaper_generation = Column(Boolean, nullable=False, default=True)
    auto_report_generation = Column(Boolean, nullable=False, default=True)
    ai_compliance_checking = Column(Boolean, nullable=False, default=True)

    # AI Configuration
    ai_model_version = Column(String, default="gpt-4-turbo")
    compliance_check_level = Column(String, default="comprehensive")

    # Notification settings
    notify_on_completion = Column(Boolean, nullable=False, default=True)
    notify_cpa_on_ready = Column(Boolean, nullable=False, default=True)
    notify_client_on_approval = Column(Boolean, nullable=False, default=True)
    notification_email = Column(String)

    # Audit settings
    require_dual_signoff = Column(Boolean, nullable=False, default=False)
    retention_years = Column(Integer, nullable=False, default=7)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    enabled_at = Column(DateTime)
    enabled_by = Column(PGUUID(as_uuid=True))


# ========================================
# Audit Engagement Model
# ========================================

class RegABAuditEngagement(Base):
    __tablename__ = "reg_ab_audit_engagements"
    __table_args__ = (
        Index("idx_reg_ab_engagements_org", "organization_id"),
        Index("idx_reg_ab_engagements_status", "status"),
        Index("idx_reg_ab_engagements_cpa", "assigned_cpa_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=False)
    organization_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Engagement details
    audit_name = Column(String, nullable=False)
    audit_period_start = Column(Date, nullable=False)
    audit_period_end = Column(Date, nullable=False)
    status = Column(SQLEnum(RegABAuditStatus), nullable=False, default=RegABAuditStatus.DRAFT)

    # Client information
    client_contact_id = Column(PGUUID(as_uuid=True))
    client_organization_id = Column(PGUUID(as_uuid=True), nullable=False)

    # CPA assignment
    assigned_cpa_id = Column(PGUUID(as_uuid=True))
    secondary_reviewer_id = Column(PGUUID(as_uuid=True))

    # AI processing metadata
    ai_processing_started_at = Column(DateTime)
    ai_processing_completed_at = Column(DateTime)
    ai_processing_duration_seconds = Column(Integer)
    ai_confidence_score = Column(Numeric(5, 4))

    # Progress tracking
    total_cmbs_deals = Column(Integer, default=0)
    processed_deals = Column(Integer, default=0)
    total_workpapers = Column(Integer, default=0)
    approved_workpapers = Column(Integer, default=0)
    total_compliance_checks = Column(Integer, default=0)
    passed_compliance_checks = Column(Integer, default=0)
    failed_compliance_checks = Column(Integer, default=0)

    # Report information
    report_generated_at = Column(DateTime)
    report_url = Column(Text)
    report_hash = Column(String)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_for_review_at = Column(DateTime)
    reviewed_at = Column(DateTime)
    finalized_at = Column(DateTime)

    # Soft delete
    deleted_at = Column(DateTime)


# ========================================
# CMBS Deal Model
# ========================================

class CMBSDeal(Base):
    __tablename__ = "cmbs_deals"
    __table_args__ = (
        Index("idx_cmbs_deals_engagement", "audit_engagement_id"),
        Index("idx_cmbs_deals_status", "status"),
        UniqueConstraint("audit_engagement_id", "deal_number"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_engagement_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Deal identification
    deal_name = Column(String, nullable=False)
    deal_number = Column(String, nullable=False)
    cusip = Column(String)
    bloomberg_id = Column(String)

    # Deal details
    origination_date = Column(Date, nullable=False)
    maturity_date = Column(Date)
    original_balance = Column(Numeric(20, 2), nullable=False)
    current_balance = Column(Numeric(20, 2), nullable=False)
    interest_rate = Column(Numeric(7, 4))

    # Operating Advisor (OA) information
    is_oa = Column(Boolean, nullable=False, default=True)
    oa_appointment_date = Column(Date)

    # Property information
    property_type = Column(String)
    property_address = Column(JSONB)
    property_count = Column(Integer)

    # Servicer information
    master_servicer = Column(String)
    special_servicer = Column(String)
    trustee = Column(String)

    # Performance metrics
    dscr = Column(Numeric(7, 4))  # Debt Service Coverage Ratio
    ltv = Column(Numeric(7, 4))   # Loan-to-Value
    occupancy_rate = Column(Numeric(5, 2))
    delinquency_status = Column(String)

    # Additional data
    status = Column(SQLEnum(CMBSDealStatus), nullable=False, default=CMBSDealStatus.PENDING_AUDIT)
    metadata = Column(JSONB)
    documents = Column(JSONB)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime)
    submitted_by = Column(PGUUID(as_uuid=True))


# ========================================
# Compliance Check Model
# ========================================

class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"
    __table_args__ = (
        Index("idx_compliance_checks_engagement", "audit_engagement_id"),
        Index("idx_compliance_checks_deal", "cmbs_deal_id"),
        Index("idx_compliance_checks_standard", "standard"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_engagement_id = Column(PGUUID(as_uuid=True), nullable=False)
    cmbs_deal_id = Column(PGUUID(as_uuid=True))

    # Check details
    check_name = Column(String, nullable=False)
    check_code = Column(String, nullable=False)
    standard = Column(SQLEnum(ComplianceStandard), nullable=False)
    standard_reference = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    # Check execution
    status = Column(SQLEnum(ComplianceCheckStatus), nullable=False, default=ComplianceCheckStatus.PENDING)
    executed_at = Column(DateTime)
    execution_duration_ms = Column(Integer)

    # AI analysis
    ai_analysis = Column(JSONB)
    ai_confidence = Column(Numeric(5, 4))
    risk_level = Column(String)

    # Results
    passed = Column(Boolean)
    findings = Column(Text)
    recommendation = Column(Text)
    remediation_steps = Column(JSONB)

    # Evidence
    evidence_references = Column(JSONB)
    data_points_analyzed = Column(JSONB)

    # Manual review
    requires_manual_review = Column(Boolean, default=False)
    manual_review_notes = Column(Text)
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# ========================================
# Workpaper Model
# ========================================

class RegABWorkpaper(Base):
    __tablename__ = "reg_ab_workpapers"
    __table_args__ = (
        Index("idx_workpapers_engagement", "audit_engagement_id"),
        Index("idx_workpapers_deal", "cmbs_deal_id"),
        Index("idx_workpapers_status", "status"),
        UniqueConstraint("audit_engagement_id", "workpaper_ref", "version"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_engagement_id = Column(PGUUID(as_uuid=True), nullable=False)
    cmbs_deal_id = Column(PGUUID(as_uuid=True))

    # Workpaper details
    workpaper_ref = Column(String, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text)

    # Content
    content = Column(JSONB, nullable=False)
    content_html = Column(Text)
    content_url = Column(String)

    # Status
    status = Column(SQLEnum(WorkpaperStatus), nullable=False, default=WorkpaperStatus.DRAFT)
    version = Column(Integer, nullable=False, default=1)

    # AI generation metadata
    ai_generated = Column(Boolean, nullable=False, default=False)
    ai_model_version = Column(String)
    ai_prompt_used = Column(Text)
    ai_generation_confidence = Column(Numeric(5, 4))
    ai_generation_timestamp = Column(DateTime)

    # CPA review
    reviewer_id = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
    revision_count = Column(Integer, default=0)

    # Compliance linkage
    compliance_checks = Column(JSONB)

    # Supporting documents
    source_documents = Column(JSONB)
    attachments = Column(JSONB)

    # Audit trail
    created_by = Column(PGUUID(as_uuid=True))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime)
    approved_by = Column(PGUUID(as_uuid=True))

    # Immutability
    locked = Column(Boolean, default=False)
    locked_at = Column(DateTime)
    content_hash = Column(String)


# ========================================
# Audit Report Model
# ========================================

class RegABAuditReport(Base):
    __tablename__ = "reg_ab_audit_reports"
    __table_args__ = (
        Index("idx_reports_engagement", "audit_engagement_id"),
        UniqueConstraint("audit_engagement_id", "version"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_engagement_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Report details
    report_type = Column(String, nullable=False, default="Regulation AB Compilation Report")
    report_period_start = Column(Date, nullable=False)
    report_period_end = Column(Date, nullable=False)
    version = Column(Integer, nullable=False, default=1)

    # Content
    executive_summary = Column(Text)
    findings_summary = Column(JSONB)
    content = Column(JSONB, nullable=False)
    content_html = Column(Text)
    content_pdf_url = Column(String)

    # Statistics
    total_deals_audited = Column(Integer, nullable=False)
    total_compliance_checks = Column(Integer, nullable=False)
    passed_checks = Column(Integer, nullable=False)
    failed_checks = Column(Integer, nullable=False)
    total_workpapers = Column(Integer, nullable=False)

    # AI generation
    ai_generated = Column(Boolean, nullable=False, default=False)
    ai_model_version = Column(String)
    ai_generation_timestamp = Column(DateTime)
    ai_confidence_score = Column(Numeric(5, 4))

    # Status
    draft = Column(Boolean, nullable=False, default=True)

    # Timestamps
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Immutability
    content_hash = Column(String)


# ========================================
# CPA Sign-off Model
# ========================================

class CPASignoff(Base):
    __tablename__ = "cpa_signoffs"
    __table_args__ = (
        Index("idx_signoffs_engagement", "audit_engagement_id"),
        Index("idx_signoffs_report", "report_id"),
        Index("idx_signoffs_cpa", "cpa_user_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_engagement_id = Column(PGUUID(as_uuid=True), nullable=False)
    report_id = Column(PGUUID(as_uuid=True), nullable=False)

    # CPA information
    cpa_user_id = Column(PGUUID(as_uuid=True), nullable=False)
    cpa_license_number = Column(String, nullable=False)
    cpa_license_state = Column(String, nullable=False)
    cpa_license_expiry = Column(Date)

    # Sign-off details
    status = Column(SQLEnum(SignoffStatus), nullable=False, default=SignoffStatus.PENDING)
    signoff_type = Column(String, nullable=False, default="final_approval")

    # Digital signature
    signature_timestamp = Column(DateTime)
    signature_ip_address = Column(INET)
    signature_method = Column(String, default="electronic")
    signature_certificate = Column(Text)
    signature_hash = Column(String)

    # Review details
    review_started_at = Column(DateTime)
    review_completed_at = Column(DateTime)
    review_duration_minutes = Column(Integer)
    review_notes = Column(Text)

    # Approval/Rejection
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    rejection_reason = Column(Text)
    revision_requests = Column(JSONB)

    # Revocation
    revoked_at = Column(DateTime)
    revoked_by = Column(PGUUID(as_uuid=True))
    revocation_reason = Column(Text)

    # Compliance attestation
    attestation_text = Column(Text)
    attestation_confirmed = Column(Boolean, default=False)
    attestation_timestamp = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
