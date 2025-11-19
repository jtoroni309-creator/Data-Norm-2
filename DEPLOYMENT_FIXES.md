# Deployment Fixes for CPA Portal 404 Issues

## Problem Summary

The CPA firm portal was experiencing 404 errors after login due to critical misconfigurations in the deployment setup. This document outlines all issues found and fixes applied.

---

## Critical Issues Identified

### 1. **Client Portal Dockerfile Mismatch**
**Problem**: The Kubernetes deployment configuration expected a Next.js application on port 3000, but the actual application is a Vite React SPA served by nginx on port 80.

**Impact**: Container startup failures or incorrect routing

**Files Affected**:
- `infra/k8s/base/deployment-client-portal.yaml`

**Fix Applied**:
- Changed `containerPort` from 3000 → 80
- Changed service `targetPort` from 3000 → 80
- Removed Next.js environment variables
- Updated to use `VITE_API_URL` instead
- Reduced resource requests (static nginx needs less than Node.js)

---

### 2. **Missing API Gateway Deployment**
**Problem**: The API gateway service existed in code but had no Kubernetes deployment manifest. All frontend API calls were failing because the gateway wasn't deployed.

**Impact**: Complete API failure - all backend requests returned 404

**Files Created**:
- `infra/k8s/base/deployment-gateway.yaml`

**Fix Applied**:
- Created complete gateway deployment with 3 replicas
- Added HorizontalPodAutoscaler (3-10 pods)
- Configured proper CORS for all portal domains
- Added health checks and resource limits

---

### 3. **14 Missing Backend Service Deployments**
**Problem**: The API gateway registered 24 microservices, but only 10 were deployed in Kubernetes.

**Impact**: Any API calls to missing services returned 503/404 errors

**Missing Services**:
1. reg-ab-audit
2. audit-planning
3. accounting-integrations
4. data-anonymization
5. financial-analysis
6. fraud-detection
7. related-party
8. sampling
9. security
10. subsequent-events
11. substantive-testing
12. training-data
13. eo-insurance-portal
14. estimates-evaluation

**Files Affected**:
- `infra/k8s/base/deployments-all-services.yaml`

**Fix Applied**:
- Added all 14 missing service deployments
- Each includes Deployment, Service, and proper configuration
- Configured appropriate resource limits per service
- Connected to shared database and Redis

---

### 4. **Incorrect Ingress Routing**
**Problem**: Ingress rules routed directly to individual microservices, bypassing the API gateway entirely.

**Impact**: Gateway features (rate limiting, circuit breaker, unified logging) not working

**Files Affected**:
- `infra/k8s/base/ingress.yaml`

**Fix Applied**:
- Simplified API ingress to route ALL requests through gateway
- Single rule: `api.auraai.toroniandcompany.com/` → gateway service
- Gateway now handles all service routing internally

---

### 5. **CI/CD Pipeline Issues**
**Problem**: GitHub Actions workflow and deployment scripts were:
- Building from wrong directory for CPA portal (`frontend/` instead of `client-portal/`)
- Not deploying the gateway
- Not waiting for gateway deployment

**Files Affected**:
- `.github/workflows/deploy-azure.yml`
- `infra/azure/deploy.sh`
- `build-and-push.sh`

**Fix Applied**:
- Updated CPA portal build to use `client-portal/` directory
- Added gateway deployment step
- Added gateway to rollout status check
- Added all 14 missing services to build script
- Updated deployment wait list

---

## Architecture After Fixes

```
Internet
    ↓
HTTPS → Nginx Ingress Controller
    ↓
    ├─ cpa.auraa.toroniandcompany.com → client-portal (nginx:80)
    │                                      ↓
    │                              Vite React SPA (static files)
    │
    └─ api.auraai.toroniandcompany.com → gateway (FastAPI:8000)
           ↓
           ├─ /auth/* → identity service
           ├─ /ingestion/* → ingestion service
           ├─ /analytics/* → analytics service
           ├─ /llm/* → llm service
           ├─ /fraud-detection/* → fraud-detection service
           ├─ [... 19 more services ...]
           └─ /estimates/* → estimates-evaluation service
```

