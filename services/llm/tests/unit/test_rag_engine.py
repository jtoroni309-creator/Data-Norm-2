"""Unit tests for RAG engine"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

from app.rag_engine import RAGEngine
from app.models import QueryPurpose, QueryStatus, DocumentType
from app.schemas import RAGQueryRequest, Citation


class TestRAGEngine:
    """Test RAG engine functionality"""

    def test_build_citations(self, db_document_with_chunks, sample_embedding):
        """Test citation building from chunks"""
        engine = RAGEngine()

        chunks = db_document_with_chunks.chunks
        scores = [0.95, 0.90, 0.85]

        citations = engine._build_citations(chunks, scores)

        assert len(citations) == len(chunks)

        for citation, score in zip(citations, scores):
            assert isinstance(citation, Citation)
            assert citation.document_id == db_document_with_chunks.id
            assert citation.document_title == db_document_with_chunks.title
            assert citation.standard_code == db_document_with_chunks.standard_code
            assert citation.similarity_score == score

    def test_assemble_context(self, db_document_with_chunks, sample_embedding):
        """Test context assembly from chunks"""
        engine = RAGEngine()

        chunks = db_document_with_chunks.chunks
        scores = [0.95, 0.90, 0.85]
        citations = engine._build_citations(chunks, scores)

        context = engine._assemble_context(chunks, citations)

        # Context should contain all chunk content
        for chunk in chunks:
            assert chunk.content in context

        # Context should be numbered
        assert "[1]" in context
        assert "[2]" in context

        # Context should include document title
        assert db_document_with_chunks.title in context

    @pytest.mark.asyncio
    async def test_retrieve_context(self, test_db, db_document_with_chunks, sample_embedding):
        """Test context retrieval with vector similarity"""
        engine = RAGEngine()

        # Use sample embedding as query
        chunks, scores = await engine.retrieve_context(
            db=test_db,
            query_embedding=sample_embedding,
            top_k=5,
            similarity_threshold=0.5
        )

        # Should retrieve chunks
        assert len(chunks) > 0
        assert len(scores) == len(chunks)

        # Scores should be between 0 and 1
        for score in scores:
            assert 0.0 <= score <= 1.0

        # Chunks should be from our test document
        for chunk in chunks:
            assert chunk.document_id == db_document_with_chunks.id

    @pytest.mark.asyncio
    async def test_retrieve_context_with_filters(
        self,
        test_db,
        db_document_with_chunks,
        sample_embedding
    ):
        """Test context retrieval with document type filters"""
        engine = RAGEngine()

        # Filter by matching document type
        chunks, scores = await engine.retrieve_context(
            db=test_db,
            query_embedding=sample_embedding,
            top_k=5,
            similarity_threshold=0.5,
            document_types=[DocumentType.GAAP_STANDARD]
        )

        assert len(chunks) > 0

        # Filter by non-matching document type
        chunks, scores = await engine.retrieve_context(
            db=test_db,
            query_embedding=sample_embedding,
            top_k=5,
            similarity_threshold=0.5,
            document_types=[DocumentType.PCAOB_RULE]
        )

        assert len(chunks) == 0

    @pytest.mark.asyncio
    async def test_retrieve_context_similarity_threshold(
        self,
        test_db,
        db_document_with_chunks,
        sample_embedding
    ):
        """Test similarity threshold filtering"""
        engine = RAGEngine()

        # High threshold should return fewer results
        chunks_high, _ = await engine.retrieve_context(
            db=test_db,
            query_embedding=sample_embedding,
            top_k=10,
            similarity_threshold=0.99  # Very high threshold
        )

        # Low threshold should return more results
        chunks_low, _ = await engine.retrieve_context(
            db=test_db,
            query_embedding=sample_embedding,
            top_k=10,
            similarity_threshold=0.5  # Low threshold
        )

        assert len(chunks_high) <= len(chunks_low)

    @pytest.mark.asyncio
    @patch('app.rag_engine.AsyncOpenAI')
    async def test_generate_response(self, mock_openai, mock_openai_response):
        """Test LLM response generation"""
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(message=Mock(content="Generated response"), finish_reason="stop")],
                usage=Mock(total_tokens=200, prompt_tokens=150, completion_tokens=50),
                model="gpt-4-turbo-preview"
            )
        )
        mock_openai.return_value = mock_client

        engine = RAGEngine()
        engine.openai_client = mock_client

        response_text, metadata, tokens_used = await engine._generate_response(
            query="What is revenue recognition?",
            context="Revenue is recognized when...",
            purpose=QueryPurpose.GENERAL_INQUIRY
        )

        assert response_text == "Generated response"
        assert tokens_used == 200
        assert "model" in metadata
        assert metadata["finish_reason"] == "stop"

        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.rag_engine.AsyncOpenAI')
    @patch('app.rag_engine.embedding_service')
    async def test_process_query_end_to_end(
        self,
        mock_embedding_service,
        mock_openai,
        test_db,
        db_document_with_chunks,
        sample_embedding
    ):
        """Test end-to-end query processing"""
        # Mock embedding service
        mock_embedding_service.generate_single_embedding = AsyncMock(
            return_value=sample_embedding
        )

        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(
                    message=Mock(content="Revenue should be recognized when control transfers."),
                    finish_reason="stop"
                )],
                usage=Mock(total_tokens=200, prompt_tokens=150, completion_tokens=50),
                model="gpt-4-turbo-preview"
            )
        )
        mock_openai.return_value = mock_client

        engine = RAGEngine()
        engine.openai_client = mock_client

        # Create request
        request = RAGQueryRequest(
            query="How should revenue be recognized?",
            purpose=QueryPurpose.GENERAL_INQUIRY,
            engagement_id=uuid4()
        )

        user_id = uuid4()

        # Process query
        query_record = await engine.process_query(
            db=test_db,
            user_id=user_id,
            request=request
        )

        # Verify query record
        assert query_record.status == QueryStatus.COMPLETED
        assert query_record.response_text is not None
        assert query_record.user_id == user_id
        assert query_record.query_text == request.query
        assert query_record.purpose == request.purpose

        # Verify timing metrics
        assert query_record.retrieval_time_ms > 0
        assert query_record.generation_time_ms > 0
        assert query_record.total_time_ms > 0

        # Verify tokens used
        assert query_record.tokens_used == 200

        # Verify citations
        assert query_record.citations is not None
        assert len(query_record.citations) > 0

    @pytest.mark.asyncio
    @patch('app.rag_engine.AsyncOpenAI')
    async def test_generate_response_with_schema(self, mock_openai):
        """Test structured output generation with JSON schema"""
        # Mock OpenAI client for JSON mode
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(
                    message=Mock(content='{"answer": "Revenue recognition", "confidence": 0.95}'),
                    finish_reason="stop"
                )],
                usage=Mock(total_tokens=150, prompt_tokens=100, completion_tokens=50),
                model="gpt-4-turbo-preview"
            )
        )
        mock_openai.return_value = mock_client

        engine = RAGEngine()
        engine.openai_client = mock_client

        schema = {
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "confidence": {"type": "number"}
            }
        }

        response_text, metadata, tokens_used = await engine._generate_response(
            query="What is this about?",
            context="Revenue recognition guidance",
            purpose=QueryPurpose.GENERAL_INQUIRY,
            output_schema=schema
        )

        # Should return valid JSON
        import json
        parsed = json.loads(response_text)
        assert "answer" in parsed
        assert "confidence" in parsed

    @pytest.mark.asyncio
    @patch('app.rag_engine.embedding_service')
    async def test_process_query_error_handling(
        self,
        mock_embedding_service,
        test_db,
        db_document_with_chunks
    ):
        """Test error handling in query processing"""
        # Mock embedding service to raise error
        mock_embedding_service.generate_single_embedding = AsyncMock(
            side_effect=Exception("Embedding generation failed")
        )

        engine = RAGEngine()

        request = RAGQueryRequest(
            query="Test query",
            purpose=QueryPurpose.GENERAL_INQUIRY
        )

        # Should raise exception
        with pytest.raises(Exception):
            await engine.process_query(
                db=test_db,
                user_id=uuid4(),
                request=request
            )

        # Query record should be marked as failed
        from sqlalchemy import select
        from app.models import RAGQuery

        result = await test_db.execute(
            select(RAGQuery).where(RAGQuery.query_text == "Test query")
        )
        query_record = result.scalar_one_or_none()

        if query_record:
            assert query_record.status == QueryStatus.FAILED
            assert query_record.error_message is not None
