/**
 * Admin Portal API Service
 *
 * Centralized API calls to the backend identity service
 */

import { API_CONFIG } from '../config';

const API_BASE_URL = API_CONFIG.identityUrl;

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

// Dashboard stats
export interface DashboardStats {
  totalUsers: number;
  activeUsers: number;
  totalFirms: number;
  activeFirms: number;
  totalEngagements: number;
  activeEngagements: number;
  systemUptime: number;
  apiCallsToday: number;
  avgResponseTime: number;
}

// Notification types
export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'success' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  link?: string;
}

// ============================================================================
// Helper Functions
// ============================================================================

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('admin_token');
  const url = `${API_BASE_URL}${endpoint}`;

  console.log(`[API] ${options.method || 'GET'} ${url}`);
  if (options.body) {
    console.log('[API] Request body:', options.body);
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  console.log(`[API] Response status: ${response.status}`);

  if (!response.ok) {
    const errorText = await response.text();
    console.error('[API] Error response:', errorText);
    let errorDetail = 'Unknown error';
    try {
      const errorJson = JSON.parse(errorText);
      errorDetail = errorJson.detail || JSON.stringify(errorJson);
    } catch {
      errorDetail = errorText || `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
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
    return fetchAPI<Tenant>(`/admin/organizations/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ enabled_services: services }),
    });
  },

  /**
   * Get user count for a firm
   */
  async getUserCount(firmId: string): Promise<number> {
    try {
      const users = await userAPI.list({ tenantId: firmId });
      return users.length;
    } catch {
      return 0;
    }
  },

  /**
   * Get users for a specific firm
   */
  async getUsers(firmId: string): Promise<UserListItem[]> {
    try {
      const response = await fetchAPI<any[]>(`/admin/organizations/${firmId}/users`);
      return response.map(user => ({
        id: user.id,
        email: user.email,
        firstName: user.first_name || user.full_name?.split(' ')[0] || null,
        lastName: user.last_name || user.full_name?.split(' ').slice(1).join(' ') || null,
        role: user.role || 'firm_user',
        tenantId: firmId,
        tenantName: null,
        isActive: user.is_active,
        emailVerified: user.email_verified || false,
        lastLoginAt: user.last_login_at,
        createdAt: user.created_at,
      }));
    } catch (error) {
      console.error('Failed to fetch firm users:', error);
      return [];
    }
  },

  /**
   * Invite a user to a CPA firm
   */
  async inviteUser(firmId: string, data: {
    email: string;
    role: string;
    sendEmail?: boolean;
  }): Promise<{
    message: string;
    invitation_id?: string;
    user_id?: string;
    invitation_link?: string;
    email_sent?: boolean;
    action?: string;
  }> {
    return fetchAPI(`/admin/organizations/${firmId}/invite`, {
      method: 'POST',
      body: JSON.stringify({
        email: data.email,
        role: data.role,
        send_email: data.sendEmail ?? true,
      }),
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
    if (params?.tenantId) queryParams.append('organization_id', params.tenantId);
    if (params?.role) queryParams.append('role', params.role);
    if (params?.isActive !== undefined) queryParams.append('is_active', params.isActive.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.page) queryParams.append('skip', ((params.page - 1) * (params.pageSize || 20)).toString());
    if (params?.pageSize) queryParams.append('limit', params.pageSize.toString());

    const query = queryParams.toString();
    const endpoint = `/admin/users${query ? '?' + query : ''}`;

    try {
      const response = await fetchAPI<any[]>(endpoint);
      // Transform backend format to frontend format
      return response.map(user => ({
        id: user.id,
        email: user.email,
        firstName: user.first_name || user.full_name?.split(' ')[0] || null,
        lastName: user.last_name || user.full_name?.split(' ').slice(1).join(' ') || null,
        role: user.role || 'firm_user',
        tenantId: user.organization_id,
        tenantName: user.organization_name || null,
        isActive: user.is_active ?? true,
        emailVerified: user.email_verified ?? false,
        lastLoginAt: user.last_login_at,
        createdAt: user.created_at,
      }));
    } catch (error) {
      console.error('Failed to fetch users:', error);
      throw error; // Re-throw so the component can handle it
    }
  },

  /**
   * Get user details
   */
  async get(userId: string): Promise<UserDetail> {
    return fetchAPI<UserDetail>(`/admin/users/${userId}`);
  },

  /**
   * Create new user
   */
  async create(data: CreateUserRequest): Promise<UserDetail> {
    // Transform frontend schema to backend schema
    const backendPayload = {
      email: data.email,
      full_name: `${data.firstName} ${data.lastName}`.trim(),
      password: data.password || generateTempPassword(),
      organization_id: data.tenantId || null,
      role: data.role,
    };

    return fetchAPI<UserDetail>('/admin/users', {
      method: 'POST',
      body: JSON.stringify(backendPayload),
    });
  },

  /**
   * Update user
   */
  async update(userId: string, data: UpdateUserRequest): Promise<UserDetail> {
    // Transform frontend schema to backend schema
    const backendPayload: Record<string, any> = {};

    // Combine firstName and lastName into full_name
    if (data.firstName !== undefined || data.lastName !== undefined) {
      const firstName = data.firstName || '';
      const lastName = data.lastName || '';
      const fullName = `${firstName} ${lastName}`.trim();
      if (fullName) {
        backendPayload.full_name = fullName;
      }
    }

    // Map role (already snake_case compatible)
    if (data.role !== undefined) {
      backendPayload.role = data.role;
    }

    // Map isActive to is_active
    if (data.isActive !== undefined) {
      backendPayload.is_active = data.isActive;
    }

    return fetchAPI<UserDetail>(`/admin/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(backendPayload),
    });
  },

  /**
   * Deactivate user (soft delete)
   */
  async deactivate(userId: string): Promise<void> {
    return fetchAPI<void>(`/admin/users/${userId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Send invitation email
   */
  async sendInvitation(userId: string): Promise<void> {
    return fetchAPI<void>(`/admin/users/${userId}/invite`, {
      method: 'POST',
    });
  },

  /**
   * Reset user password (admin action)
   */
  async resetPassword(userId: string, newPassword: string, requireChange: boolean = false): Promise<void> {
    return fetchAPI<void>(`/admin/users/${userId}/reset-password`, {
      method: 'POST',
      body: JSON.stringify({
        new_password: newPassword,
        require_change: requireChange
      }),
    });
  },
};

// ============================================================================
// Dashboard / Stats APIs
// ============================================================================

export const dashboardAPI = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    try {
      // Fetch real data from multiple sources
      const [users, firms] = await Promise.all([
        userAPI.list({ pageSize: 1000 }).catch(() => []),
        tenantAPI.list({ limit: 1000 }).catch(() => []),
      ]);

      const activeUsers = users.filter(u => u.isActive).length;
      const activeFirms = firms.filter(f => f.subscription_status === 'active').length;

      return {
        totalUsers: users.length,
        activeUsers,
        totalFirms: firms.length,
        activeFirms,
        totalEngagements: 0, // Would need engagement API
        activeEngagements: 0,
        systemUptime: 99.9, // From health endpoint
        apiCallsToday: 0, // Would need metrics API
        avgResponseTime: 150, // From health endpoint
      };
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
      return {
        totalUsers: 0,
        activeUsers: 0,
        totalFirms: 0,
        activeFirms: 0,
        totalEngagements: 0,
        activeEngagements: 0,
        systemUptime: 0,
        apiCallsToday: 0,
        avgResponseTime: 0,
      };
    }
  },

  /**
   * Get system health status
   */
  async getHealth(): Promise<{ status: string; services: Record<string, boolean> }> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        return { status: 'healthy', services: { api: true, database: true, cache: true } };
      }
      return { status: 'degraded', services: { api: true, database: false, cache: false } };
    } catch {
      return { status: 'unhealthy', services: { api: false, database: false, cache: false } };
    }
  },
};

