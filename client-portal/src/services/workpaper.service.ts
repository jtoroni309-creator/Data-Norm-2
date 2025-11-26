/**
 * Workpaper Service
 * API client for workpaper management
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface Workpaper {
  id: string;
  engagement_id: string;
  reference: string;
  title: string;
  section: string;
  preparer_id: string;
  reviewer_id?: string;
  status: 'not_started' | 'in_progress' | 'review' | 'completed';
  procedure?: string;
  results?: string;
  conclusion?: string;
  created_at: string;
  updated_at: string;
  attachments?: string[];
  cross_references?: string[];
}

export interface WorkpaperCreate {
  engagement_id: string;
  reference: string;
  title: string;
  section: string;
  procedure?: string;
  preparer_id?: string;
}

class WorkpaperService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/workpapers`,
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

  async listWorkpapers(engagementId: string): Promise<Workpaper[]> {
    const response = await this.api.get<{ workpapers: Workpaper[] }>(`/engagement/${engagementId}`);
    return response.data.workpapers || [];
  }

  async getWorkpaper(id: string): Promise<Workpaper> {
    const response = await this.api.get<Workpaper>(`/${id}`);
    return response.data;
  }

  async createWorkpaper(data: WorkpaperCreate): Promise<Workpaper> {
    const response = await this.api.post<Workpaper>('/', data);
    return response.data;
  }

  async updateWorkpaper(id: string, data: Partial<Workpaper>): Promise<Workpaper> {
    const response = await this.api.patch<Workpaper>(`/${id}`, data);
    return response.data;
  }

  async deleteWorkpaper(id: string): Promise<void> {
    await this.api.delete(`/${id}`);
  }

  async addAttachment(id: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.api.post(`/${id}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async signOff(id: string, role: 'preparer' | 'reviewer'): Promise<any> {
    const response = await this.api.post(`/${id}/signoff`, { role });
    return response.data;
  }
}

// Export singleton instance
export const workpaperService = new WorkpaperService();
export default workpaperService;
