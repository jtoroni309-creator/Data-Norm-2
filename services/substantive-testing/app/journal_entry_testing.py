"""
Journal Entry Testing Service

Implements automated journal entry testing for fraud detection and anomaly identification.

PCAOB AS 2401 (Fraud) requires testing of journal entries and adjustments,
especially focusing on entries that:
- Are made at the end of a reporting period
- Are not part of the normal course of business
- Lack adequate documentation or approval
- Contain round numbers
- Are posted by unusual persons
- Are posted outside normal business hours
"""

import logging
from datetime import datetime, time
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import re
from collections import Counter

logger = logging.getLogger(__name__)


class JournalEntryTestingService:
    """
    Automated journal entry testing for fraud risk assessment.

    Tests include:
    - Round dollar testing
    - Weekend/after-hours posting detection
    - Unusual account combinations
    - High-risk accounts testing
    - Manual entry identification
    - Lack of documentation flags
    - Authorization bypass detection
    """

    # High-risk accounts often used in fraud
    HIGH_RISK_ACCOUNTS = [
        "Revenue",
        "Accounts Receivable",
        "Allowance for Doubtful Accounts",
        "Inventory",
        "Reserve",
        "Accrued",
        "Deferred Revenue",
        "Contingent Liability",
        "Gain on Sale",
        "Loss on",
    ]

    # Accounts that should rarely have manual entries
    AUTOMATED_ACCOUNTS = [
        "Cash",
        "Accounts Payable",
        "Payroll Expense",
        "Depreciation",
        "Cost of Goods Sold",
    ]

    def __init__(self):
        """Initialize journal entry testing service."""
        self.business_hours_start = time(8, 0)  # 8:00 AM
        self.business_hours_end = time(18, 0)   # 6:00 PM

    def test_round_dollar_amounts(
        self,
        journal_entries: List[Dict],
        threshold_amount: Decimal = Decimal("10000"),
    ) -> List[Dict]:
        """
        Identify journal entries with suspicious round dollar amounts.

        Round numbers (especially large ones) may indicate estimation or manipulation.

        Args:
            journal_entries: List of journal entry dictionaries
            threshold_amount: Minimum amount to consider (default $10,000)

        Returns:
            List of suspicious entries with risk scores
        """
        suspicious_entries = []

        for entry in journal_entries:
            amount = Decimal(str(entry.get("amount", 0)))

            # Skip if below threshold
            if abs(amount) < threshold_amount:
                continue

            # Check if round number
            is_round = self._is_round_number(amount)

            if is_round:
                risk_score = self._calculate_round_number_risk(amount, entry)
                suspicious_entries.append({
                    **entry,
                    "test_failed": "round_dollar",
                    "risk_score": risk_score,
                    "risk_factors": self._get_round_number_factors(amount, entry),
                })

        return suspicious_entries

    def test_after_hours_posting(
        self,
        journal_entries: List[Dict],
    ) -> List[Dict]:
        """
        Identify entries posted outside normal business hours or on weekends.

        Fraud schemes often involve entries made when less scrutiny is present.

        Args:
            journal_entries: List of journal entry dictionaries with 'posted_datetime'

        Returns:
            List of after-hours entries with risk assessment
        """
        suspicious_entries = []

        for entry in journal_entries:
            posted_dt = entry.get("posted_datetime")
            if not posted_dt:
                continue

            if isinstance(posted_dt, str):
                posted_dt = datetime.fromisoformat(posted_dt)

            # Check if weekend
            is_weekend = posted_dt.weekday() in [5, 6]  # Saturday, Sunday

            # Check if outside business hours
            posted_time = posted_dt.time()
            is_after_hours = not (self.business_hours_start <= posted_time <= self.business_hours_end)

            if is_weekend or is_after_hours:
                risk_score = 0.6 if is_weekend else 0.4
                suspicious_entries.append({
                    **entry,
                    "test_failed": "after_hours_posting",
                    "risk_score": risk_score,
                    "is_weekend": is_weekend,
                    "is_after_hours": is_after_hours,
                    "posted_datetime": posted_dt.isoformat(),
                })

        return suspicious_entries

    def test_unusual_account_combinations(
        self,
        journal_entries: List[Dict],
        historical_combinations: Optional[List[Tuple[str, str]]] = None,
    ) -> List[Dict]:
        """
        Identify entries with unusual debit/credit account combinations.

        Compares to historical patterns to find anomalies.

        Args:
            journal_entries: List of journal entry dictionaries
            historical_combinations: List of (debit_account, credit_account) tuples seen historically

        Returns:
            List of entries with unusual combinations
        """
        if historical_combinations is None:
            historical_combinations = []

        historical_set = set(historical_combinations)
        suspicious_entries = []

        for entry in journal_entries:
            debit_account = entry.get("debit_account", "")
            credit_account = entry.get("credit_account", "")

            combination = (debit_account, credit_account)

            # Check if this combination has been seen before
            if combination not in historical_set:
                risk_score = 0.5
                suspicious_entries.append({
                    **entry,
                    "test_failed": "unusual_account_combination",
                    "risk_score": risk_score,
                    "debit_account": debit_account,
                    "credit_account": credit_account,
                    "reason": "Account combination not seen in historical data",
                })

        return suspicious_entries

    def test_high_risk_accounts(
        self,
        journal_entries: List[Dict],
    ) -> List[Dict]:
        """
        Identify entries to high-risk accounts.

        High-risk accounts are often targets for financial statement manipulation.

        Args:
            journal_entries: List of journal entry dictionaries

        Returns:
            List of entries affecting high-risk accounts
        """
        high_risk_entries = []

        for entry in journal_entries:
            debit_account = entry.get("debit_account", "")
            credit_account = entry.get("credit_account", "")

            # Check if either account is high-risk
            is_high_risk = False
            for risk_account in self.HIGH_RISK_ACCOUNTS:
                if risk_account.lower() in debit_account.lower() or risk_account.lower() in credit_account.lower():
                    is_high_risk = True
                    break

            if is_high_risk:
                risk_score = 0.4  # Base score, can be adjusted
                high_risk_entries.append({
                    **entry,
                    "test_failed": "high_risk_account",
                    "risk_score": risk_score,
                })

        return high_risk_entries

    def test_period_end_entries(
        self,
        journal_entries: List[Dict],
        period_end_date: datetime,
        days_before_end: int = 3,
    ) -> List[Dict]:
        """
        Identify entries made near period end.

        Entries near period end have higher fraud risk, especially adjusting entries.

        Args:
            journal_entries: List of journal entry dictionaries
            period_end_date: Period end date
            days_before_end: Number of days before period end to flag (default 3)

        Returns:
            List of period-end entries
        """
        period_end_entries = []

        cutoff_date = period_end_date - timedelta(days=days_before_end)

        for entry in journal_entries:
            posted_dt = entry.get("posted_datetime")
            if not posted_dt:
                continue

            if isinstance(posted_dt, str):
                posted_dt = datetime.fromisoformat(posted_dt)

            # Check if within period-end window
            if cutoff_date <= posted_dt <= period_end_date:
                # Higher risk if also manual entry
                is_manual = entry.get("entry_type", "").lower() == "manual"
                risk_score = 0.6 if is_manual else 0.4

                period_end_entries.append({
                    **entry,
                    "test_failed": "period_end_entry",
                    "risk_score": risk_score,
                    "days_before_period_end": (period_end_date - posted_dt).days,
                })

        return period_end_entries

    def test_manual_entries_to_automated_accounts(
        self,
        journal_entries: List[Dict],
    ) -> List[Dict]:
        """
        Identify manual entries to accounts that should be automated.

        Manual entries to normally-automated accounts may indicate override or manipulation.

        Args:
            journal_entries: List of journal entry dictionaries

        Returns:
            List of suspicious manual entries
        """
        suspicious_entries = []

        for entry in journal_entries:
            is_manual = entry.get("entry_type", "").lower() in ["manual", "adjusting"]

            if not is_manual:
                continue

            debit_account = entry.get("debit_account", "")
            credit_account = entry.get("credit_account", "")

            # Check if affects automated accounts
            affects_automated = False
            for auto_account in self.AUTOMATED_ACCOUNTS:
                if auto_account.lower() in debit_account.lower() or auto_account.lower() in credit_account.lower():
                    affects_automated = True
                    break

            if affects_automated:
                risk_score = 0.7  # High risk for manual entry to automated account
                suspicious_entries.append({
                    **entry,
                    "test_failed": "manual_entry_to_automated_account",
                    "risk_score": risk_score,
                })

        return suspicious_entries

    def test_authorization_bypass(
        self,
        journal_entries: List[Dict],
        approval_required_threshold: Decimal = Decimal("50000"),
    ) -> List[Dict]:
        """
        Identify entries that should require approval but lack it.

        Args:
            journal_entries: List of journal entry dictionaries
            approval_required_threshold: Amount threshold requiring approval

        Returns:
            List of entries lacking required approval
        """
        unauthorized_entries = []

        for entry in journal_entries:
            amount = Decimal(str(entry.get("amount", 0)))
            approved_by = entry.get("approved_by")

            # Check if amount exceeds threshold and lacks approval
            if abs(amount) >= approval_required_threshold and not approved_by:
                risk_score = 0.8  # High risk for lack of authorization
                unauthorized_entries.append({
                    **entry,
                    "test_failed": "authorization_bypass",
                    "risk_score": risk_score,
                    "required_approval_amount": float(approval_required_threshold),
                })

        return unauthorized_entries

    def perform_comprehensive_je_testing(
        self,
        journal_entries: List[Dict],
        period_end_date: datetime,
        historical_combinations: Optional[List[Tuple[str, str]]] = None,
    ) -> Dict[str, List[Dict]]:
        """
        Perform all journal entry tests and return comprehensive results.

        Args:
            journal_entries: List of all journal entries to test
            period_end_date: Period end date for timing tests
            historical_combinations: Historical account combinations for comparison

        Returns:
            Dictionary with test results by category and overall risk assessment
        """
        results = {
            "round_dollar": self.test_round_dollar_amounts(journal_entries),
            "after_hours": self.test_after_hours_posting(journal_entries),
            "unusual_combinations": self.test_unusual_account_combinations(
                journal_entries, historical_combinations
            ),
            "high_risk_accounts": self.test_high_risk_accounts(journal_entries),
            "period_end": self.test_period_end_entries(journal_entries, period_end_date),
            "manual_to_automated": self.test_manual_entries_to_automated_accounts(journal_entries),
            "authorization_bypass": self.test_authorization_bypass(journal_entries),
        }

        # Calculate overall statistics
        total_entries = len(journal_entries)
        total_exceptions = sum(len(exceptions) for exceptions in results.values())
        exception_rate = total_exceptions / total_entries if total_entries > 0 else 0

        # Identify high-risk entries (appearing in multiple tests)
        entry_id_counter = Counter()
        for test_results in results.values():
            for entry in test_results:
                entry_id = entry.get("id")
                if entry_id:
                    entry_id_counter[entry_id] += 1

        high_risk_entry_ids = [
            entry_id for entry_id, count in entry_id_counter.items() if count >= 2
        ]

        results["summary"] = {
            "total_entries_tested": total_entries,
            "total_exceptions": total_exceptions,
            "exception_rate": round(exception_rate, 4),
            "high_risk_entries": len(high_risk_entry_ids),
            "high_risk_entry_ids": high_risk_entry_ids,
            "tests_performed": list(results.keys()),
        }

        return results

    # Helper methods

    def _is_round_number(self, amount: Decimal) -> bool:
        """Check if amount is a suspicious round number."""
        abs_amount = abs(amount)

        # Check for exact thousands, ten-thousands, hundred-thousands, millions
        if abs_amount % 1000 == 0 and abs_amount >= 10000:
            return True

        # Check for amounts ending in 00 or 0000
        str_amount = str(int(abs_amount))
        if str_amount.endswith("00") and len(str_amount) >= 5:
            return True

        return False

    def _calculate_round_number_risk(self, amount: Decimal, entry: Dict) -> float:
        """Calculate risk score for round number entry."""
        risk_score = 0.3  # Base score for round number

        # Increase risk if also manual entry
        if entry.get("entry_type", "").lower() == "manual":
            risk_score += 0.2

        # Increase risk if large amount
        if abs(amount) > 100000:
            risk_score += 0.2

        # Increase risk if to high-risk account
        debit = entry.get("debit_account", "").lower()
        credit = entry.get("credit_account", "").lower()
        for high_risk in self.HIGH_RISK_ACCOUNTS:
            if high_risk.lower() in debit or high_risk.lower() in credit:
                risk_score += 0.2
                break

        return min(risk_score, 1.0)  # Cap at 1.0

    def _get_round_number_factors(self, amount: Decimal, entry: Dict) -> List[str]:
        """Get list of risk factors for round number entry."""
        factors = ["Round dollar amount"]

        if entry.get("entry_type", "").lower() == "manual":
            factors.append("Manual entry")

        if abs(amount) > 100000:
            factors.append("Large amount (>$100,000)")

        debit = entry.get("debit_account", "").lower()
        credit = entry.get("credit_account", "").lower()
        for high_risk in self.HIGH_RISK_ACCOUNTS:
            if high_risk.lower() in debit or high_risk.lower() in credit:
                factors.append(f"Affects high-risk account ({high_risk})")
                break

        return factors


from datetime import timedelta  # Add this import at top
