# Azure Deployment Checklist - Aura Audit AI MVP

**Version**: 1.0
**Date**: 2025-11-08
**Environment**: Production MVP
**Branch**: `claude/prepare-repo-deployment-011CUw84nAAZEAXAyTVaaZ8H`

---

## 📋 Pre-Deployment Checklist

### Prerequisites Verification

- [ ] **Azure Subscription**: Active subscription with sufficient quota
  - [ ] Subscription ID documented
  - [ ] Billing alerts configured
  - [ ] Resource quotas verified (especially for AKS, PostgreSQL)

- [ ] **Required Tools Installed**
  - [ ] Azure CLI (`az --version` ≥ 2.50.0)
  - [ ] Terraform (`terraform version` ≥ 1.7.0)
  - [ ] kubectl (`kubectl version`)
  - [ ] Helm (`helm version` ≥ 3.0)
  - [ ] Docker (`docker --version`)
  - [ ] git (`git --version`)

- [ ] **Azure CLI Authentication**
  - [ ] Logged in: `az login`
  - [ ] Correct subscription set: `az account show`
  - [ ] Service principal created for CI/CD
  - [ ] Service principal JSON saved as GitHub secret

---

## 🔧 Configuration Setup

### 1. Terraform Configuration

- [ ] **Create Backend Storage**
  ```bash
  # Create resource group for Terraform state
  az group create --name aura-tfstate-rg --location eastus

  # Create storage account (note the name)
  STORAGE_ACCOUNT_NAME="auratfstate$(date +%s)"
  az storage account create \
    --resource-group aura-tfstate-rg \
    --name $STORAGE_ACCOUNT_NAME \
    --sku Standard_LRS \
    --encryption-services blob

  # Create container
  az storage container create \
    --name tfstate \
    --account-name $STORAGE_ACCOUNT_NAME

  # Get storage account key
  az storage account keys list \
    --resource-group aura-tfstate-rg \
    --account-name $STORAGE_ACCOUNT_NAME \
    --query '[0].value' -o tsv
  ```

- [ ] **Update Configuration Files**
  - [ ] `infra/azure/backend.tf`: Update storage_account_name
  - [ ] `infra/azure/terraform.tfvars`: Review and update all REPLACE_WITH values
    - [ ] Azure AD group ID for AKS admins
    - [ ] Resource sizes appropriate for workload
    - [ ] Geographic locations correct

- [ ] **Create Azure AD Group**
  ```bash
  # Create AKS admin group
  az ad group create \
    --display-name "AKS-Aura-Admins" \
    --mail-nickname "aks-aura-admins"

  # Get group ID
  az ad group list --query "[?displayName=='AKS-Aura-Admins'].id" -o tsv

  # Add yourself to the group
  az ad group member add \
    --group "AKS-Aura-Admins" \
    --member-id $(az ad signed-in-user show --query id -o tsv)
  ```

### 2. Secrets Management

- [ ] **Generate Secrets**
  ```bash
  # JWT Secret
  echo "JWT_SECRET=$(openssl rand -hex 32)"

  # Encryption Key
  echo "ENCRYPTION_KEY=$(openssl rand -hex 32)"

  # Master Key
  echo "MASTER_KEY=$(openssl rand -hex 32)"
  ```

- [ ] **Obtain API Keys**
  - [ ] OpenAI API key: https://platform.openai.com/api-keys
  - [ ] QuickBooks credentials: https://developer.intuit.com
  - [ ] Xero credentials: https://developer.xero.com
  - [ ] NetSuite credentials (if applicable)
  - [ ] DocuSign credentials: https://developers.docusign.com
  - [ ] Stripe API keys: https://dashboard.stripe.com/apikeys
  - [ ] SendGrid API key: https://app.sendgrid.com

- [ ] **Configure GitHub Secrets**
  - [ ] AZURE_CREDENTIALS (service principal JSON)
  - [ ] OPENAI_API_KEY
  - [ ] QBO_CLIENT_ID
  - [ ] QBO_CLIENT_SECRET
  - [ ] XERO_CLIENT_ID
  - [ ] XERO_CLIENT_SECRET
  - [ ] NETSUITE_ACCOUNT_ID (if applicable)
  - [ ] STRIPE_API_KEY
  - [ ] SENDGRID_API_KEY

### 3. Domain and DNS

- [ ] **Domain Registration**
  - [ ] Domain registered: `aura-audit-ai.com`
  - [ ] Domain verified
  - [ ] DNS management access confirmed

