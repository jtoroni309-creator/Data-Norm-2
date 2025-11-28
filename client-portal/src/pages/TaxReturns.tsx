/**
 * Tax Returns Page
 * List and manage tax returns for clients
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Calculator,
  Plus,
  Search,
  Filter,
  ChevronRight,
  Calendar,
  DollarSign,
  FileText,
  CheckCircle,
  Clock,
  AlertCircle,
  XCircle,
  Send,
  RefreshCw,
  Building2,
  User,
  X,
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { taxService } from '../services/tax.service';
import {
  TaxReturnSummary,
  TaxFormType,
  TaxReturnStatus,
  FilingStatus,
} from '../types';

const TaxReturns: React.FC = () => {
  const navigate = useNavigate();
  const [returns, setReturns] = useState<TaxReturnSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [yearFilter, setYearFilter] = useState<number | 'all'>('all');
  const [formFilter, setFormFilter] = useState<TaxFormType | 'all'>('all');
  const [statusFilter, setStatusFilter] = useState<TaxReturnStatus | 'all'>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Stats
  const [stats, setStats] = useState({
    total: 0,
    draft: 0,
    inProgress: 0,
    readyToFile: 0,
    filed: 0,
    totalRefunds: 0,
    totalOwed: 0,
  });

  useEffect(() => {
    loadReturns();
  }, []);

  const loadReturns = async () => {
    setLoading(true);
    try {
      const response = await taxService.listReturns();
      setReturns(response.items || []);
      calculateStats(response.items || []);
    } catch (error) {
      console.error('Failed to load tax returns:', error);
      // Use mock data for demo
      const mockReturns = generateMockReturns();
      setReturns(mockReturns);
      calculateStats(mockReturns);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (data: TaxReturnSummary[]) => {
    const newStats = {
      total: data.length,
      draft: data.filter(r => r.status === 'draft').length,
      inProgress: data.filter(r => ['data_entry', 'review', 'calculating'].includes(r.status)).length,
      readyToFile: data.filter(r => r.status === 'ready_to_file').length,
      filed: data.filter(r => ['filed', 'accepted'].includes(r.status)).length,
      totalRefunds: data
        .filter(r => (r.refund_or_owed || 0) > 0)
        .reduce((sum, r) => sum + (r.refund_or_owed || 0), 0),
      totalOwed: data
        .filter(r => (r.refund_or_owed || 0) < 0)
        .reduce((sum, r) => sum + Math.abs(r.refund_or_owed || 0), 0),
    };
    setStats(newStats);
  };

  const generateMockReturns = (): TaxReturnSummary[] => {
    return [
      {
        id: '1',
        client_id: 'c1',
        client_name: 'Johnson Family Trust',
        tax_year: 2024,
        form_type: '1040',
        filing_status: 'married_filing_jointly',
        status: 'ready_to_file',
        taxpayer_name: 'Robert & Sarah Johnson',
        taxpayer_ssn_last4: '4532',
        total_income: 285000,
        taxable_income: 215000,
        total_tax: 42500,
        refund_or_owed: 3200,
        due_date: '2025-04-15',
        created_at: '2025-01-15',
      },
      {
        id: '2',
        client_id: 'c2',
        client_name: 'Tech Innovations LLC',
        tax_year: 2024,
        form_type: '1120S',
        status: 'data_entry',
        taxpayer_name: 'Tech Innovations LLC',
        total_income: 1250000,
        taxable_income: 890000,
        due_date: '2025-03-15',
        created_at: '2025-01-10',
      },
      {
        id: '3',
        client_id: 'c3',
        client_name: 'Williams Partnership',
        tax_year: 2024,
        form_type: '1065',
        status: 'review',
        taxpayer_name: 'Williams Investment Partners',
        total_income: 4500000,
        due_date: '2025-03-15',
        created_at: '2025-01-08',
      },
      {
        id: '4',
        client_id: 'c4',
        client_name: 'Martinez Consulting Inc',
        tax_year: 2024,
        form_type: '1120',
        status: 'filed',
        taxpayer_name: 'Martinez Consulting Inc',
        total_income: 750000,
        taxable_income: 320000,
        total_tax: 67200,
        refund_or_owed: -12500,
        filed_date: '2025-02-28',
        created_at: '2025-01-05',
      },
      {
        id: '5',
        client_id: 'c5',
        client_name: 'Emily Chen',
        tax_year: 2024,
        form_type: '1040',
        filing_status: 'single',
        status: 'accepted',
        taxpayer_name: 'Emily Chen',
        taxpayer_ssn_last4: '7891',
        total_income: 145000,
        taxable_income: 108000,
        total_tax: 21500,
        refund_or_owed: 2800,
        filed_date: '2025-02-15',
        created_at: '2025-01-20',
      },
      {
        id: '6',
        client_id: 'c6',
        client_name: 'Community Foundation',
        tax_year: 2024,
        form_type: '990',
        status: 'draft',
        taxpayer_name: 'Community Foundation of Metro',
        total_income: 2100000,
        due_date: '2025-05-15',
        created_at: '2025-02-01',
      },
    ];
  };

  const filteredReturns = returns.filter(ret => {
    const matchesSearch =
      ret.taxpayer_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ret.client_name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesYear = yearFilter === 'all' || ret.tax_year === yearFilter;
    const matchesForm = formFilter === 'all' || ret.form_type === formFilter;
    const matchesStatus = statusFilter === 'all' || ret.status === statusFilter;
    return matchesSearch && matchesYear && matchesForm && matchesStatus;
  });

  const getStatusConfig = (status: TaxReturnStatus) => {
    const configs: Record<TaxReturnStatus, { color: string; bgColor: string; icon: React.ElementType; label: string }> = {
      draft: { color: 'text-gray-600', bgColor: 'bg-gray-100', icon: FileText, label: 'Draft' },
      data_entry: { color: 'text-blue-600', bgColor: 'bg-blue-100', icon: Clock, label: 'Data Entry' },
      review: { color: 'text-yellow-600', bgColor: 'bg-yellow-100', icon: RefreshCw, label: 'In Review' },
      calculating: { color: 'text-purple-600', bgColor: 'bg-purple-100', icon: Calculator, label: 'Calculating' },
      ready_to_file: { color: 'text-green-600', bgColor: 'bg-green-100', icon: CheckCircle, label: 'Ready to File' },
      filed: { color: 'text-indigo-600', bgColor: 'bg-indigo-100', icon: Send, label: 'Filed' },
      accepted: { color: 'text-emerald-600', bgColor: 'bg-emerald-100', icon: CheckCircle, label: 'Accepted' },
      rejected: { color: 'text-red-600', bgColor: 'bg-red-100', icon: XCircle, label: 'Rejected' },
      amended: { color: 'text-orange-600', bgColor: 'bg-orange-100', icon: AlertCircle, label: 'Amended' },
    };
    return configs[status] || configs.draft;
  };

  const getFormTypeLabel = (formType: TaxFormType) => {
    const labels: Record<TaxFormType, string> = {
      '1040': 'Form 1040 - Individual',
      '1120': 'Form 1120 - C-Corp',
      '1120S': 'Form 1120-S - S-Corp',
      '1065': 'Form 1065 - Partnership',
      '990': 'Form 990 - Non-Profit',
      '941': 'Form 941 - Quarterly',
      '940': 'Form 940 - FUTA',
    };
    return labels[formType] || formType;
  };

  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading tax returns...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tax Returns</h1>
          <p className="text-gray-600 mt-1">
            Manage and file tax returns for your clients
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="fluent-btn-primary"
        >
          <Plus className="w-5 h-5" />
          New Return
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Returns</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">In Progress</p>
              <p className="text-2xl font-bold text-gray-900">{stats.inProgress}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Ready to File</p>
              <p className="text-2xl font-bold text-gray-900">{stats.readyToFile}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl p-5 shadow-sm border border-gray-200"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Refunds</p>
              <p className="text-2xl font-bold text-emerald-600">{formatCurrency(stats.totalRefunds)}</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-200">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by taxpayer or client name..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          <select
            value={yearFilter}
            onChange={(e) => setYearFilter(e.target.value === 'all' ? 'all' : Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Years</option>
            <option value="2024">2024</option>
            <option value="2023">2023</option>
            <option value="2022">2022</option>
          </select>

          <select
            value={formFilter}
            onChange={(e) => setFormFilter(e.target.value as TaxFormType | 'all')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Forms</option>
            <option value="1040">1040 - Individual</option>
            <option value="1120">1120 - C-Corp</option>
            <option value="1120S">1120-S - S-Corp</option>
            <option value="1065">1065 - Partnership</option>
            <option value="990">990 - Non-Profit</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as TaxReturnStatus | 'all')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="data_entry">Data Entry</option>
            <option value="review">In Review</option>
            <option value="ready_to_file">Ready to File</option>
            <option value="filed">Filed</option>
            <option value="accepted">Accepted</option>
          </select>
        </div>
      </div>

      {/* Returns List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Taxpayer / Client
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Form / Year
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Total Income
                </th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Refund / Owed
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Due Date
                </th>
                <th className="px-6 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredReturns.map((ret, index) => {
                const statusConfig = getStatusConfig(ret.status);
                const StatusIcon = statusConfig.icon;
                const isRefund = (ret.refund_or_owed || 0) > 0;

                return (
                  <motion.tr
                    key={ret.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate(`/firm/tax-returns/${ret.id}`)}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-gray-100 rounded-lg">
                          {ret.form_type === '1040' ? (
                            <User className="w-5 h-5 text-gray-600" />
                          ) : (
                            <Building2 className="w-5 h-5 text-gray-600" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{ret.taxpayer_name}</p>
                          <p className="text-sm text-gray-500">{ret.client_name}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">Form {ret.form_type}</p>
                        <p className="text-sm text-gray-500">Tax Year {ret.tax_year}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusConfig.bgColor} ${statusConfig.color}`}>
                        <StatusIcon className="w-3.5 h-3.5" />
                        {statusConfig.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="font-medium text-gray-900">
                        {formatCurrency(ret.total_income)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {ret.refund_or_owed !== undefined ? (
                        <span className={`font-medium ${isRefund ? 'text-green-600' : 'text-red-600'}`}>
                          {isRefund ? '+' : ''}{formatCurrency(ret.refund_or_owed)}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Calendar className="w-4 h-4" />
                        {ret.due_date ? new Date(ret.due_date).toLocaleDateString() : '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/firm/tax-returns/${ret.id}`);
                        }}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      </button>
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredReturns.length === 0 && (
          <div className="text-center py-12">
            <Calculator className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">No tax returns found</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-4 text-primary-600 hover:text-primary-700 font-medium"
            >
              Create your first tax return
            </button>
          </div>
        )}
      </div>

      {/* Create Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <CreateTaxReturnModal
            onClose={() => setShowCreateModal(false)}
            onCreated={(newReturn) => {
              setReturns([newReturn, ...returns]);
              calculateStats([newReturn, ...returns]);
              setShowCreateModal(false);
              toast.success('Tax return created successfully');
              navigate(`/firm/tax-returns/${newReturn.id}`);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

// Create Tax Return Modal Component
const CreateTaxReturnModal: React.FC<{
  onClose: () => void;
  onCreated: (ret: TaxReturnSummary) => void;
}> = ({ onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    taxpayer_first_name: '',
    taxpayer_last_name: '',
    tax_year: 2024,
    form_type: '1040' as TaxFormType,
    filing_status: 'single' as FilingStatus,
    client_id: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const newReturn = await taxService.createReturn(formData);
      onCreated({
        id: newReturn.id,
        client_id: newReturn.client_id,
        tax_year: newReturn.tax_year,
        form_type: newReturn.form_type,
        filing_status: newReturn.filing_status,
        status: newReturn.status,
        taxpayer_name: `${newReturn.taxpayer_first_name} ${newReturn.taxpayer_last_name}`,
        created_at: newReturn.created_at,
      });
    } catch (error) {
      // Mock success for demo
      const mockReturn: TaxReturnSummary = {
        id: `new-${Date.now()}`,
        client_id: formData.client_id || 'mock-client',
        tax_year: formData.tax_year,
        form_type: formData.form_type,
        filing_status: formData.filing_status,
        status: 'draft',
        taxpayer_name: `${formData.taxpayer_first_name} ${formData.taxpayer_last_name}`,
        created_at: new Date().toISOString(),
      };
      onCreated(mockReturn);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-white rounded-xl shadow-xl max-w-lg w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Create New Tax Return</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                First Name *
              </label>
              <input
                type="text"
                value={formData.taxpayer_first_name}
                onChange={(e) => setFormData({ ...formData, taxpayer_first_name: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Last Name *
              </label>
              <input
                type="text"
                value={formData.taxpayer_last_name}
                onChange={(e) => setFormData({ ...formData, taxpayer_last_name: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tax Year *
              </label>
              <select
                value={formData.tax_year}
                onChange={(e) => setFormData({ ...formData, tax_year: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value={2024}>2024</option>
                <option value={2023}>2023</option>
                <option value={2022}>2022</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Form Type *
              </label>
              <select
                value={formData.form_type}
                onChange={(e) => setFormData({ ...formData, form_type: e.target.value as TaxFormType })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="1040">1040 - Individual</option>
                <option value="1120">1120 - C-Corp</option>
                <option value="1120S">1120-S - S-Corp</option>
                <option value="1065">1065 - Partnership</option>
                <option value="990">990 - Non-Profit</option>
              </select>
            </div>
          </div>

          {formData.form_type === '1040' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Filing Status *
              </label>
              <select
                value={formData.filing_status}
                onChange={(e) => setFormData({ ...formData, filing_status: e.target.value as FilingStatus })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="single">Single</option>
                <option value="married_filing_jointly">Married Filing Jointly</option>
                <option value="married_filing_separately">Married Filing Separately</option>
                <option value="head_of_household">Head of Household</option>
                <option value="qualifying_widow">Qualifying Surviving Spouse</option>
              </select>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !formData.taxpayer_first_name || !formData.taxpayer_last_name}
              className="fluent-btn-primary"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                'Create Return'
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
};

export default TaxReturns;
