/**
 * R&D Study Automation Service
 * API client for R&D tax credit study management
 */

import axios, { AxiosInstance } from 'axios';
import {
  RDStudy,
  RDStudySummary,
  RDStudyCreate,
  RDProject,
  RDEmployee,
  RDQRE,
  RDCalculationResult,
  RDReviewItem,
  RDStudyStatus
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class RDStudyService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/rd-study`,
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

    // Handle errors gracefully - don't force logout on 401 from this service
    // The main auth service handles session management; this service should
    // just propagate errors and let the UI fall back to demo mode
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        // Log error for debugging but don't force logout
        console.warn('RD Study API error:', error.response?.status, error.message);
        return Promise.reject(error);
      }
    );
  }

  // ========================================
  // Study Management
  // ========================================

  async listStudies(params?: {
    client_id?: string;
    status?: RDStudyStatus;
    tax_year?: number;
    page?: number;
    page_size?: number;
  }): Promise<{ items: RDStudySummary[]; total: number; pages: number }> {
    const response = await this.api.get('/studies', { params });
    return response.data;
  }

  async getStudy(studyId: string): Promise<RDStudy> {
    const response = await this.api.get<RDStudy>(`/studies/${studyId}`);
    return response.data;
  }

  async createStudy(data: RDStudyCreate): Promise<RDStudy> {
    const response = await this.api.post<RDStudy>('/studies', data);
    return response.data;
  }

  async updateStudy(studyId: string, data: Partial<RDStudy>): Promise<RDStudy> {
    const response = await this.api.patch<RDStudy>(`/studies/${studyId}`, data);
    return response.data;
  }

  async transitionStudy(studyId: string, newStatus: RDStudyStatus, notes?: string): Promise<RDStudy> {
    const response = await this.api.post<RDStudy>(`/studies/${studyId}/transition`, {
      new_status: newStatus,
      notes
    });
    return response.data;
  }

  async approveStudy(studyId: string, approved: boolean, notes?: string): Promise<RDStudy> {
    const response = await this.api.post<RDStudy>(`/studies/${studyId}/cpa-approval`, {
      approved,
      notes
    });
    return response.data;
  }

  // ========================================
  // Project Management
  // ========================================

  async listProjects(studyId: string): Promise<RDProject[]> {
    const response = await this.api.get<RDProject[]>(`/studies/${studyId}/projects`);
    return response.data;
  }

  async getProject(studyId: string, projectId: string): Promise<RDProject> {
    const response = await this.api.get<RDProject>(`/studies/${studyId}/projects/${projectId}`);
    return response.data;
  }

  async createProject(studyId: string, data: Partial<RDProject>): Promise<RDProject> {
    const response = await this.api.post<RDProject>(`/studies/${studyId}/projects`, data);
    return response.data;
  }

  async qualifyProject(studyId: string, projectId: string): Promise<RDProject> {
    const response = await this.api.post<RDProject>(`/studies/${studyId}/projects/${projectId}/qualify`);
    return response.data;
  }

  async overrideProjectQualification(
    studyId: string,
    projectId: string,
    status: string,
    reason: string
  ): Promise<RDProject> {
    const response = await this.api.post<RDProject>(`/studies/${studyId}/projects/${projectId}/override`, {
      override_status: status,
      reason
    });
    return response.data;
  }

  // ========================================
  // Employee Management
  // ========================================

  async listEmployees(studyId: string): Promise<RDEmployee[]> {
    const response = await this.api.get<RDEmployee[]>(`/studies/${studyId}/employees`);
    return response.data;
  }

  async createEmployee(studyId: string, data: Partial<RDEmployee>): Promise<RDEmployee> {
    const response = await this.api.post<RDEmployee>(`/studies/${studyId}/employees`, data);
    return response.data;
  }

  async adjustEmployeeTime(
    studyId: string,
    employeeId: string,
    adjustedPercentage: number,
    reason: string
  ): Promise<RDEmployee> {
    const response = await this.api.post<RDEmployee>(
      `/studies/${studyId}/employees/${employeeId}/adjust-time`,
      { adjusted_percentage: adjustedPercentage, reason }
    );
    return response.data;
  }

  async updateEmployee(studyId: string, employeeId: string, data: Partial<RDEmployee>): Promise<RDEmployee> {
    const response = await this.api.patch<RDEmployee>(`/studies/${studyId}/employees/${employeeId}`, data);
    return response.data;
  }

  // ========================================
  // QRE Management
  // ========================================

  async listQREs(studyId: string): Promise<RDQRE[]> {
    const response = await this.api.get<RDQRE[]>(`/studies/${studyId}/qres`);
    return response.data;
  }

  async getQRESummary(studyId: string): Promise<{
    by_category: Record<string, { count: number; gross: number; qualified: number }>;
    total_gross: number;
    total_qualified: number;
  }> {
    const response = await this.api.get(`/studies/${studyId}/qres/summary`);
    return response.data;
  }

  async createQRE(studyId: string, data: Partial<RDQRE>): Promise<RDQRE> {
    const response = await this.api.post<RDQRE>(`/studies/${studyId}/qres`, data);
    return response.data;
  }

  // ========================================
  // Calculations
  // ========================================

  async calculateCredits(studyId: string, method?: string): Promise<RDCalculationResult> {
    const response = await this.api.post<RDCalculationResult>(`/studies/${studyId}/calculate`, {
      method,
      include_states: true
    });
    return response.data;
  }

  async getForm6765Data(studyId: string): Promise<Record<string, unknown>> {
    const response = await this.api.get(`/studies/${studyId}/form-6765-data`);
    return response.data;
  }

  // ========================================
  // Documents
  // ========================================

  async uploadDocument(studyId: string, file: File, documentType?: string): Promise<{ id: string; filename: string }> {
    const formData = new FormData();
    formData.append('file', file);
    if (documentType) {
      formData.append('document_type', documentType);
    }

    const response = await this.api.post(`/studies/${studyId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  async listDocuments(studyId: string): Promise<Array<{
    id: string;
    filename: string;
    document_type: string;
    processing_status: string;
    uploaded_at: string;
  }>> {
    const response = await this.api.get(`/studies/${studyId}/documents`);
    return response.data;
  }

  // ========================================
  // Narratives
  // ========================================

  async generateNarratives(studyId: string, types: string[]): Promise<{ narratives_generated: number }> {
    const response = await this.api.post(`/studies/${studyId}/narratives/generate`, {
      narrative_types: types
    });
    return response.data;
  }

  async listNarratives(studyId: string): Promise<Array<{
    id: string;
    narrative_type: string;
    title: string;
    content: string;
    ai_generated: boolean;
    cpa_edited: boolean;
  }>> {
    const response = await this.api.get(`/studies/${studyId}/narratives`);
    return response.data;
  }

  async updateNarrative(studyId: string, narrativeId: string, content: string, reason?: string): Promise<void> {
    await this.api.patch(`/studies/${studyId}/narratives/${narrativeId}`, {
      content,
      edit_reason: reason
    });
  }

  // ========================================
  // Review Queue
  // ========================================

  async getReviewQueue(studyId: string): Promise<{
    total_items: number;
    reviewed_items: number;
    pending_items: number;
    high_priority_items: number;
    items: RDReviewItem[];
  }> {
    const response = await this.api.get(`/studies/${studyId}/review-queue`);
    return response.data;
  }

  // ========================================
  // Output Generation
  // ========================================

  async generateOutputs(studyId: string, types: string[]): Promise<{ files_generated: number }> {
    const response = await this.api.post(`/studies/${studyId}/outputs/generate`, {
      output_types: types
    });
    return response.data;
  }

  async listOutputs(studyId: string): Promise<Array<{
    id: string;
    file_type: string;
    filename: string;
    is_final: boolean;
    download_url: string;
    generated_at: string;
  }>> {
    const response = await this.api.get(`/studies/${studyId}/outputs`);
    return response.data;
  }

  // ========================================
  // Audit Trail
  // ========================================

  async getAuditTrail(studyId: string, params?: {
    entity_type?: string;
    action?: string;
    page?: number;
  }): Promise<Array<{
    id: string;
    action: string;
    entity_type: string;
    change_summary: string;
    user_email: string;
    created_at: string;
  }>> {
    const response = await this.api.get(`/studies/${studyId}/audit-trail`, { params });
    return response.data;
  }

  // ========================================
  // Rules & Reference Data
  // ========================================

  async getFederalRules(): Promise<{
    regular_rate: number;
    asc_rate: number;
    base_period_years: number;
  }> {
    const response = await this.api.get('/rules/federal');
    return response.data;
  }

  async getStateRules(stateCode?: string): Promise<Array<{
    state_code: string;
    state_name: string;
    has_rd_credit: boolean;
    credit_rate: number;
  }>> {
    const url = stateCode ? `/rules/states/${stateCode}` : '/rules/states';
    const response = await this.api.get(url);
    return response.data;
  }
}

// Export singleton instance
export const rdStudyService = new RDStudyService();
export default rdStudyService;
