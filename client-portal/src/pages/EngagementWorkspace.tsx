/**
 * Engagement Workspace Dashboard
 * Main workspace for performing audit work - complete audit execution environment
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  Save,
  X,
  Settings,
  Loader2,
} from 'lucide-react';
import { engagementService, Engagement, WorkspaceStats } from '../services/engagement.service';
import { apiService } from '../services/api.service';
import { auditPlanningService } from '../services/audit-planning.service';
import toast from 'react-hot-toast';

interface AIInsight {
  type: string;
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
}

interface Activity {
  type: string;
  title: string;
  user: string;
  time: string;
  status: string;
}

interface TeamMember {
  name: string;
  role: string;
  avatar: string;
  status: string;
}

const EngagementWorkspace: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [engagement, setEngagement] = useState<Engagement | null>(null);
  const [loading, setLoading] = useState(true);
  const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
  const [recentActivity, setRecentActivity] = useState<Activity[]>([]);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [workspaceStats, setWorkspaceStats] = useState<WorkspaceStats>({
    workpapers: { total: 0, completed: 0 },
    analytics: { total: 0, completed: 0 },
    testing: { total: 0, completed: 0 },
    risk: { total: 0, completed: 0 },
    documents: { total: 0, completed: 0 },
    reports: { total: 0, completed: 0 },
  });

  // Edit modal state
  const [showEditModal, setShowEditModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editForm, setEditForm] = useState({
    name: '',
    engagement_type: 'audit' as 'audit' | 'review' | 'compilation',
    status: 'draft' as 'draft' | 'planning' | 'fieldwork' | 'review' | 'finalized',
    fiscal_year_end: '',
    start_date: '',
    expected_completion_date: '',
  });

  useEffect(() => {
    if (id) {
      loadEngagement(id);
      loadAIInsights(id);
      loadActivity(id);
      loadTeamMembers(id);
      loadWorkspaceStats(id);
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

  const loadAIInsights = async (engagementId: string) => {
    try {
      const suggestions = await apiService.getAISuggestions(engagementId);
      const insights: AIInsight[] = suggestions.map((s: any) => ({
        type: s.type || 'insight',
        title: s.title || s.message,
        description: s.description || s.details,
        severity: s.priority === 'high' ? 'high' : s.priority === 'medium' ? 'medium' : 'low',
      }));
      setAiInsights(insights);
    } catch (error) {
      console.log('AI insights not available, using defaults');
      // Fallback to contextual defaults based on engagement
      setAiInsights([
        {
          type: 'planning',
          title: 'Start with Risk Assessment',
          description: 'Begin by completing the risk assessment to determine audit approach and materiality',
          severity: 'medium',
        },
        {
          type: 'document',
          title: 'Upload Client Documents',
          description: 'Upload trial balance, bank statements, and other source documents to enable AI analysis',
          severity: 'high',
        },
      ]);
    }
  };

  const loadActivity = async (engagementId: string) => {
    try {
      const response = await apiService.getActivityFeed(engagementId);
      const activities: Activity[] = response.activities.map((a: any) => ({
        type: a.type,
        title: a.title,
        user: a.description || 'System',
        time: new Date(a.timestamp).toLocaleString(),
        status: a.type === 'warning' ? 'warning' : a.type === 'error' ? 'error' : 'completed',
      }));
      setRecentActivity(activities);
    } catch (error) {
      console.log('Activity feed not available');
      setRecentActivity([]);
    }
  };

  const loadTeamMembers = async (engagementId: string) => {
    try {
      const team = await engagementService.getEngagementTeam(engagementId);
      const members: TeamMember[] = team.map((m: any) => ({
        name: m.user_name || m.email || 'Team Member',
        role: m.role || 'Staff',
        avatar: (m.user_name || 'TM').split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2),
        status: 'active',
      }));
      setTeamMembers(members);
    } catch (error) {
      console.log('Team members not available');
      setTeamMembers([]);
    }
  };

  const loadWorkspaceStats = async (engagementId: string) => {
    try {
      const stats = await engagementService.getWorkspaceStats(engagementId);
      setWorkspaceStats(stats);
    } catch (error) {
      console.log('Workspace stats not available');
    }
  };

  const handleUploadDocuments = () => {
    navigate(`/firm/engagements/${id}/documents`);
  };

  const handleAddWorkpaper = () => {
    navigate(`/firm/engagements/${id}/workpapers`);
  };

  const handleStartPlanning = () => {
    // Navigate to AI-powered audit planning page
    navigate(`/firm/engagements/${id}/ai-planning`);
  };

  const handleOpenEditModal = () => {
    if (engagement) {
      setEditForm({
        name: engagement.name,
        engagement_type: engagement.engagement_type,
        status: engagement.status,
        fiscal_year_end: engagement.fiscal_year_end ? engagement.fiscal_year_end.split('T')[0] : '',
        start_date: engagement.start_date ? engagement.start_date.split('T')[0] : '',
        expected_completion_date: engagement.expected_completion_date ? engagement.expected_completion_date.split('T')[0] : '',
      });
      setShowEditModal(true);
    }
  };

  const handleSaveEngagement = async () => {
    if (!id || !engagement) return;

    try {
      setSaving(true);
      await engagementService.updateEngagement(id, {
        name: editForm.name,
        engagement_type: editForm.engagement_type,
        fiscal_year_end: editForm.fiscal_year_end,
        start_date: editForm.start_date || undefined,
        expected_completion_date: editForm.expected_completion_date || undefined,
      });

      // If status changed, use transition endpoint
      if (editForm.status !== engagement.status) {
        await engagementService.transitionStatus(id, editForm.status);
      }

      toast.success('Engagement saved successfully!');
      setShowEditModal(false);
      loadEngagement(id); // Reload to get updated data
    } catch (error: any) {
      console.error('Failed to save engagement:', error);
      toast.error(error.response?.data?.detail || 'Failed to save engagement');
    } finally {
      setSaving(false);
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
      stats: workspaceStats.workpapers,
    },
    {
      id: 'analytics',
      title: 'Analytical Procedures',
      description: 'AI-powered financial analysis and benchmarking',
      icon: TrendingUp,
      color: 'purple',
      path: `/firm/engagements/${id}/analytics`,
      stats: workspaceStats.analytics,
    },
    {
      id: 'testing',
      title: 'Audit Testing',
      description: 'Testing modules for all audit areas',
      icon: ClipboardList,
      color: 'green',
      path: `/firm/engagements/${id}/testing`,
      stats: workspaceStats.testing,
    },
    {
      id: 'risk',
      title: 'Risk Assessment',
      description: 'Risk matrix, materiality, and fraud assessment',
      icon: Shield,
      color: 'orange',
      path: `/firm/engagements/${id}/risk`,
      stats: workspaceStats.risk,
    },
    {
      id: 'documents',
      title: 'Documents',
      description: 'Client documents and file repository',
      icon: FolderOpen,
      color: 'cyan',
      path: `/firm/engagements/${id}/documents`,
      stats: workspaceStats.documents,
    },
    {
      id: 'reports',
      title: 'Reports',
      description: 'Audit reports and deliverables',
      icon: BarChart3,
      color: 'indigo',
      path: `/firm/engagements/${id}/reports`,
      stats: workspaceStats.reports,
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
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleOpenEditModal}
          className="fluent-btn-secondary"
        >
          <Settings className="w-4 h-4" />
          Edit Engagement
        </motion.button>
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
                const completionRate = module.stats.total > 0
                  ? Math.round((module.stats.completed / module.stats.total) * 100)
                  : 0;

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
              {teamMembers.length > 0 ? (
                teamMembers.map((member, index) => (
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
                ))
              ) : (
                <div className="text-center py-4">
                  <Users className="w-8 h-8 text-neutral-300 mx-auto mb-2" />
                  <p className="text-caption text-neutral-500">No team members assigned</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="fluent-card p-5">
            <h3 className="text-body-strong text-neutral-900 mb-4">Recent Activity</h3>
            <div className="space-y-4">
              {recentActivity.length > 0 ? (
                recentActivity.map((activity, index) => {
                  const statusColors = {
                    completed: 'success',
                    info: 'primary',
                    warning: 'warning',
                  };
                  const color = statusColors[activity.status as keyof typeof statusColors] || 'primary';

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
                })
              ) : (
                <div className="text-center py-4">
                  <Clock className="w-8 h-8 text-neutral-300 mx-auto mb-2" />
                  <p className="text-caption text-neutral-500">No recent activity</p>
                  <p className="text-caption text-neutral-400">Activity will appear as you work</p>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="fluent-card p-5">
            <h3 className="text-body-strong text-neutral-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button
                onClick={handleUploadDocuments}
                className="w-full fluent-btn-secondary text-left justify-start"
              >
                <Upload className="w-4 h-4" />
                Upload Documents
              </button>
              <button
                onClick={handleAddWorkpaper}
                className="w-full fluent-btn-secondary text-left justify-start"
              >
                <Edit className="w-4 h-4" />
                Add Workpaper
              </button>
              <button
                onClick={handleStartPlanning}
                className="w-full fluent-btn-primary text-left justify-start"
              >
                <Brain className="w-4 h-4" />
                Start AI Planning
              </button>
              <button
                onClick={() => navigate(`/firm/engagements/${id}/risk`)}
                className="w-full fluent-btn-secondary text-left justify-start"
              >
                <Shield className="w-4 h-4" />
                Risk Assessment
              </button>
              <button
                onClick={() => navigate(`/firm/engagements/${id}/reports`)}
                className="w-full fluent-btn-secondary text-left justify-start"
              >
                <Download className="w-4 h-4" />
                Generate Reports
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Engagement Modal */}
      <AnimatePresence>
        {showEditModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowEditModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-fluent-lg p-6 max-w-lg w-full shadow-fluent-16"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-fluent flex items-center justify-center">
                    <Settings className="w-5 h-5 text-white" />
                  </div>
                  <h2 className="text-title text-neutral-900">Edit Engagement</h2>
                </div>
                <button
                  onClick={() => setShowEditModal(false)}
                  className="p-2 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
                >
                  <X className="w-5 h-5 text-neutral-600" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Engagement Name <span className="text-error-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={editForm.name}
                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                    className="fluent-input"
                    placeholder="e.g., 2024 Annual Audit"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Engagement Type
                    </label>
                    <select
                      value={editForm.engagement_type}
                      onChange={(e) => setEditForm({ ...editForm, engagement_type: e.target.value as any })}
                      className="fluent-input"
                    >
                      <option value="audit">Audit</option>
                      <option value="review">Review</option>
                      <option value="compilation">Compilation</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Status
                    </label>
                    <select
                      value={editForm.status}
                      onChange={(e) => setEditForm({ ...editForm, status: e.target.value as any })}
                      className="fluent-input"
                    >
                      <option value="draft">Draft</option>
                      <option value="planning">Planning</option>
                      <option value="fieldwork">Fieldwork</option>
                      <option value="review">Review</option>
                      <option value="finalized">Finalized</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Fiscal Year End <span className="text-error-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={editForm.fiscal_year_end}
                    onChange={(e) => setEditForm({ ...editForm, fiscal_year_end: e.target.value })}
                    className="fluent-input"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Start Date
                    </label>
                    <input
                      type="date"
                      value={editForm.start_date}
                      onChange={(e) => setEditForm({ ...editForm, start_date: e.target.value })}
                      className="fluent-input"
                    />
                  </div>

                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Expected Completion
                    </label>
                    <input
                      type="date"
                      value={editForm.expected_completion_date}
                      onChange={(e) => setEditForm({ ...editForm, expected_completion_date: e.target.value })}
                      className="fluent-input"
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
                <button
                  onClick={() => setShowEditModal(false)}
                  className="fluent-btn-secondary flex-1"
                  disabled={saving}
                >
                  Cancel
                </button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSaveEngagement}
                  disabled={saving}
                  className="fluent-btn-primary flex-1"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      Save Changes
                    </>
                  )}
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EngagementWorkspace;
