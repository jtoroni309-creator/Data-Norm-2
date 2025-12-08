'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import Link from 'next/link'
import {
  LineChart,
  BarChart3,
  PieChart,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  CheckCircle2,
  FileText,
  Calculator,
  Target,
  AlertTriangle,
  Database,
  Brain,
  Zap,
  Shield,
  Eye,
  Layers,
  Activity,
  DollarSign,
  Percent,
  Scale,
  Clock,
  RefreshCw,
  Gauge,
  BarChart,
  ArrowUpRight,
  ArrowDownRight,
  Building2,
} from 'lucide-react'

export default function FinancialAnalysisPage() {
  const ratioCategories = [
    {
      category: 'Liquidity Ratios',
      ratios: ['Current Ratio', 'Quick Ratio', 'Cash Ratio', 'Working Capital'],
      icon: DollarSign,
      color: 'from-blue-500 to-cyan-500',
    },
    {
      category: 'Profitability Ratios',
      ratios: ['Gross Margin', 'Operating Margin', 'Net Margin', 'ROA', 'ROE', 'ROIC'],
      icon: TrendingUp,
      color: 'from-green-500 to-emerald-500',
    },
    {
      category: 'Efficiency Ratios',
      ratios: ['Asset Turnover', 'Inventory Turnover', 'AR Turnover', 'AP Turnover', 'Days Sales Outstanding'],
      icon: RefreshCw,
      color: 'from-purple-500 to-pink-500',
    },
    {
      category: 'Leverage Ratios',
      ratios: ['Debt to Equity', 'Debt Ratio', 'Interest Coverage', 'Equity Multiplier'],
      icon: Scale,
      color: 'from-orange-500 to-red-500',
    },
    {
      category: 'Valuation Ratios',
      ratios: ['P/E Ratio', 'EV/EBITDA', 'Price to Book', 'Price to Sales'],
      icon: Target,
      color: 'from-indigo-500 to-purple-500',
    },
    {
      category: 'Cash Flow Ratios',
      ratios: ['Operating Cash Flow Ratio', 'Free Cash Flow', 'Cash Flow Coverage', 'CAPEX Ratio'],
      icon: Activity,
      color: 'from-teal-500 to-cyan-500',
    },
  ]

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <Navigation />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 mesh-gradient" />
        <div className="absolute top-20 left-1/4 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-[120px]" />

        <div className="section-container relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 glassmorphism rounded-full mb-8">
              <LineChart className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-600">Financial Analysis Platform</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-display font-bold mb-8 leading-tight">
              <span className="text-slate-900">AI-Powered</span>
              <span className="block gradient-text">Financial Statement Analysis</span>
            </h1>

            <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              Transform raw financial data into actionable insights. Our AI analyzes statements, calculates
              50+ ratios, benchmarks against industry peers, and surfaces trends and anomalies—all in seconds.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link
                href="/#demo"
                className="group px-8 py-4 bg-gradient-to-r from-blue-600 via-blue-700 to-cyan-600 text-white font-semibold rounded-2xl hover:shadow-2xl hover:shadow-blue-500/50 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <span>Try Analysis Demo</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/case-studies"
                className="px-8 py-4 glassmorphism text-slate-900 font-semibold rounded-2xl hover:shadow-xl transition-all duration-300"
              >
                View Case Studies
              </Link>
            </div>

            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto">
              {[
                { value: '50+', label: 'Financial Ratios' },
                { value: '100+', label: 'Industry Benchmarks' },
                { value: '<30s', label: 'Full Analysis Time' },
              ].map((stat, i) => (
                <div key={i} className="text-center">
                  <div className="text-3xl md:text-4xl font-bold gradient-text-2 mb-1">{stat.value}</div>
                  <div className="text-sm text-slate-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="py-24 bg-white/50">
        <div className="section-container">
          <div className="glassmorphism rounded-3xl p-8 shadow-xl">
            <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl overflow-hidden">
              {/* Dashboard Header */}
              <div className="bg-slate-800/50 px-6 py-4 border-b border-slate-700/50 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full" />
                    <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                    <div className="w-3 h-3 bg-green-500 rounded-full" />
                  </div>
                  <span className="text-slate-400 text-sm">Aura Financial Analysis Dashboard</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded-full flex items-center">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
                    Live Analysis
                  </span>
                </div>
              </div>

              {/* Dashboard Content */}
              <div className="p-6 grid md:grid-cols-4 gap-6">
                {/* Key Metrics */}
                {[
                  { label: 'Current Ratio', value: '2.34', change: '+0.12', positive: true, icon: DollarSign },
                  { label: 'Gross Margin', value: '42.8%', change: '+3.2%', positive: true, icon: Percent },
                  { label: 'Debt to Equity', value: '0.67', change: '-0.08', positive: true, icon: Scale },
                  { label: 'ROE', value: '18.4%', change: '-1.2%', positive: false, icon: TrendingUp },
                ].map((metric, idx) => (
                  <div key={idx} className="glassmorphism-dark rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <metric.icon className="w-5 h-5 text-blue-400" />
                      <span className={`text-xs font-semibold flex items-center ${metric.positive ? 'text-green-400' : 'text-red-400'}`}>
                        {metric.positive ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                        {metric.change}
                      </span>
                    </div>
                    <div className="text-2xl font-bold text-white mb-1">{metric.value}</div>
                    <div className="text-xs text-slate-400">{metric.label}</div>
                  </div>
                ))}
              </div>

              {/* Trend Chart Placeholder */}
              <div className="px-6 pb-6">
                <div className="glassmorphism-dark rounded-xl p-4">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-white font-semibold">Revenue & Margin Trends</span>
                    <div className="flex space-x-2">
                      {['1Y', '3Y', '5Y'].map((period) => (
                        <button key={period} className="px-3 py-1 text-xs text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors">
                          {period}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="h-48 flex items-end justify-around space-x-2">
                    {[40, 45, 42, 55, 52, 60, 58, 65, 70, 68, 75, 80].map((height, idx) => (
                      <div key={idx} className="flex-1 flex flex-col items-center space-y-1">
                        <div
                          className="w-full bg-gradient-to-t from-blue-500 to-cyan-400 rounded-t-sm transition-all hover:from-blue-400 hover:to-cyan-300"
                          style={{ height: `${height}%` }}
                        />
                        <span className="text-xs text-slate-500">{['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'][idx]}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Ratio Categories */}
      <section className="py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Comprehensive
              <span className="block gradient-text">Ratio Analysis</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              50+ financial ratios calculated automatically, with industry benchmarking and trend analysis.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {ratioCategories.map((cat, index) => (
              <div key={index} className="glassmorphism rounded-3xl p-8 hover:shadow-xl transition-all">
                <div className={`w-14 h-14 bg-gradient-to-r ${cat.color} rounded-2xl flex items-center justify-center mb-6`}>
                  <cat.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-4">{cat.category}</h3>
                <div className="flex flex-wrap gap-2">
                  {cat.ratios.map((ratio, idx) => (
                    <span key={idx} className="px-3 py-1 bg-slate-100 text-slate-700 text-sm rounded-full">
                      {ratio}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Analysis Features */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
              Advanced Analysis
              <span className="block gradient-text">Capabilities</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Building2,
                title: 'Industry Benchmarking',
                description: 'Compare your client against 100+ industry benchmarks using NAICS codes and company size filters.',
                features: ['100+ industries', 'Size-adjusted benchmarks', 'Peer group analysis', 'Percentile rankings'],
              },
              {
                icon: TrendingUp,
                title: 'Trend Analysis',
                description: 'Visualize multi-year trends with AI-detected inflection points and projections.',
                features: ['Multi-period comparison', 'Trend detection', 'Seasonality analysis', 'Forecasting'],
              },
              {
                icon: AlertTriangle,
                title: 'Anomaly Detection',
                description: 'AI identifies unusual patterns, unexpected changes, and potential areas of concern.',
                features: ['Statistical outliers', 'Threshold alerts', 'Risk scoring', 'Drill-down capability'],
              },
              {
                icon: Gauge,
                title: 'Going Concern Assessment',
                description: 'Automated going concern analysis using Altman Z-score and other predictive models.',
                features: ['Z-score calculation', 'Bankruptcy prediction', 'Viability indicators', 'Risk factors'],
              },
              {
                icon: FileText,
                title: 'Automated Commentary',
                description: 'AI generates narrative analysis explaining key findings in plain language.',
                features: ['Plain English insights', 'Key takeaways', 'Management letter items', 'Board-ready summaries'],
              },
              {
                icon: Database,
                title: 'Data Integration',
                description: 'Connect to accounting systems or upload financials for instant analysis.',
                features: ['50+ integrations', 'Excel/CSV upload', 'Real-time sync', 'Historical data'],
              },
            ].map((feature, index) => (
              <div key={index} className="glassmorphism-dark rounded-2xl p-6 hover:bg-slate-800/50 transition-all">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                <p className="text-slate-400 mb-4 text-sm">{feature.description}</p>
                <div className="flex flex-wrap gap-2">
                  {feature.features.map((item, idx) => (
                    <span key={idx} className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Powerful
              <span className="block gradient-text">Use Cases</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {[
              {
                title: 'Audit Planning & Risk Assessment',
                description: 'Use financial analysis to identify high-risk areas, set materiality thresholds, and plan audit procedures based on quantitative risk indicators.',
                benefits: ['Data-driven risk assessment', 'Materiality calculations', 'Focus on high-risk areas'],
              },
              {
                title: 'Management Advisory Services',
                description: 'Provide clients with actionable insights on financial performance, benchmarking against industry peers, and recommendations for improvement.',
                benefits: ['Client advisory deliverables', 'Performance improvement', 'Strategic recommendations'],
              },
              {
                title: 'Due Diligence & M&A',
                description: 'Rapid financial health assessment for acquisitions, investments, or lending decisions with comprehensive ratio and trend analysis.',
                benefits: ['Quick financial assessment', 'Risk identification', 'Valuation support'],
              },
              {
                title: 'Continuous Monitoring',
                description: 'Set up automated monitoring of key financial metrics with alerts when thresholds are breached or unusual patterns emerge.',
                benefits: ['Real-time monitoring', 'Proactive alerts', 'Trend tracking'],
              },
            ].map((useCase, index) => (
              <div key={index} className="glassmorphism rounded-3xl p-8 hover:shadow-xl transition-all">
                <h3 className="text-2xl font-bold text-slate-900 mb-4">{useCase.title}</h3>
                <p className="text-slate-600 mb-6">{useCase.description}</p>
                <div className="space-y-2">
                  {useCase.benefits.map((benefit, idx) => (
                    <div key={idx} className="flex items-center text-sm text-slate-700">
                      <CheckCircle2 className="w-5 h-5 text-green-600 mr-3" />
                      {benefit}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-blue-600 via-cyan-600 to-teal-600 text-white">
        <div className="section-container text-center">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
            Ready to Transform Your Financial Analysis?
          </h2>
          <p className="text-xl text-white/90 mb-12 max-w-2xl mx-auto">
            See how AI-powered financial analysis can enhance your client services and audit quality.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/#demo"
              className="px-8 py-4 bg-white text-slate-900 font-semibold rounded-2xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center space-x-2"
            >
              <span>Request Demo</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/contact"
              className="px-8 py-4 border-2 border-white text-white font-semibold rounded-2xl hover:bg-white/10 transition-all duration-300"
            >
              Contact Sales
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
