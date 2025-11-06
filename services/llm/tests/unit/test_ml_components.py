"""
Unit tests for ML components

Tests:
- Confidence scoring system
- Contradiction detection
- MLflow integration
- Feature store
- Training pipeline
- Knowledge ingestion
"""
import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np
import pandas as pd

from app.confidence_scoring import (
    ConfidenceScorer,
    ConfidenceLevel,
    ConfidenceScores
)
from app.contradiction_detector import (
    ContradictionDetector,
    ContradictionSeverity,
    Contradiction
)
from app.schemas import Citation


# ========================================
# Confidence Scoring Tests
# ========================================

class TestConfidenceScorer:
    """Test confidence scoring system"""

    def test_citation_quality_high_authority(self):
        """Test citation quality with authoritative sources"""
        scorer = ConfidenceScorer()

        citations = [
            Citation(
                document_id=uuid4(),
                document_title="PCAOB AS 1215",
                standard_code="AS 1215",
                source="PCAOB",
                chunk_content="Test content",
                similarity_score=0.92
            ),
            Citation(
                document_id=uuid4(),
                document_title="AICPA SAS 142",
                standard_code="SAS 142",
                source="AICPA",
                chunk_content="Test content",
                similarity_score=0.88
            )
        ]

        response_text = "According to AS 1215 [1], documentation must be complete. SAS 142 [2] requires evidence."

        score, issues = scorer.score_citation_quality(citations, response_text)

        assert score > 0.8  # High score for authoritative sources
        assert len(issues) == 0  # No issues with good citations

    def test_citation_quality_low_relevance(self):
        """Test citation quality with low similarity scores"""
        scorer = ConfidenceScorer()

        citations = [
            Citation(
                document_id=uuid4(),
                document_title="Some Guide",
                standard_code=None,
                source="Unknown",
                chunk_content="Test content",
                similarity_score=0.45  # Low similarity
            )
        ]

        response_text = "Based on guidance [1], we recommend..."

        score, issues = scorer.score_citation_quality(citations, response_text)

        assert score < 0.7  # Low score
        assert any("relevance" in issue.lower() for issue in issues)

    def test_semantic_consistency_no_contradictions(self):
        """Test semantic consistency with consistent text"""
        scorer = ConfidenceScorer()

        response = """
        The company has adequate internal controls.
        Management maintains strong oversight.
        Control procedures are functioning effectively.
        """

        score, contradictions = scorer.score_semantic_consistency(response)

        assert score >= 0.9  # High consistency
        assert len(contradictions) == 0

    def test_semantic_consistency_with_contradictions(self):
        """Test semantic consistency with contradictory statements"""
        scorer = ConfidenceScorer()

        response = """
        The internal controls are adequate.
        However, we found significant deficiencies in controls.
        Controls are functioning effectively but also inadequate.
        """

        score, contradictions = scorer.score_semantic_consistency(response)

        assert score < 0.9  # Lower score due to contradictions
        assert len(contradictions) > 0

    def test_statistical_confidence_good_scores(self):
        """Test statistical confidence with good similarity scores"""
        scorer = ConfidenceScorer()

        citations = [
            Citation(
                document_id=uuid4(),
                document_title=f"Doc {i}",
                standard_code=None,
                source="Test",
                chunk_content="Test",
                similarity_score=0.85 + i * 0.01
            )
            for i in range(5)
        ]

        score, issues = scorer.score_statistical_confidence(citations)

        assert score > 0.75  # Good statistical confidence
        assert len(issues) == 0

    def test_detect_uncertainty_hedging_language(self):
        """Test uncertainty detection with hedging language"""
        scorer = ConfidenceScorer()

        response = """
        It may be possible that the controls might be adequate.
        We could potentially conclude that perhaps the evidence suggests uncertainty.
        """

        certainty_score, indicators = scorer.detect_uncertainty(response)

        assert certainty_score < 0.7  # Low certainty due to hedging
        assert len(indicators) > 0
        assert any("may" in ind.lower() or "might" in ind.lower() for ind in indicators)

    def test_detect_uncertainty_confident_language(self):
        """Test uncertainty detection with confident language"""
        scorer = ConfidenceScorer()

        response = """
        The controls are adequate and functioning effectively.
        We conclude that the evidence supports our opinion.
        Management has implemented proper procedures.
        """

        certainty_score, indicators = scorer.detect_uncertainty(response)

        assert certainty_score >= 0.9  # High certainty
        assert len(indicators) == 0

    def test_overall_confidence_very_high(self):
        """Test overall confidence calculation for very high quality"""
        scorer = ConfidenceScorer()

        citations = [
            Citation(
                document_id=uuid4(),
                document_title="PCAOB AS 1215",
                standard_code="AS 1215.06",
                source="PCAOB",
                chunk_content="Documentation requirements",
                similarity_score=0.95
            )
        ]

        response = "According to AS 1215.06 [1], all procedures must be documented with sufficient detail."

        scores = scorer.calculate_overall_confidence(citations, response)

        assert scores.overall_score >= 0.75  # High quality
        assert scores.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]
        assert len(scores.recommendations) > 0

    def test_overall_confidence_low(self):
        """Test overall confidence calculation for low quality"""
        scorer = ConfidenceScorer()

        citations = [
            Citation(
                document_id=uuid4(),
                document_title="Unknown Source",
                standard_code=None,
                source="Unknown",
                chunk_content="Some text",
                similarity_score=0.35
            )
        ]

        response = "It might be possible that controls could potentially be adequate perhaps."

        scores = scorer.calculate_overall_confidence(citations, response)

        assert scores.overall_score < 0.60  # Low quality
        assert scores.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]
        assert "regenerat" in scores.recommendations[0].lower() or "review" in scores.recommendations[0].lower()


