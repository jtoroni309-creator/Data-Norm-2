-- ========================================
-- Aura Audit AI (Project Atlas)
-- Regulation A/B Audit for CMBS Loans
-- Migration 0002
-- ========================================
-- Adds Regulation A/B audit functionality for CMBS loan audits
-- Supports: PCAOB, GAAP, GAAS, SEC, AICPA compliance
-- ========================================

SET search_path TO atlas, public;

-- ========================================
-- Enums
-- ========================================

CREATE TYPE reg_ab_audit_status AS ENUM (
    'draft',
    'client_input',
    'ai_processing',
    'workpaper_generation',
    'cpa_review',
    'revision_required',
    'cpa_approved',
    'finalized'
);

CREATE TYPE cmbs_deal_status AS ENUM (
    'active',
    'inactive',
    'pending_audit',
    'audit_complete'
);

CREATE TYPE workpaper_status AS ENUM (
    'draft',
    'ai_generated',
    'in_review',
    'revision_required',
    'approved'
);

CREATE TYPE compliance_standard AS ENUM (
    'PCAOB',
    'GAAP',
    'GAAS',
    'SEC',
    'AICPA'
);

CREATE TYPE compliance_check_status AS ENUM (
    'pending',
    'passed',
    'failed',
    'warning',
    'manual_review_required'
);

CREATE TYPE signoff_status AS ENUM (
    'pending',
    'approved',
    'rejected',
    'revoked'
);

-- ========================================
-- Feature Flag for Reg A/B Audit
-- ========================================

CREATE TABLE reg_ab_feature_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Feature toggles
    is_enabled BOOLEAN NOT NULL DEFAULT false,
    allow_client_portal BOOLEAN NOT NULL DEFAULT true,
    allow_cpa_portal BOOLEAN NOT NULL DEFAULT true,
    auto_workpaper_generation BOOLEAN NOT NULL DEFAULT true,
    auto_report_generation BOOLEAN NOT NULL DEFAULT true,
    ai_compliance_checking BOOLEAN NOT NULL DEFAULT true,

    -- AI Configuration
    ai_model_version TEXT DEFAULT 'gpt-4-turbo',
    compliance_check_level TEXT DEFAULT 'comprehensive', -- basic, standard, comprehensive

    -- Notification settings
    notify_on_completion BOOLEAN NOT NULL DEFAULT true,
    notify_cpa_on_ready BOOLEAN NOT NULL DEFAULT true,
    notify_client_on_approval BOOLEAN NOT NULL DEFAULT true,
    notification_email TEXT,

    -- Audit settings
    require_dual_signoff BOOLEAN NOT NULL DEFAULT false,
    retention_years INTEGER NOT NULL DEFAULT 7,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    enabled_at TIMESTAMPTZ,
    enabled_by UUID REFERENCES users(id),

    UNIQUE(organization_id)
);

CREATE INDEX idx_reg_ab_flags_org ON reg_ab_feature_flags(organization_id);
CREATE INDEX idx_reg_ab_flags_enabled ON reg_ab_feature_flags(is_enabled);

-- ========================================
-- Regulation A/B Audit Engagements
-- ========================================

