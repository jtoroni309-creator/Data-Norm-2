$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"
Write-Host "Updating R&D deployment to use latest image..."
kubectl set image deployment/rd-study-automation rd-study-automation=auraauditaiprodacr.azurecr.io/rd-study-automation:latest -n aura-audit-ai
Write-Host ""
Write-Host "Waiting for rollout..."
kubectl rollout status deployment/rd-study-automation -n aura-audit-ai --timeout=120s
Write-Host ""
Write-Host "New Pod Details:"
kubectl get pods -n aura-audit-ai -l app=rd-study-automation -o jsonpath='{.items[0].spec.containers[0].image}'
