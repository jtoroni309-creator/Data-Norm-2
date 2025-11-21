"""
Client Collaboration Portal Routes
===================================
COMPETITIVE DIFFERENTIATOR #2: Two-sided marketplace model

vs. ALL Competitors: Drata/Vanta are for auditees only, AuditBoard/CaseWare
are for auditors only. We support BOTH with seamless collaboration.

Key Features:
- Client self-service evidence upload
- Real-time collaboration and notifications
- Evidence request workflow
- Version control and audit trail
- AI-powered evidence validation
"""

import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from .database import get_db
from .models import SOCEngagement, User, UserRole
# Note: Import client portal models when migration 003 is applied

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/client-portal", tags=["Client Collaboration Portal"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ClientUserCreate(BaseModel):
    """Create client user"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    role: str = Field(..., pattern="^(CLIENT_ADMIN|CLIENT_IT_LEAD|CLIENT_CONTRIBUTOR|CLIENT_VIEWER)$")


class ClientUserResponse(BaseModel):
    """Client user response"""
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime


class EvidenceRequestCreate(BaseModel):
    """Create evidence request"""
    control_id: Optional[UUID] = None
    test_plan_id: Optional[UUID] = None
    request_title: str = Field(..., min_length=5, max_length=500)
    request_description: str = Field(..., min_length=10)
    required_evidence_types: List[str] = Field(default_factory=list)
    required_file_formats: List[str] = Field(default_factory=list)
    sample_size: Optional[int] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    due_date: Optional[date] = None
    priority: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|URGENT)$")
    assigned_to_client_user: Optional[UUID] = None


class EvidenceRequestResponse(BaseModel):
    """Evidence request response"""
    id: UUID
    engagement_id: UUID
    request_title: str
    request_description: str
    status: str
    due_date: Optional[date]
    priority: str
    created_at: datetime
    sent_to_client_at: Optional[datetime]
    client_uploaded_at: Optional[datetime]


class ClientEvidenceUploadResponse(BaseModel):
    """Client evidence upload response"""
    id: UUID
    evidence_request_id: UUID
    filename: str
    file_size_bytes: int
    client_notes: Optional[str]
    uploaded_at: datetime
    verification_status: Optional[str]
    auditor_feedback: Optional[str]


# ============================================================================
# CLIENT USER MANAGEMENT
# ============================================================================

@router.post("/engagements/{engagement_id}/client-users")
async def create_client_user(
    engagement_id: UUID,
    user_data: ClientUserCreate,
    db: AsyncSession = Depends(get_db)
    # current_user: User = Depends(get_current_user)  # Require auditor authentication
) -> ClientUserResponse:
    """
    Create a client user for collaboration portal

    Only CPA firm staff (Manager or Partner) can create client users
    """
    logger.info(f"Creating client user {user_data.email} for engagement {engagement_id}")

    # Verify engagement exists
    result = await db.execute(
        select(SOCEngagement).where(SOCEngagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # TODO: Create client_user record
    # For now, return mock response

    return ClientUserResponse(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
        last_login_at=None,
        created_at=datetime.utcnow()
    )


@router.get("/engagements/{engagement_id}/client-users")
async def list_client_users(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> List[ClientUserResponse]:
    """
    List all client users for an engagement
    """
    # TODO: Query client_users table
    return []


@router.post("/engagements/{engagement_id}/client-users/{user_id}/deactivate")
async def deactivate_client_user(
    engagement_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Deactivate a client user (when engagement ends or user leaves client)
    """
    logger.info(f"Deactivating client user {user_id}")

    # TODO: Update client_user.is_active = False

    return {"message": "Client user deactivated", "user_id": str(user_id)}


# ============================================================================
# EVIDENCE REQUESTS
# ============================================================================

