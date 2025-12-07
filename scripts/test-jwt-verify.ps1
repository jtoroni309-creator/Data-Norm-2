$pythonScript = @'
from jose import jwt
import os

secret = os.environ.get("JWT_SECRET")
algorithm = os.environ.get("JWT_ALGORITHM", "HS256")

print("JWT_SECRET:", secret[:20] + "..." if secret else "NOT SET")
print("JWT_ALGORITHM:", algorithm)

# Token created by identity service
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJ0eXBlIjoiYWNjZXNzIn0.ApxaB9uErhyl-0EsmA9ZTW8x7GjRIWxp6lIZlPCeixQ"

try:
    decoded = jwt.decode(token, secret, algorithms=[algorithm])
    print("Successfully decoded:", decoded)
except Exception as e:
    print("Error decoding:", e)
'@

$bytes = [System.Text.Encoding]::UTF8.GetBytes($pythonScript)
$encoded = [Convert]::ToBase64String($bytes)

& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/engagement -- /bin/sh -c "echo $encoded | base64 -d > /tmp/test.py && python /tmp/test.py"
