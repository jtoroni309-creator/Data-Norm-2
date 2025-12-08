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
  ExternalLink,
  MapPin,
  Globe,
  BadgeCheck,
  Landmark,
  Factory,
  Cpu,
  Beaker,
  Plane,
  Stethoscope,
  Car,
  Hammer,
  Wheat,
  Utensils,
  Package,
  Phone,
  Banknote,
  BadgeDollarSign,
  Receipt,
  ShieldCheck,
  Info,
} from 'lucide-react'

// Comprehensive state R&D credit data
const stateCredits = [
  { state: 'Arizona', abbr: 'AZ', rate: '24%', refundable: true, carryforward: '15 years', notes: 'Refundable for small businesses' },
  { state: 'California', abbr: 'CA', rate: '24%', refundable: false, carryforward: 'Indefinite', notes: 'Largest state R&D credit program' },
  { state: 'Colorado', abbr: 'CO', rate: '3%', refundable: false, carryforward: 'Indefinite', notes: 'Enterprise zone bonus available' },
  { state: 'Connecticut', abbr: 'CT', rate: '6%', refundable: true, carryforward: '15 years', notes: 'Refundable for companies <$70M' },
  { state: 'Delaware', abbr: 'DE', rate: '10%', refundable: false, carryforward: '15 years', notes: 'Additional credit for increased R&D' },
  { state: 'Florida', abbr: 'FL', rate: '10%', refundable: false, carryforward: '5 years', notes: 'Corporate income tax credit' },
  { state: 'Georgia', abbr: 'GA', rate: '10%', refundable: false, carryforward: '10 years', notes: 'Job tax credit bonus available' },
  { state: 'Hawaii', abbr: 'HI', rate: '20%', refundable: true, carryforward: '5 years', notes: 'Highest rate, refundable' },
  { state: 'Idaho', abbr: 'ID', rate: '5%', refundable: false, carryforward: '14 years', notes: 'Above $500K QREs: 4%' },
  { state: 'Illinois', abbr: 'IL', rate: '6.5%', refundable: false, carryforward: '5 years', notes: 'Incremental credit available' },
  { state: 'Indiana', abbr: 'IN', rate: '15%', refundable: false, carryforward: '10 years', notes: 'One of highest state rates' },
  { state: 'Iowa', abbr: 'IA', rate: '6.5%', refundable: true, carryforward: '5 years', notes: 'Supplemental credit available' },
  { state: 'Kansas', abbr: 'KS', rate: '6.5%', refundable: false, carryforward: '4 years', notes: 'Network center credit also available' },
  { state: 'Kentucky', abbr: 'KY', rate: '5%', refundable: false, carryforward: '10 years', notes: 'Construction credit excluded' },
  { state: 'Louisiana', abbr: 'LA', rate: '30%', refundable: true, carryforward: '5 years', notes: 'Payroll credit also available' },
  { state: 'Maine', abbr: 'ME', rate: '5%', refundable: true, carryforward: '15 years', notes: 'Super credit for R&D expansion' },
  { state: 'Maryland', abbr: 'MD', rate: '10%', refundable: true, carryforward: '7 years', notes: 'Basic and growth credits' },
  { state: 'Massachusetts', abbr: 'MA', rate: '10%', refundable: true, carryforward: '15 years', notes: 'Life sciences bonus available' },
  { state: 'Michigan', abbr: 'MI', rate: '1.9%', refundable: false, carryforward: '10 years', notes: 'Applied to MBT liability' },
  { state: 'Minnesota', abbr: 'MN', rate: '10%', refundable: false, carryforward: '15 years', notes: 'First $2M at higher rate' },
  { state: 'Mississippi', abbr: 'MS', rate: '2.5%', refundable: false, carryforward: '5 years', notes: 'Skills training credit also' },
  { state: 'Missouri', abbr: 'MO', rate: '6.5%', refundable: false, carryforward: '12 years', notes: 'Cap of $10M per year' },
  { state: 'Montana', abbr: 'MT', rate: '5%', refundable: false, carryforward: '7 years', notes: 'University research credit' },
  { state: 'Nebraska', abbr: 'NE', rate: '3%', refundable: true, carryforward: '5 years', notes: 'Refundable with agreement' },
  { state: 'New Hampshire', abbr: 'NH', rate: '10%', refundable: false, carryforward: '5 years', notes: 'Against BPT' },
  { state: 'New Jersey', abbr: 'NJ', rate: '10%', refundable: true, carryforward: '7 years', notes: 'Technology business credit' },
  { state: 'New Mexico', abbr: 'NM', rate: '5%', refundable: false, carryforward: '3 years', notes: 'Small business rate higher' },
  { state: 'New York', abbr: 'NY', rate: '6%', refundable: true, carryforward: '15 years', notes: 'Employment component bonus' },
  { state: 'North Carolina', abbr: 'NC', rate: '3.25%', refundable: false, carryforward: '15 years', notes: 'County tier bonuses' },
  { state: 'North Dakota', abbr: 'ND', rate: '8%', refundable: true, carryforward: '15 years', notes: 'Automation credit also' },
  { state: 'Ohio', abbr: 'OH', rate: '7%', refundable: false, carryforward: '7 years', notes: 'Against CAT' },
  { state: 'Oregon', abbr: 'OR', rate: '6.5%', refundable: false, carryforward: '5 years', notes: 'University partnership bonus' },
  { state: 'Pennsylvania', abbr: 'PA', rate: '10%', refundable: false, carryforward: '15 years', notes: 'Annual cap of $55M' },
  { state: 'Rhode Island', abbr: 'RI', rate: '22.5%', refundable: true, carryforward: '7 years', notes: 'High rate, some refundable' },
  { state: 'South Carolina', abbr: 'SC', rate: '5%', refundable: false, carryforward: '10 years', notes: 'Job development bonus' },
  { state: 'Tennessee', abbr: 'TN', rate: '10%', refundable: false, carryforward: '15 years', notes: 'Against franchise/excise tax' },
  { state: 'Texas', abbr: 'TX', rate: '5%', refundable: false, carryforward: '20 years', notes: 'Against franchise tax' },
  { state: 'Utah', abbr: 'UT', rate: '7.5%', refundable: true, carryforward: '14 years', notes: 'Nonrefundable portion 5%' },
  { state: 'Vermont', abbr: 'VT', rate: '27%', refundable: false, carryforward: '10 years', notes: 'Highest nominal state rate' },
  { state: 'Virginia', abbr: 'VA', rate: '15%', refundable: false, carryforward: '10 years', notes: 'Major R&D expenses credit' },
  { state: 'Wisconsin', abbr: 'WI', rate: '5.75%', refundable: false, carryforward: '15 years', notes: 'Engine/energy systems bonus' },
]

