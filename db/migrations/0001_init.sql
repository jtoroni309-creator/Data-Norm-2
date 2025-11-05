-- ========================================
-- Aura Audit AI (Project Atlas)
-- Database Schema - Initial Migration
-- ========================================
-- PostgreSQL 15 with pgvector extension
-- Supports: PCAOB AS 1215, AICPA SAS 142/145, SEC 17 CFR 210.2-06
-- ========================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create schema
CREATE SCHEMA IF NOT EXISTS atlas;
SET search_path TO atlas, public;

-- ========================================
-- Core Engagement Management
-- ========================================

CREATE TYPE engagement_status AS ENUM ('draft', 'planning', 'fieldwork', 'review', 'finalized');
CREATE TYPE engagement_type AS ENUM ('audit', 'review', 'compilation', 'agreed_upon_procedures');
CREATE TYPE user_role AS ENUM ('partner', 'manager', 'senior', 'staff', 'qc_reviewer', 'client_contact');

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    tax_id TEXT,
    industry_code TEXT,  -- SIC code
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    role user_role NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    oidc_subject TEXT,  -- OIDC 'sub' claim
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_login_at TIMESTAMPTZ
);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_oidc_subject ON users(oidc_subject);
CREATE INDEX idx_users_organization ON users(organization_id);

CREATE TABLE engagements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    engagement_type engagement_type NOT NULL,
    status engagement_status NOT NULL DEFAULT 'draft',
    fiscal_year_end DATE NOT NULL,
    start_date DATE,
    expected_completion_date DATE,
    partner_id UUID REFERENCES users(id),
    manager_id UUID REFERENCES users(id),
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    locked_at TIMESTAMPTZ,
    locked_by UUID REFERENCES users(id)
);
CREATE INDEX idx_engagements_client ON engagements(client_id);
CREATE INDEX idx_engagements_status ON engagements(status);
CREATE INDEX idx_engagements_partner ON engagements(partner_id);

CREATE TABLE engagement_team_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    role user_role NOT NULL,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    assigned_by UUID REFERENCES users(id),
    UNIQUE(engagement_id, user_id)
);
CREATE INDEX idx_team_members_engagement ON engagement_team_members(engagement_id);
CREATE INDEX idx_team_members_user ON engagement_team_members(user_id);

-- ========================================
-- EDGAR / XBRL Ingestion
-- ========================================

CREATE TYPE filing_form AS ENUM ('10-K', '10-Q', '20-F', '40-F', '6-K', '8-K', 'DEF-14A', 'S-1', 'S-3');

CREATE TABLE filings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cik TEXT NOT NULL,
    ticker TEXT,
    company_name TEXT NOT NULL,
    form filing_form NOT NULL,
    filing_date DATE NOT NULL,
    accession_number TEXT NOT NULL UNIQUE,
    source_uri TEXT NOT NULL,
    fiscal_year INTEGER,
    fiscal_period TEXT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ingested_by UUID REFERENCES users(id)
);
CREATE INDEX idx_filings_cik ON filings(cik);
CREATE INDEX idx_filings_ticker ON filings(ticker);
CREATE INDEX idx_filings_form_date ON filings(form, filing_date DESC);
CREATE INDEX idx_filings_accession ON filings(accession_number);

CREATE TABLE facts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filing_id UUID NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    concept TEXT NOT NULL,  -- e.g., us-gaap:Assets
    taxonomy TEXT NOT NULL DEFAULT 'us-gaap',
    value NUMERIC,
    unit TEXT,  -- USD, shares, etc.
    start_date DATE,
    end_date DATE,
    instant_date DATE,
    context_ref TEXT,
    decimals INTEGER,
    metadata JSONB,  -- Additional XBRL attributes
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_facts_filing ON facts(filing_id);
CREATE INDEX idx_facts_concept ON facts(concept);
CREATE INDEX idx_facts_taxonomy_concept ON facts(taxonomy, concept);
CREATE INDEX idx_facts_instant_date ON facts(instant_date);
CREATE INDEX idx_facts_end_date ON facts(end_date);

