'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Briefcase, MapPin, Clock, DollarSign, Heart, Zap, Users, Rocket, ArrowRight, CheckCircle2 } from 'lucide-react'

export default function Careers() {
  const openPositions = [
    { title: 'Senior ML Engineer', department: 'Engineering', location: 'Remote', type: 'Full-time' },
    { title: 'Full Stack Developer', department: 'Engineering', location: 'San Francisco / Remote', type: 'Full-time' },
    { title: 'Product Manager - Audit', department: 'Product', location: 'Remote', type: 'Full-time' },
    { title: 'Customer Success Manager', department: 'Sales', location: 'New York / Remote', type: 'Full-time' },
    { title: 'Senior Data Scientist', department: 'AI/ML', location: 'Remote', type: 'Full-time' },
    { title: 'Enterprise Account Executive', department: 'Sales', location: 'Remote', type: 'Full-time' },
  ]

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-green-100 rounded-full mb-6">
              <Rocket className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-700">We're Hiring! Join Our Growing Team</span>
            </div>
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Build the Future of <span className="gradient-text">Audit Technology</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Join a team of passionate innovators transforming the $17B audit industry with AI. Remote-first, competitive pay, and meaningful work.
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white">
        <div className="section-container">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            {[
              { icon: Users, label: 'Team Size', value: '50+' },
              { icon: MapPin, label: 'Locations', value: 'Global Remote' },
              { icon: DollarSign, label: 'Funding', value: 'Series A' },
              { icon: Zap, label: 'Growth', value: '300% YoY' },
            ].map((stat, i) => (
              <div key={i} className="p-6 bg-gray-50 rounded-2xl">
                <stat.icon className="w-8 h-8 mx-auto mb-3 text-primary-600" />
                <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-24 bg-gradient-to-br from-gray-50 to-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-4">Why Join Aura?</h2>
            <p className="text-xl text-gray-600">Benefits that matter</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: DollarSign, title: 'Competitive Compensation', description: 'Top-tier salary, equity, and annual bonuses' },
              { icon: Heart, title: 'Health & Wellness', description: '100% covered health, dental, vision + mental health support' },
              { icon: MapPin, title: 'Remote First', description: 'Work from anywhere with flexible hours' },
              { icon: Rocket, title: 'Growth Opportunity', description: 'Fast-growing startup with clear career paths' },
              { icon: Users, title: 'Amazing Team', description: 'Work with ex-Google, Microsoft, Big 4 talent' },
              { icon: Zap, title: 'Latest Tech', description: 'GPT-4, cutting-edge ML, modern stack' },
            ].map((benefit, i) => (
              <div key={i} className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all">
                <benefit.icon className="w-10 h-10 text-primary-600 mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">{benefit.title}</h3>
                <p className="text-gray-600">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-4">Open Positions</h2>
            <p className="text-xl text-gray-600">{openPositions.length} roles available</p>
          </div>
          <div className="max-w-4xl mx-auto space-y-4">
            {openPositions.map((job, i) => (
              <div key={i} className="flex items-center justify-between p-6 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-colors cursor-pointer group">
                <div>
                  <h3 className="text-lg font-bold text-gray-900 group-hover:text-primary-600 transition-colors">{job.title}</h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                    <span className="flex items-center"><Briefcase className="w-4 h-4 mr-1" />{job.department}</span>
                    <span className="flex items-center"><MapPin className="w-4 h-4 mr-1" />{job.location}</span>
                    <span className="flex items-center"><Clock className="w-4 h-4 mr-1" />{job.type}</span>
                  </div>
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" />
              </div>
            ))}
          </div>
          <div className="text-center mt-12">
            <p className="text-gray-600 mb-4">Don't see your role? We're always looking for talented people.</p>
            <a href="/contact" className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-xl transition-all inline-flex items-center space-x-2">
              <span>Send Us Your Resume</span>
              <ArrowRight className="w-5 h-5" />
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
