# Azure First-Time Setup Guide for Aura Audit AI

This guide walks you through the **initial Azure environment setup** from scratch. Follow these steps in order.

## 🎯 Overview

You'll set up:
- ✅ Azure subscription & resource providers
- ✅ Terraform backend storage
- ✅ Azure AD admin group
- ✅ Service principal for GitHub Actions
- ✅ Configuration files
- ✅ Secrets & credentials

**Estimated Time**: 1-2 hours
**Estimated Cost**: ~$2,495/month (production) or ~$500/month (dev)

---

## 📋 Prerequisites

### 1. Install Required Tools

```bash
# Install Azure CLI (if not already installed)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.7.0/terraform_1.7.0_linux_amd64.zip
unzip terraform_1.7.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
terraform version

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
```

### 2. Verify Azure Access

```bash
# Login to Azure
az login

# List your subscriptions
az account list --output table

# Set the subscription you want to use
az account set --subscription "YOUR_SUBSCRIPTION_NAME_OR_ID"

# Verify you're using the right subscription
az account show --output table
```

---

## 🚀 Step-by-Step Setup

### Step 1: Register Azure Resource Providers

```bash
# Register all required Azure resource providers
# This can take 2-5 minutes
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Cache
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.KeyVault
az provider register --namespace Microsoft.Network
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.Insights
az provider register --namespace Microsoft.ContainerRegistry

# Check registration status (wait until all show "Registered")
az provider list --query "[?namespace contains(@, 'Microsoft.Container') || namespace contains(@, 'Microsoft.DB') || namespace contains(@, 'Microsoft.Cache') || namespace contains(@, 'Microsoft.Storage') || namespace contains(@, 'Microsoft.KeyVault') || namespace contains(@, 'Microsoft.Network') || namespace contains(@, 'Microsoft.Operational') || namespace contains(@, 'Microsoft.Insights')].{Namespace:namespace, State:registrationState}" -o table
```

**Wait for all providers to show "Registered" before continuing.**

---

### Step 2: Create Terraform Backend Storage

Terraform needs a place to store its state file. We'll create an Azure Storage Account for this.

```bash
# Set variables
LOCATION="eastus"
TF_RG_NAME="aura-tfstate-rg"
TF_STORAGE_ACCOUNT="auratfstate$(date +%s)"  # Must be globally unique
TF_CONTAINER_NAME="tfstate"

# Create resource group
az group create \
  --name $TF_RG_NAME \
  --location $LOCATION

# Create storage account
az storage account create \
  --resource-group $TF_RG_NAME \
  --name $TF_STORAGE_ACCOUNT \
  --sku Standard_LRS \
  --encryption-services blob \
  --location $LOCATION

# Get storage account key
ACCOUNT_KEY=$(az storage account keys list \
  --resource-group $TF_RG_NAME \
  --account-name $TF_STORAGE_ACCOUNT \
  --query '[0].value' -o tsv)

# Create blob container
az storage container create \
  --name $TF_CONTAINER_NAME \
  --account-name $TF_STORAGE_ACCOUNT \
  --account-key $ACCOUNT_KEY

# Display the values (SAVE THESE!)
echo "=========================================="
echo "Terraform Backend Configuration"
echo "=========================================="
echo "Resource Group: $TF_RG_NAME"
echo "Storage Account: $TF_STORAGE_ACCOUNT"
echo "Container: $TF_CONTAINER_NAME"
echo "Access Key: $ACCOUNT_KEY"
echo "=========================================="
```

**⚠️ SAVE THESE VALUES! You'll need them in the next step.**

---

### Step 3: Update Terraform Backend Configuration

Edit `infra/azure/backend.tf` with the values from Step 2:

```bash
# Open the backend.tf file
nano infra/azure/backend.tf
```

Update these lines:
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "aura-tfstate-rg"
    storage_account_name = "auratfstate1234567890"  # <- Your storage account name
    container_name       = "tfstate"
    key                  = "aura-audit-ai.tfstate"
  }
}
```

---

### Step 4: Create Azure AD Admin Group

This group will have admin access to the AKS cluster.

```bash
# Create Azure AD group for AKS admins
az ad group create \
  --display-name "AKS-Aura-Admins" \
  --mail-nickname "aks-aura-admins"

# Get the group Object ID (SAVE THIS!)
GROUP_ID=$(az ad group show \
  --group "AKS-Aura-Admins" \
  --query id -o tsv)