CREATE TABLE reg_ab_audit_engagements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id),

    -- Engagement details
    audit_name TEXT NOT NULL,
    audit_period_start DATE NOT NULL,
    audit_period_end DATE NOT NULL,
    status reg_ab_audit_status NOT NULL DEFAULT 'draft',

    -- Client information
    client_contact_id UUID REFERENCES users(id),
    client_organization_id UUID NOT NULL REFERENCES organizations(id),

    -- CPA assignment
    assigned_cpa_id UUID REFERENCES users(id),
    secondary_reviewer_id UUID REFERENCES users(id), -- For dual signoff

    -- AI processing metadata
    ai_processing_started_at TIMESTAMPTZ,
    ai_processing_completed_at TIMESTAMPTZ,
    ai_processing_duration_seconds INTEGER,
    ai_confidence_score DECIMAL(5,4), -- 0.0000 to 1.0000

    -- Progress tracking
    total_cmbs_deals INTEGER DEFAULT 0,
    processed_deals INTEGER DEFAULT 0,
    total_workpapers INTEGER DEFAULT 0,
    approved_workpapers INTEGER DEFAULT 0,
    total_compliance_checks INTEGER DEFAULT 0,
    passed_compliance_checks INTEGER DEFAULT 0,
    failed_compliance_checks INTEGER DEFAULT 0,

    -- Report information
    report_generated_at TIMESTAMPTZ,
    report_url TEXT,
    report_hash TEXT, -- SHA-256 for immutability

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    submitted_for_review_at TIMESTAMPTZ,
    reviewed_at TIMESTAMPTZ,
    finalized_at TIMESTAMPTZ,

    -- Soft delete
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_reg_ab_engagements_org ON reg_ab_audit_engagements(organization_id);
CREATE INDEX idx_reg_ab_engagements_status ON reg_ab_audit_engagements(status);
CREATE INDEX idx_reg_ab_engagements_cpa ON reg_ab_audit_engagements(assigned_cpa_id);
CREATE INDEX idx_reg_ab_engagements_client ON reg_ab_audit_engagements(client_organization_id);
CREATE INDEX idx_reg_ab_engagements_deleted ON reg_ab_audit_engagements(deleted_at) WHERE deleted_at IS NULL;

-- ========================================
-- CMBS Deals (Client Input)
-- ========================================

CREATE TABLE cmbs_deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_engagement_id UUID NOT NULL REFERENCES reg_ab_audit_engagements(id) ON DELETE CASCADE,

    -- Deal identification
    deal_name TEXT NOT NULL,
    deal_number TEXT NOT NULL,
    cusip TEXT,
    bloomberg_id TEXT,

    -- Deal details
    origination_date DATE NOT NULL,
    maturity_date DATE,
    original_balance DECIMAL(20,2) NOT NULL,
    current_balance DECIMAL(20,2) NOT NULL,
    interest_rate DECIMAL(7,4),

    -- Operating Advisor (OA) information
    is_oa BOOLEAN NOT NULL DEFAULT true, -- Is client the OA for this deal
    oa_appointment_date DATE,

    -- Property information
    property_type TEXT,
    property_address JSONB,
    property_count INTEGER,

    -- Servicer information
    master_servicer TEXT,
    special_servicer TEXT,
    trustee TEXT,

    -- Performance metrics
    dscr DECIMAL(7,4), -- Debt Service Coverage Ratio
    ltv DECIMAL(7,4),  -- Loan-to-Value
    occupancy_rate DECIMAL(5,2),
    delinquency_status TEXT,

    -- Additional data
    status cmbs_deal_status NOT NULL DEFAULT 'pending_audit',
    metadata JSONB,
    documents JSONB, -- Array of document references

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    submitted_at TIMESTAMPTZ,
    submitted_by UUID REFERENCES users(id),

    UNIQUE(audit_engagement_id, deal_number)
);

CREATE INDEX idx_cmbs_deals_engagement ON cmbs_deals(audit_engagement_id);
CREATE INDEX idx_cmbs_deals_status ON cmbs_deals(status);
CREATE INDEX idx_cmbs_deals_cusip ON cmbs_deals(cusip);
CREATE INDEX idx_cmbs_deals_submitted ON cmbs_deals(submitted_at);

-- ========================================
-- AI Compliance Checks
-- ========================================

