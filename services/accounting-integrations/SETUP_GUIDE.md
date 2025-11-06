# Accounting Integrations Setup Guide

Complete guide to setting up QuickBooks and Xero integrations for Aura Audit AI.

## Prerequisites

- Python 3.9+
- QuickBooks Developer Account
- Xero Developer Account (optional, if supporting Xero)
- SSL certificate (for production webhooks)

## Step 1: QuickBooks Setup

### 1.1 Create QuickBooks App

1. Go to https://developer.intuit.com/
2. Sign in or create account
3. Click **"Create an App"**
4. Choose **"QuickBooks Online and Payments"**
5. Fill in app details:
   - **App Name**: Aura Audit AI
   - **Description**: AI-powered audit and assurance platform
   - **Category**: Accounting

### 1.2 Get Credentials

1. Go to **"Keys & OAuth"** section
2. Note your credentials:
   - **Client ID**: `ABxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Client Secret**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 1.3 Configure Redirect URIs

1. In **"Keys & OAuth"**, add redirect URIs:
   - Development: `http://localhost:8000/api/v1/integrations/quickbooks/callback`
   - Production: `https://app.auraauditai.com/api/v1/integrations/quickbooks/callback`

### 1.4 Set Scopes

Enable these scopes:
- ✅ `com.intuit.quickbooks.accounting` (read financial data)
- ✅ `com.intuit.quickbooks.payment` (optional, for payment data)

### 1.5 Configure Webhooks (Optional)

1. Go to **"Webhooks"** section
2. Add webhook URL:
   - Production: `https://app.auraauditai.com/api/v1/integrations/webhooks/quickbooks`
3. Copy webhook verification token

## Step 2: Xero Setup

### 2.1 Create Xero App

1. Go to https://developer.xero.com/
2. Sign in or create account
3. Click **"New App"**
4. Choose **"OAuth 2.0"**
5. Fill in app details:
   - **App Name**: Aura Audit AI
   - **Company URL**: https://auraauditai.com
   - **Integration type**: App Partnership

### 2.2 Get Credentials

1. Go to **"Configuration"**
2. Note your credentials:
   - **Client ID**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Client Secret**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2.3 Configure Redirect URIs

Add redirect URIs:
- Development: `http://localhost:8000/api/v1/integrations/xero/callback`
- Production: `https://app.auraauditai.com/api/v1/integrations/xero/callback`

### 2.4 Set Scopes

Enable these scopes:
- ✅ `offline_access` (refresh tokens)
- ✅ `accounting.transactions.read`
- ✅ `accounting.reports.read`
- ✅ `accounting.contacts.read`
- ✅ `accounting.settings.read`

### 2.5 Configure Webhooks (Optional)

1. Go to **"Webhooks"**
2. Add webhook URL: `https://app.auraauditai.com/api/v1/integrations/webhooks/xero`
3. Copy webhook key

## Step 3: Install Service

### 3.1 Clone Repository

```bash
cd services/accounting-integrations
```

### 3.2 Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3.3 Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment

### 4.1 Create `.env` File

```bash
cp .env.example .env
```

### 4.2 Edit Configuration

```bash
# QuickBooks Configuration
QUICKBOOKS_CLIENT_ID=ABxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
QUICKBOOKS_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
QUICKBOOKS_REDIRECT_URI=http://localhost:8000/api/v1/integrations/quickbooks/callback
QUICKBOOKS_ENVIRONMENT=sandbox  # Change to 'production' for live
QUICKBOOKS_WEBHOOK_TOKEN=your_webhook_token_here

# Xero Configuration
XERO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
XERO_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
XERO_REDIRECT_URI=http://localhost:8000/api/v1/integrations/xero/callback
XERO_WEBHOOK_KEY=your_webhook_key_here

# Security (for token encryption)
ENCRYPTION_KEY=generate_random_32_byte_key_here

# Database (optional)
DATABASE_URL=postgresql+asyncpg://user:password@localhost/aura_audit_ai

# Monitoring (optional)
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

### 4.3 Generate Encryption Key

```python
import os
import base64

# Generate random 32-byte key
key = os.urandom(32)
encryption_key = base64.b64encode(key).decode('utf-8')
print(f"ENCRYPTION_KEY={encryption_key}")
```

## Step 5: Test Connection

### 5.1 Start Service

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload --port 8000

# Production mode
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5.2 Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "accounting-integrations"
}
```

### 5.3 Test OAuth Flow (QuickBooks)

```bash
# Step 1: Initiate connection
curl -X POST http://localhost:8000/api/v1/integrations/connect \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "quickbooks_online",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
  }'

# Response includes authorization_url
# Open in browser to complete OAuth flow
```

### 5.4 Test Data Sync

After completing OAuth flow:

```bash
# Sync financial data
curl -X POST http://localhost:8000/api/v1/integrations/sync \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "your_connection_id_here",
    "data_types": ["chart_of_accounts", "balance_sheet"]
  }'
```

## Step 6: Verify Integration

### 6.1 Check Connection Status

