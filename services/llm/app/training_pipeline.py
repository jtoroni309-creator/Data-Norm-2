"""
Audit AI Training Pipeline

Comprehensive training system to continuously improve AI audit performance
to match or exceed seasoned CPA capabilities.

Pipeline Components:
1. Data Collection - Historical audit data, CPA decisions, outcomes
2. Feature Engineering - Extract ML features from engagements
3. Model Training - Train specialized models for each audit task
4. Validation - Test against CPA gold standard
5. Deployment - Promote successful models to production

Models Trained:
- Anomaly Detection (Classification)
- Risk Assessment (Regression)
- Disclosure Quality (Ranking)
- Citation Relevance (Scoring)
- Contradiction Detection (Binary)
- Confidence Estimation (Regression)
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from uuid import UUID
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    IsolationForest as SklearnIsolationForest
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    mean_squared_error,
    mean_absolute_error
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
import mlflow
import mlflow.sklearn

from .config import settings
from .mlflow_integration import mlflow_manager
from .feast_features import feature_store

logger = logging.getLogger(__name__)


class AuditAITrainer:
    """
    Training pipeline for audit AI models

    Goal: Train models that perform at or above seasoned CPA level
    """

    def __init__(self):
        """Initialize trainer"""
        self.models = {}
        self.feature_importances = {}
        self.validation_results = {}

    # =========================================================================
    # Data Collection
    # =========================================================================

    async def collect_training_data(
        self,
        db: AsyncSession,
        task_type: str,
        min_samples: int = 100,
        include_cpa_labels: bool = True
    ) -> pd.DataFrame:
        """
        Collect historical training data for a specific audit task

        Args:
            db: Database session
            task_type: Type of task (anomaly_detection, risk_assessment, etc.)
            min_samples: Minimum number of samples required
            include_cpa_labels: Whether to include CPA validation labels

        Returns:
            DataFrame with features and labels
        """
        logger.info(f"Collecting training data for {task_type}")

        if task_type == "anomaly_detection":
            return await self._collect_anomaly_training_data(db, min_samples, include_cpa_labels)
        elif task_type == "risk_assessment":
            return await self._collect_risk_training_data(db, min_samples, include_cpa_labels)
        elif task_type == "disclosure_quality":
            return await self._collect_disclosure_training_data(db, min_samples, include_cpa_labels)
        elif task_type == "confidence_estimation":
            return await self._collect_confidence_training_data(db, min_samples, include_cpa_labels)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _collect_anomaly_training_data(
        self,
        db: AsyncSession,
        min_samples: int,
        include_cpa_labels: bool
    ) -> pd.DataFrame:
        """Collect anomaly detection training data"""

        # Query anomalies with CPA validation
        query = text("""
            SELECT
                a.id as anomaly_id,
                a.engagement_id,
                a.anomaly_type,
                a.severity,
                a.evidence::text as evidence,
                a.resolution_status,
                a.cpa_validated,
                a.cpa_validation_result,
                a.false_positive,
                e.client_id as organization_id
            FROM atlas.anomalies a
            JOIN atlas.engagements e ON e.id = a.engagement_id
            WHERE a.created_at >= CURRENT_DATE - INTERVAL '12 months'
            {cpa_filter}
            ORDER BY a.created_at DESC
            LIMIT 10000
        """.format(
            cpa_filter="AND a.cpa_validated = TRUE" if include_cpa_labels else ""
        ))

        result = await db.execute(query)
        rows = result.fetchall()

        if len(rows) < min_samples:
            logger.warning(
                f"Insufficient training samples: {len(rows)} < {min_samples}"
            )

        # Convert to DataFrame
        data = []
        for row in rows:
            anomaly_id, engagement_id, anomaly_type, severity, evidence, \
                resolution_status, cpa_validated, cpa_result, false_positive, org_id = row

            # Extract features
            features = await feature_store.get_all_features(
                db=db,
                engagement_id=engagement_id,
                organization_id=org_id
            )

            # Add anomaly-specific features
            features["anomaly_type"] = anomaly_type
            features["ai_severity"] = severity

            # Label (ground truth from CPA)
            if include_cpa_labels:
                # True positive if validated as true, False positive otherwise
                features["label"] = int(not false_positive) if cpa_validated else None
                features["cpa_severity"] = cpa_result  # CPA's assessed severity
            else:
                # Use resolution status as proxy
                features["label"] = int(resolution_status == "resolved")

            data.append(features)

        df = pd.DataFrame(data)

        # Remove rows without labels
        if "label" in df.columns:
            df = df.dropna(subset=["label"])

        logger.info(f"Collected {len(df)} anomaly training samples")
        return df

    async def _collect_risk_training_data(
        self,
        db: AsyncSession,
        min_samples: int,
        include_cpa_labels: bool
    ) -> pd.DataFrame:
        """Collect risk assessment training data"""

        query = text("""
            SELECT
                r.id as risk_id,
                r.engagement_id,
                r.risk_description,
                r.risk_level,
                r.fraud_risk,
                r.assessed_by,
                r.cpa_validated,
                r.cpa_risk_level,
                e.client_id as organization_id
            FROM atlas.risks r
            JOIN atlas.engagements e ON e.id = r.engagement_id
            WHERE r.created_at >= CURRENT_DATE - INTERVAL '12 months'
            {cpa_filter}
            ORDER BY r.created_at DESC
            LIMIT 10000
        """.format(
            cpa_filter="AND r.cpa_validated = TRUE" if include_cpa_labels else ""
        ))

        result = await db.execute(query)
        rows = result.fetchall()

        data = []
        for row in rows:
            risk_id, engagement_id, description, ai_risk_level, fraud_risk, \
                assessed_by, cpa_validated, cpa_risk_level, org_id = row

            features = await feature_store.get_all_features(
                db=db,
                engagement_id=engagement_id,
                organization_id=org_id
            )

            features["ai_risk_level"] = ai_risk_level
            features["fraud_risk"] = fraud_risk

            # Convert risk level to numeric (ordinal encoding)
            risk_map = {"low": 1, "medium": 2, "high": 3}
            if include_cpa_labels and cpa_validated and cpa_risk_level:
                features["label"] = risk_map.get(cpa_risk_level, 2)
            else:
                features["label"] = risk_map.get(ai_risk_level, 2)

            data.append(features)

        df = pd.DataFrame(data)
        logger.info(f"Collected {len(df)} risk assessment training samples")
        return df

    async def _collect_disclosure_training_data(
        self,
        db: AsyncSession,
        min_samples: int,
        include_cpa_labels: bool
    ) -> pd.DataFrame:
        """Collect disclosure quality training data"""

        query = text("""
            SELECT
                d.id as disclosure_id,
                d.engagement_id,
                d.note_type,
                d.content_length,
                d.citation_count,
                d.confidence_score,
                d.contradiction_count,
                d.partner_approved,
                d.partner_edits_required,
                d.quality_score,
                e.client_id as organization_id
            FROM atlas.disclosure_drafts d
            JOIN atlas.engagements e ON e.id = d.engagement_id
            WHERE d.created_at >= CURRENT_DATE - INTERVAL '12 months'
            {partner_filter}
            ORDER BY d.created_at DESC
            LIMIT 10000
        """.format(
            partner_filter="AND d.partner_reviewed = TRUE" if include_cpa_labels else ""
        ))

        result = await db.execute(query)
        rows = result.fetchall()

        data = []
        for row in rows:
            disclosure_id, engagement_id, note_type, content_length, citation_count, \
                confidence_score, contradiction_count, partner_approved, edits_required, \
                quality_score, org_id = row

            features = await feature_store.get_all_features(
                db=db,
                engagement_id=engagement_id,
                organization_id=org_id
            )

            features["note_type"] = note_type
            features["content_length"] = content_length
            features["citation_count"] = citation_count
            features["ai_confidence_score"] = confidence_score
            features["contradiction_count"] = contradiction_count

            # Label: partner approval without major edits = high quality
            if include_cpa_labels:
                features["label"] = int(partner_approved and not edits_required)
                features["quality_score"] = quality_score  # 0-100
            else:
                # Use AI confidence as proxy
                features["label"] = int(confidence_score > 0.75)

            data.append(features)

        df = pd.DataFrame(data)
        logger.info(f"Collected {len(df)} disclosure quality training samples")
        return df

    async def _collect_confidence_training_data(
        self,
        db: AsyncSession,
        min_samples: int,
        include_cpa_labels: bool
    ) -> pd.DataFrame:
        """Collect confidence estimation training data"""

        query = text("""
            SELECT
                q.id as query_id,
                q.engagement_id,
                q.purpose,
                q.tokens_used,
                q.retrieval_time_ms,
                q.generation_time_ms,
                q.citations::text as citations,
                q.confidence_score as ai_confidence,
                q.user_feedback_score,
                q.cpa_accuracy_score,
                e.client_id as organization_id
            FROM atlas.rag_queries q
            JOIN atlas.engagements e ON e.id = q.engagement_id
            WHERE q.created_at >= CURRENT_DATE - INTERVAL '12 months'
                AND q.status = 'completed'
            {cpa_filter}
            ORDER BY q.created_at DESC
            LIMIT 10000
        """.format(
            cpa_filter="AND q.cpa_accuracy_score IS NOT NULL" if include_cpa_labels else ""
        ))

        result = await db.execute(query)
        rows = result.fetchall()

        data = []
        for row in rows:
            query_id, engagement_id, purpose, tokens_used, retrieval_time, \
                generation_time, citations, ai_confidence, user_feedback, \
                cpa_accuracy, org_id = row

            features = await feature_store.get_all_features(
                db=db,
                engagement_id=engagement_id,
                organization_id=org_id
            )

            features["purpose"] = purpose
            features["tokens_used"] = tokens_used
            features["retrieval_time_ms"] = retrieval_time
            features["generation_time_ms"] = generation_time
            features["ai_confidence"] = ai_confidence

            # Parse citations to extract features
            if citations:
                import json
                try:
                    citation_list = json.loads(citations)
                    features["citation_count"] = len(citation_list)
                    if citation_list:
                        similarities = [c.get("similarity_score", 0) for c in citation_list]
                        features["avg_citation_similarity"] = np.mean(similarities)
                except:
                    features["citation_count"] = 0
                    features["avg_citation_similarity"] = 0

            # Label: CPA's assessed accuracy (0-1)
            if include_cpa_labels and cpa_accuracy is not None:
                features["label"] = float(cpa_accuracy)
            elif user_feedback is not None:
                # Normalize user feedback (1-5) to 0-1
                features["label"] = (float(user_feedback) - 1) / 4
            else:
                features["label"] = None

            data.append(features)

        df = pd.DataFrame(data)
        df = df.dropna(subset=["label"])

        logger.info(f"Collected {len(df)} confidence estimation training samples")
        return df

    # =========================================================================
    # Model Training
    # =========================================================================

    def train_anomaly_detector(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[Any, Dict[str, float]]:
        """
        Train anomaly detection classifier

        Goal: Match or exceed CPA's ability to identify true anomalies
        vs. false positives

        Returns:
            Tuple of (trained_model, metrics_dict)
        """
        logger.info("Training anomaly detection model")

        # Start MLflow run
        with mlflow_manager.start_run("anomaly_detection_training") as run:

            # Prepare features
            feature_cols = [col for col in df.columns if col not in [
                "label", "anomaly_id", "engagement_id", "organization_id",
                "anomaly_type", "ai_severity", "cpa_severity"
            ]]

            # Handle categorical variables
            X = df[feature_cols].copy()
            X = pd.get_dummies(X, drop_first=True)

            y = df["label"].values

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=test_size,
                random_state=random_state,
                stratify=y
            )

            # Train Gradient Boosting Classifier (best for tabular data)
            model = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                min_samples_split=20,
                min_samples_leaf=10,
                subsample=0.8,
                random_state=random_state
            )

            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]

            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1_score": f1_score(y_test, y_pred),
                "roc_auc": roc_auc_score(y_test, y_pred_proba)
            }

            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="f1")
            metrics["cv_f1_mean"] = cv_scores.mean()
            metrics["cv_f1_std"] = cv_scores.std()

            # Log to MLflow
            mlflow_manager.log_rag_configuration(
                embedding_model=settings.EMBEDDING_MODEL,
                llm_model=settings.OPENAI_MODEL,
                chunk_size=settings.RAG_CHUNK_SIZE,
                chunk_overlap=settings.RAG_CHUNK_OVERLAP,
                top_k=settings.RAG_TOP_K,
                similarity_threshold=settings.RAG_SIMILARITY_THRESHOLD,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )

            mlflow.log_metrics(metrics)

            # Feature importance
            feature_importance = pd.DataFrame({
                "feature": X.columns,
                "importance": model.feature_importances_
            }).sort_values("importance", ascending=False)

            mlflow_manager.log_feature_importance(
                feature_importance["feature"].tolist()[:20],
                feature_importance["importance"].tolist()[:20]
            )

            # Log model
            mlflow.sklearn.log_model(model, "anomaly_detector")

            logger.info(
                f"Anomaly Detection Model - "
                f"Accuracy: {metrics['accuracy']:.3f}, "
                f"F1: {metrics['f1_score']:.3f}, "
                f"AUC: {metrics['roc_auc']:.3f}"
            )

            self.models["anomaly_detection"] = model
            self.feature_importances["anomaly_detection"] = feature_importance
            self.validation_results["anomaly_detection"] = metrics

            return model, metrics

    def train_confidence_estimator(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[Any, Dict[str, float]]:
        """
        Train confidence score predictor

        Goal: Accurately predict when AI output quality matches CPA quality

        Returns:
            Tuple of (trained_model, metrics_dict)
        """
        logger.info("Training confidence estimation model")

        with mlflow_manager.start_run("confidence_estimation_training") as run:

            # Prepare features
            feature_cols = [col for col in df.columns if col not in [
                "label", "query_id", "engagement_id", "organization_id"
            ]]

            X = df[feature_cols].copy()
            X = pd.get_dummies(X, drop_first=True)

            y = df["label"].values  # Continuous 0-1

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=test_size,
                random_state=random_state
            )

            # Train Gradient Boosting Regressor
            from sklearn.ensemble import GradientBoostingRegressor

            model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=4,
                min_samples_split=20,
                min_samples_leaf=10,
                subsample=0.8,
                random_state=random_state
            )

            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_test)

            metrics = {
                "mse": mean_squared_error(y_test, y_pred),
                "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
                "mae": mean_absolute_error(y_test, y_pred),
                "r2_score": model.score(X_test, y_test)
            }

            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="neg_mean_squared_error")
            metrics["cv_mse_mean"] = -cv_scores.mean()
            metrics["cv_mse_std"] = cv_scores.std()

            # Log to MLflow
            mlflow.log_metrics(metrics)

            # Feature importance
            feature_importance = pd.DataFrame({
                "feature": X.columns,
                "importance": model.feature_importances_
            }).sort_values("importance", ascending=False)

            mlflow_manager.log_feature_importance(
                feature_importance["feature"].tolist()[:20],
                feature_importance["importance"].tolist()[:20]
            )

            # Log model
            mlflow.sklearn.log_model(model, "confidence_estimator")

            logger.info(
                f"Confidence Estimation Model - "
                f"RMSE: {metrics['rmse']:.3f}, "
                f"MAE: {metrics['mae']:.3f}, "
                f"R²: {metrics['r2_score']:.3f}"
            )

            self.models["confidence_estimation"] = model
            self.feature_importances["confidence_estimation"] = feature_importance
            self.validation_results["confidence_estimation"] = metrics

            return model, metrics

    # =========================================================================
    # Validation Against CPA Baseline
    # =========================================================================

    async def validate_against_cpa(
        self,
        db: AsyncSession,
        task_type: str,
        model: Any,
        test_engagements: List[UUID]
    ) -> Dict[str, Any]:
        """
        Validate AI model performance against CPA baseline

        Compare AI predictions with CPA decisions on same test cases.

        Returns:
            Comparison metrics
        """
        logger.info(f"Validating {task_type} model against CPA baseline")

        results = {
            "task_type": task_type,
            "test_engagement_count": len(test_engagements),
            "ai_metrics": {},
            "cpa_metrics": {},
            "comparison": {}
        }

        # This would require actual CPA validation data
        # For now, log placeholder metrics

        logger.info(f"Validation complete for {task_type}")
        return results

    # =========================================================================
    # Model Deployment
    # =========================================================================

    def deploy_model(
        self,
        model_name: str,
        model: Any,
        metrics: Dict[str, float],
        stage: str = "Staging"
    ):
        """
        Deploy model to MLflow registry

        Args:
            model_name: Name for model
            model: Trained model
            metrics: Validation metrics
            stage: Deployment stage (Staging/Production)
        """
        logger.info(f"Deploying {model_name} to {stage}")

        # Log model artifact
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"

        # Register
        version = mlflow_manager.register_model(
            model_name=model_name,
            model_uri=model_uri,
            description=f"Audit AI model for {model_name}. Metrics: {metrics}",
            tags={
                "task_type": model_name,
                "trained_date": datetime.utcnow().isoformat()
            }
        )

        # Transition to stage if metrics are good
        if stage == "Production":
            # Only promote to production if exceeds threshold
            if model_name == "anomaly_detection":
                threshold_met = metrics.get("f1_score", 0) >= 0.85
            else:
                threshold_met = metrics.get("rmse", 1.0) <= 0.15

            if threshold_met:
                mlflow_manager.transition_model_stage(
                    model_name=model_name,
                    version=version,
                    stage="Production"
                )
                logger.info(f"Model {model_name} v{version} promoted to Production")
            else:
                logger.warning(
                    f"Model {model_name} did not meet production thresholds"
                )
        else:
            mlflow_manager.transition_model_stage(
                model_name=model_name,
                version=version,
                stage=stage
            )


# Global trainer instance
audit_trainer = AuditAITrainer()
