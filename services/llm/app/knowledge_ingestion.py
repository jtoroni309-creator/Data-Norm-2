"""
Knowledge Base Ingestion System

Ingests and processes authoritative audit knowledge sources:
- PCAOB Standards (AS series)
- AICPA Standards (SAS, SSAE, SSARS series)
- FASB Accounting Standards (ASC)
- SEC regulations
- Prior engagement workpapers
- Industry guidance

Creates vector embeddings for RAG retrieval to provide AI with
CPA-level domain expertise.
"""
import logging
import re
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pathlib import Path
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import (
    KnowledgeDocument,
    DocumentChunk,
    DocumentType,
    DocumentSource
)
from .embedding_service import embedding_service
from .config import settings

logger = logging.getLogger(__name__)


class KnowledgeIngestionPipeline:
    """
    Pipeline for ingesting authoritative audit knowledge

    Process:
    1. Document parsing (PDF, HTML, text)
    2. Text chunking (semantic boundaries)
    3. Embedding generation
    4. Database storage with metadata
    5. Quality validation
    """

    def __init__(self):
        """Initialize ingestion pipeline"""
        self.chunk_size = settings.RAG_CHUNK_SIZE
        self.chunk_overlap = settings.RAG_CHUNK_OVERLAP

    async def ingest_pcaob_standard(
        self,
        db: AsyncSession,
        standard_code: str,
        title: str,
        content: str,
        effective_date: Optional[datetime] = None,
        supersedes: Optional[str] = None
    ) -> UUID:
        """
        Ingest a PCAOB Auditing Standard

        Args:
            db: Database session
            standard_code: Standard code (e.g., "AS 1215")
            title: Standard title
            content: Full standard text
            effective_date: When standard becomes effective
            supersedes: Standard code this supersedes

        Returns:
            Document ID
        """
        logger.info(f"Ingesting PCAOB {standard_code}: {title}")

        # Create document record
        document = KnowledgeDocument(
            id=uuid4(),
            document_type=DocumentType.PCAOB_STANDARD,
            source=DocumentSource.PCAOB,
            title=f"{standard_code} - {title}",
            standard_code=standard_code,
            effective_date=effective_date,
            supersedes=supersedes,
            content_hash=self._compute_hash(content),
            is_active=True
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        # Parse into sections
        sections = self._parse_pcaob_sections(content, standard_code)

        # Chunk and embed each section
        chunk_count = 0
        for section in sections:
            section_title = section.get("title", "")
            section_number = section.get("number", "")
            section_content = section.get("content", "")

            if len(section_content) < 50:  # Skip very short sections
                continue

            # Chunk the section
            chunks = await embedding_service.chunk_text(
                section_content,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )

            # Generate embeddings
            embeddings, _ = await embedding_service.generate_embeddings(
                chunks,
                db=db,
                cache_enabled=True
            )

            # Store chunks
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = DocumentChunk(
                    id=uuid4(),
                    document_id=document.id,
                    chunk_index=chunk_count + i,
                    content=chunk_text,
                    embedding=embedding,
                    metadata={
                        "section_title": section_title,
                        "section_number": section_number,
                        "standard_code": standard_code,
                        "paragraph_count": section_content.count("\n\n") + 1
                    }
                )
                db.add(chunk)

            chunk_count += len(chunks)

        await db.commit()

        logger.info(
            f"Ingested {standard_code}: {chunk_count} chunks created"
        )

        return document.id

    async def ingest_aicpa_standard(
        self,
        db: AsyncSession,
        standard_code: str,  # e.g., "SAS 142"
        title: str,
        content: str,
        au_section: Optional[str] = None,  # e.g., "AU-C 500"
        effective_date: Optional[datetime] = None
    ) -> UUID:
        """
        Ingest an AICPA Auditing Standard

        Args:
            db: Database session
            standard_code: Standard code (e.g., "SAS 142")
            title: Standard title
            content: Full standard text
            au_section: AU-C section number
            effective_date: When standard becomes effective

        Returns:
            Document ID
        """
        logger.info(f"Ingesting AICPA {standard_code}: {title}")

        document = KnowledgeDocument(
            id=uuid4(),
            document_type=DocumentType.AICPA_STANDARD,
            source=DocumentSource.AICPA,
            title=f"{standard_code} - {title}",
            standard_code=standard_code,
            effective_date=effective_date,
            content_hash=self._compute_hash(content),
            metadata={
                "au_section": au_section
            } if au_section else {},
            is_active=True
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        # Process content (similar to PCAOB)
        chunk_count = await self._process_and_store_chunks(
            db=db,
            document=document,
            content=content,
            metadata={"standard_code": standard_code, "au_section": au_section}
        )

        logger.info(
            f"Ingested {standard_code}: {chunk_count} chunks created"
        )

        return document.id

    async def ingest_fasb_asc_topic(
        self,
        db: AsyncSession,
        topic_number: str,  # e.g., "Topic 606"
        title: str,
        content: str,
        subtopic: Optional[str] = None
    ) -> UUID:
        """
        Ingest FASB Accounting Standards Codification topic

        Args:
            db: Database session
            topic_number: ASC topic number
            title: Topic title
            content: Full topic text
            subtopic: Subtopic if applicable

        Returns:
            Document ID
        """
        logger.info(f"Ingesting FASB ASC {topic_number}: {title}")

        document = KnowledgeDocument(
            id=uuid4(),
            document_type=DocumentType.FASB_ASC,
            source=DocumentSource.FASB,
            title=f"ASC {topic_number} - {title}",
            standard_code=f"ASC {topic_number}",
            content_hash=self._compute_hash(content),
            metadata={
                "subtopic": subtopic
            } if subtopic else {},
            is_active=True
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        chunk_count = await self._process_and_store_chunks(
            db=db,
            document=document,
            content=content,
            metadata={"asc_topic": topic_number, "subtopic": subtopic}
        )

        logger.info(
            f"Ingested ASC {topic_number}: {chunk_count} chunks created"
        )

        return document.id

    async def ingest_prior_workpaper(
        self,
        db: AsyncSession,
        engagement_id: UUID,
        workpaper_title: str,
        content: str,
        author_id: UUID,
        workpaper_type: str,
        quality_score: Optional[float] = None
    ) -> UUID:
        """
        Ingest prior engagement workpaper for learning

        High-quality workpapers from completed engagements serve as
        examples for AI to learn from.

        Args:
            db: Database session
            engagement_id: Source engagement
            workpaper_title: Workpaper title
            content: Workpaper content
            author_id: Author (for quality tracking)
            workpaper_type: Type of workpaper
            quality_score: Quality score (0-1) if rated

        Returns:
            Document ID
        """
        logger.info(f"Ingesting prior workpaper: {workpaper_title}")

        document = KnowledgeDocument(
            id=uuid4(),
            document_type=DocumentType.PRIOR_WORKPAPER,
            source=DocumentSource.INTERNAL,
            title=workpaper_title,
            content_hash=self._compute_hash(content),
            metadata={
                "engagement_id": str(engagement_id),
                "author_id": str(author_id),
                "workpaper_type": workpaper_type,
                "quality_score": quality_score
            },
            is_active=quality_score is None or quality_score >= 0.7  # Only use high-quality examples
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        chunk_count = await self._process_and_store_chunks(
            db=db,
            document=document,
            content=content,
            metadata={
                "workpaper_type": workpaper_type,
                "engagement_id": str(engagement_id)
            }
        )

        logger.info(
            f"Ingested workpaper '{workpaper_title}': {chunk_count} chunks created"
        )

        return document.id

    async def ingest_industry_guidance(
        self,
        db: AsyncSession,
        industry: str,  # e.g., "healthcare", "financial_services"
        title: str,
        content: str,
        source_org: str,  # e.g., "AICPA Industry Guides"
        publication_date: Optional[datetime] = None
    ) -> UUID:
        """
        Ingest industry-specific audit guidance

        Args:
            db: Database session
            industry: Industry category
            title: Guide title
            content: Full guide text
            source_org: Source organization
            publication_date: Publication date

        Returns:
            Document ID
        """
        logger.info(f"Ingesting industry guidance for {industry}: {title}")

        document = KnowledgeDocument(
            id=uuid4(),
            document_type=DocumentType.INDUSTRY_GUIDE,
            source=DocumentSource.INDUSTRY_BODY,
            title=title,
            content_hash=self._compute_hash(content),
            metadata={
                "industry": industry,
                "source_org": source_org
            },
            publication_date=publication_date,
            is_active=True
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        chunk_count = await self._process_and_store_chunks(
            db=db,
            document=document,
            content=content,
            metadata={"industry": industry}
        )

        logger.info(
            f"Ingested {industry} guidance: {chunk_count} chunks created"
        )

        return document.id

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content for deduplication"""
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _parse_pcaob_sections(
        self,
        content: str,
        standard_code: str
    ) -> List[Dict[str, str]]:
        """
        Parse PCAOB standard into sections

        PCAOB standards follow structured format:
        .01 Introduction
        .02 Objective
        .03 Definitions
        etc.
        """
        sections = []

        # Find all section headers (format: .XX or .XX-.YY)
        section_pattern = r'\.(\d+(?:-\d+)?)\s+([^\n]+)'
        matches = list(re.finditer(section_pattern, content))

        for i, match in enumerate(matches):
            section_number = match.group(1)
            section_title = match.group(2).strip()

            # Extract content until next section
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section_content = content[start:end].strip()

            sections.append({
                "number": section_number,
                "title": section_title,
                "content": section_content
            })

        logger.debug(f"Parsed {len(sections)} sections from {standard_code}")
        return sections

    async def _process_and_store_chunks(
        self,
        db: AsyncSession,
        document: KnowledgeDocument,
        content: str,
        metadata: Dict[str, Any]
    ) -> int:
        """
        Common logic to chunk, embed, and store document content

        Returns:
            Number of chunks created
        """
        # Chunk the content
        chunks = await embedding_service.chunk_text(
            content,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        # Generate embeddings
        embeddings, _ = await embedding_service.generate_embeddings(
            chunks,
            db=db,
            cache_enabled=True
        )

        # Store chunks
        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["chunk_length"] = len(chunk_text)

            chunk = DocumentChunk(
                id=uuid4(),
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
                embedding=embedding,
                metadata=chunk_metadata
            )
            db.add(chunk)

        await db.commit()
        return len(chunks)

    async def bulk_ingest_standards(
        self,
        db: AsyncSession,
        standards_directory: Path
    ):
        """
        Bulk ingest all standards from a directory

        Directory structure expected:
        standards/
          pcaob/
            AS_1215.txt
            AS_2110.txt
            ...
          aicpa/
            SAS_142.txt
            SAS_145.txt
            ...
          fasb/
            ASC_606.txt
            ...

        Args:
            db: Database session
            standards_directory: Path to standards directory
        """
        logger.info(f"Starting bulk ingestion from {standards_directory}")

        ingestion_tasks = []

        # PCAOB standards
        pcaob_dir = standards_directory / "pcaob"
        if pcaob_dir.exists():
            for file_path in pcaob_dir.glob("*.txt"):
                # Parse filename: AS_1215.txt -> AS 1215
                standard_code = file_path.stem.replace("_", " ")
                content = file_path.read_text(encoding='utf-8')

                # Extract title from first line
                title = content.split('\n')[0].strip()
                content = '\n'.join(content.split('\n')[1:])  # Remove title line

                task = self.ingest_pcaob_standard(
                    db=db,
                    standard_code=standard_code,
                    title=title,
                    content=content
                )
                ingestion_tasks.append(task)

        # Process tasks (limit concurrency to avoid overwhelming DB)
        batch_size = 5
        for i in range(0, len(ingestion_tasks), batch_size):
            batch = ingestion_tasks[i:i + batch_size]
            await asyncio.gather(*batch)

        logger.info(f"Bulk ingestion complete: {len(ingestion_tasks)} documents processed")

    async def refresh_document(
        self,
        db: AsyncSession,
        document_id: UUID,
        new_content: str
    ):
        """
        Refresh a document with updated content

        Marks old chunks inactive and creates new ones.

        Args:
            db: Database session
            document_id: Document to refresh
            new_content: Updated content
        """
        logger.info(f"Refreshing document {document_id}")

        # Get document
        result = await db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
        )
        document = result.scalar_one()

        # Mark old chunks inactive
        from sqlalchemy import update
        await db.execute(
            update(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .values(is_active=False)
        )

        # Update document hash
        document.content_hash = self._compute_hash(new_content)
        document.updated_at = datetime.utcnow()

        # Create new chunks
        chunk_count = await self._process_and_store_chunks(
            db=db,
            document=document,
            content=new_content,
            metadata=document.metadata or {}
        )

        await db.commit()

        logger.info(f"Refreshed document {document_id}: {chunk_count} new chunks created")


# Global ingestion pipeline instance
knowledge_pipeline = KnowledgeIngestionPipeline()
