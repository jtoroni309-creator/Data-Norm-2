'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Video, Calendar, Clock, Users, ArrowRight, Play } from 'lucide-react'

export default function Webinars() {
  const upcomingWebinars = [
    {
      title: 'Getting Started with Aura: Live Demo',
      date: 'December 5, 2024',
      time: '2:00 PM ET',
      presenter: 'Sarah Williams, CPO',
      attendees: 127,
    },
    {
      title: 'AI-Powered Fraud Detection Best Practices',
      date: 'December 12, 2024',
      time: '1:00 PM ET',
      presenter: 'Dr. Michael Chen, CTO',
      attendees: 89,
    },
  ]

  const pastWebinars = [
    { title: 'PCAOB Compliance with AI Tools', duration: '45 min', views: 1240 },
    { title: 'Automating R&D Tax Credit Studies', duration: '38 min', views: 890 },
    { title: 'Journal Entry Testing with ML', duration: '52 min', views: 1567 },
    { title: 'Getting Maximum ROI from Aura', duration: '41 min', views: 723 },
    { title: 'Advanced Analytics Dashboard Tour', duration: '35 min', views: 654 },
    { title: 'Integration Best Practices', duration: '48 min', views: 512 },
  ]

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Webinars & <span className="gradient-text">Training</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Learn from experts and get the most out of Aura
            </p>
          </div>
        </div>
      </section>

      <section className="py-24 bg-white">
        <div className="section-container">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">Upcoming Webinars</h2>
          <div className="grid md:grid-cols-2 gap-8 mb-16">
            {upcomingWebinars.map((webinar, i) => (
              <div key={i} className="bg-gradient-to-br from-primary-600 to-accent-600 rounded-2xl p-8 text-white">
                <div className="flex items-start justify-between mb-4">
                  <Video className="w-10 h-10" />
                  <span className="px-3 py-1 bg-white/20 rounded-full text-sm">Live</span>
                </div>
                <h3 className="text-2xl font-bold mb-4">{webinar.title}</h3>
                <div className="space-y-2 mb-6">
                  <div className="flex items-center space-x-2 text-white/80">
                    <Calendar className="w-4 h-4" />
                    <span>{webinar.date}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-white/80">
                    <Clock className="w-4 h-4" />
                    <span>{webinar.time}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-white/80">
                    <Users className="w-4 h-4" />
                    <span>{webinar.attendees} registered</span>
                  </div>
                </div>
                <p className="text-white/80 mb-6">Presenter: {webinar.presenter}</p>
                <button className="w-full py-3 bg-white text-primary-600 font-semibold rounded-lg hover:shadow-lg transition-all">
                  Register Free
                </button>
              </div>
            ))}
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-8">On-Demand Library</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pastWebinars.map((webinar, i) => (
              <div key={i} className="group bg-gray-50 rounded-2xl overflow-hidden hover:shadow-lg transition-all cursor-pointer">
                <div className="h-32 bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center relative">
                  <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <Play className="w-12 h-12 text-white" />
                  </div>
                  <Video className="w-10 h-10 text-gray-400" />
                </div>
                <div className="p-6">
                  <h3 className="font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">{webinar.title}</h3>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{webinar.duration}</span>
                    <span>{webinar.views.toLocaleString()} views</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
