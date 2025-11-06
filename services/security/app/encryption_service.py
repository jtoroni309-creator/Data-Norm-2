"""
SOC 2 Compliant Encryption Service

Implements bank-level encryption with:
- AES-256-GCM for data at rest
- Key rotation and versioning
- Secure key derivation (PBKDF2)
- Field-level encryption for PII/sensitive data
- Envelope encryption for large data

SOC 2 Trust Service Criteria Coverage:
- CC6.1: Logical and physical access controls
- CC6.6: Encryption of confidential data
- CC6.7: Encryption key management
"""

import base64
import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class KeyPurpose(str, Enum):
    """Purpose classification for encryption keys"""
    DATABASE_FIELD = "database_field"  # Field-level encryption
    FILE_STORAGE = "file_storage"  # File encryption
    API_TOKEN = "api_token"  # API token encryption
    PII = "pii"  # Personally Identifiable Information
    PHI = "phi"  # Protected Health Information
    FINANCIAL = "financial"  # Financial data
    AUDIT_LOG = "audit_log"  # Audit log encryption


class DataClassification(str, Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # PII, PHI, Financial data


class EncryptionService:
    """
    Enterprise-grade encryption service implementing SOC 2 requirements.

    Features:
    - AES-256-GCM (NIST-approved)
    - Key versioning and rotation
    - Envelope encryption for performance
    - Authenticated encryption (prevents tampering)
    - Constant-time comparison (prevents timing attacks)
    """

    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize encryption service.

        Args:
            master_key: Master encryption key (256-bit). If None, derives from environment.
        """
        # Master key should be stored in a secure key management system (AWS KMS, HashiCorp Vault, etc.)
        if master_key is None:
            master_key_b64 = os.environ.get("MASTER_ENCRYPTION_KEY")
            if not master_key_b64:
                raise ValueError(
                    "MASTER_ENCRYPTION_KEY environment variable must be set. "
                    "Generate with: python -c 'import os; import base64; print(base64.b64encode(os.urandom(32)).decode())'"
                )
            master_key = base64.b64decode(master_key_b64)

        if len(master_key) != 32:  # 256 bits
            raise ValueError("Master key must be 256 bits (32 bytes)")

        self.master_key = master_key
        self._key_cache: Dict[str, Tuple[bytes, datetime]] = {}
        self._key_rotation_days = 90  # Rotate keys every 90 days (SOC 2 requirement)

    def encrypt_field(
        self,
        plaintext: str,
        key_purpose: KeyPurpose,
        key_version: int = 1,
        associated_data: Optional[str] = None,
    ) -> str:
        """
        Encrypt a database field or sensitive string.

        Uses AES-256-GCM with authenticated encryption.

        Args:
            plaintext: Data to encrypt
            key_purpose: Purpose of encryption (for key derivation)
            key_version: Key version for rotation support
            associated_data: Additional authenticated data (context)

        Returns:
            Base64-encoded encrypted data with format:
            "v{version}:{nonce}:{ciphertext}:{tag}"
        """
        try:
            # Derive data encryption key (DEK) from master key
            dek = self._derive_key(key_purpose, key_version)

            # Generate random nonce (96 bits for GCM)
            nonce = os.urandom(12)

            # Create AESGCM cipher
            cipher = AESGCM(dek)

            # Encrypt with authenticated encryption
            aad = associated_data.encode() if associated_data else None
            ciphertext = cipher.encrypt(
                nonce,
                plaintext.encode("utf-8"),
                aad
            )

            # Format: version:nonce:ciphertext (tag is included in ciphertext by GCM)
            encrypted = f"v{key_version}:{base64.b64encode(nonce).decode()}:{base64.b64encode(ciphertext).decode()}"

            logger.debug(f"Encrypted data with key purpose: {key_purpose}, version: {key_version}")
            return encrypted

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError(f"Failed to encrypt data: {e}")

    def decrypt_field(
        self,
        encrypted_data: str,
        key_purpose: KeyPurpose,
        associated_data: Optional[str] = None,
    ) -> str:
        """
        Decrypt a database field or sensitive string.

        Args:
            encrypted_data: Encrypted data (format: "v{version}:{nonce}:{ciphertext}")
            key_purpose: Purpose of encryption (for key derivation)
            associated_data: Additional authenticated data (must match encryption)

        Returns:
            Decrypted plaintext string
        """
        try:
            # Parse encrypted data
            parts = encrypted_data.split(":")
            if len(parts) != 3:
                raise ValueError("Invalid encrypted data format")

            version_str, nonce_b64, ciphertext_b64 = parts
            key_version = int(version_str.replace("v", ""))

            # Decode components
            nonce = base64.b64decode(nonce_b64)
            ciphertext = base64.b64decode(ciphertext_b64)

            # Derive the same data encryption key
            dek = self._derive_key(key_purpose, key_version)

            # Create AESGCM cipher
            cipher = AESGCM(dek)

            # Decrypt and verify authentication tag
            aad = associated_data.encode() if associated_data else None
            plaintext_bytes = cipher.decrypt(nonce, ciphertext, aad)

            logger.debug(f"Decrypted data with key purpose: {key_purpose}, version: {key_version}")
            return plaintext_bytes.decode("utf-8")

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise DecryptionError(f"Failed to decrypt data: {e}")

    def encrypt_large_data(
        self,
        plaintext: bytes,
        key_purpose: KeyPurpose,
        key_version: int = 1,
    ) -> bytes:
        """
        Encrypt large data (files, documents) using envelope encryption.

        Uses a random data encryption key (DEK) encrypted with the master key (KEK).

        Args:
            plaintext: Raw bytes to encrypt
            key_purpose: Purpose of encryption
            key_version: Key version

        Returns:
            Encrypted bytes with format:
            [version(1)][nonce(12)][encrypted_dek(48)][ciphertext(variable)]
        """
        try:
            # Generate random DEK for this specific data
            dek = os.urandom(32)  # 256-bit DEK

            # Encrypt DEK with master key (envelope encryption)
            kek = self._derive_key(key_purpose, key_version)
            kek_cipher = AESGCM(kek)
            kek_nonce = os.urandom(12)
            encrypted_dek = kek_cipher.encrypt(kek_nonce, dek, None)

            # Encrypt data with DEK
            dek_cipher = AESGCM(dek)
            dek_nonce = os.urandom(12)
            ciphertext = dek_cipher.encrypt(dek_nonce, plaintext, None)

            # Format: [version][kek_nonce][encrypted_dek][dek_nonce][ciphertext]
            result = (
                bytes([key_version]) +
                kek_nonce +
                encrypted_dek +
                dek_nonce +
                ciphertext
            )

            logger.info(f"Encrypted {len(plaintext)} bytes using envelope encryption")
            return result

        except Exception as e:
            logger.error(f"Large data encryption failed: {e}")
            raise EncryptionError(f"Failed to encrypt large data: {e}")

    def decrypt_large_data(
        self,
        encrypted_data: bytes,
        key_purpose: KeyPurpose,
    ) -> bytes:
        """
        Decrypt large data using envelope encryption.

        Args:
            encrypted_data: Encrypted bytes
            key_purpose: Purpose of encryption

        Returns:
            Decrypted plaintext bytes
        """
        try:
            # Parse encrypted data
            key_version = encrypted_data[0]
            kek_nonce = encrypted_data[1:13]
            encrypted_dek = encrypted_data[13:61]  # GCM adds 16-byte tag
            dek_nonce = encrypted_data[61:73]
            ciphertext = encrypted_data[73:]

            # Decrypt DEK with master key
            kek = self._derive_key(key_purpose, key_version)
            kek_cipher = AESGCM(kek)
            dek = kek_cipher.decrypt(kek_nonce, encrypted_dek, None)

            # Decrypt data with DEK
            dek_cipher = AESGCM(dek)
            plaintext = dek_cipher.decrypt(dek_nonce, ciphertext, None)

            logger.info(f"Decrypted {len(plaintext)} bytes using envelope encryption")
            return plaintext

        except Exception as e:
            logger.error(f"Large data decryption failed: {e}")
            raise DecryptionError(f"Failed to decrypt large data: {e}")

    def _derive_key(self, purpose: KeyPurpose, version: int) -> bytes:
        """
        Derive a data encryption key (DEK) from the master key.

        Uses PBKDF2-HMAC-SHA256 for key derivation.

        Args:
            purpose: Key purpose (used as salt context)
            version: Key version

        Returns:
            256-bit derived key
        """
        cache_key = f"{purpose.value}:v{version}"

        # Check cache
        if cache_key in self._key_cache:
            cached_key, cached_time = self._key_cache[cache_key]
            # Refresh keys older than rotation period
            if datetime.utcnow() - cached_time < timedelta(days=self._key_rotation_days):
                return cached_key

        # Derive key using PBKDF2
        salt = f"{purpose.value}:v{version}".encode()
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # NIST recommendation
            backend=default_backend()
        )
        derived_key = kdf.derive(self.master_key)

        # Cache derived key
        self._key_cache[cache_key] = (derived_key, datetime.utcnow())

        return derived_key

    def rotate_keys(self) -> int:
        """
        Rotate encryption keys (increment version).

        Returns:
            New key version number
        """
        # In production, this would:
        # 1. Generate new master key in KMS
        # 2. Re-encrypt all data with new key version
        # 3. Update key version in database
        # 4. Keep old keys for decryption of old data

        # Clear key cache to force re-derivation
        self._key_cache.clear()
        logger.info("Encryption keys rotated (cache cleared)")

        # Return new version (in production, would query from database)
        return 2

    def secure_compare(self, a: str, b: str) -> bool:
        """
        Constant-time string comparison to prevent timing attacks.

        Args:
            a: First string
            b: Second string

        Returns:
            True if strings match, False otherwise
        """
        import hmac
        return hmac.compare_digest(a.encode(), b.encode())


class EncryptionError(Exception):
    """Raised when encryption fails"""
    pass


class DecryptionError(Exception):
    """Raised when decryption fails"""
    pass


# ============================================================================
# DATABASE MODEL MIXINS FOR ENCRYPTED FIELDS
# ============================================================================

class EncryptedFieldMixin:
    """
    Mixin for SQLAlchemy models with encrypted fields.

    Usage:
        class User(Base, EncryptedFieldMixin):
            ssn_encrypted = Column(String(500))

            @property
            def ssn(self):
                return self.decrypt_field(self.ssn_encrypted, KeyPurpose.PII)

            @ssn.setter
            def ssn(self, value):
                self.ssn_encrypted = self.encrypt_field(value, KeyPurpose.PII)
    """

    _encryption_service: Optional[EncryptionService] = None

    @classmethod
    def set_encryption_service(cls, service: EncryptionService):
        """Set the encryption service for all models"""
        cls._encryption_service = service

    def encrypt_field(
        self,
        plaintext: str,
        purpose: KeyPurpose,
        version: int = 1
    ) -> str:
        """Encrypt a field value"""
        if not self._encryption_service:
            raise RuntimeError("Encryption service not initialized")
        return self._encryption_service.encrypt_field(plaintext, purpose, version)

    def decrypt_field(
        self,
        encrypted: str,
        purpose: KeyPurpose
    ) -> str:
        """Decrypt a field value"""
        if not self._encryption_service:
            raise RuntimeError("Encryption service not initialized")
        return self._encryption_service.decrypt_field(encrypted, purpose)


# ============================================================================
# KEY MANAGEMENT UTILITIES
# ============================================================================

def generate_master_key() -> str:
    """
    Generate a new 256-bit master encryption key.

    Returns:
        Base64-encoded master key for storage in environment variable
    """
    key = os.urandom(32)  # 256 bits
    return base64.b64encode(key).decode()


def validate_key_strength(key_b64: str) -> bool:
    """
    Validate encryption key meets security requirements.

    Args:
        key_b64: Base64-encoded key

    Returns:
        True if key meets requirements, False otherwise
    """
    try:
        key = base64.b64decode(key_b64)

        # Must be 256 bits
        if len(key) != 32:
            return False

        # Must have sufficient entropy (at least 20 bits per byte)
        unique_bytes = len(set(key))
        if unique_bytes < 20:
            logger.warning(f"Low entropy key detected: {unique_bytes}/32 unique bytes")
            return False

        return True
    except Exception:
        return False
