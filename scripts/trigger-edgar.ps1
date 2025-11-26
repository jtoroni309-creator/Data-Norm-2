$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

Write-Host "Creating EDGAR scraping job..." -ForegroundColor Cyan
kubectl create job edgar-scrape-$(Get-Date -Format 'yyyyMMdd-HHmmss') --from=cronjob/edgar-scraper-job -n aura-audit-ai

Write-Host ""
Write-Host "Checking all jobs:" -ForegroundColor Cyan
kubectl get jobs -n aura-audit-ai

Write-Host ""
Write-Host "Checking pods:" -ForegroundColor Cyan
kubectl get pods -n aura-audit-ai | Select-String -Pattern "edgar|azure-ml"
