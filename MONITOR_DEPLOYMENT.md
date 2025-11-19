# Real-Time Deployment Monitoring

## Current Deployment Status

**Workflow**: Deploy to Azure #65
**Status**: 🟡 IN PROGRESS
**Commit**: 0abde85
**Trigger**: Fix deployment configuration - resolve CPA portal 404 errors
**Started**: Just now
**Expected Duration**: 20-30 minutes

---

## Live Monitoring Links

### GitHub Actions
View live progress:
```
https://github.com/jtoroni309-creator/Data-Norm-2/actions/runs
```

Click on the "Deploy to Azure #65" run to see:
- Build progress for all 26 images
- Terraform infrastructure deployment
- Kubernetes deployment steps
- Smoke test results

### Azure Portal
Monitor Azure resources:
```
https://portal.azure.com
```

Navigate to:
- Resource Group: `aura-audit-ai-prod-rg`
- AKS Cluster: `aura-audit-ai-prod-aks`
- Container Registry: `auraauditaiprodacr`

---

## Deployment Phases & Timeline

### Phase 1: Build & Push Images (15-20 min)
**Status**: 🟡 In Progress

Building in parallel:
- ⏳ 24 backend microservices
- ⏳ 1 API gateway
- ⏳ 1 CPA portal (client-portal)
- ⏳ 1 Marketing site

**What to watch for**:
- All 26 build jobs should complete successfully
- Images pushed to `auraauditaiprodacr.azurecr.io`
- No "ImagePullBackOff" errors

### Phase 2: Deploy Infrastructure (5 min)
**Status**: ⏸️ Waiting

Terraform will:
- Verify AKS cluster configuration
- Check PostgreSQL database
- Check Redis cache
- Update networking if needed

**What to watch for**:
- Terraform apply succeeds
- No resource conflicts
- Outputs generated correctly

### Phase 3: Deploy to Kubernetes (5-10 min)
**Status**: ⏸️ Waiting

Kubernetes deployment steps:
1. Create/update namespace
2. Create secrets (DB, Redis, OpenAI)
3. Apply ConfigMap
4. Deploy identity service
5. **Deploy gateway (NEW!)**
6. **Deploy all 24 microservices (includes 14 new!)**
7. Deploy client-portal (with fixes)
8. Deploy marketing site
9. Apply ingress rules

**What to watch for**:
- All deployments reach "Available" status
- Pods start successfully (no CrashLoopBackOff)
- Services are created
- Ingress configured correctly

### Phase 4: Smoke Tests (2 min)
**Status**: ⏸️ Waiting

Tests will verify:
- Health endpoints respond
- Gateway is accessible
- Services are reachable through gateway

**What to watch for**:
- All health checks pass
- No 404 errors
- No 503 errors

---

## What's Being Deployed (New/Fixed)

### NEW Deployments (Previously Missing)
1. ✨ **API Gateway** - Complete new deployment
2. ✨ reg-ab-audit service
3. ✨ audit-planning service
4. ✨ accounting-integrations service
5. ✨ data-anonymization service
6. ✨ financial-analysis service
7. ✨ fraud-detection service
8. ✨ related-party service
9. ✨ sampling service
10. ✨ security service
11. ✨ subsequent-events service
12. ✨ substantive-testing service
13. ✨ training-data service
14. ✨ eo-insurance-portal service
15. ✨ estimates-evaluation service

### FIXED Deployments
1. 🔧 **client-portal** - Port changed 3000→80, env vars fixed
2. 🔧 **Ingress** - Now routes through gateway
3. 🔧 **CI/CD** - Builds from correct directory

### Total New Resources
- **15 new Deployments**
- **15 new Services**
- **1 new HorizontalPodAutoscaler** (gateway)
- **Updated ingress routing**

---

## Quick Status Check Commands

Once deployment completes, verify with these commands:

### Check if workflow completed successfully
```bash
# View in browser
https://github.com/jtoroni309-creator/Data-Norm-2/actions
```

### Azure CLI - Check AKS
```bash
# Login
az login

# Get cluster status
az aks show \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks \
  --query "{Status: provisioningState, Version: kubernetesVersion}"
```

### Kubectl - Check Deployments
```bash
# Get credentials
az aks get-credentials \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks

# Check all pods
kubectl get pods -n aura-audit-ai

# Count running pods
kubectl get pods -n aura-audit-ai --field-selector=status.phase=Running --no-headers | wc -l
```

Expected: Should see at least 24+ pods running (depends on replicas)

### Check Gateway Specifically
```bash
# Check gateway deployment
kubectl get deployment gateway -n aura-audit-ai

# Check gateway pods
kubectl get pods -n aura-audit-ai -l app=gateway

# Check gateway logs
kubectl logs -n aura-audit-ai -l app=gateway --tail=50
```

### Check Client Portal
```bash
# Check client-portal deployment
kubectl get deployment client-portal -n aura-audit-ai

# Check if port is 80 (not 3000)
kubectl get deployment client-portal -n aura-audit-ai -o jsonpath='{.spec.template.spec.containers[0].ports[0].containerPort}'
```

Expected: `80`

### Test Endpoints
```bash
# Get ingress IP
kubectl get ingress -n aura-audit-ai -o wide

# Test gateway health
curl https://api.auraai.toroniandcompany.com/health

# Test CPA portal
curl https://cpa.auraa.toroniandcompany.com/
```

