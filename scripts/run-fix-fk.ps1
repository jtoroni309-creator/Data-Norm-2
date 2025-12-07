$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"

# Get the SOC pod
$POD = kubectl get pods -n aura-audit-ai -l app=soc-copilot -o jsonpath='{.items[0].metadata.name}'
Write-Host "Using SOC pod: $POD"

# Python script content
$script = @'
import asyncio
import asyncpg
import os
import re
from urllib.parse import urlparse, unquote

async def main():
    db_url = os.environ.get("DATABASE_URL", "")
    print(f"Connecting to database...")

    # Remove the +asyncpg suffix if present
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    # Parse URL manually to handle special characters in password
    match = re.match(r"postgresql://([^:]+):(.+)@([^:/]+):?(\d+)?/([^?]+)", db_url)
    if match:
        user = match.group(1)
        password = unquote(match.group(2))
        host = match.group(3)
        port = int(match.group(4)) if match.group(4) else 5432
        database = match.group(5)

        print(f"Host: {host}, Port: {port}, DB: {database}, User: {user}")

        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            ssl="require"
        )
    else:
        print("Could not parse DATABASE_URL")
        return

    try:
        rows = await conn.fetch("""
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND ccu.table_name = 'users'
              AND ccu.table_schema = 'soc_copilot'
              AND tc.table_schema = 'soc_copilot'
        """)

        print(f"Found {len(rows)} FK constraints to update")

        for row in rows:
            constraint = row["constraint_name"]
            schema = row["table_schema"]
            table = row["table_name"]
            column = row["column_name"]

            print(f"Updating {schema}.{table}.{column}...")

            await conn.execute(f"ALTER TABLE {schema}.{table} DROP CONSTRAINT IF EXISTS {constraint}")
            await conn.execute(f"""
                ALTER TABLE {schema}.{table}
                ADD CONSTRAINT {constraint}
                FOREIGN KEY ({column})
                REFERENCES atlas.users(id)
            """)

            print(f"  Done!")

        print("All FK constraints updated!")
    finally:
        await conn.close()

asyncio.run(main())
'@

# Base64 encode the script
$bytes = [System.Text.Encoding]::UTF8.GetBytes($script)
$base64 = [System.Convert]::ToBase64String($bytes)

Write-Host "Running FK fix script..."
kubectl exec -n aura-audit-ai $POD -- bash -c "echo $base64 | base64 -d > /tmp/fix_fk.py && python /tmp/fix_fk.py"
