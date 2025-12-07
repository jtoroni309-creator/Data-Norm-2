$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"

# Get the SOC pod
$POD = kubectl get pods -n aura-audit-ai -l app=soc-copilot -o jsonpath='{.items[0].metadata.name}'
Write-Host "Using SOC pod: $POD"

# Run SQL to drop and recreate FK constraints
$sql = @"
-- Drop existing FK constraints on soc_copilot tables that reference soc_copilot.users
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
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
    )
    LOOP
        RAISE NOTICE 'Dropping constraint % on %.%', r.constraint_name, r.table_schema, r.table_name;
        EXECUTE format('ALTER TABLE %I.%I DROP CONSTRAINT IF EXISTS %I', r.table_schema, r.table_name, r.constraint_name);

        RAISE NOTICE 'Creating new constraint % referencing atlas.users', r.constraint_name;
        EXECUTE format('ALTER TABLE %I.%I ADD CONSTRAINT %I FOREIGN KEY (%I) REFERENCES atlas.users(id)',
            r.table_schema, r.table_name, r.constraint_name, r.column_name);
    END LOOP;
END
\$\$;

SELECT 'FK constraints updated successfully!' as result;
"@

Write-Host "Running SQL to update FK constraints..."
kubectl exec -n aura-audit-ai $POD -- python -c "
import asyncio
import asyncpg
import os

async def main():
    conn = await asyncpg.connect(os.environ['DATABASE_URL'])
    try:
        # Get list of FK constraints
        rows = await conn.fetch('''
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name,
                tc.constraint_name,
                ccu.table_schema AS fk_schema
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
        ''')

        print(f'Found {len(rows)} FK constraints to update')

        for row in rows:
            constraint = row['constraint_name']
            table = f\"{row['table_schema']}.{row['table_name']}\"
            column = row['column_name']

            print(f'Updating {table}.{column}...')

            # Drop old constraint
            await conn.execute(f'ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint}')

            # Add new constraint referencing atlas.users
            await conn.execute(f'''
                ALTER TABLE {table}
                ADD CONSTRAINT {constraint}
                FOREIGN KEY ({column})
                REFERENCES atlas.users(id)
            ''')

            print(f'  Done!')

        print('All FK constraints updated!')
    finally:
        await conn.close()

asyncio.run(main())
"
