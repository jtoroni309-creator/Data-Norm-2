$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

Write-Host "Deleting old EDGAR scrape job..." -ForegroundColor Cyan
kubectl delete job initial-edgar-scrape -n aura-audit-ai --ignore-not-found

Write-Host ""
Write-Host "Waiting 10 seconds for cleanup..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Current pods:" -ForegroundColor Cyan
kubectl get pods -l app=azure-ml-training -n aura-audit-ai

Write-Host ""
Write-Host "Deleting old replicaset pods..." -ForegroundColor Cyan
kubectl delete rs azure-ml-training-7d4f75fb59 -n aura-audit-ai --ignore-not-found

Write-Host ""
Write-Host "Waiting 15 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "Checking new pod status:" -ForegroundColor Cyan
kubectl get pods -l app=azure-ml-training -n aura-audit-ai
