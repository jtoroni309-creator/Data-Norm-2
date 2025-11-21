-- SOC Copilot Database Schema
-- PostgreSQL 15+ with pgvector extension
-- Standards: AT-C Section 320 (SSAE 18), AICPA Trust Services Criteria 2017/2022

-- ============================================================================
-- SCHEMA SETUP
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS soc_copilot;
SET search_path TO soc_copilot, public;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

CREATE TYPE engagement_type AS ENUM ('SOC1', 'SOC2');
CREATE TYPE report_type AS ENUM ('TYPE1', 'TYPE2');
CREATE TYPE engagement_status AS ENUM (
    'DRAFT',
    'PLANNING',
    'FIELDWORK',
    'REVIEW',
    'PARTNER_REVIEW',
    'SIGNED',
    'RELEASED',
    'ARCHIVED'
);

CREATE TYPE user_role AS ENUM (
    'CPA_PARTNER',
    'AUDIT_MANAGER',
    'AUDITOR',
    'CLIENT_MANAGEMENT',
    'READ_ONLY'
);

CREATE TYPE tsc_category AS ENUM (
    'SECURITY',        -- CC1-CC9 (required for SOC 2)
    'AVAILABILITY',    -- A1.1-A1.3
    'PROCESSING_INTEGRITY',  -- PI1.1-PI1.5
    'CONFIDENTIALITY', -- C1.1-C1.2
    'PRIVACY'          -- P1.1-P8.1
);

CREATE TYPE control_type AS ENUM (
    'PREVENTIVE',
    'DETECTIVE',
    'CORRECTIVE'
);

CREATE TYPE test_type AS ENUM (
    'WALKTHROUGH',
    'DESIGN_EVALUATION',
    'OPERATING_EFFECTIVENESS'
);

CREATE TYPE test_status AS ENUM (
    'PLANNED',
    'IN_PROGRESS',
    'COMPLETED',
    'PASSED',
    'FAILED',
    'DEVIATION',
    'RETESTED'
);

CREATE TYPE evidence_source_type AS ENUM (
    'IAM',
    'SIEM',
    'TICKETING',
    'CHANGE_MANAGEMENT',
    'CI_CD',
    'CLOUD_PROVIDER',
    'MANUAL_UPLOAD',
    'SYSTEM_GENERATED'
);

CREATE TYPE deviation_severity AS ENUM (
    'CRITICAL',
    'HIGH',
    'MEDIUM',
    'LOW'
);

CREATE TYPE approval_status AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED',
    'WITHDRAWN'
);

CREATE TYPE subservice_treatment AS ENUM (
    'INCLUSIVE',      -- Subservice controls included in scope
    'CARVE_OUT'       -- Subservice excluded; CSOC documented
);

-- ============================================================================
-- USER & RBAC
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    firm_name VARCHAR(255) DEFAULT 'Fred J. Toroni & Company Certified Public Accountants',
    cpa_license_number VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- SOC ENGAGEMENT
-- ============================================================================

CREATE TABLE soc_engagements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_name VARCHAR(500) NOT NULL,
    service_description TEXT NOT NULL,
    engagement_type engagement_type NOT NULL,
    report_type report_type NOT NULL,
    status engagement_status DEFAULT 'DRAFT',

    -- SOC 2 specific
    tsc_categories tsc_category[] DEFAULT ARRAY['SECURITY']::tsc_category[],

    -- Period
    review_period_start DATE,
    review_period_end DATE,
    point_in_time_date DATE,  -- For Type 1

    -- Team
    partner_id UUID REFERENCES users(id) NOT NULL,
    manager_id UUID REFERENCES users(id) NOT NULL,
    created_by UUID REFERENCES users(id) NOT NULL,

    -- Metadata
    fiscal_year_end DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    locked_at TIMESTAMPTZ,
    locked_by UUID REFERENCES users(id),

    CONSTRAINT valid_period_type1 CHECK (
        (report_type = 'TYPE1' AND point_in_time_date IS NOT NULL) OR report_type = 'TYPE2'
    ),
    CONSTRAINT valid_period_type2 CHECK (
        (report_type = 'TYPE2' AND review_period_start IS NOT NULL AND review_period_end IS NOT NULL) OR report_type = 'TYPE1'
    )
);

CREATE INDEX idx_soc_engagements_status ON soc_engagements(status);
CREATE INDEX idx_soc_engagements_partner ON soc_engagements(partner_id);
CREATE INDEX idx_soc_engagements_manager ON soc_engagements(manager_id);

-- ============================================================================
-- ENGAGEMENT TEAM
-- ============================================================================

