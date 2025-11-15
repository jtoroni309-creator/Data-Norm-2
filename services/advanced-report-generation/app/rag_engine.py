"""
Advanced RAG (Retrieval-Augmented Generation) Engine 2.0

Features:
- Hybrid search (vector + keyword)
- Cross-encoder reranking
- Reciprocal Rank Fusion
- Citation extraction
- Source attribution
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import re

from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery
import openai
from loguru import logger

from .config import settings


@dataclass
class RetrievedDocument:
    """Document retrieved from RAG"""
    document_id: str
    content: str
    title: str
    source: str
    score: float
    metadata: Dict


class AdvancedRAGEngine:
    """
    Advanced RAG 2.0 for audit work paper retrieval

    Techniques:
    - Hybrid search combining vector similarity and BM25
    - Cross-encoder reranking for better relevance
    - Reciprocal Rank Fusion (RRF) for merging results
    - Citation extraction and validation
    """

    def __init__(self):
        # Azure Cognitive Search client
        self.search_client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_INDEX_NAME,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY)
        )

        # OpenAI for embeddings
        openai.api_type = "azure"
        openai.api_base = settings.AZURE_OPENAI_ENDPOINT
        openai.api_key = settings.AZURE_OPENAI_API_KEY
        openai.api_version = settings.AZURE_OPENAI_API_VERSION

    async def retrieve_with_reranking(
        self,
        query: str,
        engagement_id: str,
        top_k: int = 10,
        rerank_top_k: int = 3,
    ) -> List[RetrievedDocument]:
        """
        Retrieve documents with hybrid search and reranking

        Steps:
        1. Vector search (semantic)
        2. Keyword search (BM25)
        3. Merge with Reciprocal Rank Fusion
        4. Rerank with cross-encoder
        5. Return top_k results
        """

        # Step 1: Vector search
        vector_results = await self._vector_search(query, engagement_id, top_k)

        # Step 2: Keyword search
        keyword_results = await self._keyword_search(query, engagement_id, top_k)

        # Step 3: Merge with RRF
        merged_results = self._reciprocal_rank_fusion(
            vector_results,
            keyword_results,
            k=60  # RRF constant
        )

        # Step 4: Rerank with cross-encoder
        reranked_results = await self._rerank_with_cross_encoder(
            query,
            merged_results[:top_k],
            rerank_top_k
        )

        return reranked_results

    async def _vector_search(
        self,
        query: str,
        engagement_id: str,
        top_k: int
    ) -> List[RetrievedDocument]:
        """Perform vector similarity search"""

        # Get query embedding
        query_embedding = await self._get_embedding(query)

        # Create vectorized query
        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=top_k,
            fields="content_vector"
        )

        # Search
        results = await self.search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            filter=f"engagement_id eq '{engagement_id}'",
            top=top_k
        )

        documents = []
        async for result in results:
            documents.append(RetrievedDocument(
                document_id=result["id"],
                content=result["content"],
                title=result.get("title", ""),
                source=result.get("source", ""),
                score=result["@search.score"],
                metadata=result.get("metadata", {})
            ))

        return documents

    async def _keyword_search(
        self,
        query: str,
        engagement_id: str,
        top_k: int
    ) -> List[RetrievedDocument]:
        """Perform BM25 keyword search"""

        results = await self.search_client.search(
            search_text=query,
            filter=f"engagement_id eq '{engagement_id}'",
            top=top_k,
            query_type="full"
        )

        documents = []
        async for result in results:
            documents.append(RetrievedDocument(
                document_id=result["id"],
                content=result["content"],
                title=result.get("title", ""),
                source=result.get("source", ""),
                score=result["@search.score"],
                metadata=result.get("metadata", {})
            ))

        return documents

    def _reciprocal_rank_fusion(
        self,
        list1: List[RetrievedDocument],
        list2: List[RetrievedDocument],
        k: int = 60
    ) -> List[RetrievedDocument]:
        """
        Merge two ranked lists using Reciprocal Rank Fusion

        RRF(d) = sum over all rankings r: 1 / (k + r(d))

        Benefits:
        - No need to normalize scores
        - Works well even when score scales differ
        - Simple and effective
        """

        # Build document scores
        doc_scores = {}

        # Add scores from list1
        for rank, doc in enumerate(list1, start=1):
            doc_scores[doc.document_id] = doc_scores.get(doc.document_id, 0) + (1.0 / (k + rank))

        # Add scores from list2
        for rank, doc in enumerate(list2, start=1):
            doc_scores[doc.document_id] = doc_scores.get(doc.document_id, 0) + (1.0 / (k + rank))

        # Create map of doc_id -> document
        doc_map = {}
        for doc in list1 + list2:
            if doc.document_id not in doc_map:
                doc_map[doc.document_id] = doc

        # Sort by RRF score
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return documents with updated scores
        merged = []
        for doc_id, score in sorted_docs:
            doc = doc_map[doc_id]
            merged.append(RetrievedDocument(
                document_id=doc.document_id,
                content=doc.content,
                title=doc.title,
                source=doc.source,
                score=score,
                metadata=doc.metadata
            ))

        return merged

    async def _rerank_with_cross_encoder(
        self,
        query: str,
        documents: List[RetrievedDocument],
        top_k: int
    ) -> List[RetrievedDocument]:
        """
        Rerank documents using GPT-4 as a cross-encoder

        Cross-encoders jointly encode query and document for better relevance

        Note: In production, use a dedicated cross-encoder model like MS MARCO
        """

        # For each document, score relevance
        scored_docs = []

        for doc in documents:
            # Use GPT-4 to score relevance (0-10)
            relevance_score = await self._score_relevance(query, doc.content)

            scored_docs.append((doc, relevance_score))

        # Sort by relevance score
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Return top_k with updated scores
        reranked = []
        for doc, score in scored_docs[:top_k]:
            reranked.append(RetrievedDocument(
                document_id=doc.document_id,
                content=doc.content,
                title=doc.title,
                source=doc.source,
                score=score,
                metadata=doc.metadata
            ))

        return reranked

    async def _score_relevance(self, query: str, document: str) -> float:
        """Score relevance of document to query using GPT-4"""

        prompt = f"""Rate the relevance of this document to the query on a scale of 0-10.

