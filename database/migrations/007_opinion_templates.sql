-- ========================================
-- AUDIT & ATTEST REPORT OPINION TEMPLATES
-- For Audit, Review, and Compilation Reports
-- ========================================

SET search_path TO atlas;

-- Opinion types
CREATE TYPE opinion_type AS ENUM (
    'unqualified',              -- Clean audit opinion
    'qualified_scope',          -- Qualified due to scope limitation
    'qualified_gaap',           -- Qualified due to GAAP departure
    'adverse',                  -- Adverse opinion
    'disclaimer',               -- Disclaimer of opinion
    'review_standard',          -- Standard SSARS review report
    'review_departure',         -- Review with GAAP departure
    'compilation_standard',     -- Standard SSARS compilation report
    'compilation_noindependence' -- Compilation without independence
);

-- Report sections
CREATE TYPE report_section_type AS ENUM (
    'opinion',                  -- Opinion paragraph
    'basis_for_opinion',        -- Basis for opinion
    'emphasis_of_matter',       -- Emphasis of matter paragraph
    'other_matter',             -- Other matter paragraph
    'responsibilities_management', -- Management's responsibilities
    'responsibilities_auditor',    -- Auditor's responsibilities
    'key_audit_matters',        -- KAMs (for public companies)
    'going_concern',            -- Going concern paragraph
    'other_information'         -- Other information paragraph
);

-- Opinion paragraph templates
CREATE TABLE IF NOT EXISTS opinion_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    template_name VARCHAR(255) NOT NULL,
    opinion_type opinion_type NOT NULL,
    engagement_type VARCHAR(50) NOT NULL,  -- 'audit', 'review', 'compilation'

    -- Template sections
    opinion_paragraph TEXT NOT NULL,
    basis_paragraph TEXT,
    responsibilities_management_paragraph TEXT,
    responsibilities_auditor_paragraph TEXT,

    -- Additional sections
    emphasis_of_matter_template TEXT,
    other_matter_template TEXT,
    going_concern_template TEXT,

    -- Report metadata
    report_title VARCHAR(255) NOT NULL,
    addressee_default VARCHAR(255),  -- e.g., "Board of Directors and Shareholders"

    -- Applicability
    applies_to_public BOOLEAN DEFAULT TRUE,
    applies_to_private BOOLEAN DEFAULT TRUE,
    applies_to_nonprofit BOOLEAN DEFAULT FALSE,

    is_standard BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_opinion_templates_type ON opinion_templates(opinion_type);
CREATE INDEX idx_opinion_templates_engagement ON opinion_templates(engagement_type);

COMMENT ON TABLE opinion_templates IS 'Templates for audit, review, and compilation report opinions';

-- Report modifications/paragraphs
CREATE TABLE IF NOT EXISTS report_modifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    modification_type report_section_type NOT NULL,
    modification_name VARCHAR(255) NOT NULL,
    modification_reason VARCHAR(500),  -- When to use this

    paragraph_template TEXT NOT NULL,

    position_order INTEGER,  -- Where in report
    is_standard BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_report_modifications_type ON report_modifications(modification_type);

COMMENT ON TABLE report_modifications IS 'Standard paragraphs for report modifications';

-- Engagement report tracking
CREATE TABLE IF NOT EXISTS engagement_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,

    report_type VARCHAR(50) NOT NULL,  -- 'audit', 'review', 'compilation'
    opinion_type opinion_type NOT NULL,

    -- Report content
    report_title VARCHAR(255) NOT NULL,
    report_date DATE NOT NULL,
    addressee TEXT NOT NULL,

    -- Opinion sections
    opinion_paragraph TEXT NOT NULL,
    basis_paragraph TEXT,
    responsibilities_management_paragraph TEXT,
    responsibilities_auditor_paragraph TEXT,

    -- Modifications
    emphasis_of_matter_paragraph TEXT,
    other_matter_paragraph TEXT,
    going_concern_paragraph TEXT,

    -- Signature
    firm_name VARCHAR(255) NOT NULL,
    firm_address TEXT,
    partner_name VARCHAR(255),
    partner_title VARCHAR(100),

    -- Status
    status VARCHAR(50) DEFAULT 'draft',  -- 'draft', 'under_review', 'approved', 'issued'
    draft_number INTEGER DEFAULT 1,

    -- Approval workflow
    drafted_by UUID REFERENCES users(id),
    drafted_at TIMESTAMPTZ,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    issued_at TIMESTAMPTZ,

    -- Document storage
    draft_document_s3_uri TEXT,
    final_document_s3_uri TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_engagement_reports_engagement ON engagement_reports(engagement_id);
