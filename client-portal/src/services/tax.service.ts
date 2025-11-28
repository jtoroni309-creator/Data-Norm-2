/**
 * Tax Engine Service
 * API client for tax computation and form preparation
 */

import axios, { AxiosInstance } from 'axios';
import {
  TaxReturn,
  TaxReturnCreate,
  TaxReturnSummary,
  TaxCalculationResult,
  TaxLineExplanation,
  TaxRule,
  TaxFormData,
  TaxSchedule,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class TaxService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/tax`,
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
    features: Record<string, boolean>;
  }> {
    const response = await this.api.get('/health');
    return response.data;
  }

  // ========================================
  // Tax Returns
  // ========================================

  async listReturns(params?: {
    client_id?: string;
    tax_year?: number;
    form_type?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ items: TaxReturnSummary[]; total: number }> {
    const response = await this.api.get('/v1/returns', { params });
    return response.data;
  }

  async getReturn(returnId: string): Promise<TaxReturn> {
    const response = await this.api.get(`/v1/returns/${returnId}`);
    return response.data;
  }

  async createReturn(data: TaxReturnCreate): Promise<TaxReturn> {
    const response = await this.api.post('/v1/returns', data);
    return response.data;
  }

  async updateReturn(returnId: string, data: Partial<TaxReturn>): Promise<TaxReturn> {
    const response = await this.api.patch(`/v1/returns/${returnId}`, data);
    return response.data;
  }

  async deleteReturn(returnId: string): Promise<void> {
    await this.api.delete(`/v1/returns/${returnId}`);
  }

  // ========================================
  // Tax Calculations
  // ========================================

  async calculateReturn(
    returnId: string,
    forceRecalculate: boolean = false
  ): Promise<TaxCalculationResult> {
    const response = await this.api.post(`/v1/returns/${returnId}/calculate`, null, {
      params: { force_recalculate: forceRecalculate },
    });
    return response.data;
  }

  async getCalculationResult(returnId: string): Promise<TaxCalculationResult> {
    const response = await this.api.get(`/v1/returns/${returnId}/calculation`);
    return response.data;
  }

  async explainLine(returnId: string, line: string): Promise<TaxLineExplanation> {
    const response = await this.api.post(`/v1/returns/${returnId}/explain/${line}`);
    return response.data;
  }

  // ========================================
  // Form Data
  // ========================================

  async getFormData(returnId: string, formType: string): Promise<TaxFormData> {
    const response = await this.api.get(`/v1/returns/${returnId}/forms/${formType}`);
    return response.data;
  }

  async updateFormData(
    returnId: string,
    formType: string,
    data: Record<string, any>
  ): Promise<TaxFormData> {
    const response = await this.api.patch(`/v1/returns/${returnId}/forms/${formType}`, data);
    return response.data;
  }

  async getSchedules(returnId: string): Promise<TaxSchedule[]> {
    const response = await this.api.get(`/v1/returns/${returnId}/schedules`);
    return response.data;
  }

  async getSchedule(returnId: string, scheduleType: string): Promise<TaxSchedule> {
    const response = await this.api.get(`/v1/returns/${returnId}/schedules/${scheduleType}`);
    return response.data;
  }

  async updateSchedule(
    returnId: string,
    scheduleType: string,
    data: Record<string, any>
  ): Promise<TaxSchedule> {
    const response = await this.api.patch(
      `/v1/returns/${returnId}/schedules/${scheduleType}`,
      data
    );
    return response.data;
  }

  // ========================================
  // Tax Rules & Reference
  // ========================================

  async getTaxRules(taxYear: number, jurisdiction: string = 'federal'): Promise<TaxRule[]> {
    const response = await this.api.get(`/v1/rules/${taxYear}`, {
      params: { jurisdiction },
    });
    return response.data.rules;
  }

  async getTaxBrackets(
    taxYear: number,
    filingStatus: string
  ): Promise<{ brackets: Array<{ min: number; max: number; rate: number }> }> {
    const response = await this.api.get(`/v1/reference/brackets/${taxYear}`, {
      params: { filing_status: filingStatus },
    });
    return response.data;
  }

  async getStandardDeduction(
    taxYear: number,
    filingStatus: string
  ): Promise<{ amount: number; additional_65_or_blind: number }> {
    const response = await this.api.get(`/v1/reference/standard-deduction/${taxYear}`, {
      params: { filing_status: filingStatus },
    });
    return response.data;
  }

  // ========================================
  // Validation
  // ========================================

  async validateReturn(returnId: string): Promise<{
    is_valid: boolean;
    errors: Array<{ field: string; message: string; severity: string }>;
    warnings: Array<{ field: string; message: string }>;
  }> {
    const response = await this.api.post(`/v1/returns/${returnId}/validate`);
    return response.data;
  }

  // ========================================
  // E-File
  // ========================================

  async prepareEfile(returnId: string): Promise<{
    efile_ready: boolean;
    xml_content?: string;
    validation_errors: string[];
  }> {
    const response = await this.api.post(`/v1/returns/${returnId}/efile/prepare`);
    return response.data;
  }

  async submitEfile(returnId: string): Promise<{
    submission_id: string;
    status: string;
    submitted_at: string;
  }> {
    const response = await this.api.post(`/v1/returns/${returnId}/efile/submit`);
    return response.data;
  }

  async getEfileStatus(returnId: string): Promise<{
    submission_id: string;
    status: string;
    irs_status?: string;
    rejection_codes?: string[];
    accepted_at?: string;
  }> {
    const response = await this.api.get(`/v1/returns/${returnId}/efile/status`);
    return response.data;
  }

  // ========================================
  // PDF Generation
  // ========================================

  async generatePDF(returnId: string, formTypes?: string[]): Promise<Blob> {
    const response = await this.api.post(
      `/v1/returns/${returnId}/pdf`,
      { form_types: formTypes },
      { responseType: 'blob' }
    );
    return response.data;
  }

  async downloadPDF(returnId: string, formTypes?: string[]): Promise<void> {
    const blob = await this.generatePDF(returnId, formTypes);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tax-return-${returnId}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  // ========================================
  // Import/Export
  // ========================================

  async importFromPriorYear(
    clientId: string,
    priorYearReturnId: string,
    taxYear: number
  ): Promise<TaxReturn> {
    const response = await this.api.post('/v1/returns/import/prior-year', {
      client_id: clientId,
      prior_year_return_id: priorYearReturnId,
      tax_year: taxYear,
    });
    return response.data;
  }

  async importFromIntegration(
    clientId: string,
    integrationId: string,
    taxYear: number
  ): Promise<TaxReturn> {
    const response = await this.api.post('/v1/returns/import/integration', {
      client_id: clientId,
      integration_id: integrationId,
      tax_year: taxYear,
    });
    return response.data;
  }
}

// Export singleton instance
export const taxService = new TaxService();
export default taxService;
