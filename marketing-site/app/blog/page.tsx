'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { Calendar, User, ArrowRight, Clock } from 'lucide-react'

export default function Blog() {
  const posts = [
    {
      title: 'How AI is Transforming the Audit Profession in 2024',
      excerpt: 'Discover how artificial intelligence is revolutionizing audit processes, from data analysis to fraud detection.',
      author: 'Jon Toroni',
      date: 'November 28, 2024',
      readTime: '8 min read',
      category: 'Industry Trends',
    },
    {
      title: 'PCAOB Compliance: A Complete Guide for AI-Powered Audits',
      excerpt: 'Everything you need to know about maintaining PCAOB compliance when using AI tools in your audit practice.',
      author: 'Sarah Williams',
      date: 'November 25, 2024',
      readTime: '12 min read',
      category: 'Compliance',
    },
    {
      title: '5 Ways to Detect Fraud with Machine Learning',
      excerpt: 'Learn the top ML techniques for identifying fraudulent transactions and financial statement manipulation.',
      author: 'Dr. Michael Chen',
      date: 'November 20, 2024',
      readTime: '10 min read',
      category: 'AI & Technology',
    },
    {
      title: 'Case Study: How Mitchell CPA Cut Audit Time by 85%',
      excerpt: 'A deep dive into how one firm transformed their practice with Aura Audit AI.',
      author: 'Marketing Team',
      date: 'November 15, 2024',
      readTime: '6 min read',
      category: 'Case Studies',
    },
    {
      title: 'The Future of R&D Tax Credits: AI-Powered Studies',
      excerpt: 'How artificial intelligence is making R&D tax credit studies faster and more accurate than ever.',
      author: 'Jon Toroni',
      date: 'November 10, 2024',
      readTime: '7 min read',
      category: 'Tax Credits',
    },
    {
      title: 'Building Trust: Our Approach to AI Explainability',
      excerpt: 'Why we believe every AI recommendation should come with a clear explanation.',
      author: 'Dr. Michael Chen',
      date: 'November 5, 2024',
      readTime: '9 min read',
      category: 'AI & Technology',
    },
  ]

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Insights & <span className="gradient-text">Resources</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Expert perspectives on AI, audit automation, and the future of the accounting profession
            </p>
          </div>
        </div>
      </section>

      <section className="py-24 bg-white">
        <div className="section-container">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {posts.map((post, i) => (
              <article key={i} className="bg-white border border-gray-200 rounded-2xl overflow-hidden hover:shadow-xl transition-all group cursor-pointer">
                <div className="h-48 bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                  <span className="text-white/80 text-sm font-medium px-4 py-2 bg-white/20 rounded-full">{post.category}</span>
                </div>
                <div className="p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-primary-600 transition-colors">{post.title}</h2>
                  <p className="text-gray-600 mb-4 line-clamp-2">{post.excerpt}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center space-x-4">
                      <span className="flex items-center"><User className="w-4 h-4 mr-1" />{post.author}</span>
                      <span className="flex items-center"><Clock className="w-4 h-4 mr-1" />{post.readTime}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                    <span className="text-sm text-gray-500">{post.date}</span>
                    <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" />
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
