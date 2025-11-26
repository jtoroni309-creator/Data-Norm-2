$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[0].metadata.name}'

Write-Host "=== Starting Model Training ===" -ForegroundColor Green

# Create JSON file in container and use it
$json = '{"model_name":"microsoft/deberta-v3-base","epochs":3,"batch_size":4}'
kubectl exec $pod -n aura-audit-ai -- sh -c "echo '$json' > /tmp/train.json && curl -s -X POST http://localhost:8000/training/start -H 'Content-Type: application/json' -d @/tmp/train.json"

Write-Host ""
Write-Host "=== Checking Training Status ===" -ForegroundColor Cyan
Start-Sleep -Seconds 5
kubectl exec $pod -n aura-audit-ai -- curl -s http://localhost:8000/training/status
