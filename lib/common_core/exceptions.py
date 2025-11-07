"""
Common exceptions for all microservices

Provides a consistent exception hierarchy for error handling across all services.
"""

from typing import Optional, Dict, Any
from fastapi import status


class AuraException(Exception):
    """Base exception for all Aura Audit AI exceptions"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AuraException):
    """Resource not found (404)"""

    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with ID '{identifier}' not found"

        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier}
        )


class ValidationError(AuraException):
    """Validation error (422)"""

    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value

        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class AuthenticationError(AuraException):
    """Authentication failed (401)"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={"www_authenticate": "Bearer"}
        )


class AuthorizationError(AuraException):
    """Authorization/permission denied (403)"""

    def __init__(self, message: str = "Permission denied", required_role: Optional[str] = None):
        details = {}
        if required_role:
            details["required_role"] = required_role

        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class DuplicateError(AuraException):
    """Duplicate resource (409)"""

    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} with {field}='{value}' already exists",
            status_code=status.HTTP_409_CONFLICT,
            details={"resource": resource, "field": field, "value": value}
        )


class ServiceError(AuraException):
    """Service-to-service communication error"""

    def __init__(self, service_name: str, message: str, original_error: Optional[Exception] = None):
        details = {"service": service_name}
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=f"Error communicating with {service_name}: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class RateLimitError(AuraException):
    """Rate limit exceeded (429)"""

    def __init__(self, retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class ConfigurationError(AuraException):
    """Configuration error (500)"""

    def __init__(self, config_key: str, message: str):
        super().__init__(
            message=f"Configuration error for '{config_key}': {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"config_key": config_key}
        )


class DatabaseError(AuraException):
    """Database operation error (500)"""

    def __init__(self, operation: str, message: str, original_error: Optional[Exception] = None):
        details = {"operation": operation}
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=f"Database {operation} failed: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )
