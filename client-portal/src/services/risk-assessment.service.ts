/**
 * Risk Assessment Service
 * API client for risk monitor and fraud detection services
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface RiskArea {
  area: string;
  inherentRisk: 'low' | 'medium' | 'high';
  controlRisk: 'low' | 'medium' | 'high';
  detectionRisk: 'low' | 'medium' | 'high';
  auditRisk: 'low' | 'medium' | 'high';
  rationale: string;
}

export interface FraudRisk {
  type: string;
  risk: 'low' | 'medium' | 'high';
  factors: string[];
  procedures: string[];
}

export interface GoingConcernIndicator {
  indicator: string;
  present: boolean;
  impact: 'low' | 'medium' | 'high';
}

export interface RiskAssessmentData {
  riskAreas: RiskArea[];
  fraudRisks: FraudRisk[];
  goingConcernIndicators: GoingConcernIndicator[];
  aiAssessment?: string;
}

class RiskAssessmentService {
  private riskApi: AxiosInstance;
  private fraudApi: AxiosInstance;

  constructor() {
    this.riskApi = axios.create({
      baseURL: `${API_BASE_URL}/risk-monitor`,
      headers: { 'Content-Type': 'application/json' },
    });

    this.fraudApi = axios.create({
      baseURL: `${API_BASE_URL}/fraud-detection`,
      headers: { 'Content-Type': 'application/json' },
    });

    // Add auth interceptor to both
    [this.riskApi, this.fraudApi].forEach(api => {
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

  async getRiskAssessment(engagementId: string): Promise<RiskAssessmentData> {
    try {
      const [riskResponse, fraudResponse, goingConcernResponse] = await Promise.all([
        this.riskApi.get(`/engagements/${engagementId}/risk-areas`).catch(() => ({ data: null })),
        this.fraudApi.get(`/engagements/${engagementId}/fraud-risks`).catch(() => ({ data: null })),
        this.riskApi.get(`/engagements/${engagementId}/going-concern`).catch(() => ({ data: null }))
      ]);

      return {
        riskAreas: riskResponse.data || this.getDefaultRiskAreas(),
        fraudRisks: fraudResponse.data || this.getDefaultFraudRisks(),
        goingConcernIndicators: goingConcernResponse.data || this.getDefaultGoingConcernIndicators(),
      };
    } catch (error) {
      console.error('Failed to fetch risk assessment data:', error);
      // Return defaults if API fails
      return {
        riskAreas: this.getDefaultRiskAreas(),
        fraudRisks: this.getDefaultFraudRisks(),
        goingConcernIndicators: this.getDefaultGoingConcernIndicators(),
      };
    }
  }

  async saveRiskArea(engagementId: string, riskArea: RiskArea): Promise<RiskArea> {
    const response = await this.riskApi.post(`/engagements/${engagementId}/risk-areas`, riskArea);
    return response.data;
  }

  async updateRiskArea(engagementId: string, areaName: string, riskArea: Partial<RiskArea>): Promise<RiskArea> {
    const response = await this.riskApi.put(`/engagements/${engagementId}/risk-areas/${encodeURIComponent(areaName)}`, riskArea);
    return response.data;
  }

  async saveFraudRisk(engagementId: string, fraudRisk: FraudRisk): Promise<FraudRisk> {
    const response = await this.fraudApi.post(`/engagements/${engagementId}/fraud-risks`, fraudRisk);
    return response.data;
  }

  async saveGoingConcernIndicator(engagementId: string, indicator: GoingConcernIndicator): Promise<GoingConcernIndicator> {
    const response = await this.riskApi.post(`/engagements/${engagementId}/going-concern`, indicator);
    return response.data;
  }

  async runAIRiskAnalysis(engagementId: string): Promise<{ assessment: string; recommendations: string[] }> {
    const response = await this.riskApi.post(`/engagements/${engagementId}/ai-analysis`);
    return response.data;
  }

  // Default data - used when API is not yet populated
  private getDefaultRiskAreas(): RiskArea[] {
    return [
      {
        area: 'Revenue Recognition',
        inherentRisk: 'high',
        controlRisk: 'medium',
        detectionRisk: 'low',
        auditRisk: 'medium',
        rationale: 'Complex revenue streams with multiple performance obligations. Controls are adequate but require substantive testing.',
      },
      {
        area: 'Inventory Valuation',
        inherentRisk: 'medium',
        controlRisk: 'low',
        detectionRisk: 'medium',
        auditRisk: 'low',
        rationale: 'Established valuation methods with strong controls. Annual physical count with reconciliation.',
      },
      {
        area: 'Accounts Receivable',
        inherentRisk: 'medium',
        controlRisk: 'medium',
        detectionRisk: 'medium',
        auditRisk: 'medium',
        rationale: 'Aging showing some collectability concerns. Allowance estimation requires judgment.',
      },
      {
        area: 'Management Override',
        inherentRisk: 'high',
        controlRisk: 'high',
        detectionRisk: 'low',
        auditRisk: 'high',
        rationale: 'Presumed fraud risk per auditing standards. Requires unpredictable procedures and professional skepticism.',
      },
      {
        area: 'Payroll',
        inherentRisk: 'low',
        controlRisk: 'low',
        detectionRisk: 'high',
        auditRisk: 'low',
        rationale: 'Routine transactions with strong automated controls and segregation of duties.',
      },
    ];
  }

  private getDefaultFraudRisks(): FraudRisk[] {
    return [
      {
        type: 'Fraudulent Financial Reporting',
        risk: 'medium',
        factors: [
          'Pressure to meet earnings targets',
          'Complex revenue recognition',
          'Significant estimates and judgments',
        ],
        procedures: [
          'Test journal entries near year-end',
          'Review significant estimates for bias',
          'Test revenue recognition near period end',
        ],
      },
      {
        type: 'Misappropriation of Assets',
        risk: 'low',
        factors: [
          'Inventory susceptible to theft',
          'Cash handling at retail locations',
        ],
        procedures: [
          'Observe inventory counts',
          'Test cash reconciliations',
          'Review unusual transactions',
        ],
      },
      {
        type: 'Management Override',
        risk: 'high',
        factors: [
          'Presumed risk per AU-C 240',
          'Management has ability to override controls',
          'Bonus structure tied to performance',
        ],
        procedures: [
          'Test appropriateness of journal entries',
          'Review accounting estimates for bias',
          'Review unusual or one-time transactions',
        ],
      },
    ];
  }

  private getDefaultGoingConcernIndicators(): GoingConcernIndicator[] {
    return [
      { indicator: 'Negative working capital', present: false, impact: 'high' },
      { indicator: 'Recurring operating losses', present: false, impact: 'high' },
      { indicator: 'Negative cash flows from operations', present: false, impact: 'high' },
      { indicator: 'Debt covenant violations', present: false, impact: 'high' },
      { indicator: 'Loss of major customer', present: false, impact: 'medium' },
      { indicator: 'Legal proceedings', present: false, impact: 'low' },
      { indicator: 'Difficulty in paying obligations', present: false, impact: 'high' },
      { indicator: 'Need for major refinancing', present: false, impact: 'medium' },
    ];
  }
}

export const riskAssessmentService = new RiskAssessmentService();
export default riskAssessmentService;
