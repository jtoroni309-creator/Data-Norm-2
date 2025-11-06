"""
Pytest configuration for ingestion service tests.
"""
import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))


@pytest.fixture
def edgar_base_url():
    """EDGAR API base URL."""
    return "https://data.sec.gov"


@pytest.fixture
def edgar_user_agent():
    """EDGAR API user agent."""
    return "Test Aura Audit AI test@example.com"


@pytest.fixture
def sample_cik():
    """Sample CIK."""
    return "0000320193"  # Apple Inc.


@pytest.fixture
def sample_company_facts():
    """Sample company facts response."""
    return {
        "cik": "0000320193",
        "entityName": "Apple Inc.",
        "facts": {
            "us-gaap": {
                "Assets": {
                    "label": "Assets",
                    "description": "Total assets",
                    "units": {
                        "USD": [
                            {"end": "2023-09-30", "val": 352755000000, "fy": 2023, "fp": "FY", "form": "10-K"}
                        ]
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_httpx_client():
    """Mock HTTP client for EDGAR API."""
    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code

        def json(self):
            return self._json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")

    class MockClient:
        def __init__(self):
            self.responses = {}

        async def get(self, url, **kwargs):
            if "company_facts" in url:
                return MockResponse({"cik": "0000320193", "entityName": "Test Corp", "facts": {}})
            return MockResponse({})

        async def aclose(self):
            pass

    return MockClient()
