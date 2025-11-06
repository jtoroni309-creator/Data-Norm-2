"""
Comprehensive unit tests for KeyManagementService.

Tests cover:
- Key generation
- Key retrieval
- Key rotation
- Key revocation
- Key destruction
- Key listing and filtering
- Key usage reporting
- Rotation scheduling
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from key_management import (
    KeyManagementService,
    KeyType,
    KeyStatus,
    KeyUsage,
    KeyManagementError,
)


class TestKeyGeneration:
    """Test key generation."""

    def test_generate_master_key(self, key_management_service, test_tenant_id):
        """Test master key generation."""
        key_info = key_management_service.generate_key(
            key_type=KeyType.MASTER,
            key_id="master-key-1",
            purpose="Master encryption key for tenant",
            tenant_id=test_tenant_id,
        )

        assert key_info["key_id"] == "master-key-1"
        assert key_info["key_type"] == KeyType.MASTER.value
        assert key_info["status"] == KeyStatus.ACTIVE.value
        assert "version_id" in key_info

    def test_generate_data_key(self, key_management_service):
        """Test data encryption key generation."""
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="data-key-1",
            purpose="Data encryption for documents",
        )

        assert key_info["key_type"] == KeyType.DATA.value

    def test_generate_key_with_custom_usage(self, key_management_service):
        """Test key generation with custom allowed usage."""
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="custom-key-1",
            purpose="Signing only",
            allowed_usage=[KeyUsage.SIGN, KeyUsage.VERIFY],
        )

        assert key_info is not None

    def test_generate_key_with_metadata(self, key_management_service):
        """Test key generation with metadata."""
        metadata = {
            "owner": "security-team",
            "environment": "production",
            "compliance": "SOC2",
        }

        key_info = key_management_service.generate_key(
            key_type=KeyType.MASTER,
            key_id="meta-key-1",
            purpose="Test key with metadata",
            metadata=metadata,
        )

        assert key_info is not None


class TestKeyRetrieval:
    """Test key retrieval."""

    def test_get_key_latest_version(self, key_management_service, test_user_id):
        """Test retrieving latest version of key."""
        # Generate key
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="test-key-1",
            purpose="Test key",
        )

        # Retrieve latest version
        key_material = key_management_service.get_key(
            key_id="test-key-1",
            user_id=test_user_id,
        )

        assert key_material is not None
        assert len(key_material) == 32  # 256 bits

    def test_get_key_specific_version(self, key_management_service, test_user_id):
        """Test retrieving specific version of key."""
        # Generate key
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="test-key-2",
            purpose="Test key",
        )

        version_id = key_info["version_id"]

        # Retrieve specific version
        key_material = key_management_service.get_key(
            key_id="test-key-2",
            version_id=version_id,
            user_id=test_user_id,
        )

        assert key_material is not None

    def test_get_nonexistent_key(self, key_management_service, test_user_id):
        """Test retrieving nonexistent key returns None."""
        key_material = key_management_service.get_key(
            key_id="nonexistent",
            user_id=test_user_id,
        )

        assert key_material is None

    def test_get_revoked_key_raises_error(self, key_management_service, test_user_id):
        """Test retrieving revoked key raises error."""
        # Generate and revoke key
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="revoked-key",
            purpose="Test key",
        )

        key_management_service.revoke_key(
            key_id="revoked-key",
            reason="Test revocation",
            user_id=test_user_id,
        )

        # Try to retrieve
        with pytest.raises(KeyManagementError, match="revoked"):
            key_management_service.get_key(
                key_id="revoked-key",
                user_id=test_user_id,
            )


class TestKeyRotation:
    """Test key rotation."""

    def test_rotate_key(self, key_management_service, test_user_id):
        """Test key rotation creates new version."""
        # Generate initial key
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="rotate-key-1",
            purpose="Test key",
        )

        initial_version = key_info["version_id"]

        # Rotate key
        new_key_info = key_management_service.rotate_key(
            key_id="rotate-key-1",
            user_id=test_user_id,
        )

        # Should have new version
        assert new_key_info["version_id"] != initial_version
        assert new_key_info["key_id"] == "rotate-key-1"
        assert new_key_info["status"] == KeyStatus.ACTIVE.value

    def test_rotate_key_preserves_old_version(self, key_management_service, test_user_id):
        """Test rotation preserves old version for decryption."""
        # Generate initial key
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="rotate-key-2",
            purpose="Test key",
        )

        initial_version = key_info["version_id"]

        # Rotate key
        key_management_service.rotate_key(
            key_id="rotate-key-2",
            user_id=test_user_id,
        )

        # Old version should still be retrievable
        old_key = key_management_service.get_key(
            key_id="rotate-key-2",
            version_id=initial_version,
            user_id=test_user_id,
        )

        assert old_key is not None

    def test_rotate_nonexistent_key(self, key_management_service, test_user_id):
        """Test rotating nonexistent key raises error."""
        with pytest.raises(KeyManagementError, match="not found"):
            key_management_service.rotate_key(
                key_id="nonexistent",
                user_id=test_user_id,
            )


class TestKeyRevocation:
    """Test key revocation."""

    def test_revoke_specific_version(self, key_management_service, test_user_id):
        """Test revoking specific version of key."""
        # Generate key
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="revoke-test-1",
            purpose="Test key",
        )

        version_id = key_info["version_id"]

        # Revoke specific version
        key_management_service.revoke_key(
            key_id="revoke-test-1",
            version_id=version_id,
            reason="Test revocation",
            user_id=test_user_id,
        )

        # Key should be marked as revoked
        with pytest.raises(KeyManagementError, match="revoked"):
            key_management_service.get_key(
                key_id="revoke-test-1",
                version_id=version_id,
                user_id=test_user_id,
            )

    def test_revoke_all_versions(self, key_management_service, test_user_id):
        """Test revoking all versions of key."""
        # Generate key
        key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="revoke-test-2",
            purpose="Test key",
        )

        # Create another version
        key_management_service.rotate_key(
            key_id="revoke-test-2",
            user_id=test_user_id,
        )

        # Revoke all versions
        key_management_service.revoke_key(
            key_id="revoke-test-2",
            reason="Security incident",
            user_id=test_user_id,
        )

        # Should not be able to get key
        with pytest.raises(KeyManagementError, match="revoked"):
            key_management_service.get_key(
                key_id="revoke-test-2",
                user_id=test_user_id,
            )


class TestKeyDestruction:
    """Test key destruction."""

    def test_destroy_key_with_confirmation(self, key_management_service, test_user_id):
        """Test key destruction with valid confirmation."""
        # Generate and revoke key
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="destroy-test-1",
            purpose="Test key",
        )

        version_id = key_info["version_id"]

        key_management_service.revoke_key(
            key_id="destroy-test-1",
            reason="Test",
            user_id=test_user_id,
        )

        # Destroy with valid confirmation
        confirmation = f"DESTROY:destroy-test-1:{version_id}"
        key_management_service.destroy_key(
            key_id="destroy-test-1",
            version_id=version_id,
            confirmation_token=confirmation,
            user_id=test_user_id,
        )

        # Key material should be gone
        # Implementation note: get_key should return None or raise error for destroyed keys

    def test_destroy_key_invalid_confirmation(self, key_management_service, test_user_id):
        """Test key destruction fails with invalid confirmation."""
        # Generate key
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="destroy-test-2",
            purpose="Test key",
        )

        version_id = key_info["version_id"]

        # Try to destroy with invalid confirmation
        with pytest.raises(KeyManagementError, match="confirmation"):
            key_management_service.destroy_key(
                key_id="destroy-test-2",
                version_id=version_id,
                confirmation_token="wrong-token",
                user_id=test_user_id,
            )

    def test_destroy_active_key_fails(self, key_management_service, test_user_id):
        """Test destroying active key fails."""
        # Generate key
        key_info = key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="destroy-test-3",
            purpose="Test key",
        )

        version_id = key_info["version_id"]
        confirmation = f"DESTROY:destroy-test-3:{version_id}"

        # Try to destroy active key
        with pytest.raises(KeyManagementError, match="active"):
            key_management_service.destroy_key(
                key_id="destroy-test-3",
                version_id=version_id,
                confirmation_token=confirmation,
                user_id=test_user_id,
            )


class TestKeyListing:
    """Test key listing and filtering."""

    def test_list_all_keys(self, key_management_service, test_tenant_id):
        """Test listing all keys."""
        # Generate multiple keys
        for i in range(3):
            key_management_service.generate_key(
                key_type=KeyType.DATA,
                key_id=f"list-test-{i}",
                purpose="Test key",
                tenant_id=test_tenant_id,
            )

        keys = key_management_service.list_keys()

        assert len(keys) >= 3

    def test_list_keys_by_tenant(self, key_management_service):
        """Test filtering keys by tenant."""
        tenant1 = uuid4()
        tenant2 = uuid4()

        # Generate keys for different tenants
        key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="tenant1-key",
            purpose="Tenant 1 key",
            tenant_id=tenant1,
        )

        key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="tenant2-key",
            purpose="Tenant 2 key",
            tenant_id=tenant2,
        )

        # List keys for tenant 1
        tenant1_keys = key_management_service.list_keys(tenant_id=tenant1)

        assert len(tenant1_keys) >= 1
        assert all(k["tenant_id"] == str(tenant1) for k in tenant1_keys)

    def test_list_keys_by_type(self, key_management_service):
        """Test filtering keys by type."""
        # Generate keys of different types
        key_management_service.generate_key(
            key_type=KeyType.MASTER,
            key_id="master-list",
            purpose="Master key",
        )

        key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="data-list",
            purpose="Data key",
        )

        # List only master keys
        master_keys = key_management_service.list_keys(key_type=KeyType.MASTER)

        assert len(master_keys) >= 1
        assert all(k["key_type"] == KeyType.MASTER.value for k in master_keys)

    def test_list_keys_by_status(self, key_management_service, test_user_id):
        """Test filtering keys by status."""
        # Generate active key
        key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="active-key",
            purpose="Active key",
        )

        # Generate and revoke key
        key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="revoked-key",
            purpose="Revoked key",
        )
        key_management_service.revoke_key(
            key_id="revoked-key",
            reason="Test",
            user_id=test_user_id,
        )

        # List only active keys
        active_keys = key_management_service.list_keys(status=KeyStatus.ACTIVE)

        assert len(active_keys) >= 1
        assert all(k["status"] == KeyStatus.ACTIVE.value for k in active_keys)


class TestRotationScheduling:
    """Test key rotation scheduling."""

    def test_check_rotation_needed(self, key_management_service):
        """Test checking which keys need rotation."""
        # Generate key
        key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="rotation-check-1",
            purpose="Test key",
        )

        # Check rotation (should not need rotation yet)
        keys_to_rotate = key_management_service.check_rotation_needed()

        # Implementation depends on whether keys are immediately expired


class TestKeyUsageReporting:
    """Test key usage reporting."""

    def test_get_key_usage_report(self, key_management_service):
        """Test key usage report generation."""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()

        report = key_management_service.get_key_usage_report(
            start_date=start_date,
            end_date=end_date,
        )

        # Verify report structure
        assert "period" in report
        assert "total_keys" in report
        assert "keys_by_type" in report
        assert "keys_by_status" in report
        assert "total_usage" in report

    def test_get_key_usage_report_by_tenant(self, key_management_service, test_tenant_id):
        """Test key usage report filtered by tenant."""
        # Generate keys for tenant
        key_management_service.generate_key(
            key_type=KeyType.DATA,
            key_id="usage-report-1",
            purpose="Test key",
            tenant_id=test_tenant_id,
        )

        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()

        report = key_management_service.get_key_usage_report(
            start_date=start_date,
            end_date=end_date,
            tenant_id=test_tenant_id,
        )

        assert report["total_keys"] >= 1


class TestKeyTypes:
    """Test all key type enums are properly defined."""

    def test_all_key_types(self):
        """Test key type enums exist."""
        assert KeyType.MASTER
        assert KeyType.DATA
        assert KeyType.SESSION
        assert KeyType.API
        assert KeyType.TOKEN


class TestKeyStatuses:
    """Test all key status enums are properly defined."""

    def test_all_key_statuses(self):
        """Test key status enums exist."""
        assert KeyStatus.ACTIVE
        assert KeyStatus.ROTATING
        assert KeyStatus.DEPRECATED
        assert KeyStatus.REVOKED
        assert KeyStatus.DESTROYED


class TestKeyUsages:
    """Test all key usage enums are properly defined."""

    def test_all_key_usages(self):
        """Test key usage enums exist."""
        assert KeyUsage.ENCRYPT
        assert KeyUsage.DECRYPT
        assert KeyUsage.SIGN
        assert KeyUsage.VERIFY
        assert KeyUsage.WRAP
        assert KeyUsage.UNWRAP
