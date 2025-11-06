"""
QuickBooks Online Integration Service

Provides OAuth 2.0 authentication and data synchronization with QuickBooks Online.
Supports pulling financial data, chart of accounts, transactions, and real-time webhooks.

Features:
- OAuth 2.0 authentication flow
- Automatic token refresh
- Data sync for financial statements, transactions, accounts
- Real-time webhook support
- Error handling and retry logic
- Multi-tenant support
"""

import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

import aiohttp
from pydantic import BaseModel, Field


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationProvider(str, Enum):
    """Supported accounting software providers"""
    QUICKBOOKS_ONLINE = "quickbooks_online"
    XERO = "xero"
    SAGE = "sage"
    FRESHBOOKS = "freshbooks"


class IntegrationStatus(str, Enum):
    """Integration connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RECONNECT_REQUIRED = "reconnect_required"
    TOKEN_EXPIRED = "token_expired"


class SyncStatus(str, Enum):
    """Data synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class DataType(str, Enum):
    """Types of data to sync"""
    CHART_OF_ACCOUNTS = "chart_of_accounts"
    GENERAL_LEDGER = "general_ledger"
    TRIAL_BALANCE = "trial_balance"
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    JOURNAL_ENTRIES = "journal_entries"
    INVOICES = "invoices"
    BILLS = "bills"
    PAYMENTS = "payments"
    CUSTOMERS = "customers"
    VENDORS = "vendors"


class QuickBooksConfig(BaseModel):
    """QuickBooks API configuration"""
    client_id: str
    client_secret: str
    redirect_uri: str
    environment: str = "production"  # or "sandbox"

    # API endpoints
    auth_url: str = "https://appcenter.intuit.com/connect/oauth2"
    token_url: str = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    api_base_url: str = "https://quickbooks.api.intuit.com/v3"
    sandbox_api_base_url: str = "https://sandbox-quickbooks.api.intuit.com/v3"

    # Scopes
    scopes: List[str] = [
        "com.intuit.quickbooks.accounting",
        "com.intuit.quickbooks.payment"
    ]

    @property
    def base_url(self) -> str:
        """Get base URL based on environment"""
        if self.environment == "sandbox":
            return self.sandbox_api_base_url
        return self.api_base_url


