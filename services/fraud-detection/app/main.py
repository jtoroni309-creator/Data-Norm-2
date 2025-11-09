"""
Fraud Detection Service - Main FastAPI Application

AI-powered fraud detection with bank integration and real-time monitoring.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from cryptography.fernet import Fernet
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db, AsyncSessionLocal
from .ml_fraud_detector import ml_fraud_detector
from .models import (
    AlertStatus,
    BankAccount,
    BankAccountStatus,
    CaseActivity,
    FeatureFlag,
    FraudAlert,
    FraudCase,
    FraudCaseStatus,
    FraudPattern,
    FraudRule,
    FraudSeverity,
    MLModel,
    Transaction,
    TransactionType,
)
from .plaid_service import plaid_service
from .schemas import (
    BankAccountCreate,
    BankAccountResponse,
    BankAccountUpdate,
    BatchTransactionAnalysisRequest,
    BatchTransactionAnalysisResponse,
    CaseActivityCreate,
    CaseActivityResponse,
    DashboardMetrics,
    FeatureFlagResponse,
    FeatureFlagUpdate,
    FraudAlertCreate,
    FraudAlertResponse,
    FraudAlertUpdate,
    FraudCaseCreate,
    FraudCaseResponse,
    FraudCaseUpdate,
    FraudRuleCreate,
    FraudRuleResponse,
    FraudRuleUpdate,
    FraudStatistics,
    PlaidLinkRequest,
    PlaidWebhook,
    TransactionAnalysisResponse,
    TransactionResponse,
)

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered fraud detection with bank account integration",
)

# Add CORS middleware - Configured for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

# Security Middleware (SOC 2 compliance - rate limiting, IP filtering, CSRF protection)
try:
    import sys
    sys.path.insert(0, '/home/user/Data-Norm-2/services')
    from security.app import SecurityMiddleware, AuditLogService

    # Initialize audit logging
    audit_log_service = AuditLogService()

    # Add security middleware
    app.add_middleware(
        SecurityMiddleware,
        audit_log_service=audit_log_service,
        enable_rate_limiting=True,
        enable_ip_filtering=False,
        enable_csrf_protection=True
    )
    logger.info("Security middleware enabled (SOC 2 compliant)")
except ImportError as e:
    logger.warning(f"Security middleware not available: {e}")

# Encryption cipher for sensitive data
# Use proper key derivation for Fernet encryption
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

def get_encryption_cipher() -> Fernet:
    """
    Create a Fernet cipher with properly derived key.

    Uses PBKDF2 key derivation function to convert the encryption key
    into a proper 32-byte key suitable for Fernet encryption.

    Returns:
        Fernet cipher instance with properly derived key
    """
    # Use PBKDF2 to derive a proper 32-byte key from the encryption key
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'aura_audit_ai_salt_v1',  # Static salt for deterministic key derivation
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.ENCRYPTION_KEY.encode()))
    return Fernet(key)

cipher = get_encryption_cipher()


# ============================================================================
# Helper Functions
# ============================================================================

def encrypt_token(token: str) -> str:
    """Encrypt sensitive token."""
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt sensitive token."""
    return cipher.decrypt(encrypted_token.encode()).decode()


async def check_feature_enabled(
    customer_id: UUID,
    db: AsyncSession
) -> FeatureFlag:
    """Check if fraud detection is enabled for customer."""
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.customer_id == customer_id)
    )
    feature_flag = result.scalar_one_or_none()

    if not feature_flag or not feature_flag.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Fraud detection is not enabled for this customer"
        )

    return feature_flag


async def generate_case_number() -> str:
    """Generate unique case number."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid4())[:8].upper()
    return f"FRAUD-{timestamp}-{unique_id}"


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Plaid Integration - Bank Account Connection
# ============================================================================

@app.post("/plaid/link-token")
async def create_link_token(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Create Plaid Link token for bank account connection.

    Returns a link_token to initialize Plaid Link in the frontend.
    """
    try:
        result = await plaid_service.create_link_token(str(user_id))
        return result
    except Exception as e:
        logger.error(f"Error creating link token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plaid/exchange-token", response_model=BankAccountResponse)