- [ ] **SSL Certificates**
  - [ ] Option chosen: [ ] Let's Encrypt (cert-manager) or [ ] Purchased certificates
  - [ ] If purchased: Certificates obtained in PFX format
  - [ ] Certificate email for Let's Encrypt configured

---

## 🚀 Deployment Execution

### Phase 1: Infrastructure Deployment

- [ ] **Initialize Terraform**
  ```bash
  cd infra/azure
  export ARM_ACCESS_KEY="<storage-account-key>"
  terraform init
  ```

- [ ] **Review Terraform Plan**
  ```bash
  terraform plan -out=tfplan
  # Review output carefully!
  # Verify resource counts, sizes, and costs
  ```

- [ ] **Apply Infrastructure**
  ```bash
  terraform apply tfplan
  # This will take 15-30 minutes
  ```

- [ ] **Save Terraform Outputs**
  ```bash
  terraform output -json > outputs.json
  # Store outputs.json securely
  ```

- [ ] **Verify Resources Created**
  - [ ] Resource group exists
  - [ ] AKS cluster running
  - [ ] PostgreSQL server accessible
  - [ ] Redis cache operational
  - [ ] Storage account created with containers
  - [ ] Container registry created
  - [ ] Key Vault created
  - [ ] Application Gateway deployed

### Phase 2: Kubernetes Configuration

- [ ] **Configure kubectl**
  ```bash
  az aks get-credentials \
    --resource-group aura-audit-ai-prod-rg \
    --name aura-audit-ai-prod-aks

  # Verify connection
  kubectl get nodes
  # Should show 6 nodes (3 system + 3 app)
  ```

- [ ] **Install AGIC (Application Gateway Ingress Controller)**
  ```bash
  # Follow AZURE_DEPLOYMENT.md section 5
  helm repo add application-gateway-kubernetes-ingress \
    https://appgwingress.blob.core.windows.net/ingress-azure-helm-package/
  helm repo update
  # Install AGIC...
  ```

- [ ] **Install CSI Driver for Key Vault**
  ```bash
  # Follow AZURE_DEPLOYMENT.md section 6
  helm repo add csi-secrets-store-provider-azure \
    https://azure.github.io/secrets-store-csi-driver-provider-azure/charts
  # Install CSI driver...
  ```

- [ ] **Create Kubernetes Namespace**
  ```bash
  kubectl apply -f infra/k8s/base/namespace.yaml
  kubectl get namespace aura-audit-ai
  ```

### Phase 3: Application Deployment

- [ ] **Build and Push Docker Images**
  ```bash
  # Login to ACR
  ACR_NAME=$(terraform output -raw acr_login_server)
  az acr login --name ${ACR_NAME%.azurecr.io}

  # Build all images (or use GitHub Actions)
  # See AZURE_DEPLOYMENT.md section 7
  ```

- [ ] **Create Kubernetes Secrets**
  ```bash
  # Get values from Terraform outputs and Key Vault
  kubectl create secret generic aura-db-connection \
    --from-literal=connection-string="postgresql://..." \
    --namespace=aura-audit-ai

  kubectl create secret generic aura-redis-connection \
    --from-literal=connection-string="rediss://..." \
    --namespace=aura-audit-ai

  kubectl create secret generic aura-openai \
    --from-literal=api-key="sk-..." \
    --namespace=aura-audit-ai

  kubectl create secret generic aura-accounting-integrations \
    --from-literal=qbo-client-id="..." \
    --from-literal=qbo-client-secret="..." \
    --from-literal=xero-client-id="..." \
    --from-literal=xero-client-secret="..." \
    --namespace=aura-audit-ai
  ```

- [ ] **Apply ConfigMap**
  ```bash
  kubectl apply -f infra/k8s/base/configmap.yaml
  kubectl get configmap aura-config -n aura-audit-ai
  ```

- [ ] **Deploy Services**
  ```bash
  kubectl apply -f infra/k8s/base/serviceaccount.yaml
  kubectl apply -f infra/k8s/base/deployment-identity.yaml
  kubectl apply -f infra/k8s/base/deployments-all-services.yaml
  ```

- [ ] **Verify Deployments**
  ```bash
  kubectl get pods -n aura-audit-ai
  # All pods should be Running

  kubectl get services -n aura-audit-ai
  # All services should have ClusterIP
  ```

