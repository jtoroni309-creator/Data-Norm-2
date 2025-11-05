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