---

## Expected Timeline

```
00:00 - Workflow starts
  ↓
00:02 - All build jobs start in parallel
  ↓
15:00 - All images built and pushed ✅
  ↓
15:30 - Terraform infrastructure deployment starts
  ↓
20:00 - Terraform completes ✅
  ↓
20:30 - Kubernetes deployment starts
  ↓
22:00 - All services deployed
  ↓
25:00 - Waiting for pods to be ready
  ↓
28:00 - Smoke tests run
  ↓
30:00 - DEPLOYMENT COMPLETE ✅
```

---

## Success Indicators

When deployment is complete, you should see:

### GitHub Actions
- ✅ All build jobs green
- ✅ Deploy infrastructure job green
- ✅ Deploy to AKS job green
- ✅ Smoke tests job green
- ✅ Overall workflow status: Success

### Azure Portal
- ✅ AKS cluster: Running
- ✅ All node pools: Ready
- ✅ 26+ images in ACR
- ✅ No failing pods in workloads view

### Kubectl
```bash
kubectl get deployments -n aura-audit-ai
```
All deployments show: READY (matching desired/current)

```bash
kubectl get pods -n aura-audit-ai
```
All pods show: STATUS Running, READY 1/1

```bash
kubectl get ingress -n aura-audit-ai
```
All ingress rules show: ADDRESS (has IP), PORTS 80,443

### Application
- ✅ CPA portal loads: https://cpa.auraa.toroniandcompany.com
- ✅ No 404 errors after login
- ✅ API gateway responds: https://api.auraai.toroniandcompany.com/health
- ✅ Service health check works: https://api.auraai.toroniandcompany.com/health/services

---

## Troubleshooting During Deployment

### If Build Phase Fails

**Check build logs in GitHub Actions**
1. Click on failed job
2. Review error message
3. Common issues:
   - Dockerfile error → Fix Dockerfile and re-push
   - ACR auth error → Check Azure credentials secret
   - Out of disk space → Clean up ACR old images

**Quick fix**:
```bash
# Manually build and push failed image
az acr login --name auraauditaiprodacr
docker build -t auraauditaiprodacr.azurecr.io/aura/<service>:latest ./services/<service>
docker push auraauditaiprodacr.azurecr.io/aura/<service>:latest
```

### If Terraform Phase Fails

**Check Terraform logs**
1. Review error in GitHub Actions
2. Common issues:
   - State lock → Wait for lock to release
   - Resource quota → Increase Azure quota
   - Permission error → Check service principal permissions

**Quick fix**:
```bash
# Run Terraform locally
cd infra/azure
terraform init
terraform plan
terraform apply
```

### If Kubernetes Deployment Fails

**Check deployment logs in GitHub Actions**
1. Look for which deployment failed
2. Common issues:
   - Image not found → Re-run build
   - Secret missing → Create secrets manually
   - Resource limits → Adjust resource requests

**Quick fix**:
```bash
# Get AKS credentials
az aks get-credentials \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks

# Check what failed
kubectl get pods -n aura-audit-ai | grep -v Running

# Fix manually
export ACR_NAME=auraauditaiprodacr
export IMAGE_TAG=latest
envsubst < infra/k8s/base/deployment-gateway.yaml | kubectl apply -f -
```

---

## What to Do After Deployment Completes

### 1. Verify Everything Works
```bash
# Run verification script
kubectl get all -n aura-audit-ai

# Test CPA portal
curl https://cpa.auraa.toroniandcompany.com/
```

### 2. Test in Browser
1. Open https://cpa.auraa.toroniandcompany.com
2. Login with test account
3. Navigate through all pages
4. Verify no 404 errors

### 3. Check Logs for Errors
```bash
# Check gateway logs
kubectl logs -n aura-audit-ai deployment/gateway --tail=100

# Check client-portal logs
kubectl logs -n aura-audit-ai deployment/client-portal --tail=100
```

### 4. Monitor for 15 Minutes
Watch for:
- Pods restarting unexpectedly
- Error logs appearing
- Performance issues

### 5. Document Results
Update [DEPLOYMENT_VERIFICATION.md](DEPLOYMENT_VERIFICATION.md) with:
- Actual deployment time
- Any issues encountered
- Final verification results

---

## Emergency Rollback

If deployment causes issues:

```bash
# Quick rollback all deployments
cd infra/k8s/base

# Rollback to previous version
kubectl rollout undo deployment/gateway -n aura-audit-ai
kubectl rollout undo deployment/client-portal -n aura-audit-ai
# ... repeat for other affected deployments

# Or use previous commit
git log --oneline -5
git checkout <previous-commit-sha>
./infra/azure/deploy.sh prod false true false
```

---

## Contact Information

If issues arise during deployment:
- Check GitHub Actions logs first
- Review Azure Portal for resource issues
- Check Kubernetes events: `kubectl get events -n aura-audit-ai --sort-by='.lastTimestamp'`

---

**Current Time**: Check workflow started time
**Expected Completion**: Started time + 30 minutes
**Monitor**: https://github.com/jtoroni309-creator/Data-Norm-2/actions

**Status Legend**:
- 🟢 Complete
- 🟡 In Progress
- ⏸️ Waiting
- 🔴 Failed
