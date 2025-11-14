'use client'

import { useState } from 'react'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { ChevronDown, HelpCircle } from 'lucide-react'

interface FAQItem {
  question: string
  answer: string
  category: string
}

const faqs: FAQItem[] = [
  // General Questions
  {
    category: 'General',
    question: 'What is Aura Audit AI?',
    answer: 'Aura Audit AI is an enterprise-grade audit automation platform designed for CPA firms and professional auditors. We use artificial intelligence and machine learning to automate routine audit tasks including trial balance normalization, journal entry testing, analytical procedures, workpaper generation, and disclosure drafting. Our platform helps auditors complete engagements 30-50% faster while maintaining full compliance with PCAOB, AICPA, and GAAP standards.',
  },
  {
    category: 'General',
    question: 'Who is Aura Audit AI for?',
    answer: 'Aura Audit AI is designed for CPA firms of all sizes, from solo practitioners to large regional firms. Our platform is ideal for firms that want to increase efficiency, improve audit quality, reduce manual work, scale their practice, and stay competitive with modern technology. We serve over 500 CPA firms across North America.',
  },
  {
    category: 'General',
    question: 'Do I need technical expertise to use Aura Audit AI?',
    answer: 'No. Aura Audit AI is designed for auditors, not IT professionals. The platform features an intuitive interface that CPAs can learn in hours, not weeks. We provide comprehensive onboarding, training, and support to ensure your team is productive from day one. No coding or technical skills required.',
  },

  // Features & Capabilities
  {
    category: 'Features',
    question: 'What audit tasks can Aura Audit AI automate?',
    answer: 'Aura Audit AI automates: (1) Trial balance import and account mapping with 95%+ accuracy, (2) Journal entry testing and anomaly detection using AI, (3) Analytical procedures and ratio analysis, (4) Risk assessment and fraud detection, (5) Workpaper generation with AI assistance, (6) Disclosure note drafting with GAAP compliance checking, (7) Quality control gates per PCAOB/AICPA standards, (8) Document management and audit trail maintenance.',
  },
  {
    category: 'Features',
    question: 'Does Aura replace auditors?',
    answer: 'No. Aura Audit AI is a tool that augments auditor capabilities, not a replacement for professional judgment. The platform automates time-consuming manual tasks—like mapping accounts, testing transactions, and drafting standard disclosures—allowing auditors to focus on analysis, client relationships, and complex judgments. All AI-generated content must be reviewed and validated by licensed CPAs.',
  },
  {
    category: 'Features',
    question: 'What accounting systems does Aura integrate with?',
    answer: 'Aura Audit AI integrates with: QuickBooks Online and Desktop, Xero, NetSuite, Sage Intacct, SAP, Oracle Financials, Microsoft Dynamics, and generic CSV/Excel uploads. We also support XBRL imports for SEC filings and can accommodate custom integrations for enterprise clients.',
  },
  {
    category: 'Features',
    question: 'Can Aura handle different types of audits?',
    answer: 'Yes. Aura supports: Financial statement audits (GAAP), Benefit plan audits (ERISA), Review and compilation engagements, Regulation A/B audits for CMBS loans, Government and nonprofit audits, SOC 1 and SOC 2 audits, and Internal audit projects. The platform is flexible and can be customized for your firm's specific needs.',
  },

  // Compliance & Security
  {
    category: 'Compliance',
    question: 'Is Aura Audit AI PCAOB compliant?',
    answer: 'Yes. Aura Audit AI is designed to meet PCAOB standards including: AS 1215 (Audit Documentation), AS 1220 (Quality Control), AS 2110 (Risk Assessment), AS 2315 (Audit Sampling), and AS 2401 (Fraud Detection). The platform includes quality control gates that enforce compliance before binder finalization, 7-year audit documentation retention with WORM storage, and immutable audit trails for all activities.',
  },
  {
    category: 'Compliance',
    question: 'What security certifications does Aura have?',
    answer: 'Aura Audit AI maintains: SOC 2 Type II certification (Security, Availability, Confidentiality), GDPR compliance with Standard Contractual Clauses, AES-256 encryption at rest and TLS 1.3 in transit, ISO 27001-aligned security controls, and Annual third-party penetration testing. We also undergo regular security audits and maintain comprehensive incident response procedures.',
  },
  {
    category: 'Compliance',
    question: 'How is my client data protected?',
    answer: 'Client data is protected through: End-to-end encryption (AES-256 at rest, TLS 1.3 in transit), Multi-tenant architecture with logical and cryptographic isolation, Role-based access control (RBAC) with MFA required, 24/7 security monitoring and intrusion detection, SOC 2 Type II certified data centers, and 7-year retention with immutable WORM storage for audit documentation. We treat all client data as confidential and never sell or share it with third parties.',
  },
  {
    category: 'Compliance',
    question: 'Is Aura GDPR compliant?',
    answer: 'Yes. For EU clients, we provide: Standard Contractual Clauses (SCCs) for international data transfers, Data Processing Agreements (DPAs) for enterprise customers, Data Subject Rights support (access, deletion, portability), Privacy by Design and Default architecture, and Optional EU data residency (Azure West Europe). Our Data Protection Officer is available at dpo@auraaudit.ai.',
  },

  // Pricing & Plans
  {
    category: 'Pricing',
    question: 'How much does Aura Audit AI cost?',
    answer: 'Aura Audit AI offers flexible pricing based on firm size and needs: Starter Plan ($299/month) for 1-2 users with essential features, Professional Plan ($799/month) for 3-10 users with advanced features and integrations, Enterprise Plan (custom pricing) for unlimited users with dedicated support, custom integrations, and SLA guarantees. All plans include unlimited engagements, storage, and support. Contact us for a custom quote.',
  },
  {
    category: 'Pricing',
    question: 'Is there a free trial?',
    answer: 'Yes! We offer a 14-day free trial with full access to all features. No credit card required to start. During the trial, you'll have access to our support team, onboarding assistance, and sample data to explore the platform. After the trial, you can choose the plan that best fits your needs.',
  },
  {
    category: 'Pricing',
    question: 'What is included in the pricing?',
    answer: 'All plans include: Unlimited audit engagements, Unlimited data storage, AI-powered automation features, Integrations with accounting systems, Email and chat support, Regular software updates, Security and compliance features (SOC 2, encryption), and Training and onboarding. Enterprise plans also include dedicated account management, custom integrations, SLA guarantees, and priority support.',
  },

  // Implementation & Support
  {
    category: 'Implementation',
    question: 'How long does implementation take?',
    answer: 'Most firms are up and running in 1-2 weeks. Our implementation process includes: Week 1: Account setup, data migration, and team training (2-4 hours), Week 2: First engagement pilot with live support, Full rollout after successful pilot. We provide dedicated onboarding support to ensure a smooth transition.',
  },
  {
    category: 'Implementation',
    question: 'What training and support do you provide?',
    answer: 'We provide comprehensive training and support: Live onboarding sessions tailored to your firm, Video tutorials and documentation library, Email and chat support (response within 4 hours), Dedicated account manager for Enterprise plans, Quarterly check-ins and best practices reviews, Community forum for peer learning, and Regular webinars on new features.',
  },
  {
    category: 'Implementation',
    question: 'Can I migrate my existing engagements to Aura?',
    answer: 'Yes. We support migration of in-progress engagements from Excel, CCH, Thomson Reuters, Caseware, and other platforms. Our team will help you import trial balances, workpapers, and documentation. Most migrations are completed within 1-2 days per engagement.',
  },
  {
    category: 'Implementation',
    question: 'What if I need help after implementation?',
    answer: 'Support is always available: Email support: support@auraaudit.ai (4-hour response time), Chat support within the platform, Phone support for urgent issues (Enterprise plans), Knowledge base with 100+ articles, Video tutorials and webinars, and Community forum for peer support. Our goal is to ensure you're never stuck.',
  },

  // AI & Technology
  {
    category: 'Technology',
    question: 'How accurate is the AI?',
    answer: 'Our AI maintains high accuracy rates: Account mapping: 95%+ accuracy with learning from corrections, Anomaly detection: 92% precision in identifying high-risk transactions, Disclosure drafting: 90%+ GAAP compliance on first draft, Risk assessment: 88% alignment with auditor judgment. All AI output includes confidence scores and requires CPA review and validation.',
  },
  {
    category: 'Technology',
    question: 'What AI models does Aura use?',
    answer: 'Aura Audit AI uses: GPT-4 Turbo for natural language processing and disclosure drafting, Custom ML models trained on 50M+ audit transactions for anomaly detection, Proprietary account mapping algorithms with 95%+ accuracy, and Ensemble models for risk assessment and fraud detection. We continuously improve our models using anonymized, aggregated data.',
  },
  {
    category: 'Technology',
    question: 'Is my data used to train AI models?',
    answer: 'No. Your confidential client data is never used to train AI models. We only use aggregated, anonymized data that cannot identify specific clients or engagements. You maintain full ownership and control of your data. We adhere to strict data privacy standards (GDPR, SOC 2) and never share client data with third parties.',
  },
  {
    category: 'Technology',
    question: 'What happens if the AI makes a mistake?',
    answer: 'All AI-generated content must be reviewed and validated by licensed CPAs. The platform includes: Confidence scores on all AI outputs to help prioritize review, Highlight of assumptions and areas requiring judgment, Ability to override or reject AI suggestions, Complete audit trail of all changes and approvals, and Quality control gates before finalization. Auditors remain fully responsible for professional judgment.',
  },

  // Data & Privacy
  {
    category: 'Data',
    question: 'Where is my data stored?',
    answer: 'Data is stored in SOC 2 Type II certified data centers: Primary: AWS US-East-1 (United States), Alternative: Microsoft Azure (US or EU based on preference), and Enterprise customers can request specific data residency locations. All data is encrypted at rest (AES-256) and in transit (TLS 1.3).',
  },
  {
    category: 'Data',
    question: 'Can I export my data?',
    answer: 'Yes. You can export all your data at any time in multiple formats: JSON for machine-readable data, CSV for spreadsheet imports, PDF for client deliverables, and XBRL for SEC filings. Exports include engagements, workpapers, trial balances, documentation, and audit trails. No vendor lock-in—your data is always accessible.',
  },
  {
    category: 'Data',
    question: 'What happens to my data if I cancel?',
    answer: 'Upon cancellation: You have 30 days to export all your data, Data is retained in archive for 90 days (for regulatory compliance), After 90 days, data is securely deleted using DOD 5220.22-M standards, and Deletion certification provided upon request. Audit documentation subject to 7-year retention is maintained separately per PCAOB/SEC requirements.',
  },
  {
    category: 'Data',
    question: 'How long is audit documentation retained?',
    answer: 'Audit documentation is retained for 7 years per PCAOB AS 1215 and SEC 17 CFR 210.2-06. We use WORM (Write Once Read Many) storage to ensure immutability. After 7 years, documentation is securely deleted unless you request extended retention. Audit trails and QC check results are preserved throughout the retention period.',
  },
]

