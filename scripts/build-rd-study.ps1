# Build and deploy R&D Study Automation Service
$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "Building R&D Study Automation Service..." -ForegroundColor Cyan
Write-Host "This may take several minutes..." -ForegroundColor Yellow

# Build the Docker image in ACR
$result = az acr build --registry auraauditaiprodacr --image "aura/rd-study-automation:latest" --file "services/rd-study-automation/Dockerfile" "services/rd-study-automation/" --no-logs 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build submitted successfully!" -ForegroundColor Green

    # Wait a bit then check the build status
    Write-Host "Checking build status..." -ForegroundColor Cyan
    Start-Sleep -Seconds 15
    az acr task list-runs --registry auraauditaiprodacr --top 1 --output table

    Write-Host ""
    Write-Host "Deploying to Kubernetes..." -ForegroundColor Cyan

    # Apply the Kubernetes deployment
    kubectl apply -f infra/k8s/base/rd-study-automation-deployment.yaml

    # Restart the deployment to pull the new image
    kubectl rollout restart deployment/rd-study-automation -n aura-audit-ai

    Write-Host ""
    Write-Host "Waiting for deployment..." -ForegroundColor Yellow
    kubectl rollout status deployment/rd-study-automation -n aura-audit-ai --timeout=120s

    Write-Host ""
    Write-Host "R&D Study Automation service deployed!" -ForegroundColor Green
    kubectl get pods -n aura-audit-ai -l app=rd-study-automation
} else {
    Write-Host "Build submission failed!" -ForegroundColor Red
    Write-Host $result
}
