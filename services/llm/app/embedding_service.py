"""Embedding generation service using sentence-transformers"""
import hashlib
import logging
import time
from typing import List, Tuple, Optional
import numpy as np

from sentence_transformers import SentenceTransformer
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import EmbeddingCache

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.model: Optional[SentenceTransformer] = None
        self.dimension = settings.EMBEDDING_DIMENSION

    def load_model(self):
        """Load the embedding model (lazy loading)"""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")

    def _compute_text_hash(self, text: str) -> str:
        """Compute SHA256 hash of text for caching"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    async def _get_cached_embedding(
        self,
        db: AsyncSession,
        text: str
    ) -> Optional[List[float]]:
        """Retrieve cached embedding if exists"""
        text_hash = self._compute_text_hash(text)

        query = select(EmbeddingCache).where(
            EmbeddingCache.text_hash == text_hash,
            EmbeddingCache.model_name == self.model_name
        )
        result = await db.execute(query)
        cache_entry = result.scalar_one_or_none()

        if cache_entry:
            # Update access statistics
            cache_entry.access_count += 1
            cache_entry.last_accessed = func.now()
            await db.commit()

            logger.debug(f"Cache hit for text hash: {text_hash}")
            return cache_entry.embedding.tolist()

        return None

    async def _cache_embedding(
        self,
        db: AsyncSession,
        text: str,
        embedding: List[float]
    ):
        """Cache embedding for future use"""
        text_hash = self._compute_text_hash(text)

        cache_entry = EmbeddingCache(
            text_hash=text_hash,
            text=text,
            embedding=embedding,
            model_name=self.model_name
        )

        db.add(cache_entry)
        try:
            await db.commit()
            logger.debug(f"Cached embedding for text hash: {text_hash}")
        except Exception as e:
            await db.rollback()
            logger.warning(f"Failed to cache embedding: {e}")

    async def generate_embeddings(
        self,
        texts: List[str],
        db: Optional[AsyncSession] = None,
        cache_enabled: bool = True,
    ) -> Tuple[List[List[float]], int]:
        """
        Generate embeddings for a list of texts

        Args:
            texts: List of text strings to embed
            db: Database session for caching
            cache_enabled: Whether to use embedding cache

        Returns:
            Tuple of (embeddings list, cache hits count)
        """
        self.load_model()

        embeddings = []
        cache_hits = 0
        texts_to_embed = []
        text_indices = []

        # Check cache for existing embeddings
        if cache_enabled and db:
            for i, text in enumerate(texts):
                cached = await self._get_cached_embedding(db, text)
                if cached:
                    embeddings.append(cached)
                    cache_hits += 1
                else:
                    texts_to_embed.append(text)
                    text_indices.append(i)
                    embeddings.append(None)  # Placeholder
        else:
            texts_to_embed = texts
            text_indices = list(range(len(texts)))
            embeddings = [None] * len(texts)

        # Generate embeddings for uncached texts
        if texts_to_embed:
            logger.info(f"Generating embeddings for {len(texts_to_embed)} texts")

            # Generate in batches
            batch_size = settings.EMBEDDING_BATCH_SIZE
            new_embeddings = []

            for i in range(0, len(texts_to_embed), batch_size):
                batch = texts_to_embed[i:i + batch_size]
                batch_embeddings = self.model.encode(
                    batch,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
                new_embeddings.extend(batch_embeddings.tolist())

            # Place new embeddings in correct positions
            for idx, embedding in zip(text_indices, new_embeddings):
                embeddings[idx] = embedding

            # Cache new embeddings
            if cache_enabled and db:
                for text, embedding in zip(texts_to_embed, new_embeddings):
                    await self._cache_embedding(db, text, embedding)

        logger.info(
            f"Generated {len(texts)} embeddings "
            f"({cache_hits} cache hits, {len(texts_to_embed)} new)"
        )

        return embeddings, cache_hits

    async def generate_single_embedding(
        self,
        text: str,
        db: Optional[AsyncSession] = None,
        cache_enabled: bool = True,
    ) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text string to embed
            db: Database session for caching
            cache_enabled: Whether to use embedding cache

        Returns:
            Embedding vector as list of floats
        """
        embeddings, _ = await self.generate_embeddings(
            [text],
            db=db,
            cache_enabled=cache_enabled
        )
        return embeddings[0]

    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0 to 1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        return float(similarity)

    async def chunk_text(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> List[str]:
        """
        Split text into chunks for embedding

        Args:
            text: Full text to chunk
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or settings.RAG_CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.RAG_CHUNK_OVERLAP

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence or paragraph boundary
            if end < len(text):
                # Look for paragraph break
                paragraph_break = text.rfind('\n\n', start, end)
                if paragraph_break > start:
                    end = paragraph_break
                else:
                    # Look for sentence break
                    sentence_break = max(
                        text.rfind('. ', start, end),
                        text.rfind('! ', start, end),
                        text.rfind('? ', start, end)
                    )
                    if sentence_break > start:
                        end = sentence_break + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move to next chunk with overlap
            start = end - chunk_overlap if end < len(text) else end

        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks


# Global embedding service instance
embedding_service = EmbeddingService()
