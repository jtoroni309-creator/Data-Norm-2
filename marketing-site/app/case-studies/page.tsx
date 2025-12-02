'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { TrendingUp, Clock, DollarSign, ArrowRight, CheckCircle2, Quote } from 'lucide-react'

export default function CaseStudies() {
  const caseStudies = [
    {
      company: 'Mitchell & Associates CPA',
      logo: 'M&A',
      industry: 'Regional CPA Firm',
      size: '25 employees',
      challenge: 'Manual audit processes taking 3+ weeks per engagement',
      solution: 'Implemented Aura for automated data ingestion and AI analysis',
      results: [
        { metric: '85%', label: 'Reduction in audit time' },
        { metric: '40%', label: 'Increase in capacity' },
        { metric: '$500K', label: 'Annual cost savings' },
      ],
      quote: 'Aura transformed our practice. We went from 3 weeks per audit to 4 days.',
      author: 'Sarah Mitchell, Managing Partner',
    },
    {
      company: 'Chen Accounting Group',
      logo: 'CAG',
      industry: 'Multi-office Firm',
      size: '75 employees',
      challenge: 'Fraud detection was inconsistent and time-consuming',
      solution: 'Deployed Aura\'s ML-powered fraud detection engine',
      results: [
        { metric: '$2.3M', label: 'Fraud detected in Year 1' },
        { metric: '10x', label: 'Faster anomaly detection' },
        { metric: '99.7%', label: 'Detection accuracy' },
      ],
      quote: 'The AI caught a $2.3M embezzlement scheme that our manual review missed.',
      author: 'David Chen, Senior Partner',
    },
    {
      company: 'Rodriguez CPA',
      logo: 'RC',
      industry: 'Solo Practitioner',
      size: '1 employee',
      challenge: 'Couldn\'t compete with larger firms on complex audits',
      solution: 'Used Aura to automate entire audit workflow',
      results: [
        { metric: '10x', label: 'Capacity increase' },
        { metric: '3x', label: 'Revenue growth' },
        { metric: '50%', label: 'Larger clients won' },
      ],
      quote: 'Aura lets me compete with firms 10x my size. It\'s like having a team of 10.',
      author: 'Maria Rodriguez, Owner',
    },
  ]

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Customer <span className="gradient-text">Success Stories</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              See how CPA firms are transforming their practices with Aura
            </p>
          </div>
        </div>
      </section>

      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="space-y-16">
            {caseStudies.map((study, i) => (
              <div key={i} className="bg-gray-50 rounded-3xl overflow-hidden">
                <div className="grid lg:grid-cols-2">
                  <div className="p-8 lg:p-12">
                    <div className="flex items-center space-x-4 mb-6">
                      <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-accent-600 rounded-xl flex items-center justify-center text-white font-bold text-xl">
                        {study.logo}
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-gray-900">{study.company}</h3>
                        <p className="text-gray-600">{study.industry} • {study.size}</p>
                      </div>
                    </div>
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-900 mb-2">Challenge:</h4>
                      <p className="text-gray-600">{study.challenge}</p>
                    </div>
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-900 mb-2">Solution:</h4>
                      <p className="text-gray-600">{study.solution}</p>
                    </div>
                    <div className="p-4 bg-white rounded-xl border-l-4 border-primary-600">
                      <Quote className="w-6 h-6 text-primary-600 mb-2" />
                      <p className="text-gray-700 italic mb-2">&ldquo;{study.quote}&rdquo;</p>
                      <p className="text-sm text-gray-500">— {study.author}</p>
                    </div>
                  </div>
                  <div className="bg-gradient-to-br from-primary-600 to-accent-600 p-8 lg:p-12 flex items-center">
                    <div className="w-full">
                      <h4 className="text-white/80 font-semibold mb-6">Key Results</h4>
                      <div className="space-y-6">
                        {study.results.map((result, j) => (
                          <div key={j} className="flex items-center space-x-4">
                            <CheckCircle2 className="w-6 h-6 text-white/80" />
                            <div>
                              <div className="text-4xl font-bold text-white">{result.metric}</div>
                              <div className="text-white/80">{result.label}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 bg-gray-50">
        <div className="section-container text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to Write Your Success Story?</h2>
          <p className="text-gray-600 mb-8">Join 500+ firms already transforming their audit practice</p>
          <a href="/#demo" className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-xl transition-all inline-flex items-center space-x-2">
            <span>Request a Demo</span>
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>
      </section>

      <Footer />
    </main>
  )
}
