# Engagement-Type Specific Workflows

## Overview

The platform supports three types of attestation engagements, each with distinct procedures, documentation requirements, and reporting standards:

1. **Audit Engagements** - Highest level of assurance (GAAS, PCAOB)
2. **Review Engagements** - Limited assurance (SSARS AR-C 90)
3. **Compilation Engagements** - No assurance (SSARS AR-C 70)

---

## Audit Engagement Workflow

### Standards Compliance
- **GAAS** (Generally Accepted Auditing Standards)
- **PCAOB** (for public companies)
- **AU-C Sections** (AICPA Clarified Standards)

### Workflow Phases

#### 1. Planning & Risk Assessment (Section A)

**Key Workpapers:**
- A-100: Engagement Letter
- A-110: Independence Evaluation
- A-120: Understanding of Entity and Environment
- A-130: Risk Assessment
- A-140: Materiality Calculation
- A-150: Audit Strategy and Plan

**Requirements:**
- Set overall materiality (typically 0.5-5% of benchmark)
- Identify significant accounts and disclosures
- Assess risk of material misstatement (RMM)
- Develop audit approach (substantive, combined, controls reliance)

**Services Integration:**
- Generate planning workpapers from binder templates
- Pull prior year data for risk assessment
- Document fraud risk discussions

#### 2. Internal Control Assessment

**Key Workpapers:**
- A-200: Internal Control Understanding
- A-210: Control Risk Assessment
- A-220: Tests of Controls (if applicable)

**Requirements:**
- Document understanding of 5 components of internal control
- Identify key controls for significant accounts
- Determine if controls reliance approach is appropriate
- Perform walkthroughs

#### 3. Substantive Testing (Sections B-H)

**Balance Sheet Testing:**

**Section B - Cash:**
- B-100: Cash Lead Sheet
- B-110: Bank Reconciliations
- B-120: Bank Confirmations
- B-130: Restricted Cash Testing

**Section C - Accounts Receivable:**
- C-100: A/R Lead Sheet
- C-110: A/R Aging Analysis
- C-120: A/R Confirmations
- C-130: Allowance for Doubtful Accounts
- C-140: Subsequent Cash Receipts Testing

**Section D - Inventory:**
- D-100: Inventory Lead Sheet
- D-110: Physical Inventory Observation
- D-120: Inventory Pricing and Valuation
- D-130: Lower of Cost or Market Testing
- D-140: Inventory Consignment Confirmations

**Section E - Fixed Assets:**
- E-100: Fixed Assets Lead Sheet
- E-110: Asset Additions and Disposals
- E-120: Depreciation Testing
- E-130: Asset Impairment Assessment

**Section F - Other Assets:**
- F-100: Prepaid Expenses
- F-110: Investments
- F-120: Intangible Assets
- F-130: Deferred Tax Assets

**Section G - Liabilities:**
- G-100: Accounts Payable Testing
- G-110: Accrued Liabilities
- G-120: Debt Testing and Confirmations
- G-130: Contingent Liabilities
- G-140: Attorney Letter

**Section H - Equity:**
- H-100: Stockholders' Equity Lead Sheet
- H-110: Stock Transactions
- H-120: Retained Earnings Analysis

**Income Statement Testing:**

**Section I - Revenue:**
- I-100: Revenue Lead Sheet
- I-110: Revenue Recognition Testing (ASC 606)
- I-120: Cutoff Testing
- I-130: Sales Returns and Allowances

**Section J - Expenses:**
- J-100: Payroll Testing
- J-110: Operating Expense Analytics
- J-120: Period End Accruals

#### 4. Confirmations (Section C, G-120, D-140)

**Required Confirmations:**
- Bank confirmations (standard form)
- A/R confirmations (positive or negative)
- Attorney letter (inquiry concerning litigation)
- Debt confirmations
- Inventory consignments (if applicable)

**Confirmation Service Usage:**
```python
# Create A/R confirmation
await confirmation_service.create_confirmation(
    engagement_id=engagement_id,
    confirmation_type=ConfirmationType.ACCOUNTS_RECEIVABLE,
    entity_name="Customer ABC Inc.",
    amount=125000.00,
    as_of_date=date(2024, 12, 31)
)

# Generate and send confirmation letter
letter_html = await confirmation_service.generate_confirmation_letter(confirmation_id)
await confirmation_service.mark_confirmation_sent(confirmation_id)

# Record response
await confirmation_service.record_confirmation_response(
    confirmation_id=confirmation_id,
    confirmed_amount=125000.00,
    received_date=date(2025, 1, 15)
)
```

