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
} from 'lucide-react'
import { useState } from 'react'

export default function Home() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    phone: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission
    console.log('Form submitted:', formData)
    alert('Thank you! We will contact you shortly to schedule your demo.')
  }

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        {/* Animated Background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute w-96 h-96 -top-48 -left-48 bg-primary-300/20 rounded-full blur-3xl animate-float" />
          <div className="absolute w-96 h-96 -bottom-48 -right-48 bg-accent-300/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
        </div>

        <div className="relative section-container py-32 lg:py-40">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Hero Content */}
            <div className="text-center lg:text-left animate-fade-in">
              <div className="inline-flex items-center space-x-2 px-4 py-2 bg-primary-100 rounded-full text-primary-700 font-medium text-sm mb-6">
                <Sparkles className="w-4 h-4" />
                <span>Trusted by 500+ CPA Firms</span>
              </div>
              <h1 className="text-5xl lg:text-7xl font-display font-bold text-gray-900 mb-6 leading-tight">
                Audit Intelligence
                <br />
                <span className="gradient-text">For Modern CPAs</span>
              </h1>
              <p className="text-xl lg:text-2xl text-gray-600 mb-8 max-w-2xl">
                AI-powered audit automation that catches what humans miss. Complete audits 30-50% faster while maintaining complete PCAOB compliance.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <a
                  href="#demo"
                  className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-2xl hover:scale-105 transition-all flex items-center justify-center space-x-2"
                >
                  <span>Request a Demo</span>
                  <ArrowRight className="w-5 h-5" />
                </a>
                <a
                  href="#features"
                  className="px-8 py-4 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-primary-600 hover:text-primary-600 transition-all"
                >
                  See How It Works
                </a>
              </div>
              <div className="mt-12 grid grid-cols-3 gap-8 max-w-lg mx-auto lg:mx-0">
                <div>
                  <div className="text-3xl font-bold gradient-text">30-50%</div>
                  <div className="text-sm text-gray-600">Time Savings</div>
                </div>
                <div>
                  <div className="text-3xl font-bold gradient-text">100K+</div>
                  <div className="text-sm text-gray-600">Trans/Hour</div>
                </div>
                <div>
                  <div className="text-3xl font-bold gradient-text">99.9%</div>
                  <div className="text-sm text-gray-600">Accuracy</div>
                </div>
              </div>
            </div>

            {/* Hero Image/Illustration */}
            <div className="relative animate-scale-in">
              <div className="relative bg-gradient-to-br from-primary-600/10 to-accent-600/10 rounded-3xl p-8 backdrop-blur-sm border border-primary-200/50">
                <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
                  <div className="bg-gray-800 px-4 py-3 flex items-center space-x-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full" />
                    <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                    <div className="w-3 h-3 bg-green-500 rounded-full" />
                  </div>
                  <div className="p-8 space-y-4">
                    <div className="flex items-center space-x-3 text-sm">
                      <Brain className="w-5 h-5 text-primary-600" />
                      <span className="text-gray-600">AI analyzing 100,000+ transactions...</span>
                    </div>
                    <div className="space-y-2">
                      <div className="h-2 bg-gradient-to-r from-primary-600 to-accent-600 rounded-full w-full" />
                      <div className="h-2 bg-gradient-to-r from-primary-600 to-accent-600 rounded-full w-3/4" />
                      <div className="h-2 bg-gradient-to-r from-primary-600 to-accent-600 rounded-full w-5/6" />
                    </div>
                    <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-6 h-6 text-green-600" />
                        <div>
                          <div className="font-semibold text-gray-900">Audit Complete</div>
                          <div className="text-sm text-gray-600">3 material findings detected</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-green-600">85%</div>
                        <div className="text-xs text-gray-600">Time saved</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="bg-gradient-to-r from-primary-600 to-accent-600 text-white py-12">
        <div className="section-container">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2">500+</div>
              <div className="text-primary-100">CPA Firms</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">10,000+</div>
              <div className="text-primary-100">Audits Completed</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">$50M+</div>
              <div className="text-primary-100">Cost Savings</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">4.9/5</div>
              <div className="text-primary-100">User Rating</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-gray-900 mb-4">
              Everything You Need to <span className="gradient-text">Audit Smarter</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From data ingestion to final report, Aura automates every step of the audit process with AI-powered intelligence.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Database,
                title: 'Automated Data Ingestion',
                description: 'Import from QuickBooks, NetSuite, Xero, and 20+ systems. Automatic account mapping with ML intelligence.',
              },
              {
                icon: Brain,
                title: 'AI-Powered Analysis',
                description: 'Analyze 100,000+ transactions per hour. Pattern recognition that catches fraud and anomalies humans would miss.',
              },
              {
                icon: FileText,
                title: 'Smart Disclosure Drafting',
                description: 'Auto-generate GAAP-compliant disclosures for 30+ ASC topics with citations and confidence scores.',
              },
              {
                icon: Search,
                title: 'Advanced Fraud Detection',
                description: 'ML-based anomaly detection, Benford\'s Law analysis, and pattern recognition for sophisticated fraud schemes.',
              },
              {
                icon: Shield,
                title: 'PCAOB Compliance Built-In',
                description: 'Immutable audit trail, 7-year retention, complete data lineage. Pass peer review with confidence.',
              },
              {
                icon: BarChart3,
                title: 'Real-Time Analytics',
                description: '30+ financial ratios, industry benchmarking against 1000+ peers, going concern assessment.',
              },
              {
                icon: FileCheck,
                title: 'Electronic Confirmations',
                description: 'Bank, AR, AP, legal, and debt confirmations with tracking and digital signatures.',
              },
              {
                icon: Users,
                title: 'Team Collaboration',
                description: 'Role-based workflows, review notes, time tracking, and engagement management.',
              },
              {
                icon: Lock,
                title: 'Enterprise Security',
                description: 'SOC 2 Type II certified, AES-256 encryption, OIDC/SSO support, row-level security.',
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="group p-8 bg-gradient-to-br from-gray-50 to-white rounded-2xl border border-gray-200 hover:border-primary-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-primary-600 to-accent-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section id="benefits" className="py-24 bg-gradient-to-br from-gray-50 to-primary-50/30">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-gray-900 mb-4">
              Why CPA Firms <span className="gradient-text">Choose Aura</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Transform your audit practice with measurable results
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
                <Clock className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Work Smart, Not Hard</h3>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">Save 15-25 hours per engagement</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">Automatic account mapping eliminates manual work</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">AI drafts disclosures in minutes, not hours</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">Take on 2-3x more clients with same staff</span>
                </li>
              </ul>
              <div className="mt-8 p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="text-3xl font-bold text-green-600 mb-1">30-50%</div>
                <div className="text-sm text-gray-700">Reduction in audit hours</div>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                <Target className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Catch More, Miss Less</h3>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">Analyze 1000x more transactions than manual testing</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">Fraud detection catches patterns humans miss</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">Going concern assessment before it's too late</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">Compare clients against 1000+ peer companies</span>
                </li>
              </ul>
              <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="text-3xl font-bold text-blue-600 mb-1">100,000+</div>
                <div className="text-sm text-gray-700">Transactions analyzed per hour</div>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-6">
                <Shield className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Audit with Confidence</h3>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-purple-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">PCAOB AS 1215 compliant audit trail</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-purple-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">Explainable AI you can trust and defend</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-purple-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">E&O insurance validation and partnerships</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-purple-600 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">Partner approval required (you stay in control)</span>
                </li>
              </ul>
              <div className="mt-8 p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div className="text-3xl font-bold text-purple-600 mb-1">99.9%</div>
                <div className="text-sm text-gray-700">Consistency across auditors</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 bg-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-gray-900 mb-4">
              From Data to Report in <span className="gradient-text">3 Simple Steps</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See how Aura transforms weeks of manual work into hours of intelligent automation
            </p>
          </div>

          <div className="max-w-4xl mx-auto space-y-8">
            {[
              {
                step: '01',
                title: 'Import & Normalize',
                description: 'Connect your accounting systems or upload trial balances. Our AI automatically maps accounts, identifies entities, and normalizes data from any format.',
                icon: Database,
              },
              {
                step: '02',
                title: 'AI-Powered Analysis',
                description: 'Watch as Aura analyzes 100,000+ transactions, performs 30+ ratio calculations, detects anomalies, and drafts GAAP-compliant disclosures—all in minutes.',
                icon: Brain,
              },
              {
                step: '03',
                title: 'Review & Finalize',
                description: 'Review AI findings with explainable recommendations, collaborate with your team, get partner approval, and generate reports with e-signatures.',
                icon: FileCheck,
              },
            ].map((item, index) => (
              <div
                key={index}
                className="flex flex-col md:flex-row items-start md:items-center space-y-6 md:space-y-0 md:space-x-8 p-8 bg-gradient-to-br from-gray-50 to-white rounded-2xl border border-gray-200 hover:border-primary-300 hover:shadow-lg transition-all"
              >
                <div className="flex-shrink-0">
                  <div className="w-20 h-20 bg-gradient-to-br from-primary-600 to-accent-600 rounded-2xl flex items-center justify-center">
                    <item.icon className="w-10 h-10 text-white" />
                  </div>
                </div>
                <div className="flex-grow">
                  <div className="text-sm font-bold text-primary-600 mb-2">STEP {item.step}</div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">{item.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 bg-gradient-to-br from-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-gray-900 mb-4">
              Trusted by <span className="gradient-text">Leading CPA Firms</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See what our customers are saying
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                quote: "Aura reduced our audit time by 40%. What used to take 3 weeks now takes 10 days. The AI catches things we would have missed.",
                author: "Sarah Mitchell",
                role: "Managing Partner",
                firm: "Mitchell & Associates CPA",
                rating: 5,
              },
              {
                quote: "The fraud detection alone paid for itself in the first month. We caught a $500K embezzlement scheme that would have gone unnoticed.",
                author: "David Chen",
                role: "Senior Audit Manager",
                firm: "Chen Accounting Group",
                rating: 5,
              },
              {
                quote: "Finally, audit software that doesn't feel like it's from 1995. My staff actually enjoys using it, and training takes hours not weeks.",
                author: "Maria Rodriguez",
                role: "Firm Owner",
                firm: "Rodriguez CPA Firm",
                rating: 5,
              },
            ].map((testimonial, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow"
              >
                <div className="flex mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                  ))}
                </div>
                <p className="text-gray-700 mb-6 italic">&ldquo;{testimonial.quote}&rdquo;</p>
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-accent-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {testimonial.author[0]}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.author}</div>
                    <div className="text-sm text-gray-600">{testimonial.role}</div>
                    <div className="text-sm text-gray-500">{testimonial.firm}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 bg-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-gray-900 mb-4">
              Simple, <span className="gradient-text">Transparent Pricing</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Choose the plan that fits your firm. All plans include PCAOB compliance and unlimited support.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                name: 'Starter',
                price: '499',
                description: 'Perfect for solo practitioners and small firms',
                features: [
                  'Up to 10 engagements/year',
                  'Basic AI analysis',
                  'Standard integrations',
                  'Email support',
                  'PCAOB compliant audit trail',
                  '1 user license',
                ],
                cta: 'Start Free Trial',
                popular: false,
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
                  'Team collaboration tools',
                  'Up to 5 user licenses',
                  'Custom reporting',
                  'API access',
                ],
                cta: 'Start Free Trial',
                popular: true,
              },
              {
                name: 'Enterprise',
                price: 'Custom',
                description: 'For firms that need maximum flexibility',
                features: [
                  'Unlimited engagements',
                  'White-label options',
                  'Dedicated account manager',
                  '24/7 phone support',
                  'Custom integrations',
                  'Unlimited user licenses',
                  'Advanced analytics',
                  'SLA guarantees',
                ],
                cta: 'Contact Sales',
                popular: false,
              },
            ].map((plan, index) => (
              <div
                key={index}
                className={`relative bg-white rounded-2xl p-8 border-2 ${
                  plan.popular
                    ? 'border-primary-600 shadow-2xl scale-105'
                    : 'border-gray-200 shadow-lg'
                } hover:shadow-xl transition-all`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="px-4 py-1 bg-gradient-to-r from-primary-600 to-accent-600 text-white text-sm font-semibold rounded-full">
                      MOST POPULAR
                    </div>
                  </div>
                )}
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{plan.description}</p>
                  <div className="flex items-baseline justify-center mb-2">
                    {plan.price !== 'Custom' && (
                      <>
                        <span className="text-5xl font-bold gradient-text">${plan.price}</span>
                        <span className="text-gray-600 ml-2">/month</span>
                      </>
                    )}
                    {plan.price === 'Custom' && (
                      <span className="text-5xl font-bold gradient-text">Custom</span>
                    )}
                  </div>
                </div>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                <a
                  href="#demo"
                  className={`block w-full py-3 px-6 text-center font-semibold rounded-lg transition-all ${
                    plan.popular
                      ? 'bg-gradient-to-r from-primary-600 to-accent-600 text-white hover:shadow-lg'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {plan.cta}
                </a>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <p className="text-gray-600">
              All plans include 14-day free trial. No credit card required.
            </p>
          </div>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="py-16 bg-gray-50">
        <div className="section-container">
          <div className="text-center mb-12">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Enterprise-Grade Security & Compliance</h3>
            <p className="text-gray-600">Trusted by firms that audit Fortune 500 companies</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center justify-items-center">
            <div className="flex flex-col items-center">
              <Award className="w-16 h-16 text-primary-600 mb-2" />
              <div className="font-semibold text-gray-900">SOC 2 Type II</div>
              <div className="text-sm text-gray-600">Certified</div>
            </div>
            <div className="flex flex-col items-center">
              <Shield className="w-16 h-16 text-primary-600 mb-2" />
              <div className="font-semibold text-gray-900">PCAOB</div>
              <div className="text-sm text-gray-600">Compliant</div>
            </div>
            <div className="flex flex-col items-center">
              <Lock className="w-16 h-16 text-primary-600 mb-2" />
              <div className="font-semibold text-gray-900">AES-256</div>
              <div className="text-sm text-gray-600">Encryption</div>
            </div>
            <div className="flex flex-col items-center">
              <Globe className="w-16 h-16 text-primary-600 mb-2" />
              <div className="font-semibold text-gray-900">GDPR</div>
              <div className="text-sm text-gray-600">Compliant</div>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Form Section */}
      <section id="demo" className="py-24 bg-gradient-to-br from-primary-600 to-accent-600">
        <div className="section-container">
          <div className="max-w-4xl mx-auto">
            <div className="text-center text-white mb-12">
              <h2 className="text-4xl lg:text-5xl font-display font-bold mb-4">
                See Aura in Action
              </h2>
              <p className="text-xl text-primary-100">
                Schedule a personalized demo and discover how Aura can transform your audit practice
              </p>
            </div>

            <div className="bg-white rounded-2xl shadow-2xl p-8 lg:p-12">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-semibold text-gray-900 mb-2">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none transition-all"
                      placeholder="John Smith"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-sm font-semibold text-gray-900 mb-2">
                      Work Email *
                    </label>
                    <input
                      type="email"
                      id="email"
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none transition-all"
                      placeholder="john@yourfirm.com"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="company" className="block text-sm font-semibold text-gray-900 mb-2">
                      Firm Name *
                    </label>
                    <input
                      type="text"
                      id="company"
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none transition-all"
                      placeholder="Smith & Associates CPA"
                      value={formData.company}
                      onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                    />
                  </div>
                  <div>
                    <label htmlFor="phone" className="block text-sm font-semibold text-gray-900 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      id="phone"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none transition-all"
                      placeholder="(555) 123-4567"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  className="w-full py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-xl hover:scale-105 transition-all flex items-center justify-center space-x-2"
                >
                  <span>Request Your Demo</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
                <p className="text-sm text-gray-600 text-center">
                  By submitting this form, you agree to receive communications from Aura Audit AI. We respect your privacy.
                </p>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 bg-white">
        <div className="section-container text-center">
          <h2 className="text-4xl lg:text-5xl font-display font-bold text-gray-900 mb-6">
            Ready to Transform Your <span className="gradient-text">Audit Practice?</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Join 500+ CPA firms already saving time and delivering better audits with Aura
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="#demo"
              className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-2xl hover:scale-105 transition-all inline-flex items-center justify-center space-x-2"
            >
              <span>Start Free Trial</span>
              <ArrowRight className="w-5 h-5" />
            </a>
            <a
              href="/contact"
              className="px-8 py-4 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-primary-600 hover:text-primary-600 transition-all"
            >
              Talk to Sales
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
