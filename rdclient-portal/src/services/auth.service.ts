/**
 * R&D Client Portal Authentication Service
 * Handles login, registration, and session management for R&D clients
 */

import api from './api';
import type {
  LoginCredentials,
  RegisterData,
  TokenResponse,
  RDClientUser,
} from '../types';

interface InvitationValidationResponse {
  valid: boolean;
  study_id: string;
  study_name: string;
  company_name: string;
  tax_year: number;
  firm_name: string;
  firm_logo?: string;
  email: string;
  name: string;
  expires_at: string;
  already_registered: boolean;
}

interface PasswordResetRequest {
  email: string;
}

interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

class AuthService {
  /**
   * Validate an invitation token
   */
  async validateInvitation(token: string): Promise<InvitationValidationResponse> {
    return api.get<InvitationValidationResponse>('/rdclient/invitations/validate', { token });
  }

  /**
   * Register a new R&D client user from an invitation
   */
  async register(data: RegisterData): Promise<TokenResponse> {
    return api.post<TokenResponse>('/rdclient/auth/register', data);
  }

  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    return api.post<TokenResponse>('/rdclient/auth/login', credentials);
  }

  /**
   * Refresh the access token
   */
  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    return api.post<TokenResponse>('/rdclient/auth/refresh', { refresh_token: refreshToken });
  }

  /**
   * Logout (invalidate token on server)
   */
  async logout(): Promise<void> {
    try {
      await api.post('/rdclient/auth/logout');
    } catch {
      // Ignore logout errors - we'll clear local state anyway
    }
  }

  /**
   * Get current user profile
   */
  async getProfile(): Promise<RDClientUser> {
    return api.get<RDClientUser>('/rdclient/auth/me');
  }

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<RDClientUser>): Promise<RDClientUser> {
    return api.patch<RDClientUser>('/rdclient/auth/me', data);
  }

  /**
   * Change password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/rdclient/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<{ message: string }> {
    return api.post<{ message: string }>('/rdclient/auth/password-reset/request', data);
  }

  /**
   * Confirm password reset with token
   */
  async confirmPasswordReset(data: PasswordResetConfirm): Promise<{ message: string }> {
    return api.post<{ message: string }>('/rdclient/auth/password-reset/confirm', data);
  }
}

export const authService = new AuthService();
export default authService;
