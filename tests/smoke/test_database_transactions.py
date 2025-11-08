"""
Database Transaction Smoke Tests

Tests database connectivity, transaction handling, and data persistence.
These tests verify that the database layer is functioning correctly after deployment.
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime, date
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_database_connectivity(db_session: AsyncSession):
    """
    Verify basic database connectivity.

    Impact: Ensures database is accessible and responding to queries.
    """
    result = await db_session.execute(text("SELECT 1 as test"))
    row = result.fetchone()
    assert row[0] == 1, "Database connection failed"


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_database_version(db_session: AsyncSession):
    """
    Verify PostgreSQL version is correct.

    Impact: Ensures correct database version is deployed.
    """
    result = await db_session.execute(text("SELECT version()"))
    version = result.fetchone()[0]
    assert "PostgreSQL" in version, "Not a PostgreSQL database"
    # Verify PostgreSQL 15+
    assert "PostgreSQL 15" in version or "PostgreSQL 16" in version, \
        f"Expected PostgreSQL 15+, got: {version}"


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_pgvector_extension(db_session: AsyncSession):
    """
    Verify pgvector extension is installed.

    Impact: Ensures vector similarity search for LLM features is available.
    """
    result = await db_session.execute(
        text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
    )
    row = result.fetchone()
    assert row is not None, "pgvector extension not installed"
    assert row[0] == "vector", "pgvector extension not found"


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_transaction_commit(db_session: AsyncSession):
    """
    Verify transaction commit works correctly.

    Impact: Ensures data persistence and ACID properties.
    """
    test_id = str(uuid4())
    test_table = "smoke_test_transactions"

    # Create test table
    await db_session.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {test_table} (
            id TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """))
    await db_session.commit()

    # Insert test data
    await db_session.execute(
        text(f"INSERT INTO {test_table} (id, value) VALUES (:id, :value)"),
        {"id": test_id, "value": "test_commit"}
    )
    await db_session.commit()

    # Verify data persisted
    result = await db_session.execute(
        text(f"SELECT value FROM {test_table} WHERE id = :id"),
        {"id": test_id}
    )
    row = result.fetchone()
    assert row is not None, "Transaction commit failed - data not persisted"
    assert row[0] == "test_commit", "Data mismatch after commit"

    # Cleanup
    await db_session.execute(text(f"DROP TABLE {test_table}"))
    await db_session.commit()


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_transaction_rollback(db_session: AsyncSession):
    """
    Verify transaction rollback works correctly.

    Impact: Ensures data integrity and error recovery.
    """
    test_id = str(uuid4())
    test_table = "smoke_test_rollback"

    # Create test table
    await db_session.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {test_table} (
            id TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """))
    await db_session.commit()

    try:
        # Start a new transaction
        await db_session.execute(
            text(f"INSERT INTO {test_table} (id, value) VALUES (:id, :value)"),
            {"id": test_id, "value": "test_rollback"}
        )

        # Force rollback
        await db_session.rollback()

        # Verify data was NOT persisted
        result = await db_session.execute(
            text(f"SELECT COUNT(*) FROM {test_table} WHERE id = :id"),
            {"id": test_id}
        )
        count = result.scalar()
        assert count == 0, "Transaction rollback failed - data was persisted"

    finally:
        # Cleanup
        await db_session.execute(text(f"DROP TABLE IF EXISTS {test_table}"))
        await db_session.commit()


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_concurrent_transactions(db_session: AsyncSession, db_engine):
    """
    Verify concurrent transaction handling.

    Impact: Ensures database can handle multiple simultaneous operations.
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker

    test_table = "smoke_test_concurrent"

    # Create test table
    await db_session.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {test_table} (
            id SERIAL PRIMARY KEY,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """))
    await db_session.commit()

    # Create multiple sessions for concurrent operations
    AsyncSessionLocal = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def insert_value(session_maker, value: str):
        """Insert a value in a separate transaction."""
        async with session_maker() as session:
            await session.execute(
                text(f"INSERT INTO {test_table} (value) VALUES (:value)"),
                {"value": value}
            )
            await session.commit()

    # Run concurrent inserts
    import asyncio
    tasks = [
        insert_value(AsyncSessionLocal, f"concurrent_{i}")
        for i in range(5)
    ]
    await asyncio.gather(*tasks)

    # Verify all inserts succeeded
    result = await db_session.execute(
        text(f"SELECT COUNT(*) FROM {test_table} WHERE value LIKE 'concurrent_%'")
    )
    count = result.scalar()
    assert count == 5, f"Expected 5 concurrent inserts, got {count}"

    # Cleanup
    await db_session.execute(text(f"DROP TABLE {test_table}"))
    await db_session.commit()


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_constraint_enforcement(db_session: AsyncSession):
    """
    Verify database constraints are enforced.

    Impact: Ensures data integrity rules are active.
    """
    test_table = "smoke_test_constraints"

    # Create table with constraints
    await db_session.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {test_table} (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            age INTEGER CHECK (age >= 0)
        )
    """))
    await db_session.commit()

    test_id = str(uuid4())

    try:
        # Test NOT NULL constraint
        with pytest.raises(Exception):  # Will raise IntegrityError
            await db_session.execute(
                text(f"INSERT INTO {test_table} (id, email, age) VALUES (:id, NULL, 25)"),
                {"id": test_id}
            )
            await db_session.commit()
        await db_session.rollback()

        # Test CHECK constraint
        with pytest.raises(Exception):  # Will raise IntegrityError
            await db_session.execute(
                text(f"INSERT INTO {test_table} (id, email, age) VALUES (:id, :email, -5)"),
                {"id": test_id, "email": "test@example.com"}
            )
            await db_session.commit()
        await db_session.rollback()

        # Test UNIQUE constraint
        await db_session.execute(
            text(f"INSERT INTO {test_table} (id, email, age) VALUES (:id, :email, 30)"),
            {"id": str(uuid4()), "email": "unique@example.com"}
        )
        await db_session.commit()

        with pytest.raises(Exception):  # Will raise IntegrityError for duplicate
            await db_session.execute(
                text(f"INSERT INTO {test_table} (id, email, age) VALUES (:id, :email, 30)"),
                {"id": str(uuid4()), "email": "unique@example.com"}
            )
            await db_session.commit()
        await db_session.rollback()

    finally:
        # Cleanup
        await db_session.execute(text(f"DROP TABLE IF EXISTS {test_table}"))
        await db_session.commit()


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_connection_pool(db_engine):
    """
    Verify database connection pooling is working.

    Impact: Ensures efficient resource utilization under load.
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker

    AsyncSessionLocal = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Test multiple sequential connections
    for i in range(10):
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT :i as iteration"), {"i": i})
            row = result.fetchone()
            assert row[0] == i, f"Connection pool failed at iteration {i}"

    # Verify pool stats
    pool = db_engine.pool
    assert pool.size() > 0, "Connection pool not initialized"


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_row_level_security_context(db_session: AsyncSession):
    """
    Verify RLS context can be set correctly.

    Impact: Ensures multi-tenant data isolation works.
    """
    test_user_id = str(uuid4())

    # Set RLS context
    await db_session.execute(
        text("SELECT set_config('app.current_user_id', :user_id, false)"),
        {"user_id": test_user_id}
    )

    # Verify context was set
    result = await db_session.execute(
        text("SELECT current_setting('app.current_user_id', true)")
    )
    current_user = result.scalar()
    assert current_user == test_user_id, "RLS context not set correctly"


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_database_performance(db_session: AsyncSession):
    """
    Verify basic database performance metrics.

    Impact: Catches performance regressions after deployment.
    """
    import time

    # Test simple query performance
    start = time.time()
    await db_session.execute(text("SELECT 1"))
    duration = time.time() - start
    assert duration < 0.1, f"Simple query took {duration}s (expected < 0.1s)"

    # Test indexed query performance (using pg_class which is indexed)
    start = time.time()
    await db_session.execute(
        text("SELECT relname FROM pg_class WHERE relname = 'pg_class'")
    )
    duration = time.time() - start
    assert duration < 0.1, f"Indexed query took {duration}s (expected < 0.1s)"


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.asyncio
async def test_json_support(db_session: AsyncSession):
    """
    Verify JSONB support is working.

    Impact: Ensures JSON data storage for flexible schemas works.
    """
    test_table = "smoke_test_json"

    await db_session.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {test_table} (
            id TEXT PRIMARY KEY,
            data JSONB NOT NULL
        )
    """))
    await db_session.commit()

    try:
        test_id = str(uuid4())
        test_data = {"key": "value", "nested": {"foo": "bar"}, "array": [1, 2, 3]}

        # Insert JSON data
        await db_session.execute(
            text(f"INSERT INTO {test_table} (id, data) VALUES (:id, :data)"),
            {"id": test_id, "data": test_data}
        )
        await db_session.commit()

        # Query JSON data
        result = await db_session.execute(
            text(f"SELECT data FROM {test_table} WHERE id = :id"),
            {"id": test_id}
        )
        row = result.fetchone()
        assert row[0] == test_data, "JSONB data mismatch"

        # Test JSON operators
        result = await db_session.execute(
            text(f"SELECT data->>'key' as key FROM {test_table} WHERE id = :id"),
            {"id": test_id}
        )
        key_value = result.scalar()
        assert key_value == "value", "JSONB operator failed"

    finally:
        await db_session.execute(text(f"DROP TABLE IF EXISTS {test_table}"))
        await db_session.commit()
