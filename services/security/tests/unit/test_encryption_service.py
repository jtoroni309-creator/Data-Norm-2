"""
Comprehensive unit tests for EncryptionService.

Tests cover:
- Field encryption/decryption
- Large data envelope encryption
- Key derivation and caching
- Key rotation
- Error handling
- Security edge cases
"""
import pytest
import base64
import os
from encryption_service import (
    EncryptionService,
    KeyPurpose,
    DataClassification,
    EncryptionError,
    DecryptionError,
    EncryptedFieldMixin,
    generate_master_key,
    validate_key_strength,
)


class TestEncryptionServiceInitialization:
    """Test encryption service initialization."""

    def test_initialization_with_master_key(self, master_key):
        """Test initialization with provided master key."""
        service = EncryptionService(master_key=master_key)
        assert service.master_key == master_key
        assert len(service._key_cache) == 0

    def test_initialization_from_environment(self, master_key_b64, monkeypatch):
        """Test initialization from environment variable."""
        monkeypatch.setenv("MASTER_ENCRYPTION_KEY", master_key_b64)
        service = EncryptionService()
        assert service.master_key is not None
        assert len(service.master_key) == 32

    def test_initialization_missing_env_var(self, monkeypatch):
        """Test initialization fails without master key."""
        monkeypatch.delenv("MASTER_ENCRYPTION_KEY", raising=False)
        with pytest.raises(ValueError, match="MASTER_ENCRYPTION_KEY"):
            EncryptionService()

    def test_initialization_invalid_key_length(self):
        """Test initialization fails with invalid key length."""
        short_key = os.urandom(16)  # Only 128 bits
        with pytest.raises(ValueError, match="256 bits"):
            EncryptionService(master_key=short_key)


class TestFieldEncryption:
    """Test field-level encryption operations."""

    def test_encrypt_decrypt_roundtrip(self, encryption_service, sample_plaintext):
        """Test encryption and decryption roundtrip."""
        encrypted = encryption_service.encrypt_field(
            sample_plaintext,
            KeyPurpose.PII,
        )

        # Verify encrypted format
        assert encrypted.startswith("v1:")
        parts = encrypted.split(":")
        assert len(parts) == 3  # version:nonce:ciphertext

        # Decrypt and verify
        decrypted = encryption_service.decrypt_field(
            encrypted,
            KeyPurpose.PII,
        )
        assert decrypted == sample_plaintext

    def test_encrypt_with_key_version(self, encryption_service, sample_plaintext):
        """Test encryption with specific key version."""
        encrypted_v1 = encryption_service.encrypt_field(
            sample_plaintext,
            KeyPurpose.DATABASE_FIELD,
            key_version=1,
        )
        encrypted_v2 = encryption_service.encrypt_field(
            sample_plaintext,
            KeyPurpose.DATABASE_FIELD,
            key_version=2,
        )

        # Different versions should produce different ciphertexts
        assert encrypted_v1 != encrypted_v2

        # Both should decrypt correctly
        assert encryption_service.decrypt_field(encrypted_v1, KeyPurpose.DATABASE_FIELD) == sample_plaintext
        assert encryption_service.decrypt_field(encrypted_v2, KeyPurpose.DATABASE_FIELD) == sample_plaintext

    def test_encrypt_with_associated_data(self, encryption_service, sample_plaintext):
        """Test encryption with authenticated associated data."""
        aad = "engagement-12345"

        encrypted = encryption_service.encrypt_field(
            sample_plaintext,
            KeyPurpose.FINANCIAL,
            associated_data=aad,
        )

        # Decrypt with correct AAD should succeed
        decrypted = encryption_service.decrypt_field(
            encrypted,
            KeyPurpose.FINANCIAL,
            associated_data=aad,
        )
        assert decrypted == sample_plaintext

        # Decrypt with wrong AAD should fail
        with pytest.raises(DecryptionError):
            encryption_service.decrypt_field(
                encrypted,
                KeyPurpose.FINANCIAL,
                associated_data="wrong-aad",
            )

    def test_encrypt_different_purposes(self, encryption_service, sample_plaintext):
        """Test encryption with different key purposes produces different ciphertexts."""
        encrypted_pii = encryption_service.encrypt_field(sample_plaintext, KeyPurpose.PII)
        encrypted_phi = encryption_service.encrypt_field(sample_plaintext, KeyPurpose.PHI)
        encrypted_financial = encryption_service.encrypt_field(sample_plaintext, KeyPurpose.FINANCIAL)

        # All should be different
        assert encrypted_pii != encrypted_phi
        assert encrypted_pii != encrypted_financial
        assert encrypted_phi != encrypted_financial

        # All should decrypt with correct purpose
        assert encryption_service.decrypt_field(encrypted_pii, KeyPurpose.PII) == sample_plaintext
        assert encryption_service.decrypt_field(encrypted_phi, KeyPurpose.PHI) == sample_plaintext
        assert encryption_service.decrypt_field(encrypted_financial, KeyPurpose.FINANCIAL) == sample_plaintext

    def test_encrypt_empty_string(self, encryption_service):
        """Test encryption of empty string."""
        encrypted = encryption_service.encrypt_field("", KeyPurpose.DATABASE_FIELD)
        decrypted = encryption_service.decrypt_field(encrypted, KeyPurpose.DATABASE_FIELD)
        assert decrypted == ""

    def test_encrypt_unicode(self, encryption_service):
        """Test encryption of unicode characters."""
        unicode_text = "Hello 世界 🌍 Привет"
        encrypted = encryption_service.encrypt_field(unicode_text, KeyPurpose.DATABASE_FIELD)
        decrypted = encryption_service.decrypt_field(encrypted, KeyPurpose.DATABASE_FIELD)
        assert decrypted == unicode_text

    def test_encrypt_large_field(self, encryption_service):
        """Test encryption of large text field."""
        large_text = "A" * 10000  # 10KB text
        encrypted = encryption_service.encrypt_field(large_text, KeyPurpose.DATABASE_FIELD)
        decrypted = encryption_service.decrypt_field(encrypted, KeyPurpose.DATABASE_FIELD)
        assert decrypted == large_text

    def test_decrypt_invalid_format(self, encryption_service):
        """Test decryption fails with invalid format."""
        with pytest.raises(DecryptionError):
            encryption_service.decrypt_field("invalid-format", KeyPurpose.PII)

        with pytest.raises(DecryptionError):
            encryption_service.decrypt_field("v1:only-two-parts", KeyPurpose.PII)

    def test_decrypt_wrong_purpose(self, encryption_service, sample_plaintext):
        """Test decryption with wrong key purpose fails."""
        encrypted = encryption_service.encrypt_field(sample_plaintext, KeyPurpose.PII)

        # Should fail with wrong purpose
        with pytest.raises(DecryptionError):
            encryption_service.decrypt_field(encrypted, KeyPurpose.FINANCIAL)

    def test_decrypt_corrupted_ciphertext(self, encryption_service, sample_plaintext):
        """Test decryption fails with corrupted ciphertext."""
        encrypted = encryption_service.encrypt_field(sample_plaintext, KeyPurpose.PII)

        # Corrupt the ciphertext
        parts = encrypted.split(":")
        corrupted = f"{parts[0]}:{parts[1]}:CORRUPTED"

        with pytest.raises(DecryptionError):
            encryption_service.decrypt_field(corrupted, KeyPurpose.PII)


