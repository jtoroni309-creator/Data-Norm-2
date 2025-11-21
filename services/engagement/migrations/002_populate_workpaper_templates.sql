-- =====================================================
-- Aura Audit AI - Workpaper Template Population
-- Comprehensive audit workpaper templates following AICPA standards
-- =====================================================

-- Clean existing templates (if re-running)
DELETE FROM atlas.workpaper_templates;
DELETE FROM atlas.binder_structure_templates;

-- =====================================================
-- SECTION A: PLANNING & RISK ASSESSMENT
-- =====================================================

INSERT INTO atlas.binder_structure_templates (code, name, description, node_type, parent_code, position, is_required)
VALUES
('A', 'Planning & Risk Assessment', 'Planning, risk assessment, and materiality', 'FOLDER', NULL, 1, true),
('A-100', 'Risk Assessment', 'Risk assessment procedures and documentation', 'FOLDER', 'A', 1, true),
('A-200', 'Materiality', 'Materiality calculations and documentation', 'FOLDER', 'A', 2, true),
('A-300', 'Engagement Planning', 'Overall audit strategy and plan', 'FOLDER', 'A', 3, true);

INSERT INTO atlas.workpaper_templates (code, name, description, section, content_type, template_content, aicpa_reference, is_required)
VALUES
-- Risk Assessment Workpapers
('A-100-01', 'Entity and Environment Understanding', 'Understanding of entity, industry, and regulatory environment', 'A-100', 'structured',
$$# Entity and Environment Understanding

## Entity Overview
- Legal structure: {{ entity.legal_structure }}
- Industry: {{ entity.industry }}
- Regulatory environment: {{ entity.regulatory_bodies }}

## Business Model
{{ business_model_description }}

## Related Parties
{% for party in related_parties %}
- {{ party.name }}: {{ party.relationship }}
{% endfor %}

## Significant Locations and Business Units
{{ locations_and_units }}

## Key Personnel
{{ key_personnel }}

## Accounting Policies
{{ accounting_policies }}

**Conclusion**: {{ conclusion }}
**Prepared by**: {{ preparer }} on {{ date }}
**Reviewed by**: {{ reviewer }} on {{ review_date }}$$,
'AU-C 315.11-.24', true),

('A-100-02', 'Fraud Risk Assessment', 'Assessment of fraud risks and responses', 'A-100', 'structured',
$$# Fraud Risk Assessment

## Brainstorming Session
**Date**: {{ brainstorming_date }}
**Attendees**: {{ attendees }}
**Discussion Summary**: {{ discussion_summary }}

## Identified Fraud Risks

### Management Override of Controls
- Risk Description: {{ management_override_risk }}
- Assessment: {{ risk_level }}
- Planned Response: {{ response }}

### Revenue Recognition Fraud
- Risk Description: {{ revenue_fraud_risk }}
- Assessment: {{ risk_level }}
- Planned Response: {{ response }}

### Asset Misappropriation
- Risk Description: {{ asset_misappropriation_risk }}
- Assessment: {{ risk_level }}
- Planned Response: {{ response }}

## Fraud Indicators Observed
{{ fraud_indicators }}

## Communication with Management
{{ management_communication }}

**Conclusion**: {{ conclusion }}
**Prepared by**: {{ preparer }} on {{ date }}
**Reviewed by**: {{ reviewer }} on {{ review_date }}$$,
'AU-C 240.14-.27', true),

-- Materiality Workpapers
('A-200-01', 'Overall Materiality Calculation', 'Calculation of overall and performance materiality', 'A-200', 'structured',
$$# Materiality Calculation

## Overall Materiality

### Selected Benchmark
- Benchmark: {{ benchmark }} (Total Assets / Total Revenue / Pretax Income)
- Benchmark Value: ${{ benchmark_value | number_format }}
- Percentage Applied: {{ percentage }}%
- **Overall Materiality**: ${{ overall_materiality | number_format }}

### Justification for Benchmark Selection
{{ benchmark_justification }}

## Performance Materiality
- Overall Materiality: ${{ overall_materiality | number_format }}
- Percentage: {{ performance_percentage }}%
- **Performance Materiality**: ${{ performance_materiality | number_format }}

### Rationale for Performance Materiality %
{{ performance_rationale }}

## Clearly Trivial Threshold
- Percentage of Overall Materiality: 5%
- **Clearly Trivial**: ${{ trivial_threshold | number_format }}

## Summary of Materiality Levels

| Level | Amount |
|-------|--------|
| Overall Materiality | ${{ overall_materiality | number_format }} |
| Performance Materiality | ${{ performance_materiality | number_format }} |
| Clearly Trivial | ${{ trivial_threshold | number_format }} |

**Prepared by**: {{ preparer }} on {{ date }}
**Reviewed by**: {{ reviewer }} on {{ review_date }}$$,
'AU-C 320.10-.12', true);

