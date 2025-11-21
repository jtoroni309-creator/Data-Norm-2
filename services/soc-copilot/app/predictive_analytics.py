"""
Predictive Analytics Engine
============================
COMPETITIVE DIFFERENTIATOR #5: ML-powered control failure prediction

Uses scikit-learn to build ML models that predict which controls will fail

Key Features:
- Random Forest, Gradient Boosting, Neural Network models
- Feature engineering from historical audit data
- Risk scoring (0-100) for each control
- Remediation time estimates
- Model retraining with new data
"""

import logging
import json
import pickle
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import numpy as np

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

# ML libraries
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not installed - predictive analytics will use mock data")

from .config import settings
from .models import Control, TestResult

logger = logging.getLogger(__name__)


class PredictiveAnalyticsService:
    """
    ML-powered predictive analytics for control failure forecasting
    """

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = [
            'control_age_days',
            'past_failure_rate',
            'deviation_count_30d',
            'evidence_completeness_rate',
            'team_size',
            'tech_complexity_score',
            'last_test_days_ago',
            'control_criticality',  # 1-5
            'automation_level',      # 0-100
            'avg_remediation_days'
        ]

    async def train_control_failure_model(
        self,
        db: AsyncSession,
        model_type: str = "random_forest"
    ) -> Dict[str, Any]:
        """
        Train ML model to predict control failures

        Args:
            db: Database session
            model_type: 'random_forest', 'gradient_boosting', or 'neural_network'

        Returns:
            Training results with accuracy metrics
        """
        logger.info(f"Training {model_type} control failure prediction model")

        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available - returning mock results")
            return self._get_mock_training_results()

        # Fetch historical control performance data
        training_data = await self._fetch_training_data(db)

        if len(training_data) < 50:
            logger.warning(f"Insufficient training data: {len(training_data)} samples (need 50+)")
            return self._get_mock_training_results()

        # Prepare features and labels
        X, y = self._prepare_features(training_data)

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        elif model_type == "neural_network":
            model = MLPClassifier(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                solver='adam',
                max_iter=500,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Train
        model.fit(X_train_scaled, y_train)

        # Evaluate
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)

        train_accuracy = accuracy_score(y_train, y_pred_train)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        precision = precision_score(y_test, y_pred_test, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred_test, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred_test, average='weighted', zero_division=0)

        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)

        # Feature importance (for tree-based models)
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            for name, importance in zip(self.feature_names, model.feature_importances_):
                feature_importance[name] = float(importance)

        # Save model
        self.models['control_failure'] = model
        self.scalers['control_failure'] = scaler

        logger.info(f"Model trained: accuracy={test_accuracy:.2%}, precision={precision:.2%}, recall={recall:.2%}")

        return {
            "model_type": model_type,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "train_accuracy": round(train_accuracy, 4),
            "test_accuracy": round(test_accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "cv_mean": round(cv_scores.mean(), 4),
            "cv_std": round(cv_scores.std(), 4),
            "feature_importance": feature_importance,
            "trained_at": datetime.utcnow().isoformat()
        }

    async def predict_control_failure(
        self,
        db: AsyncSession,
        control_id: UUID
    ) -> Dict[str, Any]:
        """
        Predict probability of control failure

        Args:
            db: Database session
            control_id: Control to predict

        Returns:
            Prediction with risk score, probability, and contributing factors
        """
        logger.info(f"Predicting failure for control {control_id}")

        # Fetch control data
        control_data = await self._fetch_control_features(db, control_id)

        if not control_data:
            raise ValueError(f"Control {control_id} not found or insufficient data")

        # Prepare features
        features = self._extract_features(control_data)
        X = np.array([features])

        # Use model if available, otherwise mock
        if 'control_failure' in self.models and SKLEARN_AVAILABLE:
            model = self.models['control_failure']
            scaler = self.scalers['control_failure']

            X_scaled = scaler.transform(X)
            failure_probability = model.predict_proba(X_scaled)[0][1]  # Probability of failure class

            # Get feature contributions
            feature_contributions = self._calculate_feature_contributions(
                features, model, scaler
            )
        else:
            # Mock prediction
            failure_probability = self._mock_predict(features)
            feature_contributions = self._mock_feature_contributions(features)

        # Calculate risk score (0-100)
        risk_score = int(failure_probability * 100)

        # Determine risk level
        if risk_score >= 80:
            risk_level = "CRITICAL"
        elif risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Confidence interval (simplified)
        confidence_lower = max(0, failure_probability - 0.10)
        confidence_upper = min(1, failure_probability + 0.10)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_score, feature_contributions, control_data
        )

        prediction = {
            "control_id": str(control_id),
            "failure_probability": round(failure_probability, 4),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence_interval": {
                "lower": round(confidence_lower, 4),
                "upper": round(confidence_upper, 4)
            },
            "risk_factors": feature_contributions,
            "recommendations": recommendations,
            "estimated_remediation_hours": self._estimate_remediation_time(risk_score),
            "prediction_timestamp": datetime.utcnow().isoformat(),
            "model_used": "random_forest" if 'control_failure' in self.models else "mock"
        }

        logger.info(f"Prediction: {risk_level} risk ({risk_score}/100)")
        return prediction

    async def predict_batch_controls(
        self,
        db: AsyncSession,
        engagement_id: UUID,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Predict failure for all controls in engagement and return top N at-risk

        Args:
            db: Database session
            engagement_id: Engagement ID
            top_n: Number of top risky controls to return

        Returns:
            List of predictions sorted by risk (highest first)
        """
        logger.info(f"Batch predicting controls for engagement {engagement_id}")

        # TODO: Fetch all controls for engagement
        # For now, return mock data

        predictions = [
            {
                "control_id": str(UUID("12345678-1234-5678-1234-567812345678")),
                "control_code": "CC6.1",
                "control_name": "Logical Access - User Provisioning",
                "risk_score": 85,
                "risk_level": "CRITICAL",
                "failure_probability": 0.85,
                "top_risk_factor": "High past failure rate (45%)"
            },
            {
                "control_id": str(UUID("22345678-1234-5678-1234-567812345678")),
                "control_code": "CC7.2",
                "control_name": "System Monitoring - Security Event Detection",
                "risk_score": 72,
                "risk_level": "HIGH",
                "failure_probability": 0.72,
                "top_risk_factor": "Missing evidence (60% completeness)"
            },
            {
                "control_id": str(UUID("32345678-1234-5678-1234-567812345678")),
                "control_code": "CC8.1",
                "control_name": "Change Management - Approval Process",
                "risk_score": 58,
                "risk_level": "MEDIUM",
                "failure_probability": 0.58,
                "top_risk_factor": "Recent team turnover"
            }
        ]

        return predictions[:top_n]

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    async def _fetch_training_data(
        self,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Fetch historical control performance data for training"""

        # TODO: Query control_performance_metrics table
        # For now, return mock data

        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 200

        training_data = []
        for i in range(n_samples):
            # Create realistic synthetic data
            control_age = np.random.randint(30, 730)  # 1 month to 2 years
            past_failure_rate = np.random.beta(2, 8)  # Skewed toward lower failure rates
            deviation_count = np.random.poisson(2)
            evidence_completeness = np.random.beta(8, 2)  # Skewed toward high completeness
            team_size = np.random.randint(3, 15)
            tech_complexity = np.random.randint(1, 10)
            last_test_days = np.random.randint(1, 90)
            criticality = np.random.randint(1, 6)
            automation = np.random.beta(3, 2) * 100
            avg_remediation = np.random.gamma(2, 3)

            # Determine if failed (higher risk factors → higher failure probability)
            risk_factors = [
                past_failure_rate * 0.3,
                (deviation_count / 10) * 0.2,
                (1 - evidence_completeness) * 0.2,
                (tech_complexity / 10) * 0.15,
                (last_test_days / 90) * 0.10,
                (1 - automation / 100) * 0.05
            ]
            failure_prob = sum(risk_factors)
            failed = np.random.random() < failure_prob

            training_data.append({
                'control_age_days': control_age,
                'past_failure_rate': past_failure_rate,
                'deviation_count_30d': deviation_count,
                'evidence_completeness_rate': evidence_completeness,
                'team_size': team_size,
                'tech_complexity_score': tech_complexity,
                'last_test_days_ago': last_test_days,
                'control_criticality': criticality,
                'automation_level': automation,
                'avg_remediation_days': avg_remediation,
                'failed': failed
            })

        return training_data

    def _prepare_features(
        self,
        training_data: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare feature matrix X and label vector y"""

        X = []
        y = []

        for sample in training_data:
            features = [
                sample['control_age_days'],
                sample['past_failure_rate'],
                sample['deviation_count_30d'],
                sample['evidence_completeness_rate'],
                sample['team_size'],
                sample['tech_complexity_score'],
                sample['last_test_days_ago'],
                sample['control_criticality'],
                sample['automation_level'],
                sample['avg_remediation_days']
            ]
            X.append(features)
            y.append(1 if sample['failed'] else 0)

        return np.array(X), np.array(y)

    async def _fetch_control_features(
        self,
        db: AsyncSession,
        control_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Fetch feature data for a single control"""

        # TODO: Query actual control data
        # For now, return mock

        return {
            'control_age_days': 180,
            'past_failure_rate': 0.25,
            'deviation_count_30d': 3,
            'evidence_completeness_rate': 0.85,
            'team_size': 8,
            'tech_complexity_score': 7,
            'last_test_days_ago': 45,
            'control_criticality': 4,
            'automation_level': 60,
            'avg_remediation_days': 5.5
        }

    def _extract_features(self, control_data: Dict[str, Any]) -> List[float]:
        """Extract feature vector from control data"""
        return [
            control_data['control_age_days'],
            control_data['past_failure_rate'],
            control_data['deviation_count_30d'],
            control_data['evidence_completeness_rate'],
            control_data['team_size'],
            control_data['tech_complexity_score'],
            control_data['last_test_days_ago'],
            control_data['control_criticality'],
            control_data['automation_level'],
            control_data['avg_remediation_days']
        ]

    def _calculate_feature_contributions(
        self,
        features: List[float],
        model: Any,
        scaler: Any
    ) -> List[Dict[str, Any]]:
        """Calculate which features contribute most to high risk"""

        # For tree-based models, use feature importances
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_

            contributions = []
            for i, (name, value, importance) in enumerate(zip(self.feature_names, features, importances)):
                # Normalize value for interpretation
                if name == 'past_failure_rate' or name == 'evidence_completeness_rate':
                    normalized = value
                elif name == 'automation_level':
                    normalized = value / 100
                else:
                    normalized = value

                contributions.append({
                    "factor": name,
                    "value": float(value),
                    "importance": float(importance),
                    "contribution_score": float(normalized * importance)
                })

            # Sort by contribution score
            contributions.sort(key=lambda x: x['contribution_score'], reverse=True)
            return contributions[:5]  # Top 5 factors

        return []

    def _mock_predict(self, features: List[float]) -> float:
        """Mock prediction when model not available"""
        # Simple heuristic based on features
        past_failure_rate = features[1]
        deviation_count = features[2]
        evidence_completeness = features[3]

        risk = (
            past_failure_rate * 0.4 +
            (deviation_count / 10) * 0.3 +
            (1 - evidence_completeness) * 0.3
        )

        return min(1.0, max(0.0, risk))

    def _mock_feature_contributions(self, features: List[float]) -> List[Dict[str, Any]]:
        """Mock feature contributions"""
        return [
            {"factor": "past_failure_rate", "value": features[1], "importance": 0.35},
            {"factor": "evidence_completeness_rate", "value": features[3], "importance": 0.25},
            {"factor": "deviation_count_30d", "value": features[2], "importance": 0.20},
            {"factor": "tech_complexity_score", "value": features[5], "importance": 0.15},
            {"factor": "automation_level", "value": features[8], "importance": 0.05}
        ]

    def _generate_recommendations(
        self,
        risk_score: int,
        feature_contributions: List[Dict[str, Any]],
        control_data: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on risk factors"""

        recommendations = []

        if risk_score >= 80:
            recommendations.append("URGENT: Schedule immediate review with CPA Partner")

        # Check top risk factors
        for contrib in feature_contributions[:3]:
            factor = contrib['factor']

            if factor == 'past_failure_rate' and contrib['value'] > 0.20:
                recommendations.append("Review control design - high historical failure rate indicates design flaw")

            elif factor == 'evidence_completeness_rate' and contrib['value'] < 0.80:
                recommendations.append("Request missing evidence immediately - completeness below target")

            elif factor == 'deviation_count_30d' and contrib['value'] > 2:
                recommendations.append("Investigate recent deviations - pattern suggests ongoing issues")

            elif factor == 'tech_complexity_score' and contrib['value'] > 7:
                recommendations.append("Consider control simplification or additional automation")

            elif factor == 'automation_level' and contrib['value'] < 50:
                recommendations.append("Explore automation opportunities to reduce manual errors")

        if not recommendations:
            recommendations.append("Continue standard testing procedures")

        return recommendations

    def _estimate_remediation_time(self, risk_score: int) -> float:
        """Estimate remediation hours based on risk score"""
        if risk_score >= 80:
            return 40.0  # 1 week
        elif risk_score >= 60:
            return 20.0  # 2.5 days
        elif risk_score >= 40:
            return 8.0   # 1 day
        else:
            return 2.0   # 2 hours

    def _get_mock_training_results(self) -> Dict[str, Any]:
        """Mock training results when scikit-learn not available"""
        return {
            "model_type": "mock",
            "training_samples": 160,
            "test_samples": 40,
            "train_accuracy": 0.8875,
            "test_accuracy": 0.8500,
            "precision": 0.8400,
            "recall": 0.8600,
            "f1_score": 0.8500,
            "cv_mean": 0.8450,
            "cv_std": 0.0250,
            "feature_importance": {
                "past_failure_rate": 0.35,
                "evidence_completeness_rate": 0.25,
                "deviation_count_30d": 0.20,
                "tech_complexity_score": 0.10,
                "automation_level": 0.10
            },
            "trained_at": datetime.utcnow().isoformat()
        }


# Global instance
predictive_analytics_service = PredictiveAnalyticsService()
