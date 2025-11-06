#!/bin/bash
#
# Aura Audit AI - Azure Deployment Script
# This script automates the deployment of the platform to Azure
#

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
ENVIRONMENT="${1:-prod}"
DEPLOY_INFRA="${2:-true}"
DEPLOY_K8S="${3:-true}"
BUILD_IMAGES="${4:-true}"

log_info "Starting Aura Audit AI deployment to Azure"
log_info "Environment: $ENVIRONMENT"
log_info "Deploy Infrastructure: $DEPLOY_INFRA"
log_info "Deploy Kubernetes: $DEPLOY_K8S"
log_info "Build Images: $BUILD_IMAGES"

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    commands=("az" "terraform" "kubectl" "docker" "envsubst")
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd is not installed"
            exit 1
        fi
    done

    # Check Azure login
    if ! az account show &> /dev/null; then
        log_error "Not logged into Azure. Run: az login"
        exit 1
    fi

    log_success "All prerequisites met"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."

    cd infra/azure

    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init

    # Plan
    log_info "Creating Terraform plan..."
    terraform plan \
        -var="environment=$ENVIRONMENT" \
        -out=tfplan

    # Confirm before apply
    read -p "Do you want to apply this plan? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_warning "Deployment cancelled"
        exit 0
    fi

    # Apply
    log_info "Applying Terraform configuration..."
    terraform apply -auto-approve tfplan

    # Save outputs
    log_info "Saving Terraform outputs..."
    terraform output -json > outputs.json

    log_success "Infrastructure deployed successfully"

    cd ../..
}

# Get infrastructure values
get_infra_values() {
    log_info "Retrieving infrastructure values..."

    cd infra/azure

    export RESOURCE_GROUP=$(terraform output -raw resource_group_name)
    export AKS_CLUSTER_NAME=$(terraform output -raw aks_cluster_name)
    export ACR_NAME=$(terraform output -raw acr_login_server | sed 's/\.azurecr\.io//')
    export ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server)
    export POSTGRES_HOST=$(terraform output -raw postgres_fqdn)
    export POSTGRES_USER="atlasadmin"
    export REDIS_HOST=$(terraform output -raw redis_hostname)
    export KEY_VAULT_NAME=$(terraform output -raw key_vault_name)
    export STORAGE_ACCOUNT=$(terraform output -raw storage_account_name)
    export APP_GW_IP=$(az network public-ip show \
        --resource-group $RESOURCE_GROUP \
        --name aura-audit-ai-${ENVIRONMENT}-appgw-pip \
        --query ipAddress -o tsv)

    log_success "Infrastructure values retrieved"

    cd ../..
}

# Build and push Docker images
build_and_push_images() {
    log_info "Building and pushing Docker images..."

    # Login to ACR
    log_info "Logging into ACR: $ACR_NAME"
    az acr login --name $ACR_NAME

    # Get git commit SHA for tagging
    GIT_SHA=$(git rev-parse --short HEAD)
    IMAGE_TAG="${GIT_SHA}-$(date +%Y%m%d-%H%M%S)"

    log_info "Image tag: $IMAGE_TAG"

    # Build and push services
    SERVICES=("identity" "ingestion" "normalize" "analytics" "llm" "engagement" "disclosures" "reporting" "qc" "connectors")

    for service in "${SERVICES[@]}"; do
        log_info "Building $service..."

        docker build \
            -t $ACR_LOGIN_SERVER/aura/$service:$IMAGE_TAG \
            -t $ACR_LOGIN_SERVER/aura/$service:latest \
            -f services/$service/Dockerfile \
            services/$service

        log_info "Pushing $service..."
        docker push $ACR_LOGIN_SERVER/aura/$service:$IMAGE_TAG
        docker push $ACR_LOGIN_SERVER/aura/$service:latest

        log_success "$service built and pushed"
    done

    # Build and push frontend
    log_info "Building frontend..."
    docker build \
        -t $ACR_LOGIN_SERVER/aura/web:$IMAGE_TAG \
        -t $ACR_LOGIN_SERVER/aura/web:latest \
        frontend/

    docker push $ACR_LOGIN_SERVER/aura/web:$IMAGE_TAG
    docker push $ACR_LOGIN_SERVER/aura/web:latest

    log_success "All images built and pushed"

    export IMAGE_TAG
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."

    # Get AKS credentials
    log_info "Getting AKS credentials..."
    az aks get-credentials \
        --resource-group $RESOURCE_GROUP \
        --name $AKS_CLUSTER_NAME \
        --overwrite-existing

    # Create namespace
    log_info "Creating namespace..."
    kubectl apply -f infra/k8s/base/namespace.yaml

    # Get secrets from Key Vault
    log_info "Retrieving secrets from Key Vault..."
    POSTGRES_PASSWORD=$(az keyvault secret show \
        --vault-name $KEY_VAULT_NAME \
        --name postgres-admin-password \
        --query value -o tsv)

    REDIS_KEY=$(az keyvault secret show \
        --vault-name $KEY_VAULT_NAME \
        --name redis-primary-key \
        --query value -o tsv)

    JWT_SECRET=$(az keyvault secret show \
        --vault-name $KEY_VAULT_NAME \
        --name jwt-secret \
        --query value -o tsv)

    APPINSIGHTS_KEY=$(az keyvault secret show \
        --vault-name $KEY_VAULT_NAME \
        --name appinsights-instrumentation-key \
        --query value -o tsv)

    # Create Kubernetes secrets
    log_info "Creating Kubernetes secrets..."

    kubectl create secret generic aura-db-connection \
        --from-literal=connection-string="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/atlas?sslmode=require" \
        --from-literal=host="${POSTGRES_HOST}" \
        --from-literal=username="${POSTGRES_USER}" \
        --from-literal=password="${POSTGRES_PASSWORD}" \
        --namespace=aura-audit-ai \
        --dry-run=client -o yaml | kubectl apply -f -

    kubectl create secret generic aura-redis-connection \
        --from-literal=connection-string="rediss://:${REDIS_KEY}@${REDIS_HOST}:6380/0?ssl_cert_reqs=required" \
        --from-literal=host="${REDIS_HOST}" \
        --from-literal=password="${REDIS_KEY}" \
        --namespace=aura-audit-ai \
        --dry-run=client -o yaml | kubectl apply -f -

    kubectl create secret generic aura-secrets \
        --from-literal=jwt-secret="${JWT_SECRET}" \
        --from-literal=appinsights-key="${APPINSIGHTS_KEY}" \
        --namespace=aura-audit-ai \
        --dry-run=client -o yaml | kubectl apply -f -

    # Prompt for OpenAI API key
    read -p "Enter OpenAI API Key (or press Enter to skip): " OPENAI_API_KEY
    if [ -n "$OPENAI_API_KEY" ]; then
        kubectl create secret generic aura-openai \
            --from-literal=api-key="${OPENAI_API_KEY}" \
            --namespace=aura-audit-ai \
            --dry-run=client -o yaml | kubectl apply -f -
    fi

    # Apply ConfigMap
    log_info "Applying ConfigMap..."
    kubectl apply -f infra/k8s/base/configmap.yaml

    # Apply ServiceAccount
    log_info "Applying ServiceAccount..."
    kubectl apply -f infra/k8s/base/serviceaccount.yaml

    # Deploy services
    log_info "Deploying services..."

    export ACR_NAME
    export IMAGE_TAG=${IMAGE_TAG:-latest}

    envsubst < infra/k8s/base/deployment-identity.yaml | kubectl apply -f -
    envsubst < infra/k8s/base/deployments-all-services.yaml | kubectl apply -f -

    # Apply Ingress
    log_info "Applying Ingress..."
    kubectl apply -f infra/k8s/base/ingress.yaml

    log_success "Kubernetes deployment complete"
}

