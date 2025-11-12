# Aura Audit AI - Smart Client for Windows

> **Enterprise-grade desktop application for CPA firms with offline-first architecture**

## Overview

The Aura Audit AI Smart Client is a **thick client** Windows desktop application that brings the power of cloud-based audit automation to your local workstation. Process data locally, work offline, and sync seamlessly with the cloud.

### Key Features

✅ **Offline-First Architecture**: Work without internet connectivity
✅ **Local Processing**: Financial analytics, ratio calculations, and validation run locally
✅ **Automatic Synchronization**: Bidirectional sync every 5 minutes
✅ **Auto-Updates**: Seamless background updates
✅ **Enterprise Security**: AES-256 encryption, secure IPC, code signing
✅ **High Performance**: Native desktop performance with Electron

---

## Architecture

### Smart Client Model

```
┌──────────────────────────────────────────────────────────────┐
│                     Your Windows PC                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          Aura Audit Client Application                 │ │
│  │                                                          │ │
│  │  • React UI (Electron Renderer)                         │ │
│  │  • Local SQLite Database                                │ │
│  │  • Analytics Processing Engine                          │ │
│  │  • Sync Engine (Cloud Integration)                      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────┬────────────────────────────────────┘
                          │ HTTPS Sync (Every 5 min)
                          ▼
           ┌──────────────────────────────┐
           │    Cloud Backend (Azure)     │
           │  • API Gateway               │
           │  • 24 Microservices          │
           │  • PostgreSQL Database       │
           │  • Document Storage          │
           └──────────────────────────────┘
```

### What Runs Locally?

The smart client processes these operations **on your workstation**:

1. **Financial Analytics**
   - Ratio calculations (liquidity, profitability, leverage)
   - Trend analysis and variance detection
   - Anomaly detection in account balances

2. **Audit Procedures**
   - Journal entry testing (round dollar, large adjustments)
   - Materiality calculations (overall, performance, specific)
   - Trial balance validation

3. **Data Validation**
   - Data quality checks
   - Format validation
   - Business rule enforcement

4. **Document Management**
   - Local document storage and indexing
   - Full-text search
   - Background cloud upload

### What Syncs to Cloud?

- Engagement data and metadata
- User profile and permissions
- Collaboration (review notes, comments)
- Documents and workpapers (backup)
- Audit reports
- Real-time updates from other users

---

## Installation

### System Requirements

- **OS**: Windows 10 (64-bit) or Windows 11
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk**: 2 GB free space (5 GB recommended)
- **Network**: Internet connection for initial setup and sync

### Quick Start

1. **Download** the installer:
   ```
   Aura-Audit-Client-Setup-1.0.0.exe
   ```

2. **Run** the installer as Administrator

3. **Launch** from Start Menu or Desktop shortcut

4. **Login** with your Aura Audit credentials

5. **Initial Sync** will download your engagements (2-10 minutes)

6. **Start Working!**

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed installation instructions.

---

## Development

### Prerequisites

- Node.js 20+
- npm or yarn
- Windows 10/11 for building Windows installers

### Setup

```bash
# Install dependencies
npm install

# Run in development mode (hot reload enabled)
npm run dev

# Build for production
npm run build:win

# Build without installer (for testing)
npm run build:dir
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
│   │   └── engine.js            # Cloud synchronization
│   └── processing/
│       └── local-processor.js   # Local analytics engine
├── src/                         # React application
│   ├── App.tsx                  # Main React component
│   ├── hooks/
│   │   └── useElectron.ts       # Electron React hooks
│   ├── pages/                   # Application pages
│   ├── components/              # Reusable components
│   └── services/                # API services
├── build/                       # Build assets
│   └── icon.ico                 # Application icon
├── dist-vite/                   # Vite build output
├── dist/                        # Electron build output
├── package.json                 # Dependencies & scripts
├── vite.config.ts               # Vite configuration
├── DEPLOYMENT.md                # Deployment guide
└── README.md                    # This file
```

---

## Usage

### First Launch

