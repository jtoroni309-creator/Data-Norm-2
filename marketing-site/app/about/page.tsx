'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Brain, Target, Users, Award, TrendingUp, Heart } from 'lucide-react'

export default function About() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      {/* Hero Section */}
      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Building the Future of <span className="gradient-text">Audit Intelligence</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              We're on a mission to transform audit practices with AI-powered automation that empowers CPAs to deliver faster, more accurate, and more insightful audits.
            </p>
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
                Aura Audit AI was founded in 2022 by Jon Toroni, a visionary entrepreneur who recognized that the auditing profession was ripe for transformation. Having witnessed the inefficiencies and manual processes that plagued traditional audit firms, Jon assembled a world-class team of auditors, data scientists, and engineers to build a revolutionary AI-powered platform.
              </p>
              <p>
                Jon's vision was clear: leverage cutting-edge artificial intelligence and machine learning to automate the tedious, time-consuming aspects of auditing while empowering CPAs to focus on what matters most—professional judgment, client relationships, and strategic insights. Under his leadership, Aura has grown from a bold idea into the leading audit automation platform trusted by CPA firms nationwide.
              </p>
              <p>
                Today, Aura serves over 500 CPA firms across North America, processing millions of transactions and helping auditors deliver higher-quality work in dramatically less time. With Jon at the helm, we're not just improving audits—we're redefining what's possible in the profession. But we're just getting started on our mission to democratize world-class audit capabilities for every firm, regardless of size.
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

      {/* Team Section */}
      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-4">
              Meet Our Leadership Team
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experienced professionals from audit, technology, and AI
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                name: 'Jon Toroni',
                role: 'Founder & CEO',
                background: 'Visionary entrepreneur with deep expertise in AI, automation, and financial technology',
                initial: 'JT',
              },
              {
                name: 'Dr. Michael Chen',
                role: 'CTO & Co-Founder',
                background: 'PhD in Machine Learning, Ex-Google AI',
                initial: 'MC',
              },
              {
                name: 'Sarah Williams',
                role: 'Chief Product Officer',
                background: '15 years in audit technology',
                initial: 'SW',
              },
              {
                name: 'David Park',
                role: 'VP of Engineering',
                background: 'Ex-Microsoft, 10+ years in enterprise SaaS',
                initial: 'DP',
              },
            ].map((member, index) => (
              <div
                key={index}
                className="text-center group"
              >
                <div className="w-32 h-32 mx-auto mb-4 bg-gradient-to-br from-primary-600 to-accent-600 rounded-full flex items-center justify-center text-white text-3xl font-bold group-hover:scale-110 transition-transform">
                  {member.initial}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-1">{member.name}</h3>
                <p className="text-primary-600 font-medium mb-2">{member.role}</p>
                <p className="text-sm text-gray-600">{member.background}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-24 bg-gradient-to-r from-primary-600 to-accent-600">
        <div className="section-container">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center text-white">
            <div>
              <div className="text-5xl font-bold mb-2">500+</div>
              <div className="text-primary-100">CPA Firms</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">10K+</div>
              <div className="text-primary-100">Audits Completed</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">50M+</div>
              <div className="text-primary-100">Transactions Analyzed</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">98%</div>
              <div className="text-primary-100">Customer Satisfaction</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-white">
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
              className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-2xl hover:scale-105 transition-all"
            >
              Request a Demo
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
