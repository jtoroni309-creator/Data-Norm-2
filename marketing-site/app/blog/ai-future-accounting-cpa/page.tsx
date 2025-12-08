'use client'

import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import Link from 'next/link'
import {
  Calendar,
  User,
  Clock,
  ArrowLeft,
  Share2,
  Linkedin,
  Twitter,
  BookOpen,
  Brain,
  TrendingUp,
  Shield,
  Users,
  Lightbulb,
  Target,
  CheckCircle2,
  Quote,
  ArrowRight,
} from 'lucide-react'

export default function BlogPost() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />

      {/* Hero Section */}
      <section className="pt-32 pb-16 bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 text-white">
        <div className="section-container">
          <div className="max-w-4xl mx-auto">
            <Link
              href="/blog"
              className="inline-flex items-center text-blue-300 hover:text-white mb-8 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Blog
            </Link>

            <div className="flex items-center space-x-4 mb-6">
              <span className="px-4 py-1 bg-blue-500/20 text-blue-300 text-sm font-medium rounded-full">
                Industry Trends
              </span>
              <span className="px-4 py-1 bg-purple-500/20 text-purple-300 text-sm font-medium rounded-full">
                Featured
              </span>
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-display font-bold mb-6 leading-tight">
              How AI Will Change the Future for Accounting and CPAs
            </h1>

            <p className="text-xl text-slate-300 mb-8 leading-relaxed">
              A senior partner's perspective on the transformative impact of artificial intelligence
              on the accounting profession—and why the firms that embrace it will thrive.
            </p>

            <div className="flex flex-wrap items-center gap-6 text-slate-400">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold mr-3">
                  JT
                </div>
                <div>
                  <div className="text-white font-semibold">Jonathan Toroni, CPA</div>
                  <div className="text-sm">Founder & CEO, Aura Audit AI</div>
                </div>
              </div>
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-2" />
                December 7, 2024
              </div>
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-2" />
                15 min read
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Article Content */}
      <article className="py-16">
        <div className="section-container">
          <div className="max-w-4xl mx-auto">
            {/* Introduction */}
            <div className="prose prose-lg max-w-none">
              <p className="text-xl text-slate-700 leading-relaxed mb-8">
                After nearly two decades in public accounting—from staff accountant to managing partner—I've witnessed
                several technological shifts that promised to "revolutionize" our profession. Most were evolutionary
                at best. But artificial intelligence is different. This isn't just another software upgrade or
                workflow optimization. AI represents a fundamental reimagining of what CPAs do, how we create value,
                and the very nature of professional judgment in an algorithmic age.
              </p>

              <p className="text-lg text-slate-600 leading-relaxed mb-8">
                In this article, I'll share my perspective—grounded in both the practical realities of running
                a CPA practice and the cutting-edge developments we're building at Aura Audit AI—on how artificial
                intelligence will reshape our profession over the next decade. More importantly, I'll offer concrete
                guidance on how forward-thinking firms can position themselves not just to survive this transition,
                but to thrive.
              </p>
            </div>

            {/* Section 1 */}
            <section className="mb-16">
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-3xl font-display font-bold text-slate-900">
                  The Current State: Where AI Meets Accounting
                </h2>
              </div>

              <div className="prose prose-lg max-w-none text-slate-600">
                <p>
                  To understand where we're going, we must first acknowledge where we are. Today's AI applications
                  in accounting fall into several categories:
                </p>

                <div className="my-8 grid md:grid-cols-2 gap-6">
                  {[
                    {
                      title: 'Document Processing',
                      description: 'AI extracts data from invoices, receipts, and financial documents with increasing accuracy.',
                    },
                    {
                      title: 'Transaction Classification',
                      description: 'Machine learning categorizes transactions into appropriate accounts with minimal human intervention.',
                    },
                    {
                      title: 'Anomaly Detection',
                      description: 'Statistical models flag unusual patterns in financial data that warrant further investigation.',
                    },
                    {
                      title: 'Predictive Analytics',
                      description: 'AI forecasts cash flows, revenue trends, and financial metrics based on historical patterns.',
                    },
                  ].map((item, idx) => (
                    <div key={idx} className="bg-slate-50 rounded-xl p-6 border border-slate-200">
                      <h4 className="font-bold text-slate-900 mb-2">{item.title}</h4>
                      <p className="text-slate-600 text-sm">{item.description}</p>
                    </div>
                  ))}
                </div>

                <p>
                  These capabilities, while impressive, are largely augmentative—they assist human accountants
                  rather than replace them. But we're rapidly approaching an inflection point where AI systems
                  can handle increasingly complex, judgment-intensive tasks that were previously the exclusive
                  domain of experienced professionals.
                </p>
              </div>
            </section>

            {/* Quote Block */}
            <blockquote className="my-12 relative">
              <div className="absolute -left-4 top-0 text-8xl text-blue-200 font-serif">"</div>
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8 pl-12">
                <p className="text-xl text-slate-800 italic leading-relaxed mb-4">
                  The question isn't whether AI will transform accounting—that's inevitable. The question is
                  whether you'll be among the firms defining what that transformation looks like, or scrambling
                  to catch up with those who did.
                </p>
                <footer className="text-slate-600">
                  — Jonathan Toroni, CPA
                </footer>
              </div>
            </blockquote>

            {/* Section 2 */}
            <section className="mb-16">
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-3xl font-display font-bold text-slate-900">
                  Five Ways AI Will Transform CPA Practices
                </h2>
              </div>

              <div className="space-y-8">
                {/* Transformation 1 */}
                <div className="bg-white border border-slate-200 rounded-2xl p-8 hover:shadow-lg transition-all">
                  <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center">
                    <span className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">1</span>
                    From Data Entry to Data Strategy
                  </h3>
                  <p className="text-slate-600 mb-4">
                    The most immediate impact is already visible: AI is eliminating the need for manual data entry
                    and basic bookkeeping. What once required hours of staff time—coding transactions, reconciling
                    accounts, preparing trial balances—can now be accomplished in minutes with AI-powered automation.
                  </p>
                  <p className="text-slate-600">
                    But here's what many miss: this isn't about doing the same work faster. It's about fundamentally
                    repositioning the accountant's role from data processor to data strategist. When the mechanics
                    of recording transactions become automated, the value shifts to interpreting what that data means
                    and advising clients on strategic decisions.
                  </p>
                  <div className="mt-4 p-4 bg-blue-50 rounded-xl">
                    <p className="text-sm text-blue-800">
                      <strong>Aura in Action:</strong> Our{' '}
                      <Link href="/services/ai-audit" className="text-blue-600 underline hover:text-blue-800">
                        AI-Powered Audit Platform
                      </Link>{' '}
                      processes over 100,000 transactions per hour, freeing auditors to focus on high-judgment areas
                      where their expertise creates the most value.
                    </p>
                  </div>
                </div>

                {/* Transformation 2 */}
                <div className="bg-white border border-slate-200 rounded-2xl p-8 hover:shadow-lg transition-all">
                  <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center">
                    <span className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">2</span>
                    100% Population Testing Becomes Standard
                  </h3>
                  <p className="text-slate-600 mb-4">
                    Statistical sampling has been a cornerstone of audit methodology for decades—not because it's
                    ideal, but because testing every transaction was impractical. AI changes this calculus entirely.
                    When machine learning can analyze an entire population of transactions in seconds, the traditional
                    justification for sampling evaporates.
                  </p>
                  <p className="text-slate-600">
                    This shift has profound implications for audit quality. Rather than extrapolating from a sample,
                    auditors can now make assertions about 100% of the data. Anomalies that might have been missed
                    through sampling are identified. The audit becomes more comprehensive and, paradoxically, more
                    efficient—because the time previously spent selecting and testing samples can be redirected to
                    investigating the specific items that AI flags as unusual.
                  </p>
                </div>

                {/* Transformation 3 */}
                <div className="bg-white border border-slate-200 rounded-2xl p-8 hover:shadow-lg transition-all">
                  <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center">
                    <span className="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">3</span>
                    Real-Time Compliance Monitoring
                  </h3>
                  <p className="text-slate-600 mb-4">
                    The traditional audit model—reviewing historical financial statements months after year-end—is
                    increasingly anachronistic. Stakeholders want real-time assurance, not a backward-looking report
                    on what happened six months ago.
                  </p>
                  <p className="text-slate-600">
                    AI enables continuous monitoring of financial data, internal controls, and compliance status.
                    Rather than a point-in-time snapshot, firms can offer ongoing assurance services that identify
                    issues as they occur rather than long after the fact.
                  </p>
                  <div className="mt-4 p-4 bg-green-50 rounded-xl">
                    <p className="text-sm text-green-800">
                      <strong>Industry Insight:</strong> Our{' '}
                      <Link href="/services/soc-compliance" className="text-green-600 underline hover:text-green-800">
                        SOC Compliance Platform
                      </Link>{' '}
                      enables continuous control monitoring for Type II examinations, providing real-time visibility
                      into control effectiveness throughout the examination period.
                    </p>
                  </div>
                </div>

                {/* Transformation 4 */}
                <div className="bg-white border border-slate-200 rounded-2xl p-8 hover:shadow-lg transition-all">
                  <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center">
                    <span className="w-8 h-8 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">4</span>
                    Democratization of Specialized Services
                  </h3>
                  <p className="text-slate-600 mb-4">
                    Historically, specialized services like R&D tax credit studies, transfer pricing analysis, or
                    complex valuation work required deep expertise that limited which firms could offer them. AI
                    changes this dynamic by codifying expert knowledge into systems that guide less experienced
                    practitioners through complex analyses.
                  </p>
                  <p className="text-slate-600">
                    This doesn't mean expertise becomes irrelevant—quite the opposite. The firms that develop
                    the best AI systems will be those with the deepest subject matter expertise to train them.
                    But it does mean that a small firm with the right AI tools can now offer services that were
                    previously the exclusive domain of Big Four specialists.
                  </p>
                  <div className="mt-4 p-4 bg-orange-50 rounded-xl">
                    <p className="text-sm text-orange-800">
                      <strong>Example:</strong> Our{' '}
                      <Link href="/services/rd-tax-credit" className="text-orange-600 underline hover:text-orange-800">
                        R&D Tax Credit Platform
                      </Link>{' '}
                      enables any CPA firm to conduct IRS-defensible R&D studies with AI that guides the analysis
                      and ensures comprehensive documentation.
                    </p>
                  </div>
                </div>

                {/* Transformation 5 */}
                <div className="bg-white border border-slate-200 rounded-2xl p-8 hover:shadow-lg transition-all">
                  <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center">
                    <span className="w-8 h-8 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">5</span>
                    The Rise of AI-Augmented Professional Judgment
                  </h3>
                  <p className="text-slate-600 mb-4">
                    Perhaps the most profound shift is in how we think about professional judgment itself. For
                    generations, professional judgment has been almost entirely a human function—the application
                    of training, experience, and intuition to complex situations where clear-cut rules don't exist.
                  </p>
                  <p className="text-slate-600">
                    AI doesn't replace this judgment, but it augments it in powerful ways. An AI system can instantly
                    surface relevant precedents, identify similar situations from across thousands of engagements,
                    and provide data-driven context that informs the human decision-maker. The judgment remains human,
                    but it's informed by analysis that would be impossible without AI.
                  </p>
                </div>
              </div>
            </section>

            {/* Section 3 */}
            <section className="mb-16">
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-3xl font-display font-bold text-slate-900">
                  Addressing the Concerns: Ethics, Liability, and Trust
                </h2>
              </div>

              <div className="prose prose-lg max-w-none text-slate-600">
                <p>
                  No discussion of AI in accounting would be complete without addressing the legitimate concerns
                  that practitioners raise. Let me address the three most common:
                </p>

                <h3 className="text-xl font-bold text-slate-900 mt-8 mb-4">Who is liable when AI makes a mistake?</h3>
                <p>
                  This is perhaps the most pressing question, and the answer is clear: the CPA remains liable.
                  AI is a tool, and like any tool, the professional using it bears responsibility for its proper
                  application. This is why transparency in AI systems is so critical. A black box that produces
                  recommendations without explanation is professionally untenable.
                </p>
                <p>
                  At Aura, we've built our entire platform around the principle of explainable AI. Every finding,
                  every recommendation, every risk assessment comes with a complete explanation of the underlying
                  reasoning. Auditors can see exactly what factors contributed to a conclusion and at what weights.
                  This isn't just good ethics—it's essential for professional responsibility.
                </p>

                <h3 className="text-xl font-bold text-slate-900 mt-8 mb-4">Can we trust AI with confidential client data?</h3>
                <p>
                  Data security is non-negotiable. Any AI platform handling financial data must meet or exceed
                  the security standards we've always applied to sensitive information. This means SOC 2 Type II
                  certification, enterprise-grade encryption, strict access controls, and comprehensive audit trails.
                </p>
                <p>
                  But beyond security, there's the question of how AI models are trained. We're committed to
                  ensuring that client data is never used to train models that serve other clients without
                  explicit consent. Each engagement's data remains siloed and protected.
                </p>

                <h3 className="text-xl font-bold text-slate-900 mt-8 mb-4">Will AI replace accountants?</h3>
                <p>
                  This question reveals a fundamental misunderstanding of both AI and accounting. AI will replace
                  certain tasks—the mechanical, repetitive aspects of what accountants do. But accounting has
                  never been just about those tasks. It's about professional judgment, client relationships,
                  ethical reasoning, and strategic advice.
                </p>
                <p>
                  The accountants who will struggle are those who've built their careers around task execution
                  rather than value creation. The accountants who will thrive are those who embrace AI as a
                  force multiplier—allowing them to serve more clients, provide deeper insights, and focus on
                  the high-judgment work where human expertise is irreplaceable.
                </p>
              </div>
            </section>

            {/* Section 4 */}
            <section className="mb-16">
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center">
                  <Target className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-3xl font-display font-bold text-slate-900">
                  A Roadmap for Firms: Embracing AI Strategically
                </h2>
              </div>

              <div className="prose prose-lg max-w-none text-slate-600">
                <p>
                  Based on our work with hundreds of CPA firms adopting AI, I recommend a phased approach:
                </p>

                <div className="my-8 space-y-6">
                  {[
                    {
                      phase: 'Phase 1: Foundation (Months 1-3)',
                      items: [
                        'Audit current workflows to identify high-volume, rule-based tasks suitable for AI',
                        'Evaluate AI platforms with a focus on security, explainability, and integration',
                        'Start with a pilot engagement to build internal expertise and confidence',
                        'Develop internal policies for AI use and quality control',
                      ],
                    },
                    {
                      phase: 'Phase 2: Expansion (Months 4-9)',
                      items: [
                        'Roll out AI tools to broader engagement teams',
                        'Develop training programs to ensure consistent, effective use',
                        'Establish feedback loops to continuously improve AI application',
                        'Begin marketing AI-enhanced services to clients',
                      ],
                    },
                    {
                      phase: 'Phase 3: Transformation (Months 10-18)',
                      items: [
                        'Restructure service offerings around AI-enabled capabilities',
                        'Develop new advisory services leveraging AI insights',
                        'Consider building custom AI agents for firm-specific workflows',
                        'Position the firm as a thought leader in AI-enabled accounting',
                      ],
                    },
                  ].map((phase, idx) => (
                    <div key={idx} className="bg-gradient-to-r from-slate-50 to-blue-50 rounded-2xl p-6 border border-slate-200">
                      <h4 className="text-lg font-bold text-slate-900 mb-4">{phase.phase}</h4>
                      <ul className="space-y-2">
                        {phase.items.map((item, i) => (
                          <li key={i} className="flex items-start">
                            <CheckCircle2 className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                            <span className="text-slate-700">{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* Conclusion */}
            <section className="mb-16">
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                  <Lightbulb className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-3xl font-display font-bold text-slate-900">
                  Conclusion: The Future Is Already Here
                </h2>
              </div>

              <div className="prose prose-lg max-w-none text-slate-600">
                <p>
                  The transformation I've described isn't a prediction about some distant future—it's happening
                  now. Firms that recognize this and act accordingly will find themselves with a significant
                  competitive advantage. Those that wait will find the gap increasingly difficult to close.
                </p>
                <p>
                  At its core, this transformation is about returning CPAs to what our profession was always meant
                  to be: trusted advisors who bring insight, judgment, and integrity to our clients' most important
                  financial decisions. AI handles the mechanics so we can focus on the meaning.
                </p>
                <p>
                  The firms that will lead our profession in the coming decade won't be defined by their size
                  or their legacy. They'll be defined by their willingness to embrace AI as a partner in
                  delivering exceptional client service—and their commitment to using that technology responsibly,
                  ethically, and in service of the public interest that has always been our profession's
                  highest calling.
                </p>
              </div>
            </section>

            {/* Author Bio */}
            <div className="bg-gradient-to-r from-slate-50 to-blue-50 rounded-2xl p-8 border border-slate-200">
              <div className="flex items-start space-x-6">
                <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-2xl flex-shrink-0">
                  JT
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">Jonathan Toroni, CPA</h3>
                  <p className="text-slate-600 mb-4">
                    Jonathan Toroni is the Founder and CEO of Aura Audit AI. With nearly two decades of experience
                    in public accounting, he founded Aura to bring the transformative power of artificial intelligence
                    to CPA firms of all sizes. Jonathan is a frequent speaker on AI in accounting and serves on
                    several industry advisory boards focused on emerging technology in the profession.
                  </p>
                  <div className="flex space-x-4">
                    <a href="#" className="text-slate-400 hover:text-blue-600 transition-colors">
                      <Linkedin className="w-5 h-5" />
                    </a>
                    <a href="#" className="text-slate-400 hover:text-blue-600 transition-colors">
                      <Twitter className="w-5 h-5" />
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="mt-12 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-center text-white">
              <h3 className="text-2xl font-bold mb-4">Ready to Transform Your Practice?</h3>
              <p className="text-white/90 mb-6 max-w-2xl mx-auto">
                See how Aura Audit AI can help your firm embrace the AI revolution.
              </p>
              <Link
                href="/#demo"
                className="inline-flex items-center px-8 py-4 bg-white text-slate-900 font-semibold rounded-xl hover:shadow-2xl transition-all"
              >
                Schedule Your Demo
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
            </div>

            {/* Related Posts */}
            <div className="mt-16">
              <h3 className="text-2xl font-bold text-slate-900 mb-8">Related Articles</h3>
              <div className="grid md:grid-cols-2 gap-6">
                {[
                  {
                    title: 'The Future of R&D Tax Credits: AI-Powered Studies',
                    excerpt: 'How artificial intelligence is making R&D tax credit studies faster and more accurate.',
                    category: 'Tax Credits',
                  },
                  {
                    title: 'Building Trust: Our Approach to AI Explainability',
                    excerpt: 'Why we believe every AI recommendation should come with a clear explanation.',
                    category: 'AI & Technology',
                  },
                ].map((post, idx) => (
                  <Link key={idx} href="/blog" className="group">
                    <div className="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-lg transition-all">
                      <span className="text-xs font-medium text-blue-600">{post.category}</span>
                      <h4 className="text-lg font-bold text-slate-900 mt-2 mb-2 group-hover:text-blue-600 transition-colors">
                        {post.title}
                      </h4>
                      <p className="text-slate-600 text-sm">{post.excerpt}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </article>

      <Footer />
    </main>
  )
}
