$env:PATH = $env:PATH + ";C:\Users\jtoroni\.azure-kubectl;C:\Users\jtoroni\.azure-kubelogin"
kubectl logs deployment/azure-ml-training -n aura-audit-ai --tail=50
