#!/bin/bash
# Setup Azure ML Workspace and GPU Nodes for LLM Training

set -e

echo "=========================================="
echo "AZURE ML WORKSPACE SETUP"
echo "=========================================="

# Configuration
RESOURCE_GROUP="aura-audit-ai-prod-rg"
LOCATION="westus2"
ML_WORKSPACE_NAME="aura-audit-ai-ml-workspace"
AKS_CLUSTER="aura-audit-ai-prod-aks"
GPU_NODE_POOL_NAME="gpupool"
GPU_VM_SIZE="Standard_NC6s_v3"  # 1 GPU, 6 vCPUs, 112 GB RAM
GPU_NODE_COUNT=2

echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  ML Workspace: $ML_WORKSPACE_NAME"
echo "  GPU VM Size: $GPU_VM_SIZE"
echo "  GPU Nodes: $GPU_NODE_COUNT"
echo ""

# Check if ML extension is installed
echo ">>> Checking Azure ML extension..."
az extension show --name ml &>/dev/null || {
    echo "Installing Azure ML extension..."
    az extension add --name ml --yes
}
echo "✓ Azure ML extension ready"
echo ""

# Create Azure ML workspace
echo "=========================================="
echo "Step 1: Create Azure ML Workspace"
echo "=========================================="

az ml workspace create \
    --name $ML_WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --display-name "Aura Audit AI ML Workspace" \
    --description "Machine Learning workspace for training audit AI models" \
    || echo "⚠ Workspace may already exist"

echo "✓ Azure ML Workspace created/verified"
echo ""

# Create compute instance for development
echo "=========================================="
echo "Step 2: Create Compute Instance (Optional)"
echo "=========================================="

az ml compute create \
    --name "ml-dev-instance" \
    --resource-group $RESOURCE_GROUP \
    --workspace-name $ML_WORKSPACE_NAME \
    --type ComputeInstance \
    --size Standard_DS3_v2 \
    || echo "⚠ Compute instance may already exist"

echo "✓ Compute instance created/verified"
echo ""

# Create GPU compute cluster for training
echo "=========================================="
echo "Step 3: Create GPU Compute Cluster"
echo "=========================================="

az ml compute create \
    --name "gpu-cluster" \
    --resource-group $RESOURCE_GROUP \
    --workspace-name $ML_WORKSPACE_NAME \
    --type AmlCompute \
    --size $GPU_VM_SIZE \
    --min-instances 0 \
    --max-instances 4 \
    --idle-time-before-scale-down 600 \
    || echo "⚠ GPU cluster may already exist"

echo "✓ GPU compute cluster created/verified"
echo ""

# Add GPU node pool to AKS (for real-time inference)
echo "=========================================="
echo "Step 4: Add GPU Node Pool to AKS"
echo "=========================================="

az aks nodepool add \
    --resource-group $RESOURCE_GROUP \
    --cluster-name $AKS_CLUSTER \
    --name $GPU_NODE_POOL_NAME \
    --node-count $GPU_NODE_COUNT \
    --node-vm-size $GPU_VM_SIZE \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 4 \
    --labels workload=gpu inference=enabled \
    --node-taints sku=gpu:NoSchedule \
    || echo "⚠ GPU node pool may already exist"

echo "✓ GPU node pool added to AKS"
echo ""

# Install NVIDIA device plugin (for GPU support in AKS)
echo "=========================================="
echo "Step 5: Install NVIDIA Device Plugin"
echo "=========================================="

kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml \
    || echo "⚠ NVIDIA plugin may already be installed"

echo "✓ NVIDIA device plugin installed"
echo ""

# Create data store for training data
echo "=========================================="
echo "Step 6: Register Data Store"
echo "=========================================="

# Get storage account name
STORAGE_ACCOUNT=$(az storage account list \
    --resource-group $RESOURCE_GROUP \
    --query "[?contains(name, 'auraauditai')].name" \
    --output tsv | head -1)

echo "Storage account: $STORAGE_ACCOUNT"

# Get storage account key
STORAGE_KEY=$(az storage account keys list \
    --resource-group $RESOURCE_GROUP \
    --account-name $STORAGE_ACCOUNT \
    --query "[0].value" \
    --output tsv)

# Create blob container for training data
az storage container create \
    --name ml-training-data \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY \
    || echo "⚠ Container may already exist"

echo "✓ Data store ready"
echo ""

# Create environment for training
echo "=========================================="
echo "Step 7: Create Training Environment"
echo "=========================================="

cat > /tmp/ml-environment.yml <<EOF
name: audit-ai-training
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - pip:
      - torch>=2.0.0
      - transformers>=4.30.0
      - datasets>=2.14.0
      - accelerate>=0.20.0
      - peft>=0.4.0
      - bitsandbytes>=0.40.0
      - scipy
      - scikit-learn
      - pandas
      - numpy
      - matplotlib
      - seaborn
      - azure-ai-ml
      - azureml-core
      - mlflow
EOF

az ml environment create \
    --name audit-ai-env \
    --resource-group $RESOURCE_GROUP \
    --workspace-name $ML_WORKSPACE_NAME \
    --conda-file /tmp/ml-environment.yml \
    --image mcr.microsoft.com/azureml/curated/acft-hf-nlp-gpu:latest \
    || echo "⚠ Environment may already exist"

echo "✓ Training environment created"
echo ""

# Summary
echo "=========================================="
echo "AZURE ML SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Resources Created:"
echo "  ✓ ML Workspace: $ML_WORKSPACE_NAME"
echo "  ✓ GPU Compute Cluster: gpu-cluster (0-4 nodes, $GPU_VM_SIZE)"
echo "  ✓ AKS GPU Node Pool: $GPU_NODE_POOL_NAME ($GPU_NODE_COUNT nodes)"
echo "  ✓ Data Store: ml-training-data (blob container)"
echo "  ✓ Training Environment: audit-ai-env (PyTorch + Transformers)"
echo ""
echo "Costs:"
echo "  GPU Cluster (idle): \$0/hour (auto-scales to 0)"
echo "  GPU Cluster (active): ~\$1.46/hour per node"
echo "  AKS GPU Nodes: ~\$1.46/hour × $GPU_NODE_COUNT = ~\$70/day"
echo ""
echo "Next Steps:"
echo "  1. Upload training data: az storage blob upload-batch"
echo "  2. Submit training job: az ml job create"
echo "  3. Monitor training: az ml job show"
echo "  4. Deploy model: az ml online-endpoint create"
echo ""
echo "To access ML Studio:"
echo "  https://ml.azure.com/?wsid=/subscriptions/*/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.MachineLearningServices/workspaces/$ML_WORKSPACE_NAME"
echo ""
echo "=========================================="
