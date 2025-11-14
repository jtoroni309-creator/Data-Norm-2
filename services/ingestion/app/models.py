"""SQLAlchemy ORM models for Ingestion Service"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Integer,
    Numeric,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from .database import Base


class Filing(Base):
    """EDGAR filing metadata"""
    __tablename__ = "filings"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    cik = Column(String, nullable=False, index=True)
    ticker = Column(String, index=True)
    company_name = Column(String, nullable=False)
    form = Column(
        SQLEnum("10-K", "10-Q", "20-F", "40-F", "6-K", "8-K", "DEF-14A", "S-1", "S-3", name="filing_form"),
        nullable=False
    )
    filing_date = Column(Date, nullable=False)
    accession_number = Column(String, nullable=False, unique=True)
    source_uri = Column(String, nullable=False)
    fiscal_year = Column(Integer)
    fiscal_period = Column(String)
    ingested_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ingested_by = Column(PGUUID(as_uuid=True))

    # Relationships
    facts = relationship("Fact", back_populates="filing", cascade="all, delete-orphan")


class Fact(Base):
    """XBRL fact (financial data point)"""
    __tablename__ = "facts"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.filings.id", ondelete="CASCADE"), nullable=False)
    concept = Column(String, nullable=False, index=True)
    taxonomy = Column(String, nullable=False, default="us-gaap")
    value = Column(Numeric)
    unit = Column(String)
    start_date = Column(Date)
    end_date = Column(Date, index=True)
    instant_date = Column(Date, index=True)
    context_ref = Column(String)
    decimals = Column(Integer)
    fact_metadata = Column("metadata", JSONB)  # Renamed to avoid SQLAlchemy reserved word
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    filing = relationship("Filing", back_populates="facts")


class TrialBalance(Base):
    """Trial balance import"""
    __tablename__ = "trial_balances"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    period_end_date = Column(Date, nullable=False)
    source = Column(String, nullable=False)
    source_metadata = Column(JSONB)
    imported_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    imported_by = Column(PGUUID(as_uuid=True))

    # Relationships
    lines = relationship("TrialBalanceLine", back_populates="trial_balance", cascade="all, delete-orphan")


class TrialBalanceLine(Base):
    """Individual trial balance line item"""
    __tablename__ = "trial_balance_lines"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    trial_balance_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("atlas.trial_balances.id", ondelete="CASCADE"),
        nullable=False
    )
    line_number = Column(Integer, nullable=False)
    account_code = Column(String, nullable=False)
    account_name = Column(String, nullable=False)
    debit_amount = Column(Numeric(18, 2))
    credit_amount = Column(Numeric(18, 2))
    balance_amount = Column(Numeric(18, 2))
    mapped_account_id = Column(PGUUID(as_uuid=True))
    mapping_confidence = Column(Numeric(3, 2))
    mapping_method = Column(String)
    taxonomy_concept = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    trial_balance = relationship("TrialBalance", back_populates="lines")
