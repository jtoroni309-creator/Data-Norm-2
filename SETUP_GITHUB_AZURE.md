# Setting Up Azure Credentials for GitHub Actions

This guide will help you configure the `AZURE_CREDENTIALS` secret so GitHub Actions can automatically deploy to Azure.

---

## Quick Setup (5 Minutes)

### Step 1: Create Azure Service Principal

Open PowerShell or Command Prompt and run these commands:

```powershell
# Login to Azure (opens browser)
az login

# Get your subscription ID
az account show --query id -o tsv

# IMPORTANT: Copy the subscription ID that appears, you'll need it in the next command
```

Save the subscription ID that appears. Then run:

```powershell
# Replace <YOUR_SUBSCRIPTION_ID> with the ID from above
# This creates a service principal with the right permissions
az ad sp create-for-rbac `
  --name "github-actions-aura-audit-ai" `
  --role contributor `
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>/resourceGroups/aura-audit-ai-prod-rg `
  --sdk-auth
```

**IMPORTANT**: This command will output JSON like this:
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

**COPY THE ENTIRE JSON OUTPUT** - you'll paste this into GitHub in the next step.

---

### Step 2: Add Secret to GitHub

1. **Open GitHub Settings**:
   - Go to: https://github.com/jtoroni309-creator/Data-Norm-2/settings/secrets/actions
   - Or manually: Your Repo → Settings → Secrets and variables → Actions

2. **Create New Secret**:
   - Click **"New repository secret"** button

3. **Add Azure Credentials**:
   - Name: `AZURE_CREDENTIALS`
   - Value: Paste the entire JSON from Step 1
   - Click **"Add secret"**

---

### Step 3: Add OpenAI API Key (Required)

While on the same GitHub secrets page:

1. Click **"New repository secret"** again

2. Add OpenAI key:
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (starts with `sk-`)
   - Click **"Add secret"**

---

### Step 4: Verify Secrets Are Added

You should now see these secrets listed:
- ✅ `AZURE_CREDENTIALS`
- ✅ `OPENAI_API_KEY`

**Note**: You can't view the values after adding them (for security), but you should see the names listed.

---

### Step 5: Trigger Deployment

Now you can trigger the automated deployment:

#### Option A: Push a Dummy Commit (Easiest)
```bash
cd "C:\Users\jtoroni\Data Norm\Data-Norm-2"

# Create empty commit to trigger workflow
git commit --allow-empty -m "Trigger Azure deployment with credentials"
git push origin main
```

#### Option B: Manual Workflow Trigger
1. Go to: https://github.com/jtoroni309-creator/Data-Norm-2/actions
2. Click on **"Deploy to Azure"** workflow (left sidebar)
3. Click **"Run workflow"** button (top right)
4. Select branch: `main`
5. Select environment: `prod`
6. Click green **"Run workflow"** button

---

## What Happens Next

Once triggered, the workflow will:

### Phase 1: Build All Services (15-20 min)
- Build 24 backend microservices in parallel
- Build API gateway
- Build CPA portal
- Build marketing site
- Push all 26 images to Azure Container Registry

### Phase 2: Deploy Infrastructure (5 min)
- Terraform verification
- Check Azure resources

### Phase 3: Deploy to Kubernetes (5-10 min)
- Deploy all 26 services to AKS
- Create gateway with auto-scaling
- Deploy client portal with fixed configuration
- Apply ingress rules

### Phase 4: Smoke Tests (2 min)
- Test health endpoints
- Verify API connectivity

**Total Time**: ~30 minutes

---

## Monitoring the Deployment

### Watch Progress in Real-Time

Go to: https://github.com/jtoroni309-creator/Data-Norm-2/actions

You'll see the workflow running with all phases:

```
Deploy to Azure
├─ Build & Push Images (24 services)
│  ├─ identity ✓
│  ├─ gateway ✓
│  ├─ llm ✓
│  ├─ fraud-detection ✓
│  ├─ financial-analysis ✓
│  └─ ... (21 more) ✓
├─ Deploy Infrastructure ✓
├─ Deploy to Kubernetes ✓
└─ Smoke Tests ✓
```

### Check Azure Portal

You can also monitor in Azure:
1. Go to: https://portal.azure.com
2. Navigate to Resource Group: `aura-audit-ai-prod-rg`
3. Click on AKS cluster: `aura-audit-ai-prod-aks`
4. Click "Workloads" to see deployments

---

## Verification After Deployment

Once the workflow completes (~30 min), verify everything works:

### 1. Check Workflow Status
- ✅ Workflow should show green checkmark
- All jobs should be successful

### 2. Test CPA Portal (Most Important!)
Open in browser: https://cpa.auraa.toroniandcompany.com

- ✅ Should load without errors
- ✅ Login should work
- ✅ **No more 404 errors!**

### 3. Test API Gateway
```bash
curl https://api.auraai.toroniandcompany.com/health
```
Expected: `{"status":"healthy","timestamp":"...","service":"api-gateway"}`

### 4. Test Service Discovery
```bash
curl https://api.auraai.toroniandcompany.com/health/services
```
Expected: JSON showing all 24 services as "healthy"

