$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"
Write-Host "=== Deployment Status ===" -ForegroundColor Cyan
kubectl get deployment azure-ml-training -n aura-audit-ai
Write-Host ""
Write-Host "=== Pods Status ===" -ForegroundColor Cyan
kubectl get pods -l app=azure-ml-training -n aura-audit-ai
Write-Host ""
Write-Host "=== CronJobs ===" -ForegroundColor Cyan
kubectl get cronjobs -n aura-audit-ai
Write-Host ""
Write-Host "=== PVCs ===" -ForegroundColor Cyan
kubectl get pvc -n aura-audit-ai
