$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

Write-Host "=== Waiting 60s for pod to be ready ===" -ForegroundColor Yellow
Start-Sleep -Seconds 60

Write-Host "=== Pod Status ===" -ForegroundColor Cyan
kubectl get pods -l app=azure-ml-training -n aura-audit-ai

$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' | Select-Object -First 1

Write-Host ""
Write-Host "=== Checking DATABASE_URL ===" -ForegroundColor Cyan
kubectl exec $pod -n aura-audit-ai -- sh -c 'echo "DATABASE_URL is set: $DATABASE_URL"' 2>&1 | Select-Object -First 1

Write-Host ""
Write-Host "=== Starting Training Again ===" -ForegroundColor Green
$pf = Start-Process -FilePath "kubectl" -ArgumentList "port-forward $pod 8888:8000 -n aura-audit-ai" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 3

$body = @{
    model_name = "microsoft/deberta-v3-base"
    epochs = 3
    batch_size = 4
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8888/training/start" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
    Write-Host "Training Response:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Stop-Process -Id $pf.Id -Force -ErrorAction SilentlyContinue
