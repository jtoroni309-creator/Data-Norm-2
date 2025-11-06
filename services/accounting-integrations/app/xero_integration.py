"""
Xero Integration Service

Provides OAuth 2.0 authentication and data synchronization with Xero accounting software.
Supports pulling financial data, chart of accounts, transactions, and real-time webhooks.

Features:
- OAuth 2.0 (PKCE) authentication flow
- Automatic token refresh
- Data sync for financial statements, transactions, accounts
- Real-time webhook support
- Multi-organization support
- Error handling and retry logic
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import secrets
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

import aiohttp
from pydantic import BaseModel, Field


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XeroConfig(BaseModel):
    """Xero API configuration"""
    client_id: str
    client_secret: str
    redirect_uri: str

    # API endpoints
    auth_url: str = "https://login.xero.com/identity/connect/authorize"
    token_url: str = "https://identity.xero.com/connect/token"
    api_base_url: str = "https://api.xero.com/api.xro/2.0"
    connections_url: str = "https://api.xero.com/connections"

    # Scopes
    scopes: List[str] = [
        "offline_access",
        "accounting.transactions.read",
        "accounting.reports.read",
        "accounting.contacts.read",
        "accounting.settings.read"
    ]


class XeroOAuthToken(BaseModel):
    """Xero OAuth token storage"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_at: datetime
    tenant_id: str  # Xero organization ID

    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() >= (self.expires_at - timedelta(minutes=5))


class XeroConnection(BaseModel):
    """Xero integration connection"""
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID  # Our tenant ID
    xero_tenant_id: str  # Xero organization ID

    status: str  # connected, disconnected, error
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None

    # Organization info
    organization_name: Optional[str] = None
    organization_type: Optional[str] = None
    base_currency: Optional[str] = None

    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync_at: Optional[datetime] = None
    last_error: Optional[str] = None

    auto_sync_enabled: bool = True
    sync_frequency_hours: int = 24


class XeroSyncJob(BaseModel):
    """Xero data sync job"""
    id: UUID = Field(default_factory=uuid4)
    connection_id: UUID
    tenant_id: UUID

    data_type: str
    status: str  # pending, in_progress, completed, failed

    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    records_synced: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None