CREATE INDEX idx_engagement_reports_type ON engagement_reports(report_type);
CREATE INDEX idx_engagement_reports_status ON engagement_reports(status);

COMMENT ON TABLE engagement_reports IS 'Generated audit/review/compilation reports';

-- ========================================
-- SEED STANDARD OPINION TEMPLATES
-- ========================================

-- AUDIT: Unqualified Opinion (Clean)
INSERT INTO opinion_templates (
    template_name,
    opinion_type,
    engagement_type,
    report_title,
    addressee_default,
    opinion_paragraph,
    basis_paragraph,
    responsibilities_management_paragraph,
    responsibilities_auditor_paragraph,
    applies_to_public,
    applies_to_private,
    is_standard
) VALUES (
    'Standard Unqualified Audit Opinion',
    'unqualified',
    'audit',
    'Independent Auditor''s Report',
    'Board of Directors and Shareholders',

    -- Opinion paragraph
    '<h3>Opinion</h3>
<p>We have audited the financial statements of {{client_name}}, which comprise the balance sheet as of {{balance_sheet_date}}, and the related statements of income, changes in stockholders'' equity, and cash flows for the year then ended, and the related notes to the financial statements.</p>

<p>In our opinion, the accompanying financial statements present fairly, in all material respects, the financial position of {{client_name}} as of {{balance_sheet_date}}, and the results of its operations and its cash flows for the year then ended in accordance with accounting principles generally accepted in the United States of America.</p>',

    -- Basis paragraph
    '<h3>Basis for Opinion</h3>
<p>We conducted our audit in accordance with auditing standards generally accepted in the United States of America (GAAS). Our responsibilities under those standards are further described in the Auditor''s Responsibilities for the Audit of the Financial Statements section of our report. We are required to be independent of {{client_name}} and to meet our other ethical responsibilities, in accordance with the relevant ethical requirements relating to our audit. We believe that the audit evidence we have obtained is sufficient and appropriate to provide a basis for our audit opinion.</p>',

    -- Management responsibilities
    '<h3>Responsibilities of Management for the Financial Statements</h3>
<p>Management is responsible for the preparation and fair presentation of the financial statements in accordance with accounting principles generally accepted in the United States of America, and for the design, implementation, and maintenance of internal control relevant to the preparation and fair presentation of financial statements that are free from material misstatement, whether due to fraud or error.</p>

<p>In preparing the financial statements, management is required to evaluate whether there are conditions or events, considered in the aggregate, that raise substantial doubt about {{client_name}}''s ability to continue as a going concern for one year after the date that the financial statements are available to be issued.</p>',

    -- Auditor responsibilities
    '<h3>Auditor''s Responsibilities for the Audit of the Financial Statements</h3>
<p>Our objectives are to obtain reasonable assurance about whether the financial statements as a whole are free from material misstatement, whether due to fraud or error, and to issue an auditor''s report that includes our opinion. Reasonable assurance is a high level of assurance but is not absolute assurance and therefore is not a guarantee that an audit conducted in accordance with GAAS will always detect a material misstatement when it exists. The risk of not detecting a material misstatement resulting from fraud is higher than for one resulting from error, as fraud may involve collusion, forgery, intentional omissions, misrepresentations, or the override of internal control. Misstatements are considered material if there is a substantial likelihood that, individually or in the aggregate, they would influence the judgment made by a reasonable user based on the financial statements.</p>

<p>In performing an audit in accordance with GAAS, we:</p>
<ul>
<li>Exercise professional judgment and maintain professional skepticism throughout the audit.</li>
<li>Identify and assess the risks of material misstatement of the financial statements, whether due to fraud or error, and design and perform audit procedures responsive to those risks. Such procedures include examining, on a test basis, evidence regarding the amounts and disclosures in the financial statements.</li>
<li>Obtain an understanding of internal control relevant to the audit in order to design audit procedures that are appropriate in the circumstances, but not for the purpose of expressing an opinion on the effectiveness of {{client_name}}''s internal control. Accordingly, no such opinion is expressed.</li>
<li>Evaluate the appropriateness of accounting policies used and the reasonableness of significant accounting estimates made by management, as well as evaluate the overall presentation of the financial statements.</li>
<li>Conclude whether, in our judgment, there are conditions or events, considered in the aggregate, that raise substantial doubt about {{client_name}}''s ability to continue as a going concern for a reasonable period of time.</li>
</ul>

<p>We are required to communicate with those charged with governance regarding, among other matters, the planned scope and timing of the audit, significant audit findings, and certain internal control–related matters that we identified during the audit.</p>',

    TRUE,
    TRUE,
    TRUE
);

