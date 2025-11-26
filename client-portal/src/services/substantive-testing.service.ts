/**
 * Substantive Testing Service
 * API client for audit testing and sampling services
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface TestModule {
  id: string;
  name: string;
  icon: string;
  color: string;
  description: string;
  tests: number;
  completed: number;
  anomalies: number;
}

export interface Test {
  id: string;
  name: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'completed';
  sampleSize?: number;
  exceptions?: number;
  aiFlags?: number;
  moduleId: string;
}

export interface AIAnomaly {
  type: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  recommendation: string;
  testArea: string;
}

export interface SampleRequest {
  method: 'statistical' | 'judgmental' | 'stratified' | 'random';
  populationSize: number;
  sampleSize: number;
  confidenceLevel: number;
  expectedErrorRate: number;
}

class SubstantiveTestingService {
  private testingApi: AxiosInstance;
  private samplingApi: AxiosInstance;

  constructor() {
    this.testingApi = axios.create({
      baseURL: `${API_BASE_URL}/substantive-testing`,
      headers: { 'Content-Type': 'application/json' },
    });

    this.samplingApi = axios.create({
      baseURL: `${API_BASE_URL}/sampling`,
      headers: { 'Content-Type': 'application/json' },
    });

    [this.testingApi, this.samplingApi].forEach(api => {
      api.interceptors.request.use((config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      });

      api.interceptors.response.use(
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

  async getTestModules(engagementId: string): Promise<TestModule[]> {
    try {
      const response = await this.testingApi.get(`/engagements/${engagementId}/modules`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch test modules:', error);
      return this.getDefaultTestModules();
    }
  }

  async getTestsForModule(engagementId: string, moduleId: string): Promise<Test[]> {
    try {
      const response = await this.testingApi.get(`/engagements/${engagementId}/modules/${moduleId}/tests`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch tests:', error);
      return this.getDefaultRevenueTests();
    }
  }

  async getAIAnomalies(engagementId: string, moduleId?: string): Promise<AIAnomaly[]> {
    try {
      const url = moduleId
        ? `/engagements/${engagementId}/modules/${moduleId}/anomalies`
        : `/engagements/${engagementId}/anomalies`;
      const response = await this.testingApi.get(url);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch AI anomalies:', error);
      return this.getDefaultAIAnomalies();
    }
  }

  async updateTestStatus(engagementId: string, testId: string, status: Test['status']): Promise<Test> {
    const response = await this.testingApi.patch(`/engagements/${engagementId}/tests/${testId}`, { status });
    return response.data;
  }

  async runAIAnalysis(engagementId: string, moduleId: string): Promise<AIAnomaly[]> {
    const response = await this.testingApi.post(`/engagements/${engagementId}/modules/${moduleId}/ai-analysis`);
    return response.data;
  }

  async generateSample(engagementId: string, request: SampleRequest): Promise<{ sampleItems: any[]; metadata: any }> {
    const response = await this.samplingApi.post(`/engagements/${engagementId}/generate-sample`, request);
    return response.data;
  }

  async createTest(engagementId: string, moduleId: string, test: Partial<Test>): Promise<Test> {
    const response = await this.testingApi.post(`/engagements/${engagementId}/modules/${moduleId}/tests`, test);
    return response.data;
  }

  // Default data
  private getDefaultTestModules(): TestModule[] {
    return [
      {
        id: 'revenue',
        name: 'Revenue Testing',
        icon: 'DollarSign',
        color: 'green',
        description: 'Revenue recognition, invoicing, and cut-off testing',
        tests: 8,
        completed: 6,
        anomalies: 3,
      },
      {
        id: 'receivables',
        name: 'Accounts Receivable',
        icon: 'FileText',
        color: 'blue',
        description: 'AR aging, confirmations, and collectability',
        tests: 6,
        completed: 5,
        anomalies: 2,
      },
      {
        id: 'inventory',
        name: 'Inventory',
        icon: 'Package',
        color: 'purple',
        description: 'Observation, valuation, and obsolescence',
        tests: 7,
        completed: 4,
        anomalies: 1,
      },
      {
        id: 'fixed_assets',
        name: 'Fixed Assets',
        icon: 'Building',
        color: 'cyan',
        description: 'Additions, disposals, and depreciation',
        tests: 5,
        completed: 3,
        anomalies: 0,
      },
      {
        id: 'liabilities',
        name: 'Liabilities & Equity',
        icon: 'CreditCard',
        color: 'orange',
        description: 'Debt, payables, and covenant compliance',
        tests: 6,
        completed: 2,
        anomalies: 1,
      },
    ];
  }

  private getDefaultRevenueTests(): Test[] {
    return [
      {
        id: '1',
        name: 'Revenue Recognition Testing',
        description: 'Test revenue recognition policies and procedures',
        status: 'completed',
        sampleSize: 60,
        exceptions: 0,
        aiFlags: 2,
        moduleId: 'revenue',
      },
      {
        id: '2',
        name: 'Statistical Sample Selection',
        description: 'Select statistically valid revenue sample',
        status: 'completed',
        sampleSize: 60,
        moduleId: 'revenue',
      },
      {
        id: '3',
        name: 'Invoice Testing',
        description: 'Test invoice to supporting documentation',
        status: 'in_progress',
        sampleSize: 60,
        exceptions: 1,
        aiFlags: 3,
        moduleId: 'revenue',
      },
      {
        id: '4',
        name: 'Cut-off Testing',
        description: 'Test revenue recorded in correct period',
        status: 'completed',
        sampleSize: 30,
        exceptions: 0,
        moduleId: 'revenue',
      },
      {
        id: '5',
        name: 'Completeness Testing',
        description: 'Test completeness of revenue recording',
        status: 'completed',
        sampleSize: 40,
        exceptions: 0,
        moduleId: 'revenue',
      },
      {
        id: '6',
        name: 'AI Anomaly Detection',
        description: 'AI-powered pattern and anomaly analysis',
        status: 'completed',
        aiFlags: 5,
        moduleId: 'revenue',
      },
      {
        id: '7',
        name: 'Revenue Analytics',
        description: 'Analytical procedures and trend analysis',
        status: 'in_progress',
        moduleId: 'revenue',
      },
      {
        id: '8',
        name: 'Contract Review',
        description: 'Review revenue contracts for ASC 606 compliance',
        status: 'not_started',
        sampleSize: 15,
        moduleId: 'revenue',
      },
    ];
  }

  private getDefaultAIAnomalies(): AIAnomaly[] {
    return [
      {
        type: 'high',
        title: 'Unusual Revenue Spike - Customer XYZ',
        description: 'Revenue from Customer XYZ increased 450% in Q4. Single invoice for $1.2M on Dec 30.',
        recommendation: 'Review invoice, contract, and delivery documentation. Verify revenue recognition timing.',
        testArea: 'Revenue Recognition',
      },
      {
        type: 'medium',
        title: 'Pricing Variance Detected',
        description: '12 invoices show pricing 15-20% below standard rates without documented approvals.',
        recommendation: 'Obtain pricing approval documentation. Assess impact on revenue completeness.',
        testArea: 'Invoice Testing',
      },
      {
        type: 'medium',
        title: 'Missing Sequential Invoice Numbers',
        description: 'Invoice sequence shows gaps: #1045-1048 missing. May indicate completeness issue.',
        recommendation: 'Investigate missing invoices. Confirm void/cancelled or potential completeness concern.',
        testArea: 'Completeness',
      },
    ];
  }
}

export const substantiveTestingService = new SubstantiveTestingService();
export default substantiveTestingService;
