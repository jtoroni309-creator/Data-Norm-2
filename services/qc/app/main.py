"""
Aura Audit AI - Quality Control (QC) Service

Enforces audit standards and firm policies with:
- PCAOB AS 1215: Audit Documentation
- AICPA SAS 142: Audit Evidence
- AICPA SAS 145: Risk Assessment
- SEC 17 CFR 210.2-06: 7-year retention
- Firm-specific policies

This service provides BLOCKING gates that prevent binder finalization
until all compliance requirements are met.
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from .config import settings
from .database import get_db
from .models import QCPolicy, QCCheck, QCCheckStatus
from .schemas import (
    QCPolicyResponse,
    QCCheckRequest,
    QCCheckResponse,
    QCResultSummary,
    PolicyCreate,
    HealthResponse
)
from .policies import (
    PolicyRegistry,
    AS1215_AuditDocumentation,
    SAS142_AuditEvidence,
    SAS145_RiskAssessment,
    PartnerSignOffPolicy,
    ReviewNotesPolicy,
    MaterialAccountsCoveragePolicy,
    SubsequentEventsPolicy
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura Audit AI - QC Service",
    description="Quality control gates and policy enforcement",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize policy registry
policy_registry = PolicyRegistry()

# Register all policies
policy_registry.register(AS1215_AuditDocumentation())
policy_registry.register(SAS142_AuditEvidence())
policy_registry.register(SAS145_RiskAssessment())
policy_registry.register(PartnerSignOffPolicy())
policy_registry.register(ReviewNotesPolicy())
policy_registry.register(MaterialAccountsCoveragePolicy())
policy_registry.register(SubsequentEventsPolicy())


# ========================================
# Mock Authentication
# ========================================

async def get_current_user_id() -> UUID:
    """Mock function to get current user ID"""
    return UUID("00000000-0000-0000-0000-000000000001")


# ========================================
# Health & Status
# ========================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="qc",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aura Audit AI - QC Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "policies_registered": len(policy_registry.policies),
        "blocking_policies": len([p for p in policy_registry.policies.values() if p.is_blocking])
    }


# ========================================
# Policy Management
# ========================================

@app.get("/policies", response_model=List[QCPolicyResponse])
async def list_policies(
    is_active: Optional[bool] = None,
    is_blocking: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all QC policies

    Policies are rules that must be satisfied before binder finalization.
    Blocking policies prevent finalization if failed.
    """
    query = select(QCPolicy)

    if is_active is not None:
        query = query.where(QCPolicy.is_active == is_active)

    if is_blocking is not None:
        query = query.where(QCPolicy.is_blocking == is_blocking)

    query = query.order_by(QCPolicy.is_blocking.desc(), QCPolicy.policy_code)

    result = await db.execute(query)
    policies = result.scalars().all()

    return [QCPolicyResponse.model_validate(policy) for policy in policies]


