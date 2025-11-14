#!/usr/bin/env python3
"""
Populate LLM Knowledge Base with Comprehensive Audit Data
This script loads maximum information to enable AI to perform extensive audit work
"""
import requests
import json
import time
from typing import List, Dict

LLM_API_URL = "http://localhost:8002"

# Comprehensive GAAP Standards for Knowledge Base
GAAP_STANDARDS = [
    {
        "document_type": "gaap_standard",
        "title": "ASC 606 - Revenue Recognition",
        "standard_code": "ASC 606",
        "source": "FASB",
        "version": "2024",
        "content": """
ASC 606 Revenue from Contracts with Customers

Core Principle: Recognize revenue to depict transfer of promised goods/services in amount reflecting consideration expected.

Five-Step Model:
1. Identify the contract(s) with customer
2. Identify performance obligations in contract
3. Determine transaction price
4. Allocate transaction price to performance obligations
5. Recognize revenue when (or as) entity satisfies performance obligation

Key Audit Procedures:
- Test contract identification and terms
- Evaluate performance obligation identification
- Test transaction price determination including variable consideration
- Verify allocation methodology
- Test timing of revenue recognition
- Review disclosure completeness

Common Issues:
- Multiple element arrangements
- Variable consideration estimation
- Principal vs agent determination
- Contract modifications
- Series guidance application

Disclosure Requirements:
- Disaggregation of revenue
- Contract balances
- Performance obligations
- Significant judgments
- Assets recognized from costs to obtain/fulfill contracts
        """
    },
    {
        "document_type": "gaap_standard",
        "title": "ASC 842 - Leases",
        "standard_code": "ASC 842",
        "source": "FASB",
        "version": "2024",
        "content": """
ASC 842 Leases

Key Changes: Nearly all leases recorded on balance sheet.

Lessee Accounting:
- Right-of-use (ROU) asset
- Lease liability at present value
- Operating lease: Single lease cost (straight-line)
- Finance lease: Amortization + interest expense

Classification Criteria (Finance if any met):
1. Transfer of ownership
2. Purchase option reasonably certain
3. Lease term major part of economic life
4. PV of payments substantially all fair value
5. Specialized asset with no alternative use

Audit Procedures:
- Test completeness of lease population
- Verify lease classification
- Test discount rate determination
- Recalculate ROU asset and liability
- Test subsequent measurement
- Review disclosure completeness

Key Judgments:
- Lease vs non-lease components
- Lease term including extension options
- Discount rate selection
- Variable lease payments

Disclosures Required:
- Maturity analysis
- Lease cost components
- Cash flows
- Weighted-average rates and terms
        """
    },
    {
        "document_type": "gaap_standard",
        "title": "ASC 326 - Credit Losses (CECL)",
        "standard_code": "ASC 326",
        "source": "FASB",
        "version": "2024",
        "content": """
ASC 326 Current Expected Credit Loss (CECL)

Principle: Estimate lifetime expected credit losses at financial asset recognition.

Scope: Financial assets measured at amortized cost, debt securities.

CECL Model Requirements:
- Forward-looking estimates
- Historical loss experience
- Current conditions
- Reasonable/supportable forecasts
- Reversion to historical loss for periods beyond forecast

Audit Procedures:
- Test data completeness and accuracy
- Evaluate model methodology and assumptions
- Test forecasts for reasonableness
- Verify segmentation approach
- Test qualitative factor adjustments
- Review disclosure adequacy

Key Considerations:
- Segmentation of financial assets
- Forecast period determination
- Reversion method selection
- Qualitative factor development
- Model validation

Required Disclosures:
- Roll-forward of allowance
- Vintage disclosures for financing receivables
- Credit quality indicators
- Past due analysis
- Modifications
        """
    },
    {
        "document_type": "gaap_standard",
        "title": "ASC 820 - Fair Value Measurement",
        "standard_code": "ASC 820",
        "source": "FASB",
        "version": "2024",
        "content": """
ASC 820 Fair Value Measurement

Definition: Price received to sell asset or paid to transfer liability in orderly transaction.

Fair Value Hierarchy:
Level 1: Quoted prices in active markets (identical assets)
Level 2: Observable inputs other than Level 1 (similar assets, inactive markets)
Level 3: Unobservable inputs (entity's own assumptions)

Valuation Techniques:
- Market approach
- Income approach
- Cost approach

Audit Procedures:
- Test valuation methodology appropriateness
- Evaluate significant assumptions and inputs
- Test data accuracy used in valuations
- Consider need for specialist
- Test fair value hierarchy classification
- Review disclosure completeness

Key Risks:
- Level 3 measurements (significant judgment)
- Valuation specialist qualifications
- Management bias in assumptions
- Market conditions at measurement date

Disclosure Requirements:
- Techniques and inputs used
- Level 3 reconciliation
- Sensitivity analysis for Level 3
- Transfers between levels
        """
    }
]

