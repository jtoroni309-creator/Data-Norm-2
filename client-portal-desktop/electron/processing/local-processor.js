const log = require('electron-log');

/**
 * Local Processor - Handles business logic processing on the client side
 * This enables offline functionality and reduces server load
 */
class LocalProcessor {
  constructor(dbManager) {
    this.dbManager = dbManager;
  }

  /**
   * Process analytics locally
   * Performs financial analysis calculations without needing cloud connectivity
   */
  async processAnalytics(engagementId) {
    try {
      log.info(`Processing analytics for engagement ${engagementId}`);

      // Get trial balance data
      const trialBalances = await this.dbManager.query(
        'SELECT * FROM trial_balances WHERE engagement_id = ?',
        [engagementId]
      );

      if (trialBalances.length === 0) {
        throw new Error('No trial balance data found');
      }

      const tbData = JSON.parse(trialBalances[0].data);
      const results = {
        engagementId,
        processedAt: Date.now(),
        analytics: {}
      };

      // 1. Calculate financial ratios
      results.analytics.ratios = await this.calculateRatios(tbData);

      // 2. Detect anomalies
      results.analytics.anomalies = await this.detectAnomalies(tbData);

      // 3. Perform basic JE testing
      results.analytics.jeTests = await this.performJETests(tbData);

      // 4. Calculate materiality
      results.analytics.materiality = await this.calculateMateriality(tbData);

      // Save results to local database
      const resultId = `analytics_${Date.now()}_${engagementId}`;
      await this.dbManager.execute(
        'INSERT INTO analytics_results (id, engagement_id, analytics_type, results, processed_at) VALUES (?, ?, ?, ?, ?)',
        [resultId, engagementId, 'full', JSON.stringify(results), Date.now()]
      );

      // Add to sync queue
      await this.dbManager.addToSyncQueue('analytics_results', resultId, 'create', results);

      log.info(`Analytics processed successfully for ${engagementId}`);
      return results;

    } catch (error) {
      log.error('Analytics processing error:', error);
      throw error;
    }
  }

  /**
   * Calculate financial ratios
   */
  async calculateRatios(financialData) {
    const ratios = {};

    try {
      // Extract key financial statement items
      const assets = this.sumAccountsByType(financialData, 'asset');
      const liabilities = this.sumAccountsByType(financialData, 'liability');
      const equity = this.sumAccountsByType(financialData, 'equity');
      const revenue = this.sumAccountsByType(financialData, 'revenue');
      const expenses = this.sumAccountsByType(financialData, 'expense');

      const currentAssets = this.sumAccountsByCategory(financialData, 'current_asset');
      const currentLiabilities = this.sumAccountsByCategory(financialData, 'current_liability');
      const inventory = this.sumAccountsByCategory(financialData, 'inventory');
      const receivables = this.sumAccountsByCategory(financialData, 'receivables');

      const netIncome = revenue - expenses;

      // Liquidity Ratios
      ratios.currentRatio = currentLiabilities !== 0
        ? (currentAssets / currentLiabilities).toFixed(2)
        : null;

      ratios.quickRatio = currentLiabilities !== 0
        ? ((currentAssets - inventory) / currentLiabilities).toFixed(2)
        : null;

      // Profitability Ratios
      ratios.profitMargin = revenue !== 0
        ? ((netIncome / revenue) * 100).toFixed(2)
        : null;

      ratios.returnOnAssets = assets !== 0
        ? ((netIncome / assets) * 100).toFixed(2)
        : null;

      ratios.returnOnEquity = equity !== 0
        ? ((netIncome / equity) * 100).toFixed(2)
        : null;

      // Leverage Ratios
      ratios.debtToEquity = equity !== 0
        ? (liabilities / equity).toFixed(2)
        : null;

      ratios.debtToAssets = assets !== 0
        ? ((liabilities / assets) * 100).toFixed(2)
        : null;

      // Activity Ratios
      ratios.assetTurnover = assets !== 0
        ? (revenue / assets).toFixed(2)
        : null;

      log.info('Financial ratios calculated:', ratios);
      return ratios;

    } catch (error) {
      log.error('Ratio calculation error:', error);
      return ratios;
    }
  }

