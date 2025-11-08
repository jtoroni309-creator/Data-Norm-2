"""
Xero Integration Client

OAuth 2.0 flow and API client for Xero accounting.

Documentation: https://developer.xero.com/documentation/api/accounting/overview
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

import httpx


class XeroClient:
    """Xero API client with OAuth 2.0"""

    # OAuth endpoints
    AUTH_URL = "https://login.xero.com/identity/connect/authorize"
    TOKEN_URL = "https://identity.xero.com/connect/token"
    CONNECTIONS_URL = "https://api.xero.com/connections"

    # API endpoints
    API_URL = "https://api.xero.com/api.xro/2.0"

    # OAuth scopes
    SCOPES = [
        "offline_access",
        "accounting.transactions",
        "accounting.contacts",
        "accounting.settings",
        "accounting.reports.read",
    ]

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.tenant_id = tenant_id

    def get_authorization_url(self) -> tuple[str, str]:
        """
        Get Xero OAuth authorization URL.

        Returns:
            (auth_url, state) tuple
        """
        state = secrets.token_urlsafe(32)

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
        }

        auth_url = f"{self.AUTH_URL}?{urlencode(params)}"

        return auth_url, state

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token data with access_token, refresh_token, expires_at
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                auth=(self.client_id, self.client_secret),
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
            )

            response.raise_for_status()
            data = response.json()

            return {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_at": datetime.utcnow() + timedelta(seconds=data["expires_in"]),
                "token_type": data["token_type"],
            }

    async def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.

        Returns:
            Updated token data
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                auth=(self.client_id, self.client_secret),
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
            )

            response.raise_for_status()
            data = response.json()

            return {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_at": datetime.utcnow() + timedelta(seconds=data["expires_in"]),
                "token_type": data["token_type"],
            }

    async def get_tenant(self, access_token: str) -> Dict[str, Any]:
        """
        Get Xero tenant (organization) for the authenticated user.

        Returns first tenant if multiple exist.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.CONNECTIONS_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )

            response.raise_for_status()
            tenants = response.json()

            if not tenants:
                raise Exception("No Xero organizations found for this user")

            # Return first tenant
            return tenants[0]

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request"""
        url = f"{self.API_URL}/{endpoint}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Xero-tenant-id": self.tenant_id,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def get_organisation(self) -> Dict[str, Any]:
        """Get organization information"""
        result = await self._make_request("GET", "Organisation")
        organisations = result.get("Organisations", [])
        return organisations[0] if organisations else {}

    async def get_chart_of_accounts(self) -> Dict[str, Any]:
        """
        Fetch chart of accounts from Xero.

        Returns standardized chart of accounts structure.
        """
        result = await self._make_request("GET", "Accounts")

        accounts = []
        for account in result.get("Accounts", []):
            accounts.append({
                "account_id": account["AccountID"],
                "account_code": account.get("Code"),
                "account_name": account["Name"],
                "account_type": account["Type"],
                "account_subtype": account.get("Class"),
                "parent_account_id": None,  # Xero doesn't have parent accounts
                "is_active": account.get("Status") == "ACTIVE",
                "balance": float(account.get("CurrentBalance", 0)),
            })

        org = await self.get_organisation()

        return {
            "accounts": accounts,
            "company_id": self.tenant_id,
            "company_name": org.get("Name"),
        }

    async def get_trial_balance(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch trial balance from Xero.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Standardized trial balance structure
        """
        # Get trial balance report
        result = await self._make_request(
            "GET",
            "Reports/TrialBalance",
            params={
                "date": end_date,
            }
        )

        line_items = []
        total_debits = 0.0
        total_credits = 0.0

        # Parse report rows
        report = result.get("Reports", [{}])[0]
        for row in report.get("Rows", []):
            if row.get("RowType") == "Row":
                cells = row.get("Cells", [])
                if len(cells) >= 3:
                    account_name = cells[0].get("Value", "")
                    debit = float(cells[1].get("Value", "0"))
                    credit = float(cells[2].get("Value", "0"))
                    balance = debit - credit

                    line_items.append({
                        "account_id": "",  # Not provided in report
                        "account_code": "",
                        "account_name": account_name,
                        "account_type": "",
                        "debit": debit,
                        "credit": credit,
                        "balance": balance,
                    })

                    total_debits += debit
                    total_credits += credit

        org = await self.get_organisation()

        return {
            "line_items": line_items,
            "start_date": start_date,
            "end_date": end_date,
            "total_debits": total_debits,
            "total_credits": total_credits,
            "company_id": self.tenant_id,
            "company_name": org.get("Name"),
        }

    async def create_journal_entry(
        self,
        entry_date: str,
        lines: List[Dict[str, Any]],
        description: Optional[str] = None,
        reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create manual journal (audit adjustment).

        Args:
            entry_date: Entry date (YYYY-MM-DD)
            lines: List of journal entry lines
            description: Entry description
            reference: Reference number

        Returns:
            Created manual journal
        """
        # Build manual journal object
        manual_journal = {
            "Date": entry_date,
            "JournalLines": [],
        }

        if description:
            manual_journal["Narration"] = description

        if reference:
            manual_journal["Reference"] = reference

        # Add lines
        for line in lines:
            journal_line = {
                "LineAmount": line["debit"] if line["debit"] > 0 else line["credit"],
                "AccountCode": line.get("account_code", line["account_id"]),
            }

            if line.get("description"):
                journal_line["Description"] = line["description"]

            manual_journal["JournalLines"].append(journal_line)

        # Create manual journal
        result = await self._make_request(
            "PUT",
            "ManualJournals",
            json={"ManualJournals": [manual_journal]},
        )

        manual_journals = result.get("ManualJournals", [])
        return manual_journals[0] if manual_journals else {}

    async def get_general_ledger(
        self,
        start_date: str,
        end_date: str,
        account_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch general ledger transactions.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            account_code: Optional account code filter

        Returns:
            General ledger transactions
        """
        params = {
            "fromDate": start_date,
            "toDate": end_date,
        }

        if account_code:
            params["accountCode"] = account_code

        result = await self._make_request(
            "GET",
            "Journals",
            params=params,
        )

        return result.get("Journals", [])
