-- ========================================
-- CONFIRMATION TRACKING SYSTEM
-- For A/R, A/P, Bank, and Attorney Confirmations
-- ========================================

SET search_path TO atlas;

-- Confirmation types enum
CREATE TYPE confirmation_type AS ENUM (
    'accounts_receivable',
    'accounts_payable',
    'bank',
    'attorney',
    'debt',
    'inventory_consignment',
    'other'
);

-- Confirmation status enum
CREATE TYPE confirmation_status AS ENUM (
    'not_sent',
    'sent',
    'received',
    'exception',
    'resolved',
    'alternative_procedures'
);

-- Response type enum
CREATE TYPE confirmation_response_type AS ENUM (
    'positive',
    'negative',
    'blank'
);

-- Confirmations master table
CREATE TABLE IF NOT EXISTS confirmations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    confirmation_type confirmation_type NOT NULL,

    -- Entity being confirmed
    entity_name VARCHAR(255) NOT NULL,
    entity_contact VARCHAR(255),
    entity_email VARCHAR(255),
    entity_address TEXT,

    -- Confirmation details
    confirmation_date DATE,
    as_of_date DATE NOT NULL,
    amount DECIMAL(18,2),
    account_number VARCHAR(100),

    -- Status tracking
    status confirmation_status NOT NULL DEFAULT 'not_sent',
    response_type confirmation_response_type,
    sent_date DATE,
    received_date DATE,
    follow_up_count INTEGER DEFAULT 0,

    -- Response details
    confirmed_amount DECIMAL(18,2),
    difference_amount DECIMAL(18,2),
    has_exception BOOLEAN DEFAULT FALSE,
    exception_description TEXT,
    exception_resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,

    -- Alternative procedures (if confirmation not received)
    alternative_procedures_performed BOOLEAN DEFAULT FALSE,
    alternative_procedures_description TEXT,
    alternative_procedures_workpaper_id UUID,

    -- Document references
    confirmation_letter_s3_uri TEXT,
    response_document_s3_uri TEXT,
    workpaper_id UUID REFERENCES binder_nodes(id),

    -- Audit trail
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,

    -- Index for performance
    CONSTRAINT confirmations_engagement_idx
        FOREIGN KEY (engagement_id) REFERENCES engagements(id) ON DELETE CASCADE
);

CREATE INDEX idx_confirmations_engagement ON confirmations(engagement_id);
CREATE INDEX idx_confirmations_type ON confirmations(confirmation_type);
CREATE INDEX idx_confirmations_status ON confirmations(status);
CREATE INDEX idx_confirmations_entity ON confirmations(entity_name);

COMMENT ON TABLE confirmations IS 'External confirmation tracking for A/R, bank, attorney, and other confirmations';

-- Confirmation templates
CREATE TABLE IF NOT EXISTS confirmation_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    confirmation_type confirmation_type NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    template_description TEXT,

    -- Template content
    subject_line VARCHAR(500),
    body_template TEXT NOT NULL,  -- HTML template with placeholders

    -- Configuration
    requires_signature BOOLEAN DEFAULT TRUE,
    response_deadline_days INTEGER DEFAULT 14,
    follow_up_frequency_days INTEGER DEFAULT 7,
    max_follow_ups INTEGER DEFAULT 2,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_confirmation_templates_type ON confirmation_templates(confirmation_type);

COMMENT ON TABLE confirmation_templates IS 'Letter templates for various confirmation types';

