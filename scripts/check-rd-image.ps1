$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"
Write-Host "R&D Pod Details:"
kubectl get pods -n aura-audit-ai -l app=rd-study-automation -o jsonpath='{.items[0].spec.containers[0].image}'
Write-Host ""
Write-Host ""
Write-Host "Pod start time:"
kubectl get pods -n aura-audit-ai -l app=rd-study-automation -o jsonpath='{.items[0].status.startTime}'
Write-Host ""
Write-Host ""
Write-Host "Image Pull Policy:"
kubectl get pods -n aura-audit-ai -l app=rd-study-automation -o jsonpath='{.items[0].spec.containers[0].imagePullPolicy}'
