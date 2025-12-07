$pythonScript = @'
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def drop_fk():
    url = os.environ.get("DATABASE_URL")
    print("Connecting to database...")
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT constraint_name FROM information_schema.table_constraints WHERE table_schema='atlas' AND table_name='engagements' AND constraint_type='FOREIGN KEY'"))
        fks = result.fetchall()
        print(f"Found FKs: {fks}")
        for fk in fks:
            if "client_id" in fk[0]:
                print(f"Dropping FK: {fk[0]}")
                await conn.execute(text(f'ALTER TABLE atlas.engagements DROP CONSTRAINT IF EXISTS "{fk[0]}"'))
                print("FK dropped successfully")
    await engine.dispose()
    print("Done")

asyncio.run(drop_fk())
'@

# Base64 encode the script to avoid quoting issues
$bytes = [System.Text.Encoding]::UTF8.GetBytes($pythonScript)
$encoded = [Convert]::ToBase64String($bytes)

# Run in the pod
& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/engagement -- /bin/sh -c "echo $encoded | base64 -d > /tmp/drop_fk.py && python /tmp/drop_fk.py"
