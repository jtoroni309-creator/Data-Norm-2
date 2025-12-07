#!/usr/bin/env python3
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://").replace("sslmode=require", "ssl=require")

async def fix_enums():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Check where the enum exists
        result = await conn.execute(text("""
            SELECT n.nspname as schema, t.typname as type
            FROM pg_type t
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            WHERE t.typname = 'tsccategory'
        """))
        rows = result.fetchall()
        print(f"Existing tsccategory: {rows}")

        # If it's in public schema, we need to set search_path or use qualified name
        # Let's set search_path and then create tables

        # First, let's just set the search_path to include public
        await conn.execute(text("SET search_path TO soc_copilot, public"))

        # Drop tables
        print("Dropping tables...")
        await conn.execute(text("DROP TABLE IF EXISTS soc_copilot.test_results CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS soc_copilot.test_plans CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS soc_copilot.controls CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS soc_copilot.control_objectives CASCADE"))

        print("Creating control_objectives table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.control_objectives (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                objective_code VARCHAR(50) NOT NULL,
                objective_name VARCHAR(500) NOT NULL,
                objective_description TEXT NOT NULL,
                icfr_assertion VARCHAR(100),
                tsc_category public.tsccategory,
                tsc_criteria VARCHAR(50),
                points_of_focus_2022 TEXT[],
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("control_objectives created!")

        print("Creating controls table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.controls (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                objective_id UUID REFERENCES soc_copilot.control_objectives(id) ON DELETE CASCADE,
                control_code VARCHAR(50) NOT NULL,
                control_name VARCHAR(500) NOT NULL,
                control_description TEXT NOT NULL,
                control_type public.controltype NOT NULL,
                control_owner VARCHAR(255),
                frequency VARCHAR(100),
                automation_level VARCHAR(50),
                design_adequate BOOLEAN,
                design_notes TEXT,
                is_key_control BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("controls created!")

        print("Creating test_plans table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.test_plans (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                control_id UUID REFERENCES soc_copilot.controls(id) ON DELETE CASCADE,
                test_type public.testtype NOT NULL,
                test_objective TEXT NOT NULL,
                test_procedures TEXT NOT NULL,
                sample_size INTEGER,
                sampling_method VARCHAR(100),
                population_size INTEGER,
                required_evidence_types TEXT[],
                ai_generated BOOLEAN DEFAULT FALSE,
                ai_confidence_score DECIMAL(3,2),
                ai_rationale TEXT,
                approved_by UUID REFERENCES soc_copilot.users(id),
                approved_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("test_plans created!")

        print("Creating test_results table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.test_results (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                test_plan_id UUID REFERENCES soc_copilot.test_plans(id) ON DELETE CASCADE,
                evidence_id UUID,
                test_status public.teststatus DEFAULT 'PLANNED',
                test_date DATE NOT NULL,
                tested_by UUID REFERENCES soc_copilot.users(id) NOT NULL,
                passed BOOLEAN,
                findings TEXT,
                conclusion TEXT,
                sample_item_identifier VARCHAR(255),
                sample_selection_method VARCHAR(100),
                reviewed_by UUID REFERENCES soc_copilot.users(id),
                reviewed_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("test_results created!")

        print("All tables created successfully!")

asyncio.run(fix_enums())
