# Smart Client Architecture for Aura Audit AI

## Executive Summary

This document describes the transformation of Aura Audit AI into a **smart client deployment model** for Windows workstations. The smart client architecture provides enterprise-grade desktop application capabilities with offline-first design, local processing, and seamless cloud synchronization.

## What is a Smart Client?

A **smart client** (also called a thick client or rich client) is a desktop application that:

1. **Installs locally** on each user's Windows workstation
2. **Processes application logic locally** on the user's device
3. **Stores data locally** for offline access
4. **Synchronizes with cloud servers** for data backup and sharing
5. **Auto-updates** from the cloud without user intervention

### Smart Client vs. Other Models

| Feature | Thin Client (Web) | Smart Client | Thick Client |
|---------|-------------------|--------------|--------------|
| Installation | None (browser) | Desktop app | Desktop app |
| Processing | Server-side | Local + Cloud | Local only |
| Offline Mode | ❌ No | ✅ Yes | ✅ Yes |
| Auto-Updates | ✅ Automatic | ✅ Automatic | ❌ Manual |
| Cloud Sync | N/A | ✅ Yes | ❌ No |
| Performance | Network-dependent | Fast (local) | Fast (local) |
| Deployment | Easy | Medium | Complex |

---

## Architecture Overview

### High-Level Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                   Windows Workstation (Local)                  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │         Aura Audit Client Desktop Application            │ │
│  │                                                            │ │
│  │  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │  React UI      │  │  Business    │  │  Local Data  │ │ │
│  │  │  (Electron)    │  │  Logic       │  │  Storage     │ │ │
│  │  │                │  │  Engine      │  │  (SQLite)    │ │ │
│  │  └────────────────┘  └──────────────┘  └──────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │            Sync Engine (Bidirectional)               │ │ │
│  │  │  • Push local changes to cloud                       │ │ │
│  │  │  • Pull updates from cloud                           │ │ │
│  │  │  • Conflict resolution                               │ │ │
│  │  │  • Runs every 5 minutes                              │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────┬───────────────────────────────────┘
                             │ HTTPS/TLS 1.3
                             │ Sync every 5 min
                             │
                             ▼
         ┌────────────────────────────────────────┐
         │    Cloud Backend (Azure/AWS)           │
         │                                        │
         │  • API Gateway                         │
         │  • 24 Microservices (FastAPI)          │
         │  • PostgreSQL Database                 │
         │  • Redis Cache                         │
         │  • Azure Blob Storage (Documents)      │
         │  • Auto-Update Server                  │
         └────────────────────────────────────────┘
```

### Technology Stack

**Desktop Application:**
- **Frontend Framework**: React 18 + TypeScript
- **Desktop Framework**: Electron 28
- **Build Tool**: Vite 5
- **Local Database**: SQLite (better-sqlite3)
- **State Management**: Zustand + React Query
- **UI Components**: Tailwind CSS + Framer Motion

**Backend Services (Cloud):**
- **API Gateway**: FastAPI (Python)
- **Microservices**: 24 FastAPI services
- **Database**: PostgreSQL 15 with pgvector
- **Cache**: Redis
- **Storage**: Azure Blob Storage / AWS S3
- **Orchestration**: Docker + Kubernetes

---

## Key Features

### 1. Local Processing

The smart client processes these operations **locally on the workstation**:

#### Financial Analytics
- **Ratio Calculations**: Liquidity, profitability, leverage, and activity ratios
- **Trend Analysis**: Historical comparisons and variance detection
- **Anomaly Detection**: Unusual balances, trial balance imbalances, outliers
- **Journal Entry Testing**: Round dollar testing, large adjustments, timing analysis

#### Audit Procedures
- **Materiality Calculations**: Overall, performance, and specific materiality
- **Trial Balance Validation**: Balance checks and account structure validation
- **Data Quality Checks**: Missing fields, invalid formats, data integrity
- **Sampling**: Audit sampling strategies

#### Benefits of Local Processing
- ⚡ **Instant Results**: No network latency
- 📶 **Works Offline**: No internet required for analysis
- 💪 **Server Load Reduction**: Offloads processing from cloud
- 🎯 **Better User Experience**: Responsive and fast

### 2. Offline-First Architecture

The application is designed to work **without internet connectivity**:

**Available Offline:**
- ✅ View all locally cached engagements
- ✅ Upload and view documents
- ✅ Perform financial analytics
- ✅ Calculate ratios and materiality
- ✅ Validate trial balances
- ✅ Edit engagement data
- ✅ Search documents
- ✅ Generate reports (from cached data)

**Requires Online:**
- ❌ Fetch new engagements from cloud
- ❌ Real-time collaboration
- ❌ AI-powered features (LLM analysis)
- ❌ Initial setup and login

**Sync Queue:**
All changes made offline are queued and automatically synced when connection is restored.

### 3. Bidirectional Synchronization

**Sync Strategy:**

```
┌─────────────────────────────────────────────────────────────┐
│                  Sync Cycle (Every 5 Minutes)                │
└─────────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         │                                     │
         ▼                                     ▼
