# Aura Audit AI - Smart Client Deployment Guide

## Overview

This document describes the deployment architecture and procedures for the Aura Audit AI Smart Client application for Windows workstations.

## Architecture

### Smart Client Model

The Aura Audit AI Smart Client is a **thick client** application that:

1. **Runs locally** on Windows workstations (Windows 10/11)
2. **Processes business logic locally** for better performance and offline capability
3. **Stores data locally** in SQLite database for offline access
4. **Synchronizes with cloud** for data backup, sharing, and server-side updates
5. **Auto-updates** seamlessly from the cloud

### Technology Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Desktop Framework**: Electron 28
- **Local Database**: SQLite (better-sqlite3)
- **State Management**: Zustand + React Query
- **Sync Engine**: Custom bidirectional sync with conflict resolution
- **Installer**: NSIS (Nullsoft Scriptable Install System) + MSI
- **Auto-Update**: electron-updater

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Windows Workstation                        │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Aura Audit Client (Electron App)              │  │
│  │                                                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │ React UI     │  │ Local        │  │ Sync Engine │ │  │
│  │  │ (Renderer)   │  │ Processor    │  │             │ │  │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │  │
│  │         │                  │                  │        │  │
│  │         └──────────────────┴──────────────────┘        │  │
│  │                         │                               │  │
│  │                  ┌──────▼──────┐                        │  │
│  │                  │   SQLite    │                        │  │
│  │                  │  Database   │                        │  │
│  │                  └─────────────┘                        │  │
│  └───────────────────────────┬─────────────────────────────┘  │
│                              │                                │
└──────────────────────────────┼────────────────────────────────┘
                               │ HTTPS (TLS 1.3)
                               │ Every 5 minutes
                               ▼
              ┌────────────────────────────────┐
              │     Cloud Backend (Azure)      │
              │                                │
              │  ┌──────────────────────────┐  │
              │  │  API Gateway (8000)      │  │
              │  └──────────────────────────┘  │
              │  ┌──────────────────────────┐  │
              │  │  24 Microservices        │  │
              │  │  (FastAPI)               │  │
              │  └──────────────────────────┘  │
              │  ┌──────────────────────────┐  │
              │  │  PostgreSQL + Redis      │  │
              │  └──────────────────────────┘  │
              │  ┌──────────────────────────┐  │
              │  │  Azure Blob Storage      │  │
              │  └──────────────────────────┘  │
              └────────────────────────────────┘
```

---

## Local Processing Capabilities

The smart client processes the following operations **locally** without requiring cloud connectivity:

### 1. Financial Analytics
- **Ratio Analysis**: Current ratio, quick ratio, debt-to-equity, ROA, ROE
- **Trend Analysis**: Historical comparisons and variance analysis
- **Anomaly Detection**: Unusual balances, trial balance imbalances, outliers
- **Journal Entry Testing**: Round dollar testing, large adjustments, timing analysis

### 2. Data Validation
- **Trial Balance Validation**: Balance checks, account structure validation
- **Data Quality Checks**: Missing fields, invalid formats, data integrity
- **Compliance Checks**: Basic GAAP validation rules

### 3. Materiality Calculations
- **Overall Materiality**: Based on assets, revenue, net income benchmarks
- **Performance Materiality**: 70% of overall materiality
- **Specific Materiality**: For sensitive account classes
- **Clearly Trivial Threshold**: 5% of overall materiality

### 4. Document Management
- **Local Storage**: Documents stored locally for offline access
- **Background Upload**: Syncs to cloud when connection available
- **Search & Indexing**: Fast local document search

---

## Installation

### System Requirements

**Minimum Requirements:**
- Windows 10 (64-bit) or Windows 11
- 4 GB RAM
- 2 GB free disk space
- Internet connection (for initial setup and sync)

**Recommended:**
- Windows 11
- 8 GB RAM
- 5 GB free disk space
- Broadband internet connection

### Installation Methods

#### Method 1: NSIS Installer (Recommended for single workstations)

1. Download `Aura-Audit-Client-Setup-1.0.0.exe` from the distribution server
2. Run the installer as Administrator
3. Follow the installation wizard:
   - Choose installation directory (default: `C:\Program Files\Aura Audit Client`)
   - Select whether to install for all users or current user
   - Create desktop shortcut
4. Launch the application from the Start Menu or Desktop shortcut

#### Method 2: MSI Installer (Recommended for enterprise deployment)

1. Download `Aura-Audit-Client-1.0.0.msi`
2. Run the MSI as Administrator
3. Follow the installation wizard

#### Method 3: Group Policy Deployment (Enterprise)

For large organizations deploying to multiple workstations:

```powershell
# Using Group Policy Object (GPO)
1. Copy the MSI to a network share accessible by all computers
2. Create a new GPO in Active Directory
3. Navigate to: Computer Configuration → Policies → Software Settings → Software Installation
4. Right-click → New → Package
5. Select the MSI file from the network share
6. Choose "Assigned" deployment method
7. Link the GPO to the appropriate OU

