-- ========================================
-- Aura Audit AI (Project Atlas)
-- Database Schema - Tax Preparation Module
-- Migration 0003
-- ========================================
-- AI-First Tax Preparation Engine
-- Federal + Multi-State Support
-- OCR Document Intake, Tax Computation, Forms, E-file
-- ========================================

SET search_path TO atlas, public;

-- ========================================
-- Tax Return Core Types
-- ========================================

CREATE TYPE entity_type AS ENUM (
    'individual',           -- Form 1040
    'c_corp',              -- Form 1120
    's_corp',              -- Form 1120-S
    'partnership',         -- Form 1065
    'llc_single',          -- Disregarded entity
    'llc_partnership',     -- Multi-member LLC
    'trust',               -- Form 1041
    'estate'               -- Form 1041
);

CREATE TYPE filing_status AS ENUM (
    'single',              -- Single
    'married_joint',       -- Married Filing Jointly
    'married_separate',    -- Married Filing Separately
    'head_of_household',   -- Head of Household
    'qualifying_widow'     -- Qualifying Widow(er)
);

CREATE TYPE tax_return_status AS ENUM (
    'draft',               -- In progress
    'in_review',           -- Awaiting reviewer approval
    'qc_review',           -- QC review in progress
    'ready_to_file',       -- Validated, ready for e-file
    'filed',               -- Submitted to IRS/state
    'accepted',            -- IRS/state accepted
    'rejected',            -- IRS/state rejected
    'amended',             -- Return was amended (see amended_from_id)
    'archived'             -- Historical, locked
);

CREATE TYPE document_type AS ENUM (
    'W-2',                 -- Wage and Tax Statement
    '1099-INT',            -- Interest Income
    '1099-DIV',            -- Dividend Income
    '1099-B',              -- Brokerage/Stock Sales
    '1099-R',              -- Distributions from Pensions
    '1099-MISC',           -- Miscellaneous Income
    '1099-NEC',            -- Nonemployee Compensation
    '1099-G',              -- Government Payments
    '1099-K',              -- Payment Card Transactions
    '1098',                -- Mortgage Interest
    '1098-E',              -- Student Loan Interest
    '1098-T',              -- Tuition Statement
    '5498',                -- IRA Contribution Information
    '5498-SA',             -- HSA Contribution Information
    'K-1-1065',            -- Partnership K-1
    'K-1-1120S',           -- S-Corp K-1
    'K-1-1041',            -- Trust/Estate K-1
    'SSA-1099',            -- Social Security Benefits
    '1095-A',              -- Health Insurance Marketplace
    '1095-B',              -- Health Coverage
    '1095-C',              -- Employer Health Coverage
    'BROKERAGE_STATEMENT', -- Year-end brokerage statement
    'PROPERTY_TAX',        -- Property tax statement
    'CHARITY_RECEIPT',     -- Charitable contribution receipt
    'BUSINESS_EXPENSE',    -- Business expense documentation
    'OTHER'                -- Other supporting documents
);

CREATE TYPE review_flag_severity AS ENUM ('low', 'medium', 'high', 'critical');

CREATE TYPE review_flag_code AS ENUM (
    'LOW_CONFIDENCE',      -- OCR confidence < 0.98
    'VARIANCE_PY',         -- Significant variance vs prior year
    'MISSING_DOC',         -- Expected document not received
    'CROSS_CHECK_FAIL',    -- Cross-form reconciliation failed
    'THRESHOLD_TRIGGER',   -- Triggered IRS threshold (NIIT, AMT, etc.)
    'BASIS_ISSUE',         -- Missing/incorrect basis in 1099-B
    'WASH_SALE',           -- Potential wash sale not reported
    'DUPLICATE_DOC',       -- Duplicate document detected
    'OUTLIER',             -- Statistical outlier vs norm
    'PHASE_OUT',           -- Credit/deduction phase-out applies
    'PASSIVE_LOSS',        -- Passive loss limitation
    'AT_RISK',             -- At-risk rules apply
    'NOL_CARRYOVER',       -- Net operating loss carryover
    'AMT_ITEM',            -- AMT adjustment item detected
    'EFILE_ERROR'          -- E-file validation error
);

-- ========================================
-- Tax Returns
-- ========================================

