import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Cookie Policy',
  description: 'Learn about how Aura Audit AI uses cookies to improve your experience, provide analytics, and deliver personalized content. Manage your cookie preferences and understand your rights.',
  keywords: [
    'cookie policy',
    'cookies',
    'privacy preferences',
    'tracking',
    'analytics cookies',
    'GDPR cookies',
    'cookie consent',
  ],
  openGraph: {
    title: 'Cookie Policy - Aura Audit AI',
    description: 'How Aura Audit AI uses cookies and your cookie management options.',
    type: 'website',
    url: 'https://auraaudit.ai/cookies',
  },
  twitter: {
    card: 'summary',
    title: 'Cookie Policy - Aura Audit AI',
    description: 'How we use cookies and your management options.',
  },
  alternates: {
    canonical: 'https://auraaudit.ai/cookies',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function CookiesLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
