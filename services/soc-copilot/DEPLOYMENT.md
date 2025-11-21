# SOC Copilot - Deployment Plan & Runbooks

## Table of Contents

1. [Deployment Architecture](#deployment-architecture)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Database Initialization](#database-initialization)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Monitoring & Observability](#monitoring--observability)
8. [Security Configuration](#security-configuration)
9. [Backup & Recovery](#backup--recovery)
10. [Runbooks](#runbooks)

---

## Deployment Architecture

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                      INGRESS / LOAD BALANCER                 │
│                    (TLS 1.3 Termination)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                              │
          ▼                              ▼
┌─────────────────────┐        ┌─────────────────────┐
│  SOC Copilot Pod 1  │        │  SOC Copilot Pod 2  │
│  (Port 8000)        │        │  (Port 8000)        │
│                     │        │                     │
│  CPU: 2 cores       │        │  CPU: 2 cores       │
│  RAM: 4 GB          │        │  RAM: 4 GB          │
└──────────┬──────────┘        └──────────┬──────────┘
           │                              │
           └──────────────┬───────────────┘
                          │
       ┌──────────────────┴──────────────────┐
       │                                     │
       ▼                                     ▼
┌──────────────────┐               ┌──────────────────┐
│  PostgreSQL 15   │               │  Redis Cluster   │
│  + pgvector      │               │  (Session/Queue) │
│                  │               │                  │
│  CPU: 4 cores    │               │  CPU: 2 cores    │
│  RAM: 16 GB      │               │  RAM: 4 GB       │
│  Storage: 500GB  │               │                  │
└──────────────────┘               └──────────────────┘
       │
       │
       ▼
┌──────────────────┐
│  Azure Blob /    │
│  AWS S3          │
│  (Evidence       │
│   Storage)       │
└──────────────────┘
```

### High Availability

- **Application Tier:** Minimum 2 replicas with HPA (2-10 pods)
- **Database Tier:** PostgreSQL with streaming replication (primary + standby)
- **Storage Tier:** Cloud object storage with versioning and lifecycle policies

---

## Prerequisites

### Required Software

- **Kubernetes:** v1.27+ (AKS, EKS, or GKE)
- **Helm:** v3.12+
- **kubectl:** v1.27+
- **Docker:** v24+
- **Terraform:** v1.5+ (for infrastructure provisioning)
- **PostgreSQL Client:** v15+

### Required Accounts

- **Cloud Provider:** Azure or AWS account with admin access
- **Container Registry:** Azure Container Registry (ACR) or Elastic Container Registry (ECR)
- **OpenAI:** API key for AI features
- **Pinecone:** API key for RAG vector store (optional)
- **SSO Provider:** Azure AD, Okta, or Auth0 tenant

---

## Environment Setup

### 1. Create Environment Files

Create `.env` files for each environment (dev, staging, prod):

```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://soc_user:PASSWORD@postgres:5432/soc_copilot
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET=<generate-with-openssl-rand-base64-32>
SECRET_KEY=<generate-with-openssl-rand-base64-32>

# CORS
CORS_ORIGINS=https://soc-copilot.example.com,https://app.example.com

# AI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
ENABLE_AI_PLANNING=true

# Storage (Azure)
STORAGE_PROVIDER=azure
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_CONTAINER_NAME=soc-evidence

# OR Storage (AWS)
# STORAGE_PROVIDER=s3
# S3_BUCKET_NAME=soc-copilot-evidence
# S3_REGION=us-east-1
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
```

### 2. Generate Secrets

```bash
# Generate JWT secret
openssl rand -base64 32

# Generate app secret key
openssl rand -base64 32
```

---

## Database Initialization

### Step 1: Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -h <postgres-host> -U postgres

# Create database and user
CREATE DATABASE soc_copilot;
CREATE USER soc_user WITH ENCRYPTED PASSWORD 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE soc_copilot TO soc_user;

# Enable extensions
\c soc_copilot
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";
```

### Step 2: Run Migrations

```bash
# Apply schema
psql -h <postgres-host> -U soc_user -d soc_copilot -f migrations/001_init_schema.sql

# Verify tables
psql -h <postgres-host> -U soc_user -d soc_copilot -c "\dt soc_copilot.*"
```

### Step 3: Load Seed Data

```bash
# Load TSC mappings and control templates
psql -h <postgres-host> -U soc_user -d soc_copilot -f seed_data/tsc_mappings.sql
psql -h <postgres-host> -U soc_user -d soc_copilot -f seed_data/control_templates.sql
```

---

## Kubernetes Deployment

### Step 1: Create Namespace

```bash
kubectl create namespace soc-copilot
```

### Step 2: Create Secrets

```bash
# Create database secret
kubectl create secret generic soc-db-secret \
  --from-literal=DATABASE_URL='postgresql+asyncpg://soc_user:PASSWORD@postgres:5432/soc_copilot' \
  -n soc-copilot

# Create OpenAI secret
kubectl create secret generic soc-ai-secret \
  --from-literal=OPENAI_API_KEY='sk-...' \
  -n soc-copilot

# Create storage secret (Azure)
kubectl create secret generic soc-storage-secret \
  --from-literal=AZURE_STORAGE_CONNECTION_STRING='...' \
  -n soc-copilot
```

### Step 3: Deploy Application

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: soc-copilot
  namespace: soc-copilot
  labels:
    app: soc-copilot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: soc-copilot
  template:
    metadata:
      labels:
        app: soc-copilot
    spec:
      containers:
      - name: soc-copilot
        image: <your-registry>/soc-copilot:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: soc-db-secret
              key: DATABASE_URL
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: soc-ai-secret
              key: OPENAI_API_KEY
        - name: AZURE_STORAGE_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: soc-storage-secret
              key: AZURE_STORAGE_CONNECTION_STRING
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: soc-copilot
  namespace: soc-copilot
spec:
  selector:
    app: soc-copilot
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: soc-copilot-hpa
  namespace: soc-copilot
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: soc-copilot
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: soc-copilot-ingress
  namespace: soc-copilot
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - soc-copilot.example.com
    secretName: soc-copilot-tls
  rules:
  - host: soc-copilot.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: soc-copilot
            port:
              number: 80
```

Apply:

```bash
kubectl apply -f k8s/deployment.yaml
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Build and Deploy SOC Copilot

on:
  push:
    branches: [main]
    paths:
      - 'services/soc-copilot/**'
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        cd services/soc-copilot
        pip install -r requirements.txt
    - name: Run tests
      run: |
        cd services/soc-copilot
        pytest tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Login to ACR
      uses: azure/docker-login@v1
      with:
        login-server: ${{ secrets.ACR_LOGIN_SERVER }}
        username: ${{ secrets.ACR_USERNAME }}
        password: ${{ secrets.ACR_PASSWORD }}
    - name: Build and push
      run: |
        cd services/soc-copilot
        docker build -t ${{ secrets.ACR_LOGIN_SERVER }}/soc-copilot:${{ github.sha }} .
        docker push ${{ secrets.ACR_LOGIN_SERVER }}/soc-copilot:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
    - name: Get AKS credentials
      uses: azure/aks-set-context@v3
      with:
        resource-group: ${{ secrets.AZURE_RG }}
        cluster-name: ${{ secrets.AKS_CLUSTER }}
    - name: Deploy to AKS
      run: |
        kubectl set image deployment/soc-copilot \
          soc-copilot=${{ secrets.ACR_LOGIN_SERVER }}/soc-copilot:${{ github.sha }} \
          -n soc-copilot
        kubectl rollout status deployment/soc-copilot -n soc-copilot
```

---

## Monitoring & Observability

### Prometheus Metrics

Expose metrics endpoint:

```python
# Add to main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Logging

All logs are structured JSON format:

```json
{
  "timestamp": "2025-01-21T10:30:00Z",
  "level": "INFO",
  "service": "soc-copilot",
  "message": "Created SOC2 TYPE2 engagement",
  "engagement_id": "uuid",
  "user_id": "uuid"
}
```

Ship logs to ELK stack or Azure Monitor.

### Alerts

Configure alerts for:

- Pod restart count > 5 in 10 minutes
- CPU utilization > 80% for 5 minutes
- Memory utilization > 90% for 5 minutes
- Database connection pool exhaustion
- Report generation failures

---

## Security Configuration

### SSL/TLS

- **In Transit:** TLS 1.3 enforced at ingress
- **At Rest:** AES-256 encryption for storage
- **Database:** SSL connections required

### Secrets Management

Use Azure Key Vault or AWS Secrets Manager:

```bash
# Azure Key Vault
az keyvault create --name soc-copilot-kv --resource-group <rg> --location eastus

az keyvault secret set --vault-name soc-copilot-kv --name DATABASE-URL --value "..."
az keyvault secret set --vault-name soc-copilot-kv --name OPENAI-API-KEY --value "sk-..."
```

### RBAC

Apply Kubernetes RBAC:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: soc-copilot
  name: soc-copilot-role
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list"]
```

---

## Backup & Recovery

### Database Backups

**Automated Daily Backups:**

```bash
# PostgreSQL backup script
pg_dump -h <host> -U soc_user -d soc_copilot --format=custom --file=backup_$(date +%Y%m%d).dump

# Upload to blob storage
az storage blob upload --account-name <storage> --container-name backups --file backup_*.dump
```

**Retention:** 30 days

**Point-in-Time Recovery:** Enabled (30 days)

### Disaster Recovery

**RTO:** 4 hours
**RPO:** 1 hour

Recovery steps:

1. Restore database from latest backup
2. Restore evidence files from blob storage
3. Redeploy application pods
4. Verify audit trail integrity (hash chain)

---

## Runbooks

### Runbook 1: Scale Application

```bash
# Scale to 5 replicas
kubectl scale deployment/soc-copilot --replicas=5 -n soc-copilot

# Verify
kubectl get pods -n soc-copilot
```

### Runbook 2: Database Connection Issues

**Symptoms:** Pods failing health checks, "connection pool exhausted" errors

**Resolution:**

```bash
# Check database connections
psql -h <host> -U soc_user -d soc_copilot -c "SELECT count(*) FROM pg_stat_activity;"

# Terminate idle connections
psql -h <host> -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < now() - interval '10 minutes';"

# Restart pods
kubectl rollout restart deployment/soc-copilot -n soc-copilot
```

### Runbook 3: Report Generation Failure

**Symptoms:** Users cannot generate SOC reports

**Resolution:**

```bash
# Check application logs
kubectl logs -l app=soc-copilot -n soc-copilot --tail=100

# Check for storage issues
az storage blob list --account-name <storage> --container-name soc-evidence

# Verify OpenAI API connectivity
kubectl exec -it <pod-name> -n soc-copilot -- curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

### Runbook 4: Security Incident Response

**Symptoms:** Unauthorized access attempt detected

**Immediate Actions:**

1. **Isolate:** Revoke compromised JWT tokens
2. **Investigate:** Review audit trail for suspicious activity
3. **Contain:** Disable affected user accounts
4. **Notify:** Alert security team and CPA partner

```bash
# Audit trail query
psql -h <host> -U soc_user -d soc_copilot -c "
SELECT * FROM soc_copilot.audit_trail
WHERE created_at > now() - interval '24 hours'
  AND action IN ('DELETE', 'UPDATE')
ORDER BY created_at DESC;
"
```

---

## Post-Deployment Checklist

- [ ] Database migrations applied
- [ ] Seed data loaded (TSC mappings, control templates)
- [ ] Secrets configured (DB, OpenAI, storage)
- [ ] SSL/TLS certificates installed
- [ ] Ingress routing verified
- [ ] Health checks passing
- [ ] Monitoring dashboards configured
- [ ] Alerts configured
- [ ] Backup jobs scheduled
- [ ] User accounts created (CPA Partner, Manager)
- [ ] SSO integration tested
- [ ] First test engagement created successfully
- [ ] Report generation tested (SOC 1 & SOC 2)

---

**Deployment Owner:** Infrastructure Team
**Support Contact:** soc-copilot-support@firm.com
**Escalation:** CPA Partner / Security Team

**Last Updated:** 2025-01-21
