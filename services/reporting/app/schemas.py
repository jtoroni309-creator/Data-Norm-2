"""Pydantic schemas for Reporting Service"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from .models import ReportType, ReportStatus, SignatureStatus, TemplateType


# ========================================
# Report Template Schemas
# ========================================

class ReportTemplateCreate(BaseModel):
    """Schema for creating report template"""
    name: str
    description: Optional[str] = None
    template_type: TemplateType = TemplateType.CUSTOM
    report_type: ReportType
    html_content: str
    css_content: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    header_template: Optional[str] = None
    footer_template: Optional[str] = None
    version: Optional[str] = None
    is_active: bool = True
    is_default: bool = False


class ReportTemplateUpdate(BaseModel):
    """Schema for updating report template"""
    name: Optional[str] = None
    description: Optional[str] = None
    html_content: Optional[str] = None
    css_content: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    header_template: Optional[str] = None
    footer_template: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class ReportTemplateResponse(BaseModel):
    """Schema for report template response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    template_type: TemplateType
    report_type: ReportType
    version: Optional[str] = None
    is_active: bool
    is_default: bool
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


# ========================================
# Report Schemas
# ========================================

class ReportCreate(BaseModel):
    """Schema for creating report"""
    engagement_id: UUID
    report_type: ReportType
    title: str
    description: Optional[str] = None
    template_id: Optional[UUID] = None
    report_data: Dict[str, Any]
    fiscal_year: Optional[str] = None
    report_date: Optional[datetime] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    has_watermark: bool = True
    watermark_text: Optional[str] = None


class ReportUpdate(BaseModel):
    """Schema for updating report"""
    title: Optional[str] = None
    description: Optional[str] = None
    report_data: Optional[Dict[str, Any]] = None
    status: Optional[ReportStatus] = None
    has_watermark: Optional[bool] = None
    watermark_text: Optional[str] = None


class ReportResponse(BaseModel):
    """Schema for report response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    engagement_id: UUID
    report_type: ReportType
    title: str
    description: Optional[str] = None
    template_id: Optional[UUID] = None
    status: ReportStatus
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    worm_file_path: Optional[str] = None
    finalized_at: Optional[datetime] = None
    version: int
    fiscal_year: Optional[str] = None
    report_date: Optional[datetime] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    has_watermark: bool
    watermark_text: Optional[str] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None


class ReportGenerateRequest(BaseModel):
    """Schema for report generation request"""
    report_id: UUID
    regenerate: bool = Field(False, description="Force regeneration even if already generated")


class ReportGenerateResponse(BaseModel):
    """Schema for report generation response"""
    report_id: UUID
    status: ReportStatus
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generation_duration_ms: Optional[int] = None
    message: str


# ========================================
# Report Section Schemas
# ========================================

class ReportSectionCreate(BaseModel):
    """Schema for creating report section"""
    section_name: str
    section_order: int
    section_title: Optional[str] = None
    html_content: str
    data: Optional[Dict[str, Any]] = None
    page_break_before: bool = False
    page_break_after: bool = False


class ReportSectionResponse(BaseModel):
    """Schema for report section response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    section_name: str
    section_order: int
    section_title: Optional[str] = None
    page_break_before: bool
    page_break_after: bool
    created_at: datetime


# ========================================
# E-Signature Schemas
# ========================================

class SignerInfo(BaseModel):
    """Schema for signer information"""
    name: str
    email: str
    routing_order: int = 1
    role: str = "signer"  # signer, cc, etc.
    client_user_id: Optional[str] = None


class SignatureEnvelopeCreate(BaseModel):
    """Schema for creating e-signature envelope"""
    report_id: UUID
    subject: str
    message: Optional[str] = None
    signers: List[SignerInfo]
    expires_in_days: int = Field(30, description="Days until envelope expires")
    send_immediately: bool = Field(True, description="Send envelope immediately")


class SignatureEnvelopeResponse(BaseModel):
    """Schema for e-signature envelope response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    docusign_envelope_id: Optional[str] = None
    subject: str
    message: Optional[str] = None
    status: SignatureStatus
    sent_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    signed_document_path: Optional[str] = None
    created_by: UUID
    created_at: datetime


class SignatureStatusUpdate(BaseModel):
    """Schema for signature status update (webhook)"""
    envelope_id: str
    status: str
    signer_email: Optional[str] = None
    signer_name: Optional[str] = None
    signed_at: Optional[datetime] = None
    declined_reason: Optional[str] = None


# ========================================
# Report Schedule Schemas
# ========================================

class ReportScheduleCreate(BaseModel):
    """Schema for creating report schedule"""
    engagement_id: UUID
    template_id: UUID
    name: str
    description: Optional[str] = None
    schedule_cron: str = Field(..., description="Cron expression for schedule")
    report_config: Optional[Dict[str, Any]] = None
    notify_on_completion: bool = True
    notification_emails: Optional[List[str]] = None


class ReportScheduleUpdate(BaseModel):
    """Schema for updating report schedule"""
    name: Optional[str] = None
    description: Optional[str] = None
    schedule_cron: Optional[str] = None
    report_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    notify_on_completion: Optional[bool] = None
    notification_emails: Optional[List[str]] = None


class ReportScheduleResponse(BaseModel):
    """Schema for report schedule response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    engagement_id: UUID
    template_id: UUID
    name: str
    description: Optional[str] = None
    schedule_cron: str
    is_active: bool
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[str] = None
    next_run_at: Optional[datetime] = None
    notify_on_completion: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime


# ========================================
# PDF Generation Schemas
# ========================================

class PDFGenerationOptions(BaseModel):
    """Schema for PDF generation options"""
    page_size: str = "LETTER"  # LETTER, A4, LEGAL
    orientation: str = "portrait"  # portrait, landscape
    dpi: int = 300
    compress: bool = True
    embed_fonts: bool = True
    enable_watermark: bool = True
    watermark_text: Optional[str] = None
    watermark_opacity: float = 0.3

    # Margins (in inches)
    margin_top: float = 0.75
    margin_bottom: float = 0.75
    margin_left: float = 0.75
    margin_right: float = 0.75

    # Header/Footer
    include_header: bool = True
    include_footer: bool = True
    include_page_numbers: bool = True


class HTMLToPDFRequest(BaseModel):
    """Schema for HTML to PDF conversion request"""
    html_content: str
    css_content: Optional[str] = None
    options: Optional[PDFGenerationOptions] = None
    header_html: Optional[str] = None
    footer_html: Optional[str] = None


class PDFDownloadRequest(BaseModel):
    """Schema for PDF download request"""
    report_id: UUID
    include_watermark: bool = True


# ========================================
# Reporting Stats Schemas
# ========================================

class ReportingStats(BaseModel):
    """Schema for reporting statistics"""
    total_reports: int
    reports_by_type: Dict[str, int]
    reports_by_status: Dict[str, int]
    total_templates: int
    active_templates: int
    pending_signatures: int
    completed_signatures: int
    avg_generation_time_ms: float
    total_storage_bytes: int


class ReportAuditLog(BaseModel):
    """Schema for report audit log entry"""
    report_id: UUID
    action: str
    performed_by: UUID
    performed_at: datetime
    details: Optional[Dict[str, Any]] = None
