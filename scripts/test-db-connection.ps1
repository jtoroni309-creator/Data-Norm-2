$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[0].metadata.name}'

Write-Host "=== Testing database connectivity ===" -ForegroundColor Cyan

# Test basic network connectivity to PostgreSQL
kubectl exec $pod -n aura-audit-ai -- sh -c "timeout 5 nc -zv aura-audit-ai-prod-psql.postgres.database.azure.com 5432 2>&1 || echo 'Connection failed'"

Write-Host ""
Write-Host "=== Checking if ingestion service has DB ===" -ForegroundColor Cyan
kubectl exec -n aura-audit-ai deploy/ingestion -- env | Select-String -Pattern "DATABASE|POSTGRES"
