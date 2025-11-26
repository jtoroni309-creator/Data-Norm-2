/**
 * SOC Engagements Page
 * SOC 1 & SOC 2 audit management for CPA firms
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  Plus,
  Search,
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  Calendar,
  Clock,
  CheckCircle2,
  X,
  Building2,
  FileText,
  Lock,
  Server,
  Database,
  ShieldCheck,
  UserCheck,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { socCopilotService, SOCEngagement, SOCEngagementCreate } from '../services/soc-copilot.service';
import { clientService, Client } from '../services/client.service';
import toast from 'react-hot-toast';

const SOCEngagements: React.FC = () => {
  const navigate = useNavigate();
  const [engagements, setEngagements] = useState<SOCEngagement[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showMenu, setShowMenu] = useState<string | null>(null);

  // Create form state
  const [createForm, setCreateForm] = useState<SOCEngagementCreate>({
    client_name: '',
    service_description: '',
    engagement_type: 'SOC2',
    report_type: 'TYPE2',
    tsc_categories: ['SECURITY'],
    review_period_start: '',
    review_period_end: '',
    point_in_time_date: '',
    partner_id: '',
    manager_id: '',
  });

  // TSC Categories for SOC 2
  const tscCategories = [
    { id: 'SECURITY', label: 'Security', icon: Shield, description: 'Common criteria - required' },
    { id: 'AVAILABILITY', label: 'Availability', icon: Server, description: 'System uptime & recovery' },
    { id: 'PROCESSING_INTEGRITY', label: 'Processing Integrity', icon: Database, description: 'Accurate & complete processing' },
    { id: 'CONFIDENTIALITY', label: 'Confidentiality', icon: Lock, description: 'Data protection' },
    { id: 'PRIVACY', label: 'Privacy', icon: UserCheck, description: 'Personal information handling' },
  ];

  useEffect(() => {
    loadEngagements();
    loadClients();
  }, []);

  const loadEngagements = async () => {
    try {
      setLoading(true);
      const data = await socCopilotService.listEngagements();
      setEngagements(data);
    } catch (error: any) {
      console.error('Failed to load SOC engagements:', error);
      // Don't show error if service unavailable - just show empty state
      setEngagements([]);
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
    }
  };

  const handleCreate = async () => {
    if (!createForm.client_name || !createForm.service_description) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Validate dates based on report type
    if (createForm.report_type === 'TYPE2' && (!createForm.review_period_start || !createForm.review_period_end)) {
      toast.error('Type 2 reports require a review period');
      return;
    }

    if (createForm.report_type === 'TYPE1' && !createForm.point_in_time_date) {
      toast.error('Type 1 reports require a point-in-time date');
      return;
    }

    try {
      await socCopilotService.createEngagement(createForm);
      toast.success('SOC engagement created successfully!');
      setShowCreateModal(false);
      setCreateForm({
        client_name: '',
        service_description: '',
        engagement_type: 'SOC2',
        report_type: 'TYPE2',
        tsc_categories: ['SECURITY'],
        review_period_start: '',
        review_period_end: '',
        point_in_time_date: '',
        partner_id: '',
        manager_id: '',
      });
      loadEngagements();
    } catch (error: any) {
      console.error('Failed to create SOC engagement:', error);
      toast.error(error.response?.data?.detail || 'Failed to create SOC engagement');
    }
  };

  const filteredEngagements = engagements.filter((engagement) => {
    const matchesSearch =
      engagement.client_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      engagement.service_description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || engagement.status === statusFilter;
    const matchesType = typeFilter === 'all' || engagement.engagement_type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const getStatusConfig = (status: string) => {
    const configs: Record<string, { label: string; color: string; icon: any }> = {
      DRAFT: { label: 'Draft', color: 'gray', icon: Edit },
      PLANNING: { label: 'Planning', color: 'blue', icon: Calendar },
      FIELDWORK: { label: 'Fieldwork', color: 'yellow', icon: Clock },
      REVIEW: { label: 'Review', color: 'purple', icon: Eye },
      PARTNER_REVIEW: { label: 'Partner Review', color: 'indigo', icon: UserCheck },
      SIGNED: { label: 'Signed', color: 'green', icon: CheckCircle2 },
      RELEASED: { label: 'Released', color: 'emerald', icon: ShieldCheck },
      ARCHIVED: { label: 'Archived', color: 'neutral', icon: FileText },
    };
    return configs[status] || configs.DRAFT;
  };

  const toggleTscCategory = (categoryId: string) => {
    // Security is always required for SOC 2
    if (categoryId === 'SECURITY') return;

    const current = createForm.tsc_categories || [];
    if (current.includes(categoryId as any)) {
      setCreateForm({
        ...createForm,
        tsc_categories: current.filter((c) => c !== categoryId) as any[],
      });
    } else {
      setCreateForm({
        ...createForm,
        tsc_categories: [...current, categoryId] as any[],
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-body text-neutral-600">Loading SOC engagements...</p>
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
          <div className="flex items-center gap-3 mb-1">
            <Shield className="w-8 h-8 text-primary-500" />
            <h1 className="text-display text-neutral-900">SOC Engagements</h1>
          </div>
          <p className="text-body text-neutral-600">
            Manage SOC 1 and SOC 2 audit engagements with AI-powered control testing
          </p>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowCreateModal(true)}
          className="fluent-btn-primary"
        >
          <Plus className="w-4 h-4" />
          New SOC Engagement
        </motion.button>
      </motion.div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total SOC Engagements', value: engagements.length, color: 'primary' },
          {
            label: 'SOC 1 Reports',
            value: engagements.filter((e) => e.engagement_type === 'SOC1').length,
            color: 'blue',
          },
          {
            label: 'SOC 2 Reports',
            value: engagements.filter((e) => e.engagement_type === 'SOC2').length,
            color: 'accent',
          },
          {
            label: 'Released',
            value: engagements.filter((e) => e.status === 'RELEASED').length,
            color: 'success',
          },
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
              placeholder="Search SOC engagements..."
              className="fluent-input pl-10"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="fluent-input w-full sm:w-48"
          >
            <option value="all">All Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="PLANNING">Planning</option>
            <option value="FIELDWORK">Fieldwork</option>
            <option value="REVIEW">Review</option>
            <option value="PARTNER_REVIEW">Partner Review</option>
            <option value="SIGNED">Signed</option>
            <option value="RELEASED">Released</option>
          </select>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="fluent-input w-full sm:w-48"
          >
            <option value="all">All Types</option>
            <option value="SOC1">SOC 1</option>
            <option value="SOC2">SOC 2</option>
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
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold ${
                      engagement.engagement_type === 'SOC1' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                    }`}>
                      {engagement.engagement_type}
                    </span>
                    <span className="text-caption text-neutral-500">
                      Type {engagement.report_type === 'TYPE1' ? 'I' : 'II'}
                    </span>
                  </div>
                  <h3 className="text-body-strong text-neutral-900 truncate">{engagement.client_name}</h3>
                  <p className="text-caption text-neutral-600 truncate">{engagement.service_description}</p>
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
                        <button
                          onClick={() => navigate(`/firm/soc-engagements/${engagement.id}/workspace`)}
                          className="w-full flex items-center gap-2 px-3 py-2 text-body text-neutral-700 hover:bg-neutral-50"
                        >
                          <Eye className="w-4 h-4" />
                          Open Workspace
                        </button>
                        <button className="w-full flex items-center gap-2 px-3 py-2 text-body text-neutral-700 hover:bg-neutral-50">
                          <Edit className="w-4 h-4" />
                          Edit
                        </button>
                        <button className="w-full flex items-center gap-2 px-3 py-2 text-body text-error-600 hover:bg-error-50">
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
              </div>

              {/* TSC Categories for SOC 2 */}
              {engagement.engagement_type === 'SOC2' && engagement.tsc_categories && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {engagement.tsc_categories.map((cat) => (
                    <span key={cat} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-neutral-100 text-neutral-600">
                      {cat.charAt(0) + cat.slice(1).toLowerCase().replace('_', ' ')}
                    </span>
                  ))}
                </div>
              )}

              <div className="space-y-2 text-caption text-neutral-600">
                {engagement.review_period_start && engagement.review_period_end && (
                  <div className="flex items-center gap-2">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>
                      {new Date(engagement.review_period_start).toLocaleDateString()} -{' '}
                      {new Date(engagement.review_period_end).toLocaleDateString()}
                    </span>
                  </div>
                )}
                {engagement.point_in_time_date && (
                  <div className="flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5" />
                    <span>As of: {new Date(engagement.point_in_time_date).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {filteredEngagements.length === 0 && (
        <div className="fluent-card text-center py-16">
          <Shield className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-title text-neutral-900 mb-2">No SOC engagements found</h3>
          <p className="text-body text-neutral-600 mb-6">
            Get started by creating your first SOC 1 or SOC 2 engagement
          </p>
          <button onClick={() => setShowCreateModal(true)} className="fluent-btn-primary">
            <Plus className="w-4 h-4" />
            Create SOC Engagement
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
                <div className="flex items-center gap-3">
                  <Shield className="w-6 h-6 text-primary-500" />
                  <h2 className="text-title-large text-neutral-900">Create SOC Engagement</h2>
                </div>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-neutral-100 rounded-fluent-sm"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-5">
                {/* Engagement Type Selection */}
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Engagement Type *</label>
                  <div className="grid grid-cols-2 gap-3">
                    {['SOC1', 'SOC2'].map((type) => (
                      <button
                        key={type}
                        onClick={() => setCreateForm({ ...createForm, engagement_type: type as any })}
                        className={`p-4 rounded-fluent border-2 transition-all ${
                          createForm.engagement_type === type
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-neutral-200 hover:border-neutral-300'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <Shield className={`w-5 h-5 ${createForm.engagement_type === type ? 'text-primary-500' : 'text-neutral-500'}`} />
                          <span className="font-semibold">{type}</span>
                        </div>
                        <p className="text-caption text-neutral-600 text-left">
                          {type === 'SOC1' ? 'Controls relevant to user entities financial reporting (ICFR)' : 'Trust Services Criteria - Security, Availability, etc.'}
                        </p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Report Type */}
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Report Type *</label>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { id: 'TYPE1', label: 'Type I', desc: 'Design & implementation at a point in time' },
                      { id: 'TYPE2', label: 'Type II', desc: 'Design, implementation & operating effectiveness' },
                    ].map((type) => (
                      <button
                        key={type.id}
                        onClick={() => setCreateForm({ ...createForm, report_type: type.id as any })}
                        className={`p-4 rounded-fluent border-2 transition-all text-left ${
                          createForm.report_type === type.id
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-neutral-200 hover:border-neutral-300'
                        }`}
                      >
                        <span className="font-semibold">{type.label}</span>
                        <p className="text-caption text-neutral-600">{type.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Client Selection */}
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Service Organization *</label>
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
                    <input
                      type="text"
                      value={createForm.client_name}
                      onChange={(e) => setCreateForm({ ...createForm, client_name: e.target.value })}
                      className="fluent-input"
                      placeholder="Enter service organization name"
                    />
                  )}
                </div>

                {/* Service Description */}
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Service Description *</label>
                  <textarea
                    value={createForm.service_description}
                    onChange={(e) => setCreateForm({ ...createForm, service_description: e.target.value })}
                    className="fluent-input min-h-[80px]"
                    placeholder="Describe the services provided by the service organization..."
                  />
                </div>

                {/* TSC Categories (SOC 2 only) */}
                {createForm.engagement_type === 'SOC2' && (
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">Trust Services Categories *</label>
                    <div className="space-y-2">
                      {tscCategories.map((cat) => {
                        const Icon = cat.icon;
                        const isSelected = createForm.tsc_categories?.includes(cat.id as any);
                        const isRequired = cat.id === 'SECURITY';
                        return (
                          <button
                            key={cat.id}
                            onClick={() => toggleTscCategory(cat.id)}
                            disabled={isRequired}
                            className={`w-full flex items-center gap-3 p-3 rounded-fluent border transition-all text-left ${
                              isSelected
                                ? 'border-primary-500 bg-primary-50'
                                : 'border-neutral-200 hover:border-neutral-300'
                            } ${isRequired ? 'opacity-90' : ''}`}
                          >
                            <Icon className={`w-5 h-5 ${isSelected ? 'text-primary-500' : 'text-neutral-500'}`} />
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <span className="font-medium">{cat.label}</span>
                                {isRequired && (
                                  <span className="text-xs bg-primary-100 text-primary-700 px-1.5 py-0.5 rounded">Required</span>
                                )}
                              </div>
                              <p className="text-caption text-neutral-600">{cat.description}</p>
                            </div>
                            <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                              isSelected ? 'border-primary-500 bg-primary-500' : 'border-neutral-300'
                            }`}>
                              {isSelected && <CheckCircle2 className="w-3 h-3 text-white" />}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Date Fields */}
                {createForm.report_type === 'TYPE2' ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-body-strong text-neutral-700 mb-2">Review Period Start *</label>
                      <input
                        type="date"
                        value={createForm.review_period_start}
                        onChange={(e) => setCreateForm({ ...createForm, review_period_start: e.target.value })}
                        className="fluent-input"
                      />
                    </div>
                    <div>
                      <label className="block text-body-strong text-neutral-700 mb-2">Review Period End *</label>
                      <input
                        type="date"
                        value={createForm.review_period_end}
                        onChange={(e) => setCreateForm({ ...createForm, review_period_end: e.target.value })}
                        className="fluent-input"
                      />
                    </div>
                  </div>
                ) : (
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">Point-in-Time Date *</label>
                    <input
                      type="date"
                      value={createForm.point_in_time_date}
                      onChange={(e) => setCreateForm({ ...createForm, point_in_time_date: e.target.value })}
                      className="fluent-input"
                    />
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
                <button onClick={() => setShowCreateModal(false)} className="fluent-btn-secondary flex-1">
                  Cancel
                </button>
                <button onClick={handleCreate} className="fluent-btn-primary flex-1">
                  <Shield className="w-4 h-4" />
                  Create SOC Engagement
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SOCEngagements;