echo "=========================================="
echo "Azure AD Group ID: $GROUP_ID"
echo "=========================================="

# Add yourself to the group (optional)
USER_ID=$(az ad signed-in-user show --query id -o tsv)
az ad group member add \
  --group "AKS-Aura-Admins" \
  --member-id $USER_ID

# Verify group membership
az ad group member list --group "AKS-Aura-Admins" -o table
```

**⚠️ SAVE THE GROUP_ID! You'll need it for terraform.tfvars.**

---

### Step 5: Create Service Principal for GitHub Actions

This allows GitHub Actions to deploy to Azure automatically.

```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create service principal
az ad sp create-for-rbac \
  --name "aura-audit-ai-cicd" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --sdk-auth > azure-credentials.json

# Display the credentials
cat azure-credentials.json

echo ""
echo "=========================================="
echo "IMPORTANT: Add this JSON to GitHub Secrets"
echo "Secret Name: AZURE_CREDENTIALS"
echo "=========================================="
```

**⚠️ Copy the JSON output and add it as a GitHub secret named `AZURE_CREDENTIALS`.**

---

### Step 6: Generate Security Secrets

Generate secure random keys for your application:

```bash
# Generate JWT Secret (64 chars)
JWT_SECRET=$(openssl rand -hex 32)

# Generate Encryption Key (64 chars)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Generate Master Key (64 chars)
MASTER_KEY=$(openssl rand -hex 32)

# Generate PostgreSQL admin password
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)

# Display all secrets (SAVE THESE SECURELY!)
echo "=========================================="
echo "Security Secrets - SAVE THESE SECURELY!"
echo "=========================================="
echo "JWT_SECRET=$JWT_SECRET"
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY"
echo "MASTER_KEY=$MASTER_KEY"
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "=========================================="
```

**⚠️ SAVE THESE SECRETS! You'll need them for .env.production and GitHub Secrets.**

---

### Step 7: Configure Terraform Variables

Create `infra/azure/terraform.tfvars` with your values:

```bash
# Copy the example file
cp infra/azure/terraform.tfvars.example infra/azure/terraform.tfvars

# Edit with your values
nano infra/azure/terraform.tfvars
```

Update the file with:
- `aks_admin_group_ids`: Use the GROUP_ID from Step 4
- Review other settings (location, node sizes, etc.)

**Example:**
```hcl
location    = "eastus"
environment = "prod"

# Use the GROUP_ID from Step 4
aks_admin_group_ids = ["YOUR_GROUP_ID_HERE"]

# Review and adjust these based on your needs
kubernetes_version    = "1.28"
aks_system_node_count = 3
aks_app_node_count    = 3
```

---

### Step 8: Configure Environment Variables

Create `.env.production` with your actual values:

```bash
# Copy the template
cp .env.production.template .env.production

# Edit with your values
nano .env.production
```

**Required Updates:**

1. **OpenAI API Key** (REQUIRED for AI features):
   - Get from: https://platform.openai.com/api-keys
   - Update: `OPENAI_API_KEY=sk-proj-...`

2. **Security Secrets** (from Step 6):
   - `JWT_SECRET`: Your generated JWT secret
   - `ENCRYPTION_KEY`: Your generated encryption key
   - `MASTER_KEY`: Your generated master key

3. **Database** (will update after deployment):
   - `POSTGRES_PASSWORD`: From Step 6
   - Leave hostname as placeholder for now

4. **Other Services** (optional, can configure later):
   - QuickBooks, Xero, NetSuite
   - DocuSign, Stripe, Plaid, SendGrid

---

### Step 9: Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Value | Source |
|-------------|-------|--------|
| `AZURE_CREDENTIALS` | JSON from Step 5 | Service principal |
| `TF_BACKEND_STORAGE_ACCOUNT` | Storage account name | Step 2 |
| `TF_BACKEND_ACCESS_KEY` | Storage account key | Step 2 |
| `OPENAI_API_KEY` | Your OpenAI API key | https://platform.openai.com |
| `JWT_SECRET` | JWT secret | Step 6 |
| `ENCRYPTION_KEY` | Encryption key | Step 6 |
| `MASTER_KEY` | Master key | Step 6 |
| `POSTGRES_PASSWORD` | PostgreSQL password | Step 6 |
| `DOCKER_HUB_USERNAME` | Your Docker Hub username | Optional (for caching) |
| `DOCKER_HUB_TOKEN` | Your Docker Hub token | Optional (for caching) |

---

### Step 10: Deploy Infrastructure with Terraform

Now you're ready to deploy!

```bash
# Navigate to the Azure infrastructure directory
cd infra/azure

