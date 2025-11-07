-- =====================================================
-- EDGAR INGESTION & ACCOUNT MAPPING TABLES
-- Purpose: Support EDGAR data ingestion and trial balance normalization
-- =====================================================

-- Set schema
SET search_path TO atlas;

-- =====================================================
-- EDGAR FILINGS TABLES
-- =====================================================

-- Filing form types enum
CREATE TYPE filing_form AS ENUM (
    '10-K', '10-Q', '20-F', '40-F', '6-K', '8-K',
    'DEF-14A', 'S-1', 'S-3', 'S-4', 'S-8', '3', '4', '5'
);

-- EDGAR filing metadata
CREATE TABLE IF NOT EXISTS filings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cik VARCHAR(20) NOT NULL,
    ticker VARCHAR(10),
    company_name VARCHAR(255) NOT NULL,
    form filing_form NOT NULL,
    filing_date DATE NOT NULL,
    accession_number VARCHAR(50) NOT NULL UNIQUE,
    source_uri TEXT NOT NULL,
    fiscal_year INTEGER,
    fiscal_period VARCHAR(10),
    raw_data_s3_uri TEXT,
    ingested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ingested_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_filings_cik ON filings(cik);
CREATE INDEX idx_filings_ticker ON filings(ticker);
CREATE INDEX idx_filings_form ON filings(form);
CREATE INDEX idx_filings_date ON filings(filing_date DESC);
CREATE INDEX idx_filings_company ON filings(company_name);

-- XBRL facts (financial data points)
CREATE TABLE IF NOT EXISTS facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filing_id UUID NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    concept VARCHAR(255) NOT NULL,
    taxonomy VARCHAR(50) NOT NULL DEFAULT 'us-gaap',
    label VARCHAR(255),
    value NUMERIC(20,2),
    unit VARCHAR(20),
    start_date DATE,
    end_date DATE,
    instant_date DATE,
    context_ref VARCHAR(100),
    decimals INTEGER,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_facts_filing ON facts(filing_id);
CREATE INDEX idx_facts_concept ON facts(concept);
CREATE INDEX idx_facts_taxonomy ON facts(taxonomy);
CREATE INDEX idx_facts_end_date ON facts(end_date DESC);
CREATE INDEX idx_facts_instant_date ON facts(instant_date DESC);
CREATE INDEX idx_facts_metadata ON facts USING GIN(metadata);

-- =====================================================
-- CHART OF ACCOUNTS
-- =====================================================

CREATE TYPE account_type AS ENUM (
    'asset', 'liability', 'equity', 'revenue', 'expense', 'contra'
);

CREATE TYPE account_subtype AS ENUM (
    'current', 'non-current', 'operating', 'non-operating',
    'retained-earnings', 'common-stock', 'preferred-stock',
    'other'
);

-- Standard chart of accounts (GAAP-based)
CREATE TABLE IF NOT EXISTS chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_code VARCHAR(50) NOT NULL UNIQUE,
    account_name VARCHAR(255) NOT NULL,
    account_type account_type NOT NULL,
    account_subtype account_subtype,
    parent_account_id UUID REFERENCES chart_of_accounts(id),
    level INTEGER NOT NULL DEFAULT 1,
    is_leaf BOOLEAN DEFAULT TRUE,
    normal_balance VARCHAR(10) CHECK (normal_balance IN ('debit', 'credit')),

    -- XBRL mapping
    xbrl_concept VARCHAR(255),
    xbrl_taxonomy VARCHAR(50) DEFAULT 'us-gaap',

    -- Classification
    financial_statement VARCHAR(50) CHECK (financial_statement IN
        ('balance_sheet', 'income_statement', 'cash_flow', 'equity', 'notes')),
    presentation_order INTEGER,

    -- Metadata
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coa_code ON chart_of_accounts(account_code);
CREATE INDEX idx_coa_name ON chart_of_accounts(account_name);
CREATE INDEX idx_coa_type ON chart_of_accounts(account_type);
CREATE INDEX idx_coa_xbrl ON chart_of_accounts(xbrl_concept);
CREATE INDEX idx_coa_parent ON chart_of_accounts(parent_account_id);
CREATE INDEX idx_coa_active ON chart_of_accounts(is_active);

-- =====================================================
-- TRIAL BALANCE TABLES
-- =====================================================