```bash
curl http://localhost:8000/api/v1/integrations/connections/{connection_id}/status
```

### 6.2 Review Sync Jobs

```bash
curl http://localhost:8000/api/v1/integrations/connections/{tenant_id}
```

### 6.3 Verify Data

```bash
# Get normalized chart of accounts
curl http://localhost:8000/api/v1/integrations/data/{connection_id}/chart-of-accounts
```

## Step 7: Production Deployment

### 7.1 Update Environment Variables

```bash
# Change to production
QUICKBOOKS_ENVIRONMENT=production

# Update redirect URIs
QUICKBOOKS_REDIRECT_URI=https://app.auraauditai.com/api/v1/integrations/quickbooks/callback
XERO_REDIRECT_URI=https://app.auraauditai.com/api/v1/integrations/xero/callback
```

### 7.2 Configure SSL

Ensure your server has valid SSL certificate for HTTPS.

### 7.3 Deploy Service

```bash
# Using Docker
docker build -t accounting-integrations .
docker run -p 8000:8000 --env-file .env accounting-integrations

# Using systemd
sudo systemctl enable accounting-integrations
sudo systemctl start accounting-integrations
```

### 7.4 Configure Reverse Proxy (Nginx)

```nginx
upstream accounting_integrations {
    server localhost:8000;
}

server {
    listen 443 ssl;
    server_name app.auraauditai.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /api/v1/integrations/ {
        proxy_pass http://accounting_integrations;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 7.5 Setup Monitoring

```bash
# Enable Sentry for error tracking
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx

# Enable Prometheus metrics
ENABLE_METRICS=true
```

## Step 8: Configure Webhooks (Production)

### 8.1 QuickBooks Webhooks

1. In QuickBooks Developer Portal:
   - Go to **Webhooks**
   - Add URL: `https://app.auraauditai.com/api/v1/integrations/webhooks/quickbooks`
   - Select entities to monitor (Account, Invoice, etc.)
   - Save verification token

2. Update `.env`:
   ```bash
   QUICKBOOKS_WEBHOOK_TOKEN=your_verification_token
   ```

### 8.2 Xero Webhooks

1. In Xero Developer Portal:
   - Go to **Webhooks**
   - Add URL: `https://app.auraauditai.com/api/v1/integrations/webhooks/xero`
   - Save webhook key

2. Update `.env`:
   ```bash
   XERO_WEBHOOK_KEY=your_webhook_key
   ```

### 8.3 Test Webhooks

```bash
# Trigger test webhook from provider portal
# Check logs for webhook receipt

# View logs
docker logs -f accounting-integrations

# Or systemd
journalctl -u accounting-integrations -f
```

## Troubleshooting

### Issue: "OAuth connection failed"

**Solution**:
1. Verify client ID and secret are correct
2. Check redirect URI matches exactly (including http/https)
3. Ensure scopes are enabled in developer portal

### Issue: "Token expired"

**Solution**:
- Service automatically refreshes tokens
- If refresh fails, user must re-authenticate
- Check refresh token is not expired (QuickBooks: 100 days, Xero: 60 days)

### Issue: "Webhook signature verification failed"

**Solution**:
1. Verify webhook token/key is correct in `.env`
2. Check webhook URL is correct in provider portal
3. Ensure HTTPS is enabled (webhooks require SSL)

### Issue: "Rate limit exceeded"

**Solution**:
- QuickBooks: 500 req/min (production), 100 req/min (sandbox)
- Xero: 60 req/min, 5000 req/day
- Implement exponential backoff (already included in service)

### Issue: "Account mapping incorrect"

**Solution**:
```bash
# Review low-confidence mappings
curl http://localhost:8000/api/v1/integrations/mappings/{connection_id}/review?threshold=0.8

# Manually override
curl -X PUT http://localhost:8000/api/v1/integrations/mappings/override \
  -H "Content-Type: application/json" \
  -d '{
    "mapping_id": "...",
    "standard_account_type": "prepaid_expenses",
    "standard_account_category": "assets"
  }'
```

## Security Checklist

- [ ] Environment variables stored securely (not in code)
- [ ] Encryption key is random and unique
- [ ] HTTPS enabled for production
- [ ] Webhook signatures verified
- [ ] OAuth tokens encrypted at rest
- [ ] Audit logging enabled
- [ ] Rate limiting configured
- [ ] Error messages don't expose sensitive data
- [ ] Database credentials secured
- [ ] Firewall rules configured

## Next Steps

1. **Integrate with main platform**: Call integration API from audit workflows
2. **Add UI components**: Connection status, sync buttons, mapping review
3. **Enable automatic sync**: Schedule daily/hourly syncs
4. **Monitor performance**: Track sync success rates, API latency
5. **Collect feedback**: Survey users on integration experience

## Support

- **Technical Issues**: support@auraauditai.com
- **Integration Help**: integrations@auraauditai.com
- **Documentation**: https://docs.auraauditai.com/integrations

---

**Last Updated**: 2025-01-06
**Version**: 1.0.0