Query: {query}

Document: {document[:500]}...

Respond with ONLY a number from 0-10, where:
- 10 = Highly relevant, directly answers the query
- 5 = Somewhat relevant
- 0 = Not relevant at all

Score:"""

        try:
            response = await openai.ChatCompletion.acreate(
                engine=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=5
            )

            score_text = response.choices[0].message.content.strip()
            score = float(score_text)

            return max(0.0, min(10.0, score))  # Clamp to [0, 10]

        except Exception as e:
            logger.warning(f"Relevance scoring failed: {e}")
            return 5.0  # Default to medium relevance

    async def _get_embedding(self, text: str) -> List[float]:
        """Get text embedding from Azure OpenAI"""

        response = await openai.Embedding.acreate(
            engine=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            input=text
        )

        return response.data[0].embedding

    def extract_citations(self, text: str) -> List[Dict[str, str]]:
        """
        Extract citations from generated text

        Citation formats:
        - [Work Paper A-1]
        - [AS 3101.08]
        - [AU-C 700.15]
        - [ASC 606-10-25-1]
        """

        citations = []

        # Pattern for work papers
        wp_pattern = r'\[(?:Work Paper |WP )([A-Z]-\d+)\]'
        for match in re.finditer(wp_pattern, text):
            citations.append({
                "type": "work_paper",
                "reference": match.group(1),
                "text": match.group(0)
            })

        # Pattern for PCAOB AS standards
        as_pattern = r'\[AS (\d+)(?:\.(\d+))?\]'
        for match in re.finditer(as_pattern, text):
            citations.append({
                "type": "pcaob_standard",
                "standard": f"AS {match.group(1)}",
                "paragraph": match.group(2) if match.group(2) else None,
                "text": match.group(0)
            })

        # Pattern for AICPA AU-C standards
        auc_pattern = r'\[AU-C (\d+)(?:\.(\d+))?\]'
        for match in re.finditer(auc_pattern, text):
            citations.append({
                "type": "aicpa_standard",
                "standard": f"AU-C {match.group(1)}",
                "paragraph": match.group(2) if match.group(2) else None,
                "text": match.group(0)
            })

        # Pattern for ASC topics
        asc_pattern = r'\[ASC (\d+-\d+-\d+-\d+)\]'
        for match in re.finditer(asc_pattern, text):
            citations.append({
                "type": "asc_topic",
                "topic": match.group(1),
                "text": match.group(0)
            })

        return citations

    async def search(
        self,
        query: str,
        engagement_id: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Simple search interface (for backward compatibility)
        """

        results = await self.retrieve_with_reranking(
            query=query,
            engagement_id=engagement_id,
            top_k=top_k,
            rerank_top_k=top_k
        )

        return [
            {
                "reference": result.source,
                "title": result.title,
                "summary": result.content[:200],
                "score": result.score
            }
            for result in results
        ]


# Global RAG engine instance
rag_engine = AdvancedRAGEngine()
