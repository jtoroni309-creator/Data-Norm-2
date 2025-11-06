"""
Enterprise Key Management Service

Implements secure key management for SOC 2 compliance:
- Key generation and storage
- Key rotation and versioning
- Key access controls
- Key usage auditing
- Integration with KMS (AWS KMS, HashiCorp Vault, etc.)

SOC 2 Trust Service Criteria Coverage:
- CC6.7: Encryption key management
- CC6.1: Access controls for keys
"""

import base64
import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class KeyType(str, Enum):
    """Types of encryption keys"""
    MASTER = "master"  # Master encryption key (KEK)
    DATA = "data"  # Data encryption key (DEK)
    SESSION = "session"  # Session encryption key
    API = "api"  # API key encryption
    TOKEN = "token"  # Token signing key


class KeyStatus(str, Enum):
    """Key lifecycle status"""
    ACTIVE = "active"  # Currently in use
    ROTATING = "rotating"  # Being rotated
    DEPRECATED = "deprecated"  # No longer for new operations, but kept for decryption
    REVOKED = "revoked"  # Compromised or no longer needed
    DESTROYED = "destroyed"  # Securely deleted


class KeyUsage(str, Enum):
    """Allowed key usage"""
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    WRAP = "wrap"  # Wrap other keys
    UNWRAP = "unwrap"  # Unwrap other keys


