"""
SQLAlchemy models for Tax OCR Intake Service
"""
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    Numeric,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from datetime import datetime
from uuid import uuid4
import enum

from .database import Base


# Enums (matching migration)
class DocumentType(str, enum.Enum):
    W2 = "W-2"
    INT_1099 = "1099-INT"
    DIV_1099 = "1099-DIV"
    B_1099 = "1099-B"
    R_1099 = "1099-R"
    MISC_1099 = "1099-MISC"
    NEC_1099 = "1099-NEC"
    G_1099 = "1099-G"
    K_1099 = "1099-K"
    MORTGAGE_1098 = "1098"
    STUDENT_LOAN_1098E = "1098-E"
    TUITION_1098T = "1098-T"
    IRA_5498 = "5498"
    HSA_5498SA = "5498-SA"
    K1_1065 = "K-1-1065"
    K1_1120S = "K-1-1120S"
    K1_1041 = "K-1-1041"
    SSA_1099 = "SSA-1099"
    HEALTH_1095A = "1095-A"
    HEALTH_1095B = "1095-B"
    HEALTH_1095C = "1095-C"
    BROKERAGE_STATEMENT = "BROKERAGE_STATEMENT"
    PROPERTY_TAX = "PROPERTY_TAX"
    CHARITY_RECEIPT = "CHARITY_RECEIPT"
    BUSINESS_EXPENSE = "BUSINESS_EXPENSE"
    OTHER = "OTHER"


class TaxDocument(Base):
    """Source documents (W-2, 1099s, etc.) for OCR processing"""

    __tablename__ = "tax_documents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_return_id = Column(PGUUID(as_uuid=True), ForeignKey("tax_returns.id"), nullable=False)

    # Document metadata
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    classification_confidence = Column(Numeric(3, 2))
    tax_year = Column(Integer)

    # File storage
    file_url = Column(Text, nullable=False)
    file_name = Column(Text)
    file_size = Column(BigInteger)
    file_checksum = Column(Text)
    mime_type = Column(Text)
    page_count = Column(Integer, default=1)

    # OCR metadata
    ocr_completed = Column(Boolean, default=False)
    ocr_completed_at = Column(DateTime)
    ocr_model_version = Column(Text)

    # Classification
    classified_by = Column(Text)
    classified_at = Column(DateTime)
    manual_classification = Column(Boolean, default=False)

    # Deduplication
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(PGUUID(as_uuid=True), ForeignKey("tax_documents.id"))

    # Version control
    version = Column(Integer, default=1)
    superseded_by_id = Column(PGUUID(as_uuid=True), ForeignKey("tax_documents.id"))

    # Metadata
    uploaded_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TaxDocumentPage(Base):
    """Individual pages from multi-page documents"""

    __tablename__ = "tax_document_pages"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_document_id = Column(
        PGUUID(as_uuid=True), ForeignKey("tax_documents.id"), nullable=False
    )

    page_number = Column(Integer, nullable=False)
    image_url = Column(Text)
    ocr_text = Column(Text)
    ocr_confidence = Column(Numeric(3, 2))

    # Layout analysis (bounding boxes, tables)
    layout = Column(JSONB)

    # Classification
    page_type = Column(SQLEnum(DocumentType))
    page_classification_confidence = Column(Numeric(3, 2))

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TaxExtractedField(Base):
    """Raw OCR field extractions with confidence scores"""

    __tablename__ = "tax_extracted_fields"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_document_id = Column(
        PGUUID(as_uuid=True), ForeignKey("tax_documents.id"), nullable=False
    )
    tax_document_page_id = Column(PGUUID(as_uuid=True), ForeignKey("tax_document_pages.id"))

    # Field identification
    field_name = Column(Text, nullable=False)
    field_label = Column(Text)
    field_value = Column(Text)
    field_value_normalized = Column(Text)
    field_type = Column(Text)

    # Confidence
    confidence = Column(Numeric(3, 2), nullable=False)

    # Bounding box
    bbox = Column(JSONB)

    # Validation
    validated = Column(Boolean, default=False)
    validation_errors = Column(JSONB)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TaxProvenance(Base):
    """Audit trail: TDS field → source document → extraction rule"""

    __tablename__ = "tax_provenance"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_return_id = Column(PGUUID(as_uuid=True), ForeignKey("tax_returns.id"), nullable=False)

    # Field mapping
    field_path = Column(Text, nullable=False)
    field_value = Column(Text)

    # Source tracing
    source_type = Column(Text)
    source_document_id = Column(PGUUID(as_uuid=True), ForeignKey("tax_documents.id"))
    source_document_page_id = Column(PGUUID(as_uuid=True), ForeignKey("tax_document_pages.id"))
    source_document_ref = Column(Text)

    # Extraction details
    extraction_method = Column(Text)
    ocr_model_version = Column(Text)
    mapping_rule_id = Column(Text)
    calculation_formula = Column(Text)

    # User attribution
    entered_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    modified_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
