"""
Test configuration and fixtures.
"""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import BankAccount, FeatureFlag, Transaction

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestingSessionLocal() as session:
        yield session

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator:
    """Create test client."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def customer_id() -> str:
    """Create test customer ID."""
    return str(uuid4())


@pytest_asyncio.fixture
async def feature_flag(
    db_session: AsyncSession,
    customer_id: str
) -> FeatureFlag:
    """Create test feature flag."""
    feature_flag = FeatureFlag(
        customer_id=customer_id,
        is_enabled=True,
        real_time_monitoring=True,
        ml_detection=True,
        rule_based_detection=True,
        anomaly_detection=True,
    )

    db_session.add(feature_flag)
    await db_session.commit()
    await db_session.refresh(feature_flag)

    return feature_flag


@pytest_asyncio.fixture
async def bank_account(
    db_session: AsyncSession,
    customer_id: str
) -> BankAccount:
    """Create test bank account."""
    from app.main import encrypt_token

    account = BankAccount(
        customer_id=customer_id,
        plaid_item_id="test_item_id",
        plaid_access_token_encrypted=encrypt_token("test_access_token"),
        plaid_account_id="test_account_id",
        account_name="Test Checking",
        account_mask="1234",
        account_type="checking",
        institution_name="Test Bank",
    )

    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def sample_transaction(
    db_session: AsyncSession,
    bank_account: BankAccount
) -> Transaction:
    """Create sample transaction."""
    from datetime import datetime
    from decimal import Decimal

    transaction = Transaction(
        bank_account_id=bank_account.id,
        plaid_transaction_id="test_txn_123",
        transaction_date=datetime.utcnow(),
        amount=Decimal("100.50"),
        description="Test Purchase",
        merchant_name="Test Merchant",
        fraud_score=0.25,
        is_flagged=False,
    )

    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    return transaction


@pytest.fixture
def mock_plaid_response():
    """Mock Plaid API responses."""
    return {
        "link_token": "link-sandbox-test-token",
        "expiration": "2024-12-31T23:59:59Z",
        "access_token": "access-sandbox-test-token",
        "item_id": "test_item_id",
        "accounts": [
            {
                "account_id": "test_account_id",
                "name": "Test Checking",
                "mask": "1234",
                "type": "depository",
                "subtype": "checking",
                "balances": {
                    "current": 1000.00,
                    "available": 950.00,
                }
            }
        ],
        "transactions": [
            {
                "transaction_id": "txn_123",
                "account_id": "test_account_id",
                "amount": 50.00,
                "date": "2024-11-06",
                "name": "Test Purchase",
                "merchant_name": "Test Merchant",
                "category": ["Shopping", "Retail"],
                "payment_channel": "in store",
                "location": {
                    "city": "San Francisco",
                    "region": "CA",
                    "country": "US",
                }
            }
        ]
    }
