-- ========================================
-- WORKPAPER TEMPLATES & STANDARD BINDER STRUCTURE
-- Complete library of audit workpaper templates
-- ========================================

SET search_path TO atlas;

-- Workpaper template categories
CREATE TYPE workpaper_category AS ENUM (
    'planning',
    'cash',
    'receivables',
    'inventory',
    'investments',
    'fixed_assets',
    'other_assets',
    'payables',
    'accruals',
    'debt',
    'equity',
    'revenue',
    'expenses',
    'analytical',
    'confirmations',
    'substantive_testing',
    'controls',
    'subsequent_events',
    'going_concern',
    'related_parties',
    'completeness',
    'final_review'
);

-- Workpaper template library
CREATE TABLE IF NOT EXISTS workpaper_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Template identification
    template_code VARCHAR(20) NOT NULL UNIQUE,  -- e.g., 'A-100', 'B-200'
    template_name VARCHAR(255) NOT NULL,
    category workpaper_category NOT NULL,

    -- Template content
    description TEXT,
    instructions TEXT,
    content_template JSONB NOT NULL,  -- Template structure

    -- Standard fields/columns
    has_tickmarks BOOLEAN DEFAULT TRUE,
    has_cross_references BOOLEAN DEFAULT TRUE,
    requires_preparer_signoff BOOLEAN DEFAULT TRUE,
    requires_reviewer_signoff BOOLEAN DEFAULT TRUE,

    -- Assertions tested (for substantive tests)
    tests_existence BOOLEAN DEFAULT FALSE,
    tests_completeness BOOLEAN DEFAULT FALSE,
    tests_rights_obligations BOOLEAN DEFAULT FALSE,
    tests_valuation BOOLEAN DEFAULT FALSE,
    tests_presentation BOOLEAN DEFAULT FALSE,

    -- Engagement type applicability
    applicable_to_audit BOOLEAN DEFAULT TRUE,
    applicable_to_review BOOLEAN DEFAULT TRUE,
    applicable_to_compilation BOOLEAN DEFAULT FALSE,

    -- Materiality/risk
    required_for_all_engagements BOOLEAN DEFAULT FALSE,
    required_if_material BOOLEAN DEFAULT TRUE,
    risk_level VARCHAR(20),  -- high, moderate, low

    -- Metadata
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workpaper_templates_code ON workpaper_templates(template_code);
CREATE INDEX idx_workpaper_templates_category ON workpaper_templates(category);

COMMENT ON TABLE workpaper_templates IS 'Library of standard workpaper templates';

-- Standard binder structure
CREATE TABLE IF NOT EXISTS binder_structure_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Structure definition
    engagement_type VARCHAR(50) NOT NULL,  -- audit, review, compilation
    section_code VARCHAR(20) NOT NULL,     -- A, B, C, etc.
    section_name VARCHAR(255) NOT NULL,
    parent_section_code VARCHAR(20),       -- For subsections

    -- Auto-generation settings
    auto_create BOOLEAN DEFAULT TRUE,
    position_order INTEGER NOT NULL,

    -- Associated workpapers
    default_workpaper_templates UUID[],    -- Array of template IDs to auto-create

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(engagement_type, section_code)
);

CREATE INDEX idx_binder_structure_engagement_type ON binder_structure_templates(engagement_type);

COMMENT ON TABLE binder_structure_templates IS 'Standard binder structure by engagement type';

-- Tickmark library
CREATE TABLE IF NOT EXISTS tickmark_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    symbol VARCHAR(10) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    standard_usage TEXT,

    -- Common tickmarks
    is_standard BOOLEAN DEFAULT TRUE,
    display_order INTEGER,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tickmark_library_standard ON tickmark_library(is_standard);

COMMENT ON TABLE tickmark_library IS 'Standard audit tickmarks';

-- ========================================
-- SEED STANDARD TICKMARKS
-- ========================================

INSERT INTO tickmark_library (symbol, description, standard_usage, is_standard, display_order) VALUES
('✓', 'Agreed to supporting documentation', 'Traced to source document', TRUE, 1),
('F', 'Footed (added vertically)', 'Verified mathematical accuracy of column totals', TRUE, 2),
('T', 'Traced', 'Followed item from one document to another', TRUE, 3),
('C/F', 'Carried forward', 'Amount agrees to amount on another workpaper', TRUE, 4),
('TB', 'Agreed to trial balance', 'Verified amount ties to trial balance', TRUE, 5),
('P/Y', 'Agreed to prior year', 'Compared to prior year amount', TRUE, 6),
('G/L', 'Agreed to general ledger', 'Verified to general ledger detail', TRUE, 7),
('R', 'Recalculated', 'Independently recalculated amount', TRUE, 8),
('I', 'Inspected', 'Physically examined or inspected document', TRUE, 9),
('Δ', 'Variance noted', 'Difference or variance identified', TRUE, 10),
('N/A', 'Not applicable', 'Procedure not applicable', TRUE, 11),
('@', 'Confirmations received', 'External confirmation obtained', TRUE, 12),
('S', 'Scanned for unusual items', 'Reviewed for unusual or unexpected items', TRUE, 13),
('M', 'Material item', 'Flagged as material for attention', TRUE, 14),
('E', 'Explained by management', 'Management provided explanation', TRUE, 15);

