"""
Fraud Detection Service - Database Models

SQLAlchemy models for fraud detection, bank integrations, and case management.
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
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import relationship

from .database import Base


# Enums
class FraudCaseStatus(str, Enum):
    """Status of a fraud case"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONFIRMED_FRAUD = "confirmed_fraud"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    CLOSED = "closed"


class FraudSeverity(str, Enum):
    """Severity level of fraud detection"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TransactionType(str, Enum):
    """Type of financial transaction"""
    DEBIT = "debit"
    CREDIT = "credit"
    TRANSFER = "transfer"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    ADJUSTMENT = "adjustment"


class BankAccountStatus(str, Enum):
    """Status of bank account connection"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    REAUTH_REQUIRED = "reauth_required"


class RuleType(str, Enum):
    """Type of fraud detection rule"""
    THRESHOLD = "threshold"
    VELOCITY = "velocity"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    BLACKLIST = "blacklist"
    GEOGRAPHIC = "geographic"
    BEHAVIORAL = "behavioral"


class AlertStatus(str, Enum):
    """Status of fraud alert"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


# Models
class BankAccount(Base):
    """
    Bank account connected via Plaid for transaction monitoring.

    Stores encrypted credentials and connection metadata.
    """
    __tablename__ = "bank_accounts"
    __table_args__ = (
        Index("idx_bank_customer_id", "customer_id"),
        Index("idx_bank_status", "status"),
        {"schema": "fraud_detection"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Plaid connection details
    plaid_item_id = Column(String(255), unique=True, nullable=False)
    plaid_access_token_encrypted = Column(Text, nullable=False)  # Encrypted
    plaid_account_id = Column(String(255), nullable=False)

    # Account information
    account_name = Column(String(255))
    account_mask = Column(String(10))  # Last 4 digits
    account_type = Column(String(50))  # checking, savings, credit
    account_subtype = Column(String(50))
    institution_id = Column(String(255))
    institution_name = Column(String(255))

    # Monitoring settings
    status = Column(SQLEnum(BankAccountStatus), default=BankAccountStatus.ACTIVE)
    monitoring_enabled = Column(Boolean, default=True)
    alert_threshold_amount = Column(Numeric(10, 2), default=10000.00)

    # Metadata
    last_sync_at = Column(DateTime(timezone=True))
    last_transaction_date = Column(DateTime(timezone=True))
    total_transactions = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    transactions = relationship("Transaction", back_populates="bank_account")
    fraud_cases = relationship("FraudCase", back_populates="bank_account")


class Transaction(Base):
    """
    Financial transaction from bank account.

    Stores transaction details and fraud analysis results.
    """
    __tablename__ = "transactions"
    __table_args__ = (
        Index("idx_transaction_bank_account", "bank_account_id"),
        Index("idx_transaction_date", "transaction_date"),
        Index("idx_transaction_fraud_score", "fraud_score"),
        Index("idx_transaction_flagged", "is_flagged"),
        {"schema": "fraud_detection"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    bank_account_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fraud_detection.bank_accounts.id"),
        nullable=False
    )

    # Plaid transaction details
    plaid_transaction_id = Column(String(255), unique=True, nullable=False)

    # Transaction information
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    posted_date = Column(DateTime(timezone=True))
    amount = Column(Numeric(10, 2), nullable=False)
    currency_code = Column(String(3), default="USD")
    transaction_type = Column(SQLEnum(TransactionType))

    # Description and categorization
    description = Column(Text)
    merchant_name = Column(String(255))
    category = Column(JSONB)  # Plaid categories
    location = Column(JSONB)  # Geographic location
    payment_channel = Column(String(50))  # online, in store, other

    # Fraud analysis
    fraud_score = Column(Float, default=0.0)  # 0.0 to 1.0
    is_flagged = Column(Boolean, default=False)
    flagged_reasons = Column(JSONB)  # List of reasons
    risk_level = Column(SQLEnum(FraudSeverity))

    # ML model results
    model_predictions = Column(JSONB)  # Predictions from multiple models
    feature_importance = Column(JSONB)  # Which features contributed
    anomaly_score = Column(Float)  # Anomaly detection score

    # Analysis metadata
    analyzed_at = Column(DateTime(timezone=True))
    analysis_version = Column(String(50))  # Model version

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bank_account = relationship("BankAccount", back_populates="transactions")
    fraud_cases = relationship("FraudCase", back_populates="transaction")
    alerts = relationship("FraudAlert", back_populates="transaction")


class FraudCase(Base):
    """
    Fraud case for investigation and tracking.

    Created when fraud is detected above threshold.
    """
    __tablename__ = "fraud_cases"
    __table_args__ = (
        Index("idx_fraud_case_customer", "customer_id"),
        Index("idx_fraud_case_status", "status"),
        Index("idx_fraud_case_severity", "severity"),
        Index("idx_fraud_case_created", "created_at"),
        {"schema": "fraud_detection"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    case_number = Column(String(50), unique=True, nullable=False)

    customer_id = Column(PGUUID(as_uuid=True), nullable=False)
    bank_account_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fraud_detection.bank_accounts.id")
    )
    transaction_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fraud_detection.transactions.id")
    )

    # Case details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(FraudCaseStatus), default=FraudCaseStatus.OPEN)
    severity = Column(SQLEnum(FraudSeverity), nullable=False)

    # Fraud information
    fraud_type = Column(String(100))  # identity_theft, unauthorized_transaction, etc.
    detected_patterns = Column(JSONB)  # Patterns that triggered detection
    affected_transactions_count = Column(Integer, default=1)
    estimated_loss_amount = Column(Numeric(12, 2))

    # Investigation
    assigned_to = Column(PGUUID(as_uuid=True))  # User ID
    investigation_notes = Column(Text)
    resolution_notes = Column(Text)
    false_positive_reason = Column(Text)

    # Timeline
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))

    # Compliance
    reported_to_authorities = Column(Boolean, default=False)
    reported_at = Column(DateTime(timezone=True))
    report_reference = Column(String(255))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bank_account = relationship("BankAccount", back_populates="fraud_cases")
    transaction = relationship("Transaction", back_populates="fraud_cases")
    alerts = relationship("FraudAlert", back_populates="fraud_case")
    activities = relationship("CaseActivity", back_populates="fraud_case")


class FraudAlert(Base):
    """
    Real-time fraud alert for immediate notification.

    Triggered when transactions exceed risk thresholds.
    """
    __tablename__ = "fraud_alerts"
    __table_args__ = (
        Index("idx_alert_status", "status"),
        Index("idx_alert_severity", "severity"),
        Index("idx_alert_created", "created_at"),
        {"schema": "fraud_detection"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    transaction_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fraud_detection.transactions.id"),
        nullable=False
    )
    fraud_case_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fraud_detection.fraud_cases.id")
    )

    # Alert details
    alert_type = Column(String(100), nullable=False)
    severity = Column(SQLEnum(FraudSeverity), nullable=False)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.NEW)

    message = Column(Text, nullable=False)
    details = Column(JSONB)
    triggered_rules = Column(JSONB)  # Which rules triggered

    # Response
    acknowledged_by = Column(PGUUID(as_uuid=True))
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_by = Column(PGUUID(as_uuid=True))
    resolved_at = Column(DateTime(timezone=True))
    resolution_action = Column(String(255))

    # Notifications
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSONB)  # email, sms, webhook

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    transaction = relationship("Transaction", back_populates="alerts")
    fraud_case = relationship("FraudCase", back_populates="alerts")


class FraudRule(Base):
    """
    Configurable fraud detection rule.

    Defines conditions for fraud detection and alerting.
    """
    __tablename__ = "fraud_rules"
    __table_args__ = (
        Index("idx_rule_type", "rule_type"),
        Index("idx_rule_enabled", "is_enabled"),
        {"schema": "fraud_detection"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Rule identification
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rule_type = Column(SQLEnum(RuleType), nullable=False)

    # Configuration
    is_enabled = Column(Boolean, default=True)
    is_global = Column(Boolean, default=True)  # Apply to all customers
    customer_id = Column(PGUUID(as_uuid=True))  # Customer-specific rule

    # Rule definition
    conditions = Column(JSONB, nullable=False)
    thresholds = Column(JSONB)
    severity = Column(SQLEnum(FraudSeverity), default=FraudSeverity.MEDIUM)

    # Actions
    create_alert = Column(Boolean, default=True)
    create_case = Column(Boolean, default=False)
    block_transaction = Column(Boolean, default=False)
    notification_channels = Column(JSONB)

    # Metadata
    priority = Column(Integer, default=100)  # Execution order
    execution_count = Column(Integer, default=0)
    true_positive_count = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(PGUUID(as_uuid=True))


class MLModel(Base):
    """
    Machine learning model for fraud detection.

    Tracks model versions, performance, and deployment status.
    """
    __tablename__ = "ml_models"
    __table_args__ = (
        Index("idx_model_status", "is_active"),
        {"schema": "fraud_detection"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Model identification
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(100), nullable=False)  # random_forest, xgboost, neural_network

    # Model artifacts
    model_path = Column(String(500))  # S3/Azure path
    model_hash = Column(String(64))  # SHA256

    # Configuration
    hyperparameters = Column(JSONB)
    feature_names = Column(JSONB)
    training_config = Column(JSONB)

    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_roc = Column(Float)

    # Training details
    training_dataset_size = Column(Integer)
    training_duration_seconds = Column(Integer)
    trained_at = Column(DateTime(timezone=True))
    trained_by = Column(PGUUID(as_uuid=True))

    # Deployment
    is_active = Column(Boolean, default=False)
    deployed_at = Column(DateTime(timezone=True))
    prediction_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraudPattern(Base):
    """
    Known fraud pattern for detection.

    Stores historical fraud patterns for pattern matching.
    """
    __tablename__ = "fraud_patterns"
    __table_args__ = (
        Index("idx_pattern_type", "pattern_type"),
        {"schema": "fraud_detection"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Pattern details
    pattern_type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Pattern definition
    pattern_signature = Column(JSONB, nullable=False)
    matching_criteria = Column(JSONB)
    confidence_threshold = Column(Float, default=0.75)

    # Statistics
    occurrence_count = Column(Integer, default=0)
    confirmed_fraud_count = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)

    # Metadata
    severity = Column(SQLEnum(FraudSeverity), default=FraudSeverity.MEDIUM)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_detected_at = Column(DateTime(timezone=True))


class CaseActivity(Base):
    """
    Activity log for fraud case investigation.

    Tracks all actions taken on a fraud case.
    """
    __tablename__ = "case_activities"
    __table_args__ = (
        Index("idx_activity_case", "fraud_case_id"),
        Index("idx_activity_created", "created_at"),
        {"schema": "fraud_detection"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    fraud_case_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("fraud_detection.fraud_cases.id"),
        nullable=False
    )

    # Activity details
    activity_type = Column(String(100), nullable=False)  # status_change, note_added, etc.
    description = Column(Text, nullable=False)
    details = Column(JSONB)

    # Actor
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    user_name = Column(String(255))

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    fraud_case = relationship("FraudCase", back_populates="activities")


class FeatureFlag(Base):
    """
    Feature flag for enabling/disabling fraud detection per customer.

    Allows granular control of fraud detection features.
    """
    __tablename__ = "feature_flags"
    __table_args__ = (
        Index("idx_feature_customer", "customer_id"),
        Index("idx_feature_enabled", "is_enabled"),
        {"schema": "fraud_detection"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    customer_id = Column(PGUUID(as_uuid=True), nullable=False, unique=True)

    # Feature flags
    is_enabled = Column(Boolean, default=False)
    real_time_monitoring = Column(Boolean, default=True)
    ml_detection = Column(Boolean, default=True)
    rule_based_detection = Column(Boolean, default=True)
    anomaly_detection = Column(Boolean, default=True)

    # Alert configuration
    alert_email = Column(Boolean, default=True)
    alert_sms = Column(Boolean, default=False)
    alert_webhook = Column(Boolean, default=False)
    webhook_url = Column(String(500))

    # Thresholds
    min_alert_severity = Column(SQLEnum(FraudSeverity), default=FraudSeverity.MEDIUM)
    auto_case_creation_threshold = Column(Float, default=0.85)  # Fraud score

    # Monitoring settings
    daily_transaction_limit = Column(Integer)
    high_risk_amount_threshold = Column(Numeric(12, 2), default=5000.00)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    enabled_at = Column(DateTime(timezone=True))
    enabled_by = Column(PGUUID(as_uuid=True))