-- =====================================================
-- SECTION B: ANALYTICAL PROCEDURES
-- =====================================================

INSERT INTO atlas.binder_structure_templates (code, name, description, node_type, parent_code, position, is_required)
VALUES
('B', 'Analytical Procedures', 'Analytical procedures and ratio analysis', 'FOLDER', NULL, 2, true),
('B-100', 'Financial Ratios', 'Financial ratio analysis and trends', 'FOLDER', 'B', 1, true),
('B-200', 'Fluctuation Analysis', 'Analysis of significant fluctuations', 'FOLDER', 'B', 2, true);

INSERT INTO atlas.workpaper_templates (code, name, description, section, content_type, template_content, aicpa_reference, is_required)
VALUES
('B-100-01', 'Financial Ratio Analysis', 'Comprehensive financial ratio analysis', 'B-100', 'structured',
$$# Financial Ratio Analysis

## Liquidity Ratios
| Ratio | Current Year | Prior Year | Industry Average | Assessment |
|-------|--------------|------------|------------------|------------|
| Current Ratio | {{ current_ratio_cy }} | {{ current_ratio_py }} | {{ industry_current }} | {{ current_assessment }} |
| Quick Ratio | {{ quick_ratio_cy }} | {{ quick_ratio_py }} | {{ industry_quick }} | {{ quick_assessment }} |
| Cash Ratio | {{ cash_ratio_cy }} | {{ cash_ratio_py }} | {{ industry_cash }} | {{ cash_assessment }} |

## Profitability Ratios
| Ratio | Current Year | Prior Year | Industry Average | Assessment |
|-------|--------------|------------|------------------|------------|
| Gross Margin % | {{ gross_margin_cy }}% | {{ gross_margin_py }}% | {{ industry_gross }}% | {{ gross_assessment }} |
| Operating Margin % | {{ operating_margin_cy }}% | {{ operating_margin_py }}% | {{ industry_operating }}% | {{ operating_assessment }} |
| Net Margin % | {{ net_margin_cy }}% | {{ net_margin_py }}% | {{ industry_net }}% | {{ net_assessment }} |
| ROA % | {{ roa_cy }}% | {{ roa_py }}% | {{ industry_roa }}% | {{ roa_assessment }} |
| ROE % | {{ roe_cy }}% | {{ roe_py }}% | {{ industry_roe }}% | {{ roe_assessment }} |

## Leverage Ratios
| Ratio | Current Year | Prior Year | Industry Average | Assessment |
|-------|--------------|------------|------------------|------------|
| Debt-to-Equity | {{ dte_cy }} | {{ dte_py }} | {{ industry_dte }} | {{ dte_assessment }} |
| Debt-to-Assets | {{ dta_cy }} | {{ dta_py }} | {{ industry_dta }} | {{ dta_assessment }} |
| Interest Coverage | {{ interest_coverage_cy }} | {{ interest_coverage_py }} | {{ industry_coverage }} | {{ coverage_assessment }} |

## Significant Variances Requiring Investigation
{{ significant_variances }}

## Going Concern Indicators
{{ going_concern_indicators }}

**Conclusion**: {{ conclusion }}
**Prepared by**: {{ preparer }} on {{ date }}
**Reviewed by**: {{ reviewer }} on {{ review_date }}$$,
'AU-C 520.05-.07', true);

-- =====================================================
-- SECTION C: CASH
-- =====================================================

INSERT INTO atlas.binder_structure_templates (code, name, description, node_type, parent_code, position, is_required)
VALUES
('C', 'Cash & Cash Equivalents', 'Cash, bank reconciliations, and confirmations', 'FOLDER', NULL, 3, true),
('C-100', 'Bank Reconciliations', 'Bank reconciliation testing', 'FOLDER', 'C', 1, true),
('C-200', 'Bank Confirmations', 'Bank confirmation procedures', 'FOLDER', 'C', 2, true);