---

## Troubleshooting

### "Secret not found" Error

**Problem**: Workflow can't find `AZURE_CREDENTIALS`

**Solution**:
1. Go to repo settings → Secrets → Actions
2. Verify `AZURE_CREDENTIALS` is listed
3. If not, repeat Step 2 above
4. Make sure you're adding it to the **correct repository**

### Service Principal Permission Error

**Problem**: `The client does not have authorization...`

**Solution**:
```bash
# Grant additional permissions
az role assignment create \
  --assignee <CLIENT_ID_FROM_JSON> \
  --role "AcrPush" \
  --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/aura-audit-ai-prod-rg/providers/Microsoft.ContainerRegistry/registries/auraauditaiprodacr
```

### Build Timeout

**Problem**: Build phase taking too long

**Solution**: This is normal for first deployment. The workflow has a 60-minute timeout which should be sufficient.

### Secrets Not Working After Adding

**Problem**: Added secrets but workflow still fails

**Solution**:
1. Make sure secret names match EXACTLY (case-sensitive)
   - Must be `AZURE_CREDENTIALS` (not `Azure_Credentials`)
   - Must be `OPENAI_API_KEY` (not `OPENAI_KEY`)
2. Try re-running the workflow
3. Check workflow logs for specific error messages

---

## Alternative: Manual Deployment

If you prefer not to set up GitHub Actions, you can deploy manually:

See: [AZURE_DEPLOYMENT_CHECK.md](AZURE_DEPLOYMENT_CHECK.md)

Run these commands locally:
```bash
# Build all images
./build-and-push.sh

# Deploy to Kubernetes
./infra/azure/deploy.sh prod false true false
```

---

## Security Notes

### Service Principal Permissions

The service principal created has:
- **Role**: Contributor
- **Scope**: Only the `aura-audit-ai-prod-rg` resource group
- **Access**: Can manage resources in that resource group only

This follows the principle of least privilege.

### Secret Storage

- Secrets in GitHub are encrypted at rest
- Never logged or displayed in workflow outputs
- Only accessible to workflows in this repository
- Can be rotated/deleted at any time

### Rotating Credentials

To rotate the service principal:

```bash
# Delete old service principal
az ad sp delete --id <CLIENT_ID>

# Create new one (repeat Step 1)
az ad sp create-for-rbac ...

# Update GitHub secret with new JSON
```

---

## What Gets Deployed

Once secrets are configured and deployment runs, you'll have:

### Azure Container Registry
- 26 Docker images (all services)
- Tagged with commit SHA and `latest`

### Azure Kubernetes Service
- 26 Kubernetes Deployments
- 26 Kubernetes Services
- API Gateway with HPA (auto-scaling 3-10 pods)
- Client Portal with HPA (auto-scaling 2-5 pods)
- Ingress rules for routing

### Services Deployed
1. **Core (10)**: identity, ingestion, normalize, analytics, llm, engagement, disclosures, reporting, qc, connectors
2. **Audit (6)**: reg-ab-audit, audit-planning, sampling, subsequent-events, substantive-testing, estimates-evaluation
3. **Financial (3)**: financial-analysis, fraud-detection, related-party
4. **Support (5)**: accounting-integrations, data-anonymization, security, training-data, eo-insurance-portal
5. **Gateway (1)**: API gateway
6. **Frontend (1)**: CPA portal

**Total: 26 services**

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ AZURE CREDENTIALS SETUP - QUICK REFERENCE               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 1. Create Service Principal:                            │
│    az ad sp create-for-rbac \                           │
│      --name "github-actions-aura-audit-ai" \            │
│      --role contributor \                                │
│      --scopes /subscriptions/<SUB_ID>/resourceGroups/... │
│      --sdk-auth                                          │
│                                                          │
│ 2. Copy entire JSON output                              │
│                                                          │
│ 3. Add to GitHub:                                       │
│    Repo → Settings → Secrets → Actions                  │
│    New secret: AZURE_CREDENTIALS                        │
│    Paste JSON → Add secret                              │
│                                                          │
│ 4. Add OPENAI_API_KEY secret                           │
│                                                          │
│ 5. Trigger deployment:                                  │
│    git commit --allow-empty -m "Deploy" && git push     │
│                                                          │
│ 6. Monitor:                                             │
│    https://github.com/.../actions                       │
│                                                          │
│ 7. Verify (~30 min later):                             │
│    https://cpa.auraa.toroniandcompany.com              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. ✅ Complete Steps 1-4 above (add secrets)
2. ✅ Trigger deployment (Step 5)
3. ⏳ Wait ~30 minutes
4. ✅ Test CPA portal
5. ✅ Verify no 404 errors
6. 🎉 Done!

---

**Need Help?**
- Check workflow logs: https://github.com/jtoroni309-creator/Data-Norm-2/actions
- Review deployment docs: [DEPLOYMENT_FIXES.md](DEPLOYMENT_FIXES.md)
- Manual deployment guide: [AZURE_DEPLOYMENT_CHECK.md](AZURE_DEPLOYMENT_CHECK.md)
