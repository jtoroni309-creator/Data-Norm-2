"""Unit tests for Analytics Service"""
import pytest
from datetime import datetime, date
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
import numpy as np

from app.models import (
    AnalyticsRule,
    AnalyticsResult,
    Anomaly,
    AnomalySeverity,
    ResolutionStatus
)
from app.schemas import (
    AnalyticsRuleCreate,
    AnalyticsRuleResponse,
    AnomalyResponse,
    AnomalyResolve,
    JETestResult,
    JETestSummary,
    RatioResult,
    RatioAnalysisSummary
)


# ========================================
# Model Tests
# ========================================

class TestAnalyticsRuleModel:
    """Test AnalyticsRule ORM model"""

    def test_analytics_rule_attributes(self):
        """Test analytics rule has correct attributes"""
        rule = AnalyticsRule(
            id=uuid4(),
            rule_code="AS1215_AUDIT_DOCS",
            rule_name="Audit Documentation Check",
            category="compliance",
            config={"threshold": 0.95},
            is_active=True
        )

        assert rule.rule_code == "AS1215_AUDIT_DOCS"
        assert rule.rule_name == "Audit Documentation Check"
        assert rule.category == "compliance"
        assert rule.config["threshold"] == 0.95
        assert rule.is_active is True

    def test_analytics_rule_jsonb_config(self):
        """Test JSONB config can store complex data"""
        config = {
            "threshold": 0.95,
            "parameters": {
                "min_workpapers": 3,
                "required_fields": ["description", "preparer"]
            }
        }

        rule = AnalyticsRule(
            id=uuid4(),
            rule_code="COMPLEX_CHECK",
            rule_name="Complex Check",
            category="compliance",
            config=config
        )

        assert rule.config["threshold"] == 0.95
        assert rule.config["parameters"]["min_workpapers"] == 3
        assert "description" in rule.config["parameters"]["required_fields"]


class TestAnalyticsResultModel:
    """Test AnalyticsResult ORM model"""

    def test_analytics_result_attributes(self):
        """Test analytics result has correct attributes"""
        engagement_id = uuid4()
        rule_id = uuid4()

        result = AnalyticsResult(
            id=uuid4(),
            engagement_id=engagement_id,
            rule_id=rule_id,
            findings_count=5,
            result_data={"issues_found": 5, "total_checked": 100}
        )

        assert result.engagement_id == engagement_id
        assert result.rule_id == rule_id
        assert result.findings_count == 5
        assert result.result_data["issues_found"] == 5


class TestAnomalyModel:
    """Test Anomaly ORM model"""

    def test_anomaly_attributes(self):
        """Test anomaly has correct attributes"""
        engagement_id = uuid4()

        anomaly = Anomaly(
            id=uuid4(),
            engagement_id=engagement_id,
            anomaly_type="round_dollar",
            severity=AnomalySeverity.MEDIUM,
            title="Round Dollar Entry",
            description="Journal entry total is exactly $10,000.00",
            evidence={
                "entry_number": "JE-001",
                "amount": 10000.00,
                "date": "2024-12-31"
            },
            resolution_status="open"
        )

        assert anomaly.engagement_id == engagement_id
        assert anomaly.anomaly_type == "round_dollar"
        assert anomaly.severity == AnomalySeverity.MEDIUM
        assert anomaly.resolution_status == "open"
        assert anomaly.evidence["entry_number"] == "JE-001"

    def test_anomaly_severity_enum(self):
        """Test anomaly severity enum values"""
        assert AnomalySeverity.INFO.value == "info"
        assert AnomalySeverity.LOW.value == "low"
        assert AnomalySeverity.MEDIUM.value == "medium"
        assert AnomalySeverity.HIGH.value == "high"
        assert AnomalySeverity.CRITICAL.value == "critical"

    def test_resolution_status_enum(self):
        """Test resolution status enum values"""
        assert ResolutionStatus.OPEN.value == "open"
        assert ResolutionStatus.INVESTIGATING.value == "investigating"
        assert ResolutionStatus.REVIEWED.value == "reviewed"
        assert ResolutionStatus.RESOLVED.value == "resolved"
        assert ResolutionStatus.FALSE_POSITIVE.value == "false_positive"


# ========================================
# Schema Tests
# ========================================

