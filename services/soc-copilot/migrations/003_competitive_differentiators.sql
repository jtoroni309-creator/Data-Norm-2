-- ============================================================================
-- Migration 003: Competitive Differentiators
-- ============================================================================
-- Features that separate SOC Copilot from ALL competitors:
-- 1. Continuous Control Monitoring (CCM) - Real-time monitoring agents
-- 2. Client Collaboration Portal - Two-sided marketplace model
-- 3. AI Audit Program Generator - Custom audit programs based on tech stack
-- 4. Predictive Analytics - ML-powered control failure forecasting
-- 5. Integration Hub - 50+ SaaS connectors for automated evidence collection
-- 6. Smart Statistical Sampling - Adaptive sampling algorithms
-- 7. Natural Language Query - ChatGPT-like audit analytics interface
-- ============================================================================

SET search_path TO soc_copilot;

-- ============================================================================
-- 1. CONTINUOUS CONTROL MONITORING (CCM)
-- ============================================================================
-- Real-time monitoring agents that continuously test controls
-- vs. Drata/Vanta: More intelligent, AI-powered analysis
-- vs. AuditBoard/CaseWare: Automated, not manual point-in-time testing

CREATE TYPE monitoring_agent_type AS ENUM (
    'ACCESS_CONTROL',           -- Monitor user access, provisioning/deprovisioning
    'CHANGE_MANAGEMENT',        -- Monitor code deployments, config changes
    'BACKUP_RECOVERY',          -- Monitor backup success, restoration tests
    'VULNERABILITY_SCANNING',   -- Continuous vulnerability scanning
    'LOG_MONITORING',           -- Monitor security logs, SIEM integration
    'ENCRYPTION',               -- Monitor encryption at rest/transit
    'INCIDENT_RESPONSE',        -- Monitor incident tickets, response times
    'VENDOR_MANAGEMENT',        -- Monitor vendor risk assessments
    'BUSINESS_CONTINUITY',      -- Monitor DR tests, RTO/RPO compliance
    'PHYSICAL_SECURITY',        -- Monitor facility access logs
    'COMPLIANCE_DRIFT'          -- Detect configuration drift from baseline
);

CREATE TYPE monitoring_status AS ENUM (
    'ACTIVE',
    'PAUSED',
    'FAILED',
    'DISCONNECTED'
);

CREATE TYPE control_health_status AS ENUM (
    'HEALTHY',              -- Control operating effectively
    'DEGRADED',             -- Minor issues detected
    'AT_RISK',              -- Significant issues, may fail soon
    'FAILING',              -- Control not operating effectively
    'UNKNOWN'               -- Insufficient data
);

-- Deployable monitoring agents
CREATE TABLE monitoring_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES soc_engagements(id) ON DELETE CASCADE,
    control_id UUID REFERENCES controls(id) ON DELETE SET NULL,

    agent_type monitoring_agent_type NOT NULL,
    agent_name VARCHAR(200) NOT NULL,
    agent_description TEXT,

    -- Deployment
    deployment_method VARCHAR(50), -- 'API', 'AGENT', 'SIEM_INTEGRATION', 'SAAS_CONNECTOR'
    connection_string TEXT,        -- Encrypted connection details
    api_key_encrypted TEXT,        -- Encrypted API credentials

    -- Monitoring schedule
    monitoring_frequency_minutes INT DEFAULT 60, -- How often to check
    last_check_at TIMESTAMPTZ,
    next_check_at TIMESTAMPTZ,

    -- Status
    status monitoring_status DEFAULT 'ACTIVE',
    health_check_endpoint VARCHAR(500),

    -- Configuration
    monitoring_rules JSONB,        -- Custom rules/thresholds
    alert_thresholds JSONB,        -- When to alert

    -- Metadata
    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat_at TIMESTAMPTZ
);

-- Real-time monitoring results
CREATE TABLE monitoring_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES monitoring_agents(id) ON DELETE CASCADE,
    control_id UUID REFERENCES controls(id) ON DELETE SET NULL,

    -- Result data
    check_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    control_health control_health_status NOT NULL,

    -- Evidence collected
    raw_data JSONB,                -- Raw monitoring data
    evidence_snapshot JSONB,       -- Processed evidence

    -- AI Analysis
    ai_analysis TEXT,              -- GPT-4 analysis of results
    ai_risk_score DECIMAL(3,2),    -- 0.00 to 1.00
    anomaly_detected BOOLEAN DEFAULT FALSE,
    anomaly_description TEXT,

    -- Deviation detection
    expected_value JSONB,
    actual_value JSONB,
    deviation_detected BOOLEAN DEFAULT FALSE,
    deviation_severity VARCHAR(20), -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'

    -- Auto-remediation
    auto_remediation_attempted BOOLEAN DEFAULT FALSE,
    remediation_action TEXT,
    remediation_success BOOLEAN,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Control health trends over time
