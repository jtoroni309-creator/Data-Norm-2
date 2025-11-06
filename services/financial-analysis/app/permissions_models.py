"""
Multi-Tenant Permission System - Database Models

Implements a hierarchical multi-tenant permission system with:
- Platform Admin: Manages all CPA firms
- Firm Admin: Manages firm users and clients
- Firm User: Creates engagements and invites clients
- Client: Accesses client portal and uploads documents

Best Practices Implemented:
- Row-level security for tenant isolation
- Role-Based Access Control (RBAC)
- Invitation-based onboarding
- Comprehensive audit logging
- Principle of least privilege
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import relationship

from .database import Base


# ============================================================================
# ENUMS
# ============================================================================


class UserRole(str, Enum):
    """
    User roles with hierarchical permissions.

    Hierarchy (highest to lowest):
    1. PLATFORM_ADMIN - Full platform access
    2. FIRM_ADMIN - Manages firm users and clients
    3. FIRM_USER - Creates engagements, invites clients
    4. CLIENT - Limited access to own data
    """
    PLATFORM_ADMIN = "platform_admin"
    FIRM_ADMIN = "firm_admin"
    FIRM_USER = "firm_user"
    CLIENT = "client"


class PermissionScope(str, Enum):
    """
    Permission scopes defining what resources can be accessed.
    """
    # Platform-wide permissions (Platform Admin only)
    PLATFORM_ALL = "platform:all"
    PLATFORM_TENANTS = "platform:tenants"
    PLATFORM_BILLING = "platform:billing"
    PLATFORM_SETTINGS = "platform:settings"

    # Firm-level permissions (Firm Admin)
    FIRM_ALL = "firm:all"
    FIRM_USERS = "firm:users"
    FIRM_CLIENTS = "firm:clients"
    FIRM_SETTINGS = "firm:settings"
    FIRM_BILLING = "firm:billing"

    # Engagement permissions (Firm User)
    ENGAGEMENT_CREATE = "engagement:create"
    ENGAGEMENT_READ = "engagement:read"
    ENGAGEMENT_UPDATE = "engagement:update"
    ENGAGEMENT_DELETE = "engagement:delete"

    # Client permissions
    CLIENT_DATA_READ = "client:data:read"
    CLIENT_DATA_UPLOAD = "client:data:upload"
    CLIENT_INTEGRATIONS = "client:integrations"

    # Confirmation permissions
    CONFIRMATION_CREATE = "confirmation:create"
    CONFIRMATION_SEND = "confirmation:send"
    CONFIRMATION_VIEW = "confirmation:view"

    # Report permissions
    REPORT_GENERATE = "report:generate"
    REPORT_SIGN = "report:sign"
    REPORT_VIEW = "report:view"


class InvitationStatus(str, Enum):
    """Status of user invitation"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class TenantStatus(str, Enum):
    """Status of CPA firm (tenant)"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"


class AuditAction(str, Enum):
    """Types of auditable actions"""
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_INVITED = "user_invited"
    ROLE_CHANGED = "role_changed"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    TENANT_CREATED = "tenant_created"
    TENANT_UPDATED = "tenant_updated"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    CLIENT_INVITED = "client_invited"
    CLIENT_ACCESS_GRANTED = "client_access_granted"
    CLIENT_ACCESS_REVOKED = "client_access_revoked"
    DATA_ACCESSED = "data_accessed"
    DATA_EXPORTED = "data_exported"


# ============================================================================
# MODELS
# ============================================================================


class Tenant(Base):
    """
    Tenant (CPA Firm) - Multi-tenancy isolation.

    Each CPA firm is a tenant with completely isolated data.
    Platform admins manage tenants, firm admins manage their tenant.
    """
    __tablename__ = "tenants"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Firm information
    firm_name = Column(String(500), nullable=False)
    firm_ein = Column(String(20), unique=True)  # Employer Identification Number
    firm_license_number = Column(String(100))  # State CPA license number

    # Contact information
    primary_contact_name = Column(String(500))
    primary_contact_email = Column(String(500))
    primary_contact_phone = Column(String(50))

    # Address
    address_line1 = Column(String(500))
    address_line2 = Column(String(500))
    city = Column(String(200))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="USA")

    # Status and subscription
    status = Column(SQLEnum(TenantStatus), default=TenantStatus.TRIAL)
    subscription_tier = Column(String(100))  # Basic, Professional, Enterprise
    max_users = Column(Integer, default=5)
    max_clients = Column(Integer, default=50)
    max_storage_gb = Column(Integer, default=100)

    # Trial information
    trial_ends_at = Column(DateTime(timezone=True))

    # Settings
    settings = Column(JSONB, default=dict)  # Firm-specific settings

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Soft delete
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    users = relationship("User", back_populates="tenant", foreign_keys="User.tenant_id")
    clients = relationship("ClientAccess", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")

    # Indexes
    __table_args__ = (
        Index("idx_tenant_status", "status"),
        Index("idx_tenant_firm_name", "firm_name"),
    )


class User(Base):
    """
    User with role-based permissions.

    Users belong to a tenant (except Platform Admins) and have one primary role.
    All data access is scoped to their tenant for isolation.
    """
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Tenant relationship (null for platform admins)
    tenant_id = Column(PGUUID(as_uuid=True), ForeignKey("tenants.id"))

    # User information
    email = Column(String(500), unique=True, nullable=False)
    first_name = Column(String(200))
    last_name = Column(String(200))
    phone = Column(String(50))

    # Role and permissions
    role = Column(SQLEnum(UserRole), nullable=False)

    # Authentication
    password_hash = Column(String(500))  # Hashed password
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True))

    # Security
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(100))
    last_login_at = Column(DateTime(timezone=True))
    last_login_ip = Column(String(50))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))

    # Professional information (for CPAs)
    cpa_license_number = Column(String(100))
    cpa_license_state = Column(String(100))
    professional_title = Column(String(200))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Soft delete
    deleted_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="users", foreign_keys=[tenant_id])
    permissions = relationship("UserPermission", back_populates="user", foreign_keys="UserPermission.user_id")
    invitations_sent = relationship("UserInvitation", back_populates="invited_by_user", foreign_keys="UserInvitation.invited_by")
    audit_logs_created = relationship("AuditLog", back_populates="user", foreign_keys="AuditLog.user_id")
    client_accesses = relationship("ClientAccess", back_populates="granted_by_user", foreign_keys="ClientAccess.granted_by")

    # Indexes
    __table_args__ = (
        Index("idx_user_tenant", "tenant_id"),
        Index("idx_user_email", "email"),
        Index("idx_user_role", "role"),
        Index("idx_user_active", "is_active"),
    )


class UserPermission(Base):
    """
    User-specific permissions (in addition to role defaults).

    Allows fine-grained permission customization beyond default role permissions.
    """
    __tablename__ = "user_permissions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Permission
    scope = Column(SQLEnum(PermissionScope), nullable=False)
    granted = Column(Boolean, default=True)  # True = granted, False = revoked

    # Constraints (optional - for resource-specific permissions)
    resource_id = Column(PGUUID(as_uuid=True))  # e.g., specific engagement ID
    resource_type = Column(String(100))  # e.g., "engagement", "client"

    # Metadata
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    granted_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    expires_at = Column(DateTime(timezone=True))
    reason = Column(Text)

    # Relationships
    user = relationship("User", back_populates="permissions", foreign_keys=[user_id])

    # Indexes and constraints
    __table_args__ = (
        Index("idx_permission_user", "user_id"),
        Index("idx_permission_scope", "scope"),
        UniqueConstraint("user_id", "scope", "resource_id", name="uq_user_permission"),
    )


class UserInvitation(Base):
    """
    User invitation for onboarding new users and clients.

    Implements secure invitation-based onboarding instead of direct user creation.
    Invitations expire after a set time period.
    """
    __tablename__ = "user_invitations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Invitation details
    email = Column(String(500), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    # Invitation token (secure random token)
    invitation_token = Column(String(500), unique=True, nullable=False)

    # Status
    status = Column(SQLEnum(InvitationStatus), default=InvitationStatus.PENDING)

    # Expiry (default: 7 days)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Acceptance
    accepted_at = Column(DateTime(timezone=True))
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))  # Set when accepted

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    invited_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Optional message
    message = Column(Text)

    # Relationships
    tenant = relationship("Tenant")
    invited_by_user = relationship("User", foreign_keys=[invited_by], back_populates="invitations_sent")
    accepted_user = relationship("User", foreign_keys=[user_id])

    # Indexes
    __table_args__ = (
        Index("idx_invitation_email", "email"),
        Index("idx_invitation_token", "invitation_token"),
        Index("idx_invitation_status", "status"),
        Index("idx_invitation_expires", "expires_at"),
    )


class ClientAccess(Base):
    """
    Client access to their data and the client portal.

    Firm users grant clients access to view their engagement data,
    upload documents, and manage integrations.
    """
    __tablename__ = "client_accesses"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Client user
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    # Access scope
    can_view_financials = Column(Boolean, default=True)
    can_upload_documents = Column(Boolean, default=True)
    can_manage_integrations = Column(Boolean, default=True)
    can_view_reports = Column(Boolean, default=False)

    # Specific engagement access (optional - null means all engagements)
    engagement_ids = Column(JSONB)  # List of engagement UUIDs

    # Access period
    access_granted_at = Column(DateTime(timezone=True), server_default=func.now())
    access_expires_at = Column(DateTime(timezone=True))

    # Metadata
    granted_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    revoked_at = Column(DateTime(timezone=True))
    revoked_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    revocation_reason = Column(Text)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    tenant = relationship("Tenant", back_populates="clients")
    granted_by_user = relationship("User", foreign_keys=[granted_by], back_populates="client_accesses")
    revoked_by_user = relationship("User", foreign_keys=[revoked_by])

    # Indexes
    __table_args__ = (
        Index("idx_client_access_user", "user_id"),
        Index("idx_client_access_tenant", "tenant_id"),
        Index("idx_client_access_granted", "granted_by"),
    )


class AuditLog(Base):
    """
    Comprehensive audit log for compliance and security.

    Tracks all permission changes, user actions, and data access
    for compliance with professional standards (AS 2201, SOC 2).
    """
    __tablename__ = "audit_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Who, what, when
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    tenant_id = Column(PGUUID(as_uuid=True), ForeignKey("tenants.id"))
    action = Column(SQLEnum(AuditAction), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Details
    resource_type = Column(String(100))  # e.g., "user", "engagement", "client"
    resource_id = Column(PGUUID(as_uuid=True))

    # Changes made (before/after values)
    changes = Column(JSONB)

    # Context
    ip_address = Column(String(50))
    user_agent = Column(Text)

    # Description
    description = Column(Text)

    # Success/failure
    success = Column(Boolean, default=True)
    error_message = Column(Text)

    # Relationships
    user = relationship("User", back_populates="audit_logs_created", foreign_keys=[user_id])
    tenant = relationship("Tenant", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_tenant", "tenant_id"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )


# ============================================================================
# PERMISSION MATRIX
# ============================================================================

# Default permissions for each role
ROLE_PERMISSIONS = {
    UserRole.PLATFORM_ADMIN: [
        # Full platform access
        PermissionScope.PLATFORM_ALL,
        PermissionScope.PLATFORM_TENANTS,
        PermissionScope.PLATFORM_BILLING,
        PermissionScope.PLATFORM_SETTINGS,
        # Can do everything
        PermissionScope.FIRM_ALL,
        PermissionScope.ENGAGEMENT_CREATE,
        PermissionScope.ENGAGEMENT_READ,
        PermissionScope.ENGAGEMENT_UPDATE,
        PermissionScope.ENGAGEMENT_DELETE,
        PermissionScope.CONFIRMATION_CREATE,
        PermissionScope.CONFIRMATION_SEND,
        PermissionScope.CONFIRMATION_VIEW,
        PermissionScope.REPORT_GENERATE,
        PermissionScope.REPORT_SIGN,
        PermissionScope.REPORT_VIEW,
    ],

    UserRole.FIRM_ADMIN: [
        # Firm-level permissions
        PermissionScope.FIRM_ALL,
        PermissionScope.FIRM_USERS,
        PermissionScope.FIRM_CLIENTS,
        PermissionScope.FIRM_SETTINGS,
        PermissionScope.FIRM_BILLING,
        # Engagement permissions
        PermissionScope.ENGAGEMENT_CREATE,
        PermissionScope.ENGAGEMENT_READ,
        PermissionScope.ENGAGEMENT_UPDATE,
        PermissionScope.ENGAGEMENT_DELETE,
        # Confirmation permissions
        PermissionScope.CONFIRMATION_CREATE,
        PermissionScope.CONFIRMATION_SEND,
        PermissionScope.CONFIRMATION_VIEW,
        # Report permissions
        PermissionScope.REPORT_GENERATE,
        PermissionScope.REPORT_SIGN,
        PermissionScope.REPORT_VIEW,
    ],

    UserRole.FIRM_USER: [
        # Engagement permissions
        PermissionScope.ENGAGEMENT_CREATE,
        PermissionScope.ENGAGEMENT_READ,
        PermissionScope.ENGAGEMENT_UPDATE,
        # Confirmation permissions
        PermissionScope.CONFIRMATION_CREATE,
        PermissionScope.CONFIRMATION_SEND,
        PermissionScope.CONFIRMATION_VIEW,
        # Report permissions
        PermissionScope.REPORT_GENERATE,
        PermissionScope.REPORT_VIEW,
        # Can invite clients
        PermissionScope.FIRM_CLIENTS,
    ],

    UserRole.CLIENT: [
        # Limited client permissions
        PermissionScope.CLIENT_DATA_READ,
        PermissionScope.CLIENT_DATA_UPLOAD,
        PermissionScope.CLIENT_INTEGRATIONS,
        PermissionScope.REPORT_VIEW,
    ],
}
