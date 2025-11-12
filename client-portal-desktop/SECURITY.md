# Security Guide - Aura Audit AI Smart Client

## Overview

This document outlines the security architecture, practices, and considerations for the Aura Audit AI Smart Client desktop application.

---

## Security Architecture

### Layered Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  • Sandboxed Renderer Process                               │
│  • Context Isolation                                         │
│  • Secure IPC Communication                                  │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  • SQLite Encryption (AES-256)                              │
│  • Encrypted Credential Storage                              │
│  • Secure File Storage                                       │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                     Communication Layer                      │
│  • HTTPS/TLS 1.3                                            │
│  • Certificate Pinning                                       │
│  • JWT Authentication                                        │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                      System Layer                            │
│  • Code Signing                                             │
│  • Windows User Account Control                              │
│  • File System Permissions                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Application Security

### 1. Electron Security Best Practices

#### Context Isolation

**Enabled** - Prevents renderer from accessing Node.js/Electron internals:

```javascript
// electron/main.js
webPreferences: {
  contextIsolation: true,       // ✅ Enabled
  nodeIntegration: false,       // ✅ Disabled
  enableRemoteModule: false,    // ✅ Disabled
  sandbox: false                // Required for database access
}
```

#### Preload Script Security

All IPC communication goes through a controlled preload script:

```javascript
// electron/preload.js
contextBridge.exposeInMainWorld('electron', {
  // Only expose specific, safe APIs
  db: { query, execute, getStats },
  sync: { start, stop, getStatus },
  // No direct access to Node.js/filesystem
});
```

#### Content Security Policy

Strict CSP prevents XSS attacks:

```javascript
// Applied to all windows
"Content-Security-Policy":
  "default-src 'self'; " +
  "script-src 'self'; " +
  "style-src 'self' 'unsafe-inline'; " +
  "img-src 'self' data: https:; " +
  "connect-src 'self' https://api.auraaudit.ai;"
```

### 2. Renderer Process Security

- **No eval()**: Never use eval() or Function() constructor
- **No Inline Scripts**: All JavaScript in separate files
- **Sanitize User Input**: All user input sanitized before rendering
- **No Dynamic Requires**: Only static requires allowed

### 3. IPC Security

All IPC channels are validated:

```javascript
// electron/main.js
ipcMain.handle('db:query', async (event, sql, params) => {
  // Validate sender
  if (event.sender !== mainWindow.webContents) {
    throw new Error('Unauthorized sender');
  }

  // Sanitize inputs
  if (typeof sql !== 'string') {
    throw new Error('Invalid SQL');
  }

  // Execute safely
  return await dbManager.query(sql, params);
});
```

---

## Data Security

### 1. Local Database Encryption

**SQLite with SQLCipher** (planned - currently using better-sqlite3):

```javascript
// Future implementation
const db = new Database('aura-audit.db', {
  encryption: 'aes256',
  key: deriveKeyFromUserPassword(userPassword)
});
```

**Current**: Database stored in user-protected directory:
- Windows: `%APPDATA%\aura-audit-client\` (user-only access)

### 2. Sensitive Data Storage

**Electron Store** with encryption:

```javascript
const Store = require('electron-store');

const store = new Store({
  encryptionKey: 'user-derived-key', // Derived from machine ID + user
  name: 'config'
});