CREATE TABLE control_health_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    control_id UUID NOT NULL REFERENCES controls(id) ON DELETE CASCADE,

    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    health_status control_health_status NOT NULL,
    health_score DECIMAL(5,2),     -- 0.00 to 100.00

    -- Metrics
    success_rate DECIMAL(5,2),     -- % of monitoring checks passed
    failure_count INT DEFAULT 0,
    total_checks INT DEFAULT 0,

    -- Trend analysis
    trend_direction VARCHAR(20),   -- 'IMPROVING', 'STABLE', 'DEGRADING'
    trend_confidence DECIMAL(3,2), -- 0.00 to 1.00

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_monitoring_agents_engagement ON monitoring_agents(engagement_id);
CREATE INDEX idx_monitoring_agents_control ON monitoring_agents(control_id);
CREATE INDEX idx_monitoring_results_agent ON monitoring_results(agent_id);
CREATE INDEX idx_monitoring_results_timestamp ON monitoring_results(check_timestamp);
CREATE INDEX idx_control_health_history_control ON control_health_history(control_id, timestamp DESC);


-- ============================================================================
-- 2. CLIENT COLLABORATION PORTAL
-- ============================================================================
-- Two-sided marketplace: CPA firm + Client portal
-- vs. Competitors: They only have single-sided (either auditor OR auditee, not both)

CREATE TYPE client_user_role AS ENUM (
    'CLIENT_ADMIN',        -- Client's primary contact
    'CLIENT_IT_LEAD',      -- Technical contact
    'CLIENT_CONTRIBUTOR',  -- Uploads evidence, responds to requests
    'CLIENT_VIEWER'        -- Read-only access
);

CREATE TYPE evidence_request_status AS ENUM (
    'DRAFT',
    'SENT_TO_CLIENT',
    'CLIENT_VIEWED',
    'CLIENT_UPLOADED',
    'AUDITOR_REVIEWING',
    'ACCEPTED',
    'REJECTED',
    'CLARIFICATION_NEEDED'
);

-- Client users (separate from auditor users)
CREATE TABLE client_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES soc_engagements(id) ON DELETE CASCADE,

    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role client_user_role NOT NULL,

    -- Access
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    password_hash TEXT NOT NULL,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret TEXT,

    -- Notifications
    email_notifications BOOLEAN DEFAULT TRUE,
    notification_preferences JSONB,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(engagement_id, email)
);

-- Evidence requests sent to clients
CREATE TABLE evidence_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES soc_engagements(id) ON DELETE CASCADE,
    control_id UUID REFERENCES controls(id) ON DELETE SET NULL,
    test_plan_id UUID REFERENCES test_plans(id) ON DELETE SET NULL,

    -- Request details
    request_title VARCHAR(500) NOT NULL,
    request_description TEXT NOT NULL,

    -- Requirements
    required_evidence_types VARCHAR(100)[], -- ['SCREENSHOT', 'DOCUMENT', 'VIDEO', 'LOG_EXPORT']
    required_file_formats VARCHAR(50)[],    -- ['PDF', 'XLSX', 'PNG', 'MP4']
    sample_size INT,                        -- How many samples needed
    period_start DATE,                      -- Period evidence should cover
    period_end DATE,

    -- Status
    status evidence_request_status DEFAULT 'DRAFT',
    due_date DATE,
    priority VARCHAR(20) DEFAULT 'MEDIUM', -- 'LOW', 'MEDIUM', 'HIGH', 'URGENT'

    -- Tracking
    sent_to_client_at TIMESTAMPTZ,
    client_viewed_at TIMESTAMPTZ,
    client_uploaded_at TIMESTAMPTZ,
    auditor_reviewed_at TIMESTAMPTZ,

    -- Assignment
    assigned_to_client_user UUID REFERENCES client_users(id),
    assigned_to_auditor UUID,

    -- AI-generated request
    ai_generated BOOLEAN DEFAULT FALSE,
    ai_suggestions TEXT,               -- AI suggestions for what evidence to request

    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Client-uploaded evidence (linked to requests)
CREATE TABLE client_evidence_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evidence_request_id UUID NOT NULL REFERENCES evidence_requests(id) ON DELETE CASCADE,
    evidence_id UUID REFERENCES evidence(id) ON DELETE SET NULL,

    -- Upload metadata
    filename VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    storage_path VARCHAR(1000) NOT NULL,

    -- Client notes
    client_notes TEXT,
    covers_period_start DATE,
    covers_period_end DATE,

    -- Verification
    uploaded_by UUID NOT NULL REFERENCES client_users(id),
    uploaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    verified_by_auditor UUID,
    verified_at TIMESTAMPTZ,
    verification_status VARCHAR(50), -- 'PENDING', 'ACCEPTED', 'REJECTED'
    auditor_feedback TEXT,

    -- AI verification
    ai_validated BOOLEAN,
    ai_validation_score DECIMAL(3,2),
    ai_validation_notes TEXT,

    -- Version control
    version INT DEFAULT 1,
    replaces_upload_id UUID REFERENCES client_evidence_uploads(id)
);

