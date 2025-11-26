/**
 * Admin Portal Configuration
 *
 * All environment-specific configuration values should be defined here.
 * Uses Vite's environment variable system (import.meta.env)
 */

// API Configuration
export const API_CONFIG = {
  // Identity service URL (authentication and admin APIs)
  identityUrl: import.meta.env.VITE_IDENTITY_API_URL || '/api',

  // Other service URLs
  engagementUrl: import.meta.env.VITE_ENGAGEMENT_API_URL || '/api/engagement',
  reportingUrl: import.meta.env.VITE_REPORTING_API_URL || '/api/reporting',
  analyticsUrl: import.meta.env.VITE_ANALYTICS_API_URL || '/api/analytics',

  // API timeouts
  defaultTimeout: 30000, // 30 seconds
  uploadTimeout: 300000, // 5 minutes for file uploads
};

// App Configuration
export const APP_CONFIG = {
  name: 'Aura AI Admin Portal',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  environment: import.meta.env.MODE || 'production',

  // Feature flags
  features: {
    analytics: true,
    userManagement: true,
    firmManagement: true,
    systemSettings: true,
    ticketManagement: true,
  },
};

// Service Catalog - All available services in the platform
export const SERVICE_CATALOG = [
  // Core Services
  { id: 'analytics', name: 'Analytics', category: 'Core', defaultEnabled: true },
  { id: 'llm', name: 'AI Language Model', category: 'Core', defaultEnabled: true },
  { id: 'engagement', name: 'Engagement Management', category: 'Core', defaultEnabled: true },
  { id: 'reporting', name: 'Reporting', category: 'Core', defaultEnabled: true },

  // Audit Services
  { id: 'audit-planning', name: 'Audit Planning', category: 'Audit', defaultEnabled: true },
  { id: 'substantive-testing', name: 'Substantive Testing', category: 'Audit', defaultEnabled: true },
  { id: 'fraud-detection', name: 'Fraud Detection', category: 'Audit', defaultEnabled: true },
  { id: 'financial-analysis', name: 'Financial Analysis', category: 'Audit', defaultEnabled: true },
  { id: 'subsequent-events', name: 'Subsequent Events', category: 'Audit', defaultEnabled: true },
  { id: 'related-party', name: 'Related Party Transactions', category: 'Audit', defaultEnabled: true },
  { id: 'sampling', name: 'Audit Sampling', category: 'Audit', defaultEnabled: true },
  { id: 'estimates-evaluation', name: 'Estimates Evaluation', category: 'Audit', defaultEnabled: true },

  // Compliance & Reporting
  { id: 'disclosures', name: 'Disclosure Generation', category: 'Compliance', defaultEnabled: true },
  { id: 'reg-ab-audit', name: 'Reg AB Audit', category: 'Compliance', defaultEnabled: true },
  { id: 'advanced-report-generation', name: 'Advanced Report Generation', category: 'Compliance', defaultEnabled: true },
  { id: 'sox-automation', name: 'SOX Automation', category: 'Compliance', defaultEnabled: true },

  // Tax Services
  { id: 'tax-engine', name: 'Tax Engine', category: 'Tax', defaultEnabled: true },
  { id: 'tax-forms', name: 'Tax Forms', category: 'Tax', defaultEnabled: true },
  { id: 'tax-review', name: 'Tax Review', category: 'Tax', defaultEnabled: true },
  { id: 'tax-ocr-intake', name: 'Tax OCR Intake', category: 'Tax', defaultEnabled: true },
  { id: 'rd-study-automation', name: 'R&D Study Automation', category: 'Tax', defaultEnabled: true },

  // Data & Integration
  { id: 'ingestion', name: 'Data Ingestion', category: 'Data', defaultEnabled: true },
  { id: 'normalize', name: 'Data Normalization', category: 'Data', defaultEnabled: true },
  { id: 'connectors', name: 'Third-Party Connectors', category: 'Data', defaultEnabled: true },
  { id: 'accounting-integrations', name: 'Accounting Integrations', category: 'Data', defaultEnabled: true },

  // Quality & Security
  { id: 'qc', name: 'Quality Control', category: 'Quality', defaultEnabled: true },
  { id: 'security', name: 'Security & Access Control', category: 'Security', defaultEnabled: true },
  { id: 'data-anonymization', name: 'Data Anonymization', category: 'Security', defaultEnabled: true },

  // AI/ML Services
  { id: 'ai-agent-builder', name: 'AI Agent Builder', category: 'AI/ML', defaultEnabled: false },
  { id: 'ai-testing', name: 'AI Testing', category: 'AI/ML', defaultEnabled: false },
  { id: 'document-intelligence', name: 'Document Intelligence', category: 'AI/ML', defaultEnabled: false },
  { id: 'training-data', name: 'Training Data Management', category: 'AI/ML', defaultEnabled: false },

  // Advanced Analytics
  { id: 'control-points-engine', name: 'Control Points Engine', category: 'Advanced Analytics', defaultEnabled: false },
  { id: 'full-population-analysis', name: 'Full Population Analysis', category: 'Advanced Analytics', defaultEnabled: false },
  { id: 'gl-monitor', name: 'GL Monitor', category: 'Advanced Analytics', defaultEnabled: false },
  { id: 'predictive-failure', name: 'Predictive Failure Analysis', category: 'Advanced Analytics', defaultEnabled: false },
  { id: 'risk-monitor', name: 'Risk Monitor', category: 'Advanced Analytics', defaultEnabled: false },
  { id: 'variance-intelligence', name: 'Variance Intelligence', category: 'Advanced Analytics', defaultEnabled: false },

  // Specialized Services
  { id: 'soc-copilot', name: 'SOC Copilot', category: 'Specialized', defaultEnabled: false },
  { id: 'eo-insurance-portal', name: 'E&O Insurance Portal', category: 'Specialized', defaultEnabled: true },
] as const;

// Security Configuration
export const SECURITY_CONFIG = {
  // Token management
  tokenStorageKey: 'admin_token',
  tokenRefreshThreshold: 300000, // Refresh token 5 minutes before expiry

  // Session management
  sessionTimeout: 1800000, // 30 minutes of inactivity
  sessionWarningTime: 300000, // Warn 5 minutes before timeout

  // Password requirements
  passwordMinLength: 12,
  passwordRequireUppercase: true,
  passwordRequireLowercase: true,
  passwordRequireNumbers: true,
  passwordRequireSpecialChars: true,
};

// UI Configuration
export const UI_CONFIG = {
  // Pagination
  defaultPageSize: 20,
  pageSizeOptions: [10, 20, 50, 100],

  // Table settings
  maxTableRows: 1000,

  // File uploads
  maxFileSize: 100 * 1024 * 1024, // 100MB
  allowedFileTypes: ['.pdf', '.xlsx', '.xls', '.csv', '.docx', '.doc', '.txt'],

  // Notifications
  notificationDuration: 5000, // 5 seconds
  errorDuration: 10000, // 10 seconds
};

// Export environment check
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;

// Export all configs as a single object for convenience
export default {
  API_CONFIG,
  APP_CONFIG,
  SERVICE_CATALOG,
  SECURITY_CONFIG,
  UI_CONFIG,
  isDevelopment,
  isProduction,
};
