"""
Unit tests for Tax OCR Intake Service
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
    assert data["service"] == "tax-ocr-intake"
    assert "features" in data


@pytest.mark.asyncio
async def test_supported_document_types():
    """Test supported document types endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/v1/supported-document-types")

    assert response.status_code == 200
    data = response.json()
    assert "document_types" in data
    assert len(data["document_types"]) > 0

    # Check W-2 is included
    w2 = next((d for d in data["document_types"] if d["code"] == "W-2"), None)
    assert w2 is not None
    assert w2["name"] == "Wage and Tax Statement"