# Initialize Terraform (downloads providers, connects to backend)
terraform init

# Validate your configuration
terraform validate

# Preview what will be created (REVIEW THIS CAREFULLY!)
terraform plan -out=tfplan

# Review the plan output
# It will show ~50-60 resources to be created

# If everything looks good, apply the changes
terraform apply tfplan
```

**This will take 15-30 minutes** and create:
- Resource group
- Virtual network & subnets
- AKS cluster (6 nodes)
- PostgreSQL database
- Redis cache
- Storage accounts
- Container registry
- Application Gateway with WAF
- Key Vault
- Log Analytics & Application Insights

---

### Step 11: Get Azure Resource Details

After Terraform completes, capture the outputs:

```bash
# Get all outputs
terraform output

# Get specific values
terraform output -raw postgres_fqdn
terraform output -raw redis_hostname
terraform output -raw storage_account_name
terraform output -raw acr_login_server
terraform output -raw appinsights_instrumentation_key

# Save these to update .env.production
```

**Update your `.env.production` file** with these values:
- `POSTGRES_HOST`: Use `postgres_fqdn`
- `REDIS_HOST`: Use `redis_hostname`
- `S3_ENDPOINT`: Use storage account blob endpoint
- `APPINSIGHTS_INSTRUMENTATION_KEY`: Use instrumentation key

---

### Step 12: Configure kubectl Access

Connect to your new AKS cluster:

```bash
# Get AKS credentials
az aks get-credentials \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks

# Verify connection
kubectl get nodes

# You should see 6 nodes (3 system + 3 app)
```

---

### Step 13: Deploy Application to Kubernetes

```bash
# Navigate back to project root
cd /home/user/Data-Norm-2

# Create Kubernetes namespace
kubectl apply -f infra/k8s/base/namespace.yaml

# Create ConfigMap
kubectl apply -f infra/k8s/base/configmap.yaml

# Create Secrets (update with your actual values first!)
# Edit infra/k8s/base/secrets.yaml with your values from .env.production
kubectl apply -f infra/k8s/base/secrets.yaml

# Deploy all services
kubectl apply -f infra/k8s/base/deployments-all-services.yaml

# Deploy service definitions
kubectl apply -f infra/k8s/base/services.yaml

# Deploy ingress
kubectl apply -f infra/k8s/base/ingress.yaml

# Watch deployment progress
kubectl get pods -n aura-audit-ai --watch
```

---

### Step 14: Run Database Migrations

```bash
# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=api-gateway -n aura-audit-ai --timeout=300s

# Run migrations
kubectl exec -it deployment/api-gateway -n aura-audit-ai -- python -m alembic upgrade head

# Or use the dedicated migration job (if available)
kubectl apply -f infra/k8s/jobs/db-migration.yaml
kubectl wait --for=condition=complete job/db-migration -n aura-audit-ai --timeout=600s
```

---

### Step 15: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n aura-audit-ai

# Check services
kubectl get svc -n aura-audit-ai

# Check ingress
kubectl get ingress -n aura-audit-ai

# Get the external IP of the Application Gateway
kubectl get ingress -n aura-audit-ai -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}'

# Test health endpoint
GATEWAY_IP=$(kubectl get ingress -n aura-audit-ai -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')
curl http://$GATEWAY_IP/health

# View logs
kubectl logs -f deployment/api-gateway -n aura-audit-ai
```

---

## 🎉 Success Checklist

- [ ] All Azure resource providers registered
- [ ] Terraform backend storage created
- [ ] Azure AD admin group created
- [ ] Service principal for GitHub Actions created
- [ ] All secrets generated and saved securely
- [ ] `terraform.tfvars` configured
- [ ] `.env.production` configured
- [ ] GitHub secrets added
- [ ] Infrastructure deployed with Terraform
- [ ] kubectl configured to access AKS
- [ ] Application deployed to Kubernetes
- [ ] All pods running (check with `kubectl get pods`)
- [ ] Database migrations completed
- [ ] Health endpoints responding

---

## 📊 What You've Deployed

### Azure Resources:
- **AKS Cluster**: 6 nodes (3 system + 3 app)
- **PostgreSQL**: Flexible Server with HA and 35-day backups
- **Redis**: Premium P1 (6GB) with persistence
- **Storage**: GRS replication with WORM compliance (7-year retention)
- **Container Registry**: Premium tier with geo-replication
- **Application Gateway**: WAF v2 with OWASP protection
- **Monitoring**: Log Analytics + Application Insights

