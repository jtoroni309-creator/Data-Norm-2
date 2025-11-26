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
    Integer,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, INET, JSONB
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


class SubscriptionTierEnum(str, Enum):
    """Subscription tier levels - values must match PostgreSQL enum exactly"""
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"


class SubscriptionStatusEnum(str, Enum):
    """Subscription status values - values must match PostgreSQL enum exactly"""
    active = "active"
    trial = "trial"
    suspended = "suspended"
    cancelled = "cancelled"


class ClientStatusEnum(str, Enum):
    """Client status values"""
    active = "active"
    inactive = "inactive"
    onboarding = "onboarding"
    terminated = "terminated"


class ClientEntityTypeEnum(str, Enum):
    """Client entity type values"""
    c_corporation = "c_corporation"
    s_corporation = "s_corporation"
    llc = "llc"
    partnership = "partnership"
    sole_proprietorship = "sole_proprietorship"
    nonprofit = "nonprofit"
    government = "government"
    other = "other"


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
    session_timeout_minutes = Column(Integer, default=30)

    # Subscription & Service Access
    # PostgreSQL enum types - columns are defined as enums in the database but we store as string
    # SQLAlchemy will read them as strings, writing requires explicit cast
    subscription_tier = Column(String, default="professional")
    subscription_status = Column(String, default="active")
    max_users = Column(Integer, default=10)
    # enabled_services = Column(JSONB, default={}, nullable=True)  # JSON object with service_id: true/false - Column doesn't exist in DB yet

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="organization")
    clients = relationship("Client", back_populates="cpa_firm")


class Client(Base):
    """Audit clients of CPA firms"""
    __tablename__ = "clients"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    cpa_firm_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.cpa_firms.id"), nullable=False)

    # Client information
    client_name = Column(String, nullable=False)
    legal_name = Column(String)
    ein = Column(String)
    # entity_type is a PostgreSQL enum, but we don't include it in insert to use default
    # entity_type = Column(String)

    # Contact information
    primary_contact_name = Column(String)
    primary_contact_email = Column(String)
    primary_contact_phone = Column(String)

    # Address
    address_line1 = Column(String)
    address_line2 = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String, default="USA")

    # Fiscal information
    fiscal_year_end = Column(String)
    industry_code = Column(String)

    # Status - Don't set default value, let the database handle it
    client_status = Column("client_status", String)
    onboarding_completed_at = Column(DateTime(timezone=True))

    # Client portal settings
    portal_enabled = Column(Boolean, default=True)
    portal_custom_domain = Column(String)
    portal_logo_url = Column(Text)

    # Feature flags
    allow_document_upload = Column(Boolean, default=True)
    allow_confirmation_response = Column(Boolean, default=True)
    allow_data_export = Column(Boolean, default=False)
    allow_report_download = Column(Boolean, default=True)
    allow_messaging = Column(Boolean, default=True)
    allow_financial_view = Column(Boolean, default=True)

    # Engagement defaults
    default_engagement_type = Column(String, default="audit")

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(PGUUID(as_uuid=True))

    # Relationships
    cpa_firm = relationship("Organization", back_populates="clients")

    @property
    def name(self):
        """Alias for backwards compatibility"""
        return self.client_name

    @name.setter
    def name(self, value):
        """Alias setter for backwards compatibility"""
        self.client_name = value

    @property
    def status(self):
        """Alias for backwards compatibility"""
        return self.client_status

    @status.setter
    def status(self, value):
        """Alias setter for backwards compatibility"""
        self.client_status = value

    @property
    def organization_id(self):
        """Alias for backwards compatibility"""
        return self.cpa_firm_id

    @organization_id.setter
    def organization_id(self, value):
        """Alias setter for backwards compatibility"""
        self.cpa_firm_id = value


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
    failed_login_attempts = Column(Integer, default=0)
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

    @full_name.setter
    def full_name(self, value):
        """Setter that splits full name into first_name and last_name"""
        if value:
            parts = value.strip().split(" ", 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else ""
        else:
            self.first_name = None
            self.last_name = None

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


class PasswordResetToken(Base):
    """Password reset tokens"""
    __tablename__ = "password_reset_tokens"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.users.id"), nullable=False)
    token = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
