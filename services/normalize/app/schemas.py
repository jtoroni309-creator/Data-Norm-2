"""Pydantic schemas for request/response validation"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .models import MappingConfidence, MappingStatus


# ========================================
# Health & Status
# ========================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


# ========================================
# Mapping Rule Schemas
# ========================================

class MappingRuleCreate(BaseModel):
    """Create mapping rule"""
    rule_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    source_pattern: str = Field(..., min_length=1)
    target_account_code: str = Field(..., min_length=1)
    priority: int = Field(default=0, ge=0, le=100)
    is_regex: bool = False
    confidence_boost: float = Field(default=0.0, ge=0.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)


class MappingRuleResponse(BaseModel):
    """Mapping rule response"""
    id: UUID
    rule_name: str
    description: Optional[str]
    source_pattern: str
    target_account_code: str
    priority: int
    is_active: bool
    is_regex: bool
    confidence_boost: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========================================
# ML Model Schemas
# ========================================

class MLModelResponse(BaseModel):
    """ML model metadata response"""
    id: UUID
    model_name: str
    model_version: str
    model_type: str
    training_samples: int
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    is_active: bool
    trained_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainModelRequest(BaseModel):
    """Request to train new ML model"""
    model_type: str = Field(default="random_forest", pattern="^(random_forest|gradient_boosting|neural_network)$")
    use_recent_history: bool = True  # Use recent mapping history as training data
    min_samples_per_account: int = Field(default=5, ge=1, le=100)

    model_config = ConfigDict(from_attributes=True)


# ========================================
# Mapping Suggestion Schemas
# ========================================

class MappingSuggestionResponse(BaseModel):
    """Mapping suggestion response"""
    id: UUID
    engagement_id: UUID
    trial_balance_line_id: UUID
    source_account_code: str
    source_account_name: str
    suggested_account_code: str
    suggested_account_name: str
    confidence_score: float
    confidence_level: MappingConfidence
    alternatives: Optional[List[Dict[str, Any]]]
    status: MappingStatus
    model_version: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MappingSuggestionListResponse(BaseModel):
    """List of mapping suggestions"""
    suggestions: List[MappingSuggestionResponse]
    total: int
    unmapped_count: int
    suggested_count: int
    confirmed_count: int


class ConfirmMappingRequest(BaseModel):
    """Confirm or reject mapping suggestion"""
    action: str = Field(..., pattern="^(confirm|reject|manual)$")
    manual_account_code: Optional[str] = None  # Required if action='manual'
    feedback_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ========================================
# Batch Mapping Schemas
# ========================================

class BatchMappingRequest(BaseModel):
    """Request to generate mapping suggestions for engagement"""
    engagement_id: UUID
    use_ml_model: bool = True
    use_mapping_rules: bool = True
    confidence_threshold: float = Field(default=0.75, ge=0.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)


class BatchMappingSummary(BaseModel):
    """Summary of batch mapping operation"""
    engagement_id: UUID
    total_lines: int
    mapped_count: int
    suggested_count: int
    unmapped_count: int
    high_confidence_count: int
    processing_time_seconds: float
    suggestions: List[MappingSuggestionResponse]


# ========================================
# Account Similarity Schemas
# ========================================

class AccountSimilarityRequest(BaseModel):
    """Request to find similar accounts"""
    account_name: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)

    model_config = ConfigDict(from_attributes=True)


class SimilarAccountResponse(BaseModel):
    """Similar account with similarity score"""
    account_code: str
    account_name: str
    account_type: str
    similarity_score: float  # 0.0 to 1.0


class AccountSimilarityResponse(BaseModel):
    """Response with similar accounts"""
    query_account: str
    similar_accounts: List[SimilarAccountResponse]
    method: str  # 'tfidf', 'levenshtein', 'ml_embedding'
