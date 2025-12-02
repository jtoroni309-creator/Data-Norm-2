'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { MessageCircle, Mail, Phone, Book, Video, Clock, ArrowRight } from 'lucide-react'

export default function Support() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              How Can We <span className="gradient-text">Help?</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Our dedicated support team is here to ensure your success with Aura
            </p>
          </div>
        </div>
      </section>

      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {[
              { icon: MessageCircle, title: 'Live Chat', description: 'Get instant help from our team', availability: 'Available 24/7', action: 'Start Chat' },
              { icon: Mail, title: 'Email Support', description: 'Send us a detailed message', availability: 'Response within 4 hours', action: 'Send Email' },
              { icon: Phone, title: 'Phone Support', description: 'Talk to a specialist', availability: 'Mon-Fri, 9am-6pm ET', action: 'Call Now' },
            ].map((item, i) => (
              <div key={i} className="text-center p-8 bg-gray-50 rounded-2xl hover:shadow-lg transition-all">
                <item.icon className="w-12 h-12 mx-auto mb-4 text-primary-600" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600 mb-2">{item.description}</p>
                <p className="text-sm text-primary-600 font-medium mb-4">{item.availability}</p>
                <button className="px-6 py-2 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all">
                  {item.action}
                </button>
              </div>
            ))}
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="p-8 bg-gray-50 rounded-2xl">
              <Book className="w-10 h-10 text-primary-600 mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-2">Knowledge Base</h3>
              <p className="text-gray-600 mb-4">Browse our comprehensive documentation and guides</p>
              <a href="/documentation" className="text-primary-600 font-semibold inline-flex items-center">
                View Documentation <ArrowRight className="w-4 h-4 ml-2" />
              </a>
            </div>
            <div className="p-8 bg-gray-50 rounded-2xl">
              <Video className="w-10 h-10 text-primary-600 mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-2">Video Tutorials</h3>
              <p className="text-gray-600 mb-4">Watch step-by-step guides and training videos</p>
              <a href="/webinars" className="text-primary-600 font-semibold inline-flex items-center">
                Watch Videos <ArrowRight className="w-4 h-4 ml-2" />
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-gradient-to-r from-primary-600 to-accent-600">
        <div className="section-container text-center text-white">
          <Clock className="w-16 h-16 mx-auto mb-6" />
          <h2 className="text-3xl font-bold mb-4">Enterprise Support</h2>
          <p className="text-white/80 mb-8 max-w-2xl mx-auto">
            Enterprise customers get dedicated account managers, priority support, and 99.9% uptime SLA
          </p>
          <a href="/contact" className="px-8 py-4 bg-white text-primary-600 font-semibold rounded-lg hover:shadow-xl transition-all inline-flex items-center space-x-2">
            <span>Contact Sales</span>
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>
      </section>

      <Footer />
    </main>
  )
}
