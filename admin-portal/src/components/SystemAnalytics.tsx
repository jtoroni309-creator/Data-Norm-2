import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Activity,
  Users,
  Globe,
  Smartphone,
  Monitor,
  Clock,
  Database,
  Server,
} from 'lucide-react';

export const SystemAnalytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | '90d'>('7d');

  const analyticsData = {
    userGrowth: {
      current: 1247,
      previous: 1109,
      percentChange: 12.4,
      trend: 'up' as const,
    },
    pageViews: {
      current: 45678,
      previous: 42341,
      percentChange: 7.9,
      trend: 'up' as const,
    },
    avgSessionTime: {
      current: '4m 32s',
      previous: '3m 58s',
      percentChange: 14.2,
      trend: 'up' as const,
    },
    bounceRate: {
      current: 32.5,
      previous: 38.7,
      percentChange: -16.0,
      trend: 'down' as const,
    },
  };

  const deviceBreakdown = [
    { name: 'Desktop', percentage: 58, color: 'bg-blue-500', count: 723 },
    { name: 'Mobile', percentage: 32, color: 'bg-green-500', count: 399 },
    { name: 'Tablet', percentage: 10, color: 'bg-purple-500', count: 125 },
  ];

  const topPages = [
    { path: '/dashboard', views: 12456, uniqueVisitors: 8234, avgTime: '5m 23s' },
    { path: '/analytics', views: 8932, uniqueVisitors: 6721, avgTime: '4m 12s' },
    { path: '/settings', views: 6543, uniqueVisitors: 5432, avgTime: '3m 45s' },
    { path: '/users', views: 5234, uniqueVisitors: 4123, avgTime: '4m 56s' },
    { path: '/reports', views: 4321, uniqueVisitors: 3456, avgTime: '6m 12s' },
  ];

  const geographicData = [
    { country: 'United States', users: 456, percentage: 36.6 },
    { country: 'United Kingdom', users: 234, percentage: 18.8 },
    { country: 'Canada', users: 178, percentage: 14.3 },
    { country: 'Germany', users: 156, percentage: 12.5 },
    { country: 'Australia', users: 98, percentage: 7.9 },
    { country: 'Others', users: 125, percentage: 10.0 },
  ];

  const performanceMetrics = [
    {
      label: 'Server Response Time',
      value: '142ms',
      status: 'good',
      icon: Server,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      label: 'Database Query Time',
      value: '28ms',
      status: 'excellent',
      icon: Database,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      label: 'Page Load Time',
      value: '1.2s',
      status: 'good',
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      label: 'API Response Time',
      value: '89ms',
      status: 'excellent',
      icon: Activity,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">System Analytics</h1>
          <p className="text-gray-600">Comprehensive insights and performance metrics</p>
        </div>
        <div className="flex items-center gap-2 bg-white rounded-xl border border-gray-200 p-1">
          {(['24h', '7d', '30d', '90d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                timeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-md border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div
              className={`flex items-center gap-1 text-sm font-medium ${
                analyticsData.userGrowth.trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {analyticsData.userGrowth.trend === 'up' ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              {Math.abs(analyticsData.userGrowth.percentChange)}%
            </div>
          </div>
          <h3 className="text-gray-600 text-sm font-medium mb-1">Total Users</h3>
          <p className="text-3xl font-bold text-gray-900">{analyticsData.userGrowth.current.toLocaleString()}</p>
          <p className="text-sm text-gray-500 mt-2">vs {analyticsData.userGrowth.previous.toLocaleString()} previous</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-md border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-green-600" />
            </div>
            <div
              className={`flex items-center gap-1 text-sm font-medium ${
                analyticsData.pageViews.trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {analyticsData.pageViews.trend === 'up' ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              {Math.abs(analyticsData.pageViews.percentChange)}%
            </div>
          </div>
          <h3 className="text-gray-600 text-sm font-medium mb-1">Page Views</h3>
          <p className="text-3xl font-bold text-gray-900">{analyticsData.pageViews.current.toLocaleString()}</p>
          <p className="text-sm text-gray-500 mt-2">vs {analyticsData.pageViews.previous.toLocaleString()} previous</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-md border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
              <Clock className="w-6 h-6 text-purple-600" />
            </div>
            <div
              className={`flex items-center gap-1 text-sm font-medium ${
                analyticsData.avgSessionTime.trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {analyticsData.avgSessionTime.trend === 'up' ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              {Math.abs(analyticsData.avgSessionTime.percentChange)}%
            </div>
          </div>
          <h3 className="text-gray-600 text-sm font-medium mb-1">Avg Session Time</h3>
          <p className="text-3xl font-bold text-gray-900">{analyticsData.avgSessionTime.current}</p>
          <p className="text-sm text-gray-500 mt-2">vs {analyticsData.avgSessionTime.previous} previous</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-md border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
              <Activity className="w-6 h-6 text-orange-600" />
            </div>
            <div
              className={`flex items-center gap-1 text-sm font-medium ${
                analyticsData.bounceRate.trend === 'down' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {analyticsData.bounceRate.trend === 'down' ? (
                <TrendingDown className="w-4 h-4" />
              ) : (
                <TrendingUp className="w-4 h-4" />
              )}
              {Math.abs(analyticsData.bounceRate.percentChange)}%
            </div>
          </div>
          <h3 className="text-gray-600 text-sm font-medium mb-1">Bounce Rate</h3>
          <p className="text-3xl font-bold text-gray-900">{analyticsData.bounceRate.current}%</p>
          <p className="text-sm text-gray-500 mt-2">vs {analyticsData.bounceRate.previous}% previous</p>
        </motion.div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Device Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-xl shadow-md border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Device Breakdown</h2>
            <PieChart className="w-5 h-5 text-gray-400" />
          </div>
          <div className="space-y-4">
            {deviceBreakdown.map((device, index) => (
              <div key={device.name} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    {device.name === 'Desktop' && <Monitor className="w-4 h-4 text-gray-600" />}
                    {device.name === 'Mobile' && <Smartphone className="w-4 h-4 text-gray-600" />}
                    {device.name === 'Tablet' && <Smartphone className="w-4 h-4 text-gray-600" />}
                    <span className="font-medium text-gray-900">{device.name}</span>
                  </div>
                  <span className="font-semibold text-gray-900">{device.percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${device.percentage}%` }}
                    transition={{ delay: 0.5 + index * 0.1, duration: 0.8 }}
                    className={`h-full ${device.color} rounded-full`}
                  />
                </div>
                <p className="text-xs text-gray-600">{device.count.toLocaleString()} users</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Geographic Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-xl shadow-md border border-gray-200 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Geographic Distribution</h2>
            <Globe className="w-5 h-5 text-gray-400" />
          </div>
          <div className="space-y-3">
            {geographicData.map((location, index) => (
              <div key={location.country} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-xs font-semibold text-blue-600">
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{location.country}</p>
                    <p className="text-xs text-gray-600">{location.users} users</p>
                  </div>
                </div>
                <span className="font-semibold text-gray-900">{location.percentage}%</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Top Pages */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-white rounded-xl shadow-md border border-gray-200 p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Top Pages</h2>
          <BarChart3 className="w-5 h-5 text-gray-400" />
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Page</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Views</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Unique</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Avg Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {topPages.map((page, index) => (
                <tr key={page.path} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-4 font-mono text-sm text-gray-900">{page.path}</td>
                  <td className="px-4 py-4 text-right font-semibold text-gray-900">{page.views.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right text-gray-600">{page.uniqueVisitors.toLocaleString()}</td>
                  <td className="px-4 py-4 text-right text-gray-600">{page.avgTime}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Performance Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-white rounded-xl shadow-md border border-gray-200 p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Performance Metrics</h2>
          <Activity className="w-5 h-5 text-gray-400" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {performanceMetrics.map((metric, index) => {
            const Icon = metric.icon;
            return (
              <div key={metric.label} className="p-4 bg-gray-50 rounded-xl">
                <div className="flex items-center gap-3 mb-3">
                  <div className={`${metric.bgColor} p-2 rounded-lg`}>
                    <Icon className={`w-5 h-5 ${metric.color}`} />
                  </div>
                  <span className={`text-xs font-semibold uppercase ${metric.color}`}>
                    {metric.status}
                  </span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</p>
                <p className="text-sm text-gray-600">{metric.label}</p>
              </div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
};
