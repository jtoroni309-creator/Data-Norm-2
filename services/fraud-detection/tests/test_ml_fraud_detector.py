"""
Tests for ML Fraud Detector.
"""

import pytest
from datetime import datetime, timedelta

from app.ml_fraud_detector import ml_fraud_detector


@pytest.mark.asyncio
class TestMLFraudDetector:
    """Test ML fraud detection functionality."""

    async def test_extract_features_basic(self):
        """Test basic feature extraction."""
        transaction = {
            'amount': 100.50,
            'transaction_date': datetime.utcnow(),
            'merchant_name': 'Test Merchant',
            'category': ['Shopping'],
            'payment_channel': 'online',
            'pending': False,
        }

        features = await ml_fraud_detector.extract_features(transaction)

        assert 'amount' in features
        assert 'amount_log' in features
        assert 'hour_of_day' in features
        assert 'day_of_week' in features
        assert 'is_online' in features
        assert features['amount'] == 100.50
        assert features['is_online'] == 1.0

    async def test_extract_features_with_history(self):
        """Test feature extraction with transaction history."""
        transaction = {
            'amount': 500.00,
            'transaction_date': datetime.utcnow(),
            'merchant_name': 'Test Merchant',
            'category': ['Shopping'],
            'payment_channel': 'online',
            'pending': False,
        }

        # Create history
        history = []
        for i in range(5):
            history.append({
                'transaction_date': datetime.utcnow() - timedelta(hours=i),
                'amount': 50.00,
                'merchant_name': 'Merchant ' + str(i)
            })

        features = await ml_fraud_detector.extract_features(
            transaction,
            account_history=history
        )

        assert 'txn_count_1h' in features
        assert 'txn_count_24h' in features
        assert 'total_amount_24h' in features
        assert features['txn_count_24h'] == 5

    async def test_predict_fraud_low_risk(self):
        """Test fraud prediction for low-risk transaction."""
        transaction = {
            'amount': 25.50,
            'transaction_date': datetime.utcnow().replace(hour=14),  # Afternoon
            'merchant_name': 'Coffee Shop',
            'category': ['Food and Drink', 'Restaurants'],
            'payment_channel': 'in store',
            'pending': False,
            'location': {'country': 'US'}
        }

        result = await ml_fraud_detector.predict_fraud(transaction)

        assert 'fraud_score' in result
        assert 'risk_level' in result
        assert 'model_predictions' in result
        assert result['fraud_score'] >= 0.0
        assert result['fraud_score'] <= 1.0
        # Small in-store purchase should be low risk
        assert result['fraud_score'] < 0.5

    async def test_predict_fraud_high_risk(self):
        """Test fraud prediction for high-risk transaction."""
        transaction = {
            'amount': 15000.00,  # Large amount
            'transaction_date': datetime.utcnow().replace(hour=3),  # Night time
            'merchant_name': 'Unknown Merchant',
            'category': ['Transfer'],
            'payment_channel': 'online',
            'pending': False,
            'location': {'country': 'XX'}  # Foreign country
        }

        # Create rapid transaction history (velocity)
        history = []
        for i in range(15):  # Many recent transactions
            history.append({
                'transaction_date': datetime.utcnow() - timedelta(minutes=i*2),
                'amount': 1000.00,
                'merchant_name': 'Merchant ' + str(i)
            })

        result = await ml_fraud_detector.predict_fraud(
            transaction,
            account_history=history
        )

        assert 'fraud_score' in result
        assert 'triggered_rules' in result
        # Large night-time foreign transaction with high velocity should be high risk
        assert result['fraud_score'] > 0.6
        assert len(result['triggered_rules']) > 0

    async def test_predict_fraud_with_account_stats(self):
        """Test fraud prediction with account statistics."""
        transaction = {
            'amount': 1000.00,
            'transaction_date': datetime.utcnow(),
            'merchant_name': 'Electronics Store',
            'category': ['Shopping'],
            'payment_channel': 'online',
            'pending': False,
        }

        account_stats = {
            'avg_amount': 50.00,  # Much higher than average
            'p95_amount': 200.00,
            'account_age_days': 30
        }

        result = await ml_fraud_detector.predict_fraud(
            transaction,
            account_stats=account_stats
        )

        assert 'features' in result
        assert result['features']['deviation_from_avg'] > 10  # 1000 / 50
        assert result['features']['is_above_p95'] == 1.0

    async def test_rule_based_scoring(self):
        """Test rule-based fraud scoring."""
        features = {
            'is_large_amount': 1.0,
            'is_night_time': 1.0,
            'has_foreign_location': 1.0,
            'txn_count_1h': 8,
            'amount': 10000.00,
        }

        score = ml_fraud_detector._rule_based_score(features)

        assert score > 0.5  # Should be high risk
        assert score <= 1.0

    async def test_velocity_features(self):
        """Test velocity feature extraction."""
        now = datetime.utcnow()
        transaction = {
            'transaction_date': now,
            'amount': 100.00,
        }

        # Create transactions at different time intervals
        history = [
            {'transaction_date': now - timedelta(minutes=30), 'amount': 50.0, 'merchant_name': 'M1'},
            {'transaction_date': now - timedelta(hours=2), 'amount': 75.0, 'merchant_name': 'M2'},
            {'transaction_date': now - timedelta(hours=12), 'amount': 100.0, 'merchant_name': 'M3'},
            {'transaction_date': now - timedelta(days=3), 'amount': 25.0, 'merchant_name': 'M4'},
        ]

        features = ml_fraud_detector._extract_velocity_features(transaction, history)

        assert features['txn_count_1h'] == 1  # One in last hour
        assert features['txn_count_24h'] == 3  # Three in last day
        assert features['txn_count_7d'] == 4  # All four in last week
        assert features['unique_merchants_24h'] == 3

    async def test_feature_importance(self):
        """Test feature importance calculation."""
        features = {
            'is_large_amount': 1.0,
            'has_foreign_location': 1.0,
            'txn_count_1h': 5,
            'is_night_time': 0.0,
        }

        importance = ml_fraud_detector._get_feature_importance(features, 0.8)

        assert isinstance(importance, dict)
        assert 'is_large_amount' in importance
        assert all(0 <= v <= 1 for v in importance.values())
        # Should sum to 1.0 (normalized)
        assert abs(sum(importance.values()) - 1.0) < 0.01

    async def test_triggered_rules(self):
        """Test rule checking."""
        features = {
            'is_large_amount': 1.0,
            'txn_count_1h': 15,
            'has_foreign_location': 1.0,
            'is_night_time': 1.0,
            'amount': 20000.00,
        }

        triggered = ml_fraud_detector._check_rules(features)

        assert isinstance(triggered, list)
        assert 'LARGE_AMOUNT' in triggered
        assert 'HIGH_VELOCITY' in triggered
        assert 'FOREIGN_TRANSACTION' in triggered
        assert 'SUSPICIOUS_TIME' in triggered

    async def test_explanation_generation(self):
        """Test human-readable explanation generation."""
        from app.models import FraudSeverity

        explanation = ml_fraud_detector._generate_explanation(
            fraud_score=0.85,
            risk_level=FraudSeverity.HIGH,
            feature_importance={'is_large_amount': 0.4, 'txn_count_1h': 0.3},
            triggered_rules=['LARGE_AMOUNT', 'HIGH_VELOCITY']
        )

        assert isinstance(explanation, str)
        assert 'HIGH' in explanation
        assert '0.85' in explanation
        assert 'LARGE_AMOUNT' in explanation
        assert 'HIGH_VELOCITY' in explanation
