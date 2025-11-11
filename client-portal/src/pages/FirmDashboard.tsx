/**
 * CPA Firm Dashboard
 * Main landing page for firm administrators with stats, quick actions, and navigation
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Building2,
  Users,
  Mail,
  FileText,
  Settings,
  TrendingUp,
  Calendar,
  Activity,
  ChevronRight,
  UserPlus,
  Bell,
  BarChart3
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
      // Get 5 most recent users
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
      icon: Users,
      color: 'blue',
      gradient: 'from-blue-500 to-blue-600',
      bgGradient: 'from-blue-500/10 to-blue-600/10',
      action: () => navigate('/firm/employees')
    },
    {
      title: 'Active Engagements',
      value: stats?.active_engagements || 0,
      icon: FileText,
      color: 'purple',
      gradient: 'from-purple-500 to-purple-600',
      bgGradient: 'from-purple-500/10 to-purple-600/10',
      action: () => navigate('/engagements')
    },
    {
      title: 'Pending Invitations',
      value: stats?.pending_invitations || 0,
      icon: Mail,
      color: 'orange',
      gradient: 'from-orange-500 to-orange-600',
      bgGradient: 'from-orange-500/10 to-orange-600/10',
      action: () => navigate('/firm/employees')
    },
    {
      title: 'Total Clients',
      value: stats?.total_clients || 0,
      icon: Building2,
      color: 'green',
      gradient: 'from-green-500 to-green-600',
      bgGradient: 'from-green-500/10 to-green-600/10',
      action: () => navigate('/clients')
    }
  ];

  const quickActions = [
    {
      title: 'Invite Employee',
      description: 'Send invitation to join your firm',
      icon: UserPlus,
      color: 'blue',
      action: () => navigate('/firm/employees?action=invite')
    },
    {
      title: 'Firm Settings',
      description: 'Manage firm profile and branding',
      icon: Settings,
      color: 'purple',
      action: () => navigate('/firm/settings')
    },
    {
      title: 'View Reports',
      description: 'Access analytics and insights',
      icon: BarChart3,
      color: 'green',
      action: () => navigate('/reports')
    },
    {
      title: 'Notifications',
      description: 'Review recent activity',
      icon: Bell,
      color: 'orange',
      action: () => navigate('/notifications')
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {organization?.logo_url && (
            <img
              src={organization.logo_url}
              alt={organization.name}
              className="w-16 h-16 rounded-2xl object-cover shadow-lg"
            />
          )}
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {organization?.name || 'Firm Dashboard'}
            </h1>
            <p className="text-gray-600 mt-1">
              Welcome back! Here's what's happening with your firm.
            </p>
          </div>
        </div>

        <button
          onClick={() => navigate('/firm/settings')}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all"
        >
          <Settings className="w-4 h-4" />
          Settings
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={stat.action}
                className="card hover:shadow-lg transition-shadow cursor-pointer group"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-gray-600 text-sm font-medium mb-1">
                      {stat.title}
                    </p>
                    <p className="text-3xl font-bold text-gray-900">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`p-3 rounded-lg bg-gradient-to-br ${stat.bgGradient}`}>
                    <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm text-gray-500 group-hover:text-blue-600 transition-colors">
                  View details
                  <ChevronRight className="w-4 h-4 ml-1" />
                </div>
              </motion.div>
            );
          })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <div className="card">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Quick Actions</h2>
                <Activity className="w-5 h-5 text-gray-400" />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {quickActions.map((action, index) => {
                  const Icon = action.icon;
                  return (
                    <motion.button
                      key={action.title}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.4 + index * 0.1 }}
                      onClick={action.action}
                      className="flex items-start gap-4 p-4 rounded-lg border-2 border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-all group text-left"
                    >
                      <div className={`p-3 rounded-lg bg-${action.color}-100 group-hover:bg-${action.color}-200 transition-colors`}>
                        <Icon className={`w-6 h-6 text-${action.color}-600`} />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1">
                          {action.title}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {action.description}
                        </p>
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors mt-2" />
                    </motion.button>
                  );
                })}
              </div>
            </div>

            {/* Recent Activity */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="card mt-6"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Recent Activity</h2>
                <Calendar className="w-5 h-5 text-gray-400" />
              </div>
              <div className="space-y-4">
                <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <Users className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      New employee joined
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Welcome to the team! 2 hours ago
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      Engagement completed
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Q4 2024 Audit finalized • 1 day ago
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                    <TrendingUp className="w-5 h-5 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      Firm settings updated
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Branding and logo refreshed • 3 days ago
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Team Overview */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="card h-fit"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Team Overview</h2>
              <Users className="w-5 h-5 text-gray-400" />
            </div>
            <div className="space-y-4">
              {recentUsers.map((user, index) => (
                <div
                  key={user.id}
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold flex-shrink-0">
                    {user.full_name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {user.full_name}
                    </p>
                    <p className="text-xs text-gray-600 capitalize">
                      {user.role.replace('_', ' ')}
                    </p>
                  </div>
                  {user.is_active && (
                    <span className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0"></span>
                  )}
                </div>
              ))}
              <button
                onClick={() => navigate('/firm/employees')}
                className="w-full py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
              >
                View all employees
              </button>
            </div>
          </motion.div>
      </div>
    </div>
  );
};

export default FirmDashboard;
