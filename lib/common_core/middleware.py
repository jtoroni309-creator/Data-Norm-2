"""
Common FastAPI middleware for all microservices

Provides:
- CORS configuration
- Error handling
- Request logging
- Response timing
"""

import time
import logging
from typing import List
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .exceptions import AuraException
from .schemas import ErrorResponse

logger = logging.getLogger(__name__)


def setup_cors_middleware(
    app: FastAPI,
    allowed_origins: List[str] = None,
    allow_credentials: bool = True,
    allow_methods: List[str] = None,
    allow_headers: List[str] = None
):
    """
    Configure CORS middleware for FastAPI app

    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins (default: ["*"])
        allow_credentials: Allow credentials (default: True)
        allow_methods: Allowed HTTP methods (default: ["*"])
        allow_headers: Allowed headers (default: ["*"])
    """
    if allowed_origins is None:
        allowed_origins = ["*"]
    if allow_methods is None:
        allow_methods = ["*"]
    if allow_headers is None:
        allow_headers = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
    )

    logger.info(f"CORS middleware configured with origins: {allowed_origins}")


def setup_error_handlers(app: FastAPI):
    """
    Configure error handlers for FastAPI app

    Handles:
    - AuraException (custom exceptions)
    - HTTPException (FastAPI/Starlette)
    - RequestValidationError (Pydantic validation)
    - Generic exceptions
    """

    @app.exception_handler(AuraException)
    async def aura_exception_handler(request: Request, exc: AuraException):
        """Handle custom Aura exceptions"""
        logger.error(
            f"AuraException: {exc.message} | "
            f"Status: {exc.status_code} | "
            f"Path: {request.url.path} | "
            f"Details: {exc.details}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.message,
                details=exc.details,
            ).model_dump()
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.error(
            f"HTTPException: {exc.detail} | "
            f"Status: {exc.status_code} | "
            f"Path: {request.url.path}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="HTTPException",
                message=str(exc.detail),
            ).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors"""
        errors = exc.errors()
        logger.error(
            f"ValidationError: {len(errors)} error(s) | "
            f"Path: {request.url.path} | "
            f"Errors: {errors}"
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="ValidationError",
                message="Request validation failed",
                details={"errors": errors}
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions"""
        logger.exception(
            f"Unhandled exception: {str(exc)} | "
            f"Path: {request.url.path}",
            exc_info=exc
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="InternalServerError",
                message="An unexpected error occurred",
                details={"error_type": exc.__class__.__name__}
            ).model_dump()
        )

    logger.info("Error handlers configured")


def setup_logging_middleware(app: FastAPI):
    """
    Configure request logging and timing middleware

    Logs:
    - Request method, path, query params
    - Response status code
    - Request processing time
    """

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests with timing"""
        start_time = time.time()

        # Log request
        logger.info(
            f"→ {request.method} {request.url.path} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        logger.info(
            f"← {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration_ms:.2f}ms"
        )

        # Add timing header
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

        return response

    logger.info("Logging middleware configured")


def setup_all_middleware(app: FastAPI, allowed_origins: List[str] = None):
    """
    Configure all common middleware for FastAPI app

    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed CORS origins
    """
    setup_cors_middleware(app, allowed_origins=allowed_origins)
    setup_error_handlers(app)
    setup_logging_middleware(app)

    logger.info("All middleware configured successfully")
