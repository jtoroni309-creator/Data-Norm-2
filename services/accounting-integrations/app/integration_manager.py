"""
Unified Integration Management Service

Manages integrations across multiple accounting software providers (QuickBooks, Xero, etc.)
Provides unified API, chart of accounts mapping, and data normalization.

Features:
- Multi-provider support
- Chart of accounts mapping and normalization
- Automatic data sync scheduling
- Unified financial data format
- Error handling and retry logic
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StandardAccountType(str, Enum):
    """
    Standardized account types across all providers
    Based on GAAP/IFRS classifications
    """
    # Assets
    CASH = "cash"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    INVENTORY = "inventory"
    PREPAID_EXPENSES = "prepaid_expenses"
    OTHER_CURRENT_ASSETS = "other_current_assets"
    FIXED_ASSETS = "fixed_assets"
    ACCUMULATED_DEPRECIATION = "accumulated_depreciation"
    INTANGIBLE_ASSETS = "intangible_assets"
    OTHER_ASSETS = "other_assets"

    # Liabilities
    ACCOUNTS_PAYABLE = "accounts_payable"
    CREDIT_CARDS = "credit_cards"
    ACCRUED_EXPENSES = "accrued_expenses"
    SHORT_TERM_DEBT = "short_term_debt"
    OTHER_CURRENT_LIABILITIES = "other_current_liabilities"
    LONG_TERM_DEBT = "long_term_debt"
    OTHER_LIABILITIES = "other_liabilities"

    # Equity
    OWNERS_EQUITY = "owners_equity"
    RETAINED_EARNINGS = "retained_earnings"
    DIVIDENDS = "dividends"

    # Revenue
    OPERATING_REVENUE = "operating_revenue"
    OTHER_REVENUE = "other_revenue"

    # Expenses
    COST_OF_GOODS_SOLD = "cost_of_goods_sold"
    SALARIES_WAGES = "salaries_wages"
    RENT_EXPENSE = "rent_expense"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    DEPRECIATION_EXPENSE = "depreciation_expense"
    INTEREST_EXPENSE = "interest_expense"
    TAXES = "taxes"
    MARKETING_ADVERTISING = "marketing_advertising"
    PROFESSIONAL_FEES = "professional_fees"
    OFFICE_EXPENSES = "office_expenses"
    OTHER_EXPENSES = "other_expenses"


class StandardAccountCategory(str, Enum):
    """High-level account categories"""
    ASSETS = "assets"
    LIABILITIES = "liabilities"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSES = "expenses"


class AccountMapping(BaseModel):
    """Mapping between provider account and standard account"""
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    connection_id: UUID

    # Provider account details
    provider_account_id: str
    provider_account_name: str
    provider_account_type: str
    provider_account_number: Optional[str] = None

    # Standard mapping
    standard_account_type: StandardAccountType
    standard_account_category: StandardAccountCategory

    # Mapping metadata
    confidence_score: float = 1.0  # 0.0-1.0, auto-mapped or manual
    is_manual_override: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NormalizedAccount(BaseModel):
    """Normalized account format across all providers"""
    id: str
    name: str
    account_number: Optional[str] = None
    description: Optional[str] = None

    # Standard classification
    standard_type: StandardAccountType
    standard_category: StandardAccountCategory

    # Financial data
    current_balance: float = 0.0
    debit_balance: float = 0.0
    credit_balance: float = 0.0

    # Hierarchy
    parent_id: Optional[str] = None
    fully_qualified_name: Optional[str] = None

    # Metadata
    active: bool = True
    is_sub_account: bool = False

    # Provider details
    provider_type: str
    provider_account_id: str
    synced_at: datetime


class NormalizedFinancialStatement(BaseModel):
    """Normalized financial statement format"""
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    connection_id: UUID

    statement_type: str  # "balance_sheet", "income_statement", "cash_flow"
    period_start: datetime
    period_end: datetime

    # Line items
    line_items: List[Dict[str, Any]]

    # Totals by category
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    total_revenue: Optional[float] = None
    total_expenses: Optional[float] = None
    net_income: Optional[float] = None

    # Metadata
    currency: str = "USD"
    synced_at: datetime = Field(default_factory=datetime.utcnow)
    provider_type: str


class AccountMappingService:
    """
    Chart of Accounts mapping service

    Maps provider-specific account types to standardized account types,
    enabling consistent financial reporting across different accounting software.
    """

    def __init__(self):
        # In-memory storage (replace with database in production)
        self._mappings: Dict[UUID, AccountMapping] = {}

        # Pre-defined mapping rules
        self._quickbooks_rules = self._build_quickbooks_rules()
        self._xero_rules = self._build_xero_rules()

    def _build_quickbooks_rules(self) -> Dict[str, tuple]:
        """
        Build QuickBooks account type to standard type mapping rules

        Returns:
            Dict mapping QB type to (StandardAccountType, StandardAccountCategory)
        """
        return {
            # Assets
            "Bank": (StandardAccountType.CASH, StandardAccountCategory.ASSETS),
            "Other Current Asset": (StandardAccountType.OTHER_CURRENT_ASSETS, StandardAccountCategory.ASSETS),
            "Fixed Asset": (StandardAccountType.FIXED_ASSETS, StandardAccountCategory.ASSETS),
            "Other Asset": (StandardAccountType.OTHER_ASSETS, StandardAccountCategory.ASSETS),
            "Accounts Receivable": (StandardAccountType.ACCOUNTS_RECEIVABLE, StandardAccountCategory.ASSETS),

            # Liabilities
            "Accounts Payable": (StandardAccountType.ACCOUNTS_PAYABLE, StandardAccountCategory.LIABILITIES),
            "Credit Card": (StandardAccountType.CREDIT_CARDS, StandardAccountCategory.LIABILITIES),
            "Other Current Liability": (StandardAccountType.OTHER_CURRENT_LIABILITIES, StandardAccountCategory.LIABILITIES),
            "Long Term Liability": (StandardAccountType.LONG_TERM_DEBT, StandardAccountCategory.LIABILITIES),

            # Equity
            "Equity": (StandardAccountType.OWNERS_EQUITY, StandardAccountCategory.EQUITY),

            # Revenue
            "Income": (StandardAccountType.OPERATING_REVENUE, StandardAccountCategory.REVENUE),
            "Other Income": (StandardAccountType.OTHER_REVENUE, StandardAccountCategory.REVENUE),

            # Expenses
            "Cost of Goods Sold": (StandardAccountType.COST_OF_GOODS_SOLD, StandardAccountCategory.EXPENSES),
            "Expense": (StandardAccountType.OTHER_EXPENSES, StandardAccountCategory.EXPENSES),
            "Other Expense": (StandardAccountType.OTHER_EXPENSES, StandardAccountCategory.EXPENSES),
        }

    def _build_xero_rules(self) -> Dict[str, tuple]:
        """Build Xero account type mapping rules"""
        return {
            # Assets
            "BANK": (StandardAccountType.CASH, StandardAccountCategory.ASSETS),
            "CURRENT": (StandardAccountType.OTHER_CURRENT_ASSETS, StandardAccountCategory.ASSETS),
            "FIXED": (StandardAccountType.FIXED_ASSETS, StandardAccountCategory.ASSETS),
            "CURRLIAB": (StandardAccountType.OTHER_CURRENT_LIABILITIES, StandardAccountCategory.LIABILITIES),
            "LIABILITY": (StandardAccountType.OTHER_LIABILITIES, StandardAccountCategory.LIABILITIES),
            "EQUITY": (StandardAccountType.OWNERS_EQUITY, StandardAccountCategory.EQUITY),
            "REVENUE": (StandardAccountType.OPERATING_REVENUE, StandardAccountCategory.REVENUE),
            "EXPENSE": (StandardAccountType.OTHER_EXPENSES, StandardAccountCategory.EXPENSES),
            "DIRECTCOSTS": (StandardAccountType.COST_OF_GOODS_SOLD, StandardAccountCategory.EXPENSES),
        }

    def auto_map_account(
        self,
        tenant_id: UUID,
        connection_id: UUID,
        provider_type: str,
        provider_account_id: str,
        provider_account_name: str,
        provider_account_type: str,
        provider_account_number: Optional[str] = None
    ) -> AccountMapping:
        """
        Automatically map provider account to standard type

        Args:
            tenant_id: Tenant ID
            connection_id: Integration connection ID
            provider_type: Provider (quickbooks_online, xero, etc.)
            provider_account_id: Provider's account ID
            provider_account_name: Account name
            provider_account_type: Provider's account type
            provider_account_number: Account number

        Returns:
            Account mapping
        """
        # Get mapping rules for provider
        if provider_type == "quickbooks_online":
            rules = self._quickbooks_rules
        elif provider_type == "xero":
            rules = self._xero_rules
        else:
            # Default to best guess
            rules = self._quickbooks_rules

        # Try to map using provider type
        if provider_account_type in rules:
            standard_type, standard_category = rules[provider_account_type]
            confidence = 0.9
        else:
            # Fall back to name-based mapping
            standard_type, standard_category = self._map_by_name(provider_account_name)
            confidence = 0.6

        # Create mapping
        mapping = AccountMapping(
            tenant_id=tenant_id,
            connection_id=connection_id,
            provider_account_id=provider_account_id,
            provider_account_name=provider_account_name,
            provider_account_type=provider_account_type,
            provider_account_number=provider_account_number,
            standard_account_type=standard_type,
            standard_account_category=standard_category,
            confidence_score=confidence,
            is_manual_override=False
        )

        self._mappings[mapping.id] = mapping

        logger.info(
            f"Auto-mapped account '{provider_account_name}' -> "
            f"{standard_type.value} (confidence: {confidence})"
        )

        return mapping

    def _map_by_name(self, account_name: str) -> tuple:
        """
        Map account by name analysis (fallback)

        Args:
            account_name: Account name

        Returns:
            (StandardAccountType, StandardAccountCategory)
        """
        name_lower = account_name.lower()

        # Cash
        if any(x in name_lower for x in ["cash", "checking", "savings", "bank"]):
            return (StandardAccountType.CASH, StandardAccountCategory.ASSETS)

        # Accounts Receivable
        if any(x in name_lower for x in ["receivable", "a/r", "ar"]):
            return (StandardAccountType.ACCOUNTS_RECEIVABLE, StandardAccountCategory.ASSETS)

        # Accounts Payable
        if any(x in name_lower for x in ["payable", "a/p", "ap"]):
            return (StandardAccountType.ACCOUNTS_PAYABLE, StandardAccountCategory.LIABILITIES)

        # Revenue
        if any(x in name_lower for x in ["revenue", "sales", "income"]):
            return (StandardAccountType.OPERATING_REVENUE, StandardAccountCategory.REVENUE)

        # Expenses
        if any(x in name_lower for x in ["expense", "cost", "salaries", "rent", "utilities"]):
            return (StandardAccountType.OTHER_EXPENSES, StandardAccountCategory.EXPENSES)

        # Default to other assets
        return (StandardAccountType.OTHER_ASSETS, StandardAccountCategory.ASSETS)

    def manual_override_mapping(
        self,
        mapping_id: UUID,
        standard_account_type: StandardAccountType,
        standard_account_category: StandardAccountCategory
    ) -> AccountMapping:
        """
        Manually override automatic mapping

        Args:
            mapping_id: Mapping ID
            standard_account_type: New standard type
            standard_account_category: New standard category

        Returns:
            Updated mapping
        """
        mapping = self._mappings.get(mapping_id)
        if not mapping:
            raise ValueError(f"Mapping {mapping_id} not found")

        mapping.standard_account_type = standard_account_type
        mapping.standard_account_category = standard_account_category
        mapping.confidence_score = 1.0
        mapping.is_manual_override = True
        mapping.updated_at = datetime.utcnow()

        logger.info(
            f"Manual override: '{mapping.provider_account_name}' -> "
            f"{standard_account_type.value}"
        )

        return mapping

    def get_mapping_by_provider_account(
        self,
        connection_id: UUID,
        provider_account_id: str
    ) -> Optional[AccountMapping]:
        """Get mapping for a provider account"""
        for mapping in self._mappings.values():
            if (mapping.connection_id == connection_id and
                mapping.provider_account_id == provider_account_id):
                return mapping
        return None

    def get_mappings_by_connection(self, connection_id: UUID) -> List[AccountMapping]:
        """Get all mappings for a connection"""
        return [
            m for m in self._mappings.values()
            if m.connection_id == connection_id
        ]

    def get_low_confidence_mappings(
        self,
        connection_id: UUID,
        threshold: float = 0.7
    ) -> List[AccountMapping]:
        """Get mappings below confidence threshold for review"""
        return [
            m for m in self._mappings.values()
            if m.connection_id == connection_id and m.confidence_score < threshold
        ]


class IntegrationManagerService:
    """
    Unified integration management service

    Coordinates multiple provider integrations, manages sync scheduling,
    and provides normalized financial data access.
    """

    def __init__(
        self,
        quickbooks_service: Optional[Any] = None,
        xero_service: Optional[Any] = None,
        mapping_service: Optional[AccountMappingService] = None
    ):
        self.quickbooks_service = quickbooks_service
        self.xero_service = xero_service
        self.mapping_service = mapping_service or AccountMappingService()

        # Sync scheduler
        self._sync_schedule: Dict[UUID, Dict] = {}  # connection_id -> schedule
        self._sync_tasks: Dict[UUID, asyncio.Task] = {}

    # ==================== Unified API ====================

    async def connect_provider(
        self,
        provider: str,
        tenant_id: UUID,
        authorization_code: str,
        realm_id: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Connect to accounting software provider

        Args:
            provider: Provider name (quickbooks_online, xero, etc.)
            tenant_id: Tenant ID
            authorization_code: OAuth authorization code
            realm_id: QuickBooks realm ID (if QuickBooks)
            **kwargs: Additional provider-specific parameters

        Returns:
            Integration connection
        """
        if provider == "quickbooks_online":
            if not self.quickbooks_service:
                raise ValueError("QuickBooks service not configured")

            connection = await self.quickbooks_service.exchange_authorization_code(
                authorization_code=authorization_code,
                realm_id=realm_id,
                tenant_id=tenant_id
            )

            # Schedule automatic sync
            await self.schedule_sync(connection.id)

            return connection

        elif provider == "xero":
            if not self.xero_service:
                raise ValueError("Xero service not configured")

            # Xero implementation would go here
            raise NotImplementedError("Xero integration coming soon")

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def sync_data(
        self,
        connection_id: UUID,
        data_types: Optional[List[str]] = None
    ) -> List[Any]:
        """
        Sync data from accounting software

        Args:
            connection_id: Integration connection ID
            data_types: Specific data types to sync (None = all configured)

        Returns:
            List of sync jobs
        """
        # Get connection to determine provider
        connection = None
        if self.quickbooks_service:
            connection = self.quickbooks_service.get_connection(connection_id)

        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        # Sync based on provider
        if connection.provider.value == "quickbooks_online":
            jobs = await self.quickbooks_service.sync_all_data(connection_id)

            # Auto-map chart of accounts
            for job in jobs:
                if job.data_type.value == "chart_of_accounts" and job.status.value == "completed":
                    await self._auto_map_chart_of_accounts(connection)

            return jobs

        else:
            raise ValueError(f"Unsupported provider: {connection.provider}")

    async def _auto_map_chart_of_accounts(self, connection: Any):
        """Automatically map chart of accounts after sync"""
        # Get synced accounts (this would come from database in production)
        # For now, we'll just log
        logger.info(
            f"Auto-mapping chart of accounts for connection {connection.id}"
        )

        # In production, you would:
        # 1. Fetch synced accounts from database
        # 2. For each account, call mapping_service.auto_map_account()
        # 3. Store mappings in database
        # 4. Identify low-confidence mappings for manual review

    async def get_normalized_chart_of_accounts(
        self,
        connection_id: UUID
    ) -> List[NormalizedAccount]:
        """
        Get normalized chart of accounts

        Args:
            connection_id: Integration connection ID

        Returns:
            List of normalized accounts
        """
        # Get provider accounts (would come from database)
        # Get mappings
        mappings = self.mapping_service.get_mappings_by_connection(connection_id)

        # Map to normalized format
        normalized_accounts = []
        for mapping in mappings:
            # In production, join with actual account data from database
            normalized = NormalizedAccount(
                id=mapping.provider_account_id,
                name=mapping.provider_account_name,
                account_number=mapping.provider_account_number,
                standard_type=mapping.standard_account_type,
                standard_category=mapping.standard_account_category,
                current_balance=0.0,  # Would come from synced data
                provider_type="quickbooks_online",  # Would come from connection
                provider_account_id=mapping.provider_account_id,
                synced_at=datetime.utcnow()
            )
            normalized_accounts.append(normalized)

        return normalized_accounts

    async def get_normalized_balance_sheet(
        self,
        connection_id: UUID,
        date: Optional[datetime] = None
    ) -> NormalizedFinancialStatement:
        """
        Get normalized balance sheet

        Args:
            connection_id: Integration connection ID
            date: Balance sheet date (default: today)

        Returns:
            Normalized balance sheet
        """
        # Get connection
        connection = self.quickbooks_service.get_connection(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        # Sync balance sheet
        date_str = date.strftime("%Y-%m-%d") if date else None
        job = await self.quickbooks_service.sync_balance_sheet(connection_id, date_str)

        if job.status.value != "completed":
            raise Exception(f"Balance sheet sync failed: {job.error_message}")

        # Get mappings
        mappings = self.mapping_service.get_mappings_by_connection(connection_id)

        # Normalize balance sheet (would process actual data in production)
        normalized = NormalizedFinancialStatement(
            tenant_id=connection.tenant_id,
            connection_id=connection_id,
            statement_type="balance_sheet",
            period_start=date or datetime.utcnow(),
            period_end=date or datetime.utcnow(),
            line_items=[],  # Would populate from actual data
            provider_type=connection.provider.value
        )

        return normalized

    # ==================== Sync Scheduling ====================

    async def schedule_sync(
        self,
        connection_id: UUID,
        frequency_hours: int = 24
    ):
        """
        Schedule automatic data synchronization

        Args:
            connection_id: Integration connection ID
            frequency_hours: Sync frequency in hours
        """
        self._sync_schedule[connection_id] = {
            "frequency_hours": frequency_hours,
            "next_sync": datetime.utcnow() + timedelta(hours=frequency_hours),
            "enabled": True
        }

        # Start background sync task
        if connection_id not in self._sync_tasks:
            task = asyncio.create_task(
                self._sync_loop(connection_id)
            )
            self._sync_tasks[connection_id] = task

        logger.info(
            f"Scheduled sync for connection {connection_id} "
            f"every {frequency_hours} hours"
        )

    async def _sync_loop(self, connection_id: UUID):
        """Background sync loop"""
        while True:
            try:
                schedule = self._sync_schedule.get(connection_id)
                if not schedule or not schedule["enabled"]:
                    break

                # Wait until next sync time
                now = datetime.utcnow()
                next_sync = schedule["next_sync"]

                if now < next_sync:
                    wait_seconds = (next_sync - now).total_seconds()
                    await asyncio.sleep(wait_seconds)

                # Perform sync
                logger.info(f"Starting scheduled sync for connection {connection_id}")
                await self.sync_data(connection_id)

                # Schedule next sync
                schedule["next_sync"] = datetime.utcnow() + timedelta(
                    hours=schedule["frequency_hours"]
                )

            except Exception as e:
                logger.error(f"Sync loop error for {connection_id}: {str(e)}")
                # Wait 1 hour before retry
                await asyncio.sleep(3600)

    def cancel_sync_schedule(self, connection_id: UUID):
        """Cancel scheduled sync"""
        if connection_id in self._sync_schedule:
            self._sync_schedule[connection_id]["enabled"] = False

        if connection_id in self._sync_tasks:
            self._sync_tasks[connection_id].cancel()
            del self._sync_tasks[connection_id]

        logger.info(f"Cancelled sync schedule for connection {connection_id}")

    # ==================== Health & Status ====================

    def get_integration_status(self, connection_id: UUID) -> Dict:
        """Get integration health status"""
        connection = None
        if self.quickbooks_service:
            connection = self.quickbooks_service.get_connection(connection_id)

        if not connection:
            return {"status": "not_found"}

        # Get recent sync jobs
        recent_jobs = []
        if self.quickbooks_service:
            all_jobs = self.quickbooks_service.get_sync_jobs_by_connection(connection_id)
            recent_jobs = sorted(all_jobs, key=lambda j: j.started_at, reverse=True)[:5]

        # Get sync schedule
        schedule = self._sync_schedule.get(connection_id)

        return {
            "connection_id": str(connection_id),
            "provider": connection.provider.value,
            "status": connection.status.value,
            "company_name": connection.company_name,
            "last_sync": connection.last_sync_at.isoformat() if connection.last_sync_at else None,
            "last_error": connection.last_error,
            "recent_jobs": [
                {
                    "data_type": job.data_type.value,
                    "status": job.status.value,
                    "records_synced": job.records_synced,
                    "started_at": job.started_at.isoformat()
                }
                for job in recent_jobs
            ],
            "sync_schedule": {
                "enabled": schedule["enabled"] if schedule else False,
                "frequency_hours": schedule["frequency_hours"] if schedule else None,
                "next_sync": schedule["next_sync"].isoformat() if schedule and schedule.get("next_sync") else None
            } if schedule else None
        }
