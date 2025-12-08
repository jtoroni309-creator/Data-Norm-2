'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import Link from 'next/link'
import { Shield, Clock, CheckCircle2, AlertTriangle, Headphones, Mail, Phone } from 'lucide-react'

export default function SLAPage() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Service Level <span className="gradient-text">Agreement</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Our commitment to reliable, high-performance service
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
            {/* Key Metrics */}
            <div className="grid md:grid-cols-3 gap-6 mb-16">
              {[
                { metric: '99.9%', label: 'Uptime Guarantee', icon: Shield },
                { metric: '< 500ms', label: 'API Response Time', icon: Clock },
                { metric: '24/7', label: 'Support Coverage', icon: Headphones },
              ].map((item, idx) => (
                <div key={idx} className="text-center glassmorphism rounded-2xl p-6">
                  <item.icon className="w-10 h-10 text-blue-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold gradient-text-2 mb-1">{item.metric}</div>
                  <div className="text-sm text-slate-600">{item.label}</div>
                </div>
              ))}
            </div>

            {/* Content */}
            <div className="prose prose-lg max-w-none">
              <h2 className="text-2xl font-bold text-slate-900 mb-4">1. Overview</h2>
              <p className="text-slate-600 mb-6">
                This Service Level Agreement ("SLA") describes the service levels Aura Audit AI, LLC ("Aura,"
                "we," "us," or "our") commits to provide for our cloud-based audit automation platform and
                related services ("Services"). This SLA applies to all customers with a valid subscription
                agreement.
              </p>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">2. Service Availability</h2>
              <h3 className="text-xl font-semibold text-slate-800 mb-3">2.1 Uptime Commitment</h3>
              <p className="text-slate-600 mb-4">
                Aura commits to maintaining a Monthly Uptime Percentage of at least 99.9% for the Services,
                excluding scheduled maintenance windows and circumstances outside our reasonable control.
              </p>

              <div className="bg-slate-50 rounded-xl p-6 mb-6">
                <h4 className="font-semibold text-slate-900 mb-4">Service Tier Commitments:</h4>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left py-2 text-slate-700">Plan</th>
                      <th className="text-left py-2 text-slate-700">Uptime SLA</th>
                      <th className="text-left py-2 text-slate-700">Credit</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-600">
                    <tr className="border-b border-slate-100">
                      <td className="py-2">Starter</td>
                      <td className="py-2">99.5%</td>
                      <td className="py-2">10% per 0.1% below SLA</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-2">Professional</td>
                      <td className="py-2">99.9%</td>
                      <td className="py-2">15% per 0.1% below SLA</td>
                    </tr>
                    <tr>
                      <td className="py-2">Enterprise</td>
                      <td className="py-2">99.95%</td>
                      <td className="py-2">25% per 0.05% below SLA</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h3 className="text-xl font-semibold text-slate-800 mb-3">2.2 Scheduled Maintenance</h3>
              <p className="text-slate-600 mb-6">
                Scheduled maintenance will be performed during low-usage periods (typically Sundays 2:00 AM - 6:00 AM EST).
                We will provide at least 72 hours advance notice for planned maintenance via email and in-app notifications.
                Scheduled maintenance does not count against uptime calculations.
              </p>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">3. Performance Standards</h2>
              <div className="space-y-4 mb-6">
                {[
                  { metric: 'API Response Time', target: '< 500ms for 95th percentile', description: 'Measured at our edge servers' },
                  { metric: 'Data Processing', target: '100,000+ transactions/hour', description: 'For standard transaction analysis' },
                  { metric: 'Report Generation', target: '< 30 seconds', description: 'For standard audit reports up to 100 pages' },
                  { metric: 'Document Upload', target: '< 5 seconds', description: 'For files up to 50MB' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start space-x-4 bg-blue-50 rounded-xl p-4">
                    <CheckCircle2 className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="font-semibold text-slate-900">{item.metric}: {item.target}</div>
                      <div className="text-sm text-slate-600">{item.description}</div>
                    </div>
                  </div>
                ))}
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">4. Support Response Times</h2>
              <div className="bg-slate-50 rounded-xl p-6 mb-6">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left py-2 text-slate-700">Severity</th>
                      <th className="text-left py-2 text-slate-700">Description</th>
                      <th className="text-left py-2 text-slate-700">Initial Response</th>
                      <th className="text-left py-2 text-slate-700">Resolution Target</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-600">
                    <tr className="border-b border-slate-100">
                      <td className="py-2 font-semibold text-red-600">Critical (P1)</td>
                      <td className="py-2">Service completely unavailable</td>
                      <td className="py-2">15 minutes</td>
                      <td className="py-2">4 hours</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-2 font-semibold text-orange-600">High (P2)</td>
                      <td className="py-2">Major feature impaired</td>
                      <td className="py-2">1 hour</td>
                      <td className="py-2">8 hours</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-2 font-semibold text-yellow-600">Medium (P3)</td>
                      <td className="py-2">Minor feature issue</td>
                      <td className="py-2">4 hours</td>
                      <td className="py-2">24 hours</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-semibold text-blue-600">Low (P4)</td>
                      <td className="py-2">General inquiry</td>
                      <td className="py-2">8 hours</td>
                      <td className="py-2">72 hours</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">5. Data Protection</h2>
              <ul className="space-y-2 text-slate-600 mb-6">
                <li className="flex items-start">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                  <span><strong>Backup Frequency:</strong> Continuous backup with point-in-time recovery available</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                  <span><strong>Data Retention:</strong> 7 years for audit data per PCAOB requirements</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                  <span><strong>Recovery Point Objective (RPO):</strong> Maximum 1 hour of data loss</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                  <span><strong>Recovery Time Objective (RTO):</strong> Service restoration within 4 hours</span>
                </li>
              </ul>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">6. Service Credits</h2>
              <p className="text-slate-600 mb-4">
                If we fail to meet our uptime commitment, eligible customers may request service credits
                as follows:
              </p>
              <div className="bg-slate-50 rounded-xl p-6 mb-6">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left py-2 text-slate-700">Monthly Uptime</th>
                      <th className="text-left py-2 text-slate-700">Service Credit</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-600">
                    <tr className="border-b border-slate-100">
                      <td className="py-2">99.0% - 99.9%</td>
                      <td className="py-2">10% of monthly fee</td>
                    </tr>
                    <tr className="border-b border-slate-100">
                      <td className="py-2">95.0% - 99.0%</td>
                      <td className="py-2">25% of monthly fee</td>
                    </tr>
                    <tr>
                      <td className="py-2">Below 95.0%</td>
                      <td className="py-2">50% of monthly fee</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">7. Exclusions</h2>
              <p className="text-slate-600 mb-4">
                This SLA does not apply to:
              </p>
              <ul className="list-disc list-inside text-slate-600 mb-6 space-y-2">
                <li>Features labeled as "Beta" or "Preview"</li>
                <li>Outages caused by factors outside our reasonable control (force majeure)</li>
                <li>Customer's equipment, software, or network connectivity issues</li>
                <li>Unauthorized access or misuse of the Services</li>
                <li>Customer's failure to follow documented configuration requirements</li>
              </ul>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">8. Credit Request Process</h2>
              <p className="text-slate-600 mb-6">
                To request a service credit, submit a support ticket within 30 days of the incident,
                including the date, time, duration of the outage, and affected services. Credits are
                applied to future invoices and do not constitute a cash refund.
              </p>

              <h2 className="text-2xl font-bold text-slate-900 mb-4">9. Contact Information</h2>
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="flex items-center space-x-3">
                    <Mail className="w-5 h-5 text-blue-600" />
                    <div>
                      <div className="text-sm text-slate-500">Email Support</div>
                      <div className="text-slate-900">support@auraaudit.ai</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Phone className="w-5 h-5 text-blue-600" />
                    <div>
                      <div className="text-sm text-slate-500">Phone (Enterprise)</div>
                      <div className="text-slate-900">1-888-AURA-AI</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="w-5 h-5 text-blue-600" />
                    <div>
                      <div className="text-sm text-slate-500">Status Page</div>
                      <div className="text-slate-900">status.auraaudit.ai</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Related Links */}
            <div className="mt-12 pt-8 border-t border-slate-200">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Related Documents</h3>
              <div className="flex flex-wrap gap-4">
                <Link href="/terms" className="text-blue-600 hover:text-blue-800 underline">Terms of Service</Link>
                <Link href="/privacy" className="text-blue-600 hover:text-blue-800 underline">Privacy Policy</Link>
                <Link href="/security" className="text-blue-600 hover:text-blue-800 underline">Security</Link>
                <Link href="/gdpr" className="text-blue-600 hover:text-blue-800 underline">GDPR Compliance</Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
