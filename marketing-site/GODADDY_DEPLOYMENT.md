# GoDaddy Deployment Guide - Aura Marketing Site

This guide covers deploying the Aura Audit AI marketing site to **https://aura.toroniandcompany.com** hosted on GoDaddy.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Domain Configuration](#domain-configuration)
3. [Deployment Options](#deployment-options)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ GoDaddy account with access to domain **aura.toroniandcompany.com**
- ✅ Node.js 18+ installed locally for building
- ✅ Git repository access
- ✅ FTP/SFTP credentials (if using GoDaddy hosting)
- ✅ Production environment variables configured

---

## Domain Configuration

### DNS Settings in GoDaddy

You have several deployment options with GoDaddy. The DNS configuration depends on where you'll host the site.

#### Option 1: Deploy to Vercel (Recommended)

If deploying to Vercel with GoDaddy domain:

1. Log into your GoDaddy account
2. Go to **Domain Settings** → **Manage DNS**
3. Add/Update these records:

```
Type    Name    Value                          TTL
----    ----    -----                          ---
A       @       76.76.21.21                    600
CNAME   www     cname.vercel-dns.com           600
```

#### Option 2: Deploy to Netlify with GoDaddy

For Netlify hosting:

```
Type    Name    Value                          TTL
----    ----    -----                          ---
A       @       75.2.60.5                      600
CNAME   www     [your-site].netlify.app        600
```

#### Option 3: GoDaddy Shared/VPS Hosting

For GoDaddy hosting:

```
Type    Name    Value                          TTL
----    ----    -----                          ---
A       @       [Your Server IP]               600
CNAME   www     @                              600
```

### Verify DNS Propagation

After updating DNS, verify propagation:

```bash
# Check A record
dig aura.toroniandcompany.com

# Check CNAME
dig www.aura.toroniandcompany.com

# Or use online tool
# https://dnschecker.org/
```

DNS propagation can take 24-48 hours but usually completes within 1-2 hours.

---

## Deployment Options

### Recommended: Vercel Deployment

Vercel provides the best performance for Next.js sites and is free for personal/commercial use.

#### Step 1: Build Configuration

```bash
# Navigate to marketing site directory
cd marketing-site

# Install dependencies
npm install

# Test production build locally
npm run build
npm start
```

#### Step 2: Deploy to Vercel

**Option A: Vercel CLI**

```bash
# Install Vercel CLI globally
npm i -g vercel

# Login to Vercel
vercel login

# Deploy (from marketing-site directory)
vercel

# Deploy to production
vercel --prod
```

**Option B: Vercel Git Integration**

1. Push your code to GitHub
2. Visit [vercel.com/new](https://vercel.com/new)
3. Import your repository
4. Configure:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `marketing-site`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next` (default)
5. Add environment variables from `.env.production`:
   ```
   NEXT_PUBLIC_SITE_URL=https://aura.toroniandcompany.com
   NEXT_PUBLIC_CONTACT_EMAIL=hello@toroniandcompany.com
   NEXT_PUBLIC_API_URL=https://api.aura.toroniandcompany.com
   ```
6. Click **Deploy**

#### Step 3: Add Custom Domain in Vercel

1. Go to your project in Vercel
2. Navigate to **Settings** → **Domains**
3. Add `aura.toroniandcompany.com`
4. Add `www.aura.toroniandcompany.com`
5. Vercel will provide DNS instructions (already configured above)
6. Wait for SSL certificate to be automatically provisioned

---

### Alternative: GoDaddy cPanel Hosting

If you have GoDaddy shared hosting with cPanel:

#### Step 1: Build Static Export

```bash
cd marketing-site

# Install dependencies
npm install

# Build for static export
npm run build

# The output will be in the .next folder
```

#### Step 2: Upload via FTP/File Manager

**Using File Manager:**
1. Log into GoDaddy cPanel
2. Open **File Manager**
3. Navigate to `public_html` or your domain's root directory
4. Upload the entire `.next` directory and `node_modules` (if needed)

**Using FTP:**
```bash
# Use an FTP client like FileZilla
Host: ftp.aura.toroniandcompany.com
Username: [Your GoDaddy FTP username]
Password: [Your GoDaddy FTP password]
Port: 21
```

#### Step 3: Configure Node.js Application (VPS/Dedicated)

If you have a VPS or dedicated server with Node.js support:

1. SSH into your server
2. Install Node.js 18+:
   ```bash
   curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
   sudo yum install -y nodejs
   ```
3. Clone/upload your repository
4. Install dependencies and build:
   ```bash
   cd /var/www/aura.toroniandcompany.com
   npm ci
   npm run build
   ```
5. Use PM2 to keep the app running:
   ```bash
   npm install -g pm2
   pm2 start npm --name "aura-marketing" -- start
   pm2 save
   pm2 startup
   ```
6. Configure Apache/Nginx as reverse proxy (see below)

---

## Reverse Proxy Configuration (VPS/Dedicated Only)

### Apache Configuration

Edit your Apache virtual host file:

```apache
<VirtualHost *:80>
    ServerName aura.toroniandcompany.com
    ServerAlias www.aura.toroniandcompany.com

    ProxyPreserveHost On
    ProxyPass / http://localhost:3000/
    ProxyPassReverse / http://localhost:3000/

    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"

    ErrorLog ${APACHE_LOG_DIR}/aura-error.log
    CustomLog ${APACHE_LOG_DIR}/aura-access.log combined
</VirtualHost>

# HTTPS configuration (after SSL setup)
<VirtualHost *:443>
    ServerName aura.toroniandcompany.com
    ServerAlias www.aura.toroniandcompany.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/aura.toroniandcompany.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/aura.toroniandcompany.com/privkey.pem

    ProxyPreserveHost On
    ProxyPass / http://localhost:3000/
    ProxyPassReverse / http://localhost:3000/

    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Strict-Transport-Security "max-age=63072000"
</VirtualHost>
```

Enable required modules and restart:
```bash
sudo a2enmod proxy proxy_http headers ssl
sudo systemctl restart apache2
```

---

## SSL/TLS Setup

### With Vercel (Automatic)
Vercel automatically provisions SSL certificates. No action needed!

### With GoDaddy Shared Hosting
1. Log into cPanel
2. Navigate to **SSL/TLS Status**
3. Click **Run AutoSSL** for your domain
4. Wait for certificate to be issued (usually 2-5 minutes)

### With Let's Encrypt (VPS/Dedicated)

```bash
# Install Certbot
sudo yum install certbot python3-certbot-apache

# Obtain certificate
sudo certbot --apache -d aura.toroniandcompany.com -d www.aura.toroniandcompany.com

# Test auto-renewal
sudo certbot renew --dry-run

# Auto-renewal is set up automatically via cron
```

---

## Post-Deployment Configuration

### 1. Verify Deployment

Check these URLs in your browser:
- ✅ https://aura.toroniandcompany.com
- ✅ https://www.aura.toroniandcompany.com
- ✅ https://aura.toroniandcompany.com/sitemap.xml
- ✅ https://aura.toroniandcompany.com/robots.txt

### 2. Test Functionality

- [ ] Homepage loads correctly
- [ ] All navigation links work
- [ ] Forms submit properly
- [ ] Images load correctly
- [ ] Mobile responsive design
- [ ] SSL certificate is valid (green padlock)

### 3. Configure Redirects

Ensure www redirects to non-www (or vice versa):

**In Vercel:** Automatically handled

**In Apache (.htaccess):**
```apache
RewriteEngine On
RewriteCond %{HTTP_HOST} ^www\.aura\.toroniandcompany\.com [NC]
RewriteRule ^(.*)$ https://aura.toroniandcompany.com/$1 [L,R=301]
```

### 4. Set Up Monitoring

- **Uptime Monitoring**: Use UptimeRobot or Pingdom
- **Analytics**: Add Google Analytics tracking code
- **Error Tracking**: Consider Sentry for error monitoring

### 5. Performance Optimization

Test your site performance:
- [Google PageSpeed Insights](https://pagespeed.web.dev/)
- [GTmetrix](https://gtmetrix.com/)
- [WebPageTest](https://www.webpagetest.org/)

Target metrics:
- Lighthouse Score: 90+
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1

---

## Environment Variables Configuration

Ensure these variables are set in your hosting environment:

### For Vercel/Netlify
Add these in the dashboard under Environment Variables:

```bash
NEXT_PUBLIC_SITE_URL=https://aura.toroniandcompany.com
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_CONTACT_EMAIL=hello@toroniandcompany.com
NEXT_PUBLIC_API_URL=https://api.aura.toroniandcompany.com
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

### For VPS/Dedicated Server
Create `.env.production` file (already created in this repo):

```bash
cp .env.production .env.local
# Edit values as needed
```

---

## Troubleshooting

### Issue: DNS Not Resolving

**Solution:**
```bash
# Clear DNS cache (local machine)
# Windows
ipconfig /flushdns

# Mac
sudo dscacheutil -flushcache

# Linux
sudo systemd-resolve --flush-caches

# Wait for DNS propagation (up to 48 hours)
```

### Issue: SSL Certificate Error

**Solution:**
- Verify DNS is pointing correctly
- Wait 10-15 minutes after DNS changes
- For Vercel: Remove and re-add domain
- For Let's Encrypt: Run `sudo certbot renew --force-renewal`

### Issue: 404 Errors on Routes

**Solution:**
- Ensure proper routing configuration
- For Apache: Check `.htaccess` rewrite rules
- For Nginx: Verify `try_files` directive
- For Vercel/Netlify: Should work automatically

### Issue: Environment Variables Not Working

**Solution:**
- Verify variables are prefixed with `NEXT_PUBLIC_`
- Rebuild the application after adding variables
- For Vercel: Redeploy after adding variables
- Check browser console for undefined values

### Issue: Slow Performance

**Solution:**
- Enable CDN (Vercel/Netlify include this)
- Optimize images (already configured)
- Enable caching headers
- Use a performance monitoring tool

---

## GoDaddy Support Resources

- **GoDaddy Support**: https://www.godaddy.com/help
- **DNS Management**: https://www.godaddy.com/help/manage-dns-680
- **SSL Certificates**: https://www.godaddy.com/help/ssl-certificates-9637
- **Node.js Hosting**: https://www.godaddy.com/help/nodejs-15601

---

## Quick Deployment Checklist

### Pre-Deployment
- [ ] Domain purchased and accessible in GoDaddy
- [ ] DNS configured correctly
- [ ] Environment variables prepared
- [ ] Local build tested successfully
- [ ] Git repository up to date

### Deployment
- [ ] Site deployed to hosting platform
- [ ] Custom domain added
- [ ] SSL certificate active
- [ ] Environment variables configured

### Post-Deployment
- [ ] Site accessible via https://aura.toroniandcompany.com
- [ ] www redirect working
- [ ] All pages load correctly
- [ ] Forms functioning
- [ ] Analytics tracking
- [ ] Sitemap accessible
- [ ] Robots.txt configured
- [ ] Performance tested
- [ ] Mobile responsive verified
- [ ] Monitoring set up

---

## Next Steps

After successful deployment:

1. **Set up Google Analytics** (update `NEXT_PUBLIC_GA_ID`)
2. **Configure contact forms** (update `NEXT_PUBLIC_FORM_ENDPOINT`)
3. **Add Google Search Console** for SEO monitoring
4. **Set up backup system** (if self-hosted)
5. **Monitor uptime and performance**
6. **Plan regular updates** (security patches, content updates)

---

## Support

For deployment assistance:
- **Technical Support**: devops@toroniandcompany.com
- **General Inquiries**: hello@toroniandcompany.com

---

## Additional Resources

- [Next.js Deployment Documentation](https://nextjs.org/docs/deployment)
- [Vercel Documentation](https://vercel.com/docs)
- [GoDaddy Help Center](https://www.godaddy.com/help)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
