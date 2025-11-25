"""
Aura Audit AI - Disclosures Service
AI-powered disclosure drafting, note generation, and financial statement disclosures
"""
import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional
from uuid import UUID

import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import engine, get_db, init_db
from .edgar import EdgarClient
from .models import Filing, Fact
from .schemas import (
    FilingInfo,
    EdgarFactsResponse,
    FactItem,
    PBCUploadResponse,
    HealthResponse
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    logger.info("Starting Ingestion Service")
    await init_db()
    yield
    logger.info("Shutting down Ingestion Service")
    await engine.dispose()


app = FastAPI(
    title="Aura Audit AI - Ingestion Service",
    description="EDGAR/XBRL ingestion, PBC uploads, and data source connectors",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize EDGAR client
edgar_client = EdgarClient(
    base_url=settings.EDGAR_BASE_URL,
    user_agent=settings.EDGAR_USER_AGENT
)


# ========================================
# Health & Status
# ========================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="ingestion",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aura Audit AI - Ingestion Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ========================================
# EDGAR / XBRL Ingestion
# ========================================

@app.get("/edgar/company-facts", response_model=EdgarFactsResponse)
async def get_edgar_company_facts(
    cik: Optional[str] = None,
    ticker: Optional[str] = None,
    form: Optional[str] = None,
    filing_date: Optional[date] = None,
    concepts: Optional[list[str]] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch normalized facts from EDGAR company-facts endpoint

    Args:
        cik: Company CIK (Central Index Key)
        ticker: Company ticker symbol
        form: Filing form type (10-K, 10-Q, etc.)
        filing_date: Specific filing date
        concepts: List of XBRL concepts to filter (e.g., ['us-gaap:Assets', 'us-gaap:Revenues'])

    Returns:
        EdgarFactsResponse with filing metadata and normalized facts
    """
    if not cik and not ticker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'cik' or 'ticker' must be provided"
        )

    try:
        # Fetch from EDGAR
        if cik:
            company_data = await edgar_client.get_company_facts(cik)
        else:
            # Resolve ticker to CIK first (you'd need a ticker->CIK mapping)
            company_data = await edgar_client.get_company_facts_by_ticker(ticker)

        # Normalize facts
        facts = edgar_client.normalize_company_facts(
            company_data,
            concepts=concepts,
            form=form,
            filing_date=filing_date
        )

        # Store in database
        filing = Filing(
            cik=company_data["entityName"]["cik"],
            company_name=company_data["entityName"]["name"],
            ticker=ticker,
            form=form or "10-K",
            filing_date=filing_date or date.today(),
            accession_number=f"CIK{company_data['entityName']['cik']}-{filing_date}",
            source_uri=f"{settings.EDGAR_BASE_URL}/companyfacts/CIK{int(company_data['entityName']['cik']):010d}.json",
        )

        db.add(filing)
        await db.flush()

        # Store facts
        for fact_data in facts:
            fact = Fact(
                filing_id=filing.id,
                concept=fact_data["concept"],
                taxonomy=fact_data.get("taxonomy", "us-gaap"),
                value=fact_data.get("value"),
                unit=fact_data.get("unit"),
                start_date=fact_data.get("start_date"),
                end_date=fact_data.get("end_date"),
                instant_date=fact_data.get("instant_date"),
                metadata=fact_data.get("metadata", {})
            )
            db.add(fact)

        await db.commit()

        return EdgarFactsResponse(
            filing=FilingInfo(
                cik=filing.cik,
                ticker=ticker,
                company_name=filing.company_name,
                form=filing.form,
                filing_date=filing.filing_date,
                source_uri=filing.source_uri
            ),
            facts=[FactItem(**f) for f in facts]
        )

    except httpx.HTTPError as e:
        logger.error(f"EDGAR API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch from EDGAR: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing EDGAR data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@app.get("/edgar/filings/{accession_number}")
async def get_filing_by_accession(
    accession_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get filing details by accession number"""
    # Implementation would query database and return filing + facts
    pass


# ========================================
# PBC Document Upload
# ========================================

@app.post("/pbc/upload", response_model=PBCUploadResponse)
async def upload_pbc_document(
    engagement_id: UUID,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a PBC (Provided By Client) document

    Args:
        engagement_id: Target engagement UUID
        file: Document file (PDF, Excel, CSV, etc.)
        description: Optional description

    Returns:
        Upload confirmation with S3 URI and metadata
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/csv",
            "image/png",
            "image/jpeg"
        ]

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed"
            )

        # Read file content
        content = await file.read()

        # Upload to S3/MinIO
        s3_key = f"pbc/{engagement_id}/{file.filename}"
        # Implementation: upload to S3 using boto3
        # s3_uri = await upload_to_s3(content, s3_key)

        # For now, mock response
        s3_uri = f"s3://{settings.S3_BUCKET}/{s3_key}"

        return PBCUploadResponse(
            engagement_id=engagement_id,
            filename=file.filename,
            s3_uri=s3_uri,
            size_bytes=len(content),
            content_type=file.content_type,
            description=description
        )

    except Exception as e:
        logger.error(f"Error uploading PBC document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


# ========================================
# Trial Balance Import
# ========================================

@app.post("/trial-balance/import")
async def import_trial_balance(
    engagement_id: UUID,
    file: UploadFile = File(...),
    period_end_date: date = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Import trial balance from Excel/CSV file

    Args:
        engagement_id: Target engagement UUID
        file: Trial balance file (Excel or CSV)
        period_end_date: Period ending date

    Returns:
        Import summary with line counts and validation results
    """
    try:
        import pandas as pd
        import io

        content = await file.read()

        # Parse file based on type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be CSV or Excel format"
            )

        # Validate required columns
        required_columns = ['account_code', 'account_name']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {required_columns}"
            )

        # Process trial balance lines
        # Implementation would create trial_balance record and lines

        return {
            "engagement_id": str(engagement_id),
            "period_end_date": period_end_date,
            "lines_imported": len(df),
            "total_debits": float(df.get('debit_amount', pd.Series([0])).sum()),
            "total_credits": float(df.get('credit_amount', pd.Series([0])).sum()),
            "validation_errors": []
        }

    except Exception as e:
        logger.error(f"Error importing trial balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
