# Update nginx ConfigMap
$kubectlPath = "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat"
$nginxPath = "c:\Users\jtoroni\Data Norm\Data-Norm-2\client-portal\nginx.conf"

# Delete existing ConfigMap
& $kubectlPath delete configmap client-portal-nginx-config -n aura-audit-ai --ignore-not-found

# Create new ConfigMap from file
& $kubectlPath create configmap client-portal-nginx-config --from-file="default.conf=$nginxPath" -n aura-audit-ai

# Restart the deployment to pick up the new config
& $kubectlPath rollout restart deployment/client-portal -n aura-audit-ai
