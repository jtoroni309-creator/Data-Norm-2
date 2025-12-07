# Check nginx config inside container
& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/client-portal -- head -70 /etc/nginx/conf.d/default.conf