class TestAnalyticsSchemas:
    """Test Pydantic schemas for validation"""

    def test_analytics_rule_create_valid(self):
        """Test valid analytics rule creation schema"""
        data = AnalyticsRuleCreate(
            rule_code="TEST_RULE",
            rule_name="Test Rule",
            description="Test description",
            category="je_testing",
            config={"threshold": 0.001}
        )

        assert data.rule_code == "TEST_RULE"
        assert data.rule_name == "Test Rule"
        assert data.category == "je_testing"
        assert data.config["threshold"] == 0.001

    def test_je_test_result_schema(self):
        """Test JE test result schema"""
        result = JETestResult(
            test_type="round_dollar",
            journal_entry_id=uuid4(),
            entry_number="JE-001",
            entry_date=datetime(2024, 12, 31),
            amount=10000.00,
            flagged=True,
            reason="Divisible by 10000",
            score=0.9
        )

        assert result.test_type == "round_dollar"
        assert result.entry_number == "JE-001"
        assert result.flagged is True
        assert result.amount == 10000.00
        assert result.score == 0.9

    def test_ratio_result_schema(self):
        """Test ratio result schema"""
        result = RatioResult(
            ratio_name="current_ratio",
            value=2.5,
            benchmark=2.0,
            deviation=0.5,
            is_outlier=False
        )

        assert result.ratio_name == "current_ratio"
        assert result.value == 2.5
        assert result.benchmark == 2.0
        assert result.deviation == 0.5
        assert result.is_outlier is False

    def test_anomaly_resolve_schema(self):
        """Test anomaly resolve schema"""
        resolve = AnomalyResolve(
            resolution_status="resolved",
            resolution_notes="Verified with client, entry is legitimate"
        )

        assert resolve.resolution_status == "resolved"
        assert "legitimate" in resolve.resolution_notes


# ========================================
# JournalEntryTester Tests
# ========================================

class TestJournalEntryTester:
    """Test JournalEntryTester class"""

    @pytest.mark.asyncio
    async def test_round_dollar_detection(self):
        """Test detection of round-dollar journal entries"""
        from app.analytics_engine import JournalEntryTester

        # Mock database response - tuple includes all fields from query
        # (id, entry_number, entry_date, total_amount, is_manual, mod_100, mod_1000, mod_10000)
        je_id = uuid4()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (je_id, "JE-001", date(2024, 12, 31), Decimal("10000.00"), True, 0, 0, 0),
        ]

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        results = await JournalEntryTester.test_round_dollar_entries(engagement_id, db)

        assert len(results) > 0
        assert results[0].entry_number == "JE-001"

    @pytest.mark.asyncio
    async def test_weekend_entry_detection(self):
        """Test detection of weekend journal entries"""
        from app.analytics_engine import JournalEntryTester

        # Mock database response - (id, entry_number, entry_date, posted_date, day_of_week, total_amount)
        je_id = uuid4()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (je_id, "JE-WEEKEND", date(2024, 12, 28), date(2024, 12, 28), 6, Decimal("5000.00"))
        ]

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        results = await JournalEntryTester.test_weekend_entries(engagement_id, db)

        assert len(results) == 1
        assert results[0].entry_number == "JE-WEEKEND"
        assert results[0].flagged is True


# ========================================
# AnomalyDetector Tests
# ========================================

class TestAnomalyDetector:
    """Test AnomalyDetector class"""

    @pytest.mark.asyncio
    async def test_zscore_outlier_detection(self):
        """Test Z-score based outlier detection"""
        from app.analytics_engine import AnomalyDetector

        # Mock database response with outlier
        # (account_code, account_name, balance_amount, mean_balance, stddev_balance, z_score, sample_count)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("1000", "Cash", Decimal("1000000.00"), Decimal("100000.00"), Decimal("50000.00"), 18.0, 5)
        ]

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        outliers = await AnomalyDetector.detect_outliers_zscore(engagement_id, db)

        assert len(outliers) == 1
        assert outliers[0]["account_code"] == "1000"
        assert outliers[0]["z_score"] == 18.0


# ========================================
# RatioAnalyzer Tests
# ========================================

class TestRatioAnalyzer:
    """Test RatioAnalyzer class"""

    @pytest.mark.asyncio
    async def test_current_ratio_calculation(self):
        """Test current ratio calculation"""
        from app.analytics_engine import RatioAnalyzer

        # Mock database response: 2:1 current ratio
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (
            Decimal("200000.00"),  # current_assets
            Decimal("100000.00")   # current_liabilities
        )

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        result = await RatioAnalyzer.calculate_current_ratio(engagement_id, db)

        assert result.ratio_name == "Current Ratio"
        assert result.value == 2.0

    @pytest.mark.asyncio
    async def test_quick_ratio_calculation(self):
        """Test quick ratio calculation"""
        from app.analytics_engine import RatioAnalyzer

        # Mock database response (quick_assets, current_liabilities)
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (
            Decimal("150000.00"),  # quick_assets (current_assets - inventory)
            Decimal("100000.00")   # current_liabilities
        )

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        result = await RatioAnalyzer.calculate_quick_ratio(engagement_id, db)

        assert result.ratio_name == "Quick Ratio"
        assert result.value == 1.5

    @pytest.mark.asyncio
    async def test_debt_to_equity_calculation(self):
        """Test debt-to-equity ratio calculation"""
        from app.analytics_engine import RatioAnalyzer

        # Mock database response: 1:2 debt-to-equity
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (
            Decimal("100000.00"),  # total_liabilities
            Decimal("200000.00")   # shareholders_equity
        )

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        result = await RatioAnalyzer.calculate_debt_to_equity(engagement_id, db)

        assert result.ratio_name == "Debt-to-Equity"
        assert result.value == 0.5


