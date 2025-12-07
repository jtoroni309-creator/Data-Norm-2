$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"
kubectl rollout restart deployment/rd-study-automation -n aura-audit-ai
kubectl rollout status deployment/rd-study-automation -n aura-audit-ai --timeout=120s
