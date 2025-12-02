'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Code, Lock, Zap, Database, ArrowRight, CheckCircle2 } from 'lucide-react'

export default function ApiPage() {
  const endpoints = [
    { method: 'GET', path: '/api/v1/studies', description: 'List all audit studies' },
    { method: 'POST', path: '/api/v1/studies', description: 'Create a new audit study' },
    { method: 'GET', path: '/api/v1/studies/{id}', description: 'Get study details' },
    { method: 'POST', path: '/api/v1/studies/{id}/analyze', description: 'Run AI analysis' },
    { method: 'GET', path: '/api/v1/transactions', description: 'List transactions' },
    { method: 'POST', path: '/api/v1/transactions/import', description: 'Import transactions' },
    { method: 'GET', path: '/api/v1/reports', description: 'List generated reports' },
    { method: 'POST', path: '/api/v1/reports/generate', description: 'Generate a new report' },
  ]

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-white/10 rounded-full mb-6">
              <Code className="w-4 h-4" />
              <span className="text-sm font-medium">REST API v1</span>
            </div>
            <h1 className="text-5xl lg:text-6xl font-display font-bold mb-6">
              API <span className="gradient-text">Reference</span>
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed">
              Build powerful integrations with our comprehensive REST API
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white">
        <div className="section-container">
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {[
              { icon: Zap, title: 'RESTful', description: 'Standard REST API with JSON responses' },
              { icon: Lock, title: 'Secure', description: 'OAuth 2.0 authentication with API keys' },
              { icon: Database, title: 'Comprehensive', description: 'Full access to all platform features' },
            ].map((item, i) => (
              <div key={i} className="text-center p-6">
                <item.icon className="w-12 h-12 mx-auto mb-4 text-primary-600" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>

          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-8">Available Endpoints</h2>
            <div className="space-y-4">
              {endpoints.map((endpoint, i) => (
                <div key={i} className="flex items-center p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                  <span className={`px-3 py-1 text-xs font-bold rounded mr-4 ${
                    endpoint.method === 'GET' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                  }`}>
                    {endpoint.method}
                  </span>
                  <code className="font-mono text-sm text-gray-700 flex-1">{endpoint.path}</code>
                  <span className="text-sm text-gray-500">{endpoint.description}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="text-center mt-16">
            <a href="/contact" className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-xl transition-all inline-flex items-center space-x-2">
              <span>Request API Access</span>
              <ArrowRight className="w-5 h-5" />
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
