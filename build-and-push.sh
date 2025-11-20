#!/bin/bash
set -e

# Configuration
ACR_LOGIN_SERVER="auraauditaiprodacr.azurecr.io"
IMAGE_TAG="bb863fb-20251111-181127"

# Core services to build
SERVICES=(
  # Core Services
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
  # "reg-ab-audit"  # DISABLED - dependency conflicts
  # Audit Services
  "audit-planning"
  "sampling"
  "related-party"
  "subsequent-events"
  "substantive-testing"
  "estimates-evaluation"
  # Integration Services
  "accounting-integrations"
  # Financial Services
  "data-anonymization"
  "financial-analysis"
  "fraud-detection"
  # Support Services
  "security"
  "training-data"
  "eo-insurance-portal"
  # AI/ML Services
  "ai-feedback"
  "ai-explainability"
  "intelligent-sampling"
  "ai-chat"
  "advanced-report-generation"
  # Tax Services
  "tax-engine"
  "tax-forms"
  "tax-ocr-intake"
  "tax-review"
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
echo "Building CPA Portal (client-portal)..."
echo "=========================================="

docker build \
  -t $ACR_LOGIN_SERVER/aura/cpa-portal:$IMAGE_TAG \
  -t $ACR_LOGIN_SERVER/aura/cpa-portal:latest \
  ./client-portal

echo "Pushing cpa-portal:$IMAGE_TAG..."
docker push $ACR_LOGIN_SERVER/aura/cpa-portal:$IMAGE_TAG

echo "Pushing cpa-portal:latest..."
docker push $ACR_LOGIN_SERVER/aura/cpa-portal:latest

echo "✓ CPA Portal complete"
echo ""

echo "=========================================="
echo "All services built and pushed successfully!"
echo "=========================================="
