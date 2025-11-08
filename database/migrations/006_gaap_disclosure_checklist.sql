-- ========================================
-- GAAP DISCLOSURE CHECKLIST SYSTEM
-- ASC Topic-by-Topic Disclosure Requirements
-- ========================================

SET search_path TO atlas;

-- ASC Topics (Accounting Standards Codification)
CREATE TYPE asc_topic_category AS ENUM (
    'presentation',
    'assets',
    'liabilities',
    'equity',
    'revenue',
    'expenses',
    'broad_transactions',
    'industry_specific'
);

-- Disclosure requirement levels
CREATE TYPE disclosure_requirement_level AS ENUM (
    'required',        -- Must include
    'conditional',     -- Required if applicable
    'recommended',     -- Best practice but not required
    'industry_specific'  -- Required for specific industries
);

-- ASC topics master table
CREATE TABLE IF NOT EXISTS asc_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_number VARCHAR(20) NOT NULL UNIQUE,  -- e.g., '606', '842', '326'
    topic_name VARCHAR(255) NOT NULL,          -- e.g., 'Revenue from Contracts with Customers'
    category asc_topic_category NOT NULL,
    description TEXT,
    effective_date DATE,
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_asc_topics_number ON asc_topics(topic_number);
CREATE INDEX idx_asc_topics_category ON asc_topics(category);

COMMENT ON TABLE asc_topics IS 'ASC (Accounting Standards Codification) topics';

-- Disclosure requirements table
CREATE TABLE IF NOT EXISTS disclosure_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asc_topic_id UUID NOT NULL REFERENCES asc_topics(id) ON DELETE CASCADE,

    requirement_code VARCHAR(50) NOT NULL,     -- e.g., '606-10-50-4'
    requirement_title VARCHAR(500) NOT NULL,
    requirement_description TEXT NOT NULL,
    requirement_level disclosure_requirement_level NOT NULL,

    -- Applicability
    applies_to_public BOOLEAN DEFAULT TRUE,
    applies_to_private BOOLEAN DEFAULT TRUE,
    applies_to_nonprofit BOOLEAN DEFAULT FALSE,

    -- Conditional logic
    condition_description TEXT,  -- When is this required?
    materiality_threshold VARCHAR(100),

    -- Template and examples
    disclosure_template TEXT,    -- Example note text
    example_disclosure TEXT,     -- Real-world example

    position_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_disclosure_requirements_topic ON disclosure_requirements(asc_topic_id);
CREATE INDEX idx_disclosure_requirements_code ON disclosure_requirements(requirement_code);
CREATE INDEX idx_disclosure_requirements_level ON disclosure_requirements(requirement_level);

COMMENT ON TABLE disclosure_requirements IS 'Specific disclosure requirements by ASC topic';

-- Engagement disclosure checklist (tracking)
CREATE TABLE IF NOT EXISTS engagement_disclosure_checklist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    disclosure_requirement_id UUID NOT NULL REFERENCES disclosure_requirements(id) ON DELETE CASCADE,

    -- Status
    is_applicable BOOLEAN,           -- Does this apply to this engagement?
    applicability_reason TEXT,       -- Why or why not?
    is_complete BOOLEAN DEFAULT FALSE,
    completion_status VARCHAR(50),   -- 'complete', 'in_progress', 'not_started', 'not_applicable'

    -- Content
    draft_disclosure TEXT,           -- Drafted note text
    final_disclosure TEXT,           -- Approved note text
    note_reference VARCHAR(100),     -- Which note is this in? (e.g., "Note 2")

    -- Review
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,
    requires_revision BOOLEAN DEFAULT FALSE,

    -- Audit trail
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_engagement_disclosure UNIQUE(engagement_id, disclosure_requirement_id)
);

CREATE INDEX idx_engagement_disclosure_engagement ON engagement_disclosure_checklist(engagement_id);
CREATE INDEX idx_engagement_disclosure_requirement ON engagement_disclosure_checklist(disclosure_requirement_id);
CREATE INDEX idx_engagement_disclosure_status ON engagement_disclosure_checklist(completion_status);

COMMENT ON TABLE engagement_disclosure_checklist IS 'Track disclosure completion for each engagement';