INSERT INTO atlas.workpaper_templates (code, name, description, section, content_type, template_content, aicpa_reference, is_required)
VALUES
('C-100-01', 'Bank Reconciliation Testing', 'Testing of bank reconciliations', 'C-100', 'structured',
$$# Bank Reconciliation Testing

## Bank Account: {{ bank_name }} - {{ account_number }}

### Reconciliation as of {{ balance_sheet_date }}

| Description | Amount |
|-------------|--------|
| Balance per Bank Statement | ${{ bank_balance | number_format }} |
| Add: Deposits in Transit | ${{ deposits_in_transit | number_format }} |
| Less: Outstanding Checks | (${{ outstanding_checks | number_format }}) |
| Other Reconciling Items | ${{ other_items | number_format }} |
| **Balance per Books** | **${{ book_balance | number_format }}** |

### Testing Procedures Performed
- [x] Obtained bank statement directly from bank or confirmed with client's online access
- [x] Footed bank reconciliation and traced balance to general ledger
- [x] Traced deposits in transit to subsequent bank statement ({{ trace_date }})
- [x] Examined outstanding checks for subsequent clearance
- [x] Investigated reconciling items over ${{ investigation_threshold | number_format }}

### Deposits in Transit
{{ deposits_detail }}
- All deposits cleared within {{ days_to_clear }} business days ✓

### Outstanding Checks
{{ checks_detail }}
- Reviewed aging of outstanding checks
- Investigated checks outstanding > 6 months

### Unusual Items Noted
{{ unusual_items }}

**Conclusion**: {{ conclusion }}
**Prepared by**: {{ preparer }} on {{ date }}
**Reviewed by**: {{ reviewer }} on {{ review_date }}$$,
'AU-C 330.A15-.A19', true);

-- =====================================================
-- SECTION E: REVENUE
-- =====================================================

INSERT INTO atlas.binder_structure_templates (code, name, description, node_type, parent_code, position, is_required)
VALUES
('E', 'Revenue', 'Revenue recognition and testing', 'FOLDER', NULL, 5, true),
('E-100', 'Revenue Testing', 'Substantive testing of revenue', 'FOLDER', 'E', 1, true),
('E-200', 'Cut-off Testing', 'Revenue cut-off procedures', 'FOLDER', 'E', 2, true);

INSERT INTO atlas.workpaper_templates (code, name, description, section, content_type, template_content, aicpa_reference, is_required)
VALUES
('E-100-01', 'Revenue Substantive Testing', 'Detail testing of revenue transactions', 'E-100', 'structured',
$$# Revenue Substantive Testing

## Sample Selection
- Population: {{ population_description }}
- Sampling Method: {{ sampling_method }}
- Sample Size: {{ sample_size }}
- Tolerable Misstatement: ${{ tolerable_misstatement | number_format }}

## Revenue Recognition Policy
{{ revenue_recognition_policy }}

## Testing Procedures

### For Each Sample Item:
1. Trace to underlying sales documentation (invoice, sales order, contract)
2. Verify delivery/performance occurred in correct period
3. Verify pricing agrees to approved price lists/contracts
4. Recalculate revenue recognition under ASC 606 five-step model
5. Trace to cash receipt (for accounts receivable items)

## Sample Testing Results

| Invoice # | Date | Customer | Amount | Documentation | Timing | Pricing | Calculation | Collection | Conclusion |
|-----------|------|----------|--------|---------------|--------|---------|-------------|------------|------------|
{% for item in sample_items %}
| {{ item.invoice }} | {{ item.date }} | {{ item.customer }} | ${{ item.amount | number_format }} | {{ item.doc_ok }} | {{ item.timing_ok }} | {{ item.price_ok }} | {{ item.calc_ok }} | {{ item.collected }} | {{ item.conclusion }} |
{% endfor %}

## Summary of Exceptions
{{ exceptions_summary }}

## Projected Misstatement
- Sample Misstatement: ${{ sample_misstatement | number_format }}
- Projected to Population: ${{ projected_misstatement | number_format }}
- Evaluation: {{ evaluation }}

**Conclusion**: {{ conclusion }}
**Prepared by**: {{ preparer }} on {{ date }}
**Reviewed by**: {{ reviewer }} on {{ review_date }}$$,
'AU-C 330.A28-.A33', true);

-- =====================================================
-- SECTION L: SUBSEQUENT EVENTS
-- =====================================================

