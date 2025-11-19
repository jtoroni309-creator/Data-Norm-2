# Deployment Verification Guide

## Current Status

**Deployment Started**: GitHub Actions workflow #65 "Deploy to Azure" is currently running
**Commit**: 0abde85 - Fix deployment configuration - resolve CPA portal 404 errors
**Branch**: main
**Triggered By**: Push to main

---

## Monitor Deployment Progress

### 1. GitHub Actions Workflow
View live deployment status:
```
https://github.com/jtoroni309-creator/Data-Norm-2/actions
```

Look for workflow: **"Deploy to Azure #65"**

Expected stages:
- ✅ Build & Push Images (24 services + gateway + CPA portal) - ~15-20 min
- ⏳ Deploy Infrastructure (Terraform) - ~5 min
- ⏳ Deploy to Kubernetes (AKS) - ~5-10 min
- ⏳ Run Smoke Tests - ~2 min

### 2. Azure Portal Monitoring
Monitor resources in Azure:
```
https://portal.azure.com/#resource/subscriptions/.../resourceGroups/aura-audit-ai-prod-rg
```

---

## Verification Checklist

### Phase 1: Build Verification (In Progress)

The following Docker images should be built and pushed to ACR:

**Backend Services (24)**:
1. ✅ identity
2. ✅ gateway (NEW - previously missing!)
3. ✅ llm
4. ✅ analytics
5. ✅ ingestion
6. ✅ normalize
7. ✅ engagement
8. ✅ reporting
9. ✅ disclosures
10. ✅ qc
11. ✅ connectors
12. ✅ reg-ab-audit (NEW!)
13. ✅ audit-planning (NEW!)
14. ✅ accounting-integrations (NEW!)
15. ✅ data-anonymization (NEW!)
16. ✅ financial-analysis (NEW!)
17. ✅ fraud-detection (NEW!)
18. ✅ related-party (NEW!)
19. ✅ sampling (NEW!)
20. ✅ security (NEW!)
21. ✅ subsequent-events (NEW!)
22. ✅ substantive-testing (NEW!)
23. ✅ training-data (NEW!)
24. ✅ eo-insurance-portal (NEW!)
25. ✅ estimates-evaluation (NEW!)

**Frontend Applications (2)**:
26. ✅ cpa-portal (FIXED - now builds from client-portal/)
27. ✅ marketing

**Total**: 26 Docker images

---

### Phase 2: Infrastructure Verification

Once Terraform completes, verify:

```bash
# Login to Azure
az login

# Set subscription (if needed)
az account set --subscription <subscription-id>

# Check AKS cluster
az aks show \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks \
  --query "provisioningState"
```

Expected: `"Succeeded"`

---

### Phase 3: Kubernetes Deployment Verification

#### Option A: Via Azure Portal
1. Go to Azure Portal → Resource Groups → aura-audit-ai-prod-rg
2. Click on AKS cluster: aura-audit-ai-prod-aks
3. Click "Workloads" in left menu
4. Verify all deployments are running

#### Option B: Via kubectl (if you have access)

**Step 1: Get AKS credentials**
```bash
az aks get-credentials \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks \
  --overwrite-existing
```

**Step 2: Check namespace**
```bash
kubectl get namespace aura-audit-ai
```
Expected: `Active`

**Step 3: Check all pods**
```bash
kubectl get pods -n aura-audit-ai
```

Expected output format:
```
NAME                                    READY   STATUS    RESTARTS   AGE
identity-xxxxx-xxxxx                    1/1     Running   0          5m
gateway-xxxxx-xxxxx                     1/1     Running   0          5m  ← NEW!
llm-xxxxx-xxxxx                         1/1     Running   0          5m
analytics-xxxxx-xxxxx                   1/1     Running   0          5m
...
client-portal-xxxxx-xxxxx               1/1     Running   0          5m  ← FIXED!
reg-ab-audit-xxxxx-xxxxx                1/1     Running   0          5m  ← NEW!
audit-planning-xxxxx-xxxxx              1/1     Running   0          5m  ← NEW!
...
```

All pods should show:
- READY: 1/1 (or higher if replicas > 1)
- STATUS: Running
- No excessive RESTARTS

