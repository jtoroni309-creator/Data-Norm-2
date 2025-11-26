$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"
Write-Host "=== Pod Description ===" -ForegroundColor Cyan
kubectl describe pod azure-ml-training-7d4f75fb59-4d5lk -n aura-audit-ai
