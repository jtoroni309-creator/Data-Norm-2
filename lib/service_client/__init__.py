"""
Service-to-Service Communication Library

Provides:
- Service discovery and registration
- Circuit breaker pattern
- Automatic retries with exponential backoff
- Request/response logging
- Authentication token propagation
"""

from .client import ServiceClient, ServiceRegistry
from .exceptions import ServiceError, ServiceUnavailableError, ServiceTimeoutError

__all__ = [
    "ServiceClient",
    "ServiceRegistry",
    "ServiceError",
    "ServiceUnavailableError",
    "ServiceTimeoutError",
]
