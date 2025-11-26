/**
 * Analytical Procedures
 * AI-powered financial analysis, ratio analysis, trend analysis, and benchmarking
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Brain,
  Download,
  Upload,
  Zap,
  Target,
  DollarSign,
  Percent,
  Calendar,
  ChevronRight,
  Info,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface FinancialRatio {
  name: string;
  value: number;
  priorYear: number;
  industry: number;
  category: string;
  description: string;
  variance: number;
  status: 'normal' | 'warning' | 'alert';
}

interface TrendData {
  period: string;
  revenue: number;
  expenses: number;
  netIncome: number;
  grossMargin: number;
}

const AnalyticalProcedures: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'ratios' | 'trends' | 'variance' | 'benchmarks'>('ratios');
  const [showAIInsights, setShowAIInsights] = useState(true);

  // Mock financial ratios
  const financialRatios: FinancialRatio[] = [
    {
      name: 'Current Ratio',
      value: 2.3,
      priorYear: 2.5,
      industry: 2.1,
      category: 'Liquidity',
      description: 'Ability to pay short-term obligations',
      variance: -8.0,
      status: 'normal',
    },
    {
      name: 'Quick Ratio',
      value: 1.5,
      priorYear: 1.8,
      industry: 1.4,
      category: 'Liquidity',
      description: 'Ability to meet short-term obligations with liquid assets',
      variance: -16.7,
      status: 'warning',
    },
    {
      name: 'Gross Margin %',
      value: 42.5,
      priorYear: 45.2,
      industry: 44.0,
      category: 'Profitability',
      description: 'Percentage of revenue retained after COGS',
      variance: -6.0,
      status: 'warning',
    },
    {
      name: 'Net Profit Margin %',
      value: 8.2,
      priorYear: 10.5,
      industry: 9.8,
      category: 'Profitability',
      description: 'Net income as percentage of revenue',
      variance: -21.9,
      status: 'alert',
    },
    {
      name: 'Return on Assets',
      value: 7.5,
      priorYear: 8.1,
      industry: 8.0,
      category: 'Profitability',
      description: 'Efficiency in using assets to generate profit',
      variance: -7.4,
      status: 'normal',
    },
    {
      name: 'Debt to Equity',
      value: 0.65,
      priorYear: 0.58,
      industry: 0.70,
      category: 'Leverage',
      description: 'Financial leverage and capital structure',
      variance: 12.1,
      status: 'normal',
    },
    {
      name: 'Interest Coverage',
      value: 4.2,
      priorYear: 5.8,
      industry: 5.0,
      category: 'Leverage',
      description: 'Ability to meet interest payments',
      variance: -27.6,
      status: 'warning',
    },
    {
      name: 'Inventory Turnover',
      value: 6.8,
      priorYear: 7.2,
      industry: 7.5,
      category: 'Efficiency',
      description: 'How quickly inventory is sold',
      variance: -5.6,
      status: 'normal',
    },
    {
      name: 'Days Sales Outstanding',
      value: 52,
      priorYear: 48,
      industry: 45,
      category: 'Efficiency',
      description: 'Average collection period for receivables',
      variance: 8.3,
      status: 'warning',
    },
    {
      name: 'Asset Turnover',
      value: 1.45,
      priorYear: 1.52,
      industry: 1.50,
      category: 'Efficiency',
      description: 'Efficiency in using assets to generate revenue',
      variance: -4.6,
      status: 'normal',
    },
  ];

  // Mock trend data
  const trendData: TrendData[] = [
    { period: 'Q1 2023', revenue: 2500000, expenses: 2100000, netIncome: 400000, grossMargin: 44.0 },
    { period: 'Q2 2023', revenue: 2650000, expenses: 2200000, netIncome: 450000, grossMargin: 45.5 },
    { period: 'Q3 2023', revenue: 2800000, expenses: 2350000, netIncome: 450000, grossMargin: 46.2 },
    { period: 'Q4 2023', revenue: 3200000, expenses: 2750000, netIncome: 450000, grossMargin: 45.8 },
    { period: 'Q1 2024', revenue: 2450000, expenses: 2050000, netIncome: 400000, grossMargin: 43.5 },
    { period: 'Q2 2024', revenue: 2600000, expenses: 2180000, netIncome: 420000, grossMargin: 42.8 },
    { period: 'Q3 2024', revenue: 2750000, expenses: 2300000, netIncome: 450000, grossMargin: 42.2 },
    { period: 'Q4 2024', revenue: 2900000, expenses: 2480000, netIncome: 420000, grossMargin: 41.5 },
  ];

  const aiInsights = [
    {
      type: 'critical',
      title: 'Significant Margin Compression',
      description: 'Gross margin has declined from 45.2% to 42.5% year-over-year. Net profit margin down 21.9%. Investigate: 1) Pricing pressure, 2) COGS increases, 3) Product mix changes.',
      recommendations: [
        'Perform detailed variance analysis on COGS by product line',
        'Review pricing strategy and competitive positioning',
        'Analyze product mix shift impact on margins',
      ],
      impact: 'high',
    },
    {
      type: 'warning',
      title: 'Declining Interest Coverage',
      description: 'Interest coverage ratio decreased 27.6% to 4.2x. While still adequate, this trend warrants attention given increasing debt levels.',
      recommendations: [
        'Review debt covenant compliance',
        'Assess refinancing opportunities',
        'Evaluate debt repayment schedule',
      ],
      impact: 'medium',
    },
    {
      type: 'info',
      title: 'Working Capital Management',
      description: 'Days Sales Outstanding increased from 48 to 52 days. Collection efficiency has declined slightly but remains close to industry average.',
      recommendations: [
        'Review aging of receivables',
        'Assess credit policies',
        'Identify slow-paying customers',
      ],
      impact: 'medium',
    },
    {
      type: 'positive',
      title: 'Strong Liquidity Position',
      description: 'Current ratio of 2.3x exceeds industry average of 2.1x. Quick ratio of 1.5x also above industry norm, indicating solid short-term liquidity.',
      recommendations: [
        'Continue monitoring working capital',
        'Evaluate optimal cash levels',
      ],
      impact: 'low',
    },
  ];

  const categories = ['All', 'Liquidity', 'Profitability', 'Leverage', 'Efficiency'];
  const [selectedCategory, setSelectedCategory] = useState('All');

  const filteredRatios =
    selectedCategory === 'All'
      ? financialRatios
      : financialRatios.filter((r) => r.category === selectedCategory);

  const getStatusColor = (status: string) => {
    const colors = {
      normal: 'success',
      warning: 'warning',
      alert: 'error',
    };
    return colors[status as keyof typeof colors] || 'neutral';
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number, decimals: number = 1) => {
    return `${value.toFixed(decimals)}%`;
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
          <h1 className="text-display text-neutral-900 mb-1">Analytical Procedures</h1>
          <p className="text-body text-neutral-600">
            AI-powered financial analysis and benchmarking
          </p>
        </div>
        <div className="flex gap-3">
          <button className="fluent-btn-secondary">
            <Upload className="w-4 h-4" />
            Import Financials
          </button>
          <button className="fluent-btn-primary">
            <Download className="w-4 h-4" />
            Export Analysis
          </button>
        </div>
      </motion.div>

      {/* AI Insights Banner */}
      <AnimatePresence>
        {showAIInsights && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fluent-card bg-gradient-to-r from-primary-50 to-purple-50 p-5 border-l-4 border-primary-500"
          >
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-fluent bg-primary-500 flex items-center justify-center flex-shrink-0">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="text-body-strong text-neutral-900 mb-1">
                  AI Analysis Complete - 4 Insights Generated
                </h3>
                <p className="text-caption text-neutral-700">
                  Our AI has analyzed financial data and identified key trends, anomalies, and areas requiring attention.
                </p>
              </div>
              <button
                onClick={() => setShowAIInsights(false)}
                className="p-1 hover:bg-primary-100 rounded-fluent-sm"
              >
                <Zap className="w-5 h-5 text-primary-600" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tabs */}
      <div className="fluent-card p-1">
        <div className="flex gap-1">
          {[
            { id: 'ratios', label: 'Financial Ratios', icon: Percent },
            { id: 'trends', label: 'Trend Analysis', icon: TrendingUp },
            { id: 'variance', label: 'Variance Analysis', icon: Activity },
            { id: 'benchmarks', label: 'Industry Benchmarks', icon: Target },
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

      {/* Financial Ratios Tab */}
      {activeTab === 'ratios' && (
        <div className="space-y-6">
          {/* Category Filter */}
          <div className="flex gap-2">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-fluent transition-all ${
                  selectedCategory === category
                    ? 'bg-primary-500 text-white'
                    : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>

          {/* Ratios Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredRatios.map((ratio, index) => {
              const statusColor = getStatusColor(ratio.status);
              const isIncrease = ratio.variance > 0;

              return (
                <motion.div
                  key={ratio.name}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  className="fluent-card p-5"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="text-body-strong text-neutral-900 mb-1">{ratio.name}</h4>
                      <p className="text-caption text-neutral-600">{ratio.description}</p>
                    </div>
                    <div
                      className={`w-8 h-8 rounded-fluent bg-${statusColor}-100 flex items-center justify-center flex-shrink-0 ml-2`}
                    >
                      {ratio.status === 'normal' ? (
                        <CheckCircle2 className={`w-4 h-4 text-${statusColor}-600`} />
                      ) : (
                        <AlertTriangle className={`w-4 h-4 text-${statusColor}-600`} />
                      )}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <div className="flex items-baseline gap-2 mb-1">
                        <span className="text-title-large text-neutral-900 font-semibold">
                          {ratio.value.toFixed(ratio.name.includes('%') ? 1 : 2)}
                          {ratio.name.includes('%') && '%'}
                        </span>
                        <div className={`flex items-center gap-1 text-${isIncrease ? 'success' : 'error'}-600`}>
                          {isIncrease ? (
                            <TrendingUp className="w-4 h-4" />
                          ) : (
                            <TrendingDown className="w-4 h-4" />
                          )}
                          <span className="text-caption font-medium">
                            {Math.abs(ratio.variance).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      <p className="text-caption text-neutral-600">Current Year</p>
                    </div>

                    <div className="grid grid-cols-2 gap-3 pt-3 border-t border-neutral-200">
                      <div>
                        <p className="text-caption text-neutral-600 mb-1">Prior Year</p>
                        <p className="text-body-strong text-neutral-900">
                          {ratio.priorYear.toFixed(ratio.name.includes('%') ? 1 : 2)}
                          {ratio.name.includes('%') && '%'}
                        </p>
                      </div>
                      <div>
                        <p className="text-caption text-neutral-600 mb-1">Industry Avg</p>
                        <p className="text-body-strong text-neutral-900">
                          {ratio.industry.toFixed(ratio.name.includes('%') ? 1 : 2)}
                          {ratio.name.includes('%') && '%'}
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* Trend Analysis Tab */}
      {activeTab === 'trends' && (
        <div className="space-y-6">
          <div className="fluent-card p-6">
            <h3 className="text-title text-neutral-900 mb-6">Quarterly Performance Trends</h3>

            {/* Revenue Trend */}
            <div className="mb-8">
              <h4 className="text-body-strong text-neutral-900 mb-4">Revenue Trend</h4>
              <div className="space-y-2">
                {trendData.map((data, index) => {
                  const maxRevenue = Math.max(...trendData.map((d) => d.revenue));
                  const percentage = (data.revenue / maxRevenue) * 100;
                  const priorRevenue = index > 0 ? trendData[index - 1].revenue : data.revenue;
                  const growth = ((data.revenue - priorRevenue) / priorRevenue) * 100;

                  return (
                    <div key={data.period}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-caption text-neutral-700">{data.period}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-body-strong text-neutral-900">
                            {formatCurrency(data.revenue)}
                          </span>
                          {index > 0 && (
                            <span
                              className={`text-caption font-medium ${
                                growth >= 0 ? 'text-success-600' : 'text-error-600'
                              }`}
                            >
                              {growth >= 0 ? '+' : ''}
                              {growth.toFixed(1)}%
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="h-8 bg-neutral-100 rounded-fluent overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary-500 to-primary-600 flex items-center justify-end px-3"
                          style={{ width: `${percentage}%` }}
                        >
                          {percentage > 30 && (
                            <span className="text-caption text-white font-medium">
                              {formatCurrency(data.revenue)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Gross Margin Trend */}
            <div>
              <h4 className="text-body-strong text-neutral-900 mb-4">Gross Margin Trend</h4>
              <div className="space-y-2">
                {trendData.map((data, index) => {
                  const priorMargin = index > 0 ? trendData[index - 1].grossMargin : data.grossMargin;
                  const change = data.grossMargin - priorMargin;

                  return (
                    <div key={data.period}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-caption text-neutral-700">{data.period}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-body-strong text-neutral-900">
                            {formatPercent(data.grossMargin)}
                          </span>
                          {index > 0 && (
                            <span
                              className={`text-caption font-medium ${
                                change >= 0 ? 'text-success-600' : 'text-error-600'
                              }`}
                            >
                              {change >= 0 ? '+' : ''}
                              {change.toFixed(1)}pp
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            data.grossMargin >= 44 ? 'bg-success-500' : 'bg-warning-500'
                          }`}
                          style={{ width: `${(data.grossMargin / 50) * 100}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Insights Section */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-primary-600" />
          <h2 className="text-title text-neutral-900">AI-Powered Insights</h2>
        </div>

        {aiInsights.map((insight, index) => {
          const typeConfig = {
            critical: { color: 'error', icon: AlertTriangle, bg: 'error' },
            warning: { color: 'warning', icon: AlertTriangle, bg: 'warning' },
            info: { color: 'primary', icon: Info, bg: 'primary' },
            positive: { color: 'success', icon: CheckCircle2, bg: 'success' },
          };
          const config = typeConfig[insight.type as keyof typeof typeConfig];
          const Icon = config.icon;

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`fluent-card p-5 border-l-4 border-${config.color}-500`}
            >
              <div className="flex items-start gap-4">
                <div
                  className={`w-10 h-10 rounded-fluent bg-${config.bg}-100 flex items-center justify-center flex-shrink-0`}
                >
                  <Icon className={`w-5 h-5 text-${config.color}-600`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-body-strong text-neutral-900">{insight.title}</h4>
                    <span
                      className={`px-2 py-0.5 rounded-fluent-sm text-caption font-medium bg-${config.bg}-100 text-${config.color}-700`}
                    >
                      {insight.impact.toUpperCase()} IMPACT
                    </span>
                  </div>
                  <p className="text-body text-neutral-700 mb-4">{insight.description}</p>
                  <div>
                    <p className="text-caption font-semibold text-neutral-900 mb-2">
                      Recommended Actions:
                    </p>
                    <ul className="space-y-1">
                      {insight.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-caption text-neutral-700">
                          <ChevronRight className="w-3.5 h-3.5 text-primary-500 flex-shrink-0 mt-0.5" />
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default AnalyticalProcedures;