CREATE TABLE compliance_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_engagement_id UUID NOT NULL REFERENCES reg_ab_audit_engagements(id) ON DELETE CASCADE,
    cmbs_deal_id UUID REFERENCES cmbs_deals(id) ON DELETE CASCADE,

    -- Check details
    check_name TEXT NOT NULL,
    check_code TEXT NOT NULL, -- e.g., 'PCAOB_AS_1215_DOC'
    standard compliance_standard NOT NULL,
    standard_reference TEXT NOT NULL, -- e.g., 'PCAOB AS 1215', 'SEC Reg AB'
    description TEXT NOT NULL,

    -- Check execution
    status compliance_check_status NOT NULL DEFAULT 'pending',
    executed_at TIMESTAMPTZ,
    execution_duration_ms INTEGER,

    -- AI analysis
    ai_analysis JSONB, -- Detailed AI reasoning
    ai_confidence DECIMAL(5,4),
    risk_level TEXT, -- low, medium, high, critical

    -- Results
    passed BOOLEAN,
    findings TEXT,
    recommendation TEXT,
    remediation_steps JSONB,

    -- Evidence
    evidence_references JSONB, -- References to workpapers, documents
    data_points_analyzed JSONB,

    -- Manual review
    requires_manual_review BOOLEAN DEFAULT false,
    manual_review_notes TEXT,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_compliance_checks_engagement ON compliance_checks(audit_engagement_id);
CREATE INDEX idx_compliance_checks_deal ON compliance_checks(cmbs_deal_id);
CREATE INDEX idx_compliance_checks_standard ON compliance_checks(standard);
CREATE INDEX idx_compliance_checks_status ON compliance_checks(status);
CREATE INDEX idx_compliance_checks_failed ON compliance_checks(status) WHERE status = 'failed';

-- ========================================
-- AI-Generated Workpapers
-- ========================================

CREATE TABLE reg_ab_workpapers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_engagement_id UUID NOT NULL REFERENCES reg_ab_audit_engagements(id) ON DELETE CASCADE,
    cmbs_deal_id UUID REFERENCES cmbs_deals(id) ON DELETE SET NULL,

    -- Workpaper details
    workpaper_ref TEXT NOT NULL, -- e.g., 'WP-A-1', 'WP-B-2.1'
    title TEXT NOT NULL,
    category TEXT NOT NULL, -- e.g., 'Cash Flow Analysis', 'Property Valuation'
    description TEXT,

    -- Content
    content JSONB NOT NULL, -- Structured workpaper content
    content_html TEXT, -- Rendered HTML version
    content_url TEXT, -- S3/MinIO URL for PDF version

    -- Status
    status workpaper_status NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1,

    -- AI generation metadata
    ai_generated BOOLEAN NOT NULL DEFAULT false,
    ai_model_version TEXT,
    ai_prompt_used TEXT,
    ai_generation_confidence DECIMAL(5,4),
    ai_generation_timestamp TIMESTAMPTZ,

    -- CPA review
    reviewer_id UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,
    revision_count INTEGER DEFAULT 0,

    -- Compliance linkage
    compliance_checks JSONB, -- Array of related compliance check IDs

    -- Supporting documents
    source_documents JSONB,
    attachments JSONB,

    -- Audit trail
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),

    -- Immutability
    locked BOOLEAN DEFAULT false,
    locked_at TIMESTAMPTZ,
    content_hash TEXT, -- SHA-256 hash for version control

    UNIQUE(audit_engagement_id, workpaper_ref, version)
);

CREATE INDEX idx_workpapers_engagement ON reg_ab_workpapers(audit_engagement_id);
CREATE INDEX idx_workpapers_deal ON reg_ab_workpapers(cmbs_deal_id);
CREATE INDEX idx_workpapers_status ON reg_ab_workpapers(status);
CREATE INDEX idx_workpapers_reviewer ON reg_ab_workpapers(reviewer_id);
CREATE INDEX idx_workpapers_ref ON reg_ab_workpapers(workpaper_ref);

-- ========================================
-- Audit Reports
-- ========================================

