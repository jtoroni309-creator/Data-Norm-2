$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = "azure-ml-training-768c9cbf75-2hh7m"

Write-Host "=== Recent Pod Logs ===" -ForegroundColor Cyan
kubectl logs $pod -n aura-audit-ai --tail=100