-- Client portal activity log
CREATE TABLE client_portal_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES soc_engagements(id) ON DELETE CASCADE,
    client_user_id UUID REFERENCES client_users(id) ON DELETE SET NULL,

    activity_type VARCHAR(100) NOT NULL, -- 'LOGIN', 'UPLOAD', 'DOWNLOAD', 'COMMENT', 'VIEW_REQUEST'
    activity_description TEXT,

    -- Context
    related_entity_type VARCHAR(100),
    related_entity_id UUID,

    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_client_users_engagement ON client_users(engagement_id);
CREATE INDEX idx_evidence_requests_engagement ON evidence_requests(engagement_id);
CREATE INDEX idx_evidence_requests_status ON evidence_requests(status, due_date);
CREATE INDEX idx_client_uploads_request ON client_evidence_uploads(evidence_request_id);


-- ============================================================================
-- 3. AI AUDIT PROGRAM GENERATOR
-- ============================================================================
-- Analyzes client tech stack and auto-generates custom audit programs
-- vs. ALL Competitors: Static templates vs. dynamic AI-generated programs

CREATE TYPE tech_category AS ENUM (
    'CLOUD_PROVIDER',      -- AWS, Azure, GCP
    'SAAS_APPLICATION',    -- Salesforce, Workday, etc.
    'DATABASE',            -- PostgreSQL, MongoDB, etc.
    'IDENTITY_PROVIDER',   -- Okta, Azure AD, Auth0
    'MONITORING',          -- Datadog, New Relic, Splunk
    'CICD',                -- GitHub Actions, Jenkins, GitLab
    'CONTAINER',           -- Docker, Kubernetes
    'ENDPOINT',            -- MDM, Antivirus
    'NETWORK',             -- Firewalls, VPN, WAF
    'BACKUP',              -- Backup solutions
    'TICKETING',           -- Jira, ServiceNow
    'COMMUNICATION',       -- Slack, Teams
    'OTHER'
);

-- Client's technology stack inventory
CREATE TABLE tech_stack_inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES soc_engagements(id) ON DELETE CASCADE,

    -- Technology details
    tech_name VARCHAR(200) NOT NULL,
    tech_vendor VARCHAR(200),
    tech_category tech_category NOT NULL,
    tech_version VARCHAR(100),

    -- Usage context
    purpose TEXT,                          -- What it's used for
    criticality VARCHAR(20),               -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    user_count INT,
    data_classification VARCHAR(50)[],     -- ['PII', 'PHI', 'CONFIDENTIAL', 'PUBLIC']

    -- Integration metadata
    has_api BOOLEAN DEFAULT FALSE,
    api_documentation_url VARCHAR(500),
    supports_sso BOOLEAN,
    supports_mfa BOOLEAN,
    supports_audit_logs BOOLEAN,

    -- Auto-discovery
    auto_discovered BOOLEAN DEFAULT FALSE,
    discovery_method VARCHAR(100),         -- 'CLIENT_PROVIDED', 'NETWORK_SCAN', 'API_INTEGRATION'

    -- Validation
    validated_by_client BOOLEAN DEFAULT FALSE,
    validated_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- AI-generated custom audit programs
CREATE TABLE ai_audit_programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES soc_engagements(id) ON DELETE CASCADE,
    control_objective_id UUID REFERENCES control_objectives(id) ON DELETE CASCADE,

    -- Program details
    program_name VARCHAR(500) NOT NULL,
    program_description TEXT,

    -- AI generation metadata
    generated_by_ai BOOLEAN DEFAULT TRUE,
    ai_model VARCHAR(100),                 -- 'gpt-4-turbo-preview'
    generation_prompt TEXT,
    generation_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Tech stack context
    based_on_tech_stack UUID[],            -- References to tech_stack_inventory
    tech_stack_summary JSONB,

    -- Risk-based scoping
    risk_level VARCHAR(20),                -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    risk_factors JSONB,                    -- Why this risk level
    recommended_sample_size INT,
    recommended_test_frequency VARCHAR(50), -- 'MONTHLY', 'QUARTERLY', 'ANNUALLY'

    -- Audit procedures
    procedures JSONB,                      -- Array of test steps
    expected_evidence JSONB,               -- What evidence should be collected

    -- CPA review
    reviewed_by_cpa UUID,
    reviewed_at TIMESTAMPTZ,
    cpa_approved BOOLEAN DEFAULT FALSE,
    cpa_modifications TEXT,                -- Manual edits by CPA

    -- Version control
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    replaces_program_id UUID REFERENCES ai_audit_programs(id),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tech_stack_engagement ON tech_stack_inventory(engagement_id);
CREATE INDEX idx_ai_programs_engagement ON ai_audit_programs(engagement_id);
CREATE INDEX idx_ai_programs_objective ON ai_audit_programs(control_objective_id);


