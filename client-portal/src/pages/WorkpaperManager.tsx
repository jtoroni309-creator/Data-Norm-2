/**
 * Workpaper Manager
 * Complete electronic workpaper system with templates, creation, and management
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  FileText,
  Plus,
  Search,
  Filter,
  FolderOpen,
  Edit,
  Trash2,
  Eye,
  User,
  Calendar,
  CheckCircle2,
  Clock,
  AlertCircle,
  X,
  Download,
  Upload,
  Link as LinkIcon,
  MessageSquare,
  ChevronRight,
  ChevronDown,
  Paperclip,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Workpaper {
  id: string;
  reference: string;
  title: string;
  section: string;
  preparer: string;
  reviewer?: string;
  status: 'not_started' | 'in_progress' | 'review' | 'completed';
  created_at: string;
  updated_at: string;
  procedure?: string;
  results?: string;
  conclusion?: string;
  attachments: number;
  cross_references: string[];
}

const WorkpaperManager: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [workpapers, setWorkpapers] = useState<Workpaper[]>([]);
  const [expandedSection, setExpandedSection] = useState<string | null>('planning');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTemplateLibrary, setShowTemplateLibrary] = useState(false);
  const [selectedWorkpaper, setSelectedWorkpaper] = useState<Workpaper | null>(null);

  // Mock data - in production this would come from API
  useEffect(() => {
    loadWorkpapers();
  }, []);

  const loadWorkpapers = () => {
    // Mock workpapers data
    const mockWorkpapers: Workpaper[] = [
      {
        id: '1',
        reference: 'A-1',
        title: 'Planning Memorandum',
        section: 'planning',
        preparer: 'John Smith',
        reviewer: 'Sarah Johnson',
        status: 'completed',
        created_at: '2024-11-01',
        updated_at: '2024-11-05',
        procedure: 'Document overall audit strategy and planning decisions',
        results: 'Completed comprehensive planning including risk assessment',
        conclusion: 'Planning phase completed satisfactorily',
        attachments: 3,
        cross_references: ['A-2', 'B-1'],
      },
      {
        id: '2',
        reference: 'A-2',
        title: 'Risk Assessment Matrix',
        section: 'planning',
        preparer: 'Sarah Johnson',
        status: 'completed',
        created_at: '2024-11-02',
        updated_at: '2024-11-06',
        attachments: 1,
        cross_references: ['A-1'],
      },
      {
        id: '3',
        reference: 'B-1',
        title: 'Revenue Recognition Testing',
        section: 'revenue',
        preparer: 'John Smith',
        status: 'in_progress',
        created_at: '2024-11-10',
        updated_at: '2024-11-20',
        attachments: 5,
        cross_references: ['B-2', 'B-3'],
      },
      {
        id: '4',
        reference: 'B-2',
        title: 'Revenue Sample Selection',
        section: 'revenue',
        preparer: 'Emily Davis',
        status: 'review',
        created_at: '2024-11-12',
        updated_at: '2024-11-18',
        attachments: 2,
        cross_references: ['B-1'],
      },
      {
        id: '5',
        reference: 'C-1',
        title: 'Cash Reconciliation',
        section: 'assets',
        preparer: 'John Smith',
        status: 'completed',
        created_at: '2024-11-08',
        updated_at: '2024-11-15',
        attachments: 4,
        cross_references: [],
      },
      {
        id: '6',
        reference: 'C-2',
        title: 'Accounts Receivable Aging',
        section: 'assets',
        preparer: 'Emily Davis',
        status: 'in_progress',
        created_at: '2024-11-14',
        updated_at: '2024-11-22',
        attachments: 1,
        cross_references: ['C-3'],
      },
    ];
    setWorkpapers(mockWorkpapers);
  };

  const sections = [
    { id: 'planning', title: 'Planning & Risk Assessment', icon: AlertCircle, color: 'blue' },
    { id: 'controls', title: 'Internal Controls Testing', icon: CheckCircle2, color: 'green' },
    { id: 'revenue', title: 'Revenue & Receivables', icon: FileText, color: 'purple' },
    { id: 'assets', title: 'Assets', icon: FolderOpen, color: 'cyan' },
    { id: 'liabilities', title: 'Liabilities & Equity', icon: FileText, color: 'orange' },
    { id: 'analytical', title: 'Analytical Procedures', icon: FileText, color: 'indigo' },
    { id: 'conclusions', title: 'Conclusions & Reporting', icon: CheckCircle2, color: 'green' },
  ];

  const templates = [
    {
      category: 'Planning',
      items: [
        'Planning Memorandum',
        'Risk Assessment Matrix',
        'Materiality Calculation',
        'Engagement Letter Review',
        'Independence Checklist',
      ],
    },
    {
      category: 'Revenue',
      items: [
        'Revenue Recognition Testing',
        'Sample Selection - Revenue',
        'Cut-off Testing',
        'Revenue Analytics',
      ],
    },
    {
      category: 'Assets',
      items: [
        'Cash Reconciliation',
        'AR Aging Analysis',
        'AR Confirmations',
        'Inventory Observation',
        'Fixed Assets Schedule',
      ],
    },
    {
      category: 'Liabilities',
      items: [
        'AP Testing',
        'Debt Schedule',
        'Covenant Compliance',
        'Subsequent Events',
      ],
    },
  ];

  const getStatusConfig = (status: string) => {
    const configs = {
      not_started: { label: 'Not Started', color: 'gray', icon: Clock },
      in_progress: { label: 'In Progress', color: 'blue', icon: Edit },
      review: { label: 'In Review', color: 'yellow', icon: Eye },
      completed: { label: 'Completed', color: 'green', icon: CheckCircle2 },
    };
    return configs[status as keyof typeof configs] || configs.not_started;
  };

  const filteredWorkpapers = workpapers.filter((wp) => {
    const matchesSearch =
      wp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      wp.reference.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || wp.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getWorkpapersBySection = (sectionId: string) => {
    return filteredWorkpapers.filter((wp) => wp.section === sectionId);
  };

  const getSectionStats = (sectionId: string) => {
    const sectionWps = workpapers.filter((wp) => wp.section === sectionId);
    const completed = sectionWps.filter((wp) => wp.status === 'completed').length;
    return { total: sectionWps.length, completed };
  };

  return (
    <div className="space-y-6 max-w-[1800px]">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <button
          onClick={() => navigate(`/firm/engagements/${id}/workspace`)}
          className="p-2 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-neutral-700" />
        </button>
        <div className="flex-1">
          <h1 className="text-display text-neutral-900 mb-1">Workpapers</h1>
          <p className="text-body text-neutral-600">Electronic workpaper library and management</p>
        </div>
        <div className="flex gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowTemplateLibrary(true)}
            className="fluent-btn-secondary"
          >
            <FolderOpen className="w-4 h-4" />
            Template Library
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowCreateModal(true)}
            className="fluent-btn-primary"
          >
            <Plus className="w-4 h-4" />
            Create Workpaper
          </motion.button>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          {
            label: 'Total Workpapers',
            value: workpapers.length,
            color: 'primary',
            icon: FileText,
          },
          {
            label: 'In Progress',
            value: workpapers.filter((w) => w.status === 'in_progress').length,
            color: 'blue',
            icon: Edit,
          },
          {
            label: 'In Review',
            value: workpapers.filter((w) => w.status === 'review').length,
            color: 'yellow',
            icon: Eye,
          },
          {
            label: 'Completed',
            value: workpapers.filter((w) => w.status === 'completed').length,
            color: 'success',
            icon: CheckCircle2,
          },
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
              <div className="flex items-center justify-between mb-2">
                <p className="text-caption text-neutral-600">{stat.label}</p>
                <Icon className={`w-4 h-4 text-${stat.color}-600`} />
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
              placeholder="Search workpapers..."
              className="fluent-input pl-10"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="fluent-input w-full sm:w-48"
          >
            <option value="all">All Status</option>
            <option value="not_started">Not Started</option>
            <option value="in_progress">In Progress</option>
            <option value="review">In Review</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      {/* Workpaper Sections */}
      <div className="space-y-4">
        {sections.map((section, index) => {
          const Icon = section.icon;
          const stats = getSectionStats(section.id);
          const sectionWorkpapers = getWorkpapersBySection(section.id);
          const isExpanded = expandedSection === section.id;
          const completionRate = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;

          return (
            <motion.div
              key={section.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="fluent-card overflow-hidden"
            >
              <button
                onClick={() => setExpandedSection(isExpanded ? null : section.id)}
                className="w-full p-5 flex items-center justify-between hover:bg-neutral-50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-fluent bg-${section.color}-100 flex items-center justify-center`}>
                    <Icon className={`w-5 h-5 text-${section.color}-600`} />
                  </div>
                  <div className="text-left">
                    <h3 className="text-body-strong text-neutral-900">{section.title}</h3>
                    <p className="text-caption text-neutral-600">
                      {stats.completed} of {stats.total} completed ({completionRate}%)
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-32 h-2 bg-neutral-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-${section.color}-500 transition-all`}
                      style={{ width: `${completionRate}%` }}
                    />
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="w-5 h-5 text-neutral-600" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-neutral-600" />
                  )}
                </div>
              </button>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="border-t border-neutral-200"
                  >
                    <div className="p-5 space-y-3">
                      {sectionWorkpapers.length > 0 ? (
                        sectionWorkpapers.map((workpaper) => {
                          const statusConfig = getStatusConfig(workpaper.status);
                          const StatusIcon = statusConfig.icon;

                          return (
                            <div
                              key={workpaper.id}
                              className="p-4 border border-neutral-200 rounded-fluent hover:border-primary-300 hover:shadow-sm transition-all cursor-pointer"
                              onClick={() => setSelectedWorkpaper(workpaper)}
                            >
                              <div className="flex items-start justify-between mb-3">
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="text-caption font-mono font-semibold text-primary-600">
                                      {workpaper.reference}
                                    </span>
                                    <span className="text-body-strong text-neutral-900">
                                      {workpaper.title}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-4 text-caption text-neutral-600">
                                    <div className="flex items-center gap-1">
                                      <User className="w-3.5 h-3.5" />
                                      <span>{workpaper.preparer}</span>
                                    </div>
                                    {workpaper.reviewer && (
                                      <div className="flex items-center gap-1">
                                        <Eye className="w-3.5 h-3.5" />
                                        <span>{workpaper.reviewer}</span>
                                      </div>
                                    )}
                                    <div className="flex items-center gap-1">
                                      <Calendar className="w-3.5 h-3.5" />
                                      <span>{new Date(workpaper.updated_at).toLocaleDateString()}</span>
                                    </div>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span
                                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-fluent-sm text-caption font-medium bg-${statusConfig.color}-50 text-${statusConfig.color}-700`}
                                  >
                                    <StatusIcon className="w-3.5 h-3.5" />
                                    {statusConfig.label}
                                  </span>
                                </div>
                              </div>

                              <div className="flex items-center gap-4 text-caption text-neutral-600">
                                {workpaper.attachments > 0 && (
                                  <div className="flex items-center gap-1">
                                    <Paperclip className="w-3.5 h-3.5" />
                                    <span>{workpaper.attachments} files</span>
                                  </div>
                                )}
                                {workpaper.cross_references.length > 0 && (
                                  <div className="flex items-center gap-1">
                                    <LinkIcon className="w-3.5 h-3.5" />
                                    <span>{workpaper.cross_references.length} references</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <div className="text-center py-8">
                          <FileText className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
                          <p className="text-body text-neutral-600 mb-4">No workpapers in this section</p>
                          <button
                            onClick={() => setShowCreateModal(true)}
                            className="fluent-btn-secondary inline-flex"
                          >
                            <Plus className="w-4 h-4" />
                            Add Workpaper
                          </button>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>

      {/* Template Library Modal */}
      <AnimatePresence>
        {showTemplateLibrary && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowTemplateLibrary(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-fluent-lg p-6 max-w-4xl w-full shadow-fluent-16 max-h-[80vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-title-large text-neutral-900">Workpaper Template Library</h2>
                <button
                  onClick={() => setShowTemplateLibrary(false)}
                  className="p-2 hover:bg-neutral-100 rounded-fluent-sm"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {templates.map((category) => (
                  <div key={category.category}>
                    <h3 className="text-body-strong text-neutral-900 mb-3">{category.category}</h3>
                    <div className="space-y-2">
                      {category.items.map((template) => (
                        <button
                          key={template}
                          className="w-full text-left p-3 border border-neutral-200 rounded-fluent hover:border-primary-300 hover:bg-primary-50 transition-all group"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-body text-neutral-900">{template}</span>
                            <Plus className="w-4 h-4 text-neutral-400 group-hover:text-primary-600" />
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Create Workpaper Modal */}
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
                <h2 className="text-title-large text-neutral-900">Create New Workpaper</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-neutral-100 rounded-fluent-sm"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Section *</label>
                  <select className="fluent-input">
                    <option value="">Select section</option>
                    {sections.map((section) => (
                      <option key={section.id} value={section.id}>
                        {section.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Title *</label>
                  <input type="text" className="fluent-input" placeholder="Workpaper title" />
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">
                    Reference Number *
                  </label>
                  <input
                    type="text"
                    className="fluent-input"
                    placeholder="e.g., A-1, B-2"
                  />
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Procedure</label>
                  <textarea
                    className="fluent-input min-h-[100px]"
                    placeholder="Describe the audit procedure..."
                  />
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Preparer</label>
                  <select className="fluent-input">
                    <option value="">Select preparer</option>
                    <option value="john">John Smith</option>
                    <option value="sarah">Sarah Johnson</option>
                    <option value="emily">Emily Davis</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
                <button onClick={() => setShowCreateModal(false)} className="fluent-btn-secondary flex-1">
                  Cancel
                </button>
                <button
                  onClick={() => {
                    toast.success('Workpaper created successfully!');
                    setShowCreateModal(false);
                  }}
                  className="fluent-btn-primary flex-1"
                >
                  Create Workpaper
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default WorkpaperManager;