# Alternative: PowerShell deployment script
$computers = Get-Content "computers.txt"
foreach ($computer in $computers) {
    Copy-Item "Aura-Audit-Client-1.0.0.msi" "\\$computer\c$\temp\"
    Invoke-Command -ComputerName $computer -ScriptBlock {
        Start-Process msiexec.exe -ArgumentList "/i C:\temp\Aura-Audit-Client-1.0.0.msi /qn" -Wait
    }
}
```

---

## Configuration

### First Launch

1. **Authentication**: Users must authenticate with their Aura Audit credentials
   - Cloud URL: `https://api.auraaudit.ai` (default)
   - Email and password login
   - OAuth/SSO support (Azure AD, Okta)

2. **Initial Sync**: The application will perform an initial data synchronization
   - Downloads organization data
   - Downloads assigned engagements
   - Downloads recent documents
   - Estimated time: 2-10 minutes depending on data volume

3. **Settings Configuration**:
   - Sync interval (default: 5 minutes)
   - Offline mode preferences
   - Local storage location
   - Update preferences

### Configuration Files

Configuration is stored in:
- **Windows**: `%APPDATA%\aura-audit-client\config.json`
- **Electron Store**: Encrypted settings in `electron-store`

```json
{
  "cloudApiUrl": "https://api.auraaudit.ai",
  "syncIntervalMs": 300000,
  "offlineMode": false,
  "autoUpdate": true,
  "logLevel": "info"
}
```

---

## Synchronization

### Sync Strategy

The application uses an **offline-first** architecture with bidirectional synchronization:

1. **Local changes** are queued in `sync_queue` table
2. **Sync runs every 5 minutes** (configurable)
3. **Changes are pushed** to cloud (creates, updates, deletes)
4. **Updates are pulled** from cloud (new data, modifications)
5. **Conflict resolution**: Last-write-wins with timestamp comparison

### Sync Process

```
┌─────────────────────────────────────────────────────────┐
│                    Sync Cycle (5 min)                    │
└─────────────────────────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         ┌──────▼──────┐       ┌─────▼──────┐
         │    PUSH     │       │    PULL    │
         │   Local     │       │   Cloud    │
         │  Changes    │       │  Updates   │
         └─────────────┘       └────────────┘
                │                     │
      ┌─────────┴─────────┐  ┌────────┴────────┐
      │ • Creates         │  │ • Engagements   │
      │ • Updates         │  │ • Trial Balance │
      │ • Deletes         │  │ • Mappings      │
      │ • Documents       │  │ • Analytics     │
      └───────────────────┘  └─────────────────┘
```

### Offline Mode

When offline, the application:
- ✅ Continues to work with locally cached data
- ✅ Queues all changes for later sync
- ✅ Performs local processing (analytics, validation)
- ✅ Stores documents locally
- ❌ Cannot fetch new engagements from cloud
- ❌ Cannot fetch real-time updates from other users

### Manual Sync

Users can force an immediate sync:
- Click the sync icon in the application header
- Keyboard shortcut: `Ctrl+Shift+S`
- Settings → Sync → "Sync Now" button

---

## Auto-Updates

### Update Mechanism

The application uses **electron-updater** for seamless auto-updates:

1. **Check for updates** on application start and every 6 hours
2. **Download updates** in the background
3. **Notify user** when update is ready
4. **Install on next restart** (or user can install immediately)

### Update Server

Updates are served from:
- **Production**: `https://updates.auraaudit.ai`
- **Staging**: `https://updates-staging.auraaudit.ai`

### Update Configuration

```javascript
// electron-builder publish configuration
{
  "publish": {
    "provider": "generic",
    "url": "https://updates.auraaudit.ai"
  }
}
```

### Serving Updates

Update files must be hosted on a static server with the following structure:

```
https://updates.auraaudit.ai/
├── latest.yml                    # Update manifest for Windows
├── Aura-Audit-Client-Setup-1.0.0.exe
├── Aura-Audit-Client-Setup-1.0.0.exe.blockmap
├── Aura-Audit-Client-1.0.0.msi
└── releases/
    ├── 1.0.0/
    │   ├── RELEASES
    │   └── ...
    └── 1.0.1/
        └── ...
```

**latest.yml** example:
```yaml
version: 1.0.1
releaseDate: '2025-11-15T10:00:00.000Z'
files:
  - url: Aura-Audit-Client-Setup-1.0.1.exe
    sha512: abc123...
    size: 75234567
path: Aura-Audit-Client-Setup-1.0.1.exe
sha512: abc123...
releaseNotes: |
  - Fixed sync issue with large files
  - Improved offline analytics performance
  - Security updates
```

### Disabling Auto-Update

For enterprise environments that control updates centrally:

```javascript
// In main.js, comment out or remove:
// autoUpdater.checkForUpdatesAndNotify();

// Or set in config:
{
  "autoUpdate": false
}
```

---

## Building the Application

### Development Setup

```bash
# Clone the repository
cd client-portal-desktop

# Install dependencies
npm install

# Run in development mode
npm run dev

# This will:
# 1. Start Vite dev server (http://localhost:3000)
# 2. Launch Electron window pointing to dev server
# 3. Enable hot reload
```

### Production Build