-- AUDIT: Qualified Opinion - Scope Limitation
INSERT INTO opinion_templates (
    template_name,
    opinion_type,
    engagement_type,
    report_title,
    opinion_paragraph,
    basis_paragraph
) VALUES (
    'Qualified Audit Opinion - Scope Limitation',
    'qualified_scope',
    'audit',
    'Independent Auditor''s Report',

    -- Opinion paragraph
    '<h3>Qualified Opinion</h3>
<p>We have audited the financial statements of {{client_name}}, which comprise the balance sheet as of {{balance_sheet_date}}, and the related statements of income, changes in stockholders'' equity, and cash flows for the year then ended, and the related notes to the financial statements.</p>

<p>In our opinion, except for the possible effects of the matter described in the Basis for Qualified Opinion section of our report, the financial statements referred to above present fairly, in all material respects, the financial position of {{client_name}} as of {{balance_sheet_date}}, and the results of its operations and its cash flows for the year then ended in accordance with accounting principles generally accepted in the United States of America.</p>',

    -- Basis paragraph
    '<h3>Basis for Qualified Opinion</h3>
<p>{{scope_limitation_description}}</p>

<p>We were unable to obtain sufficient appropriate audit evidence about {{scope_limitation_detail}}. Consequently, we were unable to determine whether any adjustments to these amounts were necessary.</p>'
);

-- AUDIT: Adverse Opinion
INSERT INTO opinion_templates (
    template_name,
    opinion_type,
    engagement_type,
    report_title,
    opinion_paragraph,
    basis_paragraph
) VALUES (
    'Adverse Audit Opinion',
    'adverse',
    'audit',
    'Independent Auditor''s Report',

    -- Opinion paragraph
    '<h3>Adverse Opinion</h3>
<p>We have audited the financial statements of {{client_name}}, which comprise the balance sheet as of {{balance_sheet_date}}, and the related statements of income, changes in stockholders'' equity, and cash flows for the year then ended, and the related notes to the financial statements.</p>

<p>In our opinion, because of the significance of the matter discussed in the Basis for Adverse Opinion section of our report, the financial statements referred to above do not present fairly the financial position of {{client_name}} as of {{balance_sheet_date}}, or the results of its operations and its cash flows for the year then ended in accordance with accounting principles generally accepted in the United States of America.</p>',

    -- Basis paragraph
    '<h3>Basis for Adverse Opinion</h3>
<p>{{gaap_departure_description}}</p>

<p>The effects of this departure from accounting principles generally accepted in the United States of America on the financial statements are both material and pervasive.</p>'
);

