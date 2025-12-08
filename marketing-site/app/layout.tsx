import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  metadataBase: new URL('https://auraai.io'),
  title: {
    default: 'Aura AI - Intelligent Audit Automation for CPA Firms',
    template: '%s | Aura AI'
  },
  description: 'End-to-end audit automation platform that catches what humans miss. AI-powered audit intelligence for CPA firms. 30-50% faster engagements with complete PCAOB compliance. SOC compliance, R&D tax credits, and financial analysis.',
  keywords: [
    // Primary keywords
    'audit automation',
    'CPA software',
    'audit AI',
    'AI auditing',
    'accounting automation',
    'audit platform',
    // Service-specific keywords
    'R&D tax credit software',
    'R&D tax credit automation',
    'SOC compliance platform',
    'SOC 1 SOC 2 SOC 3',
    'financial statement analysis',
    'ratio analysis software',
    // Industry keywords
    'CPA firm software',
    'financial audit',
    'PCAOB compliance',
    'audit technology',
    'fraud detection AI',
    'audit analytics',
    'engagement management',
    // AI-specific keywords
    'AI agents accounting',
    'custom AI agents',
    'machine learning audit',
    'intelligent automation CPA',
    // Long-tail keywords
    'automated audit workpapers',
    'AI-powered fraud detection',
    'audit risk assessment AI',
    'financial ratio calculator',
    'R&D four-part test automation',
    'SOC examination platform',
  ],
  authors: [{ name: 'Aura AI', url: 'https://auraai.io' }],
  creator: 'Aura AI',
  publisher: 'Aura AI',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  category: 'Business Software',
  classification: 'Audit Automation Platform',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://auraai.io',
    siteName: 'Aura AI',
    title: 'Aura AI - Intelligent Audit Automation for CPA Firms',
    description: 'End-to-end audit automation that catches what humans miss. 30-50% faster engagements with AI-powered intelligence. SOC compliance, R&D tax credits, and financial analysis.',
    images: [
      {
        url: '/images/og-image.svg',
        width: 1200,
        height: 630,
        alt: 'Aura AI - Intelligent Audit Automation Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Aura AI - Intelligent Audit Automation',
    description: 'AI-powered audit platform for CPA firms. 30-50% faster engagements with complete compliance.',
    images: ['/images/twitter-image.svg'],
    creator: '@aaboraai',
    site: '@auraai',
  },
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      noimageindex: false,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
    yandex: 'your-yandex-verification-code',
    other: {
      'msvalidate.01': 'your-bing-verification-code',
    },
  },
  alternates: {
    canonical: 'https://auraai.io',
    languages: {
      'en-US': 'https://auraai.io',
    },
  },
  other: {
    'apple-mobile-web-app-capable': 'yes',
    'apple-mobile-web-app-status-bar-style': 'default',
    'apple-mobile-web-app-title': 'Aura AI',
  },
}