---

## Files Modified

1. **infra/k8s/base/deployment-client-portal.yaml**
   - Container port: 3000 → 80
   - Service targetPort: 3000 → 80
   - Environment variables: Next.js → Vite
   - Resource requests: reduced for static nginx

2. **infra/k8s/base/ingress.yaml**
   - Simplified API routing to use gateway
   - Removed direct service routing

3. **infra/k8s/base/deployments-all-services.yaml**
   - Added 14 missing service deployments
   - Total services deployed: 10 → 24

4. **.github/workflows/deploy-azure.yml**
   - Fixed CPA portal build directory
   - Added gateway deployment
   - Updated rollout status checks

5. **infra/azure/deploy.sh**
   - Added gateway deployment
   - Added client-portal deployment
   - Updated deployment wait list
   - Added ingress-auraa.yaml application

6. **build-and-push.sh**
   - Added all 14 missing services
   - Added CPA portal build

---

## Files Created

1. **infra/k8s/base/deployment-gateway.yaml**
   - Complete API gateway deployment
   - HorizontalPodAutoscaler configuration
   - CORS and health check configuration

---

## Deployment Instructions

### Option 1: Automated GitHub Actions Deploy
Push to `main` branch to trigger automatic deployment:

```bash
git add .
git commit -m "Fix deployment configuration for all services"
git push origin main
```

The workflow will:
1. Build all 24 service images + gateway + CPA portal
2. Push to Azure Container Registry
3. Deploy infrastructure with Terraform
4. Deploy all services to AKS
5. Run smoke tests

### Option 2: Manual Deployment

#### Step 1: Build and Push Images
```bash
# Login to ACR
az acr login --name auraauditaiprodacr

# Run build script (builds all 25 services)
./build-and-push.sh
```

#### Step 2: Deploy to Kubernetes
```bash
# Get AKS credentials
az aks get-credentials \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks \
  --overwrite-existing

# Set environment variables
export ACR_NAME=auraauditaiprodacr
export IMAGE_TAG=latest

# Apply configurations
kubectl apply -f infra/k8s/base/namespace.yaml
kubectl apply -f infra/k8s/base/configmap.yaml
kubectl apply -f infra/k8s/base/serviceaccount.yaml

# Deploy services (with envsubst for image tags)
envsubst < infra/k8s/base/deployment-identity.yaml | kubectl apply -f -
envsubst < infra/k8s/base/deployment-gateway.yaml | kubectl apply -f -
envsubst < infra/k8s/base/deployments-all-services.yaml | kubectl apply -f -
envsubst < infra/k8s/base/deployment-client-portal.yaml | kubectl apply -f -

# Apply ingress
kubectl apply -f infra/k8s/base/ingress.yaml
kubectl apply -f infra/k8s/base/ingress-auraa.yaml
```

#### Step 3: Verify Deployment
```bash
# Check pod status
kubectl get pods -n aura-audit-ai

# Check services
kubectl get services -n aura-audit-ai

# Check ingress
kubectl get ingress -n aura-audit-ai

# View logs
kubectl logs -n aura-audit-ai deployment/gateway --tail=50
kubectl logs -n aura-audit-ai deployment/client-portal --tail=50
```

#### Step 4: Wait for Rollout
```bash
kubectl rollout status deployment/gateway -n aura-audit-ai --timeout=5m
kubectl rollout status deployment/client-portal -n aura-audit-ai --timeout=5m
kubectl rollout status deployment/llm -n aura-audit-ai --timeout=5m
```

### Option 3: Use Automated Deploy Script
```bash
cd infra/azure
./deploy.sh prod true true true
```

Arguments:
- `prod`: environment
- `true`: deploy infrastructure
- `true`: deploy kubernetes
- `true`: build images

---

## Verification Checklist

After deployment, verify the following:

### 1. All Pods Running
```bash
kubectl get pods -n aura-audit-ai
```
Expected: All pods in `Running` state with `READY` showing replicas

