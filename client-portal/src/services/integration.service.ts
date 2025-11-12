/**
 * Integration Service
 * Handles connections to accounting software, payroll systems, and Plaid
 */

import axios from 'axios';
import type { Integration, IntegrationConnection, IntegrationType } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export class IntegrationService {
  /**
   * Get all available integrations
   */
  public async getAvailableIntegrations(): Promise<Integration[]> {
    const response = await axios.get<Integration[]>(`${API_BASE_URL}/integrations/available`);
    return response.data;
  }

  /**
   * Get user's connected integrations
   */
  public async getConnectedIntegrations(): Promise<IntegrationConnection[]> {
    const response = await axios.get<IntegrationConnection[]>(`${API_BASE_URL}/integrations/connected`);
    return response.data;
  }

  /**
   * Initiate integration connection
   */
  public async initiateConnection(integrationType: IntegrationType): Promise<{ authUrl: string; state: string }> {
    const response = await axios.post<{ authUrl: string; state: string }>(
      `${API_BASE_URL}/integrations/${integrationType}/connect`
    );

    // Store state for verification
    localStorage.setItem(`integration_state_${integrationType}`, response.data.state);

    return response.data;
  }

  /**
   * Handle integration OAuth callback
   */
  public async handleIntegrationCallback(
    integrationType: IntegrationType,
    code: string,
    state: string
  ): Promise<IntegrationConnection> {
    // Verify state
    const savedState = localStorage.getItem(`integration_state_${integrationType}`);
    if (state !== savedState) {
      throw new Error('Invalid state parameter');
    }

    localStorage.removeItem(`integration_state_${integrationType}`);

    const response = await axios.post<IntegrationConnection>(
      `${API_BASE_URL}/integrations/${integrationType}/callback`,
      { code, state }
    );

    return response.data;
  }

  /**
   * Disconnect integration
   */
  public async disconnectIntegration(connectionId: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/integrations/${connectionId}`);
  }

  /**
   * Trigger manual sync
   */
  public async syncIntegration(connectionId: string): Promise<void> {
    await axios.post(`${API_BASE_URL}/integrations/${connectionId}/sync`);
  }

  /**
   * Get integration details
   */
  public getIntegrationDetails(): Record<IntegrationType, Omit<Integration, 'id' | 'status' | 'connectedAt' | 'lastSyncAt'>> {
    return {
      quickbooks: {
        type: 'quickbooks',
        name: 'QuickBooks Online',
        description: 'Automatically sync your financial statements, general ledger, and transaction data',
        icon: '/icons/quickbooks.svg',
        dataCategories: ['Financial Statements', 'General Ledger', 'Transactions', 'Account Balances'],
      },
      xero: {
        type: 'xero',
        name: 'Xero',
        description: 'Connect your Xero account to import financial data and reports',
        icon: '/icons/xero.svg',
        dataCategories: ['Financial Statements', 'Bank Transactions', 'Invoices', 'Bills'],
      },
      sage: {
        type: 'sage',
        name: 'Sage Intacct',
        description: 'Sync your Sage Intacct data including GL accounts and financial reports',
        icon: '/icons/sage.svg',
        dataCategories: ['General Ledger', 'Financial Reports', 'Dimensions', 'Transactions'],
      },
      netsuite: {
        type: 'netsuite',
        name: 'NetSuite',
        description: 'Enterprise ERP integration for comprehensive financial data',
        icon: '/icons/netsuite.svg',
        dataCategories: ['Financial Statements', 'Subsidiaries', 'Revenue Recognition', 'Multi-Entity'],
      },
      adp: {
        type: 'adp',
        name: 'ADP Workforce',
        description: 'Connect ADP to sync payroll data, tax filings, and employee information',
        icon: '/icons/adp.svg',
        dataCategories: ['Payroll Data', 'Tax Filings', 'Employee Records', 'Compensation'],
      },
      gusto: {
        type: 'gusto',
        name: 'Gusto',
        description: 'Import payroll information, benefits, and contractor payments',
        icon: '/icons/gusto.svg',
        dataCategories: ['Payroll', 'Benefits', 'Contractors', 'Time Tracking'],
      },
      paychex: {
        type: 'paychex',
        name: 'Paychex',
        description: 'Sync payroll and HR data from Paychex',
        icon: '/icons/paychex.svg',
        dataCategories: ['Payroll Processing', 'Tax Services', 'HR Data', 'Retirement Services'],
      },
      plaid: {
        type: 'plaid',
        name: 'Bank Account (Plaid)',
        description: 'Securely connect your bank accounts for fraud monitoring and transaction analysis',
        icon: '/icons/plaid.svg',
        dataCategories: ['Bank Transactions', 'Account Balances', 'Transaction Categorization', 'Fraud Detection'],
      },
    };
  }

  /**
   * Connect Plaid (special handling for bank connections)
   */
  public async initiatePlaidConnection(): Promise<{ linkToken: string }> {
    const response = await axios.post<{ linkToken: string }>(`${API_BASE_URL}/integrations/plaid/link-token`);
    return response.data;
  }

  /**
   * Exchange Plaid public token for access token
   */
  public async exchangePlaidToken(publicToken: string, metadata: any): Promise<IntegrationConnection> {
    const response = await axios.post<IntegrationConnection>(`${API_BASE_URL}/integrations/plaid/exchange`, {
      publicToken,
      metadata,
    });
    return response.data;
  }

  /**
   * Get integration sync status
   */
  public async getSyncStatus(connectionId: string): Promise<{
    status: 'idle' | 'syncing' | 'complete' | 'error';
    progress: number;
    lastSync?: string;
    nextSync?: string;
    recordsSynced?: number;
  }> {
    const response = await axios.get(`${API_BASE_URL}/integrations/${connectionId}/sync-status`);
    return response.data;
  }

  /**
   * Test integration connection
   */
  public async testConnection(connectionId: string): Promise<{ success: boolean; message: string }> {
    const response = await axios.post(`${API_BASE_URL}/integrations/${connectionId}/test`);
    return response.data;
  }

  /**
   * Convenience helpers for UI layers that expect simplified method names
   */
  public async connect(integrationType: IntegrationType): Promise<{ authUrl: string; state: string }> {
    return this.initiateConnection(integrationType);
  }

  public async disconnect(connectionId: string): Promise<void> {
    return this.disconnectIntegration(connectionId);
  }

  public async syncData(connectionId: string): Promise<void> {
    return this.syncIntegration(connectionId);
  }
}

export const integrationService = new IntegrationService();
