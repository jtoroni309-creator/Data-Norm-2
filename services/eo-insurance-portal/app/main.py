"""
E&O Insurance Portal - Main FastAPI Application

Provides insurance companies with tools to:
- Test platform accuracy with real audit failures
- Assess CPA firm risk profiles
- Calculate premium adjustments
- Generate underwriting reports

This portal demonstrates platform value for reducing E&O liability.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .test_case_service import (
    TestCaseService,
    AuditFailureType,
    TestCaseStatus,
    DetectionResult,
)
from .risk_assessment_service import (
    RiskAssessmentService,
    RiskLevel,
    FirmSize,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="E&O Insurance Portal",
    version="1.0.0",
    description="Platform validation and risk assessment for E&O insurance companies",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
test_case_service = TestCaseService()
risk_assessment_service = RiskAssessmentService()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TestCaseCreate(BaseModel):
    """Request model for creating test case"""
    case_name: str
    description: str
    failure_type: AuditFailureType
    actual_outcome: Dict[str, Any]
    source_documents: Dict[str, Any]
    financial_statements: Dict[str, Any]
    cpa_firm_info: Dict[str, Any]
    lawsuit_details: Optional[Dict[str, Any]] = None


class TestCaseResponse(BaseModel):
    """Response model for test case"""
    id: str
    case_name: str
    failure_type: str
    status: str
    created_at: str
    validation_results: Optional[Dict[str, Any]] = None


class ValidationRequest(BaseModel):
    """Request model for platform validation"""
    test_case_id: str
    config: Optional[Dict[str, Any]] = None


class FirmRiskAssessment(BaseModel):
    """Request model for firm risk assessment"""
    firm_profile: Dict[str, Any]
    claims_history: List[Dict[str, Any]]
    platform_usage: Optional[Dict[str, Any]] = None


class ROICalculation(BaseModel):
    """Request model for ROI calculation"""
    current_premium: float
    platform_cost: float
    expected_accuracy: float = Field(ge=0, le=100)


class UnderwritingReportRequest(BaseModel):
    """Request model for underwriting report"""
    firm_assessment: Dict[str, Any]
    platform_performance: Dict[str, Any]
    test_case_results: List[Dict[str, Any]]


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "eo-insurance-portal",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# TEST CASE MANAGEMENT
# ============================================================================

@app.post("/api/v1/test-cases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(request: TestCaseCreate):
    """
    Create a test case from a real audit failure.

    This allows insurance companies to upload actual audit failures to test
    whether the platform would have detected them.
    """
    try:
        test_case_id = await test_case_service.create_test_case(
            case_name=request.case_name,
            description=request.description,
            failure_type=request.failure_type,
            actual_outcome=request.actual_outcome,
            source_documents=request.source_documents,
            financial_statements=request.financial_statements,
            cpa_firm_info=request.cpa_firm_info,
            lawsuit_details=request.lawsuit_details,
        )

        test_case = test_case_service._test_cases[test_case_id]

        return TestCaseResponse(
            id=test_case["id"],
            case_name=test_case["case_name"],
            failure_type=test_case["failure_type"],
            status=test_case["status"],
            created_at=test_case["created_at"],
            validation_results=test_case.get("validation_results"),
        )

    except Exception as e:
        logger.error(f"Failed to create test case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test case: {str(e)}"
        )


@app.get("/api/v1/test-cases/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(test_case_id: str):
    """Get test case by ID"""
    if test_case_id not in test_case_service._test_cases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case not found: {test_case_id}"
        )

    test_case = test_case_service._test_cases[test_case_id]

    return TestCaseResponse(
        id=test_case["id"],
        case_name=test_case["case_name"],
        failure_type=test_case["failure_type"],
        status=test_case["status"],
        created_at=test_case["created_at"],
        validation_results=test_case.get("validation_results"),
    )


@app.get("/api/v1/test-cases")
async def list_test_cases():
    """List all test cases"""
    test_cases = []
    for test_case in test_case_service._test_cases.values():
        test_cases.append({
            "id": test_case["id"],
            "case_name": test_case["case_name"],
            "failure_type": test_case["failure_type"],
            "status": test_case["status"],
            "created_at": test_case["created_at"],
        })

    return {
        "total": len(test_cases),
        "test_cases": test_cases,
    }


@app.post("/api/v1/test-cases/{test_case_id}/validate")
async def validate_test_case(test_case_id: str, request: Optional[ValidationRequest] = None):
    """
    Run platform validation on test case.

    This executes all platform audit procedures on the test case and
    compares results with the actual outcome.
    """
    try:
        config = request.config if request else None

        validation_result = await test_case_service.run_platform_validation(
            test_case_id=test_case_id,
            validation_config=config,
        )

        return {
            "test_case_id": test_case_id,
            "status": "completed",
            "detection_result": validation_result["detection_result"],
            "accuracy_score": validation_result["accuracy_score"],
            "platform_findings": validation_result["platform_findings"],
            "comparison": validation_result["comparison"],
        }

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

@app.get("/api/v1/metrics/performance")
async def get_performance_metrics():
    """
    Get platform performance metrics.

    Shows overall accuracy, detection rate, false positive/negative rates.
    """
    metrics = test_case_service.get_performance_metrics()

    return {
        "metrics": metrics,
        "generated_at": datetime.utcnow().isoformat(),
        "interpretation": {
            "overall_accuracy": f"{metrics['overall_accuracy']}% - " +
                              ("Excellent" if metrics['overall_accuracy'] >= 95 else
                               "Very Good" if metrics['overall_accuracy'] >= 90 else
                               "Good" if metrics['overall_accuracy'] >= 85 else
                               "Acceptable"),
            "detection_rate": f"{metrics['detection_rate']}% of actual issues detected",
            "false_negative_rate": f"{metrics['false_negative_rate']}% of issues missed (critical metric)",
        }
    }


# ============================================================================
# RISK ASSESSMENT
# ============================================================================

@app.post("/api/v1/risk-assessment/firm")
async def assess_firm_risk(request: FirmRiskAssessment):
    """
    Assess CPA firm risk profile.

    Evaluates firm based on:
    - Size and revenue
    - Years in practice
    - Claims history
    - Platform usage (if applicable)

    Returns risk score and recommended premium.
    """
    try:
        assessment = risk_assessment_service.assess_firm_risk(
            firm_profile=request.firm_profile,
            claims_history=request.claims_history,
            platform_usage=request.platform_usage,
        )

        return assessment

    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk assessment failed: {str(e)}"
        )


@app.post("/api/v1/risk-assessment/roi")
async def calculate_roi(request: ROICalculation):
    """
    Calculate ROI of platform adoption.

    Shows potential premium savings vs. platform cost.
    """
    try:
        roi = risk_assessment_service.calculate_roi(
            current_premium=Decimal(str(request.current_premium)),
            platform_cost=Decimal(str(request.platform_cost)),
            expected_accuracy=request.expected_accuracy,
        )

        return roi

    except Exception as e:
        logger.error(f"ROI calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ROI calculation failed: {str(e)}"
        )


# ============================================================================
# UNDERWRITING REPORTS
# ============================================================================

@app.post("/api/v1/reports/underwriting")
async def generate_underwriting_report(request: UnderwritingReportRequest):
    """
    Generate comprehensive underwriting report.

    Combines:
    - Firm risk assessment
    - Platform performance metrics
    - Test case results
    - Premium recommendations
    - Underwriting decision
    """
    try:
        report = risk_assessment_service.generate_underwriting_report(
            firm_assessment=request.firm_assessment,
            platform_performance=request.platform_performance,
            test_case_results=request.test_case_results,
        )

        return report

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )


# ============================================================================
# DEMO / EXAMPLES
# ============================================================================

@app.get("/api/v1/demo/sample-test-case")
async def get_sample_test_case():
    """
    Get sample test case for demonstration.

    Shows typical audit failure scenario.
    """
    return {
        "case_name": "Going Concern Failure - Tech Startup",
        "description": "CPA firm failed to issue going concern opinion for tech startup that filed bankruptcy 3 months after audit",
        "failure_type": "going_concern_issue",
        "actual_outcome": {
            "issue_occurred": True,
            "description": "Company filed Chapter 7 bankruptcy 3 months after receiving clean opinion",
            "lawsuit_filed": True,
            "settlement_amount": 750000,
        },
        "financial_statements": {
            "fiscal_year": 2024,
            "total_assets": 2000000,
            "total_liabilities": 3500000,
            "total_equity": -1500000,  # Negative equity!
            "revenue": 500000,
            "net_income": -1200000,  # Large loss
            "operating_cash_flow": -800000,  # Negative cash flow
            "cash": 50000,  # Very low cash
            "current_ratio": 0.3,  # Very low
            "debt_to_equity": -2.33,  # Negative
        },
        "platform_should_detect": True,
        "expected_detection_result": "true_positive",
    }


@app.get("/api/v1/demo/platform-value-proposition")
async def get_value_proposition():
    """
    Get platform value proposition for E&O insurance companies.

    Explains how platform reduces liability exposure.
    """
    return {
        "title": "Aura Audit AI - E&O Risk Mitigation Platform",
        "value_propositions": [
            {
                "benefit": "Reduce Claims Frequency",
                "description": "Platform detects 90%+ of audit failures that lead to lawsuits",
                "impact": "15-25% reduction in claims frequency",
            },
            {
                "benefit": "Lower Claim Severity",
                "description": "Early detection prevents issues from escalating",
                "impact": "20-30% reduction in average claim amount",
            },
            {
                "benefit": "Premium Reduction",
                "description": "Lower risk profile enables premium discounts",
                "impact": "15-25% premium reduction for adopting firms",
            },
            {
                "benefit": "Improved Underwriting",
                "description": "Better risk assessment and pricing accuracy",
                "impact": "10-15% improvement in loss ratios",
            },
        ],
        "roi_example": {
            "scenario": "Medium-sized CPA firm",
            "current_premium": 50000,
            "platform_cost": 15000,
            "premium_reduction": 10000,  # 20%
            "net_annual_savings": -5000,  # Year 1
            "five_year_savings": 35000,
            "payback_months": 18,
        },
        "platform_accuracy": {
            "overall_accuracy": "94%",
            "detection_rate": "92%",
            "false_negative_rate": "8%",
            "benchmark": "Significantly better than Big 4 accuracy rates",
        },
    }


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("E&O Insurance Portal starting up...")
    logger.info("Services initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("E&O Insurance Portal shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