CREATE TABLE engagement_team (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    role user_role NOT NULL,
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    removed_at TIMESTAMPTZ,

    UNIQUE(engagement_id, user_id, removed_at)
);

CREATE INDEX idx_engagement_team_engagement ON engagement_team(engagement_id);
CREATE INDEX idx_engagement_team_user ON engagement_team(user_id);

-- ============================================================================
-- SYSTEM COMPONENTS
-- ============================================================================

CREATE TABLE system_components (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,
    component_name VARCHAR(255) NOT NULL,
    component_type VARCHAR(100),  -- infrastructure, application, data, people, processes
    description TEXT,
    in_scope BOOLEAN DEFAULT TRUE,
    boundaries TEXT,  -- System boundary definition
    data_flows JSONB,  -- Data flow diagrams/descriptions
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_system_components_engagement ON system_components(engagement_id);

-- ============================================================================
-- SUBSERVICE ORGANIZATIONS
-- ============================================================================

CREATE TABLE subservice_orgs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,
    org_name VARCHAR(255) NOT NULL,
    service_description TEXT NOT NULL,
    treatment subservice_treatment NOT NULL,
    has_soc_report BOOLEAN DEFAULT FALSE,
    soc_report_period_start DATE,
    soc_report_period_end DATE,
    soc_report_opinion VARCHAR(50),  -- unqualified, qualified, adverse, disclaimer
    monitoring_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subservice_orgs_engagement ON subservice_orgs(engagement_id);

-- ============================================================================
-- CONTROL OBJECTIVES
-- ============================================================================

CREATE TABLE control_objectives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,
    objective_code VARCHAR(50) NOT NULL,
    objective_name VARCHAR(500) NOT NULL,
    objective_description TEXT NOT NULL,

    -- SOC 1: ICFR relevance
    icfr_assertion VARCHAR(100),  -- existence, completeness, accuracy, cutoff, classification

    -- SOC 2: TSC mapping
    tsc_category tsc_category,
    tsc_criteria VARCHAR(50),  -- CC1.1, CC2.1, A1.1, etc.
    points_of_focus_2022 TEXT[],

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_control_objectives_engagement ON control_objectives(engagement_id);
CREATE INDEX idx_control_objectives_tsc ON control_objectives(tsc_category, tsc_criteria);

-- ============================================================================
-- CONTROLS
-- ============================================================================

CREATE TABLE controls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,
    objective_id UUID REFERENCES control_objectives(id) ON DELETE CASCADE,
    control_code VARCHAR(50) NOT NULL,
    control_name VARCHAR(500) NOT NULL,
    control_description TEXT NOT NULL,
    control_type control_type NOT NULL,
    control_owner VARCHAR(255),
    frequency VARCHAR(100),  -- daily, weekly, monthly, quarterly, annually, real-time
    automation_level VARCHAR(50),  -- manual, semi-automated, fully-automated

    -- Design assessment
    design_adequate BOOLEAN,
    design_notes TEXT,

    is_key_control BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_controls_engagement ON controls(engagement_id);
CREATE INDEX idx_controls_objective ON controls(objective_id);

-- ============================================================================
-- COMPLEMENTARY USER ENTITY CONTROLS (CUEC)
-- ============================================================================

CREATE TABLE cuec (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,
    control_id UUID REFERENCES controls(id),
    cuec_description TEXT NOT NULL,
    rationale TEXT,  -- Why this is client's responsibility
    disclosed_in_report BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cuec_engagement ON cuec(engagement_id);

-- ============================================================================
-- COMPLEMENTARY SUBSERVICE ORG CONTROLS (CSOC)
-- ============================================================================

CREATE TABLE csoc (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subservice_org_id UUID REFERENCES subservice_orgs(id) ON DELETE CASCADE,
    csoc_description TEXT NOT NULL,
    monitoring_procedure TEXT,
    last_monitored_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_csoc_subservice ON csoc(subservice_org_id);

-- ============================================================================
-- TEST PLANS
-- ============================================================================

CREATE TABLE test_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,
    control_id UUID REFERENCES controls(id) ON DELETE CASCADE,
    test_type test_type NOT NULL,
    test_objective TEXT NOT NULL,
    test_procedures TEXT NOT NULL,

    -- Type 2 specific
    sample_size INTEGER,
    sampling_method VARCHAR(100),  -- attribute, judgmental, random
    population_size INTEGER,

    -- Evidence requirements
    required_evidence_types TEXT[],

    -- AI suggestions
    ai_generated BOOLEAN DEFAULT FALSE,
    ai_confidence_score DECIMAL(3,2),
    ai_rationale TEXT,

    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_test_plans_engagement ON test_plans(engagement_id);
CREATE INDEX idx_test_plans_control ON test_plans(control_id);

-- ============================================================================
-- EVIDENCE SOURCES & CONNECTORS
-- ============================================================================

CREATE TABLE evidence_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,
    source_name VARCHAR(255) NOT NULL,
    source_type evidence_source_type NOT NULL,
    connection_config JSONB,  -- API credentials, endpoints (encrypted)
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_evidence_sources_engagement ON evidence_sources(engagement_id);

-- ============================================================================
-- EVIDENCE
-- ============================================================================

CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,
    source_id UUID REFERENCES evidence_sources(id),
    test_plan_id UUID REFERENCES test_plans(id),

    -- File metadata
    file_name VARCHAR(500),
    file_path TEXT,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),

    -- Chain of custody
    sha256_hash VARCHAR(64) NOT NULL,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    collected_by UUID REFERENCES users(id),

    -- Classification
    evidence_type VARCHAR(100),  -- log, screenshot, policy_doc, configuration, ticket
    description TEXT,

    -- AI quality scoring
    quality_score DECIMAL(3,2),
    relevance_score DECIMAL(3,2),
    completeness_score DECIMAL(3,2),
    ai_extracted_data JSONB,

    -- Versioning
    version INTEGER DEFAULT 1,
    superseded_by UUID REFERENCES evidence(id),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_evidence_engagement ON evidence(engagement_id);
CREATE INDEX idx_evidence_test_plan ON evidence(test_plan_id);
CREATE INDEX idx_evidence_hash ON evidence(sha256_hash);

-- ============================================================================
-- TEST RESULTS
-- ============================================================================

CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_plan_id UUID REFERENCES test_plans(id) ON DELETE CASCADE,
    evidence_id UUID REFERENCES evidence(id),

    test_status test_status NOT NULL DEFAULT 'PLANNED',
    test_date DATE NOT NULL,
    tested_by UUID REFERENCES users(id) NOT NULL,

    -- Results
    passed BOOLEAN,
    findings TEXT,
    conclusion TEXT,

    -- Sampling details (Type 2)
    sample_item_identifier VARCHAR(255),
    sample_selection_method VARCHAR(100),

    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_test_results_test_plan ON test_results(test_plan_id);
CREATE INDEX idx_test_results_status ON test_results(test_status);

-- ============================================================================
-- DEVIATIONS
-- ============================================================================

CREATE TABLE deviations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_result_id UUID REFERENCES test_results(id) ON DELETE CASCADE,
    control_id UUID REFERENCES controls(id),

    deviation_description TEXT NOT NULL,
    root_cause TEXT,
    severity deviation_severity NOT NULL,

    -- Impact assessment
    impact_on_objective TEXT,
    impact_on_opinion TEXT,

    -- Remediation
    remediation_plan TEXT,
    remediation_owner UUID REFERENCES users(id),
    remediation_deadline DATE,
    remediation_completed_at TIMESTAMPTZ,

    -- Retesting
    retest_required BOOLEAN DEFAULT TRUE,
    retest_plan_id UUID REFERENCES test_plans(id),
    retest_passed BOOLEAN,

    identified_by UUID REFERENCES users(id),
    identified_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_deviations_test_result ON deviations(test_result_id);
CREATE INDEX idx_deviations_severity ON deviations(severity);

-- ============================================================================
-- MANAGEMENT ASSERTION
-- ============================================================================

CREATE TABLE management_assertions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,

    assertion_text TEXT NOT NULL,
    assertion_date DATE NOT NULL,

    -- Signatories
    signatory_name VARCHAR(255) NOT NULL,
    signatory_title VARCHAR(255) NOT NULL,
    signatory_signature_image TEXT,  -- Base64 or S3 path

    approved BOOLEAN DEFAULT FALSE,
    approved_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_management_assertions_engagement ON management_assertions(engagement_id);

-- ============================================================================
-- SYSTEM DESCRIPTION (SOC 2)
-- ============================================================================

CREATE TABLE system_descriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,

    -- SOC 2 Description Criteria (DC) 2018
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

    -- Complementary controls
    cuec_section TEXT,
    subservice_section TEXT,

    -- AI generation
    ai_generated BOOLEAN DEFAULT FALSE,
    ai_confidence_score DECIMAL(3,2),

    drafted_by UUID REFERENCES users(id),
    drafted_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_system_descriptions_engagement ON system_descriptions(engagement_id);

-- ============================================================================
-- REPORTS
-- ============================================================================

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,

    -- Report metadata
    report_title VARCHAR(500) NOT NULL,
    report_date DATE NOT NULL,
    report_version INTEGER DEFAULT 1,

    -- Content sections
    auditor_opinion TEXT,
    scope_section TEXT,
    control_objectives_section TEXT,
    tests_and_results_section TEXT,  -- Type 2 only
    management_assertion_section TEXT,
    system_description_section TEXT,
    other_information_section TEXT,

    -- Status
    is_draft BOOLEAN DEFAULT TRUE,
    is_signed BOOLEAN DEFAULT FALSE,
    is_released BOOLEAN DEFAULT FALSE,

    -- Distribution
    restricted_distribution BOOLEAN DEFAULT TRUE,
    watermark_text VARCHAR(500),

    -- Files
    pdf_path TEXT,
    docx_path TEXT,

    drafted_by UUID REFERENCES users(id),
    drafted_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reports_engagement ON reports(engagement_id);
CREATE INDEX idx_reports_signed ON reports(is_signed);

-- ============================================================================
-- SIGNATURES
-- ============================================================================

CREATE TABLE signatures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID REFERENCES reports(id) ON DELETE CASCADE,

    signer_id UUID REFERENCES users(id) NOT NULL,
    signer_role user_role NOT NULL,

    signature_date TIMESTAMPTZ DEFAULT NOW(),
    signature_image TEXT,  -- Base64 or S3 path
    digital_signature TEXT,  -- PKI signature

    -- Attestation
    attestation_text TEXT DEFAULT 'I have reviewed this report and, based on my knowledge, the information is accurate and complete in all material respects.',

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT only_partner_signs CHECK (signer_role = 'CPA_PARTNER')
);

CREATE INDEX idx_signatures_report ON signatures(report_id);
CREATE INDEX idx_signatures_signer ON signatures(signer_id);

-- ============================================================================
-- WORKFLOW MANAGEMENT
-- ============================================================================

CREATE TABLE workflow_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,

    task_title VARCHAR(500) NOT NULL,
    task_description TEXT,
    task_type VARCHAR(100),  -- planning, testing, review, reporting

    assigned_to UUID REFERENCES users(id),
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMPTZ DEFAULT NOW(),

    due_date DATE,
    priority VARCHAR(50) DEFAULT 'MEDIUM',  -- LOW, MEDIUM, HIGH, CRITICAL

    status VARCHAR(50) DEFAULT 'TODO',  -- TODO, IN_PROGRESS, BLOCKED, COMPLETED
    completed_at TIMESTAMPTZ,

    -- Dependencies
    depends_on UUID REFERENCES workflow_tasks(id),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_workflow_tasks_engagement ON workflow_tasks(engagement_id);
CREATE INDEX idx_workflow_tasks_assigned ON workflow_tasks(assigned_to);
CREATE INDEX idx_workflow_tasks_status ON workflow_tasks(status);

-- ============================================================================
-- APPROVALS
-- ============================================================================

CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,
    report_id UUID REFERENCES reports(id),

    approval_type VARCHAR(100) NOT NULL,  -- plan, test_results, report_draft, final_release
    approval_level INTEGER NOT NULL,  -- 1=Manager, 2=Partner

    approver_id UUID REFERENCES users(id) NOT NULL,
    approval_status approval_status DEFAULT 'PENDING',

    comments TEXT,

    approved_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    rejection_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_approvals_engagement ON approvals(engagement_id);
CREATE INDEX idx_approvals_approver ON approvals(approver_id);
CREATE INDEX idx_approvals_status ON approvals(approval_status);

-- ============================================================================
-- AUDIT TRAIL (Immutable Event Log)
-- ============================================================================

CREATE TABLE audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id),

    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,

    actor_id UUID REFERENCES users(id),
    actor_ip_address INET,

    action VARCHAR(100) NOT NULL,  -- CREATE, READ, UPDATE, DELETE, APPROVE, SIGN, RELEASE

    -- Event data
    before_state JSONB,
    after_state JSONB,

    -- Hash chain (immutability)
    event_hash VARCHAR(64) NOT NULL,
    previous_hash VARCHAR(64),

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_audit_trail_engagement ON audit_trail(engagement_id);
CREATE INDEX idx_audit_trail_entity ON audit_trail(entity_type, entity_id);
CREATE INDEX idx_audit_trail_actor ON audit_trail(actor_id);
CREATE INDEX idx_audit_trail_created ON audit_trail(created_at DESC);

