# Azure Deployment Quick Start

**Get Aura Audit AI running on Azure in 3 simple steps**

---

## 🎯 What This Guide Does

This quick start guide gets you from zero to a fully deployed Azure environment for Aura Audit AI.

**Time Required**: 2-3 hours (mostly Azure provisioning time)

**Cost**: ~$2,495/month (production) or ~$500/month (development)

---

## ⚡ Quick Start (3 Steps)

### Step 1: Run the Automated Setup Script (30 minutes)

This script will:
- ✅ Check prerequisites
- ✅ Verify Azure login
- ✅ Register resource providers
- ✅ Create Terraform backend storage
- ✅ Create Azure AD admin group
- ✅ Generate service principal for CI/CD
- ✅ Generate all security secrets
- ✅ Create terraform.tfvars
- ✅ Update backend.tf

```bash
# Make sure you're logged in to Azure first
az login
az account set --subscription "YOUR_SUBSCRIPTION_NAME"

# Run the automated setup script
./setup-azure-initial.sh
```

**What you'll get**:
- `terraform-backend-config.txt` - Terraform state storage details
- `azure-credentials.json` - GitHub Actions credentials
- `azure-secrets.env` - All generated security secrets
- `infra/azure/terraform.tfvars` - Terraform configuration
- `infra/azure/backend.tf` - Updated backend configuration

**⚠️ Important**: Keep these files secure! They contain sensitive credentials.

---

### Step 2: Configure Secrets (15 minutes)

#### A. Add GitHub Secrets

Go to: **GitHub Repository → Settings → Secrets and variables → Actions**

Add these **required** secrets:

| Secret Name | Get Value From |
|-------------|----------------|
| `AZURE_CREDENTIALS` | Copy entire JSON from `azure-credentials.json` |
| `TF_BACKEND_STORAGE_ACCOUNT` | From `terraform-backend-config.txt` |
| `TF_BACKEND_ACCESS_KEY` | From `terraform-backend-config.txt` |
| `OPENAI_API_KEY` | Get from https://platform.openai.com/api-keys |
| `JWT_SECRET` | From `azure-secrets.env` |
| `ENCRYPTION_KEY` | From `azure-secrets.env` |
| `MASTER_KEY` | From `azure-secrets.env` |
| `POSTGRES_PASSWORD` | From `azure-secrets.env` |

See [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) for detailed instructions.

#### B. Create .env.production

```bash
# Copy the template
cp .env.production.template .env.production

# Edit with your values
nano .env.production
```

**Update these values**:
1. Copy secrets from `azure-secrets.env`
2. Add your OpenAI API key
3. Leave Azure resource values blank for now (will update after deployment)

---

### Step 3: Deploy Infrastructure (60-90 minutes)

```bash
# Navigate to Azure infrastructure directory
cd infra/azure

# Initialize Terraform
terraform init

# Preview changes
terraform plan -out=tfplan

# Review the plan carefully - it will create ~50-60 resources

# Deploy!
terraform apply tfplan
```

**What gets deployed**:
- ✅ AKS Kubernetes cluster (6 nodes)
- ✅ PostgreSQL database with high availability
- ✅ Redis cache (Premium tier)
- ✅ Azure Blob Storage with WORM compliance
- ✅ Container Registry
- ✅ Application Gateway with WAF
- ✅ Key Vault
- ✅ Monitoring (Log Analytics + Application Insights)

**After deployment completes**:

```bash
# Get output values
terraform output

# Save these values to update .env.production:
terraform output -raw postgres_fqdn           # For POSTGRES_HOST
terraform output -raw redis_hostname          # For REDIS_HOST
terraform output -raw storage_account_name    # For S3_ACCESS_KEY
terraform output -raw acr_login_server        # For container registry
```

**Update .env.production** with these values and redeploy application.

---

## 🚀 Deploy Application to Kubernetes

After infrastructure is ready:

```bash
# Get AKS credentials
az aks get-credentials \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-aks

# Verify connection
kubectl get nodes

# Deploy application
kubectl apply -f infra/k8s/base/namespace.yaml
kubectl apply -f infra/k8s/base/configmap.yaml

# Create secrets (update with actual values first!)
kubectl create secret generic app-secrets \
  --from-env-file=.env.production \
  -n aura-audit-ai

# Deploy all services
kubectl apply -f infra/k8s/base/deployments-all-services.yaml
kubectl apply -f infra/k8s/base/services.yaml
kubectl apply -f infra/k8s/base/ingress.yaml

# Watch deployment
kubectl get pods -n aura-audit-ai --watch

# Wait for all pods to be Running (takes 5-10 minutes)
```

---