1. **Authentication**: Enter your credentials
   - Email: your-email@firm.com
   - Password: •••••••••
   - Cloud URL: https://api.auraaudit.ai (default)

2. **Initial Sync**: Wait for data to download
   - Your organization profile
   - Assigned engagements
   - Recent documents
   - Analytics history

3. **Ready**: Start working!

### Working Offline

The application automatically detects when you're offline:

✅ **Available Offline:**
- View all locally cached engagements
- Upload and view documents
- Perform analytics (ratios, anomalies, JE tests)
- Calculate materiality
- Validate trial balances
- Edit engagement data

❌ **Requires Online:**
- Fetch new engagements from cloud
- Real-time collaboration
- AI-powered features (LLM analysis)
- Initial setup and login

### Syncing

**Automatic Sync**: Every 5 minutes (configurable)

**Manual Sync**:
- Click sync icon in header
- Press `Ctrl+Shift+S`
- Settings → Sync → "Sync Now"

**Sync Indicator**:
- 🟢 Green: Synced successfully
- 🟡 Yellow: Syncing in progress
- 🔴 Red: Sync error
- ⚫ Gray: Offline

### Local Analytics

Process analytics locally for instant results:

```typescript
import { useLocalProcessor } from '@/hooks/useElectron';

function EngagementAnalytics({ engagementId }) {
  const { processAnalytics } = useLocalProcessor();

  const runAnalytics = async () => {
    const results = await processAnalytics(engagementId);
    console.log('Ratios:', results.analytics.ratios);
    console.log('Anomalies:', results.analytics.anomalies);
    console.log('JE Tests:', results.analytics.jeTests);
  };

  return <button onClick={runAnalytics}>Run Analytics</button>;
}
```

---

## API Reference

### Electron IPC API

The application exposes a secure API via `window.electron`:

#### Database API

```typescript
// Query database
const engagements = await window.electron.db.query(
  'SELECT * FROM engagements WHERE status = ?',
  ['active']
);

// Execute command
await window.electron.db.execute(
  'INSERT INTO engagements (id, client_name) VALUES (?, ?)',
  ['eng-123', 'ABC Corp']
);

// Get statistics
const stats = await window.electron.db.getStats();
// { organizations: 1, engagements: 45, documents: 234, ... }
```

#### Sync API

```typescript
// Start sync
await window.electron.sync.start(authToken);

// Get status
const status = await window.electron.sync.getStatus();
// { isRunning: true, lastSync: 1699999999999, ... }

// Force immediate sync
await window.electron.sync.force();

// Listen for sync changes
const unsubscribe = window.electron.sync.onStatusChange((status) => {
  console.log('Sync status:', status);
});
```

#### Local Processing API

```typescript
// Process analytics
const results = await window.electron.process.analytics('engagement-id');

// Validate data
const validation = await window.electron.process.validate(
  trialBalanceData,
  'trial_balance'
);

// Calculate ratios
const ratios = await window.electron.process.ratios(financialData);
```

#### Settings API

```typescript
// Get setting
const syncInterval = await window.electron.settings.get('syncIntervalMs', 300000);

// Set setting
await window.electron.settings.set('syncIntervalMs', 600000);

// Get all settings
const allSettings = await window.electron.settings.getAll();
```

#### Updates API

```typescript
// Check for updates
await window.electron.updates.check();

// Install update (restarts app)
await window.electron.updates.install();

// Listen for update events
window.electron.updates.onAvailable((info) => {
  console.log('Update available:', info.version);
});

window.electron.updates.onDownloaded((info) => {
  console.log('Update ready to install');
});
```

### React Hooks

The application provides React hooks for easy integration:

```typescript
import {
  useIsElectron,
  useDatabase,
  useSync,
  useLocalProcessor,
  useSettings,
  useUpdates,
  useSystemInfo,
  useDatabaseStats
} from '@/hooks/useElectron';

// Check if running in Electron
const isElectron = useIsElectron();

// Database operations
const { query, execute, getStats } = useDatabase();

// Sync status and controls
const { status, loading, start, stop, force } = useSync();

// Local processing
const { processAnalytics, validate, calculateRatios } = useLocalProcessor();

// Settings management
const { value, setValue, loading } = useSettings('syncIntervalMs', 300000);

// Update management
const { updateAvailable, downloadProgress, installUpdate } = useUpdates();

// System information
const { systemInfo, version, platform, openExternal } = useSystemInfo();

// Database statistics
const { stats, loading, refresh } = useDatabaseStats();
```

