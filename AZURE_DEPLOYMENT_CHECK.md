# Azure Deployment Verification & Manual Deployment Guide

## Current Situation

The GitHub Actions workflows completed quickly (< 2 minutes), which indicates they may have:
1. Skipped the build phase (Azure credentials not configured)
2. Failed early in the process
3. Only run CI/CD checks without actual deployment

**A full deployment with 26 services should take 20-30 minutes.**

---

## Option 1: Trigger Manual Deployment via GitHub Actions

### Step 1: Configure Azure Credentials (One-time setup)

If not already done, you need to add Azure credentials to GitHub Secrets:

```bash
# Login to Azure
az login

# Get your subscription ID
az account show --query id -o tsv

# Create a service principal
az ad sp create-for-rbac \
  --name "github-actions-aura-audit-ai" \
  --role contributor \
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>/resourceGroups/aura-audit-ai-prod-rg \
  --sdk-auth

# Copy the JSON output
```

Then add to GitHub:
1. Go to: https://github.com/jtoroni309-creator/Data-Norm-2/settings/secrets/actions
2. Click "New repository secret"
3. Name: `AZURE_CREDENTIALS`
4. Value: Paste the JSON from the service principal creation

### Step 2: Add Other Required Secrets

```bash
# In GitHub repo settings → Secrets → Actions, add:

# OPENAI_API_KEY
# Your OpenAI API key for LLM services

# Any other service-specific secrets
```

### Step 3: Trigger Workflow Manually

1. Go to: https://github.com/jtoroni309-creator/Data-Norm-2/actions
2. Click "Deploy to Azure" workflow
3. Click "Run workflow" button
4. Select environment: `prod`
5. Click "Run workflow"

This will trigger a full deployment.

---

## Option 2: Manual Deployment Using Azure CLI

If GitHub Actions isn't configured, deploy manually:

### Prerequisites

```bash
# Install required tools
# - Azure CLI: https://aka.ms/azure-cli
# - kubectl: https://kubernetes.io/docs/tasks/tools/
# - Docker: https://www.docker.com/get-started

# Verify installations
az --version
kubectl version --client
docker --version
```

### Step 1: Login and Set Context

```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account list --output table
az account set --subscription <subscription-name-or-id>

# Login to ACR
az acr login --name auraauditaiprodacr

# Get AKS credentials
az aks get-credentials \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks \
  --overwrite-existing
```

### Step 2: Build and Push All Images

```bash
cd "C:\Users\jtoroni\Data Norm\Data-Norm-2"

# Option A: Use the build script (if on Linux/WSL)
./build-and-push.sh

# Option B: Build manually (Windows/PowerShell)
$ACR_LOGIN_SERVER = "auraauditaiprodacr.azurecr.io"
$IMAGE_TAG = "manual-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Build all services
$services = @(
  "identity", "gateway", "llm", "analytics", "ingestion", "normalize",
  "engagement", "reporting", "disclosures", "qc", "connectors",
  "reg-ab-audit", "audit-planning", "accounting-integrations",
  "data-anonymization", "financial-analysis", "fraud-detection",
  "related-party", "sampling", "security", "subsequent-events",
  "substantive-testing", "training-data", "eo-insurance-portal",
  "estimates-evaluation"
)

foreach ($service in $services) {
    Write-Host "Building $service..." -ForegroundColor Cyan

    docker build `
        -t "$ACR_LOGIN_SERVER/aura/${service}:$IMAGE_TAG" `
        -t "$ACR_LOGIN_SERVER/aura/${service}:latest" `
        "./services/$service"

    Write-Host "Pushing $service..." -ForegroundColor Yellow
    docker push "$ACR_LOGIN_SERVER/aura/${service}:$IMAGE_TAG"
    docker push "$ACR_LOGIN_SERVER/aura/${service}:latest"

    Write-Host "✓ $service complete" -ForegroundColor Green
}

# Build CPA Portal
Write-Host "Building CPA Portal..." -ForegroundColor Cyan
docker build `
    -t "$ACR_LOGIN_SERVER/aura/cpa-portal:$IMAGE_TAG" `
    -t "$ACR_LOGIN_SERVER/aura/cpa-portal:latest" `
    "./client-portal"
docker push "$ACR_LOGIN_SERVER/aura/cpa-portal:$IMAGE_TAG"
docker push "$ACR_LOGIN_SERVER/aura/cpa-portal:latest"

# Build Marketing Site
Write-Host "Building Marketing Site..." -ForegroundColor Cyan
docker build `
    -t "$ACR_LOGIN_SERVER/aura/marketing:$IMAGE_TAG" `
    -t "$ACR_LOGIN_SERVER/aura/marketing:latest" `
    "./marketing-site"
docker push "$ACR_LOGIN_SERVER/aura/marketing:$IMAGE_TAG"
docker push "$ACR_LOGIN_SERVER/aura/marketing:latest"

Write-Host "All images built and pushed!" -ForegroundColor Green
```

### Step 3: Deploy to Kubernetes

```bash
cd "C:\Users\jtoroni\Data Norm\Data-Norm-2"

