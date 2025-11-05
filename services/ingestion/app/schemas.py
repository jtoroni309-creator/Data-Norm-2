"""Pydantic schemas for API request/response models"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str
    version: str


class FilingInfo(BaseModel):
    """Filing metadata"""
    model_config = ConfigDict(from_attributes=True)

    cik: str
    ticker: Optional[str] = None
    company_name: str
    form: str
    filing_date: date
    source_uri: str


class FactItem(BaseModel):
    """Individual XBRL fact"""
    model_config = ConfigDict(from_attributes=True)

    concept: str
    taxonomy: str = "us-gaap"
    value: Optional[Decimal] = None
    unit: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    instant_date: Optional[date] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class EdgarFactsResponse(BaseModel):
    """Response for EDGAR company facts"""
    filing: FilingInfo
    facts: List[FactItem]
    total_facts: int = 0

    def __init__(self, **data):
        super().__init__(**data)
        self.total_facts = len(self.facts)


class PBCUploadResponse(BaseModel):
    """Response for PBC document upload"""
    engagement_id: UUID
    filename: str
    s3_uri: str
    size_bytes: int
    content_type: str
    description: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.now)


class TrialBalanceLine(BaseModel):
    """Trial balance line item"""
    line_number: int
    account_code: str
    account_name: str
    debit_amount: Optional[Decimal] = None
    credit_amount: Optional[Decimal] = None
    balance_amount: Optional[Decimal] = None
    taxonomy_concept: Optional[str] = None
    mapping_confidence: Optional[float] = None


class TrialBalanceImportRequest(BaseModel):
    """Request to import trial balance"""
    engagement_id: UUID
    period_end_date: date
    source: str = "manual"


class TrialBalanceImportResponse(BaseModel):
    """Response for trial balance import"""
    trial_balance_id: UUID
    engagement_id: UUID
    period_end_date: date
    lines_imported: int
    total_debits: Decimal
    total_credits: Decimal
    balance_difference: Decimal
    validation_errors: List[str] = Field(default_factory=list)
