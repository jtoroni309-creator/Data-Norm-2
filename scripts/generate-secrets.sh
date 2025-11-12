#!/bin/bash
################################################################################
# Aura Audit AI - Secure Secrets Generator
#
# Generates cryptographically secure secrets for production deployment
#
# Usage:
#   ./scripts/generate-secrets.sh [environment]
#
# Arguments:
#   environment - Target environment (development, staging, production)
#                 Default: development
#
# Output:
#   Creates .env.[environment] file with generated secrets
#
# WARNING: Store production secrets in Azure Key Vault!
#          DO NOT commit .env.production to version control!
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Environment (default to development)
ENVIRONMENT="${1:-development}"
OUTPUT_FILE=".env.${ENVIRONMENT}"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Aura Audit AI - Secrets Generator${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "Environment: ${GREEN}${ENVIRONMENT}${NC}"
echo -e "Output file: ${GREEN}${OUTPUT_FILE}${NC}"
echo ""

# Check if file already exists
if [ -f "$OUTPUT_FILE" ]; then
    echo -e "${YELLOW}⚠️  Warning: $OUTPUT_FILE already exists!${NC}"
    read -p "Overwrite existing file? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Aborted${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}Generating secure secrets...${NC}"
echo ""

# Generate secrets using OpenSSL
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
MASTER_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
MINIO_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Generate Fernet key for Airflow (must be 32 url-safe base64-encoded bytes)
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "$(openssl rand -base64 32)")

# Generate Airflow webserver secret
AIRFLOW_SECRET=$(openssl rand -hex 32)

# Create .env file
cat > "$OUTPUT_FILE" << EOF
################################################################################
# Aura Audit AI - Environment Configuration
# Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
# Environment: ${ENVIRONMENT}
#
# ⚠️  SECURITY WARNING ⚠️
# This file contains sensitive credentials!
# - DO NOT commit to version control
# - DO NOT share via email or chat
# - Store production secrets in Azure Key Vault
# - Rotate secrets every 90 days
################################################################################

# ========================================
# General Settings
# ========================================
ENVIRONMENT=${ENVIRONMENT}
DEBUG=$([ "$ENVIRONMENT" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$ENVIRONMENT" = "development" ] && echo "DEBUG" || echo "INFO")

# ========================================
# Database Configuration (PostgreSQL)
# ========================================
POSTGRES_USER=atlas
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=atlas
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Connection string with SSL
DATABASE_URL=postgresql://atlas:${POSTGRES_PASSWORD}@db:5432/atlas$([ "$ENVIRONMENT" != "development" ] && echo "?sslmode=require" || echo "")

# ========================================
# Redis Configuration
# ========================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# ========================================
# Object Storage (MinIO/S3)
# ========================================
MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}

S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minio
S3_SECRET_KEY=${MINIO_PASSWORD}
S3_BUCKET=workpapers
S3_WORM_BUCKET=atlas-worm
S3_USE_SSL=false

# ========================================
# Authentication & Security
# ========================================
# JWT Configuration
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=480
REFRESH_TOKEN_EXPIRATION_DAYS=30

# Encryption Keys
ENCRYPTION_KEY=${ENCRYPTION_KEY}
MASTER_KEY=${MASTER_KEY}

# OIDC/OAuth (optional - configure for production SSO)
OIDC_ENABLED=false
# OIDC_PROVIDER_URL=https://login.microsoftonline.com/{tenant_id}/v2.0
# OIDC_CLIENT_ID=your_client_id
# OIDC_CLIENT_SECRET=your_client_secret
# OIDC_REDIRECT_URI=https://api.aura-audit-ai.com/auth/callback

# ========================================
# Airflow Configuration
# ========================================
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://atlas:${POSTGRES_PASSWORD}@db:5432/airflow
AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}
AIRFLOW__CORE__LOAD_EXAMPLES=false
AIRFLOW__WEBSERVER__SECRET_KEY=${AIRFLOW_SECRET}

# ========================================
# OpenAI API Configuration
# ========================================
# IMPORTANT: Replace with your actual OpenAI API key
OPENAI_API_KEY=sk-placeholder-replace-with-real-key
OPENAI_CHAT_MODEL=gpt-4-turbo-2024-04-09
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.1

# ========================================
# Accounting Integrations
# ========================================
# QuickBooks Online (get from https://developer.intuit.com)
QBO_CLIENT_ID=placeholder
QBO_CLIENT_SECRET=placeholder
QBO_REDIRECT_URI=http://localhost:8000/api/integrations/quickbooks/callback

# Xero (get from https://developer.xero.com)
XERO_CLIENT_ID=placeholder
XERO_CLIENT_SECRET=placeholder
XERO_REDIRECT_URI=http://localhost:8000/api/integrations/xero/callback

# NetSuite
NETSUITE_ACCOUNT_ID=placeholder
NETSUITE_CONSUMER_KEY=placeholder
NETSUITE_CONSUMER_SECRET=placeholder
NETSUITE_TOKEN_ID=placeholder
NETSUITE_TOKEN_SECRET=placeholder