#### 5. Analytical Procedures (Section K)

**Key Workpapers:**
- K-100: Overall Analytical Review
- K-110: Ratio Analysis
- K-120: Trend Analysis
- K-130: Benchmarking vs Industry

**Services Integration:**
```python
# Generate financial ratios from trial balance
ratios = await analytics_service.calculate_financial_ratios(
    engagement_id=engagement_id,
    include_industry_benchmarks=True
)

# Investigate variances
significant_variances = [r for r in ratios if abs(r['variance_pct']) > 10]
```

#### 6. Disclosure Review (Section L)

**Key Workpapers:**
- L-100: GAAP Disclosure Checklist
- L-110: Financial Statement Notes Review
- L-120: Subsequent Events Review

**Disclosure Checklist Usage:**
```python
# Initialize disclosure checklist
await disclosure_service.initialize_checklist(
    engagement_id=engagement_id,
    entity_type='private'
)

# Mark applicability
await disclosure_service.mark_disclosure_applicability(
    checklist_item_id=item_id,
    is_applicable=True,
    reason="Company has operating leases - ASC 842 applies"
)

# Draft disclosure
await disclosure_service.draft_disclosure(
    checklist_item_id=item_id,
    template_variables={
        'total_lease_cost': '50000',
        'weighted_avg_term': '3.5',
        'discount_rate': '5.0'
    }
)
```

#### 7. Financial Statement Preparation (Section M)

**Key Workpapers:**
- M-100: Trial Balance to Financial Statements
- M-110: Financial Statement Draft
- M-120: Note Disclosures

**Financial Statement Generation:**
```python
# Generate balance sheet
balance_sheet = await fs_generator.generate_balance_sheet(
    engagement_id=engagement_id,
    as_of_date=date(2024, 12, 31),
    include_prior_year=True
)

# Generate income statement
income_statement = await fs_generator.generate_income_statement(
    engagement_id=engagement_id,
    period_start=date(2024, 1, 1),
    period_end=date(2024, 12, 31),
    include_prior_year=True
)

# Generate cash flows
cash_flows = await fs_generator.generate_statement_of_cash_flows(
    engagement_id=engagement_id,
    period_start=date(2024, 1, 1),
    period_end=date(2024, 12, 31),
    method='indirect'
)
```

#### 8. Report Generation (Section N)

**Key Workpapers:**
- N-100: Auditor's Report Draft
- N-110: Management Representation Letter
- N-120: Internal Control Communication
- N-130: Final Review Checklist

**Opinion Generation:**
```python
# Generate unqualified opinion
report_id = await opinion_service.generate_report_draft(
    engagement_id=engagement_id,
    opinion_type=OpinionType.UNQUALIFIED,
    report_date=date(2025, 2, 28),
    template_variables={
        'firm_name': 'Smith & Partners CPA',
        'firm_address': '123 Main St\nCityville, ST 12345',
        'partner_name': 'John Smith',
        'balance_sheet_date': 'December 31, 2024'
    }
)

# Approve and issue
await opinion_service.approve_report(report_id, partner_user_id)
await opinion_service.issue_report(report_id, final_pdf_s3_uri)
```

### Audit-Specific Requirements

✅ **Sufficient Appropriate Audit Evidence**
- Document audit procedures performed
- Retain working papers for 7 years (GAAS) or 7 years + litigation (PCAOB)

✅ **Independence**
- Verify independence at engagement and financial statement level
- Document any threats and safeguards

✅ **Professional Skepticism**
- Document fraud risk assessment
- Include fraud discussion in planning memo

✅ **Quality Control**
- Engagement quality review for public companies
- Partner review of all significant areas

---

## Review Engagement Workflow

### Standards Compliance
- **SSARS AR-C Section 90** (Review of Financial Statements)
- **AR-C 60** (General Principles for Engagements Performed in Accordance with SSARS)

### Workflow Phases

#### 1. Planning

**Key Workpapers:**
- A-100: Engagement Letter (review)
- A-110: Independence Evaluation
- A-120: Understanding of Entity
- A-140: Planning Materiality (higher than audit)

**Differences from Audit:**
- No risk assessment required
- No control documentation required
- Higher materiality threshold (typically 2-10% of benchmark)