## ✅ Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n aura-audit-ai

# You should see 25+ pods all in "Running" status

# Get the external IP
kubectl get ingress -n aura-audit-ai

# Test health endpoint
GATEWAY_IP=$(kubectl get ingress -n aura-audit-ai -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')
curl http://$GATEWAY_IP/health

# Should return: {"status": "healthy"}
```

---

## 📊 What's Running

### Infrastructure:
- **6 Kubernetes Nodes**: 3 system (D4s_v3) + 3 app (D8s_v3)
- **PostgreSQL**: 128GB storage, HA enabled, 35-day backups
- **Redis**: 6GB Premium with persistence
- **Storage**: GRS replication, WORM enabled (7-year retention)
- **Container Registry**: Premium with geo-replication
- **WAF**: OWASP 3.2 protection enabled
- **Monitoring**: Full observability with Application Insights

### Application Services (25+):
- API Gateway (port 8000)
- Identity Service (8001)
- Ingestion Service (8002)
- Normalize Service (8003)
- Analytics Service (8004)
- LLM Service (8005)
- Engagement Service (8006)
- Disclosures Service (8007)
- Reporting Service (8008)
- QC Service (8009)
- ... and 15+ more specialized services

### Frontend Apps:
- Main Web App (Next.js)
- Admin Portal (React)
- Client Portal (React)

---

## 💰 Cost Breakdown

### Production Environment (~$2,495/month):
| Service | Monthly Cost |
|---------|-------------|
| AKS Nodes | $1,290 |
| PostgreSQL | $340 |
| Redis | $300 |
| Storage | $25 |
| Container Registry | $200 |
| Application Gateway | $285 |
| Other | $55 |

### Development Environment (~$500/month):
Scale down for dev:
- Use 2 nodes instead of 6
- Use Standard_D2s_v3 instead of D8s_v3
- Disable HA for PostgreSQL
- Use Standard tier Redis
- Single-region storage

---

## 🎯 Next Steps

After successful deployment:

### 1. Configure DNS & SSL (Required for production)
```bash
# Get Application Gateway public IP
az network public-ip show \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-appgw-pip \
  --query ipAddress -o tsv

# Point your domain to this IP:
# A record: api.yourdomain.com → [IP from above]
# A record: app.yourdomain.com → [IP from above]
# A record: admin.yourdomain.com → [IP from above]
```

### 2. Set Up SSL Certificates
Option A: Let's Encrypt (Free)
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Configure Let's Encrypt issuer
kubectl apply -f infra/k8s/cert-manager/letsencrypt-issuer.yaml
```

Option B: Upload Purchased Certificate
```bash
# Upload to Key Vault
az keyvault certificate import \
  --vault-name aura-audit-ai-prod-kv \
  --name ssl-cert \
  --file your-cert.pfx
```

### 3. Configure Azure AD Authentication
```bash
# Create app registration for OAuth2
az ad app create \
  --display-name "Aura Audit AI" \
  --sign-in-audience AzureADMyOrg \
  --web-redirect-uris "https://app.yourdomain.com/auth/callback"

# Get client ID and create client secret
# Update .env.production with:
# - AZURE_AD_CLIENT_ID
# - AZURE_AD_CLIENT_SECRET
# - AZURE_AD_TENANT_ID
```

### 4. Set Up Monitoring Alerts
```bash
# Create alert for pod failures
az monitor metrics alert create \
  --name "Pod Failures" \
  --resource-group aura-audit-ai-prod-rg \
  --scopes /subscriptions/<sub-id>/resourceGroups/aura-audit-ai-prod-rg \
  --condition "avg Pod Failed > 0" \
  --description "Alert when pods fail"

# Create alert for high CPU
# Create alert for database connection failures
# etc.
```

### 5. Configure Backups
```bash
# Verify PostgreSQL backups are enabled
az postgres flexible-server backup list \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-postgres

# Test restore procedure
az postgres flexible-server restore \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-postgres-restored \
  --source-server aura-audit-ai-prod-postgres \
  --restore-time "2024-01-01T00:00:00Z"
```

### 6. Run Tests
```bash
# Run E2E tests
cd frontend
npm run test:e2e

# Run API tests
cd services/api-gateway
pytest tests/

# Run load tests
k6 run tests/load/baseline.js
```

---

## 🔧 Common Operations

### View Logs
```bash
# Application logs
kubectl logs -f deployment/api-gateway -n aura-audit-ai

# All services
kubectl logs -l app=aura-audit-ai -n aura-audit-ai --tail=100

# Azure Application Insights
az monitor app-insights query \
  --app aura-audit-ai-prod-appinsights \
  --analytics-query "traces | where timestamp > ago(1h) | order by timestamp desc"
```

### Scale Services
```bash
# Scale a specific service
kubectl scale deployment api-gateway \
  --replicas=5 \
  -n aura-audit-ai

# Scale all services
kubectl scale deployment --all \
  --replicas=5 \
  -n aura-audit-ai

# Scale AKS node pool
az aks nodepool scale \
  --resource-group aura-audit-ai-prod-rg \
  --cluster-name aura-audit-ai-prod-aks \
  --name app \
  --node-count 6
```

### Update Application
```bash
# Pull latest code
git pull origin main

# Build and push new images
docker build -t auraauditai.azurecr.io/api-gateway:latest services/api-gateway
docker push auraauditai.azurecr.io/api-gateway:latest

# Rolling update
kubectl set image deployment/api-gateway \
  api-gateway=auraauditai.azurecr.io/api-gateway:latest \
  -n aura-audit-ai

# Or use GitHub Actions (automated)
git push origin main  # Triggers CI/CD pipeline
```

### Database Operations
```bash
# Run migrations
kubectl exec -it deployment/api-gateway -n aura-audit-ai -- \
  python -m alembic upgrade head

# Backup database
az postgres flexible-server backup create \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-postgres \
  --backup-name manual-backup-$(date +%Y%m%d)

# Connect to database
kubectl exec -it deployment/api-gateway -n aura-audit-ai -- \
  psql $DATABASE_URL
```

---

## 🆘 Troubleshooting

### Pods not starting
```bash
# Check pod events
kubectl describe pod <pod-name> -n aura-audit-ai

# Check logs
kubectl logs <pod-name> -n aura-audit-ai

# Common issues:
# - ImagePullBackOff: Check ACR credentials
# - CrashLoopBackOff: Check environment variables
# - Pending: Check node resources
```

### Can't access application
```bash
# Check ingress
kubectl get ingress -n aura-audit-ai
kubectl describe ingress -n aura-audit-ai

# Check Application Gateway
az network application-gateway show \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-appgw

# Test internal service
kubectl port-forward svc/api-gateway 8000:8000 -n aura-audit-ai
curl http://localhost:8000/health
```

### Database connection issues
```bash
# Check PostgreSQL status
az postgres flexible-server show \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-postgres

# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group aura-audit-ai-prod-rg \
  --name aura-audit-ai-prod-postgres

# Test connection from pod
kubectl exec -it deployment/api-gateway -n aura-audit-ai -- \
  psql "postgresql://atlasadmin@aura-audit-ai-prod-postgres:5432/atlas?sslmode=require"
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [AZURE_FIRST_TIME_SETUP.md](AZURE_FIRST_TIME_SETUP.md) | Detailed step-by-step setup guide |
| [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) | Complete GitHub secrets reference |
| [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) | Comprehensive deployment guide |
| [AZURE_DEPLOYMENT_CHECKLIST.md](AZURE_DEPLOYMENT_CHECKLIST.md) | Pre/during/post deployment checklist |
| [DEPLOYMENT_READINESS_REPORT.md](DEPLOYMENT_READINESS_REPORT.md) | Service inventory & status |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture documentation |

---

## ✅ Success Criteria

Your deployment is successful when:

- [ ] All Terraform resources created without errors
- [ ] All 25+ pods in `Running` state
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Database migrations completed successfully
- [ ] Application Insights showing telemetry
- [ ] No errors in pod logs
- [ ] Can access API Gateway externally
- [ ] Authentication working
- [ ] File upload to blob storage working
- [ ] Redis cache functioning

---

## 🎉 You're Done!

Congratulations! You now have a fully functional, production-grade Aura Audit AI platform running on Azure.

**What you've achieved**:
- ✅ Enterprise-grade infrastructure
- ✅ High availability and disaster recovery
- ✅ Security best practices (WAF, encryption, RBAC)
- ✅ Compliance-ready (WORM storage, audit trails)
- ✅ Full observability and monitoring
- ✅ Auto-scaling capabilities
- ✅ 25+ microservices deployed
- ✅ CI/CD pipeline ready

**Next**: Start onboarding users and processing audits! 🚀

---

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review detailed documentation
3. Check Azure Portal for resource status
4. Review Application Insights for errors
5. Check GitHub Actions logs for CI/CD issues
6. Review Kubernetes events: `kubectl get events -n aura-audit-ai`

**Common Resources**:
- Azure Portal: https://portal.azure.com
- Kubernetes Dashboard: `az aks browse --resource-group aura-audit-ai-prod-rg --name aura-audit-ai-prod-aks`
- Application Insights: https://portal.azure.com → aura-audit-ai-prod-appinsights
