"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl

from .models import (
    AlertStatus,
    BankAccountStatus,
    FraudCaseStatus,
    FraudSeverity,
    RuleType,
    TransactionType,
)


# Bank Account Schemas
class PlaidLinkRequest(BaseModel):
    """Request to link bank account via Plaid"""
    public_token: str = Field(..., description="Plaid public token from Link flow")
    account_id: str = Field(..., description="Selected account ID")
    institution_id: str = Field(..., description="Institution ID")
    institution_name: str = Field(..., description="Institution name")


class BankAccountBase(BaseModel):
    """Base bank account schema"""
    account_name: Optional[str] = None
    monitoring_enabled: bool = True
    alert_threshold_amount: Decimal = Decimal("10000.00")


class BankAccountCreate(BankAccountBase):
    """Create bank account"""
    customer_id: UUID
    plaid_item_id: str
    plaid_access_token_encrypted: str
    plaid_account_id: str
    account_mask: Optional[str] = None
    account_type: Optional[str] = None
    account_subtype: Optional[str] = None
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None


class BankAccountUpdate(BaseModel):
    """Update bank account"""
    account_name: Optional[str] = None
    monitoring_enabled: Optional[bool] = None
    alert_threshold_amount: Optional[Decimal] = None
    status: Optional[BankAccountStatus] = None


class BankAccountResponse(BankAccountBase):
    """Bank account response"""
    id: UUID
    customer_id: UUID
    account_mask: Optional[str]
    account_type: Optional[str]
    institution_name: Optional[str]
    status: BankAccountStatus
    last_sync_at: Optional[datetime]
    total_transactions: int
    created_at: datetime

    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionBase(BaseModel):
    """Base transaction schema"""
    transaction_date: datetime
    amount: Decimal
    description: Optional[str] = None
    merchant_name: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Transaction response"""
    id: UUID
    bank_account_id: UUID
    transaction_type: Optional[TransactionType]
    currency_code: str
    category: Optional[Dict[str, Any]]
    location: Optional[Dict[str, Any]]
    fraud_score: float
    is_flagged: bool
    flagged_reasons: Optional[Dict[str, Any]]
    risk_level: Optional[FraudSeverity]
    analyzed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionAnalysisResponse(BaseModel):
    """Detailed transaction analysis"""
    transaction: TransactionResponse
    model_predictions: Dict[str, float]
    feature_importance: Dict[str, float]
    anomaly_score: float
    triggered_rules: List[str]
    recommendation: str


# Fraud Case Schemas
class FraudCaseBase(BaseModel):
    """Base fraud case schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    severity: FraudSeverity


class FraudCaseCreate(FraudCaseBase):
    """Create fraud case"""
    customer_id: UUID
    bank_account_id: Optional[UUID] = None
    transaction_id: Optional[UUID] = None
    fraud_type: Optional[str] = None
    estimated_loss_amount: Optional[Decimal] = None


class FraudCaseUpdate(BaseModel):
    """Update fraud case"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[FraudCaseStatus] = None
    severity: Optional[FraudSeverity] = None
    assigned_to: Optional[UUID] = None
    investigation_notes: Optional[str] = None
    resolution_notes: Optional[str] = None
    false_positive_reason: Optional[str] = None


class FraudCaseResponse(FraudCaseBase):
    """Fraud case response"""
    id: UUID
    case_number: str
    customer_id: UUID
    status: FraudCaseStatus
    fraud_type: Optional[str]
    affected_transactions_count: int
    estimated_loss_amount: Optional[Decimal]
    assigned_to: Optional[UUID]
    detected_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class CaseActivityCreate(BaseModel):
    """Create case activity"""
    activity_type: str
    description: str
    details: Optional[Dict[str, Any]] = None


class CaseActivityResponse(BaseModel):
    """Case activity response"""
    id: UUID
    fraud_case_id: UUID
    activity_type: str
    description: str
    details: Optional[Dict[str, Any]]
    user_id: UUID
    user_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Fraud Alert Schemas
class FraudAlertCreate(BaseModel):
    """Create fraud alert"""
    transaction_id: UUID
    alert_type: str
    severity: FraudSeverity
    message: str
    details: Optional[Dict[str, Any]] = None
    triggered_rules: Optional[List[str]] = None


class FraudAlertUpdate(BaseModel):
    """Update fraud alert"""
    status: AlertStatus
    resolution_action: Optional[str] = None


class FraudAlertResponse(BaseModel):
    """Fraud alert response"""
    id: UUID
    transaction_id: UUID
    fraud_case_id: Optional[UUID]
    alert_type: str
    severity: FraudSeverity
    status: AlertStatus
    message: str
    details: Optional[Dict[str, Any]]
    triggered_rules: Optional[List[str]]
    notification_sent: bool
    created_at: datetime
    acknowledged_at: Optional[datetime]

    class Config:
        from_attributes = True


# Fraud Rule Schemas
class FraudRuleBase(BaseModel):
    """Base fraud rule schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    rule_type: RuleType
    is_enabled: bool = True


