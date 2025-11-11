'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Brain, Target, Users, Award, TrendingUp, Heart, Linkedin, Mail, Building2 } from 'lucide-react'

export default function About() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      {/* Hero Section */}
      <section className="pt-32 pb-16 bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/30 relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl animate-pulse delay-1000" />
        </div>

        <div className="section-container relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full mb-8 shadow-lg">
              <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse" />
              <span className="text-sm font-semibold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                Revolutionizing Audit Excellence Since 2022
              </span>
            </div>
            <h1 className="text-5xl lg:text-7xl font-display font-bold text-slate-900 mb-6 leading-tight">
              Building the Future of <span className="gradient-text">Audit Intelligence</span>
            </h1>
            <p className="text-xl lg:text-2xl text-slate-600 leading-relaxed max-w-3xl mx-auto">
              Founded by auditors who experienced the pain of manual work firsthand, we're on a mission to transform the audit profession with cutting-edge AI technology.
            </p>
          </div>
        </div>
      </section>

      {/* Founder Section - Featured */}
      <section className="py-32 bg-white relative overflow-hidden">
        <div className="section-container">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl lg:text-5xl font-display font-bold text-slate-900 mb-4">
                Meet Our <span className="gradient-text">Founder</span>
              </h2>
              <p className="text-xl text-slate-600">
                Visionary leadership driving innovation in audit technology
              </p>
            </div>

            <div className="relative">
              {/* Decorative Elements */}
              <div className="absolute -top-10 -left-10 w-40 h-40 bg-blue-500/10 rounded-full blur-3xl" />
              <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl" />

              <div className="relative bg-gradient-to-br from-white to-slate-50 rounded-3xl shadow-2xl border border-slate-200/50 overflow-hidden">
                <div className="grid lg:grid-cols-5 gap-8 lg:gap-12 p-8 lg:p-12">
                  {/* Photo Section */}
                  <div className="lg:col-span-2 flex flex-col items-center justify-center">
                    <div className="relative group">
                      {/* Glow Effect */}
                      <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl blur-2xl opacity-30 group-hover:opacity-50 transition-opacity" />

                      {/* Photo Container */}
                      <div className="relative w-64 h-64 lg:w-72 lg:h-72 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-3xl flex items-center justify-center shadow-2xl transform group-hover:scale-105 transition-transform duration-500">
                        <div className="text-white text-8xl font-bold">JT</div>
                      </div>
                    </div>

                    {/* Social Links */}
                    <div className="flex space-x-4 mt-8">
                      <a
                        href="https://linkedin.com/in/jontoroni"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-12 h-12 bg-blue-600 hover:bg-blue-700 rounded-xl flex items-center justify-center transition-all hover:scale-110 shadow-lg"
                        aria-label="LinkedIn"
                      >
                        <Linkedin className="w-6 h-6 text-white" />
                      </a>
                      <a
                        href="mailto:jon@toroniandcompany.com"
                        className="w-12 h-12 bg-slate-700 hover:bg-slate-800 rounded-xl flex items-center justify-center transition-all hover:scale-110 shadow-lg"
                        aria-label="Email"
                      >
                        <Mail className="w-6 h-6 text-white" />
                      </a>
                    </div>
                  </div>

                  {/* Bio Section */}
                  <div className="lg:col-span-3 flex flex-col justify-center">
                    <div className="mb-6">
                      <h3 className="text-4xl lg:text-5xl font-display font-bold text-slate-900 mb-3">
                        Jon Toroni
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 mb-6">
                        <span className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-full text-lg shadow-lg">
                          Founder & CEO
                        </span>
                        <span className="inline-flex items-center px-4 py-2 bg-slate-100 text-slate-700 font-medium rounded-full">
                          <Building2 className="w-4 h-4 mr-2" />
                          Toroni and Company
                        </span>
                      </div>
                    </div>

                    <div className="prose prose-lg max-w-none text-slate-700 space-y-4">
                      <p className="text-lg leading-relaxed">
                        <strong className="text-slate-900">Jon Toroni</strong> founded Aura Audit AI after spending over 15 years in the auditing profession, where he witnessed firsthand the inefficiencies plaguing traditional audit practices. His vision was clear: harness the power of artificial intelligence to eliminate tedious manual work and empower auditors to focus on what truly matters—professional judgment and client advisory.
                      </p>
                      <p className="text-lg leading-relaxed">
                        As <strong className="text-slate-900">Founder and CEO</strong>, Jon has assembled a world-class team of auditors, data scientists, and engineers to build the most advanced audit automation platform in the industry. Under his leadership, Aura has grown to serve over 500 CPA firms, processing millions of transactions and saving thousands of hours of manual work.
                      </p>
                      <p className="text-lg leading-relaxed">
                        Jon's unique blend of deep audit expertise and technological vision has positioned Aura as the go-to platform for firms seeking to modernize their audit practices. His commitment to innovation, quality, and customer success drives every aspect of Aura's development.
                      </p>

                      {/* Key Achievements */}
                      <div className="grid md:grid-cols-2 gap-4 pt-6 not-prose">
                        <div className="flex items-start space-x-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <Award className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <div className="font-semibold text-slate-900">15+ Years</div>
                            <div className="text-sm text-slate-600">Audit Experience</div>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <Users className="w-5 h-5 text-purple-600" />
                          </div>
                          <div>
                            <div className="font-semibold text-slate-900">500+ Firms</div>
                            <div className="text-sm text-slate-600">Trusting Aura</div>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <Brain className="w-5 h-5 text-green-600" />
                          </div>
                          <div>
                            <div className="font-semibold text-slate-900">AI Innovation</div>
                            <div className="text-sm text-slate-600">Industry Leader</div>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <TrendingUp className="w-5 h-5 text-orange-600" />
                          </div>
                          <div>
                            <div className="font-semibold text-slate-900">50M+</div>
                            <div className="text-sm text-slate-600">Transactions Analyzed</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Story */}
      <section className="py-24 bg-gradient-to-br from-slate-50 to-white">
        <div className="section-container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-slate-900 mb-12 text-center">
              Our <span className="gradient-text">Story</span>
            </h2>
            <div className="prose prose-lg max-w-none text-slate-700 space-y-6">
              <p className="text-xl leading-relaxed">
                Aura Audit AI was born from frustration—the kind that comes from spending countless hours on repetitive tasks that could be automated. Our founder, <strong>Jon Toroni</strong>, experienced this firsthand during his years as an auditor, manually mapping accounts, testing transactions one by one, and drafting disclosure notes late into the night.
              </p>
              <p className="text-xl leading-relaxed">
                In 2022, Jon assembled a world-class team to build the audit platform he always wished he had. Our goal was revolutionary yet simple: leverage cutting-edge AI and machine learning to automate the tedious, time-consuming parts of auditing while keeping auditors firmly in control of professional judgment.
              </p>
              <p className="text-xl leading-relaxed">
                Today, Aura serves over <strong>500 CPA firms</strong> across North America, processing <strong>millions of transactions monthly</strong> and helping auditors deliver higher-quality work in <strong>30-50% less time</strong>. We've caught fraud schemes that would have slipped through manual processes, identified material misstatements with unprecedented accuracy, and given auditors their nights and weekends back.
              </p>
              <p className="text-xl leading-relaxed font-semibold text-slate-900">
                But we're just getting started. The future of audit is intelligent, automated, and here.
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
                name: 'Jennifer Thompson',
                role: 'CEO & Co-Founder',
                background: 'Former Big 4 Partner, 20 years in audit',
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
