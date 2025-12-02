'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Database, ArrowRight, CheckCircle2, Zap } from 'lucide-react'

export default function Integrations() {
  const integrations = [
    { name: 'QuickBooks Online', category: 'Accounting', status: 'Available' },
    { name: 'QuickBooks Desktop', category: 'Accounting', status: 'Available' },
    { name: 'Xero', category: 'Accounting', status: 'Available' },
    { name: 'Sage Intacct', category: 'Accounting', status: 'Available' },
    { name: 'NetSuite', category: 'ERP', status: 'Available' },
    { name: 'SAP', category: 'ERP', status: 'Available' },
    { name: 'Microsoft Dynamics', category: 'ERP', status: 'Available' },
    { name: 'FreshBooks', category: 'Accounting', status: 'Available' },
    { name: 'Wave', category: 'Accounting', status: 'Available' },
    { name: 'Zoho Books', category: 'Accounting', status: 'Available' },
    { name: 'ADP', category: 'Payroll', status: 'Available' },
    { name: 'Gusto', category: 'Payroll', status: 'Available' },
    { name: 'Paychex', category: 'Payroll', status: 'Available' },
    { name: 'Bill.com', category: 'AP/AR', status: 'Available' },
    { name: 'Stripe', category: 'Payments', status: 'Available' },
    { name: 'Square', category: 'POS', status: 'Available' },
  ]

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-100 rounded-full mb-6">
              <Database className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-700">50+ Native Integrations</span>
            </div>
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Connect to <span className="gradient-text">Any System</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Aura integrates with all major accounting platforms, ERPs, and financial systems. One-click connection, automatic data sync.
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white">
        <div className="section-container">
          <div className="grid md:grid-cols-3 gap-8 text-center mb-16">
            {[
              { value: '50+', label: 'Native Integrations' },
              { value: '99.9%', label: 'Uptime SLA' },
              { value: '<5 min', label: 'Setup Time' },
            ].map((stat, i) => (
              <div key={i} className="p-6 bg-gray-50 rounded-2xl">
                <div className="text-4xl font-bold gradient-text mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>

          <div className="grid md:grid-cols-4 gap-4">
            {integrations.map((integration, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                <div>
                  <div className="font-semibold text-gray-900">{integration.name}</div>
                  <div className="text-sm text-gray-500">{integration.category}</div>
                </div>
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              </div>
            ))}
          </div>

          <div className="text-center mt-16">
            <p className="text-gray-600 mb-6">Don't see your system? We support custom integrations via our API.</p>
            <a href="/contact" className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-xl transition-all inline-flex items-center space-x-2">
              <span>Request an Integration</span>
              <ArrowRight className="w-5 h-5" />
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
