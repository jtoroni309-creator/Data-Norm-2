"""
Audit Planning & Risk Assessment Models

PCAOB Standards Coverage:
- AS 1210: Using the Work of an Auditor-Engaged Specialist
- AS 2110: Identifying and Assessing Risks of Material Misstatement
- AS 2301: The Auditor's Responses to the Risks of Material Misstatement
- AS 2305: Substantive Analytical Procedures
"""

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class RiskLevel(str, enum.Enum):
    """Risk level classification"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SIGNIFICANT = "significant"


class RiskType(str, enum.Enum):
    """Type of audit risk"""
    INHERENT = "inherent"  # Risk before considering controls
    CONTROL = "control"    # Risk that controls won't prevent/detect misstatement
    DETECTION = "detection"  # Risk that auditor won't detect misstatement
    AUDIT = "audit"        # Combined risk (IR x CR x DR)


class AccountType(str, enum.Enum):
    """Financial statement account types"""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class AssertionType(str, enum.Enum):
    """Financial statement assertions (PCAOB AS 1105)"""
    EXISTENCE = "existence"  # Assets, liabilities exist (balance sheet)
    OCCURRENCE = "occurrence"  # Transactions actually occurred (income statement)
    COMPLETENESS = "completeness"  # All transactions recorded
    RIGHTS_OBLIGATIONS = "rights_obligations"  # Entity has rights/obligations
    VALUATION_ALLOCATION = "valuation_allocation"  # Appropriate amounts
    ACCURACY = "accuracy"  # Transactions recorded at correct amounts
    CUTOFF = "cutoff"  # Transactions recorded in correct period
    CLASSIFICATION = "classification"  # Transactions recorded in proper accounts
    PRESENTATION_DISCLOSURE = "presentation_disclosure"  # Proper classification and disclosure


class ControlEffectiveness(str, enum.Enum):
    """Assessment of internal control effectiveness"""
    EFFECTIVE = "effective"
    PARTIALLY_EFFECTIVE = "partially_effective"
    INEFFECTIVE = "ineffective"
    NOT_TESTED = "not_tested"


class ProcedureType(str, enum.Enum):
    """Type of audit procedure"""
    INQUIRY = "inquiry"
    OBSERVATION = "observation"
    INSPECTION = "inspection"
    CONFIRMATION = "confirmation"
    RECALCULATION = "recalculation"
    REPERFORMANCE = "reperformance"
    ANALYTICAL = "analytical"


# ============================================================================
# AUDIT PLANNING MODELS
# ============================================================================

class AuditPlan(Base):
    """
    Overall audit plan for an engagement.

    AS 2101: Audit Planning - requires planning to include:
    - Understanding the entity
    - Assessing risks
    - Determining materiality
    - Planning audit procedures
    """
    __tablename__ = "audit_plans"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), ForeignKey("engagements.id"), nullable=False)

    # Planning information
    planning_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    planned_by_id = Column(PGUUID(as_uuid=True), nullable=False)
    reviewed_by_id = Column(PGUUID(as_uuid=True))

    # Materiality calculations
    overall_materiality = Column(Numeric(20, 2))  # Planning materiality
    performance_materiality = Column(Numeric(20, 2))  # Typically 50-75% of overall
    trivial_threshold = Column(Numeric(20, 2))  # Clearly trivial (3-5% of overall)
    materiality_basis = Column(String(100))  # e.g., "Total Assets", "Revenue", "Pre-tax Income"
    materiality_percentage = Column(Numeric(5, 2))  # Percentage used in calculation

    # Risk assessments
    overall_engagement_risk = Column(SQLEnum(RiskLevel), default=RiskLevel.MODERATE)
    fraud_risk_factors = Column(JSON)  # List of fraud risk factors identified
    going_concern_indicators = Column(JSON)  # Going concern red flags

    # Staffing and timing
    estimated_hours = Column(Integer)
    budget_amount = Column(Numeric(20, 2))
    fieldwork_start_date = Column(DateTime(timezone=True))
    fieldwork_end_date = Column(DateTime(timezone=True))
    team_members = Column(JSON)  # List of team member assignments

    # Independence and quality control
    independence_confirmed = Column(Boolean, default=False)
    quality_control_reviewer_id = Column(PGUUID(as_uuid=True))

    # Specialist requirements
    requires_specialist = Column(Boolean, default=False)
    specialist_areas = Column(JSON)  # Areas requiring specialist (valuation, IT, tax, etc.)

    # Documentation
    planning_memo = Column(Text)
    strategy_summary = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Relationships
    risk_assessments = relationship("RiskAssessment", back_populates="audit_plan", cascade="all, delete-orphan")
    audit_areas = relationship("AuditArea", back_populates="audit_plan", cascade="all, delete-orphan")
    preliminary_analytics = relationship("PreliminaryAnalytics", back_populates="audit_plan")


class RiskAssessment(Base):
    """
    Risk assessment for specific account balances or transaction classes.

    AS 2110: Requires assessment of inherent risk and control risk.
    """
    __tablename__ = "risk_assessments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_plan_id = Column(PGUUID(as_uuid=True), ForeignKey("audit_plans.id"), nullable=False)

    # Account/area being assessed
    account_name = Column(String(200), nullable=False)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    account_balance = Column(Numeric(20, 2))
    assertion = Column(SQLEnum(AssertionType), nullable=False)

    # Risk ratings
    inherent_risk = Column(SQLEnum(RiskLevel), nullable=False)
    control_risk = Column(SQLEnum(RiskLevel), nullable=False)
    detection_risk = Column(SQLEnum(RiskLevel))  # Calculated based on IR and CR
    risk_of_material_misstatement = Column(SQLEnum(RiskLevel))  # IR x CR

    # Risk factors
    risk_factors = Column(JSON)  # List of specific risk factors
    fraud_risk = Column(Boolean, default=False)
    significant_risk = Column(Boolean, default=False)  # AS 2110.71

    # Control assessment
    key_controls = Column(JSON)  # Key controls for this assertion
    control_effectiveness = Column(SQLEnum(ControlEffectiveness))
    control_testing_required = Column(Boolean, default=False)

    # Audit response
    planned_procedures = Column(JSON)  # List of planned audit procedures
    sample_size_required = Column(Integer)  # If testing required
    testing_approach = Column(String(50))  # "substantive", "controls", "dual-purpose"

    # Documentation
    rationale = Column(Text)
    risk_response_memo = Column(Text)

    # Metadata
    assessed_by_id = Column(PGUUID(as_uuid=True), nullable=False)
    assessed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Relationships
    audit_plan = relationship("AuditPlan", back_populates="risk_assessments")


class AuditArea(Base):
    """
    Specific audit area with detailed risk assessment.

    Maps to major financial statement line items or transaction cycles.
    """
    __tablename__ = "audit_areas"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_plan_id = Column(PGUUID(as_uuid=True), ForeignKey("audit_plans.id"), nullable=False)

    # Area identification
    area_name = Column(String(200), nullable=False)  # e.g., "Accounts Receivable", "Revenue"
    transaction_cycle = Column(String(100))  # e.g., "Revenue Cycle", "Expenditure Cycle"
    account_type = Column(SQLEnum(AccountType), nullable=False)

    # Balances and materiality
    current_year_balance = Column(Numeric(20, 2))
    prior_year_balance = Column(Numeric(20, 2))
    is_material = Column(Boolean, default=False)
    specific_materiality = Column(Numeric(20, 2))  # Component materiality if needed

    # Risk profile
    overall_risk = Column(SQLEnum(RiskLevel), nullable=False)
    requires_specialist = Column(Boolean, default=False)
    specialist_type = Column(String(100))  # e.g., "Valuation Specialist", "IT Auditor"

    # Planned procedures
    planned_hours = Column(Integer)
    lead_auditor_id = Column(PGUUID(as_uuid=True))
    planned_procedures = Column(JSON)  # Detailed list of procedures

    # Status
    procedures_completed = Column(Integer, default=0)
    completion_percentage = Column(Integer, default=0)

    # Documentation
    planning_notes = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Relationships
    audit_plan = relationship("AuditPlan", back_populates="audit_areas")


class PreliminaryAnalytics(Base):
    """
    Preliminary analytical procedures performed during planning.

    AS 2305: Substantive Analytical Procedures
    Performed to understand the entity and identify risks.
    """
    __tablename__ = "preliminary_analytics"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_plan_id = Column(PGUUID(as_uuid=True), ForeignKey("audit_plans.id"), nullable=False)

    # Analysis details
    analysis_name = Column(String(200), nullable=False)
    account_name = Column(String(200), nullable=False)
    analysis_type = Column(String(100))  # "ratio", "trend", "comparison", "reasonableness"

    # Data
    current_year_value = Column(Numeric(20, 2))
    prior_year_value = Column(Numeric(20, 2))
    expected_value = Column(Numeric(20, 2))  # Based on expectations
    difference = Column(Numeric(20, 2))
    difference_percentage = Column(Numeric(10, 2))

    # Thresholds
    threshold_amount = Column(Numeric(20, 2))
    threshold_percentage = Column(Numeric(10, 2))
    exceeds_threshold = Column(Boolean, default=False)

    # Analysis results
    unusual_items_identified = Column(JSON)  # List of unusual items
    risk_indicators = Column(JSON)  # Specific risk indicators from analytics
    requires_investigation = Column(Boolean, default=False)

    # Documentation
    analysis_summary = Column(Text)
    investigation_notes = Column(Text)

    # Metadata
    performed_by_id = Column(PGUUID(as_uuid=True), nullable=False)
    performed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Relationships
    audit_plan = relationship("AuditPlan", back_populates="preliminary_analytics")


class RiskMatrix(Base):
    """
    Risk matrix mapping inherent risk and control risk to audit approach.

    Helps determine the nature, timing, and extent of audit procedures.
    """
    __tablename__ = "risk_matrices"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), nullable=False)

    # Risk combination
    inherent_risk = Column(SQLEnum(RiskLevel), nullable=False)
    control_risk = Column(SQLEnum(RiskLevel), nullable=False)
    combined_risk = Column(SQLEnum(RiskLevel), nullable=False)  # RMM = IR x CR

    # Audit response
    detection_risk = Column(SQLEnum(RiskLevel), nullable=False)
    substantive_procedures_required = Column(Boolean, default=True)
    control_testing_required = Column(Boolean, default=False)
    sample_size_multiplier = Column(Numeric(3, 2))  # 1.0 = standard, 1.5 = 50% more, etc.

    # Guidance
    recommended_approach = Column(Text)
    timing_guidance = Column(String(100))  # "interim", "year-end", "both"

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)


class FraudRiskFactor(Base):
    """
    Fraud risk factors identified during planning.

    AS 2401: Consideration of Fraud in a Financial Statement Audit
    """
    __tablename__ = "fraud_risk_factors"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_plan_id = Column(PGUUID(as_uuid=True), ForeignKey("audit_plans.id"), nullable=False)

    # Fraud triangle components
    fraud_category = Column(String(50))  # "incentive", "opportunity", "rationalization"
    risk_factor = Column(String(500), nullable=False)
    description = Column(Text)

    # Impact assessment
    likelihood = Column(SQLEnum(RiskLevel))
    potential_impact = Column(SQLEnum(RiskLevel))

    # Response
    planned_response = Column(Text)
    requires_unpredictable_procedures = Column(Boolean, default=False)

    # Metadata
    identified_by_id = Column(PGUUID(as_uuid=True), nullable=False)
    identified_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