# ========================================
# Configuration Tests
# ========================================

class TestConfiguration:
    """Test configuration settings"""

    def test_default_settings(self):
        """Test default configuration values"""
        from app.config import settings

        assert settings.SERVICE_NAME == "analytics"
        assert settings.VERSION == "1.0.0"
        assert settings.LOG_LEVEL == "INFO"
        assert settings.ROUND_DOLLAR_THRESHOLD == 0.001
        assert settings.OUTLIER_Z_SCORE_THRESHOLD == 3.0
        assert settings.ISOLATION_FOREST_CONTAMINATION == 0.1

    def test_analytics_thresholds(self):
        """Test analytics-specific thresholds"""
        from app.config import settings

        assert settings.ROUND_DOLLAR_THRESHOLD > 0
        assert settings.OUTLIER_Z_SCORE_THRESHOLD >= 2.0
        assert 0 < settings.ISOLATION_FOREST_CONTAMINATION < 1

    def test_mlflow_configuration(self):
        """Test MLflow integration settings"""
        from app.config import settings

        assert settings.MLFLOW_TRACKING_URI.startswith("http")
        assert "mlflow" in settings.MLFLOW_TRACKING_URI.lower()


# ========================================
# Additional JE Testing
# ========================================

class TestPeriodEndDetection:
    """Test period-end entry detection"""

    @pytest.mark.asyncio
    async def test_period_end_entry_detection(self):
        """Test detection of entries near period-end"""
        from app.analytics_engine import JournalEntryTester

        # Mock database response - entries within 3 days of close
        # (id, entry_number, entry_date, total_amount, days_to_close)
        je_id = uuid4()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (je_id, "JE-END", date(2024, 12, 30), Decimal("50000.00"), 1),  # 1 day before close
        ]

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        results = await JournalEntryTester.test_period_end_entries(engagement_id, db)

        assert len(results) == 1
        assert results[0].entry_number == "JE-END"
        assert results[0].test_type == "period_end"
        assert results[0].flagged is True
        # Score should be high (close to 1.0) since it's only 1 day before close
        assert results[0].score > 0.8

    @pytest.mark.asyncio
    async def test_period_end_material_amounts_only(self):
        """Test period-end detection filters immaterial amounts"""
        from app.analytics_engine import JournalEntryTester

        # Only entries > 10,000 should be flagged
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (uuid4(), "JE-MAT", date(2024, 12, 29), Decimal("50000.00"), 2),
        ]

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        results = await JournalEntryTester.test_period_end_entries(engagement_id, db)

        # All results should be material
        assert all(r.amount > 10000 for r in results)


# ========================================
# Additional Anomaly Detection Tests
# ========================================

class TestIsolationForestDetection:
    """Test Isolation Forest anomaly detection"""

    def test_isolation_forest_basic(self):
        """Test basic Isolation Forest detection"""
        from app.analytics_engine import AnomalyDetector

        # Create data with obvious outlier
        normal_data = np.random.normal(100, 10, 95)
        outlier_data = np.array([500])  # Clear outlier
        data = np.concatenate([normal_data, outlier_data]).reshape(-1, 1)

        predictions, scores = AnomalyDetector.detect_outliers_isolation_forest(data)

        # Should detect at least one anomaly
        anomaly_count = np.sum(predictions == -1)
        assert anomaly_count >= 1

    def test_isolation_forest_no_outliers(self):
        """Test Isolation Forest with no outliers"""
        from app.analytics_engine import AnomalyDetector

        # Normal distributed data
        data = np.random.normal(100, 10, 100).reshape(-1, 1)

        predictions, scores = AnomalyDetector.detect_outliers_isolation_forest(
            data,
            contamination=0.01  # Very strict - expect almost no anomalies
        )

        # Should detect very few or no anomalies
        anomaly_count = np.sum(predictions == -1)
        assert anomaly_count <= 2

    def test_isolation_forest_custom_contamination(self):
        """Test Isolation Forest with custom contamination rate"""
        from app.analytics_engine import AnomalyDetector

        data = np.random.normal(100, 10, 100).reshape(-1, 1)

        # Test with 10% contamination
        predictions, scores = AnomalyDetector.detect_outliers_isolation_forest(
            data,
            contamination=0.1
        )

        # Should detect approximately 10% as anomalies
        anomaly_count = np.sum(predictions == -1)
        assert 5 <= anomaly_count <= 15  # Allow some variance


