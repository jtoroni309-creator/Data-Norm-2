$pythonScript = @'
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    url = os.environ.get("DATABASE_URL")
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        # Get full policy definition
        result = await conn.execute(text("""
            SELECT polname, polcmd, polqual::text, polwithcheck::text
            FROM pg_policy
            WHERE polrelid = 'atlas.engagements'::regclass
        """))
        rows = result.fetchall()
        print("RLS Policy details:")
        for row in rows:
            print(f"  Name: {row[0]}")
            print(f"  Cmd: {row[1]}")
            print(f"  Qual: {row[2]}")
            print(f"  WithCheck: {row[3]}")

        # Test current_setting
        try:
            await conn.execute(text("SET app.current_user_id = '1e290b7a-ee49-456d-8d8d-e7fd11c78e10'"))
            result2 = await conn.execute(text("SELECT current_setting('app.current_user_id', true)"))
            setting = result2.fetchone()
            print(f"Current user setting: {setting}")

            # Now try to select with RLS
            result3 = await conn.execute(text("SELECT id, name FROM atlas.engagements"))
            engagements = result3.fetchall()
            print(f"Engagements after setting user: {len(engagements)}")
            for e in engagements:
                print(f"  {e}")
        except Exception as ex:
            print(f"Error: {ex}")

    await engine.dispose()

asyncio.run(check())
'@

$bytes = [System.Text.Encoding]::UTF8.GetBytes($pythonScript)
$encoded = [Convert]::ToBase64String($bytes)

& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/engagement -- /bin/sh -c "echo $encoded | base64 -d > /tmp/check.py && python /tmp/check.py"
