"""
Integration tests for Fraud Detection API.
"""

import pytest
from uuid import uuid4

from app.models import BankAccount, FeatureFlag, FraudCase, Transaction


@pytest.mark.asyncio
class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
class TestFeatureFlags:
    """Test feature flag management endpoints."""

    async def test_get_feature_flag_creates_default(
        self,
        client,
        customer_id,
    ):
        """Test getting feature flag creates default if not exists."""
        response = client.get(f"/feature-flags/{customer_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == customer_id
        assert data["is_enabled"] is False  # Default is disabled

    async def test_update_feature_flag(
        self,
        client,
        customer_id,
        feature_flag,
    ):
        """Test updating feature flag."""
        user_id = str(uuid4())

        update_data = {
            "is_enabled": True,
            "ml_detection": True,
            "alert_email": True,
            "min_alert_severity": "high",
            "auto_case_creation_threshold": 0.90,
        }

        response = client.patch(
            f"/feature-flags/{customer_id}?user_id={user_id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_enabled"] is True
        assert data["ml_detection"] is True
        assert data["min_alert_severity"] == "high"
        assert data["auto_case_creation_threshold"] == 0.90

    async def test_disable_fraud_detection(
        self,
        client,
        customer_id,
        feature_flag,
    ):
        """Test disabling fraud detection."""
        user_id = str(uuid4())

        response = client.patch(
            f"/feature-flags/{customer_id}?user_id={user_id}",
            json={"is_enabled": False}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_enabled"] is False


@pytest.mark.asyncio
class TestBankAccounts:
    """Test bank account management endpoints."""

    async def test_list_bank_accounts(
        self,
        client,
        customer_id,
        bank_account,
    ):
        """Test listing bank accounts."""
        response = client.get(f"/bank-accounts?customer_id={customer_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == str(bank_account.id)

    async def test_get_bank_account(
        self,
        client,
        bank_account,
    ):
        """Test getting bank account details."""
        response = client.get(f"/bank-accounts/{bank_account.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(bank_account.id)
        assert data["account_name"] == bank_account.account_name

    async def test_update_bank_account(
        self,
        client,
        bank_account,
    ):
        """Test updating bank account."""
        update_data = {
            "account_name": "Updated Account Name",
            "monitoring_enabled": False,
            "alert_threshold_amount": 5000.00,
        }

        response = client.patch(
            f"/bank-accounts/{bank_account.id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["account_name"] == "Updated Account Name"
        assert data["monitoring_enabled"] is False
        assert float(data["alert_threshold_amount"]) == 5000.00

    async def test_get_nonexistent_bank_account(self, client):
        """Test getting non-existent bank account returns 404."""
        fake_id = str(uuid4())
        response = client.get(f"/bank-accounts/{fake_id}")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestTransactions:
    """Test transaction management endpoints."""

    async def test_list_transactions(
        self,
        client,
        customer_id,
        sample_transaction,
    ):
        """Test listing transactions."""
        response = client.get(f"/transactions?customer_id={customer_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == str(sample_transaction.id)

    async def test_list_flagged_transactions_only(
        self,
        client,
        customer_id,
        db_session,
        bank_account,
    ):
        """Test filtering flagged transactions."""
        from datetime import datetime
        from decimal import Decimal

        # Create flagged transaction
        flagged_txn = Transaction(
            bank_account_id=bank_account.id,
            plaid_transaction_id="flagged_txn",
            transaction_date=datetime.utcnow(),
            amount=Decimal("10000.00"),
            fraud_score=0.95,
            is_flagged=True,
        )
        db_session.add(flagged_txn)
        await db_session.commit()

        response = client.get(
            f"/transactions?customer_id={customer_id}&flagged_only=true"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["is_flagged"] is True

    async def test_get_transaction_analysis(
        self,
        client,
        sample_transaction,
    ):
        """Test getting detailed transaction analysis."""
        response = client.get(f"/transactions/{sample_transaction.id}")

        assert response.status_code == 200
        data = response.json()
        assert "transaction" in data
        assert "model_predictions" in data
        assert "recommendation" in data

    async def test_batch_transaction_analysis(
        self,
        client,
        db_session,
        bank_account,
    ):
        """Test analyzing multiple transactions in batch."""
        from datetime import datetime
        from decimal import Decimal

        # Create multiple transactions
        txn_ids = []
        for i in range(3):
            txn = Transaction(
                bank_account_id=bank_account.id,
                plaid_transaction_id=f"batch_txn_{i}",
                transaction_date=datetime.utcnow(),
                amount=Decimal(f"{100 * (i + 1)}.00"),
            )
            db_session.add(txn)
            await db_session.flush()
            txn_ids.append(str(txn.id))

        await db_session.commit()

        request_data = {
            "transaction_ids": txn_ids,
            "force_reanalysis": False,
        }

        response = client.post("/transactions/analyze-batch", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] >= 0
        assert "processing_time_seconds" in data


@pytest.mark.asyncio
class TestFraudCases:
    """Test fraud case management endpoints."""

    async def test_create_fraud_case(
        self,
        client,
        customer_id,
        bank_account,
        sample_transaction,
    ):
        """Test creating fraud case."""
        user_id = str(uuid4())

        case_data = {
            "customer_id": customer_id,
            "bank_account_id": str(bank_account.id),
            "transaction_id": str(sample_transaction.id),
            "title": "Suspicious Transaction Detected",
            "description": "Large unusual transaction",
            "severity": "high",
            "fraud_type": "suspicious_transaction",
            "estimated_loss_amount": 1000.00,
        }

        response = client.post(
            f"/fraud-cases?user_id={user_id}",
            json=case_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == case_data["title"]
        assert data["severity"] == "high"
        assert "case_number" in data

    async def test_list_fraud_cases(
        self,
        client,
        db_session,
        customer_id,
    ):
        """Test listing fraud cases."""
        from app.models import FraudSeverity

        # Create test case
        fraud_case = FraudCase(
            case_number="FRAUD-TEST-001",
            customer_id=customer_id,
            title="Test Case",
            severity=FraudSeverity.MEDIUM,
        )
        db_session.add(fraud_case)
        await db_session.commit()

        response = client.get(f"/fraud-cases?customer_id={customer_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    async def test_update_fraud_case(
        self,
        client,
        db_session,
        customer_id,
    ):
        """Test updating fraud case."""
        from app.models import FraudCaseStatus, FraudSeverity

        # Create test case
        fraud_case = FraudCase(
            case_number="FRAUD-TEST-002",
            customer_id=customer_id,
            title="Test Case",
            severity=FraudSeverity.MEDIUM,
            status=FraudCaseStatus.OPEN,
        )
        db_session.add(fraud_case)
        await db_session.commit()
        await db_session.refresh(fraud_case)

        user_id = str(uuid4())

        update_data = {
            "status": "investigating",
            "assigned_to": user_id,
            "investigation_notes": "Starting investigation",
        }

        response = client.patch(
            f"/fraud-cases/{fraud_case.id}?user_id={user_id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "investigating"
        assert data["assigned_to"] == user_id

    async def test_get_case_activities(
        self,
        client,
        db_session,
        customer_id,
    ):
        """Test getting case activity history."""
        from app.models import CaseActivity, FraudSeverity

        # Create case with activities
        fraud_case = FraudCase(
            case_number="FRAUD-TEST-003",
            customer_id=customer_id,
            title="Test Case",
            severity=FraudSeverity.HIGH,
        )
        db_session.add(fraud_case)
        await db_session.flush()

        activity = CaseActivity(
            fraud_case_id=fraud_case.id,
            activity_type="case_created",
            description="Case created",
            user_id=uuid4(),
        )
        db_session.add(activity)
        await db_session.commit()

        response = client.get(f"/fraud-cases/{fraud_case.id}/activities")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1


@pytest.mark.asyncio
class TestStatistics:
    """Test statistics and dashboard endpoints."""

    async def test_get_statistics(
        self,
        client,
        customer_id,
        sample_transaction,
    ):
        """Test getting fraud detection statistics."""
        response = client.get(f"/statistics?customer_id={customer_id}")

        assert response.status_code == 200
        data = response.json()
        assert "total_transactions" in data
        assert "flagged_transactions" in data
        assert "total_cases" in data
        assert "average_fraud_score" in data

    async def test_get_dashboard_metrics(self, client):
        """Test getting dashboard metrics."""
        response = client.get("/dashboard")

        assert response.status_code == 200
        data = response.json()
        assert "today_transactions" in data
        assert "open_cases" in data
        assert "new_alerts" in data
        assert "total_monitored_accounts" in data
        assert "active_customers" in data
        assert "top_fraud_types" in data
        assert "recent_alerts" in data


@pytest.mark.asyncio
class TestWebhooks:
    """Test webhook handling."""

    async def test_plaid_webhook_transaction_update(
        self,
        client,
        bank_account,
    ):
        """Test handling Plaid transaction webhook."""
        webhook_data = {
            "webhook_type": "TRANSACTIONS",
            "webhook_code": "DEFAULT_UPDATE",
            "item_id": bank_account.plaid_item_id,
            "new_transactions": 5,
        }

        response = client.post("/webhooks/plaid", json=webhook_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["processed", "ignored"]

    async def test_plaid_webhook_item_error(
        self,
        client,
        bank_account,
    ):
        """Test handling Plaid item error webhook."""
        webhook_data = {
            "webhook_type": "ITEM",
            "webhook_code": "ERROR",
            "item_id": bank_account.plaid_item_id,
            "error": {
                "error_code": "ITEM_LOGIN_REQUIRED",
                "error_message": "User needs to re-authenticate",
            },
        }

        response = client.post("/webhooks/plaid", json=webhook_data)

        assert response.status_code == 200
        # Should update bank account status to ERROR
