"""RAG (Retrieval Augmented Generation) engine using LangChain and OpenAI"""
import json
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from openai import AsyncOpenAI
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import (
    DocumentChunk,
    KnowledgeDocument,
    RAGQuery,
    QueryPurpose,
    QueryStatus,
    DocumentType
)
from .schemas import Citation, RAGQueryRequest
from .embedding_service import embedding_service

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Retrieval-Augmented Generation engine

    Combines vector similarity search with LLM generation to produce
    contextually-aware, citation-backed responses.
    """

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY
        )

    async def retrieve_context(
        self,
        db: AsyncSession,
        query_embedding: List[float],
        top_k: int,
        similarity_threshold: float,
        document_types: Optional[List[DocumentType]] = None,
        standard_codes: Optional[List[str]] = None
    ) -> Tuple[List[DocumentChunk], List[float]]:
        """
        Retrieve relevant document chunks using vector similarity

        Args:
            db: Database session
            query_embedding: Query embedding vector
            top_k: Number of chunks to retrieve
            similarity_threshold: Minimum similarity score
            document_types: Filter by document types
            standard_codes: Filter by standard codes

        Returns:
            Tuple of (chunks, similarity_scores)
        """
        start_time = time.time()

        # Build query with vector similarity
        # Note: pgvector uses <=> for cosine distance (lower is more similar)
        # Cosine similarity = 1 - cosine distance
        query = (
            select(
                DocumentChunk,
                (1 - DocumentChunk.embedding.cosine_distance(query_embedding)).label("similarity")
            )
            .join(KnowledgeDocument)
            .where(KnowledgeDocument.is_active == True)
        )

        # Apply filters
        if document_types:
            query = query.where(KnowledgeDocument.document_type.in_(document_types))

        if standard_codes:
            query = query.where(KnowledgeDocument.standard_code.in_(standard_codes))

        # Order by similarity and limit
        query = query.order_by(
            (1 - DocumentChunk.embedding.cosine_distance(query_embedding)).desc()
        ).limit(top_k * 2)  # Retrieve more then filter by threshold

        result = await db.execute(query)
        rows = result.all()

        # Filter by similarity threshold
        chunks = []
        scores = []
        for chunk, similarity in rows:
            if similarity >= similarity_threshold and len(chunks) < top_k:
                chunks.append(chunk)
                scores.append(float(similarity))

        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"Retrieved {len(chunks)} chunks in {elapsed_ms}ms "
            f"(threshold: {similarity_threshold})"
        )

        return chunks, scores

    def _build_citations(
        self,
        chunks: List[DocumentChunk],
        scores: List[float]
    ) -> List[Citation]:
        """Build citation objects from retrieved chunks"""
        citations = []

        for chunk, score in zip(chunks, scores):
            doc = chunk.document
            citation = Citation(
                document_id=doc.id,
                document_title=doc.title,
                standard_code=doc.standard_code,
                source=doc.source,
                chunk_content=chunk.content,
                similarity_score=score,
                page=chunk.metadata.get("page") if chunk.metadata else None,
                section=chunk.metadata.get("section") if chunk.metadata else None
            )
            citations.append(citation)

        return citations

    def _assemble_context(
        self,
        chunks: List[DocumentChunk],
        citations: List[Citation]
    ) -> str:
        """Assemble retrieved chunks into context string"""
        context_parts = []

        for i, (chunk, citation) in enumerate(zip(chunks, citations), 1):
            header = f"[{i}] {citation.document_title}"
            if citation.standard_code:
                header += f" ({citation.standard_code})"
            if citation.section:
                header += f" - {citation.section}"

            context_parts.append(f"{header}\n{chunk.content}\n")

        return "\n".join(context_parts)

    async def _generate_response(
        self,
        query: str,
        context: str,
        purpose: QueryPurpose,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        output_schema: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any], int]:
        """
        Generate response using LLM

        Args:
            query: User query
            context: Retrieved context
            purpose: Query purpose
            temperature: LLM temperature
            max_tokens: Maximum tokens to generate
            output_schema: JSON schema for structured output

        Returns:
            Tuple of (response_text, metadata, tokens_used)
        """
        # Build system prompt based on purpose
        system_prompts = {
            QueryPurpose.DISCLOSURE_GENERATION: (
                "You are an expert financial auditor specializing in disclosure generation. "
                "Generate clear, compliant disclosures following GAAP and SEC requirements. "
                "Use the provided context to ensure accuracy and cite relevant standards."
            ),
            QueryPurpose.WORKPAPER_REVIEW: (
                "You are an expert audit reviewer analyzing workpapers. "
                "Provide thorough, professional review comments. "
                "Reference relevant audit standards and best practices from the context."
            ),
            QueryPurpose.COMPLIANCE_CHECK: (
                "You are a compliance expert specializing in PCAOB, AICPA, and SEC regulations. "
                "Assess compliance and identify any gaps or risks. "
                "Cite specific requirements from the provided regulatory context."
            ),
            QueryPurpose.ANOMALY_EXPLANATION: (
                "You are an expert forensic auditor analyzing anomalies. "
                "Provide detailed explanations of potential causes and recommended procedures. "
                "Use the context to support your analysis with industry standards."
            ),
            QueryPurpose.RECOMMENDATION: (
                "You are a senior audit advisor providing recommendations. "
                "Offer clear, actionable guidance based on best practices. "
                "Support recommendations with citations from the provided context."
            ),
            QueryPurpose.GENERAL_INQUIRY: (
                "You are a knowledgeable audit assistant. "
                "Provide accurate, helpful responses to audit-related questions. "
                "Base your answers on the provided context and cite sources."
            )
        }

        system_prompt = system_prompts.get(
            purpose,
            system_prompts[QueryPurpose.GENERAL_INQUIRY]
        )

        # Add schema instruction if structured output requested
        if output_schema:
            system_prompt += (
                "\n\nYou must respond with valid JSON that conforms to the provided schema. "
                "Do not include any text outside the JSON object."
            )

        # Build user prompt with context
        user_prompt = f"""Context from relevant standards and guidance:

