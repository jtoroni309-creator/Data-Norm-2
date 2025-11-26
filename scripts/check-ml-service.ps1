$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

Write-Host "=== ML Training Pod ===" -ForegroundColor Cyan
kubectl get pods -l app=azure-ml-training -n aura-audit-ai

Write-Host ""
Write-Host "=== Pod Logs (last 50 lines) ===" -ForegroundColor Cyan
$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[0].metadata.name}'
kubectl logs $pod -n aura-audit-ai --tail=50

Write-Host ""
Write-Host "=== Checking health endpoint ===" -ForegroundColor Cyan
kubectl exec $pod -n aura-audit-ai -- curl -s http://localhost:8000/health 2>&1