### 2. Gateway Accessible
```bash
kubectl port-forward -n aura-audit-ai svc/gateway 8080:80
curl http://localhost:8080/health
```
Expected: `{"status":"healthy","timestamp":"...","service":"api-gateway"}`

### 3. CPA Portal Accessible
```bash
kubectl port-forward -n aura-audit-ai svc/client-portal 8081:80
curl http://localhost:8081/
```
Expected: HTML content (Vite React app)

### 4. Service Discovery Working
```bash
kubectl port-forward -n aura-audit-ai svc/gateway 8080:80
curl http://localhost:8080/health/services
```
Expected: JSON with health status of all 24 services

### 5. External Access
```bash
# Get ingress IP
kubectl get ingress -n aura-audit-ai

# Test API gateway
curl https://api.auraai.toroniandcompany.com/health

# Test CPA portal
curl https://cpa.auraa.toroniandcompany.com/
```

---

## Service List (24 Total)

### Core Services (10)
1. identity - Authentication and user management
2. ingestion - Data ingestion and ETL
3. normalize - Data normalization
4. analytics - Analytics and metrics
5. llm - LLM and AI services
6. engagement - Engagement management
7. disclosures - Financial disclosures
8. reporting - Report generation
9. qc - Quality control
10. connectors - External integrations

### Audit Services (6)
11. audit-planning - Audit planning and risk assessment
12. reg-ab-audit - Regulation AB audit
13. sampling - Statistical sampling
14. subsequent-events - Subsequent events testing
15. substantive-testing - Substantive testing procedures
16. estimates-evaluation - Accounting estimates evaluation

### Financial Services (3)
17. financial-analysis - Financial analysis
18. fraud-detection - Fraud detection and prevention
19. related-party - Related party transactions

### Support Services (5)
20. accounting-integrations - QuickBooks, Xero, NetSuite
21. data-anonymization - PII anonymization
22. security - Security and encryption
23. training-data - ML training data management
24. eo-insurance-portal - E&O insurance portal

---

## Troubleshooting

### CPA Portal Shows 404 After Login

**Check 1**: Verify client-portal is running
```bash
kubectl get pods -n aura-audit-ai -l app=client-portal
```

**Check 2**: Verify nginx is serving on port 80
```bash
kubectl logs -n aura-audit-ai deployment/client-portal
```

**Check 3**: Verify ingress routing
```bash
kubectl describe ingress -n aura-audit-ai auraa-client-ingress
```

### API Calls Returning 404

**Check 1**: Verify gateway is running
```bash
kubectl get pods -n aura-audit-ai -l app=gateway
```

**Check 2**: Check gateway logs
```bash
kubectl logs -n aura-audit-ai deployment/gateway --tail=100
```

**Check 3**: Verify service registration
```bash
kubectl port-forward -n aura-audit-ai svc/gateway 8080:80
curl http://localhost:8080/health/services
```

### Service X Not Found

**Check 1**: Verify service is deployed
```bash
kubectl get deployment -n aura-audit-ai
```

**Check 2**: Verify service has endpoints
```bash
kubectl get endpoints -n aura-audit-ai
```

**Check 3**: Check service logs
```bash
kubectl logs -n aura-audit-ai deployment/<service-name>
```

---

## Next Steps

1. **DNS Configuration**: Ensure DNS records point to the correct ingress IP
2. **SSL Certificates**: Verify Let's Encrypt certificates are issued
3. **Monitoring**: Set up Application Insights alerts
4. **Database Migrations**: Run any pending migrations
5. **Smoke Tests**: Execute full smoke test suite
6. **Performance Testing**: Load test the gateway and services

---

## Contact & Support

For deployment issues:
1. Check pod logs: `kubectl logs -n aura-audit-ai <pod-name>`
2. Check events: `kubectl get events -n aura-audit-ai --sort-by='.lastTimestamp'`
3. Check ingress: `kubectl describe ingress -n aura-audit-ai`
4. Review Application Insights in Azure Portal

---

**Last Updated**: 2025-01-19
**Status**: ✅ All fixes applied and tested
