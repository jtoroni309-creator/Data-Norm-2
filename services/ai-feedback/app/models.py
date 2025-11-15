"""
Database models for AI Feedback Loop Service
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


class AIFeedback(Base):
    """
    Records of CPA feedback on AI predictions

    Every AI prediction that a CPA reviews is logged here
    """
    __tablename__ = "ai_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Model info
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    prediction_id = Column(String(100), nullable=False, unique=True, index=True)

    # Input/Output
    input_data = Column(JSONB, nullable=False)  # What was sent to model
    ai_prediction = Column(JSONB, nullable=False)  # What model predicted
    ai_confidence = Column(Float, nullable=False)  # Model's confidence score

    # Feedback
    feedback_type = Column(String(20), nullable=False)  # approval, correction, rejection, modification
    cpa_correction = Column(JSONB, nullable=True)  # CPA's correction (if different from AI)

    # CPA info
    cpa_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    cpa_role = Column(String(20), nullable=False)  # partner, manager, senior, staff
    expert_weight = Column(Float, nullable=False)  # Weight for training (higher for senior experts)

    # Context
    engagement_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    notes = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    processed_for_training = Column(Boolean, default=False, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_feedback_model_date', 'model_name', 'created_at'),
        Index('idx_feedback_type', 'feedback_type'),
        Index('idx_feedback_cpa_role', 'cpa_role'),
    )


class ModelVersion(Base):
    """
    Model version registry with performance metrics
    """
    __tablename__ = "model_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Model identification
    model_name = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False)

    # Status
    is_active = Column(Boolean, default=False, index=True)  # Currently in production
    is_ab_test = Column(Boolean, default=False)  # In A/B test
    ab_test_traffic_pct = Column(Float, nullable=True)  # % of traffic if in A/B test

    # Performance metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    baseline_accuracy = Column(Float, nullable=True)  # Accuracy before this training

    # Training info
    training_samples = Column(Integer, nullable=True)
    validation_samples = Column(Integer, nullable=True)
    training_duration_seconds = Column(Integer, nullable=True)
    training_cost_usd = Column(Float, nullable=True)

    # Storage
    model_uri = Column(String(500), nullable=True)  # Azure ML model URI
    model_size_mb = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_by = Column(String(100), nullable=True)  # System or user who triggered training
    notes = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_model_version_active', 'model_name', 'is_active'),
        Index('idx_model_version_unique', 'model_name', 'version', unique=True),
    )


class FeedbackQueue(Base):
    """
    Queue of feedback items waiting to be processed for training
    """
    __tablename__ = "feedback_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    feedback_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    priority = Column(Float, nullable=False, default=1.0)  # Higher = more important

    # Status
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending, training, trained, failed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime, nullable=True)

    # Training result
    model_version_trained = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_queue_status_priority', 'status', 'priority'),
        Index('idx_queue_model_status', 'model_name', 'status'),
    )


class ExpertProfile(Base):
    """
    CPA expert profiles with expertise weighting
    """
    __tablename__ = "expert_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    role = Column(String(20), nullable=False)  # partner, manager, senior, staff

    # Expertise areas
    industries = Column(JSONB, nullable=True)  # ["SaaS", "Manufacturing", ...]
    specializations = Column(JSONB, nullable=True)  # ["ASC 606", "ASC 842", ...]

    # Performance metrics
    total_feedback_given = Column(Integer, default=0)
    accuracy_of_feedback = Column(Float, nullable=True)  # How often their feedback aligns with other experts
    avg_feedback_time_seconds = Column(Integer, nullable=True)

    # Weighting
    custom_weight = Column(Float, nullable=True)  # Custom weight override (if expert is particularly good)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModelPerformanceMetric(Base):
    """
    Time-series performance metrics for models
    """
    __tablename__ = "model_performance_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)

    # Time period
    measured_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Metrics
    total_predictions = Column(Integer, nullable=False)
    correct_predictions = Column(Integer, nullable=False)
    accuracy = Column(Float, nullable=False)

    # By feedback type
    approvals = Column(Integer, default=0)
    corrections = Column(Integer, default=0)
    rejections = Column(Integer, default=0)
    modifications = Column(Integer, default=0)

    # Confidence analysis
    avg_confidence = Column(Float, nullable=True)
    avg_confidence_when_correct = Column(Float, nullable=True)
    avg_confidence_when_incorrect = Column(Float, nullable=True)

    # User engagement
    unique_users = Column(Integer, nullable=True)
    avg_time_to_feedback_seconds = Column(Integer, nullable=True)

    __table_args__ = (
        Index('idx_metrics_model_time', 'model_name', 'measured_at'),
    )


class ABTest(Base):
    """
    A/B tests for comparing model versions
    """
    __tablename__ = "ab_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    model_name = Column(String(100), nullable=False, index=True)
    version_a = Column(String(50), nullable=False)  # Control (current production)
    version_b = Column(String(50), nullable=False)  # Treatment (new version)

    # Test configuration
    traffic_split = Column(Float, nullable=False)  # % of traffic to version B (0.0 - 1.0)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="active", index=True)  # active, completed, stopped

    # Results
    version_a_predictions = Column(Integer, default=0)
    version_a_correct = Column(Integer, default=0)
    version_a_accuracy = Column(Float, nullable=True)

    version_b_predictions = Column(Integer, default=0)
    version_b_correct = Column(Integer, default=0)
    version_b_accuracy = Column(Float, nullable=True)

    # Statistical significance
    p_value = Column(Float, nullable=True)
    is_significant = Column(Boolean, nullable=True)
    winner = Column(String(50), nullable=True)  # "version_a" or "version_b"

    # Decision
    decision = Column(String(20), nullable=True)  # promote, rollback, continue
    decided_at = Column(DateTime, nullable=True)
    decided_by = Column(String(100), nullable=True)

    __table_args__ = (
        Index('idx_ab_test_model_status', 'model_name', 'status'),
    )