#### 2. Inquiry and Analytical Procedures

**Primary Procedures:**
- Inquiries of management
- Analytical procedures
- No testing of transactions or confirmations

**Key Workpapers:**
- B-100: Cash Analytical Review
- C-100: A/R Analytical Review
- K-100: Overall Financial Statement Analytics
- K-110: Ratio Analysis
- K-120: Unusual Items Investigation

**Example Analytical Procedures:**
```python
# Calculate key ratios and compare to prior year
ratios = await analytics_service.calculate_financial_ratios(engagement_id)

for ratio in ratios:
    if abs(ratio['variance_pct']) > 20:  # Review threshold
        # Make inquiry of management
        inquiry = {
            'ratio': ratio['name'],
            'current': ratio['current_value'],
            'prior': ratio['prior_value'],
            'variance_pct': ratio['variance_pct'],
            'management_explanation': 'To be obtained',
            'accountant_conclusion': 'TBD'
        }
```

#### 3. Disclosure Review

**Key Workpapers:**
- L-100: Review Disclosure Checklist (simplified vs audit)
- L-110: Financial Statement Notes Review

**Disclosures Required:**
- Read financial statements for obvious material misstatements
- Verify GAAP compliance for significant items
- Less comprehensive than audit disclosure checklist

#### 4. Report Generation

**Report Type:** Review Report (Limited Assurance)

**Opinion Wording:**
```
"Based on our review, we are not aware of any material modifications
that should be made to the accompanying financial statements in order
for them to be in accordance with accounting principles generally
accepted in the United States of America."
```

**Report Generation:**
```python
report_id = await opinion_service.generate_report_draft(
    engagement_id=engagement_id,
    opinion_type=OpinionType.REVIEW_STANDARD,
    report_date=date(2025, 2, 28),
    template_variables={
        'firm_name': 'Smith & Partners CPA',
        'balance_sheet_date': 'December 31, 2024'
    }
)
```

### Review-Specific Characteristics

✅ **Limited Assurance** (vs Reasonable Assurance for audit)

✅ **Substantially Less Scope than Audit:**
- No confirmations
- No observation of inventory
- No tests of controls
- No detailed transaction testing

✅ **Primary Procedures:**
- Analytical procedures
- Inquiries of management

✅ **Lower Cost & Time:**
- Approximately 20-30% of audit effort
- Typically 1-3 weeks vs 4-8 weeks for audit

---

## Compilation Engagement Workflow

### Standards Compliance
- **SSARS AR-C Section 70** (Preparation of Financial Statements)
- **AR-C 80** (Compilation Engagements)

### Workflow Phases

#### 1. Engagement Acceptance

**Key Workpapers:**
- A-100: Engagement Letter (compilation)
- A-110: Understanding of Entity's Operations
- No independence assessment if disclosed

#### 2. Financial Statement Compilation

**Procedures Performed:**
- Assist management in preparing financial statements
- Format financial statements
- Read for obvious errors

**NOT Performed:**
- No inquiries
- No analytical procedures
- No verification of data
- No assessment of internal controls

**Key Workpapers:**
- M-100: Trial Balance to Financial Statements
- M-110: Financial Statement Compilation
- Very limited working papers

#### 3. Report Generation

**Report Type:** Compilation Report (No Assurance)

**Standard Wording:**
```
"We have compiled the accompanying financial statements of [Client],
which comprise the balance sheet as of December 31, 2024, and the
related statements of income, changes in stockholders' equity, and
cash flows for the year then ended. We have not audited or reviewed
the accompanying financial statements and, accordingly, do not express
an opinion or provide any assurance about whether the financial
statements are in accordance with accounting principles generally
accepted in the United States of America."
```

**Report Generation:**
```python
report_id = await opinion_service.generate_report_draft(
    engagement_id=engagement_id,
    opinion_type=OpinionType.COMPILATION_STANDARD,
    report_date=date(2025, 2, 28),
    template_variables={
        'firm_name': 'Smith & Partners CPA',
        'balance_sheet_date': 'December 31, 2024'
    }
)
```

### Compilation-Specific Characteristics

✅ **No Assurance Provided**

✅ **Minimal Procedures:**
- Compile financial information into proper format
- Read for obvious material errors
- No verification of underlying data

✅ **Independence Not Required** (if disclosed in report)

