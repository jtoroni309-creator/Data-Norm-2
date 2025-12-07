#!/usr/bin/env python3
"""Fix soc_engagements table to use schema-qualified enum types"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://").replace("sslmode=require", "ssl=require")

async def fix_tables():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # First check what enums exist and where
        print("Checking existing enum types...")
        result = await conn.execute(text("""
            SELECT n.nspname as schema, t.typname as type
            FROM pg_type t
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            WHERE t.typname IN ('engagementtype', 'reporttype', 'engagementstatus', 'userrole',
                               'tsccategory', 'controltype', 'testtype', 'teststatus',
                               'evidencesourcetype', 'deviationseverity', 'approvalstatus',
                               'subservicetreatment')
            ORDER BY n.nspname, t.typname
        """))
        rows = result.fetchall()
        for row in rows:
            print(f"  {row[0]}.{row[1]}")

        # Drop and recreate soc_engagements and dependent tables
        print("\nDropping dependent tables...")
        tables_to_drop = [
            "soc_copilot.approvals",
            "soc_copilot.signatures",
            "soc_copilot.reports",
            "soc_copilot.deviations",
            "soc_copilot.test_results",
            "soc_copilot.evidence",
            "soc_copilot.evidence_sources",
            "soc_copilot.test_plans",
            "soc_copilot.cuec",
            "soc_copilot.controls",
            "soc_copilot.control_objectives",
            "soc_copilot.csoc",
            "soc_copilot.subservice_orgs",
            "soc_copilot.workflow_tasks",
            "soc_copilot.management_assertions",
            "soc_copilot.system_descriptions",
            "soc_copilot.system_components",
            "soc_copilot.engagement_team",
            "soc_copilot.audit_trail",
            "soc_copilot.soc_engagements",
            "soc_copilot.users"
        ]

        for table in tables_to_drop:
            await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            print(f"  Dropped {table}")

        # Recreate users table
        print("\nCreating users table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                role soc_copilot.userrole NOT NULL,
                firm_name VARCHAR(255) DEFAULT 'Fred J. Toroni & Company Certified Public Accountants',
                cpa_license_number VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                mfa_enabled BOOLEAN DEFAULT FALSE,
                last_login_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  users created!")

        # Recreate soc_engagements with schema-qualified enums
        print("\nCreating soc_engagements table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.soc_engagements (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_name VARCHAR(500) NOT NULL,
                service_description TEXT NOT NULL,
                engagement_type soc_copilot.engagementtype NOT NULL,
                report_type soc_copilot.reporttype NOT NULL,
                status soc_copilot.engagementstatus DEFAULT 'DRAFT',
                tsc_categories VARCHAR[],
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
        print("  soc_engagements created!")

        # Create engagement_team
        print("\nCreating engagement_team table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.engagement_team (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                user_id UUID REFERENCES soc_copilot.users(id),
                role soc_copilot.userrole NOT NULL,
                assigned_by UUID REFERENCES soc_copilot.users(id),
                assigned_at TIMESTAMPTZ DEFAULT NOW(),
                removed_at TIMESTAMPTZ
            )
        """))
        print("  engagement_team created!")

        # Create system_components
        print("\nCreating system_components table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.system_components (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                component_name VARCHAR(255) NOT NULL,
                component_type VARCHAR(100),
                description TEXT,
                in_scope BOOLEAN DEFAULT TRUE,
                boundaries TEXT,
                data_flows JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  system_components created!")

        # Create subservice_orgs
        print("\nCreating subservice_orgs table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.subservice_orgs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                org_name VARCHAR(255) NOT NULL,
                service_description TEXT NOT NULL,
                treatment soc_copilot.subservicetreatment NOT NULL,
                has_soc_report BOOLEAN DEFAULT FALSE,
                soc_report_period_start DATE,
                soc_report_period_end DATE,
                soc_report_opinion VARCHAR(50),
                monitoring_notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  subservice_orgs created!")

        # Create csoc
        print("\nCreating csoc table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.csoc (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                subservice_org_id UUID REFERENCES soc_copilot.subservice_orgs(id) ON DELETE CASCADE,
                csoc_description TEXT NOT NULL,
                monitoring_procedure TEXT,
                last_monitored_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  csoc created!")

        # Create control_objectives
        print("\nCreating control_objectives table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.control_objectives (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                objective_code VARCHAR(50) NOT NULL,
                objective_name VARCHAR(500) NOT NULL,
                objective_description TEXT NOT NULL,
                icfr_assertion VARCHAR(100),
                tsc_category soc_copilot.tsccategory,
                tsc_criteria VARCHAR(50),
                points_of_focus_2022 TEXT[],
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  control_objectives created!")

        # Create controls
        print("\nCreating controls table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.controls (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                objective_id UUID REFERENCES soc_copilot.control_objectives(id) ON DELETE CASCADE,
                control_code VARCHAR(50) NOT NULL,
                control_name VARCHAR(500) NOT NULL,
                control_description TEXT NOT NULL,
                control_type soc_copilot.controltype NOT NULL,
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
        print("  controls created!")

        # Create cuec
        print("\nCreating cuec table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.cuec (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                control_id UUID REFERENCES soc_copilot.controls(id),
                cuec_description TEXT NOT NULL,
                rationale TEXT,
                disclosed_in_report BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  cuec created!")

        # Create test_plans
        print("\nCreating test_plans table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.test_plans (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                control_id UUID REFERENCES soc_copilot.controls(id) ON DELETE CASCADE,
                test_type soc_copilot.testtype NOT NULL,
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
        print("  test_plans created!")

        # Create evidence_sources
        print("\nCreating evidence_sources table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.evidence_sources (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                source_name VARCHAR(255) NOT NULL,
                source_type soc_copilot.evidencesourcetype NOT NULL,
                connection_config JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                last_sync_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  evidence_sources created!")

        # Create evidence
        print("\nCreating evidence table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.evidence (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                source_id UUID REFERENCES soc_copilot.evidence_sources(id),
                test_plan_id UUID REFERENCES soc_copilot.test_plans(id),
                file_name VARCHAR(500),
                file_path TEXT,
                file_size_bytes BIGINT,
                mime_type VARCHAR(100),
                sha256_hash VARCHAR(64) NOT NULL UNIQUE,
                collected_at TIMESTAMPTZ DEFAULT NOW(),
                collected_by UUID REFERENCES soc_copilot.users(id),
                evidence_type VARCHAR(100),
                description TEXT,
                quality_score DECIMAL(3,2),
                relevance_score DECIMAL(3,2),
                completeness_score DECIMAL(3,2),
                ai_extracted_data JSONB,
                version INTEGER DEFAULT 1,
                superseded_by UUID REFERENCES soc_copilot.evidence(id),
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  evidence created!")

        # Create test_results
        print("\nCreating test_results table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.test_results (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                test_plan_id UUID REFERENCES soc_copilot.test_plans(id) ON DELETE CASCADE,
                evidence_id UUID REFERENCES soc_copilot.evidence(id),
                test_status soc_copilot.teststatus NOT NULL DEFAULT 'PLANNED',
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
        print("  test_results created!")

        # Create deviations
        print("\nCreating deviations table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.deviations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                test_result_id UUID REFERENCES soc_copilot.test_results(id) ON DELETE CASCADE,
                control_id UUID REFERENCES soc_copilot.controls(id),
                deviation_description TEXT NOT NULL,
                root_cause TEXT,
                severity soc_copilot.deviationseverity NOT NULL,
                impact_on_objective TEXT,
                impact_on_opinion TEXT,
                remediation_plan TEXT,
                remediation_owner UUID REFERENCES soc_copilot.users(id),
                remediation_deadline DATE,
                remediation_completed_at TIMESTAMPTZ,
                retest_required BOOLEAN DEFAULT TRUE,
                retest_plan_id UUID REFERENCES soc_copilot.test_plans(id),
                retest_passed BOOLEAN,
                identified_by UUID REFERENCES soc_copilot.users(id),
                identified_at TIMESTAMPTZ DEFAULT NOW(),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  deviations created!")

        # Create management_assertions
        print("\nCreating management_assertions table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.management_assertions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                assertion_text TEXT NOT NULL,
                assertion_date DATE NOT NULL,
                signatory_name VARCHAR(255) NOT NULL,
                signatory_title VARCHAR(255) NOT NULL,
                signatory_signature_image TEXT,
                approved BOOLEAN DEFAULT FALSE,
                approved_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  management_assertions created!")

        # Create system_descriptions
        print("\nCreating system_descriptions table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.system_descriptions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                overview TEXT,
                principal_service_commitments TEXT,
                system_components TEXT,
                system_boundaries TEXT,
                types_of_data_processed TEXT,
                principal_service_users TEXT,
                infrastructure TEXT,
                software TEXT,
                people TEXT,
                procedures TEXT,
                data_flows TEXT,
                cuec_section TEXT,
                subservice_section TEXT,
                ai_generated BOOLEAN DEFAULT FALSE,
                ai_confidence_score DECIMAL(3,2),
                drafted_by UUID REFERENCES soc_copilot.users(id),
                drafted_at TIMESTAMPTZ,
                approved_by UUID REFERENCES soc_copilot.users(id),
                approved_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  system_descriptions created!")

        # Create reports
        print("\nCreating reports table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.reports (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                report_title VARCHAR(500) NOT NULL,
                report_date DATE NOT NULL,
                report_version INTEGER DEFAULT 1,
                auditor_opinion TEXT,
                scope_section TEXT,
                control_objectives_section TEXT,
                tests_and_results_section TEXT,
                management_assertion_section TEXT,
                system_description_section TEXT,
                other_information_section TEXT,
                is_draft BOOLEAN DEFAULT TRUE,
                is_signed BOOLEAN DEFAULT FALSE,
                is_released BOOLEAN DEFAULT FALSE,
                restricted_distribution BOOLEAN DEFAULT TRUE,
                watermark_text VARCHAR(500),
                pdf_path TEXT,
                docx_path TEXT,
                drafted_by UUID REFERENCES soc_copilot.users(id),
                drafted_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  reports created!")

        # Create signatures
        print("\nCreating signatures table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.signatures (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                report_id UUID REFERENCES soc_copilot.reports(id) ON DELETE CASCADE,
                signer_id UUID REFERENCES soc_copilot.users(id) NOT NULL,
                signer_role soc_copilot.userrole NOT NULL,
                signature_date TIMESTAMPTZ DEFAULT NOW(),
                signature_image TEXT,
                digital_signature TEXT,
                attestation_text TEXT DEFAULT 'I have reviewed this report and, based on my knowledge, the information is accurate and complete in all material respects.',
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  signatures created!")

        # Create workflow_tasks
        print("\nCreating workflow_tasks table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.workflow_tasks (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                task_title VARCHAR(500) NOT NULL,
                task_description TEXT,
                task_type VARCHAR(100),
                assigned_to UUID REFERENCES soc_copilot.users(id),
                assigned_by UUID REFERENCES soc_copilot.users(id),
                assigned_at TIMESTAMPTZ DEFAULT NOW(),
                due_date DATE,
                priority VARCHAR(50) DEFAULT 'MEDIUM',
                status VARCHAR(50) DEFAULT 'TODO',
                completed_at TIMESTAMPTZ,
                depends_on UUID REFERENCES soc_copilot.workflow_tasks(id),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  workflow_tasks created!")

        # Create approvals
        print("\nCreating approvals table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.approvals (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id) ON DELETE CASCADE,
                report_id UUID REFERENCES soc_copilot.reports(id),
                approval_type VARCHAR(100) NOT NULL,
                approval_level INTEGER NOT NULL,
                approver_id UUID REFERENCES soc_copilot.users(id) NOT NULL,
                approval_status soc_copilot.approvalstatus DEFAULT 'PENDING',
                comments TEXT,
                approved_at TIMESTAMPTZ,
                rejected_at TIMESTAMPTZ,
                rejection_reason TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        print("  approvals created!")

        # Create audit_trail
        print("\nCreating audit_trail table...")
        await conn.execute(text("""
            CREATE TABLE soc_copilot.audit_trail (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                engagement_id UUID REFERENCES soc_copilot.soc_engagements(id),
                event_type VARCHAR(100) NOT NULL,
                entity_type VARCHAR(100) NOT NULL,
                entity_id UUID NOT NULL,
                actor_id UUID REFERENCES soc_copilot.users(id),
                actor_ip_address INET,
                action VARCHAR(100) NOT NULL,
                before_state JSONB,
                after_state JSONB,
                event_hash VARCHAR(64) NOT NULL,
                previous_hash VARCHAR(64),
                created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
            )
        """))
        print("  audit_trail created!")

        # Create indexes
        print("\nCreating indexes...")
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON soc_copilot.users(email)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_role ON soc_copilot.users(role)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_engagements_status ON soc_copilot.soc_engagements(status)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_engagements_partner ON soc_copilot.soc_engagements(partner_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_engagements_manager ON soc_copilot.soc_engagements(manager_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_entity ON soc_copilot.audit_trail(entity_type, entity_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_created ON soc_copilot.audit_trail(created_at)"))
        print("  Indexes created!")

        print("\nAll tables recreated successfully with schema-qualified enum types!")

asyncio.run(fix_tables())
