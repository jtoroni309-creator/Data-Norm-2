$pythonScript = @'
import asyncio
import httpx
import os
from jose import jwt

# Create a valid token using the JWT_SECRET
secret = os.environ.get("JWT_SECRET")
user_id = "1e290b7a-ee49-456d-8d8d-e7fd11c78e10"  # jtoroni user
token = jwt.encode({"sub": user_id, "type": "access"}, secret, algorithm="HS256")

async def test():
    async with httpx.AsyncClient() as client:
        # Get engagements
        response = await client.get(
            "http://engagement:80/engagements",
            headers={"Authorization": f"Bearer {token}"}
        )
        print("Status:", response.status_code)
        print("Response type:", type(response.json()))
        print("Response:", response.json())

asyncio.run(test())
'@

$bytes = [System.Text.Encoding]::UTF8.GetBytes($pythonScript)
$encoded = [Convert]::ToBase64String($bytes)

& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/engagement -- /bin/sh -c "pip install httpx -q 2>/dev/null && echo $encoded | base64 -d > /tmp/test.py && python /tmp/test.py"