// Store sensitive data
store.set('authToken', jwtToken);
```

### 3. Credential Management

**JWT Tokens**:
- Stored encrypted in electron-store
- Expire after 8 hours
- Refresh token used for renewal
- Cleared on logout

**Passwords**:
- Never stored locally
- Only sent over HTTPS for authentication
- Not logged anywhere

### 4. Data at Rest

| Data Type | Storage Location | Encryption | Access Control |
|-----------|------------------|------------|----------------|
| Database | `%APPDATA%` | Future: AES-256 | Windows ACLs |
| Documents | `%APPDATA%/documents` | None (planned) | Windows ACLs |
| Settings | Electron Store | AES-256 | Windows ACLs |
| Logs | `%APPDATA%/logs` | None | Windows ACLs |
| Cache | `%APPDATA%/cache` | None | Windows ACLs |

---

## Communication Security

### 1. HTTPS/TLS

All communication with cloud API uses HTTPS:

```javascript
const apiClient = axios.create({
  baseURL: 'https://api.auraaudit.ai',
  timeout: 30000,
  httpsAgent: new https.Agent({
    minVersion: 'TLSv1.3',  // Only TLS 1.3
    maxVersion: 'TLSv1.3'
  })
});
```

### 2. Certificate Pinning

Verify cloud API certificate:

```javascript
const https = require('https');
const crypto = require('crypto');

const EXPECTED_CERT_FINGERPRINT = 'sha256/abc123...';

const agent = new https.Agent({
  checkServerIdentity: (host, cert) => {
    const fingerprint = crypto
      .createHash('sha256')
      .update(cert.raw)
      .digest('base64');

    if (fingerprint !== EXPECTED_CERT_FINGERPRINT) {
      throw new Error('Certificate mismatch');
    }
  }
});
```

### 3. Authentication

**JWT Bearer Tokens**:

```javascript
apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

**Token Lifecycle**:
1. User logs in → receive JWT
2. JWT stored encrypted
3. JWT sent with each API request
4. JWT expires after 8 hours
5. Refresh token used to get new JWT
6. User re-authenticates if refresh fails

### 4. API Request Validation

All API requests validated:
- Valid JWT token
- Request signature
- Rate limiting
- Input sanitization

---

## Update Security

### 1. Code Signing

All releases signed with **EV Code Signing Certificate**:

```bash
# Windows Authenticode signing
signtool sign /f cert.pfx /p password /tr http://timestamp.digicert.com /td sha256 Aura-Audit-Client-Setup.exe
```

**Benefits**:
- Verified publisher (Aura Audit AI)
- No SmartScreen warnings
- Integrity verification
- Tamper detection

### 2. Update Verification

Updates verified before installation:

```javascript
// electron-updater automatically verifies:
// 1. SHA-512 checksum
// 2. Code signature
// 3. Download over HTTPS

autoUpdater.on('update-downloaded', (info) => {
  // Verified and ready to install
  log.info('Update verified and downloaded');
});
```

### 3. Update Manifest

**latest.yml** signed and verified:

```yaml
version: 1.0.1
files:
  - url: Aura-Audit-Client-Setup-1.0.1.exe
    sha512: abc123def456...  # SHA-512 checksum
    size: 75234567
path: Aura-Audit-Client-Setup-1.0.1.exe
sha512: abc123def456...
```

---

## Access Control

### 1. Windows User Permissions

Application respects Windows user permissions:
- Installed per-user or per-machine
- Data in user profile (not shared)
- No admin rights required after installation

### 2. File System Permissions

```
%APPDATA%\aura-audit-client\
├── aura-audit.db          (Read/Write - Current User Only)
├── config.json            (Read/Write - Current User Only)
├── logs\                  (Read/Write - Current User Only)
└── documents\             (Read/Write - Current User Only)
```

### 3. Role-Based Access Control (RBAC)

Enforced at cloud API level:
- Partner
- Manager
- Senior
- Staff
- Client Contact

The desktop app respects these roles for UI and functionality.

---

## Audit & Logging

### 1. Local Logging