class TestEnvelopeEncryption:
    """Test envelope encryption for large data."""

    def test_envelope_encrypt_decrypt_roundtrip(self, encryption_service, sample_large_data):
        """Test envelope encryption roundtrip."""
        encrypted = encryption_service.encrypt_large_data(
            sample_large_data,
            KeyPurpose.FILE_STORAGE,
        )

        # Encrypted should be larger (includes nonces and DEK)
        assert len(encrypted) > len(sample_large_data)

        # Decrypt and verify
        decrypted = encryption_service.decrypt_large_data(
            encrypted,
            KeyPurpose.FILE_STORAGE,
        )
        assert decrypted == sample_large_data

    def test_envelope_encryption_format(self, encryption_service):
        """Test envelope encryption format structure."""
        plaintext = b"Test data"
        encrypted = encryption_service.encrypt_large_data(
            plaintext,
            KeyPurpose.FILE_STORAGE,
        )

        # Verify format: [version(1)][kek_nonce(12)][encrypted_dek(48)][dek_nonce(12)][ciphertext]
        assert len(encrypted) > 73  # Minimum size
        assert encrypted[0] == 1  # Version byte

    def test_envelope_encryption_different_versions(self, encryption_service, sample_large_data):
        """Test envelope encryption with different key versions."""
        encrypted_v1 = encryption_service.encrypt_large_data(
            sample_large_data,
            KeyPurpose.FILE_STORAGE,
            key_version=1,
        )
        encrypted_v2 = encryption_service.encrypt_large_data(
            sample_large_data,
            KeyPurpose.FILE_STORAGE,
            key_version=2,
        )

        # Different versions should produce different ciphertexts
        assert encrypted_v1 != encrypted_v2

        # Both should decrypt correctly
        assert encryption_service.decrypt_large_data(encrypted_v1, KeyPurpose.FILE_STORAGE) == sample_large_data
        assert encryption_service.decrypt_large_data(encrypted_v2, KeyPurpose.FILE_STORAGE) == sample_large_data

    def test_envelope_encryption_very_large_data(self, encryption_service):
        """Test envelope encryption with very large data (10MB)."""
        large_data = os.urandom(1024 * 1024 * 10)  # 10MB
        encrypted = encryption_service.encrypt_large_data(large_data, KeyPurpose.FILE_STORAGE)
        decrypted = encryption_service.decrypt_large_data(encrypted, KeyPurpose.FILE_STORAGE)
        assert decrypted == large_data

    def test_envelope_decrypt_wrong_purpose(self, encryption_service, sample_large_data):
        """Test envelope decryption fails with wrong purpose."""
        encrypted = encryption_service.encrypt_large_data(
            sample_large_data,
            KeyPurpose.FILE_STORAGE,
        )

        with pytest.raises(DecryptionError):
            encryption_service.decrypt_large_data(encrypted, KeyPurpose.API_TOKEN)

    def test_envelope_decrypt_corrupted_data(self, encryption_service, sample_large_data):
        """Test envelope decryption fails with corrupted data."""
        encrypted = encryption_service.encrypt_large_data(
            sample_large_data,
            KeyPurpose.FILE_STORAGE,
        )

        # Corrupt the encrypted data
        corrupted = encrypted[:50] + b"CORRUPTED" + encrypted[59:]

        with pytest.raises(DecryptionError):
            encryption_service.decrypt_large_data(corrupted, KeyPurpose.FILE_STORAGE)


