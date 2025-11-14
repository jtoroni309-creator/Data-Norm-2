import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Data Processing Agreement (DPA)',
  description: 'GDPR-compliant Data Processing Agreement for Aura Audit AI enterprise customers. Standard Contractual Clauses, sub-processor information, and data protection measures for EU clients.',
  keywords: [
    'DPA',
    'data processing agreement',
    'GDPR compliance',
    'standard contractual clauses',
    'data protection',
    'sub-processors',
    'EU data transfer',
    'privacy compliance',
  ],
  openGraph: {
    title: 'Data Processing Agreement - Aura Audit AI',
    description: 'GDPR-compliant DPA with Standard Contractual Clauses for enterprise customers.',
    type: 'website',
    url: 'https://auraaudit.ai/dpa',
  },
  twitter: {
    card: 'summary',
    title: 'Data Processing Agreement - Aura Audit AI',
    description: 'GDPR-compliant DPA for enterprise customers.',
  },
  alternates: {
    canonical: 'https://auraaudit.ai/dpa',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function DPALayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
