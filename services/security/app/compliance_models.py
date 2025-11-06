"""
SOC 2 Compliance Tracking Models

Tracks compliance with SOC 2 Trust Service Criteria:
- CC (Common Criteria)
- A (Availability)
- C (Confidentiality)
- P (Processing Integrity)
- PI (Privacy)

Models track:
- Control implementations
- Evidence collection
- Control testing
- Compliance status
- Audit readiness
"""

import enum
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
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

class TrustServiceCategory(str, enum.Enum):
    """SOC 2 Trust Service Categories"""
    COMMON_CRITERIA = "cc"  # Common Criteria (applies to all)
    AVAILABILITY = "a"  # System availability
    CONFIDENTIALITY = "c"  # Data confidentiality
    PROCESSING_INTEGRITY = "pi"  # Processing integrity
    PRIVACY = "p"  # Privacy


class ControlStatus(str, enum.Enum):
    """Control implementation status"""
    NOT_IMPLEMENTED = "not_implemented"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    TESTED = "tested"
    EFFECTIVE = "effective"
    INEFFECTIVE = "ineffective"


class ControlFrequency(str, enum.Enum):
    """How often control operates"""
    CONTINUOUS = "continuous"  # Automated/always on
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    AD_HOC = "ad_hoc"  # As needed


class EvidenceType(str, enum.Enum):
    """Types of compliance evidence"""
    SCREENSHOT = "screenshot"
    LOG_FILE = "log_file"
    REPORT = "report"
    DOCUMENT = "document"
    VIDEO = "video"
    ATTESTATION = "attestation"
    SYSTEM_GENERATED = "system_generated"


class TestResult(str, enum.Enum):
    """Control testing results"""
    PASSED = "passed"
    FAILED = "failed"
    NOT_TESTED = "not_tested"
    NOT_APPLICABLE = "not_applicable"


# ============================================================================
# COMPLIANCE MODELS
# ============================================================================

class SOC2Control(Base):
    """
    SOC 2 control definition and implementation tracking.

    Maps to specific SOC 2 Trust Service Criteria.
    """
    __tablename__ = "soc2_controls"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Control identification
    control_id = Column(String(20), nullable=False, unique=True)  # e.g., "CC6.1", "A1.2"
    category = Column(SQLEnum(TrustServiceCategory), nullable=False)
    control_name = Column(String(200), nullable=False)
    control_description = Column(Text, nullable=False)

    # Control objective
    control_objective = Column(Text, nullable=False)
    risk_addressed = Column(Text)  # What risk does this control mitigate?

    # Implementation details
    implementation_description = Column(Text)
    responsible_party = Column(String(200))  # Role/person responsible
    status = Column(SQLEnum(ControlStatus), default=ControlStatus.NOT_IMPLEMENTED)
    frequency = Column(SQLEnum(ControlFrequency), nullable=False)

    # Automation
    is_automated = Column(Boolean, default=False)
    automation_tool = Column(String(200))  # Tool/system that implements control

    # Testing
    testing_procedure = Column(Text)  # How to test this control
    last_tested_at = Column(DateTime(timezone=True))
    last_test_result = Column(SQLEnum(TestResult), default=TestResult.NOT_TESTED)
    test_notes = Column(Text)

    # Effectiveness
    is_effective = Column(Boolean, default=False)
    effectiveness_notes = Column(Text)
    exceptions_identified = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(PGUUID(as_uuid=True))
    updated_by_id = Column(PGUUID(as_uuid=True))

    # Relationships
    evidence = relationship("ComplianceEvidence", back_populates="control", cascade="all, delete-orphan")
    tests = relationship("ControlTest", back_populates="control", cascade="all, delete-orphan")


