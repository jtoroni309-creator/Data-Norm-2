const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');
const log = require('electron-log');

/**
 * Local SQLite database manager for offline data storage
 * Provides CRUD operations and schema management
 */
class DatabaseManager {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.db = null;
  }

  /**
   * Initialize database and create schema
   */
  async initialize() {
    try {
      // Ensure directory exists
      const dir = path.dirname(this.dbPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      // Open database
      this.db = new Database(this.dbPath);
      this.db.pragma('journal_mode = WAL');
      this.db.pragma('foreign_keys = ON');

      log.info(`Database opened: ${this.dbPath}`);

      // Create schema
      await this.createSchema();

      return true;
    } catch (error) {
      log.error('Database initialization error:', error);
      throw error;
    }
  }

  /**
   * Create database schema
   */
  async createSchema() {
    const schema = `
      -- Organizations
      CREATE TABLE IF NOT EXISTS organizations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        settings TEXT,
        synced_at INTEGER,
        updated_at INTEGER NOT NULL,
        created_at INTEGER NOT NULL
      );

      -- Users
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        organization_id TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        settings TEXT,
        synced_at INTEGER,
        updated_at INTEGER NOT NULL,
        created_at INTEGER NOT NULL,
        FOREIGN KEY (organization_id) REFERENCES organizations(id)
      );

      -- Engagements
      CREATE TABLE IF NOT EXISTS engagements (
        id TEXT PRIMARY KEY,
        organization_id TEXT NOT NULL,
        client_name TEXT NOT NULL,
        year_end TEXT NOT NULL,
        engagement_type TEXT NOT NULL,
        status TEXT NOT NULL,
        metadata TEXT,
        synced_at INTEGER,
        updated_at INTEGER NOT NULL,
        created_at INTEGER NOT NULL,
        FOREIGN KEY (organization_id) REFERENCES organizations(id)
      );

      -- Trial Balances
      CREATE TABLE IF NOT EXISTS trial_balances (
        id TEXT PRIMARY KEY,
        engagement_id TEXT NOT NULL,
        file_name TEXT NOT NULL,
        data TEXT NOT NULL,
        normalized INTEGER DEFAULT 0,
        synced_at INTEGER,
        uploaded_at INTEGER NOT NULL,
        FOREIGN KEY (engagement_id) REFERENCES engagements(id)
      );

      -- Account Mappings
      CREATE TABLE IF NOT EXISTS account_mappings (
        id TEXT PRIMARY KEY,
        engagement_id TEXT NOT NULL,
        source_account TEXT NOT NULL,
        target_account TEXT NOT NULL,
        confidence REAL,
        verified INTEGER DEFAULT 0,
        synced_at INTEGER,
        created_at INTEGER NOT NULL,
        FOREIGN KEY (engagement_id) REFERENCES engagements(id)
      );

      -- Analytics Results
      CREATE TABLE IF NOT EXISTS analytics_results (
        id TEXT PRIMARY KEY,
        engagement_id TEXT NOT NULL,
        analytics_type TEXT NOT NULL,
        results TEXT NOT NULL,
        processed_at INTEGER NOT NULL,
        synced_at INTEGER,
        FOREIGN KEY (engagement_id) REFERENCES engagements(id)
      );

      -- Documents
      CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        engagement_id TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        mime_type TEXT NOT NULL,
        synced_at INTEGER,
        uploaded_at INTEGER NOT NULL,
        FOREIGN KEY (engagement_id) REFERENCES engagements(id)
      );

      -- Sync Queue
      CREATE TABLE IF NOT EXISTS sync_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        operation TEXT NOT NULL,
        data TEXT NOT NULL,
        retry_count INTEGER DEFAULT 0,
        last_error TEXT,
        created_at INTEGER NOT NULL
      );

      -- Sync Log
      CREATE TABLE IF NOT EXISTS sync_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sync_type TEXT NOT NULL,
        status TEXT NOT NULL,
        records_synced INTEGER DEFAULT 0,
        errors INTEGER DEFAULT 0,
        started_at INTEGER NOT NULL,
        completed_at INTEGER
      );

      -- Create indexes
      CREATE INDEX IF NOT EXISTS idx_engagements_org ON engagements(organization_id);
      CREATE INDEX IF NOT EXISTS idx_trial_balances_engagement ON trial_balances(engagement_id);
      CREATE INDEX IF NOT EXISTS idx_account_mappings_engagement ON account_mappings(engagement_id);
      CREATE INDEX IF NOT EXISTS idx_analytics_engagement ON analytics_results(engagement_id);
      CREATE INDEX IF NOT EXISTS idx_documents_engagement ON documents(engagement_id);
      CREATE INDEX IF NOT EXISTS idx_sync_queue_entity ON sync_queue(entity_type, entity_id);
      CREATE INDEX IF NOT EXISTS idx_sync_log_started ON sync_log(started_at);
    `;

    const statements = schema.split(';').filter(s => s.trim());
    for (const statement of statements) {
      if (statement.trim()) {
        this.db.exec(statement);
      }
    }

    log.info('Database schema created');
  }

  /**
   * Execute a query and return results
   */
  async query(sql, params = []) {
    try {
      const stmt = this.db.prepare(sql);
      return stmt.all(params);
    } catch (error) {
      log.error('Query error:', error, { sql, params });
      throw error;
    }
  }

  /**
   * Execute a command (INSERT, UPDATE, DELETE)
   */
  async execute(sql, params = []) {
    try {
      const stmt = this.db.prepare(sql);
      return stmt.run(params);
    } catch (error) {
      log.error('Execute error:', error, { sql, params });
      throw error;
    }
  }

  /**
   * Execute multiple statements in a transaction
   */
  async transaction(callback) {
    const transaction = this.db.transaction(callback);
    try {
      return transaction();
    } catch (error) {
      log.error('Transaction error:', error);
      throw error;
    }
  }

  /**
   * Get database statistics
   */
  async getStats() {
    const tables = [
      'organizations',
      'users',
      'engagements',
      'trial_balances',
      'account_mappings',
      'analytics_results',
      'documents',
      'sync_queue'
    ];

    const stats = {};
    for (const table of tables) {
      const result = this.db.prepare(`SELECT COUNT(*) as count FROM ${table}`).get();
      stats[table] = result.count;
    }

    // Get pending sync items
    const pendingSync = this.db.prepare('SELECT COUNT(*) as count FROM sync_queue').get();
    stats.pendingSync = pendingSync.count;

    // Get database size
    const dbStats = fs.statSync(this.dbPath);
    stats.sizeBytes = dbStats.size;
    stats.sizeMB = (dbStats.size / (1024 * 1024)).toFixed(2);

    return stats;
  }

  /**
   * Add item to sync queue
   */
  async addToSyncQueue(entityType, entityId, operation, data) {
    const sql = `
      INSERT INTO sync_queue (entity_type, entity_id, operation, data, created_at)
      VALUES (?, ?, ?, ?, ?)
    `;
    const now = Date.now();
    return this.execute(sql, [entityType, entityId, operation, JSON.stringify(data), now]);
  }

  /**
   * Get pending sync items
   */
  async getPendingSyncItems(limit = 100) {
    const sql = `
      SELECT * FROM sync_queue
      WHERE retry_count < 3
      ORDER BY created_at ASC
      LIMIT ?
    `;
    return this.query(sql, [limit]);
  }

  /**
   * Remove item from sync queue
   */
  async removeFromSyncQueue(id) {
    return this.execute('DELETE FROM sync_queue WHERE id = ?', [id]);
  }

  /**
   * Update sync queue item retry count
   */
  async updateSyncQueueRetry(id, error) {
    const sql = `
      UPDATE sync_queue
      SET retry_count = retry_count + 1, last_error = ?
      WHERE id = ?
    `;
    return this.execute(sql, [error, id]);
  }

  /**
   * Close database connection
   */
  close() {
    if (this.db) {
      this.db.close();
      log.info('Database closed');
    }
  }
}

module.exports = DatabaseManager;
