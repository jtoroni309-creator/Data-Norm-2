"""
Pytest configuration for reg-ab-audit service tests.
"""
import pytest
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    class MockOpenAIClient:
        async def chat_completions_create(self, *args, **kwargs):
            class MockResponse:
                class Choice:
                    class Message:
                        content = '{"compliant": true, "confidence": 0.95, "findings": []}'

                    message = Message()

                choices = [Choice()]

            return MockResponse()

    return MockOpenAIClient()


@pytest.fixture
def test_engagement_id():
    """Test engagement ID."""
    return uuid4()


@pytest.fixture
def test_deal_id():
    """Test CMBS deal ID."""
    return uuid4()


@pytest.fixture
def sample_cmbs_deal():
    """Sample CMBS deal data."""
    return {
        "deal_id": str(uuid4()),
        "deal_name": "Test CMBS 2024-1",
        "origination_date": date(2024, 1, 1),
        "total_principal": Decimal("500000000"),
        "loan_count": 50,
        "property_types": ["Office", "Retail"],
        "geographic_concentration": {"CA": 0.4, "NY": 0.3, "TX": 0.3},
    }


@pytest.fixture
def sample_compliance_check_result():
    """Sample compliance check result."""
    return {
        "check_id": str(uuid4()),
        "standard": "Regulation_AB",
        "rule": "1120.01",
        "status": "PASS",
        "confidence": 0.95,
        "findings": [],
        "recommendations": [],
    }
