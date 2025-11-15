"""
AI Feedback Loop Service

Captures CPA corrections and uses them to continuously improve AI models.

Features:
- Real-time feedback collection from CPAs
- Expert weighting (Partner > Manager > Senior > Staff)
- Nightly incremental retraining
- A/B testing for model versions
- Performance tracking and drift detection

Impact: Models improve automatically from every CPA interaction
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from loguru import logger

from .database import get_db, engine
from .models import (
    AIFeedback,
    ModelVersion,
    FeedbackQueue,
    ExpertProfile,
    ModelPerformanceMetric,
)
from .config import settings
from .training import IncrementalTrainer
from .ab_testing import ABTestManager


app = FastAPI(
    title="AI Feedback Loop Service",
    description="Continuous learning from CPA feedback",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching and job queue
redis_client = redis.from_url(settings.REDIS_URL)


class CPARole(str, Enum):
    """CPA expertise levels"""
    PARTNER = "partner"
    MANAGER = "manager"
    SENIOR = "senior"
    STAFF = "staff"


class FeedbackType(str, Enum):
    """Type of feedback"""
    CORRECTION = "correction"
    APPROVAL = "approval"
    REJECTION = "rejection"
    MODIFICATION = "modification"


# Expert weight mapping (used in training)
EXPERT_WEIGHTS = {
    CPARole.PARTNER: 4.0,
    CPARole.MANAGER: 2.5,
    CPARole.SENIOR: 1.5,
    CPARole.STAFF: 1.0,
}


class AIFeedbackRequest(BaseModel):
    """Request to log AI feedback"""
    # Original AI prediction
    model_name: str = Field(..., description="Model that made prediction")
    model_version: str = Field(..., description="Model version")
    prediction_id: str = Field(..., description="Unique prediction ID")
    input_data: Dict[str, Any] = Field(..., description="Input that was provided to model")
    ai_prediction: Dict[str, Any] = Field(..., description="AI's prediction")
    ai_confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")

    # CPA correction
    feedback_type: FeedbackType
    cpa_correction: Optional[Dict[str, Any]] = Field(None, description="CPA's correction (if different)")
    cpa_id: str = Field(..., description="CPA user ID")
    cpa_role: CPARole = Field(..., description="CPA's role/expertise level")

    # Context
    engagement_id: Optional[str] = None
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response after logging feedback"""
    feedback_id: str
    queued_for_training: bool
    queue_position: int
    estimated_training_time: Optional[datetime]
    message: str


class ModelPerformanceResponse(BaseModel):
    """Model performance metrics"""
    model_name: str
    model_version: str
    accuracy: float
    total_predictions: int
    total_corrections: int
    correction_rate: float
    last_trained: datetime
    improvement_over_baseline: float


