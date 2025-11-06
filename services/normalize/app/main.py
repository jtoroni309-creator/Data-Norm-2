"""
Normalize Service - Trial Balance Account Mapping

FastAPI application providing ML-powered account mapping suggestions.
"""
import logging
import time
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db
from .models import MappingSuggestion, MappingRule, MLModel, MappingHistory, MappingStatus, MappingConfidence
from .schemas import (
    HealthResponse,
    MappingRuleCreate,
    MappingRuleResponse,
    MLModelResponse,
    MappingSuggestionResponse,
    MappingSuggestionListResponse,
    ConfirmMappingRequest,
    BatchMappingRequest,
    BatchMappingSummary,
    AccountSimilarityRequest,
    AccountSimilarityResponse,
)
from .mapping_engine import HybridMapper

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Normalize Service",
    description="Trial Balance Account Mapping with ML",
    version=settings.VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize mapping engine
mapper = HybridMapper()


# ========================================
# Health Check
# ========================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.VERSION
    )


# ========================================
# Mapping Rules Endpoints
# ========================================

@app.post("/rules", response_model=MappingRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_mapping_rule(
    rule: MappingRuleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new mapping rule"""
    db_rule = MappingRule(**rule.model_dump())
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)

    logger.info(f"Created mapping rule: {db_rule.rule_name}")
    return db_rule


@app.get("/rules", response_model=List[MappingRuleResponse])
async def list_mapping_rules(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List all mapping rules"""
    query = select(MappingRule)
    if active_only:
        query = query.where(MappingRule.is_active == True)

    query = query.order_by(MappingRule.priority.desc())

    result = await db.execute(query)
    rules = result.scalars().all()

    return rules


# ========================================
# ML Model Endpoints
# ========================================

@app.get("/models", response_model=List[MLModelResponse])
async def list_ml_models(
    db: AsyncSession = Depends(get_db)
):
    """List all ML models"""
    query = select(MLModel).order_by(MLModel.trained_at.desc())
    result = await db.execute(query)
    models = result.scalars().all()

    return models


@app.get("/models/active", response_model=MLModelResponse)
async def get_active_model(
    db: AsyncSession = Depends(get_db)
):
    """Get currently active ML model"""
    query = select(MLModel).where(MLModel.is_active == True).limit(1)
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active ML model found"
        )

    return model


# ========================================
# Account Similarity Endpoints
# ========================================

@app.post("/similarity", response_model=AccountSimilarityResponse)
async def find_similar_accounts(
    request: AccountSimilarityRequest,
    db: AsyncSession = Depends(get_db)
):
    """Find similar accounts using string similarity"""
    from .mapping_engine import SimilarityMapper

    similar_accounts = await SimilarityMapper.find_similar_accounts(
        request.account_name,
        db,
        top_k=request.top_k
    )

    return AccountSimilarityResponse(
        query_account=request.account_name,
        similar_accounts=similar_accounts,
        method="levenshtein"
    )


# ========================================
# Mapping Suggestions Endpoints
# ========================================

@app.post("/engagements/{engagement_id}/map", response_model=BatchMappingSummary)
async def generate_mapping_suggestions(
    engagement_id: UUID,
    request: BatchMappingRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate mapping suggestions for all unmapped trial balance lines

    Process:
    1. Fetch all trial balance lines for engagement
    2. For each unmapped line, generate suggestion using hybrid approach
    3. Store suggestions in database
    4. Return summary with counts and suggestions
    """
    start_time = time.time()

    # Fetch trial balance lines
    query = text("""
        SELECT
            tb.id as trial_balance_id,
            tbl.id as line_id,
            tbl.account_code,
            tbl.account_name,
            tbl.balance_amount,
            tbl.mapped_account_id
        FROM atlas.trial_balances tb
        JOIN atlas.trial_balance_lines tbl ON tbl.trial_balance_id = tb.id
        WHERE tb.engagement_id = :engagement_id
        ORDER BY tbl.account_code
    """)

    result = await db.execute(query, {"engagement_id": engagement_id})
    lines = result.fetchall()

    total_lines = len(lines)
    suggestions_created = []
    high_confidence_count = 0

    for line in lines:
        tb_id, line_id, account_code, account_name, balance, mapped_account_id = line

        # Skip if already mapped
        if mapped_account_id:
            continue

        # Generate mapping suggestion
        suggestion_result = await mapper.suggest_mapping(
            account_name,
            account_code,
            db,
            use_ml=request.use_ml_model,
            use_rules=request.use_mapping_rules
        )

        # Skip if confidence below threshold
        if suggestion_result["confidence"] < request.confidence_threshold:
            continue

        # Create suggestion record
        suggestion = MappingSuggestion(
            engagement_id=engagement_id,
            trial_balance_line_id=line_id,
            source_account_code=account_code,
            source_account_name=account_name,
            suggested_account_code=suggestion_result["suggested_account_code"],
            suggested_account_name=suggestion_result["suggested_account_name"],
            confidence_score=suggestion_result["confidence"],
            confidence_level=suggestion_result["confidence_level"],
            alternatives=suggestion_result.get("alternatives", []),
            status=MappingStatus.SUGGESTED,
            model_version=None  # Set if ML model used
        )

        db.add(suggestion)
        suggestions_created.append(suggestion)

        if suggestion.confidence_level in [MappingConfidence.HIGH, MappingConfidence.VERY_HIGH]:
            high_confidence_count += 1

    await db.commit()

    # Refresh all suggestions to get IDs
    for suggestion in suggestions_created:
        await db.refresh(suggestion)

    processing_time = time.time() - start_time

    logger.info(
        f"Generated {len(suggestions_created)} mapping suggestions for engagement {engagement_id} "
        f"in {processing_time:.2f}s"
    )

    return BatchMappingSummary(
        engagement_id=engagement_id,
        total_lines=total_lines,
        mapped_count=total_lines - len([l for l in lines if not l[5]]),  # Has mapped_account_id
        suggested_count=len(suggestions_created),
        unmapped_count=len([l for l in lines if not l[5]]) - len(suggestions_created),
        high_confidence_count=high_confidence_count,
        processing_time_seconds=round(processing_time, 2),
        suggestions=[
            MappingSuggestionResponse(**{
                **suggestion.__dict__,
                "alternatives": suggestion.alternatives or []
            })
            for suggestion in suggestions_created[:50]  # Return first 50
        ]
    )


@app.get("/engagements/{engagement_id}/suggestions", response_model=MappingSuggestionListResponse)
async def list_mapping_suggestions(
    engagement_id: UUID,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all mapping suggestions for engagement"""
    query = select(MappingSuggestion).where(
        MappingSuggestion.engagement_id == engagement_id
    )

    if status_filter:
        query = query.where(MappingSuggestion.status == status_filter)

    query = query.order_by(MappingSuggestion.confidence_score.desc())

    result = await db.execute(query)
    suggestions = result.scalars().all()

    # Count by status
    unmapped_count = len([s for s in suggestions if s.status == MappingStatus.UNMAPPED])
    suggested_count = len([s for s in suggestions if s.status == MappingStatus.SUGGESTED])
    confirmed_count = len([s for s in suggestions if s.status == MappingStatus.CONFIRMED])

    return MappingSuggestionListResponse(
        suggestions=[
            MappingSuggestionResponse(**{
                **s.__dict__,
                "alternatives": s.alternatives or []
            })
            for s in suggestions
        ],
        total=len(suggestions),
        unmapped_count=unmapped_count,
        suggested_count=suggested_count,
        confirmed_count=confirmed_count
    )


@app.patch("/suggestions/{suggestion_id}", response_model=MappingSuggestionResponse)
async def confirm_mapping_suggestion(
    suggestion_id: UUID,
    request: ConfirmMappingRequest,
    db: AsyncSession = Depends(get_db)
):
    """Confirm, reject, or manually override mapping suggestion"""
    # Fetch suggestion
    query = select(MappingSuggestion).where(MappingSuggestion.id == suggestion_id)
    result = await db.execute(query)
    suggestion = result.scalar_one_or_none()

    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suggestion {suggestion_id} not found"
        )

    # Update based on action
    if request.action == "confirm":
        suggestion.status = MappingStatus.CONFIRMED

        # Update trial balance line mapping
        update_query = text("""
            UPDATE atlas.trial_balance_lines
            SET mapped_account_id = (
                SELECT id FROM atlas.chart_of_accounts
                WHERE account_code = :account_code
                LIMIT 1
            )
            WHERE id = :line_id
        """)
        await db.execute(
            update_query,
            {
                "account_code": suggestion.suggested_account_code,
                "line_id": suggestion.trial_balance_line_id
            }
        )

        # Add to mapping history for training
        history = MappingHistory(
            engagement_id=suggestion.engagement_id,
            source_account_code=suggestion.source_account_code,
            source_account_name=suggestion.source_account_name,
            mapped_account_code=suggestion.suggested_account_code,
            mapped_account_name=suggestion.suggested_account_name,
            mapping_method="confirmed_suggestion",
            confidence_score=suggestion.confidence_score,
            mapped_by=suggestion.reviewed_by  # Set from auth
        )
        db.add(history)

    elif request.action == "reject":
        suggestion.status = MappingStatus.REJECTED

    elif request.action == "manual":
        if not request.manual_account_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="manual_account_code required for manual action"
            )

        suggestion.status = MappingStatus.MANUAL
        suggestion.suggested_account_code = request.manual_account_code

        # Fetch account name
        query = text("""
            SELECT account_name FROM atlas.chart_of_accounts
            WHERE account_code = :code LIMIT 1
        """)
        result = await db.execute(query, {"code": request.manual_account_code})
        row = result.fetchone()
        if row:
            suggestion.suggested_account_name = row[0]

        # Update trial balance line
        update_query = text("""
            UPDATE atlas.trial_balance_lines
            SET mapped_account_id = (
                SELECT id FROM atlas.chart_of_accounts
                WHERE account_code = :account_code
                LIMIT 1
            )
            WHERE id = :line_id
        """)
        await db.execute(
            update_query,
            {
                "account_code": request.manual_account_code,
                "line_id": suggestion.trial_balance_line_id
            }
        )

        # Add to history
        history = MappingHistory(
            engagement_id=suggestion.engagement_id,
            source_account_code=suggestion.source_account_code,
            source_account_name=suggestion.source_account_name,
            mapped_account_code=request.manual_account_code,
            mapped_account_name=suggestion.suggested_account_name,
            mapping_method="manual_override",
            confidence_score=1.0,
            mapped_by=suggestion.reviewed_by
        )
        db.add(history)

    # Update feedback
    if request.feedback_notes:
        suggestion.feedback_notes = request.feedback_notes

    await db.commit()
    await db.refresh(suggestion)

    logger.info(f"Updated suggestion {suggestion_id}: {request.action}")

    return MappingSuggestionResponse(**{
        **suggestion.__dict__,
        "alternatives": suggestion.alternatives or []
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
