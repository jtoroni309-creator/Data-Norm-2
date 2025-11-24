/**
 * Admin Portal API Service
 *
 * Centralized API calls to the backend identity service
 */

const IDENTITY_API_URL = import.meta.env.VITE_IDENTITY_API_URL || 'http://identity.aura-audit-ai.svc.cluster.local:8000';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || IDENTITY_API_URL;

// ============================================================================
// Types
// ============================================================================

export interface Tenant {
  id: string;
  firm_name: string;
  legal_name?: string | null;
  ein?: string | null;
  primary_contact_name?: string | null;
  primary_contact_email: string;
  primary_contact_phone?: string | null;
  logo_url?: string | null;
  primary_color?: string | null;
  secondary_color?: string | null;
  require_two_factor_auth: boolean;
  session_timeout_minutes?: string | null;
  subscription_tier: string;
  subscription_status: string;
  max_users: number;
  enabled_services?: Record<string, boolean> | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTenantRequest {
  firm_name: string;
  legal_name?: string;
  ein?: string;
  primary_contact_name?: string;
  primary_contact_email: string;
  primary_contact_phone?: string;
  subscription_tier?: string;
  subscription_status?: string;
  max_users?: number;
}

export interface UpdateTenantRequest {
  firm_name?: string;
  legal_name?: string;
  ein?: string;
  primary_contact_name?: string;
  primary_contact_email?: string;
  primary_contact_phone?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  require_two_factor_auth?: boolean;
  session_timeout_minutes?: string;
  subscription_tier?: string;
  subscription_status?: string;
  max_users?: number;
  enabled_services?: Record<string, boolean>;
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
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<Tenant[]> {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append('search', params.search);
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const query = queryParams.toString();
    return fetchAPI<Tenant[]>(
      `/admin/organizations${query ? '?' + query : ''}`
    );
  },

  /**
   * Get a single CPA firm
   */
  async get(id: string): Promise<Tenant> {
    return fetchAPI<Tenant>(`/admin/organizations/${id}`);
  },

  /**
   * Create a new CPA firm
   */
  async create(data: CreateTenantRequest): Promise<Tenant> {
    return fetchAPI<Tenant>('/admin/organizations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update a CPA firm
   */
  async update(id: string, data: UpdateTenantRequest): Promise<Tenant> {
    return fetchAPI<Tenant>(`/admin/organizations/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a CPA firm
   */
  async delete(id: string): Promise<void> {
    return fetchAPI<void>(`/admin/organizations/${id}`, {
      method: 'DELETE',
    });
  },

  /**
   * Update enabled services for a CPA firm
   */
  async updateServices(id: string, services: Record<string, boolean>): Promise<Tenant> {
    return fetchAPI<Tenant>(`/admin/organizations/${id}/services`, {
      method: 'PATCH',
      body: JSON.stringify(services),
    });
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
// Authentication
// ============================================================================

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    full_name: string | null;
    role: string;
    organization_id: string | null;
    is_active: boolean;
    email_verified: boolean;
    email_verified_at: string | null;
    two_factor_enabled: boolean;
    last_login_at: string | null;
    created_at: string;
    updated_at: string | null;
  };
}

export const authAPI = {
  /**
   * Login as admin
   */
  async login(email: string, password: string): Promise<{ token: string; user: UserDetail }> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Invalid email or password');
    }

    const data: LoginResponse = await response.json();

    // Store token
    localStorage.setItem('admin_token', data.access_token);

    // Map backend user format to frontend UserDetail format
    const nameParts = (data.user.full_name || '').split(' ');
    const user: UserDetail = {
      id: data.user.id,
      email: data.user.email,
      firstName: nameParts[0] || null,
      lastName: nameParts.slice(1).join(' ') || null,
      phone: null,
      role: data.user.role,
      tenantId: data.user.organization_id,
      tenantName: null,
      isActive: data.user.is_active,
      emailVerified: data.user.email_verified,
      emailVerifiedAt: data.user.email_verified_at,
      twoFactorEnabled: data.user.two_factor_enabled,
      lastLoginAt: data.user.last_login_at,
      lastLoginIp: null,
      failedLoginAttempts: 0,
      cpaLicenseNumber: null,
      cpaLicenseState: null,
      professionalTitle: null,
      createdAt: data.user.created_at,
      updatedAt: data.user.updated_at,
      createdBy: null,
    };

    return {
      token: data.access_token,
      user,
    };
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<UserDetail> {
    return fetchAPI<UserDetail>('/auth/me');
  },

  /**
   * Logout
   */
  async logout(): Promise<void> {
    localStorage.removeItem('admin_token');
  },
};
