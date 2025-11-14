import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Frequently Asked Questions',
  description: 'Common questions about Aura Audit AI - pricing, features, security, compliance, implementation, and more. Get answers about our AI-powered audit automation platform for CPA firms.',
  keywords: [
    'audit software FAQ',
    'CPA software questions',
    'audit automation pricing',
    'PCAOB compliance',
    'SOC 2 security',
    'audit platform features',
    'implementation timeline',
    'audit AI questions',
  ],
  openGraph: {
    title: 'FAQ - Aura Audit AI',
    description: 'Everything you need to know about Aura Audit AI - from features and pricing to security and implementation.',
    type: 'website',
    url: 'https://auraaudit.ai/faq',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'FAQ - Aura Audit AI',
    description: 'Everything you need to know about our AI-powered audit automation platform.',
  },
  alternates: {
    canonical: 'https://auraaudit.ai/faq',
  },
}

export default function FAQLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
