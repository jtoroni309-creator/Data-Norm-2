"""
Pydantic Schemas for Regulation A/B Audit Service
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import (
    CMBSDealStatus,
    ComplianceCheckStatus,
    ComplianceStandard,
    RegABAuditStatus,
    SignoffStatus,
    WorkpaperStatus,
)


# ========================================
# Feature Flag Schemas
# ========================================

class FeatureFlagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    is_enabled: bool
    allow_client_portal: bool
    allow_cpa_portal: bool
    auto_workpaper_generation: bool
    auto_report_generation: bool
    ai_compliance_checking: bool
    ai_model_version: Optional[str] = None
    compliance_check_level: Optional[str] = None
    notify_on_completion: bool
    notify_cpa_on_ready: bool
    notify_client_on_approval: bool
    notification_email: Optional[str] = None
    require_dual_signoff: bool
    retention_years: int
    created_at: datetime
    updated_at: datetime
    enabled_at: Optional[datetime] = None
    enabled_by: Optional[UUID] = None


class FeatureFlagUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    allow_client_portal: Optional[bool] = None
    allow_cpa_portal: Optional[bool] = None
    auto_workpaper_generation: Optional[bool] = None
    auto_report_generation: Optional[bool] = None
    ai_compliance_checking: Optional[bool] = None
    ai_model_version: Optional[str] = None
    compliance_check_level: Optional[str] = None
    notify_on_completion: Optional[bool] = None
    notify_cpa_on_ready: Optional[bool] = None
    notify_client_on_approval: Optional[bool] = None
    notification_email: Optional[str] = None
    require_dual_signoff: Optional[bool] = None
    retention_years: Optional[int] = None


# ========================================
# Audit Engagement Schemas
# ========================================

class RegABAuditEngagementCreate(BaseModel):
    engagement_id: UUID
    audit_name: str = Field(..., min_length=1, max_length=500)
    audit_period_start: date
    audit_period_end: date
    client_organization_id: UUID
    client_contact_id: Optional[UUID] = None
    assigned_cpa_id: Optional[UUID] = None
    secondary_reviewer_id: Optional[UUID] = None


class RegABAuditEngagementUpdate(BaseModel):
    audit_name: Optional[str] = None
    status: Optional[RegABAuditStatus] = None
    assigned_cpa_id: Optional[UUID] = None
    secondary_reviewer_id: Optional[UUID] = None


class RegABAuditEngagementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    engagement_id: UUID
    organization_id: UUID
    audit_name: str
    audit_period_start: date
    audit_period_end: date
    status: RegABAuditStatus
    client_contact_id: Optional[UUID] = None
    client_organization_id: UUID
    assigned_cpa_id: Optional[UUID] = None
    secondary_reviewer_id: Optional[UUID] = None
    ai_processing_started_at: Optional[datetime] = None
    ai_processing_completed_at: Optional[datetime] = None
    ai_processing_duration_seconds: Optional[int] = None
    ai_confidence_score: Optional[Decimal] = None
    total_cmbs_deals: int
    processed_deals: int
    total_workpapers: int
    approved_workpapers: int
    total_compliance_checks: int
    passed_compliance_checks: int
    failed_compliance_checks: int
    report_generated_at: Optional[datetime] = None
    report_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    submitted_for_review_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    finalized_at: Optional[datetime] = None


# ========================================
# CMBS Deal Schemas
# ========================================

class CMBSDealCreate(BaseModel):
    deal_name: str = Field(..., min_length=1, max_length=500)
    deal_number: str = Field(..., min_length=1, max_length=100)
    cusip: Optional[str] = None
    bloomberg_id: Optional[str] = None
    origination_date: date
    maturity_date: Optional[date] = None
    original_balance: Decimal = Field(..., gt=0)
    current_balance: Decimal = Field(..., gt=0)
    interest_rate: Optional[Decimal] = None
    is_oa: bool = True
    oa_appointment_date: Optional[date] = None
    property_type: Optional[str] = None
    property_address: Optional[Dict[str, Any]] = None
    property_count: Optional[int] = None
    master_servicer: Optional[str] = None
    special_servicer: Optional[str] = None
    trustee: Optional[str] = None
    dscr: Optional[Decimal] = None
    ltv: Optional[Decimal] = None
    occupancy_rate: Optional[Decimal] = None
    delinquency_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    documents: Optional[Dict[str, Any]] = None


class CMBSDealUpdate(BaseModel):
    deal_name: Optional[str] = None
    status: Optional[CMBSDealStatus] = None
    current_balance: Optional[Decimal] = None
    interest_rate: Optional[Decimal] = None
    dscr: Optional[Decimal] = None
    ltv: Optional[Decimal] = None
    occupancy_rate: Optional[Decimal] = None
    delinquency_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CMBSDealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    audit_engagement_id: UUID
    deal_name: str
    deal_number: str
    cusip: Optional[str] = None
    bloomberg_id: Optional[str] = None
    origination_date: date
    maturity_date: Optional[date] = None
    original_balance: Decimal
    current_balance: Decimal
    interest_rate: Optional[Decimal] = None
    is_oa: bool
    oa_appointment_date: Optional[date] = None
    property_type: Optional[str] = None
    property_address: Optional[Dict[str, Any]] = None
    property_count: Optional[int] = None
    master_servicer: Optional[str] = None
    special_servicer: Optional[str] = None
    trustee: Optional[str] = None
    dscr: Optional[Decimal] = None
    ltv: Optional[Decimal] = None
    occupancy_rate: Optional[Decimal] = None
    delinquency_status: Optional[str] = None
    status: CMBSDealStatus
    metadata: Optional[Dict[str, Any]] = None
    documents: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    submitted_by: Optional[UUID] = None


# ========================================
# Compliance Check Schemas
# ========================================

class ComplianceCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    audit_engagement_id: UUID
    cmbs_deal_id: Optional[UUID] = None
    check_name: str
    check_code: str
    standard: ComplianceStandard
    standard_reference: str
    description: str
    status: ComplianceCheckStatus
    executed_at: Optional[datetime] = None
    execution_duration_ms: Optional[int] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_confidence: Optional[Decimal] = None
    risk_level: Optional[str] = None
    passed: Optional[bool] = None
    findings: Optional[str] = None
    recommendation: Optional[str] = None
    remediation_steps: Optional[Dict[str, Any]] = None
    evidence_references: Optional[Dict[str, Any]] = None
    data_points_analyzed: Optional[Dict[str, Any]] = None
    requires_manual_review: bool
    manual_review_notes: Optional[str] = None
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ========================================
# Workpaper Schemas
# ========================================

class WorkpaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    audit_engagement_id: UUID
    cmbs_deal_id: Optional[UUID] = None
    workpaper_ref: str
    title: str
    category: str
    description: Optional[str] = None
    content: Dict[str, Any]
    content_html: Optional[str] = None
    content_url: Optional[str] = None
    status: WorkpaperStatus
    version: int
    ai_generated: bool
    ai_model_version: Optional[str] = None
    ai_prompt_used: Optional[str] = None
    ai_generation_confidence: Optional[Decimal] = None
    ai_generation_timestamp: Optional[datetime] = None
    reviewer_id: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    revision_count: int
    compliance_checks: Optional[Dict[str, Any]] = None
    source_documents: Optional[Dict[str, Any]] = None
    attachments: Optional[Dict[str, Any]] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    locked: bool
    locked_at: Optional[datetime] = None
    content_hash: Optional[str] = None


# ========================================
# Report Schemas
# ========================================

class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    audit_engagement_id: UUID
    report_type: str
    report_period_start: date
    report_period_end: date
    version: int
    executive_summary: Optional[str] = None
    findings_summary: Optional[Dict[str, Any]] = None
    content: Dict[str, Any]
    content_html: Optional[str] = None
    content_pdf_url: Optional[str] = None
    total_deals_audited: int
    total_compliance_checks: int
    passed_checks: int
    failed_checks: int
    total_workpapers: int
    ai_generated: bool
    ai_model_version: Optional[str] = None
    ai_generation_timestamp: Optional[datetime] = None
    ai_confidence_score: Optional[Decimal] = None
    draft: bool
    generated_at: datetime
    created_at: datetime
    updated_at: datetime
    content_hash: Optional[str] = None


# ========================================
# CPA Sign-off Schemas
# ========================================

class CPASignoffCreate(BaseModel):
    cpa_license_number: str = Field(..., min_length=1)
    cpa_license_state: str = Field(..., min_length=2, max_length=2)
    cpa_license_expiry: Optional[date] = None
    status: SignoffStatus = SignoffStatus.PENDING
    signoff_type: str = "final_approval"
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    revision_requests: Optional[Dict[str, Any]] = None
    attestation_text: Optional[str] = None
    attestation_confirmed: bool = False


class CPASignoffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    audit_engagement_id: UUID
    report_id: UUID
    cpa_user_id: UUID
    cpa_license_number: str
    cpa_license_state: str
    cpa_license_expiry: Optional[date] = None
    status: SignoffStatus
    signoff_type: str
    signature_timestamp: Optional[datetime] = None
    signature_ip_address: Optional[str] = None
    signature_method: Optional[str] = None
    signature_certificate: Optional[str] = None
    signature_hash: Optional[str] = None
    review_started_at: Optional[datetime] = None
    review_completed_at: Optional[datetime] = None
    review_duration_minutes: Optional[int] = None
    review_notes: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    revision_requests: Optional[Dict[str, Any]] = None
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[UUID] = None
    revocation_reason: Optional[str] = None
    attestation_text: Optional[str] = None
    attestation_confirmed: bool
    attestation_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ========================================
# Dashboard Schemas
# ========================================

class DashboardMetrics(BaseModel):
    total_engagements: int
    active_engagements: int
    completed_engagements: int
    total_cmbs_deals: int
    total_compliance_checks: int
    passed_compliance_checks: int
    failed_compliance_checks: int
    compliance_pass_rate: float


# ========================================
# Internal AI Schemas (not exposed via API)
# ========================================

class ComplianceCheckRequest(BaseModel):
    """Internal schema for AI compliance check requests"""
    deal: CMBSDealResponse
    engagement: RegABAuditEngagementResponse
    rule_code: str
    rule_name: str
    standard: ComplianceStandard
    standard_reference: str
    description: str
    requirements: str
    testing_procedures: str
    ai_prompt_template: str
    risk_category: str


class WorkpaperGenerationRequest(BaseModel):
    """Internal schema for workpaper generation requests"""
    deal: CMBSDealResponse
    engagement: RegABAuditEngagementResponse
    compliance_results: List[Dict[str, Any]]
    category: str
    workpaper_ref: str


class ReportGenerationRequest(BaseModel):
    """Internal schema for report generation requests"""
    engagement: RegABAuditEngagementResponse
    deals: List[CMBSDealResponse]
    compliance_checks: List[ComplianceCheckResponse]
    workpapers: List[WorkpaperResponse]
