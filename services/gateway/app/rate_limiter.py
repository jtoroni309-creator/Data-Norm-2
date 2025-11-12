"""
Redis-backed rate limiter for API Gateway

Provides distributed rate limiting that works across multiple gateway instances.
Uses Redis as a centralized storage backend for request counts.
"""

import os
from typing import Callable
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


def get_client_identifier(request: Request) -> str:
    """
    Extract client identifier for rate limiting.

    Priority order:
    1. Authorization token (if present) - identifies authenticated users
    2. X-Forwarded-For header (if behind proxy)
    3. Client IP address

    Returns:
        str: Client identifier for rate limiting
    """
    # Try to get auth token first (for authenticated users)
    auth_header = request.headers.get("authorization", "")
    if auth_header and auth_header.startswith("Bearer "):
        # Use first 32 chars of token as identifier
        token = auth_header.replace("Bearer ", "")
        return f"token:{token[:32]}"

    # Try X-Forwarded-For (if behind proxy/load balancer)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Get the first IP in the chain (original client)
        client_ip = forwarded_for.split(",")[0].strip()
        return f"ip:{client_ip}"

    # Fall back to direct client IP
    if request.client:
        return f"ip:{request.client.host}"

    return "ip:unknown"


# Initialize Redis-backed rate limiter
limiter = Limiter(
    key_func=get_client_identifier,
    storage_uri=os.getenv("REDIS_URL", "redis://localhost:6379"),
    default_limits=["120/minute"],  # Default: 120 requests per minute
    enabled=True,
)
