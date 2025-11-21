"""
Natural Language Query API Routes
===================================
FastAPI routes for ChatGPT-like audit analytics
"""

import logging
from typing import List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .models import User
from .nl_query_service import nl_query_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nl-query", tags=["Natural Language Query"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class NLQueryRequest(BaseModel):
    """Natural language query request"""
    user_query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language question about audit data",
        examples=["Show me all failed controls", "Which evidence is missing?"]
    )
    engagement_id: Optional[UUID] = Field(
        None,
        description="Optional engagement filter"
    )


class QueryResultResponse(BaseModel):
    """Query result response"""
    success: bool
    user_query: str
    interpreted_intent: Optional[str] = None
    sql_generated: Optional[str] = None
    template_used: Optional[str] = None
    results_count: int
    results: List[dict]
    summary: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None


class QuerySuggestion(BaseModel):
    """Query suggestion/template"""
    template_name: str
    description: str
    example_question: str


class QueryHistoryItem(BaseModel):
    """Query history item"""
    id: str
    user_query: str
    interpreted_intent: Optional[str]
    results_count: int
    timestamp: str
    execution_time_ms: Optional[int]


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/execute", response_model=QueryResultResponse)
async def execute_nl_query(
    request: NLQueryRequest,
    db: AsyncSession = Depends(get_db)
    # current_user: User = Depends(get_current_user)
) -> QueryResultResponse:
    """
    Execute natural language query

    **Examples:**
    - "Show me all failed controls"
    - "Which controls are at risk of failing?"
    - "What evidence is missing or incomplete?"
    - "Show me high-risk deviations"
    - "Summarize all security controls (CC6 and CC7)"

    **Returns:**
    - SQL generated from natural language
    - Query results (up to 100 rows)
    - AI-generated summary
    - Execution time
    """
    logger.info(f"Executing NL query: {request.user_query}")

    try:
        # Execute query
        result = await nl_query_service.execute_nl_query(
            db=db,
            user_query=request.user_query,
            engagement_id=request.engagement_id,
            user_id=None  # TODO: Get from current_user
        )

        return QueryResultResponse(**result)

    except Exception as e:
        logger.error(f"NL query execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )


@router.get("/suggestions", response_model=List[QuerySuggestion])
async def get_query_suggestions(
    engagement_id: Optional[UUID] = None
) -> List[QuerySuggestion]:
    """
    Get suggested queries based on engagement context

    **Returns:** List of pre-built query templates with examples

    **Use Case:** Display as quick-start buttons in UI
    """
    try:
        suggestions = await nl_query_service.get_query_suggestions(
            engagement_id=engagement_id
        )

        return [QuerySuggestion(**s) for s in suggestions]

    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.get("/templates")
async def list_query_templates() -> dict:
    """
    List all available query templates

    **Returns:** Dictionary of template names to details
    """
    return {
        name: {
            "description": template["description"],
            "example": template["example_question"]
        }
        for name, template in nl_query_service.query_templates.items()
    }


@router.get("/schema-info")
async def get_schema_info() -> dict:
    """
    Get database schema information for context

    **Returns:** Schema description used by AI for query generation

    **Use Case:** Understanding what data is available
    """
    return {
        "schema_description": nl_query_service.schema_description,
        "available_templates": len(nl_query_service.query_templates),
        "template_names": list(nl_query_service.query_templates.keys())
    }


@router.get("/health")
async def health_check() -> dict:
    """
    Health check for NL query service

    **Returns:** Service status and AI availability
    """
    return {
        "service": "nl_query",
        "status": "healthy",
        "ai_enabled": nl_query_service.enabled,
        "available_templates": len(nl_query_service.query_templates)
    }


# ============================================================================
# ADMIN ROUTES (for query history and analytics)
# ============================================================================

@router.get("/admin/query-history", response_model=List[QueryHistoryItem])
async def get_query_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
    # current_user: User = Depends(get_current_user)
    # Require admin role
) -> List[QueryHistoryItem]:
    """
    Get query history for analytics

    **Admin Only**

    **Returns:** Recent queries with execution metrics
    """
    # TODO: Implement actual query history from database
    # For now, return empty list
    return []


@router.get("/admin/popular-queries")
async def get_popular_queries(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """
    Get most popular queries

    **Admin Only**

    **Returns:** Top queries by usage count
    """
    # TODO: Implement from nl_query_history table
    return []
