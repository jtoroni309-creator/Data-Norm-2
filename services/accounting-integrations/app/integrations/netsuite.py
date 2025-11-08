"""
NetSuite Integration Client

Token-Based Authentication (TBA) and SuiteTalk REST API client for NetSuite.

Documentation: https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/book_1559132836.html
"""

import base64
import hashlib
import hmac
import secrets
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode, quote

import httpx


class NetSuiteClient:
    """NetSuite SuiteTalk REST API client with OAuth 1.0a"""

    # API endpoint
    API_BASE_URL = "https://{account_id}.suitetalk.api.netsuite.com/services/rest"
    API_VERSION = "v1"

    def __init__(
        self,
        account_id: str,
        consumer_key: str,
        consumer_secret: str,
        token_id: str,
        token_secret: str,
    ):
        """
        Initialize NetSuite client with Token-Based Authentication (TBA) credentials.

        Args:
            account_id: NetSuite account ID (e.g., "1234567")
            consumer_key: Consumer key from integration record
            consumer_secret: Consumer secret from integration record
            token_id: Token ID from access token
            token_secret: Token secret from access token
        """
        self.account_id = account_id
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token_id = token_id
        self.token_secret = token_secret

        self.api_url = self.API_BASE_URL.format(account_id=account_id)

    def _generate_oauth_signature(
        self,
        method: str,
        url: str,
        params: Dict[str, str],
    ) -> str:
        """
        Generate OAuth 1.0a signature for NetSuite TBA.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL
            params: OAuth parameters

        Returns:
            Base64-encoded HMAC-SHA256 signature
        """
        # Sort parameters
        sorted_params = sorted(params.items())

        # Create parameter string
        param_string = "&".join(
            f"{quote(str(k), safe='')}={quote(str(v), safe='')}"
            for k, v in sorted_params
        )

        # Create signature base string
        base_string = "&".join([
            method.upper(),
            quote(url, safe=''),
            quote(param_string, safe=''),
        ])

        # Create signing key
        signing_key = "&".join([
            quote(self.consumer_secret, safe=''),
            quote(self.token_secret, safe=''),
        ])

        # Generate signature
        signature = hmac.new(
            signing_key.encode(),
            base_string.encode(),
            hashlib.sha256,
        ).digest()

        return base64.b64encode(signature).decode()

    def _get_oauth_header(self, method: str, url: str) -> str:
        """
        Generate OAuth 1.0a authorization header for NetSuite TBA.

        Args:
            method: HTTP method
            url: Full URL

        Returns:
            OAuth authorization header value
        """
        # OAuth parameters
        oauth_params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_token": self.token_id,
            "oauth_signature_method": "HMAC-SHA256",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": secrets.token_hex(16),
            "oauth_version": "1.0",
        }

        # Generate signature
        oauth_params["oauth_signature"] = self._generate_oauth_signature(
            method, url, oauth_params
        )

        # Build authorization header
        auth_header = "OAuth " + ", ".join(
            f'{k}="{quote(str(v), safe="")}"'
            for k, v in sorted(oauth_params.items())
        )

        return auth_header

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make authenticated API request to NetSuite.

        Args:
            method: HTTP method
            endpoint: API endpoint (e.g., "record/v1/account")
            **kwargs: Additional request parameters

        Returns:
            API response as dict
        """
        url = f"{self.api_url}/{endpoint}"

        # Generate OAuth header
        auth_header = self._get_oauth_header(method, url)

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test NetSuite connection.

        Returns:
            Connection status
        """
        try:
            # Try to fetch company information
            result = await self._make_request("GET", "record/v1/subsidiary")
            return {
                "status": "success",
                "message": "Connection successful",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": str(e),
            }

    async def get_chart_of_accounts(self) -> Dict[str, Any]:
        """
        Fetch chart of accounts from NetSuite.

        Returns:
            Standardized chart of accounts structure
        """
        # Query accounts using SuiteQL
        query = """
            SELECT
                id,
                accountnumber,
                displayname,
                accttype,
                parent,
                isinactive
            FROM
                account
            ORDER BY
                accountnumber
        """

        result = await self._make_request(
            "POST",
            "query/v1/suiteql",
            json={"q": query},
        )

        accounts = []
        for item in result.get("items", []):
            # Map NetSuite account types to standard types
            account_type_map = {
                "Bank": "Asset",
                "AcctRec": "Asset",
                "OthCurrAsset": "Asset",
                "FixedAsset": "Asset",
                "OthAsset": "Asset",
                "AcctPay": "Liability",
                "CreditCard": "Liability",
                "OthCurrLiab": "Liability",
                "LongTermLiab": "Liability",
                "Equity": "Equity",
                "Income": "Revenue",
                "COGS": "Expense",
                "Expense": "Expense",
                "OthIncome": "Revenue",
                "OthExpense": "Expense",
            }

            accounts.append({
                "account_id": str(item["id"]),
                "account_code": item.get("accountnumber"),
                "account_name": item["displayname"],
                "account_type": account_type_map.get(item["accttype"], "Asset"),
                "account_subtype": item["accttype"],
                "parent_account_id": str(item["parent"]) if item.get("parent") else None,
                "is_active": not item.get("isinactive", False),
                "balance": 0.0,  # Would need separate balance query
            })

        # Get company info
        company_info = await self.get_company_info()

        return {
            "accounts": accounts,
            "company_id": self.account_id,
            "company_name": company_info.get("company_name"),
        }

    async def get_company_info(self) -> Dict[str, Any]:
        """Get company information"""
        # Get subsidiary info (acts as company)
        result = await self._make_request("GET", "record/v1/subsidiary/1")

        return {
            "company_name": result.get("name"),
            "account_id": self.account_id,
        }

    async def get_trial_balance(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch trial balance from NetSuite.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Standardized trial balance structure
        """
        # Query trial balance using SuiteQL
        # This queries the transaction lines aggregated by account
        query = f"""
            SELECT
                a.id as account_id,
                a.accountnumber as account_code,
                a.displayname as account_name,
                a.accttype as account_type,
                SUM(CASE WHEN tl.debit > 0 THEN tl.debit ELSE 0 END) as total_debit,
                SUM(CASE WHEN tl.credit > 0 THEN tl.credit ELSE 0 END) as total_credit
            FROM
                transactionline tl
                INNER JOIN account a ON tl.account = a.id
                INNER JOIN transaction t ON tl.transaction = t.id
            WHERE
                t.trandate BETWEEN TO_DATE('{start_date}', 'YYYY-MM-DD')
                AND TO_DATE('{end_date}', 'YYYY-MM-DD')
            GROUP BY
                a.id, a.accountnumber, a.displayname, a.accttype
            ORDER BY
                a.accountnumber
        """

        result = await self._make_request(
            "POST",
            "query/v1/suiteql",
            json={"q": query},
        )

        line_items = []
        total_debits = 0.0
        total_credits = 0.0

        # Map NetSuite account types
        account_type_map = {
            "Bank": "Asset",
            "AcctRec": "Asset",
            "OthCurrAsset": "Asset",
            "FixedAsset": "Asset",
            "OthAsset": "Asset",
            "AcctPay": "Liability",
            "CreditCard": "Liability",
            "OthCurrLiab": "Liability",
            "LongTermLiab": "Liability",
            "Equity": "Equity",
            "Income": "Revenue",
            "COGS": "Expense",
            "Expense": "Expense",
            "OthIncome": "Revenue",
            "OthExpense": "Expense",
        }

        for item in result.get("items", []):
            debit = float(item.get("total_debit", 0))
            credit = float(item.get("total_credit", 0))
            balance = debit - credit

            line_items.append({
                "account_id": str(item["account_id"]),
                "account_code": item.get("account_code", ""),
                "account_name": item["account_name"],
                "account_type": account_type_map.get(item["account_type"], "Asset"),
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
            "company_id": self.account_id,
            "company_name": company_info.get("company_name"),
        }

    async def create_journal_entry(
        self,
        entry_date: str,
        lines: List[Dict[str, Any]],
        memo: Optional[str] = None,
        subsidiary_id: str = "1",
    ) -> Dict[str, Any]:
        """
        Create journal entry (audit adjustment).

        Args:
            entry_date: Entry date (YYYY-MM-DD)
            lines: List of journal entry lines
            memo: Entry memo
            subsidiary_id: Subsidiary ID (default: 1)

        Returns:
            Created journal entry
        """
        # Build journal entry object
        journal_entry = {
            "tranDate": entry_date,
            "subsidiary": {"id": subsidiary_id},
            "line": [],
        }

        if memo:
            journal_entry["memo"] = memo

        # Add lines
        for line in lines:
            je_line = {
                "account": {"id": line["account_id"]},
                "debit": line["debit"] if line["debit"] > 0 else None,
                "credit": line["credit"] if line["credit"] > 0 else None,
            }

            if line.get("description"):
                je_line["memo"] = line["description"]

            journal_entry["line"].append(je_line)

        # Create journal entry
        result = await self._make_request(
            "POST",
            "record/v1/journalEntry",
            json=journal_entry,
        )

        return result

    async def get_general_ledger(
        self,
        start_date: str,
        end_date: str,
        account_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch general ledger transactions.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            account_id: Optional account ID filter

        Returns:
            General ledger transactions
        """
        # Build query
        query = f"""
            SELECT
                t.id as transaction_id,
                t.tranid as transaction_number,
                t.type as transaction_type,
                t.trandate as transaction_date,
                tl.account as account_id,
                a.displayname as account_name,
                tl.debit,
                tl.credit,
                tl.memo
            FROM
                transactionline tl
                INNER JOIN transaction t ON tl.transaction = t.id
                INNER JOIN account a ON tl.account = a.id
            WHERE
                t.trandate BETWEEN TO_DATE('{start_date}', 'YYYY-MM-DD')
                AND TO_DATE('{end_date}', 'YYYY-MM-DD')
        """

        if account_id:
            query += f" AND tl.account = {account_id}"

        query += " ORDER BY t.trandate, t.id"

        result = await self._make_request(
            "POST",
            "query/v1/suiteql",
            json={"q": query},
        )

        transactions = []
        for item in result.get("items", []):
            transactions.append({
                "transaction_id": str(item["transaction_id"]),
                "transaction_number": item.get("transaction_number"),
                "transaction_type": item["transaction_type"],
                "transaction_date": item["transaction_date"],
                "account_id": str(item["account_id"]),
                "account_name": item["account_name"],
                "debit": float(item.get("debit", 0)),
                "credit": float(item.get("credit", 0)),
                "memo": item.get("memo"),
            })

        return transactions
