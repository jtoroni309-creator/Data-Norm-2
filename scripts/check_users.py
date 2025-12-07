import asyncio
import httpx

async def test_login():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test login
        print("Testing login...")
        response = await client.post(
            "http://identity:80/auth/login",
            json={
                "email": "admin@example.com",
                "password": "Admin123!"
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS! Got token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"User: {data.get('user', {})}")
        else:
            print(f"Response: {response.text}")

asyncio.run(test_login())
