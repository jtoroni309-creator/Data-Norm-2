/**
 * Firm Management Service
 * API client for organization, user, and permission management
 */

import axios, { AxiosInstance } from 'axios';
import {
  Organization,
  OrganizationUpdate,
  FirmUser,
  UserInvitation,
  UserInvitationCreate,
  UserPermission,
  UserPermissionUpdate,
  FirmStats,
  ApiResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class FirmService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/identity`,
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

  // ========================================
  // Organization Management
  // ========================================

  async getOrganization(orgId: string): Promise<Organization> {
    const response = await this.api.get<Organization>(`/organizations/${orgId}`);
    return response.data;
  }

  async getMyOrganization(): Promise<Organization> {
    const response = await this.api.get<Organization>('/organizations/me/details');
    return response.data;
  }

  async updateOrganization(orgId: string, data: OrganizationUpdate): Promise<Organization> {
    const response = await this.api.patch<Organization>(`/organizations/${orgId}`, data);
    return response.data;
  }

  // ========================================
  // User Management
  // ========================================

  async listUsers(): Promise<FirmUser[]> {
    const response = await this.api.get<FirmUser[]>('/users');
    return response.data;
  }

  async updateUser(userId: string, data: { full_name?: string; role?: string; is_active?: boolean }): Promise<FirmUser> {
    const response = await this.api.patch<FirmUser>(`/users/${userId}`, data);
    return response.data;
  }

  async deactivateUser(userId: string): Promise<void> {
    await this.api.patch(`/users/${userId}/deactivate`);
  }

  // ========================================
  // User Invitations
  // ========================================

  async createInvitation(data: UserInvitationCreate): Promise<UserInvitation> {
    const response = await this.api.post<UserInvitation>('/invitations', data);
    return response.data;
  }

  async listInvitations(): Promise<UserInvitation[]> {
    const response = await this.api.get<UserInvitation[]>('/invitations');
    return response.data;
  }

  async acceptInvitation(token: string, fullName: string, password: string): Promise<{ access_token: string }> {
    const response = await this.api.post('/invitations/accept', {
      token,
      full_name: fullName,
      password
    });
    return response.data;
  }

  async resendInvitation(invitationId: string): Promise<UserInvitation> {
    const response = await this.api.post<UserInvitation>(`/invitations/${invitationId}/resend`);
    return response.data;
  }

  // ========================================
  // User Permissions
  // ========================================

  async getUserPermissions(userId: string): Promise<UserPermission> {
    const response = await this.api.get<UserPermission>(`/users/${userId}/permissions`);
    return response.data;
  }

  async updateUserPermissions(userId: string, data: UserPermissionUpdate): Promise<UserPermission> {
    const response = await this.api.patch<UserPermission>(`/users/${userId}/permissions`, data);
    return response.data;
  }

  // ========================================
  // File Upload (for logos)
  // ========================================

  async uploadLogo(file: File): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.api.post<{ url: string }>('/upload/logo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // ========================================
  // Statistics
  // ========================================

  async getFirmStats(): Promise<FirmStats> {
    // This would be a real endpoint, for now return mock data
    const users = await this.listUsers();
    const invitations = await this.listInvitations();

    return {
      total_employees: users.length,
      active_engagements: 0, // Would come from engagement service
      pending_invitations: invitations.filter(inv => !inv.is_expired && !inv.accepted_at).length,
      total_clients: 0, // Would come from client service
      documents_uploaded_this_month: 0, // Would come from document service
      active_integrations: 0, // Would come from integration service
    };
  }
}

// Export singleton instance
export const firmService = new FirmService();
export default firmService;
