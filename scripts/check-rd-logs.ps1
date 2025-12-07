$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"
Write-Host "R&D Service Logs (last 50 lines):"
kubectl logs -n aura-audit-ai -l app=rd-study-automation --tail=50
