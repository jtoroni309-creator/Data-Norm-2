#!/usr/bin/env pwsh
# Add missing columns to soc_engagements table

Set-Location "c:\Users\jtoroni\Data Norm\Data-Norm-2"

$pythonScript = @'
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://").replace("sslmode=require", "ssl=require")

async def add_columns():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE soc_copilot.soc_engagements ADD COLUMN IF NOT EXISTS locked_at TIMESTAMPTZ"))
        await conn.execute(text("ALTER TABLE soc_copilot.soc_engagements ADD COLUMN IF NOT EXISTS locked_by UUID"))
        print("Added locked_at and locked_by columns to soc_engagements")

asyncio.run(add_columns())
'@

& ".\scripts\kubectl.bat" exec -n aura-audit-ai deployment/identity -- python -c $pythonScript