```bash
# Build for Windows
npm run build:win

# This creates:
# - dist/Aura-Audit-Client-Setup-1.0.0.exe (NSIS installer)
# - dist/Aura-Audit-Client-1.0.0.msi (MSI installer)
# - dist/win-unpacked/ (portable version)

# Build directory only (for testing)
npm run build:dir
```

### Code Signing (Production)

For production releases, sign the executables with a code signing certificate:

```bash
# Install Windows SDK for signtool
# Or use electron-builder with certificate

# electron-builder configuration
{
  "win": {
    "certificateFile": "cert.pfx",
    "certificatePassword": "password",
    "signingHashAlgorithms": ["sha256"],
    "rfc3161TimeStampServer": "http://timestamp.digicert.com"
  }
}

# Environment variables
export CSC_LINK=path/to/cert.pfx
export CSC_KEY_PASSWORD=password
npm run build:win
```

---

## Security

### Data Security

1. **Local Database Encryption**:
   - SQLite database uses SQLCipher for encryption
   - Encryption key derived from user credentials
   - AES-256 encryption at rest

2. **Communication Security**:
   - All API calls use HTTPS (TLS 1.3)
   - Certificate pinning for cloud API
   - JWT tokens for authentication

3. **Credential Storage**:
   - Passwords never stored locally
   - JWT tokens stored in encrypted electron-store
   - Windows Credential Manager integration (optional)

### Application Security

1. **Sandboxing**: Renderer process runs in sandbox mode
2. **Context Isolation**: Enabled to prevent prototype pollution
3. **Node Integration**: Disabled in renderer
4. **Secure IPC**: All communication through preload script
5. **Content Security Policy**: Strict CSP headers

### Update Security

1. **Code Signing**: All releases signed with EV certificate
2. **Update Verification**: SHA-512 checksums verified before installation
3. **HTTPS Only**: Updates only over encrypted connections

---

## Monitoring & Logging

### Local Logs

Logs are stored in:
- **Windows**: `%APPDATA%\aura-audit-client\logs\`

Log files:
- `main.log`: Electron main process logs
- `renderer.log`: Browser console logs
- `sync.log`: Synchronization logs
- `analytics.log`: Local processing logs

### Log Levels

- `error`: Critical errors
- `warn`: Warnings and potential issues
- `info`: Informational messages (default)
- `debug`: Detailed debugging information

### Remote Monitoring

The application can optionally send telemetry to the cloud:
- Application version and platform
- Sync status and performance metrics
- Error reports and stack traces
- Usage analytics (anonymized)

Users can opt-out in Settings → Privacy.

---

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Symptoms**: Double-click icon, nothing happens

**Solutions**:
- Check Windows Event Viewer for errors
- Run as Administrator
- Check antivirus isn't blocking
- Reinstall the application
- Check logs in `%APPDATA%\aura-audit-client\logs\main.log`

#### 2. Sync Failures

**Symptoms**: "Sync failed" error, data not updating

**Solutions**:
- Check internet connection
- Verify cloud API is accessible: `curl https://api.auraaudit.ai/health`
- Check JWT token hasn't expired (logout and login again)
- Force sync: Ctrl+Shift+S
- Check sync queue: Settings → Database → View Sync Queue

#### 3. Database Corruption

**Symptoms**: "Database error" messages, app crashes

**Solutions**:
- Close the application
- Backup database: Copy `%APPDATA%\aura-audit-client\aura-audit.db`
- Delete database (will re-sync from cloud)
- Restart application
- Initial sync will restore data

#### 4. Performance Issues

**Symptoms**: Slow application, high CPU/memory usage

**Solutions**:
- Close other applications
- Increase sync interval: Settings → Sync → Interval: 15 minutes
- Clear local cache: Settings → Database → Clear Cache
- Check disk space (need 2GB free)
- Update to latest version

---

## Uninstallation

### Standard Uninstall

1. Open Windows Settings → Apps
2. Find "Aura Audit Client"
3. Click Uninstall
4. Follow the uninstaller wizard

### Complete Removal

To remove all application data:

```powershell
# Uninstall application
# (Use Add/Remove Programs or run uninstaller)

# Remove user data
Remove-Item -Recurse "$env:APPDATA\aura-audit-client"

# Remove local storage
Remove-Item -Recurse "$env:LOCALAPPDATA\aura-audit-client"
```

---

## Enterprise Deployment Checklist

- [ ] Review system requirements
- [ ] Prepare installation package (NSIS or MSI)
- [ ] Configure Group Policy (if applicable)
- [ ] Test deployment on pilot group
- [ ] Configure cloud API endpoint
- [ ] Set up update server
- [ ] Configure firewall rules (allow HTTPS to api.auraaudit.ai)
- [ ] Train users on installation and usage
- [ ] Prepare helpdesk documentation
- [ ] Monitor initial rollout for issues
- [ ] Collect feedback and iterate

---

## Support

For deployment support:
- **Email**: support@auraaudit.ai
- **Documentation**: https://docs.auraaudit.ai
- **Phone**: 1-800-AURA-AUDIT

---

**Document Version**: 1.0
**Last Updated**: November 12, 2025
**Author**: Aura Audit AI Engineering Team
