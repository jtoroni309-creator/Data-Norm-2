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
  token: string;
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

// ========================================
// R&D Study Types
// ========================================

export type RDStudyStatus =
  | 'draft'
  | 'intake'
  | 'data_collection'
  | 'ai_analysis'
  | 'cpa_review'
  | 'calculation'
  | 'narrative_generation'
  | 'final_review'
  | 'approved'
  | 'finalized'
  | 'locked';

export type RDEntityType =
  | 'c_corp'
  | 's_corp'
  | 'partnership'
  | 'llc'
  | 'sole_prop'
  | 'consolidated';

export type RDCreditMethod = 'regular' | 'asc';

export type RDQualificationStatus =
  | 'pending'
  | 'qualified'
  | 'not_qualified'
  | 'partial'
  | 'needs_review';

export type RDQRECategory =
  | 'wages'
  | 'supplies'
  | 'contract_research'
  | 'basic_research'
  | 'energy_research';

export interface RDStudySummary {
  id: string;
  name: string;
  client_id: string;
  client_name?: string;
  tax_year: number;
  entity_name: string;
  entity_type: RDEntityType;
  status: RDStudyStatus;
  total_qre: number;
  federal_credit_final: number;
  total_state_credits: number;
  total_credits: number;
  has_open_flags: boolean;
  cpa_approved: boolean;
  created_at: string;
  updated_at?: string;
}

export interface RDStudy {
  id: string;
  firm_id: string;
  client_id: string;
  engagement_id?: string;
  name: string;
  tax_year: number;
  study_type: string;
  entity_type: RDEntityType;
  entity_name: string;
  ein?: string;
  fiscal_year_start: string;
  fiscal_year_end: string;
  is_short_year: boolean;
  short_year_days?: number;
  is_controlled_group: boolean;
  controlled_group_name?: string;
  aggregation_method?: string;
  status: RDStudyStatus;
  status_history: Array<{ status: string; timestamp: string; user_id: string }>;
  recommended_method?: RDCreditMethod;
  selected_method?: RDCreditMethod;
  method_selection_reason?: string;
  states: string[];
  primary_state?: string;
  ai_risk_score?: number;
  ai_opportunity_score?: number;
  ai_suggested_areas: Array<{ area: string; confidence: number }>;
  ai_analysis_summary?: string;
  total_qre: number;
  federal_credit_regular: number;
  federal_credit_asc: number;
  federal_credit_final: number;
  total_state_credits: number;
  total_credits: number;
  prior_credit_carryforward: number;
  risk_flags: Array<{ type: string; severity: string; message: string }>;
  has_open_flags: boolean;
  notes?: string;
  requires_cpa_approval: boolean;
  cpa_approved: boolean;
  cpa_approved_by?: string;
  cpa_approved_at?: string;
  cpa_approval_notes?: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
  finalized_at?: string;
}

export interface RDStudyCreate {
  name: string;
  client_id: string;
  engagement_id?: string;
  tax_year: number;
  entity_type: RDEntityType;
  entity_name: string;
  ein?: string;
  fiscal_year_start: string;
  fiscal_year_end: string;
  is_short_year?: boolean;
  short_year_days?: number;
  is_controlled_group?: boolean;
  controlled_group_name?: string;
  states?: string[];
  primary_state?: string;
  notes?: string;
}

export interface RDProject {
  id: string;
  study_id: string;
  name: string;
  code?: string;
  description?: string;
  department?: string;
  business_component?: string;
  start_date?: string;
  end_date?: string;
  is_ongoing: boolean;
  qualification_status: RDQualificationStatus;
  permitted_purpose_score?: number;
  technological_nature_score?: number;
  uncertainty_score?: number;
  experimentation_score?: number;
  overall_score?: number;
  qualification_narrative?: string;
  cpa_reviewed: boolean;
  cpa_override_status?: RDQualificationStatus;
  cpa_override_reason?: string;
  risk_flags: Array<{ type: string; message: string }>;
  created_at: string;
}

