"""
Secure Cookie-Based Authentication

Provides httpOnly, Secure cookie management for JWT tokens to prevent XSS attacks.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Response, Cookie, HTTPException, status


def set_auth_cookie(
    response: Response,
    token: str,
    expires_in_minutes: int = 480  # 8 hours default
) -> None:
    """
    Set secure authentication cookie with JWT token.

    Args:
        response: FastAPI Response object
        token: JWT token to store
        expires_in_minutes: Token expiration time in minutes

    Security features:
        - httponly=True: Prevents JavaScript access (XSS protection)
        - secure=True: HTTPS only (production)
        - samesite="lax": CSRF protection
        - domain: Can be set for cross-subdomain auth
    """
    # Determine if we're in production
    environment = os.getenv("ENVIRONMENT", "development").lower()
    is_production = environment in ["production", "prod", "staging"]

    # Calculate expiration
    expires = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

    # Get cookie domain (for cross-subdomain authentication)
    cookie_domain = os.getenv("COOKIE_DOMAIN", None)

    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,  # Prevents JavaScript access
        secure=is_production,  # HTTPS only in production
        samesite="lax",  # CSRF protection
        max_age=expires_in_minutes * 60,  # in seconds
        expires=expires,
        domain=cookie_domain,
        path="/"
    )


def clear_auth_cookie(response: Response) -> None:
    """
    Clear authentication cookie on logout.

    Args:
        response: FastAPI Response object
    """
    cookie_domain = os.getenv("COOKIE_DOMAIN", None)

    response.delete_cookie(
        key="auth_token",
        domain=cookie_domain,
        path="/"
    )


def generate_csrf_token() -> str:
    """
    Generate a cryptographically secure CSRF token.

    Returns:
        str: URL-safe CSRF token
    """
    return secrets.token_urlsafe(32)


def set_csrf_cookie(response: Response, csrf_token: str) -> None:
    """
    Set CSRF token cookie.

    Args:
        response: FastAPI Response object
        csrf_token: CSRF token to store

    Note: CSRF cookie is NOT httpOnly so JavaScript can read it
    and send it in request headers.
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    is_production = environment in ["production", "prod", "staging"]

    cookie_domain = os.getenv("COOKIE_DOMAIN", None)

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,  # JavaScript needs to read this
        secure=is_production,
        samesite="lax",
        max_age=3600 * 8,  # 8 hours
        domain=cookie_domain,
        path="/"
    )


def verify_csrf_token(
    csrf_header: Optional[str] = None,
    csrf_cookie: Optional[str] = None
) -> None:
    """
    Verify CSRF token matches between header and cookie.

    Args:
        csrf_header: CSRF token from X-CSRF-Token header
        csrf_cookie: CSRF token from cookie

    Raises:
        HTTPException: If CSRF tokens don't match or are missing
    """
    if not csrf_header or not csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing"
        )

    if csrf_header != csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )
