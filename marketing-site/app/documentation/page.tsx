'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Book, Code, Zap, Users, ArrowRight, Search, FileText, Video } from 'lucide-react'

export default function Documentation() {
  const guides = [
    { title: 'Getting Started', description: 'Quick setup guide to get Aura running in minutes', icon: Zap, link: '#' },
    { title: 'Connecting Data Sources', description: 'How to integrate with QuickBooks, Xero, and more', icon: Code, link: '#' },
    { title: 'Running Your First Audit', description: 'Step-by-step guide to complete an audit', icon: FileText, link: '#' },
    { title: 'Team Collaboration', description: 'Invite team members and manage permissions', icon: Users, link: '#' },
    { title: 'API Documentation', description: 'Full API reference for developers', icon: Code, link: '/api' },
    { title: 'Video Tutorials', description: 'Watch how-to videos and webinars', icon: Video, link: '/webinars' },
  ]

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              <span className="gradient-text">Documentation</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed mb-8">
              Everything you need to get the most out of Aura Audit AI
            </p>
            <div className="relative max-w-2xl mx-auto">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search documentation..."
                className="w-full pl-12 pr-4 py-4 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              />
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {guides.map((guide, i) => (
              <a key={i} href={guide.link} className="group p-8 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-all cursor-pointer">
                <guide.icon className="w-10 h-10 text-primary-600 mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">{guide.title}</h3>
                <p className="text-gray-600 mb-4">{guide.description}</p>
                <div className="flex items-center text-primary-600 font-semibold">
                  <span>Read more</span>
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </a>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 bg-gradient-to-r from-primary-600 to-accent-600">
        <div className="section-container text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Need Help?</h2>
          <p className="text-white/80 mb-8">Our support team is available 24/7 to help you succeed</p>
          <a href="/support" className="px-8 py-4 bg-white text-primary-600 font-semibold rounded-lg hover:shadow-xl transition-all inline-flex items-center space-x-2">
            <span>Contact Support</span>
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>
      </section>

      <Footer />
    </main>
  )
}
