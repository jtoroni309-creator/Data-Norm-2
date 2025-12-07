#!/usr/bin/env python3
"""Drop foreign key constraint on engagements.client_id"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def drop_fk():
    url = os.environ.get('DATABASE_URL')
    print(f"Connecting to database...")
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        # Check if FK exists
        result = await conn.execute(text("""
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE table_schema = 'atlas' AND table_name = 'engagements'
            AND constraint_type = 'FOREIGN KEY'
        """))
        fks = result.fetchall()
        print(f"Found FKs: {fks}")

        # Drop the client_id FK if it exists
        for fk in fks:
            if 'client_id' in fk[0]:
                print(f"Dropping FK: {fk[0]}")
                await conn.execute(text(f'ALTER TABLE atlas.engagements DROP CONSTRAINT IF EXISTS "{fk[0]}"'))
                print("FK dropped successfully")

    await engine.dispose()
    print("Done")

if __name__ == "__main__":
    asyncio.run(drop_fk())
