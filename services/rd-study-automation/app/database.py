"""
Database connection and session management for R&D Study Automation Service.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from uuid import UUID
from typing import AsyncGenerator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    Ensures proper cleanup after request.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def set_rls_context(session: AsyncSession, user_id: UUID, firm_id: UUID = None):
    """
    Set Row-Level Security context for the current session.
    This ensures users can only access data they're authorized to see.
    """
    if not settings.RLS_ENABLED:
        return

    try:
        await session.execute(
            text("SET LOCAL app.current_user_id = :user_id"),
            {"user_id": str(user_id)}
        )
        if firm_id:
            await session.execute(
                text("SET LOCAL app.current_firm_id = :firm_id"),
                {"firm_id": str(firm_id)}
            )
        logger.debug(f"RLS context set for user {user_id}, firm {firm_id}")
    except Exception as e:
        logger.error(f"Failed to set RLS context: {e}")
        raise


async def init_db():
    """
    Initialize database tables and extensions.
    Should be called on startup.
    """
    async with engine.begin() as conn:
        # Ensure schema exists
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS atlas"))

        # Ensure required extensions
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))

        # pgvector is optional - only available on certain PostgreSQL configurations
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"pgvector\""))
            logger.info("pgvector extension enabled")
        except Exception as e:
            logger.warning(f"pgvector extension not available (vector search disabled): {e}")

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized successfully")


async def close_db():
    """
    Close database connections.
    Should be called on shutdown.
    """
    await engine.dispose()
    logger.info("Database connections closed")
