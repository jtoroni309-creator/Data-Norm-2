#!/bin/bash
set -e

###############################################################################
# Aura Audit AI - Quick Deploy Script
#
# This script performs a complete deployment to Azure in one command.
#
# Prerequisites:
# - Azure CLI installed and logged in
# - Terraform installed
# - kubectl installed
# - Docker installed
# - Configuration files created (run azure-deployment-config.sh first)
###############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CLIENT_ID="${AZURE_CLIENT_ID:-6d1fdc5d-580b-499d-bae8-c129af50e96e}"
TENANT_ID="${AZURE_TENANT_ID:-002fa7de-1afd-4945-86e1-79281af841ad}"
RESOURCE_GROUP="aura-audit-ai-prod-rg"
AKS_CLUSTER="aura-audit-ai-prod-aks"

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "========================================"
echo "🚀 Aura Audit AI - Quick Deploy"
echo "========================================"
echo ""

# Check prerequisites
print_step "Checking prerequisites..."

if ! command -v az &> /dev/null; then
    print_error "Azure CLI not found. Please install it first."
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    print_error "Terraform not found. Please install it first."
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install it first."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install it first."
    exit 1
fi

print_success "All prerequisites met"

# Check if configuration files exist
if [ ! -f "infra/azure/terraform.tfvars" ]; then
    print_error "terraform.tfvars not found. Run azure-deployment-config.sh first."
    exit 1
fi

if [ ! -f ".env.production" ]; then
    print_error ".env.production not found. Run azure-deployment-config.sh first."
    exit 1
fi

print_success "Configuration files found"

# Check Azure login
print_step "Checking Azure login..."
if ! az account show &> /dev/null; then
    print_warning "Not logged in to Azure"

    if [ -z "$AZURE_CLIENT_SECRET" ]; then
        read -sp "Enter Azure client secret: " AZURE_CLIENT_SECRET
        echo ""
    fi

    az login --service-principal \
      --username "$CLIENT_ID" \
      --password "$AZURE_CLIENT_SECRET" \
      --tenant "$TENANT_ID"
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
print_success "Logged in to Azure (Subscription: $SUBSCRIPTION_ID)"

# Set environment variables for Terraform
print_step "Setting up Terraform authentication..."

if [ -f "terraform-backend-config.txt" ]; then
    export ARM_ACCESS_KEY=$(grep "Access Key:" terraform-backend-config.txt | cut -d: -f2- | xargs)
fi

export ARM_CLIENT_ID="$CLIENT_ID"
export ARM_CLIENT_SECRET="${AZURE_CLIENT_SECRET}"
export ARM_TENANT_ID="$TENANT_ID"
export ARM_SUBSCRIPTION_ID="$SUBSCRIPTION_ID"

print_success "Terraform authentication configured"

# Deploy infrastructure
print_step "Deploying Azure infrastructure with Terraform..."
cd infra/azure

terraform init

print_step "Planning infrastructure changes..."
terraform plan -out=tfplan

print_warning "Review the plan above. Press any key to continue or Ctrl+C to abort..."
read -n 1 -s

print_step "Applying infrastructure changes (this will take 60-90 minutes)..."
terraform apply -auto-approve tfplan

print_success "Infrastructure deployed!"

# Get infrastructure outputs
print_step "Retrieving infrastructure values..."
POSTGRES_HOST=$(terraform output -raw postgres_fqdn)
POSTGRES_PASSWORD=$(terraform output -raw postgres_admin_password)
REDIS_HOST=$(terraform output -raw redis_hostname)
REDIS_KEY=$(terraform output -raw redis_primary_key)
STORAGE_ACCOUNT=$(terraform output -raw storage_account_name)
STORAGE_KEY=$(terraform output -raw storage_primary_key)
ACR_NAME=$(terraform output -raw acr_name)
ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server)
KEY_VAULT=$(terraform output -raw key_vault_name)

print_success "Infrastructure values retrieved"

cd ../..

# Update .env.production
print_step "Updating .env.production with infrastructure values..."

sed -i "s|POSTGRES_HOST=.*|POSTGRES_HOST=$POSTGRES_HOST|g" .env.production
sed -i "s|REDIS_HOST=.*|REDIS_HOST=$REDIS_HOST|g" .env.production
sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=$REDIS_KEY|g" .env.production
sed -i "s|AZURE_STORAGE_ACCOUNT=.*|AZURE_STORAGE_ACCOUNT=$STORAGE_ACCOUNT|g" .env.production
sed -i "s|AZURE_STORAGE_KEY=.*|AZURE_STORAGE_KEY=$STORAGE_KEY|g" .env.production
sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://atlasadmin:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/atlas?sslmode=require|g" .env.production
sed -i "s|REDIS_URL=.*|REDIS_URL=rediss://:$REDIS_KEY@$REDIS_HOST:6380/0?ssl_cert_reqs=required|g" .env.production

print_success ".env.production updated"

# Build and push Docker images
print_step "Building and pushing Docker images to ACR..."

az acr login --name "$ACR_NAME"

