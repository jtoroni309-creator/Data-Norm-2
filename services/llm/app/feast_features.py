"""
Feast Feature Store Integration for Audit AI

Provides centralized feature management for ML models:
- Financial ratios and metrics
- Historical audit patterns
- Account behavior features
- Risk indicators
- Entity relationship features
- Temporal aggregations

Goal: Consistent, reusable features that improve model performance
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

logger = logging.getLogger(__name__)


class FeatureStore:
    """
    Feast-compatible feature store for audit AI

    Features are organized by entity:
    - Engagement features (engagement_id)
    - Account features (account_code)
    - Entity features (organization_id)
    - Temporal features (date-based aggregations)
    """

    def __init__(self):
        """Initialize feature store"""
        self.feature_cache = {}

    # =========================================================================
    # Engagement-Level Features
    # =========================================================================

    async def get_engagement_features(
        self,
        db: AsyncSession,
        engagement_id: UUID
    ) -> Dict[str, Any]:
        """
        Get comprehensive engagement-level features

        Features include:
        - Financial ratios
        - Entity size metrics
        - Risk indicators
        - Historical patterns
        - Team composition

        Returns:
            Dictionary of feature_name -> value
        """
        features = {}

        # 1. Basic engagement info
        basic_query = text("""
            SELECT
                e.engagement_type,
                e.status,
                EXTRACT(DAYS FROM CURRENT_DATE - e.fiscal_year_end) as days_since_fye,
                COUNT(DISTINCT etm.user_id) as team_size,
                COUNT(DISTINCT CASE WHEN u.role = 'partner' THEN u.id END) as partner_count,
                COUNT(DISTINCT CASE WHEN u.role IN ('manager', 'senior') THEN u.id END) as senior_staff_count
            FROM atlas.engagements e
            LEFT JOIN atlas.engagement_team_members etm ON etm.engagement_id = e.id
            LEFT JOIN atlas.users u ON u.id = etm.user_id
            WHERE e.id = :engagement_id
            GROUP BY e.id, e.engagement_type, e.status, e.fiscal_year_end
        """)

        result = await db.execute(basic_query, {"engagement_id": engagement_id})
        row = result.fetchone()

        if row:
            features["engagement_type"] = row[0]
            features["engagement_status"] = row[1]
            features["days_since_fye"] = int(row[2] or 0)
            features["team_size"] = int(row[3] or 0)
            features["has_partner"] = int(row[4] or 0) > 0
            features["senior_staff_ratio"] = float(row[5] or 0) / max(float(row[3] or 1), 1)

        # 2. Financial size metrics
        size_query = text("""
            SELECT
                COALESCE(SUM(CASE WHEN coa.account_type = 'asset' THEN tb.balance_amount END), 0) as total_assets,
                COALESCE(SUM(CASE WHEN coa.account_type = 'liability' THEN ABS(tb.balance_amount) END), 0) as total_liabilities,
                COALESCE(SUM(CASE WHEN coa.account_type = 'equity' THEN ABS(tb.balance_amount) END), 0) as total_equity,
                COALESCE(SUM(CASE WHEN coa.account_type = 'revenue' THEN ABS(tb.balance_amount) END), 0) as total_revenue,
                COUNT(DISTINCT tb.account_code) as account_count
            FROM atlas.trial_balance_lines tb
            JOIN atlas.trial_balances tbal ON tbal.id = tb.trial_balance_id
            LEFT JOIN atlas.chart_of_accounts coa ON coa.id = tb.mapped_account_id
            WHERE tbal.engagement_id = :engagement_id
        """)

        result = await db.execute(size_query, {"engagement_id": engagement_id})
        row = result.fetchone()

        if row:
            total_assets = float(row[0] or 0)
            total_liabilities = float(row[1] or 0)
            total_equity = float(row[2] or 0)
            total_revenue = float(row[3] or 0)

            features["total_assets"] = total_assets
            features["total_liabilities"] = total_liabilities
            features["total_equity"] = total_equity
            features["total_revenue"] = total_revenue
            features["account_count"] = int(row[4] or 0)

            # Log-scale for large numbers (ML-friendly)
            features["log_total_assets"] = np.log1p(total_assets)
            features["log_total_revenue"] = np.log1p(total_revenue)

            # Size category (for stratification)
            if total_assets < 1_000_000:
                features["size_category"] = "small"
            elif total_assets < 10_000_000:
                features["size_category"] = "medium"
            elif total_assets < 100_000_000:
                features["size_category"] = "large"
            else:
                features["size_category"] = "enterprise"

        # 3. Financial ratios
        if total_assets > 0:
            features["debt_to_assets"] = total_liabilities / total_assets
            features["equity_to_assets"] = total_equity / total_assets

        if total_equity > 0:
            features["debt_to_equity"] = total_liabilities / total_equity

        if total_assets > 0 and total_revenue > 0:
            features["asset_turnover"] = total_revenue / total_assets

        # 4. Risk indicators
        risk_query = text("""
            SELECT
                COUNT(*) as total_risks,
                COUNT(CASE WHEN fraud_risk = TRUE THEN 1 END) as fraud_risk_count,
                AVG(CASE
                    WHEN risk_level = 'high' THEN 3
                    WHEN risk_level = 'medium' THEN 2
                    WHEN risk_level = 'low' THEN 1
                    ELSE 0
                END) as avg_risk_level
            FROM atlas.risks
            WHERE engagement_id = :engagement_id
        """)

        result = await db.execute(risk_query, {"engagement_id": engagement_id})
        row = result.fetchone()

        if row:
            features["total_risks"] = int(row[0] or 0)
            features["fraud_risk_count"] = int(row[1] or 0)
            features["avg_risk_level"] = float(row[2] or 0)
            features["has_fraud_risk"] = features["fraud_risk_count"] > 0

        # 5. Analytics results
        analytics_query = text("""
            SELECT
                COUNT(DISTINCT a.id) as anomaly_count,
                COUNT(DISTINCT CASE WHEN a.severity = 'critical' THEN a.id END) as critical_anomalies,
                COUNT(DISTINCT CASE WHEN a.severity = 'high' THEN a.id END) as high_anomalies
            FROM atlas.anomalies a
            WHERE a.engagement_id = :engagement_id
        """)

        result = await db.execute(analytics_query, {"engagement_id": engagement_id})
        row = result.fetchone()

        if row:
            features["anomaly_count"] = int(row[0] or 0)
            features["critical_anomaly_count"] = int(row[1] or 0)
            features["high_anomaly_count"] = int(row[2] or 0)
            features["has_critical_anomalies"] = features["critical_anomaly_count"] > 0

        logger.info(f"Extracted {len(features)} engagement-level features")
        return features

    # =========================================================================
    # Account-Level Features
    # =========================================================================

    async def get_account_features(
        self,
        db: AsyncSession,
        engagement_id: UUID,
        account_code: str
    ) -> Dict[str, Any]:
        """
        Get account-level features for anomaly detection

        Features include:
        - Balance statistics
        - Transaction patterns
        - Historical comparisons
        - Volatility metrics
        """
        features = {}

        # 1. Current balance and account info
        account_query = text("""
            SELECT
                tb.balance_amount,
                tb.debit_amount,
                tb.credit_amount,
                coa.account_type,
                coa.account_subtype,
                coa.is_material
            FROM atlas.trial_balance_lines tb
            JOIN atlas.trial_balances tbal ON tbal.id = tb.trial_balance_id
            LEFT JOIN atlas.chart_of_accounts coa ON coa.id = tb.mapped_account_id
            WHERE tbal.engagement_id = :engagement_id
                AND tb.account_code = :account_code
            LIMIT 1
        """)

        result = await db.execute(
            account_query,
            {"engagement_id": engagement_id, "account_code": account_code}
        )
        row = result.fetchone()

        if row:
            balance = float(row[0] or 0)
            debit = float(row[1] or 0)
            credit = float(row[2] or 0)

            features["balance_amount"] = balance
            features["debit_amount"] = debit
            features["credit_amount"] = credit
            features["log_abs_balance"] = np.log1p(abs(balance))
            features["account_type"] = row[3]
            features["account_subtype"] = row[4]
            features["is_material"] = bool(row[5])

            # Activity ratio
            total_activity = debit + credit
            if total_activity > 0:
                features["net_activity_ratio"] = (debit - credit) / total_activity

        # 2. Journal entry patterns
        je_query = text("""
            SELECT
                COUNT(*) as entry_count,
                COUNT(CASE WHEN je.is_manual = TRUE THEN 1 END) as manual_entry_count,
                COUNT(CASE WHEN EXTRACT(DOW FROM je.posted_date) IN (0, 6) THEN 1 END) as weekend_entry_count,
                AVG(jel.debit_amount) as avg_entry_size,
                STDDEV(jel.debit_amount) as stddev_entry_size,
                MAX(jel.debit_amount) as max_entry_size
            FROM atlas.journal_entry_lines jel
            JOIN atlas.journal_entries je ON je.id = jel.journal_entry_id
            WHERE je.engagement_id = :engagement_id
                AND jel.account_code = :account_code
        """)

        result = await db.execute(
            je_query,
            {"engagement_id": engagement_id, "account_code": account_code}
        )
        row = result.fetchone()

        if row:
            entry_count = int(row[0] or 0)
            features["entry_count"] = entry_count
            features["manual_entry_count"] = int(row[1] or 0)
            features["weekend_entry_count"] = int(row[2] or 0)

            if entry_count > 0:
                features["manual_entry_ratio"] = float(row[1] or 0) / entry_count
                features["weekend_entry_ratio"] = float(row[2] or 0) / entry_count

            avg_size = float(row[3] or 0)
            stddev_size = float(row[4] or 0)
            max_size = float(row[5] or 0)

            features["avg_entry_size"] = avg_size
            features["stddev_entry_size"] = stddev_size
            features["max_entry_size"] = max_size

            # Coefficient of variation (volatility indicator)
            if avg_size > 0:
                features["entry_size_cv"] = stddev_size / avg_size

            # Outlier indicator
            if avg_size > 0 and stddev_size > 0:
                z_score = (max_size - avg_size) / stddev_size if stddev_size > 0 else 0
                features["max_entry_z_score"] = z_score
                features["has_outlier_entries"] = z_score > 3.0

        logger.info(f"Extracted {len(features)} account-level features for {account_code}")
        return features

    # =========================================================================
    # Entity-Level Features (Organization)
    # =========================================================================

    async def get_entity_features(
        self,
        db: AsyncSession,
        organization_id: UUID
    ) -> Dict[str, Any]:
        """
        Get organization-level features

        Features include:
        - Historical engagement metrics
        - Entity maturity
        - Compliance history
        """
        features = {}

        # 1. Organization basics
        org_query = text("""
            SELECT
                o.name,
                o.created_at,
                EXTRACT(DAYS FROM CURRENT_DATE - o.created_at) as days_since_created,
                COUNT(DISTINCT e.id) as total_engagements,
                COUNT(DISTINCT CASE WHEN e.status = 'finalized' THEN e.id END) as completed_engagements,
                COUNT(DISTINCT u.id) as total_users
            FROM atlas.organizations o
            LEFT JOIN atlas.engagements e ON e.client_id = o.id
            LEFT JOIN atlas.users u ON u.organization_id = o.id
            WHERE o.id = :organization_id
            GROUP BY o.id, o.name, o.created_at
        """)

        result = await db.execute(org_query, {"organization_id": organization_id})
        row = result.fetchone()

        if row:
            features["organization_name"] = row[0]
            features["days_since_created"] = int(row[2] or 0)
            total_engagements = int(row[3] or 0)
            completed_engagements = int(row[4] or 0)

            features["total_engagements"] = total_engagements
            features["completed_engagements"] = completed_engagements
            features["total_users"] = int(row[5] or 0)

            # Maturity indicator
            if total_engagements > 0:
                features["completion_rate"] = completed_engagements / total_engagements
                features["is_experienced_user"] = total_engagements >= 5

        logger.info(f"Extracted {len(features)} entity-level features")
        return features

    # =========================================================================
    # Temporal Features
    # =========================================================================

    async def get_temporal_features(
        self,
        db: AsyncSession,
        engagement_id: UUID,
        as_of_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get time-based features

        Features include:
        - Seasonality (month, quarter, year-end)
        - Days in fieldwork
        - Time to completion estimates
        """
        features = {}

        if as_of_date is None:
            as_of_date = datetime.utcnow()

        # Extract date components
        features["month"] = as_of_date.month
        features["quarter"] = (as_of_date.month - 1) // 3 + 1
        features["day_of_week"] = as_of_date.weekday()
        features["day_of_month"] = as_of_date.day
        features["is_month_end"] = as_of_date.day >= 28
        features["is_quarter_end"] = as_of_date.month in [3, 6, 9, 12] and as_of_date.day >= 28
        features["is_year_end"] = as_of_date.month == 12 and as_of_date.day >= 28

        # Engagement timeline
        timeline_query = text("""
            SELECT
                e.created_at,
                e.fiscal_year_end,
                EXTRACT(DAYS FROM :as_of_date - e.created_at) as days_in_progress
            FROM atlas.engagements e
            WHERE e.id = :engagement_id
        """)

        result = await db.execute(
            timeline_query,
            {"engagement_id": engagement_id, "as_of_date": as_of_date}
        )
        row = result.fetchone()

        if row:
            features["days_in_progress"] = int(row[2] or 0)

        logger.info(f"Extracted {len(features)} temporal features")
        return features

    # =========================================================================
    # Combined Feature Extraction
    # =========================================================================

    async def get_all_features(
        self,
        db: AsyncSession,
        engagement_id: UUID,
        account_code: Optional[str] = None,
        organization_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get all relevant features for an engagement

        Args:
            db: Database session
            engagement_id: Engagement ID
            account_code: Optional specific account to get features for
            organization_id: Optional organization ID

        Returns:
            Combined feature dictionary
        """
        all_features = {}

        # 1. Engagement features (always include)
        engagement_features = await self.get_engagement_features(db, engagement_id)
        all_features.update({f"eng_{k}": v for k, v in engagement_features.items()})

        # 2. Account features (if specified)
        if account_code:
            account_features = await self.get_account_features(db, engagement_id, account_code)
            all_features.update({f"acct_{k}": v for k, v in account_features.items()})

        # 3. Entity features (if specified)
        if organization_id:
            entity_features = await self.get_entity_features(db, organization_id)
            all_features.update({f"entity_{k}": v for k, v in entity_features.items()})

        # 4. Temporal features (always include)
        temporal_features = await self.get_temporal_features(db, engagement_id)
        all_features.update({f"time_{k}": v for k, v in temporal_features.items()})

        logger.info(f"Extracted {len(all_features)} total features")
        return all_features

    def convert_to_dataframe(
        self,
        features_list: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Convert list of feature dictionaries to pandas DataFrame

        Handles missing values and type conversions for ML.

        Args:
            features_list: List of feature dictionaries

        Returns:
            pandas DataFrame with features
        """
        df = pd.DataFrame(features_list)

        # Handle categorical variables
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            # Convert to category type
            df[col] = df[col].astype('category')

        # Fill missing numerical values with median
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)

        logger.info(f"Created DataFrame with shape {df.shape}")
        return df


# Global feature store instance
feature_store = FeatureStore()
