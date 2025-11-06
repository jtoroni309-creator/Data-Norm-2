"""
Analytics Engine - JE Testing and Anomaly Detection

Implements:
1. Journal Entry Testing (round-dollar, weekend, period-end)
2. Anomaly Detection (Z-score, Isolation Forest)
3. Ratio Analysis
4. ML Model Integration
"""
import logging
import numpy as np
from datetime import datetime, date
from typing import List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .schemas import JETestResult, RatioResult

logger = logging.getLogger(__name__)


# ========================================
# Journal Entry Testing
# ========================================

class JournalEntryTester:
    """Test journal entries for suspicious patterns"""

    @staticmethod
    async def test_round_dollar_entries(
        engagement_id: UUID,
        db: AsyncSession
    ) -> List[JETestResult]:
        """
        Detect round-dollar journal entries

        Round-dollar entries (e.g., $10,000.00, $50,000.00) can indicate
        manual adjustments or estimation bias and warrant investigation.

        Method: Check if entry total is divisible by 100, 1000, or 10000
        with minimal decimal remainder.
        """
        query = text("""
            WITH entry_totals AS (
                SELECT
                    je.id,
                    je.entry_number,
                    je.entry_date,
                    SUM(COALESCE(jel.debit_amount, 0)) as total_amount,
                    je.is_manual
                FROM atlas.journal_entries je
                JOIN atlas.journal_entry_lines jel ON jel.journal_entry_id = je.id
                WHERE je.engagement_id = :engagement_id
                GROUP BY je.id, je.entry_number, je.entry_date, je.is_manual
                HAVING SUM(COALESCE(jel.debit_amount, 0)) > 0
            )
            SELECT
                id,
                entry_number,
                entry_date,
                total_amount,
                is_manual,
                -- Check if divisible by 100, 1000, or 10000
                (total_amount % 100) as mod_100,
                (total_amount % 1000) as mod_1000,
                (total_amount % 10000) as mod_10000
            FROM entry_totals
            WHERE
                (total_amount % 100) < :threshold * 100
                OR (total_amount % 1000) < :threshold * 1000
                OR (total_amount % 10000) < :threshold * 10000
            ORDER BY total_amount DESC
        """)

        result = await db.execute(
            query,
            {
                "engagement_id": engagement_id,
                "threshold": settings.ROUND_DOLLAR_THRESHOLD
            }
        )

        results = []
        for row in result.fetchall():
            je_id, entry_number, entry_date, amount, is_manual, mod_100, mod_1000, mod_10000 = row

            # Determine which threshold was hit
            if mod_10000 < settings.ROUND_DOLLAR_THRESHOLD * 10000:
                reason = f"Round to nearest $10,000 (${amount:,.2f})"
                score = 0.9
            elif mod_1000 < settings.ROUND_DOLLAR_THRESHOLD * 1000:
                reason = f"Round to nearest $1,000 (${amount:,.2f})"
                score = 0.7
            else:
                reason = f"Round to nearest $100 (${amount:,.2f})"
                score = 0.5

            results.append(JETestResult(
                test_type="round_dollar",
                journal_entry_id=je_id,
                entry_number=entry_number,
                entry_date=entry_date,
                amount=float(amount),
                flagged=True,
                reason=reason,
                score=score
            ))

        logger.info(f"Round-dollar test found {len(results)} flagged entries")
        return results

    @staticmethod
    async def test_weekend_entries(
        engagement_id: UUID,
        db: AsyncSession
    ) -> List[JETestResult]:
        """
        Detect journal entries posted on weekends

        Entries posted on Saturday/Sunday may indicate backdating
        or unusual posting patterns warranting investigation.
        """
        query = text("""
            WITH entry_totals AS (
                SELECT
                    je.id,
                    je.entry_number,
                    je.entry_date,
                    je.posted_date,
                    EXTRACT(DOW FROM je.posted_date) as day_of_week,
                    SUM(COALESCE(jel.debit_amount, 0)) as total_amount
                FROM atlas.journal_entries je
                JOIN atlas.journal_entry_lines jel ON jel.journal_entry_id = je.id
                WHERE je.engagement_id = :engagement_id
                    AND je.posted_date IS NOT NULL
                GROUP BY je.id, je.entry_number, je.entry_date, je.posted_date
            )
            SELECT
                id,
                entry_number,
                entry_date,
                posted_date,
                day_of_week,
                total_amount
            FROM entry_totals
            WHERE day_of_week IN (0, 6)  -- Sunday=0, Saturday=6
            ORDER BY posted_date DESC
        """)

        result = await db.execute(query, {"engagement_id": engagement_id})

        results = []
        for row in result.fetchall():
            je_id, entry_number, entry_date, posted_date, dow, amount = row

            day_name = "Sunday" if dow == 0 else "Saturday"
            reason = f"Posted on {day_name} ({posted_date.strftime('%Y-%m-%d')})"

            results.append(JETestResult(
                test_type="weekend",
                journal_entry_id=je_id,
                entry_number=entry_number,
                entry_date=entry_date,
                amount=float(amount),
                flagged=True,
                reason=reason,
                score=0.8
            ))

        logger.info(f"Weekend test found {len(results)} flagged entries")
        return results

    @staticmethod
    async def test_period_end_entries(
        engagement_id: UUID,
        db: AsyncSession,
        days_before_close: int = 3
    ) -> List[JETestResult]:
        """
        Detect journal entries near period-end

        Entries posted in the last few days of a period may indicate
        earnings management or aggressive accounting.
        """
        query = text("""
            WITH engagement_period AS (
                SELECT fiscal_year_end
                FROM atlas.engagements
                WHERE id = :engagement_id
            ),
            entry_totals AS (
                SELECT
                    je.id,
                    je.entry_number,
                    je.entry_date,
                    SUM(COALESCE(jel.debit_amount, 0)) as total_amount,
                    (SELECT fiscal_year_end FROM engagement_period) as period_end,
                    (SELECT fiscal_year_end FROM engagement_period) - je.entry_date::date as days_to_close
                FROM atlas.journal_entries je
                JOIN atlas.journal_entry_lines jel ON jel.journal_entry_id = je.id
                WHERE je.engagement_id = :engagement_id
                GROUP BY je.id, je.entry_number, je.entry_date
            )
            SELECT
                id,
                entry_number,
                entry_date,
                total_amount,
                days_to_close
            FROM entry_totals
            WHERE days_to_close >= 0 AND days_to_close <= :days_before_close
                AND total_amount > 10000  -- Material amounts only
            ORDER BY days_to_close ASC, total_amount DESC
        """)

        result = await db.execute(
            query,
            {
                "engagement_id": engagement_id,
                "days_before_close": days_before_close
            }
        )

        results = []
        for row in result.fetchall():
            je_id, entry_number, entry_date, amount, days_to_close = row

            reason = f"Posted {days_to_close} day(s) before period-end (${amount:,.2f})"
            score = 1.0 - (days_to_close / days_before_close) * 0.5  # Closer = higher score

            results.append(JETestResult(
                test_type="period_end",
                journal_entry_id=je_id,
                entry_number=entry_number,
                entry_date=entry_date,
                amount=float(amount),
                flagged=True,
                reason=reason,
                score=score
            ))

        logger.info(f"Period-end test found {len(results)} flagged entries")
        return results