-- Financial statement note templates
CREATE TABLE IF NOT EXISTS financial_statement_note_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asc_topic_id UUID REFERENCES asc_topics(id) ON DELETE CASCADE,

    note_title VARCHAR(255) NOT NULL,
    note_number VARCHAR(20),           -- Typical note number (e.g., "Note 2")
    note_category VARCHAR(100),        -- 'significant_accounting_policies', 'asset', 'liability', etc.

    template_content TEXT NOT NULL,    -- Jinja2 template
    template_description TEXT,

    -- Metadata
    typical_position_order INTEGER,   -- Where this note typically appears
    is_standard BOOLEAN DEFAULT TRUE, -- Standard note vs custom
    is_active BOOLEAN DEFAULT TRUE,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_note_templates_topic ON financial_statement_note_templates(asc_topic_id);
CREATE INDEX idx_note_templates_category ON financial_statement_note_templates(note_category);

COMMENT ON TABLE financial_statement_note_templates IS 'Templates for drafting financial statement notes';

-- Seed ASC topics
INSERT INTO asc_topics (topic_number, topic_name, category, description) VALUES

-- Presentation
('205', 'Presentation of Financial Statements', 'presentation', 'Overall financial statement presentation requirements'),
('210', 'Balance Sheet', 'presentation', 'Balance sheet presentation and classification'),
('220', 'Income Statement', 'presentation', 'Income statement presentation'),
('230', 'Statement of Cash Flows', 'presentation', 'Cash flow statement requirements'),
('235', 'Notes to Financial Statements', 'presentation', 'General note disclosure requirements'),
('250', 'Accounting Changes and Error Corrections', 'presentation', 'Changes in accounting principles, estimates, and errors'),
('260', 'Earnings Per Share', 'presentation', 'EPS calculation and disclosure'),
('270', 'Interim Reporting', 'presentation', 'Interim financial statement requirements'),
('272', 'Limited Liability Entities', 'presentation', 'LLC-specific presentation'),
('280', 'Segment Reporting', 'presentation', 'Operating segment disclosures'),

-- Assets
('310', 'Receivables', 'assets', 'Accounts receivable, notes receivable, and related disclosures'),
('320', 'Investments - Debt Securities', 'assets', 'Debt security investments'),
('321', 'Investments - Equity Securities', 'assets', 'Equity security investments'),
('323', 'Investments - Equity Method and Joint Ventures', 'assets', 'Equity method investments'),
('325', 'Investments - Other', 'assets', 'Other investment types'),
('326', 'Financial Instruments - Credit Losses', 'assets', 'CECL (Current Expected Credit Loss) model'),
('330', 'Inventory', 'assets', 'Inventory valuation and disclosures'),
('340', 'Other Assets and Deferred Costs', 'assets', 'Prepaid expenses and other assets'),
('350', 'Intangibles - Goodwill and Other', 'assets', 'Goodwill and intangible asset accounting'),
('360', 'Property, Plant, and Equipment', 'assets', 'Fixed asset accounting'),

-- Liabilities
('405', 'Liabilities', 'liabilities', 'General liability recognition and measurement'),
('410', 'Asset Retirement and Environmental Obligations', 'liabilities', 'ARO and environmental liabilities'),
('420', 'Exit or Disposal Cost Obligations', 'liabilities', 'Restructuring and exit costs'),
('430', 'Deferred Revenue', 'liabilities', 'Deferred revenue and unearned income'),
('440', 'Commitments', 'liabilities', 'Commitment disclosures'),
('450', 'Contingencies', 'liabilities', 'Loss contingencies and gain contingencies'),
('460', 'Guarantees', 'liabilities', 'Guarantee disclosures'),
('470', 'Debt', 'liabilities', 'Short-term and long-term debt'),
('480', 'Distinguishing Liabilities from Equity', 'liabilities', 'Classification of financial instruments'),

-- Equity
('505', 'Equity', 'equity', 'Common stock, preferred stock, treasury stock, dividends'),

-- Revenue
('605', 'Revenue Recognition (Legacy)', 'revenue', 'Legacy revenue recognition (pre-ASC 606)'),
('606', 'Revenue from Contracts with Customers', 'revenue', 'New revenue recognition standard'),

-- Expenses
('710', 'Compensation - General', 'expenses', 'Employee compensation disclosures'),
('712', 'Compensation - Nonretirement Postemployment Benefits', 'expenses', 'Other postemployment benefits'),
('715', 'Compensation - Retirement Benefits', 'expenses', 'Pension and retirement plan accounting'),
('718', 'Compensation - Stock Compensation', 'expenses', 'Stock-based compensation'),
('720', 'Other Expenses', 'expenses', 'Other operating expenses'),
('740', 'Income Taxes', 'expenses', 'Income tax accounting and disclosures'),

