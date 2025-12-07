$pythonScript = @'
import asyncio
import httpx

async def test():
    # Test login to identity service
    async with httpx.AsyncClient() as client:
        # Login
        login_response = await client.post(
            "http://identity:80/auth/login",
            json={"email": "admin@toroniandcompany.com", "password": "Admin123!"}
        )
        print("Login status:", login_response.status_code)
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get("access_token")
            print("Got token:", token[:50] + "..." if token else "No token")

            # Try to use token to get engagements from engagement service
            eng_response = await client.get(
                "http://engagement:80/engagements",
                headers={"Authorization": f"Bearer {token}"}
            )
            print("Engagements status:", eng_response.status_code)
            print("Engagements response:", eng_response.text[:500])
        else:
            print("Login failed:", login_response.text)

asyncio.run(test())
'@

$bytes = [System.Text.Encoding]::UTF8.GetBytes($pythonScript)
$encoded = [Convert]::ToBase64String($bytes)

& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/engagement -- /bin/sh -c "pip install httpx -q && echo $encoded | base64 -d > /tmp/test.py && python /tmp/test.py"
