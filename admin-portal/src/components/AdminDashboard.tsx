import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  TrendingUp,
  Activity,
  Shield,
  Server,
  Database,
  Clock,
  AlertTriangle,
  CheckCircle,
  ArrowUpRight,
  Building2,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import { dashboardAPI, notificationAPI, type DashboardStats, type Notification } from '../services/api';

interface ActivityItem {
  id: string;
  type: 'user' | 'system' | 'security' | 'revenue';
  message: string;
  timestamp: Date;
  severity?: 'info' | 'warning' | 'success' | 'error';
}

interface SystemHealth {
  status: string;
  services: Record<string, boolean>;
}

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch all dashboard data in parallel
      const [statsData, healthData, notifications] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getHealth(),
        notificationAPI.list().catch(() => []),
      ]);

      setStats(statsData);
      setHealth(healthData);

      // Convert notifications to activity items
      const activities: ActivityItem[] = notifications.slice(0, 5).map((n: Notification) => ({
        id: n.id,
        type: n.type === 'success' ? 'user' : n.type === 'warning' ? 'security' : 'system',
        message: n.message,
        timestamp: new Date(n.timestamp),
        severity: n.type,
      }));
      setRecentActivity(activities);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadDashboardData();
    setIsRefreshing(false);
  };

  const statCards = stats ? [
    {
      title: 'Total Users',
      value: stats.totalUsers.toLocaleString(),
      subtitle: `${stats.activeUsers} active`,
      icon: Users,
      color: 'blue',
      lightBg: 'bg-blue-50',
      iconColor: 'text-blue-600',
    },
    {
      title: 'CPA Firms',
      value: stats.totalFirms.toLocaleString(),
      subtitle: `${stats.activeFirms} active subscriptions`,
      icon: Building2,
      color: 'green',
      lightBg: 'bg-green-50',
      iconColor: 'text-green-600',
    },
    {
      title: 'System Uptime',
      value: `${stats.systemUptime.toFixed(1)}%`,
      subtitle: 'Last 30 days',
      icon: Server,
      color: 'purple',
      lightBg: 'bg-purple-50',
      iconColor: 'text-purple-600',
    },
    {
      title: 'API Calls Today',
      value: stats.apiCallsToday > 1000000
        ? `${(stats.apiCallsToday / 1000000).toFixed(2)}M`
        : stats.apiCallsToday > 1000
          ? `${(stats.apiCallsToday / 1000).toFixed(1)}K`
          : stats.apiCallsToday.toString(),
      subtitle: `Avg ${stats.avgResponseTime}ms response`,
      icon: Database,
      color: 'orange',
      lightBg: 'bg-orange-50',
      iconColor: 'text-orange-600',
    },
    {
      title: 'Engagements',
      value: stats.totalEngagements.toLocaleString(),
      subtitle: `${stats.activeEngagements} in progress`,
      icon: TrendingUp,
      color: 'indigo',
      lightBg: 'bg-indigo-50',
      iconColor: 'text-indigo-600',
    },
    {
      title: 'Avg Response Time',
      value: `${stats.avgResponseTime}ms`,
      subtitle: 'API latency',
      icon: Clock,
      color: 'cyan',
      lightBg: 'bg-cyan-50',
      iconColor: 'text-cyan-600',
    },
  ] : [];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'user':
        return Users;
      case 'system':
        return Server;
      case 'security':
        return Shield;
      default:
        return Activity;
    }
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'success':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diff < 60) return `${diff} seconds ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    return `${Math.floor(diff / 86400)} days ago`;
  };

  const getServiceStatus = (serviceName: string) => {
    if (!health) return 'unknown';
    return health.services[serviceName] ? 'healthy' : 'unhealthy';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-red-800 mb-2">Failed to Load Dashboard</h3>
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={handleRefresh}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard Overview</h1>
          <p className="text-gray-600">
            Monitor system performance, user activity, and key metrics in real-time
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-md border border-gray-200 p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`${stat.lightBg} p-3 rounded-lg`}>
                  <Icon className={`w-6 h-6 ${stat.iconColor}`} />
                </div>
                <ArrowUpRight className="w-4 h-4 text-green-500" />
              </div>
              <h3 className="text-gray-600 text-sm font-medium mb-1">{stat.title}</h3>
              <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-sm text-gray-500 mt-1">{stat.subtitle}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Health */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="lg:col-span-2 bg-white rounded-xl shadow-md border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">System Health</h2>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full animate-pulse ${
                health?.status === 'healthy' ? 'bg-green-500' :
                health?.status === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
              }`}></span>
              <span className="text-sm text-gray-600">
                {health?.status === 'healthy' ? 'All systems operational' :
                 health?.status === 'degraded' ? 'Some services degraded' : 'System issues detected'}
              </span>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  getServiceStatus('api') === 'healthy' ? 'bg-green-100' : 'bg-red-100'
                }`}>
                  <Server className={`w-5 h-5 ${
                    getServiceStatus('api') === 'healthy' ? 'text-green-600' : 'text-red-600'
                  }`} />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">API Services</h4>
                  <p className="text-sm text-gray-600">
                    Response time: {stats?.avgResponseTime || 0}ms
                  </p>
                </div>
              </div>
              {getServiceStatus('api') === 'healthy' ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-red-600" />
              )}
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  getServiceStatus('database') === 'healthy' ? 'bg-blue-100' : 'bg-red-100'
                }`}>
                  <Database className={`w-5 h-5 ${
                    getServiceStatus('database') === 'healthy' ? 'text-blue-600' : 'text-red-600'
                  }`} />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Database</h4>
                  <p className="text-sm text-gray-600">PostgreSQL with pgvector</p>
                </div>
              </div>
              {getServiceStatus('database') === 'healthy' ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-red-600" />
              )}
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  getServiceStatus('cache') === 'healthy' ? 'bg-purple-100' : 'bg-yellow-100'
                }`}>
                  <Shield className={`w-5 h-5 ${
                    getServiceStatus('cache') === 'healthy' ? 'text-purple-600' : 'text-yellow-600'
                  }`} />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Cache Server</h4>
                  <p className="text-sm text-gray-600">Redis cluster</p>
                </div>
              </div>
              {getServiceStatus('cache') === 'healthy' ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-yellow-600" />
              )}
            </div>
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-white rounded-xl shadow-md border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Activity</h2>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>

          <div className="space-y-4">
            {recentActivity.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No recent activity</p>
            ) : (
              recentActivity.map((activity) => {
                const Icon = getActivityIcon(activity.type);
                return (
                  <div
                    key={activity.id}
                    className={`p-4 rounded-lg border ${getSeverityColor(activity.severity)}`}
                  >
                    <div className="flex items-start gap-3">
                      <Icon className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium">{activity.message}</p>
                        <p className="text-xs mt-1 opacity-75">
                          {formatTimestamp(activity.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <button className="w-full mt-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
            View all activity
          </button>
        </motion.div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-md p-6 text-white"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Active Users</h3>
            <Users className="w-6 h-6" />
          </div>
          <p className="text-4xl font-bold">{stats?.activeUsers || 0}</p>
          <p className="text-blue-100 text-sm mt-2">
            of {stats?.totalUsers || 0} total users
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-md p-6 text-white"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Active Firms</h3>
            <Building2 className="w-6 h-6" />
          </div>
          <p className="text-4xl font-bold">{stats?.activeFirms || 0}</p>
          <p className="text-green-100 text-sm mt-2">
            of {stats?.totalFirms || 0} total firms
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
          className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-md p-6 text-white"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">System Status</h3>
            <TrendingUp className="w-6 h-6" />
          </div>
          <p className="text-4xl font-bold">
            {health?.status === 'healthy' ? 'Healthy' :
             health?.status === 'degraded' ? 'Degraded' : 'Issues'}
          </p>
          <p className="text-purple-100 text-sm mt-2">
            {stats?.systemUptime.toFixed(1)}% uptime
          </p>
        </motion.div>
      </div>
    </div>
  );
};