-- ========================================
-- SEED STANDARD BINDER STRUCTURE (AUDIT)
-- ========================================

INSERT INTO binder_structure_templates (engagement_type, section_code, section_name, parent_section_code, position_order, auto_create) VALUES

-- Planning Section
('audit', 'A', 'Planning and Risk Assessment', NULL, 100, TRUE),
('audit', 'A-100', 'Engagement Letter and Independence', 'A', 101, TRUE),
('audit', 'A-110', 'Understanding the Entity', 'A', 102, TRUE),
('audit', 'A-120', 'Materiality Calculations', 'A', 103, TRUE),
('audit', 'A-130', 'Risk Assessment', 'A', 104, TRUE),
('audit', 'A-140', 'Audit Plan and Programs', 'A', 105, TRUE),
('audit', 'A-150', 'Analytical Procedures - Planning', 'A', 106, TRUE),

-- Cash
('audit', 'B', 'Cash and Cash Equivalents', NULL, 200, TRUE),
('audit', 'B-100', 'Cash Lead Schedule', 'B', 201, TRUE),
('audit', 'B-110', 'Bank Confirmations', 'B', 202, TRUE),
('audit', 'B-120', 'Bank Reconciliations', 'B', 203, TRUE),
('audit', 'B-130', 'Cash Cutoff Testing', 'B', 204, TRUE),

-- Accounts Receivable
('audit', 'C', 'Accounts Receivable', NULL, 300, TRUE),
('audit', 'C-100', 'Accounts Receivable Lead Schedule', 'C', 301, TRUE),
('audit', 'C-110', 'Accounts Receivable Confirmations', 'C', 302, TRUE),
('audit', 'C-120', 'Aging Analysis', 'C', 303, TRUE),
('audit', 'C-130', 'Allowance for Doubtful Accounts', 'C', 304, TRUE),
('audit', 'C-140', 'Subsequent Collections', 'C', 305, TRUE),

-- Inventory
('audit', 'D', 'Inventory', NULL, 400, TRUE),
('audit', 'D-100', 'Inventory Lead Schedule', 'D', 401, TRUE),
('audit', 'D-110', 'Inventory Observation', 'D', 402, TRUE),
('audit', 'D-120', 'Inventory Valuation', 'D', 403, TRUE),
('audit', 'D-130', 'Inventory Rollforward', 'D', 404, TRUE),

-- Fixed Assets
('audit', 'E', 'Property, Plant and Equipment', NULL, 500, TRUE),
('audit', 'E-100', 'Fixed Assets Lead Schedule', 'E', 501, TRUE),
('audit', 'E-110', 'Fixed Assets Rollforward', 'E', 502, TRUE),
('audit', 'E-120', 'Depreciation Calculation', 'E', 503, TRUE),
('audit', 'E-130', 'Additions and Disposals', 'E', 504, TRUE),

-- Other Assets
('audit', 'F', 'Other Assets', NULL, 600, TRUE),
('audit', 'F-100', 'Investments', 'F', 601, TRUE),
('audit', 'F-110', 'Intangible Assets', 'F', 602, TRUE),
('audit', 'F-120', 'Prepaid Expenses', 'F', 603, TRUE),

-- Accounts Payable and Accruals
('audit', 'G', 'Accounts Payable and Accrued Liabilities', NULL, 700, TRUE),
('audit', 'G-100', 'Accounts Payable Lead Schedule', 'G', 701, TRUE),
('audit', 'G-110', 'Accounts Payable Confirmations', 'G', 702, TRUE),
('audit', 'G-120', 'Search for Unrecorded Liabilities', 'G', 703, TRUE),
('audit', 'G-130', 'Accrued Expenses', 'G', 704, TRUE),

-- Debt
('audit', 'H', 'Debt and Long-term Liabilities', NULL, 800, TRUE),
('audit', 'H-100', 'Debt Lead Schedule', 'H', 801, TRUE),
('audit', 'H-110', 'Debt Confirmations', 'H', 802, TRUE),
('audit', 'H-120', 'Debt Covenant Compliance', 'H', 803, TRUE),
('audit', 'H-130', 'Interest Expense', 'H', 804, TRUE),

-- Equity
('audit', 'I', 'Stockholders Equity', NULL, 900, TRUE),
('audit', 'I-100', 'Equity Lead Schedule', 'I', 901, TRUE),
('audit', 'I-110', 'Stock Transactions', 'I', 902, TRUE),
('audit', 'I-120', 'Retained Earnings Rollforward', 'I', 903, TRUE),

-- Revenue
('audit', 'J', 'Revenue', NULL, 1000, TRUE),
('audit', 'J-100', 'Revenue Lead Schedule', 'J', 1001, TRUE),
('audit', 'J-110', 'Revenue Recognition Testing', 'J', 1002, TRUE),
('audit', 'J-120', 'Revenue Cutoff', 'J', 1003, TRUE),
('audit', 'J-130', 'Revenue Analytical Procedures', 'J', 1004, TRUE),