# PCAOB Auditing Standards
PCAOB_STANDARDS = [
    {
        "document_type": "pcaob_rule",
        "title": "AS 2110 - Identifying and Assessing Risks",
        "standard_code": "AS 2110",
        "source": "PCAOB",
        "version": "2024",
        "content": """
AS 2110 Identifying and Assessing Risks of Material Misstatement

Objective: Identify and assess risks of material misstatement to design audit procedures.

Risk Assessment Procedures:
1. Obtain understanding of entity and environment
2. Understand internal control
3. Perform analytical procedures
4. Conduct inquiries
5. Observe operations

Areas Requiring Understanding:
- Industry, regulatory, external factors
- Nature of entity
- Accounting policies and practices
- Objectives, strategies, business risks
- Performance measurement
- Internal control

Significant Risks:
- Require special audit consideration
- Often relate to significant non-routine transactions
- High degree of judgment in financial reporting
- Complex transactions
- Related party transactions
- Revenue recognition
- Fraud risks

Documentation Requirements:
- Discussion among engagement team
- Key elements of understanding
- Identified risks and responses
- Significant risks identified
        """
    },
    {
        "document_type": "pcaob_rule",
        "title": "AS 2301 - Auditor's Responses to Risks",
        "standard_code": "AS 2301",
        "source": "PCAOB",
        "version": "2024",
        "content": """
AS 2301 The Auditor's Responses to the Risks of Material Misstatement

Objective: Design and implement audit responses to assessed risks.

Overall Responses:
- Assignment of personnel
- Supervision requirements
- Unpredictability in procedures
- General audit approach

Responses to Significant Risks:
- Tests of controls if relying on controls
- Substantive procedures specifically responsive
- Cannot use analytical procedures alone

Substantive Procedures:
- Tests of details
- Substantive analytical procedures
- Timing considerations
- Extent of testing

Nature of Procedures:
- More reliable evidence for higher risks
- Tests of details vs analytical procedures
- External vs internal evidence
- Direct vs indirect evidence

Extent of Testing:
- Sample sizes
- Number of items selected
- More testing for higher risks

Timing Considerations:
- Tests closer to period end for higher risks
- Procedures at interim require roll-forward
        """
    },
    {
        "document_type": "pcaob_rule",
        "title": "AS 2810 - Evaluating Audit Results",
        "standard_code": "AS 2810",
        "source": "PCAOB",
        "version": "2024",
        "content": """
AS 2810 Evaluating Audit Results

Objective: Evaluate audit results to determine whether audit opinion is supported.

Evaluation Process:
1. Accumulate misstatements
2. Consider materiality
3. Evaluate audit evidence
4. Evaluate financial statement presentation

Evaluating Misstatements:
- Known misstatements
- Likely misstatements
- Qualitative considerations
- Prior period uncorrected misstatements

Materiality Considerations:
- Individual misstatements
- Aggregate of misstatements
- Both quantitative and qualitative

Evaluating Sufficiency of Evidence:
- All relevant assertions addressed
- Contradictory evidence resolved
- Need for additional procedures

Management Representations:
- Required in all audits
- Cannot substitute for evidence
- Evaluate reliability

Going Concern Considerations:
- Substantial doubt indicators
- Management's plans evaluation
- Disclosure adequacy
        """
    }
]

