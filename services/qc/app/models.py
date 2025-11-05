"""SQLAlchemy ORM models for QC Service"""
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
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from .database import Base


class QCCheckStatus(str, Enum):
    """QC check result status"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WAIVED = "waived"


class QCPolicy(Base):
    """QC Policy definition"""
    __tablename__ = "qc_policies"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_code = Column(String, nullable=False, unique=True, index=True)
    policy_name = Column(String, nullable=False)
    description = Column(Text)
    is_blocking = Column(Boolean, nullable=False, default=True)
    standard_reference = Column(String)  # 'PCAOB AS 1215', 'AICPA SAS 142', etc.
    check_logic = Column(JSONB, nullable=False)  # Structured rules
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    checks = relationship("QCCheck", back_populates="policy")


class QCCheck(Base):
    """QC check execution result"""
    __tablename__ = "qc_checks"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.qc_policies.id"), nullable=False)
    executed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    status = Column(SQLEnum(QCCheckStatus, name="qc_check_status"), nullable=False, default=QCCheckStatus.PENDING)
    result_data = Column(JSONB)  # Details of pass/fail, evidence, etc.
    waived_by = Column(PGUUID(as_uuid=True))  # User who waived the check
    waived_at = Column(DateTime(timezone=True))
    waiver_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    policy = relationship("QCPolicy", back_populates="checks")