INSERT INTO atlas.binder_structure_templates (code, name, description, node_type, parent_code, position, is_required)
VALUES
('L', 'Subsequent Events', 'Subsequent events review', 'FOLDER', NULL, 12, true);

INSERT INTO atlas.workpaper_templates (code, name, description, section, content_type, template_content, aicpa_reference, is_required)
VALUES
('L-100-01', 'Subsequent Events Review', 'Review of events after balance sheet date', 'L', 'structured',
$$# Subsequent Events Review

## Review Period
- Balance Sheet Date: {{ balance_sheet_date }}
- Date of Auditor's Report: {{ report_date }}
- Review Period: {{ review_period_days }} days

## Procedures Performed

### 1. Inquiry of Management
**Date of Inquiry**: {{ inquiry_date }}
**Discussed with**: {{ management_personnel }}

Topics Discussed:
- Significant changes in financial position or operations
- New commitments, borrowings, or guarantees
- Assets sold, destroyed, or abandoned
- Litigation or claims
- Unusual adjustments made after year-end

**Summary of Discussion**: {{ inquiry_summary }}

### 2. Review of Subsequent Period Financial Information
- Reviewed interim financial statements through {{ interim_date }}
- Reviewed budgets, forecasts, and cash flow projections
- Identified material changes: {{ material_changes }}

### 3. Minutes of Meetings
- Board of Directors meetings reviewed through {{ minutes_date }}
- Significant matters discussed: {{ board_matters }}

### 4. Legal Letters
- Obtained updated legal letters dated {{ legal_letter_date }}
- New or updated matters: {{ legal_matters }}

### 5. Subsequent Receipts and Disbursements
- Reviewed significant receipts: {{ significant_receipts }}
- Reviewed significant disbursements: {{ significant_disbursements }}

## Events Identified

### Type I Events (Conditions existed at balance sheet date)
{{ type_one_events }}

### Type II Events (Conditions arose after balance sheet date)
{{ type_two_events }}

## Disclosure Requirements
{{ disclosure_requirements }}

## Going Concern Matters
{{ going_concern_matters }}

**Conclusion**: {{ conclusion }}
**Prepared by**: {{ preparer }} on {{ date }}
**Reviewed by**: {{ reviewer }} on {{ review_date }}$$,
'AU-C 560.06-.09', true);

-- =====================================================
-- SECTION M: COMPLETION & REVIEW
-- =====================================================

INSERT INTO atlas.binder_structure_templates (code, name, description, node_type, parent_code, position, is_required)
VALUES
('M', 'Completion & Review', 'Final review and completion procedures', 'FOLDER', NULL, 13, true),
('M-100', 'Final Review', 'Partner final review checklist', 'FOLDER', 'M', 1, true),
('M-200', 'Management Representations', 'Management representation letters', 'FOLDER', 'M', 2, true);

INSERT INTO atlas.workpaper_templates (code, name, description, section, content_type, template_content, aicpa_reference, is_required)
VALUES
('M-100-01', 'Partner Final Review Checklist', 'Comprehensive final review checklist', 'M-100', 'checklist',
$$# Partner Final Review Checklist

## Engagement Completion

- [ ] All audit programs completed and signed off
- [ ] All review notes cleared
- [ ] All proposed adjustments resolved or documented
- [ ] Financial statements agree to trial balance
- [ ] Subsequent events review completed through report date
- [ ] Going concern evaluation completed
- [ ] Related party transactions identified and disclosed

## Financial Statement Review

- [ ] Financial statements reviewed for GAAP compliance
- [ ] All required disclosures included per ASC checklist
- [ ] Accounting estimates appear reasonable
- [ ] Related party disclosures adequate
- [ ] Going concern disclosure (if applicable)
- [ ] Subsequent events disclosure adequate

## Audit Documentation

- [ ] All workpapers properly prepared and reviewed
- [ ] Cross-references complete and accurate
- [ ] All exceptions properly resolved
- [ ] Sample selections properly documented
- [ ] Conclusions supported by evidence

## Opinion Matters

- [ ] Scope of audit adequate to support opinion
- [ ] No unresolved scope limitations
- [ ] No unresolved disagreements with management
- [ ] No unresolved concerns about management integrity
- [ ] Opinion type determined: {{ opinion_type }}

## Reporting

- [ ] Report date: {{ report_date }}
- [ ] Report properly formatted and signed
- [ ] Emphasis of matter paragraphs (if any) appropriate
- [ ] Other matter paragraphs (if any) appropriate

## Independence & Quality Control

- [ ] Independence confirmed for all team members
- [ ] Engagement quality review completed (if required)
- [ ] No significant deficiencies in internal control over financial reporting (or communicated)

## Consents & Approvals

- [ ] Management representation letter obtained
- [ ] Legal letters reviewed
- [ ] Use of report authorized by client

**Partner Approval**: {{ partner_name }}
**Date**: {{ approval_date }}
**Signature**: ___________________________$$,
'AU-C 230.09-.11, QC 10', true),

