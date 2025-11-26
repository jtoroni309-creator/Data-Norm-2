/**
 * Financial Analysis Service
 * API client for analytical procedures and financial analysis
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface FinancialRatio {
  name: string;
  value: number;
  priorYear: number;
  industry: number;
  category: string;
  description: string;
  variance: number;
  status: 'normal' | 'warning' | 'alert';
}

export interface TrendData {
  period: string;
  revenue: number;
  expenses: number;
  netIncome: number;
  grossMargin: number;
}

export interface AIInsight {
  type: 'critical' | 'warning' | 'info' | 'positive';
  title: string;
  description: string;
  recommendations: string[];
  impact: 'high' | 'medium' | 'low';
}

export interface FinancialAnalysisData {
  ratios: FinancialRatio[];
  trends: TrendData[];
  insights: AIInsight[];
}

class FinancialAnalysisService {
  private api: AxiosInstance;
  private analyticsApi: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/financial-analysis`,
      headers: { 'Content-Type': 'application/json' },
    });

    this.analyticsApi = axios.create({
      baseURL: `${API_BASE_URL}/analytics`,
      headers: { 'Content-Type': 'application/json' },
    });

    [this.api, this.analyticsApi].forEach(apiInstance => {
      apiInstance.interceptors.request.use((config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      });

      apiInstance.interceptors.response.use(
        (response) => response,
        (error) => {
          if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
          }
          return Promise.reject(error);
        }
      );
    });
  }

  async getFinancialAnalysis(engagementId: string): Promise<FinancialAnalysisData> {
    try {
      const [ratiosRes, trendsRes, insightsRes] = await Promise.all([
        this.api.get(`/engagements/${engagementId}/ratios`).catch(() => ({ data: null })),
        this.api.get(`/engagements/${engagementId}/trends`).catch(() => ({ data: null })),
        this.analyticsApi.get(`/engagements/${engagementId}/insights`).catch(() => ({ data: null }))
      ]);

      return {
        ratios: ratiosRes.data || this.getDefaultRatios(),
        trends: trendsRes.data || this.getDefaultTrends(),
        insights: insightsRes.data || this.getDefaultInsights(),
      };
    } catch (error) {
      console.error('Failed to fetch financial analysis:', error);
      return {
        ratios: this.getDefaultRatios(),
        trends: this.getDefaultTrends(),
        insights: this.getDefaultInsights(),
      };
    }
  }

  async getRatios(engagementId: string): Promise<FinancialRatio[]> {
    try {
      const response = await this.api.get(`/engagements/${engagementId}/ratios`);
      return response.data;
    } catch (error) {
      return this.getDefaultRatios();
    }
  }

  async getTrends(engagementId: string): Promise<TrendData[]> {
    try {
      const response = await this.api.get(`/engagements/${engagementId}/trends`);
      return response.data;
    } catch (error) {
      return this.getDefaultTrends();
    }
  }

  async getAIInsights(engagementId: string): Promise<AIInsight[]> {
    try {
      const response = await this.analyticsApi.get(`/engagements/${engagementId}/insights`);
      return response.data;
    } catch (error) {
      return this.getDefaultInsights();
    }
  }

  async runAIAnalysis(engagementId: string): Promise<AIInsight[]> {
    const response = await this.analyticsApi.post(`/engagements/${engagementId}/run-analysis`);
    return response.data;
  }

  async importFinancials(engagementId: string, data: FormData): Promise<{ success: boolean; message: string }> {
    const response = await this.api.post(`/engagements/${engagementId}/import`, data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  async exportAnalysis(engagementId: string, format: 'pdf' | 'excel' | 'csv'): Promise<Blob> {
    const response = await this.api.get(`/engagements/${engagementId}/export`, {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  }

  // Default data
  private getDefaultRatios(): FinancialRatio[] {
    return [
      {
        name: 'Current Ratio',
        value: 2.3,
        priorYear: 2.5,
        industry: 2.1,
        category: 'Liquidity',
        description: 'Ability to pay short-term obligations',
        variance: -8.0,
        status: 'normal',
      },
      {
        name: 'Quick Ratio',
        value: 1.5,
        priorYear: 1.8,
        industry: 1.4,
        category: 'Liquidity',
        description: 'Ability to meet short-term obligations with liquid assets',
        variance: -16.7,
        status: 'warning',
      },
      {
        name: 'Gross Margin %',
        value: 42.5,
        priorYear: 45.2,
        industry: 44.0,
        category: 'Profitability',
        description: 'Percentage of revenue retained after COGS',
        variance: -6.0,
        status: 'warning',
      },
      {
        name: 'Net Profit Margin %',
        value: 8.2,
        priorYear: 10.5,
        industry: 9.8,
        category: 'Profitability',
        description: 'Net income as percentage of revenue',
        variance: -21.9,
        status: 'alert',
      },
      {
        name: 'Return on Assets',
        value: 7.5,
        priorYear: 8.1,
        industry: 8.0,
        category: 'Profitability',
        description: 'Efficiency in using assets to generate profit',
        variance: -7.4,
        status: 'normal',
      },
      {
        name: 'Debt to Equity',
        value: 0.65,
        priorYear: 0.58,
        industry: 0.70,
        category: 'Leverage',
        description: 'Financial leverage and capital structure',
        variance: 12.1,
        status: 'normal',
      },
      {
        name: 'Interest Coverage',
        value: 4.2,
        priorYear: 5.8,
        industry: 5.0,
        category: 'Leverage',
        description: 'Ability to meet interest payments',
        variance: -27.6,
        status: 'warning',
      },
      {
        name: 'Inventory Turnover',
        value: 6.8,
        priorYear: 7.2,
        industry: 7.5,
        category: 'Efficiency',
        description: 'How quickly inventory is sold',
        variance: -5.6,
        status: 'normal',
      },
      {
        name: 'Days Sales Outstanding',
        value: 52,
        priorYear: 48,
        industry: 45,
        category: 'Efficiency',
        description: 'Average collection period for receivables',
        variance: 8.3,
        status: 'warning',
      },
      {
        name: 'Asset Turnover',
        value: 1.45,
        priorYear: 1.52,
        industry: 1.50,
        category: 'Efficiency',
        description: 'Efficiency in using assets to generate revenue',
        variance: -4.6,
        status: 'normal',
      },
    ];
  }

  private getDefaultTrends(): TrendData[] {
    return [
      { period: 'Q1 2023', revenue: 2500000, expenses: 2100000, netIncome: 400000, grossMargin: 44.0 },
      { period: 'Q2 2023', revenue: 2650000, expenses: 2200000, netIncome: 450000, grossMargin: 45.5 },
      { period: 'Q3 2023', revenue: 2800000, expenses: 2350000, netIncome: 450000, grossMargin: 46.2 },
      { period: 'Q4 2023', revenue: 3200000, expenses: 2750000, netIncome: 450000, grossMargin: 45.8 },
      { period: 'Q1 2024', revenue: 2450000, expenses: 2050000, netIncome: 400000, grossMargin: 43.5 },
      { period: 'Q2 2024', revenue: 2600000, expenses: 2180000, netIncome: 420000, grossMargin: 42.8 },
      { period: 'Q3 2024', revenue: 2750000, expenses: 2300000, netIncome: 450000, grossMargin: 42.2 },
      { period: 'Q4 2024', revenue: 2900000, expenses: 2480000, netIncome: 420000, grossMargin: 41.5 },
    ];
  }

  private getDefaultInsights(): AIInsight[] {
    return [
      {
        type: 'critical',
        title: 'Significant Margin Compression',
        description: 'Gross margin has declined from 45.2% to 42.5% year-over-year. Net profit margin down 21.9%. Investigate: 1) Pricing pressure, 2) COGS increases, 3) Product mix changes.',
        recommendations: [
          'Perform detailed variance analysis on COGS by product line',
          'Review pricing strategy and competitive positioning',
          'Analyze product mix shift impact on margins',
        ],
        impact: 'high',
      },
      {
        type: 'warning',
        title: 'Declining Interest Coverage',
        description: 'Interest coverage ratio decreased 27.6% to 4.2x. While still adequate, this trend warrants attention given increasing debt levels.',
        recommendations: [
          'Review debt covenant compliance',
          'Assess refinancing opportunities',
          'Evaluate debt repayment schedule',
        ],
        impact: 'medium',
      },
      {
        type: 'info',
        title: 'Working Capital Management',
        description: 'Days Sales Outstanding increased from 48 to 52 days. Collection efficiency has declined slightly but remains close to industry average.',
        recommendations: [
          'Review aging of receivables',
          'Assess credit policies',
          'Identify slow-paying customers',
        ],
        impact: 'medium',
      },
      {
        type: 'positive',
        title: 'Strong Liquidity Position',
        description: 'Current ratio of 2.3x exceeds industry average of 2.1x. Quick ratio of 1.5x also above industry norm, indicating solid short-term liquidity.',
        recommendations: [
          'Continue monitoring working capital',
          'Evaluate optimal cash levels',
        ],
        impact: 'low',
      },
    ];
  }
}

export const financialAnalysisService = new FinancialAnalysisService();
export default financialAnalysisService;