-- Broad Transactions
('805', 'Business Combinations', 'broad_transactions', 'Acquisition accounting'),
('808', 'Collaborative Arrangements', 'broad_transactions', 'Collaborative arrangement disclosures'),
('810', 'Consolidation', 'broad_transactions', 'Consolidation requirements including VIEs'),
('815', 'Derivatives and Hedging', 'broad_transactions', 'Derivative instrument disclosures'),
('820', 'Fair Value Measurement', 'broad_transactions', 'Fair value measurement and Level 1/2/3 hierarchy'),
('825', 'Financial Instruments', 'broad_transactions', 'General financial instrument disclosures'),
('830', 'Foreign Currency Matters', 'broad_transactions', 'Foreign currency translation'),
('835', 'Interest', 'broad_transactions', 'Interest capitalization and imputation'),
('840', 'Leases (Legacy)', 'broad_transactions', 'Legacy lease accounting'),
('842', 'Leases', 'broad_transactions', 'New lease accounting standard'),
('850', 'Related Party Disclosures', 'broad_transactions', 'Related party transaction disclosures'),
('852', 'Reorganizations', 'broad_transactions', 'Bankruptcy and reorganization accounting'),
('855', 'Subsequent Events', 'broad_transactions', 'Subsequent event disclosures'),
('860', 'Transfers and Servicing', 'broad_transactions', 'Asset transfer accounting');

-- Seed key disclosure requirements for most common topics

-- ASC 606 - Revenue Recognition
INSERT INTO disclosure_requirements (
    asc_topic_id,
    requirement_code,
    requirement_title,
    requirement_description,
    requirement_level,
    applies_to_public,
    applies_to_private,
    disclosure_template,
    position_order
)
SELECT
    id AS asc_topic_id,
    '606-10-50-4',
    'Revenue Recognition - Performance Obligations',
    'Disclose information about contracts with customers, including: (a) when the entity typically satisfies its performance obligations, (b) significant payment terms, (c) nature of goods or services promised, (d) obligations for returns, refunds, and warranties, and (e) types of variable consideration.',
    'required',
    TRUE,
    TRUE,
    '<p>The Company recognizes revenue when control of goods or services is transferred to customers. Revenue is measured at the transaction price, which is the amount of consideration the Company expects to receive in exchange for transferring promised goods or services.</p>

<p><strong>Performance Obligations:</strong> {{performance_obligations_description}}</p>

<p><strong>Payment Terms:</strong> {{payment_terms}}</p>

<p><strong>Variable Consideration:</strong> {{variable_consideration_description}}</p>',
    10
FROM asc_topics WHERE topic_number = '606';

-- ASC 842 - Leases
INSERT INTO disclosure_requirements (
    asc_topic_id,
    requirement_code,
    requirement_title,
    requirement_description,
    requirement_level,
    applies_to_public,
    applies_to_private,
    disclosure_template,
    position_order
)
SELECT
    id AS asc_topic_id,
    '842-20-50-1',
    'Lessee Disclosures',
    'Disclose information about the nature of leases, including: (a) general description of leases, (b) lease cost, (c) weighted-average lease term and discount rate, (d) maturity analysis showing undiscounted cash flows.',
    'conditional',
    TRUE,
    TRUE,
    '<p>The Company leases {{lease_types}} under operating leases. Lease expense for these leases is recognized on a straight-line basis over the lease term.</p>

<p><strong>Total Lease Cost:</strong> ${{total_lease_cost}}</p>
<p><strong>Weighted-Average Remaining Lease Term:</strong> {{weighted_avg_term}} years</p>
<p><strong>Weighted-Average Discount Rate:</strong> {{discount_rate}}%</p>',
    10
FROM asc_topics WHERE topic_number = '842';