@router.post("/engagements/{engagement_id}/evidence-requests")
async def create_evidence_request(
    engagement_id: UUID,
    request_data: EvidenceRequestCreate,
    db: AsyncSession = Depends(get_db)
) -> EvidenceRequestResponse:
    """
    Create evidence request to send to client

    Auditor creates request, specifying what evidence is needed.
    Client receives notification and can upload evidence through portal.
    """
    logger.info(f"Creating evidence request: {request_data.request_title}")

    # Verify engagement
    result = await db.execute(
        select(SOCEngagement).where(SOCEngagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # TODO: Create evidence_request record
    # For now, mock response

    return EvidenceRequestResponse(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        engagement_id=engagement_id,
        request_title=request_data.request_title,
        request_description=request_data.request_description,
        status="DRAFT",
        due_date=request_data.due_date,
        priority=request_data.priority,
        created_at=datetime.utcnow(),
        sent_to_client_at=None,
        client_uploaded_at=None
    )


@router.post("/engagements/{engagement_id}/evidence-requests/{request_id}/send")
async def send_evidence_request_to_client(
    engagement_id: UUID,
    request_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Send evidence request to client

    Changes status from DRAFT to SENT_TO_CLIENT and triggers email notification
    """
    logger.info(f"Sending evidence request {request_id} to client")

    # TODO: Update status, send email notification

    return {
        "message": "Evidence request sent to client",
        "request_id": str(request_id),
        "sent_at": datetime.utcnow().isoformat()
    }


@router.get("/engagements/{engagement_id}/evidence-requests")
async def list_evidence_requests(
    engagement_id: UUID,
    status: Optional[str] = None,
    overdue_only: bool = False,
    db: AsyncSession = Depends(get_db)
) -> List[EvidenceRequestResponse]:
    """
    List evidence requests for an engagement

    Filters:
    - status: Filter by status (DRAFT, SENT_TO_CLIENT, etc.)
    - overdue_only: Show only overdue requests
    """
    # TODO: Query evidence_requests with filters
    return []


@router.get("/client-view/evidence-requests")
async def client_view_evidence_requests(
    db: AsyncSession = Depends(get_db)
    # client_user: ClientUser = Depends(get_current_client_user)
) -> List[EvidenceRequestResponse]:
    """
    CLIENT-SIDE ENDPOINT: List evidence requests assigned to current client user

    This is what clients see when they log into the portal
    """
    # TODO: Filter by client_user.engagement_id and assigned_to_client_user

    return []


# ============================================================================
# CLIENT EVIDENCE UPLOADS
# ============================================================================

@router.post("/client-view/evidence-requests/{request_id}/upload")
async def client_upload_evidence(
    request_id: UUID,
    file: UploadFile = File(...),
    client_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
    # client_user: ClientUser = Depends(get_current_client_user)
) -> ClientEvidenceUploadResponse:
    """
    CLIENT-SIDE ENDPOINT: Upload evidence file in response to request

    Client uploads file through self-service portal.
    File is validated, stored, and auditor is notified.
    """
    logger.info(f"Client uploading evidence for request {request_id}: {file.filename}")

    # Validate file
    if file.size > 100 * 1024 * 1024:  # 100 MB limit
        raise HTTPException(status_code=400, detail="File size exceeds 100 MB limit")

    allowed_extensions = ['.pdf', '.xlsx', '.png', '.jpg', '.mp4', '.zip']
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # TODO: Save file to blob storage
    # TODO: Create client_evidence_upload record
    # TODO: Update evidence_request status to CLIENT_UPLOADED
    # TODO: Notify auditor

    return ClientEvidenceUploadResponse(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        evidence_request_id=request_id,
        filename=file.filename,
        file_size_bytes=file.size,
        client_notes=client_notes,
        uploaded_at=datetime.utcnow(),
        verification_status="PENDING",
        auditor_feedback=None
    )


@router.post("/evidence-uploads/{upload_id}/verify")
async def auditor_verify_evidence(
    upload_id: UUID,
    accept: bool,
    feedback: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    AUDITOR-SIDE ENDPOINT: Verify/reject client-uploaded evidence

    Auditor reviews uploaded evidence and either accepts or requests clarification
    """
    logger.info(f"Auditor verifying upload {upload_id}: accept={accept}")

    # TODO: Update client_evidence_upload
    # Set verification_status, auditor_feedback
    # If rejected, notify client

    status = "ACCEPTED" if accept else "REJECTED"

    return {
        "upload_id": str(upload_id),
        "verification_status": status,
        "feedback": feedback,
        "verified_at": datetime.utcnow().isoformat()
    }


@router.get("/evidence-requests/{request_id}/uploads")
async def list_uploads_for_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> List[ClientEvidenceUploadResponse]:
    """
    List all uploads for an evidence request (with version history)
    """
    # TODO: Query client_evidence_uploads
    return []


# ============================================================================
# CLIENT PORTAL ANALYTICS
# ============================================================================

@router.get("/engagements/{engagement_id}/client-portal-metrics")
async def get_client_portal_metrics(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get metrics on client collaboration

    Shows engagement progress from client collaboration perspective
    """
    # TODO: Query evidence_requests, client_evidence_uploads, client_portal_activity

    return {
        "engagement_id": str(engagement_id),
        "total_requests": 25,
        "requests_completed": 18,
        "requests_overdue": 3,
        "total_uploads": 42,
        "uploads_pending_review": 5,
        "uploads_accepted": 35,
        "uploads_rejected": 2,
        "client_response_time_avg_hours": 18.5,
        "auditor_review_time_avg_hours": 6.2,
        "last_client_activity": "2025-01-21T14:30:00Z",
        "active_client_users": 4
    }


@router.get("/client-view/dashboard")
async def client_dashboard(
    db: AsyncSession = Depends(get_db)
    # client_user: ClientUser = Depends(get_current_client_user)
) -> dict:
    """
    CLIENT-SIDE ENDPOINT: Client's dashboard view

    Shows what the client sees when they log into the portal
    """
    return {
        "pending_requests": 7,
        "overdue_requests": 2,
        "recent_uploads": 12,
        "pending_auditor_review": 3,
        "upcoming_deadlines": [
            {
                "request_title": "Q4 User Access Review Evidence",
                "due_date": "2025-01-25",
                "priority": "HIGH"
            }
        ],
        "recent_activity": [
            {
                "timestamp": "2025-01-21T10:00:00Z",
                "action": "Evidence accepted",
                "request": "Backup logs for December 2024"
            }
        ]
    }


# ============================================================================
# NOTIFICATIONS
# ============================================================================

@router.post("/evidence-requests/{request_id}/remind")
async def send_reminder_to_client(
    request_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Send reminder email to client for overdue evidence request
    """
    logger.info(f"Sending reminder for evidence request {request_id}")

    # TODO: Send email notification

    return {
        "message": "Reminder sent to client",
        "request_id": str(request_id),
        "sent_at": datetime.utcnow().isoformat()
    }
