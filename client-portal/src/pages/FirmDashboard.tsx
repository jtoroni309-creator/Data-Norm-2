/**
 * CPA Firm Dashboard
 * Microsoft Fluent Design inspired dashboard with elegant metrics and insights
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Building2,
  Users,
  Mail,
  FileText,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  UserPlus,
  Settings,
  BarChart3,
  Clock,
  CheckCircle2,
  Circle,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { firmService } from '../services/firm.service';
import { FirmStats, Organization, FirmUser } from '../types';
import toast from 'react-hot-toast';

const FirmDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<FirmStats | null>(null);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [recentUsers, setRecentUsers] = useState<FirmUser[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, orgData, usersData] = await Promise.all([
        firmService.getFirmStats(),
        firmService.getMyOrganization(),
        firmService.listUsers()
      ]);

      setStats(statsData);
      setOrganization(orgData);
      setRecentUsers(usersData.slice(0, 5));
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Employees',
      value: stats?.total_employees || 0,
      change: '+12%',
      trend: 'up',
      icon: Users,
      color: 'primary',
      action: () => navigate('/firm/employees')
    },
    {
      title: 'Active Engagements',
      value: stats?.active_engagements || 0,
      change: '+8%',
      trend: 'up',
      icon: FileText,
      color: 'success',
      action: () => navigate('/firm/audits')
    },
    {
      title: 'Pending Invitations',
      value: stats?.pending_invitations || 0,
      change: '-3%',
      trend: 'down',
      icon: Mail,
      color: 'accent',
      action: () => navigate('/firm/employees')
    },
    {
      title: 'Total Clients',
      value: stats?.total_clients || 0,
      change: '+24%',
      trend: 'up',
      icon: Building2,
      color: 'primary',
      action: () => navigate('/firm/clients')
    }
  ];

  const quickActions = [
    {
      title: 'Invite Team Member',
      description: 'Send invitation to join your firm',
      icon: UserPlus,
      action: () => navigate('/firm/employees?action=invite')
    },
    {
      title: 'Firm Settings',
      description: 'Manage profile and preferences',
      icon: Settings,
      action: () => navigate('/firm/settings')
    },
    {
      title: 'View Reports',
      description: 'Access analytics and insights',
      icon: BarChart3,
      action: () => navigate('/firm/reports')
    },
  ];

  const recentActivity = [
    {
      id: 1,
      type: 'user',
      title: 'New employee joined',
      description: 'Sarah Johnson accepted invitation',
      time: '2 hours ago',
      icon: Users,
      color: 'primary'
    },
    {
      id: 2,
      type: 'engagement',
      title: 'Engagement completed',
      description: 'Q4 2024 Financial Audit finalized',
      time: '1 day ago',
      icon: CheckCircle2,
      color: 'success'
    },
    {
      id: 3,
      type: 'settings',
      title: 'Firm branding updated',
      description: 'Logo and color scheme refreshed',
      time: '3 days ago',
      icon: Settings,
      color: 'accent'
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-body text-neutral-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-[1600px]">
      {/* CPA Firm Header Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="bg-gradient-to-r from-[#10893e] to-[#16a34a] rounded-2xl px-8 py-4 text-white text-center shadow-lg"
      >
        <div className="flex items-center justify-center gap-2">
          <Building2 className="w-5 h-5" />
          <h1 className="text-xl font-semibold tracking-wide">
            CPA FIRM PORTAL - MANAGE YOUR CLIENTS & ENGAGEMENTS
          </h1>
        </div>
      </motion.div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between"
      >
        <div className="flex items-center gap-4">
          {organization?.logo_url && (
            <motion.img
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, damping: 20 }}
              src={organization.logo_url}
              alt={organization.name}
              className="w-14 h-14 rounded-fluent-lg object-cover shadow-fluent-4"
            />
          )}
          <div>
            <h1 className="text-display text-neutral-900 mb-1">
              {organization?.name || 'Your Firm'}
            </h1>
            <p className="text-body text-neutral-600">
              Welcome back! Here's your firm overview
            </p>
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => navigate('/firm/settings')}
          className="fluent-btn-secondary"
        >
          <Settings className="w-4 h-4" />
          Settings
        </motion.button>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          const TrendIcon = stat.trend === 'up' ? TrendingUp : TrendingDown;
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                delay: index * 0.05,
                duration: 0.3,
                ease: [0.1, 0.9, 0.2, 1]
              }}
              onClick={stat.action}
              className="fluent-card-interactive p-6 group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-2.5 rounded-fluent bg-${stat.color}-50`}>
                  <Icon className={`w-5 h-5 text-${stat.color}-600`} />
                </div>
                <div className={`flex items-center gap-1 text-caption font-semibold ${
                  stat.trend === 'up' ? 'text-success-600' : 'text-neutral-500'
                }`}>
                  <TrendIcon className="w-3.5 h-3.5" />
                  {stat.change}
                </div>
              </div>

              <div className="space-y-1">
                <p className="text-caption text-neutral-600 font-medium">
                  {stat.title}
                </p>
                <p className="text-display text-neutral-900 font-semibold">
                  {stat.value.toLocaleString()}
                </p>
              </div>

              <div className="mt-4 flex items-center text-caption text-neutral-500 group-hover:text-primary-600 transition-colors">
                View details
                <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2 space-y-6"
        >
          {/* Quick Actions Card */}
          <div className="fluent-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-title text-neutral-900">Quick Actions</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {quickActions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <motion.button
                    key={action.title}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 + index * 0.05 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={action.action}
                    className="fluent-list-item flex-col items-start text-left p-4 bg-neutral-50 hover:bg-neutral-100 border border-neutral-200"
                  >
                    <div className="p-2 rounded-fluent-sm bg-primary-100 mb-3">
                      <Icon className="w-5 h-5 text-primary-600" />
                    </div>
                    <h3 className="text-body-strong text-neutral-900 mb-1">
                      {action.title}
                    </h3>
                    <p className="text-caption text-neutral-600">
                      {action.description}
                    </p>
                  </motion.button>
                );
              })}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="fluent-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-title text-neutral-900">Recent Activity</h2>
              <Clock className="w-5 h-5 text-neutral-400" />
            </div>
            <div className="space-y-3">
              {recentActivity.map((activity, index) => {
                const Icon = activity.icon;
                return (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    className="flex items-start gap-3 p-3 rounded-fluent hover:bg-neutral-50 transition-colors"
                  >
                    <div className={`p-2 rounded-fluent-sm bg-${activity.color}-50 flex-shrink-0`}>
                      <Icon className={`w-4 h-4 text-${activity.color}-600`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-body-strong text-neutral-900 mb-0.5">
                        {activity.title}
                      </p>
                      <p className="text-caption text-neutral-600">
                        {activity.description}
                      </p>
                    </div>
                    <span className="text-caption text-neutral-500 flex-shrink-0">
                      {activity.time}
                    </span>
                  </motion.div>
                );
              })}
            </div>
            <button className="w-full mt-4 py-2.5 text-body-strong text-primary-600 hover:bg-primary-50 rounded-fluent transition-colors">
              View all activity
            </button>
          </div>
        </motion.div>

        {/* Team Overview */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.25 }}
          className="space-y-6"
        >
          {/* Team Card */}
          <div className="fluent-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-title text-neutral-900">Team</h2>
              <Users className="w-5 h-5 text-neutral-400" />
            </div>
            <div className="space-y-2">
              {recentUsers.map((user, index) => (
                <motion.div
                  key={user.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 + index * 0.05 }}
                  className="flex items-center gap-3 p-2.5 rounded-fluent hover:bg-neutral-50 transition-colors"
                >
                  <div className="relative">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white text-body-strong flex-shrink-0">
                      {user.full_name.charAt(0).toUpperCase()}
                    </div>
                    {user.is_active && (
                      <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-success-500 rounded-full ring-2 ring-white"></span>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-body-strong text-neutral-900 truncate">
                      {user.full_name}
                    </p>
                    <p className="text-caption text-neutral-600 capitalize truncate">
                      {user.role.replace('_', ' ')}
                    </p>
                  </div>
                </motion.div>
              ))}
              <button
                onClick={() => navigate('/firm/employees')}
                className="w-full py-2.5 text-body-strong text-primary-600 hover:bg-primary-50 rounded-fluent transition-colors mt-2"
              >
                View all team members
              </button>
            </div>
          </div>

          {/* Insights Card */}
          <div className="fluent-card p-6 bg-gradient-to-br from-primary-50 to-white border-primary-200">
            <div className="mb-4">
              <div className="w-10 h-10 rounded-fluent bg-primary-500 flex items-center justify-center mb-3">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-title text-neutral-900 mb-2">
                Performance Insight
              </h3>
              <p className="text-body text-neutral-700 leading-relaxed">
                Your team productivity is up <span className="font-semibold text-success-600">24%</span> this month. Keep up the great work!
              </p>
            </div>
            <button className="fluent-btn-primary w-full">
              <BarChart3 className="w-4 h-4" />
              View Analytics
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default FirmDashboard;
