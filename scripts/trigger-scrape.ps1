$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[0].metadata.name}'

Write-Host "=== Triggering EDGAR Scraping ===" -ForegroundColor Green
kubectl exec $pod -n aura-audit-ai -- python -c "import urllib.request; req = urllib.request.Request('http://localhost:8000/api/v1/data/scrape-edgar?sp500=true', method='POST'); print(urllib.request.urlopen(req).read().decode())"
