'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Newspaper, Download, Mail, ExternalLink } from 'lucide-react'

export default function Press() {
  const pressReleases = [
    { title: 'Aura Audit AI Raises $15M Series A to Transform Audit Industry', date: 'November 2024', source: 'Company Announcement' },
    { title: 'Aura Surpasses 500 CPA Firm Customers, $50B in Processed Transactions', date: 'October 2024', source: 'Company Announcement' },
    { title: 'Aura Launches GPT-4 Powered Fraud Detection Engine', date: 'September 2024', source: 'Company Announcement' },
    { title: 'Aura Achieves SOC 2 Type II Certification', date: 'August 2024', source: 'Company Announcement' },
    { title: 'Jon Toroni Named to Forbes 30 Under 30 in Enterprise Technology', date: 'July 2024', source: 'Forbes' },
  ]

  const mediaKit = [
    { name: 'Company Logos (PNG, SVG)', size: '2.4 MB' },
    { name: 'Executive Headshots', size: '8.1 MB' },
    { name: 'Product Screenshots', size: '12.3 MB' },
    { name: 'Company Fact Sheet', size: '245 KB' },
  ]

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Press & <span className="gradient-text">Media</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              News, announcements, and media resources from Aura Audit AI
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white">
        <div className="section-container">
          <div className="grid lg:grid-cols-3 gap-12">
            <div className="lg:col-span-2">
              <h2 className="text-2xl font-bold text-gray-900 mb-8">Recent News</h2>
              <div className="space-y-6">
                {pressReleases.map((item, i) => (
                  <div key={i} className="flex items-start justify-between p-6 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-colors cursor-pointer group">
                    <div className="flex items-start space-x-4">
                      <Newspaper className="w-6 h-6 text-primary-600 mt-1" />
                      <div>
                        <h3 className="font-bold text-gray-900 group-hover:text-primary-600 transition-colors">{item.title}</h3>
                        <div className="text-sm text-gray-500 mt-1">{item.date} • {item.source}</div>
                      </div>
                    </div>
                    <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors" />
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-8">Media Kit</h2>
              <div className="space-y-4 mb-8">
                {mediaKit.map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer">
                    <div className="flex items-center space-x-3">
                      <Download className="w-5 h-5 text-gray-400" />
                      <div>
                        <div className="font-medium text-gray-900">{item.name}</div>
                        <div className="text-xs text-gray-500">{item.size}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-gradient-to-br from-primary-600 to-accent-600 rounded-2xl p-6 text-white">
                <Mail className="w-8 h-8 mb-4" />
                <h3 className="text-lg font-bold mb-2">Media Inquiries</h3>
                <p className="text-white/80 text-sm mb-4">For press inquiries, interviews, or media resources:</p>
                <a href="mailto:press@auraaudit.ai" className="text-white font-semibold hover:underline">press@auraaudit.ai</a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
