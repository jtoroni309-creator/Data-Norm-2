/**
 * Admin Portal Type Definitions
 */

// Customer (CPA Firm) Types
export interface Customer {
  id: string;
  firmName: string;
  firmEin: string;
  status: CustomerStatus;
  subscriptionTier: SubscriptionTier;
  billingEmail: string;
  primaryContact: {
    name: string;
    email: string;
    phone: string;
  };

  // Limits
  limits: {
    maxUsers: number;
    maxEngagements: number;
    maxStorageGB: number;
    maxClients: number;
  };

  // Current Usage
  usage: {
    currentUsers: number;
    currentEngagements: number;
    currentStorageGB: number;
    currentClients: number;
  };

  // Billing
  billing: {
    monthlyRevenue: number;
    lastPaymentDate: string;
    nextBillingDate: string;
    paymentMethod: string;
    billingStatus: BillingStatus;
  };

  // Metadata
  createdAt: string;
  trialEndsAt?: string;
  lastActivityAt: string;
  onboardingCompleted: boolean;
}

export type CustomerStatus = 'active' | 'trial' | 'suspended' | 'cancelled' | 'pending';
export type BillingStatus = 'current' | 'overdue' | 'pending' | 'failed';

export type SubscriptionTier = 'trial' | 'starter' | 'professional' | 'enterprise' | 'custom';

export interface SubscriptionPlan {
  id: SubscriptionTier;
  name: string;
  description: string;
  monthlyPrice: number;
  yearlyPrice: number;
  limits: {
    users: number;
    engagements: number;
    storageGB: number;
    clients: number;
  };
  features: string[];
  recommended?: boolean;
}

// Dashboard KPIs
export interface DashboardKPIs {
  // Revenue Metrics
  revenue: {
    mrr: number; // Monthly Recurring Revenue
    arr: number; // Annual Recurring Revenue
    growth: number; // Month-over-month growth %
    churn: number; // Churn rate %
  };

  // Customer Metrics
  customers: {
    total: number;
    active: number;
    trial: number;
    churned: number;
    newThisMonth: number;
  };

  // Usage Metrics
  usage: {
    totalUsers: number;
    totalEngagements: number;
    totalStorageGB: number;
    activeEngagements: number;
  };

  // Platform Health
  health: {
    uptime: number; // Percentage
    avgResponseTime: number; // milliseconds
    errorRate: number; // Percentage
    apiCalls24h: number;
  };
}

// Usage Analytics
export interface UsageAnalytics {
  customerId: string;
  period: {
    start: string;
    end: string;
  };

  // User Activity
  users: {
    activeUsers: number;
    logins: number;
    avgSessionDuration: number; // minutes
    byRole: {
      firmAdmin: number;
      firmUser: number;
      client: number;
    };
  };

  // Engagement Activity
  engagements: {
    created: number;
    completed: number;
    inProgress: number;
    byType: {
      audit: number;
      review: number;
      compilation: number;
    };
  };

  // Document Activity
  documents: {
    uploaded: number;
    totalSizeGB: number;
    aiExtractions: number;
  };

  // Integration Activity
  integrations: {
    connected: number;
    syncs: number;
    dataPointsSynced: number;
  };

  // API Usage
  api: {
    totalCalls: number;
    avgResponseTime: number;
    errors: number;
  };
}

// Billing Invoice
export interface Invoice {
  id: string;
  customerId: string;
  invoiceNumber: string;
  amount: number;
  status: 'paid' | 'pending' | 'overdue' | 'failed';
  dueDate: string;
  paidDate?: string;
  lineItems: {
    description: string;
    quantity: number;
    unitPrice: number;
    total: number;
  }[];
  subtotal: number;
  tax: number;
  total: number;
  currency: string;
}

// Activity Log
export interface ActivityLog {
  id: string;
  timestamp: string;
  customerId?: string;
  userId?: string;
  action: string;
  category: 'customer' | 'user' | 'billing' | 'system' | 'security';
  description: string;
  metadata?: Record<string, any>;
  ipAddress?: string;
}

// Platform Statistics
export interface PlatformStats {
  timeRange: 'day' | 'week' | 'month' | 'year';

  // Time series data for charts
  revenueOverTime: {
    date: string;
    value: number;
  }[];

  customersOverTime: {
    date: string;
    active: number;
    trial: number;
    churned: number;
  }[];

  usageOverTime: {
    date: string;
    users: number;
    engagements: number;
    documents: number;
  }[];

  // Top customers by revenue
  topCustomers: {
    customerId: string;
    firmName: string;
    revenue: number;
  }[];

  // Subscription distribution
  subscriptionDistribution: {
    tier: SubscriptionTier;
    count: number;
    revenue: number;
  }[];
}

// Limit Enforcement
export interface LimitCheck {
  limitType: 'users' | 'engagements' | 'storage' | 'clients';
  current: number;
  limit: number;
  percentage: number;
  exceeded: boolean;
  canAdd: boolean;
}

// Customer Creation Request
export interface CreateCustomerRequest {
  firmName: string;
  firmEin: string;
  billingEmail: string;
  primaryContact: {
    name: string;
    email: string;
    phone: string;
  };
  subscriptionTier: SubscriptionTier;

  // Address
  address: {
    line1: string;
    line2?: string;
    city: string;
    state: string;
    postalCode: string;
    country: string;
  };

  // Custom Limits (optional)
  customLimits?: {
    maxUsers?: number;
    maxEngagements?: number;
    maxStorageGB?: number;
    maxClients?: number;
  };
}

// Customer Update Request
export interface UpdateCustomerRequest {
  firmName?: string;
  status?: CustomerStatus;
  subscriptionTier?: SubscriptionTier;
  billingEmail?: string;

  limits?: {
    maxUsers?: number;
    maxEngagements?: number;
    maxStorageGB?: number;
    maxClients?: number;
  };
}

// System Alerts
export interface SystemAlert {
  id: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  category: 'billing' | 'usage' | 'performance' | 'security';
  title: string;
  message: string;
  customerId?: string;
  timestamp: string;
  acknowledged: boolean;
  actionRequired: boolean;
  actionUrl?: string;
}

// Export Summary
export interface ExportData {
  type: 'customers' | 'invoices' | 'usage' | 'analytics';
  format: 'csv' | 'xlsx' | 'json' | 'pdf';
  filters?: Record<string, any>;
  dateRange?: {
    start: string;
    end: string;
  };
}