@app.get("/policies/{policy_code}", response_model=QCPolicyResponse)
async def get_policy(
    policy_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific policy by code"""
    result = await db.execute(
        select(QCPolicy).where(QCPolicy.policy_code == policy_code)
    )
    policy = result.scalar_one_or_none()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy '{policy_code}' not found"
        )

    return QCPolicyResponse.model_validate(policy)


# ========================================
# QC Checks Execution
# ========================================

@app.post("/check", response_model=QCResultSummary)
async def run_qc_checks(
    check_request: QCCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Run all active QC checks for an engagement

    This is the PRIMARY endpoint called before binder finalization.

    Returns:
    - Summary of all checks (passed/failed/waived)
    - can_lock_binder flag (false if any blocking check failed)
    - Details of each check result

    Compliance:
    - PCAOB AS 1215: Ensures audit documentation is complete
    - AICPA SAS 142: Ensures sufficient appropriate evidence
    - AICPA SAS 145: Ensures risk assessment documented
    - Firm policies: Partner sign-off, review notes cleared, etc.
    """
    engagement_id = check_request.engagement_id

    logger.info(f"Running QC checks for engagement: {engagement_id}")

    # Get all active policies
    result = await db.execute(
        select(QCPolicy).where(QCPolicy.is_active == True)
    )
    policies = result.scalars().all()

    if not policies:
        logger.warning("No active policies found")
        return QCResultSummary(
            engagement_id=engagement_id,
            executed_at=datetime.utcnow(),
            total_checks=0,
            passed=0,
            failed=0,
            waived=0,
            blocking_failed=0,
            can_lock_binder=True,
            checks=[]
        )

    # Execute each policy check
    check_results = []
    passed_count = 0
    failed_count = 0
    waived_count = 0
    blocking_failed_count = 0

    for policy in policies:
        try:
            # Get policy evaluator from registry
            evaluator = policy_registry.get(policy.policy_code)

            if not evaluator:
                logger.warning(f"No evaluator found for policy: {policy.policy_code}")
                continue

            # Execute policy check
            check_result = await evaluator.evaluate(
                engagement_id=engagement_id,
                db=db
            )

            # Determine status
            if check_result.get("waived", False):
                check_status = QCCheckStatus.WAIVED
                waived_count += 1
            elif check_result.get("passed", False):
                check_status = QCCheckStatus.PASSED
                passed_count += 1
            else:
                check_status = QCCheckStatus.FAILED
                failed_count += 1

                if policy.is_blocking:
                    blocking_failed_count += 1

            # Save check result to database
            qc_check = QCCheck(
                engagement_id=engagement_id,
                policy_id=policy.id,
                executed_at=datetime.utcnow(),
                status=check_status,
                result_data=check_result
            )
            db.add(qc_check)

            # Build response
            check_response = QCCheckResponse(
                policy_code=policy.policy_code,
                policy_name=policy.policy_name,
                standard_reference=policy.standard_reference,
                is_blocking=policy.is_blocking,
                status=check_status,
                passed=check_result.get("passed", False),
                details=check_result.get("details", ""),
                remediation=check_result.get("remediation", ""),
                evidence=check_result.get("evidence", {})
            )

            check_results.append(check_response)

        except Exception as e:
            logger.error(f"Error executing policy {policy.policy_code}: {e}")

            # Record failed check
            qc_check = QCCheck(
                engagement_id=engagement_id,
                policy_id=policy.id,
                executed_at=datetime.utcnow(),
                status=QCCheckStatus.FAILED,
                result_data={"error": str(e)}
            )
            db.add(qc_check)

            check_results.append(QCCheckResponse(
                policy_code=policy.policy_code,
                policy_name=policy.policy_name,
                standard_reference=policy.standard_reference,
                is_blocking=policy.is_blocking,
                status=QCCheckStatus.FAILED,
                passed=False,
                details=f"Error executing check: {str(e)}",
                remediation="Contact system administrator"
            ))

            failed_count += 1
            if policy.is_blocking:
                blocking_failed_count += 1

    await db.commit()

    # Determine if binder can be locked
    can_lock_binder = blocking_failed_count == 0

    summary = QCResultSummary(
        engagement_id=engagement_id,
        executed_at=datetime.utcnow(),
        total_checks=len(check_results),
        passed=passed_count,
        failed=failed_count,
        waived=waived_count,
        blocking_failed=blocking_failed_count,
        can_lock_binder=can_lock_binder,
        checks=check_results
    )

    logger.info(
        f"QC checks completed: {passed_count} passed, {failed_count} failed, "
        f"{waived_count} waived, {blocking_failed_count} blocking failures"
    )

    if not can_lock_binder:
        logger.warning(
            f"Binder lock BLOCKED for engagement {engagement_id}: "
            f"{blocking_failed_count} blocking check(s) failed"
        )

    return summary


@app.get("/engagements/{engagement_id}/checks", response_model=List[QCCheckResponse])
async def get_engagement_checks(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all QC check results for an engagement

    Shows historical check results including passed, failed, and waived checks.
    """
    result = await db.execute(
        select(QCCheck)
        .where(QCCheck.engagement_id == engagement_id)
        .order_by(QCCheck.executed_at.desc())
    )
    checks = result.scalars().all()

    # Get policy details for each check
    check_responses = []
    for check in checks:
        result = await db.execute(
            select(QCPolicy).where(QCPolicy.id == check.policy_id)
        )
        policy = result.scalar_one_or_none()

        if policy:
            check_responses.append(QCCheckResponse(
                policy_code=policy.policy_code,
                policy_name=policy.policy_name,
                standard_reference=policy.standard_reference,
                is_blocking=policy.is_blocking,
                status=check.status,
                passed=check.status == QCCheckStatus.PASSED,
                details=check.result_data.get("details", ""),
                remediation=check.result_data.get("remediation", ""),
                evidence=check.result_data.get("evidence", {}),
                executed_at=check.executed_at
            ))

    return check_responses


@app.get("/engagements/{engagement_id}/checks/latest", response_model=QCResultSummary)
async def get_latest_check_summary(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent QC check summary for an engagement

    This endpoint is typically called by the UI to display current QC status.
    """
    # Get the most recent execution time
    result = await db.execute(
        select(QCCheck.executed_at)
        .where(QCCheck.engagement_id == engagement_id)
        .order_by(QCCheck.executed_at.desc())
        .limit(1)
    )
    latest_execution = result.scalar_one_or_none()

    if not latest_execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No QC checks have been run for this engagement"
        )

    # Get all checks from that execution
    result = await db.execute(
        select(QCCheck)
        .where(
            and_(
                QCCheck.engagement_id == engagement_id,
                QCCheck.executed_at == latest_execution
            )
        )
    )
    checks = result.scalars().all()

    # Build summary
    check_responses = []
    passed = 0
    failed = 0
    waived = 0
    blocking_failed = 0

    for check in checks:
        result = await db.execute(
            select(QCPolicy).where(QCPolicy.id == check.policy_id)
        )
        policy = result.scalar_one_or_none()

        if not policy:
            continue

        if check.status == QCCheckStatus.PASSED:
            passed += 1
        elif check.status == QCCheckStatus.FAILED:
            failed += 1
            if policy.is_blocking:
                blocking_failed += 1
        elif check.status == QCCheckStatus.WAIVED:
            waived += 1

        check_responses.append(QCCheckResponse(
            policy_code=policy.policy_code,
            policy_name=policy.policy_name,
            standard_reference=policy.standard_reference,
            is_blocking=policy.is_blocking,
            status=check.status,
            passed=check.status == QCCheckStatus.PASSED,
            details=check.result_data.get("details", ""),
            remediation=check.result_data.get("remediation", ""),
            evidence=check.result_data.get("evidence", {}),
            executed_at=check.executed_at
        ))

    return QCResultSummary(
        engagement_id=engagement_id,
        executed_at=latest_execution,
        total_checks=len(check_responses),
        passed=passed,
        failed=failed,
        waived=waived,
        blocking_failed=blocking_failed,
        can_lock_binder=blocking_failed == 0,
        checks=check_responses
    )


# ========================================
# Policy Waivers
# ========================================

@app.post("/engagements/{engagement_id}/checks/{check_id}/waive")
async def waive_check(
    engagement_id: UUID,
    check_id: UUID,
    waiver_reason: str = Field(..., min_length=10),
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Waive a failed QC check

    Requires:
    - Partner role (enforced by calling service)
    - Written justification (min 10 characters)

    Waived checks do not block binder finalization but are recorded
    for peer review and regulatory examination.

    Compliance Note:
    Per PCAOB AS 1215, waivers must be documented with:
    - Who authorized the waiver
    - When it was waived
    - Why it was waived
    - What compensating procedures were performed
    """
    result = await db.execute(
        select(QCCheck).where(
            and_(
                QCCheck.id == check_id,
                QCCheck.engagement_id == engagement_id
            )
        )
    )
    check = result.scalar_one_or_none()

    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QC check not found"
        )

    if check.status != QCCheckStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only failed checks can be waived"
        )

    # Update check to waived
    check.status = QCCheckStatus.WAIVED
    check.waived_by = current_user_id
    check.waived_at = datetime.utcnow()
    check.waiver_reason = waiver_reason

    await db.commit()

    logger.warning(
        f"QC check waived: engagement={engagement_id}, check={check_id}, "
        f"user={current_user_id}, reason={waiver_reason}"
    )

    return {
        "message": "Check waived successfully",
        "check_id": str(check_id),
        "waived_by": str(current_user_id),
        "waived_at": check.waived_at,
        "reason": waiver_reason
    }


# ========================================
# Compliance Reports
# ========================================

@app.get("/compliance/summary")
async def get_compliance_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get firm-wide compliance summary

    Shows:
    - Total engagements checked
    - Pass rate by policy
    - Common failure points
    - Waiver trends

    Useful for:
    - Internal quality reviews
    - Peer review preparation
    - PCAOB inspection readiness
    """
    # Get all checks in date range
    query = select(QCCheck)

    if start_date:
        query = query.where(QCCheck.executed_at >= start_date)

    if end_date:
        query = query.where(QCCheck.executed_at <= end_date)

    result = await db.execute(query)
    checks = result.scalars().all()

    # Calculate statistics
    total_checks = len(checks)
    passed = sum(1 for c in checks if c.status == QCCheckStatus.PASSED)
    failed = sum(1 for c in checks if c.status == QCCheckStatus.FAILED)
    waived = sum(1 for c in checks if c.status == QCCheckStatus.WAIVED)

    pass_rate = (passed / total_checks * 100) if total_checks > 0 else 0

    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "summary": {
            "total_checks": total_checks,
            "passed": passed,
            "failed": failed,
            "waived": waived,
            "pass_rate_percent": round(pass_rate, 2)
        },
        "note": "Detailed policy-level statistics not yet implemented"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