CREATE TABLE reg_ab_audit_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_engagement_id UUID NOT NULL REFERENCES reg_ab_audit_engagements(id) ON DELETE CASCADE,

    -- Report details
    report_type TEXT NOT NULL DEFAULT 'Regulation AB Compilation Report',
    report_period_start DATE NOT NULL,
    report_period_end DATE NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,

    -- Content
    executive_summary TEXT,
    findings_summary JSONB,
    content JSONB NOT NULL,
    content_html TEXT,
    content_pdf_url TEXT,

    -- Statistics
    total_deals_audited INTEGER NOT NULL,
    total_compliance_checks INTEGER NOT NULL,
    passed_checks INTEGER NOT NULL,
    failed_checks INTEGER NOT NULL,
    total_workpapers INTEGER NOT NULL,

    -- AI generation
    ai_generated BOOLEAN NOT NULL DEFAULT false,
    ai_model_version TEXT,
    ai_generation_timestamp TIMESTAMPTZ,
    ai_confidence_score DECIMAL(5,4),

    -- Status
    draft BOOLEAN NOT NULL DEFAULT true,

    -- Timestamps
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Immutability
    content_hash TEXT, -- SHA-256 for version control

    UNIQUE(audit_engagement_id, version)
);

CREATE INDEX idx_reports_engagement ON reg_ab_audit_reports(audit_engagement_id);
CREATE INDEX idx_reports_draft ON reg_ab_audit_reports(draft);

-- ========================================
-- CPA Sign-Off & Approval Workflow
-- ========================================

CREATE TABLE cpa_signoffs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_engagement_id UUID NOT NULL REFERENCES reg_ab_audit_engagements(id) ON DELETE CASCADE,
    report_id UUID NOT NULL REFERENCES reg_ab_audit_reports(id) ON DELETE CASCADE,

    -- CPA information
    cpa_user_id UUID NOT NULL REFERENCES users(id),
    cpa_license_number TEXT NOT NULL,
    cpa_license_state TEXT NOT NULL,
    cpa_license_expiry DATE,

    -- Sign-off details
    status signoff_status NOT NULL DEFAULT 'pending',
    signoff_type TEXT NOT NULL DEFAULT 'final_approval', -- draft_review, final_approval

    -- Digital signature
    signature_timestamp TIMESTAMPTZ,
    signature_ip_address INET,
    signature_method TEXT DEFAULT 'electronic', -- electronic, manual, esign_integration
    signature_certificate TEXT, -- For PKI-based signatures
    signature_hash TEXT, -- Hash of signed content

    -- Review details
    review_started_at TIMESTAMPTZ,
    review_completed_at TIMESTAMPTZ,
    review_duration_minutes INTEGER,
    review_notes TEXT,

    -- Approval/Rejection
    approved_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    rejection_reason TEXT,
    revision_requests JSONB,

    -- Revocation (if needed)
    revoked_at TIMESTAMPTZ,
    revoked_by UUID REFERENCES users(id),
    revocation_reason TEXT,

    -- Compliance attestation
    attestation_text TEXT,
    attestation_confirmed BOOLEAN DEFAULT false,
    attestation_timestamp TIMESTAMPTZ,

    -- Audit trail
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_signoffs_engagement ON cpa_signoffs(audit_engagement_id);
CREATE INDEX idx_signoffs_report ON cpa_signoffs(report_id);
CREATE INDEX idx_signoffs_cpa ON cpa_signoffs(cpa_user_id);
CREATE INDEX idx_signoffs_status ON cpa_signoffs(status);
CREATE INDEX idx_signoffs_approved ON cpa_signoffs(approved_at);

-- ========================================
-- Audit Trail & Activity Log
-- ========================================

CREATE TABLE reg_ab_audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_engagement_id UUID NOT NULL REFERENCES reg_ab_audit_engagements(id) ON DELETE CASCADE,

    -- Action details
    action_type TEXT NOT NULL, -- e.g., 'deal_submitted', 'ai_processing_started', 'cpa_review_requested'
    action_description TEXT NOT NULL,
    entity_type TEXT, -- e.g., 'cmbs_deal', 'workpaper', 'report', 'signoff'
    entity_id UUID,

    -- User information
    user_id UUID REFERENCES users(id),
    user_email TEXT,
    user_role user_role,

    -- Request metadata
    ip_address INET,
    user_agent TEXT,

    -- Data changes
    changes_before JSONB,
    changes_after JSONB,

    -- Timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_trail_engagement ON reg_ab_audit_trail(audit_engagement_id);