async def exchange_public_token(
    request: PlaidLinkRequest,
    customer_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Exchange public token and create bank account connection.

    Called after user completes Plaid Link flow.
    """
    try:
        # Exchange public token for access token
        token_response = await plaid_service.exchange_public_token(request.public_token)

        # Encrypt access token for secure storage
        encrypted_token = encrypt_token(token_response['access_token'])

        # Create bank account record
        bank_account = BankAccount(
            customer_id=customer_id,
            plaid_item_id=token_response['item_id'],
            plaid_access_token_encrypted=encrypted_token,
            plaid_account_id=request.account_id,
            institution_id=request.institution_id,
            institution_name=request.institution_name,
            status=BankAccountStatus.ACTIVE,
        )

        db.add(bank_account)
        await db.commit()
        await db.refresh(bank_account)

        # Start initial transaction sync in background
        background_tasks.add_task(
            sync_account_transactions,
            bank_account.id,
            customer_id
        )

        logger.info(f"Bank account connected: {bank_account.id}")

        return bank_account

    except Exception as e:
        logger.error(f"Error exchanging token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Bank Account Management
# ============================================================================

@app.get("/bank-accounts", response_model=List[BankAccountResponse])
async def list_bank_accounts(
    customer_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all bank accounts for a customer."""
    result = await db.execute(
        select(BankAccount)
        .where(BankAccount.customer_id == customer_id)
        .offset(skip)
        .limit(limit)
        .order_by(desc(BankAccount.created_at))
    )
    accounts = result.scalars().all()
    return accounts


@app.get("/bank-accounts/{account_id}", response_model=BankAccountResponse)
async def get_bank_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get bank account details."""
    result = await db.execute(
        select(BankAccount).where(BankAccount.id == account_id)
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    return account


@app.patch("/bank-accounts/{account_id}", response_model=BankAccountResponse)
async def update_bank_account(
    account_id: UUID,
    update_data: BankAccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update bank account settings."""
    result = await db.execute(
        select(BankAccount).where(BankAccount.id == account_id)
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    # Update fields
    if update_data.account_name is not None:
        account.account_name = update_data.account_name
    if update_data.monitoring_enabled is not None:
        account.monitoring_enabled = update_data.monitoring_enabled
    if update_data.alert_threshold_amount is not None:
        account.alert_threshold_amount = update_data.alert_threshold_amount
    if update_data.status is not None:
        account.status = update_data.status

    await db.commit()
    await db.refresh(account)

    return account


@app.post("/bank-accounts/{account_id}/sync")
async def sync_bank_account(
    account_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger transaction synchronization for a bank account.
    """
    result = await db.execute(
        select(BankAccount).where(BankAccount.id == account_id)
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    background_tasks.add_task(
        sync_account_transactions,
        account_id,
        account.customer_id
    )

    return {
        "message": "Transaction synchronization started",
        "account_id": account_id
    }


# ============================================================================
# Transaction Management
# ============================================================================

@app.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(
    customer_id: UUID,
    bank_account_id: Optional[UUID] = None,
    flagged_only: bool = False,
    min_fraud_score: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List transactions with optional filters."""
    query = (
        select(Transaction)
        .join(BankAccount)
        .where(BankAccount.customer_id == customer_id)
    )

    if bank_account_id:
        query = query.where(Transaction.bank_account_id == bank_account_id)

    if flagged_only:
        query = query.where(Transaction.is_flagged == True)

    if min_fraud_score is not None:
        query = query.where(Transaction.fraud_score >= min_fraud_score)

    if start_date:
        query = query.where(Transaction.transaction_date >= start_date)

    if end_date:
        query = query.where(Transaction.transaction_date <= end_date)

    query = query.offset(skip).limit(limit).order_by(desc(Transaction.transaction_date))

    result = await db.execute(query)
    transactions = result.scalars().all()

    return transactions


@app.get("/transactions/{transaction_id}", response_model=TransactionAnalysisResponse)
async def get_transaction_analysis(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed transaction analysis."""
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Get triggered rules
    triggered_rules = transaction.flagged_reasons.get('rules', []) if transaction.flagged_reasons else []

    # Generate recommendation
    if transaction.fraud_score >= 0.9:
        recommendation = "BLOCK - High fraud risk. Recommend immediate investigation."
    elif transaction.fraud_score >= 0.75:
        recommendation = "REVIEW - Moderate fraud risk. Manual review recommended."
    elif transaction.fraud_score >= 0.5:
        recommendation = "MONITOR - Low to moderate risk. Continue monitoring."
    else:
        recommendation = "APPROVE - Low risk transaction."

    return TransactionAnalysisResponse(
        transaction=transaction,
        model_predictions=transaction.model_predictions or {},
        feature_importance=transaction.feature_importance or {},
        anomaly_score=transaction.anomaly_score or 0.0,
        triggered_rules=triggered_rules,
        recommendation=recommendation
    )


@app.post("/transactions/analyze-batch", response_model=BatchTransactionAnalysisResponse)
async def analyze_transactions_batch(
    request: BatchTransactionAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze multiple transactions in batch.

    Useful for analyzing historical transactions or re-analyzing with updated models.
    """
    start_time = datetime.utcnow()

    # Fetch transactions
    result = await db.execute(
        select(Transaction).where(Transaction.id.in_(request.transaction_ids))
    )
    transactions = result.scalars().all()

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")

    # Analyze each transaction
    results = []
    flagged_count = 0
    new_cases_created = 0

    for transaction in transactions:
        # Skip if already analyzed and not forcing reanalysis
        if transaction.analyzed_at and not request.force_reanalysis:
            continue

        # Analyze transaction
        analysis_result = await analyze_single_transaction(transaction, db)

        if analysis_result['is_flagged']:
            flagged_count += 1

            # Check if we should create a case
            if analysis_result['fraud_score'] >= settings.AUTO_CASE_CREATION_THRESHOLD:
                await create_fraud_case_from_transaction(transaction, analysis_result, db)
                new_cases_created += 1

        results.append(analysis_result)

    await db.commit()

    processing_time = (datetime.utcnow() - start_time).total_seconds()

    return BatchTransactionAnalysisResponse(
        total_processed=len(results),
        flagged_count=flagged_count,
        new_cases_created=new_cases_created,
        processing_time_seconds=processing_time,
        results=results
    )


# ============================================================================
# Fraud Case Management
# ============================================================================

@app.post("/fraud-cases", response_model=FraudCaseResponse)
async def create_fraud_case(
    case_data: FraudCaseCreate,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Create a new fraud case."""
    case_number = await generate_case_number()

    fraud_case = FraudCase(
        case_number=case_number,
        customer_id=case_data.customer_id,
        bank_account_id=case_data.bank_account_id,
        transaction_id=case_data.transaction_id,
        title=case_data.title,
        description=case_data.description,
        severity=case_data.severity,
        fraud_type=case_data.fraud_type,
        estimated_loss_amount=case_data.estimated_loss_amount,
        status=FraudCaseStatus.OPEN,
    )

    db.add(fraud_case)
    await db.commit()
    await db.refresh(fraud_case)

    # Add activity log
    activity = CaseActivity(
        fraud_case_id=fraud_case.id,
        activity_type="case_created",
        description=f"Fraud case created: {case_data.title}",
        user_id=user_id,
    )
    db.add(activity)
    await db.commit()

    logger.info(f"Fraud case created: {fraud_case.case_number}")

    return fraud_case


@app.get("/fraud-cases", response_model=List[FraudCaseResponse])
async def list_fraud_cases(
    customer_id: Optional[UUID] = None,
    status: Optional[FraudCaseStatus] = None,
    severity: Optional[FraudSeverity] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List fraud cases with filters."""
    query = select(FraudCase)

    if customer_id:
        query = query.where(FraudCase.customer_id == customer_id)

    if status:
        query = query.where(FraudCase.status == status)

    if severity:
        query = query.where(FraudCase.severity == severity)

    query = query.offset(skip).limit(limit).order_by(desc(FraudCase.created_at))

    result = await db.execute(query)
    cases = result.scalars().all()

    return cases


@app.get("/fraud-cases/{case_id}", response_model=FraudCaseResponse)
async def get_fraud_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get fraud case details."""
    result = await db.execute(
        select(FraudCase).where(FraudCase.id == case_id)
    )
    fraud_case = result.scalar_one_or_none()

    if not fraud_case:
        raise HTTPException(status_code=404, detail="Fraud case not found")

    return fraud_case


@app.patch("/fraud-cases/{case_id}", response_model=FraudCaseResponse)
async def update_fraud_case(
    case_id: UUID,
    update_data: FraudCaseUpdate,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Update fraud case."""
    result = await db.execute(
        select(FraudCase).where(FraudCase.id == case_id)
    )
    fraud_case = result.scalar_one_or_none()

    if not fraud_case:
        raise HTTPException(status_code=404, detail="Fraud case not found")

    # Track changes for activity log
    changes = []

    if update_data.title is not None:
        fraud_case.title = update_data.title
        changes.append("title updated")

    if update_data.description is not None:
        fraud_case.description = update_data.description

    if update_data.status is not None:
        old_status = fraud_case.status
        fraud_case.status = update_data.status
        changes.append(f"status changed from {old_status.value} to {update_data.status.value}")

        # Update timestamps based on status
        if update_data.status == FraudCaseStatus.INVESTIGATING:
            fraud_case.acknowledged_at = func.now()
        elif update_data.status == FraudCaseStatus.RESOLVED:
            fraud_case.resolved_at = func.now()
        elif update_data.status == FraudCaseStatus.CLOSED:
            fraud_case.closed_at = func.now()

    if update_data.severity is not None:
        fraud_case.severity = update_data.severity
        changes.append(f"severity changed to {update_data.severity.value}")

    if update_data.assigned_to is not None:
        fraud_case.assigned_to = update_data.assigned_to
        changes.append("case reassigned")

    if update_data.investigation_notes is not None:
        fraud_case.investigation_notes = update_data.investigation_notes

    if update_data.resolution_notes is not None:
        fraud_case.resolution_notes = update_data.resolution_notes

    if update_data.false_positive_reason is not None:
        fraud_case.false_positive_reason = update_data.false_positive_reason

    await db.commit()
    await db.refresh(fraud_case)

    # Add activity log
    if changes:
        activity = CaseActivity(
            fraud_case_id=fraud_case.id,
            activity_type="case_updated",
            description=f"Case updated: {', '.join(changes)}",
            user_id=user_id,
        )
        db.add(activity)
        await db.commit()

    return fraud_case


@app.get("/fraud-cases/{case_id}/activities", response_model=List[CaseActivityResponse])
async def get_case_activities(
    case_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get case activity history."""
    result = await db.execute(
        select(CaseActivity)
        .where(CaseActivity.fraud_case_id == case_id)
        .order_by(desc(CaseActivity.created_at))
    )
    activities = result.scalars().all()

    return activities


@app.post("/fraud-cases/{case_id}/activities", response_model=CaseActivityResponse)
async def add_case_activity(
    case_id: UUID,
    activity_data: CaseActivityCreate,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Add activity to case."""
    # Verify case exists
    result = await db.execute(
        select(FraudCase).where(FraudCase.id == case_id)
    )
    fraud_case = result.scalar_one_or_none()

    if not fraud_case:
        raise HTTPException(status_code=404, detail="Fraud case not found")

    activity = CaseActivity(
        fraud_case_id=case_id,
        activity_type=activity_data.activity_type,
        description=activity_data.description,
        details=activity_data.details,
        user_id=user_id,
    )

    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    return activity


# ============================================================================
# Fraud Alerts
# ============================================================================

@app.get("/alerts", response_model=List[FraudAlertResponse])
async def list_alerts(
    status: Optional[AlertStatus] = None,
    severity: Optional[FraudSeverity] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List fraud alerts."""
    query = select(FraudAlert)

    if status:
        query = query.where(FraudAlert.status == status)

    if severity:
        query = query.where(FraudAlert.severity == severity)

    query = query.offset(skip).limit(limit).order_by(desc(FraudAlert.created_at))

    result = await db.execute(query)
    alerts = result.scalars().all()

    return alerts


@app.patch("/alerts/{alert_id}", response_model=FraudAlertResponse)
async def update_alert(
    alert_id: UUID,
    update_data: FraudAlertUpdate,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Update fraud alert."""
    result = await db.execute(
        select(FraudAlert).where(FraudAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = update_data.status

    if update_data.status == AlertStatus.ACKNOWLEDGED:
        alert.acknowledged_by = user_id
        alert.acknowledged_at = func.now()
    elif update_data.status == AlertStatus.RESOLVED:
        alert.resolved_by = user_id
        alert.resolved_at = func.now()
        if update_data.resolution_action:
            alert.resolution_action = update_data.resolution_action

    await db.commit()
    await db.refresh(alert)

    return alert


# ============================================================================
# Feature Flags
# ============================================================================

@app.get("/feature-flags/{customer_id}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get fraud detection feature flag for customer."""
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.customer_id == customer_id)
    )
    feature_flag = result.scalar_one_or_none()

    if not feature_flag:
        # Create default feature flag (disabled)
        feature_flag = FeatureFlag(
            customer_id=customer_id,
            is_enabled=False,
        )
        db.add(feature_flag)
        await db.commit()
        await db.refresh(feature_flag)

    return feature_flag


@app.patch("/feature-flags/{customer_id}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    customer_id: UUID,
    update_data: FeatureFlagUpdate,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Update fraud detection feature flag.

    Used by admin portal to enable/disable fraud detection per customer.
    """
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.customer_id == customer_id)
    )
    feature_flag = result.scalar_one_or_none()

    if not feature_flag:
        feature_flag = FeatureFlag(customer_id=customer_id)
        db.add(feature_flag)

    # Update fields
    if update_data.is_enabled is not None:
        feature_flag.is_enabled = update_data.is_enabled
        if update_data.is_enabled:
            feature_flag.enabled_at = func.now()
            feature_flag.enabled_by = user_id

    if update_data.real_time_monitoring is not None:
        feature_flag.real_time_monitoring = update_data.real_time_monitoring

    if update_data.ml_detection is not None:
        feature_flag.ml_detection = update_data.ml_detection

    if update_data.rule_based_detection is not None:
        feature_flag.rule_based_detection = update_data.rule_based_detection

    if update_data.anomaly_detection is not None:
        feature_flag.anomaly_detection = update_data.anomaly_detection

    if update_data.alert_email is not None:
        feature_flag.alert_email = update_data.alert_email

    if update_data.alert_sms is not None:
        feature_flag.alert_sms = update_data.alert_sms

    if update_data.alert_webhook is not None:
        feature_flag.alert_webhook = update_data.alert_webhook

    if update_data.webhook_url is not None:
        feature_flag.webhook_url = str(update_data.webhook_url)

    if update_data.min_alert_severity is not None:
        feature_flag.min_alert_severity = update_data.min_alert_severity

    if update_data.auto_case_creation_threshold is not None:
        feature_flag.auto_case_creation_threshold = update_data.auto_case_creation_threshold

    if update_data.daily_transaction_limit is not None:
        feature_flag.daily_transaction_limit = update_data.daily_transaction_limit

    if update_data.high_risk_amount_threshold is not None:
        feature_flag.high_risk_amount_threshold = update_data.high_risk_amount_threshold

    await db.commit()
    await db.refresh(feature_flag)

    logger.info(f"Feature flag updated for customer {customer_id}: enabled={feature_flag.is_enabled}")

    return feature_flag


# ============================================================================
# Statistics and Dashboard
# ============================================================================

@app.get("/statistics", response_model=FraudStatistics)
async def get_statistics(
    customer_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get fraud detection statistics."""
    # Build base query
    txn_query = select(Transaction)

    if customer_id:
        txn_query = txn_query.join(BankAccount).where(BankAccount.customer_id == customer_id)

    if start_date:
        txn_query = txn_query.where(Transaction.transaction_date >= start_date)

    if end_date:
        txn_query = txn_query.where(Transaction.transaction_date <= end_date)

    # Get transaction counts
    total_result = await db.execute(select(func.count()).select_from(txn_query.subquery()))
    total_transactions = total_result.scalar()

    flagged_result = await db.execute(
        select(func.count())
        .select_from(txn_query.where(Transaction.is_flagged == True).subquery())
    )
    flagged_transactions = flagged_result.scalar()

    # Case statistics
    case_query = select(FraudCase)
    if customer_id:
        case_query = case_query.where(FraudCase.customer_id == customer_id)

    if start_date:
        case_query = case_query.where(FraudCase.created_at >= start_date)

    total_cases_result = await db.execute(select(func.count()).select_from(case_query.subquery()))
    total_cases = total_cases_result.scalar()

    open_cases_result = await db.execute(
        select(func.count())
        .select_from(case_query.where(FraudCase.status == FraudCaseStatus.OPEN).subquery())
    )
    open_cases = open_cases_result.scalar()

    resolved_cases = total_cases - open_cases

    # Alert statistics
    alert_query = select(FraudAlert)
    if start_date:
        alert_query = alert_query.where(FraudAlert.created_at >= start_date)

    total_alerts_result = await db.execute(select(func.count()).select_from(alert_query.subquery()))
    total_alerts = total_alerts_result.scalar()

    critical_alerts_result = await db.execute(
        select(func.count())
        .select_from(alert_query.where(FraudAlert.severity == FraudSeverity.CRITICAL).subquery())
    )
    critical_alerts = critical_alerts_result.scalar()

    # Average fraud score
    avg_score_result = await db.execute(
        select(func.avg(Transaction.fraud_score)).select_from(txn_query.subquery())
    )
    avg_fraud_score = avg_score_result.scalar() or 0.0

    # Total potential loss
    loss_result = await db.execute(
        select(func.sum(FraudCase.estimated_loss_amount))
        .select_from(case_query.subquery())
    )
    total_potential_loss = loss_result.scalar() or Decimal("0.00")

    return FraudStatistics(
        total_transactions=total_transactions or 0,
        flagged_transactions=flagged_transactions or 0,
        flagged_percentage=(flagged_transactions / total_transactions * 100) if total_transactions > 0 else 0.0,
        total_cases=total_cases or 0,
        open_cases=open_cases or 0,
        resolved_cases=resolved_cases or 0,
        total_alerts=total_alerts or 0,
        critical_alerts=critical_alerts or 0,
        average_fraud_score=float(avg_fraud_score),
        total_potential_loss=total_potential_loss,
        false_positive_rate=None,  # Would need historical data to calculate
    )


@app.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard metrics for admin portal."""
    today = datetime.utcnow().date()

    # Today's transactions
    today_txn_result = await db.execute(
        select(func.count())
        .select_from(Transaction)
        .where(func.date(Transaction.transaction_date) == today)
    )
    today_transactions = today_txn_result.scalar() or 0

    # Today's flagged transactions
    today_flagged_result = await db.execute(
        select(func.count())
        .select_from(Transaction)
        .where(
            and_(
                func.date(Transaction.transaction_date) == today,
                Transaction.is_flagged == True
            )
        )
    )
    today_flagged = today_flagged_result.scalar() or 0

    # New alerts
    new_alerts_result = await db.execute(
        select(func.count())
        .select_from(FraudAlert)
        .where(FraudAlert.status == AlertStatus.NEW)
    )
    new_alerts = new_alerts_result.scalar() or 0

    # Open cases
    open_cases_result = await db.execute(
        select(func.count())
        .select_from(FraudCase)
        .where(FraudCase.status == FraudCaseStatus.OPEN)
    )
    open_cases = open_cases_result.scalar() or 0

    # Monitored accounts
    monitored_result = await db.execute(
        select(func.count())
        .select_from(BankAccount)
        .where(
            and_(
                BankAccount.status == BankAccountStatus.ACTIVE,
                BankAccount.monitoring_enabled == True
            )
        )
    )
    total_monitored_accounts = monitored_result.scalar() or 0

    # Active customers (with feature enabled)
    active_customers_result = await db.execute(
        select(func.count())
        .select_from(FeatureFlag)
        .where(FeatureFlag.is_enabled == True)
    )
    active_customers = active_customers_result.scalar() or 0

    # Average risk score
    avg_risk_result = await db.execute(
        select(func.avg(Transaction.fraud_score))
        .select_from(Transaction)
        .where(func.date(Transaction.transaction_date) == today)
    )
    average_risk_score = avg_risk_result.scalar() or 0.0

    # Top fraud types
    fraud_types_result = await db.execute(
        select(
            FraudCase.fraud_type,
            func.count(FraudCase.id).label('count')
        )
        .where(FraudCase.fraud_type.isnot(None))
        .group_by(FraudCase.fraud_type)
        .order_by(desc('count'))
        .limit(5)
    )
    top_fraud_types = [
        {"type": row[0], "count": row[1]}
        for row in fraud_types_result.all()
    ]

    # Recent alerts
    recent_alerts_result = await db.execute(
        select(FraudAlert)
        .order_by(desc(FraudAlert.created_at))
        .limit(10)
    )
    recent_alerts = recent_alerts_result.scalars().all()

    return DashboardMetrics(
        today_transactions=today_transactions,
        today_flagged=today_flagged,
        new_alerts=new_alerts,
        open_cases=open_cases,
        total_monitored_accounts=total_monitored_accounts,
        active_customers=active_customers,
        average_risk_score=float(average_risk_score),
        top_fraud_types=top_fraud_types,
        recent_alerts=recent_alerts,
    )


# ============================================================================
# Webhooks
# ============================================================================

@app.post("/webhooks/plaid")
async def plaid_webhook(
    webhook_data: PlaidWebhook,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Plaid webhooks for real-time transaction updates.
    """
    logger.info(f"Received Plaid webhook: {webhook_data.webhook_type} - {webhook_data.webhook_code}")

    # Find bank account by item_id
    result = await db.execute(
        select(BankAccount).where(BankAccount.plaid_item_id == webhook_data.item_id)
    )
    bank_account = result.scalar_one_or_none()

    if not bank_account:
        logger.warning(f"Bank account not found for item_id: {webhook_data.item_id}")
        return {"status": "ignored", "reason": "account_not_found"}

    # Process webhook
    webhook_result = await plaid_service.process_webhook(webhook_data.dict())

    # Handle transaction updates
    if webhook_data.webhook_type == "TRANSACTIONS":
        if webhook_data.webhook_code in ["DEFAULT_UPDATE", "INITIAL_UPDATE", "HISTORICAL_UPDATE"]:
            # Trigger transaction sync in background
            background_tasks.add_task(
                sync_account_transactions,
                bank_account.id,
                bank_account.customer_id
            )

    # Handle item errors
    elif webhook_data.webhook_type == "ITEM":
        if webhook_data.webhook_code == "ERROR":
            bank_account.status = BankAccountStatus.ERROR
            await db.commit()

    return {"status": "processed", "action": webhook_result.get('action')}


# ============================================================================
# Background Tasks
# ============================================================================

async def sync_account_transactions(
    account_id: UUID,
    customer_id: UUID
):
    """
    Background task to sync transactions from Plaid.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Get bank account
            result = await db.execute(
                select(BankAccount).where(BankAccount.id == account_id)
            )
            account = result.scalar_one_or_none()

            if not account:
                logger.error(f"Bank account not found: {account_id}")
                return

            # Check if fraud detection is enabled
            feature_result = await db.execute(
                select(FeatureFlag).where(FeatureFlag.customer_id == customer_id)
            )
            feature_flag = feature_result.scalar_one_or_none()

            if not feature_flag or not feature_flag.is_enabled:
                logger.info(f"Fraud detection not enabled for customer {customer_id}")
                return

            # Decrypt access token
            access_token = decrypt_token(account.plaid_access_token_encrypted)

            # Sync transactions
            sync_result = await plaid_service.sync_transactions(access_token)

            # Process new transactions
            for txn_data in sync_result['added']:
                # Check if transaction already exists
                existing = await db.execute(
                    select(Transaction).where(
                        Transaction.plaid_transaction_id == txn_data['transaction_id']
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                # Create transaction record
                transaction = Transaction(
                    bank_account_id=account_id,
                    plaid_transaction_id=txn_data['transaction_id'],
                    transaction_date=txn_data['date'],
                    amount=Decimal(str(txn_data['amount'])),
                    description=txn_data.get('name'),
                    merchant_name=txn_data.get('merchant_name'),
                    category=txn_data.get('category'),
                    location=txn_data.get('location'),
                    payment_channel=txn_data.get('payment_channel'),
                )

                db.add(transaction)
                await db.flush()

                # Analyze for fraud
                if feature_flag.ml_detection or feature_flag.rule_based_detection:
                    await analyze_single_transaction(transaction, db)

            # Update account sync time
            account.last_sync_at = func.now()
            account.total_transactions = account.total_transactions + len(sync_result['added'])

            await db.commit()

            logger.info(
                f"Synced {len(sync_result['added'])} transactions for account {account_id}"
            )

        except Exception as e:
            logger.error(f"Error syncing transactions: {e}")
            await db.rollback()


async def analyze_single_transaction(
    transaction: Transaction,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Analyze a single transaction for fraud.
    """
    # Get account history for velocity features
    history_result = await db.execute(
        select(Transaction)
        .where(
            and_(
                Transaction.bank_account_id == transaction.bank_account_id,
                Transaction.transaction_date < transaction.transaction_date
            )
        )
        .order_by(desc(Transaction.transaction_date))
        .limit(100)
    )
    account_history = [
        {
            'transaction_date': t.transaction_date,
            'amount': float(t.amount),
            'merchant_name': t.merchant_name
        }
        for t in history_result.scalars().all()
    ]

    # Prepare transaction data for ML model
    txn_data = {
        'amount': float(transaction.amount),
        'transaction_date': transaction.transaction_date,
        'merchant_name': transaction.merchant_name,
        'category': transaction.category,
        'location': transaction.location,
        'payment_channel': transaction.payment_channel,
        'pending': False,
    }

    # Run ML fraud detection
    fraud_result = await ml_fraud_detector.predict_fraud(
        txn_data,
        account_history=account_history
    )

    # Update transaction with analysis results
    transaction.fraud_score = fraud_result['fraud_score']
    transaction.is_flagged = fraud_result['fraud_score'] >= settings.DEFAULT_FRAUD_THRESHOLD
    transaction.risk_level = fraud_result['risk_level']
    transaction.model_predictions = fraud_result['model_predictions']
    transaction.feature_importance = fraud_result['feature_importance']
    transaction.anomaly_score = fraud_result.get('anomaly_score', 0.0)
    transaction.flagged_reasons = {
        'rules': fraud_result['triggered_rules'],
        'explanation': fraud_result['explanation']
    }
    transaction.analyzed_at = func.now()
    transaction.analysis_version = "v1.0"

    # Create alert if needed
    if transaction.is_flagged and fraud_result['risk_level'] in [FraudSeverity.HIGH, FraudSeverity.CRITICAL]:
        alert = FraudAlert(
            transaction_id=transaction.id,
            alert_type="fraud_detection",
            severity=fraud_result['risk_level'],
            message=f"High-risk transaction detected: {fraud_result['explanation']}",
            details=fraud_result,
            triggered_rules=fraud_result['triggered_rules'],
            status=AlertStatus.NEW,
        )
        db.add(alert)

    return fraud_result


async def create_fraud_case_from_transaction(
    transaction: Transaction,
    analysis_result: Dict[str, Any],
    db: AsyncSession
) -> FraudCase:
    """
    Create fraud case from high-risk transaction.
    """
    # Get bank account for customer_id
    account_result = await db.execute(
        select(BankAccount).where(BankAccount.id == transaction.bank_account_id)
    )
    account = account_result.scalar_one()

    case_number = await generate_case_number()

    fraud_case = FraudCase(
        case_number=case_number,
        customer_id=account.customer_id,
        bank_account_id=transaction.bank_account_id,
        transaction_id=transaction.id,
        title=f"Suspicious transaction: ${transaction.amount}",
        description=analysis_result.get('explanation', 'High-risk transaction detected by ML model'),
        severity=analysis_result['risk_level'],
        status=FraudCaseStatus.OPEN,
        fraud_type="suspicious_transaction",
        estimated_loss_amount=abs(transaction.amount),
        detected_patterns=analysis_result.get('triggered_rules', []),
    )

    db.add(fraud_case)

    logger.info(f"Created fraud case {case_number} for transaction {transaction.id}")

    return fraud_case


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