-- Confirmation exceptions (when amounts don't match)
CREATE TABLE IF NOT EXISTS confirmation_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    confirmation_id UUID NOT NULL REFERENCES confirmations(id) ON DELETE CASCADE,

    -- Exception details
    exception_type VARCHAR(100) NOT NULL,  -- timing, amount, existence, other
    description TEXT NOT NULL,
    amount_difference DECIMAL(18,2),

    -- Disposition
    disposition VARCHAR(100),  -- timing_difference, posting_error, valid_adjustment, other
    disposition_notes TEXT,
    requires_adjustment BOOLEAN DEFAULT FALSE,
    adjustment_amount DECIMAL(18,2),

    -- Resolution
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_confirmation_exceptions_confirmation ON confirmation_exceptions(confirmation_id);

COMMENT ON TABLE confirmation_exceptions IS 'Exceptions identified from confirmation responses';

-- Seed default confirmation templates
INSERT INTO confirmation_templates (confirmation_type, template_name, subject_line, body_template, is_default) VALUES

-- A/R Positive Confirmation
('accounts_receivable', 'Standard A/R Positive Confirmation',
'Request for Confirmation of Account Balance',
'<html>
<body>
<p>Dear {{entity_name}},</p>

<p>Our auditors, {{auditor_firm_name}}, are conducting an audit of our financial statements.
In connection with this audit, please confirm directly to our auditors the balance of our account
with you as of {{as_of_date}}.</p>

<p><strong>Our records indicate a balance of {{amount}} as of {{as_of_date}}.</strong></p>

<p>If this amount <strong>agrees</strong> with your records, please sign and date this letter in the space
provided below and return it directly to our auditors in the enclosed envelope.</p>

<p>If this amount does <strong>not agree</strong> with your records, please provide details of any
differences in the space below.</p>

<p>This is not a request for payment. Please send your reply directly to our auditors, not to us.</p>

<p>Sincerely,<br>
{{client_company_name}}<br>
{{client_contact_name}}, {{client_contact_title}}</p>

<hr>

<p>TO: {{auditor_firm_name}}<br>
{{auditor_address}}</p>

<p>☐ The balance of {{amount}} as of {{as_of_date}} is <strong>correct</strong>.</p>

<p>☐ The balance is <strong>not correct</strong>. Please see details below:</p>

<p>_________________________________________________________________</p>

<p>Signature: __________________ Date: __________</p>
<p>Name: ____________________ Title: __________</p>
</body>
</html>', TRUE),

-- Bank Confirmation (Standard)
('bank', 'Standard Bank Confirmation',
'Bank Confirmation Request',
'<html>
<body>
<p>Dear {{entity_name}},</p>

<p>Our auditors, {{auditor_firm_name}}, are conducting an audit of our financial statements.
Please provide the following information directly to our auditors as of the close of business
on {{as_of_date}}:</p>

<h3>1. Deposits and loan balances:</h3>
<p>Account Name: {{client_company_name}}<br>
Account Number: {{account_number}}</p>

<table border="1" cellpadding="5">
<tr><th>Account Description</th><th>Balance</th><th>Interest Rate</th></tr>
<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
</table>

<h3>2. Loans and contingent liabilities:</h3>
<table border="1" cellpadding="5">
<tr><th>Description</th><th>Principal Balance</th><th>Interest Rate</th><th>Maturity Date</th></tr>
<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
</table>

<h3>3. Other deposit accounts, safe deposit boxes, or custodial arrangements?</h3>
<p>☐ Yes ☐ No    If yes, please describe: _________________________</p>

<h3>4. Outstanding letters of credit:</h3>
<p>☐ None  ☐ See below:</p>

<p>Please mail your response directly to our auditors at the address below.</p>

<p>Authorized Signature: ____________________</p>
<p>{{client_company_name}}<br>
{{client_contact_name}}, {{client_contact_title}}</p>

<hr>

<p>TO: {{auditor_firm_name}}<br>
{{auditor_address}}</p>
</body>
</html>', TRUE),

-- Attorney Letter
('attorney', 'Standard Attorney Letter (Inquiry)',
'Legal Representation Letter',
'<html>
<body>
<p>{{as_of_date}}</p>

<p>{{entity_name}}<br>
{{entity_address}}</p>

<p>Dear {{entity_contact}}:</p>

<p>In connection with an audit of our financial statements at {{as_of_date}} and for the year then ended,
please furnish to our auditors, {{auditor_firm_name}}, {{auditor_address}}, the information requested below
concerning certain contingencies involving matters with respect to which you have been engaged and to which
you have devoted substantive attention on behalf of the company in the form of legal consultation or representation.</p>

<p>Your response should include matters that existed at {{as_of_date}}, and during the period from that date
to the date of your response.</p>

<h3>Pending or Threatened Litigation</h3>
<p>Please provide a description and evaluation of pending or threatened litigation, claims, and assessments, including:</p>
<ul>
<li>The nature of the matter</li>
<li>The progress of the matter to date</li>
<li>How management is responding or intends to respond</li>
<li>An evaluation of the likelihood of an unfavorable outcome</li>
<li>An estimate, if one can be made, of the amount or range of potential loss</li>
</ul>

<h3>Unasserted Claims</h3>
<p>Please identify and describe unasserted possible claims or assessments that you consider to be probable of
assertion and that, if asserted, would have at least a reasonable possibility of an unfavorable outcome.</p>

<h3>Other Matters</h3>
<p>Please include any other matters, including but not limited to legal fees, that may be relevant to the audit.</p>

<p>Your response should be sent directly to our auditors. We understand that your response is subject to the
inherent uncertainties involved in litigation and that it represents your professional judgment.</p>

<p>Very truly yours,</p>

<p>{{client_company_name}}<br>
{{client_contact_name}}, {{client_contact_title}}</p>
</body>
</html>', TRUE);

COMMENT ON TABLE confirmation_templates IS 'Standard confirmation letter templates';

-- Confirmation statistics view
CREATE OR REPLACE VIEW confirmation_summary AS
SELECT
    e.id AS engagement_id,
    e.client_name,
    c.confirmation_type,
    COUNT(*) AS total_confirmations,
    SUM(CASE WHEN c.status = 'sent' THEN 1 ELSE 0 END) AS sent_count,
    SUM(CASE WHEN c.status = 'received' THEN 1 ELSE 0 END) AS received_count,
    SUM(CASE WHEN c.has_exception THEN 1 ELSE 0 END) AS exception_count,
    SUM(CASE WHEN c.alternative_procedures_performed THEN 1 ELSE 0 END) AS alternative_procedures_count,
    ROUND(100.0 * SUM(CASE WHEN c.status = 'received' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS response_rate_pct
FROM engagements e
LEFT JOIN confirmations c ON c.engagement_id = e.id
GROUP BY e.id, e.client_name, c.confirmation_type;

COMMENT ON VIEW confirmation_summary IS 'Confirmation statistics by engagement and type';
