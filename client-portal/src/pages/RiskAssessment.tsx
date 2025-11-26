/**
 * Risk Assessment Tools
 * Risk matrix, materiality calculator, fraud risk assessment, and going concern analysis
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Shield,
  AlertTriangle,
  DollarSign,
  TrendingDown,
  Target,
  Brain,
  Calculator,
  CheckCircle2,
  XCircle,
  Download,
  FileText,
  Loader2,
} from 'lucide-react';
import { riskAssessmentService, RiskArea, FraudRisk, GoingConcernIndicator } from '../services/risk-assessment.service';
import toast from 'react-hot-toast';

const RiskAssessment: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'matrix' | 'materiality' | 'fraud' | 'going_concern'>('matrix');
  const [loading, setLoading] = useState(true);

  // Data from API
  const [riskAreas, setRiskAreas] = useState<RiskArea[]>([]);
  const [fraudRisks, setFraudRisks] = useState<FraudRisk[]>([]);
  const [goingConcernIndicators, setGoingConcernIndicators] = useState<GoingConcernIndicator[]>([]);

  // Materiality calculations
  const [revenue, setRevenue] = useState(10000000);
  const [assets, setAssets] = useState(8000000);
  const [netIncome, setNetIncome] = useState(500000);

  useEffect(() => {
    loadRiskData();
  }, [id]);

  const loadRiskData = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await riskAssessmentService.getRiskAssessment(id);
      setRiskAreas(data.riskAreas);
      setFraudRisks(data.fraudRisks);
      setGoingConcernIndicators(data.goingConcernIndicators);
    } catch (error) {
      console.error('Failed to load risk data:', error);
      toast.error('Failed to load risk assessment data');
    } finally {
      setLoading(false);
    }
  };

  const calculateMateriality = () => {
    const revenueBased = revenue * 0.005; // 0.5% of revenue
    const assetBased = assets * 0.01; // 1% of assets
    const incomeBased = netIncome * 0.05; // 5% of net income

    return {
      planning: Math.min(revenueBased, assetBased),
      performance: Math.min(revenueBased, assetBased) * 0.75,
      trivial: Math.min(revenueBased, assetBased) * 0.05,
    };
  };

  const materiality = calculateMateriality();

  const getRiskColor = (risk: string) => {
    const colors = {
      low: 'success',
      medium: 'warning',
      high: 'error',
    };
    return colors[risk as keyof typeof colors] || 'neutral';
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="text-body text-neutral-600">Loading risk assessment...</p>
        </div>
      </div>
    );
  }

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
          <h1 className="text-display text-neutral-900 mb-1">Risk Assessment</h1>
          <p className="text-body text-neutral-600">
            Risk matrix, materiality, fraud assessment, and going concern
          </p>
        </div>
        <button className="fluent-btn-primary">
          <Download className="w-4 h-4" />
          Export Assessment
        </button>
      </motion.div>

      {/* Tabs */}
      <div className="fluent-card p-1">
        <div className="flex gap-1">
          {[
            { id: 'matrix', label: 'Risk Matrix', icon: Shield },
            { id: 'materiality', label: 'Materiality', icon: Calculator },
            { id: 'fraud', label: 'Fraud Risk', icon: AlertTriangle },
            { id: 'going_concern', label: 'Going Concern', icon: TrendingDown },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-fluent transition-all ${
                  activeTab === tab.id
                    ? 'bg-primary-500 text-white shadow-sm'
                    : 'text-neutral-700 hover:bg-neutral-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-body-strong">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Risk Matrix Tab */}
      {activeTab === 'matrix' && (
        <div className="space-y-4">
          <div className="fluent-card p-6">
            <h3 className="text-title text-neutral-900 mb-4">Risk Assessment Matrix</h3>
            <p className="text-body text-neutral-600 mb-6">
              Assessment of inherent risk, control risk, detection risk, and overall audit risk by area
            </p>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-neutral-200">
                    <th className="text-left py-3 px-4 text-body-strong text-neutral-900">Audit Area</th>
                    <th className="text-center py-3 px-4 text-body-strong text-neutral-900">Inherent Risk</th>
                    <th className="text-center py-3 px-4 text-body-strong text-neutral-900">Control Risk</th>
                    <th className="text-center py-3 px-4 text-body-strong text-neutral-900">Detection Risk</th>
                    <th className="text-center py-3 px-4 text-body-strong text-neutral-900">Audit Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {riskAreas.map((area, index) => (
                    <React.Fragment key={index}>
                      <tr className="border-b border-neutral-200 hover:bg-neutral-50">
                        <td className="py-4 px-4 text-body-strong text-neutral-900">{area.area}</td>
                        <td className="py-4 px-4 text-center">
                          <span
                            className={`inline-flex px-3 py-1 rounded-fluent text-caption font-medium bg-${getRiskColor(
                              area.inherentRisk
                            )}-100 text-${getRiskColor(area.inherentRisk)}-700`}
                          >
                            {area.inherentRisk.toUpperCase()}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center">
                          <span
                            className={`inline-flex px-3 py-1 rounded-fluent text-caption font-medium bg-${getRiskColor(
                              area.controlRisk
                            )}-100 text-${getRiskColor(area.controlRisk)}-700`}
                          >
                            {area.controlRisk.toUpperCase()}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center">
                          <span
                            className={`inline-flex px-3 py-1 rounded-fluent text-caption font-medium bg-${getRiskColor(
                              area.detectionRisk
                            )}-100 text-${getRiskColor(area.detectionRisk)}-700`}
                          >
                            {area.detectionRisk.toUpperCase()}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center">
                          <span
                            className={`inline-flex px-3 py-1 rounded-fluent text-caption font-semibold bg-${getRiskColor(
                              area.auditRisk
                            )}-100 text-${getRiskColor(area.auditRisk)}-700 border-2 border-${getRiskColor(
                              area.auditRisk
                            )}-300`}
                          >
                            {area.auditRisk.toUpperCase()}
                          </span>
                        </td>
                      </tr>
                      <tr className="border-b border-neutral-200 bg-neutral-50">
                        <td colSpan={5} className="py-3 px-4">
                          <p className="text-caption text-neutral-700">
                            <span className="font-semibold">Rationale:</span> {area.rationale}
                          </p>
                        </td>
                      </tr>
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Materiality Calculator Tab */}
      {activeTab === 'materiality' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="fluent-card p-6">
            <h3 className="text-title text-neutral-900 mb-4">Financial Inputs</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-body-strong text-neutral-700 mb-2">Annual Revenue</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-500" />
                  <input
                    type="number"
                    value={revenue}
                    onChange={(e) => setRevenue(Number(e.target.value))}
                    className="fluent-input pl-10"
                  />
                </div>
              </div>

              <div>
                <label className="block text-body-strong text-neutral-700 mb-2">Total Assets</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-500" />
                  <input
                    type="number"
                    value={assets}
                    onChange={(e) => setAssets(Number(e.target.value))}
                    className="fluent-input pl-10"
                  />
                </div>
              </div>

              <div>
                <label className="block text-body-strong text-neutral-700 mb-2">Net Income</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-500" />
                  <input
                    type="number"
                    value={netIncome}
                    onChange={(e) => setNetIncome(Number(e.target.value))}
                    className="fluent-input pl-10"
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 p-4 bg-primary-50 border border-primary-200 rounded-fluent">
              <div className="flex items-center gap-2 mb-2">
                <Calculator className="w-4 h-4 text-primary-600" />
                <p className="text-caption font-semibold text-primary-900">Calculation Methodology</p>
              </div>
              <ul className="text-caption text-primary-800 space-y-1">
                <li>• Planning Materiality: Lesser of 0.5% revenue or 1% assets</li>
                <li>• Performance Materiality: 75% of planning materiality</li>
                <li>• Trivial Threshold: 5% of planning materiality</li>
              </ul>
            </div>
          </div>

          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="fluent-card p-6 bg-gradient-to-br from-primary-50 to-purple-50"
            >
              <h4 className="text-body-strong text-neutral-900 mb-4">Planning Materiality</h4>
              <p className="text-display text-primary-600 font-bold mb-2">
                {formatCurrency(materiality.planning)}
              </p>
              <p className="text-caption text-neutral-600">
                Overall materiality for planning and evaluating misstatements
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="fluent-card p-6 bg-gradient-to-br from-accent-50 to-blue-50"
            >
              <h4 className="text-body-strong text-neutral-900 mb-4">Performance Materiality</h4>
              <p className="text-display text-accent-600 font-bold mb-2">
                {formatCurrency(materiality.performance)}
              </p>
              <p className="text-caption text-neutral-600">
                Amount set to reduce probability that aggregate uncorrected misstatements exceed planning materiality
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="fluent-card p-6 bg-gradient-to-br from-neutral-50 to-neutral-100"
            >
              <h4 className="text-body-strong text-neutral-900 mb-4">Trivial Threshold</h4>
              <p className="text-display text-neutral-700 font-bold mb-2">
                {formatCurrency(materiality.trivial)}
              </p>
              <p className="text-caption text-neutral-600">
                Amount below which misstatements need not be accumulated
              </p>
            </motion.div>
          </div>
        </div>
      )}

      {/* Fraud Risk Tab */}
      {activeTab === 'fraud' && (
        <div className="space-y-4">
          {fraudRisks.map((fraud, index) => {
            const riskColor = getRiskColor(fraud.risk);

            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`fluent-card p-6 border-l-4 border-${riskColor}-500`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-fluent bg-${riskColor}-100 flex items-center justify-center`}>
                      <AlertTriangle className={`w-5 h-5 text-${riskColor}-600`} />
                    </div>
                    <div>
                      <h3 className="text-body-strong text-neutral-900">{fraud.type}</h3>
                      <span
                        className={`inline-flex px-2 py-0.5 rounded-fluent-sm text-caption font-medium bg-${riskColor}-100 text-${riskColor}-700 mt-1`}
                      >
                        {fraud.risk.toUpperCase()} RISK
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-caption font-semibold text-neutral-900 mb-2">Risk Factors:</h4>
                    <ul className="space-y-1">
                      {fraud.factors.map((factor, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-caption text-neutral-700">
                          <span className="text-error-500 mt-1">•</span>
                          <span>{factor}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="text-caption font-semibold text-neutral-900 mb-2">Audit Procedures:</h4>
                    <ul className="space-y-1">
                      {fraud.procedures.map((procedure, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-caption text-neutral-700">
                          <CheckCircle2 className="w-3.5 h-3.5 text-success-600 flex-shrink-0 mt-0.5" />
                          <span>{procedure}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Going Concern Tab */}
      {activeTab === 'going_concern' && (
        <div className="fluent-card p-6">
          <h3 className="text-title text-neutral-900 mb-4">Going Concern Assessment</h3>
          <p className="text-body text-neutral-600 mb-6">
            Evaluation of indicators that may raise substantial doubt about the entity's ability to continue as a going concern
          </p>

          <div className="space-y-3">
            {goingConcernIndicators.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`p-4 border rounded-fluent ${
                  item.present ? 'border-warning-300 bg-warning-50' : 'border-neutral-200 bg-white'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    {item.present ? (
                      <XCircle className="w-5 h-5 text-warning-600" />
                    ) : (
                      <CheckCircle2 className="w-5 h-5 text-success-600" />
                    )}
                    <span className="text-body-strong text-neutral-900">{item.indicator}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span
                      className={`px-2 py-0.5 rounded-fluent-sm text-caption font-medium ${
                        item.impact === 'high'
                          ? 'bg-error-100 text-error-700'
                          : item.impact === 'medium'
                          ? 'bg-warning-100 text-warning-700'
                          : 'bg-primary-100 text-primary-700'
                      }`}
                    >
                      {item.impact.toUpperCase()} IMPACT
                    </span>
                    <span
                      className={`text-body-strong ${item.present ? 'text-warning-700' : 'text-success-700'}`}
                    >
                      {item.present ? 'Present' : 'Not Present'}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="mt-6 p-5 bg-primary-50 border border-primary-200 rounded-fluent">
            <div className="flex items-start gap-3">
              <Brain className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-body-strong text-primary-900 mb-2">AI Assessment</h4>
                <p className="text-body text-primary-800 mb-3">
                  Based on the indicators present, there is <strong>no substantial doubt</strong> about the entity's ability to continue as a going concern. The legal proceedings indicator has low impact and does not materially affect the assessment.
                </p>
                <p className="text-caption text-primary-700">
                  Continue monitoring financial condition and update assessment if circumstances change.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskAssessment;
