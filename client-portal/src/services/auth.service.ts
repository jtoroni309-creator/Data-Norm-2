/**
 * Authentication Service
 * Handles OAuth2 authentication with Microsoft 365, Google, and JWT tokens
 */

import axios from 'axios';
import type { AuthResponse, User, OAuthProvider } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export class AuthService {
  private static instance: AuthService;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  private constructor() {
    // Load tokens from localStorage
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  /**
   * OAuth Providers configuration
   */
  public getOAuthProviders(): OAuthProvider[] {
    return [
      {
        id: 'microsoft',
        name: 'Microsoft 365',
        icon: '/icons/microsoft.svg',
        authUrl: `${API_BASE_URL}/auth/microsoft/authorize`,
      },
      {
        id: 'google',
        name: 'Google Business',
        icon: '/icons/google.svg',
        authUrl: `${API_BASE_URL}/auth/google/authorize`,
      },
    ];
  }

  /**
   * Initiate OAuth flow
   */
  public async initiateOAuth(provider: 'microsoft' | 'google'): Promise<void> {
    const { authUrl } = this.getOAuthProviders().find(p => p.id === provider)!;

    // Generate and store state parameter for CSRF protection
    const state = this.generateRandomState();
    localStorage.setItem('oauth_state', state);

    // Redirect to OAuth provider
    window.location.href = `${authUrl}?state=${state}&redirect_uri=${encodeURIComponent(window.location.origin + '/auth/callback')}`;
  }

  /**
   * Handle OAuth callback
   */
  public async handleOAuthCallback(code: string, state: string, provider: string): Promise<AuthResponse> {
    // Verify state parameter
    const savedState = localStorage.getItem('oauth_state');
    if (state !== savedState) {
      throw new Error('Invalid state parameter - potential CSRF attack');
    }

    localStorage.removeItem('oauth_state');

    // Exchange code for tokens
    const response = await axios.post<AuthResponse>(`${API_BASE_URL}/auth/${provider}/callback`, {
      code,
      redirectUri: window.location.origin + '/auth/callback',
    });

    this.setTokens(response.data.accessToken, response.data.refreshToken);
    return response.data;
  }

  /**
   * Get current user
   */
  public async getCurrentUser(): Promise<User | null> {
    if (!this.accessToken) {
      return null;
    }

    try {
      const response = await axios.get<User>(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        // Try to refresh token
        await this.refreshAccessToken();
        // Retry
        const response = await axios.get<User>(`${API_BASE_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${this.accessToken}`,
          },
        });
        return response.data;
      }
      return null;
    }
  }

  /**
   * Refresh access token
   */
  public async refreshAccessToken(): Promise<string | null> {
    if (!this.refreshToken) {
      return null;
    }

    try {
      const response = await axios.post<{ accessToken: string; expiresAt: string }>(
        `${API_BASE_URL}/auth/refresh`,
        {
          refreshToken: this.refreshToken,
        }
      );

      this.accessToken = response.data.accessToken;
      localStorage.setItem('access_token', this.accessToken);
      return this.accessToken;
    } catch (error) {
      // Refresh failed, clear tokens
      this.logout();
      return null;
    }
  }

  /**
   * Logout
   */
  public async logout(): Promise<void> {
    if (this.accessToken) {
      try {
        await axios.post(
          `${API_BASE_URL}/auth/logout`,
          {},
          {
            headers: {
              Authorization: `Bearer ${this.accessToken}`,
            },
          }
        );
      } catch (error) {
        // Ignore errors during logout
      }
    }

    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  /**
   * Check if user is authenticated
   */
  public isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  /**
   * Get access token
   */
  public getAccessToken(): string | null {
    return this.accessToken;
  }

  /**
   * Set tokens
   */
  private setTokens(accessToken: string, refreshToken: string): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  /**
   * Generate random state for OAuth
   */
  private generateRandomState(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }
}

/**
 * Axios interceptor to add auth token to requests
 */
axios.interceptors.request.use(
  (config) => {
    const token = AuthService.getInstance().getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Axios interceptor to handle 401 errors and refresh tokens
 */
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const newToken = await AuthService.getInstance().refreshAccessToken();
        if (newToken) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const authService = AuthService.getInstance();