-- REVIEW: Standard Review Report (SSARS)
INSERT INTO opinion_templates (
    template_name,
    opinion_type,
    engagement_type,
    report_title,
    opinion_paragraph,
    responsibilities_management_paragraph,
    responsibilities_auditor_paragraph
) VALUES (
    'Standard Review Report (SSARS)',
    'review_standard',
    'review',
    'Independent Accountant''s Review Report',

    -- Review conclusion paragraph
    '<h3>Accountant''s Conclusion</h3>
<p>We have reviewed the accompanying financial statements of {{client_name}}, which comprise the balance sheet as of {{balance_sheet_date}}, and the related statements of income, changes in stockholders'' equity, and cash flows for the year then ended, and the related notes to the financial statements.</p>

<p>Based on our review, we are not aware of any material modifications that should be made to the accompanying financial statements in order for them to be in accordance with accounting principles generally accepted in the United States of America.</p>',

    -- Management responsibilities
    '<h3>Responsibilities of Management for the Financial Statements</h3>
<p>Management is responsible for the preparation and fair presentation of these financial statements in accordance with accounting principles generally accepted in the United States of America; this includes the design, implementation, and maintenance of internal control relevant to the preparation and fair presentation of financial statements that are free from material misstatement whether due to fraud or error.</p>',

    -- Accountant responsibilities
    '<h3>Accountant''s Responsibility</h3>
<p>Our responsibility is to conduct the review engagement in accordance with Statements on Standards for Accounting and Review Services promulgated by the Accounting and Review Services Committee of the AICPA. Those standards require that we perform procedures to obtain limited assurance as a basis for reporting whether we are aware of any material modifications that should be made to the financial statements for them to be in accordance with accounting principles generally accepted in the United States of America. We believe that the results of our procedures provide a reasonable basis for our conclusion.</p>

<p>We are required to be independent of {{client_name}} and to meet our other ethical responsibilities, in accordance with the relevant ethical requirements related to our review.</p>

<p>A review of financial statements in accordance with Statements on Standards for Accounting and Review Services is substantially less in scope than an audit, the objective of which is the expression of an opinion regarding the financial statements as a whole. Accordingly, we do not express such an opinion.</p>'
);

-- COMPILATION: Standard Compilation Report (SSARS)
INSERT INTO opinion_templates (
    template_name,
    opinion_type,
    engagement_type,
    report_title,
    opinion_paragraph,
    responsibilities_management_paragraph
) VALUES (
    'Standard Compilation Report (SSARS)',
    'compilation_standard',
    'compilation',
    'Accountant''s Compilation Report',

    -- Compilation paragraph (no opinion)
    '<h3>Accountant''s Compilation Report</h3>
<p>We have compiled the accompanying financial statements of {{client_name}}, which comprise the balance sheet as of {{balance_sheet_date}}, and the related statements of income, changes in stockholders'' equity, and cash flows for the year then ended, and the related notes to the financial statements. We have not audited or reviewed the accompanying financial statements and, accordingly, do not express an opinion or provide any assurance about whether the financial statements are in accordance with accounting principles generally accepted in the United States of America.</p>',

    -- Management responsibilities
    '<h3>Management''s Responsibility for the Financial Statements</h3>
<p>Management is responsible for the preparation and fair presentation of these financial statements in accordance with accounting principles generally accepted in the United States of America and for designing, implementing, and maintaining internal control relevant to the preparation and fair presentation of the financial statements.</p>

<h3>Accountant''s Responsibility</h3>
<p>Our responsibility is to conduct the compilation engagement in accordance with Statements on Standards for Accounting and Review Services promulgated by the Accounting and Review Services Committee of the AICPA. The objective of a compilation is to assist management in presenting financial information in the form of financial statements without undertaking to obtain or provide any assurance that there are no material modifications that should be made to the financial statements in order for them to be in accordance with the applicable financial reporting framework.</p>'
);