CREATE INDEX idx_audit_trail_user ON reg_ab_audit_trail(user_id);
CREATE INDEX idx_audit_trail_action ON reg_ab_audit_trail(action_type);
CREATE INDEX idx_audit_trail_created ON reg_ab_audit_trail(created_at DESC);

-- ========================================
-- Compliance Rules Library (AI Knowledge Base)
-- ========================================

CREATE TABLE compliance_rules_library (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Rule identification
    rule_code TEXT NOT NULL UNIQUE,
    rule_name TEXT NOT NULL,
    standard compliance_standard NOT NULL,
    standard_reference TEXT NOT NULL,

    -- Rule details
    description TEXT NOT NULL,
    requirements TEXT NOT NULL,
    testing_procedures TEXT NOT NULL,

    -- AI prompts
    ai_prompt_template TEXT NOT NULL,
    ai_analysis_instructions TEXT,

    -- Risk assessment
    risk_category TEXT, -- low, medium, high, critical
    mandatory BOOLEAN NOT NULL DEFAULT true,

    -- Evidence requirements
    required_evidence JSONB,
    acceptable_thresholds JSONB,

    -- Active status
    is_active BOOLEAN NOT NULL DEFAULT true,
    effective_date DATE,
    superseded_date DATE,
    superseded_by UUID REFERENCES compliance_rules_library(id),

    -- Version control
    version INTEGER NOT NULL DEFAULT 1,
    version_notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_compliance_rules_standard ON compliance_rules_library(standard);
CREATE INDEX idx_compliance_rules_code ON compliance_rules_library(rule_code);
CREATE INDEX idx_compliance_rules_active ON compliance_rules_library(is_active) WHERE is_active = true;

-- ========================================
-- Views for Reporting
-- ========================================

CREATE VIEW reg_ab_engagement_summary AS
SELECT
    e.id,
    e.audit_name,
    e.status,
    e.audit_period_start,
    e.audit_period_end,
    o.name as organization_name,
    co.name as client_organization_name,
    u.full_name as assigned_cpa_name,
    e.total_cmbs_deals,
    e.processed_deals,
    e.total_workpapers,
    e.approved_workpapers,
    e.total_compliance_checks,
    e.passed_compliance_checks,
    e.failed_compliance_checks,
    ROUND((e.processed_deals::NUMERIC / NULLIF(e.total_cmbs_deals, 0)) * 100, 2) as completion_percentage,
    ROUND((e.approved_workpapers::NUMERIC / NULLIF(e.total_workpapers, 0)) * 100, 2) as approval_percentage,
    ROUND((e.passed_compliance_checks::NUMERIC / NULLIF(e.total_compliance_checks, 0)) * 100, 2) as compliance_pass_rate,
    e.created_at,
    e.submitted_for_review_at,
    e.reviewed_at,
    e.finalized_at
FROM reg_ab_audit_engagements e
LEFT JOIN organizations o ON e.organization_id = o.id
LEFT JOIN organizations co ON e.client_organization_id = co.id
LEFT JOIN users u ON e.assigned_cpa_id = u.id
WHERE e.deleted_at IS NULL;

CREATE VIEW cmbs_deals_summary AS
SELECT
    cd.id,
    cd.deal_name,
    cd.deal_number,
    cd.cusip,
    cd.original_balance,
    cd.current_balance,
    cd.interest_rate,
    cd.dscr,
    cd.ltv,
    cd.status,
    e.audit_name,
    e.status as audit_status,
    COUNT(cc.id) as total_compliance_checks,
    COUNT(CASE WHEN cc.status = 'passed' THEN 1 END) as passed_checks,
    COUNT(CASE WHEN cc.status = 'failed' THEN 1 END) as failed_checks,
    COUNT(w.id) as total_workpapers,
    COUNT(CASE WHEN w.status = 'approved' THEN 1 END) as approved_workpapers
FROM cmbs_deals cd
LEFT JOIN reg_ab_audit_engagements e ON cd.audit_engagement_id = e.id
LEFT JOIN compliance_checks cc ON cd.id = cc.cmbs_deal_id
LEFT JOIN reg_ab_workpapers w ON cd.id = w.cmbs_deal_id
GROUP BY cd.id, cd.deal_name, cd.deal_number, cd.cusip, cd.original_balance,
         cd.current_balance, cd.interest_rate, cd.dscr, cd.ltv, cd.status,
         e.audit_name, e.status;

-- ========================================
-- Seed Data: Compliance Rules Library
-- ========================================

-- PCAOB Standards
INSERT INTO compliance_rules_library (rule_code, rule_name, standard, standard_reference, description, requirements, testing_procedures, ai_prompt_template, risk_category, mandatory) VALUES
('PCAOB_AS_1215', 'Audit Documentation', 'PCAOB', 'AS 1215', 'Requires complete and accurate audit documentation', 'All audit procedures must be documented with sufficient detail to enable an experienced auditor to understand the nature, timing, extent, and results of procedures performed', 'Review workpapers for completeness, clarity, and support for audit conclusions', 'Analyze the audit workpapers for CMBS deal {deal_name}. Verify that documentation meets PCAOB AS 1215 requirements for completeness, accuracy, and support for conclusions. Provide detailed assessment.', 'critical', true),
('PCAOB_AS_2401', 'Consideration of Fraud', 'PCAOB', 'AS 2401', 'Requires consideration of fraud in a financial statement audit', 'Auditor must assess risks of material misstatement due to fraud and respond appropriately', 'Evaluate fraud risk factors, assess management override controls, and test high-risk transactions', 'Assess fraud risk for CMBS deal {deal_name} considering property type, performance metrics, and servicer information. Identify red flags and recommend testing procedures.', 'high', true),
('PCAOB_AS_1105', 'Audit Evidence', 'PCAOB', 'AS 1105', 'Establishes requirements for audit evidence', 'Auditor must obtain sufficient appropriate audit evidence to provide a reasonable basis for the audit opinion', 'Evaluate the sufficiency and appropriateness of evidence obtained for each significant assertion', 'Review evidence collected for CMBS deal {deal_name}. Assess whether evidence is sufficient and appropriate per PCAOB AS 1105. Identify any gaps.', 'critical', true);

-- GAAP Standards
INSERT INTO compliance_rules_library (rule_code, rule_name, standard, standard_reference, description, requirements, testing_procedures, ai_prompt_template, risk_category, mandatory) VALUES
('GAAP_ASC_860', 'Transfers and Servicing', 'GAAP', 'ASC 860', 'Accounting for transfers and servicing of financial assets', 'Proper recognition and measurement of transferred financial assets and servicing rights', 'Verify proper accounting for loan transfers, servicing rights valuation, and disclosure completeness', 'Analyze CMBS deal {deal_name} for compliance with ASC 860. Review transfer documentation, servicer arrangements, and financial statement presentation.', 'high', true),
('GAAP_ASC_820', 'Fair Value Measurement', 'GAAP', 'ASC 820', 'Defines fair value and establishes framework for measurement', 'Fair value measurements must use appropriate valuation techniques and inputs', 'Test fair value calculations, validate Level 1/2/3 inputs, review valuation methodologies', 'Evaluate fair value measurements for CMBS deal {deal_name} properties. Assess compliance with ASC 820 fair value hierarchy and disclosure requirements.', 'high', true),
('GAAP_ASC_310', 'Receivables - Loan Impairment', 'GAAP', 'ASC 310', 'Accounting for loan impairment', 'Properly identify and measure impaired loans', 'Test loan impairment calculations, review DSCR and LTV metrics, validate allowance adequacy', 'Assess CMBS deal {deal_name} for loan impairment under ASC 310. Analyze DSCR of {dscr}, LTV of {ltv}, and delinquency status. Determine if impairment exists.', 'high', true);

-- SEC Regulation AB
INSERT INTO compliance_rules_library (rule_code, rule_name, standard, standard_reference, description, requirements, testing_procedures, ai_prompt_template, risk_category, mandatory) VALUES
('SEC_REG_AB_1100', 'Reg AB General Disclosure', 'SEC', 'Regulation AB Item 1100', 'General disclosure requirements for asset-backed securities', 'Comprehensive disclosure of transaction structure, parties, and asset pool characteristics', 'Review transaction documentation for completeness of required disclosures', 'Review CMBS deal {deal_name} disclosures for compliance with SEC Regulation AB Item 1100. Verify all required transaction information is present and accurate.', 'critical', true),
('SEC_REG_AB_1111', 'Asset Pool Characteristics', 'SEC', 'Regulation AB Item 1111', 'Detailed disclosure of asset pool composition and characteristics', 'Statistical information about the asset pool, including delinquencies, credit enhancements, and geographic distribution', 'Verify asset pool data completeness, test statistical calculations, validate geographic and property type distributions', 'Analyze CMBS deal {deal_name} asset pool disclosures. Verify statistical data, property distributions, and performance metrics comply with Reg AB Item 1111.', 'high', true),
('SEC_REG_AB_1112', 'Delinquency and Loss Information', 'SEC', 'Regulation AB Item 1112', 'Disclosure of delinquency, loss, and cumulative loss information', 'Historical and current delinquency and loss data with appropriate aging categories', 'Test delinquency aging calculations, validate loss data, review historical trend analysis', 'Examine delinquency and loss information for CMBS deal {deal_name}. Verify compliance with SEC Reg AB Item 1112 requirements for aging categories and historical data.', 'high', true),
('SEC_REG_AB_1113', 'Servicer Information', 'SEC', 'Regulation AB Item 1113', 'Disclosure of servicer qualifications and performance', 'Information about servicers, including experience, servicing criteria, and past performance', 'Review servicer disclosures, validate servicer qualifications, assess performance history', 'Evaluate servicer information for CMBS deal {deal_name}. Master servicer: {master_servicer}, Special servicer: {special_servicer}. Assess Reg AB Item 1113 compliance.', 'medium', true);

-- AICPA Standards
INSERT INTO compliance_rules_library (rule_code, rule_name, standard, standard_reference, description, requirements, testing_procedures, ai_prompt_template, risk_category, mandatory) VALUES
('AICPA_AT_C_205', 'Examination Engagements', 'AICPA', 'AT-C Section 205', 'Standards for examination engagements', 'Obtain reasonable assurance about whether subject matter conforms to criteria', 'Plan and perform examination procedures, obtain sufficient appropriate evidence, evaluate results', 'Assess examination procedures for CMBS deal {deal_name} under AT-C 205. Evaluate if procedures provide reasonable assurance and evidence is sufficient.', 'critical', true),
('AICPA_AT_C_210', 'Review Engagements', 'AICPA', 'AT-C Section 210', 'Standards for review engagements', 'Obtain limited assurance through inquiries and analytical procedures', 'Perform inquiries and analytical procedures, obtain review evidence, evaluate results for modification', 'Review procedures performed for CMBS deal {deal_name}. Assess compliance with AT-C 210 review engagement standards.', 'high', true);

-- GAAS Standards
INSERT INTO compliance_rules_library (rule_code, rule_name, standard, standard_reference, description, requirements, testing_procedures, ai_prompt_template, risk_category, mandatory) VALUES
('GAAS_AU_C_500', 'Audit Evidence', 'GAAS', 'AU-C Section 500', 'Generally accepted auditing standards for audit evidence', 'Design and perform audit procedures to obtain sufficient appropriate audit evidence', 'Evaluate relevance and reliability of evidence, test evidence gathering procedures, assess sufficiency', 'Assess audit evidence for CMBS deal {deal_name} under AU-C 500. Evaluate if evidence is relevant, reliable, and sufficient for audit objectives.', 'critical', true),
('GAAS_AU_C_315', 'Understanding Entity and Risk Assessment', 'GAAS', 'AU-C Section 315', 'Requirements for understanding the entity and assessing risks', 'Obtain understanding of entity, its environment, and internal control to assess risks', 'Review risk assessment procedures, evaluate understanding of entity and controls, test risk identification', 'Analyze risk assessment for CMBS deal {deal_name}. Evaluate if understanding of deal structure, parties, and risks meets AU-C 315 requirements.', 'high', true),
('GAAS_AU_C_540', 'Auditing Accounting Estimates', 'GAAS', 'AU-C Section 540', 'Auditing accounting estimates and related disclosures', 'Evaluate reasonableness of accounting estimates and related disclosures', 'Test estimate methodologies, evaluate assumptions and data, assess estimate reasonableness', 'Evaluate accounting estimates for CMBS deal {deal_name} including property valuations and impairment assessments. Assess compliance with AU-C 540.', 'high', true);

-- ========================================
-- Functions & Triggers
-- ========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_reg_ab_feature_flags_updated_at BEFORE UPDATE ON reg_ab_feature_flags FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reg_ab_audit_engagements_updated_at BEFORE UPDATE ON reg_ab_audit_engagements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cmbs_deals_updated_at BEFORE UPDATE ON cmbs_deals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_compliance_checks_updated_at BEFORE UPDATE ON compliance_checks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reg_ab_workpapers_updated_at BEFORE UPDATE ON reg_ab_workpapers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reg_ab_audit_reports_updated_at BEFORE UPDATE ON reg_ab_audit_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cpa_signoffs_updated_at BEFORE UPDATE ON cpa_signoffs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_compliance_rules_library_updated_at BEFORE UPDATE ON compliance_rules_library FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to log audit trail automatically
CREATE OR REPLACE FUNCTION log_reg_ab_audit_trail()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO reg_ab_audit_trail (
        audit_engagement_id,
        action_type,
        action_description,
        entity_type,
        entity_id,
        changes_before,
        changes_after
    ) VALUES (
        COALESCE(NEW.audit_engagement_id, OLD.audit_engagement_id),
        TG_OP,
        TG_TABLE_NAME || ' ' || TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        to_jsonb(OLD),
        to_jsonb(NEW)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- Row-Level Security (RLS)
-- ========================================

-- Enable RLS on sensitive tables
ALTER TABLE reg_ab_audit_engagements ENABLE ROW LEVEL SECURITY;
ALTER TABLE cmbs_deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE reg_ab_workpapers ENABLE ROW LEVEL SECURITY;
ALTER TABLE cpa_signoffs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reg_ab_audit_reports ENABLE ROW LEVEL SECURITY;

-- RLS Policies will be added based on organization context
-- Example policy for engagement access
CREATE POLICY reg_ab_engagement_org_policy ON reg_ab_audit_engagements
    USING (organization_id = current_setting('app.current_organization_id', true)::UUID);

-- ========================================
-- Comments for Documentation
-- ========================================

COMMENT ON TABLE reg_ab_audit_engagements IS 'Regulation A/B audit engagements for CMBS loans with AI-powered compliance checking';
COMMENT ON TABLE cmbs_deals IS 'CMBS deals entered by clients for Operating Advisor (OA) audit requirements';
COMMENT ON TABLE compliance_checks IS 'AI-powered compliance checks against PCAOB, GAAP, GAAS, SEC, and AICPA standards';
COMMENT ON TABLE reg_ab_workpapers IS 'AI-generated audit workpapers with CPA review workflow';
COMMENT ON TABLE reg_ab_audit_reports IS 'Final Regulation A/B audit reports with AI assistance';
COMMENT ON TABLE cpa_signoffs IS 'CPA sign-off and approval workflow with digital signatures';
COMMENT ON TABLE compliance_rules_library IS 'Library of compliance rules with AI prompts for automated checking';
COMMENT ON TABLE reg_ab_feature_flags IS 'Feature flags for enabling/disabling Reg A/B audit functionality per organization';

-- ========================================
-- Grant Permissions
-- ========================================

-- Grant access to application role (adjust based on your setup)
-- GRANT ALL ON ALL TABLES IN SCHEMA atlas TO app_role;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA atlas TO app_role;

-- ========================================
-- END OF MIGRATION
-- ========================================
