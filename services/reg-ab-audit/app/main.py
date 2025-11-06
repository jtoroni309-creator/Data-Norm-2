"""
Regulation A/B Audit Service - Main FastAPI Application

AI-powered Regulation A/B compliance auditing for CMBS loans with automated
workpaper generation and CPA review workflow.

Supports: PCAOB, GAAP, GAAS, SEC, AICPA standards compliance
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db, AsyncSessionLocal
from .ai_compliance_engine import AIComplianceEngine
from .workpaper_generator import WorkpaperGenerator
from .report_generator import ReportGenerator
from .models import (
    CMBSDeal,
    CMBSDealStatus,
    ComplianceCheck,
    ComplianceCheckStatus,
    ComplianceStandard,
    CPASignoff,
    RegABAuditEngagement,
    RegABAuditStatus,
    RegABFeatureFlag,
    RegABWorkpaper,
    RegABAuditReport,
    SignoffStatus,
    WorkpaperStatus,
)
from .schemas import (
    CMBSDealCreate,
    CMBSDealResponse,
    CMBSDealUpdate,
    ComplianceCheckResponse,
    CPASignoffCreate,
    CPASignoffResponse,
    DashboardMetrics,
    FeatureFlagResponse,
    FeatureFlagUpdate,
    RegABAuditEngagementCreate,
    RegABAuditEngagementResponse,
    RegABAuditEngagementUpdate,
    WorkpaperResponse,
    ReportResponse,
)

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Regulation A/B audit for CMBS loans with PCAOB, GAAP, GAAS, SEC, AICPA compliance",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI services
ai_compliance_engine = AIComplianceEngine(
    api_key=settings.OPENAI_API_KEY,
    model_version=settings.AI_MODEL_VERSION
)
workpaper_generator = WorkpaperGenerator(ai_engine=ai_compliance_engine)
report_generator = ReportGenerator(ai_engine=ai_compliance_engine)

# Security Middleware
try:
    import sys
    sys.path.insert(0, '/home/user/Data-Norm-2/services')
    from security.app import SecurityMiddleware, AuditLogService

    audit_log_service = AuditLogService()
    app.add_middleware(
        SecurityMiddleware,
        audit_log_service=audit_log_service,
        enable_rate_limiting=True,
        enable_ip_filtering=False,
        enable_csrf_protection=False,
    )
except ImportError:
    logger.warning("Security middleware not available, running without enhanced security")


# ========================================
# Authentication & Authorization
# ========================================

async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Extract user from JWT token in Authorization header.
    In production, this should validate the JWT and extract user info.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    # In production: Validate JWT and extract user_id, organization_id, role
    # For now, we'll accept a simple structure
    return {
        "user_id": UUID("00000000-0000-0000-0000-000000000000"),  # Replace with actual
        "organization_id": UUID("00000000-0000-0000-0000-000000000000"),
        "role": "partner",
        "email": "user@example.com"
    }


async def require_feature_enabled(
    organization_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> RegABFeatureFlag:
    """
    Check if Regulation A/B audit feature is enabled for organization.
    """
    result = await db.execute(
        select(RegABFeatureFlag).where(
            RegABFeatureFlag.organization_id == organization_id
        )
    )
    feature_flag = result.scalar_one_or_none()

    if not feature_flag or not feature_flag.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Regulation A/B audit feature is not enabled for your organization"
        )

    return feature_flag


# ========================================
# Health Check
# ========================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "reg-ab-audit",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


# ========================================
# Feature Flag Management (Admin)
# ========================================

@app.get("/api/feature-flags/{organization_id}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    organization_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get feature flag settings for an organization.
    Creates default disabled flag if none exists.
    """
    result = await db.execute(
        select(RegABFeatureFlag).where(
            RegABFeatureFlag.organization_id == organization_id
        )
    )
    feature_flag = result.scalar_one_or_none()

    if not feature_flag:
        # Create default disabled flag
        feature_flag = RegABFeatureFlag(
            organization_id=organization_id,
            is_enabled=False
        )
        db.add(feature_flag)
        await db.commit()
        await db.refresh(feature_flag)

    return feature_flag