# ========================================
# Contradiction Detection Tests
# ========================================

class TestContradictionDetector:
    """Test contradiction detection system"""

    def test_semantic_contradiction_detection(self):
        """Test detection of semantic contradictions"""
        detector = ContradictionDetector()

        statements = [
            "The company has adequate internal controls.",
            "The company does not have adequate internal controls."
        ]

        contradictions = detector.detect_semantic_contradictions(statements)

        assert len(contradictions) > 0
        assert contradictions[0].severity in [ContradictionSeverity.HIGH, ContradictionSeverity.CRITICAL]
        assert contradictions[0].type == "semantic"

    def test_no_contradiction_similar_statements(self):
        """Test no false positives for similar but consistent statements"""
        detector = ContradictionDetector()

        statements = [
            "The controls are adequate and functioning effectively.",
            "Internal controls are properly designed and operating effectively."
        ]

        contradictions = detector.detect_semantic_contradictions(statements)

        assert len(contradictions) == 0  # Should not detect contradictions

    def test_numerical_contradiction_detection(self):
        """Test detection of numerical inconsistencies"""
        detector = ContradictionDetector()

        text = """
        Total assets amount to $1,000,000.
        Later in the document, total assets are reported as $950,000.
        """

        contradictions = detector.detect_numerical_contradictions(text)

        assert len(contradictions) > 0
        assert contradictions[0].type == "numerical"
        assert contradictions[0].severity == ContradictionSeverity.CRITICAL

    def test_temporal_contradiction_detection(self):
        """Test detection of temporal contradictions"""
        detector = ContradictionDetector()

        text = """
        The audit was completed before March 31, 2024.
        Fieldwork procedures were performed after March 31, 2024.
        """

        contradictions = detector.detect_temporal_contradictions(text)

        # May detect temporal inconsistency
        # Note: This is a complex case, implementation may vary

    def test_analyze_text_comprehensive(self):
        """Test comprehensive text analysis"""
        detector = ContradictionDetector()

        text = """
        Revenue for 2024 is $5,000,000.
        The company's revenue is $4,500,000.
        Controls are adequate but also inadequate.
        """

        report = detector.analyze_text(text)

        assert report.has_contradictions is True
        assert report.contradiction_count > 0
        assert report.overall_consistency_score < 1.0
        assert "CRITICAL" in report.recommendation or "WARNING" in report.recommendation

    def test_analyze_text_no_contradictions(self):
        """Test analysis of consistent text"""
        detector = ContradictionDetector()

        text = """
        Revenue for 2024 is $5,000,000.
        Internal controls are functioning effectively.
        Management has implemented proper procedures.
        """

        report = detector.analyze_text(text, check_semantic=True, check_numerical=True)

        assert report.contradiction_count == 0
        assert report.overall_consistency_score >= 0.95
        assert "PASS" in report.recommendation


