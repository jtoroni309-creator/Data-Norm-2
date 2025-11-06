"""Pydantic schemas for Identity Service API"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class RoleEnum(str, Enum):
    """User roles"""
    PARTNER = "partner"
    MANAGER = "manager"
    SENIOR = "senior"
    STAFF = "staff"
    QC_REVIEWER = "qc_reviewer"
    CLIENT_CONTACT = "client_contact"


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str
    version: str


# ========================================
# User Schemas
# ========================================

class UserBase(BaseModel):
    """Base user fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=200)
    role: RoleEnum


class UserCreate(UserBase):
    """User creation request"""
    password: str = Field(..., min_length=8, max_length=100)
    organization_id: Optional[UUID] = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets complexity requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')

        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')

        return v


class UserResponse(UserBase):
    """User response (no password)"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    """User update request"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


# ========================================
# Authentication Schemas
# ========================================

class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiry in seconds")


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # User ID
    email: str
    role: str
    organization_id: Optional[str] = None
    exp: datetime
    iat: datetime
    type: str = "access"


# ========================================
# Organization Schemas
# ========================================

class OrganizationBase(BaseModel):
    """Base organization fields"""
    name: str = Field(..., min_length=1, max_length=200)
    tax_id: Optional[str] = None
    industry_code: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Organization creation request"""
    pass


class OrganizationUpdate(BaseModel):
    """Organization update request"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    tax_id: Optional[str] = None
    industry_code: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    secondary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    """Organization response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    logo_url: Optional[str] = None
    primary_color: str
    secondary_color: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    timezone: str
    date_format: str
    created_at: datetime
    updated_at: datetime


# ========================================
# Audit Log Schemas
# ========================================

class LoginAttemptResponse(BaseModel):
    """Login attempt audit log"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    success: bool
    ip_address: Optional[str] = None
    attempted_at: datetime


# ========================================
# User Invitation Schemas
# ========================================

class UserInvitationCreate(BaseModel):
    """User invitation creation request"""
    email: EmailStr
    role: RoleEnum
    message: Optional[str] = Field(None, max_length=500)


class UserInvitationResponse(BaseModel):
    """User invitation response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    role: RoleEnum
    invited_by_user_id: UUID
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    is_expired: bool
    created_at: datetime


class UserInvitationAccept(BaseModel):
    """Accept invitation request"""
    token: str
    full_name: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=8, max_length=100)


# ========================================
# User Permission Schemas
# ========================================

class UserPermissionUpdate(BaseModel):
    """User permission update request"""
    can_create_engagements: Optional[bool] = None
    can_edit_engagements: Optional[bool] = None
    can_delete_engagements: Optional[bool] = None
    can_view_all_engagements: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_manage_users: Optional[bool] = None
    can_manage_roles: Optional[bool] = None
    can_edit_firm_settings: Optional[bool] = None
    can_manage_billing: Optional[bool] = None
    can_upload_documents: Optional[bool] = None
    can_delete_documents: Optional[bool] = None


class UserPermissionResponse(BaseModel):
    """User permission response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    can_create_engagements: bool
    can_edit_engagements: bool
    can_delete_engagements: bool
    can_view_all_engagements: bool
    can_invite_users: bool
    can_manage_users: bool
    can_manage_roles: bool
    can_edit_firm_settings: bool
    can_manage_billing: bool
    can_upload_documents: bool
    can_delete_documents: bool
    created_at: datetime
    updated_at: datetime
