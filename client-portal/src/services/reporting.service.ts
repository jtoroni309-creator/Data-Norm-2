/**
 * Reporting Service
 * API client for report generation and management
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface Report {
  id: string;
  engagement_id: string;
  report_type: string;
  title: string;
  description?: string;
  status: 'draft' | 'generating' | 'completed' | 'failed';
  fiscal_year?: string;
  report_date?: string;
  period_start?: string;
  period_end?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
  pdf_url?: string;
}

export interface ReportCreate {
  engagement_id: string;
  report_type: string;
  title: string;
  description?: string;
  report_data: Record<string, any>;
  fiscal_year?: string;
  report_date?: string;
  period_start?: string;
  period_end?: string;
}

export interface ReportStats {
  total_reports: number;
  completed_reports: number;
  pending_reports: number;
  failed_reports: number;
}

class ReportingService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/reporting`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth interceptor
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle 401 responses
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async listReports(): Promise<Report[]> {
    const response = await this.api.get<{ reports: Report[] }>('/reports');
    return response.data.reports || [];
  }

  async getReport(id: string): Promise<Report> {
    const response = await this.api.get<Report>(`/reports/${id}`);
    return response.data;
  }

  async createReport(data: ReportCreate): Promise<Report> {
    const response = await this.api.post<Report>('/reports', data);
    return response.data;
  }

  async generateReport(id: string): Promise<Report> {
    const response = await this.api.post<Report>(`/reports/${id}/generate`);
    return response.data;
  }

  async downloadReport(id: string): Promise<Blob> {
    const response = await this.api.get(`/reports/${id}/download`, {
      responseType: 'blob'
    });
    return response.data;
  }

  async getStats(): Promise<ReportStats> {
    const response = await this.api.get<ReportStats>('/stats');
    return response.data;
  }
}

// Export singleton instance
export const reportingService = new ReportingService();
export default reportingService;
