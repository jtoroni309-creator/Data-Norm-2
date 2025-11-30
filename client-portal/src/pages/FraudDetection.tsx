/**
 * Fraud Detection Dashboard
 * Real-time fraud monitoring service for CPA firms to offer clients
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldAlert,
  AlertTriangle,
  Activity,
  TrendingUp,
  DollarSign,
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  ChevronRight,
  Plus,
  Search,
  Filter,
  Bell,
  Building,
  CreditCard,
  RefreshCw,
  Zap,
  Target,
  BarChart3,
  Users,
  Wallet,
  X,
  Settings,
  Link2,
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { fraudDetectionService } from '../services/fraud-detection.service';
import {
  FraudCase,
  FraudAlert,
  FraudTransaction,
  FraudDashboardMetrics,
  BankAccount,
  FraudSeverity,
  FraudCaseStatus,
  AlertStatus,
} from '../types';

type TabType = 'overview' | 'alerts' | 'cases' | 'transactions' | 'accounts' | 'settings';

const FraudDetection: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [metrics, setMetrics] = useState<FraudDashboardMetrics | null>(null);
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [cases, setCases] = useState<FraudCase[]>([]);
  const [transactions, setTransactions] = useState<FraudTransaction[]>([]);
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [metricsData, alertsData, casesData] = await Promise.all([
        fraudDetectionService.getDashboardMetrics(),
        fraudDetectionService.listAlerts({ limit: 20 }),
        fraudDetectionService.listFraudCases({ limit: 20 }),
      ]);
      setMetrics(metricsData);
      setAlerts(alertsData);
      setCases(casesData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // Use mock data for demo
      setMetrics(generateMockMetrics());
      setAlerts(generateMockAlerts());
      setCases(generateMockCases());
    } finally {
      setLoading(false);
    }
  };

  const generateMockMetrics = (): FraudDashboardMetrics => ({
    today_transactions: 1247,
    today_flagged: 23,
    new_alerts: 8,
    open_cases: 12,
    total_monitored_accounts: 156,
    active_customers: 45,
    average_risk_score: 0.15,
    top_fraud_types: [
      { type: 'Account Takeover', count: 15 },
      { type: 'Payment Fraud', count: 12 },
      { type: 'Identity Theft', count: 8 },
      { type: 'Wire Fraud', count: 5 },
    ],
    recent_alerts: [],
  });

  const generateMockAlerts = (): FraudAlert[] => [
    {
      id: '1',
      transaction_id: 't1',
      alert_type: 'high_risk_transaction',
      severity: 'critical',
      status: 'new',
      message: 'Unusual wire transfer of $45,000 to foreign account',
      triggered_rules: ['LARGE_AMOUNT', 'FOREIGN_TRANSACTION'],
      created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    },
    {
      id: '2',
      transaction_id: 't2',
      alert_type: 'velocity_spike',
      severity: 'high',
      status: 'acknowledged',
      message: '15 transactions in 1 hour from same merchant',
      triggered_rules: ['HIGH_VELOCITY'],
      acknowledged_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    },
    {
      id: '3',
      transaction_id: 't3',
      alert_type: 'anomaly_detected',
      severity: 'medium',
      status: 'new',
      message: 'Transaction pattern deviation detected',
      triggered_rules: ['UNUSUAL_AMOUNT'],
      created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    },
    {
      id: '4',
      transaction_id: 't4',
      alert_type: 'suspicious_time',
      severity: 'medium',
      status: 'resolved',
      message: 'Large transaction at 3:00 AM',
      triggered_rules: ['SUSPICIOUS_TIME', 'LARGE_AMOUNT'],
      resolved_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
      created_at: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    },
  ];

  const generateMockCases = (): FraudCase[] => [
    {
      id: '1',
      case_number: 'FRAUD-20250228-A1B2C3D4',
      customer_id: 'c1',
      title: 'Suspected Account Takeover - Johnson Corp',
      description: 'Multiple unauthorized transfers detected',
      severity: 'critical',
      status: 'investigating',
      fraud_type: 'account_takeover',
      estimated_loss_amount: 125000,
      detected_patterns: ['FOREIGN_TRANSACTION', 'HIGH_VELOCITY', 'LARGE_AMOUNT'],
      assigned_to: 'John Smith',
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    },
    {
      id: '2',
      case_number: 'FRAUD-20250227-E5F6G7H8',
      customer_id: 'c2',
      title: 'Wire Fraud Attempt - Tech Solutions LLC',
      description: 'Suspicious wire request intercepted',
      severity: 'high',
      status: 'open',
      fraud_type: 'wire_fraud',
      estimated_loss_amount: 50000,
      detected_patterns: ['UNUSUAL_AMOUNT', 'FOREIGN_TRANSACTION'],
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    },
    {
      id: '3',
      case_number: 'FRAUD-20250226-I9J0K1L2',
      customer_id: 'c3',
      title: 'Payment Card Fraud - Martinez Consulting',
      description: 'Multiple fraudulent charges detected',
      severity: 'medium',
      status: 'resolved',
      fraud_type: 'payment_fraud',
      estimated_loss_amount: 8500,
      actual_loss_amount: 0,
      resolution_notes: 'All charges reversed successfully',
      resolved_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
    },
  ];

  const getSeverityConfig = (severity: FraudSeverity) => {
    const configs: Record<FraudSeverity, { color: string; bgColor: string; icon: React.ElementType }> = {
      critical: { color: 'text-red-700', bgColor: 'bg-red-100', icon: XCircle },
      high: { color: 'text-orange-700', bgColor: 'bg-orange-100', icon: AlertTriangle },
      medium: { color: 'text-yellow-700', bgColor: 'bg-yellow-100', icon: Eye },
      low: { color: 'text-green-700', bgColor: 'bg-green-100', icon: CheckCircle },
    };
    return configs[severity] || configs.medium;
  };

  const getStatusConfig = (status: FraudCaseStatus | AlertStatus) => {
    const configs: Record<string, { color: string; bgColor: string; label: string }> = {
      new: { color: 'text-blue-700', bgColor: 'bg-blue-100', label: 'New' },
      open: { color: 'text-blue-700', bgColor: 'bg-blue-100', label: 'Open' },
      acknowledged: { color: 'text-yellow-700', bgColor: 'bg-yellow-100', label: 'Acknowledged' },
      investigating: { color: 'text-purple-700', bgColor: 'bg-purple-100', label: 'Investigating' },
      pending_review: { color: 'text-orange-700', bgColor: 'bg-orange-100', label: 'Pending Review' },
      resolved: { color: 'text-green-700', bgColor: 'bg-green-100', label: 'Resolved' },
      closed: { color: 'text-gray-700', bgColor: 'bg-gray-100', label: 'Closed' },
      dismissed: { color: 'text-gray-700', bgColor: 'bg-gray-100', label: 'Dismissed' },
      false_positive: { color: 'text-gray-700', bgColor: 'bg-gray-100', label: 'False Positive' },
    };
    return configs[status] || configs.open;
  };

  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const tabs: { id: TabType; label: string; icon: React.ElementType }[] = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'alerts', label: 'Alerts', icon: Bell },
    { id: 'cases', label: 'Cases', icon: ShieldAlert },
    { id: 'transactions', label: 'Transactions', icon: CreditCard },
    { id: 'accounts', label: 'Accounts', icon: Building },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-red-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading fraud detection...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <ShieldAlert className="w-7 h-7 text-red-600" />
            Fraud Detection
          </h1>
          <p className="text-gray-600 mt-1">
            Real-time monitoring and fraud prevention for your clients
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadDashboardData}
            className="fluent-btn-secondary"
          >
            <RefreshCw className="w-5 h-5" />
            Refresh
          </button>
          <button className="fluent-btn-primary">
            <Plus className="w-5 h-5" />
            Connect Account
          </button>
        </div>
      </div>

      {/* Real-Time Status Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-4 text-white"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <p className="font-semibold">Real-Time Monitoring Active</p>
              <p className="text-sm text-green-100">
                {metrics?.total_monitored_accounts || 0} accounts monitored across {metrics?.active_customers || 0} clients
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
            <span className="text-sm">Live</span>
          </div>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Today's Transactions</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics?.today_transactions.toLocaleString()}
              </p>
              <p className="text-xs text-red-600 mt-1">
                {metrics?.today_flagged} flagged ({((metrics?.today_flagged || 0) / (metrics?.today_transactions || 1) * 100).toFixed(1)}%)
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">New Alerts</p>
              <p className="text-2xl font-bold text-red-600">{metrics?.new_alerts}</p>
              <p className="text-xs text-gray-500 mt-1">Requires attention</p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <Bell className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Open Cases</p>
              <p className="text-2xl font-bold text-orange-600">{metrics?.open_cases}</p>
              <p className="text-xs text-gray-500 mt-1">Under investigation</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <Target className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Risk Score</p>
              <p className="text-2xl font-bold text-green-600">
                {((metrics?.average_risk_score || 0) * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">Low risk baseline</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex gap-1 p-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-red-100 text-red-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                  {tab.id === 'alerts' && (metrics?.new_alerts || 0) > 0 && (
                    <span className="px-1.5 py-0.5 bg-red-500 text-white text-xs rounded-full">
                      {metrics?.new_alerts}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <OverviewTab
              metrics={metrics}
              alerts={alerts}
              cases={cases}
              onViewCase={(id) => navigate(`/firm/fraud-detection/cases/${id}`)}
            />
          )}
          {activeTab === 'alerts' && (
            <AlertsTab
              alerts={alerts}
              getSeverityConfig={getSeverityConfig}
              getStatusConfig={getStatusConfig}
              formatTimeAgo={formatTimeAgo}
            />
          )}
          {activeTab === 'cases' && (
            <CasesTab
              cases={cases}
              getSeverityConfig={getSeverityConfig}
              getStatusConfig={getStatusConfig}
              formatCurrency={formatCurrency}
              formatTimeAgo={formatTimeAgo}
              onViewCase={(id) => navigate(`/firm/fraud-detection/cases/${id}`)}
            />
          )}
          {activeTab === 'transactions' && <TransactionsTab />}
          {activeTab === 'accounts' && <AccountsTab />}
          {activeTab === 'settings' && <SettingsTab />}
        </div>
      </div>
    </div>
  );
};

// Overview Tab
const OverviewTab: React.FC<{
  metrics: FraudDashboardMetrics | null;
  alerts: FraudAlert[];
  cases: FraudCase[];
  onViewCase: (id: string) => void;
}> = ({ metrics, alerts, cases, onViewCase }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Top Fraud Types */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-gray-600" />
          Top Fraud Types
        </h3>
        <div className="space-y-3">
          {metrics?.top_fraud_types.map((type, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-gray-700">{type.type}</span>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-500 rounded-full"
                    style={{ width: `${(type.count / (metrics.top_fraud_types[0]?.count || 1)) * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-gray-600 w-8">{type.count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5 text-gray-600" />
          Recent Alerts
        </h3>
        <div className="space-y-3">
          {alerts.slice(0, 4).map((alert) => (
            <div key={alert.id} className="flex items-start gap-3 p-2 bg-white rounded-lg">
              <div className={`p-1 rounded ${
                alert.severity === 'critical' ? 'bg-red-100' :
                alert.severity === 'high' ? 'bg-orange-100' : 'bg-yellow-100'
              }`}>
                <AlertTriangle className={`w-4 h-4 ${
                  alert.severity === 'critical' ? 'text-red-600' :
                  alert.severity === 'high' ? 'text-orange-600' : 'text-yellow-600'
                }`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{alert.message}</p>
                <p className="text-xs text-gray-500">{new Date(alert.created_at).toLocaleString()}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Active Cases */}
      <div className="lg:col-span-2 bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-gray-600" />
          Active Cases
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs font-semibold text-gray-500 uppercase">
                <th className="pb-3">Case</th>
                <th className="pb-3">Severity</th>
                <th className="pb-3">Status</th>
                <th className="pb-3">Est. Loss</th>
                <th className="pb-3">Assigned</th>
                <th className="pb-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {cases.filter(c => c.status !== 'resolved' && c.status !== 'closed').slice(0, 5).map((fraudCase) => (
                <tr key={fraudCase.id} className="hover:bg-white">
                  <td className="py-3">
                    <p className="font-medium text-gray-900">{fraudCase.title}</p>
                    <p className="text-xs text-gray-500">{fraudCase.case_number}</p>
                  </td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      fraudCase.severity === 'critical' ? 'bg-red-100 text-red-700' :
                      fraudCase.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {fraudCase.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className="text-sm text-gray-600">{fraudCase.status.replace('_', ' ')}</span>
                  </td>
                  <td className="py-3">
                    <span className="text-sm font-medium text-red-600">
                      ${(fraudCase.estimated_loss_amount || 0).toLocaleString()}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className="text-sm text-gray-600">{fraudCase.assigned_to || 'Unassigned'}</span>
                  </td>
                  <td className="py-3">
                    <button
                      onClick={() => onViewCase(fraudCase.id)}
                      className="p-1 hover:bg-gray-200 rounded"
                    >
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Alerts Tab
const AlertsTab: React.FC<{
  alerts: FraudAlert[];
  getSeverityConfig: (severity: FraudSeverity) => { color: string; bgColor: string; icon: React.ElementType };
  getStatusConfig: (status: FraudCaseStatus | AlertStatus) => { color: string; bgColor: string; label: string };
  formatTimeAgo: (date: string) => string;
}> = ({ alerts, getSeverityConfig, getStatusConfig, formatTimeAgo }) => {
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredAlerts = alerts.filter(a => statusFilter === 'all' || a.status === statusFilter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Fraud Alerts</h3>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        >
          <option value="all">All Statuses</option>
          <option value="new">New</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
        </select>
      </div>

      <div className="space-y-3">
        {filteredAlerts.map((alert) => {
          const sevConfig = getSeverityConfig(alert.severity);
          const SevIcon = sevConfig.icon;
          const statusConfig = getStatusConfig(alert.status);

          return (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start gap-4">
                <div className={`p-2 rounded-lg ${sevConfig.bgColor}`}>
                  <SevIcon className={`w-5 h-5 ${sevConfig.color}`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{alert.message}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${sevConfig.bgColor} ${sevConfig.color}`}>
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusConfig.bgColor} ${statusConfig.color}`}>
                          {statusConfig.label}
                        </span>
                        {alert.triggered_rules && (
                          <span className="text-xs text-gray-500">
                            Rules: {alert.triggered_rules.join(', ')}
                          </span>
                        )}
                      </div>
                    </div>
                    <span className="text-sm text-gray-500">{formatTimeAgo(alert.created_at)}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

// Cases Tab
const CasesTab: React.FC<{
  cases: FraudCase[];
  getSeverityConfig: (severity: FraudSeverity) => { color: string; bgColor: string; icon: React.ElementType };
  getStatusConfig: (status: FraudCaseStatus | AlertStatus) => { color: string; bgColor: string; label: string };
  formatCurrency: (amount: number | undefined) => string;
  formatTimeAgo: (date: string) => string;
  onViewCase: (id: string) => void;
}> = ({ cases, getSeverityConfig, getStatusConfig, formatCurrency, formatTimeAgo, onViewCase }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Fraud Cases</h3>
        <button className="fluent-btn-primary text-sm">
          <Plus className="w-4 h-4" />
          Create Case
        </button>
      </div>

      <div className="space-y-3">
        {cases.map((fraudCase) => {
          const sevConfig = getSeverityConfig(fraudCase.severity);
          const statusConfig = getStatusConfig(fraudCase.status);

          return (
            <motion.div
              key={fraudCase.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={() => onViewCase(fraudCase.id)}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium text-gray-900">{fraudCase.title}</h4>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${sevConfig.bgColor} ${sevConfig.color}`}>
                      {fraudCase.severity.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{fraudCase.case_number}</p>
                  {fraudCase.description && (
                    <p className="text-sm text-gray-600 mt-2">{fraudCase.description}</p>
                  )}
                  <div className="flex items-center gap-4 mt-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${statusConfig.bgColor} ${statusConfig.color}`}>
                      {statusConfig.label}
                    </span>
                    {fraudCase.estimated_loss_amount && (
                      <span className="text-sm text-red-600 font-medium">
                        Est. Loss: {formatCurrency(fraudCase.estimated_loss_amount)}
                      </span>
                    )}
                    {fraudCase.assigned_to && (
                      <span className="text-sm text-gray-500">
                        Assigned: {fraudCase.assigned_to}
                      </span>
                    )}
                    <span className="text-sm text-gray-400">
                      {formatTimeAgo(fraudCase.created_at)}
                    </span>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

// Transactions Tab
const TransactionsTab: React.FC = () => {
  return (
    <div className="text-center py-12">
      <CreditCard className="w-12 h-12 text-gray-300 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">Transaction Monitor</h3>
      <p className="text-gray-600 mb-4">
        Connect bank accounts to monitor transactions in real-time
      </p>
      <button className="fluent-btn-primary">
        <Link2 className="w-5 h-5" />
        Connect Bank Account
      </button>
    </div>
  );
};

// Accounts Tab
const AccountsTab: React.FC = () => {
  return (
    <div className="text-center py-12">
      <Building className="w-12 h-12 text-gray-300 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">Connected Accounts</h3>
      <p className="text-gray-600 mb-4">
        No bank accounts connected yet. Connect via Plaid to enable fraud monitoring.
      </p>
      <button className="fluent-btn-primary">
        <Plus className="w-5 h-5" />
        Connect Account
      </button>
    </div>
  );
};

// Settings Tab
const SettingsTab: React.FC = () => {
  const [settings, setSettings] = useState({
    ml_detection: true,
    rule_based_detection: true,
    anomaly_detection: true,
    real_time_monitoring: true,
    alert_email: true,
    alert_sms: false,
    auto_case_threshold: 0.75,
    high_risk_threshold: 10000,
  });

  return (
    <div className="max-w-2xl space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Detection Settings</h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <p className="font-medium text-gray-900">ML Detection</p>
            <p className="text-sm text-gray-500">Use machine learning models for fraud detection</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={settings.ml_detection}
              onChange={(e) => setSettings({ ...settings, ml_detection: e.target.checked })}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
          </label>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <p className="font-medium text-gray-900">Rule-Based Detection</p>
            <p className="text-sm text-gray-500">Apply pre-defined fraud detection rules</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={settings.rule_based_detection}
              onChange={(e) => setSettings({ ...settings, rule_based_detection: e.target.checked })}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
          </label>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <p className="font-medium text-gray-900">Anomaly Detection</p>
            <p className="text-sm text-gray-500">Detect unusual transaction patterns</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={settings.anomaly_detection}
              onChange={(e) => setSettings({ ...settings, anomaly_detection: e.target.checked })}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
          </label>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <p className="font-medium text-gray-900">Real-Time Monitoring</p>
            <p className="text-sm text-gray-500">Process transactions in real-time via webhooks</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={settings.real_time_monitoring}
              onChange={(e) => setSettings({ ...settings, real_time_monitoring: e.target.checked })}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
          </label>
        </div>
      </div>

      <h3 className="text-lg font-semibold text-gray-900 mt-8">Alert Settings</h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <p className="font-medium text-gray-900">Email Alerts</p>
            <p className="text-sm text-gray-500">Send alerts via email</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={settings.alert_email}
              onChange={(e) => setSettings({ ...settings, alert_email: e.target.checked })}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
          </label>
        </div>

        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <p className="font-medium text-gray-900">Auto Case Creation Threshold</p>
            <span className="text-sm font-medium text-gray-600">{(settings.auto_case_threshold * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0.5"
            max="1"
            step="0.05"
            value={settings.auto_case_threshold}
            onChange={(e) => setSettings({ ...settings, auto_case_threshold: parseFloat(e.target.value) })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <p className="text-sm text-gray-500 mt-1">
            Automatically create cases for transactions with fraud score above this threshold
          </p>
        </div>

        <div className="p-4 bg-gray-50 rounded-lg">
          <label className="block">
            <p className="font-medium text-gray-900 mb-2">High Risk Amount Threshold</p>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
              <input
                type="number"
                value={settings.high_risk_threshold}
                onChange={(e) => setSettings({ ...settings, high_risk_threshold: parseInt(e.target.value) })}
                className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Transactions above this amount trigger high-risk alerts
            </p>
          </label>
        </div>
      </div>

      <div className="pt-4">
        <button className="fluent-btn-primary">
          Save Settings
        </button>
      </div>
    </div>
  );
};

export default FraudDetection;
