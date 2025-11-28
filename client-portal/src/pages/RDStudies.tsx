/**
 * R&D Studies Page
 * List and manage R&D tax credit studies
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FlaskConical,
  Plus,
  Search,
  Filter,
  DollarSign,
  Clock,
  CheckCircle,
  AlertTriangle,
  Building2,
  Calendar,
  ChevronRight,
  FileText,
  TrendingUp,
  MoreVertical
} from 'lucide-react';
import { rdStudyService } from '../services/rd-study.service';
import { RDStudySummary, RDStudyStatus } from '../types';
import toast from 'react-hot-toast';

const statusConfig: Record<RDStudyStatus, { label: string; color: string; bgColor: string }> = {
  draft: { label: 'Draft', color: 'text-gray-600', bgColor: 'bg-gray-100' },
  intake: { label: 'Intake', color: 'text-blue-600', bgColor: 'bg-blue-100' },
  data_collection: { label: 'Data Collection', color: 'text-indigo-600', bgColor: 'bg-indigo-100' },
  ai_analysis: { label: 'AI Analysis', color: 'text-purple-600', bgColor: 'bg-purple-100' },
  cpa_review: { label: 'CPA Review', color: 'text-orange-600', bgColor: 'bg-orange-100' },
  calculation: { label: 'Calculation', color: 'text-cyan-600', bgColor: 'bg-cyan-100' },
  narrative_generation: { label: 'Narratives', color: 'text-pink-600', bgColor: 'bg-pink-100' },
  final_review: { label: 'Final Review', color: 'text-amber-600', bgColor: 'bg-amber-100' },
  approved: { label: 'Approved', color: 'text-green-600', bgColor: 'bg-green-100' },
  finalized: { label: 'Finalized', color: 'text-emerald-600', bgColor: 'bg-emerald-100' },
  locked: { label: 'Locked', color: 'text-slate-600', bgColor: 'bg-slate-100' },
};

const RDStudies: React.FC = () => {
  const navigate = useNavigate();
  const [studies, setStudies] = useState<RDStudySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<RDStudyStatus | 'all'>('all');
  const [yearFilter, setYearFilter] = useState<number | 'all'>('all');

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
      setStudies(response.items || []);

      // Calculate stats
      const allStudies = response.items || [];
      setStats({
        total: allStudies.length,
        inProgress: allStudies.filter(s => !['finalized', 'locked', 'approved'].includes(s.status)).length,
        completed: allStudies.filter(s => ['finalized', 'locked', 'approved'].includes(s.status)).length,
        totalCredits: allStudies.reduce((sum, s) => sum + (s.total_credits || 0), 0)
      });
    } catch (error) {
      console.error('Failed to load studies:', error);
      toast.error('Failed to load R&D studies');
    } finally {
      setLoading(false);
    }
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
          <p className="text-gray-600">Loading R&D studies...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <FlaskConical className="w-8 h-8 text-purple-600" />
            R&D Tax Credit Studies
          </h1>
          <p className="text-gray-600 mt-1">
            Manage R&D tax credit studies with AI-powered analysis
          </p>
        </div>
        <button
          onClick={() => navigate('/firm/rd-studies/new')}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New R&D Study
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Total Studies</p>
              <p className="text-3xl font-bold">{stats.total}</p>
            </div>
            <FileText className="w-10 h-10 text-purple-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card bg-gradient-to-br from-orange-500 to-orange-600 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">In Progress</p>
              <p className="text-3xl font-bold">{stats.inProgress}</p>
            </div>
            <Clock className="w-10 h-10 text-orange-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card bg-gradient-to-br from-green-500 to-green-600 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Completed</p>
              <p className="text-3xl font-bold">{stats.completed}</p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Credits</p>
              <p className="text-2xl font-bold">{formatCurrency(stats.totalCredits)}</p>
            </div>
            <DollarSign className="w-10 h-10 text-blue-200" />
          </div>
        </motion.div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name, entity, or client..."
              className="input-field pl-10"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as RDStudyStatus | 'all')}
            className="input-field w-full md:w-48"
          >
            <option value="all">All Statuses</option>
            {Object.entries(statusConfig).map(([value, config]) => (
              <option key={value} value={value}>{config.label}</option>
            ))}
          </select>
          <select
            value={yearFilter}
            onChange={(e) => setYearFilter(e.target.value === 'all' ? 'all' : parseInt(e.target.value))}
            className="input-field w-full md:w-40"
          >
            <option value="all">All Years</option>
            {yearOptions.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Studies List */}
      {filteredStudies.length === 0 ? (
        <div className="card text-center py-16">
          <FlaskConical className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No R&D Studies Found</h3>
          <p className="text-gray-500 mb-6">
            {searchQuery || statusFilter !== 'all' || yearFilter !== 'all'
              ? 'Try adjusting your filters'
              : 'Get started by creating your first R&D tax credit study'}
          </p>
          {!searchQuery && statusFilter === 'all' && yearFilter === 'all' && (
            <button
              onClick={() => navigate('/firm/rd-studies/new')}
              className="btn-primary inline-flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Create R&D Study
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredStudies.map((study, index) => {
            const status = statusConfig[study.status] || statusConfig.draft;
            return (
              <motion.div
                key={study.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="card hover:shadow-lg transition-all cursor-pointer group"
                onClick={() => navigate(`/firm/rd-studies/${study.id}`)}
              >
                <div className="flex items-center gap-6">
                  {/* Icon */}
                  <div className="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <FlaskConical className="w-7 h-7 text-purple-600" />
                  </div>

                  {/* Main Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="text-lg font-semibold text-gray-900 truncate group-hover:text-purple-600 transition-colors">
                        {study.name}
                      </h3>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${status.bgColor} ${status.color}`}>
                        {status.label}
                      </span>
                      {study.has_open_flags && (
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-600 flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" />
                          Flags
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Building2 className="w-4 h-4" />
                        {study.entity_name}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        Tax Year {study.tax_year}
                      </span>
                      {study.client_name && (
                        <span className="text-gray-400">Client: {study.client_name}</span>
                      )}
                    </div>
                  </div>

                  {/* Credits */}
                  <div className="text-right flex-shrink-0">
                    <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                      <TrendingUp className="w-4 h-4 text-green-500" />
                      Total Credits
                    </div>
                    <p className="text-xl font-bold text-green-600">
                      {formatCurrency(study.total_credits || 0)}
                    </p>
                    <div className="text-xs text-gray-400 mt-1">
                      Fed: {formatCurrency(study.federal_credit_final || 0)} |
                      State: {formatCurrency(study.total_state_credits || 0)}
                    </div>
                  </div>

                  {/* Arrow */}
                  <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-purple-600 transition-colors" />
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RDStudies;
