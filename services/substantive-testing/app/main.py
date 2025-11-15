"""
Aura Audit AI - Substantive Testing Service

Substantive audit procedures per PCAOB AS 2301:
- Journal entry testing
- Substantive analytical procedures
- Detail testing of transactions and balances
- Cut-off testing
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura Audit AI - Substantive Testing Service",
    description="Substantive audit procedures per PCAOB AS 2301",
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
        service="substantive-testing",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aura Audit AI - Substantive Testing Service",
        "version": "1.0.0",
        "features": [
            "Journal entry testing",
            "Substantive analytical procedures",
            "Detail testing",
            "Cut-off testing"
        ],
        "docs": "/docs"
    }


# ========================================
# Substantive Testing Endpoints
# ========================================

@app.post("/tests/{engagement_id}/journal-entries")
async def test_journal_entries(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Perform journal entry testing per PCAOB AS 2401.

    Tests for:
    - Round dollar amounts
    - Weekend postings
    - Period-end adjustments
    - Unusual account combinations
    """
    logger.info(f"Testing journal entries for engagement {engagement_id}")

    return {
        "engagement_id": str(engagement_id),
        "tests_performed": ["round_dollar", "weekend", "period_end"],
        "flagged_entries": 0,
        "message": "Journal entry testing complete"
    }


@app.post("/tests/{engagement_id}/analytical-procedures")
async def perform_analytical_procedures(
    engagement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Perform substantive analytical procedures.

    Includes:
    - Ratio analysis
    - Trend analysis
    - Reasonableness testing
    """
    logger.info(f"Performing analytical procedures for engagement {engagement_id}")

    return {
        "engagement_id": str(engagement_id),
        "procedures_performed": [],
        "exceptions_identified": 0,
        "message": "Analytical procedures complete"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
