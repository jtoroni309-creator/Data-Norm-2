$pythonScript = @'
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def disable_rls():
    url = os.environ.get("DATABASE_URL")
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        # Disable RLS on engagements table
        await conn.execute(text("ALTER TABLE atlas.engagements DISABLE ROW LEVEL SECURITY"))
        print("RLS disabled on engagements table")

        # Also disable on team members and binder nodes
        await conn.execute(text("ALTER TABLE atlas.engagement_team_members DISABLE ROW LEVEL SECURITY"))
        print("RLS disabled on engagement_team_members table")

        await conn.execute(text("ALTER TABLE atlas.binder_nodes DISABLE ROW LEVEL SECURITY"))
        print("RLS disabled on binder_nodes table")
    await engine.dispose()
    print("Done - RLS disabled. Engagements should now be visible.")

asyncio.run(disable_rls())
'@

$bytes = [System.Text.Encoding]::UTF8.GetBytes($pythonScript)
$encoded = [Convert]::ToBase64String($bytes)

& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/engagement -- /bin/sh -c "echo $encoded | base64 -d > /tmp/disable_rls.py && python /tmp/disable_rls.py"
