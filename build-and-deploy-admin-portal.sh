#!/bin/bash
set -e

echo "=========================================="
echo "Building and Deploying Admin Portal"
echo "=========================================="

# Set project ID and image name
PROJECT_ID="toroni-data-norm"
IMAGE_NAME="admin-portal"
IMAGE_TAG="latest"
FULL_IMAGE="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG}"

# Navigate to admin portal directory
cd admin-portal

echo ""
echo "Step 1: Building Docker image..."
docker build \
  --build-arg VITE_IDENTITY_API_URL=https://admin.auraai.toroniandcompany.com/api \
  -t ${FULL_IMAGE} \
  --platform linux/amd64 \
  .

echo ""
echo "Step 2: Pushing image to GCR..."
docker push ${FULL_IMAGE}

echo ""
echo "Step 3: Applying Kubernetes manifests..."
cd ..
kubectl apply -f admin-portal-deployment.yaml

echo ""
echo "Step 4: Waiting for rollout to complete..."
kubectl rollout status deployment/admin-portal -n aura-audit-ai --timeout=5m

echo ""
echo "Step 5: Checking pod status..."
kubectl get pods -n aura-audit-ai -l app=admin-portal

echo ""
echo "Step 6: Getting service and ingress status..."
kubectl get svc admin-portal -n aura-audit-ai
kubectl get ingress admin-portal -n aura-audit-ai

echo ""
echo "=========================================="
echo "Admin Portal Deployment Complete!"
echo "=========================================="
echo ""
echo "Access the admin portal at: https://admin.auraai.toroniandcompany.com"
echo ""
echo "To view logs:"
echo "  kubectl logs -n aura-audit-ai -l app=admin-portal --tail=100 -f"
echo ""
echo "To restart deployment:"
echo "  kubectl rollout restart deployment/admin-portal -n aura-audit-ai"
echo ""
