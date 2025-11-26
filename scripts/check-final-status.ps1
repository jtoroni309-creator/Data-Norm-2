$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

Write-Host "Waiting 60 seconds for image pull..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

Write-Host "=== Pod Status ===" -ForegroundColor Cyan
kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o wide

Write-Host ""
Write-Host "=== Deployment ===" -ForegroundColor Cyan
kubectl get deployment azure-ml-training -n aura-audit-ai

Write-Host ""
Write-Host "=== Service ===" -ForegroundColor Cyan
kubectl get svc azure-ml-training -n aura-audit-ai

Write-Host ""
Write-Host "=== Latest Events ===" -ForegroundColor Cyan
kubectl get events -n aura-audit-ai --field-selector involvedObject.name=azure-ml-training-6dd9ddf7f-zv7xt --sort-by='.lastTimestamp'
