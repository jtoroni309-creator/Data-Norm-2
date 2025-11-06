"""
Service client with circuit breaker and retry logic
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from .exceptions import (
    ServiceError,
    ServiceUnavailableError,
    ServiceTimeoutError,
    ServiceAuthenticationError,
    ServiceNotFoundError
)

logger = logging.getLogger(__name__)


# Service registry with URLs and health endpoints
SERVICE_REGISTRY_CONFIG = {
    "identity": {"url": "http://api-identity:8000", "health": "/health"},
    "ingestion": {"url": "http://api-ingestion:8000", "health": "/health"},
    "normalize": {"url": "http://api-normalize:8000", "health": "/health"},
    "analytics": {"url": "http://api-analytics:8000", "health": "/health"},
    "llm": {"url": "http://api-llm:8000", "health": "/health"},
    "engagement": {"url": "http://api-engagement:8000", "health": "/health"},
    "disclosures": {"url": "http://api-disclosures:8000", "health": "/health"},
    "reporting": {"url": "http://api-reporting:8000", "health": "/health"},
    "qc": {"url": "http://api-qc:8000", "health": "/health"},
    "connectors": {"url": "http://api-connectors:8000", "health": "/health"},
    "reg-ab-audit": {"url": "http://api-reg-ab-audit:8000", "health": "/health"},
    "audit-planning": {"url": "http://api-audit-planning:8000", "health": "/health"},
    "accounting-integrations": {"url": "http://api-accounting-integrations:8000", "health": "/health"},
    "data-anonymization": {"url": "http://api-data-anonymization:8000", "health": "/health"},
    "financial-analysis": {"url": "http://api-financial-analysis:8000", "health": "/health"},
    "fraud-detection": {"url": "http://api-fraud-detection:8000", "health": "/health"},
    "related-party": {"url": "http://api-related-party:8000", "health": "/health"},
    "sampling": {"url": "http://api-sampling:8000", "health": "/health"},
    "security": {"url": "http://api-security:8000", "health": "/health"},
    "subsequent-events": {"url": "http://api-subsequent-events:8000", "health": "/health"},
    "substantive-testing": {"url": "http://api-substantive-testing:8000", "health": "/health"},
    "training-data": {"url": "http://api-training-data:8000", "health": "/health"},
    "eo-insurance": {"url": "http://api-eo-insurance-portal:8000", "health": "/health"},
    "estimates": {"url": "http://api-estimates-evaluation:8000", "health": "/health"},
}


class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60, half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls

        self._state: Dict[str, dict] = defaultdict(lambda: {
            "failures": 0,
            "last_failure_time": None,
            "state": "closed",  # closed, open, half_open
            "half_open_calls": 0
        })

    def record_success(self, service: str):
        """Record successful call"""
        state = self._state[service]
        state["failures"] = 0
        state["state"] = "closed"
        state["half_open_calls"] = 0
        logger.info(f"Circuit breaker for {service}: recorded success, state=closed")

    def record_failure(self, service: str):
        """Record failed call"""
        state = self._state[service]
        state["failures"] += 1
        state["last_failure_time"] = time.time()

        if state["failures"] >= self.failure_threshold:
            state["state"] = "open"
            logger.warning(
                f"Circuit breaker for {service}: OPEN "
                f"(failures={state['failures']}, threshold={self.failure_threshold})"
            )

    def can_execute(self, service: str) -> bool:
        """Check if call can be executed"""
        state = self._state[service]

        if state["state"] == "closed":
            return True

        if state["state"] == "open":
            # Check if timeout period has passed
            if state["last_failure_time"] and \
               (time.time() - state["last_failure_time"]) > self.timeout:
                state["state"] = "half_open"
                state["half_open_calls"] = 0
                logger.info(f"Circuit breaker for {service}: transitioning to HALF_OPEN")
                return True
            return False

        if state["state"] == "half_open":
            # Allow limited calls in half-open state
            if state["half_open_calls"] < self.half_open_max_calls:
                state["half_open_calls"] += 1
                return True
            return False

        return False

    def get_state(self, service: str) -> str:
        """Get current circuit breaker state"""
        return self._state[service]["state"]


class ServiceRegistry:
    """Central service registry"""

    _instance = None
    _circuit_breaker = CircuitBreaker()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_service_url(cls, service_name: str) -> str:
        """Get service URL from registry"""
        if service_name not in SERVICE_REGISTRY_CONFIG:
            raise ServiceNotFoundError(f"Service '{service_name}' not found in registry")
        return SERVICE_REGISTRY_CONFIG[service_name]["url"]

    @classmethod
    def get_circuit_breaker(cls) -> CircuitBreaker:
        """Get shared circuit breaker instance"""
        return cls._circuit_breaker

    @classmethod
    async def check_health(cls, service_name: str, timeout: float = 5.0) -> bool:
        """Check if service is healthy"""
        if service_name not in SERVICE_REGISTRY_CONFIG:
            return False

        config = SERVICE_REGISTRY_CONFIG[service_name]
        health_url = f"{config['url']}{config['health']}"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(health_url)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return False


class ServiceClient:
    """
    HTTP client for service-to-service communication

    Features:
    - Automatic service discovery
    - Circuit breaker pattern
    - Retry with exponential backoff
    - Authentication token propagation
    - Request/response logging
    """

    def __init__(
        self,
        service_name: str,
        timeout: float = 30.0,
        auth_token: Optional[str] = None
    ):
        self.service_name = service_name
        self.timeout = timeout
        self.auth_token = auth_token

        # Get service URL from registry
        self.base_url = ServiceRegistry.get_service_url(service_name)
        self.circuit_breaker = ServiceRegistry.get_circuit_breaker()

        logger.info(f"ServiceClient initialized for {service_name} at {self.base_url}")

    def _build_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers with authentication"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ServiceClient/1.0"
        }

        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        if extra_headers:
            headers.update(extra_headers)

        return headers

    async def _execute_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Execute HTTP request with circuit breaker"""

        # Check circuit breaker
        if not self.circuit_breaker.can_execute(self.service_name):
            raise ServiceUnavailableError(
                f"Service {self.service_name} is unavailable "
                f"(circuit breaker state: {self.circuit_breaker.get_state(self.service_name)})"
            )

        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"[{self.service_name}] {method} {endpoint}")

                response = await client.request(method, url, **kwargs)

                # Record success
                self.circuit_breaker.record_success(self.service_name)

                logger.debug(
                    f"[{self.service_name}] {method} {endpoint} -> {response.status_code}"
                )

                return response

        except httpx.TimeoutException as e:
            self.circuit_breaker.record_failure(self.service_name)
            logger.error(f"[{self.service_name}] Timeout: {endpoint}")
            raise ServiceTimeoutError(f"Request to {self.service_name} timed out") from e

        except httpx.ConnectError as e:
            self.circuit_breaker.record_failure(self.service_name)
            logger.error(f"[{self.service_name}] Connection error: {endpoint}")
            raise ServiceUnavailableError(
                f"Could not connect to {self.service_name}"
            ) from e

        except Exception as e:
            self.circuit_breaker.record_failure(self.service_name)
            logger.error(f"[{self.service_name}] Error: {endpoint} - {e}")
            raise ServiceError(f"Error calling {self.service_name}: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ServiceTimeoutError, ServiceUnavailableError)),
        reraise=True
    )
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute GET request"""
        response = await self._execute_request(
            "GET",
            endpoint,
            params=params,
            headers=self._build_headers(headers)
        )

        if response.status_code == 401:
            raise ServiceAuthenticationError("Authentication failed")

        response.raise_for_status()
        return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ServiceTimeoutError, ServiceUnavailableError)),
        reraise=True
    )
    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute POST request"""
        response = await self._execute_request(
            "POST",
            endpoint,
            json=json,
            data=data,
            headers=self._build_headers(headers)
        )

        if response.status_code == 401:
            raise ServiceAuthenticationError("Authentication failed")

        response.raise_for_status()
        return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ServiceTimeoutError, ServiceUnavailableError)),
        reraise=True
    )
    async def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute PUT request"""
        response = await self._execute_request(
            "PUT",
            endpoint,
            json=json,
            headers=self._build_headers(headers)
        )

        if response.status_code == 401:
            raise ServiceAuthenticationError("Authentication failed")

        response.raise_for_status()
        return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ServiceTimeoutError, ServiceUnavailableError)),
        reraise=True
    )
    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute DELETE request"""
        response = await self._execute_request(
            "DELETE",
            endpoint,
            headers=self._build_headers(headers)
        )

        if response.status_code == 401:
            raise ServiceAuthenticationError("Authentication failed")

        response.raise_for_status()

        # Handle empty responses
        if response.content:
            return response.json()
        return {"status": "success"}

    async def health_check(self) -> bool:
        """Check if service is healthy"""
        return await ServiceRegistry.check_health(self.service_name, timeout=5.0)
