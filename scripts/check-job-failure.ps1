$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

Write-Host "=== Job Description ===" -ForegroundColor Cyan
kubectl describe job edgar-scrape-20251126-050422 -n aura-audit-ai

Write-Host ""
Write-Host "=== Recent Events ===" -ForegroundColor Cyan
kubectl get events -n aura-audit-ai --sort-by='.lastTimestamp' | Select-Object -Last 20
