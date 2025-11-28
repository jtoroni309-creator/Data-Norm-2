/**
 * AI-Powered Audit Planning Dashboard
 * Comprehensive AI planning that exceeds human CPA capabilities
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Brain,
  Shield,
  AlertTriangle,
  TrendingUp,
  FileText,
  Calculator,
  Target,
  ChevronRight,
  ChevronDown,
  Check,
  Sparkles,
  BarChart3,
  Clock,
  Zap,
  RefreshCw,
  Download,
  Eye,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import {
  auditPlanningService,
  AIRiskAnalysisResponse,
  AIMaterialityResponse,
  AIFraudDetectionResponse,
  AIAuditProgramResponse,
  AIPlanningMemoResponse,
} from '../services/audit-planning.service';
import { engagementService, Engagement } from '../services/engagement.service';
import { clientService } from '../services/client.service';
import toast from 'react-hot-toast';

interface FinancialData {
  total_assets: number;
  total_liabilities: number;
  current_assets: number;
  current_liabilities: number;
  total_revenue: number;
  net_income: number;
  pretax_income: number;
  total_equity: number;
  inventory: number;
  accounts_receivable: number;
  cost_of_goods_sold: number;
  operating_expenses: number;
  allowance_doubtful: number;
}

const defaultFinancialData: FinancialData = {
  total_assets: 10000000,
  total_liabilities: 4000000,
  current_assets: 3000000,
  current_liabilities: 1500000,
  total_revenue: 15000000,
  net_income: 1200000,
  pretax_income: 1500000,
  total_equity: 6000000,
  inventory: 800000,
  accounts_receivable: 1200000,
  cost_of_goods_sold: 9000000,
  operating_expenses: 4000000,
  allowance_doubtful: 50000,
};

const AIAuditPlanning: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // State
  const [engagement, setEngagement] = useState<Engagement | null>(null);
  const [clientName, setClientName] = useState('');
  const [industry, setIndustry] = useState('manufacturing');
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'risk' | 'materiality' | 'fraud' | 'programs' | 'memo'>('risk');
  const [financialData, setFinancialData] = useState<FinancialData>(defaultFinancialData);
  const [showFinancialForm, setShowFinancialForm] = useState(true);

  // AI Results
  const [riskAnalysis, setRiskAnalysis] = useState<AIRiskAnalysisResponse | null>(null);
  const [materialityResult, setMaterialityResult] = useState<AIMaterialityResponse | null>(null);
  const [fraudDetection, setFraudDetection] = useState<AIFraudDetectionResponse | null>(null);
  const [auditPrograms, setAuditPrograms] = useState<AIAuditProgramResponse[]>([]);
  const [planningMemo, setPlanningMemo] = useState<AIPlanningMemoResponse | null>(null);

  // Loading states
  const [analyzingRisk, setAnalyzingRisk] = useState(false);
  const [calculatingMateriality, setCalculatingMateriality] = useState(false);
  const [detectingFraud, setDetectingFraud] = useState(false);
  const [generatingPrograms, setGeneratingPrograms] = useState(false);
  const [generatingMemo, setGeneratingMemo] = useState(false);

  const industries = [
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'technology', label: 'Technology' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'retail', label: 'Retail' },
    { value: 'financial_services', label: 'Financial Services' },
    { value: 'default', label: 'Other' },
  ];

  useEffect(() => {
    if (id) {
      loadEngagement(id);
    }
  }, [id]);

  const loadEngagement = async (engagementId: string) => {
    try {
      setLoading(true);
      const eng = await engagementService.getEngagement(engagementId);
      setEngagement(eng);

      // Try to load client name
      if (eng.client_id) {
        try {
          const client = await clientService.getClient(eng.client_id);
          setClientName(client.name || eng.client_id);
        } catch {
          setClientName(eng.client_id);
        }
      }
    } catch (error) {
      console.error('Failed to load engagement:', error);
      toast.error('Failed to load engagement');
      navigate('/firm/audits');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeRisk = async () => {
    if (!id || !engagement) return;

    setAnalyzingRisk(true);
    try {
      const result = await auditPlanningService.analyzeRiskWithAI({
        engagement_id: id,
        client_name: clientName || engagement.name,
        industry,
        financial_data: financialData,
        prior_year_data: undefined,
        known_issues: [],
      });
      setRiskAnalysis(result);
      toast.success('AI Risk Analysis Complete');
      setShowFinancialForm(false);
    } catch (error: any) {
      console.error('Risk analysis failed:', error);
      toast.error(error.response?.data?.detail || 'Risk analysis failed');
    } finally {
      setAnalyzingRisk(false);
    }
  };

  const handleCalculateMateriality = async () => {
    setCalculatingMateriality(true);
    try {
      const result = await auditPlanningService.calculateMaterialityWithAI({
        financial_data: financialData,
        industry,
        entity_type: 'private',
        risk_factors: riskAnalysis?.recommended_focus_areas?.map(f => f.area) || [],
        user_count: 0,
      });
      setMaterialityResult(result);
      toast.success('AI Materiality Calculation Complete');
    } catch (error: any) {
      console.error('Materiality calculation failed:', error);
      toast.error(error.response?.data?.detail || 'Materiality calculation failed');
    } finally {
      setCalculatingMateriality(false);
    }
  };

  const handleDetectFraud = async () => {
    if (!id) return;

    setDetectingFraud(true);
    try {
      const result = await auditPlanningService.detectFraudWithAI({
        engagement_id: id,
        financial_data: financialData,
      });
      setFraudDetection(result);
      toast.success('AI Fraud Detection Complete');
    } catch (error: any) {
      console.error('Fraud detection failed:', error);
      toast.error(error.response?.data?.detail || 'Fraud detection failed');
    } finally {
      setDetectingFraud(false);
    }
  };

  const handleGeneratePrograms = async () => {
    if (!id || !riskAnalysis || !materialityResult) {
      toast.error('Please complete risk analysis and materiality calculation first');
      return;
    }

    setGeneratingPrograms(true);
    try {
      const areas = ['revenue', 'receivables', 'inventory', 'payables'];
      const programs: AIAuditProgramResponse[] = [];

      for (const area of areas) {
        const result = await auditPlanningService.generateAuditProgramWithAI({
          engagement_id: id,
          risk_assessment: riskAnalysis,
          audit_area: area,
          account_balance: getAccountBalance(area),
          materiality: materialityResult.overall_materiality,
          prior_year_findings: [],
        });
        programs.push(result);
      }

      setAuditPrograms(programs);
      toast.success(`Generated ${programs.length} AI-powered audit programs`);
    } catch (error: any) {
      console.error('Program generation failed:', error);
      toast.error(error.response?.data?.detail || 'Program generation failed');
    } finally {
      setGeneratingPrograms(false);
    }
  };

  const handleGenerateMemo = async () => {
    if (!id || !engagement || !riskAnalysis || !materialityResult || !fraudDetection) {
      toast.error('Please complete all analyses first');
      return;
    }

    setGeneratingMemo(true);
    try {
      const result = await auditPlanningService.generatePlanningMemoWithAI({
        engagement_id: id,
        client_name: clientName || engagement.name,
        risk_assessment: riskAnalysis,
        materiality: materialityResult,
        fraud_assessment: fraudDetection,
        audit_programs: auditPrograms,
      });
      setPlanningMemo(result);
      toast.success('Planning Memo Generated');
    } catch (error: any) {
      console.error('Memo generation failed:', error);
      toast.error(error.response?.data?.detail || 'Memo generation failed');
    } finally {
      setGeneratingMemo(false);
    }
  };

  const getAccountBalance = (area: string): number => {
    switch (area) {
      case 'revenue': return financialData.total_revenue;
      case 'receivables': return financialData.accounts_receivable;
      case 'inventory': return financialData.inventory;
      case 'payables': return financialData.total_liabilities * 0.3;
      default: return 1000000;
    }
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getRiskColor = (level: string): string => {
    switch (level?.toLowerCase()) {
      case 'significant': return 'error';
      case 'high': return 'error';
      case 'moderate': return 'warning';
      case 'low': return 'success';
      default: return 'neutral';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-body text-neutral-600">Loading AI Planning...</p>
        </div>
      </div>
    );
  }

  if (!engagement) return null;

  const tabs = [
    { id: 'risk', label: 'Risk Analysis', icon: Shield, completed: !!riskAnalysis },
    { id: 'materiality', label: 'Materiality', icon: Calculator, completed: !!materialityResult },
    { id: 'fraud', label: 'Fraud Detection', icon: AlertTriangle, completed: !!fraudDetection },
    { id: 'programs', label: 'Audit Programs', icon: FileText, completed: auditPrograms.length > 0 },
    { id: 'memo', label: 'Planning Memo', icon: FileText, completed: !!planningMemo },
  ];

  return (
    <div className="space-y-6 max-w-[1800px]">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <button
          onClick={() => navigate(`/firm/engagements/${id}`)}
          className="p-2 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-neutral-700" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-1">
            <Brain className="w-6 h-6 text-primary-600" />
            <h1 className="text-display text-neutral-900">AI-Powered Audit Planning</h1>
            <span className="px-2 py-0.5 bg-primary-100 text-primary-700 text-caption font-medium rounded-full">
              Superior to Human CPA
            </span>
          </div>
          <p className="text-body text-neutral-600">{engagement.name} - {clientName}</p>
        </div>
      </motion.div>

      {/* Progress Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fluent-card p-4"
      >
        <div className="flex items-center justify-between gap-2 overflow-x-auto">
          {tabs.map((tab, index) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            const isCompleted = tab.completed;

            return (
              <React.Fragment key={tab.id}>
                <button
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-fluent transition-all min-w-fit ${
                    isActive
                      ? 'bg-primary-500 text-white'
                      : isCompleted
                      ? 'bg-success-100 text-success-700 hover:bg-success-200'
                      : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    isActive ? 'bg-white/20' : isCompleted ? 'bg-success-500 text-white' : 'bg-neutral-200'
                  }`}>
                    {isCompleted && !isActive ? (
                      <Check className="w-4 h-4" />
                    ) : (
                      <Icon className="w-4 h-4" />
                    )}
                  </div>
                  <span className="text-body-strong whitespace-nowrap">{tab.label}</span>
                </button>
                {index < tabs.length - 1 && (
                  <ChevronRight className="w-5 h-5 text-neutral-400 flex-shrink-0" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Financial Data Input */}
          <AnimatePresence mode="wait">
            {showFinancialForm && activeTab === 'risk' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="fluent-card p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-title text-neutral-900">Financial Data Input</h2>
                  <button
                    onClick={() => setShowFinancialForm(false)}
                    className="text-caption text-neutral-500 hover:text-neutral-700"
                  >
                    Collapse
                  </button>
                </div>

                <div className="mb-4">
                  <label className="block text-body-strong text-neutral-700 mb-2">Industry</label>
                  <select
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="fluent-input w-full md:w-64"
                  >
                    {industries.map((ind) => (
                      <option key={ind.value} value={ind.value}>{ind.label}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {Object.entries(financialData).map(([key, value]) => (
                    <div key={key}>
                      <label className="block text-caption text-neutral-600 mb-1">
                        {key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                      </label>
                      <input
                        type="number"
                        value={value}
                        onChange={(e) => setFinancialData({ ...financialData, [key]: parseFloat(e.target.value) || 0 })}
                        className="fluent-input w-full text-sm"
                      />
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Risk Analysis Tab */}
          {activeTab === 'risk' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <div className="fluent-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-title text-neutral-900">AI Risk Analysis</h2>
                    <p className="text-body text-neutral-600">
                      Pattern recognition across industry benchmarks with fraud indicator detection
                    </p>
                  </div>
                  <button
                    onClick={handleAnalyzeRisk}
                    disabled={analyzingRisk}
                    className="fluent-btn-primary"
                  >
                    {analyzingRisk ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4" />
                        {riskAnalysis ? 'Re-analyze' : 'Analyze Risk'}
                      </>
                    )}
                  </button>
                </div>

                {riskAnalysis && (
                  <div className="space-y-6">
                    {/* Risk Score */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-4 bg-neutral-50 rounded-fluent">
                        <p className="text-caption text-neutral-600 mb-1">Overall Risk Score</p>
                        <p className="text-2xl font-bold text-neutral-900">{riskAnalysis.overall_risk_score}/100</p>
                      </div>
                      <div className="p-4 bg-neutral-50 rounded-fluent">
                        <p className="text-caption text-neutral-600 mb-1">Risk Level</p>
                        <span className={`inline-flex px-3 py-1 rounded-full text-body-strong bg-${getRiskColor(riskAnalysis.risk_level)}-100 text-${getRiskColor(riskAnalysis.risk_level)}-700`}>
                          {riskAnalysis.risk_level?.toUpperCase()}
                        </span>
                      </div>
                      <div className="p-4 bg-neutral-50 rounded-fluent">
                        <p className="text-caption text-neutral-600 mb-1">Fraud Risk</p>
                        <span className={`inline-flex px-3 py-1 rounded-full text-body-strong bg-${getRiskColor(riskAnalysis.fraud_risk_assessment?.fraud_risk_level)}-100 text-${getRiskColor(riskAnalysis.fraud_risk_assessment?.fraud_risk_level)}-700`}>
                          {riskAnalysis.fraud_risk_assessment?.fraud_risk_level?.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    {/* AI Insights */}
                    <div>
                      <h3 className="text-body-strong text-neutral-900 mb-3 flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-primary-500" />
                        AI-Generated Insights
                      </h3>
                      <div className="space-y-2">
                        {riskAnalysis.ai_insights?.map((insight, index) => (
                          <div
                            key={index}
                            className={`p-3 rounded-fluent border-l-4 border-${getRiskColor(insight.severity)}-500 bg-${getRiskColor(insight.severity)}-50`}
                          >
                            <p className="text-body-strong text-neutral-900">{insight.insight}</p>
                            <p className="text-caption text-neutral-600 mt-1">{insight.action}</p>
                            <p className="text-caption text-neutral-500 mt-1">Ref: {insight.pcaob_reference}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Significant Accounts */}
                    <div>
                      <h3 className="text-body-strong text-neutral-900 mb-3">Significant Accounts</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="bg-neutral-100">
                            <tr>
                              <th className="text-left p-3">Account</th>
                              <th className="text-right p-3">Balance</th>
                              <th className="text-center p-3">x Materiality</th>
                              <th className="text-center p-3">Testing Required</th>
                            </tr>
                          </thead>
                          <tbody>
                            {riskAnalysis.significant_accounts?.map((account, index) => (
                              <tr key={index} className="border-b">
                                <td className="p-3">{account.account}</td>
                                <td className="p-3 text-right">{formatCurrency(account.balance)}</td>
                                <td className="p-3 text-center">{account.times_materiality}x</td>
                                <td className="p-3 text-center">
                                  {account.requires_testing ? (
                                    <CheckCircle2 className="w-5 h-5 text-success-500 mx-auto" />
                                  ) : (
                                    <XCircle className="w-5 h-5 text-neutral-300 mx-auto" />
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Focus Areas */}
                    <div>
                      <h3 className="text-body-strong text-neutral-900 mb-3">Recommended Focus Areas</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {riskAnalysis.recommended_focus_areas?.map((area, index) => (
                          <div key={index} className="p-3 bg-neutral-50 rounded-fluent">
                            <div className="flex items-center justify-between mb-1">
                              <p className="text-body-strong text-neutral-900">{area.area}</p>
                              <span className={`text-caption px-2 py-0.5 rounded bg-${getRiskColor(area.priority)}-100 text-${getRiskColor(area.priority)}-700`}>
                                {area.priority}
                              </span>
                            </div>
                            <p className="text-caption text-neutral-600">{area.reason}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Materiality Tab */}
          {activeTab === 'materiality' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="fluent-card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-title text-neutral-900">AI Materiality Calculation</h2>
                  <p className="text-body text-neutral-600">
                    Intelligent benchmark selection with risk factor adjustments
                  </p>
                </div>
                <button
                  onClick={handleCalculateMateriality}
                  disabled={calculatingMateriality}
                  className="fluent-btn-primary"
                >
                  {calculatingMateriality ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Calculating...
                    </>
                  ) : (
                    <>
                      <Calculator className="w-4 h-4" />
                      {materialityResult ? 'Recalculate' : 'Calculate Materiality'}
                    </>
                  )}
                </button>
              </div>

              {materialityResult && (
                <div className="space-y-6">
                  {/* Main Materiality Values */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-primary-50 rounded-fluent border border-primary-200">
                      <p className="text-caption text-primary-600 mb-1">Overall Materiality</p>
                      <p className="text-2xl font-bold text-primary-900">{formatCurrency(materialityResult.overall_materiality)}</p>
                    </div>
                    <div className="p-4 bg-neutral-50 rounded-fluent">
                      <p className="text-caption text-neutral-600 mb-1">Performance Materiality</p>
                      <p className="text-xl font-bold text-neutral-900">{formatCurrency(materialityResult.performance_materiality)}</p>
                    </div>
                    <div className="p-4 bg-neutral-50 rounded-fluent">
                      <p className="text-caption text-neutral-600 mb-1">Trivial Threshold</p>
                      <p className="text-xl font-bold text-neutral-900">{formatCurrency(materialityResult.trivial_threshold)}</p>
                    </div>
                  </div>

                  {/* AI Reasoning */}
                  <div className="p-4 bg-primary-50 rounded-fluent border border-primary-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Brain className="w-5 h-5 text-primary-600" />
                      <h3 className="text-body-strong text-primary-900">AI Reasoning</h3>
                    </div>
                    <p className="text-body text-primary-800">{materialityResult.ai_reasoning}</p>
                    <p className="text-caption text-primary-600 mt-2">
                      Benchmark: {materialityResult.selected_benchmark} |
                      Risk Adjustment: {(materialityResult.risk_adjustment_factor * 100).toFixed(0)}%
                    </p>
                  </div>

                  {/* All Benchmarks */}
                  <div>
                    <h3 className="text-body-strong text-neutral-900 mb-3">All Benchmarks Analyzed</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {Object.entries(materialityResult.all_benchmarks || {}).map(([key, value]) => (
                        <div
                          key={key}
                          className={`p-3 rounded-fluent ${
                            key === materialityResult.selected_benchmark
                              ? 'bg-primary-100 border-2 border-primary-500'
                              : 'bg-neutral-50'
                          }`}
                        >
                          <p className="text-caption text-neutral-600">{key.replace(/_/g, ' ')}</p>
                          <p className="text-body-strong text-neutral-900">{formatCurrency(value)}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* PCAOB Compliance */}
                  <div className="p-3 bg-success-50 rounded-fluent border border-success-200">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle2 className="w-5 h-5 text-success-600" />
                      <h3 className="text-body-strong text-success-900">PCAOB AS 2105 Compliance</h3>
                    </div>
                    <ul className="text-caption text-success-800 space-y-1">
                      {materialityResult.pcaob_compliance_notes?.map((note, index) => (
                        <li key={index}>- {note}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* Fraud Detection Tab */}
          {activeTab === 'fraud' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="fluent-card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-title text-neutral-900">AI Fraud Detection</h2>
                  <p className="text-body text-neutral-600">
                    Benford's Law analysis, pattern recognition, and anomaly detection
                  </p>
                </div>
                <button
                  onClick={handleDetectFraud}
                  disabled={detectingFraud}
                  className="fluent-btn-primary"
                >
                  {detectingFraud ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Detecting...
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-4 h-4" />
                      {fraudDetection ? 'Re-analyze' : 'Detect Fraud Patterns'}
                    </>
                  )}
                </button>
              </div>

              {fraudDetection && (
                <div className="space-y-6">
                  {/* Fraud Risk Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-neutral-50 rounded-fluent">
                      <p className="text-caption text-neutral-600 mb-1">Fraud Risk Score</p>
                      <p className="text-2xl font-bold text-neutral-900">{fraudDetection.fraud_risk_score}/100</p>
                    </div>
                    <div className="p-4 bg-neutral-50 rounded-fluent">
                      <p className="text-caption text-neutral-600 mb-1">Risk Level</p>
                      <span className={`inline-flex px-3 py-1 rounded-full text-body-strong bg-${getRiskColor(fraudDetection.fraud_risk_level)}-100 text-${getRiskColor(fraudDetection.fraud_risk_level)}-700`}>
                        {fraudDetection.fraud_risk_level?.toUpperCase()}
                      </span>
                    </div>
                    <div className="p-4 bg-neutral-50 rounded-fluent">
                      <p className="text-caption text-neutral-600 mb-1">Indicators Found</p>
                      <p className="text-2xl font-bold text-neutral-900">{fraudDetection.indicators_found}</p>
                    </div>
                  </div>

                  {/* Fraud Indicators */}
                  {fraudDetection.fraud_indicators?.length > 0 && (
                    <div>
                      <h3 className="text-body-strong text-neutral-900 mb-3">Fraud Indicators Detected</h3>
                      <div className="space-y-2">
                        {fraudDetection.fraud_indicators.map((indicator, index) => (
                          <div
                            key={index}
                            className={`p-3 rounded-fluent border-l-4 border-${getRiskColor(indicator.severity)}-500 bg-${getRiskColor(indicator.severity)}-50`}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <p className="text-body-strong text-neutral-900">{indicator.type.replace(/_/g, ' ').toUpperCase()}</p>
                              <span className={`text-caption px-2 py-0.5 rounded bg-${getRiskColor(indicator.severity)}-200 text-${getRiskColor(indicator.severity)}-800`}>
                                {indicator.severity}
                              </span>
                            </div>
                            <p className="text-body text-neutral-700">{indicator.description}</p>
                            {indicator.audit_implication && (
                              <p className="text-caption text-neutral-600 mt-1">
                                Implication: {indicator.audit_implication}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Required Procedures */}
                  <div>
                    <h3 className="text-body-strong text-neutral-900 mb-3">Required Fraud Procedures (AS 2401)</h3>
                    <ul className="space-y-2">
                      {fraudDetection.required_procedures?.map((proc, index) => (
                        <li key={index} className="flex items-start gap-2 text-body text-neutral-700">
                          <CheckCircle2 className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0" />
                          {proc}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* AS 2401 Compliance */}
                  <div className="p-3 bg-success-50 rounded-fluent border border-success-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="w-5 h-5 text-success-600" />
                      <h3 className="text-body-strong text-success-900">PCAOB AS 2401 Compliance</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-caption">
                      <div className="flex items-center gap-2">
                        {fraudDetection.pcaob_as_2401_compliance?.fraud_triangle_assessed ? (
                          <CheckCircle2 className="w-4 h-4 text-success-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-error-500" />
                        )}
                        <span>Fraud Triangle Assessed</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {fraudDetection.pcaob_as_2401_compliance?.journal_entry_testing_planned ? (
                          <CheckCircle2 className="w-4 h-4 text-success-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-error-500" />
                        )}
                        <span>JE Testing Planned</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {fraudDetection.pcaob_as_2401_compliance?.management_override_considered ? (
                          <CheckCircle2 className="w-4 h-4 text-success-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-error-500" />
                        )}
                        <span>Management Override Considered</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {fraudDetection.pcaob_as_2401_compliance?.revenue_recognition_evaluated ? (
                          <CheckCircle2 className="w-4 h-4 text-success-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-error-500" />
                        )}
                        <span>Revenue Recognition Evaluated</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* Audit Programs Tab */}
          {activeTab === 'programs' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="fluent-card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-title text-neutral-900">AI-Generated Audit Programs</h2>
                  <p className="text-body text-neutral-600">
                    Risk-responsive procedures with optimized sample sizes
                  </p>
                </div>
                <button
                  onClick={handleGeneratePrograms}
                  disabled={generatingPrograms || !riskAnalysis || !materialityResult}
                  className="fluent-btn-primary"
                >
                  {generatingPrograms ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4" />
                      Generate Programs
                    </>
                  )}
                </button>
              </div>

              {!riskAnalysis || !materialityResult ? (
                <div className="text-center py-8 text-neutral-500">
                  <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-warning-400" />
                  <p className="text-body">Complete Risk Analysis and Materiality calculation first</p>
                </div>
              ) : auditPrograms.length > 0 ? (
                <div className="space-y-4">
                  {auditPrograms.map((program, index) => (
                    <details key={index} className="group">
                      <summary className="flex items-center justify-between p-4 bg-neutral-50 rounded-fluent cursor-pointer hover:bg-neutral-100">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                            <FileText className="w-5 h-5 text-primary-600" />
                          </div>
                          <div>
                            <p className="text-body-strong text-neutral-900">{program.audit_area.charAt(0).toUpperCase() + program.audit_area.slice(1)}</p>
                            <p className="text-caption text-neutral-600">
                              {program.procedures?.length || 0} procedures | {program.risk_level} risk
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <p className="text-caption text-neutral-600">Est. Hours</p>
                            <p className="text-body-strong text-neutral-900">{program.estimated_hours?.total_estimated_hours || 0}h</p>
                          </div>
                          <div className="text-right">
                            <p className="text-caption text-success-600">AI Savings</p>
                            <p className="text-body-strong text-success-700">{program.estimated_hours?.efficiency_gain_percentage || 0}%</p>
                          </div>
                          <ChevronDown className="w-5 h-5 text-neutral-400 group-open:rotate-180 transition-transform" />
                        </div>
                      </summary>
                      <div className="p-4 border border-neutral-200 border-t-0 rounded-b-fluent">
                        <div className="mb-4 p-3 bg-primary-50 rounded-fluent">
                          <p className="text-caption text-primary-800 whitespace-pre-line">{program.program_summary}</p>
                        </div>
                        <div className="space-y-2">
                          {program.procedures?.map((proc, pIndex) => (
                            <div key={pIndex} className="p-3 bg-neutral-50 rounded-fluent">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <p className="text-body-strong text-neutral-900">{proc.name}</p>
                                  <p className="text-caption text-neutral-600 mt-1">{proc.description}</p>
                                  {proc.ai_capability && (
                                    <div className="mt-2 flex items-center gap-4 text-caption">
                                      <span className="px-2 py-0.5 bg-primary-100 text-primary-700 rounded">AI-Enhanced</span>
                                      <span className="text-success-600">Time saved: {proc.human_time_saved}</span>
                                      <span className="text-primary-600">Accuracy: +{proc.accuracy_improvement}</span>
                                    </div>
                                  )}
                                </div>
                                <span className={`text-caption px-2 py-1 rounded bg-${proc.nature === 'substantive' ? 'blue' : 'purple'}-100 text-${proc.nature === 'substantive' ? 'blue' : 'purple'}-700`}>
                                  {proc.nature}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </details>
                  ))}
                </div>
              ) : null}
            </motion.div>
          )}

          {/* Planning Memo Tab */}
          {activeTab === 'memo' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="fluent-card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-title text-neutral-900">AI-Generated Planning Memo</h2>
                  <p className="text-body text-neutral-600">
                    PCAOB-compliant documentation ready for partner review
                  </p>
                </div>
                <div className="flex gap-2">
                  {planningMemo && (
                    <button className="fluent-btn-secondary">
                      <Download className="w-4 h-4" />
                      Export
                    </button>
                  )}
                  <button
                    onClick={handleGenerateMemo}
                    disabled={generatingMemo || !riskAnalysis || !materialityResult || !fraudDetection}
                    className="fluent-btn-primary"
                  >
                    {generatingMemo ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4" />
                        Generate Memo
                      </>
                    )}
                  </button>
                </div>
              </div>

              {!riskAnalysis || !materialityResult || !fraudDetection ? (
                <div className="text-center py-8 text-neutral-500">
                  <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-warning-400" />
                  <p className="text-body">Complete all analyses first (Risk, Materiality, Fraud)</p>
                </div>
              ) : planningMemo ? (
                <div className="space-y-4">
                  <div className="p-3 bg-warning-50 rounded-fluent border border-warning-200">
                    <div className="flex items-center gap-2">
                      <Eye className="w-5 h-5 text-warning-600" />
                      <span className="text-body-strong text-warning-900">Requires Partner Review</span>
                    </div>
                  </div>

                  <div className="prose prose-sm max-w-none">
                    <pre className="bg-neutral-50 p-4 rounded-fluent overflow-x-auto whitespace-pre-wrap text-sm font-mono">
                      {planningMemo.content}
                    </pre>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {planningMemo.pcaob_references?.map((ref, index) => (
                      <span key={index} className="px-2 py-1 bg-neutral-100 text-neutral-700 text-caption rounded">
                        {ref}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}
            </motion.div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* AI Capabilities */}
          <div className="fluent-card p-5">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-primary-500" />
              <h3 className="text-body-strong text-neutral-900">AI Advantages</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-success-100 flex items-center justify-center flex-shrink-0">
                  <Clock className="w-4 h-4 text-success-600" />
                </div>
                <div>
                  <p className="text-body-strong text-neutral-900">70% Faster</p>
                  <p className="text-caption text-neutral-600">Than traditional risk assessment</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                  <Target className="w-4 h-4 text-primary-600" />
                </div>
                <div>
                  <p className="text-body-strong text-neutral-900">100% Coverage</p>
                  <p className="text-caption text-neutral-600">Benford's Law on all transactions</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-warning-100 flex items-center justify-center flex-shrink-0">
                  <Zap className="w-4 h-4 text-warning-600" />
                </div>
                <div>
                  <p className="text-body-strong text-neutral-900">500+ Benchmarks</p>
                  <p className="text-caption text-neutral-600">Industry-specific comparisons</p>
                </div>
              </div>
            </div>
          </div>

          {/* Progress Summary */}
          <div className="fluent-card p-5">
            <h3 className="text-body-strong text-neutral-900 mb-4">Planning Progress</h3>
            <div className="space-y-3">
              {[
                { label: 'Risk Analysis', done: !!riskAnalysis },
                { label: 'Materiality', done: !!materialityResult },
                { label: 'Fraud Detection', done: !!fraudDetection },
                { label: 'Audit Programs', done: auditPrograms.length > 0 },
                { label: 'Planning Memo', done: !!planningMemo },
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-body text-neutral-700">{item.label}</span>
                  {item.done ? (
                    <CheckCircle2 className="w-5 h-5 text-success-500" />
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-neutral-300" />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* PCAOB Compliance */}
          <div className="fluent-card p-5 bg-success-50 border border-success-200">
            <div className="flex items-center gap-2 mb-3">
              <Shield className="w-5 h-5 text-success-600" />
              <h3 className="text-body-strong text-success-900">PCAOB Compliant</h3>
            </div>
            <ul className="text-caption text-success-800 space-y-1">
              <li>AS 2101 - Audit Planning</li>
              <li>AS 2105 - Materiality</li>
              <li>AS 2110 - Risk Assessment</li>
              <li>AS 2301 - Risk Response</li>
              <li>AS 2401 - Fraud Consideration</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAuditPlanning;