('M-200-01', 'Management Representation Letter', 'Standard management representations', 'M-200', 'document',
$$[Date]

[Auditor Firm Name]
[Address]

Dear [Auditor]:

This representation letter is provided in connection with your audit of the financial statements of {{ entity_name }} as of {{ balance_sheet_date }} and for the {{ period_description }} then ended, for the purpose of expressing an opinion on whether the financial statements present fairly, in all material respects, the financial position, results of operations, and cash flows in accordance with accounting principles generally accepted in the United States of America (U.S. GAAP).

We confirm, to the best of our knowledge and belief, as of {{ report_date }}, the following representations made to you during your audit:

## Financial Statements

1. We have fulfilled our responsibilities, as set out in the terms of the audit engagement letter dated {{ engagement_letter_date }}, for the preparation and fair presentation of the financial statements in accordance with U.S. GAAP.

2. We acknowledge our responsibility for the design, implementation, and maintenance of internal control relevant to the preparation and fair presentation of financial statements that are free from material misstatement, whether due to fraud or error.

3. We acknowledge our responsibility for the design, implementation, and maintenance of internal control to prevent and detect fraud.

## Information Provided

4. We have provided you with:
   a. Access to all information of which we are aware that is relevant to the preparation and fair presentation of the financial statements;
   b. Additional information that you have requested from us for the purpose of the audit; and
   c. Unrestricted access to persons within the entity from whom you determined it necessary to obtain audit evidence.

5. All transactions have been recorded in the accounting records and are reflected in the financial statements.

6. We have disclosed to you the results of our assessment of the risk that the financial statements may be materially misstated as a result of fraud.

## Fraud

7. We have no knowledge of any fraud or suspected fraud affecting the entity involving:
   a. Management;
   b. Employees who have significant roles in internal control; or
   c. Others where the fraud could have a material effect on the financial statements.

8. We have no knowledge of any allegations of fraud or suspected fraud affecting the entity's financial statements communicated by employees, former employees, regulators, or others.

## Related Parties

9. We have disclosed to you the identity of the entity's related parties and all the related party relationships and transactions of which we are aware.

## Subsequent Events

10. All events subsequent to the date of the financial statements and for which U.S. GAAP requires adjustment or disclosure have been adjusted or disclosed.

## Litigation, Claims, and Assessments

11. We have disclosed to you all known actual or possible litigation, claims, and assessments whose effects should be considered when preparing the financial statements.

## Estimates

12. We believe that the significant assumptions used in making accounting estimates, including fair value measurements, are reasonable.

## Going Concern

13. We have no plans or intentions that may materially affect the carrying value or classification of assets and liabilities.

14. [If applicable] We have disclosed all matters relevant to the entity's ability to continue as a going concern, including significant conditions and events, and management's plans.

Sincerely,

____________________________
{{ ceo_name }}
Chief Executive Officer

____________________________
{{ cfo_name }}
Chief Financial Officer

Date: _______________$$,
'AU-C 580.A1-.A30', true);

-- Insert additional commonly used sections
INSERT INTO atlas.binder_structure_templates (code, name, description, node_type, parent_code, position, is_required)
VALUES
('D', 'Accounts Receivable', 'A/R testing and confirmations', 'FOLDER', NULL, 4, true),
('F', 'Inventory', 'Inventory observation and testing', 'FOLDER', NULL, 6, false),
('G', 'Property Plant & Equipment', 'Fixed asset testing', 'FOLDER', NULL, 7, false),
('H', 'Accounts Payable', 'A/P testing and search for unrecorded liabilities', 'FOLDER', NULL, 8, true),
('I', 'Debt', 'Long-term debt confirmations and testing', 'FOLDER', NULL, 9, false),
('J', 'Equity', 'Equity transactions and disclosure', 'FOLDER', NULL, 10, true),
('K', 'Income & Expenses', 'Testing of income statement accounts', 'FOLDER', NULL, 11, true);

COMMIT;
