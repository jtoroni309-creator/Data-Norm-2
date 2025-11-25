"""
Pytest configuration and fixtures for R&D Study Automation tests.
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from uuid import uuid4
from typing import Dict, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.config import Settings


@pytest.fixture(scope="session")
def test_settings():
    """Test configuration settings."""
    return Settings(
        DATABASE_URL="sqlite:///:memory:",
        OPENAI_API_KEY="test-key",
        RULES_VERSION="2024.1",
        ENVIRONMENT="test",
    )


@pytest.fixture(scope="session")
def engine(test_settings):
    """Create test database engine."""
    engine = create_engine(
        test_settings.DATABASE_URL,
        echo=False,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(engine):
    """Create database session for tests."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_study() -> Dict[str, Any]:
    """Sample study data for tests."""
    return {
        "id": str(uuid4()),
        "entity_name": "Test Corporation",
        "entity_type": "c_corp",
        "ein": "12-3456789",
        "tax_year": 2024,
        "fiscal_year_start": date(2024, 1, 1),
        "fiscal_year_end": date(2024, 12, 31),
        "nexus_states": ["CA", "TX", "NY"],
        "controlled_group": False,
        "status": "intake",
    }


@pytest.fixture
def sample_project() -> Dict[str, Any]:
    """Sample project data for tests."""
    return {
        "id": str(uuid4()),
        "name": "AI Model Development",
        "description": "Development of machine learning models for predictive analytics",
        "business_component": "Analytics Platform",
        "start_date": date(2024, 1, 15),
        "end_date": date(2024, 12, 1),
        "technological_uncertainty": "Uncertain whether neural network architecture would achieve required accuracy",
        "process_of_experimentation": "Iterative testing of multiple model architectures and hyperparameters",
        "qualification_status": "pending",
    }


@pytest.fixture
def sample_employee() -> Dict[str, Any]:
    """Sample employee data for tests."""
    return {
        "id": str(uuid4()),
        "name": "Jane Engineer",
        "title": "Senior Software Engineer",
        "department": "Engineering",
        "total_compensation": Decimal("180000"),
        "rd_allocation_percent": Decimal("75"),
        "work_state": "CA",
        "evidence_items": [
            {"type": "timesheet", "contemporaneous": True},
            {"type": "interview", "contemporaneous": False},
        ],
    }


@pytest.fixture
def sample_qre_summary() -> Dict[str, Any]:
    """Sample QRE summary for calculation tests."""
    return {
        "total_qre": Decimal("2500000"),
        "total_wages": Decimal("2000000"),
        "total_supplies": Decimal("300000"),
        "total_contract_research": Decimal("200000"),
        "total_basic_research": Decimal("0"),
    }


@pytest.fixture
def sample_historical_data() -> Dict[str, Any]:
    """Sample historical data for calculation tests."""
    return {
        "prior_year_1_qre": Decimal("2000000"),
        "prior_year_2_qre": Decimal("1800000"),
        "prior_year_3_qre": Decimal("1500000"),
        "fixed_base_percentage": Decimal("0.03"),
        "avg_gross_receipts_4_years": Decimal("50000000"),
    }


@pytest.fixture
def sample_four_part_test_result() -> Dict[str, Any]:
    """Sample 4-part test qualification result."""
    return {
        "permitted_purpose": {
            "score": Decimal("0.85"),
            "confidence": Decimal("0.90"),
            "evidence": ["Design document A", "Technical spec B"],
            "ai_reasoning": "Project clearly aimed at developing new functionality",
        },
        "technological_nature": {
            "score": Decimal("0.80"),
            "confidence": Decimal("0.85"),
            "evidence": ["Engineering notes", "Architecture diagrams"],
            "ai_reasoning": "Work involves computer science principles",
        },
        "elimination_of_uncertainty": {
            "score": Decimal("0.75"),
            "confidence": Decimal("0.80"),
            "evidence": ["Research log entries"],
            "ai_reasoning": "Documented uncertainty about feasibility",
        },
        "process_of_experimentation": {
            "score": Decimal("0.78"),
            "confidence": Decimal("0.82"),
            "evidence": ["Test results", "Iteration logs"],
            "ai_reasoning": "Systematic evaluation of alternatives",
        },
        "overall_score": Decimal("0.795"),
    }


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for AI tests."""
    return {
        "choices": [
            {
                "message": {
                    "content": """Based on the project documentation, the following analysis applies:

**Permitted Purpose**: The project aims to develop new software functionality. Score: 85%

**Technological Nature**: Work involves computer science and software engineering. Score: 80%

**Elimination of Uncertainty**: Documentation shows uncertainty about performance targets. Score: 75%

**Process of Experimentation**: Iterative development with systematic testing. Score: 78%

Overall qualification confidence: High"""
                }
            }
        ]
    }


# Markers for test categorization
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "golden: marks tests as golden-file tests"
    )
    config.addinivalue_line(
        "markers", "audit: marks tests as audit scenario tests"
    )
