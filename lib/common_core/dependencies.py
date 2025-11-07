"""
Common FastAPI dependencies for authentication and authorization

Provides reusable dependency injection patterns for:
- JWT token validation
- User authentication
- Role-based access control
"""

import logging
from typing import Optional, List
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from .exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_secret: Optional[str] = None,
    jwt_algorithm: str = "HS256"
) -> dict:
    """
    Extract and validate JWT token, return user payload

    Args:
        credentials: HTTP Authorization header with Bearer token
        jwt_secret: JWT secret key (should be passed from service config)
        jwt_algorithm: JWT algorithm (default: HS256)

    Returns:
        dict: User payload from JWT token

    Raises:
        AuthenticationError: If token is invalid or expired

    Usage in service:
        from lib.common_core import get_current_user_from_token
        from .config import settings

        @app.get("/protected")
        async def protected_route(
            user: dict = Depends(lambda: get_current_user_from_token(
                jwt_secret=settings.JWT_SECRET
            ))
        ):
            return {"user_id": user["sub"]}
    """
    if not jwt_secret:
        raise AuthenticationError("JWT secret not configured")

    try:
        token = credentials.credentials

        # Decode and validate token
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=[jwt_algorithm]
        )

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token: missing user ID")

        logger.debug(f"Authenticated user: {user_id}")

        return payload

    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise AuthenticationError(f"Could not validate credentials: {str(e)}")
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise AuthenticationError("Authentication failed")


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_secret: Optional[str] = None,
    jwt_algorithm: str = "HS256"
) -> UUID:
    """
    Get current user ID from JWT token

    Args:
        credentials: HTTP Authorization header with Bearer token
        jwt_secret: JWT secret key
        jwt_algorithm: JWT algorithm

    Returns:
        UUID: User ID

    Raises:
        AuthenticationError: If token is invalid

    Usage:
        @app.get("/my-data")
        async def get_my_data(
            user_id: UUID = Depends(lambda: get_current_user_id(
                jwt_secret=settings.JWT_SECRET
            ))
        ):
            return {"user_id": str(user_id)}
    """
    payload = await get_current_user_from_token(
        credentials=credentials,
        jwt_secret=jwt_secret,
        jwt_algorithm=jwt_algorithm
    )

    try:
        return UUID(payload["sub"])
    except (KeyError, ValueError) as e:
        raise AuthenticationError(f"Invalid user ID in token: {e}")


def require_authenticated(
    jwt_secret: Optional[str] = None,
    jwt_algorithm: str = "HS256"
):
    """
    Dependency factory for requiring authentication

    Args:
        jwt_secret: JWT secret key
        jwt_algorithm: JWT algorithm

    Returns:
        Dependency function that validates authentication

    Usage:
        from lib.common_core import require_authenticated
        from .config import settings

        auth_required = require_authenticated(jwt_secret=settings.JWT_SECRET)

        @app.get("/protected")
        async def protected_route(user: dict = Depends(auth_required)):
            return {"user_id": user["sub"]}
    """
    async def _require_authenticated(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        return await get_current_user_from_token(
            credentials=credentials,
            jwt_secret=jwt_secret,
            jwt_algorithm=jwt_algorithm
        )

    return _require_authenticated


def require_roles(
    allowed_roles: List[str],
    jwt_secret: Optional[str] = None,
    jwt_algorithm: str = "HS256"
):
    """
    Dependency factory for role-based access control

    Args:
        allowed_roles: List of allowed roles (e.g., ["partner", "manager"])
        jwt_secret: JWT secret key
        jwt_algorithm: JWT algorithm

    Returns:
        Dependency function that validates role authorization

    Raises:
        AuthorizationError: If user doesn't have required role

    Usage:
        from lib.common_core import require_roles
        from .config import settings

        partner_or_manager = require_roles(
            allowed_roles=["partner", "manager"],
            jwt_secret=settings.JWT_SECRET
        )

        @app.post("/engagements")
        async def create_engagement(user: dict = Depends(partner_or_manager)):
            return {"message": "Engagement created"}
    """
    async def _require_roles(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        # Authenticate user
        user = await get_current_user_from_token(
            credentials=credentials,
            jwt_secret=jwt_secret,
            jwt_algorithm=jwt_algorithm
        )

        # Check role
        user_role = user.get("role")
        if not user_role:
            raise AuthorizationError("User role not found in token")

        if user_role not in allowed_roles:
            raise AuthorizationError(
                message=f"Insufficient permissions. Required roles: {allowed_roles}",
                required_role=", ".join(allowed_roles)
            )

        logger.debug(f"User {user['sub']} authorized with role: {user_role}")

        return user

    return _require_roles


def require_permission(
    permission: str,
    jwt_secret: Optional[str] = None,
    jwt_algorithm: str = "HS256"
):
    """
    Dependency factory for permission-based access control

    Args:
        permission: Required permission (e.g., "engagements:create")
        jwt_secret: JWT secret key
        jwt_algorithm: JWT algorithm

    Returns:
        Dependency function that validates permission

    Raises:
        AuthorizationError: If user doesn't have required permission

    Usage:
        from lib.common_core import require_permission
        from .config import settings

        can_create_engagements = require_permission(
            permission="engagements:create",
            jwt_secret=settings.JWT_SECRET
        )

        @app.post("/engagements")
        async def create_engagement(user: dict = Depends(can_create_engagements)):
            return {"message": "Engagement created"}
    """
    async def _require_permission(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        # Authenticate user
        user = await get_current_user_from_token(
            credentials=credentials,
            jwt_secret=jwt_secret,
            jwt_algorithm=jwt_algorithm
        )

        # Check permissions
        user_permissions = user.get("permissions", [])
        if permission not in user_permissions:
            raise AuthorizationError(
                message=f"Missing required permission: {permission}",
                required_role=permission
            )

        logger.debug(f"User {user['sub']} authorized with permission: {permission}")

        return user

    return _require_permission