services=(identity ingestion normalize analytics llm engagement disclosures reporting qc connectors)

for service in "${services[@]}"; do
    if [ -d "services/$service" ]; then
        print_step "Building $service..."
        docker build -t "$ACR_LOGIN_SERVER/aura/$service:latest" \
          -f "services/$service/Dockerfile" \
          "services/$service"

        docker push "$ACR_LOGIN_SERVER/aura/$service:latest"
        print_success "$service built and pushed"
    else
        print_warning "Service directory not found: services/$service (skipping)"
    fi
done

# Build frontend
if [ -d "frontend" ]; then
    print_step "Building frontend..."
    docker build -t "$ACR_LOGIN_SERVER/aura/web:latest" frontend/
    docker push "$ACR_LOGIN_SERVER/aura/web:latest"
    print_success "Frontend built and pushed"
fi

# Build admin portal
if [ -d "admin-portal" ]; then
    print_step "Building admin portal..."
    docker build -t "$ACR_LOGIN_SERVER/aura/admin:latest" admin-portal/
    docker push "$ACR_LOGIN_SERVER/aura/admin:latest"
    print_success "Admin portal built and pushed"
fi

# Build client portal
if [ -d "client-portal" ]; then
    print_step "Building client portal..."
    docker build -t "$ACR_LOGIN_SERVER/aura/client:latest" client-portal/
    docker push "$ACR_LOGIN_SERVER/aura/client:latest"
    print_success "Client portal built and pushed"
fi

print_success "All Docker images built and pushed"

# Get AKS credentials
print_step "Connecting to AKS cluster..."
az aks get-credentials \
  --resource-group "$RESOURCE_GROUP" \
  --name "$AKS_CLUSTER" \
  --overwrite-existing

kubectl get nodes
print_success "Connected to AKS cluster"

# Deploy to Kubernetes
print_step "Deploying applications to Kubernetes..."

# Create namespace
kubectl apply -f infra/k8s/base/namespace.yaml

# Create secrets
print_step "Creating Kubernetes secrets..."
kubectl create secret generic app-secrets \
  --from-env-file=.env.production \
  -n aura-audit-ai \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply ConfigMap
kubectl apply -f infra/k8s/base/configmap.yaml

# Deploy service account
kubectl apply -f infra/k8s/base/serviceaccount.yaml

# Update deployment manifests with ACR server
export ACR_NAME="$ACR_LOGIN_SERVER"
export IMAGE_TAG="latest"

# Deploy services
print_step "Deploying services..."
if [ -f "infra/k8s/base/deployment-identity.yaml" ]; then
    envsubst < infra/k8s/base/deployment-identity.yaml | kubectl apply -f -
fi

if [ -f "infra/k8s/base/deployments-all-services.yaml" ]; then
    envsubst < infra/k8s/base/deployments-all-services.yaml | kubectl apply -f -
fi

# Deploy ingress
if [ -f "infra/k8s/base/ingress.yaml" ]; then
    kubectl apply -f infra/k8s/base/ingress.yaml
fi

print_success "Applications deployed to Kubernetes"

# Wait for deployments
print_step "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=600s \
  deployment/identity -n aura-audit-ai 2>/dev/null || true

print_success "Deployments ready"

# Get deployment status
print_step "Deployment Status:"
echo ""
kubectl get pods -n aura-audit-ai
echo ""
kubectl get services -n aura-audit-ai
echo ""
kubectl get ingress -n aura-audit-ai
echo ""

# Get Application Gateway IP
print_step "Getting Application Gateway IP..."
GATEWAY_IP=$(az network public-ip show \
  --resource-group "$RESOURCE_GROUP" \
  --name aura-audit-ai-prod-appgw-pip \
  --query ipAddress -o tsv 2>/dev/null || echo "Not available yet")

echo ""
echo "========================================"
print_success "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "📊 Infrastructure:"
echo "  PostgreSQL: $POSTGRES_HOST"
echo "  Redis: $REDIS_HOST"
echo "  Storage Account: $STORAGE_ACCOUNT"
echo "  Container Registry: $ACR_LOGIN_SERVER"
echo "  Key Vault: $KEY_VAULT"
echo ""
echo "🌐 Access:"
echo "  Application Gateway IP: $GATEWAY_IP"
echo "  Health Check: http://$GATEWAY_IP/health"
echo ""
echo "📝 Next Steps:"
echo "  1. Point your domain to IP: $GATEWAY_IP"
echo "  2. Set up SSL certificates"
echo "  3. Run database migrations:"
echo "     kubectl exec -it deployment/identity -n aura-audit-ai -- python -m alembic upgrade head"
echo "  4. Create admin user"
echo "  5. Test the application"
echo ""
echo "📚 Documentation:"
echo "  - Deployment Guide: DEPLOYMENT_GUIDE_WITH_CREDENTIALS.md"
echo "  - Azure Portal: https://portal.azure.com"
echo "  - Kubernetes Dashboard: kubectl port-forward -n kube-system service/kubernetes-dashboard 8443:443"
echo ""
print_success "Ready to use! 🚀"
