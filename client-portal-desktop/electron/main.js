const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { autoUpdater } = require('electron-updater');
const log = require('electron-log');
const Store = require('electron-store');
const DatabaseManager = require('./database/manager');
const SyncEngine = require('./sync/engine');
const LocalProcessor = require('./processing/local-processor');

// Configure logging
log.transports.file.level = 'info';
autoUpdater.logger = log;

// Initialize electron-store for settings
const store = new Store();

// Global references
let mainWindow = null;
let dbManager = null;
let syncEngine = null;
let localProcessor = null;

/**
 * Create the main application window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    title: 'Aura Audit Client',
    backgroundColor: '#ffffff',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js'),
      sandbox: false
    },
    show: false, // Don't show until ready
    icon: path.join(__dirname, '../build/icon.ico')
  });

  // Load the application
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist-vite/index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Check for updates
  if (process.env.NODE_ENV !== 'development') {
    setTimeout(() => {
      checkForUpdates();
    }, 3000);
  }
}

/**
 * Initialize local database and services
 */
async function initializeServices() {
  try {
    log.info('Initializing local services...');

    // Get user data path
    const userDataPath = app.getPath('userData');
    const dbPath = path.join(userDataPath, 'aura-audit.db');

    // Initialize database
    dbManager = new DatabaseManager(dbPath);
    await dbManager.initialize();
    log.info('Database initialized');

    // Initialize sync engine
    const cloudApiUrl = store.get('cloudApiUrl', 'https://api.auraaudit.ai');
    syncEngine = new SyncEngine(dbManager, cloudApiUrl);
    log.info('Sync engine initialized');

    // Initialize local processor
    localProcessor = new LocalProcessor(dbManager);
    log.info('Local processor initialized');

    // Start sync if user is authenticated
    const authToken = store.get('authToken');
    if (authToken) {
      await syncEngine.startSync(authToken);
      log.info('Sync started');
    }

  } catch (error) {
    log.error('Failed to initialize services:', error);
    dialog.showErrorBox(
      'Initialization Error',
      `Failed to initialize application services: ${error.message}`
    );
  }
}

/**
 * Check for application updates
 */
function checkForUpdates() {
  log.info('Checking for updates...');

  autoUpdater.on('update-available', (info) => {
    log.info('Update available:', info);
    mainWindow.webContents.send('update-available', info);
  });

  autoUpdater.on('update-not-available', (info) => {
    log.info('Update not available:', info);
  });

  autoUpdater.on('error', (err) => {
    log.error('Update error:', err);
  });

  autoUpdater.on('download-progress', (progressObj) => {
    log.info('Download progress:', progressObj.percent);
    mainWindow.webContents.send('download-progress', progressObj);
  });

  autoUpdater.on('update-downloaded', (info) => {
    log.info('Update downloaded:', info);
    mainWindow.webContents.send('update-downloaded', info);
  });

  autoUpdater.checkForUpdatesAndNotify();
}

/**
 * IPC Handlers - Database Operations
 */

// Query local database
ipcMain.handle('db:query', async (event, sql, params) => {
  try {
    return await dbManager.query(sql, params);
  } catch (error) {
    log.error('Database query error:', error);
    throw error;
  }
});

// Execute database command
ipcMain.handle('db:execute', async (event, sql, params) => {
  try {
    return await dbManager.execute(sql, params);
  } catch (error) {
    log.error('Database execute error:', error);
    throw error;
  }
});

// Get database stats
ipcMain.handle('db:stats', async () => {
  try {
    return await dbManager.getStats();
  } catch (error) {
    log.error('Database stats error:', error);
    throw error;
  }
});

/**
 * IPC Handlers - Sync Operations
 */

// Start sync
ipcMain.handle('sync:start', async (event, authToken) => {
  try {
    store.set('authToken', authToken);
    await syncEngine.startSync(authToken);
    return { success: true };
  } catch (error) {
    log.error('Sync start error:', error);
    throw error;
  }
});

// Stop sync
ipcMain.handle('sync:stop', async () => {
  try {
    await syncEngine.stopSync();
    return { success: true };
  } catch (error) {
    log.error('Sync stop error:', error);
    throw error;
  }
});

// Get sync status
ipcMain.handle('sync:status', async () => {
  try {
    return await syncEngine.getStatus();
  } catch (error) {
    log.error('Sync status error:', error);
    throw error;
  }
});

// Force sync now
ipcMain.handle('sync:force', async () => {
  try {
    await syncEngine.forceSync();
    return { success: true };
  } catch (error) {
    log.error('Force sync error:', error);
    throw error;
  }
});

/**
 * IPC Handlers - Local Processing
 */

// Process analytics locally
ipcMain.handle('process:analytics', async (event, engagementId) => {
  try {
    return await localProcessor.processAnalytics(engagementId);
  } catch (error) {
    log.error('Analytics processing error:', error);
    throw error;
  }
});

// Validate data locally
ipcMain.handle('process:validate', async (event, data, validationType) => {
  try {
    return await localProcessor.validateData(data, validationType);
  } catch (error) {
    log.error('Validation error:', error);
    throw error;
  }
});

// Calculate ratios locally
ipcMain.handle('process:ratios', async (event, financialData) => {
  try {
    return await localProcessor.calculateRatios(financialData);
  } catch (error) {
    log.error('Ratio calculation error:', error);
    throw error;
  }
});

/**
 * IPC Handlers - Settings & Configuration
 */

// Get setting
ipcMain.handle('settings:get', (event, key, defaultValue) => {
  return store.get(key, defaultValue);
});

// Set setting
ipcMain.handle('settings:set', (event, key, value) => {
  store.set(key, value);
  return { success: true };
});

// Get all settings
ipcMain.handle('settings:getAll', () => {
  return store.store;
});

// Reset settings
ipcMain.handle('settings:reset', () => {
  store.clear();
  return { success: true };
});

/**
 * IPC Handlers - Updates
 */

// Install update and restart
ipcMain.handle('update:install', () => {
  autoUpdater.quitAndInstall();
});

// Check for updates manually
ipcMain.handle('update:check', () => {
  checkForUpdates();
  return { success: true };
});

/**
 * IPC Handlers - System
 */

// Get app version
ipcMain.handle('system:version', () => {
  return app.getVersion();
});

// Get system info
ipcMain.handle('system:info', () => {
  return {
    version: app.getVersion(),
    platform: process.platform,
    arch: process.arch,
    electron: process.versions.electron,
    chrome: process.versions.chrome,
    node: process.versions.node,
    userDataPath: app.getPath('userData')
  };
});

// Open external link
ipcMain.handle('system:openExternal', (event, url) => {
  require('electron').shell.openExternal(url);
  return { success: true };
});

/**
 * App Lifecycle
 */

app.whenReady().then(async () => {
  await initializeServices();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', async (event) => {
  if (syncEngine && syncEngine.isRunning()) {
    event.preventDefault();
    log.info('Stopping sync before quit...');
    await syncEngine.stopSync();
    app.quit();
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  log.error('Uncaught exception:', error);
  dialog.showErrorBox('Application Error', error.message);
});

process.on('unhandledRejection', (error) => {
  log.error('Unhandled rejection:', error);
});
