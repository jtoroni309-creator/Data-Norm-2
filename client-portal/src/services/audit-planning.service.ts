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

// AI-Powered Planning Interfaces
export interface AIRiskAnalysisRequest {
  engagement_id: string;
  client_name: string;
  industry: string;
  financial_data: Record<string, any>;
  prior_year_data?: Record<string, any>;
  known_issues?: string[];
}

export interface AIRiskAnalysisResponse {
  engagement_id: string;
  client_name: string;
  industry: string;
  analysis_timestamp: string;
  overall_risk_score: number;
  risk_level: string;
  financial_ratios: Record<string, number>;
  industry_comparison: {
    benchmarks: Record<string, any>;
    anomalies: Array<{
      ratio: string;
      value: number;
      severity: string;
      description: string;
    }>;
    percentile_rankings: Record<string, number>;
  };
  fraud_risk_assessment: {
    indicators: Array<{
      type: string;
      severity: string;
      description: string;
      audit_implication: string;
    }>;
    fraud_risk_level: string;
    recommended_fraud_procedures: string[];
  };
  significant_accounts: Array<{
    account: string;
    balance: number;
    account_type: string;
    times_materiality: number;
    requires_testing: boolean;
  }>;
  ai_insights: Array<{
    insight: string;
    severity: string;
    action: string;
    pcaob_reference: string;
  }>;
  recommended_focus_areas: Array<{
    area: string;
    reason: string;
    priority: string;
  }>;
  pcaob_compliance: {
    as_2110_addressed: boolean;
    as_2301_addressed: boolean;
    as_2401_addressed: boolean;
    significant_risks_identified: boolean;
  };
}

export interface AIAuditProgramRequest {
  engagement_id: string;
  risk_assessment: Record<string, any>;
  audit_area: string;
  account_balance: number;
  materiality: number;
  prior_year_findings?: string[];
}

export interface AIAuditProgramResponse {
  engagement_id: string;
  audit_area: string;
  risk_level: string;
  account_balance: number;
  materiality: number;
  procedures: Array<{
    sequence?: number;
    name: string;
    description: string;
    nature: string;
    extent?: string;
    sample_guidance?: string;
    timing?: string;
    ai_capability?: string;
    human_time_saved?: string;
    accuracy_improvement?: string;
    priority_score?: number;
  }>;
  sample_sizes: {
    recommended_sample_size: number;
    confidence_level: number;
    tolerable_misstatement: number;
    population_size: number;
    sampling_method: string;
    high_value_items: number;
  };
  estimated_hours: {
    total_estimated_hours: number;
    traditional_hours: number;
    ai_time_savings: number;
    efficiency_gain_percentage: number;
  };
  ai_efficiency_gain: {
    ai_procedures: number;
    total_procedures: number;
    ai_coverage_percentage: number;
    average_time_saved: string;
    average_accuracy_improvement: string;
  };
  program_summary: string;
  prior_year_considerations: string[];
  generated_at: string;
}

export interface AIMaterialityRequest {
  financial_data: Record<string, any>;
  industry: string;
  entity_type?: string;
  risk_factors?: string[];
  user_count?: number;
}

export interface AIMaterialityResponse {
  overall_materiality: number;
  performance_materiality: number;
  trivial_threshold: number;
  selected_benchmark: string;
  benchmark_value: number;
  risk_adjustment_factor: number;
  all_benchmarks: Record<string, number>;
  ai_reasoning: string;
  qualitative_factors: string[];
  industry_considerations: string[];
  sensitivity_analysis: Array<{
    benchmark: string;
    base_value: number;
    risk_adjusted: number;
    conservative: number;
    aggressive: number;
  }>;
  pcaob_compliance_notes: string[];
}

export interface AIFraudDetectionRequest {
  engagement_id: string;
  financial_data: Record<string, any>;
  transaction_data?: Array<Record<string, any>>;
  journal_entries?: Array<Record<string, any>>;
}