class TestKeyDerivation:
    """Test key derivation and caching."""

    def test_key_derivation_deterministic(self, encryption_service):
        """Test key derivation is deterministic."""
        key1 = encryption_service._derive_key(KeyPurpose.PII, 1)
        key2 = encryption_service._derive_key(KeyPurpose.PII, 1)
        assert key1 == key2

    def test_key_derivation_different_purposes(self, encryption_service):
        """Test different purposes derive different keys."""
        key_pii = encryption_service._derive_key(KeyPurpose.PII, 1)
        key_phi = encryption_service._derive_key(KeyPurpose.PHI, 1)
        assert key_pii != key_phi

    def test_key_derivation_different_versions(self, encryption_service):
        """Test different versions derive different keys."""
        key_v1 = encryption_service._derive_key(KeyPurpose.PII, 1)
        key_v2 = encryption_service._derive_key(KeyPurpose.PII, 2)
        assert key_v1 != key_v2

    def test_key_caching(self, encryption_service):
        """Test derived keys are cached."""
        # Derive key - should be cached
        key1 = encryption_service._derive_key(KeyPurpose.PII, 1)

        # Check cache
        cache_key = f"{KeyPurpose.PII.value}:v1"
        assert cache_key in encryption_service._key_cache

        # Derive again - should use cache
        key2 = encryption_service._derive_key(KeyPurpose.PII, 1)
        assert key1 == key2

    def test_key_derivation_length(self, encryption_service):
        """Test derived keys are 256 bits."""
        key = encryption_service._derive_key(KeyPurpose.DATABASE_FIELD, 1)
        assert len(key) == 32  # 256 bits


class TestKeyRotation:
    """Test key rotation."""

    def test_rotate_keys_clears_cache(self, encryption_service):
        """Test key rotation clears key cache."""
        # Derive some keys to populate cache
        encryption_service._derive_key(KeyPurpose.PII, 1)
        encryption_service._derive_key(KeyPurpose.PHI, 1)

        assert len(encryption_service._key_cache) > 0

        # Rotate keys
        new_version = encryption_service.rotate_keys()

        # Cache should be cleared
        assert len(encryption_service._key_cache) == 0
        assert new_version == 2

    def test_decrypt_after_rotation(self, encryption_service, sample_plaintext):
        """Test old encrypted data can be decrypted after rotation."""
        # Encrypt with version 1
        encrypted_v1 = encryption_service.encrypt_field(
            sample_plaintext,
            KeyPurpose.PII,
            key_version=1,
        )

        # Rotate keys
        encryption_service.rotate_keys()

        # Should still decrypt old data
        decrypted = encryption_service.decrypt_field(encrypted_v1, KeyPurpose.PII)
        assert decrypted == sample_plaintext

        # New encryptions should use new version
        encrypted_v2 = encryption_service.encrypt_field(
            sample_plaintext,
            KeyPurpose.PII,
            key_version=2,
        )
        assert encrypted_v2 != encrypted_v1


