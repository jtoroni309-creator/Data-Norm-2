"""
Plaid API Integration Service

Handles bank account connections, transaction synchronization, and webhook processing.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import plaid
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from .config import settings

logger = logging.getLogger(__name__)


class PlaidService:
    """
    Service for integrating with Plaid API.

    Provides methods for:
    - Creating Link tokens for account connection
    - Exchanging public tokens for access tokens
    - Fetching account information
    - Syncing transactions
    - Processing webhooks
    """

    def __init__(self):
        """Initialize Plaid client."""
        configuration = plaid.Configuration(
            host=self._get_plaid_host(),
            api_key={
                'clientId': settings.PLAID_CLIENT_ID,
                'secret': settings.PLAID_SECRET,
            }
        )

        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

        logger.info(f"Plaid service initialized with environment: {settings.PLAID_ENVIRONMENT}")

    def _get_plaid_host(self) -> str:
        """Get Plaid API host based on environment."""
        env_map = {
            'sandbox': plaid.Environment.Sandbox,
            'development': plaid.Environment.Development,
            'production': plaid.Environment.Production,
        }
        return env_map.get(settings.PLAID_ENVIRONMENT, plaid.Environment.Sandbox)

    async def create_link_token(
        self,
        user_id: str,
        client_name: str = "Aura Audit AI"
    ) -> Dict[str, Any]:
        """
        Create a Link token for Plaid Link flow.

        Args:
            user_id: Unique identifier for the user
            client_name: Name to display in Plaid Link

        Returns:
            Dictionary containing link_token and expiration
        """
        try:
            request = LinkTokenCreateRequest(
                products=[Products("transactions"), Products("auth")],
                client_name=client_name,
                country_codes=[CountryCode('US')],
                language='en',
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id
                ),
                webhook=settings.PLAID_WEBHOOK_URL if settings.PLAID_WEBHOOK_URL else None
            )

            response = self.client.link_token_create(request)

            return {
                'link_token': response['link_token'],
                'expiration': response['expiration'],
            }

        except plaid.ApiException as e:
            logger.error(f"Error creating link token: {e}")
            raise Exception(f"Failed to create link token: {str(e)}")

    async def exchange_public_token(self, public_token: str) -> Dict[str, str]:
        """
        Exchange public token for access token.

        Args:
            public_token: Public token from Plaid Link

        Returns:
            Dictionary containing access_token and item_id
        """
        try:
            request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )

            response = self.client.item_public_token_exchange(request)

            return {
                'access_token': response['access_token'],
                'item_id': response['item_id'],
            }

        except plaid.ApiException as e:
            logger.error(f"Error exchanging public token: {e}")
            raise Exception(f"Failed to exchange public token: {str(e)}")

    async def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get account information.

        Args:
            access_token: Plaid access token

        Returns:
            List of account dictionaries
        """
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)

            accounts = []
            for account in response['accounts']:
                accounts.append({
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'mask': account.get('mask'),
                    'type': account['type'],
                    'subtype': account.get('subtype'),
                    'balances': {
                        'current': account['balances'].get('current'),
                        'available': account['balances'].get('available'),
                    }
                })

            return accounts

        except plaid.ApiException as e:
            logger.error(f"Error getting accounts: {e}")
            raise Exception(f"Failed to get accounts: {str(e)}")

    async def get_item(self, access_token: str) -> Dict[str, Any]:
        """
        Get item (institution) information.

        Args:
            access_token: Plaid access token

        Returns:
            Dictionary containing item information
        """
        try:
            request = ItemGetRequest(access_token=access_token)
            response = self.client.item_get(request)

            item = response['item']
            return {
                'item_id': item['item_id'],
                'institution_id': item.get('institution_id'),
                'webhook': item.get('webhook'),
                'error': item.get('error'),
                'available_products': item.get('available_products', []),
                'billed_products': item.get('billed_products', []),
            }

        except plaid.ApiException as e:
            logger.error(f"Error getting item: {e}")
            raise Exception(f"Failed to get item: {str(e)}")

    async def get_transactions(
        self,
        access_token: str,
        start_date: datetime,
        end_date: datetime,
        account_ids: Optional[List[str]] = None,
        count: int = 500,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get transactions for a date range.

        Args:
            access_token: Plaid access token
            start_date: Start date for transactions
            end_date: End date for transactions
            account_ids: Optional list of account IDs to filter
            count: Number of transactions to fetch (max 500)
            offset: Number of transactions to skip

        Returns:
            Dictionary containing transactions and pagination info
        """
        try:
            options = TransactionsGetRequestOptions()
            if account_ids:
                options['account_ids'] = account_ids
            options['count'] = count
            options['offset'] = offset

            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.date(),
                end_date=end_date.date(),
                options=options
            )

            response = self.client.transactions_get(request)

            transactions = []
            for txn in response['transactions']:
                transactions.append({
                    'transaction_id': txn['transaction_id'],
                    'account_id': txn['account_id'],
                    'amount': float(txn['amount']),
                    'date': txn['date'],
                    'authorized_date': txn.get('authorized_date'),
                    'name': txn['name'],
                    'merchant_name': txn.get('merchant_name'),
                    'pending': txn.get('pending', False),
                    'category': txn.get('category', []),
                    'category_id': txn.get('category_id'),
                    'payment_channel': txn.get('payment_channel'),
                    'location': {
                        'address': txn.get('location', {}).get('address'),
                        'city': txn.get('location', {}).get('city'),
                        'region': txn.get('location', {}).get('region'),
                        'postal_code': txn.get('location', {}).get('postal_code'),
                        'country': txn.get('location', {}).get('country'),
                        'lat': txn.get('location', {}).get('lat'),
                        'lon': txn.get('location', {}).get('lon'),
                    },
                    'payment_meta': txn.get('payment_meta'),
                })

            return {
                'transactions': transactions,
                'total_transactions': response['total_transactions'],
                'accounts': response['accounts'],
            }

        except plaid.ApiException as e:
            logger.error(f"Error getting transactions: {e}")
            raise Exception(f"Failed to get transactions: {str(e)}")

    async def sync_transactions(
        self,
        access_token: str,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sync transactions using the transactions/sync endpoint.

        This is more efficient for ongoing transaction monitoring.

        Args:
            access_token: Plaid access token
            cursor: Cursor for pagination (from previous sync)

        Returns:
            Dictionary containing added, modified, removed transactions and next cursor
        """
        try:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor
            )

            response = self.client.transactions_sync(request)

            added = []
            for txn in response.get('added', []):
                added.append({
                    'transaction_id': txn['transaction_id'],
                    'account_id': txn['account_id'],
                    'amount': float(txn['amount']),
                    'date': txn['date'],
                    'authorized_date': txn.get('authorized_date'),
                    'name': txn['name'],
                    'merchant_name': txn.get('merchant_name'),
                    'pending': txn.get('pending', False),
                    'category': txn.get('category', []),
                    'payment_channel': txn.get('payment_channel'),
                    'location': txn.get('location', {}),
                })

            modified = []
            for txn in response.get('modified', []):
                modified.append({
                    'transaction_id': txn['transaction_id'],
                    'account_id': txn['account_id'],
                    'amount': float(txn['amount']),
                    'date': txn['date'],
                    'pending': txn.get('pending', False),
                })

            removed = [txn['transaction_id'] for txn in response.get('removed', [])]

            return {
                'added': added,
                'modified': modified,
                'removed': removed,
                'next_cursor': response['next_cursor'],
                'has_more': response['has_more'],
            }

        except plaid.ApiException as e:
            logger.error(f"Error syncing transactions: {e}")
            raise Exception(f"Failed to sync transactions: {str(e)}")

    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Plaid webhook.

        Args:
            webhook_data: Webhook payload from Plaid

        Returns:
            Dictionary containing processing results
        """
        webhook_type = webhook_data.get('webhook_type')
        webhook_code = webhook_data.get('webhook_code')
        item_id = webhook_data.get('item_id')

        logger.info(
            f"Processing Plaid webhook: type={webhook_type}, "
            f"code={webhook_code}, item_id={item_id}"
        )

        result = {
            'webhook_type': webhook_type,
            'webhook_code': webhook_code,
            'item_id': item_id,
            'processed': True,
        }

        # Handle different webhook types
        if webhook_type == 'TRANSACTIONS':
            if webhook_code == 'INITIAL_UPDATE':
                result['action'] = 'initial_sync_complete'
            elif webhook_code == 'HISTORICAL_UPDATE':
                result['action'] = 'historical_sync_complete'
            elif webhook_code == 'DEFAULT_UPDATE':
                result['action'] = 'sync_new_transactions'
                result['new_transactions'] = webhook_data.get('new_transactions', 0)
            elif webhook_code == 'TRANSACTIONS_REMOVED':
                result['action'] = 'remove_transactions'
                result['removed_transactions'] = webhook_data.get('removed_transactions', [])

        elif webhook_type == 'ITEM':
            if webhook_code == 'ERROR':
                result['action'] = 'item_error'
                result['error'] = webhook_data.get('error')
            elif webhook_code == 'PENDING_EXPIRATION':
                result['action'] = 'reauth_required'
            elif webhook_code == 'USER_PERMISSION_REVOKED':
                result['action'] = 'permission_revoked'

        return result

    async def get_institution(self, institution_id: str) -> Dict[str, Any]:
        """
        Get institution details.

        Args:
            institution_id: Plaid institution ID

        Returns:
            Dictionary containing institution information
        """
        try:
            from plaid.model.institutions_get_by_id_request import (
                InstitutionsGetByIdRequest,
            )

            request = InstitutionsGetByIdRequest(
                institution_id=institution_id,
                country_codes=[CountryCode('US')]
            )

            response = self.client.institutions_get_by_id(request)

            institution = response['institution']
            return {
                'institution_id': institution['institution_id'],
                'name': institution['name'],
                'products': institution.get('products', []),
                'country_codes': institution.get('country_codes', []),
                'url': institution.get('url'),
                'primary_color': institution.get('primary_color'),
                'logo': institution.get('logo'),
            }

        except plaid.ApiException as e:
            logger.error(f"Error getting institution: {e}")
            raise Exception(f"Failed to get institution: {str(e)}")


# Singleton instance
plaid_service = PlaidService()
