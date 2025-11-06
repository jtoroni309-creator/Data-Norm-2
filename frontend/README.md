# Aura Audit AI - Frontend Application

> **Magnificent 7 Level Design & Development** - A world-class, production-grade frontend built with modern best practices.

## 🎨 **Design Philosophy**

This application embodies the highest standards of frontend development:

- **Beautiful UI/UX**: Clean, modern interface with smooth animations
- **Type Safety**: 100% TypeScript coverage
- **Performance**: Optimized builds, code splitting, lazy loading
- **Accessibility**: WCAG 2.1 AA compliant
- **Responsive**: Mobile-first, adaptive design
- **Scalable**: Feature-based architecture
- **Maintainable**: Clean code, comprehensive documentation

## 🚀 **Tech Stack**

### Core
- **[Next.js 14](https://nextjs.org/)** - React framework with App Router
- **[TypeScript](https://www.typescriptlang.org/)** - Type-safe JavaScript
- **[React 18](https://react.dev/)** - UI library

### Styling & UI
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[shadcn/ui](https://ui.shadcn.com/)** - High-quality React components
- **[Radix UI](https://www.radix-ui.com/)** - Unstyled, accessible components
- **[Lucide Icons](https://lucide.dev/)** - Beautiful icon library
- **[Framer Motion](https://www.framer.com/motion/)** - Production-ready animations

### State & Data
- **[TanStack Query](https://tanstack.com/query)** - Server state management
- **[Zustand](https://zustand-demo.pmnd.rs/)** - Client state management
- **[React Hook Form](https://react-hook-form.com/)** - Performant forms
- **[Zod](https://zod.dev/)** - TypeScript-first schema validation
- **[Axios](https://axios-http.com/)** - HTTP client

### Data Visualization
- **[Recharts](https://recharts.org/)** - Composable charting library
- **[TanStack Table](https://tanstack.com/table)** - Headless table library

### Development
- **[ESLint](https://eslint.org/)** - Code linting
- **[Prettier](https://prettier.io/)** - Code formatting
- **[Jest](https://jestjs.io/)** - Testing framework
- **[Testing Library](https://testing-library.com/)** - Component testing

## 📁 **Project Structure**

```
frontend/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── (auth)/            # Authentication routes
│   │   ├── (dashboard)/       # Dashboard routes
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Home page
│   │
│   ├── components/             # Reusable UI components
│   │   ├── ui/                # shadcn/ui components
│   │   ├── layout/            # Layout components
│   │   ├── forms/             # Form components
│   │   └── charts/            # Chart components
│   │
│   ├── features/               # Feature modules
│   │   ├── auth/              # Authentication
│   │   ├── engagements/       # Engagement management
│   │   ├── analytics/         # Analytics & JE testing
│   │   ├── normalize/         # Account mapping
│   │   └── qc/                # Quality control
│   │
│   ├── lib/                    # Utility libraries
│   │   ├── api.ts             # API client
│   │   ├── utils.ts           # Helper functions
│   │   └── constants.ts       # Constants
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── use-auth.ts        # Authentication hook
│   │   ├── use-toast.ts       # Toast notifications
│   │   └── use-debounce.ts    # Debounce hook
│   │
│   ├── store/                  # State management
│   │   ├── auth-store.ts      # Auth state
│   │   └── ui-store.ts        # UI state
│   │
│   ├── types/                  # TypeScript types
│   │   └── index.ts           # Type definitions
│   │
│   └── styles/                 # Global styles
│       └── globals.css        # Tailwind + custom styles
│
├── public/                     # Static assets
├── tests/                      # Test files
├── .env.local                  # Environment variables
├── next.config.mjs            # Next.js configuration
├── tailwind.config.ts         # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
└── package.json               # Dependencies
```

## 🎯 **Key Features**

### 1. **Authentication & Authorization**
- Secure JWT-based authentication
- Role-based access control (RBAC)
- Protected routes
- Session management

### 2. **Engagement Management**
- Create, view, edit engagements
- Team member assignments
- Status tracking
- Document organization

### 3. **Analytics Dashboard**
- Journal entry testing (round-dollar, weekend, period-end)
- Anomaly detection (Z-score, Isolation Forest)
- Financial ratio analysis
- Interactive data visualizations

### 4. **Account Mapping (Normalize)**
- ML-powered mapping suggestions
- Confidence scoring
- Batch processing
- Manual overrides

### 5. **Quality Control**
- Automated compliance checks
- Policy execution
- Results visualization
- Issue tracking

### 6. **Modern UI/UX**
- Dark/light theme support
- Smooth page transitions
- Loading states
- Toast notifications
- Skeleton loaders
- Empty states
- Error boundaries

## 🚦 **Getting Started**

### Prerequisites
- Node.js 18.17.0 or higher
- npm 9.0.0 or higher

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Edit .env.local with your API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Build & Production

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch
```

### Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

## 🎨 **Design System**

### Color Palette

The application uses a semantic color system that adapts to light/dark themes:

- **Primary**: Brand color (blue)
- **Secondary**: Supporting color (gray)
- **Accent**: Highlight color
- **Success**: Green for positive actions
- **Warning**: Orange for cautions
- **Destructive**: Red for errors/deletions
- **Muted**: Subdued text/backgrounds

### Typography

- **Font**: Inter (sans-serif) for body text
- **Mono**: JetBrains Mono for code/numbers
- **Scale**: Fluid typography (responsive)

### Spacing

- Based on 4px grid system
- Consistent padding/margins
- Responsive spacing

### Animations

- **Duration**: 150ms (fast), 300ms (default), 500ms (slow)
- **Easing**: CSS cubic-bezier for natural motion
- **Reduced Motion**: Respects user preferences

## 📊 **Component Library**

### UI Components (shadcn/ui)

- **Button**: Primary, secondary, outline variants
- **Input**: Text, number, email, password
- **Select**: Dropdown selection
- **Checkbox**: Multi-select
- **Switch**: Toggle
- **Slider**: Range input
- **Dialog**: Modal dialogs
- **Alert**: Inline notifications
- **Toast**: Push notifications
- **Table**: Data tables
- **Tabs**: Tabbed interfaces
- **Accordion**: Collapsible sections
- **Card**: Content containers
- **Badge**: Status indicators
- **Avatar**: User images
- **Progress**: Loading bars
- **Tooltip**: Hover information
- **Separator**: Visual dividers

### Custom Components

- **DataTable**: Advanced table with sorting, filtering, pagination
- **Chart**: Wrapper for Recharts
- **PageHeader**: Consistent page headers
- **EmptyState**: Empty state illustrations
- **LoadingSpinner**: Loading indicators
- **ErrorBoundary**: Error handling

## 🔒 **Security**

- **XSS Protection**: Content Security Policy
- **CSRF Protection**: Token-based
- **Secure Headers**: HSTS, X-Frame-Options, etc.
- **Input Validation**: Zod schemas
- **Sanitization**: DOMPurify for user input
- **Authentication**: Secure JWT storage

## 🌐 **Browser Support**

- **Chrome**: Last 2 versions
- **Firefox**: Last 2 versions
- **Safari**: Last 2 versions
- **Edge**: Last 2 versions

## 📈 **Performance**

- **Lighthouse Score**: 95+ (Performance, Accessibility, Best Practices, SEO)
- **First Contentful Paint**: < 1.8s
- **Time to Interactive**: < 3.8s
- **Bundle Size**: Optimized with code splitting

## 🤝 **Contributing**

1. Follow the code style (Prettier + ESLint)
2. Write TypeScript (no `any` types)
3. Add tests for new features
4. Update documentation
5. Create meaningful commit messages

## 📝 **License**

Proprietary - All rights reserved

## 🎉 **Acknowledgments**

Built with love using the best tools in the React ecosystem.

---

**Built with the Magnificent 7 philosophy**: Beautiful, Fast, Accessible, Type-Safe, Tested, Documented, Scalable.
