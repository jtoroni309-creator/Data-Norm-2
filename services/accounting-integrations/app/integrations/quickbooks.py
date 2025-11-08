"""
QuickBooks Online Integration Client

OAuth 2.0 flow and API client for QuickBooks Online.

Documentation: https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

import httpx


class QuickBooksClient:
    """QuickBooks Online API client"""

    # OAuth endpoints
    AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
    TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    REVOKE_URL = "https://developer.api.intuit.com/v2/oauth2/tokens/revoke"

    # API endpoints
    SANDBOX_API_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company"
    PRODUCTION_API_URL = "https://quickbooks.api.intuit.com/v3/company"

    # OAuth scopes
    SCOPES = [
        "com.intuit.quickbooks.accounting",
        "com.intuit.quickbooks.payment",
    ]

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        realm_id: Optional[str] = None,
        environment: str = "sandbox",
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.realm_id = realm_id
        self.environment = environment

        # Select API URL based on environment
        self.api_url = self.SANDBOX_API_URL if environment == "sandbox" else self.PRODUCTION_API_URL

    def get_authorization_url(self) -> tuple[str, str]:
        """
        Get OAuth authorization URL.

        Returns:
            (auth_url, state) tuple
        """
        state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
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
            {
                "access_token": "...",
                "refresh_token": "...",
                "expires_at": datetime,
                "token_type": "bearer",
            }
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                headers={
                    "Accept": "application/json",
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
                    "Accept": "application/json",
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

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request"""
        url = f"{self.api_url}/{self.realm_id}/{endpoint}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def get_company_info(self) -> Dict[str, Any]:
        """Get company information"""
        result = await self._make_request("GET", "companyinfo/1")
        return result["CompanyInfo"]

    async def get_chart_of_accounts(self) -> Dict[str, Any]:
        """
        Fetch chart of accounts from QuickBooks.

        Returns standardized chart of accounts structure.
        """
        # Query all accounts
        query = "SELECT * FROM Account"
        result = await self._make_request(
            "GET",
            "query",
            params={"query": query}
        )

        accounts = []
        for account in result.get("QueryResponse", {}).get("Account", []):
            accounts.append({
                "account_id": account["Id"],
                "account_code": account.get("AcctNum"),
                "account_name": account["Name"],
                "account_type": account["AccountType"],
                "account_subtype": account.get("AccountSubType"),
                "parent_account_id": account.get("ParentRef", {}).get("value"),
                "is_active": account.get("Active", True),
                "balance": float(account.get("CurrentBalance", 0)),
            })

        company_info = await self.get_company_info()

        return {
            "accounts": accounts,
            "company_id": self.realm_id,
            "company_name": company_info.get("CompanyName"),
        }

    async def get_trial_balance(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch trial balance from QuickBooks.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Standardized trial balance structure
        """
        # Get trial balance report
        result = await self._make_request(
            "GET",
            "reports/TrialBalance",
            params={
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        line_items = []
        total_debits = 0.0
        total_credits = 0.0

        # Parse report rows
        for row in result.get("Rows", {}).get("Row", []):
            if row.get("type") == "Data":
                cols = row.get("ColData", [])
                if len(cols) >= 3:
                    account_name = cols[0].get("value", "")
                    debit = float(cols[1].get("value", "0").replace(",", ""))
                    credit = float(cols[2].get("value", "0").replace(",", ""))
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

        company_info = await self.get_company_info()

        return {
            "line_items": line_items,
            "start_date": start_date,
            "end_date": end_date,
            "total_debits": total_debits,
            "total_credits": total_credits,
            "company_id": self.realm_id,
            "company_name": company_info.get("CompanyName"),
        }

    async def create_journal_entry(
        self,
        entry_date: str,
        lines: List[Dict[str, Any]],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create journal entry (audit adjustment).

        Args:
            entry_date: Entry date (YYYY-MM-DD)
            lines: List of journal entry lines
            description: Entry description

        Returns:
            Created journal entry
        """
        # Build journal entry object
        journal_entry = {
            "TxnDate": entry_date,
            "Line": [],
        }

        if description:
            journal_entry["PrivateNote"] = description

        # Add lines
        for line in lines:
            je_line = {
                "DetailType": "JournalEntryLineDetail",
                "Amount": line["debit"] if line["debit"] > 0 else line["credit"],
                "JournalEntryLineDetail": {
                    "PostingType": "Debit" if line["debit"] > 0 else "Credit",
                    "AccountRef": {
                        "value": line["account_id"],
                    }
                }
            }

            if line.get("description"):
                je_line["Description"] = line["description"]

            journal_entry["Line"].append(je_line)

        # Create journal entry
        result = await self._make_request(
            "POST",
            "journalentry",
            json=journal_entry,
        )

        return result["JournalEntry"]