┌─────────────────┐                   ┌─────────────────┐
│  PUSH TO CLOUD  │                   │ PULL FROM CLOUD │
│                 │                   │                 │
│ • Creates       │                   │ • Engagements   │
│ • Updates       │                   │ • Documents     │
│ • Deletes       │                   │ • Mappings      │
│ • Documents     │                   │ • Analytics     │
└─────────────────┘                   └─────────────────┘
         │                                     │
         └──────────────────┬──────────────────┘
                            │
                    ┌───────▼────────┐
                    │ Conflict       │
                    │ Resolution     │
                    │ (Last Write    │
                    │  Wins)         │
                    └────────────────┘
```

**Conflict Resolution:**
- Timestamp-based (last write wins)
- User notified of conflicts
- Option to manually resolve conflicts

**Sync Monitoring:**
- Real-time sync status indicator
- Pending changes count
- Last sync timestamp
- Error reporting

### 4. Auto-Update System

**electron-updater** provides seamless updates:

1. **Check for Updates**: On app start and every 6 hours
2. **Download in Background**: User continues working
3. **Notify User**: "Update available" notification
4. **Install on Restart**: Or user can install immediately
5. **Rollback**: Automatic rollback if update fails

**Update Server:**
- Production: `https://updates.auraaudit.ai`
- Serves Windows installers (NSIS + MSI)
- Code-signed for security
- SHA-512 checksum verification

---

## Local Data Storage

### SQLite Database Schema

```sql
-- Organizations
CREATE TABLE organizations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  settings TEXT,
  synced_at INTEGER,
  updated_at INTEGER NOT NULL
);

-- Engagements
CREATE TABLE engagements (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  client_name TEXT NOT NULL,
  year_end TEXT NOT NULL,
  status TEXT NOT NULL,
  synced_at INTEGER,
  updated_at INTEGER NOT NULL
);

-- Trial Balances
CREATE TABLE trial_balances (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL,
  data TEXT NOT NULL,
  synced_at INTEGER,
  uploaded_at INTEGER NOT NULL
);

-- Sync Queue
CREATE TABLE sync_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  operation TEXT NOT NULL,  -- 'create', 'update', 'delete'
  data TEXT NOT NULL,
  retry_count INTEGER DEFAULT 0,
  created_at INTEGER NOT NULL
);
```

### Storage Locations

**Windows:**
- Database: `%APPDATA%\aura-audit-client\aura-audit.db`
- Documents: `%APPDATA%\aura-audit-client\documents\`
- Logs: `%APPDATA%\aura-audit-client\logs\`
- Settings: `%APPDATA%\aura-audit-client\config.json`

---

## Security

### Application Security

1. **Sandboxed Renderer**: Renderer process runs in sandbox
2. **Context Isolation**: Prevents prototype pollution
3. **Secure IPC**: All communication through preload script
4. **No Node Integration**: Node.js disabled in renderer
5. **Content Security Policy**: Strict CSP to prevent XSS

### Data Security

1. **Encryption at Rest**: SQLite database encrypted (future: SQLCipher)
2. **Encryption in Transit**: All API calls over HTTPS/TLS 1.3
3. **Secure Credential Storage**: JWT tokens in encrypted electron-store
4. **No Password Storage**: Passwords never stored locally

### Update Security

1. **Code Signing**: All releases signed with EV certificate
2. **Checksum Verification**: SHA-512 checksums verified
3. **HTTPS Only**: Updates only over encrypted connections

---

## Deployment

### Installation Methods

#### Method 1: NSIS Installer (End Users)
```powershell
# Download and run
Aura-Audit-Client-Setup-1.0.0.exe

# Silent install
Aura-Audit-Client-Setup-1.0.0.exe /S
```

#### Method 2: MSI Installer (Enterprise)
```powershell
# Interactive install
msiexec /i Aura-Audit-Client-1.0.0.msi

# Silent install
msiexec /i Aura-Audit-Client-1.0.0.msi /qn

# With logging
msiexec /i Aura-Audit-Client-1.0.0.msi /qn /l*v install.log
```

#### Method 3: Group Policy (Enterprise)
```powershell
# Deploy via GPO
1. Copy MSI to network share
2. Create GPO → Software Installation
3. Add package and assign to computers
4. Automatic installation on next reboot
```

### System Requirements

**Minimum:**
- Windows 10 (64-bit) or Windows 11
- 4 GB RAM
- 2 GB disk space
- Internet connection

**Recommended:**
- Windows 11
- 8 GB RAM
- 5 GB disk space
- Broadband internet

---

## Developer Guide

### Development Setup

```bash
cd client-portal-desktop

# Install dependencies
npm install

# Run in development mode
npm run dev
# This starts Vite dev server and Electron with hot reload

