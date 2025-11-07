"""
Aura Audit AI - Common Core Library

Shared utilities, middleware, and patterns for all microservices.

This library provides:
- Common exceptions and error handling
- Standard middleware (CORS, logging, error handlers)
- Common Pydantic schemas (health checks, pagination)
- Database utilities and patterns
- Authentication dependencies
- Logging configuration
"""

from .exceptions import (
    AuraException,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    DuplicateError,
    ServiceError,
)
from .schemas import (
    HealthResponse,
    PaginatedResponse,
    ErrorResponse,
    SuccessResponse,
)
from .middleware import (
    setup_cors_middleware,
    setup_error_handlers,
    setup_logging_middleware,
)
from .logging_config import setup_logging
from .dependencies import (
    get_current_user_id,
    get_current_user_from_token,
    require_authenticated,
)

__version__ = "1.0.0"

__all__ = [
    # Exceptions
    "AuraException",
    "NotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "DuplicateError",
    "ServiceError",
    # Schemas
    "HealthResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    # Middleware
    "setup_cors_middleware",
    "setup_error_handlers",
    "setup_logging_middleware",
    # Logging
    "setup_logging",
    # Dependencies
    "get_current_user_id",
    "get_current_user_from_token",
    "require_authenticated",
]
