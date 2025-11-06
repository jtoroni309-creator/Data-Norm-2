# Aura Audit AI - Marketing Website

Professional marketing website for Aura Audit AI, an enterprise-grade audit automation platform for CPA firms.

## Features

- **Modern Design**: Built with Next.js 14, React 18, and Tailwind CSS
- **SEO Optimized**: Comprehensive meta tags, Open Graph, Twitter Cards, and structured data
- **Responsive**: Mobile-first design that works perfectly on all devices
- **Performance**: Optimized for Core Web Vitals and fast load times
- **Accessibility**: WCAG 2.1 AA compliant
- **Analytics Ready**: Easy integration with Google Analytics, Mixpanel, etc.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI**: React 18, TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Fonts**: Inter, Space Grotesk (Google Fonts)

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the website.

## Project Structure

```
marketing-site/
├── app/                    # Next.js app directory
│   ├── about/             # About page
│   ├── contact/           # Contact page
│   ├── layout.tsx         # Root layout with SEO
│   ├── page.tsx           # Home page
│   ├── globals.css        # Global styles
│   ├── sitemap.ts         # Dynamic sitemap
│   └── robots.ts          # Robots.txt
├── components/            # Reusable components
│   ├── Navigation.tsx     # Main navigation
│   └── Footer.tsx         # Site footer
├── public/                # Static assets
│   └── images/           # Images and icons
└── lib/                  # Utility functions
```

## Key Pages

- **Home** (`/`): Hero, features, benefits, testimonials, pricing, demo form
- **About** (`/about`): Company story, mission, team
- **Contact** (`/contact`): Contact form, FAQ, contact info

## SEO Features

✅ Comprehensive meta tags (title, description, keywords)
✅ Open Graph tags for social sharing
✅ Twitter Card tags
✅ Structured data (Schema.org JSON-LD)
✅ Dynamic sitemap.xml
✅ Optimized robots.txt
✅ Canonical URLs
✅ Mobile-friendly meta viewport
✅ Security headers

## Customization

### Colors

Edit `tailwind.config.ts` to customize the color palette:

```typescript
colors: {
  primary: { ... },  // Main brand color
  accent: { ... },   // Accent color
}
```

### Content

- Update page content in `app/page.tsx`, `app/about/page.tsx`, etc.
- Modify navigation links in `components/Navigation.tsx`
- Update footer content in `components/Footer.tsx`

### SEO Metadata

Update SEO metadata in `app/layout.tsx`:

```typescript
export const metadata: Metadata = {
  title: 'Your Title',
  description: 'Your Description',
  // ... more metadata
}
```

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import project to Vercel
3. Deploy automatically

### Other Platforms

```bash
# Build for production
npm run build

# The output will be in the `.next` folder
# Deploy the `.next` folder to your hosting provider
```

## Performance

This website is optimized for Core Web Vitals:

- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

## Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

## License

Proprietary - All rights reserved by Aura Audit AI

## Support

For questions or issues, contact hello@auraaudit.ai