class OAuthToken(BaseModel):
    """OAuth token storage"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_at: datetime
    realm_id: str  # QuickBooks company ID

    def is_expired(self) -> bool:
        """Check if token is expired"""
        # Refresh 5 minutes before actual expiry
        return datetime.utcnow() >= (self.expires_at - timedelta(minutes=5))


class IntegrationConnection(BaseModel):
    """Integration connection record"""
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    provider: IntegrationProvider
    status: IntegrationStatus

    # OAuth tokens
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    realm_id: Optional[str] = None  # QuickBooks company ID

    # Connection metadata
    company_name: Optional[str] = None
    company_email: Optional[str] = None
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync_at: Optional[datetime] = None
    last_error: Optional[str] = None

    # Sync settings
    auto_sync_enabled: bool = True
    sync_frequency_hours: int = 24
    data_types_to_sync: List[DataType] = Field(default_factory=lambda: [
        DataType.CHART_OF_ACCOUNTS,
        DataType.TRIAL_BALANCE,
        DataType.BALANCE_SHEET,
        DataType.INCOME_STATEMENT
    ])


class SyncJob(BaseModel):
    """Data synchronization job"""
    id: UUID = Field(default_factory=uuid4)
    connection_id: UUID
    tenant_id: UUID

    data_type: DataType
    status: SyncStatus

    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    records_synced: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None

    # Sync metadata
    last_sync_cursor: Optional[str] = None  # For incremental sync
    full_sync: bool = True


class QuickBooksIntegrationService:
    """
    QuickBooks Online integration service

    Handles OAuth authentication, token management, and data synchronization
    with QuickBooks Online API.
    """

    def __init__(
        self,
        config: QuickBooksConfig,
        encryption_service: Optional[Any] = None,
        audit_log_service: Optional[Any] = None
    ):
        self.config = config
        self.encryption_service = encryption_service
        self.audit_log_service = audit_log_service

        # In-memory storage (replace with database in production)
        self._connections: Dict[UUID, IntegrationConnection] = {}
        self._sync_jobs: Dict[UUID, SyncJob] = {}

        # HTTP session
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()

    # ==================== OAuth 2.0 Authentication ====================

    def generate_authorization_url(self, state: str) -> str:
        """
        Generate OAuth authorization URL for user to connect QuickBooks

        Args:
            state: Random state parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        scope = " ".join(self.config.scopes)

        auth_url = (
            f"{self.config.auth_url}?"
            f"client_id={self.config.client_id}&"
            f"redirect_uri={self.config.redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"state={state}"
        )

        logger.info(f"Generated authorization URL with state={state}")
        return auth_url

    async def exchange_authorization_code(
        self,
        authorization_code: str,
        realm_id: str,
        tenant_id: UUID
    ) -> IntegrationConnection:
        """
        Exchange authorization code for access token

        Args:
            authorization_code: Authorization code from OAuth callback
            realm_id: QuickBooks company ID
            tenant_id: Tenant ID

        Returns:
            Integration connection with tokens
        """
        session = await self._get_session()

        # Exchange code for tokens
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.config.redirect_uri
        }

        auth = aiohttp.BasicAuth(
            login=self.config.client_id,
            password=self.config.client_secret
        )

        async with session.post(
            self.config.token_url,
            data=data,
            auth=auth
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Token exchange failed: {error_text}")
                raise Exception(f"Failed to exchange authorization code: {error_text}")

            token_data = await response.json()

        # Calculate token expiry
        expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Get company info
        company_info = await self._get_company_info(
            token_data["access_token"],
            realm_id
        )

        # Create connection
        connection = IntegrationConnection(
            tenant_id=tenant_id,
            provider=IntegrationProvider.QUICKBOOKS_ONLINE,
            status=IntegrationStatus.CONNECTED,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_expires_at=expires_at,
            realm_id=realm_id,
            company_name=company_info.get("CompanyName"),
            company_email=company_info.get("Email", {}).get("Address")
        )

        # Encrypt tokens if encryption service available
        if self.encryption_service:
            connection.access_token = self.encryption_service.encrypt_field(
                connection.access_token,
                key_purpose="integration_token"
            )
            connection.refresh_token = self.encryption_service.encrypt_field(
                connection.refresh_token,
                key_purpose="integration_token"
            )

        # Store connection
        self._connections[connection.id] = connection

        # Audit log
        if self.audit_log_service:
            await self.audit_log_service.log_event(
                event_type="integration_connected",
                user_id=tenant_id,  # Use tenant as user for now
                resource_type="integration",
                resource_id=str(connection.id),
                action="connect",
                changes={
                    "provider": "quickbooks_online",
                    "company_name": connection.company_name
                }
            )

        logger.info(
            f"QuickBooks connected for tenant {tenant_id}, "
            f"company: {connection.company_name}"
        )

        return connection

    async def refresh_access_token(self, connection_id: UUID) -> IntegrationConnection:
        """
        Refresh access token using refresh token

        Args:
            connection_id: Integration connection ID

        Returns:
            Updated connection with new tokens
        """
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        # Decrypt refresh token
        refresh_token = connection.refresh_token
        if self.encryption_service and refresh_token:
            refresh_token = self.encryption_service.decrypt_field(refresh_token)

        session = await self._get_session()

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        auth = aiohttp.BasicAuth(
            login=self.config.client_id,
            password=self.config.client_secret
        )

        async with session.post(
            self.config.token_url,
            data=data,
            auth=auth
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Token refresh failed: {error_text}")
                connection.status = IntegrationStatus.RECONNECT_REQUIRED
                connection.last_error = f"Token refresh failed: {error_text}"
                raise Exception(f"Failed to refresh token: {error_text}")

            token_data = await response.json()

        # Update tokens
        expires_in = token_data.get("expires_in", 3600)
        connection.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        connection.access_token = token_data["access_token"]
        connection.refresh_token = token_data.get("refresh_token", refresh_token)

        # Encrypt tokens
        if self.encryption_service:
            connection.access_token = self.encryption_service.encrypt_field(
                connection.access_token,
                key_purpose="integration_token"
            )
            connection.refresh_token = self.encryption_service.encrypt_field(
                connection.refresh_token,
                key_purpose="integration_token"
            )

        connection.status = IntegrationStatus.CONNECTED
        connection.last_error = None

        logger.info(f"Refreshed access token for connection {connection_id}")

        return connection

    async def _get_access_token(self, connection: IntegrationConnection) -> str:
        """Get valid access token, refreshing if necessary"""
        # Check if token is expired
        if connection.token_expires_at and datetime.utcnow() >= connection.token_expires_at:
            logger.info(f"Token expired, refreshing for connection {connection.id}")
            connection = await self.refresh_access_token(connection.id)

        # Decrypt token
        access_token = connection.access_token
        if self.encryption_service and access_token:
            access_token = self.encryption_service.decrypt_field(access_token)

        return access_token

    # ==================== QuickBooks API Calls ====================

    async def _make_api_call(
        self,
        connection: IntegrationConnection,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict:
        """
        Make API call to QuickBooks

        Args:
            connection: Integration connection
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/company/123/account")
            params: Query parameters
            json_data: JSON body data

        Returns:
            API response data
        """
        access_token = await self._get_access_token(connection)

        url = f"{self.config.base_url}{endpoint}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        session = await self._get_session()

        async with session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data
        ) as response:
            if response.status == 401:
                # Token expired, try refreshing
                logger.warning("Received 401, attempting token refresh")
                await self.refresh_access_token(connection.id)

                # Retry with new token
                access_token = await self._get_access_token(connection)
                headers["Authorization"] = f"Bearer {access_token}"

                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data
                ) as retry_response:
                    if retry_response.status != 200:
                        error_text = await retry_response.text()
                        raise Exception(f"API call failed: {error_text}")
                    return await retry_response.json()

            elif response.status != 200:
                error_text = await response.text()
                raise Exception(f"API call failed: {error_text}")

            return await response.json()

    async def _get_company_info(self, access_token: str, realm_id: str) -> Dict:
        """Get company information"""
        url = f"{self.config.base_url}/company/{realm_id}/companyinfo/{realm_id}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        session = await self._get_session()

        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Failed to get company info: {error_text}")
                return {}

            data = await response.json()
            return data.get("CompanyInfo", {})

    # ==================== Data Synchronization ====================

    async def sync_chart_of_accounts(
        self,
        connection_id: UUID
    ) -> SyncJob:
        """
        Sync chart of accounts from QuickBooks

        Args:
            connection_id: Integration connection ID

        Returns:
            Sync job with results
        """
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        # Create sync job
        job = SyncJob(
            connection_id=connection_id,
            tenant_id=connection.tenant_id,
            data_type=DataType.CHART_OF_ACCOUNTS,
            status=SyncStatus.IN_PROGRESS
        )
        self._sync_jobs[job.id] = job

        try:
            # Query accounts
            response = await self._make_api_call(
                connection=connection,
                method="GET",
                endpoint=f"/company/{connection.realm_id}/query",
                params={"query": "SELECT * FROM Account"}
            )

            accounts = response.get("QueryResponse", {}).get("Account", [])

            # Process accounts
            processed_accounts = []
            for account in accounts:
                processed_account = {
                    "id": account.get("Id"),
                    "name": account.get("Name"),
                    "account_type": account.get("AccountType"),
                    "account_sub_type": account.get("AccountSubType"),
                    "account_number": account.get("AcctNum"),
                    "description": account.get("Description"),
                    "active": account.get("Active", True),
                    "current_balance": float(account.get("CurrentBalance", 0)),
                    "classification": account.get("Classification"),
                    "parent_ref": account.get("ParentRef", {}).get("value"),
                    "fully_qualified_name": account.get("FullyQualifiedName"),
                    "synced_at": datetime.utcnow().isoformat()
                }
                processed_accounts.append(processed_account)

            job.status = SyncStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.records_synced = len(processed_accounts)

            connection.last_sync_at = datetime.utcnow()

            logger.info(
                f"Synced {len(processed_accounts)} accounts for "
                f"connection {connection_id}"
            )

            # Audit log
            if self.audit_log_service:
                await self.audit_log_service.log_event(
                    event_type="integration_sync",
                    user_id=connection.tenant_id,
                    resource_type="chart_of_accounts",
                    resource_id=str(connection_id),
                    action="sync",
                    changes={
                        "data_type": "chart_of_accounts",
                        "records_synced": len(processed_accounts)
                    }
                )

            return job

        except Exception as e:
            logger.error(f"Chart of accounts sync failed: {str(e)}")
            job.status = SyncStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()

            connection.last_error = str(e)

            raise

    async def sync_trial_balance(
        self,
        connection_id: UUID,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> SyncJob:
        """
        Sync trial balance from QuickBooks

        Args:
            connection_id: Integration connection ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Sync job with results
        """
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        job = SyncJob(
            connection_id=connection_id,
            tenant_id=connection.tenant_id,
            data_type=DataType.TRIAL_BALANCE,
            status=SyncStatus.IN_PROGRESS
        )
        self._sync_jobs[job.id] = job

        try:
            # Build report parameters
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            # Request trial balance report
            response = await self._make_api_call(
                connection=connection,
                method="GET",
                endpoint=f"/company/{connection.realm_id}/reports/TrialBalance",
                params=params
            )

            # Process report data
            report_data = {
                "report_name": response.get("Header", {}).get("ReportName"),
                "start_period": response.get("Header", {}).get("StartPeriod"),
                "end_period": response.get("Header", {}).get("EndPeriod"),
                "currency": response.get("Header", {}).get("Currency"),
                "rows": response.get("Rows", {}).get("Row", []),
                "synced_at": datetime.utcnow().isoformat()
            }

            job.status = SyncStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.records_synced = len(report_data["rows"])

            connection.last_sync_at = datetime.utcnow()

            logger.info(
                f"Synced trial balance for connection {connection_id}"
            )

            return job

        except Exception as e:
            logger.error(f"Trial balance sync failed: {str(e)}")
            job.status = SyncStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()

            raise

    async def sync_balance_sheet(
        self,
        connection_id: UUID,
        date: Optional[str] = None
    ) -> SyncJob:
        """
        Sync balance sheet from QuickBooks

        Args:
            connection_id: Integration connection ID
            date: Report date (YYYY-MM-DD)

        Returns:
            Sync job with results
        """
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        job = SyncJob(
            connection_id=connection_id,
            tenant_id=connection.tenant_id,
            data_type=DataType.BALANCE_SHEET,
            status=SyncStatus.IN_PROGRESS
        )
        self._sync_jobs[job.id] = job

        try:
            params = {}
            if date:
                params["date"] = date

            response = await self._make_api_call(
                connection=connection,
                method="GET",
                endpoint=f"/company/{connection.realm_id}/reports/BalanceSheet",
                params=params
            )

            job.status = SyncStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.records_synced = 1  # One balance sheet

            connection.last_sync_at = datetime.utcnow()

            logger.info(f"Synced balance sheet for connection {connection_id}")

            return job

        except Exception as e:
            logger.error(f"Balance sheet sync failed: {str(e)}")
            job.status = SyncStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()

            raise

    async def sync_income_statement(
        self,
        connection_id: UUID,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> SyncJob:
        """
        Sync income statement (profit & loss) from QuickBooks

        Args:
            connection_id: Integration connection ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Sync job with results
        """
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        job = SyncJob(
            connection_id=connection_id,
            tenant_id=connection.tenant_id,
            data_type=DataType.INCOME_STATEMENT,
            status=SyncStatus.IN_PROGRESS
        )
        self._sync_jobs[job.id] = job

        try:
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            response = await self._make_api_call(
                connection=connection,
                method="GET",
                endpoint=f"/company/{connection.realm_id}/reports/ProfitAndLoss",
                params=params
            )

            job.status = SyncStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.records_synced = 1  # One income statement

            connection.last_sync_at = datetime.utcnow()

            logger.info(f"Synced income statement for connection {connection_id}")

            return job

        except Exception as e:
            logger.error(f"Income statement sync failed: {str(e)}")
            job.status = SyncStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()

            raise

    async def sync_all_data(self, connection_id: UUID) -> List[SyncJob]:
        """
        Sync all configured data types for a connection

        Args:
            connection_id: Integration connection ID

        Returns:
            List of sync jobs
        """
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        jobs = []

        for data_type in connection.data_types_to_sync:
            try:
                if data_type == DataType.CHART_OF_ACCOUNTS:
                    job = await self.sync_chart_of_accounts(connection_id)
                elif data_type == DataType.TRIAL_BALANCE:
                    job = await self.sync_trial_balance(connection_id)
                elif data_type == DataType.BALANCE_SHEET:
                    job = await self.sync_balance_sheet(connection_id)
                elif data_type == DataType.INCOME_STATEMENT:
                    job = await self.sync_income_statement(connection_id)
                else:
                    logger.warning(f"Data type {data_type} not yet implemented")
                    continue

                jobs.append(job)

            except Exception as e:
                logger.error(f"Failed to sync {data_type}: {str(e)}")
                continue

        logger.info(
            f"Completed sync for connection {connection_id}: "
            f"{len([j for j in jobs if j.status == SyncStatus.COMPLETED])} "
            f"succeeded, {len([j for j in jobs if j.status == SyncStatus.FAILED])} failed"
        )

        return jobs

    # ==================== Webhook Handling ====================

    def verify_webhook_signature(
        self,
        payload: str,
        signature: str,
        webhook_token: str
    ) -> bool:
        """
        Verify QuickBooks webhook signature

        Args:
            payload: Raw webhook payload
            signature: Signature from header
            webhook_token: Webhook verification token

        Returns:
            True if signature is valid
        """
        expected_signature = hmac.new(
            key=webhook_token.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def handle_webhook(
        self,
        payload: Dict,
        signature: str,
        webhook_token: str
    ) -> Dict:
        """
        Handle incoming webhook from QuickBooks

        Args:
            payload: Webhook payload
            signature: Signature from header
            webhook_token: Webhook verification token

        Returns:
            Processing result
        """
        # Verify signature
        payload_str = json.dumps(payload)
        if not self.verify_webhook_signature(payload_str, signature, webhook_token):
            logger.error("Invalid webhook signature")
            raise ValueError("Invalid webhook signature")

        # Process webhook events
        event_notifications = payload.get("eventNotifications", [])

        processed_events = []
        for event in event_notifications:
            realm_id = event.get("realmId")
            data_change_event = event.get("dataChangeEvent", {})
            entities = data_change_event.get("entities", [])

            for entity in entities:
                entity_name = entity.get("name")
                entity_id = entity.get("id")
                operation = entity.get("operation")

                logger.info(
                    f"Webhook: {operation} on {entity_name} "
                    f"(ID: {entity_id}) for realm {realm_id}"
                )

                # Find connection by realm_id
                connection = None
                for conn in self._connections.values():
                    if conn.realm_id == realm_id:
                        connection = conn
                        break

                if not connection:
                    logger.warning(f"No connection found for realm {realm_id}")
                    continue

                # Trigger sync based on entity type
                if entity_name == "Account":
                    await self.sync_chart_of_accounts(connection.id)
                # Add more entity types as needed

                processed_events.append({
                    "entity": entity_name,
                    "operation": operation,
                    "id": entity_id
                })

        return {
            "processed_events": len(processed_events),
            "events": processed_events
        }

    # ==================== Connection Management ====================

    def get_connection(self, connection_id: UUID) -> Optional[IntegrationConnection]:
        """Get integration connection by ID"""
        return self._connections.get(connection_id)

    def get_connections_by_tenant(self, tenant_id: UUID) -> List[IntegrationConnection]:
        """Get all connections for a tenant"""
        return [
            conn for conn in self._connections.values()
            if conn.tenant_id == tenant_id
        ]

    async def disconnect(self, connection_id: UUID):
        """Disconnect integration"""
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        connection.status = IntegrationStatus.DISCONNECTED
        connection.access_token = None
        connection.refresh_token = None

        # Audit log
        if self.audit_log_service:
            await self.audit_log_service.log_event(
                event_type="integration_disconnected",
                user_id=connection.tenant_id,
                resource_type="integration",
                resource_id=str(connection_id),
                action="disconnect",
                changes={"provider": "quickbooks_online"}
            )

        logger.info(f"Disconnected connection {connection_id}")

    def get_sync_job(self, job_id: UUID) -> Optional[SyncJob]:
        """Get sync job by ID"""
        return self._sync_jobs.get(job_id)

    def get_sync_jobs_by_connection(self, connection_id: UUID) -> List[SyncJob]:
        """Get all sync jobs for a connection"""
        return [
            job for job in self._sync_jobs.values()
            if job.connection_id == connection_id
        ]
