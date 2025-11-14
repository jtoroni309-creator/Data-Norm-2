'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Shield, Lock, Eye, FileCheck, Server, Award, CheckCircle2, AlertTriangle } from 'lucide-react'

export default function SecurityCompliance() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      {/* Hero Section */}
      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-600 to-accent-600 rounded-2xl mb-6">
              <Shield className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Enterprise-Grade <span className="gradient-text">Security & Compliance</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed max-w-3xl mx-auto">
              Aura Audit AI is built on a foundation of security, privacy, and compliance. We protect your sensitive audit data with industry-leading security measures and maintain certifications required for CPA firms.
            </p>
          </div>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="py-16 bg-white border-b border-gray-200">
        <div className="section-container">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { label: 'SOC 2 Type II', sublabel: 'Certified', icon: Award },
              { label: 'GDPR', sublabel: 'Compliant', icon: Shield },
              { label: 'AES-256', sublabel: 'Encryption', icon: Lock },
              { label: '99.9%', sublabel: 'Uptime SLA', icon: Server },
            ].map((badge, idx) => (
              <div key={idx} className="flex flex-col items-center">
                <div className="w-16 h-16 bg-gradient-to-br from-primary-100 to-accent-100 rounded-xl flex items-center justify-center mb-3">
                  <badge.icon className="w-8 h-8 text-primary-600" />
                </div>
                <div className="text-2xl font-bold text-gray-900">{badge.label}</div>
                <div className="text-sm text-gray-600">{badge.sublabel}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Measures */}
      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-4">
              Comprehensive Security Measures
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Multi-layered security architecture protecting your data at every level
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Lock,
                title: 'Encryption at Rest & In Transit',
                points: [
                  'AES-256 encryption for all stored data',
                  'TLS 1.3 for all data transmissions',
                  'Encrypted database backups',
                  'Hardware security modules (HSM) for key management',
                ],
              },
              {
                icon: Eye,
                title: 'Access Control',
                points: [
                  'Multi-factor authentication (MFA) required',
                  'Role-based access control (RBAC)',
                  'Row-level security for data isolation',
                  'Automatic session timeout (8 hours)',
                ],
              },
              {
                icon: FileCheck,
                title: 'Audit Logging',
                points: [
                  'Immutable audit trails for all activities',
                  '7-year log retention (PCAOB compliant)',
                  'Real-time alerting for suspicious activity',
                  'Comprehensive access monitoring',
                ],
              },
              {
                icon: Server,
                title: 'Infrastructure Security',
                points: [
                  'SOC 2 Type II certified data centers',
                  '24/7 security monitoring and intrusion detection',
                  'DDoS protection and rate limiting',
                  'Regular penetration testing',
                ],
              },
              {
                icon: Shield,
                title: 'Application Security',
                points: [
                  'Secure software development lifecycle (SSDLC)',
                  'Automated vulnerability scanning',
                  'Regular code reviews and security audits',
                  'Bug bounty program',
                ],
              },
              {
                icon: AlertTriangle,
                title: 'Incident Response',
                points: [
                  'Dedicated security incident response team',
                  '72-hour breach notification (GDPR compliant)',
                  'Business continuity and disaster recovery plans',
                  'Annual DR testing and validation',
                ],
              },
            ].map((measure, idx) => (
              <div
                key={idx}
                className="bg-white border border-gray-200 rounded-2xl p-8 hover:shadow-xl transition-all"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-primary-600 to-accent-600 rounded-xl flex items-center justify-center mb-6">
                  <measure.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">{measure.title}</h3>
                <ul className="space-y-3">
                  {measure.points.map((point, pidx) => (
                    <li key={pidx} className="flex items-start gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Compliance Certifications */}
      <section className="py-24 bg-gradient-to-br from-gray-50 to-primary-50/30">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-4">
              Compliance & Certifications
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Meeting the highest standards for audit platforms
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {[
              {
                title: 'SOC 2 Type II',
                description: 'Annual SOC 2 Type II audits covering Security, Availability, and Confidentiality trust service criteria',
                compliance: [
                  'Security controls and monitoring',
                  'Availability and uptime guarantees',
                  'Confidentiality of client data',
                  'Independent third-party audit',
                ],
              },
              {
                title: 'GDPR Compliance',
                description: 'Full compliance with EU General Data Protection Regulation for data privacy and protection',
                compliance: [
                  'Standard Contractual Clauses (SCCs)',
                  'Data Processing Agreements (DPAs)',
                  'Data Subject Rights support',
                  'Privacy by Design and Default',
                ],
              },
              {
                title: 'PCAOB Standards',
                description: 'Designed to meet Public Company Accounting Oversight Board requirements for audit documentation',
                compliance: [
                  '7-year audit documentation retention',
                  'WORM (Write Once Read Many) storage',
                  'Immutable audit trails',
                  'Complete documentation controls',
                ],
              },
              {
                title: 'AICPA Guidelines',
                description: 'Adherence to American Institute of CPAs standards for audit quality and professional standards',
                compliance: [
                  'SAS 142: Audit Evidence',
                  'SAS 145: Risk Assessment',
                  'Quality control frameworks',
                  'Professional standards compliance',
                ],
              },
            ].map((cert, idx) => (
              <div
                key={idx}
                className="bg-white rounded-2xl p-8 shadow-lg"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-accent-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Award className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{cert.title}</h3>
                    <p className="text-gray-600 text-sm">{cert.description}</p>
                  </div>
                </div>
                <ul className="space-y-3 mt-6">
                  {cert.compliance.map((item, iidx) => (
                    <li key={iidx} className="flex items-start gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Data Protection */}
      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-4">
                Your Data, Your Control
              </h2>
              <p className="text-xl text-gray-600">
                Complete transparency and control over your audit data
              </p>
            </div>

            <div className="space-y-6">
              {[
                {
                  title: 'Data Ownership',
                  description: 'You retain full ownership of all data uploaded to the platform. Your data is never used for training or shared with third parties without explicit consent.',
                },
                {
                  title: 'Data Residency',
                  description: 'Choose where your data is stored with options for US, EU, or other regions. Data residency compliance for regulatory requirements.',
                },
                {
                  title: 'Data Portability',
                  description: 'Export your data at any time in multiple formats (JSON, CSV, PDF). No vendor lock-in—your data is always accessible.',
                },
                {
                  title: 'Data Deletion',
                  description: 'Request deletion of your data at any time. We follow secure deletion procedures and provide certification upon request.',
                },
                {
                  title: 'Data Retention',
                  description: '7-year audit documentation retention (PCAOB/SEC compliant). Automated retention policies with secure archival and deletion.',
                },
                {
                  title: 'Data Isolation',
                  description: 'Multi-tenant architecture with strict data isolation. Your data is logically and cryptographically separated from other customers.',
                },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="bg-gray-50 border border-gray-200 rounded-xl p-6 hover:border-primary-300 transition-colors"
                >
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{item.title}</h3>
                  <p className="text-gray-700">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Security Resources */}
      <section className="py-24 bg-gradient-to-br from-gray-50 to-primary-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-4">
                Security Resources
              </h2>
              <p className="text-xl text-gray-600">
                Documentation and reports for your security review
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  title: 'SOC 2 Report',
                  description: 'Request our latest SOC 2 Type II audit report',
                  action: 'Request Report',
                  href: 'mailto:security@auraaudit.ai?subject=SOC 2 Report Request',
                },
                {
                  title: 'Security Whitepaper',
                  description: 'Detailed technical security architecture documentation',
                  action: 'Download PDF',
                  href: '#',
                },
                {
                  title: 'Penetration Test Results',
                  description: 'Summary of latest third-party security assessment',
                  action: 'Request Access',
                  href: 'mailto:security@auraaudit.ai?subject=Pen Test Results Request',
                },
              ].map((resource, idx) => (
                <div
                  key={idx}
                  className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{resource.title}</h3>
                  <p className="text-sm text-gray-600 mb-4">{resource.description}</p>
                  <a
                    href={resource.href}
                    className="inline-block px-4 py-2 bg-gradient-to-r from-primary-600 to-accent-600 text-white text-sm font-semibold rounded-lg hover:shadow-lg transition-all"
                  >
                    {resource.action}
                  </a>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Contact Security Team */}
      <section className="py-24 bg-white">
        <div className="section-container text-center">
          <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-6">
            Have Security Questions?
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Our security team is here to answer your questions and provide additional documentation
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="mailto:security@auraaudit.ai"
              className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-2xl hover:scale-105 transition-all"
            >
              Contact Security Team
            </a>
            <a
              href="/dpa"
              className="px-8 py-4 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-primary-600 hover:text-primary-600 transition-all"
            >
              View Data Processing Agreement
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
