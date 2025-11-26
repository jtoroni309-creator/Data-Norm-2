/**
 * Engagement Workspace Dashboard
 * Main workspace for performing audit work - complete audit execution environment
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Building2,
  Calendar,
  CheckCircle2,
  Clock,
  FileText,
  Users,
  BarChart3,
  Shield,
  FolderOpen,
  MessageSquare,
  TrendingUp,
  ClipboardList,
  AlertTriangle,
  ChevronRight,
  Edit,
  Upload,
  Download,
  Brain,
} from 'lucide-react';
import { engagementService, Engagement } from '../services/engagement.service';
import toast from 'react-hot-toast';

const EngagementWorkspace: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [engagement, setEngagement] = useState<Engagement | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadEngagement(id);
    }
  }, [id]);

  const loadEngagement = async (engagementId: string) => {
    try {
      setLoading(true);
      const data = await engagementService.getEngagement(engagementId);
      setEngagement(data);
    } catch (error: any) {
      console.error('Failed to load engagement:', error);
      toast.error('Failed to load engagement');
      navigate('/firm/audits');
    } finally {
      setLoading(false);
    }
  };

  const getProgressPercentage = (status: string): number => {
    const statusProgress = {
      draft: 0,
      planning: 20,
      fieldwork: 50,
      review: 75,
      finalized: 100,
    };
    return statusProgress[status as keyof typeof statusProgress] || 0;
  };

  const workspaceModules = [
    {
      id: 'workpapers',
      title: 'Workpapers',
      description: 'Electronic workpaper library and management',
      icon: FileText,
      color: 'blue',
      path: `/firm/engagements/${id}/workpapers`,
      stats: { total: 45, completed: 32 },
    },
    {
      id: 'analytics',
      title: 'Analytical Procedures',
      description: 'AI-powered financial analysis and benchmarking',
      icon: TrendingUp,
      color: 'purple',
      path: `/firm/engagements/${id}/analytics`,
      stats: { total: 12, completed: 8 },
    },
    {
      id: 'testing',
      title: 'Audit Testing',
      description: 'Testing modules for all audit areas',
      icon: ClipboardList,
      color: 'green',
      path: `/firm/engagements/${id}/testing`,
      stats: { total: 28, completed: 15 },
    },
    {
      id: 'risk',
      title: 'Risk Assessment',
      description: 'Risk matrix, materiality, and fraud assessment',
      icon: Shield,
      color: 'orange',
      path: `/firm/engagements/${id}/risk`,
      stats: { total: 8, completed: 8 },
    },
    {
      id: 'documents',
      title: 'Documents',
      description: 'Client documents and file repository',
      icon: FolderOpen,
      color: 'cyan',
      path: `/firm/engagements/${id}/documents`,
      stats: { total: 156, completed: 156 },
    },
    {
      id: 'reports',
      title: 'Reports',
      description: 'Audit reports and deliverables',
      icon: BarChart3,
      color: 'indigo',
      path: `/firm/engagements/${id}/reports`,
      stats: { total: 5, completed: 2 },
    },
  ];

  const recentActivity = [
    {
      type: 'workpaper',
      title: 'Revenue Testing - Sample Selection',
      user: 'John Smith',
      time: '2 hours ago',
      status: 'completed',
    },
    {
      type: 'document',
      title: 'Trial Balance - Q4 2024 uploaded',
      user: 'Sarah Johnson',
      time: '4 hours ago',
      status: 'info',
    },
    {
      type: 'analytics',
      title: 'Ratio Analysis flagged 3 anomalies',
      user: 'AI Assistant',
      time: '5 hours ago',
      status: 'warning',
    },
    {
      type: 'review',
      title: 'Inventory Testing reviewed and signed',
      user: 'Michael Chen (Partner)',
      time: '1 day ago',
      status: 'completed',
    },
  ];

  const teamMembers = [
    { name: 'Michael Chen', role: 'Partner', avatar: 'MC', status: 'active' },
    { name: 'Sarah Johnson', role: 'Manager', avatar: 'SJ', status: 'active' },
    { name: 'John Smith', role: 'Senior', avatar: 'JS', status: 'active' },
    { name: 'Emily Davis', role: 'Staff', avatar: 'ED', status: 'away' },
  ];

  const aiInsights = [
    {
      type: 'anomaly',
      title: 'Revenue Variance Detected',
      description: 'Q4 revenue decreased 15% vs prior year - investigate seasonality and market conditions',
      severity: 'high',
    },
    {
      type: 'compliance',
      title: 'Debt Covenant Review Required',
      description: 'Current ratio approaching covenant threshold of 1.5x (currently 1.6x)',
      severity: 'medium',
    },
    {
      type: 'efficiency',
      title: 'Workpaper Completion Ahead of Schedule',
      description: '71% of workpapers completed - 12% ahead of planned timeline',
      severity: 'low',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-body text-neutral-600">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (!engagement) {
    return null;
  }

  const progress = getProgressPercentage(engagement.status);

  return (
    <div className="space-y-6 max-w-[1800px]">
      {/* Header with Back Button */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <button
          onClick={() => navigate('/firm/audits')}
          className="p-2 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-neutral-700" />
        </button>
        <div className="flex-1">
          <h1 className="text-display text-neutral-900 mb-1">{engagement.name}</h1>
          <div className="flex items-center gap-4 text-body text-neutral-600">
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4" />
              <span>Client: {engagement.client_id}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              <span>FYE: {new Date(engagement.fiscal_year_end).toLocaleDateString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>
                {engagement.engagement_type.charAt(0).toUpperCase() + engagement.engagement_type.slice(1)}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Progress Tracker */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fluent-card p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-title text-neutral-900">Engagement Progress</h2>
          <span className="text-body-strong text-primary-600">{progress}% Complete</span>
        </div>

        <div className="relative">
          <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full"
            />
          </div>
        </div>

        <div className="grid grid-cols-5 gap-4 mt-6">
          {['Draft', 'Planning', 'Fieldwork', 'Review', 'Finalized'].map((stage, index) => {
            const isActive = engagement.status === stage.toLowerCase();
            const isCompleted = getProgressPercentage(engagement.status) > getProgressPercentage(stage.toLowerCase());

            return (
              <div key={stage} className="text-center">
                <div className={`mx-auto w-10 h-10 rounded-full flex items-center justify-center mb-2 transition-all ${
                  isActive ? 'bg-primary-500 text-white ring-4 ring-primary-100' :
                  isCompleted ? 'bg-success-500 text-white' :
                  'bg-neutral-200 text-neutral-500'
                }`}>
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : (
                    <span className="text-caption font-semibold">{index + 1}</span>
                  )}
                </div>
                <p className={`text-caption font-medium ${
                  isActive ? 'text-primary-600' : isCompleted ? 'text-success-600' : 'text-neutral-600'
                }`}>
                  {stage}
                </p>
              </div>
            );
          })}
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Workspace Modules */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <h2 className="text-title text-neutral-900 mb-4">Audit Workspace</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {workspaceModules.map((module, index) => {
                const Icon = module.icon;
                const completionRate = Math.round((module.stats.completed / module.stats.total) * 100);

                return (
                  <motion.button
                    key={module.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => navigate(module.path)}
                    className="fluent-card-interactive p-6 text-left group"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className={`w-12 h-12 rounded-fluent bg-${module.color}-100 flex items-center justify-center group-hover:scale-110 transition-transform`}>
                        <Icon className={`w-6 h-6 text-${module.color}-600`} />
                      </div>
                      <ChevronRight className="w-5 h-5 text-neutral-400 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
                    </div>

                    <h3 className="text-body-strong text-neutral-900 mb-1">{module.title}</h3>
                    <p className="text-caption text-neutral-600 mb-4">{module.description}</p>

                    <div className="flex items-center justify-between">
                      <span className="text-caption text-neutral-600">
                        {module.stats.completed} of {module.stats.total}
                      </span>
                      <span className="text-caption font-semibold text-primary-600">
                        {completionRate}%
                      </span>
                    </div>
                    <div className="mt-2 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-${module.color}-500 rounded-full transition-all`}
                        style={{ width: `${completionRate}%` }}
                      />
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </div>

          {/* AI Insights */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-5 h-5 text-primary-600" />
              <h2 className="text-title text-neutral-900">AI-Powered Insights</h2>
            </div>
            <div className="space-y-3">
              {aiInsights.map((insight, index) => {
                const severityConfig = {
                  high: { color: 'error', icon: AlertTriangle },
                  medium: { color: 'warning', icon: AlertTriangle },
                  low: { color: 'success', icon: CheckCircle2 },
                };
                const config = severityConfig[insight.severity as keyof typeof severityConfig];
                const Icon = config.icon;

                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`fluent-card p-4 border-l-4 border-${config.color}-500`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-fluent bg-${config.color}-100 flex items-center justify-center flex-shrink-0`}>
                        <Icon className={`w-4 h-4 text-${config.color}-600`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-body-strong text-neutral-900 mb-1">{insight.title}</h4>
                        <p className="text-caption text-neutral-600">{insight.description}</p>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Team Members */}
          <div className="fluent-card p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-body-strong text-neutral-900">Team</h3>
              <button className="text-caption text-primary-600 hover:text-primary-700 font-medium">
                Manage
              </button>
            </div>
            <div className="space-y-3">
              {teamMembers.map((member, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white text-caption font-semibold">
                    {member.avatar}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-body-strong text-neutral-900 truncate">{member.name}</p>
                    <p className="text-caption text-neutral-600">{member.role}</p>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${
                    member.status === 'active' ? 'bg-success-500' : 'bg-warning-500'
                  }`} />
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="fluent-card p-5">
            <h3 className="text-body-strong text-neutral-900 mb-4">Recent Activity</h3>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => {
                const statusColors = {
                  completed: 'success',
                  info: 'primary',
                  warning: 'warning',
                };
                const color = statusColors[activity.status as keyof typeof statusColors];

                return (
                  <div key={index} className="flex gap-3">
                    <div className={`w-2 h-2 rounded-full bg-${color}-500 mt-2 flex-shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-caption font-medium text-neutral-900">{activity.title}</p>
                      <p className="text-caption text-neutral-600 truncate">{activity.user}</p>
                      <p className="text-caption text-neutral-500">{activity.time}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="fluent-card p-5">
            <h3 className="text-body-strong text-neutral-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full fluent-btn-secondary text-left justify-start">
                <Upload className="w-4 h-4" />
                Upload Documents
              </button>
              <button className="w-full fluent-btn-secondary text-left justify-start">
                <Edit className="w-4 h-4" />
                Add Workpaper
              </button>
              <button className="w-full fluent-btn-secondary text-left justify-start">
                <MessageSquare className="w-4 h-4" />
                Contact Client
              </button>
              <button className="w-full fluent-btn-secondary text-left justify-start">
                <Download className="w-4 h-4" />
                Export Report
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EngagementWorkspace;
