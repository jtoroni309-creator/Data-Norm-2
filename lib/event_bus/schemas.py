"""
Event schemas for the event bus

All events must inherit from BaseEvent
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base event with common fields"""
    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Event type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    service: str = Field(..., description="Originating service")
    user_id: Optional[UUID] = Field(None, description="User who triggered the event")
    organization_id: Optional[UUID] = Field(None, description="Organization context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class EngagementCreatedEvent(BaseEvent):
    """Fired when a new engagement is created"""
    event_type: str = "engagement.created"
    engagement_id: UUID
    client_id: UUID
    fiscal_year_end: str
    engagement_type: str


class EngagementFinalizedEvent(BaseEvent):
    """Fired when an engagement is finalized"""
    event_type: str = "engagement.finalized"
    engagement_id: UUID
    finalized_by: UUID
    report_required: bool = True


class TrialBalanceUploadedEvent(BaseEvent):
    """Fired when a trial balance is uploaded"""
    event_type: str = "trial_balance.uploaded"
    trial_balance_id: UUID
    engagement_id: UUID
    period_end_date: str
    total_lines: int


class AccountsMappedEvent(BaseEvent):
    """Fired when accounts are mapped"""
    event_type: str = "accounts.mapped"
    trial_balance_id: UUID
    engagement_id: UUID
    mapped_count: int
    unmapped_count: int
    confidence_avg: float


class AnalyticsCompletedEvent(BaseEvent):
    """Fired when analytics processing completes"""
    event_type: str = "analytics.completed"
    engagement_id: UUID
    trial_balance_id: UUID
    je_tests_count: int
    anomalies_found: int
    risk_level: str


class ReportGeneratedEvent(BaseEvent):
    """Fired when a report is generated"""
    event_type: str = "report.generated"
    report_id: UUID
    engagement_id: UUID
    report_type: str
    report_url: str


class UserInvitedEvent(BaseEvent):
    """Fired when a user is invited"""
    event_type: str = "user.invited"
    invitation_id: UUID
    email: str
    role: str
    invited_by: UUID


class QPCReviewRequestedEvent(BaseEvent):
    """Fired when QC review is requested"""
    event_type: str = "qc.review_requested"
    engagement_id: UUID
    reviewer_id: UUID
    workpapers_count: int
    due_date: Optional[str] = None


class WorkpaperApprovedEvent(BaseEvent):
    """Fired when a workpaper is approved"""
    event_type: str = "workpaper.approved"
    workpaper_id: UUID
    engagement_id: UUID
    approved_by: UUID


class ComplianceCheckFailedEvent(BaseEvent):
    """Fired when a compliance check fails"""
    event_type: str = "compliance.check_failed"
    engagement_id: UUID
    check_id: UUID
    check_name: str
    risk_level: str
    requires_action: bool = True


class DataIngestionCompletedEvent(BaseEvent):
    """Fired when data ingestion completes"""
    event_type: str = "ingestion.completed"
    engagement_id: UUID
    source: str
    records_processed: int
    errors_count: int