export interface RDEmployee {
  id: string;
  study_id: string;
  employee_id?: string;
  name: string;
  title?: string;
  department?: string;
  total_wages: number;
  qualified_time_percentage: number;
  qualified_wages: number;
  cpa_reviewed: boolean;
  cpa_adjusted_percentage?: number;
  cpa_adjustment_reason?: string;
}

export interface RDQRE {
  id: string;
  study_id: string;
  project_id?: string;
  employee_id?: string;
  category: RDQRECategory;
  subcategory?: string;
  gross_amount: number;
  qualified_percentage: number;
  qualified_amount: number;
  cpa_reviewed: boolean;
  cpa_adjusted_amount?: number;
}

export interface RDCalculationResult {
  study_id: string;
  calculated_at: string;
  federal_regular?: {
    total_qre: number;
    base_amount: number;
    credit_rate: number;
    calculated_credit: number;
    final_credit: number;
  };
  federal_asc?: {
    total_qre: number;
    base_amount: number;
    credit_rate: number;
    calculated_credit: number;
    final_credit: number;
  };
  recommended_method: RDCreditMethod;
  total_federal_credit: number;
  total_state_credits: number;
  total_credits: number;
  state_calculations: Array<{
    state_code: string;
    state_name: string;
    final_credit: number;
  }>;
}

export interface RDReviewItem {
  id: string;
  entity_type: 'project' | 'employee' | 'qre' | 'narrative';
  entity_id: string;
  title: string;
  description: string;
  confidence?: string;
  risk_flags: string[];
  suggested_action: string;
}

// ========================================
// Tax Engine Types
// ========================================

export type TaxFormType =
  | '1040'      // Individual
  | '1120'      // C-Corp
  | '1120S'     // S-Corp
  | '1065'      // Partnership
  | '990'       // Non-profit
  | '941'       // Employer Quarterly
  | '940';      // FUTA

export type TaxReturnStatus =
  | 'draft'
  | 'data_entry'
  | 'review'
  | 'calculating'
  | 'ready_to_file'
  | 'filed'
  | 'accepted'
  | 'rejected'
  | 'amended';

export type FilingStatus =
  | 'single'
  | 'married_filing_jointly'
  | 'married_filing_separately'
  | 'head_of_household'
  | 'qualifying_widow';

