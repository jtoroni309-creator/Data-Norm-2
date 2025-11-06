"""
Comprehensive Test Suite for Journal Entry Testing Service

Tests all 7 automated fraud detection tests.
"""

import pytest
from datetime import datetime, timedelta

from app.journal_entry_testing import JournalEntryTestingService


class TestJournalEntryTesting:
    """Test journal entry fraud detection"""

    @pytest.fixture
    def je_service(self):
        return JournalEntryTestingService()

    @pytest.fixture
    def sample_entries(self):
        return [
            {
                "id": "JE001",
                "amount": 100000,  # Round dollar
                "debit_account": "Revenue",
                "credit_account": "Accounts Receivable",
                "posted_datetime": datetime(2025, 12, 31, 20, 0),  # After hours
                "entry_type": "manual",
                "approved_by": None,
            },
            {
                "id": "JE002",
                "amount": 45237.82,
                "debit_account": "Cash",
                "credit_account": "Revenue",
                "posted_datetime": datetime(2025, 12, 15, 10, 0),
                "entry_type": "automated",
                "approved_by": "supervisor@example.com",
            },
            {
                "id": "JE003",
                "amount": 250000,  # Round dollar
                "debit_account": "Inventory",
                "credit_account": "Accounts Payable",
                "posted_datetime": datetime(2025, 12, 28, 14, 0),  # Near period end
                "entry_type": "manual",
                "approved_by": None,  # Missing approval
            },
        ]

    def test_round_dollar_detection(self, je_service, sample_entries):
        """Test round dollar amount detection"""
        results = je_service.test_round_dollar_amounts(sample_entries)

        assert len(results) == 2  # JE001 and JE003
        assert all(r["test_failed"] == "round_dollar" for r in results)
        assert all(r["risk_score"] > 0 for r in results)

    def test_after_hours_detection(self, je_service, sample_entries):
        """Test after-hours posting detection"""
        results = je_service.test_after_hours_posting(sample_entries)

        # JE001 was posted at 8 PM (after hours)
        assert len(results) >= 1
        assert any(r["id"] == "JE001" for r in results)

    def test_high_risk_accounts(self, je_service, sample_entries):
        """Test high-risk account identification"""
        results = je_service.test_high_risk_accounts(sample_entries)

        # Should flag Revenue, Accounts Receivable, Inventory
        assert len(results) >= 2

    def test_authorization_bypass(self, je_service, sample_entries):
        """Test authorization bypass detection"""
        results = je_service.test_authorization_bypass(sample_entries)

        # JE001 and JE003 lack approval and exceed $50k
        assert len(results) == 2
        assert all(r["test_failed"] == "authorization_bypass" for r in results)
        assert all(r["risk_score"] == 0.8 for r in results)

    def test_comprehensive_testing(self, je_service, sample_entries):
        """Test comprehensive JE testing workflow"""
        period_end = datetime(2025, 12, 31)

        results = je_service.perform_comprehensive_je_testing(
            sample_entries,
            period_end,
            historical_combinations=[]
        )

        assert "summary" in results
        assert results["summary"]["total_entries_tested"] == 3
        assert results["summary"]["total_exceptions"] > 0
        assert len(results["summary"]["tests_performed"]) == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
