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
  // Generic methods - Use unknown instead of any for type safety
  get: <T = unknown>(url: string, config?: AxiosRequestConfig) =>
    apiClient.get<T>(url, config).then((res) => res.data),

  post: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiClient.post<T>(url, data, config).then((res) => res.data),

  put: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiClient.put<T>(url, data, config).then((res) => res.data),

  patch: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiClient.patch<T>(url, data, config).then((res) => res.data),

  delete: <T = unknown>(url: string, config?: AxiosRequestConfig) =>
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

  // Engagements (Full Workflow Support)
  engagements: {
    list: () => api.get('/engagements'),

    get: (id: string) => api.get(`/engagements/${id}`),

    create: (data: any) => api.post('/engagements', data),

    update: (id: string, data: any) => api.patch(`/engagements/${id}`, data),

    delete: (id: string) => api.delete(`/engagements/${id}`),

    // State Transitions
    transition: (id: string, newStatus: string) =>
      api.post(`/engagements/${id}/transition`, null, { params: { new_status: newStatus } }),

    // Team Members
    team: {
      list: (engagementId: string) =>
        api.get(`/engagements/${engagementId}/team`),

      add: (engagementId: string, data: { user_id: string; role: string }) =>
        api.post(`/engagements/${engagementId}/team`, data),

      remove: (engagementId: string, teamMemberId: string) =>
        api.delete(`/engagements/${engagementId}/team/${teamMemberId}`),
    },

    // Binder & Workpapers
    binder: {
      getTree: (engagementId: string) =>
        api.get(`/engagements/${engagementId}/binder/tree`),

      createNode: (engagementId: string, data: any) =>
        api.post(`/engagements/${engagementId}/binder/nodes`, data),

      updateNode: (nodeId: string, data: any) =>
        api.patch(`/binder/nodes/${nodeId}`, data),

      deleteNode: (nodeId: string) =>
        api.delete(`/binder/nodes/${nodeId}`),
    },

    // Workpapers
    workpapers: {
      get: (workpaperId: string) =>
        api.get(`/workpapers/${workpaperId}`),

      update: (workpaperId: string, data: any) =>
        api.patch(`/workpapers/${workpaperId}`, data),

      addReviewNote: (workpaperId: string, data: any) =>
        api.post(`/workpapers/${workpaperId}/review-notes`, data),
    },
  },

  // Disclosures
  disclosures: {
    // Disclosure Templates
    templates: {
      list: (reportType?: string) =>
        api.get('/disclosures/templates', { params: { report_type: reportType } }),

      get: (templateId: string) =>
        api.get(`/disclosures/templates/${templateId}`),

      create: (data: any) =>
        api.post('/disclosures/templates', data),

      update: (templateId: string, data: any) =>
        api.patch(`/disclosures/templates/${templateId}`, data),

      delete: (templateId: string) =>
        api.delete(`/disclosures/templates/${templateId}`),
    },

    // Engagement Disclosures
    byEngagement: {
      list: (engagementId: string) =>
        api.get(`/disclosures/engagements/${engagementId}`),

      create: (engagementId: string, data: any) =>
        api.post(`/disclosures/engagements/${engagementId}`, data),

      get: (disclosureId: string) =>
        api.get(`/disclosures/${disclosureId}`),

      update: (disclosureId: string, data: any) =>
        api.patch(`/disclosures/${disclosureId}`, data),

      delete: (disclosureId: string) =>
        api.delete(`/disclosures/${disclosureId}`),

      updateStatus: (disclosureId: string, status: string) =>
        api.patch(`/disclosures/${disclosureId}/status`, { status }),

      aiDraft: (disclosureId: string) =>
        api.post(`/disclosures/${disclosureId}/ai-draft`),
    },

    // Checklist Management
    checklists: {
      get: (engagementId: string, standard: string) =>
        api.get(`/disclosures/engagements/${engagementId}/checklist`, { params: { standard } }),

      update: (engagementId: string, data: any) =>
        api.patch(`/disclosures/engagements/${engagementId}/checklist`, data),

      generate: (engagementId: string, standard: string) =>
        api.post(`/disclosures/engagements/${engagementId}/checklist/generate`, { standard }),
    },
  },

  // Reporting
  reporting: {
    // Report Templates
    templates: {
      list: (reportType?: string) =>
        api.get('/reporting/templates', { params: { report_type: reportType } }),

      get: (templateId: string) =>
        api.get(`/reporting/templates/${templateId}`),

      create: (data: any) =>
        api.post('/reporting/templates', data),

      update: (templateId: string, data: any) =>
        api.patch(`/reporting/templates/${templateId}`, data),

      delete: (templateId: string) =>
        api.delete(`/reporting/templates/${templateId}`),
    },

    // Reports
    reports: {
      list: (engagementId?: string) =>
        api.get('/reporting/reports', { params: { engagement_id: engagementId } }),

      get: (reportId: string) =>
        api.get(`/reporting/reports/${reportId}`),

      create: (data: any) =>
        api.post('/reporting/reports', data),

      update: (reportId: string, data: any) =>
        api.patch(`/reporting/reports/${reportId}`, data),

      delete: (reportId: string) =>
        api.delete(`/reporting/reports/${reportId}`),

      generate: (reportId: string) =>
        api.post(`/reporting/reports/${reportId}/generate`),

      download: (reportId: string) =>
        api.get(`/reporting/reports/${reportId}/download`, { responseType: 'blob' }),

      finalize: (reportId: string) =>
        api.post(`/reporting/reports/${reportId}/finalize`),
    },

    // E-Signatures
    signatures: {
      create: (reportId: string, data: any) =>
        api.post(`/reporting/reports/${reportId}/signatures`, data),

      get: (envelopeId: string) =>
        api.get(`/reporting/signatures/${envelopeId}`),

      send: (envelopeId: string) =>
        api.post(`/reporting/signatures/${envelopeId}/send`),

      void: (envelopeId: string, reason: string) =>
        api.post(`/reporting/signatures/${envelopeId}/void`, { reason }),

      resend: (envelopeId: string) =>
        api.post(`/reporting/signatures/${envelopeId}/resend`),
    },

    // Opinions (Audit/Review/Compilation)
    opinions: {
      generate: (engagementId: string, data: any) =>
        api.post(`/reporting/engagements/${engagementId}/opinion`, data),

      get: (engagementId: string) =>
        api.get(`/reporting/engagements/${engagementId}/opinion`),

      update: (engagementId: string, data: any) =>
        api.patch(`/reporting/engagements/${engagementId}/opinion`, data),
    },
  },

  // Confirmations (Wire/Bank confirmations)
  confirmations: {
    list: (engagementId: string) =>
      api.get(`/confirmations/engagements/${engagementId}`),

    create: (engagementId: string, data: any) =>
      api.post(`/confirmations/engagements/${engagementId}`, data),

    get: (confirmationId: string) =>
      api.get(`/confirmations/${confirmationId}`),

    update: (confirmationId: string, data: any) =>
      api.patch(`/confirmations/${confirmationId}`, data),

    generateLetter: (confirmationId: string, templateId?: string) =>
      api.post(`/confirmations/${confirmationId}/generate-letter`, { template_id: templateId }),

    markSent: (confirmationId: string, data: any) =>
      api.post(`/confirmations/${confirmationId}/mark-sent`, data),

    recordResponse: (confirmationId: string, data: any) =>
      api.post(`/confirmations/${confirmationId}/record-response`, data),

    summary: (engagementId: string) =>
      api.get(`/confirmations/engagements/${engagementId}/summary`),
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
    mappings: {
      list: (engagementId: string) =>
        api.get(`/normalize/engagements/${engagementId}/suggestions`),

      generate: (engagementId: string) =>
        api.post(`/normalize/engagements/${engagementId}/map`),

      update: (suggestionId: string, data: any) =>
        api.patch(`/normalize/suggestions/${suggestionId}`, data),

      batch: (data: any) =>
        api.post('/normalize/suggestions/batch', data),
    },

    findSimilar: (accountName: string, topK: number = 5) =>
      api.post('/normalize/similarity', { account_name: accountName, top_k: topK }),
  },

  // QC (Quality Control)
  qc: {
    policies: {
      list: () => api.get('/qc/policies'),
      get: (policyId: string) => api.get(`/qc/policies/${policyId}`),
    },

    results: {
      list: (engagementId: string) =>
        api.get(`/qc/engagements/${engagementId}/results`),
      get: (resultId: string) => api.get(`/qc/results/${resultId}`),
    },

    execute: (engagementId: string, data: any) =>
      api.post(`/qc/engagements/${engagementId}/run`, data),
  },

  // Admin Portal
  admin: {
    // Customers
    customers: {
      list: (params?: any) => api.get('/admin/customers', { params }),
      get: (customerId: string) => api.get(`/admin/customers/${customerId}`),
      create: (data: any) => api.post('/admin/customers', data),
      update: (customerId: string, data: any) =>
        api.put(`/admin/customers/${customerId}`, data),
      delete: (customerId: string) => api.delete(`/admin/customers/${customerId}`),
      suspend: (customerId: string) =>
        api.post(`/admin/customers/${customerId}/suspend`),
      activate: (customerId: string) =>
        api.post(`/admin/customers/${customerId}/activate`),
    },

    // Licenses
    licenses: {
      list: (customerId?: string) =>
        api.get('/admin/licenses', { params: { customer_id: customerId } }),
      get: (licenseId: string) => api.get(`/admin/licenses/${licenseId}`),
      create: (data: any) => api.post('/admin/licenses', data),
      update: (licenseId: string, data: any) =>
        api.put(`/admin/licenses/${licenseId}`, data),
      cancel: (licenseId: string) =>
        api.post(`/admin/licenses/${licenseId}/cancel`),
      renew: (licenseId: string, data: any) =>
        api.post(`/admin/licenses/${licenseId}/renew`, data),
    },

    // Usage Metrics
    usage: {
      getByCustomer: (customerId: string, params?: any) =>
        api.get(`/admin/customers/${customerId}/usage`, { params }),
      getAll: (params?: any) => api.get('/admin/usage', { params }),
      export: (params?: any) =>
        api.get('/admin/usage/export', { params, responseType: 'blob' }),
    },

    // Metrics & Analytics
    metrics: {
      overview: () => api.get('/admin/metrics/overview'),
      revenue: (params?: any) => api.get('/admin/metrics/revenue', { params }),
      growth: (params?: any) => api.get('/admin/metrics/growth', { params }),
      churn: (params?: any) => api.get('/admin/metrics/churn', { params }),
    },

    // Activity Logs
    activity: {
      list: (customerId?: string, params?: any) =>
        api.get('/admin/activity', { params: { customer_id: customerId, ...params } }),
      export: (params?: any) =>
        api.get('/admin/activity/export', { params, responseType: 'blob' }),
    },

    // Invoices
    invoices: {
      list: (customerId?: string) =>
        api.get('/admin/invoices', { params: { customer_id: customerId } }),
      get: (invoiceId: string) => api.get(`/admin/invoices/${invoiceId}`),
      create: (data: any) => api.post('/admin/invoices', data),
      send: (invoiceId: string) => api.post(`/admin/invoices/${invoiceId}/send`),
      markPaid: (invoiceId: string, data: any) =>
        api.post(`/admin/invoices/${invoiceId}/mark-paid`, data),
    },

    // Support Tickets
    tickets: {
      list: (params?: any) => api.get('/admin/tickets', { params }),
      get: (ticketId: string) => api.get(`/admin/tickets/${ticketId}`),
      update: (ticketId: string, data: any) =>
        api.put(`/admin/tickets/${ticketId}`, data),
      assign: (ticketId: string, userId: string) =>
        api.post(`/admin/tickets/${ticketId}/assign`, { user_id: userId }),
      resolve: (ticketId: string, data: any) =>
        api.post(`/admin/tickets/${ticketId}/resolve`, data),
    },

    // Customer Settings
    settings: {
      get: (customerId: string) =>
        api.get(`/admin/customers/${customerId}/settings`),
      update: (customerId: string, data: any) =>
        api.put(`/admin/customers/${customerId}/settings`, data),
    },

    // Admin Users
    users: {
      list: () => api.get('/admin/users'),
      get: (userId: string) => api.get(`/admin/users/${userId}`),
      create: (data: any) => api.post('/admin/users', data),
      update: (userId: string, data: any) =>
        api.put(`/admin/users/${userId}`, data),
      delete: (userId: string) => api.delete(`/admin/users/${userId}`),
    },
  },
};

export default api;
