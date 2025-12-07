$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"
Write-Host "R&D Service:"
kubectl get svc -n aura-audit-ai rd-study-automation -o wide
Write-Host ""
Write-Host "R&D Endpoints:"
kubectl get endpoints -n aura-audit-ai rd-study-automation
Write-Host ""
Write-Host "Test connectivity from identity pod:"
$POD = kubectl get pods -n aura-audit-ai -l app=identity -o jsonpath='{.items[0].metadata.name}'
kubectl exec -n aura-audit-ai $POD -- curl -s -o /dev/null -w "%{http_code}" http://rd-study-automation:8000/health --connect-timeout 5
