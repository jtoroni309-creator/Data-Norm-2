"""SQLAlchemy ORM models for Reporting Service"""
from datetime import datetime
from uuid import uuid4
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    ForeignKey,
    Text,
    Boolean,
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

class ReportType(str, Enum):
    """Type of report"""
    AUDIT_REPORT = "audit_report"
    FINANCIAL_STATEMENT = "financial_statement"
    MANAGEMENT_LETTER = "management_letter"
    INTERNAL_CONTROL = "internal_control"
    WORKPAPER_SUMMARY = "workpaper_summary"
    ANALYTICS_SUMMARY = "analytics_summary"
    QC_REVIEW = "qc_review"
    ENGAGEMENT_SUMMARY = "engagement_summary"
    CUSTOM = "custom"


class ReportStatus(str, Enum):
    """Status of report generation"""
    DRAFT = "draft"
    GENERATING = "generating"
    GENERATED = "generated"
    REVIEW = "review"
    APPROVED = "approved"
    SIGNED = "signed"
    FINALIZED = "finalized"
    FAILED = "failed"


class SignatureStatus(str, Enum):
    """Status of e-signature"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    SIGNED = "signed"
    COMPLETED = "completed"
    DECLINED = "declined"
    VOIDED = "voided"
    EXPIRED = "expired"


class TemplateType(str, Enum):
    """Type of report template"""
    SYSTEM = "system"  # Built-in templates
    CUSTOM = "custom"  # User-created templates
    FIRM = "firm"      # Firm-wide templates


# ========================================
# ORM Models
# ========================================

class ReportTemplate(Base):
    """
    Report template definition

    Stores reusable templates for different report types.
    Templates use Jinja2 for dynamic content rendering.
    """
    __tablename__ = "report_templates"
    __table_args__ = (
        Index("idx_template_type", "template_type"),
        Index("idx_template_report_type", "report_type"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    template_type = Column(
        SQLEnum(TemplateType, name="template_type", create_type=False),
        nullable=False,
        default=TemplateType.CUSTOM
    )
    report_type = Column(
        SQLEnum(ReportType, name="report_type", create_type=False),
        nullable=False
    )

    # Template content (Jinja2 HTML)
    html_content = Column(Text, nullable=False)

    # CSS styles
    css_content = Column(Text)

    # Template configuration
    config = Column(JSONB)  # Page size, orientation, margins, etc.

    # Header/Footer templates
    header_template = Column(Text)
    footer_template = Column(Text)

    # Template metadata
    version = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)

    # Audit fields
    created_by = Column(PGUUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    reports = relationship("Report", back_populates="template")


class Report(Base):
    """
    Generated report

    Stores information about generated reports including PDF location,
    metadata, and e-signature status.
    """
    __tablename__ = "reports"
    __table_args__ = (
        Index("idx_report_engagement", "engagement_id"),
        Index("idx_report_type", "report_type"),
        Index("idx_report_status", "status"),
        Index("idx_report_created", "created_at"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Report details
    report_type = Column(
        SQLEnum(ReportType, name="report_type", create_type=False),
        nullable=False
    )
    title = Column(String, nullable=False)
    description = Column(Text)

    # Template used
    template_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.report_templates.id")
    )

    # Report data (JSON that was used to generate report)
    report_data = Column(JSONB, nullable=False)

    # Status
    status = Column(
        SQLEnum(ReportStatus, name="report_status", create_type=False),
        nullable=False,
        default=ReportStatus.DRAFT
    )

    # File information
    file_name = Column(String)
    file_path = Column(String)  # S3/Azure path
    file_size = Column(Integer)  # Bytes
    file_hash = Column(String)  # SHA256 for integrity verification

    # WORM storage (immutable final version)
    worm_file_path = Column(String)  # Path in WORM storage after finalization
    finalized_at = Column(DateTime(timezone=True))

    # Version control
    version = Column(Integer, nullable=False, default=1)
    parent_report_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.reports.id"))

    # Metadata
    fiscal_year = Column(String)
    report_date = Column(DateTime(timezone=True))
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))

    # Generation metadata
    generation_started_at = Column(DateTime(timezone=True))
    generation_completed_at = Column(DateTime(timezone=True))
    generation_duration_ms = Column(Integer)
    generation_error = Column(Text)

    # Watermark
    has_watermark = Column(Boolean, nullable=False, default=True)
    watermark_text = Column(String)

    # Audit fields
    created_by = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Approval workflow
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    approved_by = Column(PGUUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))

    # Relationships
    template = relationship("ReportTemplate", back_populates="reports")
    sections = relationship("ReportSection", back_populates="report", cascade="all, delete-orphan")
    signatures = relationship("SignatureEnvelope", back_populates="report")
    parent_report = relationship("Report", remote_side=[id], backref="revisions")


class ReportSection(Base):
    """
    Individual sections within a report

    Allows for modular report generation and easier updates
    to specific sections.
    """
    __tablename__ = "report_sections"
    __table_args__ = (
        Index("idx_section_report", "report_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.reports.id"),
        nullable=False
    )

    # Section details
    section_name = Column(String, nullable=False)
    section_order = Column(Integer, nullable=False)
    section_title = Column(String)

    # Content
    html_content = Column(Text, nullable=False)
    data = Column(JSONB)  # Section-specific data

    # Metadata
    page_break_before = Column(Boolean, default=False)
    page_break_after = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    report = relationship("Report", back_populates="sections")


class SignatureEnvelope(Base):
    """
    E-signature envelope

    Tracks DocuSign envelopes for report signatures.
    Supports multiple signers with routing order.
    """
    __tablename__ = "signature_envelopes"
    __table_args__ = (
        Index("idx_envelope_report", "report_id"),
        Index("idx_envelope_status", "status"),
        Index("idx_envelope_docusign", "docusign_envelope_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.reports.id"),
        nullable=False
    )

    # DocuSign integration
    docusign_envelope_id = Column(String, unique=True)
    docusign_status = Column(String)

    # Envelope details
    subject = Column(String, nullable=False)
    message = Column(Text)

    # Status
    status = Column(
        SQLEnum(SignatureStatus, name="signature_status", create_type=False),
        nullable=False,
        default=SignatureStatus.PENDING
    )

    # Signers
    signers = Column(JSONB, nullable=False)  # List of signer details

    # Important dates
    sent_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    voided_at = Column(DateTime(timezone=True))
    voided_reason = Column(Text)

    # Signed document
    signed_document_path = Column(String)  # Path to signed PDF

    # Audit fields
    created_by = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    report = relationship("Report", back_populates="signatures")


class ReportSchedule(Base):
    """
    Scheduled report generation

    Allows for automated report generation on a schedule
    (e.g., monthly financial statements).
    """
    __tablename__ = "report_schedules"
    __table_args__ = (
        Index("idx_schedule_engagement", "engagement_id"),
        Index("idx_schedule_active", "is_active"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=False)
    template_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.report_templates.id"),
        nullable=False
    )

    # Schedule details
    name = Column(String, nullable=False)
    description = Column(Text)

    # Schedule configuration (cron expression)
    schedule_cron = Column(String, nullable=False)  # e.g., "0 0 1 * *" for monthly

    # Report configuration
    report_config = Column(JSONB)  # Dynamic data queries, parameters

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    last_run_at = Column(DateTime(timezone=True))
    last_run_status = Column(String)
    next_run_at = Column(DateTime(timezone=True))

    # Notification
    notify_on_completion = Column(Boolean, default=True)
    notification_emails = Column(JSONB)  # List of email addresses

    # Audit fields
    created_by = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
