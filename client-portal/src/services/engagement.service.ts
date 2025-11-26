/**
 * Engagement Service
 * API client for engagement management (audits)
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface Engagement {
  id: string;
  client_id: string;
  name: string;
  engagement_type: 'audit' | 'review' | 'compilation';
  status: 'draft' | 'planning' | 'fieldwork' | 'review' | 'finalized';
  fiscal_year_end: string;
  start_date?: string;
  expected_completion_date?: string;
  partner_id?: string;
  manager_id?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface EngagementCreate {
  client_id?: string;
  client_name?: string;
  name: string;
  engagement_type: 'audit' | 'review' | 'compilation';
  fiscal_year_end: string;
  start_date?: string;
  expected_completion_date?: string;
  partner_id?: string;
  manager_id?: string;
}

class EngagementService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/engagement`,
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

  async listEngagements(): Promise<Engagement[]> {
    const response = await this.api.get<Engagement[] | { engagements: Engagement[] }>('/engagements');
    // Handle both array response and object with engagements property
    if (Array.isArray(response.data)) {
      return response.data;
    }
    return response.data.engagements || [];
  }

  async getEngagement(id: string): Promise<Engagement> {
    const response = await this.api.get<Engagement>(`/engagements/${id}`);
    return response.data;
  }

  async createEngagement(data: EngagementCreate): Promise<Engagement> {
    // Clean up empty strings to avoid validation errors on the backend
    const cleanedData: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(data)) {
      cleanedData[key] = value === '' ? null : value;
    }
    const response = await this.api.post<Engagement>('/engagements', cleanedData);
    return response.data;
  }

  async updateEngagement(id: string, data: Partial<EngagementCreate>): Promise<Engagement> {
    const response = await this.api.patch<Engagement>(`/engagements/${id}`, data);
    return response.data;
  }

  async deleteEngagement(id: string): Promise<void> {
    await this.api.delete(`/engagements/${id}`);
  }

  async transitionStatus(id: string, newStatus: string, notes?: string): Promise<any> {
    const response = await this.api.post(`/engagements/${id}/transition`, {
      new_status: newStatus,
      notes
    });
    return response.data;
  }
}

// Export singleton instance
export const engagementService = new EngagementService();
export default engagementService;
