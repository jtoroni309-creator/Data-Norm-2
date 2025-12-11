"""
API Gateway for Aura Audit AI Platform

Routes requests to appropriate microservices with:
- Authentication middleware
- Rate limiting
- Circuit breaker pattern
- Request/response logging
- Health check aggregation
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict

import httpx
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
import uvicorn

# Service registry with health check endpoints
# Service names match Kubernetes service names (not api-* prefix)
SERVICE_REGISTRY = {
    "identity": {"url": "http://identity:80", "health": "/health"},
    "ingestion": {"url": "http://ingestion:80", "health": "/health"},
    "normalize": {"url": "http://normalize:80", "health": "/health"},
    "analytics": {"url": "http://analytics:80", "health": "/health"},
    "llm": {"url": "http://llm:80", "health": "/health"},
    "engagement": {"url": "http://engagement:80", "health": "/health"},
    "disclosures": {"url": "http://disclosures:80", "health": "/health"},
    "reporting": {"url": "http://reporting:80", "health": "/health"},
    "qc": {"url": "http://qc:80", "health": "/health"},
    "connectors": {"url": "http://connectors:80", "health": "/health"},
    "reg-ab-audit": {"url": "http://reg-ab-audit:80", "health": "/health"},
    "audit-planning": {"url": "http://audit-planning:80", "health": "/health"},
    "accounting-integrations": {"url": "http://accounting-integrations:80", "health": "/health"},
    "data-anonymization": {"url": "http://data-anonymization:80", "health": "/health"},
    "financial-analysis": {"url": "http://financial-analysis:80", "health": "/health"},
    "fraud-detection": {"url": "http://fraud-detection:80", "health": "/health"},
    "related-party": {"url": "http://related-party:80", "health": "/health"},
    "sampling": {"url": "http://sampling:80", "health": "/health"},
    "security": {"url": "http://security:80", "health": "/health"},
    "subsequent-events": {"url": "http://subsequent-events:80", "health": "/health"},
    "substantive-testing": {"url": "http://substantive-testing:80", "health": "/health"},
    "training-data": {"url": "http://training-data:80", "health": "/health"},
    "eo-insurance": {"url": "http://eo-insurance-portal:80", "health": "/health"},
    "estimates": {"url": "http://estimates-evaluation:80", "health": "/health"},
    "rd-study-automation": {"url": "http://rd-study-automation:8000", "health": "/health", "strip_prefix": "/rd-study"},
    "rd-ai-document-processor": {"url": "http://rd-ai-document-processor:8000", "health": "/health"},  # GPU-accelerated
    "rd-study-automation-gpu": {"url": "http://rd-study-automation-gpu:8000", "health": "/health"},  # GPU-optimized R&D
}

# Path routing rules (prefix -> service)
ROUTE_MAP = {
    "/auth": "identity",
    "/identity": "identity",
    "/users": "identity",
    "/invitations": "identity",
    "/admin": "identity",
    "/organizations": "identity",
    "/clients": "identity",
    "/rdclient": "identity",  # R&D Client Portal auth endpoints
    "/rd-study": "rd-study-automation",
    "/rd-ai": "rd-ai-document-processor",  # GPU-accelerated document processing
    "/rd-gpu": "rd-study-automation-gpu",  # GPU-optimized R&D study service

    "/ingestion": "ingestion",
    "/edgar": "ingestion",
    "/trials": "ingestion",

    "/normalize": "normalize",
    "/mapping": "normalize",

    "/analytics": "analytics",
    "/je-testing": "analytics",
    "/ratios": "analytics",
    "/anomalies": "analytics",

    "/llm": "llm",
    "/embeddings": "llm",
    "/chat": "llm",

    "/engagements": "engagement",
    "/binders": "engagement",
    "/team": "engagement",

    "/disclosures": "disclosures",
    "/notes": "disclosures",

    "/reports": "reporting",
    "/pdf": "reporting",
    "/esign": "reporting",

    "/qc": "qc",
    "/reviews": "qc",

    "/connectors": "connectors",
    "/integrations": "connectors",

    "/reg-ab": "reg-ab-audit",
    "/reg-ab-audit": "reg-ab-audit",

    "/audit-planning": "audit-planning",
    "/risk-assessment": "audit-planning",

    "/accounting-integrations": "accounting-integrations",
    "/quickbooks": "accounting-integrations",
    "/xero": "accounting-integrations",

    "/anonymization": "data-anonymization",
    "/pii": "data-anonymization",

    "/financial-analysis": "financial-analysis",
    "/metrics": "financial-analysis",

    "/fraud-detection": "fraud-detection",
    "/fraud": "fraud-detection",

    "/related-party": "related-party",

    "/sampling": "sampling",

    "/security": "security",
    "/encryption": "security",
    "/audit-logs": "security",

    "/subsequent-events": "subsequent-events",

    "/substantive-testing": "substantive-testing",

    "/training-data": "training-data",
    "/ml-training": "training-data",

    "/eo-insurance": "eo-insurance",

    "/estimates": "estimates",
}

app = FastAPI(
    title="Aura Audit AI Gateway",
    description="API Gateway for routing requests to microservices",
    version="1.0.0"
)

# CORS configuration
import os

# Get allowed origins from environment variable
allowed_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
)

# Rate limiting storage (in-memory, use Redis in production)
rate_limit_storage: Dict[str, list] = defaultdict(list)

# Circuit breaker state
circuit_breaker_state: Dict[str, dict] = defaultdict(lambda: {
    "failures": 0,
    "last_failure": None,
    "state": "closed"  # closed, open, half-open
})


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window = 60  # seconds

    def check_rate_limit(self, client_id: str) -> bool:
        """Check if request is within rate limit"""
        now = time.time()
        window_start = now - self.window

        # Clean old requests
        rate_limit_storage[client_id] = [
            req_time for req_time in rate_limit_storage[client_id]
            if req_time > window_start
        ]

        # Check limit
        if len(rate_limit_storage[client_id]) >= self.requests_per_minute:
            return False

        # Add current request
        rate_limit_storage[client_id].append(now)
        return True


class CircuitBreaker:
    """Circuit breaker for service failures"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout

    def record_success(self, service: str):
        """Record successful request"""
        circuit_breaker_state[service]["failures"] = 0
        circuit_breaker_state[service]["state"] = "closed"

    def record_failure(self, service: str):
        """Record failed request"""
        state = circuit_breaker_state[service]
        state["failures"] += 1
        state["last_failure"] = time.time()

        if state["failures"] >= self.failure_threshold:
            state["state"] = "open"

    def can_request(self, service: str) -> bool:
        """Check if requests are allowed"""
        state = circuit_breaker_state[service]

        if state["state"] == "closed":
            return True

        if state["state"] == "open":
            # Check if timeout has passed
            if time.time() - state["last_failure"] > self.timeout:
                state["state"] = "half-open"
                return True
            return False

        # half-open state allows one request
        return True


