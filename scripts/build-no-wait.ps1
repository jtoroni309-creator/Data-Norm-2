cd "c:\Users\jtoroni\Data Norm\Data-Norm-2"
Write-Host "Submitting build to ACR (no-wait)..." -ForegroundColor Cyan

# Submit build without waiting for logs
$result = az acr build --registry auraauditaiprodacr --image "aura/azure-ml-training:latest" --file "azure-ai-ml/Dockerfile" "azure-ai-ml/" --no-wait 2>&1

Write-Host "Build submitted. Waiting 120 seconds for build to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 120

Write-Host "Checking build status..." -ForegroundColor Cyan
az acr task list-runs --registry auraauditaiprodacr --top 5 --output table

Write-Host ""
Write-Host "Checking if image exists now..." -ForegroundColor Cyan
az acr repository show-tags --name auraauditaiprodacr --repository "aura/azure-ml-training" --output table 2>&1
