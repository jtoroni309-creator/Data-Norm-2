import type { Metadata } from 'next'
import './globals.css'

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://aura.toroniandcompany.com'

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: 'Aura Audit AI - Intelligent Audit Automation for CPA Firms',
    template: '%s | Aura Audit AI'
  },
  description: 'End-to-end audit automation platform that catches what humans miss. AI-powered audit intelligence for CPA firms. 30-50% faster engagements with complete PCAOB compliance.',
  keywords: [
    'audit automation',
    'CPA software',
    'audit AI',
    'accounting automation',
    'audit platform',
    'CPA firm software',
    'financial audit',
    'PCAOB compliance',
    'audit technology',
    'AI auditing',
    'fraud detection',
    'audit analytics',
    'engagement management'
  ],
  authors: [{ name: 'Aura Audit AI' }],
  creator: 'Aura Audit AI',
  publisher: 'Aura Audit AI',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: siteUrl,
    siteName: 'Aura Audit AI',
    title: 'Aura Audit AI - Intelligent Audit Automation for CPA Firms',
    description: 'End-to-end audit automation that catches what humans miss. 30-50% faster engagements with AI-powered intelligence.',
    images: [
      {
        url: '/images/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Aura Audit AI Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Aura Audit AI - Intelligent Audit Automation',
    description: 'AI-powered audit platform for CPA firms. 30-50% faster engagements.',
    images: ['/images/twitter-image.png'],
    creator: '@auraauditai',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
    yandex: 'your-yandex-verification-code',
  },
  alternates: {
    canonical: siteUrl,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'SoftwareApplication',
              name: 'Aura Audit AI',
              applicationCategory: 'BusinessApplication',
              operatingSystem: 'Web',
              offers: {
                '@type': 'Offer',
                price: '0',
                priceCurrency: 'USD',
              },
              aggregateRating: {
                '@type': 'AggregateRating',
                ratingValue: '4.9',
                ratingCount: '127',
              },
              description: 'AI-powered audit automation platform for CPA firms',
            }),
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Organization',
              name: 'Aura Audit AI',
              url: siteUrl,
              logo: `${siteUrl}/images/logo.png`,
              description: 'Enterprise-grade audit automation platform for CPA firms',
              sameAs: [
                'https://twitter.com/auraauditai',
                'https://linkedin.com/company/auraauditai',
                'https://github.com/auraauditai',
              ],
            }),
          }}
        />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
