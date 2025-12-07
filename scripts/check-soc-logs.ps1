$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"
Write-Host "SOC Service Logs (last 50 lines):"
kubectl logs -n aura-audit-ai -l app=soc-copilot --tail=50