- [ ] **Run Database Migrations**
  ```bash
  # Connect to PostgreSQL
  POSTGRES_HOST=$(terraform output -raw postgres_fqdn)
  POSTGRES_PASSWORD=$(az keyvault secret show \
    --vault-name <key-vault-name> \
    --name postgres-admin-password \
    --query value -o tsv)

  # Create extensions
  PGPASSWORD=$POSTGRES_PASSWORD psql \
    -h $POSTGRES_HOST \
    -U atlasadmin \
    -d atlas \
    -c "CREATE EXTENSION IF NOT EXISTS vector;"

  # Run migrations (adjust based on your migration tool)
  # Option: Use Kubernetes Job for migrations
  ```

### Phase 4: Ingress and DNS

- [ ] **Deploy Ingress**
  ```bash
  kubectl apply -f infra/k8s/base/ingress.yaml
  kubectl get ingress -n aura-audit-ai
  ```

- [ ] **Get Application Gateway IP**
  ```bash
  APP_GW_IP=$(az network public-ip show \
    --resource-group aura-audit-ai-prod-rg \
    --name aura-audit-ai-prod-appgw-pip \
    --query ipAddress -o tsv)

  echo "Application Gateway IP: $APP_GW_IP"
  # Document this IP address
  ```

- [ ] **Configure DNS Records**
  - [ ] Create A record: `api.aura-audit-ai.com` → `$APP_GW_IP`
  - [ ] Create A record: `aura-audit-ai.com` → `$APP_GW_IP`
  - [ ] Create A record: `www.aura-audit-ai.com` → `$APP_GW_IP`
  - [ ] Create A record: `admin.aura-audit-ai.com` → `$APP_GW_IP`
  - [ ] Verify DNS propagation: `nslookup api.aura-audit-ai.com`

### Phase 5: SSL Configuration

