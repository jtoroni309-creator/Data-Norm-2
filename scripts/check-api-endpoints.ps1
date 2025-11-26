$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[0].metadata.name}'

Write-Host "=== API Documentation ===" -ForegroundColor Cyan
kubectl exec $pod -n aura-audit-ai -- curl -s http://localhost:8000/docs 2>&1 | Select-Object -First 50

Write-Host ""
Write-Host "=== OpenAPI Schema ===" -ForegroundColor Cyan
kubectl exec $pod -n aura-audit-ai -- curl -s http://localhost:8000/openapi.json 2>&1
