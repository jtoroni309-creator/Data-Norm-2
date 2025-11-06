"""Unit tests for Normalize Service"""
import pytest
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, patch

from app.models import (
    MappingRule,
    MLModel,
    MappingSuggestion,
    MappingHistory,
    MappingConfidence,
    MappingStatus
)
from app.schemas import (
    MappingRuleCreate,
    MappingRuleResponse,
    MLModelResponse,
    MappingSuggestionResponse,
    ConfirmMappingRequest,
    AccountSimilarityRequest,
    SimilarAccountResponse
)


# ========================================
# Model Tests
# ========================================

class TestMappingRuleModel:
    """Test MappingRule ORM model"""

    def test_mapping_rule_attributes(self):
        """Test mapping rule has correct attributes"""
        rule = MappingRule(
            id=uuid4(),
            rule_name="Cash Accounts",
            description="Map accounts containing 'cash' to 1000",
            source_pattern="cash",
            target_account_code="1000",
            priority=10,
            is_regex=False,
            is_active=True,
            confidence_boost=0.1
        )

        assert rule.rule_name == "Cash Accounts"
        assert rule.source_pattern == "cash"
        assert rule.target_account_code == "1000"
        assert rule.priority == 10
        assert rule.is_active is True

    def test_mapping_rule_regex_pattern(self):
        """Test mapping rule with regex pattern"""
        rule = MappingRule(
            id=uuid4(),
            rule_name="Receivable Pattern",
            source_pattern=r".*receivable.*",
            target_account_code="1200",
            is_regex=True
        )

        assert rule.is_regex is True
        assert "receivable" in rule.source_pattern


class TestMLModelModel:
    """Test MLModel ORM model"""

    def test_ml_model_attributes(self):
        """Test ML model has correct attributes"""
        model = MLModel(
            id=uuid4(),
            model_name="Account Mapper v1",
            model_version="1.0.0",
            model_type="random_forest",
            training_samples=1000,
            accuracy=0.92,
            precision=0.90,
            recall=0.88,
            f1_score=0.89,
            is_active=True
        )

        assert model.model_version == "1.0.0"
        assert model.model_type == "random_forest"
        assert model.accuracy == 0.92
        assert model.is_active is True

    def test_ml_model_hyperparameters(self):
        """Test ML model stores hyperparameters as JSONB"""
        hyperparams = {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5
        }

        model = MLModel(
            id=uuid4(),
            model_name="RF Model",
            model_version="1.0.0",
            model_type="random_forest",
            training_samples=500,
            hyperparameters=hyperparams
        )

        assert model.hyperparameters["n_estimators"] == 100
        assert model.hyperparameters["max_depth"] == 10


class TestMappingSuggestionModel:
    """Test MappingSuggestion ORM model"""

    def test_mapping_suggestion_attributes(self):
        """Test mapping suggestion has correct attributes"""
        engagement_id = uuid4()
        line_id = uuid4()

        suggestion = MappingSuggestion(
            id=uuid4(),
            engagement_id=engagement_id,
            trial_balance_line_id=line_id,
            source_account_code="101",
            source_account_name="Cash on Hand",
            suggested_account_code="1000",
            suggested_account_name="Cash",
            confidence_score=0.95,
            confidence_level=MappingConfidence.VERY_HIGH,
            status=MappingStatus.SUGGESTED
        )

        assert suggestion.engagement_id == engagement_id
        assert suggestion.source_account_code == "101"
        assert suggestion.suggested_account_code == "1000"
        assert suggestion.confidence_score == 0.95
        assert suggestion.confidence_level == MappingConfidence.VERY_HIGH

    def test_mapping_suggestion_alternatives(self):
        """Test mapping suggestion stores alternatives"""
        alternatives = [
            {"account_code": "1010", "account_name": "Petty Cash", "score": 0.85},
            {"account_code": "1020", "account_name": "Cash in Bank", "score": 0.80}
        ]

        suggestion = MappingSuggestion(
            id=uuid4(),
            engagement_id=uuid4(),
            trial_balance_line_id=uuid4(),
            source_account_code="101",
            source_account_name="Cash",
            suggested_account_code="1000",
            suggested_account_name="Cash",
            confidence_score=0.95,
            confidence_level=MappingConfidence.VERY_HIGH,
            status=MappingStatus.SUGGESTED,
            alternatives=alternatives
        )

        assert len(suggestion.alternatives) == 2
        assert suggestion.alternatives[0]["account_code"] == "1010"


class TestMappingStatusEnums:
    """Test enum values"""

    def test_mapping_confidence_enum(self):
        """Test mapping confidence levels"""
        assert MappingConfidence.LOW.value == "low"
        assert MappingConfidence.MEDIUM.value == "medium"
        assert MappingConfidence.HIGH.value == "high"
        assert MappingConfidence.VERY_HIGH.value == "very_high"

    def test_mapping_status_enum(self):
        """Test mapping status values"""
        assert MappingStatus.UNMAPPED.value == "unmapped"
        assert MappingStatus.SUGGESTED.value == "suggested"
        assert MappingStatus.CONFIRMED.value == "confirmed"
        assert MappingStatus.REJECTED.value == "rejected"
        assert MappingStatus.MANUAL.value == "manual"


# ========================================
# Schema Tests
# ========================================

