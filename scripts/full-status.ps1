$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"
Write-Host "=== All Pods ===" -ForegroundColor Cyan
kubectl get pods -n aura-audit-ai
Write-Host ""
Write-Host "=== All Jobs ===" -ForegroundColor Cyan
kubectl get jobs -n aura-audit-ai
Write-Host ""
Write-Host "=== Pod Events (azure-ml-training) ===" -ForegroundColor Cyan
kubectl describe pods -l app=azure-ml-training -n aura-audit-ai | Select-String -Pattern "Events:" -Context 0,20
