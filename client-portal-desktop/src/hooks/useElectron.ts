import { useState, useEffect, useCallback } from 'react';
import type { SyncStatus, DatabaseStats, UpdateInfo, DownloadProgress } from '../electron';

/**
 * Check if running in Electron environment
 */
export function useIsElectron(): boolean {
  return typeof window !== 'undefined' && window.electron?.isElectron === true;
}

/**
 * Hook for database operations
 */
export function useDatabase() {
  const isElectron = useIsElectron();

  const query = useCallback(
    async (sql: string, params?: any[]) => {
      if (!isElectron) throw new Error('Not running in Electron');
      return window.electron.db.query(sql, params);
    },
    [isElectron]
  );

  const execute = useCallback(
    async (sql: string, params?: any[]) => {
      if (!isElectron) throw new Error('Not running in Electron');
      return window.electron.db.execute(sql, params);
    },
    [isElectron]
  );

  const getStats = useCallback(async () => {
    if (!isElectron) throw new Error('Not running in Electron');
    return window.electron.db.getStats();
  }, [isElectron]);

  return { query, execute, getStats, isAvailable: isElectron };
}

/**
 * Hook for sync operations and status
 */
export function useSync() {
  const isElectron = useIsElectron();
  const [status, setStatus] = useState<SyncStatus | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isElectron) return;

    // Get initial status
    window.electron.sync.getStatus().then(setStatus);

    // Listen for status changes
    const unsubscribe = window.electron.sync.onStatusChange((newStatus) => {
      setStatus(newStatus);
    });

    return unsubscribe;
  }, [isElectron]);

  const start = useCallback(
    async (authToken: string) => {
      if (!isElectron) throw new Error('Not running in Electron');
      setLoading(true);
      try {
        await window.electron.sync.start(authToken);
        const newStatus = await window.electron.sync.getStatus();
        setStatus(newStatus);
      } finally {
        setLoading(false);
      }
    },
    [isElectron]
  );

  const stop = useCallback(async () => {
    if (!isElectron) throw new Error('Not running in Electron');
    setLoading(true);
    try {
      await window.electron.sync.stop();
      const newStatus = await window.electron.sync.getStatus();
      setStatus(newStatus);
    } finally {
      setLoading(false);
    }
  }, [isElectron]);

  const force = useCallback(async () => {
    if (!isElectron) throw new Error('Not running in Electron');
    setLoading(true);
    try {
      await window.electron.sync.force();
    } finally {
      setLoading(false);
    }
  }, [isElectron]);

  return {
    status,
    loading,
    start,
    stop,
    force,
    isAvailable: isElectron,
  };
}

/**
 * Hook for local processing operations
 */
export function useLocalProcessor() {
  const isElectron = useIsElectron();

  const processAnalytics = useCallback(
    async (engagementId: string) => {
      if (!isElectron) throw new Error('Not running in Electron');
      return window.electron.process.analytics(engagementId);
    },
    [isElectron]
  );

  const validate = useCallback(
    async (data: any, validationType: string) => {
      if (!isElectron) throw new Error('Not running in Electron');
      return window.electron.process.validate(data, validationType);
    },
    [isElectron]
  );

  const calculateRatios = useCallback(
    async (financialData: any) => {
      if (!isElectron) throw new Error('Not running in Electron');
      return window.electron.process.ratios(financialData);
    },
    [isElectron]
  );

  return {
    processAnalytics,
    validate,
    calculateRatios,
    isAvailable: isElectron,
  };
}

/**
 * Hook for application settings
 */
export function useSettings<T = any>(key: string, defaultValue?: T) {
  const isElectron = useIsElectron();
  const [value, setValue] = useState<T | undefined>(defaultValue);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isElectron) {
      setLoading(false);
      return;
    }

    window.electron.settings.get(key, defaultValue).then((val) => {
      setValue(val);
      setLoading(false);
    });
  }, [isElectron, key, defaultValue]);

  const updateValue = useCallback(
    async (newValue: T) => {
      if (!isElectron) throw new Error('Not running in Electron');
      await window.electron.settings.set(key, newValue);
      setValue(newValue);
    },
    [isElectron, key]
  );

  return {
    value,
    setValue: updateValue,
    loading,
    isAvailable: isElectron,
  };
}

/**
 * Hook for application updates
 */
export function useUpdates() {
  const isElectron = useIsElectron();
  const [updateAvailable, setUpdateAvailable] = useState<UpdateInfo | null>(null);
  const [downloadProgress, setDownloadProgress] = useState<DownloadProgress | null>(null);
  const [updateDownloaded, setUpdateDownloaded] = useState<UpdateInfo | null>(null);

  useEffect(() => {
    if (!isElectron) return;

    const unsubscribeAvailable = window.electron.updates.onAvailable((info) => {
      setUpdateAvailable(info);
    });

    const unsubscribeProgress = window.electron.updates.onProgress((progress) => {
      setDownloadProgress(progress);
    });

    const unsubscribeDownloaded = window.electron.updates.onDownloaded((info) => {
      setUpdateDownloaded(info);
      setDownloadProgress(null);
    });

    return () => {
      unsubscribeAvailable();
      unsubscribeProgress();
      unsubscribeDownloaded();
    };
  }, [isElectron]);

  const checkForUpdates = useCallback(async () => {
    if (!isElectron) throw new Error('Not running in Electron');
    await window.electron.updates.check();
  }, [isElectron]);

  const installUpdate = useCallback(async () => {
    if (!isElectron) throw new Error('Not running in Electron');
    await window.electron.updates.install();
  }, [isElectron]);

  return {
    updateAvailable,
    downloadProgress,
    updateDownloaded,
    checkForUpdates,
    installUpdate,
    isAvailable: isElectron,
  };
}

/**
 * Hook for system information
 */
export function useSystemInfo() {
  const isElectron = useIsElectron();
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [version, setVersion] = useState<string | null>(null);

  useEffect(() => {
    if (!isElectron) return;

    window.electron.system.getInfo().then(setSystemInfo);
    window.electron.system.getVersion().then(setVersion);
  }, [isElectron]);

  const openExternal = useCallback(
    async (url: string) => {
      if (!isElectron) {
        window.open(url, '_blank');
        return;
      }
      await window.electron.system.openExternal(url);
    },
    [isElectron]
  );

  return {
    systemInfo,
    version,
    platform: isElectron ? window.electron.platform : null,
    openExternal,
    isAvailable: isElectron,
  };
}

/**
 * Hook for database statistics
 */
export function useDatabaseStats() {
  const isElectron = useIsElectron();
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!isElectron) return;
    setLoading(true);
    try {
      const newStats = await window.electron.db.getStats();
      setStats(newStats);
    } finally {
      setLoading(false);
    }
  }, [isElectron]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    stats,
    loading,
    refresh,
    isAvailable: isElectron,
  };
}