{context}

---

User Query: {query}

Please provide a comprehensive response based on the context above. Include citations to specific standards or guidance where appropriate using the format [1], [2], etc. corresponding to the context sections."""

        if output_schema:
            user_prompt += f"\n\nOutput JSON Schema:\n{json.dumps(output_schema, indent=2)}"

        # Generate response
        start_time = time.time()

        if output_schema:
            # Use function calling for structured output
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature or settings.OPENAI_TEMPERATURE,
                max_tokens=max_tokens or settings.OPENAI_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
        else:
            # Standard text generation
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature or settings.OPENAI_TEMPERATURE,
                max_tokens=max_tokens or settings.OPENAI_MAX_TOKENS
            )

        generation_time_ms = int((time.time() - start_time) * 1000)

        # Extract response
        response_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        metadata = {
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "generation_time_ms": generation_time_ms
        }

        logger.info(
            f"Generated response in {generation_time_ms}ms "
            f"({tokens_used} tokens)"
        )

        return response_text, metadata, tokens_used

    async def process_query(
        self,
        db: AsyncSession,
        user_id: UUID,
        request: RAGQueryRequest
    ) -> RAGQuery:
        """
        Process a RAG query end-to-end

        Args:
            db: Database session
            user_id: User making the query
            request: RAG query request

        Returns:
            RAGQuery object with results
        """
        start_time = time.time()

        # Create query record
        query_record = RAGQuery(
            engagement_id=request.engagement_id,
            user_id=user_id,
            purpose=request.purpose,
            query_text=request.query,
            status=QueryStatus.PROCESSING
        )
        db.add(query_record)
        await db.commit()
        await db.refresh(query_record)

        try:
            # 1. Generate query embedding
            logger.info(f"Processing query {query_record.id}: {request.query[:100]}")

            query_embedding = await embedding_service.generate_single_embedding(
                request.query,
                db=db,
                cache_enabled=True
            )
            query_record.query_embedding = query_embedding

            # 2. Retrieve relevant context
            retrieval_start = time.time()

            chunks, scores = await self.retrieve_context(
                db=db,
                query_embedding=query_embedding,
                top_k=request.top_k or settings.RAG_TOP_K,
                similarity_threshold=request.similarity_threshold or settings.RAG_SIMILARITY_THRESHOLD,
                document_types=request.document_types,
                standard_codes=request.standard_codes
            )

            retrieval_time_ms = int((time.time() - retrieval_start) * 1000)
            query_record.retrieval_time_ms = retrieval_time_ms

            # Build citations
            citations = self._build_citations(chunks, scores)
            query_record.retrieved_chunks = [
                {
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "similarity": score
                }
                for chunk, score in zip(chunks, scores)
            ]

            # Assemble context
            context = self._assemble_context(chunks, citations)
            query_record.context_used = context

            # 3. Generate response
            generation_start = time.time()

            response_text, metadata, tokens_used = await self._generate_response(
                query=request.query,
                context=context,
                purpose=request.purpose,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                output_schema=request.output_schema
            )

            generation_time_ms = int((time.time() - generation_start) * 1000)
            query_record.generation_time_ms = generation_time_ms

            # 4. Parse structured output if schema provided
            structured_output = None
            if request.output_schema:
                try:
                    structured_output = json.loads(response_text)
                    query_record.structured_output = structured_output
                    query_record.schema_name = request.schema_name
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse structured output: {e}")

            # 5. Store results
            query_record.response_text = response_text
            query_record.response_metadata = metadata
            query_record.citations = [citation.model_dump() for citation in citations]
            query_record.tokens_used = tokens_used
            query_record.status = QueryStatus.COMPLETED
            query_record.total_time_ms = int((time.time() - start_time) * 1000)

            await db.commit()
            await db.refresh(query_record)

            logger.info(
                f"Query {query_record.id} completed in {query_record.total_time_ms}ms "
                f"(retrieval: {retrieval_time_ms}ms, generation: {generation_time_ms}ms)"
            )

            return query_record

        except Exception as e:
            logger.error(f"Error processing query {query_record.id}: {e}", exc_info=True)

            query_record.status = QueryStatus.FAILED
            query_record.error_message = str(e)
            query_record.retry_count = (query_record.retry_count or 0) + 1

            await db.commit()
            raise

    async def regenerate_with_feedback(
        self,
        db: AsyncSession,
        query_id: UUID,
        feedback: str
    ) -> RAGQuery:
        """
        Regenerate response incorporating user feedback

        Args:
            db: Database session
            query_id: Original query ID
            feedback: User feedback on previous response

        Returns:
            New RAGQuery with regenerated response
        """
        # Retrieve original query
        result = await db.execute(
            select(RAGQuery).where(RAGQuery.id == query_id)
        )
        original_query = result.scalar_one()

        # Create modified query with feedback
        modified_request = RAGQueryRequest(
            query=f"{original_query.query_text}\n\nAdditional context/feedback: {feedback}",
            purpose=original_query.purpose,
            engagement_id=original_query.engagement_id
        )

        # Process modified query
        return await self.process_query(
            db=db,
            user_id=original_query.user_id,
            request=modified_request
        )


# Global RAG engine instance
rag_engine = RAGEngine()