-- ========================================
-- Trial Balance & Chart of Accounts
-- ========================================

CREATE TYPE account_type AS ENUM ('asset', 'liability', 'equity', 'revenue', 'expense');
CREATE TYPE account_subtype AS ENUM (
    'current_asset', 'non_current_asset', 'current_liability', 'long_term_liability',
    'stockholders_equity', 'operating_revenue', 'non_operating_revenue',
    'operating_expense', 'non_operating_expense', 'cogs'
);

CREATE TABLE chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    account_code TEXT NOT NULL,
    account_name TEXT NOT NULL,
    account_type account_type NOT NULL,
    account_subtype account_subtype,
    parent_account_id UUID REFERENCES chart_of_accounts(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(organization_id, account_code)
);
CREATE INDEX idx_coa_organization ON chart_of_accounts(organization_id);
CREATE INDEX idx_coa_account_code ON chart_of_accounts(account_code);
CREATE INDEX idx_coa_account_type ON chart_of_accounts(account_type);

CREATE TABLE trial_balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    period_end_date DATE NOT NULL,
    source TEXT NOT NULL,  -- 'manual', 'qbo', 'netsuite', etc.
    source_metadata JSONB,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    imported_by UUID REFERENCES users(id),
    UNIQUE(engagement_id, period_end_date, source)
);
CREATE INDEX idx_tb_engagement ON trial_balances(engagement_id);

CREATE TABLE trial_balance_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trial_balance_id UUID NOT NULL REFERENCES trial_balances(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    account_code TEXT NOT NULL,
    account_name TEXT NOT NULL,
    debit_amount NUMERIC(18, 2),
    credit_amount NUMERIC(18, 2),
    balance_amount NUMERIC(18, 2),
    mapped_account_id UUID REFERENCES chart_of_accounts(id),
    mapping_confidence NUMERIC(3, 2),  -- 0.00 to 1.00
    mapping_method TEXT,  -- 'manual', 'auto_exact', 'auto_ml'
    taxonomy_concept TEXT,  -- us-gaap:Cash, etc.
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_tb_lines_tb ON trial_balance_lines(trial_balance_id);
CREATE INDEX idx_tb_lines_mapped_account ON trial_balance_lines(mapped_account_id);

-- ========================================
-- Journal Entries
-- ========================================

CREATE TYPE je_source AS ENUM ('system', 'manual', 'import', 'integration');

CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    entry_number TEXT NOT NULL,
    entry_date DATE NOT NULL,
    posted_date DATE,
    source je_source NOT NULL,
    source_system TEXT,  -- 'qbo', 'netsuite', etc.
    description TEXT,
    created_by_user_id UUID REFERENCES users(id),
    created_by_username TEXT,  -- From source system
    is_manual BOOLEAN NOT NULL DEFAULT false,
    is_reversal BOOLEAN NOT NULL DEFAULT false,
    reverses_entry_id UUID REFERENCES journal_entries(id),
    metadata JSONB,  -- Additional attributes
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(engagement_id, entry_number)
);
CREATE INDEX idx_je_engagement ON journal_entries(engagement_id);
CREATE INDEX idx_je_entry_date ON journal_entries(entry_date);
CREATE INDEX idx_je_source ON journal_entries(source);
CREATE INDEX idx_je_is_manual ON journal_entries(is_manual);

CREATE TABLE journal_entry_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    account_code TEXT NOT NULL,
    account_name TEXT,
    debit_amount NUMERIC(18, 2),
    credit_amount NUMERIC(18, 2),
    description TEXT,
    dimension_values JSONB,  -- Departments, projects, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_je_lines_entry ON journal_entry_lines(journal_entry_id);
CREATE INDEX idx_je_lines_account ON journal_entry_lines(account_code);

-- ========================================
-- Analytics & Anomalies
-- ========================================

CREATE TYPE anomaly_severity AS ENUM ('info', 'low', 'medium', 'high', 'critical');

