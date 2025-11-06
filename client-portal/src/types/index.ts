/**
 * Type definitions for Aura Audit Client Portal
 */

// User and Authentication
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'client';
  tenantId: string;
  clientAccess: ClientAccess;
  avatarUrl?: string;
  createdAt: string;
}

export interface ClientAccess {
  canViewFinancials: boolean;
  canUploadDocuments: boolean;
  canManageIntegrations: boolean;
  canViewReports: boolean;
  engagementIds?: string[];
  accessExpiresAt?: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresAt: string;
}

// Integrations
export type IntegrationType =
  | 'quickbooks'
  | 'xero'
  | 'sage'
  | 'netsuite'
  | 'adp'
  | 'gusto'
  | 'paychex'
  | 'plaid';

export interface Integration {
  id: string;
  type: IntegrationType;
  name: string;
  description: string;
  icon: string;
  status: 'not_connected' | 'connecting' | 'connected' | 'error';
  connectedAt?: string;
  lastSyncAt?: string;
  config?: Record<string, any>;
  dataCategories: string[];
}

export interface IntegrationConnection {
  id: string;
  integrationType: IntegrationType;
  status: 'active' | 'disconnected' | 'error';
  connectedAt: string;
  lastSyncAt?: string;
  syncFrequency: 'realtime' | 'daily' | 'weekly';
  dataPoints: {
    category: string;
    count: number;
    lastUpdated: string;
  }[];
  errorMessage?: string;
}

// Documents
export interface Document {
  id: string;
  fileName: string;
  fileSize: number;
  fileType: string;
  category: DocumentCategory;
  uploadedAt: string;
  uploadedBy: string;
  status: 'processing' | 'ready' | 'error';
  url?: string;
  thumbnailUrl?: string;
  aiExtracted?: {
    documentType: string;
    confidence: number;
    keyData: Record<string, any>;
  };
}

export type DocumentCategory =
  | 'financial_statements'
  | 'bank_statements'
  | 'invoices'
  | 'receipts'
  | 'contracts'
  | 'tax_documents'
  | 'payroll'
  | 'other';

export interface DocumentRequirement {
  id: string;
  category: DocumentCategory;
  title: string;
  description: string;
  required: boolean;
  status: 'pending' | 'uploaded' | 'approved' | 'rejected';
  uploadedDocuments: Document[];
  dueDate?: string;
}

// Engagement and Progress
export interface Engagement {
  id: string;
  engagementNumber: string;
  engagementType: 'audit' | 'review' | 'compilation';
  clientName: string;
  periodStart: string;
  periodEnd: string;
  status: 'planning' | 'fieldwork' | 'reporting' | 'completed';
  progress: {
    overall: number;
    documents: number;
    integrations: number;
    questionnaire: number;
  };
  assignedAuditor: {
    name: string;
    email: string;
    avatarUrl?: string;
  };
  dueDate: string;
  createdAt: string;
}

export interface EngagementProgress {
  overall: number;
  categories: {
    category: string;
    label: string;
    progress: number;
    status: 'not_started' | 'in_progress' | 'complete';
    items: {
      name: string;
      completed: boolean;
      requiredBy?: string;
    }[];
  }[];
  lastUpdated: string;
}

// AI Assistant
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  attachments?: {
    type: 'document' | 'integration' | 'checklist';
    data: any;
  }[];
}

export interface AISuggestion {
  id: string;
  type: 'document' | 'integration' | 'action';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  action?: () => void;
}

// Dashboard Data
export interface DashboardStats {
  documentsUploaded: number;
  documentsRequired: number;
  integrationsConnected: number;
  integrationsAvailable: number;
  overallProgress: number;
  nextDeadline?: {
    date: string;
    description: string;
  };
}

// OAuth
export interface OAuthProvider {
  id: 'microsoft' | 'google';
  name: string;
  icon: string;
  authUrl: string;
}

// Notifications
export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  action?: {
    label: string;
    url: string;
  };
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// CPA Firm Types
export type UserRole = 'partner' | 'manager' | 'senior' | 'staff' | 'qc_reviewer' | 'client_contact';

export interface FirmUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  organization_id: string;
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
}

export interface Organization {
  id: string;
  name: string;
  tax_id?: string;
  industry_code?: string;
  logo_url?: string;
  primary_color: string;
  secondary_color: string;
  address?: string;
  phone?: string;
  website?: string;
  timezone: string;
  date_format: string;
  created_at: string;
  updated_at: string;
}

export interface OrganizationUpdate {
  name?: string;
  tax_id?: string;
  industry_code?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  address?: string;
  phone?: string;
  website?: string;
  timezone?: string;
  date_format?: string;
}

export interface UserInvitation {
  id: string;
  email: string;
  role: UserRole;
  invited_by_user_id: string;
  expires_at: string;
  accepted_at?: string;
  is_expired: boolean;
  created_at: string;
}

export interface UserInvitationCreate {
  email: string;
  role: UserRole;
  message?: string;
}

export interface UserPermission {
  id: string;
  user_id: string;
  can_create_engagements: boolean;
  can_edit_engagements: boolean;
  can_delete_engagements: boolean;
  can_view_all_engagements: boolean;
  can_invite_users: boolean;
  can_manage_users: boolean;
  can_manage_roles: boolean;
  can_edit_firm_settings: boolean;
  can_manage_billing: boolean;
  can_upload_documents: boolean;
  can_delete_documents: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserPermissionUpdate {
  can_create_engagements?: boolean;
  can_edit_engagements?: boolean;
  can_delete_engagements?: boolean;
  can_view_all_engagements?: boolean;
  can_invite_users?: boolean;
  can_manage_users?: boolean;
  can_manage_roles?: boolean;
  can_edit_firm_settings?: boolean;
  can_manage_billing?: boolean;
  can_upload_documents?: boolean;
  can_delete_documents?: boolean;
}

export interface FirmStats {
  total_employees: number;
  active_engagements: number;
  pending_invitations: number;
  total_clients: number;
  documents_uploaded_this_month: number;
  active_integrations: number;
}
