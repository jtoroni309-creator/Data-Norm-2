# Build and push to ACR
$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "Building Docker image in ACR..." -ForegroundColor Cyan
Write-Host "This may take several minutes..." -ForegroundColor Yellow

# Use --no-logs to avoid console output issues
$result = az acr build --registry auraauditaiprodacr --image "aura/azure-ml-training:latest" --file "azure-ai-ml/Dockerfile" "azure-ai-ml/" --no-logs 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build submitted successfully!" -ForegroundColor Green

    # Wait a bit then check the build status
    Write-Host "Checking build status..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    az acr task list-runs --registry auraauditaiprodacr --top 1 --output table
} else {
    Write-Host "Build submission failed!" -ForegroundColor Red
    Write-Host $result
}
