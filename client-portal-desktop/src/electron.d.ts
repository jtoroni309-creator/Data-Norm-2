/**
 * TypeScript definitions for Electron IPC API
 * This defines the window.electron interface exposed by preload.js
 */

export interface ElectronAPI {
  // Database API
  db: {
    query: (sql: string, params?: any[]) => Promise<any[]>;
    execute: (sql: string, params?: any[]) => Promise<{ changes: number; lastInsertRowid: number }>;
    getStats: () => Promise<DatabaseStats>;
  };

  // Sync API
  sync: {
    start: (authToken: string) => Promise<{ success: boolean }>;
    stop: () => Promise<{ success: boolean }>;
    getStatus: () => Promise<SyncStatus>;
    force: () => Promise<{ success: boolean }>;
    onStatusChange: (callback: (status: SyncStatus) => void) => () => void;
  };

  // Local Processing API
  process: {
    analytics: (engagementId: string) => Promise<AnalyticsResult>;
    validate: (data: any, validationType: string) => Promise<ValidationResult>;
    ratios: (financialData: any) => Promise<FinancialRatios>;
  };

  // Settings API
  settings: {
    get: <T = any>(key: string, defaultValue?: T) => Promise<T>;
    set: (key: string, value: any) => Promise<{ success: boolean }>;
    getAll: () => Promise<Record<string, any>>;
    reset: () => Promise<{ success: boolean }>;
  };

  // Updates API
  updates: {
    check: () => Promise<{ success: boolean }>;
    install: () => Promise<void>;
    onAvailable: (callback: (info: UpdateInfo) => void) => () => void;
    onProgress: (callback: (progress: DownloadProgress) => void) => () => void;
    onDownloaded: (callback: (info: UpdateInfo) => void) => () => void;
  };

  // System API
  system: {
    getVersion: () => Promise<string>;
    getInfo: () => Promise<SystemInfo>;
    openExternal: (url: string) => Promise<{ success: boolean }>;
  };

  // Platform detection
  platform: NodeJS.Platform;
  isElectron: boolean;
}

// Type definitions
export interface DatabaseStats {
  organizations: number;
  users: number;
  engagements: number;
  trial_balances: number;
  account_mappings: number;
  analytics_results: number;
  documents: number;
  sync_queue: number;
  pendingSync: number;
  sizeBytes: number;
  sizeMB: string;
}

export interface SyncStatus {
  isRunning: boolean;
  lastSync: number | null;
  status: 'active' | 'synced' | 'error' | 'stopped';
  recordsSynced?: number;
  errors?: number;
  error?: string;
  pendingItems?: number;
  stats?: DatabaseStats;
}

export interface AnalyticsResult {
  engagementId: string;
  processedAt: number;
  analytics: {
    ratios: FinancialRatios;
    anomalies: Anomaly[];
    jeTests: JETests;
    materiality: Materiality;
  };
}

export interface FinancialRatios {
  currentRatio: string | null;
  quickRatio: string | null;
  profitMargin: string | null;
  returnOnAssets: string | null;
  returnOnEquity: string | null;
  debtToEquity: string | null;
  debtToAssets: string | null;
  assetTurnover: string | null;
}

export interface Anomaly {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  account?: string;
  balance?: number;
  message: string;
  [key: string]: any;
}

export interface JETests {
  roundDollarTesting: JournalEntry[];
  largeAdjustments: JournalEntry[];
  unusualTiming: JournalEntry[];
}

export interface JournalEntry {
  entryId: string;
  amount: number;
  date: string;
  description: string;
  [key: string]: any;
}

export interface Materiality {
  overall: number;
  performanceMateriality: number;
  specificMateriality: {
    relatedParty: number;
    executiveComp: number;
    contingencies: number;
  };
  clearlyTrivial: number;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface UpdateInfo {
  version: string;
  releaseDate: string;
  releaseNotes?: string;
}

export interface DownloadProgress {
  percent: number;
  bytesPerSecond: number;
  transferred: number;
  total: number;
}

export interface SystemInfo {
  version: string;
  platform: string;
  arch: string;
  electron: string;
  chrome: string;
  node: string;
  userDataPath: string;
}

declare global {
  interface Window {
    electron: ElectronAPI;
  }
}

export {};
