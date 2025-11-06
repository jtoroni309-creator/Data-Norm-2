"""
Pytest configuration and shared fixtures for security service tests.
"""
import pytest
import base64
import os
from uuid import uuid4
from datetime import datetime, timedelta

# Import modules to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from encryption_service import EncryptionService, KeyPurpose, DataClassification
from audit_logging import AuditLogService, AuditEventType, AuditSeverity
from key_management import KeyManagementService, KeyType, KeyStatus, KeyUsage


@pytest.fixture
def master_key():
    """Generate a test master encryption key."""
    return os.urandom(32)  # 256-bit key


@pytest.fixture
def master_key_b64(master_key):
    """Base64-encoded master key for environment variable."""
    return base64.b64encode(master_key).decode()


@pytest.fixture
def encryption_service(master_key):
    """Create encryption service instance for testing."""
    return EncryptionService(master_key=master_key)


@pytest.fixture
def audit_log_service(encryption_service):
    """Create audit log service instance for testing."""
    return AuditLogService(encryption_service=encryption_service)


@pytest.fixture
def key_management_service(audit_log_service):
    """Create key management service instance for testing."""
    return KeyManagementService(audit_log_service=audit_log_service)


@pytest.fixture
def test_user_id():
    """Generate test user ID."""
    return uuid4()


@pytest.fixture
def test_tenant_id():
    """Generate test tenant ID."""
    return uuid4()


@pytest.fixture
def test_resource_id():
    """Generate test resource ID."""
    return uuid4()


@pytest.fixture
def sample_plaintext():
    """Sample plaintext data for encryption tests."""
    return "Sensitive PII data: SSN 123-45-6789"


@pytest.fixture
def sample_large_data():
    """Sample large binary data for envelope encryption tests."""
    return os.urandom(1024 * 100)  # 100KB of random data


@pytest.fixture
def audit_event_data(test_user_id, test_tenant_id, test_resource_id):
    """Sample audit event data."""
    return {
        "event_type": AuditEventType.DATA_CREATE,
        "user_id": test_user_id,
        "tenant_id": test_tenant_id,
        "resource_type": "engagement",
        "resource_id": test_resource_id,
        "action": "Created new engagement",
        "severity": AuditSeverity.INFO,
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0",
        "metadata": {"client": "Test Client"},
    }


@pytest.fixture
def mock_kms_provider():
    """Mock external KMS provider."""
    class MockKMSProvider:
        def generate_data_key(self, key_id):
            return (os.urandom(32), os.urandom(48))

        def encrypt(self, key_id, plaintext):
            return plaintext + b"_encrypted"

        def decrypt(self, key_id, ciphertext):
            return ciphertext.replace(b"_encrypted", b"")

    return MockKMSProvider()


@pytest.fixture(autouse=True)
def reset_env_vars(monkeypatch, master_key_b64):
    """Reset environment variables for each test."""
    monkeypatch.setenv("MASTER_ENCRYPTION_KEY", master_key_b64)
    yield
    monkeypatch.delenv("MASTER_ENCRYPTION_KEY", raising=False)
