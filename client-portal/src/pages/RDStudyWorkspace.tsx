/**
 * R&D Study Workspace
 * Comprehensive workspace for managing an R&D tax credit study
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FlaskConical,
  ArrowLeft,
  Building2,
  Calendar,
  DollarSign,
  Users,
  FileText,
  CheckCircle,
  AlertTriangle,
  Clock,
  Settings,
  Upload,
  Calculator,
  MessageSquare,
  History,
  Download,
  Play,
  Check,
  X,
  ChevronRight,
  Brain,
  Target,
  TrendingUp,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { rdStudyService } from '../services/rd-study.service';
import { RDStudy, RDProject, RDEmployee, RDStudyStatus } from '../types';
import toast from 'react-hot-toast';

type TabId = 'overview' | 'projects' | 'employees' | 'qres' | 'calculations' | 'narratives' | 'documents' | 'review';

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

const tabs: { id: TabId; label: string; icon: React.ElementType }[] = [
  { id: 'overview', label: 'Overview', icon: Target },
  { id: 'projects', label: 'Projects', icon: FlaskConical },
  { id: 'employees', label: 'Employees', icon: Users },
  { id: 'qres', label: 'QREs', icon: DollarSign },
  { id: 'calculations', label: 'Calculations', icon: Calculator },
  { id: 'narratives', label: 'Narratives', icon: MessageSquare },
  { id: 'documents', label: 'Documents', icon: FileText },
  { id: 'review', label: 'Review Queue', icon: CheckCircle },
];

const RDStudyWorkspace: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [study, setStudy] = useState<RDStudy | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [projects, setProjects] = useState<RDProject[]>([]);
  const [employees, setEmployees] = useState<RDEmployee[]>([]);
  const [qreSummary, setQreSummary] = useState<any>(null);
  const [reviewQueue, setReviewQueue] = useState<any>(null);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    if (id) {
      loadStudy();
    }
  }, [id]);

  useEffect(() => {
    if (study) {
      loadTabData();
    }
  }, [activeTab, study]);

  const loadStudy = async () => {
    try {
      setLoading(true);
      const data = await rdStudyService.getStudy(id!);
      setStudy(data);
    } catch (error) {
      console.error('Failed to load study:', error);
      toast.error('Failed to load R&D study');
      navigate('/firm/rd-studies');
    } finally {
      setLoading(false);
    }
  };

  const loadTabData = async () => {
    if (!study) return;

    try {
      switch (activeTab) {
        case 'projects':
          const projectData = await rdStudyService.listProjects(study.id);
          setProjects(projectData);
          break;
        case 'employees':
          const employeeData = await rdStudyService.listEmployees(study.id);
          setEmployees(employeeData);
          break;
        case 'qres':
          const qreData = await rdStudyService.getQRESummary(study.id);
          setQreSummary(qreData);
          break;
        case 'review':
          const reviewData = await rdStudyService.getReviewQueue(study.id);
          setReviewQueue(reviewData);
          break;
      }
    } catch (error) {
      console.error(`Failed to load ${activeTab} data:`, error);
    }
  };

  const handleCalculate = async () => {
    if (!study) return;
    try {
      setCalculating(true);
      await rdStudyService.calculateCredits(study.id);
      toast.success('Credits calculated successfully');
      loadStudy();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Calculation failed');
    } finally {
      setCalculating(false);
    }
  };

  const handleTransition = async (newStatus: RDStudyStatus) => {
    if (!study) return;
    try {
      await rdStudyService.transitionStudy(study.id, newStatus);
      toast.success(`Study moved to ${statusConfig[newStatus].label}`);
      loadStudy();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update status');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 text-purple-500 animate-spin" />
          <p className="text-gray-600">Loading study...</p>
        </div>
      </div>
    );
  }

  if (!study) {
    return (
      <div className="text-center py-16">
        <h2 className="text-xl text-gray-600">Study not found</h2>
        <button onClick={() => navigate('/firm/rd-studies')} className="btn-primary mt-4">
          Back to Studies
        </button>
      </div>
    );
  }

  const status = statusConfig[study.status] || statusConfig.draft;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <button
            onClick={() => navigate('/firm/rd-studies')}
            className="text-sm text-gray-600 hover:text-gray-900 mb-3 flex items-center gap-1"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to R&D Studies
          </button>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center">
              <FlaskConical className="w-7 h-7 text-purple-600" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-gray-900">{study.name}</h1>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${status.bgColor} ${status.color}`}>
                  {status.label}
                </span>
                {study.has_open_flags && (
                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-600 flex items-center gap-1">
                    <AlertTriangle className="w-4 h-4" />
                    {study.risk_flags.length} Flags
                  </span>
                )}
              </div>
              <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <Building2 className="w-4 h-4" />
                  {study.entity_name}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  Tax Year {study.tax_year}
                </span>
                {study.ein && <span>EIN: {study.ein}</span>}
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCalculate}
            disabled={calculating}
            className="btn-secondary flex items-center gap-2"
          >
            {calculating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Calculator className="w-4 h-4" />
            )}
            Calculate Credits
          </button>
          {study.status === 'cpa_review' && (
            <button
              onClick={() => handleTransition('approved')}
              className="btn-primary flex items-center gap-2"
            >
              <Check className="w-4 h-4" />
              Approve Study
            </button>
          )}
        </div>
      </div>

      {/* Credit Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total QRE</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(study.total_qre)}</p>
            </div>
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-purple-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Federal Credit</p>
              <p className="text-2xl font-bold text-blue-600">{formatCurrency(study.federal_credit_final)}</p>
              <p className="text-xs text-gray-400 mt-1">
                {study.selected_method === 'asc' ? 'ASC Method' : 'Regular Method'}
              </p>
            </div>
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">State Credits</p>
              <p className="text-2xl font-bold text-indigo-600">{formatCurrency(study.total_state_credits)}</p>
              <p className="text-xs text-gray-400 mt-1">{study.states.length} state(s)</p>
            </div>
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <Building2 className="w-5 h-5 text-indigo-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card bg-gradient-to-br from-green-500 to-green-600 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Total Credits</p>
              <p className="text-2xl font-bold">{formatCurrency(study.total_credits)}</p>
            </div>
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-white" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-1 overflow-x-auto">
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                  isActive
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Study Details */}
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Study Details</h3>
                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">Entity Type</span>
                    <span className="font-medium">{study.entity_type.replace('_', ' ').toUpperCase()}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">Fiscal Year</span>
                    <span className="font-medium">
                      {new Date(study.fiscal_year_start).toLocaleDateString()} -
                      {new Date(study.fiscal_year_end).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">Short Year</span>
                    <span className="font-medium">{study.is_short_year ? `Yes (${study.short_year_days} days)` : 'No'}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-500">Controlled Group</span>
                    <span className="font-medium">{study.is_controlled_group ? study.controlled_group_name : 'No'}</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-gray-500">States</span>
                    <span className="font-medium">{study.states.join(', ') || 'None'}</span>
                  </div>
                </div>
              </div>

              {/* AI Analysis */}
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-500" />
                  AI Analysis
                </h3>
                {study.ai_analysis_summary ? (
                  <div className="space-y-4">
                    <p className="text-gray-600">{study.ai_analysis_summary}</p>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-3 bg-green-50 rounded-lg">
                        <p className="text-sm text-green-600">Opportunity Score</p>
                        <p className="text-2xl font-bold text-green-700">
                          {((study.ai_opportunity_score || 0) * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div className="p-3 bg-orange-50 rounded-lg">
                        <p className="text-sm text-orange-600">Risk Score</p>
                        <p className="text-2xl font-bold text-orange-700">
                          {((study.ai_risk_score || 0) * 100).toFixed(0)}%
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Brain className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p>AI analysis not yet available</p>
                    <p className="text-sm">Upload documents to trigger analysis</p>
                  </div>
                )}
              </div>

              {/* Risk Flags */}
              {study.risk_flags.length > 0 && (
                <div className="card lg:col-span-2">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-orange-500" />
                    Risk Flags ({study.risk_flags.length})
                  </h3>
                  <div className="space-y-3">
                    {study.risk_flags.map((flag, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border ${
                          flag.severity === 'high' ? 'bg-red-50 border-red-200' :
                          flag.severity === 'medium' ? 'bg-orange-50 border-orange-200' :
                          'bg-yellow-50 border-yellow-200'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <AlertTriangle className={`w-5 h-5 flex-shrink-0 ${
                            flag.severity === 'high' ? 'text-red-500' :
                            flag.severity === 'medium' ? 'text-orange-500' :
                            'text-yellow-500'
                          }`} />
                          <div>
                            <p className="font-medium text-gray-900">{flag.type}</p>
                            <p className="text-sm text-gray-600">{flag.message}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'projects' && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">R&D Projects ({projects.length})</h3>
                <button className="btn-secondary text-sm">Add Project</button>
              </div>
              {projects.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <FlaskConical className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>No projects added yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {projects.map(project => (
                    <div key={project.id} className="p-4 border rounded-lg hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">{project.name}</h4>
                          <p className="text-sm text-gray-500">{project.department}</p>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            project.qualification_status === 'qualified' ? 'bg-green-100 text-green-700' :
                            project.qualification_status === 'not_qualified' ? 'bg-red-100 text-red-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {project.qualification_status}
                          </span>
                          {project.overall_score && (
                            <span className="text-sm text-gray-500">
                              Score: {(project.overall_score * 100).toFixed(0)}%
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'employees' && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">R&D Employees ({employees.length})</h3>
                <button className="btn-secondary text-sm">Add Employee</button>
              </div>
              {employees.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Users className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>No employees added yet</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Name</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Title</th>
                        <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">Total Wages</th>
                        <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">Qualified %</th>
                        <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">Qualified Wages</th>
                        <th className="px-4 py-3 text-center text-sm font-medium text-gray-600">Reviewed</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {employees.map(emp => (
                        <tr key={emp.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-medium">{emp.name}</td>
                          <td className="px-4 py-3 text-gray-500">{emp.title || '-'}</td>
                          <td className="px-4 py-3 text-right">{formatCurrency(emp.total_wages)}</td>
                          <td className="px-4 py-3 text-right">{emp.qualified_time_percentage}%</td>
                          <td className="px-4 py-3 text-right font-medium text-green-600">
                            {formatCurrency(emp.qualified_wages)}
                          </td>
                          <td className="px-4 py-3 text-center">
                            {emp.cpa_reviewed ? (
                              <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                            ) : (
                              <Clock className="w-5 h-5 text-gray-400 mx-auto" />
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'qres' && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">QRE Summary</h3>
              {qreSummary ? (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {Object.entries(qreSummary.by_category || {}).map(([category, data]: [string, any]) => (
                    <div key={category} className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-500 capitalize">{category.replace('_', ' ')}</p>
                      <p className="text-xl font-bold text-gray-900">{formatCurrency(data.qualified || 0)}</p>
                      <p className="text-xs text-gray-400">{data.count} items</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <DollarSign className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>No QRE data available</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'calculations' && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Credit Calculations</h3>
                <button onClick={handleCalculate} disabled={calculating} className="btn-primary text-sm flex items-center gap-2">
                  {calculating ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                  Recalculate
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-3">Federal - Regular Method (20%)</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Total QRE</span>
                      <span>{formatCurrency(study.total_qre)}</span>
                    </div>
                    <div className="flex justify-between font-medium text-blue-600">
                      <span>Credit</span>
                      <span>{formatCurrency(study.federal_credit_regular)}</span>
                    </div>
                  </div>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-3">Federal - ASC Method (14%)</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Total QRE</span>
                      <span>{formatCurrency(study.total_qre)}</span>
                    </div>
                    <div className="flex justify-between font-medium text-blue-600">
                      <span>Credit</span>
                      <span>{formatCurrency(study.federal_credit_asc)}</span>
                    </div>
                  </div>
                </div>
              </div>
              {study.recommended_method && (
                <div className="mt-4 p-4 bg-green-50 rounded-lg">
                  <p className="text-green-700">
                    <strong>Recommended:</strong> {study.recommended_method === 'asc' ? 'ASC' : 'Regular'} Method
                    {study.method_selection_reason && ` - ${study.method_selection_reason}`}
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'review' && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">CPA Review Queue</h3>
              {reviewQueue ? (
                <div>
                  <div className="grid grid-cols-4 gap-4 mb-6">
                    <div className="p-3 bg-gray-50 rounded-lg text-center">
                      <p className="text-2xl font-bold">{reviewQueue.total_items}</p>
                      <p className="text-sm text-gray-500">Total Items</p>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg text-center">
                      <p className="text-2xl font-bold text-green-600">{reviewQueue.reviewed_items}</p>
                      <p className="text-sm text-gray-500">Reviewed</p>
                    </div>
                    <div className="p-3 bg-orange-50 rounded-lg text-center">
                      <p className="text-2xl font-bold text-orange-600">{reviewQueue.pending_items}</p>
                      <p className="text-sm text-gray-500">Pending</p>
                    </div>
                    <div className="p-3 bg-red-50 rounded-lg text-center">
                      <p className="text-2xl font-bold text-red-600">{reviewQueue.high_priority_items}</p>
                      <p className="text-sm text-gray-500">High Priority</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    {(reviewQueue.items || []).map((item: any) => (
                      <div key={item.id} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-xs text-gray-400 uppercase">{item.entity_type}</span>
                            <h4 className="font-medium">{item.title}</h4>
                            <p className="text-sm text-gray-500">{item.description}</p>
                          </div>
                          <button className="btn-secondary text-sm">Review</button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>Review queue loading...</p>
                </div>
              )}
            </div>
          )}

          {(activeTab === 'narratives' || activeTab === 'documents') && (
            <div className="card text-center py-12">
              <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="text-gray-500">
                {activeTab === 'narratives' ? 'Narrative management' : 'Document management'} coming soon
              </p>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default RDStudyWorkspace;