# ========================================
# Anomaly Detection
# ========================================

class AnomalyDetector:
    """Detect anomalies using statistical and ML methods"""

    @staticmethod
    async def detect_outliers_zscore(
        engagement_id: UUID,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Detect outliers using Z-score method

        Identifies account balances that are more than N standard deviations
        away from the mean (default: 3.0 std devs).
        """
        query = text("""
            WITH account_stats AS (
                SELECT
                    tb.account_code,
                    tb.account_name,
                    tb.balance_amount,
                    AVG(tb.balance_amount) OVER (PARTITION BY tb.account_code) as mean_balance,
                    STDDEV(tb.balance_amount) OVER (PARTITION BY tb.account_code) as stddev_balance,
                    COUNT(*) OVER (PARTITION BY tb.account_code) as sample_count
                FROM atlas.trial_balance_lines tb
                JOIN atlas.trial_balances tbal ON tbal.id = tb.trial_balance_id
                WHERE tbal.engagement_id = :engagement_id
            )
            SELECT
                account_code,
                account_name,
                balance_amount,
                mean_balance,
                stddev_balance,
                CASE
                    WHEN stddev_balance > 0 THEN
                        ABS((balance_amount - mean_balance) / stddev_balance)
                    ELSE 0
                END as z_score,
                sample_count
            FROM account_stats
            WHERE stddev_balance > 0
                AND ABS((balance_amount - mean_balance) / stddev_balance) > :threshold
                AND sample_count >= 3  -- Minimum sample size
            ORDER BY z_score DESC
        """)

        result = await db.execute(
            query,
            {
                "engagement_id": engagement_id,
                "threshold": settings.OUTLIER_Z_SCORE_THRESHOLD
            }
        )

        outliers = []
        for row in result.fetchall():
            account_code, account_name, balance, mean, stddev, z_score, count = row

            outliers.append({
                "account_code": account_code,
                "account_name": account_name,
                "balance_amount": float(balance),
                "mean_balance": float(mean),
                "stddev_balance": float(stddev),
                "z_score": float(z_score),
                "severity": "critical" if z_score > 5.0 else "high" if z_score > 4.0 else "medium"
            })

        logger.info(f"Z-score detection found {len(outliers)} outliers")
        return outliers

    @staticmethod
    def detect_outliers_isolation_forest(
        data: np.ndarray,
        contamination: float = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect outliers using Isolation Forest

        Isolation Forest is an ML algorithm that isolates anomalies instead
        of profiling normal data points.

        Note: Requires scikit-learn. Returns predictions and anomaly scores.
        """
        try:
            from sklearn.ensemble import IsolationForest

            if contamination is None:
                contamination = settings.ISOLATION_FOREST_CONTAMINATION

            model = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )

            # Fit and predict (-1 for anomalies, 1 for normal)
            predictions = model.fit_predict(data)

            # Get anomaly scores (lower = more anomalous)
            scores = model.score_samples(data)

            logger.info(f"Isolation Forest detected {np.sum(predictions == -1)} anomalies")

            return predictions, scores

        except ImportError:
            logger.warning("scikit-learn not installed, skipping Isolation Forest")
            return np.ones(len(data)), np.zeros(len(data))