export interface AIFraudDetectionResponse {
  engagement_id: string;
  analysis_timestamp: string;
  fraud_risk_score: number;
  fraud_risk_level: string;
  indicators_found: number;
  fraud_indicators: Array<{
    type: string;
    severity: string;
    description: string;
    audit_implication?: string;
    details?: any;
  }>;
  recommendations: string[];
  required_procedures: string[];
  pcaob_as_2401_compliance: {
    fraud_triangle_assessed: boolean;
    journal_entry_testing_planned: boolean;
    management_override_considered: boolean;
    revenue_recognition_evaluated: boolean;
  };
}

export interface AIPlanningMemoRequest {
  engagement_id: string;
  client_name: string;
  risk_assessment: Record<string, any>;
  materiality: Record<string, any>;
  fraud_assessment: Record<string, any>;
  audit_programs: Array<Record<string, any>>;
}

export interface AIPlanningMemoResponse {
  engagement_id: string;
  client_name: string;
  memo_type: string;
  generated_at: string;
  content: string;
  sections: string[];
  pcaob_references: string[];
  ai_generated: boolean;
  requires_partner_review: boolean;
}

export interface AICapabilities {
  service: string;
  version: string;
  capabilities: Array<{
    name: string;
    endpoint: string;
    description: string;
    advantages: string[];
  }>;
  pcaob_compliance: Record<string, string>;
  efficiency_gains: Record<string, string>;
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

  // ==================== AI-Powered Planning Methods ====================

  /**
   * AI-Powered Engagement Risk Analysis
   * Performs comprehensive risk analysis with pattern recognition, fraud detection,
   * and industry benchmarking that exceeds human CPA capabilities.
   */
  async analyzeRiskWithAI(data: AIRiskAnalysisRequest): Promise<AIRiskAnalysisResponse> {
    const response = await this.api.post<AIRiskAnalysisResponse>('/ai/analyze-risk', data);
    return response.data;
  }

  /**
   * AI-Generated Intelligent Audit Program
   * Creates tailored audit procedures with AI-enhanced testing, optimized sample sizes,
   * and prioritized procedures by expected audit value.
   */
  async generateAuditProgramWithAI(data: AIAuditProgramRequest): Promise<AIAuditProgramResponse> {
    const response = await this.api.post<AIAuditProgramResponse>('/ai/generate-program', data);
    return response.data;
  }

  /**
   * AI-Powered Intelligent Materiality Recommendation
   * Calculates materiality with multiple benchmarks, industry adjustments,
   * risk factor optimization, and sensitivity analysis.
   */
  async calculateMaterialityWithAI(data: AIMaterialityRequest): Promise<AIMaterialityResponse> {
    const response = await this.api.post<AIMaterialityResponse>('/ai/materiality', data);
    return response.data;
  }

  /**
   * AI-Powered Fraud Pattern Detection
   * Uses Benford's Law, journal entry analysis, and transaction anomaly detection
   * to identify fraud indicators at scale.
   */
  async detectFraudWithAI(data: AIFraudDetectionRequest): Promise<AIFraudDetectionResponse> {
    const response = await this.api.post<AIFraudDetectionResponse>('/ai/detect-fraud', data);
    return response.data;
  }

  /**
   * AI-Generated Comprehensive Planning Memorandum
   * Creates PCAOB-compliant planning documentation with executive summary,
   * risk assessment, materiality, and fraud evaluation.
   */
  async generatePlanningMemoWithAI(data: AIPlanningMemoRequest): Promise<AIPlanningMemoResponse> {
    const response = await this.api.post<AIPlanningMemoResponse>('/ai/planning-memo', data);
    return response.data;
  }

  /**
   * Get AI Planning Service Capabilities
   * Returns information about available AI-powered features and their advantages.
   */
  async getAICapabilities(): Promise<AICapabilities> {
    const response = await this.api.get<AICapabilities>('/ai/capabilities');
    return response.data;
  }
}

// Export singleton instance
export const auditPlanningService = new AuditPlanningService();
export default auditPlanningService;