// Comprehensive structured data for SEO
const structuredData = {
  organization: {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': 'https://auraai.io/#organization',
    name: 'Aura AI',
    alternateName: 'Aura AI Platform',
    url: 'https://auraai.io',
    logo: {
      '@type': 'ImageObject',
      url: 'https://auraai.io/logo.svg',
      width: 200,
      height: 56,
    },
    description: 'Enterprise-grade AI-powered audit automation platform for CPA firms. Comprehensive solutions for audits, SOC compliance, R&D tax credits, and financial analysis.',
    foundingDate: '2024',
    address: {
      '@type': 'PostalAddress',
      addressLocality: 'San Francisco',
      addressRegion: 'CA',
      addressCountry: 'US',
    },
    contactPoint: [
      {
        '@type': 'ContactPoint',
        telephone: '+1-888-AURA-AI',
        contactType: 'sales',
        availableLanguage: 'English',
      },
      {
        '@type': 'ContactPoint',
        email: 'support@auraaudit.ai',
        contactType: 'customer support',
        availableLanguage: 'English',
      },
    ],
    sameAs: [
      'https://twitter.com/auraauditai',
      'https://linkedin.com/company/auraauditai',
      'https://github.com/auraauditai',
      'https://www.youtube.com/@auraauditai',
    ],
  },
  softwareApplication: {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    '@id': 'https://auraaudit.ai/#software',
    name: 'Aura Audit AI',
    applicationCategory: 'BusinessApplication',
    applicationSubCategory: 'Audit Automation Software',
    operatingSystem: 'Web-based (Cloud)',
    offers: {
      '@type': 'AggregateOffer',
      lowPrice: '299',
      highPrice: '999',
      priceCurrency: 'USD',
      offerCount: 3,
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.9',
      ratingCount: '127',
      bestRating: '5',
      worstRating: '1',
    },
    description: 'AI-powered audit automation platform for CPA firms with SOC compliance, R&D tax credits, and financial analysis capabilities.',
    featureList: [
      'AI-Powered Audit Automation',
      'SOC 1, 2, 3 Compliance',
      'R&D Tax Credit Studies',
      'Financial Statement Analysis',
      'Custom AI Agents',
      'Fraud Detection',
      'PCAOB Compliance',
    ],
    screenshot: 'https://auraaudit.ai/images/platform-screenshot.png',
    softwareVersion: '2.0',
    releaseNotes: 'https://auraaudit.ai/changelog',
    provider: {
      '@type': 'Organization',
      name: 'Aura Audit AI',
    },
  },
  website: {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': 'https://auraaudit.ai/#website',
    name: 'Aura Audit AI',
    url: 'https://auraaudit.ai',
    publisher: {
      '@id': 'https://auraaudit.ai/#organization',
    },
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: 'https://auraaudit.ai/search?q={search_term_string}',
      },
      'query-input': 'required name=search_term_string',
    },
  },
  professionalService: {
    '@context': 'https://schema.org',
    '@type': 'ProfessionalService',
    '@id': 'https://auraaudit.ai/#service',
    name: 'Aura Audit AI Services',
    provider: {
      '@id': 'https://auraaudit.ai/#organization',
    },
    serviceType: [
      'AI-Powered Audit Automation',
      'SOC Compliance Examination',
      'R&D Tax Credit Studies',
      'Financial Statement Analysis',
      'Custom AI Agent Development',
    ],
    areaServed: {
      '@type': 'Country',
      name: 'United States',
    },
    hasOfferCatalog: {
      '@type': 'OfferCatalog',
      name: 'Aura Audit AI Services',
      itemListElement: [
        {
          '@type': 'Offer',
          itemOffered: {
            '@type': 'Service',
            name: 'AI-Powered Audits',
            description: 'Complete audit automation with AI analysis, fraud detection, and PCAOB compliance.',
            url: 'https://auraaudit.ai/services/ai-audit',
          },
        },
        {
          '@type': 'Offer',
          itemOffered: {
            '@type': 'Service',
            name: 'R&D Tax Credit Studies',
            description: 'AI-powered R&D tax credit qualification and documentation for maximum credits.',
            url: 'https://auraaudit.ai/services/rd-tax-credit',
          },
        },
        {
          '@type': 'Offer',
          itemOffered: {
            '@type': 'Service',
            name: 'SOC Compliance',
            description: 'SOC 1, 2, and 3 examination platform with automated control testing.',
            url: 'https://auraaudit.ai/services/soc-compliance',
          },
        },
        {
          '@type': 'Offer',
          itemOffered: {
            '@type': 'Service',
            name: 'Financial Analysis',
            description: '50+ financial ratios with industry benchmarking and trend analysis.',
            url: 'https://auraaudit.ai/services/financial-analysis',
          },
        },
        {
          '@type': 'Offer',
          itemOffered: {
            '@type': 'Service',
            name: 'AI Agents',
            description: 'Custom autonomous AI agents for any accounting workflow.',
            url: 'https://auraaudit.ai/services/ai-agents',
          },
        },
      ],
    },
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
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="dns-prefetch" href="https://www.googletagmanager.com" />

        {/* Organization Schema */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(structuredData.organization),
          }}
        />

        {/* Software Application Schema */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(structuredData.softwareApplication),
          }}
        />

        {/* Website Schema with Search Action */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(structuredData.website),
          }}
        />

        {/* Professional Service Schema */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(structuredData.professionalService),
          }}
        />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
