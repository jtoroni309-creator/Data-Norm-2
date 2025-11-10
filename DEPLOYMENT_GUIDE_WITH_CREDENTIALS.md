# Aura Audit AI - Azure Deployment Guide

## 🎯 Quick Overview

This guide will help you deploy Aura Audit AI to Azure using your provided Application Registration credentials.

**Your Azure Credentials:**
- Application (Client) ID: `6d1fdc5d-580b-499d-bae8-c129af50e96e`
- Object ID: `183eaec2-0a8e-448d-8b62-5143e7ca66fe`
- Directory (Tenant) ID: `002fa7de-1afd-4945-86e1-79281af841ad`

**Estimated Time:** 2-3 hours
**Estimated Cost:** ~$2,500/month (production) or ~$500/month (dev)

---

## 📋 Prerequisites

Before starting, ensure you have:

### Required Tools
```bash
# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Terraform (version 1.5+)
wget https://releases.hashicorp.com/terraform/1.7.0/terraform_1.7.0_linux_amd64.zip
unzip terraform_1.7.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Required Information
- ✅ Azure Application (Service Principal) credentials (provided above)
- ⚠️ **Client Secret** - You need the secret for the application registration
- ⚠️ **OpenAI API Key** - Get from https://platform.openai.com/api-keys
- ⚠️ **Subscription ID** - Your Azure subscription ID

---

## 🚀 Deployment Options

### Option 1: Automated Script (Recommended)

We've created a script that automates the entire setup process.

```bash
# Make the script executable
chmod +x azure-deployment-config.sh

# Run the configuration script
./azure-deployment-config.sh
```

**What it does:**
1. Logs in to Azure using your service principal
2. Registers all required Azure resource providers
3. Creates Terraform backend storage
4. Generates all security secrets
5. Creates `terraform.tfvars` with your configuration
6. Updates `backend.tf` with proper authentication
7. Creates `.env.production` with all environment variables

**What you need:**
- The client secret for your service principal
- Your Azure subscription ID

After running this script, you'll have all configuration files ready for deployment!

---

### Option 2: Manual Setup

If you prefer manual control, follow these steps:

#### Step 1: Login to Azure

```bash
# Login with service principal
az login --service-principal \
  --username 6d1fdc5d-580b-499d-bae8-c129af50e96e \
  --password YOUR_CLIENT_SECRET \
  --tenant 002fa7de-1afd-4945-86e1-79281af841ad

# Verify login and get subscription ID
az account show

# Set subscription (if you have multiple)
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

#### Step 2: Create Terraform Backend Storage

```bash
# Create resource group for Terraform state
az group create \
  --name aura-tfstate-rg \
  --location eastus

# Create storage account (name must be globally unique)
STORAGE_ACCOUNT="auratfstate$(date +%s)"

az storage account create \
  --resource-group aura-tfstate-rg \
  --name $STORAGE_ACCOUNT \
  --sku Standard_LRS \
  --encryption-services blob \
  --location eastus

# Get storage account key
ACCOUNT_KEY=$(az storage account keys list \
  --resource-group aura-tfstate-rg \
  --account-name $STORAGE_ACCOUNT \
  --query '[0].value' -o tsv)

# Create blob container
az storage container create \
  --name tfstate \
  --account-name $STORAGE_ACCOUNT \
  --account-key $ACCOUNT_KEY

echo "Storage Account: $STORAGE_ACCOUNT"
echo "Access Key: $ACCOUNT_KEY"
```

Save these values - you'll need them!

#### Step 3: Register Resource Providers

```bash
# Register all required providers
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Cache
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.KeyVault
az provider register --namespace Microsoft.Network
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.Insights
az provider register --namespace Microsoft.ContainerRegistry

# Wait for registration (takes 2-5 minutes)
```

#### Step 4: Generate Security Secrets

```bash
# Generate random secrets
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
MASTER_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)

# Save these securely!
echo "JWT_SECRET=$JWT_SECRET"
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY"
echo "MASTER_KEY=$MASTER_KEY"
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
```

#### Step 5: Update Configuration Files

Update `infra/azure/backend.tf` with your storage account:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "aura-tfstate-rg"
    storage_account_name = "YOUR_STORAGE_ACCOUNT_NAME"  # From Step 2
    container_name       = "tfstate"
    key                  = "aura-audit-ai.tfstate"
  }
}

provider "azurerm" {
  features {}

  subscription_id = "YOUR_SUBSCRIPTION_ID"
  client_id       = "6d1fdc5d-580b-499d-bae8-c129af50e96e"
  tenant_id       = "002fa7de-1afd-4945-86e1-79281af841ad"
}
```

Create `infra/azure/terraform.tfvars`:

```hcl
location    = "eastus"
environment = "prod"

# AKS Configuration
kubernetes_version    = "1.28"
aks_system_node_count = 3
aks_app_node_count    = 3

# PostgreSQL Configuration
postgres_admin_username        = "atlasadmin"
postgres_high_availability     = true
postgres_backup_retention_days = 35

# Redis Configuration
redis_sku = "Premium"

