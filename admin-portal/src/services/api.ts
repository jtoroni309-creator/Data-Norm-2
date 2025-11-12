/**
 * Admin Portal API Service
 *
 * Centralized API calls to the backend financial-analysis service
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ============================================================================
// Types
// ============================================================================

export interface Tenant {
  id: string;
  firmName: string;
  firmEin: string;
  status: string;
  subscriptionTier: string;
  userCount: number;
  maxUsers: number;
  createdAt: string;
}

export interface UserListItem {
  id: string;
  email: string;
  firstName: string | null;
  lastName: string | null;
  role: string;
  tenantId: string | null;
  tenantName: string | null;
  isActive: boolean;
  emailVerified: boolean;
  lastLoginAt: string | null;
  createdAt: string;
}

export interface UserDetail {
  id: string;
  email: string;
  firstName: string | null;
  lastName: string | null;
  phone: string | null;
  role: string;
  tenantId: string | null;
  tenantName: string | null;
  isActive: boolean;
  emailVerified: boolean;
  emailVerifiedAt: string | null;
  twoFactorEnabled: boolean;
  lastLoginAt: string | null;
  lastLoginIp: string | null;
  failedLoginAttempts: number;
  cpaLicenseNumber: string | null;
  cpaLicenseState: string | null;
  professionalTitle: string | null;
  createdAt: string;
  updatedAt: string | null;
  createdBy: string | null;
}

export interface CreateUserRequest {
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  tenantId?: string;
  password?: string;
  cpaLicenseNumber?: string;
  cpaLicenseState?: string;
  professionalTitle?: string;
  sendInvitation?: boolean;
}

export interface UpdateUserRequest {
  firstName?: string;
  lastName?: string;
  role?: string;
  tenantId?: string;
  isActive?: boolean;
  cpaLicenseNumber?: string;
  cpaLicenseState?: string;
  professionalTitle?: string;
}

// ============================================================================
// Helper Functions
// ============================================================================

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('admin_token');

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// ============================================================================
// Tenant / CPA Firm APIs
// ============================================================================

export const tenantAPI = {
  /**
   * List all CPA firms (tenants)
   */
  async list(params?: {
    status?: string;
    search?: string;
    page?: number;
    pageSize?: number;
  }): Promise<Tenant[]> {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.search) queryParams.append('search', params.search);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.pageSize) queryParams.append('pageSize', params.pageSize.toString());

    return fetchAPI<Tenant[]>(
      `/api/admin/tenants?${queryParams.toString()}`
    );
  },
};

// ============================================================================
// User Management APIs
// ============================================================================

export const userAPI = {
  /**
   * List users with filtering
   */
  async list(params?: {
    tenantId?: string;
    role?: string;
    isActive?: boolean;
    search?: string;
    page?: number;
    pageSize?: number;
  }): Promise<UserListItem[]> {
    const queryParams = new URLSearchParams();
    if (params?.tenantId) queryParams.append('tenantId', params.tenantId);
    if (params?.role) queryParams.append('role', params.role);
    if (params?.isActive !== undefined) queryParams.append('isActive', params.isActive.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.pageSize) queryParams.append('pageSize', params.pageSize.toString());

    return fetchAPI<UserListItem[]>(
      `/api/admin/users?${queryParams.toString()}`
    );
  },

  /**
   * Get user details
   */
  async get(userId: string): Promise<UserDetail> {
    return fetchAPI<UserDetail>(`/api/admin/users/${userId}`);
  },

  /**
   * Create new user
   */
  async create(data: CreateUserRequest): Promise<UserDetail> {
    return fetchAPI<UserDetail>('/api/admin/users', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update user
   */
  async update(userId: string, data: UpdateUserRequest): Promise<UserDetail> {
    return fetchAPI<UserDetail>(`/api/admin/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Deactivate user (soft delete)
   */
  async deactivate(userId: string): Promise<void> {
    return fetchAPI<void>(`/api/admin/users/${userId}`, {
      method: 'DELETE',
    });
  },
};

// ============================================================================
// Authentication (Mock for now)
// ============================================================================

export const authAPI = {
  /**
   * Login as admin
   */
  async login(email: string, password: string): Promise<{ token: string; user: UserDetail }> {
    // Mock implementation - in production, call real auth endpoint
    const mockToken = 'mock-admin-token-' + Date.now();
    localStorage.setItem('admin_token', mockToken);

    return {
      token: mockToken,
      user: {
        id: '1',
        email,
        firstName: 'Admin',
        lastName: 'User',
        phone: null,
        role: 'platform_admin',
        tenantId: null,
        tenantName: null,
        isActive: true,
        emailVerified: true,
        emailVerifiedAt: new Date().toISOString(),
        twoFactorEnabled: false,
        lastLoginAt: new Date().toISOString(),
        lastLoginIp: '127.0.0.1',
        failedLoginAttempts: 0,
        cpaLicenseNumber: null,
        cpaLicenseState: null,
        professionalTitle: 'Platform Administrator',
        createdAt: new Date().toISOString(),
        updatedAt: null,
        createdBy: null,
      },
    };
  },

  /**
   * Logout
   */
  async logout(): Promise<void> {
    localStorage.removeItem('admin_token');
  },
};
