$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

Write-Host "=== Getting pod name ===" -ForegroundColor Cyan
$pod = "azure-ml-training-768c9cbf75-2hh7m"

Write-Host "Pod: $pod"

Write-Host ""
Write-Host "=== Verifying DATABASE_URL ===" -ForegroundColor Cyan
kubectl exec $pod -n aura-audit-ai -- printenv DATABASE_URL

Write-Host ""
Write-Host "=== Starting port-forward ===" -ForegroundColor Cyan
$pf = Start-Process -FilePath "C:\Users\jtoroni\.azure-kubectl\kubectl.exe" -ArgumentList "port-forward $pod 8889:8000 -n aura-audit-ai" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "=== Triggering Training ===" -ForegroundColor Green
$body = '{"model_name":"microsoft/deberta-v3-base","epochs":3,"batch_size":4}'
Invoke-RestMethod -Uri "http://localhost:8889/training/start" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 120

Write-Host ""
Write-Host "=== Training Status ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "http://localhost:8889/training/status"

Stop-Process -Id $pf.Id -Force -ErrorAction SilentlyContinue
