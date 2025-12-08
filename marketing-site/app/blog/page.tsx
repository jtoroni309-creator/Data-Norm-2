'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import Link from 'next/link'
import { Calendar, User, ArrowRight, Clock, Sparkles } from 'lucide-react'

export default function Blog() {
  const featuredPost = {
    title: 'How AI Will Change the Future for Accounting and CPAs',
    excerpt: 'A senior partner\'s perspective on the transformative impact of artificial intelligence on the accounting profession—and why the firms that embrace it will thrive.',
    author: 'Jonathan Toroni, CPA',
    date: 'December 7, 2024',
    readTime: '15 min read',
    category: 'Industry Trends',
    slug: 'ai-future-accounting-cpa',
    featured: true,
  }

  const posts = [
    {
      title: 'How AI is Transforming the Audit Profession in 2024',
      excerpt: 'Discover how artificial intelligence is revolutionizing audit processes, from data analysis to fraud detection.',
      author: 'Jon Toroni',
      date: 'November 28, 2024',
      readTime: '8 min read',
      category: 'Industry Trends',
      slug: 'ai-transforming-audit-2024',
    },
    {
      title: 'PCAOB Compliance: A Complete Guide for AI-Powered Audits',
      excerpt: 'Everything you need to know about maintaining PCAOB compliance when using AI tools in your audit practice.',
      author: 'Sarah Williams',
      date: 'November 25, 2024',
      readTime: '12 min read',
      category: 'Compliance',
      slug: 'pcaob-compliance-guide',
    },
    {
      title: '5 Ways to Detect Fraud with Machine Learning',
      excerpt: 'Learn the top ML techniques for identifying fraudulent transactions and financial statement manipulation.',
      author: 'Dr. Michael Chen',
      date: 'November 20, 2024',
      readTime: '10 min read',
      category: 'AI & Technology',
      slug: 'fraud-detection-ml',
    },
    {
      title: 'Case Study: How Mitchell CPA Cut Audit Time by 85%',
      excerpt: 'A deep dive into how one firm transformed their practice with Aura Audit AI.',
      author: 'Marketing Team',
      date: 'November 15, 2024',
      readTime: '6 min read',
      category: 'Case Studies',
      slug: 'mitchell-cpa-case-study',
    },
    {
      title: 'The Future of R&D Tax Credits: AI-Powered Studies',
      excerpt: 'How artificial intelligence is making R&D tax credit studies faster and more accurate than ever.',
      author: 'Jon Toroni',
      date: 'November 10, 2024',
      readTime: '7 min read',
      category: 'Tax Credits',
      slug: 'rd-tax-credits-ai',
    },
    {
      title: 'Building Trust: Our Approach to AI Explainability',
      excerpt: 'Why we believe every AI recommendation should come with a clear explanation.',
      author: 'Dr. Michael Chen',
      date: 'November 5, 2024',
      readTime: '9 min read',
      category: 'AI & Technology',
      slug: 'ai-explainability',
    },
  ]

  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
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

      {/* Featured Post */}
      <section className="py-12 bg-white">
        <div className="section-container">
          <Link
            href={`/blog/${featuredPost.slug}`}
            className="block group"
          >
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 p-8 md:p-12 hover:shadow-2xl transition-all">
              <div className="absolute top-4 right-4 flex items-center space-x-2">
                <span className="px-4 py-1 bg-white/20 text-white text-sm font-medium rounded-full flex items-center">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Featured
                </span>
              </div>
              <div className="max-w-3xl">
                <span className="inline-block px-4 py-1 bg-blue-500/30 text-blue-200 text-sm font-medium rounded-full mb-6">
                  {featuredPost.category}
                </span>
                <h2 className="text-3xl md:text-4xl font-display font-bold text-white mb-4 group-hover:text-blue-200 transition-colors">
                  {featuredPost.title}
                </h2>
                <p className="text-lg text-slate-300 mb-6 leading-relaxed">
                  {featuredPost.excerpt}
                </p>
                <div className="flex flex-wrap items-center gap-6 text-slate-400">
                  <span className="flex items-center">
                    <User className="w-4 h-4 mr-2" />
                    {featuredPost.author}
                  </span>
                  <span className="flex items-center">
                    <Calendar className="w-4 h-4 mr-2" />
                    {featuredPost.date}
                  </span>
                  <span className="flex items-center">
                    <Clock className="w-4 h-4 mr-2" />
                    {featuredPost.readTime}
                  </span>
                </div>
              </div>
              <ArrowRight className="absolute bottom-8 right-8 w-8 h-8 text-white/50 group-hover:text-white group-hover:translate-x-2 transition-all" />
            </div>
          </Link>
        </div>
      </section>

      {/* All Posts */}
      <section className="py-16 bg-white">
        <div className="section-container">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">All Articles</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {posts.map((post, i) => (
              <article key={i} className="bg-white border border-gray-200 rounded-2xl overflow-hidden hover:shadow-xl transition-all group">
                <div className="h-48 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <span className="text-white/80 text-sm font-medium px-4 py-2 bg-white/20 rounded-full">{post.category}</span>
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors">{post.title}</h3>
                  <p className="text-gray-600 mb-4 line-clamp-2">{post.excerpt}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center space-x-4">
                      <span className="flex items-center"><User className="w-4 h-4 mr-1" />{post.author}</span>
                      <span className="flex items-center"><Clock className="w-4 h-4 mr-1" />{post.readTime}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                    <span className="text-sm text-gray-500">{post.date}</span>
                    <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter Signup */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="section-container">
          <div className="max-w-2xl mx-auto text-center text-white">
            <h2 className="text-3xl font-display font-bold mb-4">
              Stay Updated
            </h2>
            <p className="text-white/90 mb-8">
              Get the latest insights on AI and accounting delivered to your inbox.
            </p>
            <form className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-6 py-4 rounded-xl text-gray-900 focus:ring-2 focus:ring-white/50 outline-none"
              />
              <button
                type="submit"
                className="px-8 py-4 bg-white text-blue-600 font-semibold rounded-xl hover:shadow-lg transition-all"
              >
                Subscribe
              </button>
            </form>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
