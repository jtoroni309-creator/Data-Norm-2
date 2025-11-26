$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"
Start-Sleep -Seconds 30
Write-Host "=== All Pods Status ===" -ForegroundColor Cyan
kubectl get pods -n aura-audit-ai | Select-String -Pattern "azure-ml|edgar-scrape"
Write-Host ""
Write-Host "=== Latest Events ===" -ForegroundColor Cyan
kubectl get events -n aura-audit-ai --sort-by='.lastTimestamp' | Select-Object -Last 10
Write-Host ""
Write-Host "=== EDGAR Job Status ===" -ForegroundColor Cyan
kubectl get jobs -n aura-audit-ai
