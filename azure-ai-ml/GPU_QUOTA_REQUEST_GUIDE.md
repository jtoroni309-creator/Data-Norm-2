# GPU Quota Request Guide for Azure ML Training

## Current Situation

Your Azure subscription currently has **0 GPU quota** in the westus2 region. To enable GPU-accelerated machine learning training for Aura Audit AI, you need to request a quota increase.

## Error Encountered

```
The specified subscription has a Standard NCv3 family vCPU quota of 0
and cannot accommodate for at least 1 requested managed compute nodes
which maps to 6 vCPUs.
```

## Recommended GPU Configuration

### Option 1: Standard NCv3 Family (NVIDIA Tesla V100)
**Best for**: High-performance deep learning training, LLM fine-tuning

**Request Details:**
- **VM Family**: Standard NCv3 Family
- **Region**: West US 2
- **VM Size**: Standard_NC6s_v3
- **Quota Needed**: 24 vCPUs minimum (for 4 nodes)
- **Specs per Node**:
  - 1x NVIDIA Tesla V100 GPU (16GB)
  - 6 vCPUs
  - 112 GB RAM
  - ~$1.46/hour per node

**Recommended Request**: 48 vCPUs (allows up to 8 GPU nodes)

### Option 2: Standard NVadsA10 v5 (NVIDIA A10) - AVAILABLE IN YOUR REGION!
**Best for**: Cost-effective ML training, lower power requirements

**Request Details:**
- **VM Family**: Standard NVadsA10 v5 Family
- **Region**: West US 2
- **VM Size**: standard_nv12ads_a10_v5 (CONFIRMED AVAILABLE)
- **Quota Needed**: 48 vCPUs minimum
- **Specs per Node**:
  - 1/2 NVIDIA A10 GPU (12GB)
  - 12 vCPUs
  - 110 GB RAM
  - ~$1.06/hour per node

**Recommended Request**: 96 vCPUs (allows up to 8 GPU nodes)

### Option 3: Standard NCasT4 v3 (NVIDIA Tesla T4) - AVAILABLE IN YOUR REGION!
**Best for**: Inference and lighter training workloads

**Request Details:**
- **VM Family**: Standard NCasT4 v3 Family
- **Region**: West US 2
- **VM Size**: standard_nc16as_t4_v3 (CONFIRMED AVAILABLE)
- **Quota Needed**: 64 vCPUs minimum
- **Specs per Node**:
  - 1x NVIDIA Tesla T4 GPU (16GB)
  - 16 vCPUs
  - 110 GB RAM
  - ~$0.75/hour per node

**Recommended Request**: 128 vCPUs (allows up to 8 GPU nodes)

### Option 4: Standard NC H100 v5 (NVIDIA H100) - AVAILABLE! 🚀
**Best for**: Cutting-edge LLM training, maximum performance

**Request Details:**
- **VM Family**: Standard NCadsH100 v5 Family
- **Region**: West US 2
- **VM Size**: standard_nc40ads_h100_v5 (CONFIRMED AVAILABLE)
- **Quota Needed**: 160 vCPUs minimum
- **Specs per Node**:
  - 1x NVIDIA H100 GPU (80GB)
  - 40 vCPUs
  - 320 GB RAM
  - ~$3.67/hour per node

**Recommended Request**: 320 vCPUs (allows up to 8 GPU nodes)

## How to Request Quota Increase

### Method 1: Azure Portal (Recommended)

1. **Navigate to Quotas**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Search for "Quotas" in the top search bar
   - Select "Quotas" service

2. **Select Compute**:
   - Click on "Compute" from the list
   - Filter by Region: "West US 2"

3. **Find Your VM Family**:
   - Search for the VM family you want (e.g., "Standard NCasT4 v3 Family vCPUs")
   - Click on the quota name

4. **Request Increase**:
   - Click "Request increase" or "New quota request"
   - Enter the new limit (e.g., 128 vCPUs for NCasT4 v3)
   - Provide business justification:
     ```
     Requesting GPU quota for Aura Audit AI platform to train large
     language models on financial audit data. Need to fine-tune LLMs
     on 50+ companies' SEC filings for automated audit risk assessment.
     Expected to process 700K+ financial facts requiring GPU acceleration.
     Production SaaS platform targeting $25M ARR.
     ```

5. **Submit Request**:
   - Review and submit
   - Typical approval time: 1-3 business days
   - You'll receive email notification when approved

### Method 2: Azure CLI

