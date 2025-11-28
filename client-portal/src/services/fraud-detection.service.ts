/**
 * Fraud Detection Service
 * API client for real-time fraud detection and bank account monitoring
 */

import axios, { AxiosInstance } from 'axios';
import {
  BankAccount,
  BankAccountCreate,
  BankAccountUpdate,
  FraudAlert,
  FraudAlertUpdate,
  FraudCase,
  FraudCaseCreate,
  FraudCaseUpdate,
  FraudCaseActivity,
  FraudCaseActivityCreate,
  FraudTransaction,
  TransactionAnalysis,
  FraudStatistics,
  FraudDashboardMetrics,
  FraudFeatureFlag,
  FraudFeatureFlagUpdate,
  PlaidLinkTokenResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class FraudDetectionService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/fraud-detection`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // ========================================
  // Health & Status
  // ========================================

  async healthCheck(): Promise<{
    status: string;
    service: string;
    version: string;
  }> {
    const response = await this.api.get('/health');
    return response.data;
  }

  // ========================================
  // Plaid Integration - Bank Account Connection
  // ========================================

  async createPlaidLinkToken(userId: string): Promise<PlaidLinkTokenResponse> {
    const response = await this.api.post('/plaid/link-token', null, {
      params: { user_id: userId },
    });
    return response.data;
  }

  async exchangePlaidToken(
    customerId: string,
    publicToken: string,
    accountId: string,
    institutionId: string,
    institutionName: string
  ): Promise<BankAccount> {
    const response = await this.api.post('/plaid/exchange-token', {
      public_token: publicToken,
      account_id: accountId,
      institution_id: institutionId,
      institution_name: institutionName,
    }, {
      params: { customer_id: customerId },
    });
    return response.data;
  }

  // ========================================
  // Bank Account Management
  // ========================================

  async listBankAccounts(
    customerId: string,
    params?: { skip?: number; limit?: number }
  ): Promise<BankAccount[]> {
    const response = await this.api.get('/bank-accounts', {
      params: { customer_id: customerId, ...params },
    });
    return response.data;
  }

  async getBankAccount(accountId: string): Promise<BankAccount> {
    const response = await this.api.get(`/bank-accounts/${accountId}`);
    return response.data;
  }

  async updateBankAccount(
    accountId: string,
    data: BankAccountUpdate
  ): Promise<BankAccount> {
    const response = await this.api.patch(`/bank-accounts/${accountId}`, data);
    return response.data;
  }

  async syncBankAccount(accountId: string): Promise<{ message: string; account_id: string }> {
    const response = await this.api.post(`/bank-accounts/${accountId}/sync`);
    return response.data;
  }

  // ========================================
  // Transaction Management
  // ========================================

  async listTransactions(params: {
    customer_id: string;
    bank_account_id?: string;
    flagged_only?: boolean;
    min_fraud_score?: number;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<FraudTransaction[]> {
    const response = await this.api.get('/transactions', { params });
    return response.data;
  }

  async getTransactionAnalysis(transactionId: string): Promise<TransactionAnalysis> {
    const response = await this.api.get(`/transactions/${transactionId}`);
    return response.data;
  }

  async analyzeBatchTransactions(
    transactionIds: string[],
    forceReanalysis: boolean = false
  ): Promise<{
    total_processed: number;
    flagged_count: number;
    new_cases_created: number;
    processing_time_seconds: number;
    results: any[];
  }> {
    const response = await this.api.post('/transactions/analyze-batch', {
      transaction_ids: transactionIds,
      force_reanalysis: forceReanalysis,
    });
    return response.data;
  }

  // ========================================
  // Fraud Case Management
  // ========================================

  async createFraudCase(
    data: FraudCaseCreate,
    userId: string
  ): Promise<FraudCase> {
    const response = await this.api.post('/fraud-cases', data, {
      params: { user_id: userId },
    });
    return response.data;
  }

  async listFraudCases(params?: {
    customer_id?: string;
    status?: string;
    severity?: string;
    skip?: number;
    limit?: number;
  }): Promise<FraudCase[]> {
    const response = await this.api.get('/fraud-cases', { params });
    return response.data;
  }

  async getFraudCase(caseId: string): Promise<FraudCase> {
    const response = await this.api.get(`/fraud-cases/${caseId}`);
    return response.data;
  }

  async updateFraudCase(
    caseId: string,
    data: FraudCaseUpdate,
    userId: string
  ): Promise<FraudCase> {
    const response = await this.api.patch(`/fraud-cases/${caseId}`, data, {
      params: { user_id: userId },
    });
    return response.data;
  }

  async getCaseActivities(caseId: string): Promise<FraudCaseActivity[]> {
    const response = await this.api.get(`/fraud-cases/${caseId}/activities`);
    return response.data;
  }

  async addCaseActivity(
    caseId: string,
    data: FraudCaseActivityCreate,
    userId: string
  ): Promise<FraudCaseActivity> {
    const response = await this.api.post(`/fraud-cases/${caseId}/activities`, data, {
      params: { user_id: userId },
    });
    return response.data;
  }

  // ========================================
  // Fraud Alerts
  // ========================================

  async listAlerts(params?: {
    status?: string;
    severity?: string;
    skip?: number;
    limit?: number;
  }): Promise<FraudAlert[]> {
    const response = await this.api.get('/alerts', { params });
    return response.data;
  }

  async updateAlert(
    alertId: string,
    data: FraudAlertUpdate,
    userId: string
  ): Promise<FraudAlert> {
    const response = await this.api.patch(`/alerts/${alertId}`, data, {
      params: { user_id: userId },
    });
    return response.data;
  }

  // ========================================
  // Feature Flags
  // ========================================

  async getFeatureFlag(customerId: string): Promise<FraudFeatureFlag> {
    const response = await this.api.get(`/feature-flags/${customerId}`);
    return response.data;
  }

  async updateFeatureFlag(
    customerId: string,
    data: FraudFeatureFlagUpdate,
    userId: string
  ): Promise<FraudFeatureFlag> {
    const response = await this.api.patch(`/feature-flags/${customerId}`, data, {
      params: { user_id: userId },
    });
    return response.data;
  }

  // ========================================
  // Statistics and Dashboard
  // ========================================

  async getStatistics(params?: {
    customer_id?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<FraudStatistics> {
    const response = await this.api.get('/statistics', { params });
    return response.data;
  }

  async getDashboardMetrics(): Promise<FraudDashboardMetrics> {
    const response = await this.api.get('/dashboard');
    return response.data;
  }
}

// Export singleton instance
export const fraudDetectionService = new FraudDetectionService();
export default fraudDetectionService;
