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


# ========================================
# Compliance Report Schemas (AICPA/PCAOB/GAAP)
# ========================================

class ComplianceEngagementType(str, Enum):
    """Engagement types per professional standards"""
    COMPILATION = "compilation"  # SSARS AR-C 80
    REVIEW = "review"           # SSARS AR-C 90
    AUDIT = "audit"             # GAAS AU-C / PCAOB AS

from enum import Enum

class ComplianceOpinionType(str, Enum):
    """Opinion/Report types per professional standards"""
    # Audit Opinions (AU-C 700, AS 3101)
    UNMODIFIED = "unmodified"
    QUALIFIED_SCOPE = "qualified_scope"
    QUALIFIED_GAAP = "qualified_gaap"
    ADVERSE = "adverse"
    DISCLAIMER = "disclaimer"
    # Review Conclusions (AR-C 90)
    REVIEW_UNMODIFIED = "review_unmodified"
    REVIEW_MODIFIED = "review_modified"
    # Compilation Reports (AR-C 80)
    COMPILATION_STANDARD = "compilation_standard"
    COMPILATION_NO_INDEPENDENCE = "compilation_no_independence"
    COMPILATION_OMIT_DISCLOSURES = "compilation_omit_disclosures"


class ComplianceEntityType(str, Enum):
    """Entity types for report customization"""
    PUBLIC_COMPANY = "public_company"
    PRIVATE_COMPANY = "private_company"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    ERISA_PLAN = "erisa_plan"


class ComplianceFinancialFramework(str, Enum):
    """Financial reporting frameworks"""
    GAAP_US = "gaap_us"
    IFRS = "ifrs"
    TAX_BASIS = "tax_basis"
    CASH_BASIS = "cash_basis"
    REGULATORY_BASIS = "regulatory_basis"


class KeyAuditMatter(BaseModel):
    """Critical audit matter for public company audits (AS 3101)"""
    title: str
    description: str
    audit_response: str


class ComplianceReportContext(BaseModel):
    """Context data for compliance report generation"""
    # Required fields
    addressee: str = Field(..., description="Report addressee")
    entity_name: str = Field(..., description="Name of the entity")
    financial_statements: List[str] = Field(
        default=["income", "changes in stockholders' equity", "cash flows"],
        description="List of statements"
    )
    period_end_date: datetime = Field(..., description="Balance sheet date")
    period_description: str = Field(..., description="E.g., 'year ended December 31, 2024'")
    firm_name: str = Field(..., description="CPA firm name")
    report_date: datetime = Field(..., description="Date of report")

    # Optional fields
    entity_type: Optional[str] = "Company"
    firm_city: Optional[str] = None
    firm_state: Optional[str] = None
    partner_name: Optional[str] = None
    auditor_tenure_year: Optional[int] = None

    # Going concern
    going_concern_conditions: Optional[str] = None
    going_concern_note_number: Optional[str] = None

    # Modification bases
    qualification_basis: Optional[str] = None
    scope_limitation_basis: Optional[str] = None
    adverse_basis: Optional[str] = None
    disclaimer_basis: Optional[str] = None
    modification_basis: Optional[str] = None

    # Additional data
    additional_data: Optional[Dict[str, Any]] = None


class CompilationReportRequest(BaseModel):
    """Request for compilation report generation (SSARS AR-C 80)"""
    context: ComplianceReportContext
    opinion_type: ComplianceOpinionType = ComplianceOpinionType.COMPILATION_STANDARD
    framework: ComplianceFinancialFramework = ComplianceFinancialFramework.GAAP_US


class ReviewReportRequest(BaseModel):
    """Request for review report generation (SSARS AR-C 90)"""
    context: ComplianceReportContext
    opinion_type: ComplianceOpinionType = ComplianceOpinionType.REVIEW_UNMODIFIED
    framework: ComplianceFinancialFramework = ComplianceFinancialFramework.GAAP_US
    emphasis_paragraphs: Optional[List[str]] = None


class AuditReportRequest(BaseModel):
    """Request for audit report generation (AU-C 700 / AS 3101)"""
    context: ComplianceReportContext
    opinion_type: ComplianceOpinionType = ComplianceOpinionType.UNMODIFIED
    entity_type: ComplianceEntityType = ComplianceEntityType.PRIVATE_COMPANY
    framework: ComplianceFinancialFramework = ComplianceFinancialFramework.GAAP_US
    going_concern: bool = False
    key_audit_matters: Optional[List[KeyAuditMatter]] = None
    emphasis_paragraphs: Optional[List[str]] = None
    other_matter_paragraphs: Optional[List[str]] = None


