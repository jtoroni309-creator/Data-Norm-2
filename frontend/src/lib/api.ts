/**
 * API Client Configuration
 *
 * Centralized API client with interceptors, error handling, and type safety
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Create axios instance with default configuration
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor - Add auth token to requests
 */
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;

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
 * Response interceptor - Handle errors globally
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Clear token and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      console.error('Access denied:', error.response.data);
    }

    // Handle 404 Not Found
    if (error.response?.status === 404) {
      console.error('Resource not found:', error.response.data);
    }

    // Handle 500 Server Error
    if (error.response?.status && error.response.status >= 500) {
      console.error('Server error:', error.response.data);
    }

    return Promise.reject(error);
  }
);

/**
 * API Service Methods
 */
export const api = {
  // Generic methods
  get: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.get<T>(url, config).then((res) => res.data),

  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.post<T>(url, data, config).then((res) => res.data),

  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.put<T>(url, data, config).then((res) => res.data),

  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.patch<T>(url, data, config).then((res) => res.data),

  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.delete<T>(url, config).then((res) => res.data),

  // Authentication
  auth: {
    login: (credentials: { email: string; password: string }) =>
      api.post('/auth/login', credentials),

    register: (data: { email: string; password: string; full_name: string }) =>
      api.post('/auth/register', data),

    logout: () => api.post('/auth/logout'),

    me: () => api.get('/auth/me'),

    refreshToken: () => api.post('/auth/refresh'),
  },

  // Engagements
  engagements: {
    list: () => api.get('/engagements'),

    get: (id: string) => api.get(`/engagements/${id}`),

    create: (data: any) => api.post('/engagements', data),

    update: (id: string, data: any) => api.put(`/engagements/${id}`, data),

    delete: (id: string) => api.delete(`/engagements/${id}`),
  },

  // Analytics
  analytics: {
    jeTests: (engagementId: string) =>
      api.post(`/analytics/je-testing/${engagementId}`),

    anomalies: {
      detect: (engagementId: string, method: string = 'zscore') =>
        api.post(`/analytics/anomalies/${engagementId}/detect`, { method }),

      list: (engagementId: string) =>
        api.get(`/analytics/anomalies/${engagementId}`),

      resolve: (anomalyId: string, data: any) =>
        api.patch(`/analytics/anomalies/${anomalyId}/resolve`, data),
    },

    ratios: (engagementId: string) =>
      api.get(`/analytics/ratios/${engagementId}`),
  },

  // Normalize (Account Mapping)
  normalize: {
    generateSuggestions: (engagementId: string, options?: any) =>
      api.post(`/normalize/engagements/${engagementId}/map`, options),

    listSuggestions: (engagementId: string, status?: string) =>
      api.get(`/normalize/engagements/${engagementId}/suggestions`, {
        params: { status },
      }),

    confirmSuggestion: (suggestionId: string, action: string, data?: any) =>
      api.patch(`/normalize/suggestions/${suggestionId}`, { action, ...data }),

    findSimilar: (accountName: string, topK: number = 5) =>
      api.post('/normalize/similarity', { account_name: accountName, top_k: topK }),
  },

  // QC (Quality Control)
  qc: {
    runChecks: (engagementId: string, policies?: string[]) =>
      api.post(`/qc/engagements/${engagementId}/run`, { policies }),

    getResults: (engagementId: string) =>
      api.get(`/qc/engagements/${engagementId}/results`),

    getResult: (resultId: string) =>
      api.get(`/qc/results/${resultId}`),
  },
};

export default api;
