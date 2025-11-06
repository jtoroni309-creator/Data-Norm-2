"""
Financial Analysis Service - Database Models

Models for EDGAR data, financial statements, and AI-powered audit analysis.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import relationship

from .database import Base


# Enums
class FilingType(str, Enum):
    """Type of SEC filing"""
    FORM_10K = "10-K"
    FORM_10Q = "10-Q"
    FORM_8K = "8-K"
    FORM_DEF14A = "DEF 14A"
    FORM_S1 = "S-1"
    FORM_20F = "20-F"


class FinancialStatementType(str, Enum):
    """Type of financial statement"""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    RETAINED_EARNINGS = "retained_earnings"
    COMPREHENSIVE_INCOME = "comprehensive_income"


class AuditOpinion(str, Enum):
    """Type of audit opinion"""
    UNMODIFIED = "unmodified"  # Clean opinion
    QUALIFIED = "qualified"  # Exception noted
    ADVERSE = "adverse"  # Material misstatement
    DISCLAIMER = "disclaimer"  # Unable to obtain sufficient evidence
    GOING_CONCERN = "going_concern"  # Substantial doubt about going concern


class RiskLevel(str, Enum):
    """Risk assessment level"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisStatus(str, Enum):
    """Status of financial analysis"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEWING = "reviewing"


# Models
class Company(Base):
    """
    Company information from SEC EDGAR.

    Stores CIK, ticker, and company metadata.
    """
    __tablename__ = "companies"
    __table_args__ = (
        Index("idx_company_cik", "cik"),
        Index("idx_company_ticker", "ticker"),
        {"schema": "financial_analysis"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # SEC identifiers
    cik = Column(String(10), unique=True, nullable=False)
    ticker = Column(String(10))

    # Company information
    company_name = Column(String(500), nullable=False)
    sic_code = Column(String(4))  # Standard Industrial Classification
    sic_description = Column(String(200))
    irs_number = Column(String(10))

    # Location
    state_of_incorporation = Column(String(2))
    fiscal_year_end = Column(String(4))  # MMDD format

    # Business information
    business_address = Column(JSONB)
    mailing_address = Column(JSONB)
    phone = Column(String(20))

    # Metadata
    entity_type = Column(String(50))
    category = Column(String(50))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    filings = relationship("SECFiling", back_populates="company")
    financial_statements = relationship("FinancialStatement", back_populates="company")
    analyses = relationship("FinancialAnalysis", back_populates="company")


class SECFiling(Base):
    """
    SEC filing (10-K, 10-Q, etc.) from EDGAR.

    Stores filing metadata and links to documents.
    """
    __tablename__ = "sec_filings"
    __table_args__ = (
        Index("idx_filing_company", "company_id"),
        Index("idx_filing_type", "filing_type"),
        Index("idx_filing_date", "filing_date"),
        Index("idx_filing_accession", "accession_number"),
        {"schema": "financial_analysis"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("financial_analysis.companies.id"),
        nullable=False
    )

    # Filing identification
    accession_number = Column(String(20), unique=True, nullable=False)
    filing_type = Column(SQLEnum(FilingType), nullable=False)

    # Filing details
    filing_date = Column(DateTime(timezone=True), nullable=False)
    reporting_date = Column(DateTime(timezone=True))  # Period end date
    accepted_date = Column(DateTime(timezone=True))

    # Documents
    primary_document = Column(String(200))
    primary_doc_description = Column(Text)

    # URLs
    filing_url = Column(String(500))
    document_url = Column(String(500))

    # Content
    is_xbrl = Column(Boolean, default=False)
    xbrl_url = Column(String(500))

    # Processing status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True))
    processing_error = Column(Text)

    # Storage
    raw_filing_path = Column(String(500))  # S3/Azure path
    parsed_data_path = Column(String(500))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="filings")
    financial_statements = relationship("FinancialStatement", back_populates="filing")


class FinancialStatement(Base):
    """
    Parsed financial statement data.

    Stores structured financial data from filings.
    """
    __tablename__ = "financial_statements"
    __table_args__ = (
        Index("idx_fs_company", "company_id"),
        Index("idx_fs_type", "statement_type"),
        Index("idx_fs_period", "period_end_date"),
        {"schema": "financial_analysis"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("financial_analysis.companies.id"),
        nullable=False
    )
    filing_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("financial_analysis.sec_filings.id")
    )

    # Statement identification
    statement_type = Column(SQLEnum(FinancialStatementType), nullable=False)

    # Period information
    period_end_date = Column(DateTime(timezone=True), nullable=False)
    period_start_date = Column(DateTime(timezone=True))
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer)  # 1, 2, 3, 4 or NULL for annual

    # Financial data (JSONB for flexibility)
    statement_data = Column(JSONB, nullable=False)

    # Common line items (denormalized for quick access)
    # Balance Sheet
    total_assets = Column(Numeric(20, 2))
    total_liabilities = Column(Numeric(20, 2))
    total_equity = Column(Numeric(20, 2))
    current_assets = Column(Numeric(20, 2))
    current_liabilities = Column(Numeric(20, 2))
    cash_and_equivalents = Column(Numeric(20, 2))

    # Income Statement
    revenue = Column(Numeric(20, 2))
    gross_profit = Column(Numeric(20, 2))
    operating_income = Column(Numeric(20, 2))
    net_income = Column(Numeric(20, 2))
    earnings_per_share = Column(Numeric(10, 4))

    # Cash Flow
    operating_cash_flow = Column(Numeric(20, 2))
    investing_cash_flow = Column(Numeric(20, 2))
    financing_cash_flow = Column(Numeric(20, 2))

    # Metadata
    currency = Column(String(3), default="USD")
    scale = Column(String(20))  # "units", "thousands", "millions"

    # Quality indicators
    has_auditor_report = Column(Boolean, default=False)
    is_restated = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="financial_statements")
    filing = relationship("SECFiling", back_populates="financial_statements")
    ratios = relationship("FinancialRatio", back_populates="financial_statement")


class FinancialRatio(Base):
    """
    Calculated financial ratios and metrics.

    Stores computed ratios for analysis.
    """
    __tablename__ = "financial_ratios"
    __table_args__ = (
        Index("idx_ratio_statement", "financial_statement_id"),
        {"schema": "financial_analysis"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    financial_statement_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("financial_analysis.financial_statements.id"),
        nullable=False
    )

    # Liquidity Ratios
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    cash_ratio = Column(Float)
    working_capital = Column(Numeric(20, 2))

    # Profitability Ratios
    gross_profit_margin = Column(Float)
    operating_profit_margin = Column(Float)
    net_profit_margin = Column(Float)
    return_on_assets = Column(Float)
    return_on_equity = Column(Float)

    # Leverage Ratios
    debt_to_equity = Column(Float)
    debt_to_assets = Column(Float)
    equity_multiplier = Column(Float)
    interest_coverage = Column(Float)

    # Efficiency Ratios
    asset_turnover = Column(Float)
    inventory_turnover = Column(Float)
    receivables_turnover = Column(Float)
    days_sales_outstanding = Column(Float)

    # Market Ratios
    price_to_earnings = Column(Float)
    price_to_book = Column(Float)
    earnings_yield = Column(Float)

    # Cash Flow Ratios
    operating_cash_flow_ratio = Column(Float)
    free_cash_flow = Column(Numeric(20, 2))
    cash_flow_to_debt = Column(Float)

    # Growth Metrics
    revenue_growth = Column(Float)
    earnings_growth = Column(Float)
    asset_growth = Column(Float)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    financial_statement = relationship("FinancialStatement", back_populates="ratios")


class FinancialAnalysis(Base):
    """
    AI-powered financial analysis and audit opinion.

    Stores comprehensive analysis results with AI recommendations.
    """
    __tablename__ = "financial_analyses"
    __table_args__ = (
        Index("idx_analysis_company", "company_id"),
        Index("idx_analysis_status", "status"),
        Index("idx_analysis_created", "created_at"),
        {"schema": "financial_analysis"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("financial_analysis.companies.id"),
        nullable=False
    )
    engagement_id = Column(PGUUID(as_uuid=True))  # Link to audit engagement

    # Analysis metadata
    analysis_name = Column(String(255), nullable=False)
    analysis_type = Column(String(50))  # "annual", "quarterly", "interim"
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)

    # Period covered
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    fiscal_year = Column(Integer)

    # Financial Summary
    financial_summary = Column(JSONB)  # Key metrics summary

    # Risk Assessment
    overall_risk_level = Column(SQLEnum(RiskLevel))
    risk_factors = Column(JSONB)  # List of identified risks
    risk_score = Column(Float)  # 0.0 to 1.0

    # Materiality Assessment
    materiality_threshold = Column(Numeric(20, 2))
    performance_materiality = Column(Numeric(20, 2))
    trivial_threshold = Column(Numeric(20, 2))
    materiality_basis = Column(String(100))  # "revenue", "assets", "equity"

    # Going Concern
    going_concern_risk = Column(SQLEnum(RiskLevel))
    going_concern_indicators = Column(JSONB)
    going_concern_assessment = Column(Text)

    # Analytical Procedures
    ratio_analysis = Column(JSONB)
    trend_analysis = Column(JSONB)
    benchmarking = Column(JSONB)
    unusual_items = Column(JSONB)

    # AI-Generated Insights
    key_findings = Column(JSONB)  # List of important findings
    red_flags = Column(JSONB)  # Warning signs detected
    positive_indicators = Column(JSONB)

    # Audit Opinion Recommendation
    recommended_opinion = Column(SQLEnum(AuditOpinion))
    opinion_confidence = Column(Float)  # 0.0 to 1.0
    opinion_rationale = Column(Text)
    basis_for_opinion = Column(Text)

    # Key Audit Matters
    key_audit_matters = Column(JSONB)

    # Management Discussion
    md_and_a_summary = Column(Text)
    md_and_a_concerns = Column(JSONB)

    # Comparatives
    prior_period_comparison = Column(JSONB)
    industry_comparison = Column(JSONB)

    # AI Model Information
    model_version = Column(String(50))
    model_confidence = Column(Float)
    analysis_timestamp = Column(DateTime(timezone=True))

    # Review and Approval
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    approved_by = Column(PGUUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))

    # Final Report
    final_opinion = Column(SQLEnum(AuditOpinion))
    final_report_path = Column(String(500))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    company = relationship("Company", back_populates="analyses")
    audit_tests = relationship("AuditTest", back_populates="analysis")


class AuditTest(Base):
    """
    Individual audit test or procedure performed by AI.

    Tracks specific tests and their results.
    """
    __tablename__ = "audit_tests"
    __table_args__ = (
        Index("idx_test_analysis", "analysis_id"),
        {"schema": "financial_analysis"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    analysis_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("financial_analysis.financial_analyses.id"),
        nullable=False
    )

    # Test details
    test_name = Column(String(255), nullable=False)
    test_type = Column(String(100))  # "substantive", "analytical", "control"
    test_objective = Column(Text)

    # Assertions tested
    assertions = Column(JSONB)  # existence, completeness, accuracy, etc.

    # Procedure
    procedure_description = Column(Text)
    sample_size = Column(Integer)
    population_size = Column(Integer)

    # Results
    test_result = Column(String(50))  # "passed", "failed", "inconclusive"
    exceptions_found = Column(Integer, default=0)
    exception_details = Column(JSONB)

    # Conclusion
    test_conclusion = Column(Text)
    impact_on_opinion = Column(String(50))  # "none", "minor", "significant", "material"

    # Evidence
    evidence_obtained = Column(JSONB)
    evidence_path = Column(String(500))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    performed_at = Column(DateTime(timezone=True))

    # Relationships
    analysis = relationship("FinancialAnalysis", back_populates="audit_tests")


class TrainingDataset(Base):
    """
    Training dataset for AI model.

    Stores labeled financial statements for model training.
    """
    __tablename__ = "training_datasets"
    __table_args__ = (
        Index("idx_training_company", "company_id"),
        {"schema": "financial_analysis"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("financial_analysis.companies.id")
    )

    # Data
    features = Column(JSONB, nullable=False)  # Input features
    label = Column(SQLEnum(AuditOpinion), nullable=False)  # Target label

    # Context
    fiscal_year = Column(Integer)
    industry = Column(String(100))
    company_size = Column(String(50))  # "small", "medium", "large"

    # Quality
    is_verified = Column(Boolean, default=False)
    verified_by = Column(PGUUID(as_uuid=True))
    confidence_score = Column(Float)

    # Usage
    used_in_training = Column(Boolean, default=False)
    training_run_id = Column(String(100))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company = relationship("Company")


class ModelVersion(Base):
    """
    AI model version tracking.

    Stores model versions and performance metrics.
    """
    __tablename__ = "model_versions"
    __table_args__ = (
        Index("idx_model_active", "is_active"),
        {"schema": "financial_analysis"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Model identification
    model_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(50))  # "classification", "regression", "llm"

    # Model artifacts
    model_path = Column(String(500))  # S3/Azure path
    model_hash = Column(String(64))  # SHA256

    # Configuration
    hyperparameters = Column(JSONB)
    training_config = Column(JSONB)
    feature_names = Column(JSONB)

    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_roc = Column(Float)

    # Confusion matrix (for classification)
    confusion_matrix = Column(JSONB)

    # Training details
    training_dataset_size = Column(Integer)
    validation_dataset_size = Column(Integer)
    training_duration_seconds = Column(Integer)
    trained_at = Column(DateTime(timezone=True))

    # Deployment
    is_active = Column(Boolean, default=False)
    deployed_at = Column(DateTime(timezone=True))
    prediction_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Metadata
    description = Column(Text)
    change_log = Column(Text)


class AnalysisInsight(Base):
    """
    Individual insight generated by AI.

    Granular insights that contribute to overall analysis.
    """
    __tablename__ = "analysis_insights"
    __table_args__ = (
        Index("idx_insight_analysis", "analysis_id"),
        Index("idx_insight_type", "insight_type"),
        {"schema": "financial_analysis"}
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    analysis_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("financial_analysis.financial_analyses.id"),
        nullable=False
    )

    # Insight details
    insight_type = Column(String(100), nullable=False)  # "ratio_analysis", "trend", "red_flag"
    category = Column(String(100))  # "liquidity", "profitability", "solvency"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Severity
    severity = Column(SQLEnum(RiskLevel))
    impact_score = Column(Float)  # 0.0 to 1.0

    # Supporting data
    supporting_data = Column(JSONB)
    calculations = Column(JSONB)

    # Recommendations
    recommendation = Column(Text)
    action_required = Column(Boolean, default=False)

    # AI metadata
    confidence = Column(Float)  # 0.0 to 1.0
    generated_by = Column(String(100))  # Model name

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
