"""
Permission Middleware - FastAPI Integration

Provides decorators and dependencies for enforcing permissions in API endpoints.

Usage Examples:

```python
# Require specific permission
@router.get("/engagements")
@require_permission(PermissionScope.ENGAGEMENT_READ)
async def list_engagements(current_user: User = Depends(get_current_user)):
    ...

# Automatic tenant isolation
@router.get("/clients")
async def list_clients(
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    # tenant is automatically set based on current_user
    ...

# Role-based access
@router.post("/users")
@require_role(UserRole.FIRM_ADMIN)
async def create_user(current_user: User = Depends(get_current_user)):
    ...
```
"""

from functools import wraps
from typing import Callable, Optional
from uuid import UUID
import logging

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db
from .permission_service import PermissionService
from .permissions_models import (
    PermissionScope,
    Tenant,
    User,
    UserRole,
)

# Configure logging
logger = logging.getLogger(__name__)


# HTTP Bearer token authentication
security = HTTPBearer()


# ============================================================================
# DEPENDENCIES
# ============================================================================


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the current authenticated user from JWT token.

    Production-ready implementation that:
    1. Verifies JWT signature
    2. Checks token expiration
    3. Extracts user_id from token
    4. Loads user from database
    5. Validates user is active

    Args:
        credentials: HTTP Bearer token
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials

        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract user_id from 'sub' claim
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("JWT token missing 'sub' claim")
            raise credentials_exception

    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception

    # Fetch user from database
    try:
        result = await db.execute(
            select(User).where(
                and_(
                    User.id == UUID(user_id),
                    User.is_active == True,
                    User.deleted_at == None
                )
            )
        )
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning(f"User not found or inactive: {user_id}")
            raise credentials_exception

        # Update last login timestamp
        # Note: This is done asynchronously without committing to avoid
        # slowing down every request. Consider using a background task
        # or periodic batch update for better performance.
        # user.last_login_at = datetime.utcnow()
        # await db.commit()

        return user

    except Exception as e:
        logger.error(f"Database error while fetching user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )


async def get_current_tenant(
    current_user: User = Depends(get_current_user),
) -> Tenant:
    """
    Get the current user's tenant.

    Automatically enforces tenant isolation by returning the
    tenant associated with the current user.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user's tenant

    Raises:
        HTTPException: If user has no tenant (e.g., platform admin)
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no associated tenant",
        )

    # In production, load from database
    # For now, return tenant_id for reference
    return current_user.tenant


async def get_permission_service(
    db: AsyncSession = Depends(get_db),
) -> PermissionService:
    """
    Get permission service instance.

    Args:
        db: Database session

    Returns:
        PermissionService instance
    """
    return PermissionService(db)


# ============================================================================
# DECORATORS
# ============================================================================


def require_permission(scope: PermissionScope, tenant_id_param: Optional[str] = None):
    """
    Decorator to require a specific permission for an endpoint.

    Args:
        scope: Required permission scope
        tenant_id_param: Optional parameter name containing tenant_id

    Usage:
        @router.get("/engagements")
        @require_permission(PermissionScope.ENGAGEMENT_READ)
        async def list_engagements(current_user: User = Depends(get_current_user)):
            ...

        @router.post("/engagements/{tenant_id}/create")
        @require_permission(PermissionScope.ENGAGEMENT_CREATE, tenant_id_param="tenant_id")
        async def create_engagement(
            tenant_id: UUID,
            current_user: User = Depends(get_current_user),
        ):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Get database session from kwargs
            db = kwargs.get("db")
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not found",
                )

            # Get tenant_id from parameters if specified
            tenant_id = None
            if tenant_id_param and tenant_id_param in kwargs:
                tenant_id = kwargs[tenant_id_param]
            elif current_user.tenant_id:
                tenant_id = current_user.tenant_id

            # Get permission service
            permission_service = PermissionService(db)

            # Check permission
            has_permission = await permission_service.check_permission(
                user_id=current_user.id,
                scope=scope,
                tenant_id=tenant_id,
            )

            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {scope.value}",
                )

            # Call original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_role(*allowed_roles: UserRole):
    """
    Decorator to require specific roles for an endpoint.

    Args:
        *allowed_roles: Allowed user roles

    Usage:
        @router.post("/users")
        @require_role(UserRole.PLATFORM_ADMIN, UserRole.FIRM_ADMIN)
        async def create_user(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check role
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {', '.join(r.value for r in allowed_roles)}",
                )

            # Call original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def enforce_tenant_isolation(tenant_id_param: str = "tenant_id"):
    """
    Decorator to enforce tenant isolation.

    Ensures that users can only access resources in their own tenant
    (except platform admins who can access all tenants).

    Args:
        tenant_id_param: Parameter name containing the tenant_id to check

    Usage:
        @router.get("/tenants/{tenant_id}/clients")
        @enforce_tenant_isolation(tenant_id_param="tenant_id")
        async def list_clients(
            tenant_id: UUID,
            current_user: User = Depends(get_current_user),
        ):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Platform admins bypass tenant isolation
            if current_user.role == UserRole.PLATFORM_ADMIN:
                return await func(*args, **kwargs)

            # Get tenant_id from parameters
            requested_tenant_id = kwargs.get(tenant_id_param)
            if not requested_tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing parameter: {tenant_id_param}",
                )

            # Check tenant isolation
            if current_user.tenant_id != requested_tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Cannot access other tenant's data",
                )

            # Call original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def check_tenant_access(user: User, tenant_id: UUID) -> bool:
    """
    Check if user has access to a specific tenant.

    Args:
        user: User to check
        tenant_id: Tenant to access

    Returns:
        True if user can access tenant
    """
    # Platform admins can access all tenants
    if user.role == UserRole.PLATFORM_ADMIN:
        return True

    # Others can only access their own tenant
    return user.tenant_id == tenant_id