const categories = ['All', ...Array.from(new Set(faqs.map(faq => faq.category)))]

export default function FAQ() {
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  const filteredFAQs = selectedCategory === 'All'
    ? faqs
    : faqs.filter(faq => faq.category === selectedCategory)

  // Generate FAQ schema for SEO
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: filteredFAQs.map(faq => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  }

  return (
    <main className="min-h-screen bg-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />
      <Navigation />

      {/* Hero Section */}
      <section className="pt-32 pb-16 bg-gradient-to-br from-gray-50 via-primary-50/30 to-accent-50/30">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-600 to-accent-600 rounded-2xl mb-6">
              <HelpCircle className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Frequently Asked <span className="gradient-text">Questions</span>
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed max-w-3xl mx-auto">
              Everything you need to know about Aura Audit AI, from features and pricing to security and implementation
            </p>
          </div>
        </div>
      </section>

      {/* Category Filter */}
      <section className="py-8 bg-white border-b border-gray-200 sticky top-20 z-40">
        <div className="section-container">
          <div className="flex flex-wrap gap-3 justify-center">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-6 py-2 rounded-full font-medium transition-all ${
                  selectedCategory === category
                    ? 'bg-gradient-to-r from-primary-600 to-accent-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* FAQs */}
      <section className="py-16 bg-white">
        <div className="section-container max-w-4xl mx-auto">
          <div className="space-y-4">
            {filteredFAQs.map((faq, index) => (
              <div
                key={index}
                className="bg-white border border-gray-200 rounded-xl overflow-hidden hover:border-primary-300 transition-colors"
              >
                <button
                  onClick={() => setOpenIndex(openIndex === index ? null : index)}
                  className="w-full px-6 py-5 flex items-center justify-between text-left"
                >
                  <span className="text-lg font-semibold text-gray-900 pr-8">
                    {faq.question}
                  </span>
                  <ChevronDown
                    className={`w-6 h-6 text-primary-600 flex-shrink-0 transition-transform ${
                      openIndex === index ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                {openIndex === index && (
                  <div className="px-6 pb-5">
                    <div className="text-gray-700 leading-relaxed pt-2 border-t border-gray-100">
                      {faq.answer}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Still Have Questions CTA */}
      <section className="py-24 bg-gradient-to-br from-gray-50 to-primary-50/30">
        <div className="section-container text-center">
          <h2 className="text-3xl lg:text-4xl font-display font-bold text-gray-900 mb-6">
            Still Have Questions?
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Our team is here to help. Get in touch and we'll answer any questions you have.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/contact"
              className="px-8 py-4 bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold rounded-lg hover:shadow-2xl hover:scale-105 transition-all"
            >
              Contact Us
            </a>
            <a
              href="/#demo"
              className="px-8 py-4 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-primary-600 hover:text-primary-600 transition-all"
            >
              Request a Demo
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  )
}
