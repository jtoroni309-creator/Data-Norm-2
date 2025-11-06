"""SQLAlchemy ORM models for LLM Service"""
from datetime import datetime
from uuid import uuid4
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    ForeignKey,
    Text,
    Boolean,
    Enum as SQLEnum,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from .database import Base
from .config import settings


# ========================================
# Enums
# ========================================

class DocumentType(str, Enum):
    """Type of document in knowledge base"""
    GAAP_STANDARD = "gaap_standard"
    GAAS_STANDARD = "gaas_standard"
    PCAOB_RULE = "pcaob_rule"
    AICPA_GUIDANCE = "aicpa_guidance"
    SEC_REGULATION = "sec_regulation"
    INTERNAL_POLICY = "internal_policy"
    WORKPAPER = "workpaper"
    INDUSTRY_GUIDANCE = "industry_guidance"
    OTHER = "other"


class QueryPurpose(str, Enum):
    """Purpose of RAG query"""
    DISCLOSURE_GENERATION = "disclosure_generation"
    WORKPAPER_REVIEW = "workpaper_review"
    COMPLIANCE_CHECK = "compliance_check"
    ANOMALY_EXPLANATION = "anomaly_explanation"
    RECOMMENDATION = "recommendation"
    GENERAL_INQUIRY = "general_inquiry"


class QueryStatus(str, Enum):
    """Status of RAG query"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ========================================
# ORM Models
# ========================================

class KnowledgeDocument(Base):
    """
    Knowledge base document

    Stores reference documents (GAAP, GAAS, PCAOB, etc.) with metadata.
    Full text is chunked and embedded separately.
    """
    __tablename__ = "knowledge_documents"
    __table_args__ = (
        Index("idx_knowledge_type", "document_type"),
        Index("idx_knowledge_standard", "standard_code"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    document_type = Column(
        SQLEnum(DocumentType, name="document_type", create_type=False),
        nullable=False
    )
    title = Column(Text, nullable=False)
    standard_code = Column(String)  # e.g., "ASC 606", "AU-C 230"
    source = Column(String)  # FASB, AICPA, PCAOB, etc.
    effective_date = Column(DateTime(timezone=True))
    content = Column(Text, nullable=False)  # Full document text
    metadata = Column(JSONB)  # Additional metadata
    version = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """
    Document chunk with embedding

    Stores text chunks from knowledge documents with their vector embeddings
    for semantic search. Uses pgvector for similarity search.
    """
    __tablename__ = "document_chunks"
    __table_args__ = (
        Index("idx_chunk_document", "document_id"),
        Index(
            "idx_chunk_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"}
        ),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.knowledge_documents.id"),
        nullable=False
    )
    chunk_index = Column(Integer, nullable=False)  # Position in document
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION))  # pgvector type
    token_count = Column(Integer)
    metadata = Column(JSONB)  # Section headers, page numbers, etc.
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    document = relationship("KnowledgeDocument", back_populates="chunks")


class RAGQuery(Base):
    """
    RAG query execution record

    Tracks queries made to the RAG system including the query text,
    retrieved context, generated response, and usage metrics.
    """
    __tablename__ = "rag_queries"
    __table_args__ = (
        Index("idx_rag_engagement", "engagement_id"),
        Index("idx_rag_user", "user_id"),
        Index("idx_rag_purpose", "purpose"),
        Index("idx_rag_status", "status"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True))  # Optional: related engagement
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    purpose = Column(
        SQLEnum(QueryPurpose, name="query_purpose", create_type=False),
        nullable=False
    )
    query_text = Column(Text, nullable=False)
    query_embedding = Column(Vector(settings.EMBEDDING_DIMENSION))
    status = Column(
        SQLEnum(QueryStatus, name="query_status", create_type=False),
        nullable=False,
        default=QueryStatus.PENDING
    )

    # Retrieved context
    retrieved_chunks = Column(JSONB)  # List of chunk IDs and scores
    context_used = Column(Text)  # Assembled context sent to LLM

    # Generated response
    response_text = Column(Text)
    response_metadata = Column(JSONB)  # Model used, tokens, etc.

    # Schema-constrained output (for structured generation)
    schema_name = Column(String)  # Name of output schema if used
    structured_output = Column(JSONB)  # Structured JSON output

    # Citations
    citations = Column(JSONB)  # References to source documents

    # Performance metrics
    retrieval_time_ms = Column(Integer)
    generation_time_ms = Column(Integer)
    total_time_ms = Column(Integer)
    tokens_used = Column(Integer)

    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    feedback = relationship("QueryFeedback", back_populates="query", uselist=False)


class QueryFeedback(Base):
    """
    User feedback on RAG responses

    Allows users to rate and provide feedback on generated responses
    for continuous improvement.
    """
    __tablename__ = "query_feedback"
    __table_args__ = (
        Index("idx_feedback_query", "query_id"),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    query_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.rag_queries.id"),
        nullable=False,
        unique=True
    )
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    rating = Column(Integer)  # 1-5 scale
    helpful = Column(Boolean)
    accurate = Column(Boolean)
    feedback_text = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    query = relationship("RAGQuery", back_populates="feedback")


class EmbeddingCache(Base):
    """
    Cache for text embeddings

    Caches embeddings for frequently accessed text to reduce
    embedding API calls and improve response times.
    """
    __tablename__ = "embedding_cache"
    __table_args__ = (
        Index("idx_embedding_hash", "text_hash", unique=True),
        {"schema": "atlas"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    text_hash = Column(String(64), nullable=False, unique=True)  # SHA256 hash
    text = Column(Text, nullable=False)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION))
    model_name = Column(String, nullable=False)
    access_count = Column(Integer, nullable=False, default=1)
    last_accessed = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
