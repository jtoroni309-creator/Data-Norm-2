"""
Authentication dependencies using ServiceClient

Calls identity service to validate JWT tokens and get user information
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Header, HTTPException, status
from pydantic import BaseModel

# Import service client (assuming it's installed via requirements.txt)
try:
    from service_client import ServiceClient, ServiceUnavailableError, ServiceAuthenticationError
except ImportError:
    # Fallback for local development
    import sys
    sys.path.append('/app/../../../lib')
    from service_client import ServiceClient, ServiceUnavailableError, ServiceAuthenticationError

logger = logging.getLogger(__name__)


class User(BaseModel):
    """User model from identity service"""
    id: UUID
    email: str
    role: str
    organization_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None


async def get_current_user(
    authorization: str = Header(None)
) -> User:
    """
    Extract and validate JWT token by calling identity service

    Args:
        authorization: Authorization header with Bearer token

    Returns:
        User object with user details

    Raises:
        HTTPException: If token is missing, invalid, or service is unavailable
    """

    # Check if authorization header exists
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]

    # Call identity service to validate token
    try:
        identity_client = ServiceClient(
            service_name="identity",
            timeout=10.0,
            auth_token=token
        )

        # Call /auth/me endpoint to get current user
        user_data = await identity_client.get("/auth/me")

        # Convert to User model
        return User(**user_data)

    except ServiceAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except ServiceUnavailableError:
        logger.error("Identity service unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service temporarily unavailable"
        )

    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating authentication"
        )


async def get_current_user_id(authorization: str = Header(None)) -> UUID:
    """
    Convenience function to get only the user ID

    Args:
        authorization: Authorization header with Bearer token

    Returns:
        User ID (UUID)
    """
    user = await get_current_user(authorization)
    return user.id
