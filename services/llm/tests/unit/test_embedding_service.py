"""Unit tests for embedding service"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import numpy as np

from app.embedding_service import EmbeddingService, embedding_service
from app.models import EmbeddingCache


class TestEmbeddingService:
    """Test embedding service functionality"""

    def test_compute_text_hash(self):
        """Test text hashing"""
        service = EmbeddingService()

        text = "Hello, world!"
        hash1 = service._compute_text_hash(text)
        hash2 = service._compute_text_hash(text)

        # Same text should produce same hash
        assert hash1 == hash2

        # Different text should produce different hash
        hash3 = service._compute_text_hash("Different text")
        assert hash1 != hash3

        # Hash should be 64 character hex string (SHA256)
        assert len(hash1) == 64
        assert all(c in '0123456789abcdef' for c in hash1)

    def test_compute_similarity(self):
        """Test cosine similarity computation"""
        service = EmbeddingService()

        # Identical vectors should have similarity of 1.0
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = service.compute_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001

        # Orthogonal vectors should have similarity of 0.0
        vec3 = [1.0, 0.0, 0.0]
        vec4 = [0.0, 1.0, 0.0]
        similarity = service.compute_similarity(vec3, vec4)
        assert abs(similarity - 0.0) < 0.001

        # Opposite vectors should have similarity of -1.0
        vec5 = [1.0, 0.0, 0.0]
        vec6 = [-1.0, 0.0, 0.0]
        similarity = service.compute_similarity(vec5, vec6)
        assert abs(similarity - (-1.0)) < 0.001

    @pytest.mark.asyncio
    async def test_chunk_text_default_params(self):
        """Test text chunking with default parameters"""
        service = EmbeddingService()

        # Short text should not be chunked
        short_text = "This is a short text."
        chunks = await service.chunk_text(short_text)
        assert len(chunks) == 1
        assert chunks[0] == short_text

        # Long text should be chunked
        long_text = "This is a sentence. " * 100  # Creates ~2000 character text
        chunks = await service.chunk_text(long_text)
        assert len(chunks) > 1

        # All chunks should have content
        for chunk in chunks:
            assert len(chunk) > 0

    @pytest.mark.asyncio
    async def test_chunk_text_custom_params(self):
        """Test text chunking with custom parameters"""
        service = EmbeddingService()

        text = "This is sentence one. This is sentence two. This is sentence three."

        # Small chunk size should create more chunks
        chunks = await service.chunk_text(text, chunk_size=20, chunk_overlap=5)
        assert len(chunks) > 2

        # Verify overlap exists
        for i in range(len(chunks) - 1):
            # Some content from current chunk should appear in next chunk
            assert any(
                word in chunks[i+1]
                for word in chunks[i].split()[-3:]  # Last 3 words
            )

    @pytest.mark.asyncio
    async def test_get_cached_embedding_miss(self, test_db):
        """Test cache miss when embedding not cached"""
        service = EmbeddingService()

        cached = await service._get_cached_embedding(test_db, "Not in cache")
        assert cached is None

    @pytest.mark.asyncio
    async def test_cache_and_retrieve_embedding(self, test_db, sample_embedding):
        """Test caching and retrieving embedding"""
        service = EmbeddingService()

        text = "Cache this text"

        # Initially not cached
        cached = await service._get_cached_embedding(test_db, text)
        assert cached is None

        # Cache the embedding
        await service._cache_embedding(test_db, text, sample_embedding)

        # Should now be cached
        cached = await service._get_cached_embedding(test_db, text)
        assert cached is not None
        assert len(cached) == len(sample_embedding)

    @pytest.mark.asyncio
    @patch('app.embedding_service.SentenceTransformer')
    async def test_generate_embeddings_no_cache(self, mock_transformer, sample_embedding):
        """Test embedding generation without caching"""
        # Mock the model
        mock_model = Mock()
        mock_model.encode = Mock(return_value=np.array([sample_embedding, sample_embedding]))
        mock_transformer.return_value = mock_model

        service = EmbeddingService()
        service.model = mock_model

        texts = ["Text one", "Text two"]
        embeddings, cache_hits = await service.generate_embeddings(
            texts,
            db=None,
            cache_enabled=False
        )

        assert len(embeddings) == 2
        assert cache_hits == 0
        mock_model.encode.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.embedding_service.SentenceTransformer')
    async def test_generate_single_embedding(self, mock_transformer, sample_embedding):
        """Test single embedding generation"""
        # Mock the model
        mock_model = Mock()
        mock_model.encode = Mock(return_value=np.array([sample_embedding]))
        mock_transformer.return_value = mock_model

        service = EmbeddingService()
        service.model = mock_model

        text = "Single text"
        embedding = await service.generate_single_embedding(text, cache_enabled=False)

        assert len(embedding) == len(sample_embedding)
