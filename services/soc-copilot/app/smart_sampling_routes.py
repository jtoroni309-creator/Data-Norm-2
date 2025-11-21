"""
Smart Statistical Sampling API Routes
=======================================
FastAPI routes for AI-optimized adaptive sampling
"""

import logging
from typing import List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .models import User, UserRole
from .smart_sampling import smart_sampling_service, SamplingMethod

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sampling", tags=["Smart Sampling"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CalculateSampleSizeRequest(BaseModel):
    """Calculate sample size request"""
    population_size: int = Field(..., ge=1, description="Total population size")
    confidence_level: float = Field(default=95.0, ge=90.0, le=99.9, description="Confidence level (90-99.9%)")
    tolerable_error_rate: float = Field(default=5.0, ge=0.1, le=50.0, description="Tolerable error rate (%)")
    expected_error_rate: float = Field(default=2.0, ge=0.0, le=50.0, description="Expected error rate (%)")
    method: str = Field(default="RANDOM", pattern="^(RANDOM|STRATIFIED|SYSTEMATIC|CLUSTER|JUDGMENTAL|AI_OPTIMIZED)$")


class SampleSizeResponse(BaseModel):
    """Sample size calculation response"""
    population_size: int
    confidence_level: float
    tolerable_error_rate: float
    expected_error_rate: float
    sampling_method: str
    calculated_sample_size: int
    adjusted_sample_size: int
    recommended_sample_size: int
    minimum_sample_size: int
    sampling_percentage: float
    statistical_metrics: dict
    calculated_at: str


class AIOptimizeSampleRequest(BaseModel):
    """AI optimize sample size request"""
    population_size: int = Field(..., ge=1)
    control_info: dict = Field(
        ...,
        description="Control information (control_name, criticality, etc.)",
        examples=[{
            "control_name": "Multi-Factor Authentication",
            "control_type": "AUTOMATED",
            "criticality": "HIGH"
        }]
    )
    historical_data: Optional[dict] = Field(
        None,
        description="Historical test results for this control"
    )


class AdaptiveSamplingRequest(BaseModel):
    """Adaptive sampling adjustment request"""
    initial_sample_size: int = Field(..., ge=1)
    errors_found: int = Field(..., ge=0)
    tests_completed: int = Field(..., ge=1)
    tolerable_error_rate: float = Field(default=5.0, ge=0.1, le=50.0)


class AdaptiveSamplingResponse(BaseModel):
    """Adaptive sampling adjustment response"""
    adjustment_needed: bool
    observation: Optional[str] = None
    adjustment_trigger: Optional[str] = None
    current_error_rate: Optional[float] = None
    tolerable_error_rate: float
    original_sample_size: Optional[int] = None
    additional_samples_needed: Optional[int] = None
    new_total_sample_size: Optional[int] = None
    rationale: Optional[str] = None
    note: Optional[str] = None
    requires_cpa_approval: Optional[bool] = None
    calculated_at: str


class SamplingResultsRequest(BaseModel):
    """Calculate sampling results request"""
    sample_size: int = Field(..., ge=1)
    errors_found: int = Field(..., ge=0)
    confidence_level: float = Field(default=95.0, ge=90.0, le=99.9)


class SamplingResultsResponse(BaseModel):
    """Sampling results response"""
    sample_size: int
    errors_found: int
    error_rate: float
    confidence_level: float
    upper_confidence_limit: float
    lower_confidence_limit: float
    confidence_interval: str
    precision: float
    conclusion: str
    calculated_at: str


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/calculate-sample-size", response_model=SampleSizeResponse)
async def calculate_sample_size(
    request: CalculateSampleSizeRequest
) -> SampleSizeResponse:
    """
    Calculate required sample size using statistical formulas

    **Statistical Methods:**
    - Attribute sampling formula
    - Finite population correction
    - Z-score based on confidence level
    - Precision calculation

    **Returns:**
    - Recommended sample size
    - Sampling percentage
    - Statistical metrics (precision, sampling risk)

    **Example:**
    ```json
    {
        "population_size": 1000,
        "confidence_level": 95.0,
        "tolerable_error_rate": 5.0,
        "expected_error_rate": 2.0,
        "method": "RANDOM"
    }
    ```
    """
    logger.info(f"Calculating sample size for population={request.population_size}")

    try:
        result = smart_sampling_service.calculate_sample_size(
            population_size=request.population_size,
            confidence_level=request.confidence_level,
            tolerable_error_rate=request.tolerable_error_rate,
            expected_error_rate=request.expected_error_rate,
            method=SamplingMethod(request.method)
        )

        return SampleSizeResponse(**result)

    except Exception as e:
        logger.error(f"Sample size calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sample size calculation failed: {str(e)}"
        )


