$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"
Write-Host "=== PVC Status ===" -ForegroundColor Cyan
kubectl get pvc -n aura-audit-ai
Write-Host ""
Write-Host "=== PVC Details ===" -ForegroundColor Cyan
kubectl describe pvc ml-models-pvc -n aura-audit-ai
kubectl describe pvc ml-data-pvc -n aura-audit-ai
