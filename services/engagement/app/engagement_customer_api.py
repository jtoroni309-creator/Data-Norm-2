"""
Engagement Customer Management API

API endpoints for CPA firms to manage customer access to engagements.
Allows CPA users to:
- Add customers to engagements
- Grant/revoke access permissions
- View customer engagement assignments
- Remove customers from engagements
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .database import get_db
from .models import Engagement, EngagementCustomer

router = APIRouter(prefix="/api/engagements", tags=["Engagement Customers"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class AddCustomerRequest(BaseModel):
    """Request to add customer to engagement"""
    customerEmail: EmailStr
    role: str = "primary_contact"
    canViewReports: bool = True
    canUploadDocuments: bool = True
    canManageIntegrations: bool = True
    canViewFinancials: bool = True
    canCompleteQuestionnaires: bool = True
    canApproveConfirmations: bool = False
    notes: Optional[str] = None


class UpdateCustomerPermissionsRequest(BaseModel):
    """Update customer permissions"""
    canViewReports: Optional[bool] = None
    canUploadDocuments: Optional[bool] = None
    canManageIntegrations: Optional[bool] = None
    canViewFinancials: Optional[bool] = None
    canCompleteQuestionnaires: Optional[bool] = None
    canApproveConfirmations: Optional[bool] = None
    isActive: Optional[bool] = None
    notes: Optional[str] = None


class EngagementCustomerResponse(BaseModel):
    """Engagement customer response"""
    id: str
    engagementId: str
    customerUserId: str
    customerEmail: str
    customerName: Optional[str]
    role: str
    canViewReports: bool
    canUploadDocuments: bool
    canManageIntegrations: bool
    canViewFinancials: bool
    canCompleteQuestionnaires: bool
    canApproveConfirmations: bool
    isActive: bool
    invitedAt: str
    accessGrantedAt: Optional[str]
    lastAccessedAt: Optional[str]
    notes: Optional[str]


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post(
    "/{engagement_id}/customers",
    response_model=EngagementCustomerResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_customer_to_engagement(
    engagement_id: str,
    request: AddCustomerRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Add a customer to an engagement.

    CPA firm users can grant customers access to specific engagements
    with granular permissions for each engagement.
    """
    # In production:
    # 1. Verify current user has permission to manage this engagement
    # 2. Look up customer by email (or create invitation)
    # 3. Check if customer already has access
    # 4. Create EngagementCustomer record
    # 5. Send notification email to customer
    # 6. Log audit trail

    # Mock implementation
    customer_id = str(uuid4())
    customer_user_id = str(uuid4())  # Would be looked up from user service

    return EngagementCustomerResponse(
        id=customer_id,
        engagementId=engagement_id,
        customerUserId=customer_user_id,
        customerEmail=request.customerEmail,
        customerName="John Customer",  # Would be from user service
        role=request.role,
        canViewReports=request.canViewReports,
        canUploadDocuments=request.canUploadDocuments,
        canManageIntegrations=request.canManageIntegrations,
        canViewFinancials=request.canViewFinancials,
        canCompleteQuestionnaires=request.canCompleteQuestionnaires,
        canApproveConfirmations=request.canApproveConfirmations,
        isActive=True,
        invitedAt=datetime.utcnow().isoformat() + "Z",
        accessGrantedAt=None,
        lastAccessedAt=None,
        notes=request.notes,
    )