@router.post("/ai-optimize", response_model=SampleSizeResponse)
async def ai_optimize_sample_size(
    request: AIOptimizeSampleRequest,
    db: AsyncSession = Depends(get_db)
) -> SampleSizeResponse:
    """
    Use AI to optimize sample size based on risk factors

    **AI Considers:**
    - Control criticality and risk level
    - Historical error rates
    - Technology complexity
    - Prior audit findings
    - Cost-benefit trade-off

    **Returns:**
    - AI-recommended sample size
    - AI rationale
    - Risk factors considered
    - Statistical calculation with AI-recommended parameters

    **Example:**
    ```json
    {
        "population_size": 500,
        "control_info": {
            "control_name": "MFA Enforcement",
            "control_type": "AUTOMATED",
            "criticality": "HIGH"
        },
        "historical_data": {
            "past_failure_rate": 0.15,
            "past_sample_sizes": [25, 30, 35]
        }
    }
    ```
    """
    logger.info(f"AI optimizing sample size for: {request.control_info.get('control_name')}")

    try:
        result = await smart_sampling_service.ai_optimize_sample_size(
            db=db,
            population_size=request.population_size,
            control_info=request.control_info,
            historical_data=request.historical_data
        )

        return SampleSizeResponse(**result)

    except Exception as e:
        logger.error(f"AI sample optimization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI optimization failed: {str(e)}"
        )


@router.post("/adaptive-adjustment", response_model=AdaptiveSamplingResponse)
async def adaptive_sampling_adjustment(
    request: AdaptiveSamplingRequest
) -> AdaptiveSamplingResponse:
    """
    Evaluate if sample size should be adjusted based on errors found

    **Adaptive Logic:**
    - If error rate > tolerable: Expand sample by 50%
    - If error rate < tolerable/2: Note for future reduction
    - If within tolerance: Continue as planned

    **Requires CPA approval for expansions**

    **Returns:**
    - Whether adjustment is needed
    - Adjustment trigger (HIGH_ERROR_RATE, LOW_ERROR_RATE, etc.)
    - Additional samples needed
    - Rationale for adjustment

    **Example:**
    ```json
    {
        "initial_sample_size": 50,
        "errors_found": 5,
        "tests_completed": 30,
        "tolerable_error_rate": 5.0
    }
    ```
    """
    logger.info(f"Evaluating adaptive sampling: {request.errors_found} errors in {request.tests_completed} tests")

    try:
        result = await smart_sampling_service.adaptive_sampling_adjustment(
            initial_sample_size=request.initial_sample_size,
            errors_found=request.errors_found,
            tests_completed=request.tests_completed,
            tolerable_error_rate=request.tolerable_error_rate
        )

        return AdaptiveSamplingResponse(**result)

    except Exception as e:
        logger.error(f"Adaptive sampling evaluation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Adaptive sampling failed: {str(e)}"
        )


@router.post("/calculate-results", response_model=SamplingResultsResponse)
async def calculate_sampling_results(
    request: SamplingResultsRequest
) -> SamplingResultsResponse:
    """
    Calculate statistical results after sampling completed

    **Calculates:**
    - Observed error rate
    - Upper/Lower confidence limits (Wilson score interval)
    - Precision
    - Pass/Fail conclusion

    **Conclusion Logic:**
    - 0 errors: PASS
    - Error rate < 5%: PASS
    - Error rate 5-10%: QUALIFIED (requires review)
    - Error rate > 10%: FAIL

    **Example:**
    ```json
    {
        "sample_size": 50,
        "errors_found": 2,
        "confidence_level": 95.0
    }
    ```
    """
    logger.info(f"Calculating sampling results: {request.errors_found} errors in {request.sample_size} tests")

    try:
        result = smart_sampling_service.calculate_sampling_results(
            sample_size=request.sample_size,
            errors_found=request.errors_found,
            confidence_level=request.confidence_level
        )

        return SamplingResultsResponse(**result)

    except Exception as e:
        logger.error(f"Results calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Results calculation failed: {str(e)}"
        )


@router.get("/methods")
async def list_sampling_methods() -> dict:
    """
    List available sampling methods

    **Returns:** Description of each sampling method
    """
    return {
        "RANDOM": {
            "name": "Simple Random Sampling",
            "description": "Pure random selection from population",
            "best_for": "Homogeneous populations"
        },
        "STRATIFIED": {
            "name": "Stratified Sampling",
            "description": "Proportional representation from strata",
            "best_for": "Heterogeneous populations with clear groups"
        },
        "SYSTEMATIC": {
            "name": "Systematic Sampling",
            "description": "Select every Nth item",
            "best_for": "Ordered populations"
        },
        "CLUSTER": {
            "name": "Cluster Sampling",
            "description": "Sample entire groups/clusters",
            "best_for": "Geographically dispersed populations"
        },
        "JUDGMENTAL": {
            "name": "Judgmental Sampling",
            "description": "Expert-driven selection",
            "best_for": "Complex audit scenarios"
        },
        "AI_OPTIMIZED": {
            "name": "AI-Optimized Sampling",
            "description": "AI recommends optimal method and size",
            "best_for": "All scenarios - uses risk-based intelligence"
        }
    }


@router.get("/confidence-levels")
async def get_confidence_levels() -> dict:
    """
    Get available confidence levels and Z-scores

    **Returns:** Confidence levels with corresponding Z-scores
    """
    return {
        "90%": {"confidence": 90.0, "z_score": 1.645},
        "95%": {"confidence": 95.0, "z_score": 1.96},
        "99%": {"confidence": 99.0, "z_score": 2.576}
    }


@router.get("/health")
async def health_check() -> dict:
    """
    Health check for smart sampling service

    **Returns:** Service status
    """
    return {
        "service": "smart_sampling",
        "status": "healthy",
        "ai_enabled": smart_sampling_service.enabled,
        "available_methods": len(SamplingMethod)
    }