class TestMappingSchemas:
    """Test Pydantic schemas"""

    def test_mapping_rule_create_valid(self):
        """Test mapping rule creation schema"""
        data = MappingRuleCreate(
            rule_name="Test Rule",
            description="Test description",
            source_pattern="test",
            target_account_code="1000",
            priority=5,
            is_regex=False,
            confidence_boost=0.05
        )

        assert data.rule_name == "Test Rule"
        assert data.source_pattern == "test"
        assert data.priority == 5

    def test_confirm_mapping_request_confirm(self):
        """Test confirm mapping request schema"""
        request = ConfirmMappingRequest(
            action="confirm",
            feedback_notes="Looks good"
        )

        assert request.action == "confirm"
        assert request.feedback_notes == "Looks good"

    def test_confirm_mapping_request_manual(self):
        """Test manual mapping override"""
        request = ConfirmMappingRequest(
            action="manual",
            manual_account_code="2000",
            feedback_notes="Different account needed"
        )

        assert request.action == "manual"
        assert request.manual_account_code == "2000"

    def test_account_similarity_request(self):
        """Test similarity search request"""
        request = AccountSimilarityRequest(
            account_name="Cash on Hand",
            top_k=5
        )

        assert request.account_name == "Cash on Hand"
        assert request.top_k == 5


# ========================================
# Mapping Engine Tests
# ========================================

class TestRuleBasedMapper:
    """Test rule-based mapper"""

    @pytest.mark.asyncio
    async def test_apply_rules_keyword_match(self):
        """Test keyword-based rule matching"""
        from app.mapping_engine import RuleBasedMapper

        # Mock database response with matching rule
        # Note: rule_name field is used as the pattern to match
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("cash", "1000", 0.1, 10, False),  # Pattern "cash" will match "Cash on Hand"
        ]

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        result = await RuleBasedMapper.apply_rules("Cash on Hand", "101", db)

        assert result is not None
        assert result["suggested_account_code"] == "1000"
        assert result["method"] == "rule_keyword"

    @pytest.mark.asyncio
    async def test_apply_rules_no_match(self):
        """Test when no rules match"""
        from app.mapping_engine import RuleBasedMapper

        # Mock database response with no matching rules
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("Cash Accounts", "1000", 0.1, 10, False),  # Won't match "Inventory"
        ]

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        result = await RuleBasedMapper.apply_rules("Inventory", "301", db)

        assert result is None


class TestSimilarityMapper:
    """Test similarity-based mapper"""

    def test_levenshtein_similarity(self):
        """Test Levenshtein similarity calculation"""
        from app.mapping_engine import SimilarityMapper

        # Identical strings
        assert SimilarityMapper.levenshtein_similarity("cash", "cash") == 1.0

        # Similar strings
        score = SimilarityMapper.levenshtein_similarity("cash on hand", "cash in hand")
        assert score > 0.8

        # Different strings
        score = SimilarityMapper.levenshtein_similarity("cash", "revenue")
        assert score < 0.3

    @pytest.mark.asyncio
    async def test_find_similar_accounts(self):
        """Test finding similar accounts"""
        from app.mapping_engine import SimilarityMapper

        # Mock database response with chart of accounts
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("1000", "Cash", "asset"),
            ("1010", "Cash in Bank", "asset"),
            ("1020", "Petty Cash", "asset"),
            ("2000", "Accounts Payable", "liability"),
        ]

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        similar = await SimilarityMapper.find_similar_accounts("Cash on Hand", db, top_k=3)

        assert len(similar) <= 3
        # Should find cash-related accounts
        assert any("Cash" in acc.account_name for acc in similar)


class TestMLMapper:
    """Test ML-based mapper"""

    def test_extract_features(self):
        """Test feature extraction from account"""
        from app.mapping_engine import MLMapper

        ml_mapper = MLMapper()
        features = ml_mapper.extract_features("Accounts Receivable", "1200")

        assert features["name_length"] == len("Accounts Receivable")
        assert features["has_receivable"] == 1
        assert features["has_payable"] == 0
        assert features["has_cash"] == 0

    def test_extract_features_cash(self):
        """Test feature extraction for cash account"""
        from app.mapping_engine import MLMapper

        ml_mapper = MLMapper()
        features = ml_mapper.extract_features("Cash in Bank", "1000")

        assert features["has_cash"] == 1
        assert features["has_asset"] == 0  # "cash" doesn't contain "asset"

    def test_extract_features_expense(self):
        """Test feature extraction for expense account"""
        from app.mapping_engine import MLMapper

        ml_mapper = MLMapper()
        features = ml_mapper.extract_features("Operating Expenses", "5000")

        assert features["has_expense"] == 1
        assert features["has_revenue"] == 0


# ========================================
# Configuration Tests
# ========================================

class TestConfiguration:
    """Test configuration settings"""

    def test_default_settings(self):
        """Test default configuration values"""
        from app.config import settings

        assert settings.SERVICE_NAME == "normalize"
        assert settings.VERSION == "1.0.0"
        assert settings.LOG_LEVEL == "INFO"
        assert settings.ML_CONFIDENCE_THRESHOLD == 0.75
        assert settings.SIMILARITY_THRESHOLD == 0.6

    def test_ml_settings(self):
        """Test ML-specific settings"""
        from app.config import settings

        assert 0 < settings.ML_CONFIDENCE_THRESHOLD < 1
        assert 0 < settings.SIMILARITY_THRESHOLD < 1
        assert settings.MIN_TRAINING_SAMPLES > 0

    def test_feature_engineering_settings(self):
        """Test feature engineering configuration"""
        from app.config import settings

        assert settings.USE_TFIDF_VECTORIZER is True
        assert settings.NGRAM_RANGE_MIN >= 1
        assert settings.NGRAM_RANGE_MAX >= settings.NGRAM_RANGE_MIN
        assert settings.MAX_FEATURES > 0