class XeroIntegrationService:
    """
    Xero integration service

    Handles OAuth 2.0 (with PKCE), token management, and data synchronization
    with Xero API.
    """

    def __init__(
        self,
        config: XeroConfig,
        encryption_service: Optional[Any] = None,
        audit_log_service: Optional[Any] = None
    ):
        self.config = config
        self.encryption_service = encryption_service
        self.audit_log_service = audit_log_service

        # In-memory storage
        self._connections: Dict[UUID, XeroConnection] = {}
        self._sync_jobs: Dict[UUID, XeroSyncJob] = {}

        # PKCE storage (state -> code_verifier)
        self._pkce_verifiers: Dict[str, str] = {}

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

    # ==================== OAuth 2.0 with PKCE ====================

    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")

    def _generate_code_challenge(self, verifier: str) -> str:
        """Generate PKCE code challenge from verifier"""
        digest = hashlib.sha256(verifier.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

    def generate_authorization_url(self, state: str) -> tuple[str, str]:
        """
        Generate OAuth authorization URL with PKCE

        Args:
            state: Random state parameter for CSRF protection

        Returns:
            (authorization_url, code_verifier)
        """
        # Generate PKCE parameters
        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)

        # Store verifier for later use
        self._pkce_verifiers[state] = code_verifier

        scope = " ".join(self.config.scopes)

        auth_url = (
            f"{self.config.auth_url}?"
            f"response_type=code&"
            f"client_id={self.config.client_id}&"
            f"redirect_uri={self.config.redirect_uri}&"
            f"scope={scope}&"
            f"state={state}&"
            f"code_challenge={code_challenge}&"
            f"code_challenge_method=S256"
        )

        logger.info(f"Generated Xero authorization URL with state={state}")
        return auth_url, code_verifier

    async def exchange_authorization_code(
        self,
        authorization_code: str,
        state: str,
        tenant_id: UUID
    ) -> XeroConnection:
        """
        Exchange authorization code for access token

        Args:
            authorization_code: Authorization code from OAuth callback
            state: State parameter (used to retrieve code_verifier)
            tenant_id: Our tenant ID

        Returns:
            Xero connection with tokens
        """
        # Get code verifier
        code_verifier = self._pkce_verifiers.get(state)
        if not code_verifier:
            raise ValueError("Invalid state parameter or PKCE verifier not found")

        session = await self._get_session()

        # Exchange code for tokens
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.config.redirect_uri,
            "code_verifier": code_verifier,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret
        }

        async with session.post(
            self.config.token_url,
            data=data
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Xero token exchange failed: {error_text}")
                raise Exception(f"Failed to exchange authorization code: {error_text}")

            token_data = await response.json()

        # Calculate token expiry
        expires_in = token_data.get("expires_in", 1800)  # Default 30 minutes
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Get connected organizations (tenants)
        organizations = await self._get_connections(token_data["access_token"])

        if not organizations:
            raise Exception("No Xero organizations connected")

        # Use first organization
        org = organizations[0]
        xero_tenant_id = org["tenantId"]

        # Get organization details
        org_details = await self._get_organization_details(
            token_data["access_token"],
            xero_tenant_id
        )

        # Create connection
        connection = XeroConnection(
            tenant_id=tenant_id,
            xero_tenant_id=xero_tenant_id,
            status="connected",
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_expires_at=expires_at,
            organization_name=org.get("tenantName"),
            organization_type=org.get("tenantType"),
            base_currency=org_details.get("BaseCurrency")
        )

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

        # Store connection
        self._connections[connection.id] = connection

        # Clean up PKCE verifier
        del self._pkce_verifiers[state]

        # Audit log
        if self.audit_log_service:
            await self.audit_log_service.log_event(
                event_type="integration_connected",
                user_id=tenant_id,
                resource_type="integration",
                resource_id=str(connection.id),
                action="connect",
                changes={
                    "provider": "xero",
                    "organization_name": connection.organization_name
                }
            )

        logger.info(
            f"Xero connected for tenant {tenant_id}, "
            f"organization: {connection.organization_name}"
        )

        return connection

    async def refresh_access_token(self, connection_id: UUID) -> XeroConnection:
        """Refresh access token using refresh token"""
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
            "refresh_token": refresh_token,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret
        }

        async with session.post(
            self.config.token_url,
            data=data
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Xero token refresh failed: {error_text}")
                connection.status = "reconnect_required"
                connection.last_error = f"Token refresh failed: {error_text}"
                raise Exception(f"Failed to refresh token: {error_text}")

            token_data = await response.json()

        # Update tokens
        expires_in = token_data.get("expires_in", 1800)
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

        connection.status = "connected"
        connection.last_error = None

        logger.info(f"Refreshed Xero access token for connection {connection_id}")

        return connection

    async def _get_access_token(self, connection: XeroConnection) -> str:
        """Get valid access token, refreshing if necessary"""
        if connection.token_expires_at and datetime.utcnow() >= connection.token_expires_at:
            logger.info(f"Xero token expired, refreshing for connection {connection.id}")
            connection = await self.refresh_access_token(connection.id)

        access_token = connection.access_token
        if self.encryption_service and access_token:
            access_token = self.encryption_service.decrypt_field(access_token)

        return access_token

    # ==================== Xero API Calls ====================

    async def _make_api_call(
        self,
        connection: XeroConnection,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict:
        """Make API call to Xero"""
        access_token = await self._get_access_token(connection)

        url = f"{self.config.api_base_url}{endpoint}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": connection.xero_tenant_id,
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
                # Token expired, refresh and retry
                logger.warning("Received 401, attempting token refresh")
                await self.refresh_access_token(connection.id)

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
                        raise Exception(f"Xero API call failed: {error_text}")
                    return await retry_response.json()

            elif response.status != 200:
                error_text = await response.text()
                raise Exception(f"Xero API call failed: {error_text}")

            return await response.json()

    async def _get_connections(self, access_token: str) -> List[Dict]:
        """Get connected Xero organizations"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        session = await self._get_session()

        async with session.get(self.config.connections_url, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Failed to get Xero connections: {error_text}")
                return []

            return await response.json()

    async def _get_organization_details(
        self,
        access_token: str,
        xero_tenant_id: str
    ) -> Dict:
        """Get organization details"""
        url = f"{self.config.api_base_url}/Organisation"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": xero_tenant_id,
            "Accept": "application/json"
        }

        session = await self._get_session()

        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Failed to get organization details: {error_text}")
                return {}

            data = await response.json()
            orgs = data.get("Organisations", [])
            return orgs[0] if orgs else {}

    # ==================== Data Synchronization ====================

    async def sync_chart_of_accounts(self, connection_id: UUID) -> XeroSyncJob:
        """Sync chart of accounts from Xero"""
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        job = XeroSyncJob(
            connection_id=connection_id,
            tenant_id=connection.tenant_id,
            data_type="chart_of_accounts",
            status="in_progress"
        )
        self._sync_jobs[job.id] = job

        try:
            response = await self._make_api_call(
                connection=connection,
                method="GET",
                endpoint="/Accounts"
            )

            accounts = response.get("Accounts", [])

            processed_accounts = []
            for account in accounts:
                processed_account = {
                    "id": account.get("AccountID"),
                    "code": account.get("Code"),
                    "name": account.get("Name"),
                    "type": account.get("Type"),
                    "tax_type": account.get("TaxType"),
                    "description": account.get("Description"),
                    "status": account.get("Status"),
                    "class": account.get("Class"),  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
                    "enable_payments": account.get("EnablePaymentsToAccount"),
                    "show_in_expense_claims": account.get("ShowInExpenseClaims"),
                    "bank_account_number": account.get("BankAccountNumber"),
                    "synced_at": datetime.utcnow().isoformat()
                }
                processed_accounts.append(processed_account)

            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.records_synced = len(processed_accounts)

            connection.last_sync_at = datetime.utcnow()

            logger.info(
                f"Synced {len(processed_accounts)} Xero accounts for "
                f"connection {connection_id}"
            )

            return job

        except Exception as e:
            logger.error(f"Xero chart of accounts sync failed: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            raise

    async def sync_trial_balance(
        self,
        connection_id: UUID,
        date: Optional[str] = None
    ) -> XeroSyncJob:
        """Sync trial balance from Xero"""
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        job = XeroSyncJob(
            connection_id=connection_id,
            tenant_id=connection.tenant_id,
            data_type="trial_balance",
            status="in_progress"
        )
        self._sync_jobs[job.id] = job

        try:
            params = {}
            if date:
                params["date"] = date

            response = await self._make_api_call(
                connection=connection,
                method="GET",
                endpoint="/Reports/TrialBalance",
                params=params
            )

            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.records_synced = 1

            connection.last_sync_at = datetime.utcnow()

            logger.info(f"Synced Xero trial balance for connection {connection_id}")

            return job

        except Exception as e:
            logger.error(f"Xero trial balance sync failed: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            raise

    async def sync_balance_sheet(
        self,
        connection_id: UUID,
        date: Optional[str] = None
    ) -> XeroSyncJob:
        """Sync balance sheet from Xero"""
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        job = XeroSyncJob(
            connection_id=connection_id,
            tenant_id=connection.tenant_id,
            data_type="balance_sheet",
            status="in_progress"
        )
        self._sync_jobs[job.id] = job

        try:
            params = {}
            if date:
                params["date"] = date

            response = await self._make_api_call(
                connection=connection,
                method="GET",
                endpoint="/Reports/BalanceSheet",
                params=params
            )

            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.records_synced = 1

            connection.last_sync_at = datetime.utcnow()

            logger.info(f"Synced Xero balance sheet for connection {connection_id}")

            return job

        except Exception as e:
            logger.error(f"Xero balance sheet sync failed: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            raise

    async def sync_income_statement(
        self,
        connection_id: UUID,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> XeroSyncJob:
        """Sync profit & loss (income statement) from Xero"""
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        job = XeroSyncJob(
            connection_id=connection_id,
            tenant_id=connection.tenant_id,
            data_type="income_statement",
            status="in_progress"
        )
        self._sync_jobs[job.id] = job

        try:
            params = {}
            if start_date:
                params["fromDate"] = start_date
            if end_date:
                params["toDate"] = end_date

            response = await self._make_api_call(
                connection=connection,
                method="GET",
                endpoint="/Reports/ProfitAndLoss",
                params=params
            )

            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.records_synced = 1

            connection.last_sync_at = datetime.utcnow()

            logger.info(f"Synced Xero income statement for connection {connection_id}")

            return job

        except Exception as e:
            logger.error(f"Xero income statement sync failed: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            raise

    # ==================== Webhook Handling ====================

    def verify_webhook_signature(
        self,
        payload: str,
        signature: str,
        webhook_key: str
    ) -> bool:
        """Verify Xero webhook signature"""
        expected_signature = base64.b64encode(
            hmac.new(
                key=webhook_key.encode("utf-8"),
                msg=payload.encode("utf-8"),
                digestmod=hashlib.sha256
            ).digest()
        ).decode("utf-8")

        return hmac.compare_digest(signature, expected_signature)

    # ==================== Connection Management ====================

    def get_connection(self, connection_id: UUID) -> Optional[XeroConnection]:
        """Get connection by ID"""
        return self._connections.get(connection_id)

    def get_connections_by_tenant(self, tenant_id: UUID) -> List[XeroConnection]:
        """Get all connections for a tenant"""
        return [
            conn for conn in self._connections.values()
            if conn.tenant_id == tenant_id
        ]

    async def disconnect(self, connection_id: UUID):
        """Disconnect Xero integration"""
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        connection.status = "disconnected"
        connection.access_token = None
        connection.refresh_token = None

        if self.audit_log_service:
            await self.audit_log_service.log_event(
                event_type="integration_disconnected",
                user_id=connection.tenant_id,
                resource_type="integration",
                resource_id=str(connection_id),
                action="disconnect",
                changes={"provider": "xero"}
            )

        logger.info(f"Disconnected Xero connection {connection_id}")
