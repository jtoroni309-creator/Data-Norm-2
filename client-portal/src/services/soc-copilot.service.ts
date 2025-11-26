/**
 * SOC Copilot Service
 * API client for SOC 1 & SOC 2 audit management
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface SOCEngagementCreate {
  client_name: string;
  service_description: string;
  engagement_type: 'SOC1' | 'SOC2';
  report_type: 'TYPE1' | 'TYPE2';
  tsc_categories?: ('SECURITY' | 'AVAILABILITY' | 'PROCESSING_INTEGRITY' | 'CONFIDENTIALITY' | 'PRIVACY')[];
  review_period_start?: string;
  review_period_end?: string;
  point_in_time_date?: string;
  partner_id: string;
  manager_id: string;
  fiscal_year_end?: string;
}

export interface SOCEngagement {
  id: string;
  client_name: string;
  service_description: string;
  engagement_type: 'SOC1' | 'SOC2';
  report_type: 'TYPE1' | 'TYPE2';
  status: 'DRAFT' | 'PLANNING' | 'FIELDWORK' | 'REVIEW' | 'PARTNER_REVIEW' | 'SIGNED' | 'RELEASED' | 'ARCHIVED';
  tsc_categories?: string[];
  review_period_start?: string;
  review_period_end?: string;
  point_in_time_date?: string;
  created_at: string;
  updated_at: string;
}

export interface ControlObjectiveCreate {
  objective_code: string;
  objective_name: string;
  objective_description: string;
  icfr_assertion?: string;
  tsc_category?: 'SECURITY' | 'AVAILABILITY' | 'PROCESSING_INTEGRITY' | 'CONFIDENTIALITY' | 'PRIVACY';
  tsc_criteria?: string;
  points_of_focus_2022?: string[];
}

export interface ControlCreate {
  objective_id: string;
  control_code: string;
  control_name: string;
  control_description: string;
  control_type: string;
  control_owner?: string;
  frequency?: string;
  automation_level?: string;
}

export interface TestPlanCreate {
  control_id: string;
  test_type: 'WALKTHROUGH' | 'DESIGN_EVALUATION' | 'OPERATING_EFFECTIVENESS';
  test_objective: string;
  test_procedures: string;
  sample_size?: number;
  sampling_method?: string;
  population_size?: number;
  required_evidence_types?: string[];
}

export interface TestResultCreate {
  test_plan_id: string;
  evidence_id?: string;
  test_date: string;
  passed?: boolean;
  findings?: string;
  conclusion?: string;
  sample_item_identifier?: string;
}

export interface ReportCreate {
  engagement_id: string;
  report_title: string;
  report_date: string;
}

class SOCCopilotService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/soc-copilot`,
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

  // Engagement Management
  async listEngagements(statusFilter?: string, engagementType?: string): Promise<SOCEngagement[]> {
    const params: any = {};
    if (statusFilter) params.status_filter = statusFilter;
    if (engagementType) params.engagement_type = engagementType;

    const response = await this.api.get<SOCEngagement[]>('/engagements', { params });
    return response.data;
  }

  async getEngagement(id: string): Promise<SOCEngagement> {
    const response = await this.api.get<SOCEngagement>(`/engagements/${id}`);
    return response.data;
  }

  async createEngagement(data: SOCEngagementCreate): Promise<SOCEngagement> {
    const response = await this.api.post<SOCEngagement>('/engagements', data);
    return response.data;
  }

  async transitionEngagementStatus(id: string, newStatus: string): Promise<any> {
    const response = await this.api.post(`/engagements/${id}/transition`, null, {
      params: { new_status: newStatus }
    });
    return response.data;
  }

  // Control Objectives & Controls
  async createControlObjective(engagementId: string, data: ControlObjectiveCreate): Promise<any> {
    const response = await this.api.post(`/engagements/${engagementId}/objectives`, data);
    return response.data;
  }

  async createControl(engagementId: string, data: ControlCreate): Promise<any> {
    const response = await this.api.post(`/engagements/${engagementId}/controls`, data);
    return response.data;
  }

  // Testing & Evidence
  async createTestPlan(engagementId: string, data: TestPlanCreate): Promise<any> {
    const response = await this.api.post(`/engagements/${engagementId}/test-plans`, data);
    return response.data;
  }

  async createTestResult(engagementId: string, data: TestResultCreate): Promise<any> {
    const response = await this.api.post(`/engagements/${engagementId}/test-results`, data);
    return response.data;
  }

  // Reports
  async createReport(engagementId: string, data: ReportCreate): Promise<any> {
    const response = await this.api.post(`/engagements/${engagementId}/reports`, data);
    return response.data;
  }

  // Audit Trail
  async getAuditTrail(engagementId: string, limit: number = 100, offset: number = 0): Promise<any[]> {
    const response = await this.api.get(`/engagements/${engagementId}/audit-trail`, {
      params: { limit, offset }
    });
    return response.data;
  }
}

// Export singleton instance
export const socCopilotService = new SOCCopilotService();
export default socCopilotService;
