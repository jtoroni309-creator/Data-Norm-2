$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[0].metadata.name}'

Write-Host "=== Pod Environment Variables ===" -ForegroundColor Cyan
kubectl exec $pod -n aura-audit-ai -- env | Select-String -Pattern "POSTGRES|DATABASE|DB_"

Write-Host ""
Write-Host "=== Checking database connectivity ===" -ForegroundColor Cyan
kubectl exec $pod -n aura-audit-ai -- sh -c "python -c 'import os; print(os.environ.get(\"DATABASE_URL\", \"NOT SET\"))'"

Write-Host ""
Write-Host "=== Pod Logs (last 20 lines) ===" -ForegroundColor Cyan
kubectl logs $pod -n aura-audit-ai --tail=20