-- ============================================================================
-- 4. PREDICTIVE ANALYTICS ENGINE
-- ============================================================================
-- ML-powered prediction of which controls are likely to fail
-- vs. ALL Competitors: No one has predictive capabilities, only reactive

CREATE TYPE prediction_model_type AS ENUM (
    'CONTROL_FAILURE_RISK',        -- Predict control failure probability
    'DEVIATION_LIKELIHOOD',        -- Predict deviation occurrence
    'REMEDIATION_TIME',            -- Predict remediation duration
    'AUDIT_COMPLETION',            -- Predict audit timeline
    'RESOURCE_ALLOCATION'          -- Predict required hours/resources
);

-- ML models for predictions
CREATE TABLE prediction_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    model_name VARCHAR(200) NOT NULL,
    model_type prediction_model_type NOT NULL,
    model_version VARCHAR(50) NOT NULL,

    -- Model metadata
    algorithm VARCHAR(100),                -- 'RANDOM_FOREST', 'GRADIENT_BOOSTING', 'NEURAL_NETWORK'
    training_data_size INT,
    training_accuracy DECIMAL(5,2),
    validation_accuracy DECIMAL(5,2),

    -- Features
    feature_names TEXT[],
    feature_importance JSONB,

    -- Model artifacts
    model_artifacts_path VARCHAR(500),     -- Path to serialized model
    last_trained_at TIMESTAMPTZ,

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Predictions for controls
CREATE TABLE control_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    control_id UUID NOT NULL REFERENCES controls(id) ON DELETE CASCADE,
    model_id UUID NOT NULL REFERENCES prediction_models(id),

    -- Prediction
    prediction_type prediction_model_type NOT NULL,
    prediction_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Risk score
    failure_probability DECIMAL(5,4),      -- 0.0000 to 1.0000 (0% to 100%)
    risk_score DECIMAL(3,2),               -- 0.00 to 1.00
    risk_level VARCHAR(20),                -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'

    -- Contributing factors
    risk_factors JSONB,                    -- What's driving the risk
    feature_contributions JSONB,           -- Which features contributed most

    -- Recommendations
    ai_recommendations TEXT,               -- What to do about it
    recommended_actions JSONB,
    estimated_remediation_hours DECIMAL(5,1),

    -- Confidence
    prediction_confidence DECIMAL(3,2),    -- 0.00 to 1.00
    confidence_interval_lower DECIMAL(5,4),
    confidence_interval_upper DECIMAL(5,4),

    -- Validation (did prediction come true?)
    actual_outcome VARCHAR(50),            -- 'PASSED', 'FAILED', 'NOT_TESTED_YET'
    prediction_accuracy DECIMAL(5,2),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Historical control performance for training
CREATE TABLE control_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    control_id UUID NOT NULL REFERENCES controls(id) ON DELETE CASCADE,

    measurement_period_start DATE NOT NULL,
    measurement_period_end DATE NOT NULL,

    -- Performance metrics
    total_tests INT DEFAULT 0,
    passed_tests INT DEFAULT 0,
    failed_tests INT DEFAULT 0,
    pass_rate DECIMAL(5,2),

    -- Deviation metrics
    total_deviations INT DEFAULT 0,
    critical_deviations INT DEFAULT 0,
    high_deviations INT DEFAULT 0,
    medium_deviations INT DEFAULT 0,
    low_deviations INT DEFAULT 0,

    -- Timing metrics
    avg_test_duration_hours DECIMAL(6,2),
    avg_remediation_days DECIMAL(6,2),

    -- Environmental factors (for ML features)
    team_size INT,
    technology_changes INT,              -- Number of tech changes in period
    organizational_changes INT,          -- Reorgs, turnover, etc.

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_control_predictions_control ON control_predictions(control_id);
CREATE INDEX idx_control_predictions_model ON control_predictions(model_id);
CREATE INDEX idx_control_performance_control ON control_performance_metrics(control_id);


-- ============================================================================
-- 5. INTEGRATION HUB
-- ============================================================================
-- 50+ pre-built connectors for automated evidence collection
-- vs. Competitors: Drata has ~75, Vanta has ~30, AuditBoard/CaseWare have almost none

