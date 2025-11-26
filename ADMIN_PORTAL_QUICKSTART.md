# Admin Portal - Quick Start Guide

## Deploy in 3 Steps

### Step 1: Build and Push
```bash
cd admin-portal
docker build \
  --build-arg VITE_IDENTITY_API_URL=https://admin.auraai.toroniandcompany.com/api \
  -t gcr.io/toroni-data-norm/admin-portal:latest \
  --platform linux/amd64 .
docker push gcr.io/toroni-data-norm/admin-portal:latest
```

### Step 2: Deploy to Kubernetes
```bash
cd ..
kubectl apply -f admin-portal-deployment.yaml
kubectl rollout status deployment/admin-portal -n aura-audit-ai
```

### Step 3: Access
Open https://admin.auraai.toroniandcompany.com

## OR Use the Automated Script
```bash
chmod +x build-and-deploy-admin-portal.sh
./build-and-deploy-admin-portal.sh
```

## Key Features Implemented

### Authentication
- Real login with identity service
- JWT token management
- Protected routes
- User session persistence

### Firm Management
- List all CPA firms
- Create new firms
- Edit firm details
- **Service toggles** - Enable/disable services per firm
- View subscription status

### User Management
- List all users
- Create new users
- Assign users to firms
- Filter by role and status

### Service Control (NEW!)
Click "Manage Services" on any firm to toggle:
- Core: Analytics, LLM, Engagement, Reporting
- Audit: Planning, Testing, Fraud Detection, Analysis
- Compliance: Disclosures, Reg AB, Advanced Reports
- Tax: Engine, Forms, Review, OCR
- Data: Ingestion, Normalization, Connectors
- Quality: QC, Security, Anonymization
- AI/ML: Training Data

## API Configuration

The portal connects to:
- **Production**: `https://admin.auraai.toroniandcompany.com/api`
- Routes to identity service via ingress `/api` path

## Troubleshooting

### Can't login?
```bash
# Check identity service
kubectl get pods -n aura-audit-ai -l app=identity
kubectl logs -n aura-audit-ai -l app=identity --tail=50
```

### Portal not loading?
```bash
# Check admin portal pods
kubectl get pods -n aura-audit-ai -l app=admin-portal
kubectl logs -n aura-audit-ai -l app=admin-portal --tail=50
```

### Ingress issues?
```bash
# Check ingress
kubectl get ingress admin-portal -n aura-audit-ai
kubectl describe ingress admin-portal -n aura-audit-ai
```

### Restart portal
```bash
kubectl rollout restart deployment/admin-portal -n aura-audit-ai
```

## Default Access

1. Go to https://admin.auraai.toroniandcompany.com
2. Login with any admin user from identity service
3. Start managing firms and users!

## Files Changed

**New:**
- `admin-portal/src/contexts/AuthContext.tsx`
- `admin-portal/src/components/Login.tsx`
- `admin-portal/.env`
- `admin-portal-deployment.yaml`
- `build-and-deploy-admin-portal.sh`

**Updated:**
- `admin-portal/src/services/api.ts` - Real auth
- `admin-portal/src/App.tsx` - Route protection
- `admin-portal/src/components/FirmManagement.tsx` - Service toggles
- `admin-portal/src/components/UserManagement.tsx` - Backend integration
- `admin-portal/Dockerfile` - Env vars

## Done!

The admin portal is fully functional with:
- Real authentication
- CPA firm management with service controls
- User management
- Professional UI
- Production-ready deployment

See `ADMIN_PORTAL_IMPLEMENTATION.md` for detailed documentation.
