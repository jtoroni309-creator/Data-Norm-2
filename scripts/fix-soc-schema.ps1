#!/usr/bin/env pwsh
# Fix SOC Copilot database schema

Set-Location "c:\Users\jtoroni\Data Norm\Data-Norm-2"

$pythonScript = @'
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://").replace("sslmode=require", "ssl=require")

async def fix_schema():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Drop and recreate soc_engagements table with all columns
        print("Dropping and recreating soc_engagements table...")

        await conn.execute(text("DROP TABLE IF EXISTS soc_copilot.soc_engagements CASCADE"))

        await conn.execute(text("""
            CREATE TABLE soc_copilot.soc_engagements (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_name VARCHAR(500) NOT NULL,
                service_description TEXT NOT NULL,
                engagement_type engagementtype NOT NULL,
                report_type reporttype NOT NULL,
                status engagementstatus DEFAULT 'DRAFT',
                tsc_categories VARCHAR[] DEFAULT ARRAY['SECURITY']::VARCHAR[],
                review_period_start DATE,
                review_period_end DATE,
                point_in_time_date DATE,
                partner_id UUID REFERENCES soc_copilot.users(id) NOT NULL,
                manager_id UUID REFERENCES soc_copilot.users(id) NOT NULL,
                created_by UUID REFERENCES soc_copilot.users(id) NOT NULL,
                fiscal_year_end DATE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                locked_at TIMESTAMPTZ,
                locked_by UUID REFERENCES soc_copilot.users(id)
            )
        """))

        await conn.execute(text("CREATE INDEX idx_soc_engagements_status ON soc_copilot.soc_engagements(status)"))
        await conn.execute(text("CREATE INDEX idx_soc_engagements_partner ON soc_copilot.soc_engagements(partner_id)"))
        await conn.execute(text("CREATE INDEX idx_soc_engagements_manager ON soc_copilot.soc_engagements(manager_id)"))

        print("soc_engagements table recreated successfully!")

asyncio.run(fix_schema())
'@

& ".\scripts\kubectl.bat" exec -n aura-audit-ai deployment/identity -- python -c $pythonScript