CREATE TABLE analytics_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_code TEXT NOT NULL UNIQUE,
    rule_name TEXT NOT NULL,
    description TEXT,
    category TEXT,  -- 'je_testing', 'ratio_analysis', 'outlier_detection'
    is_active BOOLEAN NOT NULL DEFAULT true,
    config JSONB,  -- Rule-specific parameters
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE analytics_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    rule_id UUID NOT NULL REFERENCES analytics_rules(id),
    executed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    executed_by UUID REFERENCES users(id),
    result_data JSONB NOT NULL,  -- Rule-specific results
    findings_count INTEGER NOT NULL DEFAULT 0,
    model_version TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_analytics_engagement ON analytics_results(engagement_id);
CREATE INDEX idx_analytics_rule ON analytics_results(rule_id);

CREATE TABLE anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    analytics_result_id UUID REFERENCES analytics_results(id),
    anomaly_type TEXT NOT NULL,  -- 'round_dollar_je', 'weekend_je', 'outlier_ratio', etc.
    severity anomaly_severity NOT NULL DEFAULT 'medium',
    title TEXT NOT NULL,
    description TEXT,
    evidence JSONB NOT NULL,  -- Links to JEs, TB lines, etc.
    score NUMERIC(5, 2),  -- Anomaly score or confidence
    resolution_status TEXT DEFAULT 'open',  -- 'open', 'reviewed', 'resolved', 'false_positive'
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_anomalies_engagement ON anomalies(engagement_id);
CREATE INDEX idx_anomalies_type ON anomalies(anomaly_type);
CREATE INDEX idx_anomalies_severity ON anomalies(severity);
CREATE INDEX idx_anomalies_status ON anomalies(resolution_status);

-- ========================================
-- Risk & Controls (SAS 145)
-- ========================================

CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high');
CREATE TYPE control_effectiveness AS ENUM ('not_tested', 'effective', 'deficiency', 'material_weakness');

CREATE TABLE risks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    risk_area TEXT NOT NULL,  -- 'revenue', 'inventory', 'payroll', etc.
    risk_description TEXT NOT NULL,
    inherent_risk risk_level NOT NULL,
    control_risk risk_level,
    residual_risk risk_level,
    fraud_risk BOOLEAN NOT NULL DEFAULT false,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_risks_engagement ON risks(engagement_id);
CREATE INDEX idx_risks_fraud ON risks(fraud_risk);

CREATE TABLE controls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    risk_id UUID REFERENCES risks(id),
    control_id TEXT NOT NULL,
    control_description TEXT NOT NULL,
    control_type TEXT,  -- 'preventive', 'detective'
    frequency TEXT,  -- 'daily', 'weekly', 'monthly', 'annual'
    effectiveness control_effectiveness DEFAULT 'not_tested',
    test_results TEXT,
    tested_by UUID REFERENCES users(id),
    tested_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_controls_engagement ON controls(engagement_id);
CREATE INDEX idx_controls_risk ON controls(risk_id);

CREATE TABLE procedures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    risk_id UUID REFERENCES risks(id),
    procedure_code TEXT NOT NULL,
    procedure_description TEXT NOT NULL,
    procedure_type TEXT,  -- 'substantive', 'control_test', 'analytical'
    assigned_to UUID REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'not_started',  -- 'not_started', 'in_progress', 'completed', 'reviewed'
    completed_by UUID REFERENCES users(id),
    completed_at TIMESTAMPTZ,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    conclusion TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_procedures_engagement ON procedures(engagement_id);
CREATE INDEX idx_procedures_risk ON procedures(risk_id);
CREATE INDEX idx_procedures_assigned ON procedures(assigned_to);
CREATE INDEX idx_procedures_status ON procedures(status);

-- ========================================
-- Binder & Workpapers
-- ========================================

CREATE TYPE binder_node_type AS ENUM ('folder', 'workpaper', 'evidence', 'note');
CREATE TYPE workpaper_status AS ENUM ('draft', 'prepared', 'reviewed', 'approved');