rate_limiter = RateLimiter(requests_per_minute=120)
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)


def get_client_id(request: Request) -> str:
    """Extract client identifier for rate limiting"""
    # Use authorization token if available, otherwise IP
    auth_header = request.headers.get("authorization")
    if auth_header:
        return auth_header[:50]  # Use token prefix
    return request.client.host if request.client else "unknown"


def resolve_service(path: str) -> Optional[str]:
    """Resolve service name from request path"""
    for prefix, service in ROUTE_MAP.items():
        if path.startswith(prefix):
            return service
    return None


async def proxy_request(
    request: Request,
    service_url: str,
    path: str,
    method: str
) -> StreamingResponse:
    """Proxy request to backend service"""

    # Build target URL
    target_url = f"{service_url}{path}"
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    # Prepare headers (exclude host)
    headers = dict(request.headers)
    headers.pop("host", None)

    # Read request body
    body = await request.body()

    # Make request to backend service
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                content=body
            )

            # Return streaming response
            return StreamingResponse(
                content=response.aiter_bytes(),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Service request timed out"
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable"
            )


@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    """Gateway middleware for rate limiting and routing"""

    # Skip middleware for gateway health check
    if request.url.path == "/health":
        return await call_next(request)

    # Rate limiting
    client_id = get_client_id(request)
    if not rate_limiter.check_rate_limit(client_id):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded"}
        )

    # Request logging
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Response logging
    duration = time.time() - start_time
    print(f"[{datetime.now().isoformat()}] {request.method} {request.url.path} "
          f"-> {response.status_code} ({duration:.3f}s)")

    return response


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(request: Request, path: str):
    """Main gateway routing endpoint"""

    # Resolve target service
    service_name = resolve_service(f"/{path}")

    if not service_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No service found for path: /{path}"
        )

    # Get service configuration
    service_config = SERVICE_REGISTRY.get(service_name)
    if not service_config:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Service {service_name} not registered"
        )

    # Circuit breaker check
    if not circuit_breaker.can_request(service_name):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service {service_name} is temporarily unavailable (circuit breaker open)"
        )

    # Proxy request to backend
    try:
        # Build the forwarded path, stripping prefix if configured
        forward_path = f"/{path}"
        strip_prefix = service_config.get("strip_prefix")
        if strip_prefix and forward_path.startswith(strip_prefix):
            forward_path = forward_path[len(strip_prefix):] or "/"

        response = await proxy_request(
            request=request,
            service_url=service_config["url"],
            path=forward_path,
            method=request.method
        )

        # Record success
        circuit_breaker.record_success(service_name)

        return response

    except HTTPException as e:
        # Record failure for 5xx errors
        if e.status_code >= 500:
            circuit_breaker.record_failure(service_name)
        raise


@app.get("/health")
async def health_check():
    """Gateway health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "api-gateway"
    }


@app.get("/health/services")
async def check_all_services():
    """Check health of all backend services"""

    results = {}

    async def check_service(name: str, config: dict):
        """Check individual service health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{config['url']}{config['health']}")
                results[name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            results[name] = {
                "status": "unreachable",
                "error": str(e)
            }

    # Check all services concurrently
    await asyncio.gather(*[
        check_service(name, config)
        for name, config in SERVICE_REGISTRY.items()
    ])

    # Calculate overall health
    healthy_count = sum(1 for r in results.values() if r["status"] == "healthy")
    total_count = len(results)

    return {
        "overall_status": "healthy" if healthy_count == total_count else "degraded",
        "healthy_services": healthy_count,
        "total_services": total_count,
        "services": results,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/metrics")
async def get_metrics():
    """Get gateway metrics"""

    return {
        "rate_limits": {
            "active_clients": len(rate_limit_storage),
            "total_requests": sum(len(reqs) for reqs in rate_limit_storage.values())
        },
        "circuit_breakers": {
            name: {
                "state": state["state"],
                "failures": state["failures"]
            }
            for name, state in circuit_breaker_state.items()
        },
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
