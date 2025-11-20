'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import {
  Brain,
  Zap,
  Shield,
  TrendingUp,
  Users,
  FileCheck,
  Clock,
  Target,
  CheckCircle,
  ArrowRight,
  Sparkles,
  Database,
  Lock,
  BarChart3,
  FileText,
  Search,
  AlertTriangle,
  Globe,
  Award,
  Star,
  LineChart,
  Layers,
  Cpu,
  CheckCircle2,
  Play,
} from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Home() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    phone: '',
  })
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Form submitted:', formData)
    alert('Thank you! We will contact you shortly to schedule your demo.')
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <Navigation />

      {/* Hero Section - Adobe-Inspired */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Animated Mesh Background */}
        <div className="absolute inset-0 mesh-gradient">
          <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-500/20 rounded-full blur-[120px] animate-float-slow" />
          <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-500/20 rounded-full blur-[120px] animate-float-medium" style={{ animationDelay: '2s' }} />
          <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-pink-500/15 rounded-full blur-[120px] animate-float-slow" style={{ animationDelay: '4s' }} />
        </div>

        {/* Grid Pattern Overlay */}
        <div className="absolute inset-0 opacity-[0.015]" style={{
          backgroundImage: `linear-gradient(to right, #0ea5e9 1px, transparent 1px), linear-gradient(to bottom, #0ea5e9 1px, transparent 1px)`,
          backgroundSize: '64px 64px'
        }} />

        <div className="relative section-container py-20 lg:py-32 z-10">
          <div className="max-w-5xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 px-4 py-2 glassmorphism rounded-full mb-8 animate-fade-in-up">
              <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                Trusted by 500+ Leading CPA Firms
              </span>
            </div>

            {/* Main Headline */}
            <h1 className="text-6xl md:text-7xl lg:text-8xl font-display font-bold mb-8 leading-[1.1] animate-fade-in-up delay-100">
              <span className="block text-slate-900">Transform Audits</span>
              <span className="block gradient-text">With AI Intelligence</span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed animate-fade-in-up delay-200">
              Complete audits 30-50% faster with AI-powered automation that catches what humans miss.
              PCAOB compliant, enterprise-grade security, trusted by the world's top firms.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-fade-in-up delay-300">
              <a
                href="https://portal.auraai.toroniandcompany.com/login"
                className="group px-8 py-4 bg-gradient-to-r from-blue-600 via-blue-700 to-purple-600 text-white font-semibold rounded-2xl hover:shadow-2xl hover:shadow-blue-500/50 transition-all duration-300 flex items-center justify-center space-x-2 hover:scale-[1.02]"
              >
                <span>Login to Portal</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </a>
              <a
                href="#demo"
                className="group px-8 py-4 glassmorphism text-slate-900 font-semibold rounded-2xl hover:shadow-xl transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <Play className="w-5 h-5" />
                <span>Watch Demo</span>
              </a>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto animate-fade-in-up delay-400">
              {[
                { value: '30-50%', label: 'Time Saved' },
                { value: '100K+', label: 'Trans/Hour' },
                { value: '99.9%', label: 'Accuracy' },
              ].map((stat, i) => (
                <div key={i} className="text-center">
                  <div className="text-3xl md:text-4xl font-bold gradient-text-2 mb-1">{stat.value}</div>
                  <div className="text-sm text-slate-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Hero Visual */}
          <div className="max-w-6xl mx-auto mt-20 animate-fade-in-up delay-500">
            <div className="relative">
              {/* Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-3xl blur-3xl opacity-20" />

              {/* Main Card */}
              <div className="relative glassmorphism rounded-3xl p-8 shadow-2xl">
                <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl overflow-hidden shadow-2xl">
                  {/* Browser Chrome */}
                  <div className="bg-slate-800/50 backdrop-blur-sm px-4 py-3 flex items-center justify-between border-b border-slate-700/50">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full" />
                      <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                      <div className="w-3 h-3 bg-green-500 rounded-full" />
                    </div>
                    <div className="flex-1 mx-4">
                      <div className="glassmorphism-dark rounded-lg px-4 py-1.5 text-xs text-slate-400 max-w-md mx-auto">
                        aura-audit.ai/dashboard
                      </div>
                    </div>
                  </div>

                  {/* Dashboard Content */}
                  <div className="p-8 space-y-6">
                    {/* Header */}
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-slate-400 text-sm mb-1">Current Analysis</div>
                        <div className="text-white text-2xl font-bold">Acme Corp Q4 Audit</div>
                      </div>
                      <div className="glassmorphism-dark px-4 py-2 rounded-xl">
                        <div className="text-emerald-400 text-sm font-semibold flex items-center space-x-2">
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Processing</span>
                        </div>
                      </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-3 gap-4">
                      {[
                        { icon: Database, label: 'Transactions', value: '147,382', change: '+12%' },
                        { icon: AlertTriangle, label: 'Anomalies', value: '23', change: '-45%' },
                        { icon: CheckCircle2, label: 'Validated', value: '99.7%', change: '+2.1%' },
                      ].map((item, i) => (
                        <div key={i} className="glassmorphism-dark rounded-xl p-4">
                          <div className="flex items-center justify-between mb-2">
                            <item.icon className="w-5 h-5 text-blue-400" />
                            <span className="text-emerald-400 text-xs font-semibold">{item.change}</span>
                          </div>
                          <div className="text-white text-xl font-bold mb-1">{item.value}</div>
                          <div className="text-slate-400 text-xs">{item.label}</div>
                        </div>
                      ))}
                    </div>

                    {/* Progress Bars */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-400">AI Analysis Progress</span>
                        <span className="text-white font-semibold">87%</span>
                      </div>
                      <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full" style={{ width: '87%' }} />
                      </div>
                    </div>

                    {/* Recent Findings */}
                    <div className="glassmorphism-dark rounded-xl p-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                          <Brain className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-white font-semibold mb-1">AI Detected Material Finding</div>
                          <div className="text-slate-400 text-sm">Revenue recognition pattern anomaly in Q3. Confidence: 94%</div>
                        </div>
                        <button className="text-blue-400 text-sm font-semibold hover:text-blue-300 transition-colors flex-shrink-0">
                          Review
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border-2 border-slate-300 rounded-full flex justify-center">
            <div className="w-1.5 h-3 bg-slate-400 rounded-full mt-2" />
          </div>
        </div>
      </section>

      {/* Trusted By Logos - Simplified */}
      <section className="py-16 bg-white/50 backdrop-blur-sm border-y border-slate-200">
        <div className="section-container">
          <div className="text-center mb-8">
            <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Trusted By Industry Leaders</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center justify-items-center opacity-40">
            {['Deloitte', 'PwC', 'KPMG', 'EY'].map((name, i) => (
              <div key={i} className="text-2xl font-bold text-slate-400">{name}</div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section - Adobe Style */}
      <section id="features" className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 mesh-gradient opacity-50" />

        <div className="section-container relative z-10">
          <div className="text-center mb-20 max-w-3xl mx-auto">
            <h2 className="text-5xl md:text-6xl font-display font-bold text-slate-900 mb-6">
              Everything you need to
              <span className="block gradient-text">audit smarter</span>
            </h2>
            <p className="text-xl text-slate-600 leading-relaxed">
              From data ingestion to final report, Aura automates every step with AI-powered intelligence.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Database,
                title: 'Automated Data Ingestion',
                description: 'Connect to 20+ accounting systems. Automatic account mapping with ML intelligence.',
                gradient: 'from-blue-500 to-cyan-500',
              },
              {
                icon: Brain,
                title: 'AI-Powered Analysis',
                description: 'Analyze 100,000+ transactions per hour with pattern recognition that catches fraud.',
                gradient: 'from-purple-500 to-pink-500',
              },
              {
                icon: FileText,
                title: 'Smart Disclosure Drafting',
                description: 'Auto-generate GAAP-compliant disclosures for 30+ ASC topics with citations.',
                gradient: 'from-blue-500 to-purple-500',
              },
              {
                icon: Search,
                title: 'Advanced Fraud Detection',
                description: 'ML-based anomaly detection and pattern recognition for sophisticated schemes.',
                gradient: 'from-pink-500 to-red-500',
              },
              {
                icon: Shield,
                title: 'PCAOB Compliance',
                description: 'Immutable audit trail, 7-year retention, complete data lineage built-in.',
                gradient: 'from-green-500 to-emerald-500',
              },
              {
                icon: BarChart3,
                title: 'Real-Time Analytics',
                description: '30+ financial ratios, industry benchmarking, going concern assessment.',
                gradient: 'from-orange-500 to-yellow-500',
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="group relative floating-card glassmorphism rounded-3xl p-8 hover:shadow-2xl transition-all duration-500"
              >
                {/* Gradient Glow on Hover */}
                <div className={`absolute inset-0 bg-gradient-to-r ${feature.gradient} rounded-3xl opacity-0 group-hover:opacity-10 transition-opacity duration-500 blur-xl`} />

                <div className="relative">
                  <div className={`w-14 h-14 bg-gradient-to-r ${feature.gradient} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500`}>
                    <feature.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                  <p className="text-slate-600 leading-relaxed">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works - Modern Timeline */}
      <section className="py-32 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, rgba(255,255,255,0.15) 1px, transparent 0)`,
          backgroundSize: '48px 48px'
        }} />

        <div className="section-container relative z-10">
          <div className="text-center mb-20 max-w-3xl mx-auto">
            <h2 className="text-5xl md:text-6xl font-display font-bold mb-6">
              From data to report in
              <span className="block gradient-text">three simple steps</span>
            </h2>
            <p className="text-xl text-slate-400 leading-relaxed">
              Transform weeks of manual work into hours of intelligent automation
            </p>
          </div>

          <div className="max-w-5xl mx-auto space-y-12">
            {[
              {
                step: '01',
                title: 'Import & Normalize',
                description: 'Connect your accounting systems or upload trial balances. Our AI automatically maps accounts, identifies entities, and normalizes data from any format.',
                icon: Database,
                color: 'from-blue-500 to-cyan-500',
              },
              {
                step: '02',
                title: 'AI-Powered Analysis',
                description: 'Watch as Aura analyzes 100,000+ transactions, performs 30+ ratio calculations, detects anomalies, and drafts GAAP-compliant disclosures—all in minutes.',
                icon: Brain,
                color: 'from-purple-500 to-pink-500',
              },
              {
                step: '03',
                title: 'Review & Finalize',
                description: 'Review AI findings with explainable recommendations, collaborate with your team, get partner approval, and generate reports with e-signatures.',
                icon: FileCheck,
                color: 'from-green-500 to-emerald-500',
              },
            ].map((item, index) => (
              <div
                key={index}
                className="group relative flex flex-col md:flex-row items-start gap-8 p-8 glassmorphism-dark rounded-3xl hover:shadow-2xl transition-all duration-500"
              >
                {/* Step Number */}
                <div className="flex-shrink-0">
                  <div className={`w-20 h-20 bg-gradient-to-br ${item.color} rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-500`}>
                    <item.icon className="w-10 h-10 text-white" />
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1">
                  <div className="text-sm font-bold text-slate-500 mb-2">STEP {item.step}</div>
                  <h3 className="text-3xl font-bold mb-4">{item.title}</h3>
                  <p className="text-lg text-slate-400 leading-relaxed">{item.description}</p>
                </div>

                {/* Connection Line */}
                {index < 2 && (
                  <div className="hidden md:block absolute left-10 top-full w-0.5 h-12 bg-gradient-to-b from-slate-700 to-transparent" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof - Testimonials */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 mesh-gradient opacity-50" />

        <div className="section-container relative z-10">
          <div className="text-center mb-20 max-w-3xl mx-auto">
            <h2 className="text-5xl md:text-6xl font-display font-bold text-slate-900 mb-6">
              Loved by
              <span className="block gradient-text">audit professionals</span>
            </h2>
            <p className="text-xl text-slate-600">See what our customers are saying</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                quote: "Aura reduced our audit time by 40%. The AI catches things we would have missed. Absolutely game-changing.",
                author: "Sarah Mitchell",
                role: "Managing Partner",
                firm: "Mitchell & Associates CPA",
                rating: 5,
              },
              {
                quote: "The fraud detection alone paid for itself in the first month. We caught a $500K embezzlement scheme.",
                author: "David Chen",
                role: "Senior Audit Manager",
                firm: "Chen Accounting Group",
                rating: 5,
              },
              {
                quote: "Finally, audit software that doesn't feel like it's from 1995. My staff actually enjoys using it.",
                author: "Maria Rodriguez",
                role: "Firm Owner",
                firm: "Rodriguez CPA Firm",
                rating: 5,
              },
            ].map((testimonial, index) => (
              <div
                key={index}
                className="floating-card glassmorphism rounded-3xl p-8 shadow-xl"
              >
                <div className="flex mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                  ))}
                </div>
                <p className="text-slate-700 mb-6 text-lg leading-relaxed">&ldquo;{testimonial.quote}&rdquo;</p>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {testimonial.author[0]}
                  </div>
                  <div>
                    <div className="font-semibold text-slate-900">{testimonial.author}</div>
                    <div className="text-sm text-slate-600">{testimonial.role}</div>
                    <div className="text-sm text-slate-500">{testimonial.firm}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section - Modern Cards */}
      <section id="pricing" className="py-32 bg-gradient-to-br from-slate-50 to-white">
        <div className="section-container">
          <div className="text-center mb-20 max-w-3xl mx-auto">
            <h2 className="text-5xl md:text-6xl font-display font-bold text-slate-900 mb-6">
              Simple, transparent
              <span className="block gradient-text">pricing</span>
            </h2>
            <p className="text-xl text-slate-600">
              Choose the plan that fits your firm. All plans include PCAOB compliance.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                name: 'Starter',
                price: '499',
                description: 'Perfect for solo practitioners',
                features: [
                  'Up to 10 engagements/year',
                  'Basic AI analysis',
                  'Standard integrations',
                  'Email support',
                  'PCAOB audit trail',
                  '1 user license',
                ],
                cta: 'Start Free Trial',
                popular: false,
                gradient: 'from-blue-500 to-cyan-500',
              },
              {
                name: 'Professional',
                price: '1,299',
                description: 'Most popular for growing firms',
                features: [
                  'Up to 50 engagements/year',
                  'Advanced AI + fraud detection',
                  'All integrations',
                  'Priority support',
                  'Team collaboration',
                  'Up to 5 user licenses',
                  'Custom reporting',
                  'API access',
                ],
                cta: 'Start Free Trial',
                popular: true,
                gradient: 'from-purple-500 to-pink-500',
              },
              {
                name: 'Enterprise',
                price: 'Custom',
                description: 'Maximum flexibility',
                features: [
                  'Unlimited engagements',
                  'White-label options',
                  'Dedicated account manager',
                  '24/7 phone support',
                  'Custom integrations',
                  'Unlimited users',
                  'Advanced analytics',
                  'SLA guarantees',
                ],
                cta: 'Contact Sales',
                popular: false,
                gradient: 'from-green-500 to-emerald-500',
              },
            ].map((plan, index) => (
              <div
                key={index}
                className={`relative floating-card glassmorphism rounded-3xl p-8 ${
                  plan.popular ? 'ring-2 ring-purple-500 shadow-2xl scale-105' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className={`px-4 py-1 bg-gradient-to-r ${plan.gradient} text-white text-sm font-semibold rounded-full shadow-lg`}>
                      MOST POPULAR
                    </div>
                  </div>
                )}

                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-slate-900 mb-2">{plan.name}</h3>
                  <p className="text-slate-600 text-sm mb-6">{plan.description}</p>
                  <div className="flex items-baseline justify-center mb-2">
                    {plan.price !== 'Custom' ? (
                      <>
                        <span className="text-5xl font-bold gradient-text-2">${plan.price}</span>
                        <span className="text-slate-600 ml-2">/month</span>
                      </>
                    ) : (
                      <span className="text-5xl font-bold gradient-text-2">Custom</span>
                    )}
                  </div>
                </div>

                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start space-x-3">
                      <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-slate-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <a
                  href="#demo"
                  className={`block w-full py-3 px-6 text-center font-semibold rounded-xl transition-all duration-300 ${
                    plan.popular
                      ? `bg-gradient-to-r ${plan.gradient} text-white hover:shadow-lg hover:shadow-purple-500/50`
                      : 'bg-slate-100 text-slate-900 hover:bg-slate-200'
                  }`}
                >
                  {plan.cta}
                </a>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <p className="text-slate-600">All plans include 14-day free trial. No credit card required.</p>
          </div>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="py-20 bg-white/50 backdrop-blur-sm border-y border-slate-200">
        <div className="section-container">
          <div className="text-center mb-12">
            <h3 className="text-2xl font-bold text-slate-900 mb-2">Enterprise-Grade Security & Compliance</h3>
            <p className="text-slate-600">Trusted by firms that audit Fortune 500 companies</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center justify-items-center">
            {[
              { icon: Award, label: 'SOC 2 Type II', sublabel: 'Certified' },
              { icon: Shield, label: 'PCAOB', sublabel: 'Compliant' },
              { icon: Lock, label: 'AES-256', sublabel: 'Encryption' },
              { icon: Globe, label: 'GDPR', sublabel: 'Compliant' },
            ].map((item, i) => (
              <div key={i} className="flex flex-col items-center text-center">
                <item.icon className="w-16 h-16 text-blue-600 mb-3" />
                <div className="font-semibold text-slate-900">{item.label}</div>
                <div className="text-sm text-slate-600">{item.sublabel}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Form Section */}
      <section id="demo" className="py-32 relative overflow-hidden bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600">
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 0)`,
          backgroundSize: '48px 48px'
        }} />

        <div className="section-container relative z-10">
          <div className="max-w-4xl mx-auto">
            <div className="text-center text-white mb-12">
              <h2 className="text-5xl md:text-6xl font-display font-bold mb-6">
                See Aura in action
              </h2>
              <p className="text-xl text-white/90">
                Schedule a personalized demo and transform your audit practice
              </p>
            </div>

            <div className="glassmorphism rounded-3xl shadow-2xl p-8 lg:p-12">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-semibold text-slate-900 mb-2">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      required
                      className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                      placeholder="John Smith"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-sm font-semibold text-slate-900 mb-2">
                      Work Email *
                    </label>
                    <input
                      type="email"
                      id="email"
                      required
                      className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                      placeholder="john@yourfirm.com"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="company" className="block text-sm font-semibold text-slate-900 mb-2">
                      Firm Name *
                    </label>
                    <input
                      type="text"
                      id="company"
                      required
                      className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                      placeholder="Smith & Associates CPA"
                      value={formData.company}
                      onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                    />
                  </div>
                  <div>
                    <label htmlFor="phone" className="block text-sm font-semibold text-slate-900 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      id="phone"
                      className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                      placeholder="(555) 123-4567"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  className="w-full py-4 bg-gradient-to-r from-slate-900 to-slate-800 text-white font-semibold rounded-xl hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 flex items-center justify-center space-x-2"
                >
                  <span>Request Your Demo</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
                <p className="text-sm text-slate-700 text-center">
                  By submitting this form, you agree to receive communications from Aura Audit AI.
                </p>
              </form>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