CREATE TABLE binder_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES binder_nodes(id) ON DELETE CASCADE,
    node_type binder_node_type NOT NULL,
    node_code TEXT,  -- e.g., 'A-100', 'B-200'
    title TEXT NOT NULL,
    description TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    status workpaper_status DEFAULT 'draft',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_binder_nodes_engagement ON binder_nodes(engagement_id);
CREATE INDEX idx_binder_nodes_parent ON binder_nodes(parent_id);
CREATE INDEX idx_binder_nodes_position ON binder_nodes(engagement_id, parent_id, position);

CREATE TABLE workpapers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    binder_node_id UUID NOT NULL REFERENCES binder_nodes(id) ON DELETE CASCADE,
    content JSONB,  -- Rich text / structured content
    prepared_by UUID REFERENCES users(id),
    prepared_at TIMESTAMPTZ,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_workpapers_node ON workpapers(binder_node_id);

CREATE TABLE evidence_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workpaper_id UUID REFERENCES workpapers(id) ON DELETE CASCADE,
    procedure_id UUID REFERENCES procedures(id),
    anomaly_id UUID REFERENCES anomalies(id),
    source_type TEXT NOT NULL,  -- 'file', 'url', 'tb_line', 'je', 'fact', 's3_object'
    source_reference TEXT NOT NULL,  -- ID, URI, or path
    description TEXT,
    file_hash TEXT,  -- SHA-256
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_evidence_workpaper ON evidence_links(workpaper_id);
CREATE INDEX idx_evidence_procedure ON evidence_links(procedure_id);
CREATE INDEX idx_evidence_hash ON evidence_links(file_hash);

CREATE TABLE review_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workpaper_id UUID REFERENCES workpapers(id) ON DELETE CASCADE,
    procedure_id UUID REFERENCES procedures(id),
    reviewer_id UUID NOT NULL REFERENCES users(id),
    note_text TEXT NOT NULL,
    is_blocking BOOLEAN NOT NULL DEFAULT false,
    status TEXT NOT NULL DEFAULT 'open',  -- 'open', 'addressed', 'cleared'
    addressed_by UUID REFERENCES users(id),
    addressed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_review_notes_workpaper ON review_notes(workpaper_id);
CREATE INDEX idx_review_notes_reviewer ON review_notes(reviewer_id);
CREATE INDEX idx_review_notes_status ON review_notes(status);

-- ========================================
-- Disclosures (LLM-Generated)
-- ========================================

CREATE TABLE note_drafts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    section TEXT NOT NULL,  -- 'summary_of_significant_policies', 'revenue_recognition', etc.
    json JSONB NOT NULL,  -- Structured disclosure content
    citations JSONB,  -- Array of source references
    confidence NUMERIC(3, 2),  -- 0.00 to 1.00
    contradictions JSONB,  -- Array of conflicting statements
    model_version TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    temperature NUMERIC(3, 2),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    generated_by UUID REFERENCES users(id),
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    approved BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_note_drafts_engagement ON note_drafts(engagement_id);
CREATE INDEX idx_note_drafts_section ON note_drafts(section);

-- ========================================
-- Binder Versioning & Immutability
-- ========================================

CREATE TABLE binder_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    snapshot_data JSONB NOT NULL,  -- Complete binder state
    content_hash TEXT NOT NULL,  -- SHA-256 of snapshot
    worm_uri TEXT,  -- S3 Object Lock / Azure Immutable URI
    is_final BOOLEAN NOT NULL DEFAULT false,
    locked_at TIMESTAMPTZ,
    locked_by UUID REFERENCES users(id),
    retention_until TIMESTAMPTZ,  -- 7 years from lock
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(engagement_id, version)
);
CREATE INDEX idx_binder_versions_engagement ON binder_versions(engagement_id);
CREATE INDEX idx_binder_versions_is_final ON binder_versions(is_final);
CREATE INDEX idx_binder_versions_hash ON binder_versions(content_hash);

-- ========================================
-- E-Signature & Reporting
-- ========================================

CREATE TYPE signature_type AS ENUM ('partner_approval', 'manager_review', 'qc_review', 'client_acceptance');

