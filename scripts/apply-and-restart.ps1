$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

Write-Host "=== Applying updated deployment ===" -ForegroundColor Cyan
kubectl apply -f "c:\Users\jtoroni\Data Norm\Data-Norm-2\infra\k8s\base\11-azure-ml-training.yaml"

Write-Host ""
Write-Host "=== Restarting deployment ===" -ForegroundColor Cyan
kubectl rollout restart deployment/azure-ml-training -n aura-audit-ai

Write-Host ""
Write-Host "=== Waiting for rollout ===" -ForegroundColor Yellow
kubectl rollout status deployment/azure-ml-training -n aura-audit-ai --timeout=120s

Write-Host ""
Write-Host "=== New Pod Status ===" -ForegroundColor Cyan
kubectl get pods -l app=azure-ml-training -n aura-audit-ai