### Application Services:
- 25+ microservices (API Gateway + specialized services)
- Next.js frontend
- React admin portal
- React client portal

---

## 🔐 Security Best Practices

✅ **Completed Automatically**:
- Network isolation (VNet with private subnets)
- TLS/SSL encryption in transit
- Encryption at rest (all storage)
- WAF protection (OWASP rules)
- Azure AD authentication for AKS
- Key Vault for secrets
- Private endpoints for databases

⚠️ **Manual Configuration Needed**:
1. **Configure DNS**: Point your domain to Application Gateway IP
2. **SSL Certificates**: Upload or configure Let's Encrypt
3. **Azure AD Integration**: Configure OAuth2/OIDC for user authentication
4. **Backup Testing**: Verify PostgreSQL backups work
5. **Disaster Recovery**: Test failover procedures
6. **Monitoring Alerts**: Configure alerts in Application Insights

---

## 💰 Cost Management

### Monthly Cost Breakdown (Production):
- AKS: ~$1,290
- PostgreSQL: $340
- Redis: $300
- Storage: $25
- Container Registry: $200
- Application Gateway: $285
- Other: $55
- **Total: ~$2,495/month**

### Cost Optimization Tips:
1. **Use Dev Environment** for non-production:
   - Smaller node sizes (D2s_v3 instead of D8s_v3)
   - Single-zone instead of HA
   - Disable geo-replication
   - **Estimated savings: ~$1,800/month**

2. **Reserved Instances**: Save 30-40% by committing to 1-3 years
3. **Auto-scaling**: Configure HPA to scale down during off-hours
4. **Storage Lifecycle**: Move cold data to Archive tier

---

## 🔧 Next Steps

1. **Configure DNS & SSL**:
   - Point domain to Application Gateway IP
   - Configure SSL certificate (Let's Encrypt or purchased)

2. **Configure Azure AD Authentication**:
   - Set up app registration for OAuth2
   - Configure OIDC for user authentication

3. **Set Up Monitoring & Alerts**:
   - Configure Application Insights alerts
   - Set up log queries for audit trail
   - Create dashboards for key metrics

4. **Configure Integrations** (as needed):
   - QuickBooks, Xero, NetSuite
   - DocuSign for e-signatures
   - Stripe for payments
   - SendGrid for emails

5. **Testing**:
   - Run E2E tests with Playwright
   - Perform load testing
   - Validate backup/restore procedures

6. **Documentation**:
   - Document your deployment specifics
   - Create runbook for common operations
   - Train team on platform

---

## 🆘 Troubleshooting

### Issue: Terraform backend initialization fails
**Solution**: Verify storage account exists and you have access:
```bash
az storage account show --name YOUR_STORAGE_ACCOUNT --resource-group aura-tfstate-rg
```

### Issue: AKS cluster creation fails
**Solution**: Check resource provider registration:
```bash
az provider show --namespace Microsoft.ContainerService --query "registrationState"
```

### Issue: Pods stuck in Pending state
**Solution**: Check node capacity and events:
```bash
kubectl describe pod POD_NAME -n aura-audit-ai
kubectl get nodes -o wide
```

### Issue: Can't connect to PostgreSQL
**Solution**: Verify firewall rules and credentials:
```bash
az postgres flexible-server firewall-rule list \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-postgres
```

### Issue: Application Gateway not routing traffic
**Solution**: Check ingress configuration:
```bash
kubectl describe ingress -n aura-audit-ai
kubectl logs -n kube-system -l app=ingress-nginx
```

---

## 📚 Additional Resources

- [Azure Deployment Guide](AZURE_DEPLOYMENT.md) - Comprehensive deployment documentation
- [Azure Deployment Checklist](AZURE_DEPLOYMENT_CHECKLIST.md) - Step-by-step checklist
- [Deployment Readiness Report](DEPLOYMENT_READINESS_REPORT.md) - Service inventory
- [Architecture Documentation](ARCHITECTURE.md) - System architecture

---

## 🎯 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Azure Portal for resource status
3. Check Application Insights for errors
4. Review Kubernetes logs: `kubectl logs POD_NAME -n aura-audit-ai`
5. Check GitHub Actions logs for CI/CD issues

---

**Congratulations!** 🎉 You've successfully set up your Azure environment for Aura Audit AI!
