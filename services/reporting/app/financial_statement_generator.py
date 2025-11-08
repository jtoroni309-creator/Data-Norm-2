"""
Financial Statement Generator
Generates balance sheet, income statement, cash flow statement from trial balance
"""
import logging
from datetime import date
from typing import Dict, List, Optional, Any
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class FinancialStatementGenerator:
    """Generate GAAP-compliant financial statements from trial balance"""

    # Account type classifications
    BALANCE_SHEET_ACCOUNTS = {
        'asset': {'statement': 'balance_sheet', 'section': 'assets', 'normal_balance': 'debit'},
        'liability': {'statement': 'balance_sheet', 'section': 'liabilities', 'normal_balance': 'credit'},
        'equity': {'statement': 'balance_sheet', 'section': 'equity', 'normal_balance': 'credit'}
    }

    INCOME_STATEMENT_ACCOUNTS = {
        'revenue': {'statement': 'income_statement', 'section': 'revenue', 'normal_balance': 'credit'},
        'expense': {'statement': 'income_statement', 'section': 'expenses', 'normal_balance': 'debit'}
    }

    def __init__(self, db: AsyncSession):
        """
        Initialize financial statement generator

        Args:
            db: Database session
        """
        self.db = db

    async def generate_balance_sheet(
        self,
        engagement_id: UUID,
        as_of_date: date,
        include_prior_year: bool = True
    ) -> Dict[str, Any]:
        """
        Generate balance sheet from trial balance

        Args:
            engagement_id: Engagement ID
            as_of_date: Balance sheet date
            include_prior_year: Include comparative prior year

        Returns:
            Balance sheet structure with assets, liabilities, equity
        """
        logger.info(f"Generating balance sheet for engagement {engagement_id} as of {as_of_date}")

        # Get trial balance data
        current_year_data = await self._get_trial_balance_summary(engagement_id, as_of_date)

        prior_year_data = None
        if include_prior_year:
            prior_year_date = date(as_of_date.year - 1, as_of_date.month, as_of_date.day)
            prior_year_data = await self._get_trial_balance_summary(engagement_id, prior_year_date)

        # Build balance sheet structure
        balance_sheet = {
            'statement_type': 'balance_sheet',
            'as_of_date': as_of_date.isoformat(),
            'company_name': current_year_data.get('company_name', 'Company Name'),
            'assets': self._build_assets_section(current_year_data, prior_year_data),
            'liabilities': self._build_liabilities_section(current_year_data, prior_year_data),
            'equity': self._build_equity_section(current_year_data, prior_year_data),
            'has_comparative': include_prior_year
        }

        # Calculate totals
        balance_sheet['total_assets_current'] = self._sum_section(balance_sheet['assets']['current_assets'])
        balance_sheet['total_assets_noncurrent'] = self._sum_section(balance_sheet['assets']['noncurrent_assets'])
        balance_sheet['total_assets'] = balance_sheet['total_assets_current'] + balance_sheet['total_assets_noncurrent']

        balance_sheet['total_liabilities_current'] = self._sum_section(balance_sheet['liabilities']['current_liabilities'])
        balance_sheet['total_liabilities_noncurrent'] = self._sum_section(balance_sheet['liabilities']['noncurrent_liabilities'])
        balance_sheet['total_liabilities'] = balance_sheet['total_liabilities_current'] + balance_sheet['total_liabilities_noncurrent']

        balance_sheet['total_equity'] = self._sum_section(balance_sheet['equity'])
        balance_sheet['total_liabilities_and_equity'] = balance_sheet['total_liabilities'] + balance_sheet['total_equity']

        # Verify balance
        balance_sheet['in_balance'] = abs(balance_sheet['total_assets'] - balance_sheet['total_liabilities_and_equity']) < 0.01

        return balance_sheet

    async def generate_income_statement(
        self,
        engagement_id: UUID,
        period_start: date,
        period_end: date,
        include_prior_year: bool = True
    ) -> Dict[str, Any]:
        """
        Generate income statement from trial balance

        Args:
            engagement_id: Engagement ID
            period_start: Period start date
            period_end: Period end date
            include_prior_year: Include comparative prior year

        Returns:
            Income statement structure
        """
        logger.info(f"Generating income statement for engagement {engagement_id} for period {period_start} to {period_end}")

        # Get trial balance data for period
        current_year_data = await self._get_trial_balance_summary(engagement_id, period_end, period_start)

        prior_year_data = None
        if include_prior_year:
            prior_year_start = date(period_start.year - 1, period_start.month, period_start.day)
            prior_year_end = date(period_end.year - 1, period_end.month, period_end.day)
            prior_year_data = await self._get_trial_balance_summary(engagement_id, prior_year_end, prior_year_start)

        # Build income statement
        income_statement = {
            'statement_type': 'income_statement',
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'company_name': current_year_data.get('company_name', 'Company Name'),
            'revenue': self._build_revenue_section(current_year_data, prior_year_data),
            'cost_of_revenue': self._build_cost_of_revenue_section(current_year_data, prior_year_data),
            'operating_expenses': self._build_operating_expenses_section(current_year_data, prior_year_data),
            'other_income_expense': self._build_other_income_expense_section(current_year_data, prior_year_data),
            'has_comparative': include_prior_year
        }

        # Calculate totals
        income_statement['total_revenue'] = self._sum_section(income_statement['revenue'])
        income_statement['total_cost_of_revenue'] = self._sum_section(income_statement['cost_of_revenue'])
        income_statement['gross_profit'] = income_statement['total_revenue'] - income_statement['total_cost_of_revenue']
        income_statement['gross_margin_pct'] = (income_statement['gross_profit'] / income_statement['total_revenue'] * 100) if income_statement['total_revenue'] > 0 else 0

        income_statement['total_operating_expenses'] = self._sum_section(income_statement['operating_expenses'])
        income_statement['operating_income'] = income_statement['gross_profit'] - income_statement['total_operating_expenses']

        income_statement['total_other_income_expense'] = self._sum_section(income_statement['other_income_expense'])
        income_statement['income_before_taxes'] = income_statement['operating_income'] + income_statement['total_other_income_expense']

        # Get tax expense from trial balance
        income_statement['income_tax_expense'] = self._get_account_balance(current_year_data, 'income_tax_expense', 0)
        income_statement['net_income'] = income_statement['income_before_taxes'] - income_statement['income_tax_expense']

        return income_statement

    async def generate_statement_of_cash_flows(
        self,
        engagement_id: UUID,
        period_start: date,
        period_end: date,
        method: str = 'indirect'
    ) -> Dict[str, Any]:
        """
        Generate statement of cash flows (indirect method)

        Args:
            engagement_id: Engagement ID
            period_start: Period start date
            period_end: Period end date
            method: 'indirect' or 'direct'

        Returns:
            Cash flow statement structure
        """
        logger.info(f"Generating cash flow statement ({method} method) for engagement {engagement_id}")

        # For indirect method, start with net income
        income_stmt = await self.generate_income_statement(engagement_id, period_start, period_end, include_prior_year=False)

        # Get balance sheet changes
        current_bs = await self.generate_balance_sheet(engagement_id, period_end, include_prior_year=False)
        prior_bs = await self.generate_balance_sheet(
            engagement_id,
            date(period_start.year, period_start.month, period_start.day),
            include_prior_year=False
        )

        # Build cash flow statement (indirect method)
        cash_flow_statement = {
            'statement_type': 'cash_flow_statement',
            'method': method,
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'company_name': current_bs.get('company_name', 'Company Name'),
        }

        if method == 'indirect':
            cash_flow_statement['operating_activities'] = self._build_operating_cash_flows_indirect(
                income_stmt,
                current_bs,
                prior_bs
            )
            cash_flow_statement['investing_activities'] = self._build_investing_cash_flows(current_bs, prior_bs)
            cash_flow_statement['financing_activities'] = self._build_financing_cash_flows(current_bs, prior_bs)

            # Calculate totals
            cash_flow_statement['net_cash_from_operating'] = self._sum_section(cash_flow_statement['operating_activities'])
            cash_flow_statement['net_cash_from_investing'] = self._sum_section(cash_flow_statement['investing_activities'])
            cash_flow_statement['net_cash_from_financing'] = self._sum_section(cash_flow_statement['financing_activities'])

            cash_flow_statement['net_change_in_cash'] = (
                cash_flow_statement['net_cash_from_operating'] +
                cash_flow_statement['net_cash_from_investing'] +
                cash_flow_statement['net_cash_from_financing']
            )

            # Cash reconciliation
            beginning_cash = self._get_beginning_cash(prior_bs)
            ending_cash = self._get_ending_cash(current_bs)

            cash_flow_statement['cash_beginning_of_period'] = beginning_cash
            cash_flow_statement['cash_end_of_period'] = ending_cash
            cash_flow_statement['calculated_cash_change'] = ending_cash - beginning_cash

            # Verify
            cash_flow_statement['reconciles'] = abs(
                cash_flow_statement['net_change_in_cash'] - cash_flow_statement['calculated_cash_change']
            ) < 0.01

        return cash_flow_statement

    async def _get_trial_balance_summary(
        self,
        engagement_id: UUID,
        as_of_date: date,
        from_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get trial balance summary with mapped accounts

        Args:
            engagement_id: Engagement ID
            as_of_date: As of date
            from_date: From date for period-based queries

        Returns:
            Trial balance data organized by account type
        """
        # Query trial balance with mapped accounts
        query = text("""
            SELECT
                coa.account_code,
                coa.account_name,
                coa.account_type,
                coa.account_subtype,
                coa.normal_balance,
                tbl.balance_amount,
                tbl.debit_amount,
                tbl.credit_amount
            FROM atlas.trial_balances tb
            JOIN atlas.trial_balance_lines tbl ON tbl.trial_balance_id = tb.id
            JOIN atlas.chart_of_accounts coa ON coa.id = tbl.mapped_account_id
            WHERE tb.engagement_id = :engagement_id
            AND tb.period_end_date = :as_of_date
            AND coa.is_active = true
            ORDER BY coa.account_code
        """)

        result = await self.db.execute(query, {
            'engagement_id': engagement_id,
            'as_of_date': as_of_date
        })

        rows = result.fetchall()

        # Organize by account type
        summary = {
            'as_of_date': as_of_date,
            'accounts': {},
            'by_type': {}
        }

        for row in rows:
            account_code, account_name, account_type, account_subtype, normal_balance, balance, debit, credit = row

            account_data = {
                'account_code': account_code,
                'account_name': account_name,
                'account_type': account_type,
                'account_subtype': account_subtype,
                'normal_balance': normal_balance,
                'balance': float(balance) if balance else 0.0,
                'debit': float(debit) if debit else 0.0,
                'credit': float(credit) if credit else 0.0
            }

            summary['accounts'][account_code] = account_data

            # Group by type
            if account_type not in summary['by_type']:
                summary['by_type'][account_type] = []
            summary['by_type'][account_type].append(account_data)

        return summary

    def _build_assets_section(self, current_data: Dict, prior_data: Optional[Dict]) -> Dict:
        """Build assets section of balance sheet"""
        assets = {
            'current_assets': [],
            'noncurrent_assets': []
        }

        # Get asset accounts
        asset_accounts = current_data.get('by_type', {}).get('asset', [])

        for account in asset_accounts:
            line_item = {
                'account_code': account['account_code'],
                'description': account['account_name'],
                'current_year': account['balance'],
                'prior_year': self._get_prior_year_balance(prior_data, account['account_code']) if prior_data else None
            }

            # Classify as current or non-current based on subtype
            if account.get('account_subtype') == 'current':
                assets['current_assets'].append(line_item)
            else:
                assets['noncurrent_assets'].append(line_item)

        return assets

    def _build_liabilities_section(self, current_data: Dict, prior_data: Optional[Dict]) -> Dict:
        """Build liabilities section of balance sheet"""
        liabilities = {
            'current_liabilities': [],
            'noncurrent_liabilities': []
        }

        liability_accounts = current_data.get('by_type', {}).get('liability', [])

        for account in liability_accounts:
            line_item = {
                'account_code': account['account_code'],
                'description': account['account_name'],
                'current_year': account['balance'],
                'prior_year': self._get_prior_year_balance(prior_data, account['account_code']) if prior_data else None
            }

            if account.get('account_subtype') == 'current':
                liabilities['current_liabilities'].append(line_item)
            else:
                liabilities['noncurrent_liabilities'].append(line_item)

        return liabilities

    def _build_equity_section(self, current_data: Dict, prior_data: Optional[Dict]) -> List[Dict]:
        """Build equity section of balance sheet"""
        equity = []

        equity_accounts = current_data.get('by_type', {}).get('equity', [])

        for account in equity_accounts:
            equity.append({
                'account_code': account['account_code'],
                'description': account['account_name'],
                'current_year': account['balance'],
                'prior_year': self._get_prior_year_balance(prior_data, account['account_code']) if prior_data else None
            })

        return equity

    def _build_revenue_section(self, current_data: Dict, prior_data: Optional[Dict]) -> List[Dict]:
        """Build revenue section of income statement"""
        revenue = []

        revenue_accounts = current_data.get('by_type', {}).get('revenue', [])

        for account in revenue_accounts:
            # Revenue accounts have credit normal balance, so balance is positive
            revenue.append({
                'account_code': account['account_code'],
                'description': account['account_name'],
                'current_year': account['balance'],
                'prior_year': self._get_prior_year_balance(prior_data, account['account_code']) if prior_data else None
            })

        return revenue

    def _build_cost_of_revenue_section(self, current_data: Dict, prior_data: Optional[Dict]) -> List[Dict]:
        """Build cost of revenue section"""
        # Filter expense accounts that are cost of revenue
        cost_accounts = [
            acc for acc in current_data.get('by_type', {}).get('expense', [])
            if 'cost' in acc['account_name'].lower() or 'cogs' in acc['account_name'].lower()
        ]

        return [{
            'account_code': acc['account_code'],
            'description': acc['account_name'],
            'current_year': acc['balance'],
            'prior_year': self._get_prior_year_balance(prior_data, acc['account_code']) if prior_data else None
        } for acc in cost_accounts]

    def _build_operating_expenses_section(self, current_data: Dict, prior_data: Optional[Dict]) -> List[Dict]:
        """Build operating expenses section"""
        # Filter expense accounts that are operating expenses (exclude cost of revenue)
        op_expense_accounts = [
            acc for acc in current_data.get('by_type', {}).get('expense', [])
            if not ('cost' in acc['account_name'].lower() or 'cogs' in acc['account_name'].lower())
            and 'tax' not in acc['account_name'].lower()
        ]

        return [{
            'account_code': acc['account_code'],
            'description': acc['account_name'],
            'current_year': acc['balance'],
            'prior_year': self._get_prior_year_balance(prior_data, acc['account_code']) if prior_data else None
        } for acc in op_expense_accounts]

    def _build_other_income_expense_section(self, current_data: Dict, prior_data: Optional[Dict]) -> List[Dict]:
        """Build other income/expense section"""
        # This would include interest income/expense, gains/losses, etc.
        # For now, return empty - would need more sophisticated account classification
        return []

    def _build_operating_cash_flows_indirect(
        self,
        income_stmt: Dict,
        current_bs: Dict,
        prior_bs: Dict
    ) -> List[Dict]:
        """Build operating cash flows using indirect method"""
        cash_flows = []

        # Start with net income
        cash_flows.append({
            'description': 'Net Income',
            'amount': income_stmt['net_income']
        })

        # Add back non-cash expenses (depreciation, amortization)
        # This would need to be extracted from expense accounts
        # For now, placeholder

        # Adjustments for changes in working capital
        # Increase in A/R is a use of cash
        # Increase in A/P is a source of cash, etc.

        return cash_flows

    def _build_investing_cash_flows(self, current_bs: Dict, prior_bs: Dict) -> List[Dict]:
        """Build investing cash flows"""
        # Capital expenditures, asset purchases/sales, investments
        return []

    def _build_financing_cash_flows(self, current_bs: Dict, prior_bs: Dict) -> List[Dict]:
        """Build financing cash flows"""
        # Debt issuance/repayment, equity transactions, dividends
        return []

    def _get_prior_year_balance(self, prior_data: Optional[Dict], account_code: str) -> Optional[float]:
        """Get prior year balance for an account"""
        if not prior_data:
            return None
        account = prior_data.get('accounts', {}).get(account_code)
        return account['balance'] if account else 0.0

    def _get_account_balance(self, data: Dict, account_identifier: str, default: float = 0.0) -> float:
        """Get account balance by code or name pattern"""
        for account_code, account_data in data.get('accounts', {}).items():
            if account_identifier in account_code.lower() or account_identifier in account_data['account_name'].lower():
                return account_data['balance']
        return default

    def _get_beginning_cash(self, balance_sheet: Dict) -> float:
        """Get beginning cash balance"""
        cash_accounts = balance_sheet.get('assets', {}).get('current_assets', [])
        for account in cash_accounts:
            if 'cash' in account['description'].lower():
                return account.get('prior_year', 0.0) or 0.0
        return 0.0

    def _get_ending_cash(self, balance_sheet: Dict) -> float:
        """Get ending cash balance"""
        cash_accounts = balance_sheet.get('assets', {}).get('current_assets', [])
        for account in cash_accounts:
            if 'cash' in account['description'].lower():
                return account.get('current_year', 0.0)
        return 0.0

    def _sum_section(self, section: List[Dict]) -> float:
        """Sum all amounts in a section"""
        if isinstance(section, dict):
            section = list(section.values())
        return sum(item.get('current_year', 0.0) for item in section if isinstance(item, dict))
