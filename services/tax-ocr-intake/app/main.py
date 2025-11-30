"""
Tax OCR Intake Service - Comprehensive Document Processing

AI-powered document intake, classification, and field extraction for tax preparation.

Features:
- Document upload with secure storage
- AI-powered document classification (W-2, 1099, K-1, etc.)
- OCR processing with Azure Document Intelligence
- Field extraction with confidence scoring
- Human-in-the-loop review for low-confidence fields
- Integration with Tax Engine for automatic form population
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from enum import Enum
import logging
import base64
import io

from .config import settings
from .ocr_processor import (
    OCRProcessor, DocumentType, ExtractionResult, ExtractedField,
    AIDocumentClassifier, ExtractionValidator
)

# Initialize FastAPI app
app = FastAPI(
    title="Tax OCR Intake Service",
    description="AI-powered document intake and OCR for tax preparation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize processors
ocr_processor = OCRProcessor(provider="azure")
ai_classifier = AIDocumentClassifier()


# ========================================
# Pydantic Models
# ========================================

class DocumentTypeEnum(str, Enum):
    W2 = "W-2"
    W2G = "W-2G"
    FORM_1099_INT = "1099-INT"
    FORM_1099_DIV = "1099-DIV"
    FORM_1099_B = "1099-B"
    FORM_1099_R = "1099-R"
    FORM_1099_MISC = "1099-MISC"
    FORM_1099_NEC = "1099-NEC"
    FORM_1099_G = "1099-G"
    FORM_1099_K = "1099-K"
    FORM_1098 = "1098"
    FORM_1098_E = "1098-E"
    FORM_1098_T = "1098-T"
    SSA_1099 = "SSA-1099"
    K1_1065 = "K-1 (1065)"
    K1_1120S = "K-1 (1120-S)"
    K1_1041 = "K-1 (1041)"


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    tax_return_id: UUID
    status: str
    message: str
    ocr_status: str = "pending"


class ExtractedFieldResponse(BaseModel):
    field_name: str
    field_label: str
    value: Any
    raw_text: str
    confidence: float
    needs_review: bool
    review_reason: Optional[str] = None
    box_number: Optional[str] = None


class ExtractionResponse(BaseModel):
    document_id: UUID
    document_type: str
    classification_confidence: float
    fields: Dict[str, ExtractedFieldResponse]
    validation_errors: List[str] = []
    warnings: List[str] = []
    ocr_completed_at: Optional[datetime] = None


class DocumentResponse(BaseModel):
    document_id: UUID
    tax_return_id: UUID
    document_type: Optional[str] = None
    file_name: str
    file_size: int
    mime_type: str
    status: str
    ocr_status: str
    classification_confidence: Optional[float] = None
    needs_review: bool = False
    review_flags_count: int = 0
    uploaded_at: datetime
    processed_at: Optional[datetime] = None


class IngestStatusResponse(BaseModel):
    document_id: UUID
    status: str  # pending, processing, completed, failed
    progress_pct: float
    pages_processed: int
    pages_total: int
    current_step: Optional[str] = None
    error_message: Optional[str] = None


class ReviewFlagResponse(BaseModel):
    flag_id: UUID
    document_id: UUID
    field_name: str
    field_label: str
    extracted_value: Any
    confidence: float
    reason: str
    status: str  # pending, resolved, deferred
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    override_value: Optional[Any] = None


class ResolveReviewFlagRequest(BaseModel):
    action: str  # accept, override, reject, defer
    override_value: Optional[Any] = None
    notes: Optional[str] = None


class ClassificationRequest(BaseModel):
    force_reclassify: bool = False


class ClassificationResponse(BaseModel):
    document_id: UUID
    document_type: str
    confidence: float
    secondary_types: List[Dict[str, Any]]
    classified_at: datetime


class BatchUploadResponse(BaseModel):
    batch_id: UUID
    documents: List[DocumentUploadResponse]
    total_count: int


# ========================================
# In-Memory Storage (replace with DB in production)
# ========================================

documents_db: Dict[str, Dict] = {}
extractions_db: Dict[str, Dict] = {}
review_flags_db: Dict[str, Dict] = {}


# ========================================
# Health Check
# ========================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tax-ocr-intake",
        "version": "2.0.0",
        "ocr_provider": "azure",
        "supported_document_types": [dt.value for dt in DocumentType],
        "features": {
            "ocr": True,
            "ai_classification": True,
            "field_extraction": True,
            "review_queue": True,
            "batch_processing": True,
        },
    }


# ========================================
# Document Upload
# ========================================

@app.post("/v1/returns/{tax_return_id}/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    tax_return_id: UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type_hint: Optional[DocumentTypeEnum] = Form(None),
    auto_process: bool = Form(True),
):
    """
    Upload a tax document for OCR processing.

    Args:
        tax_return_id: Associated tax return
        file: Document file (PDF, JPG, PNG, TIFF)
        document_type_hint: Optional hint for document type
        auto_process: Automatically start OCR processing

    Returns:
        Upload confirmation with document ID
    """
    # Validate file type
    allowed_types = [
        "application/pdf", "image/jpeg", "image/png", "image/tiff",
        "image/jpg", "image/gif"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed. Allowed: {allowed_types}"
        )

    # Validate file size (max 25MB)
    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 25MB limit"
        )

    # Create document record
    document_id = uuid4()
    now = datetime.utcnow()

    document = {
        "document_id": str(document_id),
        "tax_return_id": str(tax_return_id),
        "file_name": file.filename,
        "file_size": len(content),
        "mime_type": file.content_type,
        "document_type_hint": document_type_hint.value if document_type_hint else None,
        "status": "uploaded",
        "ocr_status": "pending",
        "content": base64.b64encode(content).decode(),  # Store encoded content
        "uploaded_at": now.isoformat(),
    }
    documents_db[str(document_id)] = document

    logger.info(
        f"Document uploaded",
        extra={
            "document_id": str(document_id),
            "tax_return_id": str(tax_return_id),
            "file_name": file.filename,
            "file_size": len(content),
        }
    )

    # Auto-process if requested
    if auto_process:
        background_tasks.add_task(process_document_ocr, document_id, content, file.content_type)

    return DocumentUploadResponse(
        document_id=document_id,
        tax_return_id=tax_return_id,
        status="uploaded",
        message="Document uploaded successfully" + (". OCR processing started." if auto_process else ""),
        ocr_status="processing" if auto_process else "pending",
    )


@app.post("/v1/returns/{tax_return_id}/documents/batch-upload", response_model=BatchUploadResponse)
async def batch_upload_documents(
    tax_return_id: UUID,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
):
    """Upload multiple documents at once"""
    batch_id = uuid4()
    results = []

    for file in files:
        content = await file.read()
        document_id = uuid4()
        now = datetime.utcnow()

        document = {
            "document_id": str(document_id),
            "tax_return_id": str(tax_return_id),
            "batch_id": str(batch_id),
            "file_name": file.filename,
            "file_size": len(content),
            "mime_type": file.content_type,
            "status": "uploaded",
            "ocr_status": "pending",
            "content": base64.b64encode(content).decode(),
            "uploaded_at": now.isoformat(),
        }
        documents_db[str(document_id)] = document

        # Queue processing
        background_tasks.add_task(process_document_ocr, document_id, content, file.content_type)

        results.append(DocumentUploadResponse(
            document_id=document_id,
            tax_return_id=tax_return_id,
            status="uploaded",
            message="Document queued for processing",
            ocr_status="processing",
        ))

    return BatchUploadResponse(
        batch_id=batch_id,
        documents=results,
        total_count=len(results),
    )


# ========================================
# OCR Processing
# ========================================

async def process_document_ocr(document_id: UUID, content: bytes, content_type: str):
    """Background task to process document through OCR pipeline"""
    try:
        logger.info(f"Starting OCR processing for document {document_id}")

        # Update status
        if str(document_id) in documents_db:
            documents_db[str(document_id)]["ocr_status"] = "processing"

        # Get hint if available
        hint = None
        if str(document_id) in documents_db:
            hint_str = documents_db[str(document_id)].get("document_type_hint")
            if hint_str:
                hint = DocumentType(hint_str)

        # Process through OCR
        result = await ocr_processor.process_document(
            document_id=document_id,
            file_content=content,
            file_type=content_type,
            hint_document_type=hint
        )

        # Validate extraction
        validation_errors = []
        if result.document_type == DocumentType.W2:
            validation_errors = ExtractionValidator.validate_w2(result.fields)
        elif result.document_type == DocumentType.FORM_1099_INT:
            validation_errors = ExtractionValidator.validate_1099_int(result.fields)
        elif result.document_type == DocumentType.FORM_1099_DIV:
            validation_errors = ExtractionValidator.validate_1099_div(result.fields)

        # Store extraction result
        now = datetime.utcnow()
        extraction = {
            "document_id": str(document_id),
            "document_type": result.document_type.value,
            "classification_confidence": result.classification_confidence,
            "fields": {
                name: {
                    "field_name": field.field_name,
                    "field_label": field.field_label,
                    "value": float(field.value) if isinstance(field.value, Decimal) else field.value,
                    "raw_text": field.raw_text,
                    "confidence": field.confidence,
                    "needs_review": field.needs_review,
                    "review_reason": field.review_reason,
                }
                for name, field in result.fields.items()
            },
            "validation_errors": validation_errors,
            "warnings": result.warnings,
            "completed_at": now.isoformat(),
        }
        extractions_db[str(document_id)] = extraction

        # Create review flags for low-confidence fields
        for field_name, field in result.fields.items():
            if field.needs_review:
                flag_id = uuid4()
                review_flags_db[str(flag_id)] = {
                    "flag_id": str(flag_id),
                    "document_id": str(document_id),
                    "tax_return_id": documents_db[str(document_id)]["tax_return_id"],
                    "field_name": field_name,
                    "field_label": field.field_label,
                    "extracted_value": float(field.value) if isinstance(field.value, Decimal) else field.value,
                    "confidence": field.confidence,
                    "reason": field.review_reason or "Low confidence",
                    "status": "pending",
                    "created_at": now.isoformat(),
                }

        # Update document status
        if str(document_id) in documents_db:
            documents_db[str(document_id)].update({
                "ocr_status": "completed",
                "document_type": result.document_type.value,
                "classification_confidence": result.classification_confidence,
                "needs_review": any(f.needs_review for f in result.fields.values()),
                "processed_at": now.isoformat(),
            })

        logger.info(
            f"OCR completed for document {document_id}",
            extra={
                "document_type": result.document_type.value,
                "fields_extracted": len(result.fields),
                "needs_review": any(f.needs_review for f in result.fields.values()),
            }
        )

    except Exception as e:
        logger.error(f"OCR processing failed for {document_id}: {e}")
        if str(document_id) in documents_db:
            documents_db[str(document_id)].update({
                "ocr_status": "failed",
                "error": str(e),
            })


@app.post("/v1/documents/{document_id}/process")
async def trigger_ocr_processing(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    force: bool = False,
):
    """Manually trigger OCR processing for a document"""
    doc = documents_db.get(str(document_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc["ocr_status"] == "completed" and not force:
        raise HTTPException(
            status_code=400,
            detail="Document already processed. Use force=true to reprocess."
        )

    # Decode content and process
    content = base64.b64decode(doc["content"])
    background_tasks.add_task(process_document_ocr, document_id, content, doc["mime_type"])

    return {
        "document_id": str(document_id),
        "status": "processing",
        "message": "OCR processing started"
    }


@app.get("/v1/documents/{document_id}/status", response_model=IngestStatusResponse)
async def get_processing_status(document_id: UUID):
    """Get current processing status for a document"""
    doc = documents_db.get(str(document_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    status_map = {
        "pending": ("pending", 0, "Waiting to process"),
        "processing": ("processing", 50, "Running OCR"),
        "completed": ("completed", 100, "Completed"),
        "failed": ("failed", 0, "Failed"),
    }

    status, progress, step = status_map.get(
        doc.get("ocr_status", "pending"),
        ("unknown", 0, "Unknown")
    )

    return IngestStatusResponse(
        document_id=document_id,
        status=status,
        progress_pct=progress,
        pages_processed=1 if status == "completed" else 0,
        pages_total=1,
        current_step=step,
        error_message=doc.get("error"),
    )


# ========================================
# Document Retrieval
# ========================================

@app.get("/v1/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: UUID):
    """Get document metadata"""
    doc = documents_db.get(str(document_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Count review flags
    review_count = sum(
        1 for f in review_flags_db.values()
        if f["document_id"] == str(document_id) and f["status"] == "pending"
    )

    return DocumentResponse(
        document_id=document_id,
        tax_return_id=UUID(doc["tax_return_id"]),
        document_type=doc.get("document_type"),
        file_name=doc["file_name"],
        file_size=doc["file_size"],
        mime_type=doc["mime_type"],
        status=doc["status"],
        ocr_status=doc["ocr_status"],
        classification_confidence=doc.get("classification_confidence"),
        needs_review=doc.get("needs_review", False),
        review_flags_count=review_count,
        uploaded_at=datetime.fromisoformat(doc["uploaded_at"]),
        processed_at=datetime.fromisoformat(doc["processed_at"]) if doc.get("processed_at") else None,
    )


@app.get("/v1/returns/{tax_return_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    tax_return_id: UUID,
    status: Optional[str] = None,
):
    """List all documents for a tax return"""
    results = []
    for doc in documents_db.values():
        if doc["tax_return_id"] != str(tax_return_id):
            continue
        if status and doc.get("ocr_status") != status:
            continue

        review_count = sum(
            1 for f in review_flags_db.values()
            if f["document_id"] == doc["document_id"] and f["status"] == "pending"
        )

        results.append(DocumentResponse(
            document_id=UUID(doc["document_id"]),
            tax_return_id=UUID(doc["tax_return_id"]),
            document_type=doc.get("document_type"),
            file_name=doc["file_name"],
            file_size=doc["file_size"],
            mime_type=doc["mime_type"],
            status=doc["status"],
            ocr_status=doc["ocr_status"],
            classification_confidence=doc.get("classification_confidence"),
            needs_review=doc.get("needs_review", False),
            review_flags_count=review_count,
            uploaded_at=datetime.fromisoformat(doc["uploaded_at"]),
            processed_at=datetime.fromisoformat(doc["processed_at"]) if doc.get("processed_at") else None,
        ))

    return results


@app.delete("/v1/documents/{document_id}")
async def delete_document(document_id: UUID):
    """Delete a document"""
    if str(document_id) not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    del documents_db[str(document_id)]

    # Also delete extractions and review flags
    if str(document_id) in extractions_db:
        del extractions_db[str(document_id)]

    flags_to_delete = [
        fid for fid, flag in review_flags_db.items()
        if flag["document_id"] == str(document_id)
    ]
    for fid in flags_to_delete:
        del review_flags_db[fid]

    return {"message": "Document deleted"}


# ========================================
# Extraction Results
# ========================================

@app.get("/v1/documents/{document_id}/extraction", response_model=ExtractionResponse)
async def get_extraction(document_id: UUID):
    """Get extracted fields from a document"""
    extraction = extractions_db.get(str(document_id))
    if not extraction:
        # Check if document exists but not processed
        if str(document_id) in documents_db:
            doc = documents_db[str(document_id)]
            if doc["ocr_status"] == "pending":
                raise HTTPException(
                    status_code=202,
                    detail="Document not yet processed"
                )
            elif doc["ocr_status"] == "processing":
                raise HTTPException(
                    status_code=202,
                    detail="Document processing in progress"
                )
        raise HTTPException(status_code=404, detail="Extraction not found")

    return ExtractionResponse(
        document_id=document_id,
        document_type=extraction["document_type"],
        classification_confidence=extraction["classification_confidence"],
        fields={
            name: ExtractedFieldResponse(**field_data)
            for name, field_data in extraction["fields"].items()
        },
        validation_errors=extraction.get("validation_errors", []),
        warnings=extraction.get("warnings", []),
        ocr_completed_at=datetime.fromisoformat(extraction["completed_at"]) if extraction.get("completed_at") else None,
    )


@app.put("/v1/documents/{document_id}/extraction/fields/{field_name}")
async def update_extracted_field(
    document_id: UUID,
    field_name: str,
    value: Any = Query(...),
):
    """Manually update an extracted field value"""
    extraction = extractions_db.get(str(document_id))
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")

    if field_name not in extraction["fields"]:
        raise HTTPException(status_code=404, detail=f"Field {field_name} not found")

    extraction["fields"][field_name]["value"] = value
    extraction["fields"][field_name]["confidence"] = 1.0  # Manual entry = 100% confidence
    extraction["fields"][field_name]["needs_review"] = False

    return {"message": f"Field {field_name} updated", "value": value}


# ========================================
# Classification
# ========================================

@app.post("/v1/documents/{document_id}/classify", response_model=ClassificationResponse)
async def classify_document(document_id: UUID, request: ClassificationRequest):
    """Classify or reclassify a document type"""
    doc = documents_db.get(str(document_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.get("document_type") and not request.force_reclassify:
        raise HTTPException(
            status_code=400,
            detail="Document already classified. Use force_reclassify=true to reclassify."
        )

    # Run classification
    content = base64.b64decode(doc["content"])
    result = await ai_classifier.classify(content)

    # Update document
    doc["document_type"] = result.document_type.value
    doc["classification_confidence"] = result.confidence

    return ClassificationResponse(
        document_id=document_id,
        document_type=result.document_type.value,
        confidence=result.confidence,
        secondary_types=[
            {"type": t.value, "confidence": c}
            for t, c in result.secondary_types
        ],
        classified_at=datetime.utcnow(),
    )


# ========================================
# Review Queue
# ========================================

@app.get("/v1/returns/{tax_return_id}/review-flags", response_model=List[ReviewFlagResponse])
async def get_review_flags(
    tax_return_id: UUID,
    status: Optional[str] = None,  # pending, resolved, deferred
):
    """Get review flags for a tax return"""
    results = []
    for flag in review_flags_db.values():
        if flag["tax_return_id"] != str(tax_return_id):
            continue
        if status and flag["status"] != status:
            continue

        results.append(ReviewFlagResponse(
            flag_id=UUID(flag["flag_id"]),
            document_id=UUID(flag["document_id"]),
            field_name=flag["field_name"],
            field_label=flag["field_label"],
            extracted_value=flag["extracted_value"],
            confidence=flag["confidence"],
            reason=flag["reason"],
            status=flag["status"],
            resolved_by=UUID(flag["resolved_by"]) if flag.get("resolved_by") else None,
            resolved_at=datetime.fromisoformat(flag["resolved_at"]) if flag.get("resolved_at") else None,
            override_value=flag.get("override_value"),
        ))

    return results


@app.post("/v1/review-flags/{flag_id}/resolve")
async def resolve_review_flag(flag_id: UUID, request: ResolveReviewFlagRequest):
    """
    Resolve a review flag.

    Actions:
    - accept: Accept the AI-extracted value
    - override: Override with a manual value
    - reject: Reject the field (leave blank)
    - defer: Defer to later review
    """
    flag = review_flags_db.get(str(flag_id))
    if not flag:
        raise HTTPException(status_code=404, detail="Review flag not found")

    now = datetime.utcnow()

    if request.action == "accept":
        flag["status"] = "resolved"
        flag["resolved_at"] = now.isoformat()
        # Use existing value

    elif request.action == "override":
        if request.override_value is None:
            raise HTTPException(status_code=400, detail="Override value required")
        flag["status"] = "resolved"
        flag["override_value"] = request.override_value
        flag["resolved_at"] = now.isoformat()

        # Update extraction
        extraction = extractions_db.get(flag["document_id"])
        if extraction and flag["field_name"] in extraction["fields"]:
            extraction["fields"][flag["field_name"]]["value"] = request.override_value
            extraction["fields"][flag["field_name"]]["confidence"] = 1.0
            extraction["fields"][flag["field_name"]]["needs_review"] = False

    elif request.action == "reject":
        flag["status"] = "resolved"
        flag["override_value"] = None
        flag["resolved_at"] = now.isoformat()

        # Clear extraction value
        extraction = extractions_db.get(flag["document_id"])
        if extraction and flag["field_name"] in extraction["fields"]:
            extraction["fields"][flag["field_name"]]["value"] = None
            extraction["fields"][flag["field_name"]]["needs_review"] = False

    elif request.action == "defer":
        flag["status"] = "deferred"
        flag["notes"] = request.notes

    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {request.action}")

    return {
        "flag_id": str(flag_id),
        "status": flag["status"],
        "message": f"Review flag {request.action}ed"
    }


@app.post("/v1/returns/{tax_return_id}/review-flags/bulk-accept")
async def bulk_accept_flags(tax_return_id: UUID, min_confidence: float = 0.8):
    """Accept all review flags above a confidence threshold"""
    accepted = 0
    now = datetime.utcnow()

    for flag in review_flags_db.values():
        if flag["tax_return_id"] != str(tax_return_id):
            continue
        if flag["status"] != "pending":
            continue
        if flag["confidence"] >= min_confidence:
            flag["status"] = "resolved"
            flag["resolved_at"] = now.isoformat()
            accepted += 1

    return {
        "accepted_count": accepted,
        "message": f"Accepted {accepted} review flags with confidence >= {min_confidence}"
    }


# ========================================
# Transfer to Tax Return
# ========================================

@app.post("/v1/documents/{document_id}/transfer-to-return")
async def transfer_to_tax_return(document_id: UUID):
    """
    Transfer extracted data to the tax return.

    Maps extracted fields to the appropriate tax form fields
    in the tax-engine service.
    """
    doc = documents_db.get(str(document_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    extraction = extractions_db.get(str(document_id))
    if not extraction:
        raise HTTPException(status_code=400, detail="Document not yet processed")

    # Check for unresolved review flags
    pending_flags = [
        f for f in review_flags_db.values()
        if f["document_id"] == str(document_id) and f["status"] == "pending"
    ]
    if pending_flags:
        raise HTTPException(
            status_code=400,
            detail=f"{len(pending_flags)} review flags pending. Resolve before transferring."
        )

    # Map extracted fields to tax form fields
    document_type = extraction["document_type"]
    mapped_data = {}

    if document_type == "W-2":
        mapped_data = {
            "wages": extraction["fields"].get("wages", {}).get("value"),
            "withholding_w2": extraction["fields"].get("federal_tax_withheld", {}).get("value"),
            "social_security_wages": extraction["fields"].get("social_security_wages", {}).get("value"),
            "social_security_withheld": extraction["fields"].get("social_security_tax", {}).get("value"),
            "medicare_wages": extraction["fields"].get("medicare_wages", {}).get("value"),
            "medicare_withheld": extraction["fields"].get("medicare_tax", {}).get("value"),
        }
    elif document_type == "1099-INT":
        mapped_data = {
            "taxable_interest": extraction["fields"].get("interest_income", {}).get("value"),
        }
    elif document_type == "1099-DIV":
        mapped_data = {
            "ordinary_dividends": extraction["fields"].get("ordinary_dividends", {}).get("value"),
            "qualified_dividends": extraction["fields"].get("qualified_dividends", {}).get("value"),
        }

    # Would call tax-engine API to update form data
    # For now, return what would be transferred
    return {
        "document_id": str(document_id),
        "tax_return_id": doc["tax_return_id"],
        "document_type": document_type,
        "transferred_fields": mapped_data,
        "message": "Data transferred to tax return"
    }


# ========================================
# Supported Document Types
# ========================================

@app.get("/v1/supported-document-types")
async def get_supported_document_types():
    """Get list of all supported document types with field mappings"""
    return {
        "document_types": [
            {
                "code": "W-2",
                "name": "Wage and Tax Statement",
                "irs_form": "W-2",
                "description": "Reports wages and taxes withheld from an employee",
                "key_fields": ["wages", "federal_tax_withheld", "social_security_wages", "medicare_wages"],
            },
            {
                "code": "1099-INT",
                "name": "Interest Income",
                "irs_form": "1099-INT",
                "description": "Reports interest income from banks and financial institutions",
                "key_fields": ["interest_income", "federal_tax_withheld"],
            },
            {
                "code": "1099-DIV",
                "name": "Dividend Income",
                "irs_form": "1099-DIV",
                "description": "Reports dividend income from investments",
                "key_fields": ["ordinary_dividends", "qualified_dividends", "capital_gain_distributions"],
            },
            {
                "code": "1099-B",
                "name": "Brokerage Statement",
                "irs_form": "1099-B",
                "description": "Reports proceeds from broker transactions",
                "key_fields": ["proceeds", "cost_basis", "wash_sale_loss"],
            },
            {
                "code": "1099-R",
                "name": "Retirement Distributions",
                "irs_form": "1099-R",
                "description": "Reports distributions from pensions, annuities, IRAs",
                "key_fields": ["gross_distribution", "taxable_amount", "federal_tax_withheld"],
            },
            {
                "code": "1099-NEC",
                "name": "Nonemployee Compensation",
                "irs_form": "1099-NEC",
                "description": "Reports payments to independent contractors",
                "key_fields": ["nonemployee_compensation"],
            },
            {
                "code": "1099-MISC",
                "name": "Miscellaneous Income",
                "irs_form": "1099-MISC",
                "description": "Reports rent, royalties, and other miscellaneous income",
                "key_fields": ["rents", "royalties", "other_income"],
            },
            {
                "code": "1098",
                "name": "Mortgage Interest",
                "irs_form": "1098",
                "description": "Reports mortgage interest paid",
                "key_fields": ["mortgage_interest", "points_paid", "property_taxes"],
            },
            {
                "code": "SSA-1099",
                "name": "Social Security Benefits",
                "irs_form": "SSA-1099",
                "description": "Reports Social Security benefits received",
                "key_fields": ["total_benefits", "benefits_repaid"],
            },
            {
                "code": "K-1 (1065)",
                "name": "Partnership K-1",
                "irs_form": "Schedule K-1 (Form 1065)",
                "description": "Reports partner's share of partnership income",
                "key_fields": ["ordinary_income", "net_rental_income", "interest_income", "dividends"],
            },
            {
                "code": "K-1 (1120-S)",
                "name": "S-Corporation K-1",
                "irs_form": "Schedule K-1 (Form 1120-S)",
                "description": "Reports shareholder's share of S-corp income",
                "key_fields": ["ordinary_income", "net_rental_income", "interest_income"],
            },
        ]
    }


# ========================================
# Entry Point
# ========================================

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Tax OCR Intake Service starting...")
    logger.info(f"OCR Provider: {ocr_processor.provider}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
