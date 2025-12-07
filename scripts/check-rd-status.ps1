$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"
Write-Host "R&D Pod Status:"
kubectl get pods -n aura-audit-ai -l app=rd-study-automation -o wide
Write-Host ""
Write-Host "R&D Pod Events:"
kubectl describe pod -n aura-audit-ai -l app=rd-study-automation | Select-String -Pattern "Events:" -Context 0,20
Write-Host ""
Write-Host "R&D Pod Logs:"
kubectl logs -n aura-audit-ai -l app=rd-study-automation --tail=30