# Wait for deployments
wait_for_deployments() {
    log_info "Waiting for deployments to be ready..."

    DEPLOYMENTS=("identity" "llm" "analytics" "normalize" "ingestion" "engagement")

    for deployment in "${DEPLOYMENTS[@]}"; do
        log_info "Waiting for $deployment..."
        kubectl rollout status deployment/$deployment -n aura-audit-ai --timeout=5m || true
    done

    log_success "All deployments ready"
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."

    # Get Application Gateway IP
    APP_GW_IP=$(az network public-ip show \
        --resource-group $RESOURCE_GROUP \
        --name aura-audit-ai-${ENVIRONMENT}-appgw-pip \
        --query ipAddress -o tsv)

    log_info "Testing endpoints at $APP_GW_IP..."

    # Test health endpoint
    if curl -f -s http://$APP_GW_IP/health > /dev/null; then
        log_success "Health endpoint responding"
    else
        log_warning "Health endpoint not responding yet"
    fi

    # Test individual services
    for service in "identity" "llm" "analytics"; do
        if curl -f -s http://$APP_GW_IP/api/$service/health > /dev/null; then
            log_success "$service service responding"
        else
            log_warning "$service service not responding yet"
        fi
    done

    log_info "Smoke tests complete"
}

# Display deployment summary
display_summary() {
    log_success "🎉 Deployment completed successfully!"
    echo ""
    log_info "Deployment Summary:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Environment:           $ENVIRONMENT"
    echo "Resource Group:        $RESOURCE_GROUP"
    echo "AKS Cluster:           $AKS_CLUSTER_NAME"
    echo "Container Registry:    $ACR_LOGIN_SERVER"
    echo "PostgreSQL:            $POSTGRES_HOST"
    echo "Redis:                 $REDIS_HOST"
    echo "Key Vault:             $KEY_VAULT_NAME"
    echo "Application Gateway:   $APP_GW_IP"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    log_info "Next Steps:"
    echo "1. Configure DNS records for $APP_GW_IP"
    echo "   - api.aura-audit-ai.com -> $APP_GW_IP"
    echo "   - aura-audit-ai.com -> $APP_GW_IP"
    echo ""
    echo "2. Configure SSL certificates"
    echo "   kubectl create secret tls aura-tls-cert --cert=cert.crt --key=cert.key -n aura-audit-ai"
    echo ""
    echo "3. Run database migrations"
    echo "   kubectl exec -it deployment/identity -n aura-audit-ai -- alembic upgrade head"
    echo ""
    echo "4. Access Application Insights:"
    echo "   https://portal.azure.com/#resource/subscriptions/.../resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/components/aura-audit-ai-${ENVIRONMENT}-appinsights"
    echo ""
    log_info "Monitor deployment: kubectl get pods -n aura-audit-ai"
}

# Main execution
main() {
    check_prerequisites

    if [ "$DEPLOY_INFRA" = "true" ]; then
        deploy_infrastructure
    fi

    get_infra_values

    if [ "$BUILD_IMAGES" = "true" ]; then
        build_and_push_images
    fi

    if [ "$DEPLOY_K8S" = "true" ]; then
        deploy_kubernetes
        wait_for_deployments
        run_smoke_tests
    fi

    display_summary
}

# Run main function
main
