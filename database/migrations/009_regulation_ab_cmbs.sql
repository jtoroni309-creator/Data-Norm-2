-- ========================================
-- REGULATION AB CMBS AUDIT SYSTEM
-- Commercial Mortgage-Backed Securities Compliance
-- ========================================

SET search_path TO atlas;

-- ========================================
-- 1. CMBS DEALS & STRUCTURES
-- ========================================

CREATE TYPE deal_status AS ENUM (
    'active',
    'matured',
    'liquidated',
    'in_default'
);

CREATE TYPE servicer_role AS ENUM (
    'master_servicer',
    'special_servicer',
    'sub_servicer',
    'backup_servicer'
);

-- CMBS Deal Master Table
CREATE TABLE IF NOT EXISTS cmbs_deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,

    -- Deal identification
    deal_name VARCHAR(255) NOT NULL,
    cusip VARCHAR(20),
    bloomberg_ticker VARCHAR(50),
    closing_date DATE NOT NULL,
    expected_maturity_date DATE,

    -- Deal structure
    total_original_balance DECIMAL(18,2) NOT NULL,
    current_balance DECIMAL(18,2),
    number_of_loans INTEGER,
    number_of_properties INTEGER,

    -- Deal documents
    psa_document_s3_uri TEXT,  -- Pooling and Servicing Agreement
    prospectus_s3_uri TEXT,
    rating_agency_reports_s3_uri TEXT,

    -- Parties
    depositor VARCHAR(255),
    sponsor VARCHAR(255),
    trustee VARCHAR(255),
    certificate_administrator VARCHAR(255),

    -- Status
    deal_status deal_status DEFAULT 'active',
    is_shelf_eligible BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_cmbs_deals_client ON cmbs_deals(client_id);
CREATE INDEX idx_cmbs_deals_status ON cmbs_deals(deal_status);
CREATE INDEX idx_cmbs_deals_name ON cmbs_deals(deal_name);

COMMENT ON TABLE cmbs_deals IS 'CMBS deal master records';

-- CMBS Servicers
CREATE TABLE IF NOT EXISTS cmbs_servicers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES cmbs_deals(id) ON DELETE CASCADE,

    servicer_name VARCHAR(255) NOT NULL,
    servicer_role servicer_role NOT NULL,
    servicer_code VARCHAR(50),

    -- Contact
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),

    -- Servicing details
    servicing_start_date DATE,
    servicing_end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cmbs_servicers_deal ON cmbs_servicers(deal_id);
CREATE INDEX idx_cmbs_servicers_role ON cmbs_servicers(servicer_role);

COMMENT ON TABLE cmbs_servicers IS 'Servicers for CMBS deals';

