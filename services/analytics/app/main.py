"""
Aura Audit AI - Analytics Service

Journal Entry Testing, Anomaly Detection, and Ratio Analysis

Features:
- Journal Entry Testing (round-dollar, weekend, period-end)
- Anomaly Detection (Z-score, Isolation Forest)
- Ratio Analysis (liquidity, leverage, profitability)
- ML Model Integration with MLflow
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .config import settings
from .database import get_db
from .models import AnalyticsRule, AnalyticsResult, Anomaly, AnomalySeverity
from .schemas import (
    HealthResponse,
    AnalyticsRuleCreate,
    AnalyticsRuleResponse,
    RunAnalyticsRequest,
    RunAnalyticsSummary,
    AnalyticsResultResponse,
    AnomalyResponse,
    AnomalyListResponse,
    AnomalyResolve,
    JETestSummary,
    RatioAnalysisSummary
)
from .analytics_engine import (
    JournalEntryTester,
    AnomalyDetector,
    RatioAnalyzer
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura Audit AI - Analytics Service",
    description="JE testing, anomaly detection, and ratio analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        service="analytics",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aura Audit AI - Analytics Service",
        "version": "1.0.0",
        "features": [
            "Journal Entry Testing (round-dollar, weekend, period-end)",
            "Anomaly Detection (Z-score, Isolation Forest)",
            "Ratio Analysis (liquidity, leverage, profitability)"
        ],
        "docs": "/docs"
    }


# ========================================
# Journal Entry Testing
# ========================================

@app.post("/je-testing/{engagement_id}", response_model=JETestSummary)
async def run_je_tests(
    engagement_id: UUID,
    test_types: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Run journal entry tests on engagement

    Test Types:
    - round_dollar: Detect round-dollar amounts (e.g., $10,000.00)
    - weekend: Detect entries posted on weekends
    - period_end: Detect entries near period-end

    If test_types is None, all tests are run.
    """
    tester = JournalEntryTester()
    all_results = []

    # Determine which tests to run
    if test_types is None:
        test_types = ["round_dollar", "weekend", "period_end"]

    # Run selected tests
    if "round_dollar" in test_types:
        round_dollar_results = await tester.test_round_dollar_entries(engagement_id, db)
        all_results.extend(round_dollar_results)

    if "weekend" in test_types:
        weekend_results = await tester.test_weekend_entries(engagement_id, db)
        all_results.extend(weekend_results)

    if "period_end" in test_types:
        period_end_results = await tester.test_period_end_entries(engagement_id, db)
        all_results.extend(period_end_results)

    # Count results by type
    round_dollar_count = len([r for r in all_results if r.test_type == "round_dollar"])
    weekend_count = len([r for r in all_results if r.test_type == "weekend"])
    period_end_count = len([r for r in all_results if r.test_type == "period_end"])

    logger.info(
        f"JE tests completed for engagement {engagement_id}: "
        f"{round_dollar_count} round-dollar, {weekend_count} weekend, "
        f"{period_end_count} period-end"
    )

    return JETestSummary(
        engagement_id=engagement_id,
        total_entries_tested=len(all_results),
        round_dollar_flagged=round_dollar_count,
        weekend_flagged=weekend_count,
        period_end_flagged=period_end_count,
        results=all_results
    )


# ========================================
# Anomaly Detection
# ========================================

