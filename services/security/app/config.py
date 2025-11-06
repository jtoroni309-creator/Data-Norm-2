"""
Security Service Configuration

SOC 2 compliant configuration settings for:
- Encryption
- Audit logging
- Key management
- Security policies
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class SecuritySettings(BaseSettings):
    """Security configuration settings"""

    # ========================================================================
    # ENCRYPTION SETTINGS
    # ========================================================================

    # Master encryption key (256-bit, base64-encoded)
    # Generate with: python -c 'import os; import base64; print(base64.b64encode(os.urandom(32)).decode())'
    MASTER_ENCRYPTION_KEY: str

    # Key rotation period (days)
    KEY_ROTATION_DAYS: int = 90

    # Enable field-level encryption
    ENABLE_FIELD_ENCRYPTION: bool = True

    # ========================================================================
    # AUDIT LOGGING SETTINGS
    # ========================================================================

    # Enable comprehensive audit logging
    ENABLE_AUDIT_LOGGING: bool = True

    # Audit log retention periods (days)
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years (financial compliance)
    SECURITY_LOG_RETENTION_DAYS: int = 730  # 2 years
    ACCESS_LOG_RETENTION_DAYS: int = 365  # 1 year

    # Log to external system (Splunk, ELK, etc.)
    EXTERNAL_LOG_ENDPOINT: str = ""
    EXTERNAL_LOG_API_KEY: str = ""

    # ========================================================================
    # SECURITY MIDDLEWARE SETTINGS
    # ========================================================================

    # Enable rate limiting
    ENABLE_RATE_LIMITING: bool = True

    # Rate limits
    RATE_LIMIT_DEFAULT: int = 100  # requests per minute
    RATE_LIMIT_AUTHENTICATED: int = 1000  # requests per minute
    RATE_LIMIT_LOGIN: int = 5  # attempts per 5 minutes

    # Enable IP filtering
    ENABLE_IP_FILTERING: bool = False

    # IP allowlist (comma-separated)
    IP_ALLOWLIST: str = ""

    # IP denylist (comma-separated)
    IP_DENYLIST: str = ""

    # Enable CSRF protection
    ENABLE_CSRF_PROTECTION: bool = True

    # CSRF token expiry (hours)
    CSRF_TOKEN_EXPIRY_HOURS: int = 1

    # ========================================================================
    # SESSION SECURITY SETTINGS
    # ========================================================================

    # Session timeout (minutes of inactivity)
    SESSION_TIMEOUT_MINUTES: int = 30

    # Absolute session timeout (hours)
    SESSION_ABSOLUTE_TIMEOUT_HOURS: int = 8

    # Max concurrent sessions per user
    MAX_CONCURRENT_SESSIONS: int = 3

    # Require MFA for privileged operations
    REQUIRE_MFA_FOR_PRIVILEGED: bool = True

    # ========================================================================
    # KEY MANAGEMENT SETTINGS
    # ========================================================================

    # Use external KMS (aws_kms, vault, azure_kms)
    KMS_PROVIDER: str = "internal"

    # AWS KMS settings
    AWS_KMS_KEY_ID: str = ""
    AWS_KMS_REGION: str = "us-east-1"

    # HashiCorp Vault settings
    VAULT_ADDR: str = ""
    VAULT_TOKEN: str = ""
    VAULT_NAMESPACE: str = ""

    # Azure Key Vault settings
    AZURE_KEY_VAULT_URL: str = ""
    AZURE_KEY_VAULT_KEY_NAME: str = ""

    # ========================================================================
    # SOC 2 COMPLIANCE SETTINGS
    # ========================================================================

    # Enable SOC 2 compliance tracking
    ENABLE_SOC2_TRACKING: bool = True

    # Current audit period
    SOC2_AUDIT_PERIOD_START: str = "2025-01-01"
    SOC2_AUDIT_PERIOD_END: str = "2025-12-31"

    # Audit firm
    SOC2_AUDIT_FIRM: str = ""
    SOC2_AUDIT_PARTNER: str = ""

    # Trust service categories enabled
    SOC2_TSC_CATEGORIES: List[str] = ["CC", "A", "C", "PI"]  # CC, A, C, PI, P

    # ========================================================================
    # SECURITY MONITORING SETTINGS
    # ========================================================================

    # Enable security monitoring
    ENABLE_SECURITY_MONITORING: bool = True

    # Alert on suspicious activity
    ENABLE_SECURITY_ALERTS: bool = True

    # Alert threshold (failed login attempts)
    FAILED_LOGIN_ALERT_THRESHOLD: int = 5

    # Alert threshold (unauthorized access attempts)
    UNAUTHORIZED_ACCESS_ALERT_THRESHOLD: int = 3

    # Security alert email
    SECURITY_ALERT_EMAIL: str = ""

    # Security alert webhook
    SECURITY_ALERT_WEBHOOK: str = ""

    # ========================================================================
    # VULNERABILITY SCANNING SETTINGS
    # ========================================================================

    # Enable automated vulnerability scanning
    ENABLE_VULNERABILITY_SCANNING: bool = True

    # Vulnerability scan frequency (days)
    VULNERABILITY_SCAN_FREQUENCY_DAYS: int = 7

    # Vulnerability scan tool
    VULNERABILITY_SCAN_TOOL: str = ""  # "snyk", "trivy", "sonarqube"

    # ========================================================================
    # BACKUP AND RECOVERY SETTINGS
    # ========================================================================

    # Enable automated backups
    ENABLE_AUTOMATED_BACKUPS: bool = True

    # Backup frequency (hours)
    BACKUP_FREQUENCY_HOURS: int = 24

    # Backup retention (days)
    BACKUP_RETENTION_DAYS: int = 30

    # Backup encryption
    ENCRYPT_BACKUPS: bool = True

    # Test recovery quarterly
    TEST_RECOVERY_QUARTERLY: bool = True

    # ========================================================================
    # DATABASE SETTINGS
    # ========================================================================

    # Database URL
    DATABASE_URL: str = "postgresql+asyncpg://localhost/aura_security"

    # ========================================================================
    # GENERAL SETTINGS
    # ========================================================================

    # Environment
    ENVIRONMENT: str = "production"

    # Debug mode (NEVER enable in production)
    DEBUG: bool = False

    # Service name
    SERVICE_NAME: str = "security-service"

    class Config:
        env_file = ".env"
        case_sensitive = True


# ============================================================================
# SECURITY POLICY CONSTANTS
# ============================================================================

class SecurityPolicies:
    """
    Security policy constants for SOC 2 compliance.
    """

    # Password requirements
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL_CHARS = True
    PASSWORD_MAX_AGE_DAYS = 90
    PASSWORD_HISTORY_COUNT = 12  # Cannot reuse last 12 passwords

    # Account lockout
    ACCOUNT_LOCKOUT_THRESHOLD = 5  # Failed login attempts
    ACCOUNT_LOCKOUT_DURATION_MINUTES = 30
    ACCOUNT_LOCKOUT_RESET_MINUTES = 15

    # Access control
    REQUIRE_MFA_FOR_ADMIN = True
    REQUIRE_MFA_FOR_FINANCIAL_DATA = True
    REQUIRE_IP_RESTRICTION_FOR_ADMIN = False

    # Data classification
    DEFAULT_DATA_CLASSIFICATION = "confidential"
    PII_FIELDS = ["ssn", "tax_id", "bank_account", "credit_card", "passport"]
    FINANCIAL_FIELDS = ["balance", "revenue", "income", "assets", "liabilities"]

    # Encryption requirements
    ENCRYPT_AT_REST = True
    ENCRYPT_IN_TRANSIT = True
    MINIMUM_TLS_VERSION = "1.3"
    ALLOWED_CIPHER_SUITES = [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256",
    ]

    # Audit logging
    LOG_ALL_DATA_ACCESS = True
    LOG_ALL_DATA_MODIFICATIONS = True
    LOG_ALL_AUTHENTICATION_ATTEMPTS = True
    LOG_ALL_AUTHORIZATION_CHECKS = True
    LOG_ALL_SECURITY_EVENTS = True

    # Key management
    KEY_ROTATION_FREQUENCY_DAYS = 90
    KEY_BACKUP_REQUIRED = True
    KEY_SEPARATION_OF_DUTIES = True  # Different people for key generation and usage

    # Incident response
    INCIDENT_DETECTION_TIME_TARGET_HOURS = 1
    INCIDENT_RESPONSE_TIME_TARGET_HOURS = 4
    INCIDENT_RESOLUTION_TIME_TARGET_HOURS = 24

    # Compliance reporting
    ACCESS_REVIEW_FREQUENCY_DAYS = 90  # Quarterly
    VULNERABILITY_SCAN_FREQUENCY_DAYS = 7  # Weekly
    PENETRATION_TEST_FREQUENCY_DAYS = 365  # Annually
    SOC2_AUDIT_FREQUENCY_DAYS = 365  # Annually


# Initialize settings
settings = SecuritySettings()
