/**
 * Testing Service
 * API client for audit testing procedures
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface Test {
  id: string;
  engagement_id: string;
  module: string;
  name: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'completed';
  sampleSize?: number;
  exceptions?: number;
  aiFlags?: number;
  created_at: string;
  updated_at: string;
}

export interface TestCreate {
  engagement_id: string;
  module: string;
  name: string;
  description: string;
  sampleSize?: number;
}

export interface SampleSelection {
  method: 'statistical' | 'judgmental' | 'stratified' | 'random';
  populationSize: number;
  sampleSize: number;
  confidenceLevel: number;
  expectedErrorRate: number;
}

export interface TestAnomaly {
  type: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  recommendation: string;
  testArea: string;
  affectedItems?: string[];
}

class TestingService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/testing`,
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

  async listTests(engagementId: string, module?: string): Promise<Test[]> {
    const url = module
      ? `/tests/${engagementId}?module=${module}`
      : `/tests/${engagementId}`;
    const response = await this.api.get<{ tests: Test[] }>(url);
    return response.data.tests || [];
  }

  async getTest(id: string): Promise<Test> {
    const response = await this.api.get<Test>(`/tests/${id}`);
    return response.data;
  }

  async createTest(data: TestCreate): Promise<Test> {
    const response = await this.api.post<Test>('/tests', data);
    return response.data;
  }

  async updateTest(id: string, data: Partial<Test>): Promise<Test> {
    const response = await this.api.patch<Test>(`/tests/${id}`, data);
    return response.data;
  }

  async deleteTest(id: string): Promise<void> {
    await this.api.delete(`/tests/${id}`);
  }

  async generateSample(selection: SampleSelection): Promise<any> {
    const response = await this.api.post('/sample-selection', selection);
    return response.data;
  }

  async runAIAnalysis(testId: string): Promise<TestAnomaly[]> {
    const response = await this.api.post<{ anomalies: TestAnomaly[] }>(
      `/ai-analysis/${testId}`
    );
    return response.data.anomalies || [];
  }

  async getAnomalies(engagementId: string, module?: string): Promise<TestAnomaly[]> {
    const url = module
      ? `/anomalies/${engagementId}?module=${module}`
      : `/anomalies/${engagementId}`;
    const response = await this.api.get<{ anomalies: TestAnomaly[] }>(url);
    return response.data.anomalies || [];
  }

  async recordException(testId: string, exception: any): Promise<any> {
    const response = await this.api.post(`/tests/${testId}/exceptions`, exception);
    return response.data;
  }
}

// Export singleton instance
export const testingService = new TestingService();
export default testingService;