Logs stored in: `%APPDATA%\aura-audit-client\logs\`

**Log Files**:
- `main.log`: Application lifecycle, errors
- `sync.log`: Synchronization events
- `analytics.log`: Local processing
- `security.log`: Authentication, access events

**Log Format**:
```
[2025-11-12 14:23:45] [INFO] User authenticated: user@example.com
[2025-11-12 14:24:00] [INFO] Sync started
[2025-11-12 14:24:15] [INFO] Sync completed: 45 records
[2025-11-12 14:25:00] [WARN] API request failed: Network error
[2025-11-12 14:25:05] [ERROR] Database query failed: Syntax error
```

**What's Logged**:
- ✅ Authentication attempts
- ✅ API requests/responses
- ✅ Sync operations
- ✅ Database operations
- ✅ Errors and exceptions
- ❌ Passwords
- ❌ JWT tokens
- ❌ Sensitive user data

### 2. Remote Audit Trail

Optionally send audit events to cloud:
- Authentication events
- Data access events
- Modification events
- Error events

Users can opt-out in Settings → Privacy.

### 3. Log Rotation

Logs automatically rotated:
- Max file size: 10 MB
- Max files: 5
- Total max size: 50 MB
- Auto-delete old logs

---

## Privacy

### 1. Data Collection

**What We Collect**:
- Application version
- Platform (Windows 10/11)
- Sync status and performance metrics
- Error reports and stack traces
- Feature usage (anonymized)

**What We Don't Collect**:
- Passwords
- Financial data
- Client information
- Personal user data
- Keystrokes or screenshots

### 2. Telemetry

Telemetry can be disabled:
- Settings → Privacy → Disable Telemetry

Even with telemetry enabled:
- No PII collected
- All data anonymized
- Sent over HTTPS
- Not shared with third parties

---

## Incident Response

### 1. Security Incident

If you suspect a security breach:

1. **Disconnect**: Disconnect from network
2. **Report**: Email security@auraaudit.ai immediately
3. **Document**: Note what happened, when, what was accessed
4. **Preserve**: Don't delete logs or evidence
5. **Await**: Wait for security team guidance

### 2. Compromised Credentials

If credentials are compromised:

1. **Logout**: Logout from desktop app immediately
2. **Change Password**: Change password at https://app.auraaudit.ai
3. **Revoke Tokens**: Contact support to revoke all JWT tokens
4. **Audit**: Review audit logs for unauthorized access
5. **Monitor**: Monitor for suspicious activity

---

## Compliance

### 1. SOC 2 Type II

The cloud backend is SOC 2 Type II compliant:
- Access controls
- Encryption at rest and in transit
- Audit logging
- Incident response
- Business continuity

### 2. AICPA Standards

Meets AICPA requirements for audit software:
- Immutable audit trail
- Access controls
- Data integrity
- Evidence retention (7 years)

### 3. PCAOB Standards

Complies with PCAOB audit documentation requirements:
- Complete and accurate records
- Retention period (7 years)
- Protection from alteration
- Audit trail

---

## Security Checklist

### For Administrators

- [ ] Install from official source only
- [ ] Verify code signature before installation
- [ ] Configure Windows Firewall rules
- [ ] Enable BitLocker on workstations
- [ ] Enforce strong passwords
- [ ] Enable two-factor authentication
- [ ] Configure auto-update
- [ ] Review audit logs regularly
- [ ] Train users on security best practices
- [ ] Have incident response plan

### For Users

- [ ] Use strong, unique password
- [ ] Enable two-factor authentication
- [ ] Keep application updated
- [ ] Lock workstation when away
- [ ] Don't share credentials
- [ ] Report suspicious activity
- [ ] Logout when done
- [ ] Don't install on shared computers
- [ ] Verify sync status regularly
- [ ] Back up important work

---

## Security Contacts

### Report Security Issues

**Email**: security@auraaudit.ai
**PGP Key**: https://auraaudit.ai/pgp-key.asc
**Response Time**: 24 hours

### Security Updates

Subscribe to security bulletins:
https://auraaudit.ai/security-updates

---

## References

- [Electron Security Checklist](https://www.electronjs.org/docs/latest/tutorial/security)
- [OWASP Desktop App Security](https://owasp.org/www-project-desktop-app-security-top-10/)
- [Windows Security Best Practices](https://docs.microsoft.com/en-us/windows/security/)

---

**Document Version**: 1.0
**Last Updated**: November 12, 2025
**Security Team**: security@auraaudit.ai
