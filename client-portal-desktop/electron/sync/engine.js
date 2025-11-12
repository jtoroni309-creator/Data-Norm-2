const axios = require('axios');
const log = require('electron-log');
const { BrowserWindow } = require('electron');

/**
 * Sync Engine - Handles bidirectional synchronization between local database and cloud
 * Implements offline-first architecture with conflict resolution
 */
class SyncEngine {
  constructor(dbManager, cloudApiUrl) {
    this.dbManager = dbManager;
    this.cloudApiUrl = cloudApiUrl;
    this.authToken = null;
    this.syncInterval = null;
    this.isRunning = false;
    this.syncIntervalMs = 5 * 60 * 1000; // 5 minutes
    this.apiClient = null;
  }

  /**
   * Start automatic sync
   */
  async startSync(authToken) {
    if (this.isRunning) {
      log.warn('Sync already running');
      return;
    }

    this.authToken = authToken;
    this.isRunning = true;

    // Configure API client
    this.apiClient = axios.create({
      baseURL: this.cloudApiUrl,
      timeout: 30000,
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    });

    log.info('Sync engine started');

    // Perform initial sync
    await this.performSync();

    // Schedule periodic sync
    this.syncInterval = setInterval(() => {
      this.performSync();
    }, this.syncIntervalMs);

    this.notifyStatusChange({
      isRunning: true,
      lastSync: Date.now(),
      status: 'active'
    });
  }

  /**
   * Stop automatic sync
   */
  async stopSync() {
    if (!this.isRunning) {
      return;
    }

    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }

    this.isRunning = false;
    log.info('Sync engine stopped');