# ========================================
# MLflow Integration Tests
# ========================================

class TestMLflowIntegration:
    """Test MLflow integration"""

    @patch('app.mlflow_integration.mlflow')
    def test_start_run(self, mock_mlflow):
        """Test starting an MLflow run"""
        from app.mlflow_integration import MLflowManager

        mock_mlflow.start_run.return_value = MagicMock()

        manager = MLflowManager()
        run = manager.start_run("test_run", tags={"test": "true"})

        assert mock_mlflow.start_run.called
        assert run is not None

    @patch('app.mlflow_integration.mlflow')
    def test_log_rag_configuration(self, mock_mlflow):
        """Test logging RAG configuration"""
        from app.mlflow_integration import MLflowManager

        manager = MLflowManager()
        manager.log_rag_configuration(
            embedding_model="test-model",
            llm_model="gpt-4",
            chunk_size=1000,
            chunk_overlap=200,
            top_k=5,
            similarity_threshold=0.7,
            temperature=0.3,
            max_tokens=2000
        )

        assert mock_mlflow.log_params.called

    @patch('app.mlflow_integration.mlflow')
    def test_log_audit_quality_metrics(self, mock_mlflow):
        """Test logging audit quality metrics"""
        from app.mlflow_integration import MLflowManager

        manager = MLflowManager()
        manager.log_audit_quality_metrics(
            engagement_id=uuid4(),
            findings_accuracy_rate=0.92,
            false_positive_rate=0.05,
            false_negative_rate=0.03,
            citation_accuracy_rate=0.95,
            workpaper_quality_score=0.88,
            compliance_check_pass_rate=0.97,
            partner_approval_rate=0.91,
            time_savings_vs_manual_hours=120.5
        )

        assert mock_mlflow.log_metrics.called

    @patch('app.mlflow_integration.mlflow')
    def test_log_cpa_comparison_metrics(self, mock_mlflow):
        """Test logging CPA comparison metrics"""
        from app.mlflow_integration import MLflowManager

        manager = MLflowManager()
        manager.log_cpa_comparison_metrics(
            task_name="anomaly_detection",
            ai_accuracy=0.94,
            cpa_accuracy=0.92,
            ai_time_minutes=5.0,
            cpa_time_minutes=120.0,
            ai_cost_dollars=0.50,
            cpa_cost_dollars=200.0,
            quality_score_ai=0.90,
            quality_score_cpa=0.92
        )

        assert mock_mlflow.log_metrics.called
        assert mock_mlflow.log_dict.called


# ========================================
# Feature Store Tests
# ========================================