# Audit Procedure Templates
AUDIT_PROCEDURES = [
    {
        "document_type": "aicpa_guidance",
        "title": "Cash Audit Procedures",
        "standard_code": "CASH-001",
        "source": "AICPA",
        "version": "2024",
        "content": """
Cash Audit Procedures - Comprehensive Checklist

1. Bank Confirmations:
   - Send confirmations to all banks
   - Confirm balance, loans, contingencies
   - Follow up on non-responses
   - Test cutoff of deposits/checks in transit

2. Bank Reconciliations:
   - Obtain all bank reconciliations
   - Foot and cross-foot
   - Trace to general ledger
   - Vouch outstanding checks (large/old items)
   - Trace deposits in transit to cutoff statement
   - Investigate unusual reconciling items

3. Cash Count (if applicable):
   - Surprise count preferred
   - Count all cash simultaneously
   - Obtain signed receipt
   - Trace to books

4. Analytical Procedures:
   - Days cash on hand
   - Cash as % of current assets
   - Compare to prior period
   - Investigate unusual fluctuations

5. Restricted Cash:
   - Identify all restrictions
   - Test classification
   - Review disclosure

6. Foreign Currency:
   - Test translation rates
   - Review gain/loss calculations
   - Test hedge accounting if applicable

Common Red Flags:
- Frequent bank transfers near period end
- Unusual reconciling items
- Stale outstanding checks
- Negative bank confirmations
- Multiple accounts at same institution
        """
    },
    {
        "document_type": "aicpa_guidance",
        "title": "Revenue Audit Procedures",
        "standard_code": "REV-001",
        "source": "AICPA",
        "version": "2024",
        "content": """
Revenue Audit Procedures - ASC 606 Focused

1. Understanding Revenue Streams:
   - Document all revenue types
   - Identify performance obligations
   - Understand timing of recognition
   - Map to five-step model

2. Contract Review:
   - Select sample of contracts
   - Identify performance obligations
   - Verify transaction price
   - Test allocation methodology
   - Confirm recognition timing

3. Cutoff Testing:
   - Select transactions before/after year-end
   - Trace to shipping documents
   - Verify proper period recording
   - Test bills of lading/delivery receipts

4. Substantive Analytical Procedures:
   - Gross margin analysis by product/service
   - Revenue per day trend analysis
   - Comparison to industry benchmarks
   - Sales per customer analysis
   - Unusual trends investigation

5. Tests of Details:
   - Vouch revenue to source documents
   - Test pricing authorization
   - Verify customer credit approval
   - Test accounts receivable aging
   - Confirm receivables with customers

6. Variable Consideration:
   - Test estimate methodology
   - Review constraint application
   - Test subsequent settlement
   - Evaluate disclosure

7. Contract Assets/Liabilities:
   - Test opening balances
   - Trace activity during period
   - Verify proper classification
   - Review disclosure

Fraud Indicators:
- Round-dollar transactions
- Near period-end transactions
- Bill and hold arrangements
- Channel stuffing
- Side agreements
- Related party sales
        """
    },
    {
        "document_type": "aicpa_guidance",
        "title": "Inventory Audit Procedures",
        "standard_code": "INV-001",
        "source": "AICPA",
        "version": "2024",
        "content": """
Inventory Audit Procedures

1. Physical Observation:
   - Plan observation procedures
   - Observe client's count
   - Perform test counts
   - Document condition and identify obsolete items
   - Control over count tags/sheets
   - Cutoff documentation

2. Inventory Valuation:
   - Test standard costs to actuals
   - Test overhead allocation
   - Review for lower of cost or NRV
   - Identify slow-moving/obsolete items
   - Test reserves for obsolescence

3. Inventory Costing:
   - Verify cost method (FIFO, average, etc.)
   - Test cost accumulation
   - Test overhead rates
   - Review variances
   - Test inventory layers (if LIFO)

4. Analytical Procedures:
   - Inventory turnover
   - Days in inventory
   - Gross margin analysis
   - Comparison to prior periods
   - Industry comparisons

5. Cutoff Testing:
   - Last receiving report number
   - Last shipping document number
   - Trace to purchases/sales
   - Review for proper period

6. Consignment/Third-Party Inventory:
   - Confirm quantities
   - Review agreements
   - Test ownership
   - Consider observation

Common Issues:
- Errors in count
- Obsolete inventory not identified
- Overhead allocation errors
- Cut-off problems
- Consignment inventory included/excluded improperly
- NRV not properly applied
        """
    }
]

