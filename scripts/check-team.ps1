$pythonScript = @'
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    url = os.environ.get("DATABASE_URL")
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        # Check team members
        result = await conn.execute(text("SELECT engagement_id, user_id, role FROM atlas.engagement_team_members"))
        rows = result.fetchall()
        print(f"Team members: {len(rows)}")
        for row in rows:
            print(f"  {row}")

        # Check RLS policies
        result2 = await conn.execute(text("SELECT polname, polcmd, polroles FROM pg_policy WHERE polrelid = 'atlas.engagements'::regclass"))
        policies = result2.fetchall()
        print(f"RLS Policies: {policies}")

        # Check if RLS is enabled
        result3 = await conn.execute(text("SELECT relrowsecurity FROM pg_class WHERE relname = 'engagements'"))
        rls = result3.fetchone()
        print(f"RLS enabled: {rls}")
    await engine.dispose()

asyncio.run(check())
'@

$bytes = [System.Text.Encoding]::UTF8.GetBytes($pythonScript)
$encoded = [Convert]::ToBase64String($bytes)

& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/engagement -- /bin/sh -c "echo $encoded | base64 -d > /tmp/check.py && python /tmp/check.py"