  /**
   * Detect anomalies in financial data
   */
  async detectAnomalies(financialData) {
    const anomalies = [];

    try {
      // 1. Check for unusual account balances
      for (const account of financialData.accounts || []) {
        // Negative balance in asset accounts
        if (account.type === 'asset' && account.balance < 0) {
          anomalies.push({
            type: 'negative_asset',
            severity: 'high',
            account: account.name,
            balance: account.balance,
            message: `Asset account has negative balance: ${account.name}`
          });
        }

        // Positive balance in liability/equity accounts (credit accounts)
        if (['liability', 'equity'].includes(account.type) && account.balance > 0) {
          anomalies.push({
            type: 'positive_liability',
            severity: 'medium',
            account: account.name,
            balance: account.balance,
            message: `Liability/Equity account has positive balance: ${account.name}`
          });
        }

        // Extremely large balances (outliers)
        const avgBalance = this.calculateAverageBalance(financialData);
        if (Math.abs(account.balance) > avgBalance * 10) {
          anomalies.push({
            type: 'outlier_balance',
            severity: 'medium',
            account: account.name,
            balance: account.balance,
            average: avgBalance,
            message: `Account balance is significantly higher than average`
          });
        }
      }

      // 2. Check trial balance
      const debits = this.sumDebits(financialData);
      const credits = this.sumCredits(financialData);
      const difference = Math.abs(debits - credits);

      if (difference > 0.01) {
        anomalies.push({
          type: 'trial_balance_imbalance',
          severity: 'critical',
          debits,
          credits,
          difference,
          message: `Trial balance does not balance: difference of ${difference}`
        });
      }

      log.info(`Detected ${anomalies.length} anomalies`);
      return anomalies;

    } catch (error) {
      log.error('Anomaly detection error:', error);
      return anomalies;
    }
  }

  /**
   * Perform basic journal entry testing
   */
  async performJETests(financialData) {
    const tests = {
      roundDollarTesting: [],
      largeAdjustments: [],
      unusualTiming: []
    };

    try {
      const entries = financialData.journal_entries || [];

      for (const entry of entries) {
        // Round dollar testing
        if (Math.abs(entry.amount % 100) === 0 && Math.abs(entry.amount) >= 1000) {
          tests.roundDollarTesting.push({
            entryId: entry.id,
            amount: entry.amount,
            date: entry.date,
            description: entry.description
          });
        }

        // Large adjustments (> 5% of materiality)
        const materiality = this.calculateMaterialityThreshold(financialData);
        if (Math.abs(entry.amount) > materiality * 0.05) {
          tests.largeAdjustments.push({
            entryId: entry.id,
            amount: entry.amount,
            date: entry.date,
            description: entry.description,
            percentOfMateriality: ((Math.abs(entry.amount) / materiality) * 100).toFixed(2)
          });
        }

        // Unusual timing (entries near year-end)
        const entryDate = new Date(entry.date);
        const yearEnd = new Date(financialData.year_end);
        const daysDiff = Math.abs((yearEnd - entryDate) / (1000 * 60 * 60 * 24));

        if (daysDiff <= 5 && Math.abs(entry.amount) > materiality * 0.01) {
          tests.unusualTiming.push({
            entryId: entry.id,
            amount: entry.amount,
            date: entry.date,
            daysBefore YearEnd: daysDiff,
            description: entry.description
          });
        }
      }

      log.info('JE testing completed');
      return tests;

    } catch (error) {
      log.error('JE testing error:', error);
      return tests;
    }
  }

