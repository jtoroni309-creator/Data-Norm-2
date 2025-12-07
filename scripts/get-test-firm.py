import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os

DATABASE_URL = os.environ.get('DATABASE_URL', '').replace('postgresql://', 'postgresql+asyncpg://').replace('sslmode=require', 'ssl=require')

async def get_firm():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT id, name, max_users FROM atlas.cpa_firms
            WHERE name LIKE '%Toroni%'
        """))
        for row in result:
            print(f'Firm ID: {row[0]}, Name: {row[1]}, Max Users: {row[2]}')

asyncio.run(get_firm())
