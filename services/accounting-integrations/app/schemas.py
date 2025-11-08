"""Pydantic schemas for API validation"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class ConnectionCreate(BaseModel):
    """Create a new connection"""
    organization_id: UUID
    provider: str
    provider_company_id: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    settings: Dict[str, Any] = {}


class ConnectionResponse(BaseModel):
    """Connection response"""
    id: UUID
    organization_id: UUID
    provider: str
    provider_company_id: str
    status: str
    last_sync_at: Optional[datetime] = None
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountResponse(BaseModel):
    """Chart of account item"""
    account_id: str
    account_code: Optional[str] = None
    account_name: str
    account_type: str  # Asset, Liability, Equity, Revenue, Expense
    account_subtype: Optional[str] = None
    parent_account_id: Optional[str] = None
    is_active: bool = True
    balance: Optional[float] = None


class ChartOfAccountsResponse(BaseModel):
    """Chart of accounts"""
    accounts: List[AccountResponse]
    as_of_date: Optional[str] = None
    company_id: str
    company_name: Optional[str] = None


class TrialBalanceLineItem(BaseModel):
    """Trial balance line item"""
    account_id: str
    account_code: Optional[str] = None
    account_name: str
    account_type: str
    debit: float = 0.0
    credit: float = 0.0
    balance: float = 0.0


class TrialBalanceResponse(BaseModel):
    """Trial balance"""
    line_items: List[TrialBalanceLineItem]
    start_date: str
    end_date: str
    total_debits: float
    total_credits: float
    company_id: str
    company_name: Optional[str] = None

    class Config:
        from_attributes = True


class JournalEntryLine(BaseModel):
    """Journal entry line"""
    account_id: str
    account_name: str
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None


class JournalEntryCreate(BaseModel):
    """Create journal entry (audit adjustment)"""
    connection_id: UUID
    entry_date: str  # YYYY-MM-DD
    description: str
    lines: List[JournalEntryLine]
    reference: Optional[str] = None  # Workpaper reference


class JournalEntryResponse(BaseModel):
    """Journal entry response"""
    id: UUID
    connection_id: UUID
    provider_entry_id: Optional[str] = None  # ID in accounting system
    entry_date: str
    description: str
    lines: List[JournalEntryLine]
    reference: Optional[str] = None
    created_at: datetime
    synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True