```bash
# Create quota request using Azure CLI
az support tickets create \
  --ticket-name "GPU-Quota-Increase-$(date +%Y%m%d)" \
  --title "GPU Quota Increase for ML Training - NCasT4 v3" \
  --description "Request increase for Standard NCasT4 v3 Family vCPUs quota in West US 2 region for machine learning workloads. Current: 0, Requested: 128 vCPUs" \
  --severity "minimal" \
  --problem-classification "/providers/Microsoft.Support/services/quota-service-guid/problemClassifications/compute-vm-cores-service-guid" \
  --contact-first-name "Jonathan" \
  --contact-last-name "Toroni" \
  --contact-method "email" \
  --contact-email "jtoroni@toroniandcompany.com" \
  --contact-country "US" \
  --contact-timezone "Pacific Standard Time" \
  --contact-language "en-us"
```

### Method 3: Support Ticket

1. Go to Azure Portal > Help + Support > New Support Request
2. **Issue type**: Service and subscription limits (quotas)
3. **Subscription**: Select your subscription
4. **Quota type**: Compute-VM (cores-vCPUs) subscription limit increases
5. **Problem type**: Select the region and VM family
6. Fill in details and submit

## Recommended Approach for Aura Audit AI

### BEST OPTION: Standard NCasT4 v3 (Tesla T4)

**Why:**
- ✅ Confirmed available in West US 2
- ✅ Cost-effective at $0.75/hour per node
- ✅ 16GB GPU memory sufficient for LLM fine-tuning
- ✅ Good balance of performance and cost
- ✅ 16 vCPUs per node allows efficient batch processing

**Request:**
- VM Family: **Standard NCasT4 v3 Family vCPUs**
- Region: **West US 2**
- New Limit: **128 vCPUs** (allows 8 GPU nodes)
- Business Justification: "ML training for audit AI platform processing 700K+ financial facts from SEC filings"

### ALTERNATIVE: Standard NVadsA10 v5 (A10) - More Economical

**Why:**
- ✅ Confirmed available in West US 2
- ✅ Most cost-effective at $1.06/hour per node
- ✅ 12GB GPU memory
- ✅ Good for moderate training workloads

**Request:**
- VM Family: **Standard NVadsA10 v5 Family vCPUs**
- Region: **West US 2**
- New Limit: **96 vCPUs** (allows 8 GPU nodes)

## Cost Estimates

### Monthly Training Costs (8 hours/day training)

**NCasT4 v3 (Tesla T4):**
- Per node: $0.75/hour × 8 hours × 30 days = $180/month
- 4 nodes: $720/month
- 8 nodes: $1,440/month

**NVadsA10 v5 (A10):**
- Per node: $1.06/hour × 8 hours × 30 days = $254/month
- 4 nodes: $1,016/month
- 8 nodes: $2,032/month

**NCadsH100 v5 (H100) - Premium:**
- Per node: $3.67/hour × 8 hours × 30 days = $881/month
- 4 nodes: $3,524/month
- 8 nodes: $7,048/month

## After Quota Approval

Once your quota is approved, run these commands:

### For Azure ML Compute Cluster:

```bash
# Create GPU compute cluster with approved VM size
az ml compute create \
  --name gpu-cluster \
  --resource-group aura-audit-ai-prod-rg \
  --workspace-name aura-audit-ai-ml-workspace \
  --type AmlCompute \
  --size Standard_NC16as_T4_v3 \
  --min-instances 0 \
  --max-instances 4 \
  --idle-time-before-scale-down 600
```

### For AKS GPU Node Pool:

```bash
# Add GPU node pool to AKS
az aks nodepool add \
  --resource-group aura-audit-ai-prod-rg \
  --cluster-name aura-audit-ai-prod-aks \
  --name gpupool \
  --node-count 2 \
  --node-vm-size Standard_NC16as_T4_v3 \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 4 \
  --labels workload=gpu inference=enabled \
  --node-taints sku=gpu:NoSchedule
```

## Summary

✅ **Immediate Action Required:**
1. Request quota increase for **Standard NCasT4 v3 Family vCPUs** in **West US 2**
2. Request amount: **128 vCPUs** (minimum 64 vCPUs)
3. Use Azure Portal quota request method (fastest approval)

✅ **Expected Timeline:**
- Quota request approval: 1-3 business days
- GPU cluster provisioning: 5-10 minutes after approval
- First training job ready: Same day as approval

✅ **Total Setup Cost:**
- Zero cost when idle (auto-scales to 0)
- $0.75/hour per active node (NCasT4 v3)
- Estimated $720-1,440/month for regular training workloads

---

**Document Created**: November 20, 2025
**Last Updated**: November 20, 2025
**Azure Subscription**: f844239d-efd6-415a-84ff-f8e9019015d6
**Region**: West US 2
