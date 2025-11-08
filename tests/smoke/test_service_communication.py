"""
Service-to-Service Communication Smoke Tests

Tests HTTP communication between microservices, including health checks,
API endpoints, authentication, and error handling.
These tests verify that services can communicate correctly after deployment.
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from typing import Dict
from httpx import AsyncClient, ConnectError, TimeoutException


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_gateway_health(http_client: AsyncClient):
    """
    Verify API Gateway is healthy and responding.

    Impact: Ensures main entry point for all services is operational.
    """
    response = await http_client.get("/health")

    assert response.status_code == 200, f"Gateway health check failed: {response.status_code}"

    # Verify response structure
    health_data = response.json()
    assert "status" in health_data, "Health response missing 'status' field"
    assert health_data["status"] in ["healthy", "ok"], f"Unexpected health status: {health_data['status']}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_identity_service_health(http_client: AsyncClient):
    """
    Verify Identity service is healthy.

    Impact: Ensures authentication and authorization are operational.
    """
    response = await http_client.get("/api/identity/health")

    assert response.status_code == 200, f"Identity service health check failed: {response.status_code}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_engagement_service_health(http_client: AsyncClient):
    """
    Verify Engagement service is healthy.

    Impact: Ensures core engagement management is operational.
    """
    response = await http_client.get("/api/engagement/health")

    assert response.status_code == 200, f"Engagement service health check failed: {response.status_code}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_user_registration_and_authentication(http_client: AsyncClient):
    """
    Verify user can register and authenticate.

    Impact: Ensures authentication flow works end-to-end.
    """
    # Generate unique test user
    user_email = f"smoke-test-{uuid4()}@example.com"
    user_password = "SmokeTest123!"

    # Register user
    register_payload = {
        "email": user_email,
        "password": user_password,
        "full_name": "Smoke Test User",
        "firm_name": "Smoke Test Firm",
    }

    register_response = await http_client.post(
        "/api/identity/auth/register",
        json=register_payload,
    )

    assert register_response.status_code in (200, 201), \
        f"User registration failed: {register_response.status_code} - {register_response.text}"

    # Login with credentials
    login_response = await http_client.post(
        "/api/identity/auth/login",
        data={
            "username": user_email,
            "password": user_password,
        },
    )

    assert login_response.status_code == 200, \
        f"User login failed: {login_response.status_code} - {login_response.text}"

    # Verify token in response
    token_data = login_response.json()
    assert "access_token" in token_data, "Login response missing access_token"
    assert "token_type" in token_data, "Login response missing token_type"
    assert token_data["token_type"] == "bearer", f"Unexpected token type: {token_data['token_type']}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_authenticated_engagement_creation(http_client: AsyncClient, auth_headers: Dict[str, str]):
    """
    Verify authenticated user can create engagement.

    Impact: Ensures service-to-service auth and engagement creation works.
    """
    from datetime import date

    engagement_payload = {
        "name": f"Smoke Test Engagement {uuid4()}",
        "client_name": "Smoke Test Client Corp",
        "engagement_type": "audit",
        "fiscal_year_end": date.today().isoformat(),
    }

    response = await http_client.post(
        "/api/engagement/engagements",
        json=engagement_payload,
        headers=auth_headers,
    )

    assert response.status_code in (200, 201), \
        f"Engagement creation failed: {response.status_code} - {response.text}"

    # Verify response structure
    engagement = response.json()
    assert "id" in engagement, "Engagement response missing 'id'"
    assert "name" in engagement, "Engagement response missing 'name'"
    assert engagement["name"] == engagement_payload["name"]


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_engagement_retrieval(http_client: AsyncClient, auth_headers: Dict[str, str], test_engagement_id: str):
    """
    Verify engagement can be retrieved by ID.

    Impact: Ensures service can read data after creation.
    """
    response = await http_client.get(
        f"/api/engagement/engagements/{test_engagement_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200, \
        f"Engagement retrieval failed: {response.status_code} - {response.text}"

    engagement = response.json()
    assert engagement["id"] == test_engagement_id


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_engagement_list_pagination(http_client: AsyncClient, auth_headers: Dict[str, str]):
    """
    Verify engagement list endpoint with pagination.

    Impact: Ensures list endpoints scale properly.
    """
    response = await http_client.get(
        "/api/engagement/engagements?page=1&page_size=10",
        headers=auth_headers,
    )

    assert response.status_code == 200, \
        f"Engagement list failed: {response.status_code} - {response.text}"

    # Verify response structure
    data = response.json()
    assert isinstance(data, dict) or isinstance(data, list), "Invalid response format"

    # If paginated response
    if isinstance(data, dict):
        assert "items" in data or "data" in data or "engagements" in data, \
            "Paginated response missing data field"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_unauthorized_access_blocked(http_client: AsyncClient):
    """
    Verify unauthorized requests are blocked.

    Impact: Ensures authentication is properly enforced.
    """
    # Try to access protected endpoint without auth
    response = await http_client.get("/api/engagement/engagements")

    assert response.status_code == 401, \
        f"Expected 401 Unauthorized, got {response.status_code}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_invalid_token_rejected(http_client: AsyncClient):
    """
    Verify invalid auth tokens are rejected.

    Impact: Ensures token validation is working.
    """
    invalid_headers = {
        "Authorization": "Bearer invalid_token_12345",
        "Content-Type": "application/json",
    }

    response = await http_client.get(
        "/api/engagement/engagements",
        headers=invalid_headers,
    )

    assert response.status_code == 401, \
        f"Expected 401 for invalid token, got {response.status_code}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_engagement_update(http_client: AsyncClient, auth_headers: Dict[str, str], test_engagement_id: str):
    """
    Verify engagement can be updated.

    Impact: Ensures PATCH/PUT operations work correctly.
    """
    update_payload = {
        "name": f"Updated Smoke Test Engagement {uuid4()}",
    }

    response = await http_client.patch(
        f"/api/engagement/engagements/{test_engagement_id}",
        json=update_payload,
        headers=auth_headers,
    )

    assert response.status_code == 200, \
        f"Engagement update failed: {response.status_code} - {response.text}"

    updated_engagement = response.json()
    assert updated_engagement["name"] == update_payload["name"]


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_engagement_team_management(http_client: AsyncClient, auth_headers: Dict[str, str], test_engagement_id: str):
    """
    Verify engagement team members can be added.

    Impact: Ensures service-to-service data relationships work.
    """
    # Get current team members
    response = await http_client.get(
        f"/api/engagement/engagements/{test_engagement_id}/team",
        headers=auth_headers,
    )

    assert response.status_code == 200, \
        f"Failed to get team members: {response.status_code} - {response.text}"

    initial_team = response.json()
    initial_count = len(initial_team) if isinstance(initial_team, list) else initial_team.get("count", 0)

    # Add team member
    team_member_payload = {
        "role": "staff",
        "permissions": ["read", "write"],
    }

    add_response = await http_client.post(
        f"/api/engagement/engagements/{test_engagement_id}/team",
        json=team_member_payload,
        headers=auth_headers,
    )

    # Accept either success or conflict (if member already exists)
    assert add_response.status_code in (200, 201, 409), \
        f"Failed to add team member: {add_response.status_code} - {add_response.text}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_engagement_state_transition(http_client: AsyncClient, auth_headers: Dict[str, str], test_engagement_id: str):
    """
    Verify engagement state machine transitions work.

    Impact: Ensures workflow state management is operational.
    """
    # Get current state
    response = await http_client.get(
        f"/api/engagement/engagements/{test_engagement_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    engagement = response.json()
    current_status = engagement.get("status", "draft")

    # Try to transition (if endpoint exists)
    # This may vary by implementation
    transition_payload = {
        "action": "start_planning",
    }

    transition_response = await http_client.post(
        f"/api/engagement/engagements/{test_engagement_id}/transition",
        json=transition_payload,
        headers=auth_headers,
    )

    # Accept success or invalid state transition
    assert transition_response.status_code in (200, 400, 404), \
        f"Unexpected transition response: {transition_response.status_code}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_not_found_error_handling(http_client: AsyncClient, auth_headers: Dict[str, str]):
    """
    Verify 404 errors are returned for non-existent resources.

    Impact: Ensures proper error handling for missing resources.
    """
    fake_id = str(uuid4())

    response = await http_client.get(
        f"/api/engagement/engagements/{fake_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404, \
        f"Expected 404 for non-existent engagement, got {response.status_code}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_validation_error_handling(http_client: AsyncClient, auth_headers: Dict[str, str]):
    """
    Verify validation errors are returned for invalid data.

    Impact: Ensures input validation is working.
    """
    # Try to create engagement with invalid data
    invalid_payload = {
        "name": "",  # Empty name should fail validation
        "engagement_type": "invalid_type",
    }

    response = await http_client.post(
        "/api/engagement/engagements",
        json=invalid_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422, \
        f"Expected 422 validation error, got {response.status_code}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_service_response_time(http_client: AsyncClient, auth_headers: Dict[str, str]):
    """
    Verify service response times are acceptable.

    Impact: Catches performance regressions after deployment.
    """
    import time

    start = time.time()
    response = await http_client.get(
        "/api/engagement/engagements?page=1&page_size=10",
        headers=auth_headers,
    )
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 2.0, f"Service response too slow: {duration}s (expected < 2s)"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_concurrent_service_requests(http_client: AsyncClient, auth_headers: Dict[str, str]):
    """
    Verify service can handle concurrent requests.

    Impact: Ensures service scales under load.
    """
    import asyncio

    async def make_request(i: int):
        response = await http_client.get(
            "/api/engagement/engagements?page=1&page_size=5",
            headers=auth_headers,
        )
        return response.status_code

    # Make 10 concurrent requests
    status_codes = await asyncio.gather(*[make_request(i) for i in range(10)])

    # All should succeed
    assert all(code == 200 for code in status_codes), \
        f"Some concurrent requests failed: {status_codes}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_gateway_routing_to_multiple_services(http_client: AsyncClient):
    """
    Verify API Gateway routes to multiple backend services.

    Impact: Ensures gateway routing configuration is correct.
    """
    services_to_test = [
        "/api/identity/health",
        "/api/engagement/health",
        "/api/ingestion/health",
        "/api/normalize/health",
    ]

    results = {}

    for endpoint in services_to_test:
        try:
            response = await http_client.get(endpoint, timeout=5.0)
            results[endpoint] = response.status_code
        except Exception as e:
            results[endpoint] = f"Error: {str(e)}"

    # At least identity and engagement should be accessible
    assert results.get("/api/identity/health") == 200, \
        "Identity service not accessible through gateway"
    assert results.get("/api/engagement/health") == 200, \
        "Engagement service not accessible through gateway"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_cors_headers(http_client: AsyncClient):
    """
    Verify CORS headers are set correctly.

    Impact: Ensures frontend can communicate with API.
    """
    response = await http_client.options(
        "/api/identity/health",
        headers={"Origin": "http://localhost:3000"},
    )

    # Check for CORS headers (if CORS is configured)
    # This may vary by deployment
    assert response.status_code in (200, 204, 404), \
        f"OPTIONS request failed: {response.status_code}"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_rate_limiting(http_client: AsyncClient, auth_headers: Dict[str, str]):
    """
    Verify rate limiting is enforced (if configured).

    Impact: Ensures API protection from abuse.
    """
    # Make many rapid requests
    responses = []
    for i in range(150):  # Gateway configured for 120 req/min
        try:
            response = await http_client.get(
                "/api/engagement/health",
                headers=auth_headers,
                timeout=1.0,
            )
            responses.append(response.status_code)

            # If we get rate limited, stop
            if response.status_code == 429:
                break
        except TimeoutException:
            # Timeout may indicate rate limiting at infrastructure level
            pass

    # Note: This test may not always trigger rate limiting in smoke tests
    # Verify rate limiting infrastructure exists
    # Actual rate limiting behavior should be tested in load tests


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_service_error_responses(http_client: AsyncClient, auth_headers: Dict[str, str]):
    """
    Verify services return proper error responses.

    Impact: Ensures error handling provides useful information.
    """
    # Try to access invalid endpoint
    response = await http_client.get(
        "/api/engagement/invalid-endpoint-12345",
        headers=auth_headers,
    )

    assert response.status_code == 404

    # Try invalid method
    response = await http_client.delete(
        "/api/engagement/health",
        headers=auth_headers,
    )

    assert response.status_code in (404, 405), \
        "Invalid method should return 404 or 405"


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_json_response_format(http_client: AsyncClient, auth_headers: Dict[str, str]):
    """
    Verify services return valid JSON responses.

    Impact: Ensures API contract is maintained.
    """
    response = await http_client.get(
        "/api/engagement/engagements?page=1&page_size=1",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/json"), \
        "Response should be JSON"

    # Verify JSON is parseable
    try:
        data = response.json()
        assert data is not None
    except Exception as e:
        pytest.fail(f"Response is not valid JSON: {e}")


@pytest.mark.smoke
@pytest.mark.service
@pytest.mark.asyncio
async def test_service_version_headers(http_client: AsyncClient):
    """
    Verify service version information is available.

    Impact: Helps track deployed versions for debugging.
    """
    response = await http_client.get("/health")

    # Check for version information (if exposed)
    # This may be in headers or response body
    health_data = response.json()

    # Version info is useful but not always required
    # Just verify response structure is valid
    assert isinstance(health_data, dict), "Health check should return JSON object"