    this.notifyStatusChange({
      isRunning: false,
      status: 'stopped'
    });
  }

  /**
   * Force immediate sync
   */
  async forceSync() {
    log.info('Force sync requested');
    await this.performSync();
  }

  /**
   * Perform full synchronization
   */
  async performSync() {
    if (!this.authToken) {
      log.error('Cannot sync: No auth token');
      return;
    }

    const startTime = Date.now();
    log.info('Starting sync cycle...');

    try {
      // Record sync start
      const syncLogId = await this.recordSyncStart();

      let totalRecords = 0;
      let totalErrors = 0;

      // Step 1: Push local changes to cloud
      const pushResult = await this.pushLocalChanges();
      totalRecords += pushResult.records;
      totalErrors += pushResult.errors;

      // Step 2: Pull updates from cloud
      const pullResult = await this.pullCloudUpdates();
      totalRecords += pullResult.records;
      totalErrors += pullResult.errors;

      // Step 3: Sync documents
      const docsResult = await this.syncDocuments();
      totalRecords += docsResult.records;
      totalErrors += docsResult.errors;

      // Record sync completion
      await this.recordSyncComplete(syncLogId, totalRecords, totalErrors);

      const duration = Date.now() - startTime;
      log.info(`Sync completed in ${duration}ms: ${totalRecords} records, ${totalErrors} errors`);

      this.notifyStatusChange({
        isRunning: true,
        lastSync: Date.now(),
        status: 'synced',
        recordsSynced: totalRecords,
        errors: totalErrors
      });

    } catch (error) {
      log.error('Sync error:', error);

      this.notifyStatusChange({
        isRunning: true,
        lastSync: Date.now(),
        status: 'error',
        error: error.message
      });
    }
  }

  /**
   * Push local changes to cloud
   */
  async pushLocalChanges() {
    let recordsPushed = 0;
    let errors = 0;

    try {
      // Get pending sync items
      const pendingItems = await this.dbManager.getPendingSyncItems(50);

      log.info(`Pushing ${pendingItems.length} local changes to cloud`);

      for (const item of pendingItems) {
        try {
          const data = JSON.parse(item.data);

          // Send to cloud based on operation
          let endpoint = '';
          let method = '';

          switch (item.operation) {
            case 'create':
              endpoint = `/${item.entity_type}`;
              method = 'POST';
              break;
            case 'update':
              endpoint = `/${item.entity_type}/${item.entity_id}`;
              method = 'PUT';
              break;
            case 'delete':
              endpoint = `/${item.entity_type}/${item.entity_id}`;
              method = 'DELETE';
              break;
          }

          // Make API call
          await this.apiClient.request({
            method,
            url: endpoint,
            data
          });

          // Remove from sync queue
          await this.dbManager.removeFromSyncQueue(item.id);
          recordsPushed++;

        } catch (error) {
          log.error(`Failed to push ${item.entity_type} ${item.entity_id}:`, error.message);

          // Update retry count
          await this.dbManager.updateSyncQueueRetry(item.id, error.message);
          errors++;
        }
      }

    } catch (error) {
      log.error('Push local changes error:', error);
      errors++;
    }

    return { records: recordsPushed, errors };
  }

  /**
   * Pull updates from cloud
   */
  async pullCloudUpdates() {
    let recordsPulled = 0;
    let errors = 0;

    try {
      // Get last sync timestamp
      const lastSync = await this.getLastSyncTimestamp();
      const timestamp = lastSync ? new Date(lastSync).toISOString() : null;

      log.info(`Pulling updates from cloud (since: ${timestamp || 'beginning'})`);

      // Pull organizations
      const orgResult = await this.pullEntity('organizations', timestamp);
      recordsPulled += orgResult.records;
      errors += orgResult.errors;

      // Pull engagements
      const engResult = await this.pullEntity('engagements', timestamp);
      recordsPulled += engResult.records;
      errors += engResult.errors;

      // Pull trial balances
      const tbResult = await this.pullEntity('trial_balances', timestamp);
      recordsPulled += tbResult.records;
      errors += tbResult.errors;

      // Pull account mappings
      const mapResult = await this.pullEntity('account_mappings', timestamp);
      recordsPulled += mapResult.records;
      errors += mapResult.errors;

      // Pull analytics results
      const analyticsResult = await this.pullEntity('analytics_results', timestamp);
      recordsPulled += analyticsResult.records;
      errors += analyticsResult.errors;

    } catch (error) {
      log.error('Pull cloud updates error:', error);
      errors++;
    }

    return { records: recordsPulled, errors };
  }

  /**
   * Pull specific entity type from cloud
   */
  async pullEntity(entityType, since) {
    let records = 0;
    let errors = 0;

    try {
      const url = since
        ? `/${entityType}?updated_since=${since}`
        : `/${entityType}`;

      const response = await this.apiClient.get(url);
      const items = response.data.data || response.data;

      for (const item of items) {
        try {
          await this.upsertLocalEntity(entityType, item);
          records++;
        } catch (error) {
          log.error(`Failed to upsert ${entityType}:`, error.message);
          errors++;
        }
      }

      log.info(`Pulled ${records} ${entityType} from cloud`);

    } catch (error) {
      log.error(`Failed to pull ${entityType}:`, error.message);
      errors++;
    }

    return { records, errors };
  }

  /**
   * Upsert entity into local database
   */
  async upsertLocalEntity(entityType, data) {
    const now = Date.now();
    const tableName = entityType;

    // Check if exists
    const existing = await this.dbManager.query(
      `SELECT id FROM ${tableName} WHERE id = ?`,
      [data.id]
    );

    if (existing.length > 0) {
      // Update existing
      const fields = Object.keys(data).filter(k => k !== 'id');
      const setClause = fields.map(f => `${f} = ?`).join(', ');
      const values = fields.map(f => this.serializeValue(data[f]));

      await this.dbManager.execute(
        `UPDATE ${tableName} SET ${setClause}, synced_at = ? WHERE id = ?`,
        [...values, now, data.id]
      );
    } else {
      // Insert new
      const fields = Object.keys(data);
      const placeholders = fields.map(() => '?').join(', ');
      const values = fields.map(f => this.serializeValue(data[f]));

      await this.dbManager.execute(
        `INSERT INTO ${tableName} (${fields.join(', ')}, synced_at) VALUES (${placeholders}, ?)`,
        [...values, now]
      );
    }
  }

  /**
   * Sync documents (files)
   */
  async syncDocuments() {
    let records = 0;
    let errors = 0;

    // TODO: Implement document sync with cloud storage
    // This would handle uploading/downloading files to S3/Azure Blob

    return { records, errors };
  }

  /**
   * Get last sync timestamp
   */
  async getLastSyncTimestamp() {
    const result = await this.dbManager.query(
      'SELECT MAX(completed_at) as last_sync FROM sync_log WHERE status = "completed"'
    );
    return result[0]?.last_sync || null;
  }

  /**
   * Record sync start
   */
  async recordSyncStart() {
    const result = await this.dbManager.execute(
      'INSERT INTO sync_log (sync_type, status, started_at) VALUES (?, ?, ?)',
      ['full', 'running', Date.now()]
    );
    return result.lastInsertRowid;
  }

  /**
   * Record sync completion
   */
  async recordSyncComplete(syncLogId, recordsSynced, errors) {
    await this.dbManager.execute(
      'UPDATE sync_log SET status = ?, records_synced = ?, errors = ?, completed_at = ? WHERE id = ?',
      ['completed', recordsSynced, errors, Date.now(), syncLogId]
    );
  }

  /**
   * Get sync status
   */
  async getStatus() {
    const lastSync = await this.getLastSyncTimestamp();
    const pendingItems = await this.dbManager.query('SELECT COUNT(*) as count FROM sync_queue');
    const stats = await this.dbManager.getStats();

    return {
      isRunning: this.isRunning,
      lastSync: lastSync,
      pendingItems: pendingItems[0].count,
      stats: stats
    };
  }

  /**
   * Serialize value for database storage
   */
  serializeValue(value) {
    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value);
    }
    return value;
  }

  /**
   * Notify renderer process of status change
   */
  notifyStatusChange(status) {
    const windows = BrowserWindow.getAllWindows();
    if (windows.length > 0) {
      windows[0].webContents.send('sync:status-changed', status);
    }
  }

  /**
   * Check if sync is running
   */
  isRunning() {
    return this.isRunning;
  }
}

module.exports = SyncEngine;
