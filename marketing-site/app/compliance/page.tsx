'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Shield, Lock, Award, Globe, CheckCircle2, FileText, Server, Eye } from 'lucide-react'

export default function Compliance() {
  const certifications = [
    { icon: Award, title: 'SOC 2 Type II', description: 'Independently audited security controls', status: 'Certified' },
    { icon: Shield, title: 'PCAOB Compliant', description: 'Full audit trail and retention requirements', status: 'Compliant' },
    { icon: Lock, title: 'AES-256 Encryption', description: 'Data encrypted at rest and in transit', status: 'Implemented' },
    { icon: Globe, title: 'GDPR', description: 'EU data protection compliance', status: 'Compliant' },
    { icon: FileText, title: 'CCPA', description: 'California consumer privacy compliance', status: 'Compliant' },
    { icon: Server, title: 'HIPAA Ready', description: 'Healthcare data handling capabilities', status: 'Available' },
  ]

  const securityFeatures = [
    'End-to-end encryption for all data',
    'Multi-factor authentication required',
    'Role-based access controls',
    'Immutable audit logs',
    '7-year data retention',
    'Regular penetration testing',
    'SOC 2 Type II certified',
    '99.9% uptime SLA',
    'Disaster recovery in place',
    'PCAOB-compliant workpapers',
  ]

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-green-100 rounded-full mb-6">
              <Shield className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-700">Enterprise-Grade Security</span>
            </div>
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Security & <span className="gradient-text">Compliance</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Trusted by firms that audit Fortune 500 companies
            </p>
          </div>
        </div>
      </section>

      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Certifications & Compliance</h2>
            <p className="text-gray-600">Industry-leading security standards</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {certifications.map((cert, i) => (
              <div key={i} className="p-8 bg-gray-50 rounded-2xl hover:shadow-lg transition-all">
                <div className="flex items-start justify-between mb-4">
                  <cert.icon className="w-10 h-10 text-primary-600" />
                  <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">{cert.status}</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{cert.title}</h3>
                <p className="text-gray-600">{cert.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-24 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
        <div className="section-container">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">Security Built Into Everything</h2>
              <p className="text-gray-300 mb-8">
                From day one, we've built Aura with security as a core requirement—not an afterthought.
                Our platform is designed to meet the most stringent requirements of financial services firms.
              </p>
              <div className="grid grid-cols-2 gap-4">
                {securityFeatures.map((feature, i) => (
                  <div key={i} className="flex items-center space-x-2">
                    <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
                    <span className="text-sm text-gray-300">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8">
              <Eye className="w-12 h-12 text-primary-400 mb-6" />
              <h3 className="text-2xl font-bold mb-4">Request Security Documentation</h3>
              <p className="text-gray-300 mb-6">
                Get access to our SOC 2 report, penetration test results, and security questionnaire responses.
              </p>
              <a href="/contact" className="px-6 py-3 bg-white text-gray-900 font-semibold rounded-lg hover:shadow-lg transition-all inline-block">
                Contact Security Team
              </a>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
