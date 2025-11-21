"""
Predictive Analytics API Routes
=================================
FastAPI routes for ML-powered control failure prediction
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .models import User, UserRole
from .predictive_analytics import predictive_analytics_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictive-analytics", tags=["Predictive Analytics"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class TrainModelRequest(BaseModel):
    """Train ML model request"""
    model_type: str = Field(
        default="random_forest",
        pattern="^(random_forest|gradient_boosting|neural_network)$",
        description="ML model type to train"
    )


class TrainingResultResponse(BaseModel):
    """Training results response"""
    model_type: str
    training_samples: int
    test_samples: int
    train_accuracy: float
    test_accuracy: float
    precision: float
    recall: float
    f1_score: float
    cv_mean: float
    cv_std: float
    feature_importance: dict
    trained_at: str


class ControlPredictionResponse(BaseModel):
    """Control failure prediction response"""
    control_id: str
    failure_probability: float
    risk_score: int
    risk_level: str
    confidence_interval: dict
    risk_factors: List[dict]
    recommendations: List[str]
    estimated_remediation_hours: float
    prediction_timestamp: str
    model_used: str


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    control_id: str
    control_code: str
    control_name: str
    risk_score: int
    risk_level: str
    failure_probability: float
    top_risk_factor: str


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/train-model", response_model=TrainingResultResponse)
async def train_prediction_model(
    request: TrainModelRequest,
    db: AsyncSession = Depends(get_db)
    # current_user: User = Depends(get_current_user)  # TODO: Uncomment when auth is wired
) -> TrainingResultResponse:
    """
    Train ML model for control failure prediction

    **Requires:** CPA Partner or Manager role

    **Returns:** Training metrics and accuracy
    """
    logger.info(f"Training {request.model_type} model")

    try:
        results = await predictive_analytics_service.train_control_failure_model(
            db=db,
            model_type=request.model_type
        )

        return TrainingResultResponse(**results)

    except Exception as e:
        logger.error(f"Model training failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(e)}"
        )


@router.get("/controls/{control_id}/predict", response_model=ControlPredictionResponse)
async def predict_control_failure(
    control_id: UUID,
    db: AsyncSession = Depends(get_db)
    # current_user: User = Depends(get_current_user)
) -> ControlPredictionResponse:
    """
    Predict probability of control failure

    **Input:** Control ID

    **Returns:**
    - Failure probability (0.0 to 1.0)
    - Risk score (0-100)
    - Risk level (LOW, MEDIUM, HIGH, CRITICAL)
    - Contributing risk factors
    - AI-generated recommendations
    - Estimated remediation time
    """
    logger.info(f"Predicting failure for control {control_id}")

    try:
        prediction = await predictive_analytics_service.predict_control_failure(
            db=db,
            control_id=control_id
        )

        return ControlPredictionResponse(**prediction)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/engagements/{engagement_id}/at-risk-controls", response_model=List[BatchPredictionResponse])
async def get_at_risk_controls(
    engagement_id: UUID,
    top_n: int = 10,
    db: AsyncSession = Depends(get_db)
    # current_user: User = Depends(get_current_user)
) -> List[BatchPredictionResponse]:
    """
    Get top N at-risk controls for an engagement

    Predicts failure probability for all controls and returns highest risk ones.

    **Input:**
    - engagement_id: SOC engagement ID
    - top_n: Number of top risky controls to return (default: 10)

    **Returns:** List of at-risk controls sorted by risk score (highest first)

    **Use Case:** Identify which controls to focus testing on
    """
    logger.info(f"Getting at-risk controls for engagement {engagement_id}, top {top_n}")

    try:
        predictions = await predictive_analytics_service.predict_batch_controls(
            db=db,
            engagement_id=engagement_id,
            top_n=top_n
        )

        return [BatchPredictionResponse(**pred) for pred in predictions]

    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@router.get("/health")
async def health_check() -> dict:
    """
    Health check for predictive analytics service

    **Returns:** Service status and model availability
    """
    return {
        "service": "predictive_analytics",
        "status": "healthy",
        "models_loaded": len(predictive_analytics_service.models),
        "available_models": list(predictive_analytics_service.models.keys())
    }


@router.get("/model-info")
async def get_model_info() -> dict:
    """
    Get information about loaded ML models

    **Returns:**
    - Model types loaded
    - Feature names
    - Training status
    """
    return {
        "models_loaded": list(predictive_analytics_service.models.keys()),
        "feature_names": predictive_analytics_service.feature_names,
        "total_features": len(predictive_analytics_service.feature_names),
        "supported_model_types": ["random_forest", "gradient_boosting", "neural_network"]
    }