// Key statistics for backlink-worthy content
const rdStatistics = [
  { stat: '$18.8 Billion', label: 'Total R&D Credits Claimed (2020)', source: 'IRS Statistics of Income' },
  { stat: '23,000+', label: 'Companies Claiming R&D Credit', source: 'IRS Data' },
  { stat: '~10%', label: 'Companies Eligible but Not Claiming', source: 'Industry Estimates' },
  { stat: '$500K', label: 'Max Payroll Tax Offset for Startups', source: 'PATH Act (2015)' },
  { stat: '40+', label: 'States with R&D Tax Credits', source: 'State Tax Authorities' },
  { stat: '1981', label: 'Federal R&D Credit Enacted', source: 'Economic Recovery Tax Act' },
]

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
              <span className="text-sm font-medium text-green-600">Federal & State R&D Tax Credit Services</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-display font-bold mb-8 leading-tight">
              <span className="text-slate-900">AI-Powered</span>
              <span className="block gradient-text">R&D Tax Credit Studies</span>
            </h1>

            <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              Maximize federal and state R&D tax credits for your clients. Our comprehensive AI platform handles
              qualification analysis, credit calculations, and IRS-ready documentation—delivering audit-proof
              studies that unlock millions in tax savings.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link
                href="#pricing"
                className="group px-8 py-4 bg-gradient-to-r from-green-600 via-green-700 to-emerald-600 text-white font-semibold rounded-2xl hover:shadow-2xl hover:shadow-green-500/50 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <span>View R&D Study Pricing</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/#demo"
                className="px-8 py-4 glassmorphism text-slate-900 font-semibold rounded-2xl hover:shadow-xl transition-all duration-300"
              >
                Schedule Demo
              </Link>
            </div>

            {/* Key Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
              {[
                { value: '$18.8B', label: 'Credits Claimed Annually' },
                { value: '99.8%', label: 'IRS Audit Success Rate' },
                { value: '40+', label: 'States with R&D Credits' },
                { value: '75%', label: 'Time Savings vs Manual' },
              ].map((stat, i) => (
                <div key={i} className="text-center glassmorphism rounded-xl p-4">
                  <div className="text-2xl md:text-3xl font-bold gradient-text-2 mb-1">{stat.value}</div>
                  <div className="text-xs md:text-sm text-slate-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* What is the Federal R&D Tax Credit - Comprehensive Guide */}
      <section id="federal-credit" className="py-24 bg-white/50">
        <div className="section-container">
          <div className="max-w-4xl mx-auto mb-16">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-50 rounded-full mb-6">
              <Landmark className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-600">Federal R&D Tax Credit</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Federal R&D Tax Credit
              <span className="block gradient-text">Complete Guide (IRC Section 41)</span>
            </h2>
            <p className="text-xl text-slate-600 leading-relaxed">
              The Research and Development Tax Credit, codified under <strong>Internal Revenue Code Section 41</strong>,
              is a dollar-for-dollar tax incentive designed to encourage American businesses to invest in innovation.
              Originally enacted as part of the <strong>Economic Recovery Tax Act of 1981</strong>, the credit was made
              permanent by the <strong>Protecting Americans from Tax Hikes (PATH) Act of 2015</strong>.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8 mb-16">
            {/* History & Background */}
            <div className="glassmorphism rounded-3xl p-8">
              <div className="w-14 h-14 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center mb-6">
                <BookOpen className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-4">History & Background</h3>
              <div className="space-y-3 text-slate-600">
                <p><strong>1981:</strong> R&D credit created (ERTA)</p>
                <p><strong>1986:</strong> Alternative Incremental Research Credit added</p>
                <p><strong>2007:</strong> Alternative Simplified Credit (ASC) introduced</p>
                <p><strong>2015:</strong> PATH Act makes credit permanent</p>
                <p><strong>2016:</strong> Payroll tax offset for startups begins</p>
                <p><strong>2022:</strong> R&D amortization requirement (Section 174)</p>
              </div>
            </div>

            {/* Who Qualifies */}
            <div className="glassmorphism rounded-3xl p-8">
              <div className="w-14 h-14 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center mb-6">
                <BadgeCheck className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-4">Who Qualifies?</h3>
              <div className="space-y-3 text-slate-600">
                <p>Any business that develops or improves products, processes, software, or formulas may qualify, including:</p>
                <ul className="space-y-2">
                  <li className="flex items-center"><CheckCircle2 className="w-4 h-4 text-green-600 mr-2" />C-corporations and S-corporations</li>
                  <li className="flex items-center"><CheckCircle2 className="w-4 h-4 text-green-600 mr-2" />Partnerships and LLCs</li>
                  <li className="flex items-center"><CheckCircle2 className="w-4 h-4 text-green-600 mr-2" />Sole proprietorships</li>
                  <li className="flex items-center"><CheckCircle2 className="w-4 h-4 text-green-600 mr-2" />Startups (payroll offset)</li>
                </ul>
              </div>
            </div>

            {/* Credit Value */}
            <div className="glassmorphism rounded-3xl p-8">
              <div className="w-14 h-14 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mb-6">
                <BadgeDollarSign className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-4">Credit Value</h3>
              <div className="space-y-3 text-slate-600">
                <p>The federal R&D credit typically yields:</p>
                <div className="space-y-2">
                  <div className="flex justify-between p-2 bg-green-50 rounded-lg">
                    <span>Regular Credit:</span>
                    <span className="font-bold text-green-600">~20% of QREs</span>
                  </div>
                  <div className="flex justify-between p-2 bg-green-50 rounded-lg">
                    <span>ASC Method:</span>
                    <span className="font-bold text-green-600">~6-7% of QREs</span>
                  </div>
                  <div className="flex justify-between p-2 bg-green-50 rounded-lg">
                    <span>Startup Offset:</span>
                    <span className="font-bold text-green-600">Up to $500K/year</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* The Four-Part Test - Detailed */}
          <div className="glassmorphism rounded-3xl p-8 mb-16">
            <h3 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
              <HelpCircle className="w-6 h-6 text-green-600 mr-3" />
              The Four-Part Test (IRC Section 41(d))
            </h3>
            <p className="text-slate-600 mb-8">
              For an activity to qualify for the R&D tax credit, it must satisfy all four parts of the following test.
              This is the foundation of every R&D tax credit study and the primary focus during IRS examinations.
            </p>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                {
                  title: '1. Permitted Purpose (Section 41(d)(1)(B)(i))',
                  desc: 'The activity must be undertaken to create new or improved functionality, performance, reliability, or quality of a business component (product, process, formula, invention, technique, or software).',
                  examples: ['Designing a new product feature', 'Improving manufacturing efficiency', 'Enhancing software performance', 'Developing new formulations'],
                  bgClass: 'bg-blue-50 border-blue-100',
                  dotClass: 'bg-blue-500',
                },
                {
                  title: '2. Technological in Nature (Section 41(d)(1)(B)(ii))',
                  desc: 'The activity must fundamentally rely on principles of the physical sciences, biological sciences, engineering, or computer science.',
                  examples: ['Engineering analysis', 'Software development', 'Chemical formulation', 'Biological research'],
                  bgClass: 'bg-purple-50 border-purple-100',
                  dotClass: 'bg-purple-500',
                },
                {
                  title: '3. Elimination of Uncertainty (Section 41(d)(1)(B)(iii))',
                  desc: 'There must be technological uncertainty at the outset regarding capability, method, or appropriate design of the business component.',
                  examples: ['Uncertainty about feasibility', 'Unknown optimal design', 'Performance outcome questions', 'Method effectiveness uncertainty'],
                  bgClass: 'bg-orange-50 border-orange-100',
                  dotClass: 'bg-orange-500',
                },
                {
                  title: '4. Process of Experimentation (Section 41(d)(1)(C))',
                  desc: 'Substantially all activities must constitute a process of experimentation—evaluating alternatives through systematic trial and error, modeling, simulation, or testing.',
                  examples: ['Prototype development', 'Testing iterations', 'Simulation modeling', 'Design alternatives evaluation'],
                  bgClass: 'bg-green-50 border-green-100',
                  dotClass: 'bg-green-500',
                },
              ].map((test, idx) => (
                <div key={idx} className={`p-6 rounded-2xl border ${test.bgClass}`}>
                  <h4 className="font-bold text-slate-900 mb-3 text-lg">{test.title}</h4>
                  <p className="text-slate-600 mb-4">{test.desc}</p>
                  <div className="text-sm">
                    <span className="font-semibold text-slate-700">Examples:</span>
                    <ul className="mt-2 space-y-1">
                      {test.examples.map((ex, i) => (
                        <li key={i} className="flex items-center text-slate-600">
                          <div className={`w-1.5 h-1.5 ${test.dotClass} rounded-full mr-2`} />
                          {ex}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Qualified Research Expenses */}
          <div className="grid lg:grid-cols-2 gap-8">
            <div className="glassmorphism rounded-3xl p-8">
              <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
                <Receipt className="w-6 h-6 text-green-600 mr-3" />
                Qualified Research Expenses (QREs)
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-green-50 rounded-xl">
                  <h4 className="font-bold text-slate-900 mb-2">Wages (IRC 41(b)(2)(A))</h4>
                  <p className="text-slate-600 text-sm">W-2 wages for employees directly engaged in, supervising, or supporting qualified research activities. Typically 65-70% of total QREs.</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-xl">
                  <h4 className="font-bold text-slate-900 mb-2">Supplies (IRC 41(b)(2)(B))</h4>
                  <p className="text-slate-600 text-sm">Tangible property (other than land, improvements, or property subject to depreciation) used and consumed in qualified research.</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-xl">
                  <h4 className="font-bold text-slate-900 mb-2">Contract Research (IRC 41(b)(3))</h4>
                  <p className="text-slate-600 text-sm">65% of amounts paid to third parties for qualified research performed on behalf of the taxpayer. Must be research conducted in the U.S.</p>
                </div>
                <div className="p-4 bg-orange-50 rounded-xl">
                  <h4 className="font-bold text-slate-900 mb-2">Basic Research Payments (IRC 41(e))</h4>
                  <p className="text-slate-600 text-sm">Payments to qualified organizations (universities, research consortiums) for basic research. 100% included.</p>
                </div>
              </div>
            </div>

            <div className="glassmorphism rounded-3xl p-8">
              <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
                <AlertCircle className="w-6 h-6 text-red-600 mr-3" />
                Excluded Activities (Section 41(d)(4))
              </h3>
              <p className="text-slate-600 mb-4">The following activities are specifically excluded from the R&D credit:</p>
              <div className="space-y-3">
                {[
                  'Research conducted after commercial production begins',
                  'Adaptation of existing products for specific customers',
                  'Duplication of existing products or processes',
                  'Surveys, studies, or market research',
                  'Quality control and routine testing',
                  'Efficiency surveys and management studies',
                  'Research conducted outside the United States',
                  'Research in social sciences, arts, or humanities',
                  'Research funded by grants or contracts',
                  'Reverse engineering of competitors\' products',
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start p-2 bg-red-50 rounded-lg">
                    <AlertCircle className="w-4 h-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-700 text-sm">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Credit Calculation Methods */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
              Federal Credit
              <span className="block gradient-text">Calculation Methods</span>
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Three calculation methods are available. Our platform evaluates all three to maximize your clients' benefit.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'Regular Credit (RC)',
                subtitle: 'IRC Section 41(a)(1)',
                rate: '20%',
                rateDesc: 'of QREs exceeding base amount',
                formula: 'Credit = 20% × (QREs - Base Amount)',
                baseCalc: 'Base = Fixed Base % × Avg Gross Receipts',
                ideal: 'Companies with consistent R&D history and strong base period',
                pros: ['Highest potential credit rate', 'Best for mature companies', 'Rewards R&D growth'],
                cons: ['Requires historical data', 'Complex calculation', 'Base amount considerations'],
                gradient: 'from-blue-500 to-indigo-500',
              },
              {
                title: 'Alternative Simplified Credit (ASC)',
                subtitle: 'IRC Section 41(c)(5)',
                rate: '14%',
                rateDesc: 'of QREs exceeding 50% of 3-year average',
                formula: 'Credit = 14% × (QREs - 50% × Avg Prior 3yr QREs)',
                baseCalc: 'If no prior QREs: 6% × Current Year QREs',
                ideal: 'Companies with fluctuating R&D or limited history',
                pros: ['Simpler calculation', 'No gross receipts needed', 'Good for new R&D programs'],
                cons: ['Lower rate than RC', 'Three-year lookback required', 'Limited benefit in year one'],
                gradient: 'from-green-500 to-emerald-500',
              },
              {
                title: 'Payroll Tax Offset',
                subtitle: 'IRC Section 41(h) - PATH Act',
                rate: '$500K',
                rateDesc: 'maximum annual payroll tax offset',
                formula: 'Up to $250K/year (FICA employer portion)',
                baseCalc: 'Qualified Small Business: <$5M gross receipts',
                ideal: 'Pre-revenue startups with R&D expenses',
                pros: ['Immediate cash benefit', 'Offsets payroll taxes', 'Available pre-revenue'],
                cons: ['$5M gross receipts limit', 'Five-year limitation', 'No prior gross receipts allowed'],
                gradient: 'from-purple-500 to-pink-500',
              },
            ].map((method, index) => (
              <div key={index} className="bg-white/5 backdrop-blur-sm rounded-3xl p-8 border border-white/10">
                <div className={`text-sm font-medium text-transparent bg-gradient-to-r ${method.gradient} bg-clip-text mb-2`}>
                  {method.subtitle}
                </div>
                <h3 className="text-2xl font-bold mb-4">{method.title}</h3>

                <div className={`bg-gradient-to-r ${method.gradient} rounded-xl p-4 text-center mb-6`}>
                  <div className="text-4xl font-bold mb-1">{method.rate}</div>
                  <div className="text-sm text-white/80">{method.rateDesc}</div>
                </div>

                <div className="space-y-4 mb-6">
                  <div className="p-3 bg-white/5 rounded-lg">
                    <div className="text-xs text-slate-400 mb-1">Formula:</div>
                    <div className="text-sm font-mono">{method.formula}</div>
                  </div>
                  <div className="p-3 bg-white/5 rounded-lg">
                    <div className="text-xs text-slate-400 mb-1">Base Calculation:</div>
                    <div className="text-sm font-mono">{method.baseCalc}</div>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="text-sm font-semibold mb-2 flex items-center">
                    <Target className="w-4 h-4 mr-2 text-green-400" /> Ideal For:
                  </div>
                  <p className="text-sm text-slate-400">{method.ideal}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="font-semibold text-green-400 mb-2">Pros:</div>
                    <ul className="space-y-1">
                      {method.pros.map((pro, i) => (
                        <li key={i} className="flex items-center text-slate-400">
                          <CheckCircle2 className="w-3 h-3 mr-1 text-green-400 flex-shrink-0" />
                          {pro}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div className="font-semibold text-orange-400 mb-2">Considerations:</div>
                    <ul className="space-y-1">
                      {method.cons.map((con, i) => (
                        <li key={i} className="flex items-center text-slate-400">
                          <AlertCircle className="w-3 h-3 mr-1 text-orange-400 flex-shrink-0" />
                          {con}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* State R&D Credits - Comprehensive Section */}
      <section id="state-credits" className="py-24 bg-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-purple-50 rounded-full mb-6">
              <MapPin className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-medium text-purple-600">State R&D Tax Credits</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              State R&D Tax Credits
              <span className="block gradient-text">40+ States Offer Additional Benefits</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Beyond the federal credit, over 40 states offer their own R&D tax incentives. Combined federal and state
              credits can return 10-30% of qualified research expenses. Our platform automatically calculates credits
              for all applicable jurisdictions.
            </p>
          </div>

          {/* State Credit Highlights */}
          <div className="grid md:grid-cols-4 gap-4 mb-12">
            <div className="glassmorphism rounded-xl p-6 text-center border-l-4 border-green-500">
              <TrendingUp className="w-8 h-8 text-green-600 mx-auto mb-3" />
              <div className="text-xs text-slate-500 mb-1">Highest Rate</div>
              <div className="font-bold text-slate-900">Vermont 27%</div>
            </div>
            <div className="glassmorphism rounded-xl p-6 text-center border-l-4 border-blue-500">
              <Banknote className="w-8 h-8 text-blue-600 mx-auto mb-3" />
              <div className="text-xs text-slate-500 mb-1">Best Refundable</div>
              <div className="font-bold text-slate-900">Hawaii 20%</div>
            </div>
            <div className="glassmorphism rounded-xl p-6 text-center border-l-4 border-purple-500">
              <Building2 className="w-8 h-8 text-purple-600 mx-auto mb-3" />
              <div className="text-xs text-slate-500 mb-1">Largest Program</div>
              <div className="font-bold text-slate-900">California</div>
            </div>
            <div className="glassmorphism rounded-xl p-6 text-center border-l-4 border-orange-500">
              <Zap className="w-8 h-8 text-orange-600 mx-auto mb-3" />
              <div className="text-xs text-slate-500 mb-1">Best for Startups</div>
              <div className="font-bold text-slate-900">Arizona 24%</div>
            </div>
          </div>

          {/* Full State Credit Table */}
          <div className="glassmorphism rounded-3xl p-8 overflow-hidden">
            <h3 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
              <Globe className="w-6 h-6 text-purple-600 mr-3" />
              Complete State R&D Credit Reference
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">State</th>
                    <th className="text-center py-3 px-4 font-semibold text-slate-700">Credit Rate</th>
                    <th className="text-center py-3 px-4 font-semibold text-slate-700">Refundable?</th>
                    <th className="text-center py-3 px-4 font-semibold text-slate-700">Carryforward</th>
                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Key Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {stateCredits.map((state, idx) => (
                    <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-3 px-4 font-medium text-slate-900">
                        <span className="inline-flex items-center">
                          <span className="w-8 h-5 bg-slate-200 rounded text-xs flex items-center justify-center mr-2 font-bold">
                            {state.abbr}
                          </span>
                          {state.state}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className="font-bold text-green-600">{state.rate}</span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        {state.refundable ? (
                          <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                            <CheckCircle2 className="w-3 h-3 mr-1" /> Yes
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 bg-slate-100 text-slate-600 rounded-full text-xs">
                            No
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-center text-slate-600">{state.carryforward}</td>
                      <td className="py-3 px-4 text-slate-600 text-xs">{state.notes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-slate-500 mt-4">
              * State credit rates and provisions are subject to change. Please verify current rates with state tax authorities.
              Our platform maintains up-to-date state credit calculations.
            </p>
          </div>

          {/* State Credit Calculator Example */}
          <div className="mt-12 grid lg:grid-cols-2 gap-8">
            <div className="glassmorphism rounded-3xl p-8">
              <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
                <Calculator className="w-6 h-6 text-green-600 mr-3" />
                Multi-State Credit Example
              </h3>
              <p className="text-slate-600 mb-6">
                Software company with operations in California and Massachusetts with $2.5M in qualified research expenses:
              </p>
              <div className="space-y-3">
                <div className="flex justify-between p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-600">Qualified Research Expenses</span>
                  <span className="font-bold text-slate-900">$2,500,000</span>
                </div>
                <div className="flex justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="text-slate-600">Federal R&D Credit (ASC)</span>
                  <span className="font-bold text-blue-600">$175,000</span>
                </div>
                <div className="flex justify-between p-3 bg-purple-50 rounded-lg">
                  <span className="text-slate-600">California R&D Credit</span>
                  <span className="font-bold text-purple-600">$375,000</span>
                </div>
                <div className="flex justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-slate-600">Massachusetts R&D Credit</span>
                  <span className="font-bold text-green-600">$75,000</span>
                </div>
                <div className="flex justify-between p-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg text-white">
                  <span className="font-semibold">Total Credits</span>
                  <span className="font-bold text-xl">$625,000</span>
                </div>
              </div>
              <p className="text-sm text-slate-500 mt-4">
                * Example for illustration. Actual credits depend on company-specific factors, base amounts, and state apportionment.
              </p>
            </div>

            <div className="glassmorphism rounded-3xl p-8">
              <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
                <Info className="w-6 h-6 text-blue-600 mr-3" />
                State Credit Considerations
              </h3>
              <div className="space-y-4">
                {[
                  {
                    title: 'Nexus Requirements',
                    desc: 'Companies must have tax nexus in a state to claim its R&D credit. Remote employees may create nexus.',
                  },
                  {
                    title: 'Apportionment',
                    desc: 'Multi-state companies typically apportion QREs based on payroll, property, or sales factors.',
                  },
                  {
                    title: 'Refundability',
                    desc: 'Some states offer refundable credits (immediate cash) while others are non-refundable (reduce tax liability).',
                  },
                  {
                    title: 'Carryforward Periods',
                    desc: 'Unused credits can often be carried forward. Periods range from 3 years to indefinite depending on state.',
                  },
                  {
                    title: 'Annual Caps',
                    desc: 'Some states cap total R&D credits awarded statewide or per taxpayer. Early filing may be advantageous.',
                  },
                ].map((item, idx) => (
                  <div key={idx} className="p-4 bg-slate-50 rounded-xl">
                    <h4 className="font-bold text-slate-900 mb-1">{item.title}</h4>
                    <p className="text-sm text-slate-600">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Industries We Serve */}
      <section className="py-24 bg-slate-50">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Industries That Qualify for
              <span className="block gradient-text">R&D Tax Credits</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              R&D tax credits aren't just for labs and tech companies. If your clients are solving problems, improving
              products, or developing new processes, they likely qualify.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Cpu, name: 'Software & Technology', examples: ['Application development', 'Cloud infrastructure', 'AI/ML development', 'Cybersecurity solutions'] },
              { icon: Factory, name: 'Manufacturing', examples: ['Process automation', 'Quality improvements', 'New product development', 'Tooling design'] },
              { icon: Beaker, name: 'Life Sciences', examples: ['Drug development', 'Medical devices', 'Clinical trials', 'Formulation R&D'] },
              { icon: Settings, name: 'Engineering', examples: ['Product design', 'CAD/CAM development', 'Testing & simulation', 'Prototype development'] },
              { icon: Plane, name: 'Aerospace & Defense', examples: ['Systems integration', 'Avionics development', 'Materials research', 'Compliance engineering'] },
              { icon: Stethoscope, name: 'Healthcare', examples: ['Medical software', 'Treatment protocols', 'Equipment development', 'Telehealth systems'] },
              { icon: Car, name: 'Automotive', examples: ['EV development', 'Safety systems', 'Emissions reduction', 'Connected vehicles'] },
              { icon: Hammer, name: 'Construction', examples: ['Green building methods', 'Structural innovations', 'Material testing', 'Safety systems'] },
              { icon: Wheat, name: 'Agriculture', examples: ['Crop development', 'Equipment innovation', 'Sustainability research', 'Processing improvements'] },
              { icon: Utensils, name: 'Food & Beverage', examples: ['New formulations', 'Shelf life extension', 'Process optimization', 'Packaging innovation'] },
              { icon: Package, name: 'Consumer Products', examples: ['Product development', 'Material innovation', 'Manufacturing processes', 'Quality improvements'] },
              { icon: Phone, name: 'Telecommunications', examples: ['Network development', '5G/6G research', 'Infrastructure', 'IoT solutions'] },
            ].map((industry, idx) => (
              <div key={idx} className="glassmorphism rounded-2xl p-6 hover:shadow-lg transition-all">
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mb-4">
                  <industry.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 mb-3">{industry.name}</h3>
                <ul className="space-y-1">
                  {industry.examples.map((ex, i) => (
                    <li key={i} className="text-sm text-slate-600 flex items-center">
                      <div className="w-1 h-1 bg-green-500 rounded-full mr-2" />
                      {ex}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
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

      {/* Pricing Section */}
      <section id="pricing" className="py-24 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-white/10 rounded-full mb-6">
              <BadgeDollarSign className="w-5 h-5 text-green-400" />
              <span className="text-sm font-medium text-green-400">Transparent Pricing</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
              R&D Study
              <span className="block gradient-text">Pricing Plans</span>
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Flexible pricing options for CPA firms. Use our platform yourself or let Aura AI handle the entire study.
            </p>
          </div>

          {/* Self-Service Pricing */}
          <div className="mb-16">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold mb-2 flex items-center justify-center">
                <Settings className="w-6 h-6 text-blue-400 mr-2" />
                Self-Service Platform
              </h3>
              <p className="text-slate-400">CPA firm licenses software and completes the study</p>
            </div>

            <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              {/* Under $25K Credits */}
              <div className="bg-white/5 backdrop-blur-sm rounded-3xl p-8 border border-white/10">
                <div className="text-center mb-6">
                  <div className="text-sm text-slate-400 mb-2">Credits Under $25,000</div>
                  <div className="inline-flex items-center justify-center px-4 py-2 bg-blue-500/20 rounded-full text-blue-400 text-sm font-medium mb-4">
                    Small Business Studies
                  </div>
                </div>

                <div className="space-y-4 mb-8">
                  <div className="p-4 bg-white/5 rounded-xl">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-slate-300">Federal Only</span>
                      <span className="text-3xl font-bold text-white">$800</span>
                    </div>
                    <p className="text-sm text-slate-500">Flat fee per study</p>
                  </div>
                  <div className="p-4 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-xl border border-green-500/30">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-slate-300">Federal + State</span>
                      <span className="text-3xl font-bold text-green-400">$1,250</span>
                    </div>
                    <p className="text-sm text-slate-500">Includes one state credit calculation</p>
                  </div>
                </div>

                <ul className="space-y-3 mb-8">
                  {[
                    'Full platform access',
                    'AI qualification analysis',
                    'Employee survey system',
                    'Credit calculations (all methods)',
                    'IRS-ready documentation',
                    'Form 6765 preparation',
                    'Email support',
                  ].map((item, idx) => (
                    <li key={idx} className="flex items-center text-slate-300 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-green-400 mr-2" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              {/* $25K - $125K Credits */}
              <div className="bg-white/5 backdrop-blur-sm rounded-3xl p-8 border border-green-500/30 relative">
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full text-sm font-bold">
                  Most Popular
                </div>
                <div className="text-center mb-6">
                  <div className="text-sm text-slate-400 mb-2">Credits $25,000 - $125,000</div>
                  <div className="inline-flex items-center justify-center px-4 py-2 bg-purple-500/20 rounded-full text-purple-400 text-sm font-medium mb-4">
                    Mid-Market Studies
                  </div>
                </div>

                <div className="space-y-4 mb-8">
                  <div className="p-4 bg-white/5 rounded-xl">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-slate-300">Federal Only</span>
                      <span className="text-3xl font-bold text-white">$1,500</span>
                    </div>
                    <p className="text-sm text-slate-500">Flat fee per study</p>
                  </div>
                  <div className="p-4 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-xl border border-green-500/30">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-slate-300">Federal + 1 State</span>
                      <span className="text-3xl font-bold text-green-400">$2,000</span>
                    </div>
                    <p className="text-sm text-slate-500">Each additional state: <span className="text-green-400 font-bold">+$300</span></p>
                  </div>
                </div>

                <ul className="space-y-3 mb-8">
                  {[
                    'Everything in Small Business, plus:',
                    'Multi-state credit optimization',
                    'Enhanced documentation package',
                    'ASC 740 impact analysis',
                    'Priority support',
                    'Audit defense materials',
                    'Calculation workpapers',
                  ].map((item, idx) => (
                    <li key={idx} className="flex items-center text-slate-300 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-green-400 mr-2" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Full-Service Pricing */}
          <div className="max-w-3xl mx-auto">
            <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm rounded-3xl p-8 border border-purple-500/30">
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center px-4 py-2 bg-purple-500/30 rounded-full text-purple-300 text-sm font-medium mb-4">
                  <ShieldCheck className="w-4 h-4 mr-2" />
                  Full-Service with Audit Protection
                </div>
                <h3 className="text-2xl font-bold mb-2">Aura AI Completes Your Study</h3>
                <p className="text-slate-400">We handle everything—your client just provides access to data</p>
              </div>

              <div className="flex flex-col md:flex-row items-center justify-center gap-8 mb-8">
                <div className="text-center">
                  <div className="text-5xl font-bold gradient-text mb-2">15%</div>
                  <div className="text-slate-400">of Credit Award</div>
                </div>
                <div className="hidden md:block w-px h-20 bg-slate-600" />
                <div className="text-left space-y-2 text-sm text-slate-300">
                  <div className="flex items-center"><CheckCircle2 className="w-4 h-4 text-green-400 mr-2" />Complete study execution by Aura AI experts</div>
                  <div className="flex items-center"><CheckCircle2 className="w-4 h-4 text-green-400 mr-2" />All federal and state credit calculations included</div>
                  <div className="flex items-center"><CheckCircle2 className="w-4 h-4 text-green-400 mr-2" />IRS audit protection and defense</div>
                  <div className="flex items-center"><CheckCircle2 className="w-4 h-4 text-green-400 mr-2" />Expert witness support if needed</div>
                  <div className="flex items-center"><CheckCircle2 className="w-4 h-4 text-green-400 mr-2" />No upfront cost—fee from realized credits only</div>
                </div>
              </div>

              <div className="text-center">
                <Link
                  href="/#demo"
                  className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-2xl hover:shadow-2xl transition-all duration-300"
                >
                  <span>Schedule Consultation</span>
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </div>
            </div>
          </div>

          {/* Pricing Notes */}
          <div className="mt-12 text-center text-sm text-slate-500 max-w-2xl mx-auto">
            <p className="mb-2">
              * Self-service pricing requires annual platform license. Contact us for volume discounts and enterprise pricing.
            </p>
            <p>
              * Full-service audit protection covers IRS and state examinations for the credit year studied.
              Additional years available at discounted rates.
            </p>
          </div>
        </div>
      </section>

      {/* R&D Tax Credit Statistics - Backlink-worthy content */}
      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              R&D Tax Credit
              <span className="block gradient-text">Industry Statistics</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Key statistics about the federal and state R&D tax credit programs.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-16">
            {rdStatistics.map((item, idx) => (
              <div key={idx} className="glassmorphism rounded-2xl p-6 text-center">
                <div className="text-3xl font-bold gradient-text mb-2">{item.stat}</div>
                <div className="text-slate-900 font-medium mb-2">{item.label}</div>
                <div className="text-xs text-slate-500">Source: {item.source}</div>
              </div>
            ))}
          </div>

          {/* Official Resources - Great for backlinks */}
          <div className="glassmorphism rounded-3xl p-8">
            <h3 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
              <ExternalLink className="w-6 h-6 text-blue-600 mr-3" />
              Official R&D Tax Credit Resources
            </h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { name: 'IRS R&D Credit Page', url: 'https://www.irs.gov/businesses/small-businesses-self-employed/research-and-experimentation-tax-credit', org: 'IRS' },
                { name: 'IRC Section 41 (Full Text)', url: 'https://www.law.cornell.edu/uscode/text/26/41', org: 'Cornell Law' },
                { name: 'Treasury Regulations §1.41', url: 'https://www.ecfr.gov/current/title-26/chapter-I/subchapter-A/part-1', org: 'eCFR' },
                { name: 'Form 6765 Instructions', url: 'https://www.irs.gov/forms-pubs/about-form-6765', org: 'IRS' },
                { name: 'Statistics of Income - R&D Credit', url: 'https://www.irs.gov/statistics/soi-tax-stats-corporation-research-credit', org: 'IRS SOI' },
                { name: 'PATH Act (2015)', url: 'https://www.congress.gov/bill/114th-congress/house-bill/2029', org: 'Congress.gov' },
              ].map((resource, idx) => (
                <a
                  key={idx}
                  href={resource.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-4 bg-slate-50 rounded-xl hover:bg-blue-50 transition-colors group"
                >
                  <div>
                    <div className="font-medium text-slate-900 group-hover:text-blue-600">{resource.name}</div>
                    <div className="text-xs text-slate-500">{resource.org}</div>
                  </div>
                  <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-blue-600" />
                </a>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section - Good for SEO */}
      <section className="py-24 bg-slate-50">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">
              Frequently Asked
              <span className="block gradient-text">Questions</span>
            </h2>
          </div>

          <div className="max-w-3xl mx-auto space-y-4">
            {[
              {
                q: 'What is the R&D tax credit worth?',
                a: 'The federal R&D credit typically equals 6-7% of qualified research expenses using the ASC method, or up to 20% using the regular credit method. Combined with state credits (where available), businesses can recover 10-30% of their R&D spending.',
              },
              {
                q: 'Can startups claim the R&D credit?',
                a: 'Yes! The PATH Act of 2015 allows qualified small businesses (gross receipts under $5 million with no gross receipts prior to 5 years ago) to apply up to $500,000 of R&D credits against payroll taxes annually. This provides immediate cash benefit even for pre-revenue companies.',
              },
              {
                q: 'What activities qualify for the R&D credit?',
                a: 'Qualifying activities must meet the four-part test: 1) Permitted purpose (new/improved product, process, software, etc.), 2) Technological in nature (based on hard sciences), 3) Elimination of uncertainty (technical challenges exist), and 4) Process of experimentation (systematic trial and error).',
              },
              {
                q: 'How far back can I amend returns to claim R&D credits?',
                a: 'You can generally amend returns up to 3 years from the filing date (or 2 years from payment date). Many states have different lookback periods. Our platform can help identify credits for prior years.',
              },
              {
                q: 'Is the R&D credit refundable?',
                a: 'The federal credit is generally non-refundable but can be carried forward for 20 years. However, qualified small businesses can offset payroll taxes. Some states (Arizona, Hawaii, Louisiana, etc.) offer refundable state R&D credits.',
              },
              {
                q: 'What documentation is required for an R&D credit study?',
                a: 'Key documentation includes: project descriptions, employee time records, payroll data, general ledger detail for supplies and contracts, organizational charts, and contemporaneous records showing the four-part test is met for each project.',
              },
              {
                q: 'How long does an R&D study take?',
                a: 'Using our AI-powered platform, most studies complete in 4-8 weeks (vs. 3-6 months manually). Timeline depends on company size, number of projects, and data availability.',
              },
              {
                q: 'What triggers an IRS audit of R&D credits?',
                a: 'Common triggers include: large or rapidly increasing credits, credits relative to company size, first-time claims, and inadequate documentation. Our platform creates contemporaneous, audit-ready documentation to minimize risk.',
              },
            ].map((faq, idx) => (
              <div key={idx} className="glassmorphism rounded-2xl p-6">
                <h3 className="font-bold text-slate-900 mb-3 flex items-start">
                  <HelpCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  {faq.q}
                </h3>
                <p className="text-slate-600 pl-7">{faq.a}</p>
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
              href="#pricing"
              className="px-8 py-4 border-2 border-white text-white font-semibold rounded-2xl hover:bg-white/10 transition-all duration-300"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
