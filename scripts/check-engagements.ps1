$pythonScript = @'
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    url = os.environ.get("DATABASE_URL")
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT id, name, status FROM atlas.engagements LIMIT 10"))
        rows = result.fetchall()
        print(f"Engagements in DB: {len(rows)}")
        for row in rows:
            print(f"  {row}")
    await engine.dispose()

asyncio.run(check())
'@

$bytes = [System.Text.Encoding]::UTF8.GetBytes($pythonScript)
$encoded = [Convert]::ToBase64String($bytes)

& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/engagement -- /bin/sh -c "echo $encoded | base64 -d > /tmp/check.py && python /tmp/check.py"
