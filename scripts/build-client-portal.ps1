$ErrorActionPreference = 'SilentlyContinue'
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$logFile = "$env:TEMP\acr-build.log"

Write-Host "Starting ACR build..."
az acr build --registry auraauditaiprodacr --image aura/client-portal:v3 --file client-portal/Dockerfile client-portal/ 2>&1 | Out-File -FilePath $logFile -Encoding utf8

Write-Host "Build completed. Checking result..."
if (Test-Path $logFile) {
    Get-Content $logFile | Select-Object -Last 20
}

# Check if image was pushed
Write-Host "`nChecking if image was pushed..."
az acr repository show-tags --name auraauditaiprodacr --repository aura/client-portal --orderby time_desc --top 5 --output table
