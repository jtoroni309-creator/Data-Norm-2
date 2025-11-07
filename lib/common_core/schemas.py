"""
Common Pydantic schemas for all microservices

Provides standardized response models for:
- Health checks
- Pagination
- Error responses
- Success responses
"""

from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


# ===================================
# Health Check Schemas
# ===================================

class HealthResponse(BaseModel):
    """Standard health check response"""

    status: str = Field(..., description="Health status (healthy, degraded, unhealthy)")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current timestamp")
    dependencies: Optional[Dict[str, str]] = Field(None, description="Dependency health status")

    model_config = {"json_schema_extra": {
        "example": {
            "status": "healthy",
            "service": "identity",
            "version": "1.0.0",
            "timestamp": "2025-01-01T00:00:00",
            "dependencies": {
                "database": "healthy",
                "redis": "healthy"
            }
        }
    }}


# ===================================
# Error Response Schemas
# ===================================

class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request correlation ID")

    model_config = {"json_schema_extra": {
        "example": {
            "error": "NotFoundError",
            "message": "User with ID '123' not found",
            "details": {"resource": "User", "identifier": "123"},
            "timestamp": "2025-01-01T00:00:00",
            "request_id": "abc123"
        }
    }}


# ===================================
# Success Response Schemas
# ===================================

class SuccessResponse(BaseModel):
    """Standard success response for operations without data"""

    success: bool = Field(True, description="Operation success flag")
    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    model_config = {"json_schema_extra": {
        "example": {
            "success": True,
            "message": "User deactivated successfully",
            "timestamp": "2025-01-01T00:00:00"
        }
    }}


# ===================================
# Pagination Schemas
# ===================================

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response"""

    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items across all pages")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int = 1,
        page_size: int = 50
    ) -> "PaginatedResponse[T]":
        """
        Create paginated response from items and total count

        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number (1-indexed)
            page_size: Number of items per page

        Returns:
            PaginatedResponse with calculated pagination metadata
        """
        total_pages = (total + page_size - 1) // page_size  # Ceiling division

        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class PaginationParams(BaseModel):
    """Standard pagination query parameters"""

    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(50, ge=1, le=1000, description="Items per page (max 1000)")

    @property
    def skip(self) -> int:
        """Calculate SQLAlchemy offset"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get SQLAlchemy limit"""
        return self.page_size


# ===================================
# Service Info Schemas
# ===================================

class ServiceInfo(BaseModel):
    """Service information response"""

    name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    description: str = Field(..., description="Service description")
    docs_url: str = Field("/docs", description="API documentation URL")
    health_url: str = Field("/health", description="Health check endpoint")
    features: Optional[List[str]] = Field(None, description="List of service features")

    model_config = {"json_schema_extra": {
        "example": {
            "name": "identity",
            "version": "1.0.0",
            "description": "Authentication and authorization service",
            "docs_url": "/docs",
            "health_url": "/health",
            "features": ["JWT authentication", "RBAC", "User management"]
        }
    }}


# ===================================
# Audit/Metadata Schemas
# ===================================

class AuditMetadata(BaseModel):
    """Common audit metadata for entities"""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User ID who created the entity")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the entity")

    model_config = {
        "json_schema_extra": {
            "example": {
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-02T00:00:00",
                "created_by": "user-123",
                "updated_by": "user-456"
            }
        }
    }


# ===================================
# Batch Operation Schemas
# ===================================

class BatchOperationResult(BaseModel):
    """Result of a batch operation"""

    total: int = Field(..., description="Total items processed")
    succeeded: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="List of errors encountered")
    duration_ms: Optional[float] = Field(None, description="Operation duration in milliseconds")

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total == 0:
            return 0.0
        return (self.succeeded / self.total) * 100

    model_config = {"json_schema_extra": {
        "example": {
            "total": 100,
            "succeeded": 98,
            "failed": 2,
            "errors": [
                {"item_id": "123", "error": "Validation failed"},
                {"item_id": "456", "error": "Duplicate entry"}
            ],
            "duration_ms": 1234.56
        }
    }}