@app.post("/anomalies/{engagement_id}/detect")
async def detect_anomalies(
    engagement_id: UUID,
    method: str = "zscore",  # 'zscore' or 'isolation_forest'
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Detect anomalies in trial balance using statistical methods

    Methods:
    - zscore: Z-score outlier detection (default)
    - isolation_forest: Isolation Forest ML algorithm
    """
    detector = AnomalyDetector()

    if method == "zscore":
        outliers = await detector.detect_outliers_zscore(engagement_id, db)

        # Create anomaly records
        anomalies_created = []
        for outlier in outliers:
            anomaly = Anomaly(
                engagement_id=engagement_id,
                anomaly_type="outlier_zscore",
                severity=AnomalySeverity[outlier["severity"].upper()],
                title=f"Z-Score Outlier: {outlier['account_name']}",
                description=f"Account balance is {outlier['z_score']:.2f} standard deviations from mean",
                evidence=outlier,
                score=outlier["z_score"]
            )
            db.add(anomaly)
            anomalies_created.append(anomaly)

        await db.commit()

        logger.info(f"Created {len(anomalies_created)} anomaly records for engagement {engagement_id}")

        return {
            "method": "zscore",
            "engagement_id": engagement_id,
            "anomalies_detected": len(outliers),
            "outliers": outliers
        }

    elif method == "isolation_forest":
        # TODO: Implement Isolation Forest with trial balance data
        return {
            "method": "isolation_forest",
            "engagement_id": engagement_id,
            "message": "Isolation Forest detection coming soon"
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown method: {method}. Use 'zscore' or 'isolation_forest'"
        )


@app.get("/anomalies/{engagement_id}", response_model=AnomalyListResponse)
async def list_anomalies(
    engagement_id: UUID,
    severity: Optional[str] = None,
    resolution_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    List anomalies for engagement

    Filters:
    - severity: Filter by severity (info, low, medium, high, critical)
    - resolution_status: Filter by status (open, reviewed, resolved, false_positive)
    """
    query = select(Anomaly).where(Anomaly.engagement_id == engagement_id)

    if severity:
        query = query.where(Anomaly.severity == severity)

    if resolution_status:
        query = query.where(Anomaly.resolution_status == resolution_status)

    query = query.offset(skip).limit(limit).order_by(Anomaly.created_at.desc())

    result = await db.execute(query)
    anomalies = result.scalars().all()

    # Get counts
    total_result = await db.execute(
        select(Anomaly).where(Anomaly.engagement_id == engagement_id)
    )
    total = len(total_result.scalars().all())

    open_result = await db.execute(
        select(Anomaly).where(
            Anomaly.engagement_id == engagement_id,
            Anomaly.resolution_status == "open"
        )
    )
    open_count = len(open_result.scalars().all())

    critical_result = await db.execute(
        select(Anomaly).where(
            Anomaly.engagement_id == engagement_id,
            Anomaly.severity == AnomalySeverity.CRITICAL
        )
    )
    critical_count = len(critical_result.scalars().all())

    return AnomalyListResponse(
        anomalies=[AnomalyResponse.model_validate(a) for a in anomalies],
        total=total,
        open_count=open_count,
        critical_count=critical_count
    )


@app.patch("/anomalies/{anomaly_id}/resolve", response_model=AnomalyResponse)
async def resolve_anomaly(
    anomaly_id: UUID,
    resolution: AnomalyResolve,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Resolve an anomaly

    Status options: reviewed, resolved, false_positive
    """
    result = await db.execute(
        select(Anomaly).where(Anomaly.id == anomaly_id)
    )
    anomaly = result.scalar_one_or_none()

    if not anomaly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anomaly not found"
        )

    # Update resolution
    from datetime import datetime
    anomaly.resolution_status = resolution.resolution_status
    anomaly.resolution_notes = resolution.resolution_notes
    anomaly.resolved_by = current_user_id
    anomaly.resolved_at = datetime.utcnow()

    await db.commit()
    await db.refresh(anomaly)

    logger.info(f"Anomaly {anomaly_id} resolved as {resolution.resolution_status}")

    return AnomalyResponse.model_validate(anomaly)


# ========================================
# Ratio Analysis
# ========================================

@app.get("/ratios/{engagement_id}", response_model=RatioAnalysisSummary)
async def calculate_ratios(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Calculate financial ratios for engagement

    Ratios calculated:
    - Current Ratio (liquidity)
    - Quick Ratio (liquidity)
    - Debt-to-Equity (leverage)
    """
    analyzer = RatioAnalyzer()

    # Calculate ratios
    current_ratio = await analyzer.calculate_current_ratio(engagement_id, db)
    quick_ratio = await analyzer.calculate_quick_ratio(engagement_id, db)
    debt_to_equity = await analyzer.calculate_debt_to_equity(engagement_id, db)

    ratios = [current_ratio, quick_ratio, debt_to_equity]
    outliers_detected = sum(1 for r in ratios if r.is_outlier)

    logger.info(f"Calculated {len(ratios)} ratios for engagement {engagement_id}")

    return RatioAnalysisSummary(
        engagement_id=engagement_id,
        ratios_calculated=len(ratios),
        outliers_detected=outliers_detected,
        ratios=ratios
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
