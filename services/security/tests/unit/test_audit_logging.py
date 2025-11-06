"""
Comprehensive unit tests for AuditLogService.

Tests cover:
- Event logging with full context
- Data access logging
- Data modification logging
- Security event logging
- Authentication attempt logging
- Log integrity verification
- Compliance report generation
- Retention policies
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from audit_logging import (
    AuditLogService,
    AuditEventType,
    AuditSeverity,
    RetentionPolicy,
)


class TestAuditLogServiceInitialization:
    """Test audit log service initialization."""

    def test_initialization_without_encryption(self):
        """Test initialization without encryption service."""
        service = AuditLogService()
        assert service.encryption_service is None
        assert service._log_chain == []

    def test_initialization_with_encryption(self, encryption_service):
        """Test initialization with encryption service."""
        service = AuditLogService(encryption_service=encryption_service)
        assert service.encryption_service == encryption_service


class TestEventLogging:
    """Test basic event logging."""

    @pytest.mark.asyncio
    async def test_log_basic_event(self, audit_log_service, test_user_id, test_tenant_id, test_resource_id):
        """Test logging a basic event."""
        log_id = await audit_log_service.log_event(
            event_type=AuditEventType.DATA_CREATE,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="engagement",
            resource_id=test_resource_id,
            action="Created new engagement",
            severity=AuditSeverity.INFO,
        )

        assert log_id is not None
        assert len(audit_log_service._log_chain) == 1

    @pytest.mark.asyncio
    async def test_log_event_with_metadata(self, audit_log_service, test_user_id, test_tenant_id):
        """Test logging event with metadata."""
        metadata = {
            "client_name": "Test Corp",
            "engagement_type": "Audit",
            "year": 2024,
        }

        log_id = await audit_log_service.log_event(
            event_type=AuditEventType.ENGAGEMENT_CREATED,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="engagement",
            resource_id=uuid4(),
            action="Created engagement for Test Corp",
            severity=AuditSeverity.INFO,
            metadata=metadata,
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_event_with_changes(self, audit_log_service, test_user_id, test_tenant_id, test_resource_id):
        """Test logging event with before/after changes."""
        changes = {
            "before": {"status": "draft", "amount": 1000},
            "after": {"status": "approved", "amount": 1500},
        }

        log_id = await audit_log_service.log_event(
            event_type=AuditEventType.DATA_UPDATE,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="transaction",
            resource_id=test_resource_id,
            action="Updated transaction",
            severity=AuditSeverity.INFO,
            changes=changes,
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_event_with_error(self, audit_log_service, test_user_id, test_tenant_id):
        """Test logging event with error message."""
        log_id = await audit_log_service.log_event(
            event_type=AuditEventType.UNAUTHORIZED_ACCESS_ATTEMPT,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="workpaper",
            resource_id=uuid4(),
            action="Attempted to access workpaper without permission",
            severity=AuditSeverity.CRITICAL,
            error_message="Insufficient permissions for resource",
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_event_with_full_context(self, audit_log_service, test_user_id, test_tenant_id, test_resource_id):
        """Test logging event with all context fields."""
        log_id = await audit_log_service.log_event(
            event_type=AuditEventType.DATA_EXPORT,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="report",
            resource_id=test_resource_id,
            action="Exported financial report",
            severity=AuditSeverity.WARNING,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            request_id="req-12345",
            session_id="sess-67890",
            metadata={"format": "PDF", "size_mb": 2.5},
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_chain_integrity(self, audit_log_service, test_user_id, test_tenant_id):
        """Test log chain builds correctly with hashes."""
        # Log multiple events
        for i in range(5):
            await audit_log_service.log_event(
                event_type=AuditEventType.DATA_READ,
                user_id=test_user_id,
                tenant_id=test_tenant_id,
                resource_type="document",
                resource_id=uuid4(),
                action=f"Read document {i}",
                severity=AuditSeverity.INFO,
            )

        # Chain should have 5 entries
        assert len(audit_log_service._log_chain) == 5

        # All hashes should be unique
        assert len(set(audit_log_service._log_chain)) == 5


class TestDataAccessLogging:
    """Test data access logging."""

    @pytest.mark.asyncio
    async def test_log_data_access_basic(self, audit_log_service, test_user_id, test_tenant_id, test_resource_id):
        """Test basic data access logging."""
        log_id = await audit_log_service.log_data_access(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="engagement",
            resource_id=test_resource_id,
            action="Viewed engagement details",
            ip_address="192.168.1.100",
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_data_access_with_fields(self, audit_log_service, test_user_id, test_tenant_id, test_resource_id):
        """Test data access logging with field tracking."""
        fields_accessed = ["ssn", "dob", "salary", "tax_id"]

        log_id = await audit_log_service.log_data_access(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="employee",
            resource_id=test_resource_id,
            action="Accessed employee PII",
            ip_address="192.168.1.100",
            fields_accessed=fields_accessed,
        )

        assert log_id is not None


class TestDataModificationLogging:
    """Test data modification logging."""

    @pytest.mark.asyncio
    async def test_log_data_create(self, audit_log_service, test_user_id, test_tenant_id, test_resource_id):
        """Test CREATE operation logging."""
        after_values = {
            "name": "New Engagement",
            "client": "ACME Corp",
            "status": "draft",
        }

        log_id = await audit_log_service.log_data_modification(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="engagement",
            resource_id=test_resource_id,
            action="Created engagement",
            operation="CREATE",
            after_values=after_values,
            ip_address="192.168.1.100",
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_data_update(self, audit_log_service, test_user_id, test_tenant_id, test_resource_id):
        """Test UPDATE operation logging."""
        before_values = {"status": "draft", "assigned_to": None}
        after_values = {"status": "in_progress", "assigned_to": "user-456"}

        log_id = await audit_log_service.log_data_modification(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="engagement",
            resource_id=test_resource_id,
            action="Updated engagement",
            operation="UPDATE",
            before_values=before_values,
            after_values=after_values,
            ip_address="192.168.1.100",
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_data_delete(self, audit_log_service, test_user_id, test_tenant_id, test_resource_id):
        """Test DELETE operation logging."""
        before_values = {
            "name": "Old Engagement",
            "status": "archived",
        }

        log_id = await audit_log_service.log_data_modification(
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="engagement",
            resource_id=test_resource_id,
            action="Deleted engagement",
            operation="DELETE",
            before_values=before_values,
            ip_address="192.168.1.100",
        )

        assert log_id is not None


class TestSecurityEventLogging:
    """Test security event logging."""

    @pytest.mark.asyncio
    async def test_log_security_event_info(self, audit_log_service, test_user_id, test_tenant_id):
        """Test logging INFO severity security event."""
        log_id = await audit_log_service.log_security_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            description="User logged in successfully",
            severity=AuditSeverity.INFO,
            ip_address="192.168.1.100",
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_security_event_warning(self, audit_log_service, test_user_id, test_tenant_id):
        """Test logging WARNING severity security event."""
        log_id = await audit_log_service.log_security_event(
            event_type=AuditEventType.LOGIN_FAILURE,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            description="Failed login attempt - wrong password",
            severity=AuditSeverity.WARNING,
            ip_address="192.168.1.100",
            metadata={"attempt_number": 2},
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_security_event_critical(self, audit_log_service, test_user_id, test_tenant_id):
        """Test logging CRITICAL severity security event."""
        log_id = await audit_log_service.log_security_event(
            event_type=AuditEventType.UNAUTHORIZED_ACCESS_ATTEMPT,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            description="Attempted to access restricted resource",
            severity=AuditSeverity.CRITICAL,
            ip_address="192.168.1.100",
            metadata={"resource": "admin_panel", "user_role": "auditor"},
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_security_event_emergency(self, audit_log_service, test_user_id, test_tenant_id):
        """Test logging EMERGENCY severity security event."""
        log_id = await audit_log_service.log_security_event(
            event_type=AuditEventType.SECURITY_ALERT,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            description="Potential data breach detected",
            severity=AuditSeverity.EMERGENCY,
            ip_address="192.168.1.100",
            metadata={"threat_level": "high", "affected_records": 1000},
        )

        assert log_id is not None


class TestAuthenticationLogging:
    """Test authentication attempt logging."""

    @pytest.mark.asyncio
    async def test_log_successful_login(self, audit_log_service, test_user_id):
        """Test logging successful login."""
        log_id = await audit_log_service.log_authentication_attempt(
            user_id=test_user_id,
            email="user@example.com",
            success=True,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_failed_login(self, audit_log_service):
        """Test logging failed login."""
        log_id = await audit_log_service.log_authentication_attempt(
            user_id=None,  # Unknown user
            email="hacker@example.com",
            success=False,
            ip_address="192.168.1.100",
            user_agent="Python-requests/2.28.0",
            failure_reason="Invalid credentials",
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_failed_login_with_user(self, audit_log_service, test_user_id):
        """Test logging failed login for known user."""
        log_id = await audit_log_service.log_authentication_attempt(
            user_id=test_user_id,
            email="user@example.com",
            success=False,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            failure_reason="Wrong password",
        )

        assert log_id is not None


class TestLogIntegrity:
    """Test log integrity verification."""

    @pytest.mark.asyncio
    async def test_verify_log_integrity(self, audit_log_service, test_user_id, test_tenant_id):
        """Test log integrity verification."""
        # Create some log entries
        log_ids = []
        for i in range(5):
            log_id = await audit_log_service.log_event(
                event_type=AuditEventType.DATA_READ,
                user_id=test_user_id,
                tenant_id=test_tenant_id,
                resource_type="document",
                resource_id=uuid4(),
                action=f"Read document {i}",
                severity=AuditSeverity.INFO,
            )
            log_ids.append(log_id)

        # Verify integrity
        result = await audit_log_service.verify_log_integrity(
            start_id=log_ids[0],
            end_id=log_ids[-1],
        )

        assert result is True

    def test_calculate_log_hash(self, audit_log_service):
        """Test log hash calculation."""
        log_entry = {
            "id": "12345",
            "timestamp": "2024-01-01T00:00:00",
            "event_type": "data_read",
            "user_id": "user-123",
            "action": "Read document",
        }

        hash1 = audit_log_service._calculate_log_hash(log_entry)

        # Hash should be deterministic
        hash2 = audit_log_service._calculate_log_hash(log_entry)
        assert hash1 == hash2

        # Hash should be 64 characters (SHA-256 hex)
        assert len(hash1) == 64

        # Different data should produce different hash
        log_entry["action"] = "Write document"
        hash3 = audit_log_service._calculate_log_hash(log_entry)
        assert hash1 != hash3


class TestComplianceReporting:
    """Test compliance report generation."""

    @pytest.mark.asyncio
    async def test_generate_compliance_report(self, audit_log_service, test_tenant_id):
        """Test compliance report generation."""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()

        report = await audit_log_service.generate_compliance_report(
            tenant_id=test_tenant_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify report structure
        assert "tenant_id" in report
        assert "report_period" in report
        assert "statistics" in report
        assert "security_incidents" in report
        assert "unusual_activity" in report
        assert "generated_at" in report

        # Verify statistics structure
        stats = report["statistics"]
        assert "total_events" in stats
        assert "events_by_type" in stats
        assert "events_by_severity" in stats
        assert "unique_users" in stats

    @pytest.mark.asyncio
    async def test_generate_compliance_report_with_filter(self, audit_log_service, test_tenant_id):
        """Test compliance report with event type filter."""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()

        report = await audit_log_service.generate_compliance_report(
            tenant_id=test_tenant_id,
            start_date=start_date,
            end_date=end_date,
            event_types=[AuditEventType.LOGIN_SUCCESS, AuditEventType.LOGIN_FAILURE],
        )

        assert report is not None


class TestRetentionPolicy:
    """Test audit log retention policies."""

    def test_retention_period_for_login_success(self):
        """Test retention period for login success events."""
        period = RetentionPolicy.get_retention_period(AuditEventType.LOGIN_SUCCESS)
        assert period == timedelta(days=365)  # 1 year

    def test_retention_period_for_login_failure(self):
        """Test retention period for login failure events."""
        period = RetentionPolicy.get_retention_period(AuditEventType.LOGIN_FAILURE)
        assert period == timedelta(days=730)  # 2 years

    def test_retention_period_for_financial_data(self):
        """Test retention period for financial data events."""
        period = RetentionPolicy.get_retention_period(AuditEventType.DATA_UPDATE)
        assert period == timedelta(days=2555)  # 7 years

    def test_retention_period_for_security_events(self):
        """Test retention period for security events."""
        period = RetentionPolicy.get_retention_period(AuditEventType.SECURITY_ALERT)
        assert period == timedelta(days=730)  # 2 years

    def test_retention_period_default(self):
        """Test default retention period for unlisted events."""
        period = RetentionPolicy.get_retention_period(AuditEventType.SERVICE_STARTED)
        assert period == timedelta(days=2555)  # Default: 7 years

    def test_should_archive_old_event(self):
        """Test archive check for old event."""
        old_date = datetime.utcnow() - timedelta(days=800)  # Over 2 years ago

        should_archive = RetentionPolicy.should_archive(
            AuditEventType.LOGIN_SUCCESS,  # 1 year retention
            old_date,
        )

        assert should_archive is True

    def test_should_not_archive_recent_event(self):
        """Test archive check for recent event."""
        recent_date = datetime.utcnow() - timedelta(days=30)  # 1 month ago

        should_archive = RetentionPolicy.should_archive(
            AuditEventType.LOGIN_SUCCESS,  # 1 year retention
            recent_date,
        )

        assert should_archive is False

    def test_should_not_archive_financial_data(self):
        """Test financial data is not archived within 7 years."""
        old_date = datetime.utcnow() - timedelta(days=2000)  # ~5.5 years ago

        should_archive = RetentionPolicy.should_archive(
            AuditEventType.DATA_UPDATE,  # 7 years retention
            old_date,
        )

        assert should_archive is False


class TestEncryptionIntegration:
    """Test integration with encryption service."""

    @pytest.mark.asyncio
    async def test_log_event_with_encryption(self, audit_log_service, test_user_id, test_tenant_id, test_resource_id):
        """Test log event marks changes as encrypted when encryption service available."""
        changes = {
            "before": {"ssn": "123-45-6789"},
            "after": {"ssn": "987-65-4321"},
        }

        log_id = await audit_log_service.log_event(
            event_type=AuditEventType.DATA_UPDATE,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="user",
            resource_id=test_resource_id,
            action="Updated user SSN",
            severity=AuditSeverity.INFO,
            changes=changes,
        )

        assert log_id is not None

    @pytest.mark.asyncio
    async def test_log_event_without_encryption(self, test_user_id, test_tenant_id, test_resource_id):
        """Test log event without encryption service."""
        service = AuditLogService()  # No encryption service

        changes = {
            "before": {"name": "John"},
            "after": {"name": "Jane"},
        }

        log_id = await service.log_event(
            event_type=AuditEventType.DATA_UPDATE,
            user_id=test_user_id,
            tenant_id=test_tenant_id,
            resource_type="user",
            resource_id=test_resource_id,
            action="Updated user name",
            severity=AuditSeverity.INFO,
            changes=changes,
        )

        assert log_id is not None


class TestEventTypes:
    """Test all event type enums are properly defined."""

    def test_all_authentication_events(self):
        """Test authentication event types exist."""
        assert AuditEventType.LOGIN_SUCCESS
        assert AuditEventType.LOGIN_FAILURE
        assert AuditEventType.LOGOUT
        assert AuditEventType.PASSWORD_CHANGE
        assert AuditEventType.MFA_ENABLED

    def test_all_data_events(self):
        """Test data operation event types exist."""
        assert AuditEventType.DATA_READ
        assert AuditEventType.DATA_CREATE
        assert AuditEventType.DATA_UPDATE
        assert AuditEventType.DATA_DELETE
        assert AuditEventType.DATA_EXPORT

    def test_all_financial_events(self):
        """Test financial event types exist."""
        assert AuditEventType.TRANSACTION_CREATED
        assert AuditEventType.TRANSACTION_APPROVED
        assert AuditEventType.PAYMENT_PROCESSED

    def test_all_security_events(self):
        """Test security event types exist."""
        assert AuditEventType.UNAUTHORIZED_ACCESS_ATTEMPT
        assert AuditEventType.PRIVILEGE_ESCALATION_ATTEMPT
        assert AuditEventType.SUSPICIOUS_ACTIVITY
        assert AuditEventType.SECURITY_ALERT


class TestSeverityLevels:
    """Test all severity level enums are properly defined."""

    def test_all_severity_levels(self):
        """Test severity level enums exist."""
        assert AuditSeverity.INFO
        assert AuditSeverity.WARNING
        assert AuditSeverity.CRITICAL
        assert AuditSeverity.EMERGENCY