CREATE TABLE signatures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    binder_version_id UUID REFERENCES binder_versions(id),
    user_id UUID NOT NULL REFERENCES users(id),
    signature_type signature_type NOT NULL,
    signed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ip_address INET,
    device_fingerprint TEXT,
    certificate_fingerprint TEXT,  -- For PKI-based e-sign
    signature_data TEXT,  -- Base64-encoded signature or DocuSign envelope ID
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_signatures_engagement ON signatures(engagement_id);
CREATE INDEX idx_signatures_user ON signatures(user_id);
CREATE INDEX idx_signatures_binder_version ON signatures(binder_version_id);

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    report_type TEXT NOT NULL,  -- 'audit_report', 'review_report', 'compilation'
    report_date DATE NOT NULL,
    opinion TEXT,  -- 'unmodified', 'qualified', 'adverse', 'disclaimer'
    content JSONB,  -- Structured report content
    pdf_uri TEXT,  -- S3/Azure Blob URI
    pdf_hash TEXT,  -- SHA-256
    signed_by UUID REFERENCES users(id),
    signed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_reports_engagement ON reports(engagement_id);
CREATE INDEX idx_reports_type ON reports(report_type);

-- ========================================
-- QC & Policy Engine
-- ========================================

CREATE TYPE qc_check_status AS ENUM ('pending', 'passed', 'failed', 'waived');

CREATE TABLE qc_policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_code TEXT NOT NULL UNIQUE,
    policy_name TEXT NOT NULL,
    description TEXT,
    is_blocking BOOLEAN NOT NULL DEFAULT true,  -- Block binder lock if failed
    standard_reference TEXT,  -- 'PCAOB AS 1215', 'AICPA SAS 142', etc.
    check_logic JSONB NOT NULL,  -- Structured rules
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE qc_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    policy_id UUID NOT NULL REFERENCES qc_policies(id),
    executed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status qc_check_status NOT NULL DEFAULT 'pending',
    result_data JSONB,  -- Details of pass/fail
    waived_by UUID REFERENCES users(id),
    waived_at TIMESTAMPTZ,
    waiver_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_qc_checks_engagement ON qc_checks(engagement_id);
CREATE INDEX idx_qc_checks_policy ON qc_checks(policy_id);
CREATE INDEX idx_qc_checks_status ON qc_checks(status);

-- ========================================
-- ERP / Payroll Connectors
-- ========================================

CREATE TYPE connector_status AS ENUM ('disconnected', 'connected', 'error', 'syncing');

CREATE TABLE connector_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    engagement_id UUID REFERENCES engagements(id),
    vendor TEXT NOT NULL,  -- 'qbo', 'netsuite', 'xero', 'adp', etc.
    status connector_status NOT NULL DEFAULT 'disconnected',
    credentials_encrypted TEXT,  -- Encrypted OAuth tokens or API keys
    config JSONB,  -- Vendor-specific settings
    last_sync_at TIMESTAMPTZ,
    last_sync_status TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(organization_id, vendor)
);
CREATE INDEX idx_connectors_organization ON connector_integrations(organization_id);
CREATE INDEX idx_connectors_vendor ON connector_integrations(vendor);

CREATE TABLE connector_sync_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connector_id UUID NOT NULL REFERENCES connector_integrations(id) ON DELETE CASCADE,
    sync_type TEXT NOT NULL,  -- 'full', 'incremental', 'manual'
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'running',  -- 'running', 'completed', 'failed'
    records_synced INTEGER,
    error_message TEXT,
    metadata JSONB
);
CREATE INDEX idx_sync_jobs_connector ON connector_sync_jobs(connector_id);
CREATE INDEX idx_sync_jobs_started ON connector_sync_jobs(started_at DESC);

-- ========================================
-- Lineage & Audit Trail (OpenLineage)
-- ========================================

CREATE TYPE lineage_event_type AS ENUM ('create', 'update', 'delete', 'read', 'execute', 'lock', 'sign');