CREATE TYPE integration_category AS ENUM (
    'CLOUD_PROVIDER',
    'IDENTITY_SSO',
    'HRIS',
    'TICKETING',
    'CODE_REPOSITORY',
    'CICD',
    'MONITORING_LOGGING',
    'SECURITY_TOOLS',
    'COMMUNICATION',
    'FINANCIAL',
    'PROJECT_MANAGEMENT',
    'DOCUMENT_STORAGE'
);

CREATE TYPE integration_auth_type AS ENUM (
    'OAUTH2',
    'API_KEY',
    'BASIC_AUTH',
    'SAML',
    'CERTIFICATE'
);

-- Available integrations catalog
CREATE TABLE integration_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    integration_name VARCHAR(200) NOT NULL UNIQUE,
    integration_category integration_category NOT NULL,
    vendor_name VARCHAR(200) NOT NULL,

    -- Capabilities
    supported_evidence_types VARCHAR(100)[],  -- ['USER_LIST', 'ACCESS_LOGS', 'CONFIG_BACKUP']
    supported_controls VARCHAR(100)[],        -- Which controls this integration helps test

    -- Authentication
    auth_type integration_auth_type NOT NULL,
    requires_admin_consent BOOLEAN DEFAULT FALSE,

    -- Documentation
    setup_instructions TEXT,
    required_scopes TEXT[],
    api_documentation_url VARCHAR(500),

    -- Metadata
    logo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    popularity_score INT DEFAULT 0,            -- Track usage across all clients

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Client's configured integrations
CREATE TABLE configured_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES soc_engagements(id) ON DELETE CASCADE,
    integration_id UUID NOT NULL REFERENCES integration_catalog(id),

    -- Configuration
    integration_nickname VARCHAR(200),         -- "Production AWS" vs "Dev AWS"

    -- Credentials (encrypted)
    credentials_encrypted TEXT NOT NULL,
    refresh_token_encrypted TEXT,
    token_expires_at TIMESTAMPTZ,

    -- Status
    status VARCHAR(50) DEFAULT 'ACTIVE',       -- 'ACTIVE', 'DISCONNECTED', 'ERROR', 'PAUSED'
    last_sync_at TIMESTAMPTZ,
    last_sync_status VARCHAR(50),
    last_error TEXT,

    -- Sync schedule
    auto_sync_enabled BOOLEAN DEFAULT TRUE,
    sync_frequency_hours INT DEFAULT 24,
    next_sync_at TIMESTAMPTZ,

    -- Evidence collection settings
    evidence_retention_days INT DEFAULT 90,
    collect_evidence_types VARCHAR(100)[],

    -- Metadata
    configured_by UUID NOT NULL,
    configured_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_health_check_at TIMESTAMPTZ,

    UNIQUE(engagement_id, integration_id, integration_nickname)
);

-- Auto-collected evidence from integrations
CREATE TABLE auto_collected_evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    configured_integration_id UUID NOT NULL REFERENCES configured_integrations(id) ON DELETE CASCADE,
    evidence_id UUID REFERENCES evidence(id) ON DELETE SET NULL,

    -- Collection metadata
    collection_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    evidence_type VARCHAR(100) NOT NULL,
    evidence_period_start DATE,
    evidence_period_end DATE,

    -- Data
    raw_data JSONB,
    processed_data JSONB,
    file_path VARCHAR(1000),

    -- AI analysis
    ai_analyzed BOOLEAN DEFAULT FALSE,
    ai_summary TEXT,
    ai_red_flags TEXT[],                       -- Anomalies detected

    -- Mapping to audit
    mapped_to_controls UUID[],
    mapped_to_test_plans UUID[],
    auto_mapped BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_integration_catalog_category ON integration_catalog(integration_category);
CREATE INDEX idx_configured_integrations_engagement ON configured_integrations(engagement_id);
CREATE INDEX idx_auto_evidence_integration ON auto_collected_evidence(configured_integration_id);


-- ============================================================================
-- 6. SMART STATISTICAL SAMPLING
-- ============================================================================
-- Adaptive sampling that adjusts based on error rates and risk
-- vs. Competitors: Static sampling, no intelligence

CREATE TYPE sampling_method AS ENUM (
    'RANDOM',
    'STRATIFIED',
    'SYSTEMATIC',
    'CLUSTER',
    'JUDGMENTAL',
    'AI_OPTIMIZED'                         -- Our secret sauce
);