-- Loan Tape (individual loans in the pool)
CREATE TABLE IF NOT EXISTS cmbs_loan_tape (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES cmbs_deals(id) ON DELETE CASCADE,

    -- Loan identification
    loan_number VARCHAR(100) NOT NULL,
    prospectus_loan_id VARCHAR(100),

    -- Borrower
    borrower_name VARCHAR(255),
    borrower_sponsor VARCHAR(255),

    -- Property
    property_name VARCHAR(255),
    property_address TEXT,
    property_city VARCHAR(100),
    property_state VARCHAR(50),
    property_zip VARCHAR(20),
    property_type VARCHAR(100),  -- Office, Retail, Multifamily, Industrial, Hotel, Mixed Use
    property_square_feet INTEGER,
    year_built INTEGER,

    -- Loan details
    original_balance DECIMAL(18,2) NOT NULL,
    current_balance DECIMAL(18,2),
    interest_rate DECIMAL(8,5),
    original_term_months INTEGER,
    remaining_term_months INTEGER,
    origination_date DATE,
    maturity_date DATE,
    first_payment_date DATE,

    -- Underwriting
    original_ltv DECIMAL(8,4),  -- Loan-to-Value
    original_dscr DECIMAL(8,4), -- Debt Service Coverage Ratio
    original_debt_yield DECIMAL(8,4),
    original_appraised_value DECIMAL(18,2),

    -- Current status
    current_ltv DECIMAL(8,4),
    current_dscr DECIMAL(8,4),
    current_debt_yield DECIMAL(8,4),
    current_occupancy_rate DECIMAL(8,4),

    -- Performance
    is_current BOOLEAN DEFAULT TRUE,
    days_delinquent INTEGER DEFAULT 0,
    is_specially_serviced BOOLEAN DEFAULT FALSE,
    watchlist_status VARCHAR(50),

    -- Metadata
    as_of_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cmbs_loan_tape_deal ON cmbs_loan_tape(deal_id);
CREATE INDEX idx_cmbs_loan_tape_loan_number ON cmbs_loan_tape(loan_number);
CREATE INDEX idx_cmbs_loan_tape_property_type ON cmbs_loan_tape(property_type);
CREATE INDEX idx_cmbs_loan_tape_current ON cmbs_loan_tape(is_current);
CREATE INDEX idx_cmbs_loan_tape_specially_serviced ON cmbs_loan_tape(is_specially_serviced);

COMMENT ON TABLE cmbs_loan_tape IS 'Individual loans in CMBS pool';

-- Servicer Remittance Reports
CREATE TABLE IF NOT EXISTS servicer_remittance_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES cmbs_deals(id) ON DELETE CASCADE,
    servicer_id UUID NOT NULL REFERENCES cmbs_servicers(id),

    report_period DATE NOT NULL,
    report_received_date DATE,
    report_s3_uri TEXT,

    -- Summary data
    beginning_pool_balance DECIMAL(18,2),
    scheduled_principal DECIMAL(18,2),
    unscheduled_principal DECIMAL(18,2),
    ending_pool_balance DECIMAL(18,2),
    interest_collected DECIMAL(18,2),

    -- Delinquency
    loans_30_days DECIMAL(18,2),
    loans_60_days DECIMAL(18,2),
    loans_90_plus_days DECIMAL(18,2),
    loans_in_foreclosure DECIMAL(18,2),
    reo_balance DECIMAL(18,2),

    -- Special servicing
    specially_serviced_loans INTEGER,
    specially_serviced_balance DECIMAL(18,2),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_servicer_remittance_deal ON servicer_remittance_reports(deal_id);
CREATE INDEX idx_servicer_remittance_period ON servicer_remittance_reports(report_period);

COMMENT ON TABLE servicer_remittance_reports IS 'Monthly servicer remittance reports';

-- ========================================
-- 2. REG AB SERVICING CRITERIA
-- ========================================

CREATE TYPE servicing_criterion_category AS ENUM (
    'general_servicing',
    'cash_collection',
    'investor_remittances',
    'pool_asset_administration',
    'servicing_advances'
);

-- Servicing Criteria (from Reg AB Item 1122)
CREATE TABLE IF NOT EXISTS reg_ab_servicing_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    criterion_number VARCHAR(20) NOT NULL UNIQUE,  -- e.g., 'SC-1', 'SC-2'
    criterion_category servicing_criterion_category NOT NULL,
    criterion_title VARCHAR(500) NOT NULL,
    criterion_description TEXT NOT NULL,

    -- Testing requirements
    testing_procedure TEXT,
    sample_size_guidance TEXT,
    exception_threshold DECIMAL(8,4),  -- e.g., 0.05 for 5%

    -- References
    reg_ab_reference VARCHAR(100),  -- e.g., 'Item 1122(d)(1)(i)'
    aicpa_reference VARCHAR(100),   -- e.g., 'AT-C Section 320'

    is_active BOOLEAN DEFAULT TRUE,
    position_order INTEGER,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_servicing_criteria_category ON reg_ab_servicing_criteria(criterion_category);
CREATE INDEX idx_servicing_criteria_number ON reg_ab_servicing_criteria(criterion_number);

COMMENT ON TABLE reg_ab_servicing_criteria IS 'Regulation AB servicing criteria to test';

-- Seed servicing criteria
INSERT INTO reg_ab_servicing_criteria (
    criterion_number, criterion_category, criterion_title, criterion_description,
    testing_procedure, reg_ab_reference, position_order
) VALUES
-- General Servicing Considerations
('SC-1', 'general_servicing', 'Policies and Procedures',
'The servicer has maintained policies and procedures that set forth the activities performed by the servicer and the timelines for their completion.',
'Review servicer''s policies and procedures manual. Test compliance with documented procedures through sampling.',
'Item 1122(d)(1)(i)', 10),

('SC-2', 'general_servicing', 'Periodic Evaluation of Policies',
'The servicer has maintained a management information system that facilitates evaluating, on a regular basis, the performance of the servicer.',
'Review management reports. Test that performance metrics are tracked and reviewed.',
'Item 1122(d)(1)(ii)', 20),

('SC-3', 'general_servicing', 'Monitoring Third Parties',
'The servicer has maintained a process for monitoring the performance of third-party vendors.',
'Review vendor management policies. Test monitoring activities for key vendors.',
'Item 1122(d)(1)(iii)', 30),

-- Cash Collection and Administration
('SC-4', 'cash_collection', 'Accurate and Timely Cash Application',
'The servicer has maintained accurate and timely cash application.',
'Test cash receipts for accurate application to correct loans and accurate posting dates.',
'Item 1122(d)(2)(i)', 40),

('SC-5', 'cash_collection', 'Collections Deposited',
'The servicer has deposited or otherwise credited collections received from or on behalf of obligors into the appropriate custodial bank accounts.',
'Test deposit of collections into custodial accounts within required timeframes.',
'Item 1122(d)(2)(ii)', 50),

('SC-6', 'cash_collection', 'Trust Account Reconciliation',
'The servicer has maintained accurate records of collections deposited into custodial bank accounts.',
'Test reconciliation of custodial bank accounts on monthly basis.',
'Item 1122(d)(2)(iii)', 60),

-- Investor Remittances and Reporting
('SC-7', 'investor_remittances', 'Timely Distribution',
'The servicer has made the distributions to security holders in accordance with transaction documents.',
'Test that distributions were made on correct payment dates per PSA requirements.',
'Item 1122(d)(3)(i)', 70),

('SC-8', 'investor_remittances', 'Accurate Distribution Calculations',
'The servicer has distributed to security holders the appropriate amounts.',
'Recalculate distribution amounts and compare to actual distributions.',
'Item 1122(d)(3)(ii)', 80),

('SC-9', 'investor_remittances', 'Accurate Investor Reporting',
'The servicer has provided accurate investor reports in accordance with transaction documents.',
'Test accuracy of data in investor reports against source records.',
'Item 1122(d)(3)(iii)', 90),

-- Pool Asset Administration
('SC-10', 'pool_asset_administration', 'Default Identification',
'The servicer has identified default or delinquency events on the pool assets.',
'Test that delinquencies are accurately identified and aged.',
'Item 1122(d)(4)(i)', 100),

('SC-11', 'pool_asset_administration', 'Loss Mitigation',
'The servicer has instituted and maintained practices for effecting loss mitigation efforts.',
'Review loss mitigation strategies. Test that efforts are documented and timely.',
'Item 1122(d)(4)(ii)', 110),

('SC-12', 'pool_asset_administration', 'Property Inspections',
'The servicer has maintained and updated pool asset records.',
'Test property inspection records for specially serviced loans.',
'Item 1122(d)(4)(iii)', 120),

('SC-13', 'pool_asset_administration', 'Evidence of Insurance',
'The servicer has maintained evidence of required insurance coverage.',
'Test insurance certificates for active loans.',
'Item 1122(d)(4)(iv)', 130),

('SC-14', 'pool_asset_administration', 'Tax and Assessment Payments',
'The servicer has maintained tax payment records.',
'Test that property taxes were paid timely from escrow or by borrower.',
'Item 1122(d)(4)(v)', 140);

-- ========================================
-- 3. REG AB AUDIT ENGAGEMENTS
-- ========================================

CREATE TYPE reg_ab_engagement_type AS ENUM (
    'assessment_of_compliance',  -- AoC examination
    'agreed_upon_procedures',    -- AUP
    'review_engagement'          -- Review
);

CREATE TYPE reg_ab_report_period AS ENUM (
    'annual',
    'interim'
);

-- Reg AB Engagements (extends base engagements)
CREATE TABLE IF NOT EXISTS reg_ab_engagements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    deal_id UUID NOT NULL REFERENCES cmbs_deals(id) ON DELETE CASCADE,

    -- Engagement details
    reg_ab_engagement_type reg_ab_engagement_type DEFAULT 'assessment_of_compliance',
    report_period reg_ab_report_period DEFAULT 'annual',
    assessment_period_start DATE NOT NULL,
    assessment_period_end DATE NOT NULL,

    -- Servicer assertion
    servicer_assertion_received BOOLEAN DEFAULT FALSE,
    servicer_assertion_date DATE,
    servicer_assertion_s3_uri TEXT,

    -- Testing
    total_criteria_tested INTEGER,
    criteria_passed INTEGER,
    criteria_failed INTEGER,
    total_exceptions INTEGER,
    material_exceptions INTEGER,

    -- Reports
    aoc_report_s3_uri TEXT,
    examination_report_s3_uri TEXT,
    management_letter_s3_uri TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reg_ab_engagements_engagement ON reg_ab_engagements(engagement_id);
CREATE INDEX idx_reg_ab_engagements_deal ON reg_ab_engagements(deal_id);

COMMENT ON TABLE reg_ab_engagements IS 'Regulation AB examination engagements';

-- ========================================
-- 4. COMPLIANCE TESTING
-- ========================================

CREATE TYPE test_result AS ENUM (
    'pass',
    'fail',
    'not_applicable',
    'inconclusive'
);

-- Servicing Criteria Testing
CREATE TABLE IF NOT EXISTS servicing_criteria_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reg_ab_engagement_id UUID NOT NULL REFERENCES reg_ab_engagements(id) ON DELETE CASCADE,
    servicing_criterion_id UUID NOT NULL REFERENCES reg_ab_servicing_criteria(id),

    -- Test design
    test_description TEXT,
    sample_size INTEGER,
    population_size INTEGER,
    sampling_method VARCHAR(100),  -- 'random', 'stratified', 'judgmental', '100%'

    -- Test execution
    test_performed_by UUID REFERENCES users(id),
    test_performed_date DATE,
    test_reviewed_by UUID REFERENCES users(id),
    test_reviewed_date DATE,

    -- Results
    test_result test_result,
    items_tested INTEGER,
    exceptions_noted INTEGER,
    exception_rate DECIMAL(8,4),

    -- Documentation
    workpaper_reference VARCHAR(100),
    test_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_servicing_criteria_tests_engagement ON servicing_criteria_tests(reg_ab_engagement_id);
CREATE INDEX idx_servicing_criteria_tests_criterion ON servicing_criteria_tests(servicing_criterion_id);
CREATE INDEX idx_servicing_criteria_tests_result ON servicing_criteria_tests(test_result);

COMMENT ON TABLE servicing_criteria_tests IS 'Testing of individual servicing criteria';

-- Test Exceptions
CREATE TABLE IF NOT EXISTS servicing_test_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    servicing_criteria_test_id UUID NOT NULL REFERENCES servicing_criteria_tests(id) ON DELETE CASCADE,

    -- Exception details
    item_identifier VARCHAR(255),  -- Loan number, report period, etc.
    exception_description TEXT NOT NULL,
    exception_amount DECIMAL(18,2),

    -- Severity
    is_material BOOLEAN DEFAULT FALSE,
    materiality_justification TEXT,

    -- Resolution
    is_resolved BOOLEAN DEFAULT FALSE,
    resolution_description TEXT,
    resolved_by UUID REFERENCES users(id),
    resolved_date DATE,

    -- Root cause
    root_cause TEXT,
    corrective_action TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_exceptions_test ON servicing_test_exceptions(servicing_criteria_test_id);
CREATE INDEX idx_test_exceptions_material ON servicing_test_exceptions(is_material);
CREATE INDEX idx_test_exceptions_resolved ON servicing_test_exceptions(is_resolved);

COMMENT ON TABLE servicing_test_exceptions IS 'Exceptions noted during servicing criteria testing';

-- ========================================
-- 5. AI-EXTRACTED DATA
-- ========================================

-- AI-extracted deal terms from PSA
CREATE TABLE IF NOT EXISTS ai_extracted_deal_terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES cmbs_deals(id) ON DELETE CASCADE,

    -- Source document
    source_document_type VARCHAR(100),  -- 'PSA', 'Prospectus', 'Rating Report'
    source_document_s3_uri TEXT,
    extraction_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Extracted data (JSONB for flexibility)
    extracted_terms JSONB NOT NULL,

    -- Examples of extracted terms:
    -- {
    --   "payment_dates": "25th of each month",
    --   "distribution_priority": {...},
    --   "servicer_compensation": {...},
    --   "trigger_events": {...},
    --   "cleanup_call_provisions": {...},
    --   "expense_priorities": {...}
    -- }

    -- AI metadata
    ai_model_used VARCHAR(100),
    confidence_score DECIMAL(5,4),

    -- Verification
    verified_by UUID REFERENCES users(id),
    verified_date DATE,
    verification_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_extracted_deal ON ai_extracted_deal_terms(deal_id);

COMMENT ON TABLE ai_extracted_deal_terms IS 'AI-extracted terms from deal documents';

-- AI-identified risks and issues
CREATE TABLE IF NOT EXISTS ai_identified_risks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES cmbs_deals(id) ON DELETE CASCADE,
    reg_ab_engagement_id UUID REFERENCES reg_ab_engagements(id),

    -- Risk identification
    risk_category VARCHAR(100),  -- 'concentration', 'delinquency', 'property_type', 'geographic'
    risk_title VARCHAR(500),
    risk_description TEXT,
    risk_severity VARCHAR(50),   -- 'low', 'medium', 'high', 'critical'

    -- Supporting data
    supporting_data JSONB,
    affected_loans TEXT[],  -- Array of loan numbers

    -- AI metadata
    ai_model_used VARCHAR(100),
    confidence_score DECIMAL(5,4),

    -- Auditor review
    reviewed_by UUID REFERENCES users(id),
    reviewed_date DATE,
    is_confirmed BOOLEAN,
    auditor_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_risks_deal ON ai_identified_risks(deal_id);
CREATE INDEX idx_ai_risks_engagement ON ai_identified_risks(reg_ab_engagement_id);
CREATE INDEX idx_ai_risks_severity ON ai_identified_risks(risk_severity);

COMMENT ON TABLE ai_identified_risks IS 'AI-identified risks in CMBS deals';

-- ========================================
-- 6. ASSESSMENT OF COMPLIANCE (AoC)
-- ========================================

CREATE TYPE aoc_opinion_type AS ENUM (
    'unqualified',        -- No exceptions
    'qualified',          -- Exceptions noted
    'adverse',            -- Significant non-compliance
    'disclaimer'          -- Unable to complete examination
);

-- Assessment of Compliance Report
CREATE TABLE IF NOT EXISTS aoc_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reg_ab_engagement_id UUID NOT NULL REFERENCES reg_ab_engagements(id) ON DELETE CASCADE,

    report_date DATE NOT NULL,
    opinion_type aoc_opinion_type,

    -- Report sections (generated by AI)
    executive_summary TEXT,
    scope_section TEXT,
    criteria_tested_section TEXT,
    test_results_section TEXT,
    exceptions_section TEXT,
    opinion_paragraph TEXT,

    -- Attachments
    detailed_test_results_s3_uri TEXT,
    exception_detail_s3_uri TEXT,

    -- Approval
    drafted_by UUID REFERENCES users(id),
    drafted_at TIMESTAMPTZ,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,

    -- Issuance
    issued_to_client BOOLEAN DEFAULT FALSE,
    issued_date DATE,
    final_report_s3_uri TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_aoc_reports_engagement ON aoc_reports(reg_ab_engagement_id);
CREATE INDEX idx_aoc_reports_opinion ON aoc_reports(opinion_type);

COMMENT ON TABLE aoc_reports IS 'Assessment of Compliance examination reports';

-- ========================================
-- 7. VIEWS & ANALYTICS
-- ========================================

-- Deal summary view
CREATE OR REPLACE VIEW cmbs_deal_summary AS
SELECT
    d.id AS deal_id,
    d.deal_name,
    d.cusip,
    d.closing_date,
    d.total_original_balance,
    d.current_balance,
    d.number_of_loans,
    d.deal_status,
    COUNT(DISTINCT s.id) AS servicer_count,
    COUNT(DISTINCT lt.id) AS current_loan_count,
    SUM(CASE WHEN lt.is_current = FALSE THEN 1 ELSE 0 END) AS delinquent_loan_count,
    SUM(CASE WHEN lt.is_specially_serviced = TRUE THEN 1 ELSE 0 END) AS specially_serviced_count,
    SUM(CASE WHEN lt.days_delinquent >= 90 THEN lt.current_balance ELSE 0 END) AS balance_90_plus_days
FROM cmbs_deals d
LEFT JOIN cmbs_servicers s ON s.deal_id = d.id AND s.is_active = TRUE
LEFT JOIN cmbs_loan_tape lt ON lt.deal_id = d.id
GROUP BY d.id, d.deal_name, d.cusip, d.closing_date, d.total_original_balance,
    d.current_balance, d.number_of_loans, d.deal_status;

COMMENT ON VIEW cmbs_deal_summary IS 'Summary metrics for CMBS deals';

-- Servicing criteria test results summary
CREATE OR REPLACE VIEW servicing_criteria_test_summary AS
SELECT
    rae.id AS engagement_id,
    rae.deal_id,
    d.deal_name,
    COUNT(DISTINCT sct.id) AS total_tests,
    COUNT(DISTINCT sct.id) FILTER (WHERE sct.test_result = 'pass') AS tests_passed,
    COUNT(DISTINCT sct.id) FILTER (WHERE sct.test_result = 'fail') AS tests_failed,
    SUM(sct.exceptions_noted) AS total_exceptions,
    COUNT(DISTINCT ste.id) FILTER (WHERE ste.is_material = TRUE) AS material_exceptions
FROM reg_ab_engagements rae
JOIN cmbs_deals d ON d.id = rae.deal_id
LEFT JOIN servicing_criteria_tests sct ON sct.reg_ab_engagement_id = rae.id
LEFT JOIN servicing_test_exceptions ste ON ste.servicing_criteria_test_id = sct.id
GROUP BY rae.id, rae.deal_id, d.deal_name;

COMMENT ON VIEW servicing_criteria_test_summary IS 'Test results summary by engagement';
