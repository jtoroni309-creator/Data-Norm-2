"""
Financial Analysis Service - Main Application

This is the main FastAPI application for the Financial Analysis service.
It provides comprehensive financial analysis, audit procedures, and
compliance features for CPA firms performing assurance engagements.

Features:
- EDGAR/SEC data integration
- AI-powered financial analysis and audit opinions
- Multi-tenant permission system with RBAC
- Stripe payment processing
- Jira issue tracking
- Disclosure note generation
- Electronic confirmations
- Engagement management
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from .config import settings
from .database import engine, Base, async_session
from .permission_middleware import PermissionMiddleware

# Import routers
from .client_portal_api import router as client_router
from .admin_portal_api import router as admin_router
from .jira_api import router as jira_router
from .stripe_api import router as stripe_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Financial Analysis Service...")

    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

        # Log configuration
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
        logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")

    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Financial Analysis Service...")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="Aura Audit AI - Financial Analysis Service",
    description="""
    ## Financial Analysis Service

    Comprehensive financial analysis and audit procedures for CPA firms.

    ### Key Features

    **Financial Analysis**
    - EDGAR/SEC data integration
    - 30+ financial ratio calculations
    - Multi-period trend analysis
    - Industry benchmarking
    - Red flag detection
    - Materiality calculation
    - Going concern assessment
    - AI-powered audit opinion recommendations

    **Audit Procedures**
    - Electronic confirmations
    - Disclosure note generation with AI
    - Engagement management (Audit, Review, Compilation)
    - Workpaper organization
    - Quality control gates

    **Enterprise Features**
    - Multi-tenant architecture with RBAC
    - Row-level security (RLS)
    - Stripe payment integration
    - Jira issue tracking
    - Comprehensive audit trails

    ### API Organization

    - `/api/v1/*` - Client portal endpoints
    - `/admin/*` - Admin portal endpoints
    - `/api/jira/*` - Jira integration
    - `/api/stripe/*` - Stripe payment integration
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Security Middleware (SOC 2 compliance - rate limiting, IP filtering, CSRF protection)
try:
    import sys
    sys.path.insert(0, '/home/user/Data-Norm-2/services')
    from security.app import SecurityMiddleware, AuditLogService

    # Initialize audit logging
    audit_log_service = AuditLogService()

    # Add security middleware
    app.add_middleware(
        SecurityMiddleware,
        audit_log_service=audit_log_service,
        enable_rate_limiting=True,
        enable_ip_filtering=False,
        enable_csrf_protection=True
    )
    logger.info("Security middleware enabled (SOC 2 compliant)")
except ImportError as e:
    logger.warning(f"Security middleware not available: {e}")

# Permission Middleware (for RBAC enforcement)
app.add_middleware(PermissionMiddleware)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed information."""
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Request validation failed. Please check your input."
        }
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors gracefully."""
    logger.error(f"Database error on {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "A database error occurred. Please try again later.",
            "error_type": type(exc).__name__
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "An unexpected error occurred. Our team has been notified.",
            "error_type": type(exc).__name__
        }
    )


# ============================================================================
# ROUTERS
# ============================================================================

# Client Portal API (Customer-facing endpoints)
app.include_router(
    client_router,
    prefix="/api/v1",
    tags=["Client Portal"]
)

# Admin Portal API (Admin dashboard endpoints)
app.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin Portal"]
)

# Jira Integration API
app.include_router(
    jira_router,
    tags=["Jira Integration"]
)

# Stripe Payment Integration API
app.include_router(
    stripe_router,
    tags=["Stripe Integration"]
)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring systems.
    """
    return {
        "status": "healthy",
        "service": "financial-analysis",
        "version": "1.0.0"
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check - verifies database connectivity.
    """
    try:
        async with async_session() as session:
            await session.execute("SELECT 1")
        return {
            "status": "ready",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "service": "Aura Audit AI - Financial Analysis Service",
        "version": "1.0.0",
        "description": "Comprehensive financial analysis and audit procedures for CPA firms",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "client_portal": "/api/v1",
            "admin_portal": "/admin",
            "jira": "/api/jira",
            "stripe": "/api/stripe"
        },
        "health": {
            "health_check": "/health",
            "readiness": "/health/ready"
        }
    }


# ============================================================================
# STARTUP MESSAGE
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("="*80)
    logger.info("Starting Financial Analysis Service in development mode")
    logger.info("="*80)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