@router.get(
    "/{engagement_id}/customers",
    response_model=List[EngagementCustomerResponse]
)
async def list_engagement_customers(
    engagement_id: str,
    includeInactive: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """
    List all customers assigned to an engagement.

    Returns customers with their access permissions for the engagement.
    """
    # In production:
    # 1. Verify current user has access to this engagement
    # 2. Query EngagementCustomer records
    # 3. Join with User table to get customer details
    # 4. Return paginated list

    # Mock implementation
    customers = [
        EngagementCustomerResponse(
            id=str(uuid4()),
            engagementId=engagement_id,
            customerUserId=str(uuid4()),
            customerEmail="john.customer@company.com",
            customerName="John Customer",
            role="primary_contact",
            canViewReports=True,
            canUploadDocuments=True,
            canManageIntegrations=True,
            canViewFinancials=True,
            canCompleteQuestionnaires=True,
            canApproveConfirmations=True,
            isActive=True,
            invitedAt="2024-11-01T10:00:00Z",
            accessGrantedAt="2024-11-01T12:00:00Z",
            lastAccessedAt="2024-11-12T09:00:00Z",
            notes="Primary contact for engagement",
        ),
        EngagementCustomerResponse(
            id=str(uuid4()),
            engagementId=engagement_id,
            customerUserId=str(uuid4()),
            customerEmail="jane.finance@company.com",
            customerName="Jane Finance",
            role="secondary_contact",
            canViewReports=True,
            canUploadDocuments=True,
            canManageIntegrations=False,
            canViewFinancials=True,
            canCompleteQuestionnaires=True,
            canApproveConfirmations=False,
            isActive=True,
            invitedAt="2024-11-02T10:00:00Z",
            accessGrantedAt="2024-11-02T14:00:00Z",
            lastAccessedAt="2024-11-11T15:00:00Z",
            notes="Secondary contact - finance manager",
        ),
    ]

    if not includeInactive:
        customers = [c for c in customers if c.isActive]

    return customers


@router.get(
    "/{engagement_id}/customers/{customer_id}",
    response_model=EngagementCustomerResponse
)
async def get_engagement_customer(
    engagement_id: str,
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a customer's access to an engagement.
    """
    # In production: Query EngagementCustomer by ID with verification

    return EngagementCustomerResponse(
        id=customer_id,
        engagementId=engagement_id,
        customerUserId=str(uuid4()),
        customerEmail="john.customer@company.com",
        customerName="John Customer",
        role="primary_contact",
        canViewReports=True,
        canUploadDocuments=True,
        canManageIntegrations=True,
        canViewFinancials=True,
        canCompleteQuestionnaires=True,
        canApproveConfirmations=True,
        isActive=True,
        invitedAt="2024-11-01T10:00:00Z",
        accessGrantedAt="2024-11-01T12:00:00Z",
        lastAccessedAt="2024-11-12T09:00:00Z",
        notes="Primary contact for engagement",
    )


@router.patch(
    "/{engagement_id}/customers/{customer_id}",
    response_model=EngagementCustomerResponse
)
async def update_customer_permissions(
    engagement_id: str,
    customer_id: str,
    request: UpdateCustomerPermissionsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update customer permissions for an engagement.

    Allows CPA firm users to modify what a customer can do on the engagement.
    """
    # In production:
    # 1. Verify current user has permission
    # 2. Query EngagementCustomer record
    # 3. Update permissions
    # 4. Log audit trail
    # 5. Send notification if significant change

    # Mock implementation - return updated customer
    return EngagementCustomerResponse(
        id=customer_id,
        engagementId=engagement_id,
        customerUserId=str(uuid4()),
        customerEmail="john.customer@company.com",
        customerName="John Customer",
        role="primary_contact",
        canViewReports=request.canViewReports if request.canViewReports is not None else True,
        canUploadDocuments=request.canUploadDocuments if request.canUploadDocuments is not None else True,
        canManageIntegrations=request.canManageIntegrations if request.canManageIntegrations is not None else True,
        canViewFinancials=request.canViewFinancials if request.canViewFinancials is not None else True,
        canCompleteQuestionnaires=request.canCompleteQuestionnaires if request.canCompleteQuestionnaires is not None else True,
        canApproveConfirmations=request.canApproveConfirmations if request.canApproveConfirmations is not None else True,
        isActive=request.isActive if request.isActive is not None else True,
        invitedAt="2024-11-01T10:00:00Z",
        accessGrantedAt="2024-11-01T12:00:00Z",
        lastAccessedAt="2024-11-12T09:00:00Z",
        notes=request.notes,
    )


@router.delete(
    "/{engagement_id}/customers/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_customer_from_engagement(
    engagement_id: str,
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Remove customer access from an engagement.

    Sets is_active to False (soft delete).
    Customer can be re-added if needed.
    """
    # In production:
    # 1. Verify current user has permission
    # 2. Update EngagementCustomer.is_active = False
    # 3. Log audit trail
    # 4. Send notification email

    return None


@router.post(
    "/{engagement_id}/customers/{customer_id}/resend-invitation",
    status_code=status.HTTP_200_OK
)
async def resend_customer_invitation(
    engagement_id: str,
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Resend invitation email to customer.

    Useful if customer didn't receive or lost the original invitation.
    """
    # In production:
    # 1. Verify current user has permission
    # 2. Generate new invitation token
    # 3. Send invitation email
    # 4. Log audit trail

    return {
        "message": "Invitation email sent successfully",
        "sentAt": datetime.utcnow().isoformat() + "Z",
    }