  /**
   * Calculate materiality thresholds
   */
  async calculateMateriality(financialData) {
    try {
      const assets = this.sumAccountsByType(financialData, 'asset');
      const revenue = this.sumAccountsByType(financialData, 'revenue');
      const expenses = this.sumAccountsByType(financialData, 'expense');
      const netIncome = revenue - expenses;

      // Multiple benchmarks for materiality
      const materiality = {
        overall: Math.max(
          assets * 0.01,           // 1% of assets
          revenue * 0.005,         // 0.5% of revenue
          Math.abs(netIncome) * 0.05  // 5% of net income
        ),
        performanceMateriality: 0,
        specificMateriality: {},
        clearlyTrivial: 0
      };

      // Performance materiality (70% of overall)
      materiality.performanceMateriality = materiality.overall * 0.70;

      // Clearly trivial threshold (5% of overall)
      materiality.clearlyTrivial = materiality.overall * 0.05;

      // Specific materiality for sensitive accounts
      materiality.specificMateriality = {
        relatedParty: materiality.overall * 0.30,
        executiveComp: materiality.overall * 0.20,
        contingencies: materiality.overall * 0.40
      };

      log.info('Materiality calculated:', materiality);
      return materiality;

    } catch (error) {
      log.error('Materiality calculation error:', error);
      throw error;
    }
  }

  /**
   * Validate data against rules
   */
  async validateData(data, validationType) {
    const errors = [];
    const warnings = [];

    try {
      switch (validationType) {
        case 'trial_balance':
          // Check required fields
          if (!data.accounts || !Array.isArray(data.accounts)) {
            errors.push('Trial balance must contain accounts array');
          }

          // Validate each account
          for (const account of data.accounts || []) {
            if (!account.name) {
              errors.push(`Account missing name: ${JSON.stringify(account)}`);
            }
            if (typeof account.balance !== 'number') {
              errors.push(`Account ${account.name} has invalid balance`);
            }
            if (!account.type) {
              warnings.push(`Account ${account.name} missing type`);
            }
          }

          // Check balance
          const debits = this.sumDebits(data);
          const credits = this.sumCredits(data);
          if (Math.abs(debits - credits) > 0.01) {
            errors.push(`Trial balance does not balance: ${debits} vs ${credits}`);
          }
          break;

        case 'engagement':
          if (!data.client_name) errors.push('Client name required');
          if (!data.year_end) errors.push('Year end required');
          if (!data.engagement_type) errors.push('Engagement type required');
          break;

        case 'document':
          if (!data.file_name) errors.push('File name required');
          if (!data.mime_type) errors.push('MIME type required');
          break;
      }

      return {
        valid: errors.length === 0,
        errors,
        warnings
      };

    } catch (error) {
      log.error('Validation error:', error);
      return {
        valid: false,
        errors: [error.message],
        warnings
      };
    }
  }

  // Helper methods

  sumAccountsByType(data, type) {
    return (data.accounts || [])
      .filter(a => a.type === type)
      .reduce((sum, a) => sum + Math.abs(a.balance), 0);
  }

  sumAccountsByCategory(data, category) {
    return (data.accounts || [])
      .filter(a => a.category === category)
      .reduce((sum, a) => sum + Math.abs(a.balance), 0);
  }

  sumDebits(data) {
    return (data.accounts || [])
      .filter(a => a.balance > 0)
      .reduce((sum, a) => sum + a.balance, 0);
  }

  sumCredits(data) {
    return (data.accounts || [])
      .filter(a => a.balance < 0)
      .reduce((sum, a) => sum + Math.abs(a.balance), 0);
  }

  calculateAverageBalance(data) {
    const balances = (data.accounts || []).map(a => Math.abs(a.balance));
    return balances.reduce((sum, b) => sum + b, 0) / balances.length;
  }

  calculateMaterialityThreshold(data) {
    const assets = this.sumAccountsByType(data, 'asset');
    return assets * 0.01; // 1% of assets
  }
}

module.exports = LocalProcessor;