-- Expenses
('audit', 'K', 'Operating Expenses', NULL, 1100, TRUE),
('audit', 'K-100', 'Expense Lead Schedule', 'K', 1101, TRUE),
('audit', 'K-110', 'Payroll Testing', 'K', 1102, TRUE),
('audit', 'K-120', 'Expense Analytics', 'K', 1103, TRUE),

-- Income Taxes
('audit', 'L', 'Income Taxes', NULL, 1200, TRUE),
('audit', 'L-100', 'Income Tax Lead Schedule', 'L', 1201, TRUE),
('audit', 'L-110', 'Tax Provision Review', 'L', 1202, TRUE),
('audit', 'L-120', 'Deferred Taxes', 'L', 1203, TRUE),

-- Other Procedures
('audit', 'M', 'Other Audit Procedures', NULL, 1300, TRUE),
('audit', 'M-100', 'Related Party Transactions', 'M', 1301, TRUE),
('audit', 'M-110', 'Subsequent Events Review', 'M', 1302, TRUE),
('audit', 'M-120', 'Going Concern Assessment', 'M', 1303, TRUE),
('audit', 'M-130', 'Attorney Letters', 'M', 1304, TRUE),
('audit', 'M-140', 'Management Representations', 'M', 1305, TRUE),

-- Completion
('audit', 'N', 'Final Review and Completion', NULL, 1400, TRUE),
('audit', 'N-100', 'Final Analytical Procedures', 'N', 1401, TRUE),
('audit', 'N-110', 'Financial Statement Review', 'N', 1402, TRUE),
('audit', 'N-120', 'Disclosure Checklist', 'N', 1403, TRUE),
('audit', 'N-130', 'Summary of Unadjusted Differences', 'N', 1404, TRUE),
('audit', 'N-140', 'Engagement Quality Review', 'N', 1405, TRUE);

-- ========================================
-- SEED WORKPAPER TEMPLATES
-- ========================================

-- Planning Templates
INSERT INTO workpaper_templates (template_code, template_name, category, description, content_template, required_for_all_engagements) VALUES
('A-120', 'Materiality Calculation',
 'planning',
 'Calculate overall materiality, performance materiality, and trivial threshold',
 '{
   "sections": [
     {"title": "Benchmarks", "type": "table", "columns": ["Benchmark", "Amount", "Selected"]},
     {"title": "Materiality Levels", "type": "calculation", "fields": ["overall_materiality", "performance_materiality", "trivial_threshold"]},
     {"title": "Justification", "type": "text"}
   ]
 }',
 TRUE),

('A-130', 'Risk Assessment Summary',
 'planning',
 'Document assessed risks at financial statement and assertion levels',
 '{
   "sections": [
     {"title": "Financial Statement Level Risks", "type": "table"},
     {"title": "Significant Risks", "type": "table"},
     {"title": "Fraud Risks", "type": "table"},
     {"title": "Response to Risks", "type": "text"}
   ]
 }',
 TRUE);

-- Cash Templates
INSERT INTO workpaper_templates (template_code, template_name, category, description, content_template, tests_existence, tests_valuation) VALUES
('B-100', 'Cash Lead Schedule',
 'cash',
 'Summary of all cash accounts with tie to trial balance',
 '{
   "columns": ["Account", "Per Books", "Adjustments", "Per Audit", "TB Reference"],
   "footer_rows": ["Total Cash", "Agree to F/S"],
   "tickmarks": ["TB", "F", "C/F"]
 }',
 TRUE, TRUE),

('B-120', 'Bank Reconciliation Review',
 'cash',
 'Review and test bank reconciliations',
 '{
   "sections": [
     {"title": "Reconciliation Review", "type": "table"},
     {"title": "Outstanding Checks > 90 days", "type": "list"},
     {"title": "Deposits in Transit", "type": "table"},
     {"title": "Reconciling Items", "type": "table"}
   ]
 }',
 TRUE, TRUE);

-- Accounts Receivable Templates
INSERT INTO workpaper_templates (template_code, template_name, category, description, content_template, tests_existence, tests_valuation) VALUES
('C-100', 'Accounts Receivable Lead Schedule',
 'receivables',
 'Summary of accounts receivable with aging and allowance',
 '{
   "sections": [
     {"title": "A/R Summary", "type": "table", "columns": ["Account", "Gross A/R", "Allowance", "Net A/R", "TB Ref"]},
     {"title": "Aging Analysis Summary", "type": "table"},
     {"title": "Tie to Financial Statements", "type": "calculation"}
   ]
 }',
 TRUE, TRUE),

('C-130', 'Allowance for Doubtful Accounts',
 'receivables',
 'Test allowance for uncollectible accounts',
 '{
   "sections": [
     {"title": "Allowance Methodology", "type": "text"},
     {"title": "Historical Loss Rates", "type": "table"},
     {"title": "CECL Analysis (if applicable)", "type": "table"},
     {"title": "Recalculation", "type": "calculation"},
     {"title": "Reasonableness", "type": "text"}
   ]
 }',
 FALSE, TRUE);

COMMENT ON TABLE workpaper_templates IS 'Standard audit workpaper templates';