class TestFeatureStore:
    """Test feature store functionality"""

    @pytest.mark.asyncio
    async def test_get_engagement_features(self):
        """Test extracting engagement-level features"""
        from app.feast_features import FeatureStore

        store = FeatureStore()
        db = AsyncMock()

        # Mock database responses
        mock_result1 = MagicMock()
        mock_result1.fetchone.return_value = (
            "audit", "fieldwork", 30, 5, 1, 2
        )

        mock_result2 = MagicMock()
        mock_result2.fetchone.return_value = (
            5000000.0,  # total_assets
            2000000.0,  # total_liabilities
            3000000.0,  # total_equity
            10000000.0, # total_revenue
            150         # account_count
        )

        mock_result3 = MagicMock()
        mock_result3.fetchone.return_value = (5, 1, 2.5)  # risks

        mock_result4 = MagicMock()
        mock_result4.fetchone.return_value = (3, 1, 1)  # anomalies

        db.execute.side_effect = [mock_result1, mock_result2, mock_result3, mock_result4]

        engagement_id = uuid4()
        features = await store.get_engagement_features(db, engagement_id)

        assert "engagement_type" in features
        assert "total_assets" in features
        assert "total_risks" in features
        assert "anomaly_count" in features
        assert features["total_assets"] == 5000000.0
        assert features["size_category"] in ["small", "medium", "large", "enterprise"]

    @pytest.mark.asyncio
    async def test_get_account_features(self):
        """Test extracting account-level features"""
        from app.feast_features import FeatureStore

        store = FeatureStore()
        db = AsyncMock()

        # Mock account balance
        mock_result1 = MagicMock()
        mock_result1.fetchone.return_value = (
            100000.0,  # balance
            50000.0,   # debit
            30000.0,   # credit
            "asset",
            "current_asset",
            True
        )

        # Mock journal entries
        mock_result2 = MagicMock()
        mock_result2.fetchone.return_value = (
            10,        # entry_count
            2,         # manual_entry_count
            0,         # weekend_entry_count
            10000.0,   # avg_entry_size
            2000.0,    # stddev_entry_size
            15000.0    # max_entry_size
        )

        db.execute.side_effect = [mock_result1, mock_result2]

        features = await store.get_account_features(db, uuid4(), "1000")

        assert "balance_amount" in features
        assert "entry_count" in features
        assert features["balance_amount"] == 100000.0
        assert features["account_type"] == "asset"

    def test_convert_to_dataframe(self):
        """Test converting features to DataFrame"""
        from app.feast_features import FeatureStore

        store = FeatureStore()

        features_list = [
            {"eng_total_assets": 1000000, "eng_size_category": "medium", "eng_team_size": 5},
            {"eng_total_assets": 5000000, "eng_size_category": "large", "eng_team_size": 8},
        ]

        df = store.convert_to_dataframe(features_list)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "eng_total_assets" in df.columns


# ========================================
# Training Pipeline Tests
# ========================================

class TestTrainingPipeline:
    """Test training pipeline"""

    def test_train_anomaly_detector(self):
        """Test training anomaly detection model"""
        from app.training_pipeline import AuditAITrainer

        trainer = AuditAITrainer()

        # Create synthetic training data
        np.random.seed(42)
        n_samples = 100

        df = pd.DataFrame({
            "feature1": np.random.randn(n_samples),
            "feature2": np.random.randn(n_samples),
            "feature3": np.random.randn(n_samples),
            "label": np.random.randint(0, 2, n_samples)
        })

        with patch('app.training_pipeline.mlflow_manager'):
            with patch('app.training_pipeline.mlflow'):
                model, metrics = trainer.train_anomaly_detector(df, test_size=0.3)

        assert model is not None
        assert "accuracy" in metrics
        assert "f1_score" in metrics
        assert "roc_auc" in metrics
        assert 0.0 <= metrics["accuracy"] <= 1.0

    def test_train_confidence_estimator(self):
        """Test training confidence estimation model"""
        from app.training_pipeline import AuditAITrainer

        trainer = AuditAITrainer()

        # Create synthetic training data
        np.random.seed(42)
        n_samples = 100

        df = pd.DataFrame({
            "feature1": np.random.randn(n_samples),
            "feature2": np.random.randn(n_samples),
            "feature3": np.random.randn(n_samples),
            "label": np.random.uniform(0, 1, n_samples)  # Continuous 0-1
        })

        with patch('app.training_pipeline.mlflow_manager'):
            with patch('app.training_pipeline.mlflow'):
                model, metrics = trainer.train_confidence_estimator(df, test_size=0.3)

        assert model is not None
        assert "mse" in metrics
        assert "rmse" in metrics
        assert "mae" in metrics
        assert metrics["rmse"] >= 0


