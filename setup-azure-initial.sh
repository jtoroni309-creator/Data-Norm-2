#!/bin/bash
set -e

#######################################################
# Aura Audit AI - Azure Initial Setup Script
# This script automates the first-time Azure setup
#######################################################

echo "=========================================="
echo "🚀 Aura Audit AI - Azure Initial Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOCATION="${AZURE_LOCATION:-eastus}"
ENVIRONMENT="${ENVIRONMENT:-prod}"
TF_RG_NAME="aura-tfstate-rg"
TF_CONTAINER_NAME="tfstate"

# Functions
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."

    local missing_tools=()

    if ! command_exists az; then
        missing_tools+=("Azure CLI (az)")
    fi

    if ! command_exists terraform; then
        missing_tools+=("Terraform")
    fi

    if ! command_exists kubectl; then
        missing_tools+=("kubectl")
    fi

    if ! command_exists openssl; then
        missing_tools+=("openssl")
    fi

    if [ ${#missing_tools[@]} -gt 0 ]; then
        print_error "Missing required tools:"
        for tool in "${missing_tools[@]}"; do
            echo "  - $tool"
        done
        echo ""
        echo "Please install missing tools. See AZURE_FIRST_TIME_SETUP.md for installation instructions."
        exit 1
    fi

    print_success "All required tools are installed"
}

# Check Azure login
check_azure_login() {
    print_step "Checking Azure login status..."

    if ! az account show >/dev/null 2>&1; then
        print_warning "Not logged in to Azure"
        print_step "Opening Azure login..."
        az login
    fi

    print_success "Azure login verified"

    # Show current subscription
    CURRENT_SUB=$(az account show --query name -o tsv)
    CURRENT_SUB_ID=$(az account show --query id -o tsv)
    echo ""
    echo "Current subscription: $CURRENT_SUB"
    echo "Subscription ID: $CURRENT_SUB_ID"
    echo ""

    read -p "Is this the correct subscription? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Please set the correct subscription using:"
        echo "az account set --subscription \"<subscription-name-or-id>\""
        exit 1
    fi
}

# Register resource providers
register_providers() {
    print_step "Registering Azure resource providers..."

    local providers=(
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
        az provider register --namespace "$provider" --wait >/dev/null 2>&1 || true
        echo "done"
    done

    print_success "Resource providers registered (may take a few minutes to complete)"
}

# Create Terraform backend storage
create_terraform_backend() {
    print_step "Creating Terraform backend storage..."

    # Generate unique storage account name
    TF_STORAGE_ACCOUNT="auratfstate$(date +%s)"

    # Create resource group
    print_step "Creating resource group: $TF_RG_NAME"
    az group create \
        --name "$TF_RG_NAME" \
        --location "$LOCATION" \
        --output none

    # Create storage account
    print_step "Creating storage account: $TF_STORAGE_ACCOUNT"
    az storage account create \
        --resource-group "$TF_RG_NAME" \
        --name "$TF_STORAGE_ACCOUNT" \
        --sku Standard_LRS \
        --encryption-services blob \
        --location "$LOCATION" \
        --output none

    # Get storage account key
    ACCOUNT_KEY=$(az storage account keys list \
        --resource-group "$TF_RG_NAME" \
        --account-name "$TF_STORAGE_ACCOUNT" \
        --query '[0].value' -o tsv)

    # Create blob container
    print_step "Creating blob container: $TF_CONTAINER_NAME"
    az storage container create \
        --name "$TF_CONTAINER_NAME" \
        --account-name "$TF_STORAGE_ACCOUNT" \
        --account-key "$ACCOUNT_KEY" \
        --output none

    print_success "Terraform backend storage created"

    # Save to file
    cat > terraform-backend-config.txt <<EOF
========================================
Terraform Backend Configuration
========================================
Resource Group: $TF_RG_NAME
Storage Account: $TF_STORAGE_ACCOUNT
Container: $TF_CONTAINER_NAME
Access Key: $ACCOUNT_KEY
========================================

Update infra/azure/backend.tf with:

terraform {
  backend "azurerm" {
    resource_group_name  = "$TF_RG_NAME"
    storage_account_name = "$TF_STORAGE_ACCOUNT"
    container_name       = "$TF_CONTAINER_NAME"
    key                  = "aura-audit-ai.tfstate"
  }
}

GitHub Secrets:
- TF_BACKEND_STORAGE_ACCOUNT: $TF_STORAGE_ACCOUNT
- TF_BACKEND_ACCESS_KEY: $ACCOUNT_KEY
EOF

    print_success "Terraform backend configuration saved to terraform-backend-config.txt"
}

# Create Azure AD group
create_ad_group() {
    print_step "Creating Azure AD admin group..."

    # Check if group already exists
    if az ad group show --group "AKS-Aura-Admins" >/dev/null 2>&1; then
        print_warning "Group 'AKS-Aura-Admins' already exists"
        GROUP_ID=$(az ad group show --group "AKS-Aura-Admins" --query id -o tsv)
    else
        # Create group
        az ad group create \
            --display-name "AKS-Aura-Admins" \
            --mail-nickname "aks-aura-admins" \
            --output none

        GROUP_ID=$(az ad group show --group "AKS-Aura-Admins" --query id -o tsv)
        print_success "Azure AD group created"
    fi

    # Add current user to group
    USER_ID=$(az ad signed-in-user show --query id -o tsv 2>/dev/null || echo "")
    if [ -n "$USER_ID" ]; then
        print_step "Adding current user to admin group..."
        az ad group member add \
            --group "AKS-Aura-Admins" \
            --member-id "$USER_ID" \
            --output none 2>/dev/null || true
        print_success "Current user added to admin group"
    fi

    # Save group ID
    echo "$GROUP_ID" > azure-ad-group-id.txt

    print_success "Azure AD Group ID: $GROUP_ID"
    print_success "Group ID saved to azure-ad-group-id.txt"
}

# Create service principal
create_service_principal() {
    print_step "Creating service principal for GitHub Actions..."

    SUBSCRIPTION_ID=$(az account show --query id -o tsv)

    # Check if service principal already exists
    SP_NAME="aura-audit-ai-cicd"
    if az ad sp list --display-name "$SP_NAME" --query "[0].appId" -o tsv | grep -q .; then
        print_warning "Service principal '$SP_NAME' already exists"
        read -p "Do you want to reset credentials? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            APP_ID=$(az ad sp list --display-name "$SP_NAME" --query "[0].appId" -o tsv)
            az ad sp credential reset --id "$APP_ID" --sdk-auth > azure-credentials.json
            print_success "Service principal credentials reset"
        else
            print_warning "Skipping service principal creation"
            return
        fi
    else
        az ad sp create-for-rbac \
            --name "$SP_NAME" \
            --role contributor \
            --scopes "/subscriptions/$SUBSCRIPTION_ID" \
            --sdk-auth > azure-credentials.json

        print_success "Service principal created"
    fi

    print_success "Service principal credentials saved to azure-credentials.json"
    print_warning "Add this JSON to GitHub Secrets as: AZURE_CREDENTIALS"
}

# Generate secrets
generate_secrets() {
    print_step "Generating security secrets..."

    JWT_SECRET=$(openssl rand -hex 32)
    ENCRYPTION_KEY=$(openssl rand -hex 32)
    MASTER_KEY=$(openssl rand -hex 32)
    POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)

    # Save to file
    cat > azure-secrets.env <<EOF
# ========================================
# Security Secrets - SAVE THESE SECURELY!
# ========================================
# Generated: $(date)
#
# Add these to GitHub Secrets and .env.production

JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY
MASTER_KEY=$MASTER_KEY
POSTGRES_PASSWORD=$POSTGRES_PASSWORD

# GitHub Secrets to add:
# - JWT_SECRET
# - ENCRYPTION_KEY
# - MASTER_KEY
# - POSTGRES_PASSWORD
# - OPENAI_API_KEY (get from https://platform.openai.com)
EOF

    print_success "Security secrets generated and saved to azure-secrets.env"
    print_warning "IMPORTANT: Keep azure-secrets.env secure and do not commit to git!"
}

# Create terraform.tfvars
create_terraform_tfvars() {
    print_step "Creating terraform.tfvars..."

    if [ ! -f "azure-ad-group-id.txt" ]; then
        print_error "Azure AD Group ID file not found. Run create_ad_group first."
        return 1
    fi

    GROUP_ID=$(cat azure-ad-group-id.txt)

    cat > infra/azure/terraform.tfvars <<EOF
# ===========================================
# Aura Audit AI - Azure Configuration
# ===========================================
# Auto-generated: $(date)

# General Configuration
location    = "$LOCATION"
environment = "$ENVIRONMENT"

# Azure AD Admin Group
aks_admin_group_ids = ["$GROUP_ID"]

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

    print_success "terraform.tfvars created at infra/azure/terraform.tfvars"
}

# Update backend.tf
update_backend_tf() {
    print_step "Updating Terraform backend configuration..."

    if [ ! -f "terraform-backend-config.txt" ]; then
        print_error "Terraform backend config file not found. Run create_terraform_backend first."
        return 1
    fi

    # Extract storage account name from config file
    TF_STORAGE_ACCOUNT=$(grep "Storage Account:" terraform-backend-config.txt | cut -d: -f2 | tr -d ' ')

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
}
EOF

    print_success "backend.tf updated at infra/azure/backend.tf"
}

