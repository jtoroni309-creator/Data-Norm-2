import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Security & Compliance',
  description: 'Aura Audit AI security and compliance certifications: SOC 2 Type II, GDPR, PCAOB standards. Enterprise-grade encryption, access controls, audit logging, and data protection measures.',
  keywords: [
    'SOC 2 Type II',
    'security certification',
    'GDPR compliance',
    'PCAOB standards',
    'audit security',
    'data encryption',
    'AES-256',
    'compliance audit',
    'security measures',
    'data protection',
  ],
  openGraph: {
    title: 'Security & Compliance - Aura Audit AI',
    description: 'Enterprise-grade security with SOC 2 Type II, GDPR, and PCAOB compliance.',
    type: 'website',
    url: 'https://auraaudit.ai/security',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Security & Compliance - Aura Audit AI',
    description: 'Enterprise-grade security and compliance certifications.',
  },
  alternates: {
    canonical: 'https://auraaudit.ai/security',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function SecurityLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