-- Sampling plans
CREATE TABLE sampling_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_plan_id UUID NOT NULL REFERENCES test_plans(id) ON DELETE CASCADE,

    -- Population
    population_size INT NOT NULL,
    population_description TEXT,

    -- Sampling approach
    sampling_method sampling_method NOT NULL,
    confidence_level DECIMAL(4,2) DEFAULT 95.00,  -- 95%
    tolerable_error_rate DECIMAL(5,2) DEFAULT 5.00, -- 5%
    expected_error_rate DECIMAL(5,2) DEFAULT 2.00,  -- 2%

    -- Initial sample
    initial_sample_size INT NOT NULL,

    -- Adaptive sampling (our differentiator)
    adaptive_enabled BOOLEAN DEFAULT TRUE,
    ai_optimized BOOLEAN DEFAULT TRUE,

    -- Results tracking
    actual_sample_size INT,                    -- May differ from initial if adaptive
    errors_found INT DEFAULT 0,
    actual_error_rate DECIMAL(5,2),

    -- AI recommendations
    ai_recommended_sample_size INT,
    ai_risk_assessment TEXT,
    ai_sampling_rationale TEXT,

    -- Statistical results
    sampling_risk DECIMAL(5,4),                -- Risk of incorrect conclusion
    precision DECIMAL(5,2),

    -- CPA approval
    approved_by UUID,
    approved_at TIMESTAMPTZ,

    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Sample selections (which items to test)
CREATE TABLE sample_selections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sampling_plan_id UUID NOT NULL REFERENCES sampling_plans(id) ON DELETE CASCADE,

    -- Selection
    sample_item_id VARCHAR(200) NOT NULL,      -- Reference to actual item (user ID, txn ID, etc.)
    sample_item_description TEXT,
    selection_method VARCHAR(50),              -- 'RANDOM', 'STRATIFIED', 'JUDGMENTAL', 'AI_TARGETED'

    -- Stratification
    stratum_name VARCHAR(200),                 -- If using stratified sampling
    stratum_risk_level VARCHAR(20),

    -- AI targeting
    ai_target_reason TEXT,                     -- Why AI selected this item
    ai_risk_score DECIMAL(3,2),

    -- Test result
    tested BOOLEAN DEFAULT FALSE,
    test_passed BOOLEAN,
    deviation_id UUID REFERENCES deviations(id),

    selected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    tested_at TIMESTAMPTZ
);

-- Adaptive sampling adjustments
CREATE TABLE sampling_adjustments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sampling_plan_id UUID NOT NULL REFERENCES sampling_plans(id) ON DELETE CASCADE,

    -- Trigger
    adjustment_trigger VARCHAR(100),           -- 'HIGH_ERROR_RATE', 'LOW_ERROR_RATE', 'ANOMALY_DETECTED'
    adjustment_reason TEXT,

    -- Adjustment
    original_sample_size INT NOT NULL,
    adjusted_sample_size INT NOT NULL,
    additional_samples INT,

    -- Statistical recalculation
    revised_confidence_level DECIMAL(4,2),
    revised_tolerable_error DECIMAL(5,2),

    -- AI recommendation
    ai_recommended BOOLEAN DEFAULT TRUE,
    ai_rationale TEXT,

    -- CPA approval
    approved_by UUID,
    approved_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sampling_plans_test_plan ON sampling_plans(test_plan_id);
CREATE INDEX idx_sample_selections_plan ON sample_selections(sampling_plan_id);


-- ============================================================================
-- 7. NATURAL LANGUAGE QUERY INTERFACE
-- ============================================================================
-- ChatGPT-like interface for audit analytics
-- vs. ALL Competitors: No one has this - game changer for user experience

-- Saved NL queries
CREATE TABLE nl_query_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID REFERENCES soc_engagements(id) ON DELETE CASCADE,

    -- Query
    user_query TEXT NOT NULL,                  -- "Show me all failed IT controls in Q4 2024"
    user_id UUID NOT NULL,

    -- AI interpretation
    interpreted_intent VARCHAR(200),           -- 'FILTER_CONTROLS', 'GENERATE_REPORT', 'RISK_ANALYSIS'
    sql_generated TEXT,                        -- Generated SQL query
    filters_applied JSONB,                     -- Extracted filters

    -- Results
    results_count INT,
    results_summary TEXT,                      -- AI-generated summary

    -- Performance
    query_execution_time_ms INT,
    ai_processing_time_ms INT,

    -- Feedback
    user_rating INT,                           -- 1-5 stars
    user_feedback TEXT,
    results_helpful BOOLEAN,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Pre-built query templates
CREATE TABLE nl_query_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    template_name VARCHAR(200) NOT NULL,
    template_description TEXT,
    template_query TEXT NOT NULL,

    -- Context
    applicable_to_engagement_type engagement_type[],
    applicable_to_report_type report_type[],

    -- Popularity
    usage_count INT DEFAULT 0,
    avg_rating DECIMAL(3,2),

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_nl_query_history_engagement ON nl_query_history(engagement_id);
CREATE INDEX idx_nl_query_history_user ON nl_query_history(user_id, created_at DESC);