-- ========================================
-- SEED STANDARD REPORT MODIFICATIONS
-- ========================================

-- Emphasis of Matter - Going Concern (no modification to opinion)
INSERT INTO report_modifications (
    modification_type,
    modification_name,
    modification_reason,
    paragraph_template,
    position_order
) VALUES (
    'emphasis_of_matter',
    'Going Concern - Emphasis of Matter',
    'Use when substantial doubt exists but financial statements adequately disclose the matter',
    '<h3>Emphasis of Matter</h3>
<p>The accompanying financial statements have been prepared assuming that {{client_name}} will continue as a going concern. As discussed in Note {{note_reference}} to the financial statements, {{going_concern_description}}, which raises substantial doubt about its ability to continue as a going concern. Management''s plans in regard to these matters are also described in Note {{note_reference}}. The financial statements do not include any adjustments that might result from the outcome of this uncertainty. Our opinion is not modified with respect to this matter.</p>',
    50
);

-- Going Concern - Qualified Opinion
INSERT INTO report_modifications (
    modification_type,
    modification_name,
    modification_reason,
    paragraph_template,
    position_order
) VALUES (
    'going_concern',
    'Going Concern - Inadequate Disclosure',
    'Use when substantial doubt exists and disclosure is inadequate',
    '<h3>Basis for Qualified Opinion</h3>
<p>As discussed in Note {{note_reference}}, {{going_concern_description}}. This raises substantial doubt about the entity''s ability to continue as a going concern. The financial statements do not adequately disclose this matter.</p>

<h3>Qualified Opinion</h3>
<p>In our opinion, except for the incomplete disclosure of the information discussed in the Basis for Qualified Opinion section, the financial statements present fairly, in all material respects...</p>',
    40
);

-- Other Matter - Comparative Financial Statements
INSERT INTO report_modifications (
    modification_type,
    modification_name,
    modification_reason,
    paragraph_template,
    position_order
) VALUES (
    'other_matter',
    'Comparative Financial Statements - Prior Year Not Audited',
    'Use when current year is audited but prior year was reviewed or compiled',
    '<h3>Other Matter</h3>
<p>The financial statements of {{client_name}} as of {{prior_year_date}} were {{prior_year_service_type}} by us (or other accountants), and we (they) expressed {{prior_year_opinion_type}} on those financial statements in our (their) report dated {{prior_year_report_date}}.</p>',
    60
);

-- Key Audit Matters (for public companies)
INSERT INTO report_modifications (
    modification_type,
    modification_name,
    modification_reason,
    paragraph_template,
    position_order
) VALUES (
    'key_audit_matters',
    'Key Audit Matters',
    'Required for audits of listed entities in some jurisdictions',
    '<h3>Key Audit Matters</h3>
<p>Key audit matters are those matters that, in our professional judgment, were of most significance in our audit of the financial statements of the current period. These matters were addressed in the context of our audit of the financial statements as a whole, and in forming our opinion thereon, and we do not provide a separate opinion on these matters.</p>

<h4>{{kam_title}}</h4>
<p><strong>Description:</strong> {{kam_description}}</p>
<p><strong>How our audit addressed the key audit matter:</strong> {{kam_audit_response}}</p>',
    30
);

-- View: Report generation summary
CREATE OR REPLACE VIEW engagement_report_summary AS
SELECT
    e.id AS engagement_id,
    e.client_name,
    e.engagement_type,
    er.report_type,
    er.opinion_type,
    er.status,
    er.report_date,
    er.drafted_by,
    er.reviewed_by,
    er.approved_by,
    er.issued_at,
    er.final_document_s3_uri
FROM engagements e
LEFT JOIN engagement_reports er ON er.engagement_id = e.id
WHERE er.status IN ('approved', 'issued');

COMMENT ON VIEW engagement_report_summary IS 'Summary of issued audit/review/compilation reports';
