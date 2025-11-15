"""
Aura Audit AI - Statistical Sampling Service

Implements audit sampling methods per PCAOB AS 2315 and AICPA AU-C 530:
- Monetary Unit Sampling (MUS/PPS)
- Classical Variables Sampling
- Attribute Sampling for control testing
- Sample size determination
- Sample evaluation and error projection
"""
import logging
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db
from .sampling_service import (
    MonetaryUnitSampling,
    ClassicalVariablesSampling,
    AttributeSampling,
    SamplingService,
    SamplingMethod,
    RiskLevel
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura Audit AI - Statistical Sampling Service",
    description="Audit sampling per PCAOB AS 2315 and AICPA AU-C 530",
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
# Schemas
# ========================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


class MUSSampleSizeRequest(BaseModel):
    """Request for MUS sample size calculation"""
    population_value: Decimal
    tolerable_misstatement: Decimal
    expected_misstatement: Decimal = Decimal("0")
    risk_level: str = "moderate"


class MUSSampleSizeResponse(BaseModel):
    """MUS sample size response"""
    sample_size: int
    sampling_interval: Decimal
    population_value: Decimal
    tolerable_misstatement: Decimal
    risk_level: str
    reliability_factor: float


class AttributeSampleRequest(BaseModel):
    """Request for attribute sample size"""
    population_size: int
    expected_deviation_rate: float
    tolerable_deviation_rate: float
    risk_level: str = "moderate"


class AttributeSampleResponse(BaseModel):
    """Attribute sample size response"""
    sample_size: int
    expected_deviations: int
    tolerable_deviations: int
    confidence_level: float


class SampleSelectionRequest(BaseModel):
    """Request for sample selection"""
    population_items: List[Dict]
    sample_size: int
    method: str = "mus"


class SampleEvaluationRequest(BaseModel):
    """Request for sample evaluation"""
    population_value: Decimal
    sample_items: List[Dict]
    tolerable_misstatement: Decimal
    risk_level: str = "moderate"


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
        service="sampling",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aura Audit AI - Statistical Sampling Service",
        "version": "1.0.0",
        "features": [
            "Monetary Unit Sampling (MUS/PPS)",
            "Classical Variables Sampling",
            "Attribute Sampling for controls",
            "Sample size determination",
            "Error projection and evaluation"
        ],
        "docs": "/docs"
    }


# ========================================
# Monetary Unit Sampling (MUS)
# ========================================

