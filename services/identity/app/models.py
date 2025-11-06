"""SQLAlchemy ORM models for Identity Service"""
from datetime import datetime
from uuid import uuid4
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, INET
from sqlalchemy.orm import relationship

from .database import Base


class RoleEnum(str, Enum):
    """User roles with hierarchical permissions"""
    PARTNER = "partner"
    MANAGER = "manager"
    SENIOR = "senior"
    STAFF = "staff"
    QC_REVIEWER = "qc_reviewer"
    CLIENT_CONTACT = "client_contact"


class Organization(Base):
    """Organization (CPA firm or client company)"""
    __tablename__ = "organizations"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    tax_id = Column(String)
    industry_code = Column(String)

    # Firm branding
    logo_url = Column(String)  # URL/path to uploaded logo
    primary_color = Column(String, default="#2563eb")  # Brand primary color
    secondary_color = Column(String, default="#7c3aed")  # Brand secondary color

    # Contact information
    address = Column(Text)
    phone = Column(String)
    website = Column(String)

    # Settings
    timezone = Column(String, default="America/New_York")
    date_format = Column(String, default="MM/DD/YYYY")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="organization")


class User(Base):
    """User account with RBAC"""
    __tablename__ = "users"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, nullable=False, unique=True, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.organizations.id"))
    role = Column(SQLEnum(RoleEnum, name="user_role"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    oidc_subject = Column(String, index=True)  # OIDC 'sub' claim
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))

    # Relationships
    organization = relationship("Organization", back_populates="users")


class LoginAuditLog(Base):
    """Login attempts for security auditing"""
    __tablename__ = "login_audit_logs"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, nullable=False, index=True)
    success = Column(Boolean, nullable=False)
    ip_address = Column(INET)
    user_agent = Column(Text)
    error_message = Column(Text)
    attempted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)


class UserInvitation(Base):
    """User invitation for onboarding"""
    __tablename__ = "user_invitations"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, nullable=False, index=True)
    organization_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.organizations.id"), nullable=False)
    role = Column(SQLEnum(RoleEnum, name="user_role"), nullable=False)
    invited_by_user_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), nullable=False)
    token = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True))
    is_expired = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class UserPermission(Base):
    """Granular permissions for users"""
    __tablename__ = "user_permissions"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), nullable=False)

    # Engagement permissions
    can_create_engagements = Column(Boolean, default=False)
    can_edit_engagements = Column(Boolean, default=False)
    can_delete_engagements = Column(Boolean, default=False)
    can_view_all_engagements = Column(Boolean, default=False)

    # User management permissions
    can_invite_users = Column(Boolean, default=False)
    can_manage_users = Column(Boolean, default=False)
    can_manage_roles = Column(Boolean, default=False)

    # Firm settings permissions
    can_edit_firm_settings = Column(Boolean, default=False)
    can_manage_billing = Column(Boolean, default=False)

    # Document permissions
    can_upload_documents = Column(Boolean, default=True)
    can_delete_documents = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