# Storage Configuration
storage_replication_type = "GRS"
```

---

## 🏗️ Deploy Infrastructure

Once configuration is complete:

```bash
# Navigate to infrastructure directory
cd infra/azure

# Set backend authentication
export ARM_ACCESS_KEY="YOUR_STORAGE_ACCOUNT_KEY"
export ARM_CLIENT_ID="6d1fdc5d-580b-499d-bae8-c129af50e96e"
export ARM_CLIENT_SECRET="YOUR_CLIENT_SECRET"
export ARM_TENANT_ID="002fa7de-1afd-4945-86e1-79281af841ad"
export ARM_SUBSCRIPTION_ID="YOUR_SUBSCRIPTION_ID"

# Initialize Terraform
terraform init

# Preview what will be created
terraform plan

# Review the plan carefully - it will create 50+ resources

# Deploy infrastructure
terraform apply

# This will take 60-90 minutes
```

**What gets deployed:**
- AKS Kubernetes cluster (6 nodes)
- PostgreSQL Flexible Server (with HA)
- Azure Cache for Redis (Premium tier)
- Azure Blob Storage (with WORM compliance)
- Azure Container Registry
- Application Gateway with WAF
- Azure Key Vault
- Log Analytics workspace
- Application Insights

---

## 📦 Build and Deploy Applications

After infrastructure is deployed:

### Step 1: Get Azure Resource Values

```bash
cd infra/azure

# Get all outputs
terraform output

# Save these specific values:
POSTGRES_HOST=$(terraform output -raw postgres_fqdn)
REDIS_HOST=$(terraform output -raw redis_hostname)
REDIS_KEY=$(terraform output -raw redis_primary_key)
STORAGE_ACCOUNT=$(terraform output -raw storage_account_name)
STORAGE_KEY=$(terraform output -raw storage_primary_key)
ACR_NAME=$(terraform output -raw acr_login_server)
```

### Step 2: Update Environment Variables

Update `.env.production` with the values from Step 1:

```env
POSTGRES_HOST=aura-audit-ai-prod-postgres.postgres.database.azure.com
REDIS_HOST=aura-audit-ai-prod-redis.redis.cache.windows.net
REDIS_PASSWORD=YOUR_REDIS_KEY
AZURE_STORAGE_ACCOUNT=YOUR_STORAGE_ACCOUNT
AZURE_STORAGE_KEY=YOUR_STORAGE_KEY
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Build and Push Docker Images

```bash
# Login to Azure Container Registry
az acr login --name $(terraform output -raw acr_name)

# Build and push each service
services=(identity ingestion normalize analytics llm engagement disclosures reporting qc connectors)

for service in "${services[@]}"; do
  echo "Building $service..."
  docker build -t $(terraform output -raw acr_login_server)/aura/$service:latest \
    -f services/$service/Dockerfile \
    services/$service

  docker push $(terraform output -raw acr_login_server)/aura/$service:latest
done

# Build and push frontend
docker build -t $(terraform output -raw acr_login_server)/aura/web:latest frontend/
docker push $(terraform output -raw acr_login_server)/aura/web:latest
```

### Step 4: Deploy to Kubernetes

```bash
# Get AKS credentials
az aks get-credentials \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks \
  --overwrite-existing

# Verify connection
kubectl get nodes

# Create namespace
kubectl apply -f infra/k8s/base/namespace.yaml

# Create secrets from .env.production
kubectl create secret generic app-secrets \
  --from-env-file=.env.production \
  -n aura-audit-ai

# Apply ConfigMap
kubectl apply -f infra/k8s/base/configmap.yaml

# Deploy all services
kubectl apply -f infra/k8s/base/serviceaccount.yaml
kubectl apply -f infra/k8s/base/deployment-identity.yaml
kubectl apply -f infra/k8s/base/deployments-all-services.yaml
kubectl apply -f infra/k8s/base/ingress.yaml

# Watch deployment progress
kubectl get pods -n aura-audit-ai --watch
```

---

## ✅ Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n aura-audit-ai

# You should see 25+ pods all in "Running" status

# Get the Application Gateway IP
az network public-ip show \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-appgw-pip \
  --query ipAddress -o tsv

# Test health endpoint
GATEWAY_IP=$(az network public-ip show \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-appgw-pip \
  --query ipAddress -o tsv)

curl http://$GATEWAY_IP/health

# Should return: {"status": "healthy"}
```

---

## 🔄 GitHub Actions CI/CD (Optional)

To enable automated deployments via GitHub Actions:

### Add GitHub Secrets

Go to: **Repository → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Value |
|------------|-------|
| `AZURE_CREDENTIALS` | Service principal JSON (see below) |
| `TF_BACKEND_STORAGE_ACCOUNT` | Your storage account name |
| `TF_BACKEND_ACCESS_KEY` | Your storage access key |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `JWT_SECRET` | Generated JWT secret |
| `ENCRYPTION_KEY` | Generated encryption key |
| `MASTER_KEY` | Generated master key |
| `POSTGRES_PASSWORD` | Generated PostgreSQL password |

**AZURE_CREDENTIALS format:**
```json
{
  "clientId": "6d1fdc5d-580b-499d-bae8-c129af50e96e",
  "clientSecret": "YOUR_CLIENT_SECRET",
  "subscriptionId": "YOUR_SUBSCRIPTION_ID",
  "tenantId": "002fa7de-1afd-4945-86e1-79281af841ad"
}
```

### Trigger Deployment

After adding secrets:

```bash
# Push to main branch to trigger deployment
git push origin main