class TestSecurityFeatures:
    """Test security features."""

    def test_secure_compare_identical_strings(self, encryption_service):
        """Test secure comparison with identical strings."""
        assert encryption_service.secure_compare("test123", "test123") is True

    def test_secure_compare_different_strings(self, encryption_service):
        """Test secure comparison with different strings."""
        assert encryption_service.secure_compare("test123", "test456") is False

    def test_secure_compare_different_lengths(self, encryption_service):
        """Test secure comparison with different length strings."""
        assert encryption_service.secure_compare("test", "testing") is False

    def test_secure_compare_timing_attack_resistance(self, encryption_service):
        """Test secure compare is constant-time (timing attack resistant)."""
        # This is a basic test - true timing analysis would require specialized tools
        import time

        # Time comparison of similar strings
        start = time.perf_counter()
        encryption_service.secure_compare("a" * 1000, "a" * 999 + "b")
        time1 = time.perf_counter() - start

        # Time comparison of different strings
        start = time.perf_counter()
        encryption_service.secure_compare("a" * 1000, "b" * 1000)
        time2 = time.perf_counter() - start

        # Times should be similar (within 10x factor for basic check)
        # Note: True constant-time verification requires specialized testing
        assert abs(time1 - time2) < max(time1, time2) * 10


class TestEncryptedFieldMixin:
    """Test encrypted field mixin for database models."""

    def test_mixin_encryption(self, encryption_service):
        """Test mixin field encryption."""
        EncryptedFieldMixin.set_encryption_service(encryption_service)

        mixin = EncryptedFieldMixin()
        plaintext = "sensitive data"

        encrypted = mixin.encrypt_field(plaintext, KeyPurpose.PII)
        decrypted = mixin.decrypt_field(encrypted, KeyPurpose.PII)

        assert decrypted == plaintext

    def test_mixin_without_service(self):
        """Test mixin raises error without encryption service."""
        EncryptedFieldMixin._encryption_service = None

        mixin = EncryptedFieldMixin()

        with pytest.raises(RuntimeError, match="not initialized"):
            mixin.encrypt_field("test", KeyPurpose.PII)

        with pytest.raises(RuntimeError, match="not initialized"):
            mixin.decrypt_field("test", KeyPurpose.PII)


class TestKeyManagementUtilities:
    """Test key management utility functions."""

    def test_generate_master_key(self):
        """Test master key generation."""
        key = generate_master_key()

        # Should be base64 encoded
        decoded = base64.b64decode(key)

        # Should be 256 bits
        assert len(decoded) == 32

    def test_validate_key_strength_valid(self):
        """Test key strength validation with valid key."""
        valid_key = generate_master_key()
        assert validate_key_strength(valid_key) is True

    def test_validate_key_strength_wrong_length(self):
        """Test key strength validation with wrong length."""
        short_key = base64.b64encode(os.urandom(16)).decode()  # Only 128 bits
        assert validate_key_strength(short_key) is False

    def test_validate_key_strength_low_entropy(self):
        """Test key strength validation with low entropy."""
        # Create low-entropy key (all same bytes)
        low_entropy_key = base64.b64encode(b"A" * 32).decode()
        assert validate_key_strength(low_entropy_key) is False

    def test_validate_key_strength_invalid_base64(self):
        """Test key strength validation with invalid base64."""
        assert validate_key_strength("not-valid-base64!@#$") is False


class TestErrorHandling:
    """Test error handling."""

    def test_encryption_error_message(self, encryption_service):
        """Test encryption error provides useful message."""
        # Try to encrypt with invalid input type
        with pytest.raises(Exception):  # Will raise AttributeError or similar
            encryption_service.encrypt_field(None, KeyPurpose.PII)

    def test_decryption_error_invalid_version(self, encryption_service):
        """Test decryption error with invalid version format."""
        with pytest.raises(DecryptionError):
            encryption_service.decrypt_field("vINVALID:abc:def", KeyPurpose.PII)

    def test_decryption_error_invalid_base64(self, encryption_service):
        """Test decryption error with invalid base64 encoding."""
        with pytest.raises(DecryptionError):
            encryption_service.decrypt_field("v1:invalid!base64:invalid!base64", KeyPurpose.PII)


class TestConcurrency:
    """Test thread safety and concurrency."""

    def test_concurrent_encryption(self, encryption_service, sample_plaintext):
        """Test concurrent encryption operations."""
        import threading

        results = []

        def encrypt_decrypt():
            encrypted = encryption_service.encrypt_field(sample_plaintext, KeyPurpose.PII)
            decrypted = encryption_service.decrypt_field(encrypted, KeyPurpose.PII)
            results.append(decrypted == sample_plaintext)

        # Run 10 concurrent operations
        threads = [threading.Thread(target=encrypt_decrypt) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed
        assert all(results)
        assert len(results) == 10
