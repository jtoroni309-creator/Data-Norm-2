$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"

Write-Host "Checking secrets and environment..."
Write-Host ""

$SOC_POD = kubectl get pods -n aura-audit-ai -l app=soc-copilot -o jsonpath='{.items[0].metadata.name}'
$IDENTITY_POD = kubectl get pods -n aura-audit-ai -l app=identity -o jsonpath='{.items[0].metadata.name}'

Write-Host "SOC Pod: $SOC_POD"
Write-Host "Identity Pod: $IDENTITY_POD"
Write-Host ""

Write-Host "SOC Service JWT_SECRET (first 20 chars):"
kubectl exec -n aura-audit-ai $SOC_POD -- printenv JWT_SECRET 2>&1 | ForEach-Object { $_.Substring(0, [Math]::Min(20, $_.Length)) }

Write-Host ""
Write-Host "Identity Service JWT_SECRET (first 20 chars):"
kubectl exec -n aura-audit-ai $IDENTITY_POD -- printenv JWT_SECRET 2>&1 | ForEach-Object { $_.Substring(0, [Math]::Min(20, $_.Length)) }

Write-Host ""
Write-Host "SOC Service JWT_ALGORITHM:"
kubectl exec -n aura-audit-ai $SOC_POD -- printenv JWT_ALGORITHM 2>&1

Write-Host ""
Write-Host "Identity Service JWT_ALGORITHM:"
kubectl exec -n aura-audit-ai $IDENTITY_POD -- printenv JWT_ALGORITHM 2>&1
