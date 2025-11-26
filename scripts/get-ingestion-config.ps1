$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"
kubectl get deploy ingestion -n aura-audit-ai -o yaml | Select-String -Pattern "DATABASE_URL" -Context 0,5