@app.post("/feedback", response_model=FeedbackResponse)
async def log_feedback(
    request: AIFeedbackRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Log CPA feedback on AI prediction

    This is called whenever a CPA:
    - Approves an AI prediction
    - Corrects an AI prediction
    - Rejects an AI prediction
    """

    # Create feedback record
    feedback = AIFeedback(
        model_name=request.model_name,
        model_version=request.model_version,
        prediction_id=request.prediction_id,
        input_data=request.input_data,
        ai_prediction=request.ai_prediction,
        ai_confidence=request.ai_confidence,
        feedback_type=request.feedback_type.value,
        cpa_correction=request.cpa_correction,
        cpa_id=request.cpa_id,
        cpa_role=request.cpa_role.value,
        expert_weight=EXPERT_WEIGHTS[request.cpa_role],
        engagement_id=request.engagement_id,
        notes=request.notes,
        created_at=datetime.utcnow(),
    )

    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    logger.info(
        f"Feedback logged: {request.feedback_type.value} by {request.cpa_role.value} "
        f"on {request.model_name} prediction"
    )

    # Add to training queue if it's a correction
    queued = False
    queue_position = 0

    if request.feedback_type in [FeedbackType.CORRECTION, FeedbackType.MODIFICATION]:
        queue_item = FeedbackQueue(
            feedback_id=feedback.id,
            model_name=request.model_name,
            priority=EXPERT_WEIGHTS[request.cpa_role],  # Higher priority for senior experts
            status="pending",
            created_at=datetime.utcnow(),
        )

        db.add(queue_item)
        await db.commit()

        queued = True

        # Get queue position
        queue_count = await db.execute(
            select(func.count()).select_from(FeedbackQueue).where(
                FeedbackQueue.status == "pending"
            )
        )
        queue_position = queue_count.scalar()

    # Trigger background check for retraining
    background_tasks.add_task(check_retraining_threshold, request.model_name)

    # Estimate training time (nightly job, so next occurrence)
    now = datetime.utcnow()
    next_training = now.replace(hour=2, minute=0, second=0, microsecond=0)  # 2 AM UTC
    if now.hour >= 2:
        next_training += timedelta(days=1)

    return FeedbackResponse(
        feedback_id=str(feedback.id),
        queued_for_training=queued,
        queue_position=queue_position,
        estimated_training_time=next_training if queued else None,
        message=f"Feedback logged successfully. {'Queued for tonight\'s training.' if queued else 'Approved - no retraining needed.'}"
    )


async def check_retraining_threshold(model_name: str):
    """
    Check if we have enough feedback to trigger immediate retraining

    Threshold: 100 high-priority corrections (from Partners/Managers)
    """
    async with AsyncSession(engine) as db:
        # Count high-priority pending feedback
        result = await db.execute(
            select(func.count()).select_from(FeedbackQueue).where(
                FeedbackQueue.model_name == model_name,
                FeedbackQueue.status == "pending",
                FeedbackQueue.priority >= 2.5,  # Manager or Partner
            )
        )

        high_priority_count = result.scalar()

        if high_priority_count >= 100:
            logger.warning(
                f"High-priority feedback threshold reached for {model_name}: {high_priority_count} corrections. "
                "Triggering immediate retraining."
            )

            # Trigger immediate retraining
            await trigger_immediate_retraining(model_name)


async def trigger_immediate_retraining(model_name: str):
    """Trigger immediate retraining (for urgent corrections)"""
    trainer = IncrementalTrainer()

    try:
        await trainer.incremental_train(model_name, urgent=True)
        logger.success(f"Immediate retraining completed for {model_name}")
    except Exception as e:
        logger.error(f"Immediate retraining failed for {model_name}: {e}")


@app.get("/feedback/stats/{model_name}", response_model=ModelPerformanceResponse)
async def get_model_stats(
    model_name: str,
    version: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get performance statistics for a model

    Shows:
    - Accuracy (approvals / total predictions)
    - Correction rate
    - Total feedback count
    - Improvement over baseline
    """

    # Get model version
    if not version:
        result = await db.execute(
            select(ModelVersion).where(
                ModelVersion.model_name == model_name,
                ModelVersion.is_active == True,
            ).order_by(ModelVersion.created_at.desc())
        )
        model_version_obj = result.scalar_one_or_none()
        if not model_version_obj:
            raise HTTPException(404, f"No active version found for {model_name}")
        version = model_version_obj.version
    else:
        result = await db.execute(
            select(ModelVersion).where(
                ModelVersion.model_name == model_name,
                ModelVersion.version == version,
            )
        )
        model_version_obj = result.scalar_one_or_none()
        if not model_version_obj:
            raise HTTPException(404, f"Version {version} not found for {model_name}")

    # Get feedback stats
    total_result = await db.execute(
        select(func.count()).select_from(AIFeedback).where(
            AIFeedback.model_name == model_name,
            AIFeedback.model_version == version,
        )
    )
    total_predictions = total_result.scalar()

    approvals_result = await db.execute(
        select(func.count()).select_from(AIFeedback).where(
            AIFeedback.model_name == model_name,
            AIFeedback.model_version == version,
            AIFeedback.feedback_type == FeedbackType.APPROVAL.value,
        )
    )
    approvals = approvals_result.scalar()

    corrections_result = await db.execute(
        select(func.count()).select_from(AIFeedback).where(
            AIFeedback.model_name == model_name,
            AIFeedback.model_version == version,
            AIFeedback.feedback_type.in_([FeedbackType.CORRECTION.value, FeedbackType.MODIFICATION.value]),
        )
    )
    corrections = corrections_result.scalar()

    # Calculate metrics
    accuracy = approvals / total_predictions if total_predictions > 0 else 0
    correction_rate = corrections / total_predictions if total_predictions > 0 else 0

    # Get baseline performance
    baseline_accuracy = model_version_obj.baseline_accuracy or 0.90
    improvement = accuracy - baseline_accuracy

    return ModelPerformanceResponse(
        model_name=model_name,
        model_version=version,
        accuracy=accuracy,
        total_predictions=total_predictions,
        total_corrections=corrections,
        correction_rate=correction_rate,
        last_trained=model_version_obj.created_at,
        improvement_over_baseline=improvement,
    )


@app.post("/training/nightly")
async def run_nightly_training(background_tasks: BackgroundTasks):
    """
    Trigger nightly incremental training

    This endpoint is called by a cron job every night at 2 AM UTC

    Process:
    1. Collect all pending feedback from queue
    2. For each model with feedback:
       - Incremental training on new examples
       - Evaluate on validation set
       - If improvement > 2%, promote to A/B test
       - If A/B test shows improvement, deploy as active
    """

    background_tasks.add_task(nightly_training_job)

    return {"message": "Nightly training job started", "started_at": datetime.utcnow()}


async def nightly_training_job():
    """Background job for nightly training"""
    logger.info("Starting nightly training job...")

    async with AsyncSession(engine) as db:
        # Get all models with pending feedback
        result = await db.execute(
            select(FeedbackQueue.model_name, func.count().label('count'))
            .where(FeedbackQueue.status == "pending")
            .group_by(FeedbackQueue.model_name)
        )

        models_to_train = result.all()

        logger.info(f"Found {len(models_to_train)} models with pending feedback")

        for model_name, feedback_count in models_to_train:
            logger.info(f"Training {model_name} with {feedback_count} new examples...")

            try:
                trainer = IncrementalTrainer()
                new_version = await trainer.incremental_train(model_name)

                # Mark feedback as processed
                await db.execute(
                    FeedbackQueue.__table__.update()
                    .where(
                        FeedbackQueue.model_name == model_name,
                        FeedbackQueue.status == "pending",
                    )
                    .values(
                        status="trained",
                        processed_at=datetime.utcnow(),
                        model_version_trained=new_version,
                    )
                )
                await db.commit()

                logger.success(f"✓ {model_name} trained successfully: version {new_version}")

            except Exception as e:
                logger.error(f"✗ Training failed for {model_name}: {e}")

                # Mark as failed
                await db.execute(
                    FeedbackQueue.__table__.update()
                    .where(
                        FeedbackQueue.model_name == model_name,
                        FeedbackQueue.status == "pending",
                    )
                    .values(
                        status="failed",
                        processed_at=datetime.utcnow(),
                        error_message=str(e),
                    )
                )
                await db.commit()

    logger.info("Nightly training job completed")


@app.get("/models/{model_name}/versions")
async def list_model_versions(
    model_name: str,
    db: AsyncSession = Depends(get_db),
):
    """List all versions of a model with their performance"""

    result = await db.execute(
        select(ModelVersion)
        .where(ModelVersion.model_name == model_name)
        .order_by(ModelVersion.created_at.desc())
    )

    versions = result.scalars().all()

    return {
        "model_name": model_name,
        "versions": [
            {
                "version": v.version,
                "is_active": v.is_active,
                "is_ab_test": v.is_ab_test,
                "ab_test_traffic_pct": v.ab_test_traffic_pct,
                "accuracy": v.accuracy,
                "baseline_accuracy": v.baseline_accuracy,
                "training_samples": v.training_samples,
                "created_at": v.created_at,
            }
            for v in versions
        ]
    }


@app.post("/models/{model_name}/ab-test")
async def start_ab_test(
    model_name: str,
    old_version: str,
    new_version: str,
    traffic_percentage: float = 10.0,
    db: AsyncSession = Depends(get_db),
):
    """
    Start A/B test between two model versions

    Args:
        old_version: Current production version
        new_version: New version to test
        traffic_percentage: % of traffic to send to new version (default 10%)
    """

    ab_manager = ABTestManager(db)

    test_id = await ab_manager.start_test(
        model_name=model_name,
        version_a=old_version,
        version_b=new_version,
        traffic_split=traffic_percentage / 100.0,
    )

    return {
        "test_id": test_id,
        "model_name": model_name,
        "version_a": old_version,
        "version_b": new_version,
        "traffic_to_b": traffic_percentage,
        "message": f"A/B test started. {traffic_percentage}% of traffic will use {new_version}",
    }


@app.get("/models/{model_name}/ab-test/results")
async def get_ab_test_results(
    model_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Get A/B test results"""

    ab_manager = ABTestManager(db)
    results = await ab_manager.get_test_results(model_name)

    return results


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Feedback Loop",
        "timestamp": datetime.utcnow(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