# Set environment variables
$env:ACR_NAME = "auraauditaiprodacr"
$env:IMAGE_TAG = "latest"  # or use the tag from Step 2

# Apply namespace
kubectl apply -f infra/k8s/base/namespace.yaml

# Create secrets (if not already exist)
# Note: You'll need to get these values from Azure Key Vault or your secure storage

# Database connection
kubectl create secret generic aura-db-connection `
  --from-literal=connection-string="<your-postgres-connection-string>" `
  --namespace=aura-audit-ai `
  --dry-run=client -o yaml | kubectl apply -f -

# Redis connection
kubectl create secret generic aura-redis-connection `
  --from-literal=connection-string="<your-redis-connection-string>" `
  --namespace=aura-audit-ai `
  --dry-run=client -o yaml | kubectl apply -f -

# OpenAI secret
kubectl create secret generic aura-secrets `
  --from-literal=openai-api-key="<your-openai-key>" `
  --from-literal=storage-connection-string="<your-storage-connection>" `
  --namespace=aura-audit-ai `
  --dry-run=client -o yaml | kubectl apply -f -

# Apply ConfigMap
kubectl apply -f infra/k8s/base/configmap.yaml

# Apply ServiceAccount
kubectl apply -f infra/k8s/base/serviceaccount.yaml

# Deploy services (using envsubst on Linux, or manually replace on Windows)
# For Windows PowerShell, you need to replace ${ACR_NAME} and ${IMAGE_TAG} manually
# or install envsubst for Windows

# Deploy identity
(Get-Content infra/k8s/base/deployment-identity.yaml) `
  -replace '\$\{ACR_NAME\}', $env:ACR_NAME `
  -replace '\$\{IMAGE_TAG\}', $env:IMAGE_TAG | kubectl apply -f -

# Deploy gateway
(Get-Content infra/k8s/base/deployment-gateway.yaml) `
  -replace '\$\{ACR_NAME\}', $env:ACR_NAME `
  -replace '\$\{IMAGE_TAG\}', $env:IMAGE_TAG | kubectl apply -f -

# Deploy all services
(Get-Content infra/k8s/base/deployments-all-services.yaml) `
  -replace '\$\{ACR_NAME\}', $env:ACR_NAME `
  -replace '\$\{IMAGE_TAG\}', $env:IMAGE_TAG | kubectl apply -f -

# Deploy client portal
(Get-Content infra/k8s/base/deployment-client-portal.yaml) `
  -replace '\$\{ACR_NAME\}', $env:ACR_NAME `
  -replace '\$\{IMAGE_TAG\}', $env:IMAGE_TAG | kubectl apply -f -

# Deploy marketing (if exists)
if (Test-Path infra/k8s/base/deployment-marketing.yaml) {
    (Get-Content infra/k8s/base/deployment-marketing.yaml) `
      -replace '\$\{ACR_NAME\}', $env:ACR_NAME `
      -replace '\$\{IMAGE_TAG\}', $env:IMAGE_TAG | kubectl apply -f -
}

# Apply ingress
kubectl apply -f infra/k8s/base/ingress.yaml
kubectl apply -f infra/k8s/base/ingress-auraa.yaml
```

### Step 4: Wait for Deployments

```bash
# Check deployment status
kubectl get deployments -n aura-audit-ai

# Wait for specific deployments
kubectl rollout status deployment/identity -n aura-audit-ai --timeout=5m
kubectl rollout status deployment/gateway -n aura-audit-ai --timeout=5m
kubectl rollout status deployment/llm -n aura-audit-ai --timeout=5m
kubectl rollout status deployment/client-portal -n aura-audit-ai --timeout=5m

# Check all pods
kubectl get pods -n aura-audit-ai
```

---

## Verification Checklist

### 1. Check Images in ACR

```bash
# List all repositories
az acr repository list --name auraauditaiprodacr --output table

# Verify specific images
az acr repository show-tags --name auraauditaiprodacr --repository aura/gateway
az acr repository show-tags --name auraauditaiprodacr --repository aura/reg-ab-audit
az acr repository show-tags --name auraauditaiprodacr --repository aura/fraud-detection
az acr repository show-tags --name auraauditaiprodacr --repository aura/financial-analysis
```

Expected: All 26 images should exist with `latest` tag

### 2. Check AKS Deployments

```bash
# Get all deployments
kubectl get deployments -n aura-audit-ai -o wide

# Count deployments
kubectl get deployments -n aura-audit-ai --no-headers | wc -l
```

Expected: Should see at least 26 deployments

### 3. Check Pods Status

```bash
# Get all pods
kubectl get pods -n aura-audit-ai

# Count running pods
kubectl get pods -n aura-audit-ai --field-selector=status.phase=Running --no-headers | wc -l