class ComplianceEvidence(Base):
    """
    Evidence of control implementation and effectiveness.

    SOC 2 auditors require documented evidence for all controls.
    """
    __tablename__ = "compliance_evidence"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    control_id = Column(PGUUID(as_uuid=True), ForeignKey("soc2_controls.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Evidence details
    evidence_type = Column(SQLEnum(EvidenceType), nullable=False)
    evidence_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=False)

    # Storage
    file_path = Column(String(500))  # Path to stored evidence file
    file_url = Column(String(500))  # URL to access evidence
    file_hash = Column(String(64))  # SHA-256 hash for integrity

    # Metadata
    collected_by_id = Column(PGUUID(as_uuid=True), nullable=False)
    collected_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    tags = Column(JSON)  # Tags for categorization
    notes = Column(Text)

    # Relationships
    control = relationship("SOC2Control", back_populates="evidence")


class ControlTest(Base):
    """
    Record of control testing (for auditor review).

    Documents testing methodology, sample selection, and results.
    """
    __tablename__ = "control_tests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    control_id = Column(PGUUID(as_uuid=True), ForeignKey("soc2_controls.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Test details
    test_date = Column(DateTime(timezone=True), nullable=False)
    test_period_start = Column(DateTime(timezone=True))
    test_period_end = Column(DateTime(timezone=True))
    testing_procedure = Column(Text, nullable=False)

    # Sample selection
    population_size = Column(Integer)  # Total items in population
    sample_size = Column(Integer)  # Items tested
    sampling_method = Column(String(100))  # "random", "judgmental", "all"
    sample_selection_criteria = Column(Text)

    # Results
    test_result = Column(SQLEnum(TestResult), nullable=False)
    items_tested = Column(Integer)
    exceptions_found = Column(Integer, default=0)
    exception_details = Column(JSON)  # Details of any exceptions

    # Conclusion
    conclusion = Column(Text, nullable=False)
    recommendations = Column(Text)

    # Tester information
    tested_by_id = Column(PGUUID(as_uuid=True), nullable=False)
    reviewed_by_id = Column(PGUUID(as_uuid=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    control = relationship("SOC2Control", back_populates="tests")


class CompliancePeriod(Base):
    """
    SOC 2 audit period tracking.

    Tracks compliance status over specific time periods (typically 6-12 months).
    """
    __tablename__ = "compliance_periods"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Period details
    period_name = Column(String(200), nullable=False)  # e.g., "2025 Annual SOC 2"
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    # Report type
    report_type = Column(String(20), nullable=False)  # "Type I" or "Type II"
    trust_service_categories = Column(JSON)  # List of categories (CC, A, C, PI, P)

    # Status
    is_active = Column(Boolean, default=True)
    audit_firm = Column(String(200))  # External auditor
    audit_partner = Column(String(200))
    audit_start_date = Column(DateTime(timezone=True))
    audit_completion_date = Column(DateTime(timezone=True))

    # Results
    total_controls = Column(Integer, default=0)
    controls_implemented = Column(Integer, default=0)
    controls_tested = Column(Integer, default=0)
    controls_effective = Column(Integer, default=0)
    exceptions_identified = Column(Integer, default=0)

    # Opinion
    audit_opinion = Column(String(50))  # "Unqualified", "Qualified", "Adverse", "Disclaimer"
    opinion_date = Column(DateTime(timezone=True))
    report_url = Column(String(500))

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class SecurityIncident(Base):
    """
    Security incident tracking for SOC 2 compliance.

    Must document all security incidents and responses.
    """
    __tablename__ = "security_incidents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Incident details
    incident_date = Column(DateTime(timezone=True), nullable=False)
    discovered_date = Column(DateTime(timezone=True), nullable=False)
    incident_type = Column(String(100), nullable=False)  # "data_breach", "unauthorized_access", etc.
    severity = Column(String(20), nullable=False)  # "low", "medium", "high", "critical"

    # Description
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    affected_systems = Column(JSON)  # List of affected systems
    affected_data = Column(JSON)  # Types of data affected

    # Impact assessment
    customer_impact = Column(Boolean, default=False)
    customers_affected = Column(Integer, default=0)
    data_exfiltrated = Column(Boolean, default=False)
    estimated_cost = Column(Integer)  # Dollar amount

    # Response
    response_actions = Column(JSON)  # List of actions taken
    containment_date = Column(DateTime(timezone=True))
    resolution_date = Column(DateTime(timezone=True))
    root_cause = Column(Text)
    lessons_learned = Column(Text)

    # Reporting
    reported_to_authorities = Column(Boolean, default=False)
    reporting_details = Column(JSON)
    customer_notification_sent = Column(Boolean, default=False)
    notification_date = Column(DateTime(timezone=True))

    # Status
    status = Column(String(50), default="open")  # "open", "investigating", "contained", "resolved", "closed"

    # Responsible parties
    incident_manager_id = Column(PGUUID(as_uuid=True))
    discovered_by_id = Column(PGUUID(as_uuid=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class VulnerabilityAssessment(Base):
    """
    Vulnerability assessment tracking.

    SOC 2 requires regular vulnerability assessments and remediation.
    """
    __tablename__ = "vulnerability_assessments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Assessment details
    assessment_date = Column(DateTime(timezone=True), nullable=False)
    assessment_type = Column(String(100), nullable=False)  # "automated_scan", "penetration_test", "code_review"
    tool_used = Column(String(200))
    scope = Column(Text)  # What was assessed

    # Findings
    vulnerabilities_found = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)

    # Results
    report_url = Column(String(500))
    findings_summary = Column(JSON)  # List of key findings

    # Remediation
    remediation_deadline = Column(DateTime(timezone=True))
    remediation_completed = Column(Boolean, default=False)
    remediation_date = Column(DateTime(timezone=True))
    remediation_notes = Column(Text)

    # Performed by
    performed_by = Column(String(200))  # Internal team or external vendor
    assessor_id = Column(PGUUID(as_uuid=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class AccessReview(Base):
    """
    Periodic access review tracking.

    SOC 2 requires regular review of user access rights.
    """
    __tablename__ = "access_reviews"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Review details
    review_date = Column(DateTime(timezone=True), nullable=False)
    review_period_start = Column(DateTime(timezone=True), nullable=False)
    review_period_end = Column(DateTime(timezone=True), nullable=False)
    review_type = Column(String(100))  # "user_access", "admin_access", "database_access"

    # Scope
    total_users_reviewed = Column(Integer, default=0)
    total_permissions_reviewed = Column(Integer, default=0)

    # Findings
    inappropriate_access_found = Column(Integer, default=0)
    access_revoked = Column(Integer, default=0)
    access_modified = Column(Integer, default=0)
    findings = Column(JSON)  # List of specific findings

    # Conclusion
    review_notes = Column(Text)
    exceptions = Column(JSON)  # Any exceptions granted

    # Reviewer information
    reviewed_by_id = Column(PGUUID(as_uuid=True), nullable=False)
    approved_by_id = Column(PGUUID(as_uuid=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# PREDEFINED SOC 2 CONTROLS
# ============================================================================

SOC2_CONTROLS = [
    # Common Criteria - Security
    {
        "control_id": "CC6.1",
        "category": TrustServiceCategory.COMMON_CRITERIA,
        "control_name": "Logical and Physical Access Controls",
        "control_description": "The entity implements logical and physical access controls to protect against unauthorized access.",
        "control_objective": "Ensure only authorized personnel can access systems and data",
        "frequency": ControlFrequency.CONTINUOUS,
    },
    {
        "control_id": "CC6.6",
        "category": TrustServiceCategory.COMMON_CRITERIA,
        "control_name": "Encryption of Confidential Data",
        "control_description": "The entity protects confidential information during transmission and storage through encryption.",
        "control_objective": "Prevent unauthorized disclosure of sensitive data",
        "frequency": ControlFrequency.CONTINUOUS,
    },
    {
        "control_id": "CC6.7",
        "category": TrustServiceCategory.COMMON_CRITERIA,
        "control_name": "Encryption Key Management",
        "control_description": "The entity restricts access to encryption keys and periodically rotates keys.",
        "control_objective": "Protect encryption keys from unauthorized access and compromise",
        "frequency": ControlFrequency.QUARTERLY,
    },
    {
        "control_id": "CC7.2",
        "category": TrustServiceCategory.COMMON_CRITERIA,
        "control_name": "System Monitoring",
        "control_description": "The entity monitors system components to identify anomalies and security events.",
        "control_objective": "Detect and respond to security threats in a timely manner",
        "frequency": ControlFrequency.CONTINUOUS,
    },
    {
        "control_id": "CC7.3",
        "category": TrustServiceCategory.COMMON_CRITERIA,
        "control_name": "Security Event Evaluation and Response",
        "control_description": "The entity evaluates security events and responds to security incidents.",
        "control_objective": "Ensure timely detection and response to security incidents",
        "frequency": ControlFrequency.CONTINUOUS,
    },

    # Availability
    {
        "control_id": "A1.1",
        "category": TrustServiceCategory.AVAILABILITY,
        "control_name": "System Availability",
        "control_description": "The entity maintains system availability per committed service levels.",
        "control_objective": "Ensure systems are available for use as committed",
        "frequency": ControlFrequency.CONTINUOUS,
    },
    {
        "control_id": "A1.2",
        "category": TrustServiceCategory.AVAILABILITY,
        "control_name": "Backup and Recovery",
        "control_description": "The entity performs regular backups and tests recovery procedures.",
        "control_objective": "Ensure data can be recovered in case of loss",
        "frequency": ControlFrequency.DAILY,
    },

    # Confidentiality
    {
        "control_id": "C1.1",
        "category": TrustServiceCategory.CONFIDENTIALITY,
        "control_name": "Confidential Information Identification",
        "control_description": "The entity identifies and classifies confidential information.",
        "control_objective": "Ensure confidential data is properly identified and protected",
        "frequency": ControlFrequency.QUARTERLY,
    },
    {
        "control_id": "C1.2",
        "category": TrustServiceCategory.CONFIDENTIALITY,
        "control_name": "Disposal of Confidential Information",
        "control_description": "The entity disposes of confidential information securely.",
        "control_objective": "Prevent unauthorized access to disposed confidential data",
        "frequency": ControlFrequency.AD_HOC,
    },

    # Processing Integrity
    {
        "control_id": "PI1.1",
        "category": TrustServiceCategory.PROCESSING_INTEGRITY,
        "control_name": "Processing Completeness and Accuracy",
        "control_description": "The entity ensures processing is complete, accurate, timely, and authorized.",
        "control_objective": "Ensure data processing maintains integrity",
        "frequency": ControlFrequency.CONTINUOUS,
    },
]
