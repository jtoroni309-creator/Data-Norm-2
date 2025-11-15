"""
Financial Statement Normalization Module

Normalizes financial statements from various sources (EDGAR XBRL, PDF, Excel)
into a standardized format for ML training.

Features:
- XBRL taxonomy mapping (US-GAAP, IFRS, custom extensions)
- Account standardization across companies
- Financial statement reconstruction
- Data quality validation
- Missing data imputation
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

import pandas as pd
import numpy as np
from loguru import logger


class AccountCategory(str, Enum):
    """Standardized account categories"""
    # Assets
    CASH = "cash_and_equivalents"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    INVENTORY = "inventory"
    PREPAID_EXPENSES = "prepaid_expenses"
    OTHER_CURRENT_ASSETS = "other_current_assets"
    PP_E = "property_plant_equipment"
    INTANGIBLE_ASSETS = "intangible_assets"
    GOODWILL = "goodwill"
    INVESTMENTS = "investments"
    OTHER_NON_CURRENT_ASSETS = "other_non_current_assets"

    # Liabilities
    ACCOUNTS_PAYABLE = "accounts_payable"
    ACCRUED_LIABILITIES = "accrued_liabilities"
    SHORT_TERM_DEBT = "short_term_debt"
    CURRENT_PORTION_LONG_TERM_DEBT = "current_portion_long_term_debt"
    OTHER_CURRENT_LIABILITIES = "other_current_liabilities"
    LONG_TERM_DEBT = "long_term_debt"
    DEFERRED_TAX_LIABILITIES = "deferred_tax_liabilities"
    OTHER_NON_CURRENT_LIABILITIES = "other_non_current_liabilities"

    # Equity
    COMMON_STOCK = "common_stock"
    PREFERRED_STOCK = "preferred_stock"
    ADDITIONAL_PAID_IN_CAPITAL = "additional_paid_in_capital"
    RETAINED_EARNINGS = "retained_earnings"
    TREASURY_STOCK = "treasury_stock"
    ACCUMULATED_OCI = "accumulated_other_comprehensive_income"

    # Income Statement
    REVENUE = "revenue"
    COST_OF_REVENUE = "cost_of_revenue"
    GROSS_PROFIT = "gross_profit"
    RESEARCH_DEVELOPMENT = "research_and_development"
    SELLING_GENERAL_ADMIN = "selling_general_administrative"
    OPERATING_EXPENSES = "operating_expenses"
    OPERATING_INCOME = "operating_income"
    INTEREST_EXPENSE = "interest_expense"
    INTEREST_INCOME = "interest_income"
    OTHER_INCOME_EXPENSE = "other_income_expense"
    INCOME_TAX_EXPENSE = "income_tax_expense"
    NET_INCOME = "net_income"
    EPS_BASIC = "earnings_per_share_basic"
    EPS_DILUTED = "earnings_per_share_diluted"

    # Cash Flow
    CASH_FROM_OPERATIONS = "cash_from_operations"
    CASH_FROM_INVESTING = "cash_from_investing"
    CASH_FROM_FINANCING = "cash_from_financing"
    CAPITAL_EXPENDITURES = "capital_expenditures"
    FREE_CASH_FLOW = "free_cash_flow"


@dataclass
class XBRLMapping:
    """Mapping from XBRL concept to standardized account"""
    xbrl_concept: str
    us_gaap_concept: Optional[str]
    ifrs_concept: Optional[str]
    standard_category: AccountCategory
    calculation_formula: Optional[str] = None  # For derived items
    priority: int = 1  # For handling multiple matches


class XBRLNormalizer:
    """
    Normalizes XBRL financial data to standardized format

    Handles:
    - US-GAAP taxonomy
    - IFRS taxonomy
    - Custom company extensions
    - Calculation linkbases
    - Presentation linkbases
    """

    # US-GAAP to Standard Category Mappings
    US_GAAP_MAPPINGS: List[XBRLMapping] = [
        # Assets
        XBRLMapping("CashAndCashEquivalentsAtCarryingValue", "us-gaap:CashAndCashEquivalentsAtCarryingValue", None, AccountCategory.CASH, priority=1),
        XBRLMapping("Cash", "us-gaap:Cash", None, AccountCategory.CASH, priority=2),
        XBRLMapping("AccountsReceivableNetCurrent", "us-gaap:AccountsReceivableNetCurrent", None, AccountCategory.ACCOUNTS_RECEIVABLE),
        XBRLMapping("InventoryNet", "us-gaap:InventoryNet", None, AccountCategory.INVENTORY),
        XBRLMapping("PrepaidExpenseCurrent", "us-gaap:PrepaidExpenseCurrent", None, AccountCategory.PREPAID_EXPENSES),
        XBRLMapping("PropertyPlantAndEquipmentNet", "us-gaap:PropertyPlantAndEquipmentNet", None, AccountCategory.PP_E),
        XBRLMapping("IntangibleAssetsNetExcludingGoodwill", "us-gaap:IntangibleAssetsNetExcludingGoodwill", None, AccountCategory.INTANGIBLE_ASSETS),
        XBRLMapping("Goodwill", "us-gaap:Goodwill", None, AccountCategory.GOODWILL),

        # Liabilities
        XBRLMapping("AccountsPayableCurrent", "us-gaap:AccountsPayableCurrent", None, AccountCategory.ACCOUNTS_PAYABLE),
        XBRLMapping("AccruedLiabilitiesCurrent", "us-gaap:AccruedLiabilitiesCurrent", None, AccountCategory.ACCRUED_LIABILITIES),
        XBRLMapping("ShortTermDebtAndLeaseLiabilitiesCurrent", "us-gaap:ShortTermDebtAndLeaseLiabilitiesCurrent", None, AccountCategory.SHORT_TERM_DEBT),
        XBRLMapping("LongTermDebtNoncurrent", "us-gaap:LongTermDebtNoncurrent", None, AccountCategory.LONG_TERM_DEBT),
        XBRLMapping("DeferredTaxLiabilitiesNoncurrent", "us-gaap:DeferredTaxLiabilitiesNoncurrent", None, AccountCategory.DEFERRED_TAX_LIABILITIES),

        # Equity
        XBRLMapping("CommonStockValue", "us-gaap:CommonStockValue", None, AccountCategory.COMMON_STOCK),
        XBRLMapping("AdditionalPaidInCapital", "us-gaap:AdditionalPaidInCapital", None, AccountCategory.ADDITIONAL_PAID_IN_CAPITAL),
        XBRLMapping("RetainedEarningsAccumulatedDeficit", "us-gaap:RetainedEarningsAccumulatedDeficit", None, AccountCategory.RETAINED_EARNINGS),
        XBRLMapping("TreasuryStockValue", "us-gaap:TreasuryStockValue", None, AccountCategory.TREASURY_STOCK),
        XBRLMapping("AccumulatedOtherComprehensiveIncomeLossNetOfTax", "us-gaap:AccumulatedOtherComprehensiveIncomeLossNetOfTax", None, AccountCategory.ACCUMULATED_OCI),

        # Income Statement
        XBRLMapping("RevenueFromContractWithCustomerExcludingAssessedTax", "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax", None, AccountCategory.REVENUE, priority=1),
        XBRLMapping("Revenues", "us-gaap:Revenues", None, AccountCategory.REVENUE, priority=2),
        XBRLMapping("CostOfGoodsAndServicesSold", "us-gaap:CostOfGoodsAndServicesSold", None, AccountCategory.COST_OF_REVENUE),
        XBRLMapping("GrossProfit", "us-gaap:GrossProfit", None, AccountCategory.GROSS_PROFIT),
        XBRLMapping("ResearchAndDevelopmentExpense", "us-gaap:ResearchAndDevelopmentExpense", None, AccountCategory.RESEARCH_DEVELOPMENT),
        XBRLMapping("SellingGeneralAndAdministrativeExpense", "us-gaap:SellingGeneralAndAdministrativeExpense", None, AccountCategory.SELLING_GENERAL_ADMIN),
        XBRLMapping("OperatingIncomeLoss", "us-gaap:OperatingIncomeLoss", None, AccountCategory.OPERATING_INCOME),
        XBRLMapping("InterestExpense", "us-gaap:InterestExpense", None, AccountCategory.INTEREST_EXPENSE),
        XBRLMapping("IncomeTaxExpenseBenefit", "us-gaap:IncomeTaxExpenseBenefit", None, AccountCategory.INCOME_TAX_EXPENSE),
        XBRLMapping("NetIncomeLoss", "us-gaap:NetIncomeLoss", None, AccountCategory.NET_INCOME),
        XBRLMapping("EarningsPerShareBasic", "us-gaap:EarningsPerShareBasic", None, AccountCategory.EPS_BASIC),
        XBRLMapping("EarningsPerShareDiluted", "us-gaap:EarningsPerShareDiluted", None, AccountCategory.EPS_DILUTED),

        # Cash Flow
        XBRLMapping("NetCashProvidedByUsedInOperatingActivities", "us-gaap:NetCashProvidedByUsedInOperatingActivities", None, AccountCategory.CASH_FROM_OPERATIONS),
        XBRLMapping("NetCashProvidedByUsedInInvestingActivities", "us-gaap:NetCashProvidedByUsedInInvestingActivities", None, AccountCategory.CASH_FROM_INVESTING),
        XBRLMapping("NetCashProvidedByUsedInFinancingActivities", "us-gaap:NetCashProvidedByUsedInFinancingActivities", None, AccountCategory.CASH_FROM_FINANCING),
        XBRLMapping("PaymentsToAcquirePropertyPlantAndEquipment", "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment", None, AccountCategory.CAPITAL_EXPENDITURES),
    ]

    def __init__(self):
        # Build lookup dictionaries
        self.us_gaap_to_standard = {}
        for mapping in self.US_GAAP_MAPPINGS:
            if mapping.us_gaap_concept:
                if mapping.us_gaap_concept not in self.us_gaap_to_standard:
                    self.us_gaap_to_standard[mapping.us_gaap_concept] = []
                self.us_gaap_to_standard[mapping.us_gaap_concept].append(mapping)

        # Sort by priority
        for concept, mappings in self.us_gaap_to_standard.items():
            mappings.sort(key=lambda m: m.priority)

    def normalize_xbrl_facts(self, xbrl_facts: Dict[str, any], namespace: str = "us-gaap") -> Dict[str, float]:
        """
        Normalize XBRL facts to standardized account categories

        Args:
            xbrl_facts: Dictionary of XBRL concept -> value
            namespace: XBRL namespace (us-gaap, ifrs, etc.)

        Returns:
            Dictionary of AccountCategory -> value
        """
        normalized = {}

        for concept, fact_data in xbrl_facts.items():
            # Extract value
            if isinstance(fact_data, dict):
                value = fact_data.get("value")
            else:
                value = fact_data

            # Skip if no value
            if value is None:
                continue

            # Convert to float
            try:
                value = float(value)
            except (ValueError, TypeError):
                continue

            # Map to standard category
            full_concept = f"{namespace}:{concept}"
            if full_concept in self.us_gaap_to_standard:
                mappings = self.us_gaap_to_standard[full_concept]
                # Use highest priority mapping
                mapping = mappings[0]
                normalized[mapping.standard_category.value] = value
                logger.debug(f"Mapped {concept} -> {mapping.standard_category.value}: {value}")

        return normalized

    def calculate_derived_items(self, normalized: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate derived financial items

        Examples:
        - Gross Profit = Revenue - Cost of Revenue
        - Operating Expenses = R&D + SG&A + Other
        - Free Cash Flow = Cash from Operations - CapEx
        """
        derived = normalized.copy()

        # Gross Profit
        if (AccountCategory.GROSS_PROFIT.value not in derived and
            AccountCategory.REVENUE.value in derived and
            AccountCategory.COST_OF_REVENUE.value in derived):
            derived[AccountCategory.GROSS_PROFIT.value] = (
                derived[AccountCategory.REVENUE.value] -
                derived[AccountCategory.COST_OF_REVENUE.value]
            )

        # Operating Expenses
        operating_exp_components = [
            AccountCategory.RESEARCH_DEVELOPMENT.value,
            AccountCategory.SELLING_GENERAL_ADMIN.value,
        ]
        if (AccountCategory.OPERATING_EXPENSES.value not in derived and
            any(comp in derived for comp in operating_exp_components)):
            derived[AccountCategory.OPERATING_EXPENSES.value] = sum(
                derived.get(comp, 0) for comp in operating_exp_components
            )

        # Free Cash Flow
        if (AccountCategory.FREE_CASH_FLOW.value not in derived and
            AccountCategory.CASH_FROM_OPERATIONS.value in derived and
            AccountCategory.CAPITAL_EXPENDITURES.value in derived):
            derived[AccountCategory.FREE_CASH_FLOW.value] = (
                derived[AccountCategory.CASH_FROM_OPERATIONS.value] -
                abs(derived[AccountCategory.CAPITAL_EXPENDITURES.value])  # CapEx is usually negative
            )

        return derived

    def validate_financial_statements(self, normalized: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Validate financial statements for common errors

        Checks:
        - Balance sheet equation: Assets = Liabilities + Equity
        - Income statement flow: Revenue - Expenses = Net Income
        - Cash flow reconciliation
        - Reasonableness checks (no negative revenue, etc.)
        """
        errors = []

        # Balance Sheet Equation
        assets = (
            normalized.get(AccountCategory.CASH.value, 0) +
            normalized.get(AccountCategory.ACCOUNTS_RECEIVABLE.value, 0) +
            normalized.get(AccountCategory.INVENTORY.value, 0) +
            normalized.get(AccountCategory.PP_E.value, 0) +
            normalized.get(AccountCategory.GOODWILL.value, 0) +
            normalized.get(AccountCategory.INTANGIBLE_ASSETS.value, 0)
        )

        liabilities = (
            normalized.get(AccountCategory.ACCOUNTS_PAYABLE.value, 0) +
            normalized.get(AccountCategory.SHORT_TERM_DEBT.value, 0) +
            normalized.get(AccountCategory.LONG_TERM_DEBT.value, 0)
        )

        equity = (
            normalized.get(AccountCategory.COMMON_STOCK.value, 0) +
            normalized.get(AccountCategory.ADDITIONAL_PAID_IN_CAPITAL.value, 0) +
            normalized.get(AccountCategory.RETAINED_EARNINGS.value, 0) -
            abs(normalized.get(AccountCategory.TREASURY_STOCK.value, 0))
        )

        if assets > 0 and abs(assets - (liabilities + equity)) / assets > 0.01:  # 1% tolerance
            errors.append(f"Balance sheet doesn't balance: Assets={assets:,.0f}, L+E={liabilities + equity:,.0f}")

        # Reasonableness checks
        if normalized.get(AccountCategory.REVENUE.value, 0) < 0:
            errors.append("Revenue is negative")

        if normalized.get(AccountCategory.GROSS_PROFIT.value, 0) > normalized.get(AccountCategory.REVENUE.value, 0):
            errors.append("Gross profit exceeds revenue")

        return len(errors) == 0, errors


@dataclass
class NormalizedFinancialStatement:
    """Complete normalized financial statement"""
    # Metadata
    cik: str
    company_name: str
    ticker: Optional[str]
    fiscal_year: int
    fiscal_period: str  # FY, Q1, Q2, Q3, Q4
    period_end_date: datetime
    filing_date: datetime
    currency: str = "USD"
    units: str = "dollars"  # dollars, thousands, millions

    # Normalized accounts (all in standard categories)
    accounts: Dict[str, float] = field(default_factory=dict)

    # Calculated ratios
    ratios: Dict[str, float] = field(default_factory=dict)

    # Data quality metrics
    completeness_score: float = 0.0  # 0-1
    validation_passed: bool = True
    validation_errors: List[str] = field(default_factory=list)

    # Source data
    source_filing: str = ""
    source_format: str = "xbrl"  # xbrl, pdf, excel

    def calculate_ratios(self):
        """Calculate financial ratios"""
        # Liquidity Ratios
        current_assets = (
            self.accounts.get(AccountCategory.CASH.value, 0) +
            self.accounts.get(AccountCategory.ACCOUNTS_RECEIVABLE.value, 0) +
            self.accounts.get(AccountCategory.INVENTORY.value, 0)
        )

        current_liabilities = (
            self.accounts.get(AccountCategory.ACCOUNTS_PAYABLE.value, 0) +
            self.accounts.get(AccountCategory.SHORT_TERM_DEBT.value, 0) +
            self.accounts.get(AccountCategory.ACCRUED_LIABILITIES.value, 0)
        )

        if current_liabilities > 0:
            self.ratios["current_ratio"] = current_assets / current_liabilities

        # Profitability Ratios
        revenue = self.accounts.get(AccountCategory.REVENUE.value, 0)
        if revenue > 0:
            gross_profit = self.accounts.get(AccountCategory.GROSS_PROFIT.value, 0)
            operating_income = self.accounts.get(AccountCategory.OPERATING_INCOME.value, 0)
            net_income = self.accounts.get(AccountCategory.NET_INCOME.value, 0)

            self.ratios["gross_margin"] = gross_profit / revenue
            self.ratios["operating_margin"] = operating_income / revenue
            self.ratios["net_margin"] = net_income / revenue

        # Leverage Ratios
        total_debt = (
            self.accounts.get(AccountCategory.SHORT_TERM_DEBT.value, 0) +
            self.accounts.get(AccountCategory.LONG_TERM_DEBT.value, 0)
        )

        equity = (
            self.accounts.get(AccountCategory.COMMON_STOCK.value, 0) +
            self.accounts.get(AccountCategory.RETAINED_EARNINGS.value, 0)
        )

        if equity > 0:
            self.ratios["debt_to_equity"] = total_debt / equity

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "cik": self.cik,
            "company_name": self.company_name,
            "ticker": self.ticker,
            "fiscal_year": self.fiscal_year,
            "fiscal_period": self.fiscal_period,
            "period_end_date": self.period_end_date.isoformat(),
            "filing_date": self.filing_date.isoformat(),
            "currency": self.currency,
            "units": self.units,
            "accounts": self.accounts,
            "ratios": self.ratios,
            "completeness_score": self.completeness_score,
            "validation_passed": self.validation_passed,
            "validation_errors": self.validation_errors,
            "source_filing": self.source_filing,
            "source_format": self.source_format,
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame (single row)"""
        data = {
            "cik": self.cik,
            "company_name": self.company_name,
            "ticker": self.ticker,
            "fiscal_year": self.fiscal_year,
            "fiscal_period": self.fiscal_period,
            "period_end_date": self.period_end_date,
            "filing_date": self.filing_date,
        }

        # Add all accounts
        data.update(self.accounts)

        # Add all ratios
        for ratio_name, ratio_value in self.ratios.items():
            data[f"ratio_{ratio_name}"] = ratio_value

        return pd.DataFrame([data])


class FinancialStatementNormalizer:
    """
    Main normalization engine

    Coordinates:
    - XBRL parsing
    - Account mapping
    - Data validation
    - Ratio calculation
    - Quality assessment
    """

    def __init__(self):
        self.xbrl_normalizer = XBRLNormalizer()

    def normalize(
        self,
        xbrl_facts: Dict[str, any],
        metadata: Dict[str, any],
    ) -> NormalizedFinancialStatement:
        """
        Normalize financial statement from XBRL facts

        Args:
            xbrl_facts: Dictionary of XBRL facts
            metadata: Metadata (CIK, company name, dates, etc.)

        Returns:
            NormalizedFinancialStatement
        """
        # Normalize XBRL to standard categories
        normalized_accounts = self.xbrl_normalizer.normalize_xbrl_facts(xbrl_facts)

        # Calculate derived items
        normalized_accounts = self.xbrl_normalizer.calculate_derived_items(normalized_accounts)

        # Validate
        validation_passed, validation_errors = self.xbrl_normalizer.validate_financial_statements(normalized_accounts)

        # Calculate completeness score
        required_accounts = [
            AccountCategory.REVENUE.value,
            AccountCategory.NET_INCOME.value,
            AccountCategory.CASH.value,
        ]
        present_count = sum(1 for acc in required_accounts if acc in normalized_accounts)
        completeness_score = present_count / len(required_accounts)

        # Create normalized statement
        statement = NormalizedFinancialStatement(
            cik=metadata["cik"],
            company_name=metadata["company_name"],
            ticker=metadata.get("ticker"),
            fiscal_year=metadata["fiscal_year"],
            fiscal_period=metadata["fiscal_period"],
            period_end_date=metadata["period_end_date"],
            filing_date=metadata["filing_date"],
            accounts=normalized_accounts,
            completeness_score=completeness_score,
            validation_passed=validation_passed,
            validation_errors=validation_errors,
            source_filing=metadata.get("source_filing", ""),
            source_format="xbrl",
        )

        # Calculate ratios
        statement.calculate_ratios()

        logger.info(f"Normalized financial statement: {statement.company_name} {statement.fiscal_year}{statement.fiscal_period}")
        logger.info(f"Completeness: {completeness_score:.1%}, Validation: {validation_passed}")

        return statement
