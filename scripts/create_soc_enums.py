#!/usr/bin/env python3
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://").replace("sslmode=require", "ssl=require")

async def create_enums():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        enums = [
            ("tsccategory", ['SECURITY', 'AVAILABILITY', 'PROCESSING_INTEGRITY', 'CONFIDENTIALITY', 'PRIVACY']),
            ("controltype", ['PREVENTIVE', 'DETECTIVE', 'CORRECTIVE']),
            ("testtype", ['WALKTHROUGH', 'DESIGN_EVALUATION', 'OPERATING_EFFECTIVENESS']),
            ("teststatus", ['PLANNED', 'IN_PROGRESS', 'COMPLETED', 'PASSED', 'FAILED', 'DEVIATION', 'RETESTED']),
            ("evidencesourcetype", ['IAM', 'SIEM', 'TICKETING', 'CHANGE_MANAGEMENT', 'CI_CD', 'CLOUD_PROVIDER', 'MANUAL_UPLOAD', 'SYSTEM_GENERATED']),
            ("deviationseverity", ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
            ("approvalstatus", ['PENDING', 'APPROVED', 'REJECTED', 'WITHDRAWN']),
            ("subservicetreatment", ['INCLUSIVE', 'CARVE_OUT']),
        ]

        for enum_name, values in enums:
            # Check if enum exists
            result = await conn.execute(text(f"SELECT 1 FROM pg_type WHERE typname = '{enum_name}'"))
            exists = result.fetchone()

            if not exists:
                values_str = ", ".join([f"'{v}'" for v in values])
                sql = f"CREATE TYPE {enum_name} AS ENUM ({values_str})"
                print(f"Creating enum: {enum_name}")
                await conn.execute(text(sql))
            else:
                print(f"Enum {enum_name} already exists")

        print("All enums created!")

asyncio.run(create_enums())
