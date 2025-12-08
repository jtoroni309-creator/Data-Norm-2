'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import Link from 'next/link'
import {
  Shield,
  Lock,
  Eye,
  Trash2,
  Download,
  Bell,
  Globe,
  Server,
  FileCheck,
  Users,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Mail,
  Building2
} from 'lucide-react'

export default function GDPRPage() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl mb-6">
              <Shield className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              GDPR <span className="gradient-text">Compliance</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Our commitment to protecting your data rights under the General Data Protection Regulation
            </p>
            <p className="text-sm text-gray-500 mt-4">
              Last updated: December 7, 2024
            </p>
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="section-container">
          <div className="max-w-4xl mx-auto">
            {/* Key Rights Overview */}
            <div className="grid md:grid-cols-4 gap-4 mb-16">
              {[
                { icon: Eye, label: 'Right to Access', description: 'View your data' },
                { icon: FileCheck, label: 'Right to Rectify', description: 'Correct inaccuracies' },
                { icon: Trash2, label: 'Right to Erasure', description: 'Delete your data' },
                { icon: Download, label: 'Right to Portability', description: 'Export your data' },
              ].map((item, idx) => (
                <div key={idx} className="text-center glassmorphism rounded-2xl p-4">
                  <item.icon className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                  <div className="font-semibold text-slate-900 text-sm">{item.label}</div>
                  <div className="text-xs text-slate-500">{item.description}</div>
                </div>
              ))}
            </div>

            {/* Content */}
            <div className="prose prose-lg max-w-none">
              <h2 className="text-2xl font-bold text-slate-900 mb-4">1. Introduction</h2>
              <p className="text-slate-600 mb-6">
                Aura Audit AI, LLC ("Aura," "we," "us," or "our") is committed to protecting the privacy
                and security of personal data in accordance with the General Data Protection Regulation
                (GDPR) (EU) 2016/679. This document outlines our compliance measures and your rights as
                a data subject when using our AI-powered audit automation platform.
              </p>
              <p className="text-slate-600 mb-6">
                As a data processor for CPA firms and their clients, we implement stringent technical
                and organizational measures to ensure GDPR compliance throughout our services.
              </p>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">2. Our Role Under GDPR</h2>
              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <div className="bg-blue-50 rounded-xl p-6">
                  <div className="flex items-center mb-3">
                    <Building2 className="w-6 h-6 text-blue-600 mr-3" />
                    <h4 className="font-semibold text-slate-900">Data Controller</h4>
                  </div>
                  <p className="text-sm text-slate-600">
                    For our direct customers (CPA firms), we act as a Data Controller for account
                    information, billing data, and usage analytics.
                  </p>
                </div>
                <div className="bg-purple-50 rounded-xl p-6">
                  <div className="flex items-center mb-3">
                    <Server className="w-6 h-6 text-purple-600 mr-3" />
                    <h4 className="font-semibold text-slate-900">Data Processor</h4>
                  </div>
                  <p className="text-sm text-slate-600">
                    For audit engagement data uploaded by CPA firms on behalf of their clients,
                    we act as a Data Processor under instructions from the Controller.
                  </p>
                </div>
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">3. Lawful Basis for Processing</h2>
              <p className="text-slate-600 mb-4">
                We process personal data under the following lawful bases as defined in Article 6 of GDPR:
              </p>
              <div className="space-y-3 mb-6">
                {[
                  { basis: 'Contractual Necessity', description: 'Processing necessary to perform our services under your subscription agreement' },
                  { basis: 'Legitimate Interests', description: 'Processing for fraud prevention, security, and service improvement' },
                  { basis: 'Legal Obligation', description: 'Processing required to comply with PCAOB, SEC, and tax regulations' },
                  { basis: 'Consent', description: 'Marketing communications and optional analytics (where applicable)' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start space-x-3 bg-slate-50 rounded-xl p-4">
                    <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="font-semibold text-slate-900">{item.basis}:</span>
                      <span className="text-slate-600 ml-1">{item.description}</span>
                    </div>
                  </div>
                ))}
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">4. Your Data Subject Rights</h2>
              <p className="text-slate-600 mb-4">
                Under GDPR, you have the following rights regarding your personal data:
              </p>

              <div className="space-y-4 mb-6">
                {[
                  {
                    icon: Eye,
                    title: 'Right of Access (Article 15)',
                    description: 'You have the right to obtain confirmation of whether we process your personal data and, if so, access to that data along with information about the processing.'
                  },
                  {
                    icon: FileCheck,
                    title: 'Right to Rectification (Article 16)',
                    description: 'You have the right to correct inaccurate personal data and to have incomplete data completed.'
                  },
                  {
                    icon: Trash2,
                    title: 'Right to Erasure (Article 17)',
                    description: 'You have the right to request deletion of your personal data when it is no longer necessary for the purposes for which it was collected, subject to legal retention requirements.'
                  },
                  {
                    icon: Lock,
                    title: 'Right to Restriction (Article 18)',
                    description: 'You have the right to restrict processing of your personal data in certain circumstances, such as when contesting accuracy or objecting to processing.'
                  },
                  {
                    icon: Download,
                    title: 'Right to Data Portability (Article 20)',
                    description: 'You have the right to receive your personal data in a structured, commonly used, machine-readable format and to transmit it to another controller.'
                  },
                  {
                    icon: Bell,
                    title: 'Right to Object (Article 21)',
                    description: 'You have the right to object to processing based on legitimate interests, including profiling, and to direct marketing at any time.'
                  },
                  {
                    icon: Users,
                    title: 'Rights Related to Automated Decision-Making (Article 22)',
                    description: 'You have the right not to be subject to decisions based solely on automated processing that produce legal or similarly significant effects, with safeguards in place.'
                  },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start space-x-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-5">
                    <item.icon className="w-6 h-6 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="font-semibold text-slate-900 mb-1">{item.title}</div>
                      <div className="text-sm text-slate-600">{item.description}</div>
                    </div>
                  </div>
                ))}
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">5. Data Processing Activities</h2>
              <div className="bg-slate-50 rounded-xl p-6 mb-6 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left py-2 text-slate-700">Data Category</th>
                      <th className="text-left py-2 text-slate-700">Purpose</th>
                      <th className="text-left py-2 text-slate-700">Retention</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-600">
                    <tr className="border-b border-slate-100">
                      <td className="py-3">Account Information</td>
                      <td className="py-3">Service delivery, billing</td>
                      <td className="py-3">Duration of contract + 7 years</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3">Audit Engagement Data</td>
                      <td className="py-3">AI analysis, report generation</td>
                      <td className="py-3">Per PCAOB: 7 years minimum</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3">Financial Statements</td>
                      <td className="py-3">Transaction analysis, ratios</td>
                      <td className="py-3">7 years</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-3">Usage Analytics</td>
                      <td className="py-3">Service improvement</td>
                      <td className="py-3">2 years (anonymized)</td>
                    </tr>
                    <tr>
                      <td className="py-3">Support Communications</td>
                      <td className="py-3">Customer service</td>
                      <td className="py-3">3 years</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">6. International Data Transfers</h2>
              <p className="text-slate-600 mb-4">
                When transferring personal data outside the European Economic Area (EEA), we ensure
                appropriate safeguards are in place:
              </p>
              <ul className="space-y-2 text-slate-600 mb-6">
                <li className="flex items-start">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                  <span><strong>Standard Contractual Clauses (SCCs):</strong> EU-approved contract terms for international transfers</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                  <span><strong>Data Processing Agreements:</strong> Binding agreements with all sub-processors</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                  <span><strong>Transfer Impact Assessments:</strong> Regular evaluation of destination country protections</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                  <span><strong>Encryption in Transit:</strong> TLS 1.3 encryption for all data transfers</span>
                </li>
              </ul>

              <div className="bg-blue-50 rounded-xl p-6 mb-6">
                <div className="flex items-start space-x-3">
                  <Globe className="w-6 h-6 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2">Data Residency Options</h4>
                    <p className="text-sm text-slate-600">
                      Enterprise customers can request EU-only data residency, ensuring all personal data
                      remains within the European Economic Area. Contact our sales team for details.
                    </p>
                  </div>
                </div>
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">7. Technical & Organizational Measures</h2>
              <p className="text-slate-600 mb-4">
                We implement comprehensive security measures as required by Article 32 of GDPR:
              </p>
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                {[
                  { title: 'Encryption', items: ['AES-256 encryption at rest', 'TLS 1.3 in transit', 'End-to-end encryption for sensitive data'] },
                  { title: 'Access Control', items: ['Role-based access (RBAC)', 'Multi-factor authentication', 'Least privilege principle'] },
                  { title: 'Monitoring', items: ['24/7 security monitoring', 'Intrusion detection systems', 'Automated threat response'] },
                  { title: 'Business Continuity', items: ['Redundant infrastructure', 'Regular backups', 'Disaster recovery plans'] },
                ].map((section, idx) => (
                  <div key={idx} className="bg-slate-50 rounded-xl p-4">
                    <h4 className="font-semibold text-slate-900 mb-3">{section.title}</h4>
                    <ul className="space-y-1">
                      {section.items.map((item, i) => (
                        <li key={i} className="flex items-center text-sm text-slate-600">
                          <CheckCircle2 className="w-4 h-4 text-green-600 mr-2 flex-shrink-0" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">8. Data Breach Notification</h2>
              <p className="text-slate-600 mb-4">
                In the event of a personal data breach, we follow strict notification procedures:
              </p>
              <div className="bg-red-50 border border-red-100 rounded-xl p-6 mb-6">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-6 h-6 text-red-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2">Breach Response Timeline</h4>
                    <ul className="space-y-2 text-sm text-slate-600">
                      <li className="flex items-center">
                        <Clock className="w-4 h-4 text-red-600 mr-2" />
                        <strong>Within 72 hours:</strong>&nbsp;Notification to supervisory authority (as required)
                      </li>
                      <li className="flex items-center">
                        <Clock className="w-4 h-4 text-red-600 mr-2" />
                        <strong>Without undue delay:</strong>&nbsp;Notification to affected data subjects (if high risk)
                      </li>
                      <li className="flex items-center">
                        <Clock className="w-4 h-4 text-red-600 mr-2" />
                        <strong>Immediate:</strong>&nbsp;Containment measures and investigation initiation
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">9. Data Protection Officer</h2>
              <p className="text-slate-600 mb-4">
                We have appointed a Data Protection Officer (DPO) who is responsible for overseeing our
                data protection strategy and GDPR compliance:
              </p>
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 mb-6">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                    <Shield className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <div className="font-semibold text-slate-900">Data Protection Officer</div>
                    <div className="text-slate-600">dpo@auraaudit.ai</div>
                    <div className="text-sm text-slate-500 mt-1">
                      For all GDPR inquiries and data subject requests
                    </div>
                  </div>
                </div>
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">10. Exercising Your Rights</h2>
              <p className="text-slate-600 mb-4">
                To exercise any of your data subject rights, you may:
              </p>
              <div className="space-y-3 mb-6">
                <div className="flex items-center space-x-3 bg-slate-50 rounded-xl p-4">
                  <Mail className="w-5 h-5 text-blue-600" />
                  <div>
                    <div className="font-medium text-slate-900">Email our DPO</div>
                    <div className="text-sm text-slate-600">dpo@auraaudit.ai</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3 bg-slate-50 rounded-xl p-4">
                  <Users className="w-5 h-5 text-blue-600" />
                  <div>
                    <div className="font-medium text-slate-900">Use the in-app Privacy Center</div>
                    <div className="text-sm text-slate-600">Available in your account settings</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3 bg-slate-50 rounded-xl p-4">
                  <FileCheck className="w-5 h-5 text-blue-600" />
                  <div>
                    <div className="font-medium text-slate-900">Submit a formal request</div>
                    <div className="text-sm text-slate-600">privacy@auraaudit.ai (response within 30 days)</div>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-100 rounded-xl p-6 mb-6">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-6 h-6 text-yellow-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2">Verification Required</h4>
                    <p className="text-sm text-slate-600">
                      To protect your data, we may need to verify your identity before processing
                      certain requests. This may include requesting additional information or using
                      multi-factor authentication.
                    </p>
                  </div>
                </div>
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">11. Supervisory Authority</h2>
              <p className="text-slate-600 mb-6">
                If you believe we have not adequately addressed your data protection concerns, you have
                the right to lodge a complaint with your local supervisory authority. For EU residents,
                a list of supervisory authorities is available at the European Data Protection Board website.
              </p>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">12. Updates to This Policy</h2>
              <p className="text-slate-600 mb-6">
                We may update this GDPR Compliance statement periodically. Material changes will be
                communicated via email and in-app notifications. We encourage you to review this page
                regularly for the latest information on our data protection practices.
              </p>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">13. Contact Information</h2>
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-3">Aura Audit AI, LLC</h4>
                    <p className="text-sm text-slate-600">
                      123 Innovation Drive<br />
                      Suite 400<br />
                      San Francisco, CA 94107<br />
                      United States
                    </p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-3">Data Protection Contacts</h4>
                    <p className="text-sm text-slate-600">
                      <strong>DPO:</strong> dpo@auraaudit.ai<br />
                      <strong>Privacy:</strong> privacy@auraaudit.ai<br />
                      <strong>Security:</strong> security@auraaudit.ai
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Related Links */}
            <div className="mt-12 pt-8 border-t border-slate-200">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Related Documents</h3>
              <div className="flex flex-wrap gap-4">
                <Link href="/privacy" className="text-blue-600 hover:text-blue-800 underline">Privacy Policy</Link>
                <Link href="/terms" className="text-blue-600 hover:text-blue-800 underline">Terms of Service</Link>
                <Link href="/security" className="text-blue-600 hover:text-blue-800 underline">Security</Link>
                <Link href="/sla" className="text-blue-600 hover:text-blue-800 underline">Service Level Agreement</Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
