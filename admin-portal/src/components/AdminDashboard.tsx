import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  Users,
  TrendingUp,
  Activity,
  DollarSign,
  Shield,
  Server,
  Database,
  Clock,
  AlertTriangle,
  CheckCircle,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';

interface DashboardStats {
  totalUsers: number;
  activeUsers: number;
  totalRevenue: number;
  systemUptime: number;
  activeIncidents: number;
  resolvedToday: number;
  apiCalls: number;
  avgResponseTime: number;
}

interface ActivityItem {
  id: string;
  type: 'user' | 'system' | 'security' | 'revenue';
  message: string;
  timestamp: Date;
  severity?: 'info' | 'warning' | 'success' | 'error';
}

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 1247,
    activeUsers: 892,
    totalRevenue: 156789,
    systemUptime: 99.97,
    activeIncidents: 3,
    resolvedToday: 12,
    apiCalls: 2456789,
    avgResponseTime: 142,
  });

  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([
    {
      id: '1',
      type: 'user',
      message: 'New user registration: john.doe@example.com',
      timestamp: new Date(Date.now() - 5 * 60000),
      severity: 'success',
    },
    {
      id: '2',
      type: 'system',
      message: 'Database backup completed successfully',
      timestamp: new Date(Date.now() - 15 * 60000),
      severity: 'success',
    },
    {
      id: '3',
      type: 'security',
      message: 'Failed login attempt detected - IP blocked',
      timestamp: new Date(Date.now() - 30 * 60000),
      severity: 'warning',
    },
    {
      id: '4',
      type: 'revenue',
      message: 'New subscription: Enterprise Plan - $499/mo',
      timestamp: new Date(Date.now() - 45 * 60000),
      severity: 'success',
    },
  ]);

  const statCards = [
    {
      title: 'Total Users',
      value: stats.totalUsers.toLocaleString(),
      change: '+12.5%',
      isPositive: true,
      icon: Users,
      color: 'blue',
      bgColor: 'bg-blue-500',
      lightBg: 'bg-blue-50',
    },
    {
      title: 'Active Now',
      value: stats.activeUsers.toLocaleString(),
      change: '+8.2%',
      isPositive: true,
      icon: Activity,
      color: 'green',
      bgColor: 'bg-green-500',
      lightBg: 'bg-green-50',
    },
    {
      title: 'Monthly Revenue',
      value: `$${(stats.totalRevenue / 1000).toFixed(1)}k`,
      change: '+23.1%',
      isPositive: true,
      icon: DollarSign,
      color: 'purple',
      bgColor: 'bg-purple-500',
      lightBg: 'bg-purple-50',
    },
    {
      title: 'System Uptime',
      value: `${stats.systemUptime}%`,
      change: 'Stable',
      isPositive: true,
      icon: Server,
      color: 'orange',
      bgColor: 'bg-orange-500',
      lightBg: 'bg-orange-50',
    },
    {
      title: 'API Calls',
      value: `${(stats.apiCalls / 1000000).toFixed(2)}M`,
      change: '+15.7%',
      isPositive: true,
      icon: Database,
      color: 'indigo',
      bgColor: 'bg-indigo-500',
      lightBg: 'bg-indigo-50',
    },
    {
      title: 'Avg Response',
      value: `${stats.avgResponseTime}ms`,
      change: '-5.3%',
      isPositive: true,
      icon: Clock,
      color: 'cyan',
      bgColor: 'bg-cyan-500',
      lightBg: 'bg-cyan-50',
    },
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'user':
        return Users;
      case 'system':
        return Server;
      case 'security':
        return Shield;
      case 'revenue':
        return DollarSign;
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard Overview</h1>
        <p className="text-gray-600">
          Monitor system performance, user activity, and key metrics in real-time
        </p>
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
                  <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
                <div
                  className={`flex items-center gap-1 text-sm font-medium ${
                    stat.isPositive ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {stat.isPositive ? (
                    <ArrowUpRight className="w-4 h-4" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4" />
                  )}
                  {stat.change}
                </div>
              </div>
              <h3 className="text-gray-600 text-sm font-medium mb-1">{stat.title}</h3>
              <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
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
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm text-gray-600">All systems operational</span>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <Server className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">API Services</h4>
                  <p className="text-sm text-gray-600">Response time: {stats.avgResponseTime}ms</p>
                </div>
              </div>
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Database className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Database</h4>
                  <p className="text-sm text-gray-600">Connections: 234/1000</p>
                </div>
              </div>
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Shield className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Security</h4>
                  <p className="text-sm text-gray-600">3 active monitors</p>
                </div>
              </div>
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>

            <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-yellow-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Cache Server</h4>
                  <p className="text-sm text-gray-600">Memory usage: 87%</p>
                </div>
              </div>
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
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
            {recentActivity.map((activity, index) => {
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
            })}
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
            <h3 className="text-lg font-semibold">Active Incidents</h3>
            <AlertTriangle className="w-6 h-6" />
          </div>
          <p className="text-4xl font-bold">{stats.activeIncidents}</p>
          <p className="text-blue-100 text-sm mt-2">Requires attention</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-md p-6 text-white"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Resolved Today</h3>
            <CheckCircle className="w-6 h-6" />
          </div>
          <p className="text-4xl font-bold">{stats.resolvedToday}</p>
          <p className="text-green-100 text-sm mt-2">Great progress!</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
          className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-md p-6 text-white"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Performance</h3>
            <TrendingUp className="w-6 h-6" />
          </div>
          <p className="text-4xl font-bold">Excellent</p>
          <p className="text-purple-100 text-sm mt-2">All metrics in range</p>
        </motion.div>
      </div>
    </div>
  );
};