@app.post("/mus/sample-size", response_model=MUSSampleSizeResponse)
async def calculate_mus_sample_size(
    request: MUSSampleSizeRequest,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Calculate MUS sample size per PCAOB AS 2315.

    Monetary Unit Sampling automatically stratifies population
    and is efficient when low error rates are expected.
    """
    try:
        risk_level = RiskLevel[request.risk_level.upper()]

        result = MonetaryUnitSampling.calculate_sample_size(
            population_value=request.population_value,
            tolerable_misstatement=request.tolerable_misstatement,
            expected_misstatement=request.expected_misstatement,
            risk_level=risk_level
        )

        logger.info(
            f"MUS sample size calculated: {result['sample_size']} items "
            f"for population ${request.population_value:,.0f}"
        )

        return MUSSampleSizeResponse(
            sample_size=result["sample_size"],
            sampling_interval=result["sampling_interval"],
            population_value=request.population_value,
            tolerable_misstatement=request.tolerable_misstatement,
            risk_level=request.risk_level,
            reliability_factor=float(result["reliability_factor"])
        )

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid risk level: {request.risk_level}. Use: low, moderate, high"
        )
    except Exception as e:
        logger.error(f"Error calculating MUS sample size: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate sample size: {str(e)}"
        )


@app.post("/mus/select-sample")
async def select_mus_sample(
    population_items: List[Dict],
    sampling_interval: Decimal,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Select sample items using MUS systematic selection.

    Each monetary unit has equal probability of selection,
    automatically giving larger items higher selection probability.
    """
    try:
        selected = MonetaryUnitSampling.select_sample(
            population=population_items,
            sampling_interval=sampling_interval
        )

        logger.info(f"Selected {len(selected)} items using MUS")

        return {
            "method": "mus",
            "selected_items": len(selected),
            "sample": selected
        }

    except Exception as e:
        logger.error(f"Error selecting MUS sample: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to select sample: {str(e)}"
        )


@app.post("/mus/evaluate")
async def evaluate_mus_sample(
    request: SampleEvaluationRequest,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Evaluate MUS sample and project errors to population.

    Calculates:
    - Most likely misstatement
    - Upper misstatement limit
    - Conclusion (accept/reject population)
    """
    try:
        risk_level = RiskLevel[request.risk_level.upper()]

        result = MonetaryUnitSampling.evaluate_sample(
            population_value=request.population_value,
            sample_items=request.sample_items,
            tolerable_misstatement=request.tolerable_misstatement,
            risk_level=risk_level
        )

        logger.info(
            f"MUS evaluation: Most likely error ${result['most_likely_misstatement']:,.0f}, "
            f"Upper limit ${result['upper_misstatement_limit']:,.0f}"
        )

        return result

    except Exception as e:
        logger.error(f"Error evaluating MUS sample: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate sample: {str(e)}"
        )


# ========================================
# Attribute Sampling
# ========================================

@app.post("/attribute/sample-size", response_model=AttributeSampleResponse)
async def calculate_attribute_sample_size(
    request: AttributeSampleRequest,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Calculate attribute sample size for control testing.

    Used to test operating effectiveness of internal controls.
    """
    try:
        risk_level = RiskLevel[request.risk_level.upper()]

        result = AttributeSampling.calculate_sample_size(
            population_size=request.population_size,
            expected_deviation_rate=request.expected_deviation_rate,
            tolerable_deviation_rate=request.tolerable_deviation_rate,
            risk_level=risk_level
        )

        logger.info(
            f"Attribute sample size: {result['sample_size']} from "
            f"population of {request.population_size}"
        )

        return AttributeSampleResponse(
            sample_size=result["sample_size"],
            expected_deviations=result["expected_deviations"],
            tolerable_deviations=result["tolerable_deviations"],
            confidence_level=result["confidence_level"]
        )

    except Exception as e:
        logger.error(f"Error calculating attribute sample size: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate sample size: {str(e)}"
        )


@app.post("/attribute/evaluate")
async def evaluate_attribute_sample(
    population_size: int,
    sample_size: int,
    deviations_found: int,
    tolerable_deviation_rate: float,
    risk_level: str = "moderate",
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Evaluate attribute sample results.

    Determines if control can be relied upon based on
    deviation rate and upper deviation limit.
    """
    try:
        risk_level_enum = RiskLevel[risk_level.upper()]

        result = AttributeSampling.evaluate_sample(
            sample_size=sample_size,
            deviations_found=deviations_found,
            tolerable_deviation_rate=tolerable_deviation_rate,
            risk_level=risk_level_enum
        )

        logger.info(
            f"Attribute evaluation: {deviations_found} deviations found, "
            f"conclusion: {result['conclusion']}"
        )

        return result

    except Exception as e:
        logger.error(f"Error evaluating attribute sample: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate sample: {str(e)}"
        )


# ========================================
# Classical Variables Sampling
# ========================================

@app.post("/classical/sample-size")
async def calculate_classical_sample_size(
    population_size: int,
    population_std_dev: Decimal,
    tolerable_misstatement: Decimal,
    risk_level: str = "moderate",
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Calculate sample size for classical variables sampling.

    Methods: mean-per-unit, ratio estimation, difference estimation
    """
    try:
        risk_level_enum = RiskLevel[risk_level.upper()]

        result = ClassicalVariablesSampling.calculate_sample_size(
            population_size=population_size,
            population_std_dev=population_std_dev,
            tolerable_misstatement=tolerable_misstatement,
            risk_level=risk_level_enum
        )

        logger.info(
            f"Classical variables sample size: {result['sample_size']} "
            f"from population of {population_size}"
        )

        return result

    except Exception as e:
        logger.error(f"Error calculating classical sample size: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate sample size: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