---

## Security

### Data Security

- **Encryption at Rest**: SQLite database encrypted with AES-256
- **Encryption in Transit**: All API calls over HTTPS (TLS 1.3)
- **Secure Credential Storage**: JWT tokens in encrypted electron-store
- **No Password Storage**: Passwords never stored locally

### Application Security

- **Sandboxed Renderer**: Renderer process runs in sandbox mode
- **Context Isolation**: Prevents prototype pollution attacks
- **Secure IPC**: All communication through controlled preload script
- **Content Security Policy**: Strict CSP to prevent XSS
- **Code Signing**: All releases signed with EV certificate

### Network Security

- **Certificate Pinning**: Cloud API certificate verification
- **Token Expiration**: JWT tokens expire after 8 hours
- **Rate Limiting**: Protection against abuse
- **Audit Logging**: All API calls logged

---

## Troubleshooting

### App Won't Start

```bash
# Check logs
type %APPDATA%\aura-audit-client\logs\main.log

# Run as Administrator
Right-click → Run as Administrator

# Reinstall
Uninstall and reinstall the application
```

### Sync Not Working

```bash
# Check internet connection
ping api.auraaudit.ai

# Force sync
Ctrl+Shift+S

# Check sync queue
Settings → Database → View Sync Queue

# Re-authenticate
Logout and login again
```

### Performance Issues

```bash
# Clear cache
Settings → Database → Clear Cache

# Increase sync interval
Settings → Sync → Interval: 15 minutes

# Check disk space
Need at least 2GB free
```

### Database Corruption

```bash
# Backup database
copy %APPDATA%\aura-audit-client\aura-audit.db aura-audit-backup.db

# Delete and re-sync
del %APPDATA%\aura-audit-client\aura-audit.db
# Restart app (will re-download from cloud)
```

---

## Building from Source

### Development Build

```bash
npm run dev
```

This starts:
1. Vite dev server on http://localhost:3000
2. Electron window with hot reload
3. DevTools open

### Production Build

```bash
# Build for Windows (NSIS + MSI)
npm run build:win

# Output:
# dist/Aura-Audit-Client-Setup-1.0.0.exe   (NSIS installer)
# dist/Aura-Audit-Client-1.0.0.msi         (MSI installer)
# dist/win-unpacked/                        (Portable)
```

### Code Signing

For production releases:

```bash
# Set environment variables
set CSC_LINK=path\to\certificate.pfx
set CSC_KEY_PASSWORD=your-password

# Build with signing
npm run build:win
```

---

## Configuration

### Environment Variables

```bash
# Development
NODE_ENV=development
VITE_API_URL=http://localhost:8000

# Production
NODE_ENV=production
VITE_API_URL=https://api.auraaudit.ai
```

### Electron Builder Config

See `package.json` → `build` section:

```json
{
  "build": {
    "appId": "com.auraaudit.client",
    "productName": "Aura Audit Client",
    "win": {
      "target": ["nsis", "msi"],
      "icon": "build/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "perMachine": true,
      "allowToChangeInstallationDirectory": true
    }
  }
}
```

---

## Contributing

This is a proprietary application. For internal development:

1. Create a feature branch
2. Make your changes
3. Run tests: `npm test`
4. Build locally: `npm run build:dir`
5. Submit pull request

---

## Support

- **Documentation**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Email**: support@auraaudit.ai
- **Phone**: 1-800-AURA-AUDIT
- **Web**: https://docs.auraaudit.ai

---

## License

Proprietary - Aura Audit AI © 2025

---

**Version**: 1.0.0
**Last Updated**: November 12, 2025
**Electron**: 28.1.0
**React**: 18.2.0
