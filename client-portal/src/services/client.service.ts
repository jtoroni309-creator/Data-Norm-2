/**
 * Client Management Service
 * API client for managing audit clients
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface Client {
  id: string;
  organization_id: string;
  name: string;
  ein?: string;
  industry?: string;
  address?: string;
  phone?: string;
  email?: string;
  primary_contact_name?: string;
  primary_contact_email?: string;
  primary_contact_phone?: string;
  status: 'active' | 'inactive' | 'prospect';
  fiscal_year_end?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ClientCreate {
  name: string;
  ein?: string;
  industry?: string;
  address?: string;
  phone?: string;
  email?: string;
  primary_contact_name?: string;
  primary_contact_email?: string;
  primary_contact_phone?: string;
  status?: 'active' | 'inactive' | 'prospect';
  fiscal_year_end?: string;
  notes?: string;
}

export interface ClientUpdate {
  name?: string;
  ein?: string;
  industry?: string;
  address?: string;
  phone?: string;
  email?: string;
  primary_contact_name?: string;
  primary_contact_email?: string;
  primary_contact_phone?: string;
  status?: 'active' | 'inactive' | 'prospect';
  fiscal_year_end?: string;
  notes?: string;
}

class ClientService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/clients`,
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

  async listClients(): Promise<Client[]> {
    const response = await this.api.get<{ clients: Client[] } | Client[]>('');
    // Handle both formats: {clients: [...]} and plain array
    if (Array.isArray(response.data)) {
      return response.data;
    }
    return response.data.clients || [];
  }

  async getClient(id: string): Promise<Client> {
    const response = await this.api.get<Client>(`/${id}`);
    return response.data;
  }

  async createClient(data: ClientCreate): Promise<Client> {
    // Clean up empty strings to avoid validation errors on the backend
    const cleanedData: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(data)) {
      cleanedData[key] = value === '' ? null : value;
    }
    const response = await this.api.post<Client>('', cleanedData);
    return response.data;
  }

  async updateClient(id: string, data: ClientUpdate): Promise<Client> {
    // Clean up empty strings to avoid validation errors on the backend
    const cleanedData: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(data)) {
      cleanedData[key] = value === '' ? null : value;
    }
    const response = await this.api.patch<Client>(`/${id}`, cleanedData);
    return response.data;
  }

  async deleteClient(id: string): Promise<void> {
    await this.api.delete(`/${id}`);
  }

  async getClientEngagements(clientId: string): Promise<any[]> {
    const response = await this.api.get(`/${clientId}/engagements`);
    return response.data.engagements || [];
  }
}

// Export singleton instance
export const clientService = new ClientService();
export default clientService;