CREATE TABLE lineage_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type lineage_event_type NOT NULL,
    entity_type TEXT NOT NULL,  -- 'engagement', 'workpaper', 'binder_version', etc.
    entity_id UUID NOT NULL,
    user_id UUID REFERENCES users(id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    ip_address INET,
    user_agent TEXT,
    changes JSONB,  -- Before/after for updates
    metadata JSONB,  -- Job ID, run ID, dataset hashes, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_lineage_entity ON lineage_events(entity_type, entity_id);
CREATE INDEX idx_lineage_user ON lineage_events(user_id);
CREATE INDEX idx_lineage_timestamp ON lineage_events(timestamp DESC);

-- ========================================
-- ML Model & Prompt Registry
-- ========================================

CREATE TABLE model_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    model_type TEXT,  -- 'classification', 'regression', 'llm', 'embedding'
    training_data_description TEXT,
    training_date TIMESTAMPTZ,
    framework TEXT,  -- 'scikit-learn', 'pytorch', 'openai'
    metrics JSONB,  -- Accuracy, F1, RMSE, etc.
    artifacts_uri TEXT,  -- MLflow run URI
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(model_name, model_version)
);

CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_name TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    template TEXT NOT NULL,
    model_name TEXT,
    parameters JSONB,  -- temperature, max_tokens, etc.
    evaluation_metrics JSONB,  -- Hallucination rate, citation accuracy, etc.
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(prompt_name, prompt_version)
);

-- ========================================
-- RAG / Embeddings
-- ========================================

CREATE TABLE knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type TEXT NOT NULL,  -- 'taxonomy', 'standard', 'template', 'prior_year'
    source_id TEXT,
    chunk_text TEXT NOT NULL,
    chunk_number INTEGER,
    metadata JSONB,  -- Section, page, standard reference, etc.
    embedding vector(1536),  -- OpenAI text-embedding-3-large dimension
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_chunks_source ON knowledge_chunks(source_type, source_id);
CREATE INDEX idx_chunks_embedding ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops);

-- ========================================
-- Row-Level Security (RLS)
-- ========================================

-- Enable RLS on key tables
ALTER TABLE engagements ENABLE ROW LEVEL SECURITY;
ALTER TABLE engagement_team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE trial_balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE binder_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE workpapers ENABLE ROW LEVEL SECURITY;
ALTER TABLE procedures ENABLE ROW LEVEL SECURITY;
ALTER TABLE risks ENABLE ROW LEVEL SECURITY;
ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;
ALTER TABLE note_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE binder_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE signatures ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access engagements they are team members of
CREATE POLICY engagement_access_policy ON engagements
    FOR ALL
    USING (
        id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
        OR
        created_by = current_setting('app.current_user_id')::UUID
    );