def get_accessible_tenant_ids(user: User) -> Optional[list[UUID]]:
    """
    Get list of tenant IDs the user can access.

    Args:
        user: User to check

    Returns:
        List of tenant IDs (None means all tenants for platform admins)
    """
    # Platform admins can access all tenants
    if user.role == UserRole.PLATFORM_ADMIN:
        return None  # None means "all"

    # Others can only access their own tenant
    if user.tenant_id:
        return [user.tenant_id]

    return []


# ============================================================================
# EXAMPLE API ROUTER
# ============================================================================

"""
Example FastAPI router using the permission system:

from fastapi import APIRouter, Depends
from uuid import UUID

router = APIRouter()


@router.post("/platform/tenants")
@require_role(UserRole.PLATFORM_ADMIN)
async def create_tenant(
    firm_name: str,
    firm_ein: str,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
):
    '''Create a new tenant (Platform Admin only).'''
    return await permission_service.create_tenant(
        firm_name=firm_name,
        firm_ein=firm_ein,
        created_by_user_id=current_user.id,
    )


@router.post("/tenants/{tenant_id}/users")
@enforce_tenant_isolation(tenant_id_param="tenant_id")
@require_permission(PermissionScope.FIRM_USERS)
async def create_user(
    tenant_id: UUID,
    email: str,
    role: UserRole,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
):
    '''Create a new user in the tenant (Firm Admin only).'''
    return await permission_service.create_user(
        email=email,
        role=role,
        tenant_id=tenant_id,
        created_by_user_id=current_user.id,
    )


@router.post("/tenants/{tenant_id}/invitations")
@enforce_tenant_isolation(tenant_id_param="tenant_id")
@require_permission(PermissionScope.FIRM_USERS)
async def invite_user(
    tenant_id: UUID,
    email: str,
    role: UserRole,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
):
    '''Invite a new user to the tenant.'''
    return await permission_service.invite_user(
        inviting_user_id=current_user.id,
        email=email,
        role=role,
        tenant_id=tenant_id,
    )


@router.post("/tenants/{tenant_id}/clients/grant-access")
@enforce_tenant_isolation(tenant_id_param="tenant_id")
@require_permission(PermissionScope.FIRM_CLIENTS)
async def grant_client_access(
    tenant_id: UUID,
    client_email: str,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
):
    '''Grant a client access to the portal.'''
    return await permission_service.grant_client_access(
        granting_user_id=current_user.id,
        client_email=client_email,
        tenant_id=tenant_id,
    )


@router.get("/engagements")
@require_permission(PermissionScope.ENGAGEMENT_READ)
async def list_engagements(
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    '''List engagements for the current tenant.'''
    # Automatically filtered to current tenant
    # Implementation here...
    pass


@router.get("/audit-logs")
@require_role(UserRole.PLATFORM_ADMIN, UserRole.FIRM_ADMIN)
async def get_audit_logs(
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
):
    '''Get audit logs (Admin only).'''
    return await permission_service.get_audit_logs(
        user_id=current_user.id,
    )
"""
