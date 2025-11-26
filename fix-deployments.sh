#!/bin/bash
# Fix deployments by adding missing environment variables

set -e

NAMESPACE="aura-audit-ai"
SERVICES=(
  "advanced-report-generation"
  "financial-analysis"
  "fraud-detection"
  "reg-ab-audit"
  "tax-engine"
  "tax-forms"
  "tax-ocr-intake"
  "tax-review"
)

echo "Patching failing deployments to add missing environment variables..."

for SERVICE in "${SERVICES[@]}"; do
  echo "Patching $SERVICE..."

  kubectl patch deployment $SERVICE -n $NAMESPACE --type='strategic' --patch '
spec:
  template:
    spec:
      serviceAccountName: aura-workload-identity
      containers:
      - name: '"$SERVICE"'
        envFrom:
        - configMapRef:
            name: aura-config
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
        - name: STORAGE_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: aura-secrets
              key: storage-connection-string
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: aura-secrets
              key: jwt-secret
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: aura-secrets
              key: jwt-secret
'

  echo "✓ Patched $SERVICE"
done

echo ""
echo "All deployments patched successfully!"
echo ""
echo "Restarting deployments..."
for SERVICE in "${SERVICES[@]}"; do
  kubectl rollout restart deployment/$SERVICE -n $NAMESPACE
done

echo "Waiting for deployments to stabilize..."
sleep 10

echo ""
echo "Checking deployment status..."
kubectl get deployments -n $NAMESPACE | grep -E '(NAME|advanced-report|financial-analysis|fraud-detection|reg-ab-audit|tax-engine|tax-forms|tax-ocr-intake|tax-review)'