- [ ] **Install cert-manager (if using Let's Encrypt)**
  ```bash
  helm repo add jetstack https://charts.jetstack.io
  helm repo update
  helm install cert-manager jetstack/cert-manager \
    --namespace cert-manager \
    --create-namespace \
    --set installCRDs=true
  ```

- [ ] **Create ClusterIssuer**
  ```bash
  # Update email in ClusterIssuer manifest
  # Apply ClusterIssuer for Let's Encrypt
  ```

- [ ] **Update Ingress with TLS**
  - [ ] Update ingress.yaml with TLS configuration
  - [ ] Apply updated ingress
  - [ ] Verify certificate issued: `kubectl get certificate -n aura-audit-ai`

---

## ✅ Verification & Testing

### Health Checks

- [ ] **Test Health Endpoints**
  ```bash
  curl https://api.aura-audit-ai.com/api/identity/health
  curl https://api.aura-audit-ai.com/api/llm/health
  curl https://api.aura-audit-ai.com/api/normalize/health
  curl https://api.aura-audit-ai.com/api/analytics/health
  curl https://api.aura-audit-ai.com/api/accounting-integrations/health
  ```

- [ ] **Check Pod Status**
  ```bash
  kubectl get pods -n aura-audit-ai
  # All should be Running with 1/1 or 2/2 ready
  ```

- [ ] **View Logs**
  ```bash
  kubectl logs -f deployment/identity -n aura-audit-ai
  kubectl logs -f deployment/accounting-integrations -n aura-audit-ai
  # Look for errors
  ```

### Functional Tests

- [ ] **Test Authentication**
  - [ ] User registration works
  - [ ] User login works
  - [ ] JWT tokens issued correctly

- [ ] **Test Accounting Integrations**
  - [ ] QuickBooks OAuth flow works
  - [ ] Xero OAuth flow works
  - [ ] NetSuite connection works (if applicable)

- [ ] **Test Data Normalization**
  - [ ] Trial balance upload works
  - [ ] Account mapping creates suggestions
  - [ ] Data persists correctly

- [ ] **Test Analytics**
  - [ ] Journal entry testing executes
  - [ ] Anomaly detection runs
  - [ ] Ratio analysis calculates

- [ ] **Test Reporting**
  - [ ] PDF generation works
  - [ ] WORM storage saves correctly
  - [ ] Reports downloadable

### Smoke Tests

- [ ] **Run Automated Smoke Tests**
  ```bash
  # Run smoke tests
  pytest tests/smoke/ -v
  ```

- [ ] **End-to-End Test**
  - [ ] Create organization
  - [ ] Create engagement
  - [ ] Upload trial balance
  - [ ] Map accounts
  - [ ] Run analytics
  - [ ] Generate disclosure
  - [ ] Run QC checks
  - [ ] Generate report
  - [ ] Finalize engagement

---

## 📊 Monitoring Setup

### Azure Monitor

- [ ] **Configure Application Insights**
  - [ ] Get instrumentation key from Terraform outputs
  - [ ] Verify telemetry flowing
  - [ ] Set up availability tests

- [ ] **Create Dashboards**
  - [ ] Infrastructure health dashboard
  - [ ] Application performance dashboard
  - [ ] Business metrics dashboard

- [ ] **Configure Alerts**
  - [ ] Pod crash alerts
  - [ ] High error rate alerts
  - [ ] Database connection alerts
  - [ ] Slow response time alerts
  - [ ] Cost threshold alerts

### Cost Management

- [ ] **Set Up Budgets**
  ```bash
  az consumption budget create \
    --budget-name aura-monthly-budget \
    --amount 3000 \
    --category Cost \
    --time-grain Monthly \
    --resource-group aura-audit-ai-prod-rg
  ```

- [ ] **Configure Cost Alerts**
  - [ ] 50% budget threshold
  - [ ] 80% budget threshold
  - [ ] 100% budget threshold

---

## 🔒 Security Verification

### Security Checklist

- [ ] **Network Security**
  - [ ] VNet configured with proper subnets
  - [ ] NSGs applied
  - [ ] Private endpoints enabled for PaaS services
  - [ ] WAF enabled on Application Gateway

- [ ] **Data Encryption**
  - [ ] PostgreSQL TDE enabled
  - [ ] Redis SSL/TLS enforced
  - [ ] Blob Storage SSE enabled
  - [ ] TLS 1.2+ enforced on all endpoints

- [ ] **Access Control**
  - [ ] RBAC configured for AKS
  - [ ] Azure AD integration enabled
  - [ ] Service accounts with minimal permissions
  - [ ] Key Vault access policies set

- [ ] **Secrets Management**
  - [ ] All secrets stored in Key Vault
  - [ ] No hardcoded secrets in code
  - [ ] Secrets rotation policy configured
  - [ ] Audit logging enabled

- [ ] **Compliance**
  - [ ] WORM storage configured (7-year retention)
  - [ ] Audit logs enabled
  - [ ] Backup retention policy set (35 days)
  - [ ] Geo-redundancy enabled

### Security Scans

- [ ] **Run Security Scans**
  - [ ] Azure Security Center recommendations reviewed
  - [ ] Container vulnerability scanning enabled
  - [ ] Dependency scanning (npm audit, pip-audit)
  - [ ] OWASP ZAP scan (if applicable)

---

## 📝 Documentation

- [ ] **Update Documentation**
  - [ ] Deployment guide updated with actual values
  - [ ] Architecture diagram updated
  - [ ] Runbook created for common operations
  - [ ] Incident response plan documented

- [ ] **Team Handoff**
  - [ ] Access credentials shared securely
  - [ ] On-call rotation established
  - [ ] Escalation procedures documented
  - [ ] Knowledge transfer completed

---

## 🎯 Go-Live Criteria

### Must-Have (All must be checked)

- [ ] All infrastructure resources deployed successfully
- [ ] All microservices running without errors
- [ ] Database migrations completed
- [ ] SSL certificates valid and auto-renewing
- [ ] DNS configured and propagated
- [ ] Health checks passing for all services
- [ ] Authentication and authorization working
- [ ] Critical user flows tested and working
- [ ] Smoke tests passing
- [ ] Monitoring and alerting configured
- [ ] Cost alerts configured
- [ ] Security scans passed
- [ ] Backup verification completed
- [ ] Documentation updated
- [ ] Team trained on operations

### Nice-to-Have (80%+ recommended)

- [ ] HPA configured for auto-scaling
- [ ] Network policies applied
- [ ] Pod disruption budgets configured
- [ ] Disaster recovery tested
- [ ] Load testing completed
- [ ] Performance optimizations applied

---

## 📞 Support Contacts

- **Azure Support**: Portal → Help + Support
- **OpenAI Support**: https://help.openai.com
- **Team Lead**: [Your contact info]
- **On-Call Engineer**: [On-call schedule]

---

## 🔄 Post-Deployment Tasks

- [ ] **Week 1**: Monitor metrics daily
- [ ] **Week 2**: Review cost reports
- [ ] **Week 3**: Conduct DR drill
- [ ] **Week 4**: Review and optimize

---

## ✅ Sign-Off

**Deployed by**: _______________________
**Date**: _______________________
**Verified by**: _______________________
**Production approved**: [ ] Yes [ ] No

---

**Notes**:

_Use this space to document any deployment-specific notes, issues encountered, or deviations from the standard process._

---

**Version History**:
- v1.0 (2025-11-08): Initial checklist created for MVP deployment
