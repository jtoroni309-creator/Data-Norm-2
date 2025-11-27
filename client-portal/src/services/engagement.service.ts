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

  async getEngagementTeam(id: string): Promise<any[]> {
    try {
      const response = await this.api.get(`/engagements/${id}/team`);
      return response.data.team || response.data || [];
    } catch (error) {
      console.log('Team endpoint not available');
      return [];
    }
  }

  async addTeamMember(engagementId: string, userId: string, role: string): Promise<any> {
    const response = await this.api.post(`/engagements/${engagementId}/team`, {
      user_id: userId,
      role
    });
    return response.data;
  }

  async getBinderTree(engagementId: string): Promise<any[]> {
    try {
      const response = await this.api.get(`/engagements/${engagementId}/binder/tree`);
      return response.data || [];
    } catch (error) {
      console.log('Binder tree not available');
      return [];
    }
  }

  async getWorkspaceStats(engagementId: string): Promise<WorkspaceStats> {
    try {
      // Fetch binder tree to count workpapers
      const binderTree = await this.getBinderTree(engagementId);

      // Count workpapers from binder tree
      const countWorkpapers = (nodes: any[]): { total: number; completed: number } => {
        let total = 0;
        let completed = 0;
        for (const node of nodes) {
          if (node.node_type === 'workpaper') {
            total++;
            if (node.status === 'completed' || node.status === 'reviewed' || node.status === 'signed_off') {
              completed++;
            }
          }
          if (node.children && node.children.length > 0) {
            const childStats = countWorkpapers(node.children);
            total += childStats.total;
            completed += childStats.completed;
          }
        }
        return { total, completed };
      };

      const workpaperStats = countWorkpapers(binderTree);

      // Try to fetch document stats from documents service
      let documentStats = { total: 0, completed: 0 };
      try {
        const docResponse = await fetch(`/api/documents/engagements/${engagementId}/stats`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (docResponse.ok) {
          const docData = await docResponse.json();
          documentStats = {
            total: docData.total_documents || 0,
            completed: docData.processed_documents || docData.total_documents || 0
          };
        }
      } catch (e) {
        console.log('Document stats not available');
      }

      // Try to fetch analytics/testing stats
      let analyticsStats = { total: 0, completed: 0 };
      let testingStats = { total: 0, completed: 0 };
      let riskStats = { total: 0, completed: 0 };
      let reportStats = { total: 0, completed: 0 };

      try {
        const analyticsResponse = await fetch(`/api/financial-analysis/engagements/${engagementId}/stats`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (analyticsResponse.ok) {
          const data = await analyticsResponse.json();
          analyticsStats = { total: data.total_procedures || 0, completed: data.completed_procedures || 0 };
        }
      } catch (e) {
        console.log('Analytics stats not available');
      }

      try {
        const testingResponse = await fetch(`/api/substantive-testing/engagements/${engagementId}/stats`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (testingResponse.ok) {
          const data = await testingResponse.json();
          testingStats = { total: data.total_tests || 0, completed: data.completed_tests || 0 };
        }
      } catch (e) {
        console.log('Testing stats not available');
      }

      try {
        const riskResponse = await fetch(`/api/risk-monitor/engagements/${engagementId}/stats`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (riskResponse.ok) {
          const data = await riskResponse.json();
          riskStats = { total: data.total_assessments || 0, completed: data.completed_assessments || 0 };
        }
      } catch (e) {
        console.log('Risk stats not available');
      }

      try {
        const reportResponse = await fetch(`/api/reporting/engagements/${engagementId}/stats`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (reportResponse.ok) {
          const data = await reportResponse.json();
          reportStats = { total: data.total_reports || 0, completed: data.completed_reports || 0 };
        }
      } catch (e) {
        console.log('Report stats not available');
      }

      return {
        workpapers: workpaperStats,
        analytics: analyticsStats,
        testing: testingStats,
        risk: riskStats,
        documents: documentStats,
        reports: reportStats
      };
    } catch (error) {
      console.error('Failed to fetch workspace stats:', error);
      // Return empty stats - this is production behavior when no data exists
      return {
        workpapers: { total: 0, completed: 0 },
        analytics: { total: 0, completed: 0 },
        testing: { total: 0, completed: 0 },
        risk: { total: 0, completed: 0 },
        documents: { total: 0, completed: 0 },
        reports: { total: 0, completed: 0 }
      };
    }
  }
}

export interface WorkspaceStats {
  workpapers: { total: number; completed: number };
  analytics: { total: number; completed: number };
  testing: { total: number; completed: number };
  risk: { total: number; completed: number };
  documents: { total: number; completed: number };
  reports: { total: number; completed: number };
}

// Export singleton instance
export const engagementService = new EngagementService();
export default engagementService;