CREATE TABLE tax_returns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    engagement_id UUID REFERENCES engagements(id),  -- Link to audit engagement (if applicable)

    -- Taxpayer identification
    taxpayer_name TEXT NOT NULL,
    taxpayer_ssn TEXT,        -- Encrypted SSN
    taxpayer_ein TEXT,        -- Encrypted EIN (for entities)
    spouse_name TEXT,
    spouse_ssn TEXT,          -- Encrypted
    entity_type entity_type NOT NULL,
    filing_status filing_status,  -- NULL for entities

    -- Tax year
    tax_year INTEGER NOT NULL CHECK (tax_year >= 1900 AND tax_year <= 2100),
    fiscal_year_end DATE,     -- For entities with fiscal year
    is_fiscal_year BOOLEAN DEFAULT false,

    -- Address
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    state TEXT,               -- 2-letter state code
    zip_code TEXT,
    country TEXT DEFAULT 'US',

    -- Dependents (JSONB for flexibility)
    dependents JSONB,         -- [{name, ssn, relationship, dob, months_lived}]

    -- Income (detailed JSONB storage)
    income JSONB,             -- TDS income structure

    -- Adjustments to income
    adjustments JSONB,        -- {educator_expenses, hsa, ...}

    -- Deductions
    deductions JSONB,         -- {itemized, standard, ...}

    -- Credits
    credits JSONB,            -- {child_tax_credit, erc, ...}

    -- Payments & withholding
    payments JSONB,           -- {withholding, estimated, ...}

    -- Carryovers
    carryovers JSONB,         -- {cap_loss, nol, passive_loss, ...}

    -- K-1 data (partnerships, S-corps, trusts)
    k1_data JSONB,            -- {partnership: [...], scorp: [...]}

    -- Depreciation & assets
    assets JSONB,             -- {depreciation, Section 179, bonus, ...}

    -- State-specific data
    state_returns JSONB,      -- {CA: {...}, NY: {...}}

    -- Calculated results
    gross_income NUMERIC(15, 2),
    adjusted_gross_income NUMERIC(15, 2),
    taxable_income NUMERIC(15, 2),
    federal_income_tax NUMERIC(15, 2),
    federal_amt NUMERIC(15, 2),
    federal_se_tax NUMERIC(15, 2),
    federal_niit NUMERIC(15, 2),
    federal_total_tax NUMERIC(15, 2),
    federal_total_payments NUMERIC(15, 2),
    federal_balance NUMERIC(15, 2),  -- Positive = owe, negative = refund

    state_total_tax NUMERIC(15, 2),
    state_total_payments NUMERIC(15, 2),
    state_balance NUMERIC(15, 2),

    -- Elections (JSONB for flexibility)
    elections JSONB,          -- {itemize, mfs_itemize, capital_loss_carryback, ...}

    -- Status & workflow
    status tax_return_status DEFAULT 'draft',
    last_calculated_at TIMESTAMPTZ,
    calculation_version TEXT,  -- Semantic version of tax engine

    -- Review & approval
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    qc_reviewed_by UUID REFERENCES users(id),
    qc_reviewed_at TIMESTAMPTZ,

    -- E-file
    efile_validated BOOLEAN DEFAULT false,
    efile_validation_errors JSONB,
    irs_confirmation_number TEXT,
    irs_submission_id TEXT,
    filed_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    rejection_reasons JSONB,

    -- Amendments
    is_amended BOOLEAN DEFAULT false,
    amended_from_id UUID REFERENCES tax_returns(id),
    amendment_reason TEXT,

    -- Prior year comparison
    prior_year_return_id UUID REFERENCES tax_returns(id),

    -- Metadata
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    locked_at TIMESTAMPTZ,
    locked_by UUID REFERENCES users(id)
);

CREATE INDEX idx_tax_returns_org ON tax_returns(organization_id);
CREATE INDEX idx_tax_returns_engagement ON tax_returns(engagement_id);
CREATE INDEX idx_tax_returns_year ON tax_returns(tax_year);
CREATE INDEX idx_tax_returns_status ON tax_returns(status);
CREATE INDEX idx_tax_returns_taxpayer_ssn ON tax_returns(taxpayer_ssn);  -- Encrypted search
CREATE INDEX idx_tax_returns_created_by ON tax_returns(created_by);

-- Row-level security for multi-tenancy
ALTER TABLE tax_returns ENABLE ROW LEVEL SECURITY;

