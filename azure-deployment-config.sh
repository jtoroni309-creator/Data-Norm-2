#!/bin/bash
set -e

###############################################################################
# Azure Deployment Configuration Script
#
# This script configures your Azure environment for deploying Aura Audit AI
# using the provided Application Registration credentials.
#
# Prerequisites:
# - Azure CLI installed and logged in
# - Contributor access to the Azure subscription
###############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Azure credentials provided
CLIENT_ID="6d1fdc5d-580b-499d-bae8-c129af50e96e"
TENANT_ID="002fa7de-1afd-4945-86e1-79281af841ad"

# Configuration
LOCATION="${AZURE_LOCATION:-eastus}"
ENVIRONMENT="${ENVIRONMENT:-prod}"
TF_RG_NAME="aura-tfstate-rg"
TF_CONTAINER_NAME="tfstate"

echo "========================================"
echo "🚀 Aura Audit AI - Azure Deployment Setup"
echo "========================================"
echo ""
echo "Application (Client) ID: $CLIENT_ID"
echo "Tenant ID: $TENANT_ID"
echo "Location: $LOCATION"
echo "Environment: $ENVIRONMENT"
echo ""

# Function to print colored messages
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed!"
    echo ""
    echo "Please install Azure CLI:"
    echo "  https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

print_success "Azure CLI is installed"

# Login to Azure with the service principal
print_step "Logging in to Azure..."
echo ""
echo "Please ensure you have the client secret for the service principal."
read -sp "Enter the client secret: " CLIENT_SECRET
echo ""

az login --service-principal \
  --username "$CLIENT_ID" \
  --password "$CLIENT_SECRET" \
  --tenant "$TENANT_ID"

if [ $? -ne 0 ]; then
    print_error "Failed to login to Azure"
    exit 1
fi

print_success "Successfully logged in to Azure"

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
print_success "Using subscription: $SUBSCRIPTION_ID"

# Register required resource providers
print_step "Registering Azure resource providers..."
providers=(
    "Microsoft.ContainerService"
    "Microsoft.DBforPostgreSQL"
    "Microsoft.Cache"
    "Microsoft.Storage"
    "Microsoft.KeyVault"
    "Microsoft.Network"
    "Microsoft.OperationalInsights"
    "Microsoft.Insights"
    "Microsoft.ContainerRegistry"
)

for provider in "${providers[@]}"; do
    echo -n "  Registering $provider... "
    az provider register --namespace "$provider" --wait 2>/dev/null || true
    echo "done"
done

print_success "Resource providers registered"

# Create Terraform backend storage
print_step "Creating Terraform backend storage..."

TF_STORAGE_ACCOUNT="auratfstate$(date +%s)"

# Create resource group
az group create \
    --name "$TF_RG_NAME" \
    --location "$LOCATION" \
    --output none

print_success "Created resource group: $TF_RG_NAME"

# Create storage account
az storage account create \
    --resource-group "$TF_RG_NAME" \
    --name "$TF_STORAGE_ACCOUNT" \
    --sku Standard_LRS \
    --encryption-services blob \
    --location "$LOCATION" \
    --output none

print_success "Created storage account: $TF_STORAGE_ACCOUNT"

# Get storage account key
ACCOUNT_KEY=$(az storage account keys list \
    --resource-group "$TF_RG_NAME" \
    --account-name "$TF_STORAGE_ACCOUNT" \
    --query '[0].value' -o tsv)

# Create blob container
az storage container create \
    --name "$TF_CONTAINER_NAME" \
    --account-name "$TF_STORAGE_ACCOUNT" \
    --account-key "$ACCOUNT_KEY" \
    --output none

print_success "Created blob container: $TF_CONTAINER_NAME"

# Generate secrets
print_step "Generating security secrets..."

JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
MASTER_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)

# Save configuration to files
cat > terraform-backend-config.txt <<EOF
========================================
Terraform Backend Configuration
========================================
Resource Group: $TF_RG_NAME
Storage Account: $TF_STORAGE_ACCOUNT
Container: $TF_CONTAINER_NAME
Access Key: $ACCOUNT_KEY

Subscription ID: $SUBSCRIPTION_ID
========================================
EOF

cat > azure-secrets.env <<EOF
# ========================================
# Security Secrets - SAVE THESE SECURELY!
# ========================================
# Generated: $(date)

# Azure Service Principal
AZURE_CLIENT_ID=$CLIENT_ID
AZURE_TENANT_ID=$TENANT_ID
AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID

# Application Secrets
JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY
MASTER_KEY=$MASTER_KEY
POSTGRES_PASSWORD=$POSTGRES_PASSWORD

# Terraform Backend
TF_BACKEND_STORAGE_ACCOUNT=$TF_STORAGE_ACCOUNT
TF_BACKEND_ACCESS_KEY=$ACCOUNT_KEY
EOF

cat > infra/azure/terraform.tfvars <<EOF
# ===========================================
# Aura Audit AI - Azure Configuration
# ===========================================
# Auto-generated: $(date)

