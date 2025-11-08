"""
Database connection and session management
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from .config import settings
from typing import AsyncGenerator
from uuid import UUID

Base = declarative_base()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session

    Usage:
        @app.post("/items")
        async def create_item(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session


async def set_rls_context(db: AsyncSession, organization_id: UUID) -> None:
    """
    Set Row-Level Security context for multi-tenancy

    Args:
        db: Database session
        organization_id: Organization UUID

    Usage:
        await set_rls_context(db, user.organization_id)
    """
    await db.execute(
        text("SET app.current_organization_id = :org_id"),
        {"org_id": str(organization_id)},
    )
