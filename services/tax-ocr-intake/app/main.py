"""
Tax OCR Intake Service

Document upload, classification, OCR, and field extraction for tax documents.

Capabilities:
- Document upload (PDF, TIFF, JPG, PNG)
- AI-powered classification (W-2, 1099 variants, K-1, etc.)
- OCR with confidence scoring
- Field extraction and mapping to Tax Data Schema
- Human-in-the-loop review queues for low-confidence fields
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID, uuid4
import logging

from .config import settings
from .database import get_db
from .models import TaxDocument, TaxDocumentPage, TaxExtractedField
from .schemas import (
    DocumentUploadResponse,
    DocumentResponse,
    IngestStatusResponse,
    ExtractionResponse,
    ReviewFlagResponse,
)

# Initialize FastAPI app
app = FastAPI(
    title="Tax OCR Intake Service",
    description="AI-powered document intake and OCR for tax preparation",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========================================
# Health Check
# ========================================


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tax-ocr-intake",
        "version": "1.0.0",
        "features": {
            "ocr_v1": settings.FEATURE_TAX_OCR_V1,
            "ai_classification": settings.FEATURE_AI_CLASSIFICATION,
        },
    }


# ========================================
# Document Upload
# ========================================


@app.post("/v1/returns/{tax_return_id}/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    tax_return_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a tax document (W-2, 1099, etc.)

    Returns a presigned URL for direct upload to object storage.
    """
    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed. "
            f"Allowed types: {settings.ALLOWED_FILE_TYPES}",
        )

    # TODO: Validate file size
    # TODO: Generate presigned URL for MinIO/S3 upload
    # TODO: Create TaxDocument record

    document_id = uuid4()

    logger.info(
        f"Document upload initiated",
        extra={
            "tax_return_id": str(tax_return_id),
            "document_id": str(document_id),
            "file_name": file.filename,
            "mime_type": file.content_type,
        },
    )

    return DocumentUploadResponse(
        document_id=document_id,
        upload_url=f"https://{settings.STORAGE_ENDPOINT}/{settings.STORAGE_BUCKET}/{document_id}",
        expires_at=None,  # TODO: Calculate expiration
    )


# ========================================
# Document Ingestion
# ========================================


@app.post("/v1/documents/{document_id}/ingest", response_model=IngestStatusResponse)
async def ingest_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger OCR and extraction for uploaded document

    Pipeline:
    1. Page splitting (for multi-page PDFs)
    2. Classification (document type detection)
    3. OCR + layout analysis
    4. Field extraction with confidence scoring
    5. Mapping to Tax Data Schema
    6. Review flag generation for low-confidence fields
    """
    # TODO: Load document from database
    # TODO: Queue background task for OCR pipeline
    # background_tasks.add_task(process_document, document_id)

    logger.info(f"Document ingestion started", extra={"document_id": str(document_id)})

    return IngestStatusResponse(
        ingest_id=document_id,
        status="processing",
        progress_pct=0.0,
        pages_processed=0,
        pages_total=1,
    )


@app.get("/v1/documents/{document_id}/ingest/status", response_model=IngestStatusResponse)
async def get_ingest_status(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get status of document ingestion"""
    # TODO: Load from database/Redis cache
    return IngestStatusResponse(
        ingest_id=document_id,
        status="completed",
        progress_pct=100.0,
        pages_processed=1,
        pages_total=1,
    )


# ========================================
# Document Retrieval
# ========================================


@app.get("/v1/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get document metadata"""
    # TODO: Load from database
    raise HTTPException(status_code=404, detail="Document not found")


@app.get("/v1/returns/{tax_return_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    tax_return_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all documents for a tax return"""
    # TODO: Query database
    return []


# ========================================
# Field Extraction
# ========================================


@app.get("/v1/documents/{document_id}/extraction", response_model=ExtractionResponse)
async def get_extraction(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get extracted fields from document

    Returns both raw extracted fields and structured data (W2Extraction, etc.)
    """
    # TODO: Load from database
    raise HTTPException(status_code=404, detail="Extraction not found")


# ========================================
# Classification
# ========================================


@app.post("/v1/documents/{document_id}/classify")
async def classify_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Manually trigger or re-trigger document classification

    Uses GPT-4 Vision to classify document type
    """
    # TODO: Call LLM service for classification
    # TODO: Update database
    return {"status": "classification_queued"}


# ========================================
# Review Queue
# ========================================


@app.get("/v1/returns/{tax_return_id}/review-flags", response_model=List[ReviewFlagResponse])
async def get_review_flags(
    tax_return_id: UUID,
    resolved: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get review flags for a tax return

    Filters:
    - resolved: True (resolved flags), False (unresolved), None (all)
    """
    # TODO: Query database
    return []


@app.post("/v1/review-flags/{flag_id}/resolve")
async def resolve_review_flag(
    flag_id: UUID,
    resolution_action: str,
    override_value: Optional[str] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Resolve a review flag

    Actions:
    - accept: Accept AI suggestion
    - override: Override with manual value
    - reject: Reject and leave blank
    - defer: Defer to later review
    """
    # TODO: Update flag in database
    # TODO: Update TDS if override provided
    # TODO: Publish event: tax.review_flag.resolved

    return {"status": "resolved"}


# ========================================
# Utility Endpoints
# ========================================


@app.get("/v1/supported-document-types")
async def get_supported_document_types():
    """Get list of supported document types"""
    return {
        "document_types": [
            {"code": "W-2", "name": "Wage and Tax Statement", "irs_form": "W-2"},
            {"code": "1099-INT", "name": "Interest Income", "irs_form": "1099-INT"},
            {"code": "1099-DIV", "name": "Dividend Income", "irs_form": "1099-DIV"},
            {"code": "1099-B", "name": "Brokerage/Stock Sales", "irs_form": "1099-B"},
            {"code": "1099-R", "name": "Pension Distributions", "irs_form": "1099-R"},
            {"code": "1099-MISC", "name": "Miscellaneous Income", "irs_form": "1099-MISC"},
            {"code": "1099-NEC", "name": "Nonemployee Compensation", "irs_form": "1099-NEC"},
            {"code": "K-1-1065", "name": "Partnership K-1", "irs_form": "Schedule K-1 (1065)"},
            {"code": "K-1-1120S", "name": "S-Corp K-1", "irs_form": "Schedule K-1 (1120-S)"},
            {"code": "1098", "name": "Mortgage Interest", "irs_form": "1098"},
            {"code": "SSA-1099", "name": "Social Security Benefits", "irs_form": "SSA-1099"},
        ]
    }


# ========================================
# Entry Point
# ========================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
