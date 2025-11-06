"""
E&O Insurance Portal

Platform validation and risk assessment for E&O insurance companies.

Features:
- Test platform accuracy with real audit failures
- Assess CPA firm risk profiles
- Calculate premium adjustments
- Generate underwriting reports
- Demonstrate platform ROI
"""

from .test_case_service import (
    TestCaseService,
    AuditFailureType,
    TestCaseStatus,
    DetectionResult,
    TestCaseError,
)

from .risk_assessment_service import (
    RiskAssessmentService,
    RiskLevel,
    FirmSize,
    RiskAssessmentError,
)

__all__ = [
    "TestCaseService",
    "AuditFailureType",
    "TestCaseStatus",
    "DetectionResult",
    "TestCaseError",
    "RiskAssessmentService",
    "RiskLevel",
    "FirmSize",
    "RiskAssessmentError",
]

__version__ = "1.0.0"
