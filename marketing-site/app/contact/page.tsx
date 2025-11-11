'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Mail, Phone, MapPin, Send, MessageSquare, HelpCircle } from 'lucide-react'
import { useState } from 'react'

export default function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    subject: '',
    message: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Form submitted:', formData)
    alert('Thank you for contacting us! We will get back to you within 24 hours.')
    setFormData({ name: '', email: '', company: '', subject: '', message: '' })
  }

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      {/* Hero Section */}
      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Get in <span className="gradient-text">Touch</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Have questions? We'd love to hear from you. Our team is here to help.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Info Cards */}
      <section className="py-16 bg-white">
        <div className="section-container">
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <a
              href="mailto:hello@toroniandcompany.com"
              className="p-8 bg-gradient-to-br from-slate-50 to-white rounded-2xl border-2 border-slate-200 hover:border-blue-400 hover:shadow-2xl transition-all text-center group transform hover:scale-105"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-lg">
                <Mail className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-2">Email Us</h3>
              <p className="text-slate-600 mb-2">We reply within 24 hours</p>
              <p className="text-blue-600 font-bold">hello@toroniandcompany.com</p>
            </a>

            <a
              href="tel:+18885551234"
              className="p-8 bg-gradient-to-br from-slate-50 to-white rounded-2xl border-2 border-slate-200 hover:border-blue-400 hover:shadow-2xl transition-all text-center group transform hover:scale-105"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-lg">
                <Phone className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-2">Call Us</h3>
              <p className="text-slate-600 mb-2">Mon-Fri, 8am-6pm EST</p>
              <p className="text-blue-600 font-bold">1 (888) 555-1234</p>
            </a>

            <a
              href="mailto:jon@toroniandcompany.com"
              className="p-8 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl border-2 border-blue-300 shadow-xl text-center group transform hover:scale-105 transition-all"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-lg">
                <MessageSquare className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-2">Contact Founder</h3>
              <p className="text-slate-600 mb-2">Jon Toroni, CEO</p>
              <p className="text-blue-600 font-bold">jon@toroniandcompany.com</p>
            </a>
          </div>
        </div>
      </section>

      {/* Contact Form */}
      <section className="py-24 bg-gradient-to-br from-gray-50 to-primary-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-display font-bold text-gray-900 mb-4">
                Send Us a Message
              </h2>
              <p className="text-xl text-gray-600">
                Fill out the form below and we'll get back to you within 24 hours
              </p>
            </div>

            <div className="bg-white rounded-2xl shadow-xl p-8 lg:p-12">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-semibold text-gray-900 mb-2">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none transition-all"
                      placeholder="John Smith"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-sm font-semibold text-gray-900 mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      id="email"
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none transition-all"
                      placeholder="john@example.com"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="company" className="block text-sm font-semibold text-gray-900 mb-2">
                      Company Name
                    </label>
                    <input
                      type="text"
                      id="company"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none transition-all"
                      placeholder="Your Firm Name"
                      value={formData.company}
                      onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                    />
                  </div>
                  <div>
                    <label htmlFor="subject" className="block text-sm font-semibold text-gray-900 mb-2">
                      Subject *
                    </label>
                    <select
                      id="subject"
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none transition-all"
                      value={formData.subject}
                      onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    >
                      <option value="">Select a subject</option>
                      <option value="demo">Request a Demo</option>
                      <option value="sales">Sales Inquiry</option>
                      <option value="support">Technical Support</option>
                      <option value="partnership">Partnership Opportunity</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-semibold text-gray-900 mb-2">
                    Message *
                  </label>
                  <textarea
                    id="message"
                    required
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none transition-all resize-none"
                    placeholder="Tell us how we can help..."
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-xl hover:scale-105 transition-all flex items-center justify-center space-x-2"
                >
                  <span>Send Message</span>
                  <Send className="w-5 h-5" />
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-display font-bold text-gray-900 mb-4">
                Frequently Asked Questions
              </h2>
              <p className="text-xl text-gray-600">
                Quick answers to common questions
              </p>
            </div>

            <div className="space-y-6">
              {[
                {
                  question: 'How quickly can we get started with Aura?',
                  answer: 'Most firms are up and running within 1-2 weeks. We provide white-glove onboarding, data migration assistance, and comprehensive training for your team.',
                },
                {
                  question: 'Is Aura PCAOB compliant?',
                  answer: 'Yes, Aura is built from the ground up to meet PCAOB standards including AS 1215 (audit documentation) and AS 1000 (general responsibilities). We maintain a complete immutable audit trail with 7-year retention.',
                },
                {
                  question: 'What accounting systems does Aura integrate with?',
                  answer: 'Aura integrates with 20+ systems including QuickBooks, Xero, NetSuite, Sage, SAP, Oracle, Workday, ADP, and more. We also support manual file uploads for any system.',
                },
                {
                  question: 'Do you offer training and support?',
                  answer: 'Absolutely! All plans include comprehensive onboarding training, video tutorials, documentation, and ongoing support. Professional and Enterprise plans include priority support and dedicated account management.',
                },
                {
                  question: 'Can I try Aura before committing?',
                  answer: 'Yes! We offer a 14-day free trial with full access to all features. No credit card required. We also provide live demos tailored to your firm\'s needs.',
                },
                {
                  question: 'Is my data secure?',
                  answer: 'Security is our top priority. We use AES-256 encryption, are SOC 2 Type II certified, and maintain enterprise-grade security practices. Your data is encrypted both in transit and at rest.',
                },
              ].map((faq, index) => (
                <div
                  key={index}
                  className="p-6 bg-gray-50 rounded-xl border border-gray-200 hover:border-primary-300 transition-colors"
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <HelpCircle className="w-6 h-6 text-primary-600 mt-1" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">{faq.question}</h3>
                      <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-12 text-center">
              <p className="text-slate-600 mb-4 text-lg">Still have questions?</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href="mailto:hello@toroniandcompany.com"
                  className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-xl transition-all hover:scale-105"
                >
                  <MessageSquare className="w-5 h-5" />
                  <span>Chat with our team</span>
                </a>
                <a
                  href="/#demo"
                  className="inline-flex items-center space-x-2 px-6 py-3 bg-slate-100 text-slate-900 font-semibold rounded-xl hover:bg-slate-200 transition-all"
                >
                  <span>Schedule a Demo</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