# General Configuration
location    = "$LOCATION"
environment = "$ENVIRONMENT"

# AKS Configuration
kubernetes_version    = "1.28"
aks_system_node_count = 3
aks_app_node_count    = 3
aks_system_node_size  = "Standard_D4s_v3"
aks_app_node_size     = "Standard_D8s_v3"

# PostgreSQL Configuration
postgres_admin_username          = "atlasadmin"
postgres_sku                     = "GP_Standard_D4s_v3"
postgres_storage_mb              = 131072  # 128 GB
postgres_high_availability       = true
postgres_standby_zone            = "2"
postgres_backup_retention_days   = 35
postgres_geo_redundant_backup    = true

# Redis Configuration
redis_sku      = "Premium"
redis_family   = "P"
redis_capacity = 1

# Storage Configuration
storage_replication_type   = "GRS"
blob_delete_retention_days = 30

# Container Registry
acr_sku             = "Premium"
acr_georeplications = ["westus2"]

# Application Gateway
appgw_sku_name  = "WAF_v2"
appgw_sku_tier  = "WAF_v2"
appgw_capacity  = 2

# Monitoring
log_retention_days = 90

# Tags
tags = {
  CostCenter  = "Engineering"
  Owner       = "Platform Team"
  Environment = "Production"
  Purpose     = "Audit AI Platform"
}
EOF

# Update backend.tf
cat > infra/azure/backend.tf <<EOF
# Terraform Backend Configuration
# Auto-generated: $(date)

terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.45"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  backend "azurerm" {
    resource_group_name  = "$TF_RG_NAME"
    storage_account_name = "$TF_STORAGE_ACCOUNT"
    container_name       = "$TF_CONTAINER_NAME"
    key                  = "aura-audit-ai.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }

  subscription_id = "$SUBSCRIPTION_ID"
  client_id       = "$CLIENT_ID"
  tenant_id       = "$TENANT_ID"
}

provider "azuread" {
  client_id = "$CLIENT_ID"
  tenant_id = "$TENANT_ID"
}
EOF

# Create .env.production
cat > .env.production <<EOF
# ===========================================
# Aura Audit AI - Production Environment
# ===========================================
# Generated: $(date)

# Environment
NODE_ENV=production
ENVIRONMENT=production

# Azure Configuration
AZURE_CLIENT_ID=$CLIENT_ID
AZURE_TENANT_ID=$TENANT_ID
AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID

# Database (will be updated after Terraform deployment)
POSTGRES_HOST=to-be-filled-after-terraform
POSTGRES_PORT=5432
POSTGRES_USER=atlasadmin
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=atlas
DATABASE_URL=postgresql+asyncpg://atlasadmin:$POSTGRES_PASSWORD@to-be-filled:5432/atlas?sslmode=require

# Redis (will be updated after Terraform deployment)
REDIS_HOST=to-be-filled-after-terraform
REDIS_PORT=6380
REDIS_PASSWORD=to-be-filled-after-terraform
REDIS_URL=rediss://:to-be-filled@to-be-filled:6380/0?ssl_cert_reqs=required

# Security
JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY
MASTER_KEY=$MASTER_KEY
SESSION_SECRET=$JWT_SECRET

# OpenAI (ADD YOUR KEY HERE)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Storage (will be updated after Terraform deployment)
AZURE_STORAGE_ACCOUNT=to-be-filled-after-terraform
AZURE_STORAGE_KEY=to-be-filled-after-terraform
AZURE_STORAGE_CONTAINER=audit-documents

# Application URLs (update with your domain)
FRONTEND_URL=https://app.yourauditsaas.com
API_URL=https://api.yourauditsaas.com
ADMIN_URL=https://admin.yourauditsaas.com

# Monitoring
LOG_LEVEL=info
ENABLE_METRICS=true
ENABLE_TRACING=true
EOF

echo ""
print_success "✅ Configuration complete!"
echo ""
echo "Files created:"
echo "  ✓ terraform-backend-config.txt"
echo "  ✓ azure-secrets.env"
echo "  ✓ infra/azure/terraform.tfvars"
echo "  ✓ infra/azure/backend.tf"
echo "  ✓ .env.production"
echo ""
print_warning "IMPORTANT: Keep these files secure! Do not commit secrets to git."
echo ""
echo "Next steps:"
echo "  1. Review the generated files"
echo "  2. Add your OpenAI API key to .env.production"
echo "  3. Deploy infrastructure:"
echo "     cd infra/azure"
echo "     terraform init"
echo "     terraform plan"
echo "     terraform apply"
echo ""
echo "  4. After Terraform completes, update .env.production with:"
echo "     - POSTGRES_HOST (from terraform output postgres_fqdn)"
echo "     - REDIS_HOST (from terraform output redis_hostname)"
echo "     - REDIS_PASSWORD (from terraform output redis_primary_key)"
echo "     - AZURE_STORAGE_ACCOUNT (from terraform output storage_account_name)"
echo "     - AZURE_STORAGE_KEY (from terraform output storage_primary_key)"
echo ""
print_success "Ready to deploy! 🚀"
