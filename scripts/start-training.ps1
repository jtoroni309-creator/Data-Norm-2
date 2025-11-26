$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"

$pod = kubectl get pods -l app=azure-ml-training -n aura-audit-ai -o jsonpath='{.items[0].metadata.name}'

Write-Host "=== Starting Audit Opinion Model Training ===" -ForegroundColor Green
kubectl exec $pod -n aura-audit-ai -- python -c "import urllib.request, json; req = urllib.request.Request('http://localhost:8000/api/v1/train/audit-opinion', data=json.dumps({'model_type':'audit_opinion','target_accuracy':0.995,'use_azure_compute':True}).encode(), headers={'Content-Type':'application/json'}); print(urllib.request.urlopen(req).read().decode())"

Write-Host ""
