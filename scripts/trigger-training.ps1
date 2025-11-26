$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[0].metadata.name}'

Write-Host "=== Copying JSON to pod ===" -ForegroundColor Cyan
kubectl cp "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\train.json" "aura-audit-ai/${pod}:/tmp/train.json"

Write-Host ""
Write-Host "=== Starting Training ===" -ForegroundColor Green
kubectl exec $pod -n aura-audit-ai -- sh -c 'curl -s -X POST http://localhost:8000/training/start -H "Content-Type: application/json" -d @/tmp/train.json'

Write-Host ""
Write-Host "=== Training Status ===" -ForegroundColor Cyan
Start-Sleep -Seconds 3
kubectl exec $pod -n aura-audit-ai -- curl -s http://localhost:8000/training/status
