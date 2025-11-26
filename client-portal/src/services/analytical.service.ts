/**
 * Analytical Procedures Service
 * API client for financial analysis and AI-powered insights
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface FinancialData {
  period: string;
  revenue: number;
  expenses: number;
  netIncome: number;
  assets: number;
  liabilities: number;
  equity: number;
}

export interface FinancialRatio {
  name: string;
  value: number;
  priorYear?: number;
  industryAverage?: number;
  category: string;
}

export interface AnalyticalInsight {
  type: 'anomaly' | 'trend' | 'variance' | 'risk';
  severity: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  recommendation: string;
  affectedArea: string;
}

class AnalyticalService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/analytical`,
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

  async calculateRatios(engagementId: string, financialData: FinancialData): Promise<FinancialRatio[]> {
    const response = await this.api.post<{ ratios: FinancialRatio[] }>(
      `/ratios/${engagementId}`,
      financialData
    );
    return response.data.ratios || [];
  }

  async getTrendAnalysis(engagementId: string, periods: number = 8): Promise<FinancialData[]> {
    const response = await this.api.get<{ trends: FinancialData[] }>(
      `/trends/${engagementId}?periods=${periods}`
    );
    return response.data.trends || [];
  }

  async getVarianceAnalysis(engagementId: string): Promise<any> {
    const response = await this.api.get(`/variance/${engagementId}`);
    return response.data;
  }

  async getIndustryBenchmarks(industry: string): Promise<FinancialRatio[]> {
    const response = await this.api.get<{ benchmarks: FinancialRatio[] }>(
      `/benchmarks/${industry}`
    );
    return response.data.benchmarks || [];
  }

  async getAIInsights(engagementId: string): Promise<AnalyticalInsight[]> {
    const response = await this.api.get<{ insights: AnalyticalInsight[] }>(
      `/ai-insights/${engagementId}`
    );
    return response.data.insights || [];
  }

  async runAnalysis(engagementId: string, analysisType: string): Promise<any> {
    const response = await this.api.post(`/run/${engagementId}`, { analysisType });
    return response.data;
  }
}

// Export singleton instance
export const analyticalService = new AnalyticalService();
export default analyticalService;
