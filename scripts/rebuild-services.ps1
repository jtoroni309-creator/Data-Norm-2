# Rebuild and Redeploy All Affected Services
# This script rebuilds Docker images and redeploys to AKS

$ErrorActionPreference = "Continue"
$ACR = "auraauditaiprodacr"
$ResourceGroup = "aura-audit-ai-prod"

$services = @(
    "sampling",
    "substantive-testing",
    "estimates-evaluation",
    "disclosures",
    "qc",
    "related-party",
    "subsequent-events",
    "advanced-report-generation"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Rebuilding All Affected Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

foreach ($service in $services) {
    Write-Host "`nBuilding $service..." -ForegroundColor Yellow
    $servicePath = "services/$service"
    $imageTag = "$ACR.azurecr.io/aura/${service}:fixed-v1"

    # Build using ACR
    az acr build --registry $ACR --image "aura/${service}:fixed-v1" $servicePath 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Built $service" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Build may have issues for $service" -ForegroundColor Yellow
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Updating Kubernetes Deployments" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$kubectlPath = "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat"

foreach ($service in $services) {
    Write-Host "Updating $service deployment..." -ForegroundColor Yellow
    $imageTag = "$ACR.azurecr.io/aura/${service}:fixed-v1"

    & $kubectlPath set image deployment/$service $service=$imageTag -n aura-audit-ai 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Updated $service" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] May need manual update for $service" -ForegroundColor Yellow
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Restarting Deployments" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

foreach ($service in $services) {
    Write-Host "Restarting $service..." -ForegroundColor Yellow
    & $kubectlPath rollout restart deployment/$service -n aura-audit-ai 2>&1
}

Write-Host "`nWaiting 60 seconds for pods to restart..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Checking Pod Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

& $kubectlPath get pods -n aura-audit-ai -l "app in (sampling,substantive-testing,estimates-evaluation,disclosures,qc,related-party,subsequent-events,advanced-report-generation)"

Write-Host "`nDone!" -ForegroundColor Green