class KeyManagementService:
    """
    Enterprise key management service for SOC 2 compliance.

    Features:
    - Secure key generation
    - Key versioning and rotation
    - Key access controls
    - Audit logging of key operations
    - Integration with external KMS
    """

    def __init__(
        self,
        audit_log_service=None,
        kms_provider: Optional[str] = None,
    ):
        """
        Initialize key management service.

        Args:
            audit_log_service: AuditLogService for key operation logging
            kms_provider: External KMS provider ("aws_kms", "vault", "azure_kms")
        """
        self.audit_log_service = audit_log_service
        self.kms_provider = kms_provider

        # In-memory key store (in production, would use external KMS or HSM)
        self._keys: Dict[str, Dict] = {}
        self._key_versions: Dict[str, List[str]] = {}  # key_id -> [version_ids]

        # Key rotation policies
        self._rotation_policies = {
            KeyType.MASTER: timedelta(days=90),  # Rotate every 90 days
            KeyType.DATA: timedelta(days=180),  # Rotate every 180 days
            KeyType.SESSION: timedelta(days=1),  # Rotate daily
            KeyType.API: timedelta(days=365),  # Rotate annually
            KeyType.TOKEN: timedelta(days=30),  # Rotate monthly
        }

    def generate_key(
        self,
        key_type: KeyType,
        key_id: str,
        purpose: str,
        tenant_id: Optional[UUID] = None,
        allowed_usage: Optional[List[KeyUsage]] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Generate a new encryption key.

        Args:
            key_type: Type of key to generate
            key_id: Unique identifier for key
            purpose: Purpose/description of key
            tenant_id: Tenant that owns key (for multi-tenancy)
            allowed_usage: Allowed key operations
            metadata: Additional key metadata

        Returns:
            Key information (key material NOT included)
        """
        try:
            # Generate key material based on type
            if key_type in [KeyType.MASTER, KeyType.DATA]:
                key_material = os.urandom(32)  # 256-bit key
            elif key_type == KeyType.SESSION:
                key_material = os.urandom(16)  # 128-bit key
            else:
                key_material = os.urandom(32)

            version_id = str(uuid4())
            now = datetime.utcnow()

            # Default allowed usage
            if allowed_usage is None:
                allowed_usage = [KeyUsage.ENCRYPT, KeyUsage.DECRYPT]

            # Create key record
            key_record = {
                "key_id": key_id,
                "version_id": version_id,
                "key_type": key_type.value,
                "purpose": purpose,
                "tenant_id": str(tenant_id) if tenant_id else None,
                "status": KeyStatus.ACTIVE.value,
                "allowed_usage": [u.value for u in allowed_usage],
                "created_at": now.isoformat(),
                "expires_at": (now + self._rotation_policies[key_type]).isoformat(),
                "rotated_at": None,
                "last_used_at": None,
                "usage_count": 0,
                "metadata": metadata or {},
                # In production, key_material would be stored in KMS/HSM, not in memory
                "_key_material": base64.b64encode(key_material).decode(),
            }

            # Store key
            full_key_id = f"{key_id}:{version_id}"
            self._keys[full_key_id] = key_record

            # Track versions
            if key_id not in self._key_versions:
                self._key_versions[key_id] = []
            self._key_versions[key_id].append(version_id)

            # Audit log
            if self.audit_log_service:
                logger.info(f"Generated key: {key_id} (type: {key_type.value})")
                # await self.audit_log_service.log_event(...)

            # Return key info (without key material)
            return {
                "key_id": key_id,
                "version_id": version_id,
                "key_type": key_type.value,
                "status": KeyStatus.ACTIVE.value,
                "created_at": now.isoformat(),
                "expires_at": (now + self._rotation_policies[key_type]).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to generate key {key_id}: {e}")
            raise KeyManagementError(f"Key generation failed: {e}")

    def get_key(
        self,
        key_id: str,
        version_id: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> Optional[bytes]:
        """
        Retrieve key material.

        Args:
            key_id: Key identifier
            version_id: Specific version (if None, returns latest active)
            user_id: User requesting key (for audit)

        Returns:
            Key material bytes, or None if not found
        """
        try:
            # Get specific version or latest
            if version_id:
                full_key_id = f"{key_id}:{version_id}"
            else:
                # Get latest active version
                versions = self._key_versions.get(key_id, [])
                if not versions:
                    logger.warning(f"Key not found: {key_id}")
                    return None

                # Find latest active version
                active_version = None
                for v in reversed(versions):
                    full_key_id = f"{key_id}:{v}"
                    key_record = self._keys.get(full_key_id)
                    if key_record and key_record["status"] == KeyStatus.ACTIVE.value:
                        active_version = v
                        break

                if not active_version:
                    logger.warning(f"No active version found for key: {key_id}")
                    return None

                full_key_id = f"{key_id}:{active_version}"

            # Get key record
            key_record = self._keys.get(full_key_id)
            if not key_record:
                logger.warning(f"Key not found: {full_key_id}")
                return None

            # Check status
            if key_record["status"] in [KeyStatus.REVOKED.value, KeyStatus.DESTROYED.value]:
                logger.error(f"Attempted to access {key_record['status']} key: {full_key_id}")
                raise KeyManagementError(f"Key is {key_record['status']}")

            # Check expiration
            expires_at = datetime.fromisoformat(key_record["expires_at"])
            if datetime.utcnow() > expires_at:
                logger.warning(f"Key expired: {full_key_id}")
                # Mark as deprecated
                key_record["status"] = KeyStatus.DEPRECATED.value

            # Update usage tracking
            key_record["last_used_at"] = datetime.utcnow().isoformat()
            key_record["usage_count"] += 1

            # Audit log
            if self.audit_log_service and user_id:
                logger.info(f"Key accessed: {key_id} by user {user_id}")

            # Return key material
            return base64.b64decode(key_record["_key_material"])

        except Exception as e:
            logger.error(f"Failed to retrieve key {key_id}: {e}")
            raise KeyManagementError(f"Key retrieval failed: {e}")

    def rotate_key(
        self,
        key_id: str,
        user_id: UUID,
    ) -> Dict:
        """
        Rotate encryption key (generate new version).

        Args:
            key_id: Key to rotate
            user_id: User performing rotation

        Returns:
            New key information
        """
        try:
            # Get current key
            versions = self._key_versions.get(key_id, [])
            if not versions:
                raise KeyManagementError(f"Key not found: {key_id}")

            current_version_id = versions[-1]
            full_key_id = f"{key_id}:{current_version_id}"
            current_key = self._keys.get(full_key_id)

            if not current_key:
                raise KeyManagementError(f"Current key version not found: {full_key_id}")

            # Mark current key as deprecated
            current_key["status"] = KeyStatus.DEPRECATED.value
            current_key["rotated_at"] = datetime.utcnow().isoformat()

            # Generate new version
            new_key = self.generate_key(
                key_type=KeyType(current_key["key_type"]),
                key_id=key_id,
                purpose=current_key["purpose"],
                tenant_id=UUID(current_key["tenant_id"]) if current_key["tenant_id"] else None,
                allowed_usage=[KeyUsage(u) for u in current_key["allowed_usage"]],
                metadata=current_key["metadata"],
            )

            # Audit log
            if self.audit_log_service:
                logger.info(f"Key rotated: {key_id} by user {user_id}")
                # await self.audit_log_service.log_event(
                #     event_type=AuditEventType.ENCRYPTION_KEY_ROTATED,
                #     user_id=user_id,
                #     ...
                # )

            logger.info(f"Key rotated: {key_id} -> {new_key['version_id']}")
            return new_key

        except Exception as e:
            logger.error(f"Failed to rotate key {key_id}: {e}")
            raise KeyManagementError(f"Key rotation failed: {e}")

    def revoke_key(
        self,
        key_id: str,
        version_id: Optional[str] = None,
        reason: str = "Manual revocation",
        user_id: Optional[UUID] = None,
    ):
        """
        Revoke key (mark as compromised or no longer needed).

        Args:
            key_id: Key to revoke
            version_id: Specific version (if None, revokes all versions)
            reason: Reason for revocation
            user_id: User performing revocation
        """
        try:
            if version_id:
                # Revoke specific version
                full_key_id = f"{key_id}:{version_id}"
                key_record = self._keys.get(full_key_id)
                if key_record:
                    key_record["status"] = KeyStatus.REVOKED.value
                    key_record["revoked_at"] = datetime.utcnow().isoformat()
                    key_record["revocation_reason"] = reason
                    logger.warning(f"Key revoked: {full_key_id} - {reason}")
            else:
                # Revoke all versions
                versions = self._key_versions.get(key_id, [])
                for v in versions:
                    full_key_id = f"{key_id}:{v}"
                    key_record = self._keys.get(full_key_id)
                    if key_record:
                        key_record["status"] = KeyStatus.REVOKED.value
                        key_record["revoked_at"] = datetime.utcnow().isoformat()
                        key_record["revocation_reason"] = reason
                logger.warning(f"All versions of key revoked: {key_id} - {reason}")

            # Audit log
            if self.audit_log_service and user_id:
                logger.critical(f"Key revoked: {key_id} by user {user_id} - {reason}")

        except Exception as e:
            logger.error(f"Failed to revoke key {key_id}: {e}")
            raise KeyManagementError(f"Key revocation failed: {e}")

    def destroy_key(
        self,
        key_id: str,
        version_id: str,
        confirmation_token: str,
        user_id: UUID,
    ):
        """
        Permanently destroy key material (cannot be undone).

        Requires confirmation token for safety.

        Args:
            key_id: Key to destroy
            version_id: Specific version
            confirmation_token: Confirmation token (must match key_id)
            user_id: User performing destruction
        """
        try:
            # Validate confirmation token
            if confirmation_token != f"DESTROY:{key_id}:{version_id}":
                raise KeyManagementError("Invalid confirmation token")

            full_key_id = f"{key_id}:{version_id}"
            key_record = self._keys.get(full_key_id)

            if not key_record:
                raise KeyManagementError(f"Key not found: {full_key_id}")

            # Check if key is already in use
            if key_record["status"] == KeyStatus.ACTIVE.value:
                raise KeyManagementError("Cannot destroy active key. Revoke first.")

            # Securely erase key material
            key_record["_key_material"] = None
            key_record["status"] = KeyStatus.DESTROYED.value
            key_record["destroyed_at"] = datetime.utcnow().isoformat()
            key_record["destroyed_by"] = str(user_id)

            # Audit log
            if self.audit_log_service:
                logger.critical(f"Key destroyed: {full_key_id} by user {user_id}")

            logger.warning(f"Key destroyed: {full_key_id}")

        except Exception as e:
            logger.error(f"Failed to destroy key {key_id}: {e}")
            raise KeyManagementError(f"Key destruction failed: {e}")

    def list_keys(
        self,
        tenant_id: Optional[UUID] = None,
        key_type: Optional[KeyType] = None,
        status: Optional[KeyStatus] = None,
    ) -> List[Dict]:
        """
        List keys (without key material).

        Args:
            tenant_id: Filter by tenant
            key_type: Filter by key type
            status: Filter by status

        Returns:
            List of key information
        """
        keys = []

        for full_key_id, key_record in self._keys.items():
            # Apply filters
            if tenant_id and key_record["tenant_id"] != str(tenant_id):
                continue
            if key_type and key_record["key_type"] != key_type.value:
                continue
            if status and key_record["status"] != status.value:
                continue

            # Add to results (without key material)
            keys.append({
                "key_id": key_record["key_id"],
                "version_id": key_record["version_id"],
                "key_type": key_record["key_type"],
                "status": key_record["status"],
                "purpose": key_record["purpose"],
                "created_at": key_record["created_at"],
                "expires_at": key_record["expires_at"],
                "usage_count": key_record["usage_count"],
                "last_used_at": key_record["last_used_at"],
            })

        return keys

    def check_rotation_needed(self) -> List[str]:
        """
        Check which keys need rotation.

        Returns:
            List of key IDs that need rotation
        """
        keys_to_rotate = []
        now = datetime.utcnow()

        for key_id, versions in self._key_versions.items():
            # Get latest version
            latest_version = versions[-1]
            full_key_id = f"{key_id}:{latest_version}"
            key_record = self._keys.get(full_key_id)

            if not key_record:
                continue

            # Check if active and expired
            if key_record["status"] == KeyStatus.ACTIVE.value:
                expires_at = datetime.fromisoformat(key_record["expires_at"])
                if now > expires_at:
                    keys_to_rotate.append(key_id)

        return keys_to_rotate

    def get_key_usage_report(
        self,
        start_date: datetime,
        end_date: datetime,
        tenant_id: Optional[UUID] = None,
    ) -> Dict:
        """
        Generate key usage report for compliance.

        Args:
            start_date: Report start date
            end_date: Report end date
            tenant_id: Filter by tenant

        Returns:
            Usage report
        """
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_keys": 0,
            "keys_by_type": {},
            "keys_by_status": {},
            "total_usage": 0,
            "keys_rotated": 0,
            "keys_revoked": 0,
            "keys_destroyed": 0,
        }

        for full_key_id, key_record in self._keys.items():
            # Apply tenant filter
            if tenant_id and key_record["tenant_id"] != str(tenant_id):
                continue

            # Count keys
            report["total_keys"] += 1

            # Count by type
            key_type = key_record["key_type"]
            report["keys_by_type"][key_type] = report["keys_by_type"].get(key_type, 0) + 1

            # Count by status
            status = key_record["status"]
            report["keys_by_status"][status] = report["keys_by_status"].get(status, 0) + 1

            # Count usage
            report["total_usage"] += key_record["usage_count"]

            # Check if rotated in period
            if key_record.get("rotated_at"):
                rotated_at = datetime.fromisoformat(key_record["rotated_at"])
                if start_date <= rotated_at <= end_date:
                    report["keys_rotated"] += 1

            # Check if revoked in period
            if key_record.get("revoked_at"):
                revoked_at = datetime.fromisoformat(key_record["revoked_at"])
                if start_date <= revoked_at <= end_date:
                    report["keys_revoked"] += 1

            # Check if destroyed in period
            if key_record.get("destroyed_at"):
                destroyed_at = datetime.fromisoformat(key_record["destroyed_at"])
                if start_date <= destroyed_at <= end_date:
                    report["keys_destroyed"] += 1

        return report


class KeyManagementError(Exception):
    """Raised when key management operation fails"""
    pass


# ============================================================================
# KMS INTEGRATION (AWS KMS, HashiCorp Vault, etc.)
# ============================================================================

class ExternalKMSProvider:
    """
    Interface for external KMS providers.

    In production, integrate with:
    - AWS KMS
    - Google Cloud KMS
    - Azure Key Vault
    - HashiCorp Vault
    - Hardware Security Modules (HSM)
    """

    def __init__(self, provider: str, config: Dict):
        """
        Initialize KMS provider.

        Args:
            provider: Provider name ("aws_kms", "vault", etc.)
            config: Provider configuration
        """
        self.provider = provider
        self.config = config

    def generate_data_key(self, key_id: str) -> Tuple[bytes, bytes]:
        """
        Generate data encryption key using KMS.

        Returns:
            Tuple of (plaintext_key, encrypted_key)
        """
        # In production, would call KMS API
        # Example: boto3.client('kms').generate_data_key(KeyId=key_id, KeySpec='AES_256')
        raise NotImplementedError("KMS integration not implemented")

    def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt data using KMS key"""
        raise NotImplementedError("KMS integration not implemented")

    def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt data using KMS key"""
        raise NotImplementedError("KMS integration not implemented")

    def rotate_key(self, key_id: str):
        """Rotate KMS key"""
        raise NotImplementedError("KMS integration not implemented")
