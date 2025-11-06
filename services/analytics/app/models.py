"""SQLAlchemy ORM models for Analytics Service"""
from datetime import datetime
from uuid import uuid4
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    ForeignKey,
    Text,
    Numeric,
    Boolean,
    Enum as SQLEnum,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from .database import Base


# ========================================
# Enums
# ========================================

class AnomalySeverity(str, Enum):
    """Severity level of detected anomaly"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResolutionStatus(str, Enum):
    """Status of anomaly resolution"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


# ========================================
# ORM Models
# ========================================

class AnalyticsRule(Base):
    """
    Analytics rule definition

    Defines rules for journal entry testing, ratio analysis, outlier detection, etc.
    Each rule has configuration parameters stored as JSONB.
    """
    __tablename__ = "analytics_rules"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_code = Column(String, nullable=False, unique=True, index=True)
    rule_name = Column(Text, nullable=False)
    description = Column(Text)
    category = Column(String)  # 'je_testing', 'ratio_analysis', 'outlier_detection'
    is_active = Column(Boolean, nullable=False, default=True)
    config = Column(JSONB)  # Rule-specific parameters
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    results = relationship("AnalyticsResult", back_populates="rule")


class AnalyticsResult(Base):
    """
    Analytics execution result

    Stores the result of running an analytics rule on an engagement.
    Includes findings count and model version for ML-based rules.
    """
    __tablename__ = "analytics_results"
    __table_args__ = (
        Index("idx_analytics_engagement", "engagement_id"),
        Index("idx_analytics_rule", "rule_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=False)
    rule_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.analytics_rules.id"),
        nullable=False
    )
    executed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    executed_by = Column(PGUUID(as_uuid=True))
    result_data = Column(JSONB, nullable=False)  # Rule-specific results
    findings_count = Column(Integer, nullable=False, default=0)
    model_version = Column(String)  # For ML models
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    rule = relationship("AnalyticsRule", back_populates="results")
    anomalies = relationship("Anomaly", back_populates="analytics_result")


class Anomaly(Base):
    """
    Detected anomaly

    Represents a detected anomaly from analytics rules.
    Includes severity, evidence, and resolution workflow.
    """
    __tablename__ = "anomalies"
    __table_args__ = (
        Index("idx_anomalies_engagement", "engagement_id"),
        Index("idx_anomalies_type", "anomaly_type"),
        Index("idx_anomalies_severity", "severity"),
        Index("idx_anomalies_status", "resolution_status"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=False)
    analytics_result_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.analytics_results.id")
    )
    anomaly_type = Column(String, nullable=False)  # 'round_dollar_je', 'weekend_je', etc.
    severity = Column(
        SQLEnum(AnomalySeverity, name="anomaly_severity", create_type=False),
        nullable=False,
        default=AnomalySeverity.MEDIUM
    )
    title = Column(Text, nullable=False)
    description = Column(Text)
    evidence = Column(JSONB, nullable=False)  # Links to JEs, TB lines, etc.
    score = Column(Numeric(5, 2))  # Anomaly score or confidence
    resolution_status = Column(String, nullable=False, default="open")
    resolved_by = Column(PGUUID(as_uuid=True))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    analytics_result = relationship("AnalyticsResult", back_populates="anomalies")
