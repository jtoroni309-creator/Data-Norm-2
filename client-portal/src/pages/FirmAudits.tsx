/**
 * Firm Audits Page
 * Engagement management for CPA firms - create, view, and manage audits
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText,
  Plus,
  Search,
  Filter,
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  Calendar,
  Clock,
  CheckCircle2,
  AlertCircle,
  X,
  Building2,
  User,
  Users,
  ChevronRight,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { engagementService, Engagement, EngagementCreate } from '../services/engagement.service';
import { clientService, Client } from '../services/client.service';
import toast from 'react-hot-toast';

const FirmAudits: React.FC = () => {
  const navigate = useNavigate();
  const [engagements, setEngagements] = useState<Engagement[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showMenu, setShowMenu] = useState<string | null>(null);

  // Create form state
  const [createForm, setCreateForm] = useState<EngagementCreate>({
    client_name: '',
    name: '',
    engagement_type: 'audit',
    fiscal_year_end: '',
    start_date: '',
    expected_completion_date: '',
  });

  useEffect(() => {
    loadEngagements();
    loadClients();
  }, []);

  const loadEngagements = async () => {
    try {
      setLoading(true);
      const data = await engagementService.listEngagements();
      setEngagements(data);
    } catch (error: any) {
      console.error('Failed to load engagements:', error);
      toast.error(error.response?.data?.detail || 'Failed to load engagements');
    } finally {
      setLoading(false);
    }
  };

  const loadClients = async () => {
    try {
      const data = await clientService.listClients();
      setClients(data);
    } catch (error: any) {
      console.error('Failed to load clients:', error);
      // Don't show error toast for clients, just log it
    }
  };

  const handleCreate = async () => {
    if (!createForm.client_name || !createForm.name || !createForm.fiscal_year_end) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      await engagementService.createEngagement(createForm);
      toast.success('Engagement created successfully!');
      setShowCreateModal(false);
      setCreateForm({
        client_name: '',
        name: '',
        engagement_type: 'audit',
        fiscal_year_end: '',
        start_date: '',
        expected_completion_date: '',
      });
      loadEngagements();
    } catch (error: any) {
      console.error('Failed to create engagement:', error);
      toast.error(error.response?.data?.detail || 'Failed to create engagement');
    }
  };

  const handleDelete = async (engagement: Engagement) => {
    if (!confirm(`Are you sure you want to delete "${engagement.name}"?`)) {
      return;
    }

    try {
      await engagementService.deleteEngagement(engagement.id);
      toast.success('Engagement deleted successfully');
      loadEngagements();
    } catch (error: any) {
      console.error('Failed to delete engagement:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete engagement');
    }
  };

  const filteredEngagements = engagements.filter((engagement) => {
    const matchesSearch =
      engagement.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (engagement.client_id && engagement.client_id.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || engagement.status === statusFilter;
    const matchesType = typeFilter === 'all' || engagement.engagement_type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const getStatusConfig = (status: string) => {
    const configs = {
      draft: { label: 'Draft', color: 'gray', icon: Edit },
      planning: { label: 'Planning', color: 'blue', icon: Calendar },
      fieldwork: { label: 'Fieldwork', color: 'yellow', icon: Clock },
      review: { label: 'Review', color: 'purple', icon: Eye },
      finalized: { label: 'Finalized', color: 'green', icon: CheckCircle2 },
    };
    return configs[status as keyof typeof configs] || configs.draft;
  };

  const getTypeLabel = (type: string) => {
    const labels = {
      audit: 'Audit',
      review: 'Review',
      compilation: 'Compilation',
    };
    return labels[type as keyof typeof labels] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-body text-neutral-600">Loading engagements...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-[1600px]">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between"
      >
        <div>
          <h1 className="text-display text-neutral-900 mb-1">Audits & Engagements</h1>
          <p className="text-body text-neutral-600">
            Manage audit engagements, reviews, and compilations
          </p>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowCreateModal(true)}
          className="fluent-btn-primary"
        >
          <Plus className="w-4 h-4" />
          New Engagement
        </motion.button>
      </motion.div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Engagements', value: engagements.length, color: 'primary' },
          {
            label: 'In Progress',
            value: engagements.filter((e) => ['planning', 'fieldwork', 'review'].includes(e.status)).length,
            color: 'accent',
          },
          {
            label: 'Finalized',
            value: engagements.filter((e) => e.status === 'finalized').length,
            color: 'success',
          },
          { label: 'Draft', value: engagements.filter((e) => e.status === 'draft').length, color: 'neutral' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="fluent-card p-4"
          >
            <p className="text-caption text-neutral-600 mb-1">{stat.label}</p>
            <p className={`text-title-large text-${stat.color}-600 font-semibold`}>{stat.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Filters */}
      <div className="fluent-card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search engagements..."
              className="fluent-input pl-10"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="fluent-input w-full sm:w-48"
          >
            <option value="all">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="planning">Planning</option>
            <option value="fieldwork">Fieldwork</option>
            <option value="review">Review</option>
            <option value="finalized">Finalized</option>
          </select>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="fluent-input w-full sm:w-48"
          >
            <option value="all">All Types</option>
            <option value="audit">Audit</option>
            <option value="review">Review</option>
            <option value="compilation">Compilation</option>
          </select>
        </div>
      </div>

      {/* Engagements List */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredEngagements.map((engagement, index) => {
          const statusConfig = getStatusConfig(engagement.status);
          const StatusIcon = statusConfig.icon;

          return (
            <motion.div
              key={engagement.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.03 }}
              className="fluent-card-interactive p-5 relative"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-body-strong text-neutral-900 truncate mb-1">{engagement.name}</h3>
                  <div className="flex items-center gap-2 text-caption text-neutral-600">
                    <Building2 className="w-3.5 h-3.5" />
                    <span className="truncate">Client ID: {engagement.client_id}</span>
                  </div>
                </div>
                <div className="relative">
                  <button
                    onClick={() => setShowMenu(showMenu === engagement.id ? null : engagement.id)}
                    className="p-1.5 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
                  >
                    <MoreVertical className="w-4 h-4 text-neutral-600" />
                  </button>
                  <AnimatePresence>
                    {showMenu === engagement.id && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -5 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="absolute right-0 top-full mt-1 bg-white rounded-fluent shadow-fluent-8 py-1 z-10 min-w-[180px]"
                      >
                        <button onClick={() => navigate(`/firm/engagements/${engagement.id}/workspace`)} className="w-full flex items-center gap-2 px-3 py-2 text-body text-neutral-700 hover:bg-neutral-50">
                          <Eye className="w-4 h-4" />
                          Open Workspace
                        </button>
                        <button className="w-full flex items-center gap-2 px-3 py-2 text-body text-neutral-700 hover:bg-neutral-50">
                          <Edit className="w-4 h-4" />
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(engagement)}
                          className="w-full flex items-center gap-2 px-3 py-2 text-body text-error-600 hover:bg-error-50"
                        >
                          <Trash2 className="w-4 h-4" />
                          Delete
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>

              <div className="flex items-center gap-2 mb-3">
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-fluent-sm text-caption font-medium bg-${statusConfig.color}-50 text-${statusConfig.color}-700`}>
                  <StatusIcon className="w-3.5 h-3.5" />
                  {statusConfig.label}
                </span>
                <span className="inline-flex items-center px-2.5 py-1 rounded-fluent-sm text-caption font-medium bg-neutral-100 text-neutral-700">
                  {getTypeLabel(engagement.engagement_type)}
                </span>
              </div>

              <div className="space-y-2 text-caption text-neutral-600">
                <div className="flex items-center gap-2">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>FYE: {new Date(engagement.fiscal_year_end).toLocaleDateString()}</span>
                </div>
                {engagement.expected_completion_date && (
                  <div className="flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Due: {new Date(engagement.expected_completion_date).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {filteredEngagements.length === 0 && (
        <div className="fluent-card text-center py-16">
          <FileText className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-title text-neutral-900 mb-2">No engagements found</h3>
          <p className="text-body text-neutral-600 mb-6">Get started by creating your first engagement</p>
          <button onClick={() => setShowCreateModal(true)} className="fluent-btn-primary">
            <Plus className="w-4 h-4" />
            Create Engagement
          </button>
        </div>
      )}

      {/* Create Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-fluent-lg p-6 max-w-2xl w-full shadow-fluent-16 max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-title-large text-neutral-900">Create New Engagement</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-neutral-100 rounded-fluent-sm"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Client *</label>
                  {clients.length > 0 ? (
                    <select
                      value={createForm.client_name}
                      onChange={(e) => setCreateForm({ ...createForm, client_name: e.target.value })}
                      className="fluent-input"
                    >
                      <option value="">Select a client</option>
                      {clients.map((client) => (
                        <option key={client.id} value={client.name}>
                          {client.name}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="space-y-2">
                      <input
                        type="text"
                        value={createForm.client_name}
                        onChange={(e) => setCreateForm({ ...createForm, client_name: e.target.value })}
                        className="fluent-input"
                        placeholder="Enter client name"
                      />
                      <p className="text-caption text-neutral-600">
                        <button
                          onClick={() => {
                            setShowCreateModal(false);
                            navigate('/firm/clients');
                          }}
                          className="text-primary-500 hover:text-primary-600 font-medium"
                        >
                          Add clients
                        </button>{' '}
                        first for easier engagement setup
                      </p>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Engagement Name *</label>
                  <input
                    type="text"
                    value={createForm.name}
                    onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                    className="fluent-input"
                    placeholder="e.g., FY 2024 Financial Audit"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">Engagement Type *</label>
                    <select
                      value={createForm.engagement_type}
                      onChange={(e) => setCreateForm({ ...createForm, engagement_type: e.target.value as any })}
                      className="fluent-input"
                    >
                      <option value="audit">Audit</option>
                      <option value="review">Review</option>
                      <option value="compilation">Compilation</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">Fiscal Year End *</label>
                    <input
                      type="date"
                      value={createForm.fiscal_year_end}
                      onChange={(e) => setCreateForm({ ...createForm, fiscal_year_end: e.target.value })}
                      className="fluent-input"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">Start Date</label>
                    <input
                      type="date"
                      value={createForm.start_date}
                      onChange={(e) => setCreateForm({ ...createForm, start_date: e.target.value })}
                      className="fluent-input"
                    />
                  </div>

                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">Expected Completion</label>
                    <input
                      type="date"
                      value={createForm.expected_completion_date}
                      onChange={(e) => setCreateForm({ ...createForm, expected_completion_date: e.target.value })}
                      className="fluent-input"
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
                <button onClick={() => setShowCreateModal(false)} className="fluent-btn-secondary flex-1">
                  Cancel
                </button>
                <button onClick={handleCreate} className="fluent-btn-primary flex-1">
                  Create Engagement
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FirmAudits;