CREATE POLICY tax_returns_org_policy ON tax_returns
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

-- ========================================
-- Tax Documents (Source Documents)
-- ========================================

CREATE TABLE tax_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_return_id UUID NOT NULL REFERENCES tax_returns(id) ON DELETE CASCADE,

    -- Document metadata
    document_type document_type NOT NULL,
    classification_confidence NUMERIC(3, 2) CHECK (classification_confidence >= 0 AND classification_confidence <= 1),
    tax_year INTEGER,

    -- File storage
    file_url TEXT NOT NULL,   -- MinIO/S3 URL
    file_name TEXT,
    file_size BIGINT,         -- Bytes
    file_checksum TEXT,       -- SHA-256 for deduplication
    mime_type TEXT,
    page_count INTEGER DEFAULT 1,

    -- OCR metadata
    ocr_completed BOOLEAN DEFAULT false,
    ocr_completed_at TIMESTAMPTZ,
    ocr_model_version TEXT,   -- "gpt-4-vision-preview", etc.

    -- Classification
    classified_by TEXT,       -- "ai" or "user_id"
    classified_at TIMESTAMPTZ,
    manual_classification BOOLEAN DEFAULT false,

    -- Deduplication
    is_duplicate BOOLEAN DEFAULT false,
    duplicate_of_id UUID REFERENCES tax_documents(id),

    -- Version control (if user uploads replacement)
    version INTEGER DEFAULT 1,
    superseded_by_id UUID REFERENCES tax_documents(id),

    -- Metadata
    uploaded_by UUID NOT NULL REFERENCES users(id),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_documents_return ON tax_documents(tax_return_id);
CREATE INDEX idx_tax_documents_type ON tax_documents(document_type);
CREATE INDEX idx_tax_documents_checksum ON tax_documents(file_checksum);
CREATE INDEX idx_tax_documents_uploaded_by ON tax_documents(uploaded_by);

-- ========================================
-- Tax Document Pages (for multi-page PDFs)
-- ========================================

CREATE TABLE tax_document_pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_document_id UUID NOT NULL REFERENCES tax_documents(id) ON DELETE CASCADE,

    page_number INTEGER NOT NULL CHECK (page_number > 0),
    image_url TEXT,           -- Extracted page image
    ocr_text TEXT,            -- Full OCR text
    ocr_confidence NUMERIC(3, 2),

    -- Layout analysis (JSONB for bounding boxes)
    layout JSONB,             -- {boxes: [{x, y, w, h, text, confidence}], tables: [...]}

    -- Classification (pages may have different types)
    page_type document_type,
    page_classification_confidence NUMERIC(3, 2),

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_document_pages_document ON tax_document_pages(tax_document_id);
CREATE INDEX idx_tax_document_pages_page_num ON tax_document_pages(tax_document_id, page_number);

-- ========================================
-- Tax Extracted Fields (Raw OCR Output)
-- ========================================

