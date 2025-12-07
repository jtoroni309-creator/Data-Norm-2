$env:Path = $env:Path + ";C:\Users\jtoroni\.azure-kubectl"

# Check R&D service logs for errors
Write-Host "R&D Service recent errors:"
kubectl logs -n aura-audit-ai -l app=rd-study-automation --tail=30 | Select-String -Pattern "error|Error|ERROR|500|exception|Exception"

Write-Host ""
Write-Host "SOC service recent logs:"
kubectl logs -n aura-audit-ai -l app=soc-copilot --tail=30 | Select-String -Pattern "error|Error|ERROR|401|credential|auth"
