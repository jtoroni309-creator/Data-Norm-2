#!/usr/bin/env python3
"""Fix SOC foreign key constraints to reference atlas.users"""
import asyncio
import asyncpg
import os

async def main():
    conn = await asyncpg.connect(os.environ['DATABASE_URL'])
    try:
        rows = await conn.fetch("""
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
        """)

        print(f"Found {len(rows)} FK constraints to update")

        for row in rows:
            constraint = row['constraint_name']
            schema = row['table_schema']
            table = row['table_name']
            column = row['column_name']

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

if __name__ == "__main__":
    asyncio.run(main())