**Step 4: Check deployments**
```bash
kubectl get deployments -n aura-audit-ai
```

Expected: 26 deployments (24 services + gateway + client-portal + marketing + identity)

**Step 5: Check services**
```bash
kubectl get services -n aura-audit-ai
```

Expected: Each deployment should have a corresponding ClusterIP service

**Step 6: Check ingress**
```bash
kubectl get ingress -n aura-audit-ai
```

Expected ingress rules:
- `aura-api-ingress` → api.auraai.toroniandcompany.com → gateway:80
- `aura-client-ingress` → cpa.auraai.toroniandcompany.com → client-portal:80
- `auraa-client-ingress` → cpa.auraa.toroniandcompany.com → client-portal:80

**Step 7: Verify Gateway is routing correctly**
```bash
# Port forward to gateway
kubectl port-forward -n aura-audit-ai svc/gateway 8080:80

# In another terminal, test gateway health
curl http://localhost:8080/health

# Test service discovery
curl http://localhost:8080/health/services
```

Expected response from `/health/services`:
```json
{
  "overall_status": "healthy",
  "healthy_services": 24,
  "total_services": 24,
  "services": {
    "identity": {"status": "healthy", ...},
    "ingestion": {"status": "healthy", ...},
    "gateway": {"status": "healthy", ...},
    ...
  }
}
```

**Step 8: Verify Client Portal**
```bash
# Port forward to client portal
kubectl port-forward -n aura-audit-ai svc/client-portal 8081:80

# Test in browser or curl
curl http://localhost:8081/
```

Expected: HTML response with Vite React app

---

### Phase 4: External Access Verification

**Step 1: Get Ingress IP**
```bash
kubectl get ingress -n aura-audit-ai -o wide
```

Look for the ADDRESS column - this is your ingress IP

**Step 2: Test API Gateway**
```bash
# Test via domain (if DNS is configured)
curl https://api.auraai.toroniandcompany.com/health

# Or test via IP
curl http://<INGRESS-IP>/health -H "Host: api.auraai.toroniandcompany.com"
```

Expected:
```json
{"status":"healthy","timestamp":"...","service":"api-gateway"}
```

**Step 3: Test CPA Portal**
```bash
# Via domain
curl https://cpa.auraa.toroniandcompany.com/

# Or via IP
curl http://<INGRESS-IP>/ -H "Host: cpa.auraa.toroniandcompany.com"
```

Expected: HTML response with React app

**Step 4: Test API Endpoint**
```bash
# Test identity service through gateway
curl https://api.auraai.toroniandcompany.com/auth/health

# Test other services
curl https://api.auraai.toroniandcompany.com/llm/health
curl https://api.auraai.toroniandcompany.com/analytics/health
curl https://api.auraai.toroniandcompany.com/fraud-detection/health
```

All should return healthy status

---

### Phase 5: End-to-End Testing

**Test 1: Login to CPA Portal**
1. Navigate to `https://cpa.auraa.toroniandcompany.com/`
2. Should see login page (no 404!)
3. Login with test credentials
4. Should redirect to dashboard (no 404!)
5. Click navigation items - should load without 404 errors

**Test 2: API Connectivity**
1. Open browser dev tools → Network tab
2. Login to CPA portal
3. Verify API calls go to `https://api.auraai.toroniandcompany.com`
4. All API responses should be 200/201/etc (not 404)

**Test 3: Gateway Routing**
```bash
# Test that gateway routes to correct services
curl https://api.auraai.toroniandcompany.com/auth/health
curl https://api.auraai.toroniandcompany.com/llm/health
curl https://api.auraai.toroniandcompany.com/fraud-detection/health
curl https://api.auraai.toroniandcompany.com/reg-ab-audit/health
```

---

## Common Issues & Solutions

### Issue: Pods stuck in "ImagePullBackOff"

**Cause**: Image not in ACR or wrong tag