class FraudRuleCreate(FraudRuleBase):
    """Create fraud rule"""
    is_global: bool = True
    customer_id: Optional[UUID] = None
    conditions: Dict[str, Any]
    thresholds: Optional[Dict[str, Any]] = None
    severity: FraudSeverity = FraudSeverity.MEDIUM
    create_alert: bool = True
    create_case: bool = False
    notification_channels: Optional[List[str]] = None
    priority: int = 100


class FraudRuleUpdate(BaseModel):
    """Update fraud rule"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    conditions: Optional[Dict[str, Any]] = None
    thresholds: Optional[Dict[str, Any]] = None
    severity: Optional[FraudSeverity] = None
    create_alert: Optional[bool] = None
    create_case: Optional[bool] = None
    priority: Optional[int] = None


class FraudRuleResponse(FraudRuleBase):
    """Fraud rule response"""
    id: UUID
    is_global: bool
    customer_id: Optional[UUID]
    conditions: Dict[str, Any]
    thresholds: Optional[Dict[str, Any]]
    severity: FraudSeverity
    create_alert: bool
    create_case: bool
    priority: int
    execution_count: int
    true_positive_count: int
    false_positive_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ML Model Schemas
class MLModelBase(BaseModel):
    """Base ML model schema"""
    name: str
    version: str
    model_type: str


class MLModelCreate(MLModelBase):
    """Create ML model"""
    model_path: str
    model_hash: str
    hyperparameters: Dict[str, Any]
    feature_names: List[str]
    training_config: Dict[str, Any]
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    training_dataset_size: Optional[int] = None
    training_duration_seconds: Optional[int] = None


class MLModelResponse(MLModelBase):
    """ML model response"""
    id: UUID
    model_path: str
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    auc_roc: Optional[float]
    is_active: bool
    prediction_count: int
    trained_at: Optional[datetime]
    deployed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Feature Flag Schemas
class FeatureFlagUpdate(BaseModel):
    """Update feature flag"""
    is_enabled: Optional[bool] = None
    real_time_monitoring: Optional[bool] = None
    ml_detection: Optional[bool] = None
    rule_based_detection: Optional[bool] = None
    anomaly_detection: Optional[bool] = None
    alert_email: Optional[bool] = None
    alert_sms: Optional[bool] = None
    alert_webhook: Optional[bool] = None
    webhook_url: Optional[HttpUrl] = None
    min_alert_severity: Optional[FraudSeverity] = None
    auto_case_creation_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    daily_transaction_limit: Optional[int] = None
    high_risk_amount_threshold: Optional[Decimal] = None


class FeatureFlagResponse(BaseModel):
    """Feature flag response"""
    id: UUID
    customer_id: UUID
    is_enabled: bool
    real_time_monitoring: bool
    ml_detection: bool
    rule_based_detection: bool
    anomaly_detection: bool
    alert_email: bool
    alert_sms: bool
    alert_webhook: bool
    webhook_url: Optional[str]
    min_alert_severity: FraudSeverity
    auto_case_creation_threshold: float
    daily_transaction_limit: Optional[int]
    high_risk_amount_threshold: Decimal
    created_at: datetime
    enabled_at: Optional[datetime]

    class Config:
        from_attributes = True


# Statistics Schemas
class FraudStatistics(BaseModel):
    """Fraud detection statistics"""
    total_transactions: int
    flagged_transactions: int
    flagged_percentage: float
    total_cases: int
    open_cases: int
    resolved_cases: int
    total_alerts: int
    critical_alerts: int
    average_fraud_score: float
    total_potential_loss: Decimal
    false_positive_rate: Optional[float]


class DashboardMetrics(BaseModel):
    """Dashboard metrics for admin portal"""
    today_transactions: int
    today_flagged: int
    new_alerts: int
    open_cases: int
    total_monitored_accounts: int
    active_customers: int
    average_risk_score: float
    top_fraud_types: List[Dict[str, Any]]
    recent_alerts: List[FraudAlertResponse]


# Webhook Schemas
class PlaidWebhook(BaseModel):
    """Plaid webhook payload"""
    webhook_type: str
    webhook_code: str
    item_id: str
    error: Optional[Dict[str, Any]] = None


class TransactionWebhook(BaseModel):
    """Transaction update webhook"""
    webhook_type: str = "TRANSACTIONS"
    webhook_code: str
    item_id: str
    new_transactions: int
    removed_transactions: List[str] = []


# Batch Operations
class BatchTransactionAnalysisRequest(BaseModel):
    """Request to analyze multiple transactions"""
    transaction_ids: List[UUID] = Field(..., min_length=1, max_length=1000)
    force_reanalysis: bool = False


class BatchTransactionAnalysisResponse(BaseModel):
    """Response for batch analysis"""
    total_processed: int
    flagged_count: int
    new_cases_created: int
    processing_time_seconds: float
    results: List[TransactionAnalysisResponse]
