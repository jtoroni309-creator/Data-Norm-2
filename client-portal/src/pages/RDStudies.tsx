/**
 * R&D Tax Credit Studies Page
 * Manage R&D tax credit studies with AI-powered analysis
 * Microsoft Fluent Design inspired UI
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FlaskConical,
  Plus,
  Search,
  DollarSign,
  Clock,
  CheckCircle,
  AlertTriangle,
  Building2,
  Calendar,
  ChevronRight,
  FileText,
  TrendingUp,
  X,
  Sparkles,
  Users,
  FolderOpen,
  ArrowRight,
  Lightbulb,
  Target,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import { rdStudyService } from '../services/rd-study.service';
import { RDStudySummary, RDStudyStatus } from '../types';
import toast from 'react-hot-toast';

const statusConfig: Record<RDStudyStatus, { label: string; color: string; bgColor: string; textColor: string }> = {
  draft: { label: 'Draft', color: 'neutral', bgColor: 'bg-neutral-100', textColor: 'text-neutral-700' },
  intake: { label: 'Intake', color: 'blue', bgColor: 'bg-blue-50', textColor: 'text-blue-700' },
  data_collection: { label: 'Data Collection', color: 'indigo', bgColor: 'bg-indigo-50', textColor: 'text-indigo-700' },
  ai_analysis: { label: 'AI Analysis', color: 'purple', bgColor: 'bg-purple-50', textColor: 'text-purple-700' },
  cpa_review: { label: 'CPA Review', color: 'orange', bgColor: 'bg-orange-50', textColor: 'text-orange-700' },
  calculation: { label: 'Calculation', color: 'cyan', bgColor: 'bg-cyan-50', textColor: 'text-cyan-700' },
  narrative_generation: { label: 'Narratives', color: 'pink', bgColor: 'bg-pink-50', textColor: 'text-pink-700' },
  final_review: { label: 'Final Review', color: 'amber', bgColor: 'bg-amber-50', textColor: 'text-amber-700' },
  approved: { label: 'Approved', color: 'green', bgColor: 'bg-green-50', textColor: 'text-green-700' },
  finalized: { label: 'Finalized', color: 'emerald', bgColor: 'bg-emerald-50', textColor: 'text-emerald-700' },
  locked: { label: 'Locked', color: 'slate', bgColor: 'bg-slate-100', textColor: 'text-slate-700' },
};

// Demo data for when backend is unavailable
const generateDemoStudies = (): RDStudySummary[] => {
  const statuses: RDStudyStatus[] = ['draft', 'data_collection', 'ai_analysis', 'cpa_review', 'finalized'];
  const companies = [
    { name: 'TechCorp Solutions', entity: 'TechCorp Solutions Inc.' },
    { name: 'BioMed Research', entity: 'BioMed Research LLC' },
    { name: 'Advanced Manufacturing', entity: 'Advanced Manufacturing Co.' },
    { name: 'Software Dynamics', entity: 'Software Dynamics Corp' },
    { name: 'Green Energy Labs', entity: 'Green Energy Labs Inc.' },
  ];

  return companies.map((company, index) => ({
    id: `demo-${index + 1}`,
    name: `${company.name} - ${2024 - (index % 2)} R&D Study`,
    entity_name: company.entity,
    client_name: company.name,
    tax_year: 2024 - (index % 2),
    status: statuses[index % statuses.length],
    total_credits: Math.floor(Math.random() * 500000) + 50000,
    federal_credit_final: Math.floor(Math.random() * 400000) + 40000,
    total_state_credits: Math.floor(Math.random() * 100000) + 10000,
    has_open_flags: index === 2,
    created_at: new Date(Date.now() - index * 7 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - index * 2 * 24 * 60 * 60 * 1000).toISOString(),
  }));
};

const RDStudies: React.FC = () => {
  const navigate = useNavigate();
  const [studies, setStudies] = useState<RDStudySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<RDStudyStatus | 'all'>('all');
  const [yearFilter, setYearFilter] = useState<number | 'all'>('all');
  const [demoMode, setDemoMode] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Create form state
  const [createForm, setCreateForm] = useState({
    client_name: '',
    entity_name: '',
    tax_year: new Date().getFullYear() - 1,
    study_name: '',
  });

  // Stats
  const [stats, setStats] = useState({
    total: 0,
    inProgress: 0,
    completed: 0,
    totalCredits: 0
  });

  useEffect(() => {
    loadStudies();
  }, [statusFilter, yearFilter]);

  const loadStudies = async () => {
    try {
      setLoading(true);
      const params: Record<string, unknown> = {};
      if (statusFilter !== 'all') params.status = statusFilter;
      if (yearFilter !== 'all') params.tax_year = yearFilter;

      const response = await rdStudyService.listStudies(params as any);
      const studyList = response.items || [];
      setStudies(studyList);
      setDemoMode(false);
      calculateStats(studyList);
    } catch (error) {
      console.error('Failed to load studies:', error);
      // Use demo data when backend is unavailable
      const demoStudies = generateDemoStudies();
      setStudies(demoStudies);
      setDemoMode(true);
      calculateStats(demoStudies);
      // Don't show error toast, just use demo mode
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (studyList: RDStudySummary[]) => {
    setStats({
      total: studyList.length,
      inProgress: studyList.filter(s => !['finalized', 'locked', 'approved'].includes(s.status)).length,
      completed: studyList.filter(s => ['finalized', 'locked', 'approved'].includes(s.status)).length,
      totalCredits: studyList.reduce((sum, s) => sum + (s.total_credits || 0), 0)
    });
  };

  const handleCreateStudy = async () => {
    if (!createForm.client_name || !createForm.entity_name) {
      toast.error('Client name and entity name are required');
      return;
    }

    const studyName = createForm.study_name ||
      `${createForm.client_name} - ${createForm.tax_year} R&D Tax Credit Study`;

    if (demoMode) {
      // Create demo study
      const newStudy: RDStudySummary = {
        id: `demo-new-${Date.now()}`,
        name: studyName,
        entity_name: createForm.entity_name,
        client_name: createForm.client_name,
        tax_year: createForm.tax_year,
        status: 'draft',
        total_credits: 0,
        federal_credit_final: 0,
        total_state_credits: 0,
        has_open_flags: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setStudies(prev => [newStudy, ...prev]);
      calculateStats([newStudy, ...studies]);
      toast.success('R&D Study created successfully!');
      setShowCreateModal(false);
      resetCreateForm();
      // Navigate to the new study
      navigate(`/firm/rd-studies/${newStudy.id}`);
    } else {
      try {
        const newStudy = await rdStudyService.createStudy({
          name: studyName,
          entity_name: createForm.entity_name,
          client_id: createForm.client_name, // This would normally be a UUID
          tax_year: createForm.tax_year,
        });
        toast.success('R&D Study created successfully!');
        setShowCreateModal(false);
        resetCreateForm();
        navigate(`/firm/rd-studies/${newStudy.id}`);
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Failed to create study');
      }
    }
  };

  const resetCreateForm = () => {
    setCreateForm({
      client_name: '',
      entity_name: '',
      tax_year: new Date().getFullYear() - 1,
      study_name: '',
    });
  };

  const filteredStudies = studies.filter(study => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      study.name.toLowerCase().includes(query) ||
      study.entity_name.toLowerCase().includes(query) ||
      (study.client_name && study.client_name.toLowerCase().includes(query))
    );
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 5 }, (_, i) => currentYear - i);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-body text-neutral-600">Loading R&D studies...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-[1600px]">
      {/* Demo Mode Banner */}
      {demoMode && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-purple-500 to-indigo-500 rounded-fluent-lg px-6 py-3 text-white flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5" />
            <span className="font-medium">Demo Mode - Showing sample R&D studies. Connect backend service for live data.</span>
          </div>
          <button
            onClick={loadStudies}
            className="flex items-center gap-2 px-3 py-1.5 bg-white/20 hover:bg-white/30 rounded-fluent-sm transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </motion.div>
      )}

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between"
      >
        <div>
          <h1 className="text-display text-neutral-900 flex items-center gap-3 mb-1">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-fluent flex items-center justify-center">
              <FlaskConical className="w-6 h-6 text-white" />
            </div>
            R&D Tax Credit Studies
          </h1>
          <p className="text-body text-neutral-600">
            Manage R&D tax credit studies with AI-powered qualification analysis and credit calculations
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowCreateModal(true)}
          className="fluent-btn-primary"
        >
          <Plus className="w-4 h-4" />
          New R&D Study
        </motion.button>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Studies', value: stats.total, icon: FileText, color: 'purple', gradient: 'from-purple-500 to-purple-600' },
          { label: 'In Progress', value: stats.inProgress, icon: Clock, color: 'orange', gradient: 'from-orange-500 to-orange-600' },
          { label: 'Completed', value: stats.completed, icon: CheckCircle, color: 'green', gradient: 'from-green-500 to-green-600' },
          { label: 'Total Credits', value: formatCurrency(stats.totalCredits), icon: DollarSign, color: 'blue', gradient: 'from-blue-500 to-blue-600', isLarge: true },
        ].map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`fluent-card p-5 bg-gradient-to-br ${stat.gradient} text-white`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white/80 text-caption font-medium mb-1">{stat.label}</p>
                  <p className={`font-bold ${stat.isLarge ? 'text-xl' : 'text-display'}`}>{stat.value}</p>
                </div>
                <div className="w-12 h-12 bg-white/20 rounded-fluent flex items-center justify-center">
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="fluent-card p-4"
      >
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name, entity, or client..."
              className="fluent-input pl-10"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as RDStudyStatus | 'all')}
            className="fluent-input w-full md:w-48"
          >
            <option value="all">All Statuses</option>
            {Object.entries(statusConfig).map(([value, config]) => (
              <option key={value} value={value}>{config.label}</option>
            ))}
          </select>
          <select
            value={yearFilter}
            onChange={(e) => setYearFilter(e.target.value === 'all' ? 'all' : parseInt(e.target.value))}
            className="fluent-input w-full md:w-40"
          >
            <option value="all">All Years</option>
            {yearOptions.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
      </motion.div>

      {/* Studies List */}
      {filteredStudies.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="fluent-card text-center py-16"
        >
          <div className="w-20 h-20 bg-purple-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <FlaskConical className="w-10 h-10 text-purple-300" />
          </div>
          <h3 className="text-title text-neutral-900 mb-2">No R&D Studies Found</h3>
          <p className="text-body text-neutral-600 mb-6 max-w-md mx-auto">
            {searchQuery || statusFilter !== 'all' || yearFilter !== 'all'
              ? 'Try adjusting your filters to find what you\'re looking for'
              : 'Get started by creating your first R&D tax credit study. Our AI will help identify qualifying activities and calculate credits.'}
          </p>
          {!searchQuery && statusFilter === 'all' && yearFilter === 'all' && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowCreateModal(true)}
              className="fluent-btn-primary"
            >
              <Plus className="w-4 h-4" />
              Create R&D Study
            </motion.button>
          )}
        </motion.div>
      ) : (
        <div className="space-y-3">
          {filteredStudies.map((study, index) => {
            const status = statusConfig[study.status] || statusConfig.draft;
            return (
              <motion.div
                key={study.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
                className="fluent-card-interactive p-5 group"
                onClick={() => navigate(`/firm/rd-studies/${study.id}`)}
              >
                <div className="flex items-center gap-6">
                  {/* Icon */}
                  <div className="w-14 h-14 bg-gradient-to-br from-purple-100 to-indigo-100 rounded-fluent-lg flex items-center justify-center flex-shrink-0 group-hover:from-purple-200 group-hover:to-indigo-200 transition-colors">
                    <FlaskConical className="w-7 h-7 text-purple-600" />
                  </div>

                  {/* Main Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1.5">
                      <h3 className="text-body-strong text-neutral-900 truncate group-hover:text-purple-600 transition-colors">
                        {study.name}
                      </h3>
                      <span className={`px-2.5 py-0.5 rounded-fluent-sm text-caption font-medium ${status.bgColor} ${status.textColor}`}>
                        {status.label}
                      </span>
                      {study.has_open_flags && (
                        <span className="px-2.5 py-0.5 rounded-fluent-sm text-caption font-medium bg-error-50 text-error-600 flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" />
                          Flags
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-caption text-neutral-600">
                      <span className="flex items-center gap-1.5">
                        <Building2 className="w-4 h-4" />
                        {study.entity_name}
                      </span>
                      <span className="flex items-center gap-1.5">
                        <Calendar className="w-4 h-4" />
                        Tax Year {study.tax_year}
                      </span>
                      {study.client_name && (
                        <span className="text-neutral-500">Client: {study.client_name}</span>
                      )}
                    </div>
                  </div>

                  {/* Credits */}
                  <div className="text-right flex-shrink-0">
                    <div className="flex items-center gap-2 text-caption text-neutral-500 mb-1">
                      <TrendingUp className="w-4 h-4 text-success-500" />
                      Total Credits
                    </div>
                    <p className="text-title text-success-600 font-semibold">
                      {formatCurrency(study.total_credits || 0)}
                    </p>
                    <div className="text-caption text-neutral-500 mt-1">
                      Fed: {formatCurrency(study.federal_credit_final || 0)} |
                      State: {formatCurrency(study.total_state_credits || 0)}
                    </div>
                  </div>

                  {/* Arrow */}
                  <ChevronRight className="w-5 h-5 text-neutral-400 group-hover:text-purple-600 group-hover:translate-x-1 transition-all" />
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Features Section (shown when empty or few studies) */}
      {filteredStudies.length <= 2 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8"
        >
          {[
            {
              icon: Lightbulb,
              title: 'AI-Powered Qualification',
              description: 'Our AI analyzes your projects against the 4-part test to identify qualifying R&D activities.',
              color: 'purple'
            },
            {
              icon: Target,
              title: 'Accurate Calculations',
              description: 'Automated QRE calculations with support for both Regular and ASC methods.',
              color: 'blue'
            },
            {
              icon: BarChart3,
              title: 'Comprehensive Reports',
              description: 'Generate Form 6765, state credit forms, and contemporaneous documentation.',
              color: 'green'
            }
          ].map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="fluent-card p-6 hover:shadow-fluent-8 transition-shadow"
              >
                <div className={`w-12 h-12 bg-${feature.color}-100 rounded-fluent flex items-center justify-center mb-4`}>
                  <Icon className={`w-6 h-6 text-${feature.color}-600`} />
                </div>
                <h4 className="text-body-strong text-neutral-900 mb-2">{feature.title}</h4>
                <p className="text-caption text-neutral-600">{feature.description}</p>
              </motion.div>
            );
          })}
        </motion.div>
      )}

      {/* Create Study Modal */}
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
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-fluent-lg p-6 max-w-lg w-full shadow-fluent-16"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-fluent flex items-center justify-center">
                    <FlaskConical className="w-5 h-5 text-white" />
                  </div>
                  <h2 className="text-title text-neutral-900">New R&D Tax Credit Study</h2>
                </div>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
                >
                  <X className="w-5 h-5 text-neutral-600" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Client Name <span className="text-error-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={createForm.client_name}
                    onChange={(e) => setCreateForm({ ...createForm, client_name: e.target.value })}
                    className="fluent-input"
                    placeholder="e.g., ABC Corporation"
                  />
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Legal Entity Name <span className="text-error-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={createForm.entity_name}
                    onChange={(e) => setCreateForm({ ...createForm, entity_name: e.target.value })}
                    className="fluent-input"
                    placeholder="e.g., ABC Corporation Inc."
                  />
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Tax Year <span className="text-error-500">*</span>
                  </label>
                  <select
                    value={createForm.tax_year}
                    onChange={(e) => setCreateForm({ ...createForm, tax_year: parseInt(e.target.value) })}
                    className="fluent-input"
                  >
                    {yearOptions.map(year => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Study Name (Optional)
                  </label>
                  <input
                    type="text"
                    value={createForm.study_name}
                    onChange={(e) => setCreateForm({ ...createForm, study_name: e.target.value })}
                    className="fluent-input"
                    placeholder="Auto-generated if left blank"
                  />
                  <p className="text-caption text-neutral-500 mt-1">
                    Leave blank to auto-generate: "{createForm.client_name || 'Client'} - {createForm.tax_year} R&D Tax Credit Study"
                  </p>
                </div>
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="fluent-btn-secondary flex-1"
                >
                  Cancel
                </button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleCreateStudy}
                  className="fluent-btn-primary flex-1"
                >
                  <Plus className="w-4 h-4" />
                  Create Study
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default RDStudies;