-- Trial balance imports
CREATE TABLE IF NOT EXISTS trial_balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    period_end_date DATE NOT NULL,
    source VARCHAR(100) NOT NULL,
    source_metadata JSONB,
    file_s3_uri TEXT,
    total_debits NUMERIC(20,2),
    total_credits NUMERIC(20,2),
    balance_difference NUMERIC(20,2),
    is_balanced BOOLEAN DEFAULT FALSE,
    line_count INTEGER,
    imported_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    imported_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tb_engagement ON trial_balances(engagement_id);
CREATE INDEX idx_tb_period ON trial_balances(period_end_date DESC);
CREATE INDEX idx_tb_source ON trial_balances(source);

-- Trial balance line items
CREATE TABLE IF NOT EXISTS trial_balance_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trial_balance_id UUID NOT NULL REFERENCES trial_balances(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    account_code VARCHAR(100) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    debit_amount NUMERIC(18,2),
    credit_amount NUMERIC(18,2),
    balance_amount NUMERIC(18,2),

    -- Mapping to standard chart of accounts
    mapped_account_id UUID REFERENCES chart_of_accounts(id),
    mapping_confidence NUMERIC(3,2),
    mapping_method VARCHAR(50),
    taxonomy_concept VARCHAR(255),

    -- Metadata
    notes TEXT,
    is_material BOOLEAN DEFAULT FALSE,
    requires_testing BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(trial_balance_id, line_number)
);

CREATE INDEX idx_tbl_trial_balance ON trial_balance_lines(trial_balance_id);
CREATE INDEX idx_tbl_account_code ON trial_balance_lines(account_code);
CREATE INDEX idx_tbl_mapped_account ON trial_balance_lines(mapped_account_id);
CREATE INDEX idx_tbl_material ON trial_balance_lines(is_material);

-- =====================================================
-- ACCOUNT MAPPING TABLES
-- =====================================================

CREATE TYPE mapping_confidence AS ENUM ('low', 'medium', 'high', 'very_high');
CREATE TYPE mapping_status AS ENUM ('unmapped', 'suggested', 'confirmed', 'rejected', 'manual');

-- Mapping rules for pattern-based mapping
CREATE TABLE IF NOT EXISTS mapping_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(255) NOT NULL,
    description TEXT,
    source_pattern VARCHAR(500) NOT NULL,
    target_account_code VARCHAR(50) NOT NULL REFERENCES chart_of_accounts(account_code),
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_regex BOOLEAN DEFAULT FALSE,
    confidence_boost NUMERIC(3,2) DEFAULT 0.0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mapping_rules_pattern ON mapping_rules(source_pattern);
CREATE INDEX idx_mapping_rules_account ON mapping_rules(target_account_code);
CREATE INDEX idx_mapping_rules_active ON mapping_rules(is_active);
CREATE INDEX idx_mapping_rules_priority ON mapping_rules(priority DESC);

-- ML model versions for mapping
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(50) NOT NULL UNIQUE,
    model_type VARCHAR(100) NOT NULL,
    model_path TEXT,
    training_samples INTEGER NOT NULL,
    accuracy NUMERIC(5,4),
    precision NUMERIC(5,4),
    recall NUMERIC(5,4),
    f1_score NUMERIC(5,4),
    feature_importance JSONB,
    hyperparameters JSONB,
    is_active BOOLEAN DEFAULT FALSE,
    trained_by UUID REFERENCES users(id),
    trained_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ml_models_version ON ml_models(model_version);
CREATE INDEX idx_ml_models_active ON ml_models(is_active);
CREATE INDEX idx_ml_models_type ON ml_models(model_type);

-- ML-generated mapping suggestions
CREATE TABLE IF NOT EXISTS mapping_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    trial_balance_line_id UUID NOT NULL REFERENCES trial_balance_lines(id) ON DELETE CASCADE,

    -- Source account
    source_account_code VARCHAR(100) NOT NULL,
    source_account_name VARCHAR(255) NOT NULL,

    -- Suggested mapping
    suggested_account_code VARCHAR(50) NOT NULL,
    suggested_account_name VARCHAR(255) NOT NULL,
    confidence_score NUMERIC(5,4) NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    confidence_level mapping_confidence NOT NULL,

    -- ML model info
    model_version VARCHAR(50),
    model_features JSONB,

    -- Alternatives
    alternatives JSONB,

    -- Status and feedback
    status mapping_status NOT NULL DEFAULT 'suggested',
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    feedback_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mapping_suggestions_engagement ON mapping_suggestions(engagement_id);
CREATE INDEX idx_mapping_suggestions_tb_line ON mapping_suggestions(trial_balance_line_id);
CREATE INDEX idx_mapping_suggestions_status ON mapping_suggestions(status);
CREATE INDEX idx_mapping_suggestions_confidence ON mapping_suggestions(confidence_score DESC);

