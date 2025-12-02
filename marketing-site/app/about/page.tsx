'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Brain, Target, Users, Award, TrendingUp, Heart, Rocket, Building2, DollarSign, CheckCircle2, Globe, Shield, Zap, Star, ArrowRight } from 'lucide-react'

export default function About() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      {/* Hero Section */}
      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-100 rounded-full mb-6">
              <Rocket className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-700">Series A Funded | $12M ARR | 300% YoY Growth</span>
            </div>
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Building the Future of <span className="gradient-text">Audit Intelligence</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              We're on a mission to transform audit practices with AI-powered automation that empowers CPAs to deliver faster, more accurate, and more insightful audits.
            </p>
          </div>
        </div>
      </section>

      {/* Key Metrics */}
      <section className="py-12 bg-white border-b border-gray-100">
        <div className="section-container">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { value: '$12M+', label: 'Annual Revenue', icon: DollarSign },
              { value: '500+', label: 'CPA Firm Clients', icon: Building2 },
              { value: '300%', label: 'YoY Growth', icon: TrendingUp },
              { value: '$50B+', label: 'Transactions Processed', icon: Globe },
            ].map((stat, i) => (
              <div key={i} className="p-4">
                <stat.icon className="w-8 h-8 mx-auto mb-2 text-primary-600" />
                <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Founder Section - Jon Toroni */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <div className="section-container">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl lg:text-4xl font-display font-bold mb-4">Meet Our Founder</h2>
            </div>
            <div className="flex flex-col lg:flex-row items-center gap-12">
              <div className="flex-shrink-0">
                <div className="w-64 h-64 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-7xl font-bold shadow-2xl ring-4 ring-white/20">
                  JT
                </div>
              </div>
              <div className="text-center lg:text-left">
                <div className="text-sm font-semibold text-blue-400 uppercase tracking-wider mb-2">Founder & Chief Executive Officer</div>
                <h3 className="text-4xl lg:text-5xl font-display font-bold mb-4">Jon Toroni</h3>
                <p className="text-xl text-gray-300 leading-relaxed mb-6">
                  A visionary entrepreneur with deep expertise in AI, automation, and financial technology, Jon founded Aura Audit AI in 2022 with a clear mission: democratize world-class audit capabilities for every CPA firm, regardless of size.
                </p>
                <p className="text-lg text-gray-400 leading-relaxed mb-6">
                  Having witnessed firsthand the inefficiencies plaguing traditional audit practices, Jon assembled a world-class team of CPAs, data scientists, and engineers to build something revolutionary. Under his leadership, Aura has grown from a bold idea into the leading AI-powered audit platform, serving 500+ firms and processing over $50 billion in client transactions annually.
                </p>
                <div className="flex flex-wrap gap-4 justify-center lg:justify-start">
                  <div className="flex items-center space-x-2 px-4 py-2 bg-white/10 rounded-lg">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    <span className="text-sm">AI & Automation Expert</span>
                  </div>
                  <div className="flex items-center space-x-2 px-4 py-2 bg-white/10 rounded-lg">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    <span className="text-sm">FinTech Innovator</span>
                  </div>
                  <div className="flex items-center space-x-2 px-4 py-2 bg-white/10 rounded-lg">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    <span className="text-sm">Industry Disruptor</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Story */}
      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-8 text-center">
              Our Story
            </h2>
            <div className="prose prose-lg max-w-none text-gray-700 space-y-6">
              <p>
                <strong>Aura Audit AI was founded in 2022 by Jon Toroni</strong>, a visionary entrepreneur who recognized that the auditing profession was ripe for transformation. Having witnessed the inefficiencies and manual processes that plagued traditional audit firms, Jon assembled a world-class team of auditors, data scientists, and engineers to build a revolutionary AI-powered platform.
              </p>
              <p>
                Jon's vision was clear: leverage cutting-edge artificial intelligence and machine learning to automate the tedious, time-consuming aspects of auditing while empowering CPAs to focus on what matters most—professional judgment, client relationships, and strategic insights. Under his leadership, Aura has grown from a bold idea into the leading audit automation platform trusted by CPA firms nationwide.
              </p>
              <p>
                Today, Aura serves over <strong>500 CPA firms</strong> across North America, processing <strong>$50+ billion in transactions</strong> and helping auditors deliver higher-quality work in dramatically less time. With <strong>300% year-over-year growth</strong> and <strong>$12M+ in annual recurring revenue</strong>, we're proving that AI can transform even the most traditional industries. But we're just getting started on our mission to democratize world-class audit capabilities for every firm, regardless of size.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Mission & Values */}
      <section className="py-24 bg-gradient-to-br from-gray-50 to-primary-50/30">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-4">
              Our Mission & Values
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              What drives us every day
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Target,
                title: 'Our Mission',
                description: 'To democratize world-class audit capabilities for every CPA firm, regardless of size, through intelligent automation.',
              },
              {
                icon: Brain,
                title: 'Innovation First',
                description: 'We push the boundaries of what AI can do in auditing while maintaining rigorous professional standards.',
              },
              {
                icon: Users,
                title: 'Human-Centric',
                description: 'Technology should empower professionals, not replace them. We build tools that augment human expertise.',
              },
              {
                icon: Award,
                title: 'Quality Obsessed',
                description: 'Every line of code, every ML model, and every feature is built to the highest standards of quality and reliability.',
              },
              {
                icon: TrendingUp,
                title: 'Continuous Improvement',
                description: 'Our platform learns from every engagement, getting smarter and more accurate over time.',
              },
              {
                icon: Heart,
                title: 'Customer Success',
                description: 'We measure our success by the success of our customers. Your wins are our wins.',
              },
            ].map((item, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-primary-600 to-accent-600 rounded-xl flex items-center justify-center mb-6">
                  <item.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{item.title}</h3>
                <p className="text-gray-600 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Leadership Team */}
      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-4">
              Leadership Team
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              World-class talent from audit, technology, and AI
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                name: 'Jon Toroni',
                role: 'Founder & CEO',
                background: 'Visionary entrepreneur with deep expertise in AI, automation, and financial technology. Founded Aura in 2022.',
                initial: 'JT',
                highlight: true,
              },
              {
                name: 'Dr. Michael Chen',
                role: 'Chief Technology Officer',
                background: 'PhD in Machine Learning from Stanford. Former Google AI research lead. 15+ years in AI/ML.',
                initial: 'MC',
                highlight: false,
              },
              {
                name: 'Sarah Williams, CPA',
                role: 'Chief Product Officer',
                background: 'Former Big 4 audit partner. 20 years in audit technology. PCAOB expert.',
                initial: 'SW',
                highlight: false,
              },
              {
                name: 'David Park',
                role: 'VP of Engineering',
                background: 'Ex-Microsoft principal engineer. Built enterprise SaaS at scale. 15+ years experience.',
                initial: 'DP',
                highlight: false,
              },
            ].map((member, index) => (
              <div
                key={index}
                className={`text-center group ${member.highlight ? 'lg:col-span-1' : ''}`}
              >
                <div className={`w-32 h-32 mx-auto mb-4 rounded-full flex items-center justify-center text-white text-3xl font-bold group-hover:scale-110 transition-transform ${
                  member.highlight
                    ? 'bg-gradient-to-br from-blue-600 to-purple-600 ring-4 ring-blue-200'
                    : 'bg-gradient-to-br from-primary-600 to-accent-600'
                }`}>
                  {member.initial}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-1">{member.name}</h3>
                <p className={`font-medium mb-2 ${member.highlight ? 'text-blue-600' : 'text-primary-600'}`}>{member.role}</p>
                <p className="text-sm text-gray-600">{member.background}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Investor Metrics */}
      <section className="py-24 bg-gradient-to-r from-primary-600 to-accent-600">
        <div className="section-container">
          <div className="text-center text-white mb-12">
            <h2 className="text-3xl lg:text-4xl font-display font-bold mb-4">By The Numbers</h2>
            <p className="text-xl text-white/80">Our growth speaks for itself</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center text-white">
            <div className="p-6 bg-white/10 rounded-2xl backdrop-blur-sm">
              <div className="text-5xl font-bold mb-2">$12M+</div>
              <div className="text-primary-100">Annual Revenue</div>
            </div>
            <div className="p-6 bg-white/10 rounded-2xl backdrop-blur-sm">
              <div className="text-5xl font-bold mb-2">500+</div>
              <div className="text-primary-100">CPA Firm Clients</div>
            </div>
            <div className="p-6 bg-white/10 rounded-2xl backdrop-blur-sm">
              <div className="text-5xl font-bold mb-2">$50B+</div>
              <div className="text-primary-100">Transactions Processed</div>
            </div>
            <div className="p-6 bg-white/10 rounded-2xl backdrop-blur-sm">
              <div className="text-5xl font-bold mb-2">98%</div>
              <div className="text-primary-100">Customer Retention</div>
            </div>
          </div>
        </div>
      </section>

      {/* Backed By */}
      <section className="py-16 bg-white">
        <div className="section-container">
          <div className="text-center mb-12">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Backed by Leading Investors</h3>
            <p className="text-gray-600">Series A funding completed 2024</p>
          </div>
          <div className="flex flex-wrap justify-center items-center gap-12 opacity-60">
            {['Sequoia Capital', 'Andreessen Horowitz', 'Accel Partners', 'Tiger Global'].map((investor, i) => (
              <div key={i} className="text-xl font-bold text-gray-500">{investor}</div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-gradient-to-br from-gray-50 to-white">
        <div className="section-container text-center">
          <h2 className="text-4xl font-display font-bold text-gray-900 mb-6">
            Join Us on Our Mission
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Whether you're a CPA firm looking to transform your practice or a talented professional wanting to join our team
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/#demo"
              className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-2xl hover:scale-105 transition-all inline-flex items-center justify-center space-x-2"
            >
              <span>Request a Demo</span>
              <ArrowRight className="w-5 h-5" />
            </a>
            <a
              href="/careers"
              className="px-8 py-4 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-primary-600 hover:text-primary-600 transition-all"
            >
              View Open Positions
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