def create_knowledge_document(doc: Dict) -> bool:
    """Create a knowledge document in the LLM service"""
    try:
        response = requests.post(
            f"{LLM_API_URL}/knowledge/documents",
            json=doc,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code in [200, 201]:
            data = response.json()
            doc_id = data.get('id', 'unknown')
            chunk_count = data.get('chunk_count', 0)
            print(f"  ✓ Created: {doc['title'][:50]}... ({chunk_count} chunks, ID: {doc_id[:8]}...)")
            return True
        else:
            error = response.json().get('detail', 'Unknown error')
            print(f"  ✗ Failed: {doc['title'][:50]}... - {error[:100]}")
            return False

    except Exception as e:
        print(f"  ✗ Error: {doc['title'][:50]}... - {str(e)[:100]}")
        return False

def populate_knowledge_base():
    """Populate the LLM knowledge base with comprehensive audit data"""

    print("=" * 70)
    print("POPULATING LLM KNOWLEDGE BASE FOR MAXIMUM AUDIT AUTOMATION")
    print("=" * 70)

    # 1. Load GAAP Standards
    print(f"\n📘 Loading {len(GAAP_STANDARDS)} GAAP Standards...")
    gaap_success = 0
    for standard in GAAP_STANDARDS:
        if create_knowledge_document(standard):
            gaap_success += 1
        time.sleep(0.5)
    print(f"   Loaded {gaap_success}/{len(GAAP_STANDARDS)} GAAP standards")

    # 2. Load PCAOB Standards
    print(f"\n📗 Loading {len(PCAOB_STANDARDS)} PCAOB Standards...")
    pcaob_success = 0
    for standard in PCAOB_STANDARDS:
        if create_knowledge_document(standard):
            pcaob_success += 1
        time.sleep(0.5)
    print(f"   Loaded {pcaob_success}/{len(PCAOB_STANDARDS)} PCAOB standards")

    # 3. Load Audit Procedures
    print(f"\n📙 Loading {len(AUDIT_PROCEDURES)} Audit Procedure Templates...")
    proc_success = 0
    for procedure in AUDIT_PROCEDURES:
        if create_knowledge_document(procedure):
            proc_success += 1
        time.sleep(0.5)
    print(f"   Loaded {proc_success}/{len(AUDIT_PROCEDURES)} procedure templates")

    # Summary
    total_docs = len(GAAP_STANDARDS) + len(PCAOB_STANDARDS) + len(AUDIT_PROCEDURES)
    total_success = gaap_success + pcaob_success + proc_success

    print("\n" + "=" * 70)
    print("KNOWLEDGE BASE POPULATION COMPLETE")
    print("=" * 70)
    print(f"Total Documents Loaded: {total_success}/{total_docs}")
    print(f"  - GAAP Standards: {gaap_success}/{len(GAAP_STANDARDS)}")
    print(f"  - PCAOB Standards: {pcaob_success}/{len(PCAOB_STANDARDS)}")
    print(f"  - Audit Procedures: {proc_success}/{len(AUDIT_PROCEDURES)}")
    print("\n🎯 AI is now ready to assist with comprehensive audit work!")
    print("=" * 70)

if __name__ == "__main__":
    populate_knowledge_base()
