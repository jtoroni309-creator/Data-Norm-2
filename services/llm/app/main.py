"""Main FastAPI application for LLM Service"""
import logging
from contextlib import asynccontextmanager
from typing import List
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import init_db, close_db, get_db
from .models import (
    KnowledgeDocument,
    DocumentChunk,
    RAGQuery,
    QueryFeedback,
    DocumentType,
    QueryStatus
)
from .schemas import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGStreamChunk,
    QueryFeedbackCreate,
    QueryFeedbackResponse,
    VectorSearchRequest,
    VectorSearchResult,
    EmbeddingStats,
    RAGStats,
    Citation,
    DisclosureRequest,
    DisclosureResponse,
    AnomalyExplanationRequest,
    AnomalyExplanationResponse
)
from .embedding_service import embedding_service
from .rag_engine import rag_engine

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} service v{settings.VERSION}")
    await init_db()
    embedding_service.load_model()
    logger.info("LLM service ready")

    yield

    # Shutdown
    logger.info("Shutting down LLM service")
    await close_db()


app = FastAPI(
    title="Aura Audit AI - LLM Service",
    description="RAG-powered AI assistant for audit insights and document generation",
    version=settings.VERSION,
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


# ========================================
# Dependency: User Authentication
# ========================================

async def get_current_user_id() -> UUID:
    """
    Get current user ID from JWT token
    TODO: Implement actual JWT validation
    """
    # For now, return a mock user ID
    # In production, this should extract and validate JWT from Authorization header
    return UUID("00000000-0000-0000-0000-000000000001")


# ========================================
# Health Check
# ========================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION
    }


# ========================================
# Knowledge Base Management
# ========================================

