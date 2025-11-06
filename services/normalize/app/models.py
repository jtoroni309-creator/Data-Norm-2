"""SQLAlchemy ORM models for Normalize Service"""
from datetime import datetime
from uuid import uuid4
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Float,
    Integer,
    ForeignKey,
    Text,
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

class MappingConfidence(str, Enum):
    """Confidence level of mapping suggestion"""
    LOW = "low"          # < 60%
    MEDIUM = "medium"    # 60-75%
    HIGH = "high"        # 75-90%
    VERY_HIGH = "very_high"  # > 90%


class MappingStatus(str, Enum):
    """Status of account mapping"""
    UNMAPPED = "unmapped"
    SUGGESTED = "suggested"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    MANUAL = "manual"


# ========================================
# ORM Models
# ========================================

class MappingRule(Base):
    """
    Account mapping rule

    Stores patterns and rules for mapping trial balance accounts
    to standard chart of accounts.
    """
    __tablename__ = "mapping_rules"
    __table_args__ = (
        Index("idx_mapping_rules_pattern", "source_pattern"),
        Index("idx_mapping_rules_account", "target_account_code"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_name = Column(String, nullable=False)
    description = Column(Text)
    source_pattern = Column(String, nullable=False)  # Regex or keyword pattern
    target_account_code = Column(String, nullable=False)
    priority = Column(Integer, default=0)  # Higher priority rules evaluated first
    is_active = Column(Boolean, default=True)
    is_regex = Column(Boolean, default=False)
    confidence_boost = Column(Float, default=0.0)  # Additional confidence for this rule
    created_by = Column(PGUUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class MLModel(Base):
    """
    ML model version tracking

    Tracks trained machine learning models for account mapping.
    Stores model metadata, performance metrics, and file location.
    """
    __tablename__ = "ml_models"
    __table_args__ = (
        Index("idx_ml_models_version", "model_version"),
        Index("idx_ml_models_active", "is_active"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False, unique=True)
    model_type = Column(String, nullable=False)  # 'random_forest', 'neural_network', etc.
    model_path = Column(String)  # Path to serialized model file
    training_samples = Column(Integer, nullable=False)
    accuracy = Column(Float)  # Overall accuracy
    precision = Column(Float)  # Precision score
    recall = Column(Float)  # Recall score
    f1_score = Column(Float)  # F1 score
    feature_importance = Column(JSONB)  # Feature importance scores
    hyperparameters = Column(JSONB)  # Model hyperparameters
    is_active = Column(Boolean, default=False)  # Only one model can be active
    trained_by = Column(PGUUID(as_uuid=True))
    trained_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class MappingSuggestion(Base):
    """
    ML-generated mapping suggestion

    Stores machine learning suggestions for mapping trial balance
    accounts to chart of accounts.
    """
    __tablename__ = "mapping_suggestions"
    __table_args__ = (
        Index("idx_mapping_suggestions_engagement", "engagement_id"),
        Index("idx_mapping_suggestions_tb_line", "trial_balance_line_id"),
        Index("idx_mapping_suggestions_status", "status"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=False)
    trial_balance_line_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Source account info (from trial balance)
    source_account_code = Column(String, nullable=False)
    source_account_name = Column(String, nullable=False)

    # Suggested mapping
    suggested_account_code = Column(String, nullable=False)
    suggested_account_name = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    confidence_level = Column(
        SQLEnum(MappingConfidence, name="mapping_confidence", create_type=False),
        nullable=False
    )

    # ML model info
    model_version = Column(String)
    model_features = Column(JSONB)  # Features used for prediction

    # Alternative suggestions
    alternatives = Column(JSONB)  # List of alternative mappings with scores

    # Status and feedback
    status = Column(
        SQLEnum(MappingStatus, name="mapping_status", create_type=False),
        nullable=False,
        default=MappingStatus.SUGGESTED
    )
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    feedback_notes = Column(Text)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class MappingHistory(Base):
    """
    Historical account mappings

    Stores confirmed mappings to build training data for ML models.
    Used for continuous improvement of mapping suggestions.
    """
    __tablename__ = "mapping_history"
    __table_args__ = (
        Index("idx_mapping_history_engagement", "engagement_id"),
        Index("idx_mapping_history_source", "source_account_code", "source_account_name"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Source account
    source_account_code = Column(String, nullable=False)
    source_account_name = Column(String, nullable=False)
    source_account_balance = Column(Float)

    # Mapped account
    mapped_account_code = Column(String, nullable=False)
    mapped_account_name = Column(String, nullable=False)

    # Mapping method
    mapping_method = Column(String)  # 'ml', 'rule', 'manual'
    confidence_score = Column(Float)

    # Audit trail
    mapped_by = Column(PGUUID(as_uuid=True), nullable=False)
    mapped_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
