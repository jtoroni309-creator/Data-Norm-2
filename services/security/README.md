# Security Service - SOC 2 Compliant Security Framework

Bank-level encryption and SOC 2 compliance for Aura Audit AI platform.

## Features

### 🔐 Bank-Level Encryption
- **AES-256-GCM** encryption at rest (NIST FIPS 197 approved)
- **TLS 1.3** encryption in transit
- Field-level encryption for PII/PHI
- Envelope encryption for large files
- Authenticated encryption (prevents tampering)

### 📋 SOC 2 Compliance
- Full implementation of SOC 2 Trust Service Criteria
- Common Criteria (CC) - Security controls
- Availability (A) - System availability
- Confidentiality (C) - Data confidentiality
- Processing Integrity (PI) - Data processing integrity

### 📊 Comprehensive Audit Logging
- Immutable audit trail
- 7-year retention for financial data
- Hash chain for tamper detection
- All actions logged with full context
- Real-time security event monitoring

### 🔑 Enterprise Key Management
- Automated key rotation (90-day policy)
- Key versioning and lifecycle management
- Integration with external KMS (AWS KMS, Vault, Azure)
- Secure key generation and storage

### 🛡️ Security Middleware
- Rate limiting (100-1000 req/min)
- IP filtering (allowlist/denylist)
- CSRF protection
- Security headers (HSTS, CSP, X-Frame-Options)
- Session management with timeouts

## Installation

```bash
cd services/security
pip install -r requirements.txt
```

## Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Generate a master encryption key:
```bash
python -c 'import os; import base64; print(base64.b64encode(os.urandom(32)).decode())'
```

3. Update `.env` with the generated key:
```bash
MASTER_ENCRYPTION_KEY=<your_generated_key>
```

## Quick Start

### Initialize Security Service

```python
from services.security.app import (
    EncryptionService,
    AuditLogService,
    SecurityMiddleware,
    KeyManagementService,
)

# Initialize services
encryption_service = EncryptionService()
audit_log_service = AuditLogService(encryption_service)
key_management_service = KeyManagementService(audit_log_service)
```

### Add Security Middleware to FastAPI

```python
from fastapi import FastAPI
from services.security.app import SecurityMiddleware, AuditLogService

app = FastAPI()

# Initialize security
audit_log = AuditLogService()
app.add_middleware(
    SecurityMiddleware,
    audit_log_service=audit_log,
    enable_rate_limiting=True,
    enable_csrf_protection=True
)
```

### Encrypt Sensitive Database Fields

```python
from services.security.app import EncryptedFieldMixin, KeyPurpose
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base, EncryptedFieldMixin):
    __tablename__ = "users"

    ssn_encrypted = Column(String(500))

    @property
    def ssn(self):
        return self.decrypt_field(self.ssn_encrypted, KeyPurpose.PII)

    @ssn.setter
    def ssn(self, value):
        self.ssn_encrypted = self.encrypt_field(value, KeyPurpose.PII)
```

### Log Audit Events

```python
from services.security.app import AuditLogService, AuditEventType

audit_log = AuditLogService()

# Log data access
await audit_log.log_data_access(
    user_id=user_id,
    tenant_id=tenant_id,
    resource_type="engagement",
    resource_id=engagement_id,
    action="Viewed engagement details",
    ip_address=request.client.host
)

# Log data modification
await audit_log.log_data_modification(
    user_id=user_id,
    tenant_id=tenant_id,
    resource_type="engagement",
    resource_id=engagement_id,
    action="Updated status",
    operation="UPDATE",
    before_values={"status": "draft"},
    after_values={"status": "in_progress"}
)
```

## Integration Examples

### Example 1: Secure API Endpoint

```python
from fastapi import FastAPI, Depends, HTTPException
from services.security.app import AuditLogService, AuditEventType

app = FastAPI()
audit_log = AuditLogService()

@app.get("/api/v1/engagements/{engagement_id}")
async def get_engagement(engagement_id: str, request: Request):
    # Log data access
    await audit_log.log_data_access(
        user_id=request.state.user_id,
        tenant_id=request.state.tenant_id,
        resource_type="engagement",
        resource_id=engagement_id,
        action="Retrieved engagement",
        ip_address=request.client.host
    )

    # Fetch and return engagement
    engagement = await fetch_engagement(engagement_id)
    return engagement

@app.put("/api/v1/engagements/{engagement_id}")
async def update_engagement(
    engagement_id: str,
    update_data: dict,
    request: Request
):
    # Get current values
    current_engagement = await fetch_engagement(engagement_id)

    # Update engagement
    updated_engagement = await update_engagement_db(engagement_id, update_data)

    # Log modification
    await audit_log.log_data_modification(
        user_id=request.state.user_id,
        tenant_id=request.state.tenant_id,
        resource_type="engagement",
        resource_id=engagement_id,
        action="Updated engagement",
        operation="UPDATE",
        before_values=current_engagement.dict(),
        after_values=updated_engagement.dict(),
        ip_address=request.client.host
    )

    return updated_engagement
```

### Example 2: Key Rotation Script

```python
from services.security.app import KeyManagementService

kms = KeyManagementService()

# Check which keys need rotation
keys_to_rotate = kms.check_rotation_needed()

for key_id in keys_to_rotate:
    print(f"Rotating key: {key_id}")
    new_key = kms.rotate_key(key_id, admin_user_id)
    print(f"  New version: {new_key['version_id']}")
```

## Testing

Run the test suite:

```bash
pytest tests/ -v --cov=app
```

## Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Rotate keys regularly** - Automated 90-day rotation policy
3. **Monitor audit logs** - Review logs daily for anomalies
4. **Enable all security features** - Rate limiting, CSRF, encryption
5. **Use HTTPS/TLS 1.3** - Never transmit data unencrypted
6. **Implement MFA** - For all privileged operations
7. **Regular backups** - Daily automated encrypted backups
8. **Vulnerability scanning** - Weekly automated scans

## SOC 2 Audit Preparation

See [SOC2_COMPLIANCE_GUIDE.md](SOC2_COMPLIANCE_GUIDE.md) for:
- Control implementation details
- Evidence collection
- Audit preparation checklist
- Compliance reporting

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                               │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/TLS 1.3
                     │
┌────────────────────▼────────────────────────────────────────┐
│              SECURITY MIDDLEWARE                             │
│  • Rate Limiting                                            │
│  • IP Filtering                                             │
│  • CSRF Protection                                          │
│  • Security Headers                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│           AUDIT LOGGING LAYER                                │
│  • All actions logged                                       │
│  • Immutable audit trail                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│          ENCRYPTION LAYER                                    │
│  • AES-256-GCM                                              │
│  • Field-level encryption                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│            DATABASE (ENCRYPTED)                              │
└─────────────────────────────────────────────────────────────┘
```

## Environment Variables

See [.env.example](.env.example) for all configuration options.

Required variables:
- `MASTER_ENCRYPTION_KEY` - Master encryption key (256-bit)
- `DATABASE_URL` - PostgreSQL connection string
- `ENVIRONMENT` - Environment (production, staging, development)

## Support

For security concerns:
- Email: security@yourcompany.com
- Emergency: Available 24/7

## License

Proprietary - Aura Audit AI

## Version

**Version**: 1.0.0
**Last Updated**: 2025-01-06