-- ASC 326 - Credit Losses (CECL)
INSERT INTO disclosure_requirements (
    asc_topic_id,
    requirement_code,
    requirement_title,
    requirement_description,
    requirement_level,
    applies_to_public,
    applies_to_private,
    disclosure_template,
    position_order
)
SELECT
    id AS asc_topic_id,
    '326-20-50-11',
    'Allowance for Credit Losses Rollforward',
    'Provide a rollforward of the allowance for credit losses, showing beginning balance, current-period provision, write-offs, recoveries, and ending balance.',
    'conditional',
    TRUE,
    FALSE,  -- Private companies can use simpler methods
    '<p>The Company maintains an allowance for credit losses based on expected losses over the life of the receivables.</p>

<table>
<tr><th>Allowance for Credit Losses</th><th>Amount</th></tr>
<tr><td>Balance, beginning of year</td><td>${{beginning_balance}}</td></tr>
<tr><td>Provision for credit losses</td><td>${{provision}}</td></tr>
<tr><td>Write-offs</td><td>{{writeoffs}}</td></tr>
<tr><td>Recoveries</td><td>${{recoveries}}</td></tr>
<tr><td>Balance, end of year</td><td>${{ending_balance}}</td></tr>
</table>',
    10
FROM asc_topics WHERE topic_number = '326';

-- ASC 740 - Income Taxes
INSERT INTO disclosure_requirements (
    asc_topic_id,
    requirement_code,
    requirement_title,
    requirement_description,
    requirement_level,
    applies_to_public,
    applies_to_private,
    disclosure_template,
    position_order
)
SELECT
    id AS asc_topic_id,
    '740-10-50-2',
    'Income Tax Provision Components',
    'Disclose the components of income tax expense or benefit, including: (a) current tax expense or benefit, (b) deferred tax expense or benefit, (c) investment tax credits, (d) government grants.',
    'required',
    TRUE,
    TRUE,
    '<p>Income tax expense consists of the following:</p>

<table>
<tr><th></th><th>{{current_year}}</th><th>{{prior_year}}</th></tr>
<tr><td>Current tax expense</td><td>${{current_tax_current}}</td><td>${{current_tax_prior}}</td></tr>
<tr><td>Deferred tax expense</td><td>${{deferred_tax_current}}</td><td>${{deferred_tax_prior}}</td></tr>
<tr><td>Total income tax expense</td><td>${{total_tax_current}}</td><td>${{total_tax_prior}}</td></tr>
</table>',
    10
FROM asc_topics WHERE topic_number = '740';

-- ASC 235 - Notes to Financial Statements (General)
INSERT INTO disclosure_requirements (
    asc_topic_id,
    requirement_code,
    requirement_title,
    requirement_description,
    requirement_level,
    applies_to_public,
    applies_to_private,
    disclosure_template,
    position_order
)
SELECT
    id AS asc_topic_id,
    '235-10-50-1',
    'Significant Accounting Policies',
    'Disclose accounting policies that are significant to the financial statements, including: (a) measurement basis, (b) principles and methods, (c) policies specific to the industry.',
    'required',
    TRUE,
    TRUE,
    '<h3>Note 1 - Significant Accounting Policies</h3>

<p><strong>Basis of Presentation:</strong> {{basis_of_presentation}}</p>

<p><strong>Use of Estimates:</strong> The preparation of financial statements in conformity with GAAP requires management to make estimates and assumptions that affect reported amounts. Actual results could differ from those estimates.</p>

<p><strong>Cash and Cash Equivalents:</strong> {{cash_policy}}</p>

<p><strong>Revenue Recognition:</strong> {{revenue_policy}}</p>

<p><strong>Inventory:</strong> {{inventory_policy}}</p>

<p><strong>Property and Equipment:</strong> {{ppe_policy}}</p>',
    1
FROM asc_topics WHERE topic_number = '235';

-- ASC 850 - Related Party Transactions
INSERT INTO disclosure_requirements (
    asc_topic_id,
    requirement_code,
    requirement_title,
    requirement_description,
    requirement_level,
    applies_to_public,
    applies_to_private,
    disclosure_template,
    position_order
)
SELECT
    id AS asc_topic_id,
    '850-10-50-1',
    'Related Party Transaction Disclosures',
    'Disclose material related party transactions, including: (a) nature of relationship, (b) description of transactions, (c) dollar amounts, (d) amounts due to/from related parties.',
    'conditional',
    TRUE,
    TRUE,
    '<p>The Company entered into the following transactions with related parties:</p>

<p><strong>Nature of Relationship:</strong> {{relationship_description}}</p>

<p><strong>Description of Transactions:</strong> {{transaction_description}}</p>

