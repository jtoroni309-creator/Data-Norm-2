"""Test configuration and fixtures for Reporting Service"""
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
from app.models import ReportTemplate, Report, ReportType, TemplateType

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
def sample_template() -> dict:
    """Sample report template data"""
    return {
        "name": "Standard Audit Report",
        "description": "Standard audit report template",
        "template_type": "system",
        "report_type": "audit_report",
        "html_content": """
        <html>
        <head><title>{{ title }}</title></head>
        <body>
            <h1>{{ title }}</h1>
            <p>Engagement: {{ engagement_name }}</p>
            <p>Fiscal Year: {{ fiscal_year }}</p>
            <div>{{ content }}</div>
        </body>
        </html>
        """,
        "css_content": "body { font-family: Arial; }",
        "version": "1.0"
    }


@pytest.fixture
def sample_report() -> dict:
    """Sample report data"""
    return {
        "engagement_id": str(uuid4()),
        "report_type": "audit_report",
        "title": "Annual Audit Report 2024",
        "description": "Comprehensive audit report for fiscal year 2024",
        "report_data": {
            "engagement_name": "ABC Corporation",
            "fiscal_year": "2024",
            "content": "<p>This is the audit report content.</p>"
        },
        "fiscal_year": "2024",
        "has_watermark": True
    }


@pytest_asyncio.fixture
async def db_template(test_db: AsyncSession, sample_template: dict) -> ReportTemplate:
    """Create test template in database"""
    template = ReportTemplate(**sample_template, created_by=uuid4())
    test_db.add(template)
    await test_db.commit()
    await test_db.refresh(template)
    return template


@pytest_asyncio.fixture
async def db_report(test_db: AsyncSession, sample_report: dict, db_template: ReportTemplate) -> Report:
    """Create test report in database"""
    report_data = sample_report.copy()
    report_data['template_id'] = db_template.id
    report = Report(**report_data, created_by=uuid4())
    test_db.add(report)
    await test_db.commit()
    await test_db.refresh(report)
    return report
