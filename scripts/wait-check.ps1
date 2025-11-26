$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"
Start-Sleep -Seconds 15
Write-Host "=== Pod Status After Wait ===" -ForegroundColor Cyan
kubectl get pods -l app=azure-ml-training -n aura-audit-ai
Write-Host ""
Write-Host "=== Latest Events ===" -ForegroundColor Cyan
kubectl get events -n aura-audit-ai --sort-by='.lastTimestamp' | Select-Object -Last 15