# Or trigger manually from GitHub Actions UI
```

---

## 🎯 Post-Deployment Steps

### 1. Configure DNS

Point your domain to the Application Gateway IP:

```
A record: api.yourauditsaas.com → [Gateway IP]
A record: app.yourauditsaas.com → [Gateway IP]
A record: admin.yourauditsaas.com → [Gateway IP]
```

### 2. Set Up SSL Certificates

Use cert-manager for Let's Encrypt:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 3. Run Database Migrations

```bash
kubectl exec -it deployment/identity -n aura-audit-ai -- \
  python -m alembic upgrade head
```

### 4. Create Admin User

```bash
kubectl exec -it deployment/identity -n aura-audit-ai -- \
  python scripts/create_admin.py --email admin@yourcompany.com
```

---

## 📊 Monitoring & Logs

### View Application Logs

```bash
# View logs for a specific service
kubectl logs -f deployment/identity -n aura-audit-ai

# View logs for all services
kubectl logs -l app=aura-audit-ai -n aura-audit-ai --tail=100
```

### Access Application Insights

```bash
# Get Application Insights instrumentation key
az monitor app-insights component show \
  --app aura-audit-ai-prod-appinsights \
  --resource-group aura-audit-ai-prod-rg \
  --query instrumentationKey -o tsv
```

View in Azure Portal: https://portal.azure.com → Application Insights

---

## 💰 Cost Management

### Production Environment (~$2,495/month)

| Service | Monthly Cost |
|---------|-------------|
| AKS Nodes (6) | $1,290 |
| PostgreSQL | $340 |
| Redis Premium | $300 |
| Storage (GRS) | $25 |
| Container Registry | $200 |
| Application Gateway | $285 |
| Monitoring | $55 |

### Reduce Costs for Development

To reduce costs for dev/test environments:

```hcl
# Update terraform.tfvars
aks_system_node_count = 1
aks_app_node_count = 1
aks_app_node_size = "Standard_D2s_v3"

postgres_high_availability = false
redis_sku = "Standard"
storage_replication_type = "LRS"
```

This reduces costs to ~$500/month for development.

---

## 🆘 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n aura-audit-ai

# Check logs
kubectl logs <pod-name> -n aura-audit-ai

# Common issues:
# - ImagePullBackOff: Check ACR authentication
# - CrashLoopBackOff: Check environment variables
# - Pending: Check node resources
```

### Database Connection Issues

```bash
# Test connection from pod
kubectl exec -it deployment/identity -n aura-audit-ai -- \
  psql "postgresql://atlasadmin@aura-audit-ai-prod-postgres:5432/atlas?sslmode=require"

# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-postgres
```

### Terraform Errors

```bash
# If terraform init fails
rm -rf .terraform
rm .terraform.lock.hcl
terraform init

# If terraform apply fails
terraform plan  # Review what's being created
terraform apply -target=<specific-resource>  # Deploy one resource at a time
```

---

## 🔐 Security Best Practices

1. **Rotate Secrets Regularly**
   - Client secrets every 90 days
   - Database passwords every 180 days
   - JWT secrets annually

2. **Enable Azure AD Authentication**
   - Configure managed identities for services
   - Use Azure AD for user authentication

3. **Configure Network Security**
   - Enable private endpoints for PostgreSQL
   - Configure NSG rules
   - Enable Azure Firewall

4. **Audit Logging**
   - Enable Azure Monitor
   - Configure Log Analytics alerts
   - Review security logs weekly

---

## 📚 Additional Resources

- [Azure Quickstart Guide](AZURE_QUICKSTART.md)
- [GitHub Secrets Setup](GITHUB_SECRETS_SETUP.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Deployment Checklist](AZURE_DEPLOYMENT_CHECKLIST.md)

---

## ✅ Success Checklist

Deployment is successful when:

- [ ] All Terraform resources created without errors
- [ ] All 25+ pods in `Running` state
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Database migrations completed
- [ ] Application Insights showing telemetry
- [ ] Can access services via Application Gateway
- [ ] Authentication working
- [ ] File upload to blob storage working
- [ ] Redis cache functioning

---

## 🎉 Next Steps

After successful deployment:

1. **Configure your domain and SSL certificates**
2. **Create admin users and set up RBAC**
3. **Import initial data and configure workflows**
4. **Set up monitoring alerts**
5. **Run end-to-end tests**
6. **Onboard your first users!**

---

**Need help?** Check the troubleshooting section or review the Azure Portal for resource status.

**Cost monitoring:** Set up budget alerts in Azure Cost Management to track spending.

**Backup:** Verify automated backups are enabled for PostgreSQL and configure disaster recovery procedures.