CREATE TABLE tax_extracted_fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_document_id UUID NOT NULL REFERENCES tax_documents(id) ON DELETE CASCADE,
    tax_document_page_id UUID REFERENCES tax_document_pages(id) ON DELETE CASCADE,

    -- Field identification
    field_name TEXT NOT NULL,     -- "box1_wages", "box2_federal_withholding", etc.
    field_label TEXT,             -- "Wages, tips, other compensation"
    field_value TEXT,             -- Raw extracted value
    field_value_normalized TEXT,  -- Cleaned/parsed value
    field_type TEXT,              -- "currency", "ssn", "ein", "text", "date"

    -- Confidence & quality
    confidence NUMERIC(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    low_confidence BOOLEAN GENERATED ALWAYS AS (confidence < 0.98) STORED,

    -- Bounding box (for UI highlighting)
    bbox JSONB,               -- {x, y, width, height} in pixels

    -- Validation
    validated BOOLEAN DEFAULT false,
    validation_errors JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_extracted_fields_document ON tax_extracted_fields(tax_document_id);
CREATE INDEX idx_tax_extracted_fields_page ON tax_extracted_fields(tax_document_page_id);
CREATE INDEX idx_tax_extracted_fields_low_conf ON tax_extracted_fields(low_confidence) WHERE low_confidence = true;

-- ========================================
-- Tax Forms (Generated IRS Forms)
-- ========================================

CREATE TABLE tax_forms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_return_id UUID NOT NULL REFERENCES tax_returns(id) ON DELETE CASCADE,

    -- Form identification
    form_type TEXT NOT NULL,      -- "1040", "1120", "Schedule C", "Schedule D", etc.
    form_year INTEGER NOT NULL,
    form_version TEXT,            -- IRS form version

    -- Form data (line-by-line)
    form_data JSONB NOT NULL,     -- {line1a: 50000, line1b: 0, ...}

    -- Generated PDF
    pdf_url TEXT,                 -- MinIO/S3 URL of filled PDF
    pdf_generated_at TIMESTAMPTZ,

    -- Schema version
    schema_version TEXT,          -- Version of form schema used

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_forms_return ON tax_forms(tax_return_id);
CREATE INDEX idx_tax_forms_type ON tax_forms(form_type);

-- ========================================
-- Tax Deductions
-- ========================================

CREATE TABLE tax_deductions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_return_id UUID NOT NULL REFERENCES tax_returns(id) ON DELETE CASCADE,

    -- Deduction classification
    category TEXT NOT NULL,       -- "business_expense", "charitable", "medical", etc.
    subcategory TEXT,             -- More specific classification
    description TEXT,

    -- Amount
    amount NUMERIC(15, 2) NOT NULL CHECK (amount >= 0),

    -- AI suggestion
    suggested_by_ai BOOLEAN DEFAULT false,
    ai_confidence NUMERIC(3, 2) CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    ai_rationale TEXT,

    -- Documentation
    documentation_url TEXT,       -- Receipt/invoice in MinIO/S3
    documentation_document_id UUID REFERENCES tax_documents(id),

    -- Form/schedule mapping
    applies_to_form TEXT,         -- "Schedule A", "Schedule C", etc.
    form_line TEXT,               -- "Line 5a" (medical expenses)

    -- Approval
    approved BOOLEAN DEFAULT false,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_deductions_return ON tax_deductions(tax_return_id);
CREATE INDEX idx_tax_deductions_category ON tax_deductions(category);
CREATE INDEX idx_tax_deductions_ai ON tax_deductions(suggested_by_ai) WHERE suggested_by_ai = true;

-- ========================================
-- Tax Credits
-- ========================================

CREATE TABLE tax_credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_return_id UUID NOT NULL REFERENCES tax_returns(id) ON DELETE CASCADE,

    -- Credit type
    credit_type TEXT NOT NULL,    -- "child_tax_credit", "erc", "r_d_credit", etc.
    description TEXT,

    -- Amount
    amount NUMERIC(15, 2) NOT NULL CHECK (amount >= 0),

    -- Supporting data
    supporting_data JSONB,        -- Credit-specific data (# of children, etc.)

    -- Form mapping
    form_type TEXT,               -- "Form 8863", "Form 8995", etc.

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_credits_return ON tax_credits(tax_return_id);
CREATE INDEX idx_tax_credits_type ON tax_credits(credit_type);

-- ========================================
-- Tax Review Flags
-- ========================================

CREATE TABLE tax_review_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_return_id UUID NOT NULL REFERENCES tax_returns(id) ON DELETE CASCADE,

    -- Flag classification
    code review_flag_code NOT NULL,
    severity review_flag_severity NOT NULL,
    message TEXT NOT NULL,

    -- Context
    field_path TEXT,              -- JSON path in TDS: "income.w2[0].wages"
    current_value TEXT,
    prior_year_value TEXT,
    variance_pct NUMERIC(5, 2),

    -- Supporting documents
    source_document_id UUID REFERENCES tax_documents(id),
    source_document_snippet_url TEXT,  -- Cropped image of relevant section

    -- AI analysis
    ai_suggestion TEXT,
    ai_confidence NUMERIC(3, 2),

    -- Resolution
    resolved BOOLEAN DEFAULT false,
    resolution_action TEXT,       -- "accept", "override", "reject", "defer"
    override_value TEXT,
    resolution_notes TEXT,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_review_flags_return ON tax_review_flags(tax_return_id);
CREATE INDEX idx_tax_review_flags_resolved ON tax_review_flags(resolved) WHERE resolved = false;
CREATE INDEX idx_tax_review_flags_severity ON tax_review_flags(severity);

-- ========================================
-- Tax Provenance (Audit Trail)
-- ========================================

CREATE TABLE tax_provenance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_return_id UUID NOT NULL REFERENCES tax_returns(id) ON DELETE CASCADE,

    -- Field mapping
    field_path TEXT NOT NULL,     -- "income.w2[0].wages"
    field_value TEXT,

    -- Source tracing
    source_type TEXT,             -- "ocr_extraction", "manual_entry", "calculation", "import"
    source_document_id UUID REFERENCES tax_documents(id),
    source_document_page_id UUID REFERENCES tax_document_pages(id),
    source_document_ref TEXT,     -- "doc:W2#1@page1:box1"

    -- Extraction/calculation details
    extraction_method TEXT,       -- "gpt-4-vision", "manual"
    ocr_model_version TEXT,
    mapping_rule_id TEXT,         -- "M-W2-Box1"
    calculation_formula TEXT,     -- For computed fields

    -- User attribution
    entered_by UUID REFERENCES users(id),
    modified_by UUID REFERENCES users(id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_provenance_return ON tax_provenance(tax_return_id);
CREATE INDEX idx_tax_provenance_field ON tax_provenance(field_path);
CREATE INDEX idx_tax_provenance_source_doc ON tax_provenance(source_document_id);

-- ========================================
-- Prior Year Returns (Imported Data)
-- ========================================

CREATE TABLE prior_year_returns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    tax_return_id UUID REFERENCES tax_returns(id),  -- Link to current year if applicable

    -- Prior year details
    tax_year INTEGER NOT NULL CHECK (tax_year >= 1900 AND tax_year <= 2100),
    taxpayer_name TEXT NOT NULL,
    taxpayer_ssn TEXT,            -- Encrypted
    entity_type entity_type NOT NULL,
    filing_status filing_status,

    -- Import source
    source_type TEXT,             -- "manual", "pdf_upload", "software_import", "irs_transcript"
    source_file_url TEXT,         -- Original uploaded file

    -- Extracted data (full TDS structure)
    return_data JSONB NOT NULL,

    -- Import quality
    import_method TEXT,           -- "ai_pdf_parse", "manual_entry", "api_import"
    import_confidence NUMERIC(3, 2),
    import_errors JSONB,

    -- Metadata
    imported_by UUID NOT NULL REFERENCES users(id),
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_prior_year_returns_org ON prior_year_returns(organization_id);
CREATE INDEX idx_prior_year_returns_year ON prior_year_returns(tax_year);
CREATE INDEX idx_prior_year_returns_current_return ON prior_year_returns(tax_return_id);

-- ========================================
-- Tax Rules Catalog (Configuration)
-- ========================================

CREATE TABLE tax_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id TEXT NOT NULL UNIQUE,  -- "RULE-2024-1040-STD-DEDUCTION-SINGLE"

    -- Rule classification
    rule_type TEXT NOT NULL,       -- "standard_deduction", "tax_bracket", "credit_limit", etc.
    tax_year INTEGER NOT NULL,
    jurisdiction TEXT NOT NULL,    -- "federal", "CA", "NY", etc.
    entity_type entity_type,
    filing_status filing_status,

    -- Rule definition
    rule_name TEXT NOT NULL,
    description TEXT,
    rule_data JSONB NOT NULL,      -- {amount: 14600, phase_out: {...}}

    -- IRS citation
    irs_publication TEXT,          -- "Pub 17", "Pub 542", etc.
    irs_section TEXT,              -- IRC §199A, etc.
    irs_url TEXT,

    -- Versioning
    effective_date DATE NOT NULL,
    expiration_date DATE,
    superseded_by_id UUID REFERENCES tax_rules(id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_rules_rule_id ON tax_rules(rule_id);
CREATE INDEX idx_tax_rules_year_jurisdiction ON tax_rules(tax_year, jurisdiction);
CREATE INDEX idx_tax_rules_type ON tax_rules(rule_type);

-- ========================================
-- Tax Calculation Logs (Explainability)
-- ========================================

CREATE TABLE tax_calculation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_return_id UUID NOT NULL REFERENCES tax_returns(id) ON DELETE CASCADE,

    -- Calculation metadata
    calculation_version TEXT NOT NULL,  -- Engine version
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Input snapshot
    input_data JSONB NOT NULL,     -- Full TDS at time of calculation

    -- Output
    output_data JSONB NOT NULL,    -- Calculated results

    -- Explanation graph
    explanation_graph JSONB,       -- {nodes: [...], edges: [...]} for lineage

    -- Performance metrics
    calculation_time_ms INTEGER,

    -- User attribution
    triggered_by UUID REFERENCES users(id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_calculation_logs_return ON tax_calculation_logs(tax_return_id);
CREATE INDEX idx_tax_calculation_logs_calculated_at ON tax_calculation_logs(calculated_at);

-- ========================================
-- E-file Submissions
-- ========================================

CREATE TABLE efile_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tax_return_id UUID NOT NULL REFERENCES tax_returns(id),

    -- Submission details
    jurisdiction TEXT NOT NULL,    -- "federal", "CA", etc.
    submission_type TEXT NOT NULL, -- "original", "amended"
    form_type TEXT NOT NULL,       -- "1040", "1120", etc.

    -- MeF XML
    mef_xml TEXT,                  -- Full MeF XML
    mef_schema_version TEXT,       -- "2024v1.0"
    mef_validation_passed BOOLEAN DEFAULT false,
    mef_validation_errors JSONB,

    -- Submission
    submitted_at TIMESTAMPTZ,
    submitted_by UUID REFERENCES users(id),
    submission_id TEXT,            -- IRS submission ID

    -- Response
    irs_confirmation_number TEXT,
    response_received_at TIMESTAMPTZ,
    response_status TEXT,          -- "accepted", "rejected", "pending"
    response_data JSONB,

    -- Rejection handling
    rejection_code TEXT,
    rejection_message TEXT,
    resubmit_planned BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_efile_submissions_return ON efile_submissions(tax_return_id);
CREATE INDEX idx_efile_submissions_status ON efile_submissions(response_status);
CREATE INDEX idx_efile_submissions_submitted_at ON efile_submissions(submitted_at);

-- ========================================
-- Tax Engagement Settings (Per Organization)
-- ========================================

CREATE TABLE tax_engagement_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) UNIQUE,

    -- Default preferences
    default_confidence_threshold NUMERIC(3, 2) DEFAULT 0.98,
    enable_ai_suggestions BOOLEAN DEFAULT true,
    enable_prior_year_variance_checks BOOLEAN DEFAULT true,
    variance_threshold_pct NUMERIC(5, 2) DEFAULT 50.00,  -- Flag if >50% variance

    -- State tax defaults
    default_state TEXT,            -- Primary state for returns
    multi_state_enabled BOOLEAN DEFAULT false,

    -- E-file settings
    irs_etin TEXT,                 -- Electronic Transmitter Identification Number
    irs_efin TEXT,                 -- Electronic Filing Identification Number
    irs_ptin TEXT,                 -- Preparer Tax Identification Number
    efile_enabled BOOLEAN DEFAULT false,

    -- ERO (Electronic Return Originator) details
    ero_name TEXT,
    ero_firm_name TEXT,
    ero_phone TEXT,
    ero_certificate_url TEXT,      -- X.509 certificate for MeF signing

    -- Integration settings
    quickbooks_enabled BOOLEAN DEFAULT false,
    xero_enabled BOOLEAN DEFAULT false,
    netsuite_enabled BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tax_engagement_settings_org ON tax_engagement_settings(organization_id);

-- ========================================
-- Audit Triggers (Update timestamps)
-- ========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tax_returns_updated_at
    BEFORE UPDATE ON tax_returns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tax_forms_updated_at
    BEFORE UPDATE ON tax_forms
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tax_rules_updated_at
    BEFORE UPDATE ON tax_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tax_engagement_settings_updated_at
    BEFORE UPDATE ON tax_engagement_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- Initial Tax Rules (2024 Federal)
-- ========================================

-- Standard Deductions (2024)
INSERT INTO tax_rules (rule_id, rule_type, tax_year, jurisdiction, entity_type, filing_status, rule_name, description, rule_data, irs_publication, effective_date) VALUES
('RULE-2024-FED-STD-DEDUCTION-SINGLE', 'standard_deduction', 2024, 'federal', 'individual', 'single', 'Standard Deduction - Single', '2024 standard deduction for single filers', '{"amount": 14600}', 'Pub 17', '2024-01-01'),
('RULE-2024-FED-STD-DEDUCTION-MFJ', 'standard_deduction', 2024, 'federal', 'individual', 'married_joint', 'Standard Deduction - MFJ', '2024 standard deduction for married filing jointly', '{"amount": 29200}', 'Pub 17', '2024-01-01'),
('RULE-2024-FED-STD-DEDUCTION-MFS', 'standard_deduction', 2024, 'federal', 'individual', 'married_separate', 'Standard Deduction - MFS', '2024 standard deduction for married filing separately', '{"amount": 14600}', 'Pub 17', '2024-01-01'),
('RULE-2024-FED-STD-DEDUCTION-HOH', 'standard_deduction', 2024, 'federal', 'individual', 'head_of_household', 'Standard Deduction - HOH', '2024 standard deduction for head of household', '{"amount": 21900}', 'Pub 17', '2024-01-01');

-- Tax Brackets (2024 - Single)
INSERT INTO tax_rules (rule_id, rule_type, tax_year, jurisdiction, entity_type, filing_status, rule_name, description, rule_data, irs_publication, effective_date) VALUES
('RULE-2024-FED-BRACKET-SINGLE', 'tax_bracket', 2024, 'federal', 'individual', 'single', 'Tax Brackets - Single', '2024 federal income tax brackets for single filers', '{"brackets": [{"min": 0, "max": 11600, "rate": 0.10}, {"min": 11600, "max": 47150, "rate": 0.12}, {"min": 47150, "max": 100525, "rate": 0.22}, {"min": 100525, "max": 191950, "rate": 0.24}, {"min": 191950, "max": 243725, "rate": 0.32}, {"min": 243725, "max": 609350, "rate": 0.35}, {"min": 609350, "max": null, "rate": 0.37}]}', 'Pub 17', '2024-01-01');

-- Tax Brackets (2024 - MFJ)
INSERT INTO tax_rules (rule_id, rule_type, tax_year, jurisdiction, entity_type, filing_status, rule_name, description, rule_data, irs_publication, effective_date) VALUES
('RULE-2024-FED-BRACKET-MFJ', 'tax_bracket', 2024, 'federal', 'individual', 'married_joint', 'Tax Brackets - MFJ', '2024 federal income tax brackets for married filing jointly', '{"brackets": [{"min": 0, "max": 23200, "rate": 0.10}, {"min": 23200, "max": 94300, "rate": 0.12}, {"min": 94300, "max": 201050, "rate": 0.22}, {"min": 201050, "max": 383900, "rate": 0.24}, {"min": 383900, "max": 487450, "rate": 0.32}, {"min": 487450, "max": 731200, "rate": 0.35}, {"min": 731200, "max": null, "rate": 0.37}]}', 'Pub 17', '2024-01-01');

-- QBI Deduction Thresholds (§199A)
INSERT INTO tax_rules (rule_id, rule_type, tax_year, jurisdiction, entity_type, filing_status, rule_name, description, rule_data, irs_publication, effective_date) VALUES
('RULE-2024-FED-QBI-THRESHOLD-SINGLE', 'qbi_threshold', 2024, 'federal', 'individual', 'single', 'QBI Deduction Threshold - Single', '§199A QBI deduction phase-out threshold', '{"threshold": 191950, "phase_out_range": 50000}', 'Pub 535', '2024-01-01'),
('RULE-2024-FED-QBI-THRESHOLD-MFJ', 'qbi_threshold', 2024, 'federal', 'individual', 'married_joint', 'QBI Deduction Threshold - MFJ', '§199A QBI deduction phase-out threshold', '{"threshold": 383900, "phase_out_range": 100000}', 'Pub 535', '2024-01-01');

-- NIIT Threshold (3.8% Net Investment Income Tax)
INSERT INTO tax_rules (rule_id, rule_type, tax_year, jurisdiction, entity_type, filing_status, rule_name, description, rule_data, irs_publication, effective_date) VALUES
('RULE-2024-FED-NIIT-THRESHOLD-SINGLE', 'niit_threshold', 2024, 'federal', 'individual', 'single', 'NIIT Threshold - Single', 'Net Investment Income Tax threshold', '{"threshold": 200000, "rate": 0.038}', 'Pub 550', '2024-01-01'),
('RULE-2024-FED-NIIT-THRESHOLD-MFJ', 'niit_threshold', 2024, 'federal', 'individual', 'married_joint', 'NIIT Threshold - MFJ', 'Net Investment Income Tax threshold', '{"threshold": 250000, "rate": 0.038}', 'Pub 550', '2024-01-01');

-- Child Tax Credit (2024)
INSERT INTO tax_rules (rule_id, rule_type, tax_year, jurisdiction, entity_type, rule_name, description, rule_data, irs_publication, effective_date) VALUES
('RULE-2024-FED-CHILD-TAX-CREDIT', 'credit', 2024, 'federal', 'individual', 'Child Tax Credit', 'Child tax credit per qualifying child', '{"amount_per_child": 2000, "refundable_portion": 1700, "age_limit": 17, "phase_out_start_single": 200000, "phase_out_start_mfj": 400000, "phase_out_rate": 0.05}', 'Pub 972', '2024-01-01');

-- AMT Exemption (2024)
INSERT INTO tax_rules (rule_id, rule_type, tax_year, jurisdiction, entity_type, filing_status, rule_name, description, rule_data, irs_publication, effective_date) VALUES
('RULE-2024-FED-AMT-EXEMPTION-SINGLE', 'amt_exemption', 2024, 'federal', 'individual', 'single', 'AMT Exemption - Single', 'Alternative Minimum Tax exemption amount', '{"exemption": 85700, "phase_out_start": 609350, "phase_out_rate": 0.25}', 'Form 6251', '2024-01-01'),
('RULE-2024-FED-AMT-EXEMPTION-MFJ', 'amt_exemption', 2024, 'federal', 'individual', 'married_joint', 'AMT Exemption - MFJ', 'Alternative Minimum Tax exemption amount', '{"exemption": 133300, "phase_out_start": 1218700, "phase_out_rate": 0.25}', 'Form 6251', '2024-01-01');

-- Capital Gains Rates (2024)
INSERT INTO tax_rules (rule_id, rule_type, tax_year, jurisdiction, entity_type, filing_status, rule_name, description, rule_data, irs_publication, effective_date) VALUES
('RULE-2024-FED-LTCG-RATES-SINGLE', 'capital_gains_rate', 2024, 'federal', 'individual', 'single', 'Long-Term Capital Gains Rates - Single', '2024 LTCG tax rates', '{"brackets": [{"min": 0, "max": 47025, "rate": 0.00}, {"min": 47025, "max": 518900, "rate": 0.15}, {"min": 518900, "max": null, "rate": 0.20}]}', 'Pub 550', '2024-01-01'),
('RULE-2024-FED-LTCG-RATES-MFJ', 'capital_gains_rate', 2024, 'federal', 'individual', 'married_joint', 'Long-Term Capital Gains Rates - MFJ', '2024 LTCG tax rates', '{"brackets": [{"min": 0, "max": 94050, "rate": 0.00}, {"min": 94050, "max": 583750, "rate": 0.15}, {"min": 583750, "max": null, "rate": 0.20}]}', 'Pub 550', '2024-01-01');

-- ========================================
-- Comments
-- ========================================

COMMENT ON TABLE tax_returns IS 'Core tax return entity with TDS (Tax Data Schema) stored as JSONB';
COMMENT ON TABLE tax_documents IS 'Source documents (W-2, 1099s, etc.) uploaded for OCR processing';
COMMENT ON TABLE tax_document_pages IS 'Individual pages from multi-page documents with OCR results';
COMMENT ON TABLE tax_extracted_fields IS 'Raw OCR field extractions with confidence scores';
COMMENT ON TABLE tax_forms IS 'Generated IRS forms (1040, schedules) with PDF output';
COMMENT ON TABLE tax_deductions IS 'Itemized deductions with AI suggestions';
COMMENT ON TABLE tax_credits IS 'Tax credits applied to return';
COMMENT ON TABLE tax_review_flags IS 'Issues requiring human review (low confidence, variances, etc.)';
COMMENT ON TABLE tax_provenance IS 'Complete audit trail: TDS field → source document → extraction rule';
COMMENT ON TABLE prior_year_returns IS 'Imported prior year data for variance analysis';
COMMENT ON TABLE tax_rules IS 'Tax rules catalog (brackets, limits, phase-outs) by year and jurisdiction';
COMMENT ON TABLE tax_calculation_logs IS 'Calculation history with explainability graphs';
COMMENT ON TABLE efile_submissions IS 'IRS/state e-file submission tracking';
COMMENT ON TABLE tax_engagement_settings IS 'Organization-level tax preferences and ERO settings';

-- ========================================
-- Migration Complete
-- ========================================
