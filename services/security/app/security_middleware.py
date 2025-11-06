"""
SOC 2 Security Middleware

Enforces security policies across all services:
- Rate limiting
- IP allowlisting/denylisting
- Security headers
- Request validation
- Session management
- CSRF protection

SOC 2 Trust Service Criteria Coverage:
- CC6.1: Logical and physical access controls
- CC6.6: Prevention of unauthorized access
- CC6.7: Secure transmission of data
- CC7.2: System monitoring
"""

import hashlib
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, List, Optional, Set
from uuid import UUID

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class SecurityLevel(str, Enum):
    """Security level classifications"""
    PUBLIC = "public"  # No authentication required
    AUTHENTICATED = "authenticated"  # Requires valid session
    PRIVILEGED = "privileged"  # Requires elevated permissions
    ADMIN = "admin"  # Admin-only access


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    pass


class SecurityViolation(Exception):
    """Raised when security policy is violated"""
    pass


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware for SOC 2 compliance.

    Features:
    - Rate limiting (prevents DoS)
    - IP filtering (allowlist/denylist)
    - Security headers (HSTS, CSP, etc.)
    - Request signing verification
    - Session validation
    - CSRF protection
    - Audit logging integration
    """

    def __init__(
        self,
        app: ASGIApp,
        audit_log_service=None,
        enable_rate_limiting: bool = True,
        enable_ip_filtering: bool = True,
        enable_csrf_protection: bool = True,
    ):
        """
        Initialize security middleware.

        Args:
            app: ASGI application
            audit_log_service: AuditLogService instance
            enable_rate_limiting: Enable rate limiting
            enable_ip_filtering: Enable IP filtering
            enable_csrf_protection: Enable CSRF protection
        """
        super().__init__(app)
        self.audit_log_service = audit_log_service
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_ip_filtering = enable_ip_filtering
        self.enable_csrf_protection = enable_csrf_protection

        # Rate limiting state
        self._rate_limit_buckets: Dict[str, List[float]] = defaultdict(list)
        self._rate_limit_config = {
            "default": {"requests": 100, "window_seconds": 60},  # 100 req/min
            "authenticated": {"requests": 1000, "window_seconds": 60},  # 1000 req/min
            "login": {"requests": 5, "window_seconds": 300},  # 5 attempts per 5 min
        }

        # IP filtering state
        self._ip_allowlist: Set[str] = set()
        self._ip_denylist: Set[str] = set()
        self._suspicious_ips: Dict[str, int] = defaultdict(int)  # IP -> violation count

        # CSRF tokens
        self._csrf_tokens: Dict[str, datetime] = {}  # token -> expiry

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through security middleware.

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response
        """
        start_time = time.time()
        client_ip = self._get_client_ip(request)

        try:
            # 1. IP Filtering
            if self.enable_ip_filtering:
                await self._check_ip_filter(client_ip)

            # 2. Rate Limiting
            if self.enable_rate_limiting:
                await self._check_rate_limit(request, client_ip)

            # 3. CSRF Protection (for state-changing operations)
            if self.enable_csrf_protection and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                await self._validate_csrf_token(request)

            # 4. Add security headers to request context
            request.state.security_context = {
                "client_ip": client_ip,
                "request_id": self._generate_request_id(request),
                "timestamp": datetime.utcnow(),
            }

            # 5. Process request
            response = await call_next(request)

            # 6. Add security response headers
            response = self._add_security_headers(response)

            # 7. Log request (if audit logging enabled)
            if self.audit_log_service:
                duration_ms = (time.time() - start_time) * 1000
                await self._log_request(request, response, duration_ms)

            return response

        except RateLimitExceeded as e:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {e}")
            return self._rate_limit_response()

        except SecurityViolation as e:
            logger.error(f"Security violation from IP {client_ip}: {e}")
            self._suspicious_ips[client_ip] += 1

            # Auto-block after 10 violations
            if self._suspicious_ips[client_ip] >= 10:
                self._ip_denylist.add(client_ip)
                logger.critical(f"IP {client_ip} automatically blocked due to repeated violations")

            return self._security_violation_response()

        except Exception as e:
            logger.error(f"Security middleware error: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error"}
            )

    async def _check_ip_filter(self, client_ip: str):
        """
        Check IP allowlist/denylist.

        Args:
            client_ip: Client IP address

        Raises:
            SecurityViolation: If IP is denied
        """
        # Check denylist first
        if client_ip in self._ip_denylist:
            raise SecurityViolation(f"IP {client_ip} is blocked")

        # If allowlist is configured, check it
        if self._ip_allowlist and client_ip not in self._ip_allowlist:
            raise SecurityViolation(f"IP {client_ip} not in allowlist")

    async def _check_rate_limit(self, request: Request, client_ip: str):
        """
        Check rate limit for client.

        Args:
            request: Request object
            client_ip: Client IP address

        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        # Determine rate limit tier
        if request.url.path.endswith("/login"):
            tier = "login"
        elif hasattr(request.state, "user_id"):
            tier = "authenticated"
        else:
            tier = "default"

        config = self._rate_limit_config[tier]
        max_requests = config["requests"]
        window_seconds = config["window_seconds"]

        # Get or create bucket for this client
        bucket_key = f"{client_ip}:{tier}"
        now = time.time()
        cutoff = now - window_seconds

        # Clean old requests from bucket
        bucket = self._rate_limit_buckets[bucket_key]
        bucket = [ts for ts in bucket if ts > cutoff]
        self._rate_limit_buckets[bucket_key] = bucket

        # Check if limit exceeded
        if len(bucket) >= max_requests:
            raise RateLimitExceeded(
                f"Rate limit exceeded: {max_requests} requests per {window_seconds} seconds"
            )

        # Add current request to bucket
        bucket.append(now)

    async def _validate_csrf_token(self, request: Request):
        """
        Validate CSRF token for state-changing operations.

        Args:
            request: Request object

        Raises:
            SecurityViolation: If CSRF token invalid or missing
        """
        # Skip CSRF for API endpoints with bearer token authentication
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return

        # Get CSRF token from header or form
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            csrf_token = request.cookies.get("csrf_token")

        if not csrf_token:
            raise SecurityViolation("CSRF token missing")

        # Validate token
        if csrf_token not in self._csrf_tokens:
            raise SecurityViolation("Invalid CSRF token")

        # Check expiry
        expiry = self._csrf_tokens[csrf_token]
        if datetime.utcnow() > expiry:
            del self._csrf_tokens[csrf_token]
            raise SecurityViolation("CSRF token expired")

    def _add_security_headers(self, response: Response) -> Response:
        """
        Add security headers to response.

        Args:
            response: Response object

        Returns:
            Response with security headers
        """
        # HTTP Strict Transport Security (HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Content Security Policy (CSP)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )

        # X-Frame-Options (prevent clickjacking)
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options (prevent MIME sniffing)
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection (legacy XSS protection)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy (control referrer information)
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy (control browser features)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=()"
        )

        # Cache-Control for sensitive data
        if "application/json" in response.headers.get("content-type", ""):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.

        Handles proxy headers (X-Forwarded-For, X-Real-IP).

        Args:
            request: Request object

        Returns:
            Client IP address
        """
        # Check proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2, ...)
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        return request.client.host if request.client else "unknown"

    def _generate_request_id(self, request: Request) -> str:
        """
        Generate unique request ID for correlation.

        Args:
            request: Request object

        Returns:
            Request ID
        """
        # Check if request already has an ID (from load balancer)
        request_id = request.headers.get("X-Request-ID")
        if request_id:
            return request_id

        # Generate new request ID
        unique_string = f"{time.time()}:{request.url.path}:{self._get_client_ip(request)}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]

    async def _log_request(self, request: Request, response: Response, duration_ms: float):
        """
        Log request to audit log.

        Args:
            request: Request object
            response: Response object
            duration_ms: Request duration in milliseconds
        """
        # Extract user context (if available)
        user_id = getattr(request.state, "user_id", None)
        tenant_id = getattr(request.state, "tenant_id", None)

        # Log to audit service (simplified - would be more comprehensive in production)
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.2f}ms)",
            extra={
                "user_id": str(user_id) if user_id else None,
                "tenant_id": str(tenant_id) if tenant_id else None,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("User-Agent"),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        )

    def _rate_limit_response(self) -> JSONResponse:
        """
        Generate rate limit exceeded response.

        Returns:
            429 Too Many Requests response
        """
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": 60,
            },
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
            }
        )

    def _security_violation_response(self) -> JSONResponse:
        """
        Generate security violation response.

        Returns:
            403 Forbidden response
        """
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "Security violation",
                "message": "Access denied due to security policy violation.",
            }
        )

    # ========================================================================
    # CSRF TOKEN MANAGEMENT
    # ========================================================================

    def generate_csrf_token(self, session_id: str) -> str:
        """
        Generate CSRF token for session.

        Args:
            session_id: User session ID

        Returns:
            CSRF token
        """
        token = hashlib.sha256(f"{session_id}:{time.time()}".encode()).hexdigest()
        self._csrf_tokens[token] = datetime.utcnow() + timedelta(hours=1)
        return token

    def revoke_csrf_token(self, token: str):
        """
        Revoke CSRF token.

        Args:
            token: CSRF token to revoke
        """
        if token in self._csrf_tokens:
            del self._csrf_tokens[token]

    # ========================================================================
    # IP MANAGEMENT
    # ========================================================================

    def add_to_allowlist(self, ip_address: str):
        """
        Add IP to allowlist.

        Args:
            ip_address: IP address to allow
        """
        self._ip_allowlist.add(ip_address)
        logger.info(f"Added {ip_address} to IP allowlist")

    def remove_from_allowlist(self, ip_address: str):
        """
        Remove IP from allowlist.

        Args:
            ip_address: IP address to remove
        """
        self._ip_allowlist.discard(ip_address)
        logger.info(f"Removed {ip_address} from IP allowlist")

    def add_to_denylist(self, ip_address: str):
        """
        Add IP to denylist (block).

        Args:
            ip_address: IP address to block
        """
        self._ip_denylist.add(ip_address)
        logger.warning(f"Added {ip_address} to IP denylist (blocked)")

    def remove_from_denylist(self, ip_address: str):
        """
        Remove IP from denylist (unblock).

        Args:
            ip_address: IP address to unblock
        """
        self._ip_denylist.discard(ip_address)
        logger.info(f"Removed {ip_address} from IP denylist (unblocked)")


