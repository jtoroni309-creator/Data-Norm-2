"""
Database configuration for Security Service
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from .config import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL if hasattr(settings, 'DATABASE_URL') else "postgresql+asyncpg://localhost/aura_security",
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative base for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session.

    Usage in FastAPI:
        @app.get("/")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            # Use db session
            pass
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables.

    Call this during application startup.
    """
    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from .compliance_models import (
            SOC2Control,
            ComplianceEvidence,
            ControlTest,
            CompliancePeriod,
            SecurityIncident,
            VulnerabilityAssessment,
            AccessReview,
        )

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db():
    """
    Dispose database engine.

    Call this during application shutdown.
    """
    await engine.dispose()
