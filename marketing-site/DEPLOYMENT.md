# Deployment Guide - Aura Audit AI Marketing Website

This guide covers deploying the marketing website to various hosting platforms.

## Table of Contents

1. [Vercel Deployment](#vercel-deployment)
2. [Netlify Deployment](#netlify-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Custom Server Deployment](#custom-server-deployment)

---

## Prerequisites

Before deploying, ensure you have:

- Node.js 18+ installed
- Git repository set up
- Environment variables configured
- Production build tested locally

```bash
# Test production build locally
npm run build
npm start
```

---

## Vercel Deployment (Recommended)

Vercel is the recommended platform as it's optimized for Next.js applications.

### Option 1: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

### Option 2: Deploy via Git Integration

1. Push your code to GitHub/GitLab/Bitbucket
2. Visit [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your repository
5. Configure:
   - Framework Preset: **Next.js**
   - Root Directory: **marketing-site**
   - Build Command: `npm run build`
   - Output Directory: `.next`
6. Add environment variables (see .env.example)
7. Click "Deploy"

### Custom Domain Setup (Vercel)

1. Go to Project Settings → Domains
2. Add your domain (e.g., auraaudit.ai)
3. Configure DNS:
   ```
   A Record: @ → 76.76.21.21
   CNAME Record: www → cname.vercel-dns.com
   ```

---

## Netlify Deployment

### Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Login
netlify login

# Initialize site
netlify init

# Deploy
netlify deploy --prod
```

### Build Settings (Netlify)

- Build command: `npm run build`
- Publish directory: `.next`
- Environment variables: Add from .env.example

### netlify.toml Configuration

Create `netlify.toml` in the root:

```toml
[build]
  command = "npm run build"
  publish = ".next"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

## AWS Deployment

### Option 1: AWS Amplify

1. Visit [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Connect your Git repository
3. Configure build settings:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: .next
       files:
         - '**/*'
     cache:
       paths:
         - node_modules/**/*
   ```
4. Deploy

### Option 2: AWS S3 + CloudFront

```bash
# Build the site
npm run build
npm run export

# Upload to S3
aws s3 sync ./out s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Option 3: AWS EC2 with PM2

```bash
# SSH into EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Clone repository
git clone https://github.com/your-org/aura-marketing-site.git
cd aura-marketing-site/marketing-site

# Install dependencies
npm ci

# Build
npm run build

# Install PM2
sudo npm install -g pm2

# Start application
pm2 start npm --name "aura-marketing" -- start

# Save PM2 configuration
pm2 save
pm2 startup
```

---

## Docker Deployment

### Dockerfile

Create `Dockerfile` in marketing-site directory:

```dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  marketing-site:
    build:
      context: ./marketing-site
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_SITE_URL=https://auraaudit.ai
    restart: unless-stopped
```

### Build and Run

```bash
# Build Docker image
docker build -t aura-marketing-site .

# Run container
docker run -p 3000:3000 aura-marketing-site

# Using docker-compose
docker-compose up -d
```

---

## Custom Server Deployment

### Using Node.js

```bash
# Clone and setup
git clone https://github.com/your-org/repo.git
cd marketing-site
npm ci
npm run build

# Start with PM2
pm2 start npm --name "aura-marketing" -- start
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name auraaudit.ai www.auraaudit.ai;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name auraaudit.ai www.auraaudit.ai;

    ssl_certificate /etc/letsencrypt/live/auraaudit.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/auraaudit.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

---

## Post-Deployment Checklist

After deploying, verify the following:

### Functionality
- [ ] Homepage loads correctly
- [ ] All navigation links work
- [ ] Forms submit successfully
- [ ] Demo request form works
- [ ] Contact form sends emails
- [ ] Mobile responsive design works

### SEO
- [ ] Sitemap accessible at `/sitemap.xml`
- [ ] Robots.txt accessible at `/robots.txt`
- [ ] Meta tags render correctly (view source)
- [ ] Open Graph tags present
- [ ] Twitter Cards present
- [ ] Structured data validates ([Google Rich Results Test](https://search.google.com/test/rich-results))

### Performance
- [ ] Core Web Vitals pass ([PageSpeed Insights](https://pagespeed.web.dev/))
- [ ] LCP < 2.5s
- [ ] FID < 100ms
- [ ] CLS < 0.1
- [ ] Images optimized and loading

### Security
- [ ] HTTPS enabled
- [ ] SSL certificate valid
- [ ] Security headers present
- [ ] No mixed content warnings
- [ ] CSP headers configured (if applicable)

### Analytics
- [ ] Google Analytics tracking
- [ ] Event tracking works
- [ ] Form submissions tracked
- [ ] Conversion tracking setup

### Domain & DNS
- [ ] Domain points to hosting
- [ ] WWW redirect works
- [ ] SSL certificate covers www and apex domain
- [ ] DNS propagation complete

---

## Environment Variables

Set these in your hosting platform:

```bash
NEXT_PUBLIC_SITE_URL=https://auraaudit.ai
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_CONTACT_EMAIL=hello@auraaudit.ai
NEXT_PUBLIC_API_URL=https://api.auraaudit.ai
```

---

## Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Marketing Site

on:
  push:
    branches: [main]
    paths:
      - 'marketing-site/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd marketing-site
          npm ci
      - name: Build
        run: |
          cd marketing-site
          npm run build
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          working-directory: ./marketing-site
```

---

## Monitoring & Maintenance

### Uptime Monitoring
- Use UptimeRobot or Pingdom
- Monitor: Homepage, API endpoints

### Error Tracking
- Sentry integration for error monitoring
- Monitor 404s and broken links

### Analytics
- Google Analytics for traffic
- Hotjar for user behavior
- Google Search Console for SEO

### Regular Updates
- Update dependencies monthly
- Security patches ASAP
- Content updates as needed

---

## Support

For deployment issues, contact: devops@auraaudit.ai

---

## Additional Resources

- [Next.js Deployment Documentation](https://nextjs.org/docs/deployment)
- [Vercel Documentation](https://vercel.com/docs)
- [AWS Amplify Documentation](https://docs.amplify.aws/)
- [Docker Documentation](https://docs.docker.com/)