-- Mapping history for training data
CREATE TABLE IF NOT EXISTS mapping_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,

    -- Source account
    source_account_code VARCHAR(100) NOT NULL,
    source_account_name VARCHAR(255) NOT NULL,
    source_account_balance NUMERIC(18,2),

    -- Mapped account
    mapped_account_code VARCHAR(50) NOT NULL,
    mapped_account_name VARCHAR(255) NOT NULL,

    -- Mapping details
    mapping_method VARCHAR(50),
    confidence_score NUMERIC(5,4),

    -- Audit trail
    mapped_by UUID NOT NULL REFERENCES users(id),
    mapped_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mapping_history_engagement ON mapping_history(engagement_id);
CREATE INDEX idx_mapping_history_source ON mapping_history(source_account_code, source_account_name);
CREATE INDEX idx_mapping_history_mapped ON mapping_history(mapped_account_code);
CREATE INDEX idx_mapping_history_method ON mapping_history(mapping_method);

-- =====================================================
-- SEED DATA: Standard Chart of Accounts
-- =====================================================

-- Insert standard GAAP chart of accounts
INSERT INTO chart_of_accounts (account_code, account_name, account_type, account_subtype, normal_balance, financial_statement, presentation_order, xbrl_concept, description) VALUES
-- Assets
('1000', 'Assets', 'asset', 'current', 'debit', 'balance_sheet', 10, 'us-gaap:Assets', 'Total Assets'),
('1100', 'Current Assets', 'asset', 'current', 'debit', 'balance_sheet', 11, 'us-gaap:AssetsCurrent', 'Current Assets'),
('1110', 'Cash and Cash Equivalents', 'asset', 'current', 'debit', 'balance_sheet', 12, 'us-gaap:CashAndCashEquivalentsAtCarryingValue', 'Cash and equivalents'),
('1120', 'Accounts Receivable', 'asset', 'current', 'debit', 'balance_sheet', 13, 'us-gaap:AccountsReceivableNetCurrent', 'Trade accounts receivable'),
('1130', 'Inventory', 'asset', 'current', 'debit', 'balance_sheet', 14, 'us-gaap:InventoryNet', 'Inventory at cost'),
('1140', 'Prepaid Expenses', 'asset', 'current', 'debit', 'balance_sheet', 15, 'us-gaap:PrepaidExpenseCurrent', 'Prepaid expenses'),
('1200', 'Non-Current Assets', 'asset', 'non-current', 'debit', 'balance_sheet', 20, 'us-gaap:AssetsNoncurrent', 'Non-current Assets'),
('1210', 'Property, Plant & Equipment', 'asset', 'non-current', 'debit', 'balance_sheet', 21, 'us-gaap:PropertyPlantAndEquipmentNet', 'PP&E net of depreciation'),
('1220', 'Intangible Assets', 'asset', 'non-current', 'debit', 'balance_sheet', 22, 'us-gaap:IntangibleAssetsNetExcludingGoodwill', 'Intangibles net of amortization'),
('1230', 'Goodwill', 'asset', 'non-current', 'debit', 'balance_sheet', 23, 'us-gaap:Goodwill', 'Goodwill'),

-- Liabilities
('2000', 'Liabilities', 'liability', 'current', 'credit', 'balance_sheet', 30, 'us-gaap:Liabilities', 'Total Liabilities'),
('2100', 'Current Liabilities', 'liability', 'current', 'credit', 'balance_sheet', 31, 'us-gaap:LiabilitiesCurrent', 'Current Liabilities'),
('2110', 'Accounts Payable', 'liability', 'current', 'credit', 'balance_sheet', 32, 'us-gaap:AccountsPayableCurrent', 'Trade accounts payable'),
('2120', 'Accrued Expenses', 'liability', 'current', 'credit', 'balance_sheet', 33, 'us-gaap:AccruedLiabilitiesCurrent', 'Accrued liabilities'),
('2130', 'Short-term Debt', 'liability', 'current', 'credit', 'balance_sheet', 34, 'us-gaap:ShortTermBorrowings', 'Short-term borrowings'),
('2200', 'Non-Current Liabilities', 'liability', 'non-current', 'credit', 'balance_sheet', 40, 'us-gaap:LiabilitiesNoncurrent', 'Non-current Liabilities'),
('2210', 'Long-term Debt', 'liability', 'non-current', 'credit', 'balance_sheet', 41, 'us-gaap:LongTermDebtNoncurrent', 'Long-term debt'),
('2220', 'Deferred Tax Liabilities', 'liability', 'non-current', 'credit', 'balance_sheet', 42, 'us-gaap:DeferredIncomeTaxLiabilitiesNet', 'Deferred taxes'),

