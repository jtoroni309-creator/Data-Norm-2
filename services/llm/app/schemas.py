"""Pydantic schemas for LLM Service"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from .models import DocumentType, QueryPurpose, QueryStatus


# ========================================
# Knowledge Base Schemas
# ========================================

class KnowledgeDocumentCreate(BaseModel):
    """Schema for creating knowledge document"""
    document_type: DocumentType
    title: str
    standard_code: Optional[str] = None
    source: Optional[str] = None
    effective_date: Optional[datetime] = None
    content: str
    metadata: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    is_active: bool = True


class KnowledgeDocumentUpdate(BaseModel):
    """Schema for updating knowledge document"""
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None


class KnowledgeDocumentResponse(BaseModel):
    """Schema for knowledge document response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_type: DocumentType
    title: str
    standard_code: Optional[str] = None
    source: Optional[str] = None
    effective_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    chunk_count: Optional[int] = None


# ========================================
# Embedding Schemas
# ========================================

class EmbeddingRequest(BaseModel):
    """Schema for embedding generation request"""
    texts: List[str] = Field(..., description="List of texts to embed")
    cache_enabled: bool = Field(True, description="Enable embedding cache")


class EmbeddingResponse(BaseModel):
    """Schema for embedding generation response"""
    embeddings: List[List[float]] = Field(..., description="List of embedding vectors")
    model_name: str = Field(..., description="Embedding model used")
    cache_hits: int = Field(0, description="Number of cache hits")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


# ========================================
# RAG Schemas
# ========================================

class Citation(BaseModel):
    """Schema for document citation"""
    document_id: UUID
    document_title: str
    standard_code: Optional[str] = None
    source: Optional[str] = None
    chunk_content: str
    similarity_score: float
    page: Optional[int] = None
    section: Optional[str] = None


class RAGQueryRequest(BaseModel):
    """Schema for RAG query request"""
    query: str = Field(..., description="User query text")
    purpose: QueryPurpose = Field(..., description="Purpose of the query")
    engagement_id: Optional[UUID] = Field(None, description="Related engagement ID")

    # Retrieval parameters
    top_k: Optional[int] = Field(None, description="Number of documents to retrieve")
    similarity_threshold: Optional[float] = Field(None, description="Minimum similarity score")

    # Generation parameters
    temperature: Optional[float] = Field(None, description="LLM temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")

    # Filtering
    document_types: Optional[List[DocumentType]] = Field(None, description="Filter by document types")
    standard_codes: Optional[List[str]] = Field(None, description="Filter by standard codes")

    # Schema-constrained generation
    output_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for structured output")
    schema_name: Optional[str] = Field(None, description="Name of output schema")


class RAGQueryResponse(BaseModel):
    """Schema for RAG query response"""
    query_id: UUID
    response: str
    citations: List[Citation]

    # Optional structured output
    structured_output: Optional[Dict[str, Any]] = None

    # Metadata
    status: QueryStatus
    retrieval_time_ms: int
    generation_time_ms: int
    total_time_ms: int
    tokens_used: int

    created_at: datetime
    completed_at: Optional[datetime] = None


class RAGStreamChunk(BaseModel):
    """Schema for streaming RAG response chunk"""
    query_id: UUID
    chunk: str
    is_final: bool = False
    citations: Optional[List[Citation]] = None
    metadata: Optional[Dict[str, Any]] = None


# ========================================
# Structured Generation Schemas
# ========================================

class DisclosureRequest(BaseModel):
    """Schema for disclosure generation request"""
    engagement_id: UUID
    disclosure_type: str = Field(..., description="Type of disclosure (revenue, inventory, etc.)")
    account_data: Dict[str, Any] = Field(..., description="Account balances and transactions")
    fiscal_year: str

    # Additional context
    prior_year_disclosure: Optional[str] = None
    industry_context: Optional[str] = None
    custom_requirements: Optional[List[str]] = None


class DisclosureResponse(BaseModel):
    """Schema for generated disclosure"""
    query_id: UUID
    disclosure_text: str
    structured_data: Dict[str, Any]  # Formatted tables, footnotes, etc.
    citations: List[Citation]
    compliance_references: List[str]  # Relevant standards

    # Quality metrics
    completeness_score: float
    compliance_score: float

    created_at: datetime


class AnomalyExplanationRequest(BaseModel):
    """Schema for anomaly explanation request"""
    anomaly_id: UUID
    anomaly_type: str
    engagement_id: UUID
    evidence: Dict[str, Any]  # Transaction details, ratios, etc.

    # Context
    industry: Optional[str] = None
    materiality_threshold: Optional[float] = None


class AnomalyExplanationResponse(BaseModel):
    """Schema for anomaly explanation"""
    query_id: UUID
    explanation: str
    potential_causes: List[str]
    recommended_procedures: List[str]
    risk_assessment: str
    citations: List[Citation]

    created_at: datetime


# ========================================
# Feedback Schemas
# ========================================

class QueryFeedbackCreate(BaseModel):
    """Schema for creating query feedback"""
    query_id: UUID
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")
    helpful: Optional[bool] = None
    accurate: Optional[bool] = None
    feedback_text: Optional[str] = None


class QueryFeedbackResponse(BaseModel):
    """Schema for query feedback response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    query_id: UUID
    user_id: UUID
    rating: Optional[int] = None
    helpful: Optional[bool] = None
    accurate: Optional[bool] = None
    feedback_text: Optional[str] = None
    created_at: datetime


# ========================================
# Admin/Management Schemas
# ========================================

class VectorSearchRequest(BaseModel):
    """Schema for direct vector similarity search"""
    query: str
    top_k: int = Field(5, description="Number of results to return")
    similarity_threshold: float = Field(0.7, description="Minimum similarity score")
    document_types: Optional[List[DocumentType]] = None


class VectorSearchResult(BaseModel):
    """Schema for vector search result"""
    chunk_id: UUID
    document_id: UUID
    document_title: str
    content: str
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = None


class EmbeddingStats(BaseModel):
    """Schema for embedding statistics"""
    total_documents: int
    total_chunks: int
    total_embeddings: int
    cache_size: int
    cache_hit_rate: float
    avg_chunk_size: float
    models_used: List[str]


class RAGStats(BaseModel):
    """Schema for RAG usage statistics"""
    total_queries: int
    queries_by_purpose: Dict[str, int]
    avg_retrieval_time_ms: float
    avg_generation_time_ms: float
    avg_total_time_ms: float
    avg_tokens_used: float
    success_rate: float
    avg_rating: Optional[float] = None