-- Prevent updates/deletes (immutable)
CREATE OR REPLACE FUNCTION prevent_audit_trail_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit trail records are immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_update_audit_trail
    BEFORE UPDATE ON audit_trail
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_trail_modification();

CREATE TRIGGER no_delete_audit_trail
    BEFORE DELETE ON audit_trail
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_trail_modification();

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE soc_engagements ENABLE ROW LEVEL SECURITY;
ALTER TABLE controls ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access engagements they are team members of
CREATE POLICY engagement_team_policy ON soc_engagements
    USING (
        EXISTS (
            SELECT 1 FROM engagement_team
            WHERE engagement_team.engagement_id = soc_engagements.id
              AND engagement_team.user_id = current_setting('app.current_user_id')::UUID
              AND engagement_team.removed_at IS NULL
        )
    );

-- Apply similar RLS to related tables
CREATE POLICY controls_access_policy ON controls
    USING (
        EXISTS (
            SELECT 1 FROM engagement_team
            WHERE engagement_team.engagement_id = controls.engagement_id
              AND engagement_team.user_id = current_setting('app.current_user_id')::UUID
              AND engagement_team.removed_at IS NULL
        )
    );

CREATE POLICY test_results_access_policy ON test_results
    USING (
        EXISTS (
            SELECT 1 FROM test_plans
            JOIN engagement_team ON engagement_team.engagement_id = test_plans.engagement_id
            WHERE test_plans.id = test_results.test_plan_id
              AND engagement_team.user_id = current_setting('app.current_user_id')::UUID
              AND engagement_team.removed_at IS NULL
        )
    );

