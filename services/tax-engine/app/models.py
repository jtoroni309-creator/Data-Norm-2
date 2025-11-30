"""
Tax Engine Database Models

Comprehensive models for tax calculations, rules, and all form types.
Supports Individual, Corporate, Partnership, S-Corp, Trust, Estate, Non-profit.
"""
from sqlalchemy import (
    Column, String, Integer, Text, Boolean, DateTime, Date,
    ForeignKey, Index, Numeric, JSON, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from enum import Enum
from decimal import Decimal

Base = declarative_base()


# ========================================
# Enumerations
# ========================================

class TaxFormType(str, Enum):
    """All supported tax form types"""
    # Individual
    FORM_1040 = "1040"
    FORM_1040_SR = "1040-SR"  # Seniors
    FORM_1040_NR = "1040-NR"  # Non-resident
    FORM_1040_X = "1040-X"    # Amended

    # Corporate
    FORM_1120 = "1120"        # C-Corporation
    FORM_1120_S = "1120-S"    # S-Corporation
    FORM_1120_F = "1120-F"    # Foreign Corporation
    FORM_1120_H = "1120-H"    # HOA
    FORM_1120_REIT = "1120-REIT"  # Real Estate Investment Trust

    # Partnership
    FORM_1065 = "1065"        # Partnership

    # Trust/Estate
    FORM_1041 = "1041"        # Trust/Estate

    # Non-profit
    FORM_990 = "990"          # Non-profit
    FORM_990_EZ = "990-EZ"    # Small Non-profit
    FORM_990_PF = "990-PF"    # Private Foundation
    FORM_990_N = "990-N"      # e-Postcard

    # Employment
    FORM_941 = "941"          # Quarterly Employment
    FORM_940 = "940"          # Annual Unemployment
    FORM_943 = "943"          # Agricultural Employment
    FORM_944 = "944"          # Annual Employment (small)
    FORM_945 = "945"          # Annual Withholding

    # Information Returns
    FORM_1099_MISC = "1099-MISC"
    FORM_1099_NEC = "1099-NEC"
    FORM_1099_INT = "1099-INT"
    FORM_1099_DIV = "1099-DIV"
    FORM_1099_B = "1099-B"
    FORM_1099_R = "1099-R"
    FORM_1099_K = "1099-K"
    FORM_W2 = "W-2"
    FORM_W2G = "W-2G"
    FORM_K1_1065 = "K-1 (1065)"
    FORM_K1_1120S = "K-1 (1120-S)"
    FORM_K1_1041 = "K-1 (1041)"


class FilingStatus(str, Enum):
    """Individual filing statuses"""
    SINGLE = "single"
    MARRIED_FILING_JOINTLY = "married_filing_jointly"
    MARRIED_FILING_SEPARATELY = "married_filing_separately"
    HEAD_OF_HOUSEHOLD = "head_of_household"
    QUALIFYING_SURVIVING_SPOUSE = "qualifying_surviving_spouse"


class TaxReturnStatus(str, Enum):
    """Tax return processing status"""
    DRAFT = "draft"
    DATA_ENTRY = "data_entry"
    OCR_PROCESSING = "ocr_processing"
    REVIEW = "review"
    CALCULATING = "calculating"
    VALIDATION = "validation"
    READY_TO_FILE = "ready_to_file"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    AMENDED = "amended"
    EXTENSION_FILED = "extension_filed"


class EntityType(str, Enum):
    """Business entity types"""
    INDIVIDUAL = "individual"
    C_CORPORATION = "c_corporation"
    S_CORPORATION = "s_corporation"
    PARTNERSHIP = "partnership"
    LLC_SINGLE = "llc_single_member"
    LLC_MULTI = "llc_multi_member"
    TRUST = "trust"
    ESTATE = "estate"
    NON_PROFIT = "non_profit"
    PRIVATE_FOUNDATION = "private_foundation"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"


class JurisdictionType(str, Enum):
    """Tax jurisdiction types"""
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"
    CITY = "city"
    COUNTY = "county"


# ========================================
# Core Tax Return Models
# ========================================

class TaxReturn(Base):
    """
    Master tax return record

    Supports all entity types and form types with comprehensive
    tracking of status, calculations, and e-filing.
    """
    __tablename__ = "tax_returns"
    __table_args__ = (
        Index("idx_tax_returns_firm_client", "firm_id", "client_id"),
        Index("idx_tax_returns_tax_year", "tax_year"),
        Index("idx_tax_returns_form_type", "form_type"),
        Index("idx_tax_returns_status", "status"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    firm_id = Column(PGUUID(as_uuid=True), nullable=False)
    client_id = Column(PGUUID(as_uuid=True), nullable=False)
    engagement_id = Column(PGUUID(as_uuid=True))  # Link to engagement if applicable

    # Return identification
    tax_year = Column(Integer, nullable=False)
    form_type = Column(String(50), nullable=False)  # 1040, 1120, 1065, etc.
    entity_type = Column(String(50), nullable=False)
    return_name = Column(Text)  # Display name

    # Taxpayer information
    taxpayer_name = Column(Text, nullable=False)
    taxpayer_ssn_ein = Column(String(20))  # Encrypted
    filing_status = Column(String(50))  # For individuals

    # Fiscal period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    is_fiscal_year = Column(Boolean, default=False)
    is_short_period = Column(Boolean, default=False)

    # Status tracking
    status = Column(String(50), default="draft")
    status_history = Column(JSONB, default=list)

    # Calculation results (cached)
    total_income = Column(Numeric(15, 2), default=0)
    total_deductions = Column(Numeric(15, 2), default=0)
    taxable_income = Column(Numeric(15, 2), default=0)
    total_tax = Column(Numeric(15, 2), default=0)
    total_credits = Column(Numeric(15, 2), default=0)
    total_payments = Column(Numeric(15, 2), default=0)
    refund_amount = Column(Numeric(15, 2), default=0)
    amount_owed = Column(Numeric(15, 2), default=0)

    # E-filing
    efile_status = Column(String(50))
    efile_submission_id = Column(String(100))
    efile_submitted_at = Column(DateTime(timezone=True))
    efile_accepted_at = Column(DateTime(timezone=True))
    efile_rejection_codes = Column(JSONB)

    # Validation
    validation_errors = Column(JSONB, default=list)
    validation_warnings = Column(JSONB, default=list)
    last_validated_at = Column(DateTime(timezone=True))

    # Prior year comparison
    prior_year_return_id = Column(PGUUID(as_uuid=True))
    prior_year_comparison = Column(JSONB)

    # Assignment and workflow
    preparer_id = Column(PGUUID(as_uuid=True))
    reviewer_id = Column(PGUUID(as_uuid=True))
    due_date = Column(Date)
    extended_due_date = Column(Date)

    # Metadata
    created_by = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    locked_at = Column(DateTime(timezone=True))
    locked_by = Column(PGUUID(as_uuid=True))

    # Relationships
    form_data = relationship("TaxFormData", back_populates="tax_return", cascade="all, delete-orphan")
    schedules = relationship("TaxSchedule", back_populates="tax_return", cascade="all, delete-orphan")
    calculations = relationship("TaxCalculationResult", back_populates="tax_return", cascade="all, delete-orphan")
    documents = relationship("TaxDocument", back_populates="tax_return", cascade="all, delete-orphan")
    state_returns = relationship("StateTaxReturn", back_populates="federal_return", cascade="all, delete-orphan")


class TaxFormData(Base):
    """
    Form-specific data storage

    Each form type has its own data schema stored as JSONB
    with validation rules.
    """
    __tablename__ = "tax_form_data"
    __table_args__ = (
        Index("idx_tax_form_data_return", "tax_return_id"),
        Index("idx_tax_form_data_form", "form_code"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_return_id = Column(PGUUID(as_uuid=True), ForeignKey("tax.tax_returns.id", ondelete="CASCADE"), nullable=False)

    form_code = Column(String(50), nullable=False)  # 1040, Schedule A, etc.
    form_version = Column(String(20))  # 2024v1.0

    # Form data as flexible JSON
    data = Column(JSONB, nullable=False, default=dict)

    # Line-by-line calculated values
    calculated_lines = Column(JSONB, default=dict)

    # Validation
    is_complete = Column(Boolean, default=False)
    completion_percentage = Column(Integer, default=0)
    validation_errors = Column(JSONB, default=list)

    # OCR source tracking
    ocr_source_documents = Column(JSONB, default=list)  # List of document IDs
    ocr_confidence_scores = Column(JSONB, default=dict)  # Line -> confidence

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    tax_return = relationship("TaxReturn", back_populates="form_data")


class TaxSchedule(Base):
    """
    Schedule and attachment data

    Handles Schedule A, B, C, D, E, SE, K-1s, etc.
    """
    __tablename__ = "tax_schedules"
    __table_args__ = (
        Index("idx_tax_schedules_return", "tax_return_id"),
        Index("idx_tax_schedules_type", "schedule_type"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_return_id = Column(PGUUID(as_uuid=True), ForeignKey("tax.tax_returns.id", ondelete="CASCADE"), nullable=False)

    schedule_type = Column(String(50), nullable=False)  # A, B, C, D, E, SE, K-1, etc.
    schedule_name = Column(Text)  # Human readable name
    schedule_number = Column(Integer, default=1)  # For multiple instances (e.g., multiple Schedule C)

    # Schedule data
    data = Column(JSONB, nullable=False, default=dict)
    calculated_lines = Column(JSONB, default=dict)

    # Totals that flow to main form
    schedule_total = Column(Numeric(15, 2), default=0)
    flow_to_line = Column(String(50))  # e.g., "1040.line7"

    # Completion
    is_complete = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    tax_return = relationship("TaxReturn", back_populates="schedules")


# ========================================
# State Tax Models
# ========================================

class StateTaxReturn(Base):
    """
    State tax return linked to federal return
    """
    __tablename__ = "state_tax_returns"
    __table_args__ = (
        Index("idx_state_returns_federal", "federal_return_id"),
        Index("idx_state_returns_state", "state_code"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    federal_return_id = Column(PGUUID(as_uuid=True), ForeignKey("tax.tax_returns.id", ondelete="CASCADE"), nullable=False)

    state_code = Column(String(2), nullable=False)  # CA, NY, TX, etc.
    state_form = Column(String(50))  # CA 540, NY IT-201, etc.

    # Residency
    residency_status = Column(String(50))  # resident, nonresident, part_year
    residency_start_date = Column(Date)
    residency_end_date = Column(Date)

    # State-specific data
    state_agi = Column(Numeric(15, 2), default=0)
    state_taxable_income = Column(Numeric(15, 2), default=0)
    state_tax = Column(Numeric(15, 2), default=0)
    state_credits = Column(Numeric(15, 2), default=0)
    state_payments = Column(Numeric(15, 2), default=0)
    state_refund = Column(Numeric(15, 2), default=0)
    state_owed = Column(Numeric(15, 2), default=0)

    # Form data
    form_data = Column(JSONB, default=dict)

    # Status
    status = Column(String(50), default="draft")
    efile_status = Column(String(50))

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    federal_return = relationship("TaxReturn", back_populates="state_returns")


# ========================================
# Tax Rules and Brackets
# ========================================

class TaxBracket(Base):
    """
    Tax brackets for all years and filing statuses
    """
    __tablename__ = "tax_brackets"
    __table_args__ = (
        Index("idx_tax_brackets_year_status", "tax_year", "filing_status"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_year = Column(Integer, nullable=False)
    filing_status = Column(String(50), nullable=False)  # single, mfj, mfs, hoh, qss
    bracket_type = Column(String(50), default="ordinary")  # ordinary, capital_gains, amt

    # Bracket ranges (array of thresholds and rates)
    brackets = Column(JSONB, nullable=False)
    # Format: [{"min": 0, "max": 11600, "rate": 0.10}, {"min": 11600, "max": 47150, "rate": 0.12}, ...]

    # Metadata
    effective_date = Column(Date)
    source = Column(Text)  # IRS publication reference
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class TaxRule(Base):
    """
    Tax rules, thresholds, and limits
    """
    __tablename__ = "tax_rules"
    __table_args__ = (
        Index("idx_tax_rules_year_type", "tax_year", "rule_type"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_year = Column(Integer, nullable=False)
    rule_type = Column(String(100), nullable=False)
    rule_code = Column(String(100), nullable=False)

    # Rule values
    value = Column(Numeric(15, 2))
    values = Column(JSONB)  # For complex rules with multiple values

    # Applicability
    form_types = Column(JSONB)  # Which forms this applies to
    filing_statuses = Column(JSONB)  # Which filing statuses

    # Phase-out rules
    phase_out_start = Column(Numeric(15, 2))
    phase_out_end = Column(Numeric(15, 2))
    phase_out_rate = Column(Numeric(5, 4))

    # Description
    description = Column(Text)
    irs_citation = Column(String(200))  # e.g., "IRC §151(d)(3)"

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


# ========================================
# Calculation Results and Explainability
# ========================================

class TaxCalculationResult(Base):
    """
    Stores calculation results with full audit trail
    """
    __tablename__ = "tax_calculation_results"
    __table_args__ = (
        Index("idx_calc_results_return", "tax_return_id"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_return_id = Column(PGUUID(as_uuid=True), ForeignKey("tax.tax_returns.id", ondelete="CASCADE"), nullable=False)

    calculation_version = Column(Integer, default=1)
    calculated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Summary results
    gross_income = Column(Numeric(15, 2), default=0)
    adjustments = Column(Numeric(15, 2), default=0)
    agi = Column(Numeric(15, 2), default=0)
    deductions = Column(Numeric(15, 2), default=0)
    qbi_deduction = Column(Numeric(15, 2), default=0)
    taxable_income = Column(Numeric(15, 2), default=0)

    # Tax calculations
    regular_tax = Column(Numeric(15, 2), default=0)
    amt = Column(Numeric(15, 2), default=0)
    niit = Column(Numeric(15, 2), default=0)
    se_tax = Column(Numeric(15, 2), default=0)
    other_taxes = Column(Numeric(15, 2), default=0)
    total_tax = Column(Numeric(15, 2), default=0)

    # Credits
    nonrefundable_credits = Column(Numeric(15, 2), default=0)
    refundable_credits = Column(Numeric(15, 2), default=0)
    total_credits = Column(Numeric(15, 2), default=0)

    # Payments
    withholding = Column(Numeric(15, 2), default=0)
    estimated_payments = Column(Numeric(15, 2), default=0)
    prior_year_overpayment = Column(Numeric(15, 2), default=0)
    other_payments = Column(Numeric(15, 2), default=0)
    total_payments = Column(Numeric(15, 2), default=0)

    # Final result
    tax_after_credits = Column(Numeric(15, 2), default=0)
    refund_or_owed = Column(Numeric(15, 2), default=0)
    is_refund = Column(Boolean, default=False)

    # Detailed breakdown by line
    line_calculations = Column(JSONB, default=dict)

    # Calculation graph for explainability
    calculation_graph = Column(JSONB, default=dict)

    # State summary
    state_calculations = Column(JSONB, default=dict)

    # Metadata
    engine_version = Column(String(20))
    rules_version = Column(String(20))

    # Relationships
    tax_return = relationship("TaxReturn", back_populates="calculations")


class TaxLineExplanation(Base):
    """
    Line-by-line explanations with provenance
    """
    __tablename__ = "tax_line_explanations"
    __table_args__ = (
        Index("idx_line_explanations_calc", "calculation_id"),
        Index("idx_line_explanations_line", "line_reference"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    calculation_id = Column(PGUUID(as_uuid=True), ForeignKey("tax.tax_calculation_results.id", ondelete="CASCADE"), nullable=False)

    line_reference = Column(String(100), nullable=False)  # e.g., "1040.line15"
    line_description = Column(Text)

    # Calculated value
    calculated_value = Column(Numeric(15, 2), default=0)

    # Explanation
    formula = Column(Text)  # e.g., "Line 15 = Line 11 - Line 14"
    explanation = Column(Text)  # Natural language
    irs_instructions = Column(Text)  # From IRS instructions

    # Source inputs
    input_lines = Column(JSONB, default=list)  # Lines that feed into this
    input_values = Column(JSONB, default=dict)  # Actual values used

    # Rules applied
    rules_applied = Column(JSONB, default=list)  # List of rule IDs/codes

    # Source documents
    source_documents = Column(JSONB, default=list)  # Document IDs that provided data

    # Confidence (for OCR-derived values)
    confidence_score = Column(Numeric(5, 4))
    needs_review = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


# ========================================
# Document Management
# ========================================

class TaxDocument(Base):
    """
    Source documents for tax return
    """
    __tablename__ = "tax_documents"
    __table_args__ = (
        Index("idx_tax_documents_return", "tax_return_id"),
        Index("idx_tax_documents_type", "document_type"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_return_id = Column(PGUUID(as_uuid=True), ForeignKey("tax.tax_returns.id", ondelete="CASCADE"), nullable=False)

    # Document info
    document_type = Column(String(50), nullable=False)  # W-2, 1099-INT, etc.
    document_name = Column(Text)
    issuer_name = Column(Text)  # Employer name, payer name
    issuer_ein = Column(String(20))

    # Storage
    storage_path = Column(Text)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    page_count = Column(Integer, default=1)

    # OCR status
    ocr_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    ocr_completed_at = Column(DateTime(timezone=True))
    ocr_confidence = Column(Numeric(5, 4))

    # Extracted data
    extracted_data = Column(JSONB, default=dict)
    extraction_version = Column(String(20))

    # Review
    needs_review = Column(Boolean, default=False)
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))

    # Metadata
    uploaded_by = Column(PGUUID(as_uuid=True))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tax_return = relationship("TaxReturn", back_populates="documents")


# ========================================
# E-File Models
# ========================================

class EFileSubmission(Base):
    """
    E-file submission tracking
    """
    __tablename__ = "efile_submissions"
    __table_args__ = (
        Index("idx_efile_return", "tax_return_id"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_return_id = Column(PGUUID(as_uuid=True), ForeignKey("tax.tax_returns.id", ondelete="CASCADE"), nullable=False)

    # Submission info
    submission_id = Column(String(100))  # IRS submission ID
    transmission_id = Column(String(100))

    # XML data
    mef_xml = Column(Text)  # Generated MeF XML
    xml_hash = Column(String(64))  # SHA-256 hash

    # Status tracking
    status = Column(String(50), default="pending")
    submitted_at = Column(DateTime(timezone=True))
    acknowledged_at = Column(DateTime(timezone=True))
    accepted_at = Column(DateTime(timezone=True))
    rejected_at = Column(DateTime(timezone=True))

    # Response
    irs_response = Column(JSONB)
    rejection_codes = Column(JSONB, default=list)

    # Retry tracking
    attempt_number = Column(Integer, default=1)
    last_error = Column(Text)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


# ========================================
# Form Templates and Schemas
# ========================================

class FormSchema(Base):
    """
    Form schema definitions for all supported forms
    """
    __tablename__ = "form_schemas"
    __table_args__ = (
        Index("idx_form_schemas_code_year", "form_code", "tax_year"),
        {"schema": "tax"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    form_code = Column(String(50), nullable=False)  # 1040, Schedule A, etc.
    tax_year = Column(Integer, nullable=False)
    form_name = Column(Text, nullable=False)  # "U.S. Individual Income Tax Return"

    # Schema definition
    schema_version = Column(String(20))
    line_definitions = Column(JSONB, nullable=False)  # Array of line definitions
    # Format: [{"line": "1", "label": "Total wages...", "type": "currency", "source": "W-2.box1", ...}]

    # Calculation rules
    calculation_rules = Column(JSONB, default=list)
    # Format: [{"output_line": "15", "formula": "line11 - line14", "dependencies": ["11", "14"]}]

    # Validation rules
    validation_rules = Column(JSONB, default=list)
    # Format: [{"rule_id": "R001", "type": "required", "line": "1", "message": "...", "severity": "error"}]

    # E-file mapping
    mef_mapping = Column(JSONB)  # Maps lines to MeF XML elements

    # PDF template info
    pdf_template_path = Column(Text)
    pdf_field_mapping = Column(JSONB)  # Maps lines to PDF form fields

    # Metadata
    effective_date = Column(Date)
    irs_revision_date = Column(Date)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
