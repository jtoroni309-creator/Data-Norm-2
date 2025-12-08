'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import Link from 'next/link'
import {
  Brain,
  Shield,
  TrendingUp,
  FileCheck,
  Clock,
  Target,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Database,
  Lock,
  BarChart3,
  FileText,
  Search,
  AlertTriangle,
  Eye,
  Layers,
  Cpu,
  Zap,
  RefreshCw,
  Settings,
  LineChart,
  PieChart,
  Activity,
  GitBranch,
  Workflow,
} from 'lucide-react'

export default function AIAuditPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <Navigation />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 mesh-gradient" />
        <div className="absolute top-20 left-1/4 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-purple-500/10 rounded-full blur-[120px]" />

        <div className="section-container relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 glassmorphism rounded-full mb-8">
              <Brain className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-600">AI-Powered Audit Platform</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-display font-bold mb-8 leading-tight">
              <span className="text-slate-900">AI-Assisted</span>
              <span className="block gradient-text">Compliance & Audits</span>
            </h1>

            <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              Transform your audit practice with intelligent automation that analyzes millions of transactions,
              detects anomalies in real-time, and generates PCAOB-compliant documentation—all while you focus
              on high-value advisory work.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/#demo"
                className="group px-8 py-4 bg-gradient-to-r from-blue-600 via-blue-700 to-purple-600 text-white font-semibold rounded-2xl hover:shadow-2xl hover:shadow-blue-500/50 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <span>Schedule Demo</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/case-studies"
                className="px-8 py-4 glassmorphism text-slate-900 font-semibold rounded-2xl hover:shadow-xl transition-all duration-300"
              >
                View Case Studies
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Key Stats */}
      <section className="py-16 bg-white/50 backdrop-blur-sm border-y border-slate-200">
        <div className="section-container">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: '30-50%', label: 'Faster Audit Completion', icon: Clock },
              { value: '100K+', label: 'Transactions/Hour', icon: Zap },
              { value: '99.9%', label: 'Detection Accuracy', icon: Target },
              { value: '85%', label: 'Less Manual Work', icon: RefreshCw },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <stat.icon className="w-8 h-8 text-blue-600 mx-auto mb-3" />
                <div className="text-3xl md:text-4xl font-bold gradient-text-2 mb-1">{stat.value}</div>
                <div className="text-sm text-slate-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Core Capabilities */}
      <section className="py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Comprehensive Audit
              <span className="block gradient-text">Intelligence Platform</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Every feature designed by CPAs, for CPAs—combining deep accounting expertise with
              cutting-edge artificial intelligence.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Database,
                title: 'Intelligent Data Ingestion',
                description: 'Connect to 50+ accounting systems including QuickBooks, Xero, NetSuite, SAP, and Oracle. Our ML engine automatically maps chart of accounts, identifies entities, and normalizes data from any format—CSV, Excel, API, or direct database connection.',
                features: ['Auto-mapping with 99% accuracy', 'Multi-entity consolidation', 'Historical data import', 'Real-time sync capabilities'],
                gradient: 'from-blue-500 to-cyan-500',
              },
              {
                icon: Brain,
                title: 'AI Transaction Analysis',
                description: 'Process over 100,000 transactions per hour with deep learning models trained on millions of audit engagements. Identify patterns, flag anomalies, and surface material findings that human review might miss.',
                features: ['Pattern recognition AI', 'Benford\'s Law analysis', 'Journal entry testing', 'Cutoff testing automation'],
                gradient: 'from-purple-500 to-pink-500',
              },
              {
                icon: AlertTriangle,
                title: 'Advanced Fraud Detection',
                description: 'Multi-layered fraud detection using ensemble machine learning models. Detect sophisticated schemes including round-tripping, channel stuffing, fictitious vendors, and ghost employees with confidence scoring.',
                features: ['Behavioral anomaly detection', 'Network analysis', 'Temporal pattern analysis', 'Risk-based sampling'],
                gradient: 'from-red-500 to-orange-500',
              },
              {
                icon: FileText,
                title: 'Smart Disclosure Drafting',
                description: 'Auto-generate GAAP-compliant disclosures for 30+ ASC topics with proper citations. Our AI understands context, materiality thresholds, and regulatory requirements to produce audit-ready documentation.',
                features: ['ASC topic coverage', 'Citation auto-linking', 'Materiality-aware drafting', 'Regulatory updates'],
                gradient: 'from-green-500 to-emerald-500',
              },
              {
                icon: BarChart3,
                title: 'Real-Time Analytics Dashboard',
                description: 'Monitor engagement progress with 30+ financial ratios, industry benchmarking, going concern indicators, and trend analysis. Drill down from summary to transaction level instantly.',
                features: ['Industry benchmarking', 'Going concern assessment', 'Trend analysis', 'Custom KPI tracking'],
                gradient: 'from-indigo-500 to-purple-500',
              },
              {
                icon: Shield,
                title: 'PCAOB Compliance Engine',
                description: 'Built-in compliance framework ensures every engagement meets PCAOB, AICPA, and ISA standards. Immutable audit trail, 7-year retention, complete data lineage, and automated workpaper generation.',
                features: ['Immutable audit trail', 'Automated workpapers', 'Electronic sign-off', 'Archive management'],
                gradient: 'from-slate-600 to-slate-800',
              },
            ].map((feature, index) => (
              <div key={index} className="group glassmorphism rounded-3xl p-8 hover:shadow-2xl transition-all duration-500">
                <div className={`w-14 h-14 bg-gradient-to-r ${feature.gradient} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-600 mb-6 leading-relaxed">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.features.map((item, idx) => (
                    <li key={idx} className="flex items-center text-sm text-slate-700">
                      <CheckCircle2 className="w-4 h-4 text-green-600 mr-2 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works - Detailed */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
              The AI Audit
              <span className="block gradient-text">Workflow</span>
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              From data ingestion to final sign-off, see how AI transforms every step of your audit process.
            </p>
          </div>

          <div className="max-w-5xl mx-auto">
            {[
              {
                step: '01',
                title: 'Data Collection & Normalization',
                description: 'Connect your client\'s accounting system or upload trial balances, general ledgers, and supporting documents. Our AI automatically:',
                details: [
                  'Maps accounts to standardized chart of accounts using ML classification',
                  'Identifies and consolidates related party transactions',
                  'Normalizes data formats from 50+ source systems',
                  'Validates data integrity and flags missing periods or gaps',
                  'Creates secure, encrypted data warehouse for the engagement',
                ],
                icon: Database,
              },
              {
                step: '02',
                title: 'Risk Assessment & Planning',
                description: 'AI analyzes historical data and industry patterns to identify high-risk areas and optimize your audit approach:',
                details: [
                  'Calculates preliminary materiality using AI-recommended thresholds',
                  'Identifies significant accounts and assertions automatically',
                  'Generates risk heat maps by account and transaction type',
                  'Recommends sample sizes based on statistical models',
                  'Creates audit programs tailored to identified risks',
                ],
                icon: Target,
              },
              {
                step: '03',
                title: 'Substantive Testing & Analysis',
                description: 'Execute comprehensive testing at scale with AI-powered procedures:',
                details: [
                  'Performs 100% population testing on all transactions',
                  'Executes 30+ analytical procedures automatically',
                  'Identifies anomalies using Benford\'s Law and statistical models',
                  'Tests cutoff, completeness, and existence assertions',
                  'Generates audit evidence with source document linking',
                ],
                icon: Search,
              },
              {
                step: '04',
                title: 'Findings & Documentation',
                description: 'AI synthesizes results into clear, actionable findings:',
                details: [
                  'Prioritizes findings by materiality and risk impact',
                  'Drafts management letter comments with recommendations',
                  'Generates GAAP-compliant disclosure language',
                  'Creates visual summaries for partner review',
                  'Maintains complete audit trail with timestamps',
                ],
                icon: FileCheck,
              },
              {
                step: '05',
                title: 'Review & Sign-off',
                description: 'Streamlined review process with intelligent quality control:',
                details: [
                  'Multi-level review workflow with role-based access',
                  'AI-suggested review points based on risk areas',
                  'Electronic sign-off with audit trail',
                  'Automatic archival meeting retention requirements',
                  'Client portal for secure document delivery',
                ],
                icon: Shield,
              },
            ].map((item, index) => (
              <div key={index} className="relative flex gap-8 mb-12 last:mb-0">
                <div className="flex-shrink-0 relative">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
                    <item.icon className="w-8 h-8 text-white" />
                  </div>
                  {index < 4 && (
                    <div className="absolute left-1/2 top-full w-0.5 h-12 bg-gradient-to-b from-purple-500 to-transparent -translate-x-1/2" />
                  )}
                </div>
                <div className="flex-1 pb-8">
                  <div className="text-sm font-bold text-purple-400 mb-2">STEP {item.step}</div>
                  <h3 className="text-2xl font-bold mb-3">{item.title}</h3>
                  <p className="text-slate-400 mb-4">{item.description}</p>
                  <ul className="space-y-2">
                    {item.details.map((detail, idx) => (
                      <li key={idx} className="flex items-start text-slate-300">
                        <CheckCircle2 className="w-5 h-5 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                        {detail}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Explainability */}
      <section className="py-24">
        <div className="section-container">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
                Transparent AI
                <span className="block gradient-text">You Can Trust</span>
              </h2>
              <p className="text-xl text-slate-600 mb-8">
                Every AI recommendation comes with complete explainability. Understand exactly why the
                system flagged a transaction, what patterns it detected, and the confidence level—so you
                can make informed professional judgments.
              </p>

              <div className="space-y-6">
                {[
                  {
                    icon: Eye,
                    title: 'Complete Transparency',
                    description: 'See the exact factors and weights that contributed to each AI decision.',
                  },
                  {
                    icon: GitBranch,
                    title: 'Audit Trail',
                    description: 'Every AI action is logged with timestamps, model versions, and confidence scores.',
                  },
                  {
                    icon: Settings,
                    title: 'Adjustable Thresholds',
                    description: 'Fine-tune sensitivity levels based on your professional judgment and client risk.',
                  },
                  {
                    icon: Activity,
                    title: 'Confidence Scoring',
                    description: 'Each finding includes a confidence percentage so you know where to focus review.',
                  },
                ].map((item, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-900 mb-1">{item.title}</h3>
                      <p className="text-slate-600">{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glassmorphism rounded-3xl p-8 shadow-xl">
              <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center space-x-3">
                    <Brain className="w-6 h-6 text-purple-400" />
                    <span className="text-white font-semibold">AI Finding Analysis</span>
                  </div>
                  <span className="px-3 py-1 bg-orange-500/20 text-orange-400 text-sm rounded-full">High Confidence</span>
                </div>

                <div className="space-y-4 mb-6">
                  <div className="glassmorphism-dark rounded-xl p-4">
                    <div className="text-sm text-slate-400 mb-1">Finding</div>
                    <div className="text-white">Unusual revenue recognition pattern in Q4</div>
                  </div>

                  <div className="glassmorphism-dark rounded-xl p-4">
                    <div className="text-sm text-slate-400 mb-2">Contributing Factors</div>
                    <div className="space-y-2">
                      {[
                        { factor: 'Q4 revenue 43% higher than prior quarters', weight: 35 },
                        { factor: '12 large transactions on last day of quarter', weight: 30 },
                        { factor: 'Unusual counterparty concentration', weight: 20 },
                        { factor: 'Deviation from industry benchmark', weight: 15 },
                      ].map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between">
                          <span className="text-sm text-slate-300">{item.factor}</span>
                          <span className="text-xs text-purple-400">{item.weight}%</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="glassmorphism-dark rounded-xl p-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-400">Confidence Score</span>
                      <span className="text-2xl font-bold text-green-400">94%</span>
                    </div>
                    <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full" style={{ width: '94%' }} />
                    </div>
                  </div>
                </div>

                <button className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all">
                  View Full Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Integration Ecosystem */}
      <section className="py-24 bg-slate-50">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Connects to Your
              <span className="block gradient-text">Entire Ecosystem</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Seamless integration with 50+ accounting systems, ERPs, and practice management tools.
            </p>
          </div>

          <div className="grid grid-cols-3 md:grid-cols-6 gap-8 items-center justify-items-center">
            {['QuickBooks', 'Xero', 'NetSuite', 'SAP', 'Oracle', 'Sage', 'Dynamics', 'FreshBooks', 'Wave', 'Zoho', 'ADP', 'Gusto'].map((name, i) => (
              <div key={i} className="glassmorphism rounded-2xl px-6 py-4 text-center hover:shadow-lg transition-all">
                <span className="font-semibold text-slate-700">{name}</span>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link href="/integrations" className="inline-flex items-center text-blue-600 font-semibold hover:text-blue-700">
              View all 50+ integrations <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 text-white">
        <div className="section-container text-center">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
            Ready to Transform Your Audit Practice?
          </h2>
          <p className="text-xl text-white/90 mb-12 max-w-2xl mx-auto">
            Join 500+ CPA firms already using Aura to deliver faster, more accurate audits.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/#demo"
              className="px-8 py-4 bg-white text-slate-900 font-semibold rounded-2xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center space-x-2"
            >
              <span>Schedule Your Demo</span>
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
