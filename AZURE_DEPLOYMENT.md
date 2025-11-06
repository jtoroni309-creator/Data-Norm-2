# Aura Audit AI - Azure Deployment Guide

This guide covers the complete deployment of Aura Audit AI platform to Microsoft Azure using Infrastructure as Code (Terraform) and Kubernetes (AKS).

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Azure Resources](#azure-resources)
4. [Deployment Steps](#deployment-steps)
5. [Configuration](#configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Cost Optimization](#cost-optimization)
8. [Troubleshooting](#troubleshooting)
9. [Security & Compliance](#security--compliance)

## Prerequisites

### Required Tools

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.7.0/terraform_1.7.0_linux_amd64.zip
unzip terraform_1.7.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Azure Subscription Setup

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "<your-subscription-id>"

# Register required resource providers
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Cache
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.KeyVault
az provider register --namespace Microsoft.Network
az provider register --namespace Microsoft.OperationalInsights
```

### Service Principal for GitHub Actions

```bash
# Create service principal for CI/CD
az ad sp create-for-rbac \
  --name "aura-audit-ai-cicd" \
  --role contributor \
  --scopes /subscriptions/<subscription-id> \
  --sdk-auth

# Save the output JSON as GitHub secret: AZURE_CREDENTIALS
```

## Architecture Overview

### High-Level Architecture

```
                                  ┌─────────────────┐
                                  │  Azure DNS      │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ App Gateway     │
                                  │  + WAF          │
                                  └────────┬────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
           ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
           │  Frontend      │    │  API Services  │    │  Admin Portal  │
           │  (Next.js)     │    │  (10 services) │    │                │
           └────────────────┘    └───────┬────────┘    └────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
           ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
           │  PostgreSQL    │   │  Redis Cache   │   │  Blob Storage  │
           │  (pgvector)    │   │                │   │  (WORM)        │
           └────────────────┘   └────────────────┘   └────────────────┘
                    │
                    ▼
           ┌────────────────┐
           │  Key Vault     │
           │  (Secrets)     │
           └────────────────┘
```

### Components

- **AKS Cluster**: Kubernetes cluster for microservices
  - System node pool: 3x Standard_D4s_v3
  - Application node pool: 3x Standard_D8s_v3 (auto-scaling 3-9)

- **Azure Database for PostgreSQL Flexible Server**:
  - SKU: GP_Standard_D4s_v3
  - Storage: 128 GB
  - High Availability: Zone-redundant
  - Backup: 35 days retention, geo-redundant

- **Azure Cache for Redis Premium**:
  - P1 tier (6 GB)
  - Data persistence enabled
  - Geo-replication (optional)

- **Azure Blob Storage**:
  - GRS (geo-redundant)
  - Containers: workpapers, engagements, reports, atlas-worm
  - WORM retention: 7 years (2555 days)

- **Azure Container Registry Premium**:
  - Geo-replication enabled
  - Content trust & vulnerability scanning

- **Azure Key Vault Premium**:
  - HSM-backed keys
  - Soft delete & purge protection
  - RBAC authorization

- **Azure Application Gateway v2**:
  - WAF enabled (OWASP 3.2)
  - SSL termination
  - Auto-scaling (2-10 instances)

## Azure Resources

### Resource Naming Convention

```
{project}-{resource}-{environment}

Examples:
- aura-audit-ai-prod-rg         (Resource Group)
- aura-audit-ai-prod-aks        (AKS Cluster)
- aura-audit-ai-prod-psql       (PostgreSQL)
- auraauditaiprodacr            (Container Registry - no hyphens)
```

### Estimated Monthly Costs (Production)

| Resource | SKU/Tier | Estimated Cost |
|----------|----------|----------------|
| AKS (system nodes) | 3x D4s_v3 | $430 |
| AKS (app nodes) | 3x D8s_v3 | $860 |
| PostgreSQL | GP_Standard_D4s_v3 | $340 |
| Redis | P1 Premium | $300 |
| Blob Storage | GRS (100GB) | $25 |
| ACR | Premium | $200 |
| Application Gateway | WAF_v2 | $285 |
| Key Vault | Premium | $5 |
| Log Analytics | Pay-as-you-go | $50 |
| **Total** | | **~$2,495/month** |

## Deployment Steps

### 1. Clone Repository

```bash
git clone https://github.com/your-org/Data-Norm-2.git
cd Data-Norm-2
```

### 2. Configure Terraform Variables

Create `infra/azure/terraform.tfvars`:

```hcl
# General
location    = "eastus"
environment = "prod"

# AKS
kubernetes_version    = "1.28"
aks_system_node_count = 3
aks_app_node_count    = 3
aks_system_node_size  = "Standard_D4s_v3"
aks_app_node_size     = "Standard_D8s_v3"

# PostgreSQL
postgres_admin_username        = "atlasadmin"
postgres_sku                   = "GP_Standard_D4s_v3"
postgres_storage_mb            = 131072  # 128 GB
postgres_high_availability     = true
postgres_backup_retention_days = 35
postgres_geo_redundant_backup  = true

# Redis
redis_sku      = "Premium"
redis_family   = "P"
redis_capacity = 1

# Storage
storage_replication_type    = "GRS"
blob_delete_retention_days  = 30

# Application Gateway
appgw_sku_name  = "WAF_v2"
appgw_sku_tier  = "WAF_v2"
appgw_capacity  = 2

# Monitoring
log_retention_days = 90

# Tags
tags = {
  CostCenter = "Engineering"
  Owner      = "Platform Team"
}
```

### 3. Deploy Infrastructure

```bash
cd infra/azure

# Initialize Terraform
terraform init

# Review plan
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan

# Save outputs
terraform output -json > outputs.json
```

### 4. Configure kubectl

```bash
# Get AKS credentials
az aks get-credentials \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks

# Verify connection
kubectl get nodes
```

### 5. Install Application Gateway Ingress Controller

```bash
# Add Helm repo
helm repo add application-gateway-kubernetes-ingress https://appgwingress.blob.core.windows.net/ingress-azure-helm-package/
helm repo update

# Get Application Gateway details
APP_GW_NAME=$(terraform output -raw application_gateway_name)
RESOURCE_GROUP=$(terraform output -raw resource_group_name)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Install AGIC
helm install ingress-azure \
  application-gateway-kubernetes-ingress/ingress-azure \
  --namespace kube-system \
  --set appgw.name=$APP_GW_NAME \
  --set appgw.resourceGroup=$RESOURCE_GROUP \
  --set appgw.subscriptionId=$SUBSCRIPTION_ID \
  --set appgw.shared=false \
  --set kubernetes.watchNamespace=aura-audit-ai \
  --set armAuth.type=workloadIdentity \
  --set rbac.enabled=true
```

### 6. Install Secrets Store CSI Driver

```bash
# Install CSI driver for Azure Key Vault
helm repo add csi-secrets-store-provider-azure https://azure.github.io/secrets-store-csi-driver-provider-azure/charts
helm install csi-secrets-store-provider-azure/csi-secrets-store-provider-azure \
  --generate-name \
  --namespace kube-system \
  --set secrets-store-csi-driver.syncSecret.enabled=true
```

### 7. Build and Push Docker Images

```bash
# Login to ACR
ACR_NAME=$(terraform output -raw acr_login_server)
az acr login --name ${ACR_NAME%.azurecr.io}

# Build and push all services
SERVICES=("identity" "ingestion" "normalize" "analytics" "llm" "engagement" "disclosures" "reporting" "qc" "connectors")

for service in "${SERVICES[@]}"; do
  echo "Building $service..."
  docker build -t $ACR_NAME/aura/$service:latest \
    -f services/$service/Dockerfile \
    services/$service
  docker push $ACR_NAME/aura/$service:latest
done

# Build frontend
docker build -t $ACR_NAME/aura/web:latest frontend/
docker push $ACR_NAME/aura/web:latest
```

### 8. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f infra/k8s/base/namespace.yaml

# Get secrets from Key Vault
KEY_VAULT_NAME=$(terraform output -raw key_vault_name)
POSTGRES_HOST=$(terraform output -raw postgres_fqdn)
POSTGRES_PASSWORD=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name postgres-admin-password --query value -o tsv)
REDIS_HOST=$(terraform output -raw redis_hostname)
REDIS_KEY=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name redis-primary-key --query value -o tsv)

# Create secrets in Kubernetes
kubectl create secret generic aura-db-connection \
  --from-literal=connection-string="postgresql+asyncpg://atlasadmin:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/atlas?sslmode=require" \
  --namespace=aura-audit-ai

kubectl create secret generic aura-redis-connection \
  --from-literal=connection-string="rediss://:${REDIS_KEY}@${REDIS_HOST}:6380/0?ssl_cert_reqs=required" \
  --namespace=aura-audit-ai

# OpenAI API key (set manually or from CI/CD)
kubectl create secret generic aura-openai \
  --from-literal=api-key="sk-..." \
  --namespace=aura-audit-ai

# Apply ConfigMap
kubectl apply -f infra/k8s/base/configmap.yaml

# Apply ServiceAccount
kubectl apply -f infra/k8s/base/serviceaccount.yaml

# Deploy services
export ACR_NAME=$(terraform output -raw acr_login_server | sed 's/\.azurecr\.io//')
export IMAGE_TAG=latest

envsubst < infra/k8s/base/deployment-identity.yaml | kubectl apply -f -
envsubst < infra/k8s/base/deployments-all-services.yaml | kubectl apply -f -

# Apply Ingress
kubectl apply -f infra/k8s/base/ingress.yaml
```

### 9. Configure DNS

```bash
# Get Application Gateway Public IP
APP_GW_IP=$(az network public-ip show \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-appgw-pip \
  --query ipAddress -o tsv)

echo "Application Gateway IP: $APP_GW_IP"

# Create DNS A records:
# api.aura-audit-ai.com  -> $APP_GW_IP
# aura-audit-ai.com      -> $APP_GW_IP
# www.aura-audit-ai.com  -> $APP_GW_IP
```

### 10. Configure SSL Certificates

```bash
# Option 1: Use Let's Encrypt with cert-manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Create ClusterIssuer (see infra/k8s/cert-manager/)

# Option 2: Use Azure Key Vault Certificates
# Upload your SSL certificates to Key Vault
az keyvault certificate import \
  --vault-name $KEY_VAULT_NAME \
  --name aura-tls-cert \
  --file /path/to/cert.pfx
```

### 11. Run Database Migrations

```bash
# Connect to PostgreSQL
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U atlasadmin -d atlas -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run migrations (if using Alembic)
kubectl run -it --rm migration \
  --image=$ACR_NAME.azurecr.io/aura/identity:latest \
  --restart=Never \
  --namespace=aura-audit-ai \
  -- alembic upgrade head
```

### 12. Verify Deployment

```bash
# Check pod status
kubectl get pods -n aura-audit-ai

# Check services
kubectl get services -n aura-audit-ai

# Check ingress
kubectl get ingress -n aura-audit-ai

# Test health endpoints
curl http://$APP_GW_IP/health
curl http://$APP_GW_IP/api/identity/health
curl http://$APP_GW_IP/api/llm/health
```

## Configuration

### Environment Variables

Key environment variables are managed through:

1. **ConfigMap** (`aura-config`): Non-sensitive configuration
2. **Secrets** (`aura-db-connection`, `aura-redis-connection`, etc.): Sensitive data
3. **Azure Key Vault**: Central secret management

### Scaling Configuration

```bash
# Manually scale a deployment
kubectl scale deployment identity --replicas=5 -n aura-audit-ai

# HPA automatically scales based on CPU/Memory (already configured)
kubectl get hpa -n aura-audit-ai
```

### Resource Limits

Default resource allocation per service:

- **Identity, Normalize, Engagement, QC**: 250m CPU, 512Mi RAM
- **Analytics, LLM**: 500m CPU, 1-2Gi RAM
- **Ingestion, Reporting**: 250m CPU, 512Mi-1Gi RAM

Adjust in deployment manifests as needed.

## Monitoring & Maintenance

### Azure Monitor

```bash
# View Application Insights
az monitor app-insights component show \
  --resource-group aura-audit-ai-prod-rg \
  --app aura-audit-ai-prod-appinsights

# Get instrumentation key
az monitor app-insights component show \
  --resource-group aura-audit-ai-prod-rg \
  --app aura-audit-ai-prod-appinsights \
  --query instrumentationKey -o tsv
```

### Log Analytics Queries

Access Log Analytics workspace in Azure Portal:

```kusto
// Failed requests
requests
| where success == false
| summarize count() by resultCode, name
| order by count_ desc

// Slow requests
requests
| where duration > 1000
| project timestamp, name, duration, resultCode
| order by duration desc

// Exception tracking
exceptions
| summarize count() by type, outerMessage
| order by count_ desc
```

### Kubectl Monitoring

```bash
# View logs
kubectl logs -f deployment/llm -n aura-audit-ai
kubectl logs -f deployment/analytics -n aura-audit-ai

# View events
kubectl get events -n aura-audit-ai --sort-by='.lastTimestamp'

# Resource usage
kubectl top nodes
kubectl top pods -n aura-audit-ai
```

### Alerts

Configure alerts in Azure Monitor for:

- Pod crash loops
- High CPU/memory usage
- Failed deployments
- Database connection failures
- High error rates
- Response time degradation

## Cost Optimization

### Development Environment

For dev/staging, use smaller SKUs:

```hcl
# Dev environment terraform.tfvars
aks_system_node_count = 1
aks_app_node_count = 2
aks_system_node_size = "Standard_D2s_v3"
aks_app_node_size = "Standard_D4s_v3"
postgres_sku = "B_Standard_B2s"
postgres_high_availability = false
redis_sku = "Standard"
redis_capacity = 0
storage_replication_type = "LRS"
appgw_capacity = 1
```

### Cost Saving Tips

1. **Stop non-prod environments overnight**:
   ```bash
   az aks stop --name aura-audit-ai-dev-aks --resource-group aura-audit-ai-dev-rg
   az aks start --name aura-audit-ai-dev-aks --resource-group aura-audit-ai-dev-rg
   ```

2. **Use Azure Reservations**: Save up to 72% with 3-year reservations

3. **Right-size resources**: Monitor usage and adjust VM sizes

4. **Enable autoscaling**: Scale down during low traffic

5. **Use Azure Hybrid Benefit**: If you have Windows Server licenses

## Troubleshooting

### Common Issues

#### Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n aura-audit-ai

# Common causes:
# 1. Image pull errors - verify ACR authentication
# 2. Resource limits - increase CPU/memory
# 3. Database connection - check secrets
```

#### Database connection errors

```bash
# Test PostgreSQL connectivity
kubectl run -it --rm psql-test \
  --image=postgres:15 \
  --restart=Never \
  --namespace=aura-audit-ai \
  -- psql -h <postgres-host> -U atlasadmin -d atlas

# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-psql
```

#### Ingress not working

```bash
# Check AGIC pod logs
kubectl logs -l app=ingress-azure -n kube-system

# Verify Application Gateway configuration
az network application-gateway show \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-appgw
```

#### High costs

```bash
# Cost analysis
az consumption usage list --start-date 2024-01-01 --end-date 2024-01-31

# Identify expensive resources
az costmanagement query --type Usage --dataset-granularity Daily \
  --timeframe MonthToDate
```

## Security & Compliance

### Security Checklist

- ✅ Network isolation (VNet, subnets, NSGs)
- ✅ Encryption at rest (PostgreSQL, Storage, Redis)
- ✅ Encryption in transit (TLS 1.2+)
- ✅ Key management (Azure Key Vault)
- ✅ Secrets rotation (automated via Key Vault)
- ✅ RBAC (Azure AD + Kubernetes)
- ✅ WAF protection (OWASP rules)
- ✅ Private endpoints (Redis, PostgreSQL)
- ✅ Container scanning (ACR vulnerability scanning)
- ✅ Audit logging (Log Analytics)
- ✅ WORM storage (7-year retention)
- ✅ Backup & DR (geo-redundant)

### Compliance Standards

Platform meets requirements for:

- **PCAOB**: Audit trail, data integrity, retention
- **AICPA**: Security, confidentiality, availability
- **SEC**: Record retention, immutability
- **SOC 2**: Security controls, monitoring
- **GDPR**: Data protection, privacy (if applicable)

### Penetration Testing

Before production:

1. Run Azure Security Center recommendations
2. Conduct external penetration testing
3. Review OWASP Top 10 vulnerabilities
4. Perform load testing
5. Validate disaster recovery procedures

## Support

For deployment issues:

- **Documentation**: [docs.aura-audit-ai.com](https://docs.aura-audit-ai.com)
- **GitHub Issues**: [github.com/your-org/Data-Norm-2/issues](https://github.com/your-org/Data-Norm-2/issues)
- **Email**: devops@aura-audit-ai.com

## License

Copyright © 2024 Aura Audit AI. All rights reserved.
