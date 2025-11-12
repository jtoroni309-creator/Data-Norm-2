const { contextBridge, ipcRenderer } = require('electron');

/**
 * Preload script - Exposes secure IPC channels to renderer process
 * This provides a secure bridge between Electron and React
 */

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electron', {
  // Database API
  db: {
    query: (sql, params) => ipcRenderer.invoke('db:query', sql, params),
    execute: (sql, params) => ipcRenderer.invoke('db:execute', sql, params),
    getStats: () => ipcRenderer.invoke('db:stats')
  },

  // Sync API
  sync: {
    start: (authToken) => ipcRenderer.invoke('sync:start', authToken),
    stop: () => ipcRenderer.invoke('sync:stop'),
    getStatus: () => ipcRenderer.invoke('sync:status'),
    force: () => ipcRenderer.invoke('sync:force'),
    onStatusChange: (callback) => {
      ipcRenderer.on('sync:status-changed', (event, status) => callback(status));
      return () => ipcRenderer.removeListener('sync:status-changed', callback);
    }
  },

  // Local Processing API
  process: {
    analytics: (engagementId) => ipcRenderer.invoke('process:analytics', engagementId),
    validate: (data, validationType) => ipcRenderer.invoke('process:validate', data, validationType),
    ratios: (financialData) => ipcRenderer.invoke('process:ratios', financialData)
  },

  // Settings API
  settings: {
    get: (key, defaultValue) => ipcRenderer.invoke('settings:get', key, defaultValue),
    set: (key, value) => ipcRenderer.invoke('settings:set', key, value),
    getAll: () => ipcRenderer.invoke('settings:getAll'),
    reset: () => ipcRenderer.invoke('settings:reset')
  },

  // Updates API
  updates: {
    check: () => ipcRenderer.invoke('update:check'),
    install: () => ipcRenderer.invoke('update:install'),
    onAvailable: (callback) => {
      ipcRenderer.on('update-available', (event, info) => callback(info));
      return () => ipcRenderer.removeListener('update-available', callback);
    },
    onProgress: (callback) => {
      ipcRenderer.on('download-progress', (event, progress) => callback(progress));
      return () => ipcRenderer.removeListener('download-progress', callback);
    },
    onDownloaded: (callback) => {
      ipcRenderer.on('update-downloaded', (event, info) => callback(info));
      return () => ipcRenderer.removeListener('update-downloaded', callback);
    }
  },

  // System API
  system: {
    getVersion: () => ipcRenderer.invoke('system:version'),
    getInfo: () => ipcRenderer.invoke('system:info'),
    openExternal: (url) => ipcRenderer.invoke('system:openExternal', url)
  },

  // Platform detection
  platform: process.platform,
  isElectron: true
});