✅ **Lowest Cost & Time:**
- Approximately 5-10% of audit effort
- Typically 1-5 days

✅ **Common Uses:**
- Internal use only
- Bank submission (when audit/review not required)
- Small businesses with limited resources

---

## Comparison Matrix

| Feature | Audit | Review | Compilation |
|---------|-------|--------|-------------|
| **Assurance Level** | Reasonable (highest) | Limited | None |
| **Standards** | GAAS, PCAOB | SSARS AR-C 90 | SSARS AR-C 70/80 |
| **Opinion Wording** | "Present fairly..." | "Not aware of material modifications..." | "No opinion expressed..." |
| **Independence Required** | Yes | Yes | No (if disclosed) |
| **Confirmations** | Yes (required) | No | No |
| **Analytical Procedures** | Yes (substantive) | Yes (primary procedure) | No |
| **Transaction Testing** | Yes (extensive) | No | No |
| **Internal Controls** | Yes (document & test if relying) | No | No |
| **Typical Duration** | 4-8 weeks | 1-3 weeks | 1-5 days |
| **Relative Cost** | 100% | 20-30% | 5-10% |
| **Workpaper Sections** | A through N (14 sections) | A, K, L, M, N (5 sections) | A, M, N (3 sections) |
| **Disclosure Checklist** | Comprehensive | Simplified | Minimal |

---

## Engagement Type Selection

Use the `engagement_workflow_service` to automatically configure the correct procedures:

```python
# Create audit engagement
engagement, summary = await workflow_service.create_engagement_with_workflow(
    client_name="ABC Corporation",
    engagement_type="audit",  # 'audit', 'review', or 'compilation'
    fiscal_year_end=date(2024, 12, 31),
    engagement_partner="John Smith, CPA",
    entity_type="private",
    user_id=current_user_id
)

print(f"Created {engagement.engagement_type} engagement")
print(f"Binder: {summary['binder']['sections']} sections, {summary['binder']['workpapers']} workpapers")
print(f"Disclosures: {summary['disclosures']['total']} requirements")
```

The system automatically:
- ✅ Creates appropriate binder structure based on engagement type
- ✅ Initializes correct disclosure checklist (audit/review only)
- ✅ Sets up phase workflow
- ✅ Configures quality control requirements
- ✅ Generates appropriate report template

---

## Phase Advancement

Track progress and advance through phases:

```python
# Get engagement status
dashboard = await workflow_service.get_engagement_dashboard(engagement_id)
print(f"Current phase: {dashboard['engagement']['current_phase']}")
print(f"Overall completion: {dashboard['overall_completion']}%")
print(f"Binder completion: {dashboard['binder']['completion_percentage']}%")

# Check for blockers
blockers = await workflow_service.get_engagement_blockers(engagement_id)
if len(blockers) == 0:
    # Advance to next phase
    await workflow_service.advance_to_next_phase(engagement_id, user_id)
else:
    print(f"Cannot advance: {len(blockers)} blockers")
    for blocker in blockers:
        print(f"  - {blocker['description']}")
```

---

## Best Practices

### For Audit Engagements:
1. Complete planning and risk assessment before fieldwork
2. Send confirmations early (30-45 days before year-end)
3. Document all significant judgments
4. Perform interim procedures to spread workload
5. Use engagement quality review for high-risk clients

### For Review Engagements:
1. Focus on analytical procedures and inquiries
2. Document unusual trends or ratios
3. Obtain representation letter from management
4. Read subsequent period financials for unusual items

### For Compilation Engagements:
1. Ensure engagement letter clearly states no assurance
2. Verify CPA is not associated with misleading financials
3. Minimal working papers - focus on compilation checklist
4. Consider lack of independence disclosure

---

## Integration with Services

All engagement types integrate with:
- ✅ **Binder Generation Service** - Auto-creates workpaper structure
- ✅ **Financial Statement Generator** - Creates balance sheet, income statement, cash flows
- ✅ **Disclosure Checklist Service** - Tracks GAAP compliance (audit/review)
- ✅ **Opinion Service** - Generates appropriate report
- ✅ **Confirmation Service** - Manages A/R, bank, attorney confirmations (audit only)
- ✅ **Analytics Service** - Calculates ratios, trends, benchmarks (audit/review)

This provides a complete end-to-end workflow that matches or exceeds the capabilities of a seasoned CPA firm.