@app.patch("/api/feature-flags/{organization_id}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    organization_id: UUID,
    update_data: FeatureFlagUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update feature flag settings (Admin only).
    """
    # Check admin role
    if current_user.get("role") not in ["partner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only partners and admins can modify feature flags"
        )

    result = await db.execute(
        select(RegABFeatureFlag).where(
            RegABFeatureFlag.organization_id == organization_id
        )
    )
    feature_flag = result.scalar_one_or_none()

    if not feature_flag:
        feature_flag = RegABFeatureFlag(organization_id=organization_id)
        db.add(feature_flag)

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(feature_flag, key, value)

    # Track enablement
    if update_data.is_enabled and not feature_flag.enabled_at:
        feature_flag.enabled_at = datetime.utcnow()
        feature_flag.enabled_by = current_user["user_id"]

    await db.commit()
    await db.refresh(feature_flag)

    logger.info(f"Feature flag updated for organization {organization_id} by {current_user['email']}")

    return feature_flag


# ========================================
# Audit Engagement Management
# ========================================

@app.get("/api/engagements", response_model=List[RegABAuditEngagementResponse])
async def list_engagements(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all Regulation A/B audit engagements for the current user's organization.
    """
    query = select(RegABAuditEngagement).where(
        and_(
            RegABAuditEngagement.organization_id == current_user["organization_id"],
            RegABAuditEngagement.deleted_at.is_(None)
        )
    )

    if status:
        query = query.where(RegABAuditEngagement.status == status)

    query = query.offset(skip).limit(limit).order_by(desc(RegABAuditEngagement.created_at))

    result = await db.execute(query)
    engagements = result.scalars().all()

    return engagements


@app.post("/api/engagements", response_model=RegABAuditEngagementResponse, status_code=201)
async def create_engagement(
    engagement: RegABAuditEngagementCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new Regulation A/B audit engagement.
    """
    # Check feature is enabled
    await require_feature_enabled(current_user["organization_id"], db)

    # Create engagement
    db_engagement = RegABAuditEngagement(
        **engagement.model_dump(),
        organization_id=current_user["organization_id"]
    )

    db.add(db_engagement)
    await db.commit()
    await db.refresh(db_engagement)

    logger.info(f"Created Reg A/B engagement {db_engagement.id} by {current_user['email']}")

    return db_engagement


@app.get("/api/engagements/{engagement_id}", response_model=RegABAuditEngagementResponse)
async def get_engagement(
    engagement_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific audit engagement by ID."""
    result = await db.execute(
        select(RegABAuditEngagement).where(
            and_(
                RegABAuditEngagement.id == engagement_id,
                RegABAuditEngagement.organization_id == current_user["organization_id"],
                RegABAuditEngagement.deleted_at.is_(None)
            )
        )
    )
    engagement = result.scalar_one_or_none()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    return engagement


@app.patch("/api/engagements/{engagement_id}", response_model=RegABAuditEngagementResponse)
async def update_engagement(
    engagement_id: UUID,
    update_data: RegABAuditEngagementUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an audit engagement."""
    result = await db.execute(
        select(RegABAuditEngagement).where(
            and_(
                RegABAuditEngagement.id == engagement_id,
                RegABAuditEngagement.organization_id == current_user["organization_id"]
            )
        )
    )
    engagement = result.scalar_one_or_none()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(engagement, key, value)

    await db.commit()
    await db.refresh(engagement)

    return engagement


# ========================================
# CMBS Deal Management (Client Portal)
# ========================================

@app.get("/api/engagements/{engagement_id}/deals", response_model=List[CMBSDealResponse])
async def list_deals(
    engagement_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all CMBS deals for an engagement."""
    result = await db.execute(
        select(CMBSDeal).where(
            CMBSDeal.audit_engagement_id == engagement_id
        ).order_by(CMBSDeal.created_at)
    )
    deals = result.scalars().all()
    return deals


@app.post("/api/engagements/{engagement_id}/deals", response_model=CMBSDealResponse, status_code=201)
async def create_deal(
    engagement_id: UUID,
    deal: CMBSDealCreate,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new CMBS deal (Client Portal).
    Triggers AI processing in background.
    """
    # Verify engagement exists
    result = await db.execute(
        select(RegABAuditEngagement).where(RegABAuditEngagement.id == engagement_id)
    )
    engagement = result.scalar_one_or_none()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # Create deal
    db_deal = CMBSDeal(
        **deal.model_dump(),
        audit_engagement_id=engagement_id,
        submitted_by=current_user["user_id"],
        submitted_at=datetime.utcnow()
    )

    db.add(db_deal)

    # Update engagement counts
    engagement.total_cmbs_deals = (engagement.total_cmbs_deals or 0) + 1

    await db.commit()
    await db.refresh(db_deal)

    # Trigger AI processing in background
    background_tasks.add_task(
        process_deal_with_ai,
        deal_id=db_deal.id,
        engagement_id=engagement_id
    )

    logger.info(f"Created CMBS deal {db_deal.id} for engagement {engagement_id}")

    return db_deal


@app.get("/api/deals/{deal_id}", response_model=CMBSDealResponse)
async def get_deal(
    deal_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific CMBS deal."""
    result = await db.execute(
        select(CMBSDeal).where(CMBSDeal.id == deal_id)
    )
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    return deal


# ========================================
# AI Processing & Compliance Checks
# ========================================

async def process_deal_with_ai(deal_id: UUID, engagement_id: UUID):
    """
    Background task to process a CMBS deal with AI compliance checking.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Get deal and engagement
            deal_result = await db.execute(
                select(CMBSDeal).where(CMBSDeal.id == deal_id)
            )
            deal = deal_result.scalar_one()

            engagement_result = await db.execute(
                select(RegABAuditEngagement).where(
                    RegABAuditEngagement.id == engagement_id
                )
            )
            engagement = engagement_result.scalar_one()

            # Update status
            deal.status = CMBSDealStatus.PENDING_AUDIT
            engagement.status = RegABAuditStatus.AI_PROCESSING
            if not engagement.ai_processing_started_at:
                engagement.ai_processing_started_at = datetime.utcnow()

            await db.commit()

            # Run AI compliance checks
            logger.info(f"Starting AI compliance checks for deal {deal_id}")

            compliance_results = await ai_compliance_engine.run_compliance_checks(
                deal=deal,
                engagement=engagement
            )

            # Save compliance check results
            for check_result in compliance_results:
                db_check = ComplianceCheck(**check_result)
                db.add(db_check)

            # Update engagement statistics
            engagement.processed_deals = (engagement.processed_deals or 0) + 1
            engagement.total_compliance_checks = (engagement.total_compliance_checks or 0) + len(compliance_results)
            engagement.passed_compliance_checks = (engagement.passed_compliance_checks or 0) + sum(
                1 for r in compliance_results if r.get("passed")
            )
            engagement.failed_compliance_checks = (engagement.failed_compliance_checks or 0) + sum(
                1 for r in compliance_results if not r.get("passed")
            )

            await db.commit()

            # Generate workpapers
            logger.info(f"Generating workpapers for deal {deal_id}")

            workpapers = await workpaper_generator.generate_workpapers(
                deal=deal,
                engagement=engagement,
                compliance_results=compliance_results
            )

            for workpaper_data in workpapers:
                db_workpaper = RegABWorkpaper(**workpaper_data)
                db.add(db_workpaper)

            engagement.total_workpapers = (engagement.total_workpapers or 0) + len(workpapers)

            await db.commit()

            # Update deal status
            deal.status = CMBSDealStatus.AUDIT_COMPLETE

            # Check if all deals processed
            deals_result = await db.execute(
                select(func.count(CMBSDeal.id)).where(
                    CMBSDeal.audit_engagement_id == engagement_id
                )
            )
            total_deals = deals_result.scalar()

            if engagement.processed_deals >= total_deals:
                engagement.status = RegABAuditStatus.WORKPAPER_GENERATION
                engagement.ai_processing_completed_at = datetime.utcnow()

                if engagement.ai_processing_started_at:
                    duration = (engagement.ai_processing_completed_at - engagement.ai_processing_started_at).total_seconds()
                    engagement.ai_processing_duration_seconds = int(duration)

                # Generate audit report
                logger.info(f"All deals processed, generating audit report for engagement {engagement_id}")

                report_data = await report_generator.generate_report(
                    engagement=engagement,
                    db=db
                )

                db_report = RegABAuditReport(**report_data)
                db.add(db_report)

                engagement.status = RegABAuditStatus.CPA_REVIEW
                engagement.report_generated_at = datetime.utcnow()
                engagement.report_url = report_data.get("content_pdf_url")

                # Notify CPA for review
                # TODO: Send notification

            await db.commit()

            logger.info(f"Successfully processed deal {deal_id}")

        except Exception as e:
            logger.error(f"Error processing deal {deal_id}: {str(e)}", exc_info=True)
            await db.rollback()


@app.get("/api/engagements/{engagement_id}/compliance-checks", response_model=List[ComplianceCheckResponse])
async def list_compliance_checks(
    engagement_id: UUID,
    standard: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all compliance checks for an engagement."""
    query = select(ComplianceCheck).where(
        ComplianceCheck.audit_engagement_id == engagement_id
    )

    if standard:
        query = query.where(ComplianceCheck.standard == standard)
    if status:
        query = query.where(ComplianceCheck.status == status)

    query = query.order_by(ComplianceCheck.created_at)

    result = await db.execute(query)
    checks = result.scalars().all()

    return checks


# ========================================
# Workpaper Management (CPA Portal)
# ========================================

@app.get("/api/engagements/{engagement_id}/workpapers", response_model=List[WorkpaperResponse])
async def list_workpapers(
    engagement_id: UUID,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all workpapers for an engagement."""
    query = select(RegABWorkpaper).where(
        RegABWorkpaper.audit_engagement_id == engagement_id
    )

    if status:
        query = query.where(RegABWorkpaper.status == status)

    query = query.order_by(RegABWorkpaper.workpaper_ref)

    result = await db.execute(query)
    workpapers = result.scalars().all()

    return workpapers


@app.get("/api/workpapers/{workpaper_id}", response_model=WorkpaperResponse)
async def get_workpaper(
    workpaper_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific workpaper."""
    result = await db.execute(
        select(RegABWorkpaper).where(RegABWorkpaper.id == workpaper_id)
    )
    workpaper = result.scalar_one_or_none()

    if not workpaper:
        raise HTTPException(status_code=404, detail="Workpaper not found")

    return workpaper


@app.post("/api/workpapers/{workpaper_id}/review")
async def review_workpaper(
    workpaper_id: UUID,
    action: str,  # 'approve' or 'request_revision'
    notes: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    CPA review of workpaper.
    """
    # Check CPA role
    if current_user.get("role") not in ["partner", "manager", "senior"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only CPAs can review workpapers"
        )

    result = await db.execute(
        select(RegABWorkpaper).where(RegABWorkpaper.id == workpaper_id)
    )
    workpaper = result.scalar_one_or_none()

    if not workpaper:
        raise HTTPException(status_code=404, detail="Workpaper not found")

    if action == "approve":
        workpaper.status = WorkpaperStatus.APPROVED
        workpaper.approved_at = datetime.utcnow()
        workpaper.approved_by = current_user["user_id"]

        # Update engagement statistics
        engagement_result = await db.execute(
            select(RegABAuditEngagement).where(
                RegABAuditEngagement.id == workpaper.audit_engagement_id
            )
        )
        engagement = engagement_result.scalar_one()
        engagement.approved_workpapers = (engagement.approved_workpapers or 0) + 1

    elif action == "request_revision":
        workpaper.status = WorkpaperStatus.REVISION_REQUIRED
        workpaper.revision_count = (workpaper.revision_count or 0) + 1
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    workpaper.reviewer_id = current_user["user_id"]
    workpaper.reviewed_at = datetime.utcnow()
    workpaper.review_notes = notes

    await db.commit()
    await db.refresh(workpaper)

    return {"status": "success", "workpaper": workpaper}


# ========================================
# Report Management
# ========================================

@app.get("/api/engagements/{engagement_id}/reports", response_model=List[ReportResponse])
async def list_reports(
    engagement_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all reports for an engagement."""
    result = await db.execute(
        select(RegABAuditReport).where(
            RegABAuditReport.audit_engagement_id == engagement_id
        ).order_by(desc(RegABAuditReport.version))
    )
    reports = result.scalars().all()

    return reports


@app.get("/api/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific report."""
    result = await db.execute(
        select(RegABAuditReport).where(RegABAuditReport.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


# ========================================
# CPA Sign-Off Workflow
# ========================================

@app.post("/api/reports/{report_id}/signoff", response_model=CPASignoffResponse, status_code=201)
async def create_signoff(
    report_id: UUID,
    signoff: CPASignoffCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    CPA signs off on a report.
    """
    # Verify CPA credentials
    if current_user.get("role") not in ["partner", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only licensed CPAs can sign off on reports"
        )

    # Get report and engagement
    report_result = await db.execute(
        select(RegABAuditReport).where(RegABAuditReport.id == report_id)
    )
    report = report_result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Create sign-off
    db_signoff = CPASignoff(
        **signoff.model_dump(),
        audit_engagement_id=report.audit_engagement_id,
        report_id=report_id,
        cpa_user_id=current_user["user_id"],
        signature_timestamp=datetime.utcnow(),
        # signature_ip_address would be extracted from request in production
    )

    db.add(db_signoff)

    # Update engagement status
    engagement_result = await db.execute(
        select(RegABAuditEngagement).where(
            RegABAuditEngagement.id == report.audit_engagement_id
        )
    )
    engagement = engagement_result.scalar_one()

    if signoff.status == SignoffStatus.APPROVED:
        db_signoff.approved_at = datetime.utcnow()
        engagement.status = RegABAuditStatus.CPA_APPROVED
        engagement.reviewed_at = datetime.utcnow()
        report.draft = False

        # Check if finalization is allowed
        # (e.g., all workpapers approved, all checks passed)
        can_finalize = True  # Add actual logic here

        if can_finalize:
            engagement.status = RegABAuditStatus.FINALIZED
            engagement.finalized_at = datetime.utcnow()

    elif signoff.status == SignoffStatus.REJECTED:
        db_signoff.rejected_at = datetime.utcnow()
        engagement.status = RegABAuditStatus.REVISION_REQUIRED

    await db.commit()
    await db.refresh(db_signoff)

    logger.info(f"CPA signoff created for report {report_id} by {current_user['email']}")

    return db_signoff


@app.get("/api/engagements/{engagement_id}/signoffs", response_model=List[CPASignoffResponse])
async def list_signoffs(
    engagement_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all sign-offs for an engagement."""
    result = await db.execute(
        select(CPASignoff).where(
            CPASignoff.audit_engagement_id == engagement_id
        ).order_by(desc(CPASignoff.created_at))
    )
    signoffs = result.scalars().all()

    return signoffs


# ========================================
# Dashboard & Metrics
# ========================================

@app.get("/api/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard metrics for the organization.
    """
    org_id = current_user["organization_id"]

    # Count engagements by status
    engagement_counts = await db.execute(
        select(
            RegABAuditEngagement.status,
            func.count(RegABAuditEngagement.id)
        ).where(
            and_(
                RegABAuditEngagement.organization_id == org_id,
                RegABAuditEngagement.deleted_at.is_(None)
            )
        ).group_by(RegABAuditEngagement.status)
    )

    status_counts = {row[0]: row[1] for row in engagement_counts}

    # Total CMBS deals
    total_deals = await db.execute(
        select(func.count(CMBSDeal.id)).select_from(
            CMBSDeal
        ).join(
            RegABAuditEngagement,
            CMBSDeal.audit_engagement_id == RegABAuditEngagement.id
        ).where(
            RegABAuditEngagement.organization_id == org_id
        )
    )

    # Compliance statistics
    compliance_stats = await db.execute(
        select(
            func.count(ComplianceCheck.id).label("total"),
            func.count(ComplianceCheck.id).filter(
                ComplianceCheck.status == ComplianceCheckStatus.PASSED
            ).label("passed"),
            func.count(ComplianceCheck.id).filter(
                ComplianceCheck.status == ComplianceCheckStatus.FAILED
            ).label("failed")
        ).select_from(
            ComplianceCheck
        ).join(
            RegABAuditEngagement,
            ComplianceCheck.audit_engagement_id == RegABAuditEngagement.id
        ).where(
            RegABAuditEngagement.organization_id == org_id
        )
    )

    comp_stats = compliance_stats.one()

    return {
        "total_engagements": sum(status_counts.values()),
        "active_engagements": status_counts.get(RegABAuditStatus.AI_PROCESSING, 0) +
                             status_counts.get(RegABAuditStatus.CPA_REVIEW, 0),
        "completed_engagements": status_counts.get(RegABAuditStatus.FINALIZED, 0),
        "total_cmbs_deals": total_deals.scalar(),
        "total_compliance_checks": comp_stats.total or 0,
        "passed_compliance_checks": comp_stats.passed or 0,
        "failed_compliance_checks": comp_stats.failed or 0,
        "compliance_pass_rate": (
            (comp_stats.passed / comp_stats.total * 100) if comp_stats.total else 0
        )
    }


# ========================================
# Main Entry Point
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
