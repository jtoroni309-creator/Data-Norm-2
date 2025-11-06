"""
Security Service - SOC 2 Compliant Security Framework

Provides:
- Bank-level encryption (AES-256-GCM)
- Comprehensive audit logging
- Security middleware
- Key management
- SOC 2 compliance tracking
"""

from .encryption_service import (
    EncryptionService,
    KeyPurpose,
    DataClassification,
    EncryptionError,
    DecryptionError,
    EncryptedFieldMixin,
    generate_master_key,
    validate_key_strength,
)

from .audit_logging import (
    AuditLogService,
    AuditEventType,
    AuditSeverity,
    RetentionPolicy,
)

from .security_middleware import (
    SecurityMiddleware,
    SecurityLevel,
    SecurityViolation,
    RateLimitExceeded,
    SessionSecurity,
)

from .key_management import (
    KeyManagementService,
    KeyType,
    KeyStatus,
    KeyUsage,
    KeyManagementError,
)

__all__ = [
    # Encryption
    "EncryptionService",
    "KeyPurpose",
    "DataClassification",
    "EncryptionError",
    "DecryptionError",
    "EncryptedFieldMixin",
    "generate_master_key",
    "validate_key_strength",
    # Audit Logging
    "AuditLogService",
    "AuditEventType",
    "AuditSeverity",
    "RetentionPolicy",
    # Security Middleware
    "SecurityMiddleware",
    "SecurityLevel",
    "SecurityViolation",
    "RateLimitExceeded",
    "SessionSecurity",
    # Key Management
    "KeyManagementService",
    "KeyType",
    "KeyStatus",
    "KeyUsage",
    "KeyManagementError",
]

__version__ = "1.0.0"