export interface TaxReturnSummary {
  id: string;
  client_id: string;
  client_name?: string;
  tax_year: number;
  form_type: TaxFormType;
  filing_status?: FilingStatus;
  status: TaxReturnStatus;
  taxpayer_name: string;
  taxpayer_ssn_last4?: string;
  total_income?: number;
  taxable_income?: number;
  total_tax?: number;
  refund_or_owed?: number;
  due_date?: string;
  filed_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface TaxReturn {
  id: string;
  firm_id: string;
  client_id: string;
  engagement_id?: string;
  tax_year: number;
  form_type: TaxFormType;
  status: TaxReturnStatus;
  // Taxpayer Info
  taxpayer_first_name: string;
  taxpayer_last_name: string;
  taxpayer_ssn?: string;
  taxpayer_dob?: string;
  spouse_first_name?: string;
  spouse_last_name?: string;
  spouse_ssn?: string;
  spouse_dob?: string;
  filing_status: FilingStatus;
  // Address
  address_street: string;
  address_city: string;
  address_state: string;
  address_zip: string;
  // Filing Info
  occupation?: string;
  spouse_occupation?: string;
  presidential_campaign_self?: boolean;
  presidential_campaign_spouse?: boolean;
  // Calculated Values
  total_income?: number;
  adjusted_gross_income?: number;
  taxable_income?: number;
  total_tax?: number;
  total_payments?: number;
  refund_or_owed?: number;
  // State
  state_returns?: string[];
  // Metadata
  preparer_id?: string;
  reviewer_id?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
  filed_at?: string;
}

export interface TaxReturnCreate {
  client_id: string;
  engagement_id?: string;
  tax_year: number;
  form_type: TaxFormType;
  taxpayer_first_name: string;
  taxpayer_last_name: string;
  taxpayer_ssn?: string;
  filing_status: FilingStatus;
  address_street?: string;
  address_city?: string;
  address_state?: string;
  address_zip?: string;
}

export interface TaxCalculationResult {
  tax_return_id: string;
  calculated_at: string;
  calculation_status: 'completed' | 'error' | 'incomplete';
  // Income
  wages: number;
  interest_income: number;
  dividend_income: number;
  business_income: number;
  capital_gains: number;
  other_income: number;
  total_income: number;
  // Adjustments
  adjustments_to_income: number;
  adjusted_gross_income: number;
  // Deductions
  standard_deduction: number;
  itemized_deductions?: number;
  deduction_used: 'standard' | 'itemized';
  qualified_business_income_deduction?: number;
  taxable_income: number;
  // Tax
  regular_tax: number;
  amt?: number;
  niit?: number;
  self_employment_tax?: number;
  total_tax: number;
  // Credits
  child_tax_credit?: number;
  earned_income_credit?: number;
  education_credits?: number;
  other_credits?: number;
  total_credits: number;
  // Payments
  withholding: number;
  estimated_payments: number;
  other_payments: number;
  total_payments: number;
  // Result
  refund_or_owed: number;
  // State
  state_tax_liability?: number;
  state_refund_or_owed?: number;
  // Explainability
  calculation_graph?: Record<string, any>;
  warnings?: string[];
}

export interface TaxLineExplanation {
  line: string;
  value: number;
  explanation: string;
  formula?: string;
  inputs: Record<string, number>;
  rules_applied: Array<{
    rule_id: string;
    description: string;
    irs_citation?: string;
  }>;
}

export interface TaxRule {
  id: string;
  tax_year: number;
  jurisdiction: string;
  rule_type: string;
  description: string;
  formula?: string;
  parameters: Record<string, any>;
  irs_citation?: string;
  effective_date: string;
  expiration_date?: string;
}

export interface TaxFormData {
  return_id: string;
  form_type: string;
  lines: Record<string, {
    value: number | string;
    source?: 'manual' | 'calculated' | 'imported';
    locked?: boolean;
  }>;
  updated_at: string;
}

export interface TaxSchedule {
  id: string;
  return_id: string;
  schedule_type: string; // 'A', 'B', 'C', 'D', 'E', 'SE', etc.
  schedule_name: string;
  data: Record<string, any>;
  total?: number;
  is_required: boolean;
  is_complete: boolean;
  updated_at: string;
}

// ========================================
// Fraud Detection Types
// ========================================

export type BankAccountStatus = 'active' | 'disconnected' | 'error' | 'pending';

export type FraudSeverity = 'low' | 'medium' | 'high' | 'critical';

export type AlertStatus = 'new' | 'acknowledged' | 'investigating' | 'resolved' | 'dismissed';

export type FraudCaseStatus = 'open' | 'investigating' | 'pending_review' | 'resolved' | 'closed' | 'false_positive';

export interface BankAccount {
  id: string;
  customer_id: string;
  plaid_item_id: string;
  plaid_account_id: string;
  institution_id: string;
  institution_name: string;
  account_name?: string;
  account_type?: string;
  account_subtype?: string;
  mask?: string;
  status: BankAccountStatus;
  monitoring_enabled: boolean;
  alert_threshold_amount?: number;
  last_sync_at?: string;
  total_transactions: number;
  flagged_transactions: number;
  created_at: string;
  updated_at?: string;
}

export interface BankAccountCreate {
  customer_id: string;
  public_token: string;
  account_id: string;
  institution_id: string;
  institution_name: string;
}

export interface BankAccountUpdate {
  account_name?: string;
  monitoring_enabled?: boolean;
  alert_threshold_amount?: number;
  status?: BankAccountStatus;
}

export interface FraudTransaction {
  id: string;
  bank_account_id: string;
  plaid_transaction_id: string;
  transaction_date: string;
  amount: number;
  description?: string;
  merchant_name?: string;
  category?: string[];
  location?: {
    city?: string;
    region?: string;
    country?: string;
    lat?: number;
    lon?: number;
  };
  payment_channel?: string;
  is_flagged: boolean;
  fraud_score: number;
  risk_level: FraudSeverity;
  flagged_reasons?: {
    rules: string[];
    explanation: string;
  };
  analyzed_at?: string;
  created_at: string;
}

export interface TransactionAnalysis {
  transaction: FraudTransaction;
  model_predictions: Record<string, number>;
  feature_importance: Record<string, number>;
  anomaly_score: number;
  triggered_rules: string[];
  recommendation: string;
}

export interface FraudAlert {
  id: string;
  transaction_id?: string;
  fraud_case_id?: string;
  alert_type: string;
  severity: FraudSeverity;
  status: AlertStatus;
  message: string;
  details?: Record<string, any>;
  triggered_rules?: string[];
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolved_by?: string;
  resolved_at?: string;
  resolution_action?: string;
  created_at: string;
}

export interface FraudAlertUpdate {
  status: AlertStatus;
  resolution_action?: string;
}

export interface FraudCase {
  id: string;
  case_number: string;
  customer_id: string;
  bank_account_id?: string;
  transaction_id?: string;
  title: string;
  description?: string;
  severity: FraudSeverity;
  status: FraudCaseStatus;
  fraud_type?: string;
  estimated_loss_amount?: number;
  actual_loss_amount?: number;
  detected_patterns?: string[];
  investigation_notes?: string;
  resolution_notes?: string;
  false_positive_reason?: string;
  assigned_to?: string;
  acknowledged_at?: string;
  resolved_at?: string;
  closed_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface FraudCaseCreate {
  customer_id: string;
  bank_account_id?: string;
  transaction_id?: string;
  title: string;
  description?: string;
  severity: FraudSeverity;
  fraud_type?: string;
  estimated_loss_amount?: number;
}

export interface FraudCaseUpdate {
  title?: string;
  description?: string;
  status?: FraudCaseStatus;
  severity?: FraudSeverity;
  assigned_to?: string;
  investigation_notes?: string;
  resolution_notes?: string;
  false_positive_reason?: string;
}

export interface FraudCaseActivity {
  id: string;
  fraud_case_id: string;
  activity_type: string;
  description: string;
  details?: Record<string, any>;
  user_id: string;
  created_at: string;
}

export interface FraudCaseActivityCreate {
  activity_type: string;
  description: string;
  details?: Record<string, any>;
}

export interface FraudFeatureFlag {
  id: string;
  customer_id: string;
  is_enabled: boolean;
  real_time_monitoring: boolean;
  ml_detection: boolean;
  rule_based_detection: boolean;
  anomaly_detection: boolean;
  alert_email: boolean;
  alert_sms: boolean;
  alert_webhook: boolean;
  webhook_url?: string;
  min_alert_severity: FraudSeverity;
  auto_case_creation_threshold: number;
  daily_transaction_limit?: number;
  high_risk_amount_threshold?: number;
  enabled_at?: string;
  enabled_by?: string;
  created_at: string;
  updated_at?: string;
}

export interface FraudFeatureFlagUpdate {
  is_enabled?: boolean;
  real_time_monitoring?: boolean;
  ml_detection?: boolean;
  rule_based_detection?: boolean;
  anomaly_detection?: boolean;
  alert_email?: boolean;
  alert_sms?: boolean;
  alert_webhook?: boolean;
  webhook_url?: string;
  min_alert_severity?: FraudSeverity;
  auto_case_creation_threshold?: number;
  daily_transaction_limit?: number;
  high_risk_amount_threshold?: number;
}

export interface FraudStatistics {
  total_transactions: number;
  flagged_transactions: number;
  flagged_percentage: number;
  total_cases: number;
  open_cases: number;
  resolved_cases: number;
  total_alerts: number;
  critical_alerts: number;
  average_fraud_score: number;
  total_potential_loss: number;
  false_positive_rate?: number;
}

export interface FraudDashboardMetrics {
  today_transactions: number;
  today_flagged: number;
  new_alerts: number;
  open_cases: number;
  total_monitored_accounts: number;
  active_customers: number;
  average_risk_score: number;
  top_fraud_types: Array<{ type: string; count: number }>;
  recent_alerts: FraudAlert[];
}

export interface PlaidLinkTokenResponse {
  link_token: string;
  expiration: string;
}
