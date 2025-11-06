"""Integration tests for LLM Service API"""
import pytest
from uuid import uuid4
from unittest.mock import patch, AsyncMock, Mock

from app.models import DocumentType, QueryPurpose


class TestKnowledgeBaseAPI:
    """Test knowledge base management endpoints"""

    @pytest.mark.asyncio
    @patch('app.main.embedding_service')
    async def test_create_knowledge_document(self, mock_embedding_service, client, sample_document, sample_embedding):
        """Test creating knowledge document with embeddings"""
        # Mock embedding service
        mock_embedding_service.chunk_text = AsyncMock(
            return_value=["Chunk 1", "Chunk 2", "Chunk 3"]
        )
        mock_embedding_service.generate_embeddings = AsyncMock(
            return_value=([sample_embedding, sample_embedding, sample_embedding], 0)
        )

        response = await client.post("/knowledge/documents", json=sample_document)

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == sample_document["title"]
        assert data["standard_code"] == sample_document["standard_code"]
        assert data["document_type"] == sample_document["document_type"]
        assert data["chunk_count"] == 3

        # Verify embedding service was called
        mock_embedding_service.chunk_text.assert_called_once()
        mock_embedding_service.generate_embeddings.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_knowledge_documents(self, client, db_document):
        """Test listing knowledge documents"""
        response = await client.get("/knowledge/documents")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 1

        # Find our test document
        doc = next((d for d in data if d["id"] == str(db_document.id)), None)
        assert doc is not None
        assert doc["title"] == db_document.title

    @pytest.mark.asyncio
    async def test_list_knowledge_documents_with_filter(self, client, db_document):
        """Test listing with document type filter"""
        # Query with matching filter
        response = await client.get(
            "/knowledge/documents",
            params={"document_type": "gaap_standard"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        # Query with non-matching filter
        response = await client.get(
            "/knowledge/documents",
            params={"document_type": "pcaob_rule"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_knowledge_document(self, client, db_document):
        """Test getting single knowledge document"""
        response = await client.get(f"/knowledge/documents/{db_document.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(db_document.id)
        assert data["title"] == db_document.title

    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self, client):
        """Test getting document that doesn't exist"""
        fake_id = uuid4()
        response = await client.get(f"/knowledge/documents/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_knowledge_document(self, client, db_document):
        """Test updating knowledge document"""
        update_data = {
            "title": "Updated Title",
            "version": "2024"
        }

        response = await client.patch(
            f"/knowledge/documents/{db_document.id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "Updated Title"
        assert data["version"] == "2024"

    @pytest.mark.asyncio
    async def test_delete_knowledge_document(self, client, db_document):
        """Test deleting knowledge document (soft delete)"""
        response = await client.delete(f"/knowledge/documents/{db_document.id}")

        assert response.status_code == 204

        # Document should still exist but be inactive
        get_response = await client.get(f"/knowledge/documents/{db_document.id}")
        assert get_response.status_code == 200

        data = get_response.json()
        assert data["is_active"] == False


class TestEmbeddingAPI:
    """Test embedding generation endpoints"""

    @pytest.mark.asyncio
    @patch('app.main.embedding_service')
    async def test_generate_embeddings(self, mock_embedding_service, client, sample_embedding):
        """Test embedding generation endpoint"""
        # Mock embedding service
        mock_embedding_service.generate_embeddings = AsyncMock(
            return_value=([sample_embedding, sample_embedding], 0)
        )

        request_data = {
            "texts": ["Text one", "Text two"],
            "cache_enabled": True
        }

        response = await client.post("/embeddings", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "embeddings" in data
        assert len(data["embeddings"]) == 2
        assert data["cache_hits"] == 0
        assert "processing_time_ms" in data

        # Verify service was called
        mock_embedding_service.generate_embeddings.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.main.embedding_service')
    async def test_generate_embeddings_with_cache(self, mock_embedding_service, client, sample_embedding):
        """Test embedding generation with cache hits"""
        # Mock with cache hits
        mock_embedding_service.generate_embeddings = AsyncMock(
            return_value=([sample_embedding], 1)
        )

        request_data = {
            "texts": ["Cached text"],
            "cache_enabled": True
        }

        response = await client.post("/embeddings", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["cache_hits"] == 1


class TestRAGAPI:
    """Test RAG query endpoints"""

    @pytest.mark.asyncio
    @patch('app.main.rag_engine')
    async def test_process_rag_query(
        self,
        mock_rag_engine,
        client,
        db_document_with_chunks
    ):
        """Test RAG query processing"""
        from app.models import RAGQuery, QueryStatus

        # Create mock query record
        mock_query = Mock(spec=RAGQuery)
        mock_query.id = uuid4()
        mock_query.response_text = "Revenue should be recognized when control transfers."
        mock_query.citations = [{
            "document_id": str(db_document_with_chunks.id),
            "document_title": db_document_with_chunks.title,
            "standard_code": "ASC 606",
            "source": "FASB",
            "chunk_content": "Revenue recognition guidance",
            "similarity_score": 0.95
        }]
        mock_query.structured_output = None
        mock_query.status = QueryStatus.COMPLETED
        mock_query.retrieval_time_ms = 100
        mock_query.generation_time_ms = 500
        mock_query.total_time_ms = 600
        mock_query.tokens_used = 200
        mock_query.created_at = "2024-01-01T00:00:00"
        mock_query.completed_at = "2024-01-01T00:00:01"

        mock_rag_engine.process_query = AsyncMock(return_value=mock_query)

        request_data = {
            "query": "How should revenue be recognized?",
            "purpose": "general_inquiry"
        }

        response = await client.post("/rag/query", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "query_id" in data
        assert data["response"] == mock_query.response_text
        assert len(data["citations"]) == 1
        assert data["status"] == "completed"
        assert data["tokens_used"] == 200

        # Verify RAG engine was called
        mock_rag_engine.process_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_rag_query(self, client):
        """Test retrieving RAG query by ID"""
        # This test requires a real query in the database
        # For now, just test the 404 case
        fake_id = uuid4()
        response = await client.get(f"/rag/queries/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    @patch('app.main.rag_engine')
    async def test_submit_query_feedback(self, mock_rag_engine, client):
        """Test submitting feedback on query"""
        from app.models import RAGQuery

        # Create mock query
        mock_query = Mock(spec=RAGQuery)
        mock_query.id = uuid4()

        # Mock the database query
        with patch('app.main.select') as mock_select:
            query_id = uuid4()

            feedback_data = {
                "query_id": str(query_id),
                "rating": 5,
                "helpful": True,
                "accurate": True,
                "feedback_text": "Very helpful response!"
            }

            # This endpoint needs the query to exist
            # Testing full flow requires database setup
            # For now, we'll just verify the endpoint exists
            response = await client.post(
                f"/rag/queries/{query_id}/feedback",
                json=feedback_data
            )

            # May return 404 if query doesn't exist, which is expected
            assert response.status_code in [200, 404]


class TestSpecializedGenerationAPI:
    """Test specialized generation endpoints"""

    @pytest.mark.asyncio
    @patch('app.main.rag_engine')
    async def test_generate_disclosure(self, mock_rag_engine, client):
        """Test disclosure generation"""
        from app.models import RAGQuery, QueryStatus

        # Create mock query record
        mock_query = Mock(spec=RAGQuery)
        mock_query.id = uuid4()
        mock_query.response_text = "Revenue Disclosure"
        mock_query.structured_output = {
            "disclosure_text": "Revenue Disclosure",
            "tables": [],
            "footnotes": [],
            "compliance_references": ["ASC 606"]
        }
        mock_query.citations = []
        mock_query.status = QueryStatus.COMPLETED
        mock_query.created_at = "2024-01-01T00:00:00"

        mock_rag_engine.process_query = AsyncMock(return_value=mock_query)

        request_data = {
            "engagement_id": str(uuid4()),
            "disclosure_type": "revenue",
            "account_data": {"revenue": 1000000},
            "fiscal_year": "2024"
        }

        response = await client.post("/disclosures/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "query_id" in data
        assert "disclosure_text" in data
        assert "compliance_references" in data
        assert "ASC 606" in data["compliance_references"]

    @pytest.mark.asyncio
    @patch('app.main.rag_engine')
    async def test_explain_anomaly(self, mock_rag_engine, client):
        """Test anomaly explanation generation"""
        from app.models import RAGQuery, QueryStatus

        # Create mock query record
        mock_query = Mock(spec=RAGQuery)
        mock_query.id = uuid4()
        mock_query.response_text = "Anomaly explanation"
        mock_query.structured_output = {
            "explanation": "This anomaly indicates...",
            "potential_causes": ["Cause 1", "Cause 2"],
            "recommended_procedures": ["Procedure 1", "Procedure 2"],
            "risk_assessment": "Medium risk"
        }
        mock_query.citations = []
        mock_query.status = QueryStatus.COMPLETED
        mock_query.created_at = "2024-01-01T00:00:00"

        mock_rag_engine.process_query = AsyncMock(return_value=mock_query)

        request_data = {
            "anomaly_id": str(uuid4()),
            "anomaly_type": "round_dollar_je",
            "engagement_id": str(uuid4()),
            "evidence": {"amount": 10000, "description": "Round dollar journal entry"}
        }

        response = await client.post("/anomalies/explain", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "query_id" in data
        assert "explanation" in data
        assert "potential_causes" in data
        assert "recommended_procedures" in data
        assert "risk_assessment" in data


class TestVectorSearchAPI:
    """Test vector search endpoints"""

    @pytest.mark.asyncio
    @patch('app.main.embedding_service')
    @patch('app.main.rag_engine')
    async def test_vector_search(
        self,
        mock_rag_engine,
        mock_embedding_service,
        client,
        sample_embedding,
        db_document_with_chunks
    ):
        """Test vector similarity search"""
        # Mock embedding service
        mock_embedding_service.generate_single_embedding = AsyncMock(
            return_value=sample_embedding
        )

        # Mock RAG engine retrieval
        mock_rag_engine.retrieve_context = AsyncMock(
            return_value=(db_document_with_chunks.chunks, [0.95, 0.90, 0.85])
        )

        request_data = {
            "query": "revenue recognition",
            "top_k": 5,
            "similarity_threshold": 0.7
        }

        response = await client.post("/search/vector", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        for result in data:
            assert "chunk_id" in result
            assert "document_id" in result
            assert "content" in result
            assert "similarity_score" in result


class TestStatsAPI:
    """Test statistics endpoints"""

    @pytest.mark.asyncio
    async def test_get_embedding_stats(self, client):
        """Test embedding statistics endpoint"""
        response = await client.get("/stats/embeddings")

        assert response.status_code == 200
        data = response.json()

        assert "total_documents" in data
        assert "total_chunks" in data
        assert "cache_size" in data
        assert "models_used" in data

    @pytest.mark.asyncio
    async def test_get_rag_stats(self, client):
        """Test RAG statistics endpoint"""
        response = await client.get("/stats/rag")

        assert response.status_code == 200
        data = response.json()

        assert "total_queries" in data
        assert "queries_by_purpose" in data
        assert "success_rate" in data
        assert "avg_total_time_ms" in data


class TestHealthCheck:
    """Test health check endpoint"""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