# ========================================
# Ratio Edge Cases
# ========================================

class TestRatioEdgeCases:
    """Test ratio calculation edge cases"""

    @pytest.mark.asyncio
    async def test_current_ratio_zero_liabilities(self):
        """Test current ratio with zero liabilities"""
        from app.analytics_engine import RatioAnalyzer

        # Mock zero liabilities (should not crash)
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (
            Decimal("100000.00"),  # current_assets
            Decimal("0")           # current_liabilities (zero!)
        )

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        result = await RatioAnalyzer.calculate_current_ratio(engagement_id, db)

        # Should handle gracefully, not crash
        assert result is not None
        assert result.ratio_name == "Current Ratio"

    @pytest.mark.asyncio
    async def test_current_ratio_outlier_detection(self):
        """Test current ratio outlier flagging"""
        from app.analytics_engine import RatioAnalyzer

        # Mock very low ratio (0.5:1 - concerning)
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (
            Decimal("50000.00"),   # current_assets
            Decimal("100000.00")   # current_liabilities
        )

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        result = await RatioAnalyzer.calculate_current_ratio(engagement_id, db)

        assert result.value == 0.5
        assert result.is_outlier is True  # Below 1.0 should be flagged

    @pytest.mark.asyncio
    async def test_debt_to_equity_high_leverage(self):
        """Test debt-to-equity with high leverage"""
        from app.analytics_engine import RatioAnalyzer

        # Mock very high leverage (4:1 debt-to-equity)
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (
            Decimal("400000.00"),  # total_liabilities
            Decimal("100000.00")   # total_equity
        )

        db = AsyncMock()
        db.execute = AsyncMock(return_value=mock_result)

        engagement_id = uuid4()
        result = await RatioAnalyzer.calculate_debt_to_equity(engagement_id, db)

        assert result.value == 4.0
        assert result.is_outlier is True  # > 3.0 should be flagged


# ========================================
# Business Logic Validation
# ========================================

class TestAnalyticsBusinessLogic:
    """Test analytics business logic"""

    def test_anomaly_severity_ordering(self):
        """Test anomaly severity has correct priority"""
        assert AnomalySeverity.INFO.value == "info"
        assert AnomalySeverity.LOW.value == "low"
        assert AnomalySeverity.MEDIUM.value == "medium"
        assert AnomalySeverity.HIGH.value == "high"
        assert AnomalySeverity.CRITICAL.value == "critical"

        # Critical should have highest priority
        severities = [e.value for e in AnomalySeverity]
        assert severities.index("critical") > severities.index("high")
        assert severities.index("high") > severities.index("medium")

    def test_anomaly_resolution_workflow(self):
        """Test anomaly resolution status workflow"""
        anomaly = Anomaly(
            id=uuid4(),
            engagement_id=uuid4(),
            anomaly_type="test",
            severity=AnomalySeverity.MEDIUM,
            title="Test",
            description="Test description",
            resolution_status="open"
        )

        # Initially open
        assert anomaly.resolution_status == "open"
        assert anomaly.resolved_by is None

        # Move to investigating
        anomaly.resolution_status = "investigating"
        assert anomaly.resolution_status == "investigating"

        # Resolve
        anomaly.resolution_status = "resolved"
        anomaly.resolved_by = uuid4()
        anomaly.resolved_at = datetime.utcnow()

        assert anomaly.resolution_status == "resolved"
        assert anomaly.resolved_by is not None
        assert anomaly.resolved_at is not None

    def test_je_test_score_range(self):
        """Test JE test scores are in valid range"""
        # Test that scores are between 0.0 and 1.0
        test_result = JETestResult(
            test_type="round_dollar",
            journal_entry_id=uuid4(),
            entry_number="JE-001",
            entry_date=datetime.utcnow(),
            amount=10000.00,
            flagged=True,
            reason="Test",
            score=0.9
        )

        assert 0.0 <= test_result.score <= 1.0

    def test_ratio_deviation_calculation(self):
        """Test ratio deviation is calculated correctly"""
        result = RatioResult(
            ratio_name="test_ratio",
            value=3.0,
            benchmark=2.0,
            deviation=0.5,  # (3.0 - 2.0) / 2.0 = 0.5
            is_outlier=False
        )

        # Verify deviation is correct
        expected_deviation = abs(result.value - result.benchmark) / result.benchmark
        assert abs(result.deviation - expected_deviation) < 0.01
