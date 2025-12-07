#!/usr/bin/env python3
"""Fix SOC foreign key constraints to reference atlas.users instead of soc_copilot.users"""

import asyncio
import asyncpg
import os

async def main():
    # Database URL from environment
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/aura')

    # Parse DATABASE_URL if it exists
    if db_url.startswith('postgresql://'):
        # Convert to asyncpg format
        db_url = db_url.replace('postgresql://', '')

    # Connect to database
    conn = await asyncpg.connect(
        host='aura-audit-ai-prod-db.postgres.database.azure.com',
        database='postgres',
        user='auradbadmin',
        password=os.getenv('DB_PASSWORD', ''),
        ssl='require'
    )

    try:
        # Check current FK constraints
        print("Current foreign key constraints referencing users:")
        rows = await conn.fetch("""
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND ccu.table_name = 'users'
              AND tc.table_schema = 'soc_copilot'
        """)

        for row in rows:
            print(f"  {row['table_schema']}.{row['table_name']}.{row['column_name']} -> "
                  f"{row['foreign_table_schema']}.{row['foreign_table_name']}.{row['foreign_column_name']} "
                  f"({row['constraint_name']})")

        if not rows:
            print("  No FK constraints found referencing users in soc_copilot schema")
            return

        # Drop and recreate FK constraints to reference atlas.users
        print("\nUpdating foreign key constraints to reference atlas.users...")

        for row in rows:
            constraint_name = row['constraint_name']
            table_schema = row['table_schema']
            table_name = row['table_name']
            column_name = row['column_name']

            print(f"  Updating {table_schema}.{table_name}.{column_name}...")

            # Drop old constraint
            await conn.execute(f"""
                ALTER TABLE {table_schema}.{table_name}
                DROP CONSTRAINT IF EXISTS {constraint_name}
            """)

            # Add new constraint referencing atlas.users
            await conn.execute(f"""
                ALTER TABLE {table_schema}.{table_name}
                ADD CONSTRAINT {constraint_name}
                FOREIGN KEY ({column_name})
                REFERENCES atlas.users(id)
            """)

            print(f"    Done!")

        print("\nAll FK constraints updated successfully!")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