-- Equity
('3000', 'Equity', 'equity', 'other', 'credit', 'balance_sheet', 50, 'us-gaap:StockholdersEquity', 'Total Equity'),
('3100', 'Common Stock', 'equity', 'common-stock', 'credit', 'balance_sheet', 51, 'us-gaap:CommonStockValue', 'Common stock'),
('3200', 'Retained Earnings', 'equity', 'retained-earnings', 'credit', 'balance_sheet', 52, 'us-gaap:RetainedEarningsAccumulatedDeficit', 'Retained earnings'),
('3300', 'Additional Paid-in Capital', 'equity', 'other', 'credit', 'balance_sheet', 53, 'us-gaap:AdditionalPaidInCapital', 'APIC'),

-- Revenue
('4000', 'Revenue', 'revenue', 'operating', 'credit', 'income_statement', 60, 'us-gaap:Revenues', 'Total Revenue'),
('4100', 'Product Revenue', 'revenue', 'operating', 'credit', 'income_statement', 61, 'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax', 'Product sales'),
('4200', 'Service Revenue', 'revenue', 'operating', 'credit', 'income_statement', 62, 'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax', 'Service revenue'),

-- Expenses
('5000', 'Cost of Revenue', 'expense', 'operating', 'debit', 'income_statement', 70, 'us-gaap:CostOfRevenue', 'Cost of goods/services sold'),
('6000', 'Operating Expenses', 'expense', 'operating', 'debit', 'income_statement', 80, 'us-gaap:OperatingExpenses', 'Operating expenses'),
('6100', 'Sales & Marketing', 'expense', 'operating', 'debit', 'income_statement', 81, 'us-gaap:SellingAndMarketingExpense', 'Sales and marketing'),
('6200', 'General & Administrative', 'expense', 'operating', 'debit', 'income_statement', 82, 'us-gaap:GeneralAndAdministrativeExpense', 'G&A expenses'),
('6300', 'Research & Development', 'expense', 'operating', 'debit', 'income_statement', 83, 'us-gaap:ResearchAndDevelopmentExpense', 'R&D expenses'),
('7000', 'Other Income/Expense', 'expense', 'non-operating', 'debit', 'income_statement', 90, 'us-gaap:NonoperatingIncomeExpense', 'Non-operating items'),
('7100', 'Interest Expense', 'expense', 'non-operating', 'debit', 'income_statement', 91, 'us-gaap:InterestExpense', 'Interest expense'),
('7200', 'Interest Income', 'revenue', 'non-operating', 'credit', 'income_statement', 92, 'us-gaap:InterestIncomeOther', 'Interest income'),
('8000', 'Income Tax Expense', 'expense', 'operating', 'debit', 'income_statement', 100, 'us-gaap:IncomeTaxExpenseBenefit', 'Income tax provision')
ON CONFLICT (account_code) DO NOTHING;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE filings IS 'SEC EDGAR filing metadata and source references';
COMMENT ON TABLE facts IS 'Individual XBRL facts (financial data points) from SEC filings';
COMMENT ON TABLE chart_of_accounts IS 'Standard GAAP-based chart of accounts with XBRL mappings';
COMMENT ON TABLE trial_balances IS 'Client trial balance imports from various sources';
COMMENT ON TABLE trial_balance_lines IS 'Individual trial balance line items';
COMMENT ON TABLE mapping_rules IS 'Pattern-based rules for account mapping';
COMMENT ON TABLE ml_models IS 'ML model versions for account mapping';
COMMENT ON TABLE mapping_suggestions IS 'AI-generated account mapping suggestions';
COMMENT ON TABLE mapping_history IS 'Historical account mappings for training data';