# ========================================
# Ratio Analysis
# ========================================

class RatioAnalyzer:
    """Calculate and analyze financial ratios"""

    @staticmethod
    async def calculate_current_ratio(
        engagement_id: UUID,
        db: AsyncSession
    ) -> RatioResult:
        """
        Calculate Current Ratio = Current Assets / Current Liabilities

        Benchmark: 1.5 to 3.0 is typical for most industries
        """
        query = text("""
            SELECT
                SUM(CASE WHEN coa.account_subtype = 'current_asset' THEN tb.balance_amount ELSE 0 END) as current_assets,
                SUM(CASE WHEN coa.account_subtype = 'current_liability' THEN ABS(tb.balance_amount) ELSE 0 END) as current_liabilities
            FROM atlas.trial_balance_lines tb
            JOIN atlas.trial_balances tbal ON tbal.id = tb.trial_balance_id
            LEFT JOIN atlas.chart_of_accounts coa ON coa.id = tb.mapped_account_id
            WHERE tbal.engagement_id = :engagement_id
        """)

        result = await db.execute(query, {"engagement_id": engagement_id})
        row = result.fetchone()

        current_assets = float(row[0]) if row and row[0] else 0
        current_liabilities = float(row[1]) if row and row[1] else 1  # Avoid division by zero

        ratio = current_assets / current_liabilities if current_liabilities != 0 else 0
        benchmark = 2.0
        deviation = abs(ratio - benchmark) / benchmark

        return RatioResult(
            ratio_name="Current Ratio",
            value=round(ratio, 2),
            benchmark=benchmark,
            deviation=round(deviation, 2),
            is_outlier=(ratio < 1.0 or ratio > 4.0)  # Outside reasonable range
        )

    @staticmethod
    async def calculate_quick_ratio(
        engagement_id: UUID,
        db: AsyncSession
    ) -> RatioResult:
        """
        Calculate Quick Ratio = (Current Assets - Inventory) / Current Liabilities

        Benchmark: 1.0 or higher indicates good liquidity
        """
        query = text("""
            SELECT
                SUM(CASE
                    WHEN coa.account_subtype = 'current_asset'
                        AND coa.account_name NOT ILIKE '%inventory%'
                    THEN tb.balance_amount
                    ELSE 0
                END) as quick_assets,
                SUM(CASE
                    WHEN coa.account_subtype = 'current_liability'
                    THEN ABS(tb.balance_amount)
                    ELSE 0
                END) as current_liabilities
            FROM atlas.trial_balance_lines tb
            JOIN atlas.trial_balances tbal ON tbal.id = tb.trial_balance_id
            LEFT JOIN atlas.chart_of_accounts coa ON coa.id = tb.mapped_account_id
            WHERE tbal.engagement_id = :engagement_id
        """)

        result = await db.execute(query, {"engagement_id": engagement_id})
        row = result.fetchone()

        quick_assets = float(row[0]) if row and row[0] else 0
        current_liabilities = float(row[1]) if row and row[1] else 1

        ratio = quick_assets / current_liabilities if current_liabilities != 0 else 0
        benchmark = 1.0
        deviation = abs(ratio - benchmark) / benchmark if benchmark != 0 else 0

        return RatioResult(
            ratio_name="Quick Ratio",
            value=round(ratio, 2),
            benchmark=benchmark,
            deviation=round(deviation, 2),
            is_outlier=(ratio < 0.5 or ratio > 3.0)
        )

    @staticmethod
    async def calculate_debt_to_equity(
        engagement_id: UUID,
        db: AsyncSession
    ) -> RatioResult:
        """
        Calculate Debt-to-Equity = Total Liabilities / Shareholders' Equity

        Benchmark: Varies by industry, typically 0.5 to 2.0
        """
        query = text("""
            SELECT
                SUM(CASE WHEN coa.account_type = 'liability' THEN ABS(tb.balance_amount) ELSE 0 END) as total_liabilities,
                SUM(CASE WHEN coa.account_type = 'equity' THEN ABS(tb.balance_amount) ELSE 0 END) as total_equity
            FROM atlas.trial_balance_lines tb
            JOIN atlas.trial_balances tbal ON tbal.id = tb.trial_balance_id
            LEFT JOIN atlas.chart_of_accounts coa ON coa.id = tb.mapped_account_id
            WHERE tbal.engagement_id = :engagement_id
        """)

        result = await db.execute(query, {"engagement_id": engagement_id})
        row = result.fetchone()

        total_liabilities = float(row[0]) if row and row[0] else 0
        total_equity = float(row[1]) if row and row[1] else 1

        ratio = total_liabilities / total_equity if total_equity != 0 else 0
        benchmark = 1.0
        deviation = abs(ratio - benchmark) / benchmark if benchmark != 0 else 0

        return RatioResult(
            ratio_name="Debt-to-Equity",
            value=round(ratio, 2),
            benchmark=benchmark,
            deviation=round(deviation, 2),
            is_outlier=(ratio > 3.0)  # Very high leverage
        )