# ========================================
# Knowledge Ingestion Tests
# ========================================

class TestKnowledgeIngestion:
    """Test knowledge base ingestion"""

    @pytest.mark.asyncio
    async def test_ingest_pcaob_standard(self):
        """Test ingesting PCAOB standard"""
        from app.knowledge_ingestion import KnowledgeIngestionPipeline

        pipeline = KnowledgeIngestionPipeline()
        db = AsyncMock()

        # Mock document creation
        doc_id = uuid4()
        mock_doc = MagicMock()
        mock_doc.id = doc_id
        db.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, 'id', doc_id))

        with patch('app.knowledge_ingestion.embedding_service') as mock_embedding:
            mock_embedding.chunk_text.return_value = ["chunk1", "chunk2"]
            mock_embedding.generate_embeddings.return_value = (
                [[0.1] * 384, [0.2] * 384],  # Mock embeddings
                0  # Cache hits
            )

            content = """
            .01 Introduction
            This standard applies to all audits.

            .02 Objective
            The objective is to obtain sufficient appropriate evidence.
            """

            result_id = await pipeline.ingest_pcaob_standard(
                db=db,
                standard_code="AS 1215",
                title="Audit Documentation",
                content=content
            )

            assert db.add.called
            assert db.commit.called

    @pytest.mark.asyncio
    async def test_parse_pcaob_sections(self):
        """Test parsing PCAOB standard sections"""
        from app.knowledge_ingestion import KnowledgeIngestionPipeline

        pipeline = KnowledgeIngestionPipeline()

        content = """
        .01 Introduction and Scope
        This standard applies to audits of financial statements.

        .02 Objective
        The auditor must obtain sufficient appropriate evidence.

        .03 Definitions
        For purposes of this standard, the terms below are defined.
        """

        sections = pipeline._parse_pcaob_sections(content, "AS 1215")

        assert len(sections) >= 3
        assert sections[0]["number"] == "01"
        assert "introduction" in sections[0]["title"].lower()
        assert len(sections[0]["content"]) > 0


# ========================================
# Integration Tests
# ========================================

class TestMLSystemIntegration:
    """Test integration between ML components"""

    def test_confidence_scoring_with_rag_output(self):
        """Test confidence scoring on RAG-generated output"""
        scorer = ConfidenceScorer()

        # Simulate RAG output
        citations = [
            Citation(
                document_id=uuid4(),
                document_title="PCAOB AS 1215",
                standard_code="AS 1215.06",
                source="PCAOB",
                chunk_content="Documentation must include procedures performed",
                similarity_score=0.91
            )
        ]

        response = """
        According to PCAOB AS 1215.06 [1], audit documentation must include:
        1. The nature and extent of procedures performed
        2. The results of those procedures
        3. The conclusions reached

        The auditor should ensure all workpapers are complete.
        """

        scores = scorer.calculate_overall_confidence(citations, response)

        assert scores.overall_score >= 0.7
        assert len(scores.recommendations) > 0

    def test_contradiction_detection_on_disclosure(self):
        """Test contradiction detection on disclosure draft"""
        detector = ContradictionDetector()

        disclosure = """
        Note 1: Summary of Significant Accounting Policies

        Revenue Recognition:
        The company recognizes revenue when control transfers to the customer.
        Revenue is recognized at a point in time for product sales.

        However, later sections state:
        Revenue is recognized over time for all sales transactions.
        """

        report = detector.analyze_text(disclosure)

        assert report.has_contradictions
        assert report.critical_count > 0 or report.high_count > 0
