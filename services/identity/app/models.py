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
    """CPA Firm (renamed from organizations to match actual schema)"""
    __tablename__ = "cpa_firms"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    firm_name = Column(String, nullable=False)
    legal_name = Column(String)
    ein = Column(String)

    # Contact information
    primary_contact_name = Column(String)
    primary_contact_email = Column(String, nullable=False)
    primary_contact_phone = Column(String)

    # Firm branding
    logo_url = Column(Text)
    primary_color = Column(String)
    secondary_color = Column(String)

    # Settings
    require_two_factor_auth = Column(Boolean, default=False)
    session_timeout_minutes = Column(String, default=30)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="organization")


class User(Base):
    """User account with RBAC"""
    __tablename__ = "users"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    cpa_firm_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.cpa_firms.id"))
    client_id = Column(PGUUID(as_uuid=True))
    email = Column(String, nullable=False, unique=True, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    password_hash = Column(String)
    require_password_change = Column(Boolean, default=False)
    last_password_change = Column(DateTime(timezone=True))
    failed_login_attempts = Column(String, default=0)
    locked_until = Column(DateTime(timezone=True))
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String)
    last_login_at = Column(DateTime(timezone=True))
    last_activity_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, nullable=False, default=True)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(PGUUID(as_uuid=True))

    # Relationships
    organization = relationship("Organization", back_populates="users")

    @property
    def full_name(self):
        """Computed property for backwards compatibility"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email

    @property
    def hashed_password(self):
        """Alias for backwards compatibility"""
        return self.password_hash

    @hashed_password.setter
    def hashed_password(self, value):
        """Alias setter for backwards compatibility"""
        self.password_hash = value

    @property
    def organization_id(self):
        """Alias for backwards compatibility"""
        return self.cpa_firm_id

    @organization_id.setter
    def organization_id(self, value):
        """Alias setter for backwards compatibility"""
        self.cpa_firm_id = value


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
