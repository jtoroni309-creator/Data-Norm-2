$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[0].metadata.name}'

Write-Host "=== Starting Training ===" -ForegroundColor Green

# Use printf to avoid escaping issues
kubectl exec $pod -n aura-audit-ai -- sh -c "printf '%s' '{\"model_name\":\"microsoft/deberta-v3-base\",\"epochs\":3,\"batch_size\":4}' | curl -s -X POST http://localhost:8000/training/start -H 'Content-Type: application/json' -d @-"

Write-Host ""
Write-Host "=== Training Status ===" -ForegroundColor Cyan
Start-Sleep -Seconds 5
kubectl exec $pod -n aura-audit-ai -- curl -s http://localhost:8000/training/status