@app.post("/knowledge/documents", response_model=KnowledgeDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_document(
    document: KnowledgeDocumentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new knowledge document and generate embeddings"""
    # Create document
    db_document = KnowledgeDocument(**document.model_dump())
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)

    # Generate chunks and embeddings
    chunks_text = await embedding_service.chunk_text(document.content)
    embeddings, _ = await embedding_service.generate_embeddings(
        chunks_text,
        db=db,
        cache_enabled=False  # Don't cache document chunks
    )

    # Create chunk records
    for i, (chunk_text, embedding) in enumerate(zip(chunks_text, embeddings)):
        chunk = DocumentChunk(
            document_id=db_document.id,
            chunk_index=i,
            content=chunk_text,
            embedding=embedding,
            token_count=len(chunk_text.split())
        )
        db.add(chunk)

    await db.commit()
    await db.refresh(db_document)

    response = KnowledgeDocumentResponse.model_validate(db_document)
    response.chunk_count = len(chunks_text)

    logger.info(
        f"Created knowledge document {db_document.id} "
        f"with {len(chunks_text)} chunks"
    )

    return response


@app.get("/knowledge/documents", response_model=List[KnowledgeDocumentResponse])
async def list_knowledge_documents(
    document_type: DocumentType | None = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List knowledge documents with optional filters"""
    query = select(KnowledgeDocument).where(
        KnowledgeDocument.is_active == is_active
    )

    if document_type:
        query = query.where(KnowledgeDocument.document_type == document_type)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    documents = result.scalars().all()

    # Get chunk counts
    responses = []
    for doc in documents:
        response = KnowledgeDocumentResponse.model_validate(doc)

        # Count chunks
        chunk_count_query = select(func.count()).where(
            DocumentChunk.document_id == doc.id
        )
        chunk_count_result = await db.execute(chunk_count_query)
        response.chunk_count = chunk_count_result.scalar()

        responses.append(response)

    return responses


@app.get("/knowledge/documents/{document_id}", response_model=KnowledgeDocumentResponse)
async def get_knowledge_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get knowledge document by ID"""
    result = await db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    response = KnowledgeDocumentResponse.model_validate(document)

    # Get chunk count
    chunk_count_query = select(func.count()).where(
        DocumentChunk.document_id == document.id
    )
    chunk_count_result = await db.execute(chunk_count_query)
    response.chunk_count = chunk_count_result.scalar()

    return response


@app.patch("/knowledge/documents/{document_id}", response_model=KnowledgeDocumentResponse)
async def update_knowledge_document(
    document_id: UUID,
    update: KnowledgeDocumentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update knowledge document"""
    result = await db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Update fields
    update_data = update.model_dump(exclude_unset=True)

    # If content is updated, regenerate embeddings
    content_updated = False
    if "content" in update_data:
        content_updated = True

    for field, value in update_data.items():
        setattr(document, field, value)

    await db.commit()

    # Regenerate embeddings if content changed
    if content_updated:
        # Delete old chunks
        await db.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        await db.commit()

        # Generate new chunks
        chunks_text = await embedding_service.chunk_text(document.content)
        embeddings, _ = await embedding_service.generate_embeddings(
            chunks_text,
            db=db,
            cache_enabled=False
        )

        for i, (chunk_text, embedding) in enumerate(zip(chunks_text, embeddings)):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
                embedding=embedding,
                token_count=len(chunk_text.split())
            )
            db.add(chunk)

        await db.commit()

    await db.refresh(document)

    response = KnowledgeDocumentResponse.model_validate(document)
    return response


@app.delete("/knowledge/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete knowledge document (soft delete)"""
    result = await db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    document.is_active = False
    await db.commit()

    logger.info(f"Soft deleted knowledge document {document_id}")


# ========================================
# Embedding Generation
# ========================================

@app.post("/embeddings", response_model=EmbeddingResponse)
async def generate_embeddings(
    request: EmbeddingRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate embeddings for text inputs"""
    import time

    start_time = time.time()

    embeddings, cache_hits = await embedding_service.generate_embeddings(
        request.texts,
        db=db,
        cache_enabled=request.cache_enabled
    )

    processing_time_ms = int((time.time() - start_time) * 1000)

    return EmbeddingResponse(
        embeddings=embeddings,
        model_name=settings.EMBEDDING_MODEL,
        cache_hits=cache_hits,
        processing_time_ms=processing_time_ms
    )


# ========================================
# RAG Query Processing
# ========================================

@app.post("/rag/query", response_model=RAGQueryResponse)
async def process_rag_query(
    request: RAGQueryRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Process RAG query and generate response"""
    query_record = await rag_engine.process_query(
        db=db,
        user_id=user_id,
        request=request
    )

    # Build response
    citations = [Citation(**c) for c in query_record.citations]

    return RAGQueryResponse(
        query_id=query_record.id,
        response=query_record.response_text,
        citations=citations,
        structured_output=query_record.structured_output,
        status=query_record.status,
        retrieval_time_ms=query_record.retrieval_time_ms,
        generation_time_ms=query_record.generation_time_ms,
        total_time_ms=query_record.total_time_ms,
        tokens_used=query_record.tokens_used,
        created_at=query_record.created_at,
        completed_at=query_record.completed_at
    )


@app.get("/rag/queries/{query_id}", response_model=RAGQueryResponse)
async def get_rag_query(
    query_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get RAG query by ID"""
    result = await db.execute(
        select(RAGQuery).where(RAGQuery.id == query_id)
    )
    query_record = result.scalar_one_or_none()

    if not query_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )

    citations = [Citation(**c) for c in query_record.citations] if query_record.citations else []

    return RAGQueryResponse(
        query_id=query_record.id,
        response=query_record.response_text,
        citations=citations,
        structured_output=query_record.structured_output,
        status=query_record.status,
        retrieval_time_ms=query_record.retrieval_time_ms,
        generation_time_ms=query_record.generation_time_ms,
        total_time_ms=query_record.total_time_ms,
        tokens_used=query_record.tokens_used,
        created_at=query_record.created_at,
        completed_at=query_record.completed_at
    )


# ========================================
# Specialized Generation Endpoints
# ========================================

@app.post("/disclosures/generate", response_model=DisclosureResponse)
async def generate_disclosure(
    request: DisclosureRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Generate financial disclosure using RAG"""
    # Build specialized query for disclosure generation
    query_text = f"""Generate a {request.disclosure_type} disclosure for fiscal year {request.fiscal_year}.

Account Data:
{request.account_data}

Requirements:
- Follow GAAP standards for {request.disclosure_type} disclosures
- Include all required elements
- Ensure compliance with SEC regulations
- Format for 10-K filing
"""

    if request.prior_year_disclosure:
        query_text += f"\n\nPrior Year Disclosure (for reference):\n{request.prior_year_disclosure}"

    if request.industry_context:
        query_text += f"\n\nIndustry Context: {request.industry_context}"

    if request.custom_requirements:
        query_text += f"\n\nCustom Requirements:\n" + "\n".join(f"- {req}" for req in request.custom_requirements)

    # Define output schema for disclosure
    output_schema = {
        "type": "object",
        "properties": {
            "disclosure_text": {"type": "string"},
            "tables": {"type": "array", "items": {"type": "object"}},
            "footnotes": {"type": "array", "items": {"type": "string"}},
            "compliance_references": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["disclosure_text", "compliance_references"]
    }

    rag_request = RAGQueryRequest(
        query=query_text,
        purpose="disclosure_generation",
        engagement_id=request.engagement_id,
        output_schema=output_schema,
        schema_name="disclosure",
        document_types=[DocumentType.GAAP_STANDARD, DocumentType.SEC_REGULATION]
    )

    query_record = await rag_engine.process_query(
        db=db,
        user_id=user_id,
        request=rag_request
    )

    # Extract structured output
    structured = query_record.structured_output or {}
    citations = [Citation(**c) for c in query_record.citations]

    return DisclosureResponse(
        query_id=query_record.id,
        disclosure_text=structured.get("disclosure_text", query_record.response_text),
        structured_data=structured,
        citations=citations,
        compliance_references=structured.get("compliance_references", []),
        completeness_score=0.95,  # TODO: Implement scoring
        compliance_score=0.98,
        created_at=query_record.created_at
    )


@app.post("/anomalies/explain", response_model=AnomalyExplanationResponse)
async def explain_anomaly(
    request: AnomalyExplanationRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Generate explanation for detected anomaly"""
    # Build specialized query for anomaly explanation
    query_text = f"""Analyze and explain the following {request.anomaly_type} anomaly.

Evidence:
{request.evidence}

Provide:
1. Detailed explanation of the anomaly
2. Potential causes
3. Recommended audit procedures
4. Risk assessment
"""

    if request.industry:
        query_text += f"\n\nIndustry: {request.industry}"

    if request.materiality_threshold:
        query_text += f"\nMateriality Threshold: ${request.materiality_threshold:,.2f}"

    # Define output schema
    output_schema = {
        "type": "object",
        "properties": {
            "explanation": {"type": "string"},
            "potential_causes": {"type": "array", "items": {"type": "string"}},
            "recommended_procedures": {"type": "array", "items": {"type": "string"}},
            "risk_assessment": {"type": "string"}
        },
        "required": ["explanation", "potential_causes", "recommended_procedures", "risk_assessment"]
    }

    rag_request = RAGQueryRequest(
        query=query_text,
        purpose="anomaly_explanation",
        engagement_id=request.engagement_id,
        output_schema=output_schema,
        schema_name="anomaly_explanation",
        document_types=[DocumentType.GAAS_STANDARD, DocumentType.PCAOB_RULE]
    )

    query_record = await rag_engine.process_query(
        db=db,
        user_id=user_id,
        request=rag_request
    )

    # Extract structured output
    structured = query_record.structured_output or {}
    citations = [Citation(**c) for c in query_record.citations]

    return AnomalyExplanationResponse(
        query_id=query_record.id,
        explanation=structured.get("explanation", ""),
        potential_causes=structured.get("potential_causes", []),
        recommended_procedures=structured.get("recommended_procedures", []),
        risk_assessment=structured.get("risk_assessment", ""),
        citations=citations,
        created_at=query_record.created_at
    )


# ========================================
# Query Feedback
# ========================================

@app.post("/rag/queries/{query_id}/feedback", response_model=QueryFeedbackResponse)
async def submit_query_feedback(
    query_id: UUID,
    feedback: QueryFeedbackCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback on RAG query response"""
    # Verify query exists
    result = await db.execute(
        select(RAGQuery).where(RAGQuery.id == query_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )

    # Create feedback
    db_feedback = QueryFeedback(
        query_id=query_id,
        user_id=user_id,
        **feedback.model_dump(exclude={"query_id"})
    )

    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)

    return QueryFeedbackResponse.model_validate(db_feedback)


# ========================================
# Vector Search
# ========================================

@app.post("/search/vector", response_model=List[VectorSearchResult])
async def vector_search(
    request: VectorSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Perform direct vector similarity search"""
    # Generate query embedding
    query_embedding = await embedding_service.generate_single_embedding(
        request.query,
        db=db,
        cache_enabled=True
    )

    # Search for similar chunks
    chunks, scores = await rag_engine.retrieve_context(
        db=db,
        query_embedding=query_embedding,
        top_k=request.top_k,
        similarity_threshold=request.similarity_threshold,
        document_types=request.document_types
    )

    # Build results
    results = []
    for chunk, score in zip(chunks, scores):
        doc = chunk.document
        result = VectorSearchResult(
            chunk_id=chunk.id,
            document_id=doc.id,
            document_title=doc.title,
            content=chunk.content,
            similarity_score=score,
            metadata=chunk.metadata
        )
        results.append(result)

    return results


# ========================================
# Statistics & Analytics
# ========================================

@app.get("/stats/embeddings", response_model=EmbeddingStats)
async def get_embedding_stats(db: AsyncSession = Depends(get_db)):
    """Get embedding statistics"""
    # Total documents
    doc_count = await db.execute(
        select(func.count()).select_from(KnowledgeDocument).where(
            KnowledgeDocument.is_active == True
        )
    )
    total_documents = doc_count.scalar()

    # Total chunks
    chunk_count = await db.execute(select(func.count()).select_from(DocumentChunk))
    total_chunks = chunk_count.scalar()

    # Cache stats
    from .models import EmbeddingCache
    cache_count = await db.execute(select(func.count()).select_from(EmbeddingCache))
    cache_size = cache_count.scalar()

    # Average chunk size
    avg_size = await db.execute(
        select(func.avg(func.length(DocumentChunk.content)))
    )
    avg_chunk_size = float(avg_size.scalar() or 0)

    return EmbeddingStats(
        total_documents=total_documents,
        total_chunks=total_chunks,
        total_embeddings=total_chunks,
        cache_size=cache_size,
        cache_hit_rate=0.0,  # TODO: Track hit rate
        avg_chunk_size=avg_chunk_size,
        models_used=[settings.EMBEDDING_MODEL]
    )


@app.get("/stats/rag", response_model=RAGStats)
async def get_rag_stats(db: AsyncSession = Depends(get_db)):
    """Get RAG usage statistics"""
    from .models import QueryPurpose

    # Total queries
    total_count = await db.execute(select(func.count()).select_from(RAGQuery))
    total_queries = total_count.scalar()

    # Queries by purpose
    queries_by_purpose = {}
    for purpose in QueryPurpose:
        count = await db.execute(
            select(func.count()).select_from(RAGQuery).where(
                RAGQuery.purpose == purpose
            )
        )
        queries_by_purpose[purpose.value] = count.scalar()

    # Average timings
    avg_timings = await db.execute(
        select(
            func.avg(RAGQuery.retrieval_time_ms),
            func.avg(RAGQuery.generation_time_ms),
            func.avg(RAGQuery.total_time_ms),
            func.avg(RAGQuery.tokens_used)
        ).where(RAGQuery.status == QueryStatus.COMPLETED)
    )
    timings = avg_timings.first()

    # Success rate
    success_count = await db.execute(
        select(func.count()).select_from(RAGQuery).where(
            RAGQuery.status == QueryStatus.COMPLETED
        )
    )
    successes = success_count.scalar()
    success_rate = (successes / total_queries * 100) if total_queries > 0 else 0

    # Average rating
    avg_rating_result = await db.execute(
        select(func.avg(QueryFeedback.rating)).where(
            QueryFeedback.rating.isnot(None)
        )
    )
    avg_rating = avg_rating_result.scalar()

    return RAGStats(
        total_queries=total_queries,
        queries_by_purpose=queries_by_purpose,
        avg_retrieval_time_ms=float(timings[0] or 0),
        avg_generation_time_ms=float(timings[1] or 0),
        avg_total_time_ms=float(timings[2] or 0),
        avg_tokens_used=float(timings[3] or 0),
        success_rate=success_rate,
        avg_rating=float(avg_rating) if avg_rating else None
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
