$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

Write-Host "=== Restarting ML Training Deployment ===" -ForegroundColor Green
kubectl rollout restart deployment/azure-ml-training -n aura-audit-ai

Write-Host ""
Write-Host "=== Waiting for rollout ===" -ForegroundColor Cyan
kubectl rollout status deployment/azure-ml-training -n aura-audit-ai --timeout=180s

Write-Host ""
Write-Host "=== Pod Status ===" -ForegroundColor Cyan
kubectl get pods -l app=azure-ml-training -n aura-audit-ai
