#!/bin/bash
set -e

# Configuration
ACR_LOGIN_SERVER="auraauditaiprodacr.azurecr.io"
IMAGE_TAG="bb863fb-20251111-181127"

# Core services to build
SERVICES=(
  "identity"
  "gateway"
  "llm"
  "analytics"
  "ingestion"
  "normalize"
  "engagement"
  "reporting"
  "disclosures"
  "qc"
  "connectors"
)

echo "Building and pushing Docker images to ACR..."
echo "Tag: $IMAGE_TAG"
echo "ACR: $ACR_LOGIN_SERVER"
echo ""

cd /workspaces/Data-Norm-2

for service in "${SERVICES[@]}"; do
  echo "=========================================="
  echo "Building $service..."
  echo "=========================================="

  # Build the image
  docker build \
    -t $ACR_LOGIN_SERVER/aura/$service:$IMAGE_TAG \
    -t $ACR_LOGIN_SERVER/aura/$service:latest \
    ./services/$service

  echo "Pushing $service:$IMAGE_TAG..."
  docker push $ACR_LOGIN_SERVER/aura/$service:$IMAGE_TAG

  echo "Pushing $service:latest..."
  docker push $ACR_LOGIN_SERVER/aura/$service:latest

  echo "✓ $service complete"
  echo ""
done

echo "=========================================="
echo "All services built and pushed successfully!"
echo "=========================================="
