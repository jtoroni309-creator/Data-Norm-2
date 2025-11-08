"""
Unit tests for Tax Computation Engine
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "tax-engine"


@pytest.mark.asyncio
async def test_get_tax_rules():
    """Test tax rules endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/v1/rules/2024?jurisdiction=federal")

    assert response.status_code == 200
    data = response.json()
    assert data["tax_year"] == 2024
    assert data["jurisdiction"] == "federal"