# Build for production
npm run build:win
# Creates NSIS and MSI installers in dist/
```

### Project Structure

```
client-portal-desktop/
├── electron/                    # Electron main process
│   ├── main.js                  # Application entry point
│   ├── preload.js               # Secure IPC bridge
│   ├── database/
│   │   └── manager.js           # SQLite database manager
│   ├── sync/
│   │   └── engine.js            # Bidirectional sync engine
│   └── processing/
│       └── local-processor.js   # Local analytics engine
├── src/                         # React application
│   ├── App.tsx
│   ├── hooks/
│   │   └── useElectron.ts       # React hooks for Electron
│   ├── pages/
│   ├── components/
│   └── services/
├── build/
│   └── icon.ico                 # Application icon
├── package.json                 # Dependencies & build config
├── vite.config.ts               # Vite configuration
├── DEPLOYMENT.md                # Deployment guide
├── SECURITY.md                  # Security documentation
└── README.md                    # User guide
```

### API Reference

**React Hooks:**

```typescript
import {
  useIsElectron,      // Check if running in Electron
  useDatabase,        // Database operations
  useSync,            // Sync status and controls
  useLocalProcessor,  // Local analytics
  useSettings,        // Application settings
  useUpdates,         // Auto-update management
  useDatabaseStats    // Database statistics
} from '@/hooks/useElectron';
```

**Electron IPC API:**

```typescript
// Database
await window.electron.db.query(sql, params);
await window.electron.db.execute(sql, params);

// Sync
await window.electron.sync.start(authToken);
await window.electron.sync.force();
const status = await window.electron.sync.getStatus();

// Processing
const results = await window.electron.process.analytics(engagementId);
const ratios = await window.electron.process.ratios(financialData);

// Settings
await window.electron.settings.set('key', 'value');
const value = await window.electron.settings.get('key');

// Updates
await window.electron.updates.check();
await window.electron.updates.install();
```

---

## Benefits of Smart Client Architecture

### For End Users

1. **⚡ Fast Performance**: Local processing eliminates network latency
2. **📶 Offline Capability**: Work without internet connection
3. **💾 Automatic Backup**: Data syncs to cloud automatically
4. **🔄 Seamless Updates**: App updates in background
5. **🖥️ Native Experience**: Windows-native UI and interactions

### For Organizations

1. **📉 Reduced Server Load**: Processing happens on client devices
2. **💰 Lower Cloud Costs**: Less compute and bandwidth usage
3. **🔒 Enhanced Security**: Data encrypted locally and in transit
4. **📊 Better Control**: Centralized deployment and updates via GPO
5. **🌐 Scalability**: Scales with number of users, not server capacity

### For IT Administrators

1. **🚀 Easy Deployment**: MSI installer + Group Policy
2. **🔄 Automatic Updates**: No manual update distribution
3. **📝 Centralized Logging**: Remote monitoring and diagnostics
4. **🛡️ Security Compliance**: Code signing, encryption, audit trails
5. **💻 Standard Windows App**: Integrates with existing IT infrastructure

---

## Migration from Web to Desktop

### Phase 1: Initial Setup (Complete)
- ✅ Electron application scaffold
- ✅ Local database with SQLite
- ✅ Sync engine implementation
- ✅ Local processing engine
- ✅ Auto-update system
- ✅ Documentation

### Phase 2: Feature Parity (Next Steps)
- [ ] Copy React components from client-portal
- [ ] Integrate authentication
- [ ] Implement document management
- [ ] Add offline indicators
- [ ] Testing and QA

### Phase 3: Deployment (Future)
- [ ] Code signing certificate
- [ ] Update server setup
- [ ] Pilot deployment
- [ ] User training
- [ ] Production rollout

---

## Comparison: Before vs. After

### Before (Web Application)

```
User → Browser → Internet → Cloud API → Database
                  ↑
              Bottleneck: Network latency
              Single point of failure
              Requires constant connectivity
```

**Issues:**
- ❌ Requires internet for all operations
- ❌ Network latency affects performance
- ❌ Server costs scale with users
- ❌ No offline capability
- ❌ Browser compatibility issues

### After (Smart Client)

```
User → Desktop App → Local Database
           ↓
       Local Processing
           ↓
       Sync Engine → Cloud (every 5 min)
```

**Benefits:**
- ✅ Works offline
- ✅ Instant local processing
- ✅ Lower server costs
- ✅ Better user experience
- ✅ Native Windows features

---

## Conclusion

The Smart Client architecture transforms Aura Audit AI into a **powerful desktop application** that combines the best of both worlds:

- **Cloud connectivity** for data backup, sharing, and collaboration
- **Local processing** for performance, offline capability, and reduced costs

This architecture is ideal for **enterprise environments** where:
- Users work on dedicated Windows workstations
- Offline capability is required
- Performance is critical
- Security and control are paramount

---

## Next Steps

1. **Review Documentation**:
   - [README.md](client-portal-desktop/README.md) - User guide
   - [DEPLOYMENT.md](client-portal-desktop/DEPLOYMENT.md) - Installation guide
   - [SECURITY.md](client-portal-desktop/SECURITY.md) - Security documentation

2. **Development**:
   ```bash
   cd client-portal-desktop
   npm install
   npm run dev
   ```

3. **Build**:
   ```bash
   npm run build:win
   ```

4. **Deploy**:
   - Test installer on Windows VM
   - Set up update server
   - Create deployment plan
   - Train end users

---

**Document Version**: 1.0
**Date**: November 12, 2025
**Author**: Aura Audit AI Engineering Team
