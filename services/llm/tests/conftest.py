"""Test configuration and fixtures for LLM Service"""
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from httpx import AsyncClient

from app.database import Base
from app.main import app, get_db
from app.config import settings
from app.models import KnowledgeDocument, DocumentChunk, DocumentType

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://atlas:atlas_dev_password@localhost:5432/atlas_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database and session"""
    # Create test engine
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    TestSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with TestSessionLocal() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override"""

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_document() -> dict:
    """Sample knowledge document data"""
    return {
        "document_type": "gaap_standard",
        "title": "ASC 606 - Revenue Recognition",
        "standard_code": "ASC 606",
        "source": "FASB",
        "content": """
ASC 606 establishes principles for reporting information about the nature,
amount, timing, and uncertainty of revenue and cash flows from contracts
with customers.

The core principle is that an entity recognizes revenue to depict the
transfer of goods or services to customers at an amount that reflects the
consideration to which the entity expects to be entitled.

The five-step model:
1. Identify the contract with the customer
2. Identify the performance obligations
3. Determine the transaction price
4. Allocate the transaction price
5. Recognize revenue when performance obligations are satisfied
        """,
        "version": "2023",
        "is_active": True
    }


@pytest.fixture
def sample_embedding() -> list:
    """Sample embedding vector (384 dimensions)"""
    import numpy as np
    # Generate random normalized vector
    vec = np.random.randn(384)
    vec = vec / np.linalg.norm(vec)
    return vec.tolist()


@pytest_asyncio.fixture
async def db_document(test_db: AsyncSession, sample_document: dict) -> KnowledgeDocument:
    """Create test knowledge document in database"""
    doc = KnowledgeDocument(**sample_document)
    test_db.add(doc)
    await test_db.commit()
    await test_db.refresh(doc)
    return doc


@pytest_asyncio.fixture
async def db_document_with_chunks(
    test_db: AsyncSession,
    db_document: KnowledgeDocument,
    sample_embedding: list
) -> KnowledgeDocument:
    """Create test document with chunks and embeddings"""
    # Create sample chunks
    chunks_text = [
        "ASC 606 establishes principles for reporting revenue information.",
        "The core principle is recognizing revenue at the amount of consideration expected.",
        "The five-step model includes: identify contract, identify obligations, determine price, allocate price, recognize revenue."
    ]

    for i, chunk_text in enumerate(chunks_text):
        chunk = DocumentChunk(
            document_id=db_document.id,
            chunk_index=i,
            content=chunk_text,
            embedding=sample_embedding,
            token_count=len(chunk_text.split()),
            metadata={"section": f"Section {i+1}"}
        )
        test_db.add(chunk)

    await test_db.commit()
    await test_db.refresh(db_document)
    return db_document


@pytest.fixture
def mock_openai_response() -> dict:
    """Mock OpenAI API response"""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4-turbo-preview",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Revenue should be recognized when control of goods or services transfers to the customer, following ASC 606 guidance."
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 150,
            "completion_tokens": 50,
            "total_tokens": 200
        }
    }
