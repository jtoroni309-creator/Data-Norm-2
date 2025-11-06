// Admin Portal Types

export interface Customer {
  id: string;
  company_name: string;
  contact_name: string;
  contact_email: string;
  contact_phone?: string;
  industry?: string;
  company_size?: 'small' | 'medium' | 'large' | 'enterprise';
  status: CustomerStatus;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export enum CustomerStatus {
  ACTIVE = 'active',
  TRIAL = 'trial',
  SUSPENDED = 'suspended',
  CANCELLED = 'cancelled',
  PENDING = 'pending',
}

export interface License {
  id: string;
  customer_id: string;
  plan_type: PlanType;
  status: LicenseStatus;
  seats: number;
  seats_used: number;
  features: string[];
  start_date: string;
  end_date: string;
  trial_ends_at?: string;
  auto_renew: boolean;
  billing_cycle: BillingCycle;
  price_per_month: number;
  created_at: string;
  updated_at: string;
}

export enum PlanType {
  STARTER = 'starter',
  PROFESSIONAL = 'professional',
  ENTERPRISE = 'enterprise',
  CUSTOM = 'custom',
}

export enum LicenseStatus {
  ACTIVE = 'active',
  TRIAL = 'trial',
  EXPIRED = 'expired',
  CANCELLED = 'cancelled',
  SUSPENDED = 'suspended',
}

export enum BillingCycle {
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  ANNUALLY = 'annually',
}

export interface UsageMetrics {
  customer_id: string;
  period_start: string;
  period_end: string;
  engagements_count: number;
  users_count: number;
  analytics_runs: number;
  qc_checks: number;
  normalize_operations: number;
  storage_gb: number;
  api_calls: number;
}

export interface CustomerMetrics {
  total_customers: number;
  active_customers: number;
  trial_customers: number;
  churned_this_month: number;
  revenue_mrr: number;
  revenue_arr: number;
  average_seats_per_customer: number;
  total_seats: number;
  seats_utilized: number;
}

export interface ActivityLog {
  id: string;
  customer_id: string;
  user_id?: string;
  action: string;
  description: string;
  ip_address?: string;
  user_agent?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Invoice {
  id: string;
  customer_id: string;
  invoice_number: string;
  amount: number;
  tax: number;
  total: number;
  status: InvoiceStatus;
  due_date: string;
  paid_date?: string;
  items: InvoiceItem[];
  created_at: string;
}

export enum InvoiceStatus {
  DRAFT = 'draft',
  SENT = 'sent',
  PAID = 'paid',
  OVERDUE = 'overdue',
  CANCELLED = 'cancelled',
}

export interface InvoiceItem {
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

export interface SupportTicket {
  id: string;
  customer_id: string;
  user_id?: string;
  subject: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  assigned_to?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
}

export enum TicketStatus {
  OPEN = 'open',
  IN_PROGRESS = 'in_progress',
  WAITING = 'waiting',
  RESOLVED = 'resolved',
  CLOSED = 'closed',
}

export enum TicketPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export interface CustomerSettings {
  customer_id: string;
  branding: {
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
  };
  features: {
    analytics_enabled: boolean;
    normalize_enabled: boolean;
    qc_enabled: boolean;
    api_access: boolean;
    sso_enabled: boolean;
  };
  limits: {
    max_users: number;
    max_engagements: number;
    max_storage_gb: number;
    api_rate_limit: number;
  };
  notifications: {
    email_alerts: boolean;
    usage_warnings: boolean;
    billing_reminders: boolean;
  };
}

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  role: AdminRole;
  permissions: string[];
  created_at: string;
  last_login?: string;
}

export enum AdminRole {
  SUPER_ADMIN = 'super_admin',
  ADMIN = 'admin',
  SUPPORT = 'support',
  BILLING = 'billing',
}