# ========================================
# Third-Party Services
# ========================================
# DocuSign (get from https://developers.docusign.com)
DOCUSIGN_INTEGRATION_KEY=placeholder
DOCUSIGN_SECRET_KEY=placeholder
DOCUSIGN_ACCOUNT_ID=placeholder
DOCUSIGN_USER_ID=placeholder
DOCUSIGN_BASE_URL=https://demo.docusign.net/restapi
DOCUSIGN_PRIVATE_KEY_PATH=/secrets/docusign_private_key.pem

# Stripe (get from https://dashboard.stripe.com/apikeys)
STRIPE_API_KEY=$([ "$ENVIRONMENT" = "production" ] && echo "sk_live_placeholder" || echo "sk_test_placeholder")
STRIPE_PUBLISHABLE_KEY=$([ "$ENVIRONMENT" = "production" ] && echo "pk_live_placeholder" || echo "pk_test_placeholder")
STRIPE_WEBHOOK_SECRET=whsec_placeholder

# Plaid (get from https://dashboard.plaid.com)
PLAID_CLIENT_ID=placeholder
PLAID_SECRET=placeholder
PLAID_ENVIRONMENT=$([ "$ENVIRONMENT" = "production" ] && echo "production" || echo "sandbox")

# SendGrid (get from https://app.sendgrid.com)
SENDGRID_API_KEY=SG.placeholder
SENDGRID_FROM_EMAIL=noreply@aura-audit-ai.com
SENDGRID_FROM_NAME=Aura Audit AI

# ========================================
# Application Settings
# ========================================
# CORS Configuration
CORS_ORIGINS=$([ "$ENVIRONMENT" = "production" ] && echo "https://aura-audit-ai.com,https://app.aura-audit-ai.com,https://admin.aura-audit-ai.com" || echo "http://localhost:3000,http://localhost:5173,http://localhost:3001")

# Cookie Domain (for cross-subdomain authentication)
COOKIE_DOMAIN=$([ "$ENVIRONMENT" = "production" ] && echo ".aura-audit-ai.com" || echo "")

# ========================================
# Monitoring & Observability
# ========================================
# Sentry (optional)
SENTRY_DSN=
SENTRY_ENVIRONMENT=${ENVIRONMENT}
SENTRY_TRACES_SAMPLE_RATE=$([ "$ENVIRONMENT" = "production" ] && echo "0.1" || echo "1.0")

# Azure Application Insights (optional)
APPINSIGHTS_INSTRUMENTATION_KEY=
APPINSIGHTS_CONNECTION_STRING=

# OpenTelemetry
OTEL_ENABLED=false
OTEL_SERVICE_NAME=atlas
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318

# ========================================
# Feature Flags
# ========================================
FEATURE_EDGAR_SCRAPING=true
FEATURE_AI_DISCLOSURES=true
FEATURE_FRAUD_DETECTION=true
FEATURE_REG_AB_AUDIT=true
FEATURE_MULTI_TENANT=true
FEATURE_E_SIGNATURE=true

# ========================================
# Compliance & Retention
# ========================================
WORM_RETENTION_YEARS=7
AUDIT_LOG_RETENTION_DAYS=2555
KEY_ROTATION_DAYS=90
SESSION_TIMEOUT_MINUTES=30

# ========================================
# Performance & Scaling
# ========================================
MAX_WORKERS=4
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
REDIS_POOL_SIZE=50
CACHE_TTL_SECONDS=3600

# ========================================
# EDGAR Configuration
# ========================================
EDGAR_BASE_URL=https://data.sec.gov
EDGAR_USER_AGENT=Aura Audit AI contact@aura-audit-ai.com
EDGAR_RATE_LIMIT_REQUESTS=10
EDGAR_RATE_LIMIT_PERIOD=1

EOF

# Set secure permissions
chmod 600 "$OUTPUT_FILE"

echo -e "${GREEN}✅ Secrets generated successfully!${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚠️  IMPORTANT SECURITY REMINDERS ⚠️${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "1. ${RED}DO NOT${NC} commit ${OUTPUT_FILE} to version control"
echo -e "2. Store production secrets in ${BLUE}Azure Key Vault${NC}"
echo -e "3. Replace placeholder values for third-party services:"
echo -e "   - OPENAI_API_KEY"
echo -e "   - DOCUSIGN_* credentials"
echo -e "   - STRIPE_* credentials"
echo -e "   - QBO_*, XERO_*, NETSUITE_* credentials"
echo -e "4. Rotate all secrets every ${BLUE}90 days${NC}"
echo -e "5. Use different secrets for each environment"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo -e "1. Review and update ${OUTPUT_FILE}"
echo -e "2. Replace placeholder values with actual credentials"
echo -e "3. For production: Upload secrets to Azure Key Vault"
echo -e "4. Start services: ${BLUE}docker-compose --env-file ${OUTPUT_FILE} up${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Show generated secrets summary (for verification)
if [ "$ENVIRONMENT" != "production" ]; then
    echo ""
    echo -e "${BLUE}Generated Secrets Summary (for verification):${NC}"
    echo -e "  JWT_SECRET: ${GREEN}${JWT_SECRET:0:16}...${NC} (64 chars)"
    echo -e "  ENCRYPTION_KEY: ${GREEN}${ENCRYPTION_KEY:0:16}...${NC} (64 chars)"
    echo -e "  POSTGRES_PASSWORD: ${GREEN}${POSTGRES_PASSWORD:0:8}...${NC} (25 chars)"
    echo ""
fi