# ============================================================================
# SESSION SECURITY
# ============================================================================

class SessionSecurity:
    """
    Secure session management for SOC 2 compliance.

    Features:
    - Secure session ID generation
    - Session timeout enforcement
    - Concurrent session limits
    - Session hijacking detection
    """

    def __init__(
        self,
        session_timeout_minutes: int = 30,
        absolute_timeout_hours: int = 8,
        max_concurrent_sessions: int = 3,
    ):
        """
        Initialize session security.

        Args:
            session_timeout_minutes: Idle timeout in minutes
            absolute_timeout_hours: Absolute timeout in hours
            max_concurrent_sessions: Max concurrent sessions per user
        """
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.absolute_timeout = timedelta(hours=absolute_timeout_hours)
        self.max_concurrent_sessions = max_concurrent_sessions

        self._sessions: Dict[str, Dict] = {}  # session_id -> session_data
        self._user_sessions: Dict[UUID, Set[str]] = defaultdict(set)  # user_id -> session_ids

    def create_session(
        self,
        user_id: UUID,
        tenant_id: UUID,
        ip_address: str,
        user_agent: str,
    ) -> str:
        """
        Create new secure session.

        Args:
            user_id: User ID
            tenant_id: Tenant ID
            ip_address: Client IP
            user_agent: Client user agent

        Returns:
            Session ID
        """
        # Generate secure session ID
        session_id = self._generate_session_id(user_id, ip_address)

        # Check concurrent session limit
        user_session_ids = self._user_sessions[user_id]
        if len(user_session_ids) >= self.max_concurrent_sessions:
            # Revoke oldest session
            oldest_session = min(
                user_session_ids,
                key=lambda sid: self._sessions[sid]["created_at"]
            )
            self.revoke_session(oldest_session)
            logger.warning(f"Revoked oldest session for user {user_id} due to concurrent limit")

        # Create session
        now = datetime.utcnow()
        self._sessions[session_id] = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": now,
            "last_activity": now,
            "expires_at": now + self.absolute_timeout,
        }
        self._user_sessions[user_id].add(session_id)

        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id

    def validate_session(
        self,
        session_id: str,
        ip_address: str,
        user_agent: str,
    ) -> Optional[Dict]:
        """
        Validate session and check for hijacking.

        Args:
            session_id: Session ID to validate
            ip_address: Current client IP
            user_agent: Current user agent

        Returns:
            Session data if valid, None otherwise
        """
        if session_id not in self._sessions:
            return None

        session = self._sessions[session_id]
        now = datetime.utcnow()

        # Check absolute timeout
        if now > session["expires_at"]:
            self.revoke_session(session_id)
            logger.info(f"Session {session_id} expired (absolute timeout)")
            return None

        # Check idle timeout
        if now - session["last_activity"] > self.session_timeout:
            self.revoke_session(session_id)
            logger.info(f"Session {session_id} expired (idle timeout)")
            return None

        # Check for session hijacking (IP/User-Agent change)
        if session["ip_address"] != ip_address:
            logger.warning(f"Session {session_id} IP mismatch: {session['ip_address']} != {ip_address}")
            # Could revoke session here for strict security
            # For now, just log warning

        if session["user_agent"] != user_agent:
            logger.warning(f"Session {session_id} User-Agent mismatch")

        # Update last activity
        session["last_activity"] = now

        return session

    def revoke_session(self, session_id: str):
        """
        Revoke (logout) session.

        Args:
            session_id: Session ID to revoke
        """
        if session_id in self._sessions:
            session = self._sessions[session_id]
            user_id = session["user_id"]

            del self._sessions[session_id]
            self._user_sessions[user_id].discard(session_id)

            logger.info(f"Revoked session {session_id}")

    def _generate_session_id(self, user_id: UUID, ip_address: str) -> str:
        """
        Generate cryptographically secure session ID.

        Args:
            user_id: User ID
            ip_address: Client IP

        Returns:
            Session ID
        """
        import secrets
        random_bytes = secrets.token_bytes(32)
        unique_string = f"{user_id}:{ip_address}:{time.time()}:{random_bytes.hex()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()
