$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"

Write-Host "Updating SOC deployment to use latest image..."
kubectl set image deployment/soc-copilot soc-copilot=auraauditaiprodacr.azurecr.io/soc-copilot:latest -n aura-audit-ai
Write-Host ""

Write-Host "Restarting SOC deployment..."
kubectl rollout restart deployment/soc-copilot -n aura-audit-ai
Write-Host ""

Write-Host "Waiting for rollout..."
kubectl rollout status deployment/soc-copilot -n aura-audit-ai --timeout=120s
Write-Host ""

Write-Host "SOC Pod Status:"
kubectl get pods -n aura-audit-ai -l app=soc-copilot -o wide
