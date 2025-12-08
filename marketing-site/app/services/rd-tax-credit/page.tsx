'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import Link from 'next/link'
import {
  Lightbulb,
  DollarSign,
  FileText,
  Shield,
  Clock,
  Target,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Database,
  BarChart3,
  Users,
  Building2,
  Calculator,
  FileSearch,
  TrendingUp,
  Award,
  Scale,
  Briefcase,
  Layers,
  Search,
  ClipboardCheck,
  FileCheck,
  Brain,
  Zap,
  Lock,
  PieChart,
  AlertCircle,
  HelpCircle,
  BookOpen,
  Settings,
  Workflow,
} from 'lucide-react'

export default function RDTaxCreditPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-green-50">
      <Navigation />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute inset-0 mesh-gradient" />
        <div className="absolute top-20 left-1/4 w-[500px] h-[500px] bg-green-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-blue-500/10 rounded-full blur-[120px]" />

        <div className="section-container relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 glassmorphism rounded-full mb-8">
              <Lightbulb className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-green-600">R&D Tax Credit Services</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-display font-bold mb-8 leading-tight">
              <span className="text-slate-900">AI-Powered</span>
              <span className="block gradient-text">R&D Tax Credit Studies</span>
            </h1>

            <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              Maximize your clients' R&D tax credits with our comprehensive AI platform. From qualification
              analysis to IRS-ready documentation, we automate the entire R&D study process while ensuring
              audit-proof defensibility.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link
                href="/#demo"
                className="group px-8 py-4 bg-gradient-to-r from-green-600 via-green-700 to-emerald-600 text-white font-semibold rounded-2xl hover:shadow-2xl hover:shadow-green-500/50 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <span>Start R&D Study</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/case-studies"
                className="px-8 py-4 glassmorphism text-slate-900 font-semibold rounded-2xl hover:shadow-xl transition-all duration-300"
              >
                View Success Stories
              </Link>
            </div>

            {/* Value Proposition Stats */}
            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto">
              {[
                { value: '$2.5M+', label: 'Average Credits Identified' },
                { value: '99.8%', label: 'IRS Audit Success Rate' },
                { value: '75%', label: 'Time Savings vs Manual' },
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

      {/* What is the R&D Tax Credit */}
      <section className="py-24 bg-white/50">
        <div className="section-container">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
                Understanding the
                <span className="block gradient-text">R&D Tax Credit</span>
              </h2>
              <p className="text-xl text-slate-600 mb-6 leading-relaxed">
                The Research & Development Tax Credit (IRC Section 41) is one of the most valuable tax
                incentives available to businesses. It provides a dollar-for-dollar reduction in federal
                tax liability for companies that engage in qualifying research activities.
              </p>
              <p className="text-lg text-slate-600 mb-8">
                Many businesses don't realize they qualify—including those in manufacturing, software
                development, engineering, life sciences, and countless other industries.
              </p>

              <div className="glassmorphism rounded-2xl p-6 mb-8">
                <h3 className="font-bold text-slate-900 mb-4 flex items-center">
                  <HelpCircle className="w-5 h-5 text-green-600 mr-2" />
                  The Four-Part Test
                </h3>
                <div className="space-y-3">
                  {[
                    { title: 'Permitted Purpose', desc: 'New or improved functionality, performance, reliability, or quality' },
                    { title: 'Technological Uncertainty', desc: 'Uncertainty exists at the start of the project' },
                    { title: 'Process of Experimentation', desc: 'Systematic evaluation of alternatives' },
                    { title: 'Technological in Nature', desc: 'Relies on principles of physical/biological sciences, engineering, or computer science' },
                  ].map((test, idx) => (
                    <div key={idx} className="flex items-start">
                      <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
                      <div>
                        <span className="font-semibold text-slate-900">{test.title}:</span>{' '}
                        <span className="text-slate-600">{test.desc}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="glassmorphism rounded-3xl p-8 shadow-xl">
              <h3 className="text-2xl font-bold text-slate-900 mb-6">Industries We Serve</h3>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { icon: Building2, name: 'Manufacturing' },
                  { icon: Settings, name: 'Software & Tech' },
                  { icon: Lightbulb, name: 'Engineering' },
                  { icon: Database, name: 'Life Sciences' },
                  { icon: Layers, name: 'Architecture' },
                  { icon: Workflow, name: 'Food & Beverage' },
                  { icon: Shield, name: 'Aerospace & Defense' },
                  { icon: TrendingUp, name: 'Financial Services' },
                  { icon: Users, name: 'Healthcare' },
                  { icon: Briefcase, name: 'Professional Services' },
                  { icon: Award, name: 'Agriculture' },
                  { icon: Calculator, name: 'Construction' },
                ].map((industry, idx) => (
                  <div key={idx} className="flex items-center space-x-3 p-3 rounded-xl hover:bg-green-50 transition-colors">
                    <industry.icon className="w-5 h-5 text-green-600" />
                    <span className="text-slate-700 font-medium">{industry.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Platform Features */}
      <section className="py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Complete R&D Tax Credit
              <span className="block gradient-text">Platform Features</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Our AI-powered platform handles every aspect of R&D tax credit studies—from initial
              qualification through IRS defense.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Search,
                title: 'AI Qualification Analysis',
                description: 'Our AI analyzes project descriptions, engineering documents, and financial data to automatically identify qualifying R&D activities using the four-part test.',
                features: ['Natural language processing', 'Technical uncertainty detection', 'Automatic categorization', 'Confidence scoring'],
                gradient: 'from-green-500 to-emerald-500',
              },
              {
                icon: Calculator,
                title: 'Credit Calculation Engine',
                description: 'Automatically calculate federal and state R&D credits using regular, alternative simplified, and startup methods—optimizing for maximum benefit.',
                features: ['Multi-method comparison', 'State credit optimization', 'ASC 740 impact analysis', 'Carry-forward tracking'],
                gradient: 'from-blue-500 to-cyan-500',
              },
              {
                icon: Users,
                title: 'Employee Survey System',
                description: 'Digital survey platform with smart questionnaires that guide employees through time allocation and project contribution documentation.',
                features: ['Smart questionnaires', 'Time allocation capture', 'Mobile-friendly interface', 'Automated reminders'],
                gradient: 'from-purple-500 to-pink-500',
              },
              {
                icon: FileSearch,
                title: 'Document Analysis AI',
                description: 'AI-powered document extraction that pulls qualifying information from project files, emails, specs, and contracts.',
                features: ['OCR for all formats', 'Semantic understanding', 'Key data extraction', 'Evidence linking'],
                gradient: 'from-orange-500 to-red-500',
              },
              {
                icon: ClipboardCheck,
                title: 'Contemporaneous Documentation',
                description: 'Generate IRS-compliant documentation packages with detailed project narratives, calculations, and supporting evidence.',
                features: ['IRS audit-ready format', 'Automatic narratives', 'Evidence indexing', 'Version control'],
                gradient: 'from-indigo-500 to-purple-500',
              },
              {
                icon: Shield,
                title: 'Audit Defense Package',
                description: 'Complete audit defense documentation including technical summaries, calculation support, and interview preparation materials.',
                features: ['Defense strategies', 'Response templates', 'Technical summaries', 'Expert witness support'],
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

      {/* The R&D Study Process */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
              Our AI-Powered
              <span className="block gradient-text">Study Process</span>
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              From engagement to IRS-ready deliverables in a fraction of the traditional time.
            </p>
          </div>

          <div className="max-w-5xl mx-auto">
            {[
              {
                step: '01',
                phase: 'Discovery & Data Collection',
                title: 'AI-Assisted Client Onboarding',
                description: 'Our platform guides clients through a streamlined data collection process:',
                details: [
                  'Client portal for secure document upload (project files, org charts, payroll)',
                  'AI analyzes uploaded documents to identify potential qualifying activities',
                  'Smart questionnaires adapt based on industry and project types',
                  'Automated PBC (Provided By Client) tracking and reminders',
                  'Integration with accounting systems for payroll and expense data',
                ],
                icon: Database,
                duration: '1-2 weeks',
              },
              {
                step: '02',
                phase: 'Technical Analysis',
                title: 'Four-Part Test Evaluation',
                description: 'AI evaluates each project against IRC Section 41 requirements:',
                details: [
                  'Natural language processing analyzes project descriptions for technical uncertainty',
                  'Pattern recognition identifies process of experimentation from documentation',
                  'Classification algorithms categorize activities by permitted purpose',
                  'Confidence scoring helps focus SME review on borderline cases',
                  'Automatic exclusion of activities that don\'t qualify (surveys, market research, etc.)',
                ],
                icon: Brain,
                duration: '1-2 weeks',
              },
              {
                step: '03',
                phase: 'Employee Interviews',
                title: 'Digital Survey & Time Allocation',
                description: 'Capture time and effort data directly from technical personnel:',
                details: [
                  'Role-based questionnaires tailored to engineering, IT, and management',
                  'Time allocation capture by project with supporting explanations',
                  'Mobile-friendly interface for maximum participation',
                  'AI-assisted response validation and consistency checking',
                  'Automated follow-up for incomplete or inconsistent responses',
                ],
                icon: Users,
                duration: '2-3 weeks',
              },
              {
                step: '04',
                phase: 'Credit Calculation',
                title: 'Multi-Method Optimization',
                description: 'Calculate credits using all available methodologies:',
                details: [
                  'Qualified Research Expenses (QREs) categorization and validation',
                  'Regular Credit vs. Alternative Simplified Credit comparison',
                  'Startup company provisions and limitations analysis',
                  'State credit calculations for all applicable jurisdictions',
                  'ASC 740 financial statement impact modeling',
                ],
                icon: Calculator,
                duration: '1 week',
              },
              {
                step: '05',
                phase: 'Documentation & Delivery',
                title: 'IRS-Ready Deliverables',
                description: 'Generate comprehensive study documentation:',
                details: [
                  'Detailed technical narratives for each qualifying project',
                  'Calculation workpapers with complete audit trail',
                  'Form 6765 preparation and supporting schedules',
                  'Executive summary with key findings and recommendations',
                  'Contemporaneous documentation package for audit defense',
                ],
                icon: FileCheck,
                duration: '1 week',
              },
            ].map((item, index) => (
              <div key={index} className="relative flex gap-8 mb-12 last:mb-0">
                <div className="flex-shrink-0 relative">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center">
                    <item.icon className="w-8 h-8 text-white" />
                  </div>
                  {index < 4 && (
                    <div className="absolute left-1/2 top-full w-0.5 h-12 bg-gradient-to-b from-green-500 to-transparent -translate-x-1/2" />
                  )}
                </div>
                <div className="flex-1 pb-8">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-sm font-bold text-green-400">STEP {item.step}: {item.phase}</div>
                    <span className="px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                      {item.duration}
                    </span>
                  </div>
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

      {/* Credit Calculation Methods */}
      <section className="py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Credit Calculation
              <span className="block gradient-text">Methodologies</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Our platform evaluates all available methods to maximize your clients' R&D tax benefits.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'Regular Credit (RC)',
                subtitle: 'For established companies',
                description: 'The traditional R&D credit calculation based on QREs exceeding a base amount determined by the company\'s historical research intensity.',
                rate: '20%',
                rateLabel: 'of QREs over base amount',
                ideal: 'Companies with consistent R&D history',
                considerations: ['Requires historical data', 'More complex calculation', 'Higher potential benefit'],
              },
              {
                title: 'Alternative Simplified Credit (ASC)',
                subtitle: 'Most commonly used',
                description: 'Simplified calculation using 14% of QREs exceeding 50% of average QREs for the prior three years.',
                rate: '14%',
                rateLabel: 'of QREs over base',
                ideal: 'Companies with limited history or fluctuating R&D',
                considerations: ['Simpler calculation', 'No gross receipts needed', 'Three-year lookback'],
              },
              {
                title: 'Startup Credit',
                subtitle: 'For qualifying startups',
                description: 'Allows eligible small businesses to apply up to $500,000 of R&D credit against payroll taxes annually.',
                rate: '$500K',
                rateLabel: 'max payroll tax offset',
                ideal: 'Pre-revenue or early-stage companies',
                considerations: ['Gross receipts < $5M', 'Immediate cash benefit', 'Five-year lookback'],
              },
            ].map((method, index) => (
              <div key={index} className="glassmorphism rounded-3xl p-8 hover:shadow-xl transition-all">
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-slate-900 mb-1">{method.title}</h3>
                  <p className="text-sm text-green-600 font-medium">{method.subtitle}</p>
                </div>
                <p className="text-slate-600 mb-6">{method.description}</p>
                <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-4 text-center text-white mb-6">
                  <div className="text-4xl font-bold mb-1">{method.rate}</div>
                  <div className="text-sm text-white/80">{method.rateLabel}</div>
                </div>
                <div className="mb-4">
                  <div className="text-sm font-semibold text-slate-900 mb-2">Ideal For:</div>
                  <p className="text-sm text-slate-600">{method.ideal}</p>
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-900 mb-2">Key Considerations:</div>
                  <ul className="space-y-1">
                    {method.considerations.map((item, idx) => (
                      <li key={idx} className="text-sm text-slate-600 flex items-center">
                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* State Credits */}
      <section className="py-24 bg-slate-50">
        <div className="section-container">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
                State R&D
                <span className="block gradient-text">Tax Credits</span>
              </h2>
              <p className="text-xl text-slate-600 mb-8">
                In addition to the federal credit, over 40 states offer their own R&D tax incentives.
                Our platform automatically calculates and optimizes state credits based on your clients'
                locations and activities.
              </p>

              <div className="space-y-4">
                {[
                  { state: 'California', rate: 'Up to 24% (combined)' },
                  { state: 'Massachusetts', rate: 'Up to 10% refundable' },
                  { state: 'Connecticut', rate: 'Up to 6% with carry-forward' },
                  { state: 'Arizona', rate: 'Up to 24% refundable' },
                  { state: 'New York', rate: 'Up to 6% with employment component' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between glassmorphism rounded-xl p-4">
                    <span className="font-semibold text-slate-900">{item.state}</span>
                    <span className="text-green-600 font-medium">{item.rate}</span>
                  </div>
                ))}
              </div>

              <p className="text-sm text-slate-500 mt-6">
                * Rates vary by company size, industry, and specific state provisions. Our platform analyzes
                all applicable state credits.
              </p>
            </div>

            <div className="glassmorphism rounded-3xl p-8 shadow-xl">
              <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
                <PieChart className="w-6 h-6 text-green-600 mr-3" />
                Sample Credit Analysis
              </h3>

              <div className="space-y-4 mb-8">
                <div className="flex items-center justify-between py-3 border-b border-slate-200">
                  <span className="text-slate-600">Qualified Research Expenses (QREs)</span>
                  <span className="font-bold text-slate-900">$5,200,000</span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-slate-200">
                  <span className="text-slate-600">Federal R&D Credit (ASC Method)</span>
                  <span className="font-bold text-green-600">$364,000</span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-slate-200">
                  <span className="text-slate-600">California R&D Credit</span>
                  <span className="font-bold text-green-600">$780,000</span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-slate-200">
                  <span className="text-slate-600">Massachusetts R&D Credit</span>
                  <span className="font-bold text-green-600">$156,000</span>
                </div>
              </div>

              <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-6 text-center text-white">
                <div className="text-sm font-medium text-white/80 mb-1">Total Credits Identified</div>
                <div className="text-4xl font-bold">$1,300,000</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Audit Defense */}
      <section className="py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              IRS Audit
              <span className="block gradient-text">Defense Ready</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Our documentation is designed to withstand IRS scrutiny. With a 99.8% audit success rate,
              our studies are built for defensibility from day one.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {[
              {
                icon: FileText,
                title: 'Contemporaneous Documentation',
                description: 'All documentation is created during the study process, not reconstructed after the fact—exactly what IRS examiners look for.',
              },
              {
                icon: Scale,
                title: 'Four-Part Test Analysis',
                description: 'Detailed project-by-project analysis demonstrating how each activity meets the statutory requirements of IRC Section 41.',
              },
              {
                icon: BookOpen,
                title: 'Technical Narratives',
                description: 'Clear, detailed narratives explaining the technological uncertainty and systematic experimentation for each project.',
              },
              {
                icon: ClipboardCheck,
                title: 'Calculation Workpapers',
                description: 'Complete audit trail from payroll data to final credit calculation with source document references.',
              },
              {
                icon: Users,
                title: 'Employee Documentation',
                description: 'Signed attestations, time allocation summaries, and interview notes for all contributing personnel.',
              },
              {
                icon: AlertCircle,
                title: 'Exclusion Analysis',
                description: 'Documentation of excluded activities and reasoning, demonstrating thorough and conservative approach.',
              },
            ].map((item, index) => (
              <div key={index} className="flex gap-6 glassmorphism rounded-2xl p-6 hover:shadow-lg transition-all">
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl flex items-center justify-center flex-shrink-0">
                  <item.icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2">{item.title}</h3>
                  <p className="text-slate-600">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-green-600 via-emerald-600 to-teal-600 text-white">
        <div className="section-container text-center">
          <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
            Ready to Unlock R&D Credits for Your Clients?
          </h2>
          <p className="text-xl text-white/90 mb-12 max-w-2xl mx-auto">
            Join hundreds of CPA firms using our platform to deliver high-quality R&D studies faster than ever.
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
              Contact Our R&D Team
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
