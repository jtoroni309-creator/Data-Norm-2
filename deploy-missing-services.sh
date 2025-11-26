#!/bin/bash
# Deploy all 18 missing services to AKS

set -e

NAMESPACE="aura-audit-ai"
ACR="auraauditaiprodacr.azurecr.io"

# List of all missing services
SERVICES=(
  "accounting-integrations"
  "advanced-report-generation"
  "audit-planning"
  "data-anonymization"
  "estimates-evaluation"
  "financial-analysis"
  "fraud-detection"
  "reg-ab-audit"
  "related-party"
  "sampling"
  "security"
  "subsequent-events"
  "substantive-testing"
  "tax-engine"
  "tax-forms"
  "tax-ocr-intake"
  "tax-review"
  "training-data"
)

echo "Deploying 18 missing services to AKS..."

for SERVICE in "${SERVICES[@]}"; do
  echo "Creating deployment for $SERVICE..."

  # Create deployment YAML
  cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE
  namespace: $NAMESPACE
  labels:
    app: $SERVICE
    component: api
spec:
  replicas: 1
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: $SERVICE
  template:
    metadata:
      labels:
        app: $SERVICE
        component: api
    spec:
      containers:
      - name: $SERVICE
        image: $ACR/aura/$SERVICE:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: aura-db-connection
              key: connection-string
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: aura-redis-connection
              key: connection-string
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
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
          initialDelaySeconds: 15
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: $SERVICE
  namespace: $NAMESPACE
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: $SERVICE
EOF

  echo "✓ Deployed $SERVICE"
done

echo ""
echo "All 18 services deployed successfully!"
echo ""
echo "Checking deployment status..."
kubectl get deployments -n $NAMESPACE