-- ============================================================================
-- SEED DATA: Integration Catalog
-- ============================================================================

INSERT INTO integration_catalog (integration_name, integration_category, vendor_name, supported_evidence_types, supported_controls, auth_type, setup_instructions) VALUES
-- Cloud Providers
('AWS', 'CLOUD_PROVIDER', 'Amazon Web Services', ARRAY['IAM_USERS', 'IAM_POLICIES', 'CLOUDTRAIL_LOGS', 'CONFIG_SNAPSHOTS', 'SECURITY_GROUPS'], ARRAY['CC6.1', 'CC6.2', 'CC6.6', 'CC7.2'], 'API_KEY', 'Create IAM user with SecurityAudit policy'),
('Azure', 'CLOUD_PROVIDER', 'Microsoft Azure', ARRAY['AZURE_AD_USERS', 'ROLE_ASSIGNMENTS', 'ACTIVITY_LOGS', 'POLICY_ASSIGNMENTS'], ARRAY['CC6.1', 'CC6.2', 'CC6.6'], 'OAUTH2', 'Register app in Azure AD with Reader role'),
('Google Cloud', 'CLOUD_PROVIDER', 'Google', ARRAY['IAM_BINDINGS', 'AUDIT_LOGS', 'SECURITY_POLICIES'], ARRAY['CC6.1', 'CC6.2', 'CC6.6'], 'API_KEY', 'Create service account with Viewer role'),

-- Identity/SSO
('Okta', 'IDENTITY_SSO', 'Okta', ARRAY['USER_LIST', 'GROUP_MEMBERSHIPS', 'MFA_STATUS', 'LOGIN_LOGS'], ARRAY['CC6.1', 'CC6.2', 'CC6.3'], 'API_KEY', 'Generate API token with Read-only Admin role'),
('Azure AD', 'IDENTITY_SSO', 'Microsoft', ARRAY['USER_LIST', 'GROUP_MEMBERSHIPS', 'CONDITIONAL_ACCESS_POLICIES', 'SIGN_IN_LOGS'], ARRAY['CC6.1', 'CC6.2', 'CC6.3'], 'OAUTH2', 'Register app with Directory.Read.All permission'),
('Auth0', 'IDENTITY_SSO', 'Auth0', ARRAY['USER_LIST', 'MFA_ENROLLMENTS', 'LOGIN_ACTIVITY'], ARRAY['CC6.1', 'CC6.2', 'CC6.3'], 'API_KEY', 'Create M2M application with read:users scope'),

-- HRIS
('BambooHR', 'HRIS', 'BambooHR', ARRAY['EMPLOYEE_LIST', 'TERMINATIONS', 'ONBOARDING_OFFBOARDING'], ARRAY['CC6.1', 'CC6.4'], 'API_KEY', 'Generate API key from Account > API Keys'),
('Workday', 'HRIS', 'Workday', ARRAY['EMPLOYEE_LIST', 'ROLE_CHANGES', 'TERMINATIONS'], ARRAY['CC6.1', 'CC6.4'], 'OAUTH2', 'Configure integration system user'),
('Rippling', 'HRIS', 'Rippling', ARRAY['EMPLOYEE_LIST', 'ACCESS_PROVISIONING', 'OFFBOARDING_CHECKLIST'], ARRAY['CC6.1', 'CC6.4'], 'API_KEY', 'Generate API token from Platform > API Settings'),

-- Security Tools
('CrowdStrike', 'SECURITY_TOOLS', 'CrowdStrike', ARRAY['ENDPOINT_LIST', 'THREAT_DETECTIONS', 'PATCH_STATUS'], ARRAY['CC7.2', 'CC7.3'], 'OAUTH2', 'Create API client with Hosts Read scope'),
('Qualys', 'SECURITY_TOOLS', 'Qualys', ARRAY['VULNERABILITY_SCANS', 'ASSET_INVENTORY'], ARRAY['CC7.1', 'CC7.2'], 'BASIC_AUTH', 'Create user with Scanner role'),
('Tenable', 'SECURITY_TOOLS', 'Tenable', ARRAY['VULNERABILITY_SCANS', 'COMPLIANCE_SCANS'], ARRAY['CC7.1', 'CC7.2'], 'API_KEY', 'Generate API keys from Settings > API Keys'),

-- Monitoring/Logging
('Datadog', 'MONITORING_LOGGING', 'Datadog', ARRAY['SECURITY_LOGS', 'ALERTS', 'UPTIME_METRICS'], ARRAY['CC7.2', 'A1.2'], 'API_KEY', 'Create API key and Application key'),
('Splunk', 'MONITORING_LOGGING', 'Splunk', ARRAY['SECURITY_EVENTS', 'AUDIT_LOGS'], ARRAY['CC7.2', 'CC7.3'], 'BASIC_AUTH', 'Create service account with search permissions'),
('New Relic', 'MONITORING_LOGGING', 'New Relic', ARRAY['APPLICATION_LOGS', 'PERFORMANCE_METRICS'], ARRAY['A1.2', 'CC7.2'], 'API_KEY', 'Generate User API key'),