**Solution**:
```bash
# Check if images exist in ACR
az acr repository list --name auraauditaiprodacr

# Check specific image tags
az acr repository show-tags --name auraauditaiprodacr --repository aura/gateway

# If image missing, manually build and push
docker build -t auraauditaiprodacr.azurecr.io/aura/gateway:latest ./services/gateway
docker push auraauditaiprodacr.azurecr.io/aura/gateway:latest
```

### Issue: Pods stuck in "CrashLoopBackOff"

**Cause**: Application error on startup

**Solution**:
```bash
# Check pod logs
kubectl logs -n aura-audit-ai deployment/gateway --tail=100

# Check events
kubectl describe pod -n aura-audit-ai <pod-name>

# Common fixes:
# - Check environment variables
# - Check database connection
# - Check Redis connection
```

### Issue: 404 errors persist after deployment

**Cause**: Ingress not updated or DNS not configured

**Solution**:
```bash
# Re-apply ingress
kubectl apply -f infra/k8s/base/ingress.yaml

# Check ingress status
kubectl describe ingress -n aura-audit-ai aura-api-ingress

# Verify DNS points to correct IP
nslookup api.auraai.toroniandcompany.com
nslookup cpa.auraa.toroniandcompany.com
```

### Issue: Gateway returns 503 for some services

**Cause**: Service not deployed or not healthy

**Solution**:
```bash
# Check which services are missing/unhealthy
kubectl port-forward -n aura-audit-ai svc/gateway 8080:80
curl http://localhost:8080/health/services | jq

# Deploy missing service
export ACR_NAME=auraauditaiprodacr
export IMAGE_TAG=latest
envsubst < infra/k8s/base/deployments-all-services.yaml | kubectl apply -f -
```

---

## Rollback Procedure (If Needed)

If deployment fails and you need to rollback:

```bash
# Rollback specific deployment
kubectl rollout undo deployment/gateway -n aura-audit-ai
kubectl rollout undo deployment/client-portal -n aura-audit-ai

# Or rollback all
for deploy in $(kubectl get deployments -n aura-audit-ai -o name); do
  kubectl rollout undo $deploy -n aura-audit-ai
done

# Verify rollback
kubectl rollout status deployment/gateway -n aura-audit-ai
```

---

## Success Criteria

✅ All 26 Docker images built and pushed to ACR
✅ All 26 Kubernetes deployments show "Available" status
✅ All pods in "Running" state with READY 1/1
✅ Gateway service responds to /health endpoint
✅ Gateway /health/services shows all 24 services healthy
✅ Client portal accessible at https://cpa.auraa.toroniandcompany.com
✅ No 404 errors after login
✅ API calls route through gateway successfully
✅ All ingress rules configured correctly
✅ SSL certificates valid (if using Let's Encrypt)

---

## Post-Deployment Tasks

Once deployment is successful:

1. **Update DNS (if not already done)**
   - Ensure `api.auraai.toroniandcompany.com` points to ingress IP
   - Ensure `cpa.auraa.toroniandcompany.com` points to ingress IP

2. **Verify SSL Certificates**
   ```bash
   kubectl get certificates -n aura-audit-ai
   ```

3. **Set up Monitoring**
   - Configure Application Insights alerts
   - Set up log analytics queries
   - Configure uptime monitoring

4. **Run Full Test Suite**
   ```bash
   # If you have smoke tests
   ./tests/smoke/run_smoke_tests.sh
   ```

5. **Document Deployment**
   - Record deployment time
   - Document any issues encountered
   - Update runbook if needed

---

## Monitoring Commands

Quick commands for ongoing monitoring:

```bash
# Watch pod status
kubectl get pods -n aura-audit-ai -w

# Watch deployments
kubectl get deployments -n aura-audit-ai -w

# View recent events
kubectl get events -n aura-audit-ai --sort-by='.lastTimestamp' | tail -20

# Check gateway logs
kubectl logs -n aura-audit-ai -l app=gateway --tail=100 -f

# Check client-portal logs
kubectl logs -n aura-audit-ai -l app=client-portal --tail=100 -f

# Get resource usage
kubectl top pods -n aura-audit-ai
kubectl top nodes
```

---

**Last Updated**: 2025-01-19
**Deployment Commit**: 0abde85
**Status**: 🟡 In Progress - Workflow #65 Running
