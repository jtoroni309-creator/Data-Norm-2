$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = "azure-ml-training-768c9cbf75-2hh7m"

Write-Host "=== Starting port-forward ===" -ForegroundColor Cyan
$pf = Start-Process -FilePath "C:\Users\jtoroni\.azure-kubectl\kubectl.exe" -ArgumentList "port-forward $pod 8890:8000 -n aura-audit-ai" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "=== Triggering Training with BERT ===" -ForegroundColor Green
$body = '{"model_name":"bert-base-uncased","epochs":3,"batch_size":4}'
$response = Invoke-RestMethod -Uri "http://localhost:8890/training/start" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 300
$response | ConvertTo-Json -Depth 10

Stop-Process -Id $pf.Id -Force -ErrorAction SilentlyContinue
