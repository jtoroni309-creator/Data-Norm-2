$pythonScript = @'
from jose import jwt
import os

secret = os.environ.get("JWT_SECRET")
algorithm = os.environ.get("JWT_ALGORITHM", "HS256")

print("JWT_SECRET:", secret[:20] + "..." if secret else "NOT SET")
print("JWT_ALGORITHM:", algorithm)

# Create token
token = jwt.encode({"sub": "test-user-id", "type": "access"}, secret, algorithm=algorithm)
print("Token:", token)

# Verify it works
decoded = jwt.decode(token, secret, algorithms=[algorithm])
print("Decoded:", decoded)
'@

$bytes = [System.Text.Encoding]::UTF8.GetBytes($pythonScript)
$encoded = [Convert]::ToBase64String($bytes)

& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/identity -- /bin/sh -c "echo $encoded | base64 -d > /tmp/test.py && cd /app && python /tmp/test.py"
