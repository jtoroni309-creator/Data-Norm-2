"""
SQLAlchemy ORM Models for AI Training Infrastructure

This module provides Python data models for the comprehensive AI training database schema.
Models are organized by functional area and include full type hints for IDE support.

Usage:
    from database.models.ai_training_models import JournalEntryMetadata, FeatureStore
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('postgresql://user:pass@localhost/atlas')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query example
    high_risk_entries = session.query(JournalEntryMetadata).filter(
        JournalEntryMetadata.fraud_risk_score > 0.8
    ).all()
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, Integer, String, Text, Numeric, Date, DateTime,
    JSON, ARRAY, ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()


# ============================================================================
# SECTION 1: ENHANCED TRANSACTION & FINANCIAL DATA
# ============================================================================

class JournalEntryMetadata(Base):
    """
    Enhanced metadata for journal entries capturing 50+ derived features
    for pattern recognition, anomaly detection, and risk assessment.

    This table extends journal_entries with temporal, behavioral, and
    statistical features that enable AI models to detect patterns
    humans would miss.
    """
    __tablename__ = "journal_entry_metadata"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    journal_entry_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Temporal features (15 variables)
    time_of_day_category: Mapped[Optional[str]] = mapped_column(String(20))
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer)
    day_of_month: Mapped[Optional[int]] = mapped_column(Integer)
    week_of_year: Mapped[Optional[int]] = mapped_column(Integer)
    quarter: Mapped[Optional[int]] = mapped_column(Integer)
    is_month_end: Mapped[bool] = mapped_column(Boolean, default=False)
    is_quarter_end: Mapped[bool] = mapped_column(Boolean, default=False)
    is_year_end: Mapped[bool] = mapped_column(Boolean, default=False)
    days_from_period_close: Mapped[Optional[int]] = mapped_column(Integer)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False)
    business_day_of_month: Mapped[Optional[int]] = mapped_column(Integer)

    # Behavioral features (10 variables)
    posting_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    approving_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    modified_count: Mapped[int] = mapped_column(Integer, default=0)
    time_to_approve_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    is_rush_posting: Mapped[bool] = mapped_column(Boolean, default=False)

    # Transaction characteristics (15 variables)
    line_count: Mapped[int] = mapped_column(Integer, nullable=False)
    account_diversity_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    debit_credit_balance_check: Mapped[bool] = mapped_column(Boolean, default=True)
    has_foreign_currency: Mapped[bool] = mapped_column(Boolean, default=False)
    currency_count: Mapped[int] = mapped_column(Integer, default=1)
    max_line_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    min_line_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    avg_line_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    std_dev_line_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))

    # Anomaly indicators (10 variables)
    is_round_dollar: Mapped[bool] = mapped_column(Boolean, default=False)
    round_dollar_divisor: Mapped[Optional[int]] = mapped_column(Integer)
    is_statistical_outlier: Mapped[bool] = mapped_column(Boolean, default=False)
    outlier_zscore: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    is_duplicate_suspected: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_similarity_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

    # Relationships (5 variables)
    has_supporting_documents: Mapped[bool] = mapped_column(Boolean, default=False)
    document_count: Mapped[int] = mapped_column(Integer, default=0)
    has_approval_workflow: Mapped[bool] = mapped_column(Boolean, default=False)
    linked_procedure_count: Mapped[int] = mapped_column(Integer, default=0)

    # Risk indicators (3 variables)
    fraud_risk_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    misstatement_risk_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    complexity_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

    # ML features
    features: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    embedding_vector = mapped_column(Vector(1536))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("fraud_risk_score BETWEEN 0 AND 1", name="ck_fraud_risk_score"),
        CheckConstraint("misstatement_risk_score BETWEEN 0 AND 1", name="ck_misstatement_risk_score"),
        CheckConstraint("complexity_score BETWEEN 0 AND 1", name="ck_complexity_score"),
        Index("idx_je_metadata_time_patterns", "day_of_week", "time_of_day_category", "is_month_end"),
        Index("idx_je_metadata_risk_scores", "fraud_risk_score", "misstatement_risk_score"),
        Index("idx_je_metadata_anomalies", "is_round_dollar", "is_statistical_outlier", "is_duplicate_suspected"),
    )


class TransactionSequence(Base):
    """
    Identifies and tracks recurring transaction patterns, batch processes,
    and sequences for anomaly detection.

    Examples: recurring payroll, monthly close batches, adjustment chains,
    reversal pairs (fraud indicator).
    """
    __tablename__ = "transaction_sequences"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False)

    # Sequence identification
    sequence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sequence_identifier: Mapped[Optional[str]] = mapped_column(String(255))

    # Sequence members
    journal_entry_ids: Mapped[List[UUID]] = mapped_column(ARRAY(PG_UUID(as_uuid=True)), nullable=False)
    entry_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Temporal analysis
    first_entry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_entry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    frequency_days: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    is_regular_frequency: Mapped[bool] = mapped_column(Boolean, default=False)

    # Amount analysis
    total_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    avg_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    amount_variance: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    is_consistent_amount: Mapped[bool] = mapped_column(Boolean, default=False)

    # Pattern characteristics
    accounts_involved: Mapped[List[str]] = mapped_column(ARRAY(String(255)))
    is_automated: Mapped[bool] = mapped_column(Boolean, default=False)
    source_system: Mapped[Optional[str]] = mapped_column(String(100))

    # Risk assessment
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)
    suspicion_reasons: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    requires_testing: Mapped[bool] = mapped_column(Boolean, default=False)

    # AI insights
    pattern_confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    detected_by_model: Mapped[Optional[str]] = mapped_column(String(100))
    detection_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("pattern_confidence BETWEEN 0 AND 1", name="ck_pattern_confidence"),
        Index("idx_txn_sequences_engagement", "engagement_id"),
        Index("idx_txn_sequences_type", "sequence_type"),
        Index("idx_txn_sequences_suspicious", "is_suspicious", "requires_testing"),
    )


class AccountBalanceHistory(Base):
    """
    Time-series tracking of account balances with trend analysis,
    statistical features, and anomaly detection.

    Captures 30+ features per account per period for trend detection
    and comparative analysis.
    """
    __tablename__ = "account_balance_history"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chart_of_accounts.id", ondelete="CASCADE"), nullable=False)

    # Period identification
    period_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    fiscal_period: Mapped[int] = mapped_column(Integer, nullable=False)

    # Balance information
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    period_change: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    period_change_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    # Activity metrics
    debit_count: Mapped[int] = mapped_column(Integer, default=0)
    credit_count: Mapped[int] = mapped_column(Integer, default=0)
    total_debits: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    total_credits: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    net_change: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)

    # Statistical features
    avg_transaction_size: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    max_transaction_size: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    min_transaction_size: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    std_dev_transaction_size: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))

    # Trend indicators
    moving_avg_3_period: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    moving_avg_6_period: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    moving_avg_12_period: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    trend_direction: Mapped[Optional[str]] = mapped_column(String(20))
    volatility_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

    # Anomaly detection
    is_anomalous: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    expected_balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    variance_from_expected: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))

    # Comparative analysis
    prior_period_balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    year_over_year_change: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    year_over_year_change_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    industry_benchmark_balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    variance_from_benchmark_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    # Metadata
    data_quality_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    completeness_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("engagement_id", "account_id", "period_date", "period_type", name="uq_account_balance_history"),
        CheckConstraint("period_type IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')", name="ck_period_type"),
        CheckConstraint("data_quality_score BETWEEN 0 AND 1", name="ck_data_quality_score"),
        CheckConstraint("completeness_score BETWEEN 0 AND 1", name="ck_completeness_score"),
        Index("idx_acct_balance_history_engagement_account", "engagement_id", "account_id", "period_date"),
        Index("idx_acct_balance_history_anomalies", "is_anomalous", "anomaly_score"),
        Index("idx_acct_balance_history_trends", "trend_direction", "volatility_score"),
    )


# ============================================================================
# SECTION 2: AI TRAINING INFRASTRUCTURE
# ============================================================================

class FeatureStore(Base):
    """
    Centralized feature repository for ML models with statistics,
    importance scores, and versioning.

    Stores metadata for 500+ features used across all AI models.
    """
    __tablename__ = "feature_store"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Feature identification
    feature_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    feature_group: Mapped[str] = mapped_column(String(100), nullable=False)
    feature_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Feature definition
    description: Mapped[str] = mapped_column(Text, nullable=False)
    calculation_logic: Mapped[str] = mapped_column(Text, nullable=False)
    dependencies: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # Data type and constraints
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)
    min_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    max_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    allowed_values: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    is_nullable: Mapped[bool] = mapped_column(Boolean, default=False)

    # Feature statistics
    mean_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    std_dev: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    percentile_25: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    percentile_50: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    percentile_75: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    percentile_95: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    percentile_99: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4))
    missing_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

    # Feature importance
    importance_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    importance_rank: Mapped[Optional[int]] = mapped_column(Integer)
    models_using_feature: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # Feature quality
    data_quality_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    stability_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    correlation_with_target: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deprecated_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    replacement_feature_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("feature_store.id"))

    # Metadata
    created_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    last_updated_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("feature_type IN ('numerical', 'categorical', 'boolean', 'text', 'embedding', 'derived')", name="ck_feature_type"),
        CheckConstraint("importance_score BETWEEN 0 AND 1", name="ck_importance_score"),
        CheckConstraint("data_quality_score BETWEEN 0 AND 1", name="ck_dq_score"),
        CheckConstraint("stability_score BETWEEN 0 AND 1", name="ck_stability_score"),
        Index("idx_feature_store_group_type", "feature_group", "feature_type"),
        Index("idx_feature_store_importance", "importance_score"),
        Index("idx_feature_store_active", "is_active", "deprecated_date"),
    )


class TrainingDataset(Base):
    """
    Version-controlled training datasets for reproducible model training.

    Each dataset is immutable and tracks features, labels, quality metrics,
    and usage across model experiments.
    """
    __tablename__ = "training_datasets"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Dataset identification
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    dataset_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Purpose and scope
    purpose: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Data selection criteria
    engagement_criteria: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    date_range_start: Mapped[Optional[date]] = mapped_column(Date)
    date_range_end: Mapped[Optional[date]] = mapped_column(Date)
    included_engagement_ids: Mapped[Optional[List[UUID]]] = mapped_column(ARRAY(PG_UUID(as_uuid=True)))
    excluded_engagement_ids: Mapped[Optional[List[UUID]]] = mapped_column(ARRAY(PG_UUID(as_uuid=True)))

    # Features and labels
    feature_names: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    label_column: Mapped[Optional[str]] = mapped_column(String(255))
    label_type: Mapped[Optional[str]] = mapped_column(String(50))
    class_distribution: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    # Dataset statistics
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    positive_class_count: Mapped[Optional[int]] = mapped_column(Integer)
    negative_class_count: Mapped[Optional[int]] = mapped_column(Integer)
    class_balance_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    feature_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Data quality
    completeness_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    quality_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    has_duplicates: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0)

    # Storage information
    storage_location: Mapped[str] = mapped_column(Text, nullable=False)
    storage_format: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size_mb: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    compression_type: Mapped[Optional[str]] = mapped_column(String(50))

    # Versioning and lineage
    parent_dataset_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("training_datasets.id"))
    is_latest_version: Mapped[bool] = mapped_column(Boolean, default=True)

    # Usage tracking
    model_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Metadata
    created_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("dataset_name", "dataset_version", name="uq_training_dataset"),
        CheckConstraint("dataset_type IN ('training', 'validation', 'test', 'production')", name="ck_dataset_type"),
        CheckConstraint("label_type IN ('binary', 'multiclass', 'regression', 'multilabel')", name="ck_label_type"),
        CheckConstraint("completeness_score BETWEEN 0 AND 1", name="ck_completeness_score"),
        CheckConstraint("quality_score BETWEEN 0 AND 1", name="ck_quality_score"),
        Index("idx_training_datasets_purpose", "purpose", "is_latest_version"),
        Index("idx_training_datasets_type", "dataset_type", "created_at"),
    )


class TrainingLabel(Base):
    """
    Ground truth labels for supervised learning with multi-expert consensus.

    Captures labels from human experts with confidence scores, validation,
    and agreement tracking for high-quality training data.
    """
    __tablename__ = "training_labels"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Label identification
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    engagement_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"))

    # Label information
    label_type: Mapped[str] = mapped_column(String(100), nullable=False)
    label_value: Mapped[str] = mapped_column(Text, nullable=False)
    label_confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

    # Label source
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    labeler_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    labeler_role: Mapped[Optional[str]] = mapped_column(String(50))
    labeling_method: Mapped[Optional[str]] = mapped_column(String(100))

    # Quality and validation
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    validation_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    validated_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    validation_method: Mapped[Optional[str]] = mapped_column(String(100))

    # Multi-labeler consensus
    total_labelers: Mapped[int] = mapped_column(Integer, default=1)
    agreement_count: Mapped[int] = mapped_column(Integer, default=1)
    agreement_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    alternative_labels: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    # Context information
    labeling_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    evidence_ids: Mapped[Optional[List[UUID]]] = mapped_column(ARRAY(PG_UUID(as_uuid=True)))
    rationale: Mapped[Optional[str]] = mapped_column(Text)

    # Temporal information
    label_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    effective_date: Mapped[Optional[date]] = mapped_column(Date)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date)

    # Usage tracking
    used_in_training: Mapped[bool] = mapped_column(Boolean, default=False)
    training_dataset_ids: Mapped[Optional[List[UUID]]] = mapped_column(ARRAY(PG_UUID(as_uuid=True)))
    model_versions_trained: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # Metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("source_type IN ('human_expert', 'model_prediction', 'rule_based', 'peer_review', 'regulatory')", name="ck_source_type"),
        CheckConstraint("label_confidence BETWEEN 0 AND 1", name="ck_label_confidence"),
        CheckConstraint("agreement_score BETWEEN 0 AND 1", name="ck_agreement_score"),
        Index("idx_training_labels_entity", "entity_type", "entity_id"),
        Index("idx_training_labels_type", "label_type", "label_value"),
        Index("idx_training_labels_engagement", "engagement_id"),
        Index("idx_training_labels_validated", "is_validated", "validation_date"),
        Index("idx_training_labels_source", "source_type", "labeler_user_id"),
    )


class ModelExperiment(Base):
    """
    Complete MLOps tracking for model experiments including hyperparameters,
    performance metrics, and artifacts.

    Tracks 100+ experiments with full reproducibility and comparison metrics.
    """
    __tablename__ = "model_experiments"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Experiment identification
    experiment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    experiment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    model_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Model architecture
    algorithm: Mapped[str] = mapped_column(String(100), nullable=False)
    framework: Mapped[Optional[str]] = mapped_column(String(50))
    model_architecture: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    hyperparameters: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Training configuration
    training_dataset_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("training_datasets.id"))
    validation_dataset_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("training_datasets.id"))
    test_dataset_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("training_datasets.id"))
    features_used: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    feature_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Training execution
    training_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    training_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    training_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    epochs: Mapped[Optional[int]] = mapped_column(Integer)
    batch_size: Mapped[Optional[int]] = mapped_column(Integer)
    learning_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8))
    early_stopping_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    stopped_early: Mapped[bool] = mapped_column(Boolean, default=False)

    # Model performance metrics - Classification
    accuracy: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    precision_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    recall_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    f1_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    roc_auc: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    pr_auc: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))

    # Model performance metrics - Regression
    mae: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 6))
    mse: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 6))
    rmse: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 6))
    r2_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))

    # Business metrics
    false_positive_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    false_negative_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    true_positive_count: Mapped[Optional[int]] = mapped_column(Integer)
    false_positive_count: Mapped[Optional[int]] = mapped_column(Integer)
    true_negative_count: Mapped[Optional[int]] = mapped_column(Integer)
    false_negative_count: Mapped[Optional[int]] = mapped_column(Integer)

    # Feature importance
    feature_importance: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    top_10_features: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # Model artifacts
    model_artifact_uri: Mapped[Optional[str]] = mapped_column(Text)
    checkpoint_uri: Mapped[Optional[str]] = mapped_column(Text)
    tensorboard_uri: Mapped[Optional[str]] = mapped_column(Text)

    # Comparison with baseline
    baseline_model_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("model_experiments.id"))
    improvement_over_baseline: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    is_best_model: Mapped[bool] = mapped_column(Boolean, default=False)

    # Production readiness
    is_production_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    passed_validation: Mapped[bool] = mapped_column(Boolean, default=False)
    deployed_to_production: Mapped[bool] = mapped_column(Boolean, default=False)
    deployment_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Resource utilization
    gpu_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    cpu_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    memory_peak_gb: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    training_cost_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Metadata
    researcher_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    git_commit_hash: Mapped[Optional[str]] = mapped_column(String(40))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("experiment_name", "experiment_number", name="uq_model_experiment"),
        Index("idx_model_experiments_type", "model_type", "f1_score"),
        Index("idx_model_experiments_best", "is_best_model", "is_production_ready"),
        Index("idx_model_experiments_performance", "roc_auc", "f1_score"),
    )


class ModelPrediction(Base):
    """
    Every prediction tracked with explainability and feedback loop.

    Enables continuous learning from production data and human corrections.
    """
    __tablename__ = "model_predictions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Prediction identification
    model_experiment_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("model_experiments.id"))
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Entity being predicted
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    engagement_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"))

    # Prediction details
    prediction_type: Mapped[str] = mapped_column(String(100), nullable=False)
    predicted_value: Mapped[str] = mapped_column(Text, nullable=False)
    prediction_confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    prediction_probabilities: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    # Model explanation (XAI - Explainable AI)
    feature_contributions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    top_influencing_features: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    explanation_text: Mapped[Optional[str]] = mapped_column(Text)

    # Prediction context
    input_features: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    prediction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    inference_time_ms: Mapped[Optional[int]] = mapped_column(Integer)

    # Validation and feedback
    actual_value: Mapped[Optional[str]] = mapped_column(Text)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean)
    prediction_error: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 6))

    # Human feedback
    feedback_received: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    feedback_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    feedback_type: Mapped[Optional[str]] = mapped_column(String(50))
    feedback_comments: Mapped[Optional[str]] = mapped_column(Text)

    # Impact tracking
    action_taken: Mapped[Optional[str]] = mapped_column(String(100))
    action_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    action_user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))

    # Model monitoring
    is_anomalous_prediction: Mapped[bool] = mapped_column(Boolean, default=False)
    drift_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    requires_review: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    review_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reviewer_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("prediction_confidence BETWEEN 0 AND 1", name="ck_prediction_confidence"),
        CheckConstraint("feedback_type IN ('correct', 'incorrect', 'partially_correct', 'unsure')", name="ck_feedback_type"),
        Index("idx_model_predictions_entity", "entity_type", "entity_id"),
        Index("idx_model_predictions_model", "model_experiment_id", "prediction_timestamp"),
        Index("idx_model_predictions_engagement", "engagement_id"),
        Index("idx_model_predictions_feedback", "feedback_received", "is_correct"),
        Index("idx_model_predictions_review", "requires_review", "reviewed"),
    )


class HumanFeedback(Base):
    """
    Captures expert corrections and feedback for continuous learning.

    Creates a virtuous cycle where human experts improve AI models
    with every correction.
    """
    __tablename__ = "human_feedback"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Feedback identification
    feedback_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    engagement_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"))

    # User providing feedback
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_role: Mapped[str] = mapped_column(String(50), nullable=False)
    user_expertise_level: Mapped[Optional[str]] = mapped_column(String(50))

    # Original prediction (if applicable)
    original_prediction_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("model_predictions.id"))
    original_value: Mapped[Optional[str]] = mapped_column(Text)
    original_confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

    # Corrected information
    corrected_value: Mapped[Optional[str]] = mapped_column(Text)
    correction_confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    correction_rationale: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_evidence_ids: Mapped[Optional[List[UUID]]] = mapped_column(ARRAY(PG_UUID(as_uuid=True)))

    # Feedback details
    feedback_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    is_critical_feedback: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_model_retrain: Mapped[bool] = mapped_column(Boolean, default=False)

    # Processing status
    status: Mapped[str] = mapped_column(String(50), default='pending', nullable=False)
    reviewed_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    review_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    review_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Impact tracking
    incorporated_in_dataset_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("training_datasets.id"))
    incorporated_in_model_version: Mapped[Optional[str]] = mapped_column(String(50))
    incorporation_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Quality scoring
    feedback_quality_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    agreement_with_other_experts: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

    # Metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("user_expertise_level IN ('junior', 'senior', 'manager', 'partner', 'expert')", name="ck_expertise_level"),
        CheckConstraint("status IN ('pending', 'reviewed', 'incorporated', 'rejected', 'deferred')", name="ck_status"),
        CheckConstraint("correction_confidence BETWEEN 0 AND 1", name="ck_correction_confidence"),
        CheckConstraint("feedback_quality_score BETWEEN 0 AND 1", name="ck_feedback_quality_score"),
        Index("idx_human_feedback_entity", "entity_type", "entity_id"),
        Index("idx_human_feedback_user", "user_id", "created_at"),
        Index("idx_human_feedback_status", "status", "requires_model_retrain"),
        Index("idx_human_feedback_engagement", "engagement_id"),
    )


# Export all models
__all__ = [
    'Base',
    'JournalEntryMetadata',
    'TransactionSequence',
    'AccountBalanceHistory',
    'FeatureStore',
    'TrainingDataset',
    'TrainingLabel',
    'ModelExperiment',
    'ModelPrediction',
    'HumanFeedback',
]