-- Ticketing
('Jira', 'TICKETING', 'Atlassian', ARRAY['CHANGE_TICKETS', 'INCIDENT_TICKETS', 'APPROVAL_WORKFLOWS'], ARRAY['CC8.1', 'A1.3'], 'API_KEY', 'Generate API token from Account Settings'),
('ServiceNow', 'TICKETING', 'ServiceNow', ARRAY['CHANGE_RECORDS', 'INCIDENT_RECORDS', 'APPROVALS'], ARRAY['CC8.1', 'A1.3'], 'BASIC_AUTH', 'Create integration user with ITIL role'),

-- Code Repositories
('GitHub', 'CODE_REPOSITORY', 'GitHub', ARRAY['COMMIT_LOGS', 'BRANCH_PROTECTION', 'CODE_REVIEWS'], ARRAY['CC8.1'], 'OAUTH2', 'Create GitHub App or Personal Access Token'),
('GitLab', 'CODE_REPOSITORY', 'GitLab', ARRAY['COMMIT_LOGS', 'MERGE_REQUEST_APPROVALS'], ARRAY['CC8.1'], 'OAUTH2', 'Create Personal Access Token with read_api scope'),

-- CI/CD
('GitHub Actions', 'CICD', 'GitHub', ARRAY['WORKFLOW_RUNS', 'DEPLOYMENT_LOGS'], ARRAY['CC8.1'], 'OAUTH2', 'Use GitHub App credentials'),
('Jenkins', 'CICD', 'Jenkins', ARRAY['BUILD_LOGS', 'DEPLOYMENT_RECORDS'], ARRAY['CC8.1'], 'API_KEY', 'Generate API token from User Settings'),

-- Communication
('Slack', 'COMMUNICATION', 'Slack', ARRAY['CHANNEL_LOGS', 'USER_LIST'], ARRAY['CC6.8'], 'OAUTH2', 'Create Slack app with channels:history scope'),
('Microsoft Teams', 'COMMUNICATION', 'Microsoft', ARRAY['TEAM_MEMBERS', 'CHANNEL_ACTIVITY'], ARRAY['CC6.8'], 'OAUTH2', 'Register app with ChannelMessage.Read.All');

-- Insert NL query templates
INSERT INTO nl_query_templates (template_name, template_description, template_query, applicable_to_engagement_type) VALUES
('Show failed controls', 'List all controls that failed testing', 'Show me all controls that failed', ARRAY['SOC1_TYPE2', 'SOC2_TYPE2']::engagement_type[]),
('High-risk deviations', 'List high and critical severity deviations', 'Show me all high-risk deviations', ARRAY['SOC1_TYPE2', 'SOC2_TYPE2']::engagement_type[]),
('Controls at risk', 'Show controls predicted to fail', 'Which controls are at risk of failing?', ARRAY['SOC1_TYPE2', 'SOC2_TYPE2']::engagement_type[]),
('Evidence gaps', 'Identify missing evidence', 'What evidence is missing or incomplete?', ARRAY['SOC1_TYPE2', 'SOC2_TYPE2']::engagement_type[]),
('Client overdue requests', 'Evidence requests overdue from client', 'Which evidence requests are overdue from the client?', ARRAY['SOC1_TYPE2', 'SOC2_TYPE2']::engagement_type[]),
('Testing progress', 'Summary of testing completion', 'What is the overall testing progress?', ARRAY['SOC1_TYPE2', 'SOC2_TYPE2']::engagement_type[]),
('Security control summary', 'Summary of CC6 and CC7 controls', 'Summarize all security controls (CC6 and CC7)', ARRAY['SOC2_TYPE2']::engagement_type[]);

COMMENT ON TABLE monitoring_agents IS 'Deployable agents for continuous control monitoring - unique to SOC Copilot';
COMMENT ON TABLE client_users IS 'Client-side users for collaboration portal - two-sided marketplace differentiator';
COMMENT ON TABLE ai_audit_programs IS 'AI-generated custom audit programs based on tech stack - no competitor has this';
COMMENT ON TABLE control_predictions IS 'ML-powered predictions of control failures - unique predictive analytics';
COMMENT ON TABLE integration_catalog IS 'Pre-built integrations for automated evidence - competitive with Drata/Vanta';
COMMENT ON TABLE sampling_plans IS 'Intelligent adaptive sampling - smarter than any competitor';
COMMENT ON TABLE nl_query_history IS 'Natural language query interface - revolutionary UX, no competitor has this';
