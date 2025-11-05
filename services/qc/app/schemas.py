"""Pydantic schemas for QC Service API"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .models import QCCheckStatus


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str
    version: str


# ========================================
# Policy Schemas
# ========================================

class PolicyBase(BaseModel):
    """Base policy fields"""
    policy_code: str = Field(..., min_length=1, max_length=100)
    policy_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    is_blocking: bool = True
    standard_reference: Optional[str] = None


class PolicyCreate(PolicyBase):
    """Policy creation request"""
    check_logic: Dict[str, Any] = Field(..., description="Structured policy check rules")


class QCPolicyResponse(PolicyBase):
    """Policy response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    check_logic: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ========================================
# Check Request/Response Schemas
# ========================================

class QCCheckRequest(BaseModel):
    """Request to run QC checks"""
    engagement_id: UUID
    policy_codes: Optional[List[str]] = Field(
        None,
        description="Specific policies to check (if None, runs all active policies)"
    )


class QCCheckResponse(BaseModel):
    """Individual QC check result"""
    policy_code: str
    policy_name: str
    standard_reference: Optional[str] = None
    is_blocking: bool
    status: QCCheckStatus
    passed: bool
    details: str = Field(..., description="Explanation of result")
    remediation: str = Field(..., description="Steps to resolve if failed")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Supporting evidence")
    executed_at: Optional[datetime] = None


class QCResultSummary(BaseModel):
    """Summary of all QC checks for an engagement"""
    engagement_id: UUID
    executed_at: datetime
    total_checks: int
    passed: int
    failed: int
    waived: int
    blocking_failed: int = Field(
        ...,
        description="Number of blocking checks that failed (prevents finalization)"
    )
    can_lock_binder: bool = Field(
        ...,
        description="True if engagement can proceed to finalization"
    )
    checks: List[QCCheckResponse]


# ========================================
# Waiver Schemas
# ========================================

class WaiverRequest(BaseModel):
    """Request to waive a failed check"""
    check_id: UUID
    reason: str = Field(..., min_length=10, max_length=500)


class WaiverResponse(BaseModel):
    """Waiver confirmation"""
    check_id: UUID
    waived_by: UUID
    waived_at: datetime
    reason: str


# ========================================
# Compliance Report Schemas
# ========================================

class ComplianceSummary(BaseModel):
    """Firm-wide compliance summary"""
    period: Dict[str, Optional[datetime]]
    summary: Dict[str, Any]
    policy_statistics: Optional[List[Dict[str, Any]]] = None


# ========================================
# Policy Evaluation Schemas
# ========================================

class PolicyEvaluationResult(BaseModel):
    """Result of evaluating a single policy"""
    passed: bool
    details: str
    remediation: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    waived: bool = False