# Main setup flow
main() {
    echo ""
    print_step "Starting Azure initial setup..."
    echo ""

    # Run setup steps
    check_prerequisites
    check_azure_login
    register_providers
    create_terraform_backend
    create_ad_group
    create_service_principal
    generate_secrets
    create_terraform_tfvars
    update_backend_tf

    echo ""
    echo "=========================================="
    print_success "Azure Initial Setup Complete! 🎉"
    echo "=========================================="
    echo ""
    echo "Files created:"
    echo "  ✓ terraform-backend-config.txt"
    echo "  ✓ azure-ad-group-id.txt"
    echo "  ✓ azure-credentials.json"
    echo "  ✓ azure-secrets.env"
    echo "  ✓ infra/azure/terraform.tfvars"
    echo "  ✓ infra/azure/backend.tf"
    echo ""
    echo "Next steps:"
    echo "  1. Review and add secrets to GitHub:"
    echo "     - AZURE_CREDENTIALS (from azure-credentials.json)"
    echo "     - OPENAI_API_KEY (get from https://platform.openai.com)"
    echo "     - JWT_SECRET, ENCRYPTION_KEY, MASTER_KEY (from azure-secrets.env)"
    echo ""
    echo "  2. Copy .env.production.template to .env.production:"
    echo "     cp .env.production.template .env.production"
    echo ""
    echo "  3. Edit .env.production with secrets from azure-secrets.env"
    echo ""
    echo "  4. Deploy infrastructure:"
    echo "     cd infra/azure"
    echo "     terraform init"
    echo "     terraform plan"
    echo "     terraform apply"
    echo ""
    echo "  5. Follow the complete guide: AZURE_FIRST_TIME_SETUP.md"
    echo ""
    print_warning "IMPORTANT: Keep generated files secure and do not commit to git!"
    echo "=========================================="
}

# Run main function
main "$@"
