/**
 * Firm Reports Page
 * Report generation and management for CPA firms
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart3,
  FileText,
  Download,
  Plus,
  Search,
  Filter,
  CheckCircle2,
  AlertCircle,
  Clock,
  FileCheck,
  Eye,
  Trash2,
  MoreVertical,
  TrendingUp,
  Calendar,
  X,
  Loader,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { reportingService, Report, ReportCreate } from '../services/reporting.service';
import { engagementService, Engagement } from '../services/engagement.service';
import toast from 'react-hot-toast';

const FirmReports: React.FC = () => {
  const navigate = useNavigate();
  const [reports, setReports] = useState<Report[]>([]);
  const [engagements, setEngagements] = useState<Engagement[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showMenu, setShowMenu] = useState<string | null>(null);

  // Create form state
  const [createForm, setCreateForm] = useState<Partial<ReportCreate>>({
    engagement_id: '',
    report_type: 'financial_statement',
    title: '',
    description: '',
    report_data: {},
    fiscal_year: new Date().getFullYear().toString(),
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [reportsData, engagementsData] = await Promise.all([
        reportingService.listReports(),
        engagementService.listEngagements(),
      ]);
      setReports(reportsData);
      setEngagements(engagementsData);
    } catch (error: any) {
      console.error('Failed to load data:', error);
      toast.error(error.response?.data?.detail || 'Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!createForm.engagement_id || !createForm.title) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const report = await reportingService.createReport(createForm as ReportCreate);
      toast.success('Report created successfully!');
      setShowCreateModal(false);
      setCreateForm({
        engagement_id: '',
        report_type: 'financial_statement',
        title: '',
        description: '',
        report_data: {},
        fiscal_year: new Date().getFullYear().toString(),
      });
      loadData();

      // Auto-generate the report
      try {
        await reportingService.generateReport(report.id);
        toast.success('Report generation started');
        loadData();
      } catch (genError) {
        console.error('Failed to generate report:', genError);
      }
    } catch (error: any) {
      console.error('Failed to create report:', error);
      toast.error(error.response?.data?.detail || 'Failed to create report');
    }
  };

  const handleDownload = async (report: Report) => {
    try {
      const blob = await reportingService.downloadReport(report.id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${report.title}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Report downloaded successfully');
    } catch (error: any) {
      console.error('Failed to download report:', error);
      toast.error(error.response?.data?.detail || 'Failed to download report');
    }
  };

  const filteredReports = reports.filter((report) => {
    const matchesSearch =
      report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (report.description && report.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || report.status === statusFilter;
    const matchesType = typeFilter === 'all' || report.report_type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const getStatusConfig = (status: string) => {
    const configs = {
      draft: { label: 'Draft', color: 'neutral', icon: FileText },
      generating: { label: 'Generating', color: 'blue', icon: Loader },
      completed: { label: 'Completed', color: 'success', icon: CheckCircle2 },
      failed: { label: 'Failed', color: 'error', icon: AlertCircle },
    };
    return configs[status as keyof typeof configs] || configs.draft;
  };

  const reportTypes = [
    { value: 'financial_statement', label: 'Financial Statement' },
    { value: 'audit_report', label: 'Audit Report' },
    { value: 'management_letter', label: 'Management Letter' },
    { value: 'tax_return', label: 'Tax Return' },
    { value: 'compilation_report', label: 'Compilation Report' },
    { value: 'review_report', label: 'Review Report' },
  ];

  const getReportTypeLabel = (type: string) => {
    return reportTypes.find((t) => t.value === type)?.label || type;
  };

  const stats = {
    total: reports.length,
    completed: reports.filter((r) => r.status === 'completed').length,
    generating: reports.filter((r) => r.status === 'generating').length,
    failed: reports.filter((r) => r.status === 'failed').length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-body text-neutral-600">Loading reports...</p>
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
          <h1 className="text-display text-neutral-900 mb-1">Reports & Analytics</h1>
          <p className="text-body text-neutral-600">Generate and manage audit reports, financial statements, and more</p>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowCreateModal(true)}
          className="fluent-btn-primary"
        >
          <Plus className="w-4 h-4" />
          Generate Report
        </motion.button>
      </motion.div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Reports', value: stats.total, color: 'primary', icon: BarChart3 },
          { label: 'Completed', value: stats.completed, color: 'success', icon: CheckCircle2 },
          { label: 'Generating', value: stats.generating, color: 'accent', icon: Clock },
          { label: 'Failed', value: stats.failed, color: 'error', icon: AlertCircle },
        ].map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="fluent-card p-4"
            >
              <div className="flex items-start justify-between mb-2">
                <p className="text-caption text-neutral-600">{stat.label}</p>
                <Icon className={`w-4 h-4 text-${stat.color}-500`} />
              </div>
              <p className={`text-title-large text-${stat.color}-600 font-semibold`}>{stat.value}</p>
            </motion.div>
          );
        })}
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
              placeholder="Search reports..."
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
            <option value="generating">Generating</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="fluent-input w-full sm:w-48"
          >
            <option value="all">All Types</option>
            {reportTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Reports List */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredReports.map((report, index) => {
          const statusConfig = getStatusConfig(report.status);
          const StatusIcon = statusConfig.icon;

          return (
            <motion.div
              key={report.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.03 }}
              className="fluent-card-interactive p-5 relative"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-body-strong text-neutral-900 mb-1">{report.title}</h3>
                  {report.description && (
                    <p className="text-caption text-neutral-600 line-clamp-2">{report.description}</p>
                  )}
                </div>
                <div className="relative">
                  <button
                    onClick={() => setShowMenu(showMenu === report.id ? null : report.id)}
                    className="p-1.5 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
                  >
                    <MoreVertical className="w-4 h-4 text-neutral-600" />
                  </button>
                  <AnimatePresence>
                    {showMenu === report.id && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -5 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="absolute right-0 top-full mt-1 bg-white rounded-fluent shadow-fluent-8 py-1 z-10 min-w-[140px]"
                      >
                        {report.status === 'completed' && (
                          <button
                            onClick={() => handleDownload(report)}
                            className="w-full flex items-center gap-2 px-3 py-2 text-body text-neutral-700 hover:bg-neutral-50"
                          >
                            <Download className="w-4 h-4" />
                            Download PDF
                          </button>
                        )}
                        <button className="w-full flex items-center gap-2 px-3 py-2 text-body text-neutral-700 hover:bg-neutral-50">
                          <Eye className="w-4 h-4" />
                          View Details
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
                <span
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-fluent-sm text-caption font-medium bg-${statusConfig.color}-50 text-${statusConfig.color}-700`}
                >
                  <StatusIcon className={`w-3.5 h-3.5 ${report.status === 'generating' ? 'animate-spin' : ''}`} />
                  {statusConfig.label}
                </span>
                <span className="inline-flex items-center px-2.5 py-1 rounded-fluent-sm text-caption font-medium bg-neutral-100 text-neutral-700">
                  {getReportTypeLabel(report.report_type)}
                </span>
              </div>

              <div className="space-y-2 text-caption text-neutral-600">
                {report.fiscal_year && (
                  <div className="flex items-center gap-2">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>FY {report.fiscal_year}</span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Created {new Date(report.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              {report.status === 'completed' && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleDownload(report)}
                  className="w-full mt-3 fluent-btn-primary py-2"
                >
                  <Download className="w-4 h-4" />
                  Download PDF
                </motion.button>
              )}
            </motion.div>
          );
        })}
      </div>

      {filteredReports.length === 0 && (
        <div className="fluent-card text-center py-16">
          <BarChart3 className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <h3 className="text-title text-neutral-900 mb-2">No reports found</h3>
          <p className="text-body text-neutral-600 mb-6">Generate your first report to get started</p>
          <button onClick={() => setShowCreateModal(true)} className="fluent-btn-primary">
            <Plus className="w-4 h-4" />
            Generate Report
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
                <h2 className="text-title-large text-neutral-900">Generate New Report</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-neutral-100 rounded-fluent-sm"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Engagement *</label>
                  <select
                    value={createForm.engagement_id}
                    onChange={(e) => setCreateForm({ ...createForm, engagement_id: e.target.value })}
                    className="fluent-input"
                  >
                    <option value="">Select engagement</option>
                    {engagements.map((engagement) => (
                      <option key={engagement.id} value={engagement.id}>
                        {engagement.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Report Type *</label>
                  <select
                    value={createForm.report_type}
                    onChange={(e) => setCreateForm({ ...createForm, report_type: e.target.value })}
                    className="fluent-input"
                  >
                    {reportTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Report Title *</label>
                  <input
                    type="text"
                    value={createForm.title}
                    onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                    className="fluent-input"
                    placeholder="e.g., FY 2024 Audit Report"
                  />
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Description</label>
                  <textarea
                    value={createForm.description}
                    onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                    className="fluent-input"
                    rows={3}
                    placeholder="Optional description"
                  />
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Fiscal Year</label>
                  <input
                    type="text"
                    value={createForm.fiscal_year}
                    onChange={(e) => setCreateForm({ ...createForm, fiscal_year: e.target.value })}
                    className="fluent-input"
                    placeholder="2024"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
                <button onClick={() => setShowCreateModal(false)} className="fluent-btn-secondary flex-1">
                  Cancel
                </button>
                <button onClick={handleCreate} className="fluent-btn-primary flex-1">
                  Generate Report
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FirmReports;
