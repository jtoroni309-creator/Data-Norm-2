'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import Link from 'next/link'
import {
  Shield,
  ShieldCheck,
  Lock,
  FileCheck,
  CheckCircle2,
  ArrowRight,
  AlertTriangle,
  Database,
  Eye,
  Users,
  Building2,
  ClipboardList,
  Target,
  Gauge,
  FileText,
  Clock,
  TrendingUp,
  Network,
  Server,
  Key,
  Fingerprint,
  Activity,
  BarChart3,
  Layers,
  Settings,
  RefreshCw,
  Workflow,
  Award,
  BookOpen,
  Zap,
} from 'lucide-react'

export default function SOCCompliancePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50">
      <Navigation />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 mesh-gradient" />
        <div className="absolute top-20 right-1/4 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-1/4 w-[400px] h-[400px] bg-blue-500/10 rounded-full blur-[120px]" />

        <div className="section-container relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 glassmorphism rounded-full mb-8">
              <ShieldCheck className="w-5 h-5 text-indigo-600" />
              <span className="text-sm font-medium text-indigo-600">SOC Compliance Platform</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-display font-bold mb-8 leading-tight">
              <span className="text-slate-900">AI-Powered</span>
              <span className="block gradient-text">SOC Examinations</span>
            </h1>

            <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              Streamline SOC 1, SOC 2, and SOC 3 examinations with intelligent automation. Our platform
              handles control testing, evidence collection, and report generation—reducing examination
              time by up to 60%.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link
                href="/#demo"
                className="group px-8 py-4 bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 text-white font-semibold rounded-2xl hover:shadow-2xl hover:shadow-indigo-500/50 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <span>Start SOC Engagement</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/compliance"
                className="px-8 py-4 glassmorphism text-slate-900 font-semibold rounded-2xl hover:shadow-xl transition-all duration-300"
              >
                Our Certifications
              </Link>
            </div>

            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto">
              {[
                { value: '60%', label: 'Faster Examinations' },
                { value: '500+', label: 'SOC Reports Delivered' },
                { value: '100%', label: 'AICPA Compliant' },
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

      {/* SOC Report Types */}
      <section className="py-24 bg-white/50">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Complete SOC
              <span className="block gradient-text">Examination Coverage</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Our platform supports all SOC examination types with specialized workflows and controls testing.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'SOC 1',
                subtitle: 'ICFR Controls',
                description: 'For service organizations that impact their clients\' internal controls over financial reporting (ICFR). Type I and Type II reports available.',
                features: [
                  'SSAE 18 compliant',
                  'Control objectives mapping',
                  'Carve-out/Inclusive methods',
                  'Complementary user entity controls',
                  'Financial auditor coordination',
                ],
                gradient: 'from-blue-500 to-cyan-500',
                icon: FileCheck,
              },
              {
                title: 'SOC 2',
                subtitle: 'Trust Services Criteria',
                description: 'Evaluates controls relevant to security, availability, processing integrity, confidentiality, and privacy. The gold standard for technology companies.',
                features: [
                  'All 5 Trust Services Criteria',
                  'Common Criteria coverage',
                  'Point of focus testing',
                  'Gap analysis & remediation',
                  'Continuous monitoring support',
                ],
                gradient: 'from-indigo-500 to-purple-500',
                icon: Shield,
              },
              {
                title: 'SOC 3',
                subtitle: 'Public Report',
                description: 'A publicly available summary report based on SOC 2 criteria. Ideal for marketing and building trust with prospects.',
                features: [
                  'Public distribution',
                  'SOC 2 seal of approval',
                  'Marketing ready',
                  'Trust badge included',
                  'Annual renewal support',
                ],
                gradient: 'from-purple-500 to-pink-500',
                icon: Award,
              },
            ].map((report, index) => (
              <div key={index} className="glassmorphism rounded-3xl p-8 hover:shadow-xl transition-all">
                <div className={`w-14 h-14 bg-gradient-to-r ${report.gradient} rounded-2xl flex items-center justify-center mb-6`}>
                  <report.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 mb-1">{report.title}</h3>
                <p className="text-sm text-indigo-600 font-medium mb-4">{report.subtitle}</p>
                <p className="text-slate-600 mb-6">{report.description}</p>
                <ul className="space-y-2">
                  {report.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center text-sm text-slate-700">
                      <CheckCircle2 className="w-4 h-4 text-green-600 mr-2 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Services Criteria */}
      <section className="py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Trust Services
              <span className="block gradient-text">Criteria Coverage</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Our platform includes pre-built control matrices and testing procedures for all five Trust Services Criteria.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-6">
            {[
              {
                icon: Lock,
                title: 'Security',
                description: 'Protection against unauthorized access',
                controls: '25+ controls',
                color: 'from-blue-500 to-blue-600',
              },
              {
                icon: Activity,
                title: 'Availability',
                description: 'Systems accessible as agreed',
                controls: '15+ controls',
                color: 'from-green-500 to-green-600',
              },
              {
                icon: Target,
                title: 'Processing Integrity',
                description: 'Accurate, complete processing',
                controls: '20+ controls',
                color: 'from-orange-500 to-orange-600',
              },
              {
                icon: Eye,
                title: 'Confidentiality',
                description: 'Protected confidential info',
                controls: '15+ controls',
                color: 'from-purple-500 to-purple-600',
              },
              {
                icon: Fingerprint,
                title: 'Privacy',
                description: 'Personal info handling',
                controls: '30+ controls',
                color: 'from-pink-500 to-pink-600',
              },
            ].map((criteria, index) => (
              <div key={index} className="text-center glassmorphism rounded-2xl p-6 hover:shadow-lg transition-all">
                <div className={`w-14 h-14 bg-gradient-to-r ${criteria.color} rounded-xl flex items-center justify-center mx-auto mb-4`}>
                  <criteria.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 mb-2">{criteria.title}</h3>
                <p className="text-sm text-slate-600 mb-3">{criteria.description}</p>
                <span className="inline-block px-3 py-1 bg-slate-100 text-slate-700 text-xs font-medium rounded-full">
                  {criteria.controls}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platform Features */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
              AI-Powered
              <span className="block gradient-text">Examination Features</span>
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Every tool you need to conduct efficient, high-quality SOC examinations.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: ClipboardList,
                title: 'Control Matrix Builder',
                description: 'Pre-built control matrices for all SOC types. Customize controls, map to criteria, and define testing procedures.',
                features: ['Template library', 'Drag-and-drop builder', 'Criteria mapping', 'Risk ranking'],
              },
              {
                icon: Database,
                title: 'Evidence Collection Portal',
                description: 'Secure client portal for evidence upload with automatic organization and validation.',
                features: ['Secure upload', 'Auto-categorization', 'Completeness tracking', 'Version control'],
              },
              {
                icon: Workflow,
                title: 'Automated Control Testing',
                description: 'AI performs initial control testing, samples transactions, and flags exceptions for review.',
                features: ['Statistical sampling', 'Exception detection', 'Population analysis', 'Test documentation'],
              },
              {
                icon: RefreshCw,
                title: 'Continuous Monitoring',
                description: 'Real-time control monitoring for Type II examinations with automated alerting.',
                features: ['Real-time dashboards', 'Alert configuration', 'Trend analysis', 'Deviation tracking'],
              },
              {
                icon: FileText,
                title: 'Report Generation',
                description: 'AI-assisted report drafting with AICPA-compliant templates and reviewer workflow.',
                features: ['AICPA templates', 'Auto-population', 'Review workflow', 'Version management'],
              },
              {
                icon: Users,
                title: 'Client Collaboration',
                description: 'Shared workspace for management responses, remediation tracking, and status updates.',
                features: ['Response portal', 'Remediation tracking', 'Status dashboards', 'Comment threads'],
              },
            ].map((feature, index) => (
              <div key={index} className="glassmorphism-dark rounded-2xl p-6 hover:bg-slate-800/50 transition-all">
                <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                <p className="text-slate-400 mb-4 text-sm">{feature.description}</p>
                <div className="flex flex-wrap gap-2">
                  {feature.features.map((item, idx) => (
                    <span key={idx} className="px-2 py-1 bg-indigo-500/20 text-indigo-300 text-xs rounded-full">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Examination Process */}
      <section className="py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Streamlined
              <span className="block gradient-text">Examination Process</span>
            </h2>
          </div>

          <div className="max-w-4xl mx-auto">
            {[
              {
                phase: 'Planning',
                title: 'Engagement Setup & Scoping',
                description: 'Define examination scope, identify systems, and establish control objectives.',
                tasks: ['Client onboarding', 'System inventory', 'Control scoping', 'Timeline planning'],
                duration: '1-2 weeks',
              },
              {
                phase: 'Assessment',
                title: 'Control Design Evaluation',
                description: 'Evaluate control design against Trust Services Criteria and identify gaps.',
                tasks: ['Control walkthroughs', 'Design assessment', 'Gap identification', 'Remediation recommendations'],
                duration: '2-3 weeks',
              },
              {
                phase: 'Testing',
                title: 'Control Testing & Evidence',
                description: 'Test control operating effectiveness through inquiry, observation, and inspection.',
                tasks: ['Sample selection', 'Evidence collection', 'Exception testing', 'Results documentation'],
                duration: '3-4 weeks',
              },
              {
                phase: 'Reporting',
                title: 'Report Preparation & Review',
                description: 'Draft SOC report with management assertions and auditor opinion.',
                tasks: ['Report drafting', 'Management review', 'QC review', 'Final delivery'],
                duration: '1-2 weeks',
              },
            ].map((step, index) => (
              <div key={index} className="flex gap-8 mb-8 last:mb-0">
                <div className="flex-shrink-0 text-center">
                  <div className="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center text-white font-bold text-xl mb-2">
                    {String(index + 1).padStart(2, '0')}
                  </div>
                  {index < 3 && <div className="w-0.5 h-12 bg-gradient-to-b from-indigo-500 to-transparent mx-auto" />}
                </div>
                <div className="flex-1 glassmorphism rounded-2xl p-6 mb-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-bold text-indigo-600">{step.phase}</span>
                    <span className="text-sm text-slate-500">{step.duration}</span>
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">{step.title}</h3>
                  <p className="text-slate-600 mb-4">{step.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {step.tasks.map((task, idx) => (
                      <span key={idx} className="px-3 py-1 bg-indigo-100 text-indigo-700 text-sm rounded-full">
                        {task}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 text-white">
        <div className="section-container text-center">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
            Ready to Transform Your SOC Practice?
          </h2>
          <p className="text-xl text-white/90 mb-12 max-w-2xl mx-auto">
            Join the leading CPA firms using Aura to deliver SOC examinations faster and more efficiently.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/#demo"
              className="px-8 py-4 bg-white text-slate-900 font-semibold rounded-2xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center space-x-2"
            >
              <span>Schedule Demo</span>
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
