"""Pydantic schemas for request/response validation"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .models import AnomalySeverity, ResolutionStatus


# ========================================
# Health & Status
# ========================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


# ========================================
# Analytics Rule Schemas
# ========================================

class AnalyticsRuleCreate(BaseModel):
    """Create analytics rule"""
    rule_code: str = Field(..., min_length=1, max_length=100)
    rule_name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: str = Field(..., pattern="^(je_testing|ratio_analysis|outlier_detection)$")
    config: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class AnalyticsRuleResponse(BaseModel):
    """Analytics rule response"""
    id: UUID
    rule_code: str
    rule_name: str
    description: Optional[str] = None
    category: str
    is_active: bool
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========================================
# Analytics Execution Schemas
# ========================================

class RunAnalyticsRequest(BaseModel):
    """Request to run analytics on engagement"""
    engagement_id: UUID
    rule_codes: Optional[List[str]] = None  # If None, run all active rules

    model_config = ConfigDict(from_attributes=True)


class AnalyticsResultResponse(BaseModel):
    """Analytics result response"""
    id: UUID
    engagement_id: UUID
    rule_id: UUID
    executed_at: datetime
    findings_count: int
    result_data: Dict[str, Any]
    model_version: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RunAnalyticsSummary(BaseModel):
    """Summary of analytics execution"""
    engagement_id: UUID
    rules_executed: int
    total_findings: int
    anomalies_created: int
    results: List[AnalyticsResultResponse]


# ========================================
# Anomaly Schemas
# ========================================

class AnomalyResponse(BaseModel):
    """Anomaly response"""
    id: UUID
    engagement_id: UUID
    analytics_result_id: Optional[UUID] = None
    anomaly_type: str
    severity: AnomalySeverity
    title: str
    description: Optional[str] = None
    evidence: Dict[str, Any]
    score: Optional[float] = None
    resolution_status: str
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnomalyListResponse(BaseModel):
    """List of anomalies"""
    anomalies: List[AnomalyResponse]
    total: int
    open_count: int
    critical_count: int


class AnomalyResolve(BaseModel):
    """Resolve anomaly"""
    resolution_status: str = Field(..., pattern="^(reviewed|resolved|false_positive)$")
    resolution_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ========================================
# JE Testing Schemas
# ========================================

class JETestResult(BaseModel):
    """Result of JE testing"""
    test_type: str  # 'round_dollar', 'weekend', 'period_end'
    journal_entry_id: UUID
    entry_number: str
    entry_date: datetime
    amount: float
    flagged: bool
    reason: str
    score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class JETestSummary(BaseModel):
    """Summary of JE testing"""
    engagement_id: UUID
    total_entries_tested: int
    round_dollar_flagged: int
    weekend_flagged: int
    period_end_flagged: int
    results: List[JETestResult]


# ========================================
# Ratio Analysis Schemas
# ========================================

class RatioResult(BaseModel):
    """Financial ratio result"""
    ratio_name: str
    value: float
    benchmark: Optional[float] = None
    deviation: Optional[float] = None
    is_outlier: bool

    model_config = ConfigDict(from_attributes=True)


class RatioAnalysisSummary(BaseModel):
    """Summary of ratio analysis"""
    engagement_id: UUID
    ratios_calculated: int
    outliers_detected: int
    ratios: List[RatioResult]
