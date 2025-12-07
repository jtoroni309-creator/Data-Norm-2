"""
Database connection and session management
Async SQLAlchemy with PostgreSQL
"""
import logging
from typing import AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from .config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    echo=settings.DEBUG,
    future=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get database session

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database (create tables)
    In production, use Alembic migrations instead
    """
    async with engine.begin() as conn:
        # Create schema
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS soc_copilot"))

        # In production, run migrations instead:
        # await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized")


async def set_rls_context(db: AsyncSession, user_id: UUID):
    """
    Set Row-Level Security (RLS) context for current session

    Args:
        db: Database session
        user_id: Current user ID for RLS policy enforcement

    Usage:
        await set_rls_context(db, current_user_id)
    """
    if settings.ENABLE_RLS:
        # Use set_config() function instead of SET command for asyncpg compatibility
        await db.execute(
            text("SELECT set_config('app.current_user_id', :user_id, false)"),
            {"user_id": str(user_id)}
        )


async def close_db():
    """Close database connections on shutdown"""
    await engine.dispose()
    logger.info("Database connections closed")