CREATE POLICY evidence_access_policy ON evidence
    USING (
        EXISTS (
            SELECT 1 FROM engagement_team
            WHERE engagement_team.engagement_id = evidence.engagement_id
              AND engagement_team.user_id = current_setting('app.current_user_id')::UUID
              AND engagement_team.removed_at IS NULL
        )
    );

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Hash chain for audit trail
CREATE OR REPLACE FUNCTION generate_audit_trail_hash()
RETURNS TRIGGER AS $$
DECLARE
    prev_hash VARCHAR(64);
BEGIN
    -- Get previous hash
    SELECT event_hash INTO prev_hash
    FROM audit_trail
    ORDER BY created_at DESC
    LIMIT 1;

    -- Generate new hash
    NEW.previous_hash := prev_hash;
    NEW.event_hash := encode(
        digest(
            CONCAT(
                NEW.id::TEXT,
                NEW.event_type,
                NEW.entity_type,
                NEW.entity_id::TEXT,
                NEW.action,
                COALESCE(prev_hash, ''),
                NEW.created_at::TEXT
            ),
            'sha256'
        ),
        'hex'
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_trail_hash_trigger
    BEFORE INSERT ON audit_trail
    FOR EACH ROW EXECUTE FUNCTION generate_audit_trail_hash();

-- Update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_soc_engagements_updated_at BEFORE UPDATE ON soc_engagements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_controls_updated_at BEFORE UPDATE ON controls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_test_plans_updated_at BEFORE UPDATE ON test_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_test_results_updated_at BEFORE UPDATE ON test_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_deviations_updated_at BEFORE UPDATE ON deviations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Full-text search on reports
CREATE INDEX idx_reports_fts ON reports USING gin(to_tsvector('english', auditor_opinion || ' ' || COALESCE(scope_section, '')));

-- Evidence lookup by hash (integrity verification)
CREATE UNIQUE INDEX idx_evidence_sha256_unique ON evidence(sha256_hash);

-- ============================================================================
-- COMMENTS (Documentation)
-- ============================================================================

COMMENT ON SCHEMA soc_copilot IS 'SOC 1 & SOC 2 audit platform schema per AT-C 320 and AICPA TSC 2017/2022';
COMMENT ON TABLE soc_engagements IS 'Top-level SOC 1/SOC 2 engagements (Type 1/Type 2)';
COMMENT ON TABLE control_objectives IS 'ICFR-relevant objectives (SOC 1) or TSC-mapped objectives (SOC 2)';
COMMENT ON TABLE cuec IS 'Complementary User Entity Controls per AT-C 320';
COMMENT ON TABLE csoc IS 'Complementary Subservice Organization Controls';
COMMENT ON TABLE audit_trail IS 'Immutable event log with SHA-256 hash chain';
COMMENT ON COLUMN evidence.sha256_hash IS 'SHA-256 hash for integrity verification and chain-of-custody';

-- ============================================================================
-- GRANTS (Adjust based on your application user)
-- ============================================================================

-- GRANT USAGE ON SCHEMA soc_copilot TO soc_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA soc_copilot TO soc_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA soc_copilot TO soc_app_user;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
