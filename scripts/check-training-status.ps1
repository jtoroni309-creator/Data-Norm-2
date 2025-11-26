$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

Write-Host "=== ML Training Pod ===" -ForegroundColor Cyan
kubectl get pods -l app=azure-ml-training -n aura-audit-ai

Write-Host ""
Write-Host "=== EDGAR Scraping Job ===" -ForegroundColor Cyan
kubectl get jobs -n aura-audit-ai

Write-Host ""
Write-Host "=== Job Pod Status ===" -ForegroundColor Cyan
kubectl get pods -n aura-audit-ai | Select-String -Pattern "edgar"

Write-Host ""
Write-Host "=== EDGAR Job Logs (last 30 lines) ===" -ForegroundColor Cyan
kubectl logs job/edgar-scrape-20251126-050422 -n aura-audit-ai --tail=30 2>&1
