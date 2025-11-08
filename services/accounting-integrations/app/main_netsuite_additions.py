"""
NetSuite Integration Endpoints

Add these endpoints to the main FastAPI app for NetSuite support.

Usage:
    Include these functions in your main.py file after importing NetSuiteClient
"""

from fastapi import HTTPException, Depends, Query
from uuid import UUID

from .integrations.netsuite import NetSuiteClient
from .config import get_settings
from .database import get_db
from .models import Connection, ConnectionStatus
from sqlalchemy.ext.asyncio import AsyncSession

settings = get_settings()


# NetSuite - No OAuth flow, uses Token-Based Authentication (TBA)

async def create_netsuite_connection(
    organization_id: UUID,
    account_id: str,
    consumer_key: str,
    consumer_secret: str,
    token_id: str,
    token_secret: str,
    company_name: str = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Create NetSuite connection using Token-Based Authentication (TBA).

    Unlike QuickBooks/Xero, NetSuite doesn't use OAuth 2.0.
    Credentials are obtained from NetSuite's Integration Records and Access Tokens.

    Steps to get credentials:
    1. In NetSuite: Setup > Integration > Manage Integrations > New
    2. Create integration record → Get Consumer Key/Secret
    3. Setup > Users/Roles > Access Tokens > New
    4. Create access token → Get Token ID/Secret

    Args:
        organization_id: Your organization ID
        account_id: NetSuite account ID (e.g., "1234567")
        consumer_key: From integration record
        consumer_secret: From integration record
        token_id: From access token
        token_secret: From access token
        company_name: Optional company name
    """
    try:
        # Test connection first
        client = NetSuiteClient(
            account_id=account_id,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            token_id=token_id,
            token_secret=token_secret,
        )

        # Test the connection
        test_result = await client.test_connection()
        if test_result["status"] != "success":
            raise HTTPException(
                status_code=400,
                detail=f"NetSuite connection test failed: {test_result.get('message')}"
            )

        # Get company info if not provided
        if not company_name:
            company_info = await client.get_company_info()
            company_name = company_info.get("company_name")

        # Create connection record
        connection = Connection(
            organization_id=organization_id,
            provider="netsuite",
            provider_company_id=account_id,
            access_token=consumer_key,  # Store consumer key as access token
            refresh_token=None,  # NetSuite TBA doesn't use refresh tokens
            token_expires_at=None,  # TBA tokens don't expire
            status=ConnectionStatus.ACTIVE,
            settings={
                "account_id": account_id,
                "company_name": company_name,
                "consumer_secret": consumer_secret,  # Encrypted by model
                "token_id": token_id,
                "token_secret": token_secret,  # Encrypted by model
            },
        )

        db.add(connection)
        await db.commit()
        await db.refresh(connection)

        logger.info(
            f"NetSuite connection created",
            extra={
                "organization_id": str(organization_id),
                "account_id": account_id,
                "connection_id": str(connection.id),
            }
        )

        return connection

    except Exception as e:
        logger.error(f"NetSuite connection creation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def get_netsuite_trial_balance(
    connection_id: UUID,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch trial balance from NetSuite.

    Returns standardized trial balance data.
    """
    connection = await db.get(Connection, connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if connection.provider != "netsuite":
        raise HTTPException(status_code=400, detail="Not a NetSuite connection")

    client = NetSuiteClient(
        account_id=connection.settings["account_id"],
        consumer_key=connection.access_token,
        consumer_secret=connection.settings["consumer_secret"],
        token_id=connection.settings["token_id"],
        token_secret=connection.settings["token_secret"],
    )

    trial_balance = await client.get_trial_balance(start_date, end_date)

    return trial_balance


async def get_netsuite_chart_of_accounts(
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch chart of accounts from NetSuite.
    """
    connection = await db.get(Connection, connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if connection.provider != "netsuite":
        raise HTTPException(status_code=400, detail="Not a NetSuite connection")

    client = NetSuiteClient(
        account_id=connection.settings["account_id"],
        consumer_key=connection.access_token,
        consumer_secret=connection.settings["consumer_secret"],
        token_id=connection.settings["token_id"],
        token_secret=connection.settings["token_secret"],
    )

    coa = await client.get_chart_of_accounts()

    return coa


async def create_netsuite_journal_entry(
    connection_id: UUID,
    entry_date: str,
    lines: list,
    memo: str = None,
    subsidiary_id: str = "1",
    db: AsyncSession = Depends(get_db),
):
    """
    Create journal entry in NetSuite (audit adjustment).
    """
    connection = await db.get(Connection, connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if connection.provider != "netsuite":
        raise HTTPException(status_code=400, detail="Not a NetSuite connection")

    client = NetSuiteClient(
        account_id=connection.settings["account_id"],
        consumer_key=connection.access_token,
        consumer_secret=connection.settings["consumer_secret"],
        token_id=connection.settings["token_id"],
        token_secret=connection.settings["token_secret"],
    )

    journal_entry = await client.create_journal_entry(
        entry_date=entry_date,
        lines=lines,
        memo=memo,
        subsidiary_id=subsidiary_id,
    )

    return journal_entry


# Add these to your main app:
"""
from .main_netsuite_additions import (
    create_netsuite_connection,
    get_netsuite_trial_balance,
    get_netsuite_chart_of_accounts,
    create_netsuite_journal_entry,
)

# NetSuite endpoints (Token-Based Authentication)
@app.post("/netsuite/connect", response_model=ConnectionResponse)
async def connect_netsuite(
    organization_id: UUID,
    account_id: str,
    consumer_key: str,
    consumer_secret: str,
    token_id: str,
    token_secret: str,
    company_name: str = None,
    db: AsyncSession = Depends(get_db),
):
    return await create_netsuite_connection(
        organization_id, account_id, consumer_key, consumer_secret,
        token_id, token_secret, company_name, db
    )

@app.get("/netsuite/{connection_id}/trial-balance", response_model=TrialBalanceResponse)
async def netsuite_trial_balance(
    connection_id: UUID,
    start_date: str,
    end_date: str,
    db: AsyncSession = Depends(get_db),
):
    return await get_netsuite_trial_balance(connection_id, start_date, end_date, db)

@app.get("/netsuite/{connection_id}/chart-of-accounts", response_model=ChartOfAccountsResponse)
async def netsuite_coa(connection_id: UUID, db: AsyncSession = Depends(get_db)):
    return await get_netsuite_chart_of_accounts(connection_id, db)
"""
