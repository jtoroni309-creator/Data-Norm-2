"""Database connection and session management"""
import logging
from typing import AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from .config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Enable connection health checks
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def set_rls_context(db: AsyncSession, user_id: UUID) -> None:
    """
    Set Row-Level Security context for PostgreSQL

    This sets the current user ID in PostgreSQL session variables,
    which RLS policies use to filter data by engagement team membership.

    Args:
        db: Database session
        user_id: Current user UUID

    Example RLS Policy:
        CREATE POLICY engagement_access_policy ON engagements
        FOR ALL USING (
            id IN (
                SELECT engagement_id FROM engagement_team_members
                WHERE user_id = current_setting('app.current_user_id')::UUID
            )
        );
    """
    if settings.RLS_ENABLED:
        try:
            await db.execute(
                text("SELECT set_config('app.current_user_id', :user_id, false)"),
                {"user_id": str(user_id)}
            )
            logger.debug(f"Set RLS context for user: {user_id}")
        except Exception as e:
            logger.warning(f"Failed to set RLS context: {e}")
            # Don't fail the request if RLS context setting fails
            pass


async def init_db() -> None:
    """
    Initialize database tables

    Note: In production, use Alembic migrations instead.
    This is provided for development/testing convenience.
    """
    async with engine.begin() as conn:
        # Import models to register them with Base
        from . import models  # noqa: F401

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")


async def close_db() -> None:
    """Close database engine and connections"""
    await engine.dispose()
    logger.info("Database connections closed")