# Check for issues
kubectl get pods -n aura-audit-ai | grep -v Running
```

Expected: All pods should be "Running" with "READY 1/1" (or higher for multi-replica)

### 4. Check ML/AI Related Services

```bash
# Specifically check ML-related services
kubectl get deployment -n aura-audit-ai | grep -E "(llm|fraud-detection|financial-analysis|training-data)"

# Check pods for ML services
kubectl get pods -n aura-audit-ai -l app=llm
kubectl get pods -n aura-audit-ai -l app=fraud-detection
kubectl get pods -n aura-audit-ai -l app=financial-analysis
kubectl get pods -n aura-audit-ai -l app=training-data
```

Expected: Each ML service should have running pods

### 5. Test Gateway and Services

```bash
# Port forward to gateway
kubectl port-forward -n aura-audit-ai svc/gateway 8080:80

# In another terminal, test health
curl http://localhost:8080/health

# Test service discovery
curl http://localhost:8080/health/services | jq
```

Expected:
- Gateway health returns: `{"status":"healthy"...}`
- Service health shows all 24 services as "healthy"

### 6. Test External Access

```bash
# Get ingress IP
kubectl get ingress -n aura-audit-ai -o wide

# Test API
curl https://api.auraai.toroniandcompany.com/health

# Test CPA Portal
curl https://cpa.auraa.toroniandcompany.com/
```

---

## ML Services Deployment Checklist

Specifically verify these ML/AI services are deployed:

- [ ] **llm** - LLM and embeddings service
- [ ] **fraud-detection** - Fraud detection ML models
- [ ] **financial-analysis** - Financial analysis with ML
- [ ] **training-data** - ML training data management
- [ ] **analytics** - Analytics with ML capabilities
- [ ] **substantive-testing** - ML-powered substantive testing
- [ ] **estimates-evaluation** - ML-based estimates evaluation

Verification command:
```bash
kubectl get deployments -n aura-audit-ai | grep -E "(llm|fraud|financial|training|analytics|substantive|estimates)"
```

---

## Troubleshooting

### Images Not in ACR

**Problem**: `az acr repository list` doesn't show expected images

**Solution**:
```bash
# Check ACR login
az acr login --name auraauditaiprodacr

# Manually build and push missing image
docker build -t auraauditaiprodacr.azurecr.io/aura/<service>:latest ./services/<service>
docker push auraauditaiprodacr.azurecr.io/aura/<service>:latest
```

### Pods in ImagePullBackOff

**Problem**: Pod can't pull image from ACR

**Solution**:
```bash
# Check ACR attachment to AKS
az aks check-acr \
  --name aura-audit-ai-prod-aks \
  --resource-group aura-audit-ai-prod-rg \
  --acr auraauditaiprodacr.azurecr.io

# Attach ACR to AKS (if needed)
az aks update \
  --name aura-audit-ai-prod-aks \
  --resource-group aura-audit-ai-prod-rg \
  --attach-acr auraauditaiprodacr
```

### Pods in CrashLoopBackOff

**Problem**: Application error on startup

**Solution**:
```bash
# Check logs
kubectl logs -n aura-audit-ai deployment/<service-name> --tail=100

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Redis connection failed
# - Missing secrets

# Check events
kubectl describe pod -n aura-audit-ai <pod-name>
```

### Services Not Accessible

**Problem**: Can't reach API or CPA portal

**Solution**:
```bash
# Check ingress
kubectl get ingress -n aura-audit-ai
kubectl describe ingress -n aura-audit-ai aura-api-ingress

# Check DNS
nslookup api.auraai.toroniandcompany.com
nslookup cpa.auraa.toroniandcompany.com

# Verify ingress controller
kubectl get pods -n ingress-nginx  # or wherever your ingress controller is
```

---

## Quick Deployment Script (Linux/WSL)

Save as `deploy-all.sh`:

```bash
#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "🚀 Starting full deployment..."

# Build and push
echo "📦 Building and pushing images..."
./build-and-push.sh

# Deploy to K8s
echo "☸️  Deploying to Kubernetes..."
./infra/azure/deploy.sh prod false true false

echo "✅ Deployment complete!"
echo "🔍 Verify with: kubectl get pods -n aura-audit-ai"
```

Make executable:
```bash
chmod +x deploy-all.sh
./deploy-all.sh
```

---

## Summary

**To ensure ML services and all 26 services are deployed:**

1. **Verify ACR has all images**: `az acr repository list --name auraauditaiprodacr`
2. **Check K8s deployments**: `kubectl get deployments -n aura-audit-ai`
3. **Verify pods running**: `kubectl get pods -n aura-audit-ai`
4. **Test gateway**: `curl https://api.auraai.toroniandcompany.com/health`
5. **Test CPA portal**: `curl https://cpa.auraa.toroniandcompany.com/`

If GitHub Actions isn't deploying, use **Option 2: Manual Deployment** above.

---

**Need Help?**
- Check logs: `kubectl logs -n aura-audit-ai deployment/<service-name>`
- Check events: `kubectl get events -n aura-audit-ai --sort-by='.lastTimestamp'`
- Describe pod: `kubectl describe pod -n aura-audit-ai <pod-name>`
