"""
Smoke Test Configuration and Fixtures

Provides shared fixtures and configuration for deployment smoke tests.
These tests verify critical integration points after deployment.
"""

import asyncio
import os
from typing import AsyncGenerator, Dict, Any
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from lib.event_bus.event_bus import EventBus


# Environment Configuration
TEST_DATABASE_URL = os.getenv(
    "SMOKE_TEST_DATABASE_URL",
    "postgresql+asyncpg://atlas:atlas_dev_password@localhost:5432/atlas_test"
)
TEST_REDIS_URL = os.getenv("SMOKE_TEST_REDIS_URL", "redis://localhost:6379/1")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
SERVICE_TIMEOUT = int(os.getenv("SMOKE_TEST_TIMEOUT", "30"))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session-scoped async fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Create database engine for smoke tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session with transaction rollback."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture(scope="session")
async def redis_client() -> AsyncGenerator[Redis, None]:
    """Create Redis client for smoke tests."""
    client = Redis.from_url(
        TEST_REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )
    try:
        await client.ping()
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture
async def event_bus(redis_client: Redis) -> AsyncGenerator[EventBus, None]:
    """Create EventBus instance for testing event flows."""
    bus = EventBus(redis_client)
    yield bus
    # Cleanup: unsubscribe from all channels
    # EventBus should handle cleanup internally


@pytest_asyncio.fixture
async def http_client() -> AsyncGenerator[AsyncClient, None]:
    """Create HTTP client for service-to-service tests."""
    async with AsyncClient(
        base_url=GATEWAY_URL,
        timeout=SERVICE_TIMEOUT,
        follow_redirects=True,
    ) as client:
        yield client


@pytest_asyncio.fixture
async def test_user_token(http_client: AsyncClient) -> str:
    """
    Create test user and return auth token.

    This fixture assumes the identity service is running and accessible.
    """
    # Register a test user
    user_data = {
        "email": f"smoke-test-{uuid4()}@example.com",
        "password": "SmokeTest123!",
        "full_name": "Smoke Test User",
        "firm_name": "Smoke Test Firm",
    }

    register_response = await http_client.post(
        "/api/identity/auth/register",
        json=user_data,
    )

    if register_response.status_code not in (200, 201):
        pytest.skip(f"Cannot create test user: {register_response.text}")

    # Login to get token
    login_response = await http_client.post(
        "/api/identity/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )

    if login_response.status_code != 200:
        pytest.skip(f"Cannot login test user: {login_response.text}")

    token_data = login_response.json()
    return token_data["access_token"]


@pytest.fixture
def auth_headers(test_user_token: str) -> Dict[str, str]:
    """Create authorization headers with test user token."""
    return {
        "Authorization": f"Bearer {test_user_token}",
        "Content-Type": "application/json",
    }


@pytest_asyncio.fixture
async def test_engagement_id(http_client: AsyncClient, auth_headers: Dict[str, str]) -> str:
    """
    Create a test engagement and return its ID.

    This fixture creates a minimal engagement for integration testing.
    """
    from datetime import date

    engagement_data = {
        "name": f"Smoke Test Engagement {uuid4()}",
        "client_name": "Smoke Test Client",
        "engagement_type": "audit",
        "fiscal_year_end": date.today().isoformat(),
    }

    response = await http_client.post(
        "/api/engagement/engagements",
        json=engagement_data,
        headers=auth_headers,
    )

    if response.status_code not in (200, 201):
        pytest.skip(f"Cannot create test engagement: {response.text}")

    engagement = response.json()
    return engagement["id"]


# Test markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "smoke: deployment smoke tests for critical integration points"
    )
    config.addinivalue_line(
        "markers", "database: tests that require database connectivity"
    )
    config.addinivalue_line(
        "markers", "redis: tests that require Redis connectivity"
    )
    config.addinivalue_line(
        "markers", "service: tests that require service-to-service communication"
    )
