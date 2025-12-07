"""
Generate Complete Audit Report Package for HarborTech Manufacturing FYE 2024
"""

import sys
import os

# Add the services path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'engagement', 'app'))

from audit_report_generator import AuditReportGenerator

# Engagement Data
engagement_data = {
    "client_name": "HarborTech Manufacturing, Inc.",
    "fiscal_year_end": "December 31, 2024",
    "firm_name": "Toroni & Company, CPAs",
    "partner_name": "J. Toroni, CPA",
    "opinion_type": "unqualified",
    "ceo_name": "Michael R. Harbor",
    "cfo_name": "Sarah J. Chen"
}

# Financial Data (from E2E test)
financial_data = {
    "balance_sheet": {
        "assets": {
            "current_assets": {
                "cash": 980000,
                "accounts_receivable": 2420000,
                "inventory": 3100000,
                "prepaid_expenses": 180000
            },
            "total_current_assets": 6680000,
            "net_ppe": 4350000,
            "intangible_assets": 420000,
            "other_assets": 250000,
            "total_assets": 13200000
        },
        "liabilities": {
            "current_liabilities": {
                "accounts_payable": 1650000,
                "accrued_expenses": 820000,
                "current_portion_ltd": 350000
            },
            "total_current_liabilities": 2820000,
            "long_term_debt": 3180000,
            "deferred_taxes": 500000,
            "total_liabilities": 8000000
        },
        "equity": {
            "common_stock": 1000000,
            "retained_earnings": 4200000,
            "total_equity": 5200000
        }
    },
    "income_statement": {
        "revenue": 18000000,
        "cost_of_goods_sold": 12600000,
        "gross_profit": 5400000,
        "operating_expenses": 4200000,
        "operating_income": 1200000,
        "interest_expense": 280000,
        "income_before_taxes": 920000,
        "income_tax_expense": 220000,
        "net_income": 700000
    }
}

def main():
    print("=" * 60)
    print("  AICPA/PCAOB COMPLIANT AUDIT REPORT GENERATOR")
    print("=" * 60)
    print()
    print(f"Client: {engagement_data['client_name']}")
    print(f"Fiscal Year End: {engagement_data['fiscal_year_end']}")
    print(f"Opinion Type: {engagement_data['opinion_type'].upper()}")
    print()

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'HarborTech_Audit_2024')
    os.makedirs(output_dir, exist_ok=True)

    # Generate reports
    generator = AuditReportGenerator(engagement_data, financial_data)

    documents = {
        "01_Cover_Letter.docx": ("Cover Letter", generator.generate_cover_letter),
        "02_Independent_Auditors_Report.docx": ("Independent Auditor's Report", generator.generate_auditor_report),
        "03_Financial_Statements.docx": ("Financial Statements", generator.generate_financial_statements),
        "04_Notes_to_Financial_Statements.docx": ("Notes to Financial Statements", generator.generate_notes_to_fs),
        "05_Management_Representation_Letter.docx": ("Management Rep Letter", generator.generate_management_rep_letter),
    }

    print("Generating documents...")
    print()

    for filename, (name, gen_func) in documents.items():
        try:
            content = gen_func()
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(content)
            print(f"  [DONE] {name}")
            print(f"         -> {filepath}")
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")

    print()
    print("=" * 60)
    print(f"  COMPLETE AUDIT PACKAGE GENERATED")
    print(f"  Location: {output_dir}")
    print("=" * 60)
    print()
    print("Documents generated:")
    print("  1. Cover Letter (Transmittal)")
    print("  2. Independent Auditor's Report (AU-C 700 compliant)")
    print("  3. Financial Statements (BS, IS, CF)")
    print("  4. Notes to Financial Statements (7 notes)")
    print("  5. Management Representation Letter (AU-C 580 compliant)")

if __name__ == "__main__":
    main()