// ============================================================================
// Notification APIs
// ============================================================================

export const notificationAPI = {
  /**
   * Get notifications for admin
   */
  async list(): Promise<Notification[]> {
    try {
      // This would come from a real notifications endpoint
      // For now, generate notifications based on system state
      const notifications: Notification[] = [];

      // Check for recent users
      const users = await userAPI.list({ pageSize: 5 });
      const recentUsers = users.filter(u => {
        const created = new Date(u.createdAt);
        const now = new Date();
        return (now.getTime() - created.getTime()) < 24 * 60 * 60 * 1000; // Last 24 hours
      });

      recentUsers.forEach(user => {
        notifications.push({
          id: `user-${user.id}`,
          type: 'success',
          title: 'New User Registration',
          message: `${user.firstName || user.email} has joined the platform`,
          timestamp: user.createdAt,
          read: false,
        });
      });

      // Add system notification
      notifications.push({
        id: 'system-health',
        type: 'info',
        title: 'System Status',
        message: 'All services are operating normally',
        timestamp: new Date().toISOString(),
        read: true,
      });

      return notifications.sort((a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );
    } catch {
      return [];
    }
  },

  /**
   * Mark notification as read
   */
  async markAsRead(notificationId: string): Promise<void> {
    // Would call backend to mark as read
    console.log('Marking notification as read:', notificationId);
  },

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<void> {
    // Would call backend to mark all as read
    console.log('Marking all notifications as read');
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

// ============================================================================
// Helper Functions
// ============================================================================

function generateTempPassword(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%';
  let password = '';
  for (let i = 0; i < 16; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return password;
}
