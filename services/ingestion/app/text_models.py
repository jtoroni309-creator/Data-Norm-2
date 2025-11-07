"""
SQLAlchemy ORM models for filing text content
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Text,
    Boolean,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, VECTOR
from sqlalchemy.orm import relationship

from .database import Base


class FilingSection(Base):
    """Filing section content (MD&A, Risk Factors, etc.)"""
    __tablename__ = "filing_sections"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.filings.id", ondelete="CASCADE"), nullable=False)
    section_type = Column(String(100), nullable=False)
    section_title = Column(String(500))
    content = Column(Text, nullable=False)
    content_length = Column(Integer, nullable=False)
    word_count = Column(Integer)
    s3_uri = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class FilingNote(Base):
    """Financial statement note"""
    __tablename__ = "filing_notes"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.filings.id", ondelete="CASCADE"), nullable=False)
    note_number = Column(String(10), nullable=False)
    note_title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    content_length = Column(Integer, nullable=False)
    word_count = Column(Integer)
    s3_uri = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class FilingRiskFactor(Base):
    """Risk factor"""
    __tablename__ = "filing_risk_factors"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.filings.id", ondelete="CASCADE"), nullable=False)
    risk_text = Column(Text, nullable=False)
    risk_category = Column(String(100))
    severity = Column(String(20))
    embedding_vector = Column(VECTOR(1536))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class FilingAccountingPolicy(Base):
    """Accounting policy"""
    __tablename__ = "filing_accounting_policies"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.filings.id", ondelete="CASCADE"), nullable=False)
    policy_type = Column(String(100))
    policy_title = Column(String(500))
    content = Column(Text, nullable=False)
    content_length = Column(Integer, nullable=False)
    s3_uri = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class FilingFullText(Base):
    """Full text content of filing"""
    __tablename__ = "filing_full_text"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    filing_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.filings.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_text = Column(Text, nullable=False)
    text_length = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    page_count = Column(Integer)
    s3_uri = Column(Text)
    processed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
