/**
 * Type Definitions for Aura Audit AI
 */

// ========================================
// User & Authentication
// ========================================

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export enum UserRole {
  ADMIN = 'admin',
  PARTNER = 'partner',
  MANAGER = 'manager',
  SENIOR = 'senior',
  STAFF = 'staff',
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ========================================
// Engagement
// ========================================

export interface Engagement {
  id: string;
  client_name: string;
  engagement_type: EngagementType;
  fiscal_year_end: string;
  status: EngagementStatus;
  partner_id: string;
  manager_id?: string;
  created_at: string;
  updated_at: string;
}

export enum EngagementType {
  AUDIT = 'audit',
  REVIEW = 'review',
  COMPILATION = 'compilation',
  TAX = 'tax',
}

export enum EngagementStatus {
  DRAFT = 'draft',
  PLANNING = 'planning',
  FIELDWORK = 'fieldwork',
  REVIEW = 'review',
  FINALIZED = 'finalized',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

// ========================================
// Analytics
// ========================================

export interface JETestResult {
  test_type: string;
  journal_entry_id: string;
  entry_number: string;
  entry_date: string;
  amount: number;
  flagged: boolean;
  reason: string;
  score?: number;
}

export interface JETestSummary {
  engagement_id: string;
  total_entries_tested: number;
  round_dollar_flagged: number;
  weekend_flagged: number;
  period_end_flagged: number;
  results: JETestResult[];
}

export interface Anomaly {
  id: string;
  engagement_id: string;
  anomaly_type: string;
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description?: string;
  evidence: Record<string, any>;
  score?: number;
  resolution_status: string;
  created_at: string;
}

export interface RatioResult {
  ratio_name: string;
  value: number;
  benchmark?: number;
  deviation?: number;
  is_outlier: boolean;
}

// ========================================
// Normalize (Account Mapping)
// ========================================

export interface MappingSuggestion {
  id: string;
  engagement_id: string;
  trial_balance_line_id: string;
  source_account_code: string;
  source_account_name: string;
  suggested_account_code: string;
  suggested_account_name: string;
  confidence_score: number;
  confidence_level: 'low' | 'medium' | 'high' | 'very_high';
  status: 'unmapped' | 'suggested' | 'confirmed' | 'rejected' | 'manual';
  alternatives?: Array<{
    account_code: string;
    account_name?: string;
    score: number;
  }>;
  created_at: string;
}

// ========================================
// QC (Quality Control)
// ========================================

export interface QCResult {
  id: string;
  engagement_id: string;
  policy_code: string;
  policy_name: string;
  passed: boolean;
  score?: number;
  findings: any[];
  details: Record<string, any>;
  executed_at: string;
}

// ========================================
// UI State
// ========================================

export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: 'default' | 'success' | 'warning' | 'error';
  duration?: number;
}

export interface PaginationParams {
  page: number;
  limit: number;
  total?: number;
}

export interface FilterParams {
  search?: string;
  status?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// ========================================
// API Response
// ========================================

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}
