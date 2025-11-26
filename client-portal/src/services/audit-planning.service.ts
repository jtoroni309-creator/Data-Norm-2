/**
 * Audit Planning Service
 * API client for audit planning, materiality, and risk assessment
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface MaterialityRequest {
  total_assets: number;
  total_revenue: number;
  pretax_income: number;
  total_equity: number;
  entity_type?: string;
}

export interface MaterialityResponse {
  overall_materiality: number;
  performance_materiality: number;
  trivial_threshold: number;
  benchmark_used: string;
  all_benchmarks: Record<string, number>;
}

export interface RiskAssessmentRequest {
  engagement_id: string;
  account_name: string;
  account_balance: number;
  assertion_type: string;
  factors?: Record<string, any>;
}

export interface RiskAssessmentResponse {
  inherent_risk: string;
  control_risk: string;
  detection_risk: number;
  audit_risk: string;
  recommendations: string[];
}

export interface AuditPlanRequest {
  engagement_id: string;
  fiscal_year_end: string;
  materiality_amount: number;
  risk_level: string;
}

export interface AuditPlan {
  id: string;
  engagement_id: string;
  plan_status: string;
  fiscal_year_end: string;
  overall_materiality: number;
  created_at: string;
}

export interface AuditProgram {
  engagement_id: string;
  audit_area: string;
  risk_level: string;
  procedures_count: number;
  procedures: Array<{
    step: number;
    description: string;
    procedure_type: string;
    sample_size?: number;
  }>;
}

class AuditPlanningService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/audit-planning`,
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

  async calculateMateriality(data: MaterialityRequest): Promise<MaterialityResponse> {
    const response = await this.api.post<MaterialityResponse>('/materiality/calculate', data);
    return response.data;
  }

  async assessRisk(data: RiskAssessmentRequest): Promise<RiskAssessmentResponse> {
    const response = await this.api.post<RiskAssessmentResponse>('/risk/assess', data);
    return response.data;
  }

  async createAuditPlan(data: AuditPlanRequest): Promise<AuditPlan> {
    const response = await this.api.post<AuditPlan>('/plans', data);
    return response.data;
  }

  async getAuditPlan(engagementId: string): Promise<AuditPlan> {
    const response = await this.api.get<AuditPlan>(`/plans/${engagementId}`);
    return response.data;
  }

  async generateAuditProgram(
    engagementId: string,
    area: string,
    riskLevel: string = 'moderate'
  ): Promise<AuditProgram> {
    const response = await this.api.post<AuditProgram>(
      `/programs/generate/${engagementId}`,
      null,
      {
        params: { area, risk_level: riskLevel }
      }
    );
    return response.data;
  }
}

// Export singleton instance
export const auditPlanningService = new AuditPlanningService();
export default auditPlanningService;
