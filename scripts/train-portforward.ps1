$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[0].metadata.name}'

Write-Host "=== Starting port-forward ===" -ForegroundColor Cyan
$pf = Start-Process -FilePath "kubectl" -ArgumentList "port-forward $pod 8888:8000 -n aura-audit-ai" -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 3

Write-Host "=== Calling training API ===" -ForegroundColor Green
$body = @{
    model_name = "microsoft/deberta-v3-base"
    epochs = 3
    batch_size = 4
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8888/training/start" -Method Post -Body $body -ContentType "application/json"
    $response | ConvertTo-Json
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host $_.Exception.Response.StatusCode
}

Write-Host ""
Write-Host "=== Training Status ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "http://localhost:8888/training/status" | ConvertTo-Json

Stop-Process -Id $pf.Id -Force -ErrorAction SilentlyContinue