class ManagementRepLetterContext(BaseModel):
    """Context for management representation letter"""
    firm_name: str
    firm_address: Optional[str] = None
    entity_name: str
    entity_address: Optional[str] = None
    period_end_date: datetime
    period_description: str
    ceo_name: str
    ceo_title: Optional[str] = "Chief Executive Officer"
    cfo_name: str
    cfo_title: Optional[str] = "Chief Financial Officer"
    letter_date: datetime
    additional_data: Optional[Dict[str, Any]] = None


class ManagementRepLetterRequest(BaseModel):
    """Request for management representation letter (AU-C 580 / AS 2805)"""
    context: ManagementRepLetterContext
    engagement_type: ComplianceEngagementType = ComplianceEngagementType.AUDIT
    include_fraud_representations: bool = True
    include_going_concern: bool = False
    additional_representations: Optional[List[str]] = None


class CoverLetterContext(BaseModel):
    """Context for cover letter"""
    recipient_name: str
    recipient_title: Optional[str] = None
    recipient_company: Optional[str] = None
    recipient_address: Optional[str] = None
    recipient_salutation: Optional[str] = None
    entity_name: str
    period_description: str
    firm_name: str
    firm_address: Optional[str] = None
    firm_phone: Optional[str] = None
    firm_email: Optional[str] = None
    partner_name: str
    partner_title: Optional[str] = "Partner"
    letter_date: datetime
    deliverables: Optional[List[str]] = None
    management_letter_included: bool = False
    additional_data: Optional[Dict[str, Any]] = None


class CoverLetterRequest(BaseModel):
    """Request for cover letter generation"""
    context: CoverLetterContext
    engagement_type: ComplianceEngagementType = ComplianceEngagementType.AUDIT
    include_deliverables_list: bool = True


class NotesContext(BaseModel):
    """Context for notes to financial statements"""
    entity_name: str
    entity_type: Optional[str] = "Company"
    period_end_date: datetime
    period_description: Optional[str] = None
    nature_of_business: str
    fiscal_year_end: Optional[str] = None

    # Formation details
    formation_date: Optional[datetime] = None
    formation_type: Optional[str] = "incorporated"
    formation_state: Optional[str] = None

    # Going concern
    going_concern_conditions: Optional[str] = None
    going_concern_plans: Optional[str] = None

    # Accounting policies
    significant_estimates: Optional[str] = None
    inventory_method: Optional[str] = "first-in, first-out (FIFO)"
    inventory_components: Optional[str] = None
    depreciation_method: Optional[str] = "straight-line"
    useful_lives: Optional[str] = "3 to 39 years"
    intangible_types: Optional[str] = None

    # Revenue
    revenue_streams: Optional[List[Dict[str, str]]] = None

    # Debt
    debt_details: Optional[List[Dict[str, Any]]] = None
    total_debt: Optional[float] = None
    current_debt: Optional[float] = None
    long_term_debt: Optional[float] = None
    debt_maturities: Optional[List[Dict[str, Any]]] = None

    # Commitments
    lease_commitments: Optional[str] = None
    legal_contingencies: Optional[str] = None
    other_commitments: Optional[str] = None

    # Related parties
    related_parties: Optional[List[Dict[str, str]]] = None

    # Equity
    authorized_shares: Optional[str] = "10,000,000"
    par_value: Optional[str] = "0.001"
    stock_transactions: Optional[List[str]] = None
    dividends: Optional[str] = None

    # Concentrations
    major_customers: Optional[List[Dict[str, Any]]] = None

    # Subsequent events
    report_date: Optional[datetime] = None
    subsequent_events_date: Optional[datetime] = None
    subsequent_events_items: Optional[List[str]] = None

    additional_data: Optional[Dict[str, Any]] = None


class NotesRequest(BaseModel):
    """Request for notes to financial statements (FASB ASC)"""
    context: NotesContext
    framework: ComplianceFinancialFramework = ComplianceFinancialFramework.GAAP_US
    disclosure_selections: Optional[Dict[str, bool]] = None


class CompletePackageRequest(BaseModel):
    """Request for complete financial statement package"""
    context: Dict[str, Any] = Field(..., description="Full context data for all components")
    engagement_type: ComplianceEngagementType
    opinion_type: ComplianceOpinionType
    entity_type: ComplianceEntityType = ComplianceEntityType.PRIVATE_COMPANY
    framework: ComplianceFinancialFramework = ComplianceFinancialFramework.GAAP_US
    include_sections: Optional[Dict[str, bool]] = None


class ComplianceReportResponse(BaseModel):
    """Response for compliance report generation"""
    html_content: str
    report_type: str
    generated_at: datetime
    standards_compliance: List[str] = Field(
        default=["AICPA", "GAAP"],
        description="Standards this report complies with"
    )


class CompletePackageResponse(BaseModel):
    """Response for complete package generation"""
    sections: Dict[str, str]
    engagement_type: str
    generated_at: datetime
    standards_compliance: List[str]