<p><strong>Amounts:</strong></p>
<ul>
<li>Revenue from related parties: ${{related_party_revenue}}</li>
<li>Expenses to related parties: ${{related_party_expenses}}</li>
<li>Amounts due from related parties: ${{amounts_due_from}}</li>
<li>Amounts due to related parties: ${{amounts_due_to}}</li>
</ul>',
    50
FROM asc_topics WHERE topic_number = '850';

-- ASC 855 - Subsequent Events
INSERT INTO disclosure_requirements (
    asc_topic_id,
    requirement_code,
    requirement_title,
    requirement_description,
    requirement_level,
    applies_to_public,
    applies_to_private,
    disclosure_template,
    position_order
)
SELECT
    id AS asc_topic_id,
    '855-10-50-2',
    'Subsequent Events Through Financial Statement Availability Date',
    'Disclose the date through which subsequent events have been evaluated and whether that date represents the date the financial statements were issued or were available to be issued.',
    'required',
    TRUE,
    TRUE,
    '<p>The Company has evaluated subsequent events through {{evaluation_date}}, the date the financial statements were {{issued_or_available}}.</p>

<p>{{subsequent_events_description}}</p>',
    100
FROM asc_topics WHERE topic_number = '855';

-- Seed note templates
INSERT INTO financial_statement_note_templates (
    asc_topic_id,
    note_title,
    note_number,
    note_category,
    template_content,
    typical_position_order
)
SELECT
    id,
    'Organization and Summary of Significant Accounting Policies',
    'Note 1',
    'significant_accounting_policies',
    '<h3>Note 1 - Organization and Summary of Significant Accounting Policies</h3>

<h4>Organization</h4>
<p>{{company_name}} (the "Company") was {{incorporation_details}}. The Company''s principal business activities include {{business_description}}.</p>

<h4>Basis of Presentation</h4>
<p>The accompanying financial statements have been prepared in accordance with accounting principles generally accepted in the United States of America (GAAP).</p>

<h4>Use of Estimates</h4>
<p>The preparation of financial statements in conformity with GAAP requires management to make estimates and assumptions that affect the reported amounts of assets and liabilities and disclosure of contingent assets and liabilities at the date of the financial statements and the reported amounts of revenues and expenses during the reporting period. Actual results could differ from those estimates.</p>

<h4>Cash and Cash Equivalents</h4>
<p>The Company considers all highly liquid investments with original maturities of three months or less to be cash equivalents.</p>

<h4>Accounts Receivable</h4>
<p>{{accounts_receivable_policy}}</p>

<h4>Inventory</h4>
<p>{{inventory_policy}}</p>

<h4>Property and Equipment</h4>
<p>{{ppe_policy}}</p>

<h4>Revenue Recognition</h4>
<p>{{revenue_recognition_policy}}</p>

<h4>Income Taxes</h4>
<p>{{income_tax_policy}}</p>',
    1
FROM asc_topics WHERE topic_number = '235';

-- View: Disclosure completeness by engagement
CREATE OR REPLACE VIEW engagement_disclosure_completeness AS
SELECT
    e.id AS engagement_id,
    e.client_name,
    e.engagement_type,
    COUNT(dr.id) AS total_requirements,
    COUNT(CASE WHEN edc.is_applicable = TRUE THEN 1 END) AS applicable_requirements,
    COUNT(CASE WHEN edc.is_applicable = TRUE AND edc.is_complete = TRUE THEN 1 END) AS completed_requirements,
    COUNT(CASE WHEN edc.is_applicable = TRUE AND edc.is_complete = FALSE THEN 1 END) AS incomplete_requirements,
    ROUND(
        100.0 * COUNT(CASE WHEN edc.is_applicable = TRUE AND edc.is_complete = TRUE THEN 1 END) /
        NULLIF(COUNT(CASE WHEN edc.is_applicable = TRUE THEN 1 END), 0),
        2
    ) AS completion_percentage
FROM engagements e
CROSS JOIN disclosure_requirements dr
LEFT JOIN engagement_disclosure_checklist edc ON edc.engagement_id = e.id AND edc.disclosure_requirement_id = dr.id
WHERE dr.is_active = TRUE
GROUP BY e.id, e.client_name, e.engagement_type;

COMMENT ON VIEW engagement_disclosure_completeness IS 'Disclosure checklist completion status by engagement';
