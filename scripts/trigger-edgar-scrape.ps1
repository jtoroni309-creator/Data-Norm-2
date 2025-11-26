$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"
Write-Host "Creating manual EDGAR scraping job..." -ForegroundColor Cyan
kubectl create job initial-edgar-scrape --from=cronjob/edgar-scraper-job -n aura-audit-ai
Write-Host ""
Write-Host "Job created! Monitor with:" -ForegroundColor Green
Write-Host "kubectl logs -f job/initial-edgar-scrape -n aura-audit-ai"
