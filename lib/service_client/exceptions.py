"""Custom exceptions for service communication"""


class ServiceError(Exception):
    """Base exception for service errors"""
    pass


class ServiceUnavailableError(ServiceError):
    """Service is unavailable (circuit breaker open or connection error)"""
    pass


class ServiceTimeoutError(ServiceError):
    """Service request timed out"""
    pass


class ServiceAuthenticationError(ServiceError):
    """Authentication failed when calling service"""
    pass


class ServiceNotFoundError(ServiceError):
    """Service not found in registry"""
    pass
