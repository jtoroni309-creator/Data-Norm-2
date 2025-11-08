"""
Pydantic schemas for Tax OCR Intake Service
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
from decimal import Decimal


# ========================================
# Document Classification
# ========================================


class DocumentClassification(BaseModel):
    """Result of document classification"""

    document_type: str = Field(..., description="Classified document type (W-2, 1099-INT, etc.)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    tax_year: Optional[int] = Field(None, description="Tax year detected in document")


# ========================================
# Document Upload
# ========================================


class DocumentUploadRequest(BaseModel):
    """Request to upload a tax document"""

    tax_return_id: UUID = Field(..., description="Tax return to attach document to")
    file_name: str = Field(..., description="Original file name")
    mime_type: str = Field(..., description="MIME type")


class DocumentUploadResponse(BaseModel):
    """Response after document upload"""

    document_id: UUID
    upload_url: str = Field(..., description="Presigned URL for file upload")
    expires_at: datetime


class IngestRequest(BaseModel):
    """Request to ingest and process a document"""

    tax_return_id: UUID
    document_id: UUID


class IngestStatusResponse(BaseModel):
    """Status of document ingestion"""

    ingest_id: UUID
    status: str = Field(..., description="pending, processing, completed, failed")
    progress_pct: float = Field(..., ge=0.0, le=100.0)
    pages_processed: int
    pages_total: int
    error_message: Optional[str] = None


# ========================================
# Field Extraction
# ========================================


class BoundingBox(BaseModel):
    """Bounding box coordinates for OCR field"""

    x: int
    y: int
    width: int
    height: int


class ExtractedField(BaseModel):
    """Single extracted field from OCR"""

    field_name: str
    field_label: Optional[str] = None
    field_value: str
    field_value_normalized: Optional[str] = None
    field_type: str = Field(..., description="currency, ssn, ein, text, date")
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: Optional[BoundingBox] = None

    class Config:
        from_attributes = True


class W2Extraction(BaseModel):
    """Structured W-2 extraction"""

    ein: Optional[str] = Field(None, description="Employer EIN (Box b)")
    employer_name: Optional[str] = Field(None, description="Employer name (Box c)")
    wages: Optional[Decimal] = Field(None, description="Box 1: Wages, tips, other compensation")
    federal_withholding: Optional[Decimal] = Field(None, description="Box 2: Federal income tax withheld")
    social_security_wages: Optional[Decimal] = Field(None, description="Box 3: Social security wages")
    social_security_withholding: Optional[Decimal] = Field(
        None, description="Box 4: Social security tax withheld"
    )
    medicare_wages: Optional[Decimal] = Field(None, description="Box 5: Medicare wages and tips")
    medicare_withholding: Optional[Decimal] = Field(
        None, description="Box 6: Medicare tax withheld"
    )
    state: Optional[str] = Field(None, description="Box 15: State")
    state_wages: Optional[Decimal] = Field(None, description="Box 16: State wages, tips, etc.")
    state_withholding: Optional[Decimal] = Field(
        None, description="Box 17: State income tax withheld"
    )

    # Confidence per field
    confidence_scores: Dict[str, float] = Field(
        default_factory=dict, description="Confidence score per field"
    )


class Form1099IntExtraction(BaseModel):
    """Structured 1099-INT extraction"""

    payer_ein: Optional[str] = Field(None, description="Payer's EIN")
    payer_name: Optional[str] = Field(None, description="Payer's name")
    interest_income: Optional[Decimal] = Field(None, description="Box 1: Interest income")
    early_withdrawal_penalty: Optional[Decimal] = Field(
        None, description="Box 2: Early withdrawal penalty"
    )
    interest_on_us_savings_bonds: Optional[Decimal] = Field(
        None, description="Box 3: Interest on U.S. Savings Bonds"
    )
    federal_withholding: Optional[Decimal] = Field(
        None, description="Box 4: Federal income tax withheld"
    )
    investment_expenses: Optional[Decimal] = Field(None, description="Box 5: Investment expenses")
    foreign_tax_paid: Optional[Decimal] = Field(None, description="Box 6: Foreign tax paid")

    confidence_scores: Dict[str, float] = Field(default_factory=dict)


class Form1099BExtraction(BaseModel):
    """Structured 1099-B extraction (brokerage)"""

    payer_ein: Optional[str] = Field(None, description="Payer's EIN")
    payer_name: Optional[str] = Field(None, description="Payer's name (broker)")
    total_proceeds: Optional[Decimal] = Field(None, description="Total proceeds")
    total_basis: Optional[Decimal] = Field(None, description="Total cost basis")
    short_term_gain_loss: Optional[Decimal] = Field(None, description="Short-term gain/loss")
    long_term_gain_loss: Optional[Decimal] = Field(None, description="Long-term gain/loss")
    wash_sale_adjustment: Optional[Decimal] = Field(None, description="Wash sale adjustment")
    federal_withholding: Optional[Decimal] = Field(None, description="Federal withholding")

    # Detailed lot information (if available)
    lots: List[Dict[str, Any]] = Field(default_factory=list, description="Individual lot details")

    confidence_scores: Dict[str, float] = Field(default_factory=dict)


# ========================================
# Document Responses
# ========================================


class DocumentResponse(BaseModel):
    """Tax document details"""

    id: UUID
    tax_return_id: UUID
    document_type: str
    classification_confidence: Optional[float] = None
    tax_year: Optional[int] = None
    file_url: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    page_count: int
    ocr_completed: bool
    ocr_completed_at: Optional[datetime] = None
    uploaded_by: UUID
    uploaded_at: datetime

    class Config:
        from_attributes = True


class PageResponse(BaseModel):
    """Document page details"""

    id: UUID
    tax_document_id: UUID
    page_number: int
    image_url: Optional[str] = None
    ocr_confidence: Optional[float] = None
    page_type: Optional[str] = None

    class Config:
        from_attributes = True


class ExtractionResponse(BaseModel):
    """OCR extraction result for a document"""

    document_id: UUID
    document_type: str
    extracted_fields: List[ExtractedField]
    structured_data: Optional[Dict[str, Any]] = Field(
        None, description="Type-specific structured extraction (W2Extraction, etc.)"
    )
    average_confidence: float
    low_confidence_fields: List[str] = Field(
        default_factory=list, description="Field names with confidence < 0.98"
    )


# ========================================
# Review Queue
# ========================================


class ReviewFlagResponse(BaseModel):
    """Review flag for human attention"""

    id: UUID
    tax_return_id: UUID
    code: str
    severity: str
    message: str
    field_path: Optional[str] = None
    current_value: Optional[str] = None
    source_document_id: Optional[UUID] = None
    source_document_snippet_url: Optional[str] = None
    ai_suggestion: Optional[str] = None
    ai_confidence: Optional[float] = None
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True