-- Apply similar policies to child tables
CREATE POLICY team_members_access ON engagement_team_members
    FOR ALL
    USING (
        engagement_id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY trial_balances_access ON trial_balances
    FOR ALL
    USING (
        engagement_id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY journal_entries_access ON journal_entries
    FOR ALL
    USING (
        engagement_id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY binder_nodes_access ON binder_nodes
    FOR ALL
    USING (
        engagement_id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY workpapers_access ON workpapers
    FOR ALL
    USING (
        binder_node_id IN (
            SELECT id FROM binder_nodes
            WHERE engagement_id IN (
                SELECT engagement_id FROM engagement_team_members
                WHERE user_id = current_setting('app.current_user_id')::UUID
            )
        )
    );

CREATE POLICY procedures_access ON procedures
    FOR ALL
    USING (
        engagement_id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY risks_access ON risks
    FOR ALL
    USING (
        engagement_id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY anomalies_access ON anomalies
    FOR ALL
    USING (
        engagement_id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY note_drafts_access ON note_drafts
    FOR ALL
    USING (
        engagement_id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY binder_versions_access ON binder_versions
    FOR ALL
    USING (
        engagement_id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY signatures_access ON signatures
    FOR ALL
    USING (
        engagement_id IN (
            SELECT engagement_id FROM engagement_team_members
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- ========================================
-- Functions & Triggers
-- ========================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT table_name FROM information_schema.columns
        WHERE table_schema = 'atlas' AND column_name = 'updated_at'
    LOOP
        EXECUTE format('
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        ', t, t);
    END LOOP;
END $$;

-- Function to verify JE balancing (debits = credits)
CREATE OR REPLACE FUNCTION check_je_balanced()
RETURNS TRIGGER AS $$
DECLARE
    total_debits NUMERIC;
    total_credits NUMERIC;
BEGIN
    SELECT COALESCE(SUM(debit_amount), 0), COALESCE(SUM(credit_amount), 0)
    INTO total_debits, total_credits
    FROM journal_entry_lines
    WHERE journal_entry_id = NEW.journal_entry_id;

    IF ABS(total_debits - total_credits) > 0.01 THEN
        RAISE EXCEPTION 'Journal entry % is not balanced: debits=%, credits=%',
            NEW.journal_entry_id, total_debits, total_credits;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_je_lines_balanced
    AFTER INSERT OR UPDATE ON journal_entry_lines
    FOR EACH ROW EXECUTE FUNCTION check_je_balanced();

-- ========================================
-- Seed Data (Development Only)
-- ========================================

-- Insert default QC policies
INSERT INTO qc_policies (policy_code, policy_name, description, is_blocking, standard_reference, check_logic) VALUES
('AS1215_DOCUMENTATION', 'AS 1215 - Audit Documentation Complete', 'All audit procedures must have supporting workpapers', true, 'PCAOB AS 1215', '{"check": "procedures_have_workpapers"}'),
('SAS142_EVIDENCE', 'SAS 142 - Sufficient Appropriate Evidence', 'All significant accounts must have sufficient evidence', true, 'AICPA SAS 142', '{"check": "material_accounts_have_evidence"}'),
('SAS145_RISK_ASSESSMENT', 'SAS 145 - Risk Assessment Documentation', 'All identified risks must have linked procedures', true, 'AICPA SAS 145', '{"check": "risks_have_procedures"}'),
('PARTNER_SIGN_OFF', 'Partner Sign-Off Required', 'Partner must e-sign before binder lock', true, 'Firm Policy', '{"check": "partner_signature_exists"}'),
('QC_REVIEW_COMPLETE', 'QC Review Complete', 'QC reviewer must clear all blocking review notes', true, 'Firm Policy', '{"check": "no_open_blocking_notes"}');

-- Insert default analytics rules
INSERT INTO analytics_rules (rule_code, rule_name, description, category, config) VALUES
('JE_ROUND_DOLLAR', 'Round-Dollar Journal Entries', 'Flag JEs with round-dollar amounts (e.g., $10,000.00)', 'je_testing', '{"threshold": 1000}'),
('JE_WEEKEND', 'Weekend/Holiday Journal Entries', 'Flag JEs posted on weekends or holidays', 'je_testing', '{}'),
('JE_PERIOD_END_SPIKE', 'Period-End Journal Entry Spike', 'Flag unusual spikes in JE volume near period end', 'je_testing', '{"days_before_period_end": 3}'),
('RATIO_CURRENT', 'Current Ratio Analysis', 'Calculate current ratio and compare to prior year', 'ratio_analysis', '{"warning_threshold": 0.2}'),
('RATIO_QUICK', 'Quick Ratio Analysis', 'Calculate quick ratio and compare to prior year', 'ratio_analysis', '{"warning_threshold": 0.2}');

-- Create Airflow database (separate from atlas)
CREATE DATABASE airflow OWNER atlas;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE atlas TO atlas;
GRANT ALL PRIVILEGES ON DATABASE airflow TO atlas;
GRANT ALL PRIVILEGES ON SCHEMA atlas TO atlas;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA atlas TO atlas;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA atlas TO atlas;

COMMENT ON SCHEMA atlas IS 'Aura Audit AI (Project Atlas) - Enterprise Audit Platform Schema';
