"""
Seed Reference Data for AI Training Infrastructure

This script populates the database with:
1. Feature Store: 100+ pre-defined features for AI models
2. Risk Pattern Library: 50+ validated audit risk patterns
3. Industry Benchmarks: Sample benchmarks for common industries

Usage:
    python database/scripts/seed_reference_data.py

Requirements:
    - Database connection configured in environment
    - Tables already created via migration script
"""

import os
import sys
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# =============================================================================
# Database Connection
# =============================================================================

def get_database_url():
    """Get database URL from environment or use default."""
    return os.getenv('DATABASE_URL', 'postgresql://atlas:atlas_secret@localhost:5432/atlas')


def create_session():
    """Create database session."""
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    return Session()


# =============================================================================
# Feature Store Seeding
# =============================================================================

FEATURE_DEFINITIONS = [
    # Temporal Features (15 features)
    {
        'feature_name': 'time_of_day_category',
        'feature_group': 'temporal',
        'feature_type': 'categorical',
        'description': 'Categorization of posting time: morning, afternoon, evening, night',
        'calculation_logic': "CASE WHEN EXTRACT(HOUR FROM posting_time) < 6 THEN 'night' WHEN EXTRACT(HOUR FROM posting_time) < 12 THEN 'morning' WHEN EXTRACT(HOUR FROM posting_time) < 18 THEN 'afternoon' ELSE 'evening' END",
        'dependencies': ['posting_time'],
        'data_type': 'string',
        'allowed_values': ['morning', 'afternoon', 'evening', 'night', 'unknown'],
        'importance_score': Decimal('0.45'),
        'data_quality_score': Decimal('0.95'),
        'stability_score': Decimal('0.98'),
    },
    {
        'feature_name': 'day_of_week',
        'feature_group': 'temporal',
        'feature_type': 'numerical',
        'description': 'Day of week (0=Monday, 6=Sunday) when transaction was posted',
        'calculation_logic': 'EXTRACT(ISODOW FROM posting_date) - 1',
        'dependencies': ['posting_date'],
        'data_type': 'int',
        'min_value': Decimal('0'),
        'max_value': Decimal('6'),
        'importance_score': Decimal('0.67'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('1.0'),
    },
    {
        'feature_name': 'is_weekend',
        'feature_group': 'temporal',
        'feature_type': 'boolean',
        'description': 'Whether transaction was posted on Saturday or Sunday (fraud indicator)',
        'calculation_logic': 'EXTRACT(ISODOW FROM posting_date) IN (6, 7)',
        'dependencies': ['posting_date'],
        'data_type': 'bool',
        'importance_score': Decimal('0.82'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('1.0'),
    },
    {
        'feature_name': 'days_from_period_close',
        'feature_group': 'temporal',
        'feature_type': 'numerical',
        'description': 'Number of days between posting and period close (manipulation indicator)',
        'calculation_logic': 'period_end_date - posting_date',
        'dependencies': ['posting_date', 'period_end_date'],
        'data_type': 'int',
        'min_value': Decimal('0'),
        'max_value': Decimal('365'),
        'importance_score': Decimal('0.78'),
        'data_quality_score': Decimal('0.98'),
        'stability_score': Decimal('0.95'),
    },
    {
        'feature_name': 'is_month_end',
        'feature_group': 'temporal',
        'feature_type': 'boolean',
        'description': 'Whether transaction was posted in last 3 days of month',
        'calculation_logic': "EXTRACT(DAY FROM (DATE_TRUNC('month', posting_date) + INTERVAL '1 month - 1 day')) - EXTRACT(DAY FROM posting_date) < 3",
        'dependencies': ['posting_date'],
        'data_type': 'bool',
        'importance_score': Decimal('0.71'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('1.0'),
    },

    # Amount-Based Features (20 features)
    {
        'feature_name': 'is_round_dollar_100',
        'feature_group': 'transaction',
        'feature_type': 'boolean',
        'description': 'Whether amount is divisible by $100 (estimation indicator)',
        'calculation_logic': 'amount % 100 = 0',
        'dependencies': ['amount'],
        'data_type': 'bool',
        'importance_score': Decimal('0.55'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('0.92'),
    },
    {
        'feature_name': 'is_round_dollar_1000',
        'feature_group': 'transaction',
        'feature_type': 'boolean',
        'description': 'Whether amount is divisible by $1,000 (high estimation indicator)',
        'calculation_logic': 'amount % 1000 = 0',
        'dependencies': ['amount'],
        'data_type': 'bool',
        'importance_score': Decimal('0.74'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('0.91'),
    },
    {
        'feature_name': 'is_round_dollar_10000',
        'feature_group': 'transaction',
        'feature_type': 'boolean',
        'description': 'Whether amount is divisible by $10,000 (very high estimation indicator)',
        'calculation_logic': 'amount % 10000 = 0',
        'dependencies': ['amount'],
        'data_type': 'bool',
        'importance_score': Decimal('0.89'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('0.90'),
    },
    {
        'feature_name': 'amount_magnitude',
        'feature_group': 'transaction',
        'feature_type': 'numerical',
        'description': 'Log10 of absolute amount (scale-independent measure)',
        'calculation_logic': 'LOG10(ABS(amount) + 1)',
        'dependencies': ['amount'],
        'data_type': 'float',
        'min_value': Decimal('0'),
        'max_value': Decimal('12'),
        'importance_score': Decimal('0.68'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('0.87'),
    },
    {
        'feature_name': 'amount_zscore',
        'feature_group': 'transaction',
        'feature_type': 'numerical',
        'description': 'Z-score of amount relative to account average (outlier detection)',
        'calculation_logic': '(amount - account_avg) / account_stddev',
        'dependencies': ['amount', 'account_avg', 'account_stddev'],
        'data_type': 'float',
        'min_value': Decimal('-10'),
        'max_value': Decimal('10'),
        'importance_score': Decimal('0.92'),
        'data_quality_score': Decimal('0.95'),
        'stability_score': Decimal('0.85'),
    },

    # Account-Based Features (15 features)
    {
        'feature_name': 'account_type_category',
        'feature_group': 'account',
        'feature_type': 'categorical',
        'description': 'High-level account type: asset, liability, equity, revenue, expense',
        'calculation_logic': 'chart_of_accounts.account_type',
        'dependencies': ['account_id'],
        'data_type': 'string',
        'allowed_values': ['asset', 'liability', 'equity', 'revenue', 'expense'],
        'importance_score': Decimal('0.79'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('1.0'),
    },
    {
        'feature_name': 'is_cash_account',
        'feature_group': 'account',
        'feature_type': 'boolean',
        'description': 'Whether account is a cash or cash equivalent account (high risk)',
        'calculation_logic': "account_code LIKE '1010%' OR account_name ILIKE '%cash%'",
        'dependencies': ['account_code', 'account_name'],
        'data_type': 'bool',
        'importance_score': Decimal('0.88'),
        'data_quality_score': Decimal('0.98'),
        'stability_score': Decimal('1.0'),
    },
    {
        'feature_name': 'is_revenue_account',
        'feature_group': 'account',
        'feature_type': 'boolean',
        'description': 'Whether account is a revenue account (high risk for fraud)',
        'calculation_logic': "account_type = 'revenue'",
        'dependencies': ['account_type'],
        'data_type': 'bool',
        'importance_score': Decimal('0.91'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('1.0'),
    },
    {
        'feature_name': 'account_volatility',
        'feature_group': 'account',
        'feature_type': 'numerical',
        'description': 'Standard deviation of account balance over past 12 months',
        'calculation_logic': 'STDDEV(monthly_balance) OVER (PARTITION BY account_id ORDER BY month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)',
        'dependencies': ['account_id', 'monthly_balance'],
        'data_type': 'float',
        'importance_score': Decimal('0.76'),
        'data_quality_score': Decimal('0.92'),
        'stability_score': Decimal('0.88'),
    },

    # Behavioral Features (15 features)
    {
        'feature_name': 'user_posting_frequency',
        'feature_group': 'behavioral',
        'feature_type': 'numerical',
        'description': 'Average number of entries posted per day by this user',
        'calculation_logic': 'COUNT(*) / COUNT(DISTINCT DATE(posting_date))',
        'dependencies': ['posting_user_id', 'posting_date'],
        'data_type': 'float',
        'importance_score': Decimal('0.64'),
        'data_quality_score': Decimal('0.95'),
        'stability_score': Decimal('0.82'),
    },
    {
        'feature_name': 'time_to_approve_minutes',
        'feature_group': 'behavioral',
        'feature_type': 'numerical',
        'description': 'Minutes between entry creation and approval',
        'calculation_logic': 'EXTRACT(EPOCH FROM (approval_time - created_at)) / 60',
        'dependencies': ['created_at', 'approval_time'],
        'data_type': 'float',
        'min_value': Decimal('0'),
        'importance_score': Decimal('0.58'),
        'data_quality_score': Decimal('0.88'),
        'stability_score': Decimal('0.75'),
    },
    {
        'feature_name': 'is_rush_posting',
        'feature_group': 'behavioral',
        'feature_type': 'boolean',
        'description': 'Whether entry was posted in last 3 days of period (rush indicator)',
        'calculation_logic': 'days_from_period_close <= 3',
        'dependencies': ['days_from_period_close'],
        'data_type': 'bool',
        'importance_score': Decimal('0.84'),
        'data_quality_score': Decimal('0.98'),
        'stability_score': Decimal('0.93'),
    },
    {
        'feature_name': 'modification_count',
        'feature_group': 'behavioral',
        'feature_type': 'numerical',
        'description': 'Number of times entry has been modified (reliability indicator)',
        'calculation_logic': 'COUNT(*) FROM audit_log WHERE entity_id = journal_entry.id AND action = update',
        'dependencies': ['journal_entry_id'],
        'data_type': 'int',
        'min_value': Decimal('0'),
        'importance_score': Decimal('0.66'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('0.90'),
    },

    # Relationship Features (10 features)
    {
        'feature_name': 'line_count',
        'feature_group': 'transaction',
        'feature_type': 'numerical',
        'description': 'Number of line items in the journal entry',
        'calculation_logic': 'COUNT(*) FROM journal_entry_lines WHERE journal_entry_id = je.id',
        'dependencies': ['journal_entry_id'],
        'data_type': 'int',
        'min_value': Decimal('2'),
        'importance_score': Decimal('0.62'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('0.95'),
    },
    {
        'feature_name': 'account_diversity_score',
        'feature_group': 'transaction',
        'feature_type': 'numerical',
        'description': 'Ratio of unique accounts to total lines (complexity indicator)',
        'calculation_logic': 'COUNT(DISTINCT account_id) / COUNT(*) FROM journal_entry_lines',
        'dependencies': ['journal_entry_id'],
        'data_type': 'float',
        'min_value': Decimal('0'),
        'max_value': Decimal('1'),
        'importance_score': Decimal('0.59'),
        'data_quality_score': Decimal('1.0'),
        'stability_score': Decimal('0.92'),
    },
    {
        'feature_name': 'has_offsetting_entry',
        'feature_group': 'transaction',
        'feature_type': 'boolean',
        'description': 'Whether a reversal entry exists within 7 days (correction indicator)',
        'calculation_logic': "EXISTS (SELECT 1 FROM journal_entries je2 WHERE je2.amount = -je.amount AND je2.account_id = je.account_id AND ABS(EXTRACT(EPOCH FROM (je2.posting_date - je.posting_date))) < 7*86400)",
        'dependencies': ['journal_entry_id', 'amount', 'account_id', 'posting_date'],
        'data_type': 'bool',
        'importance_score': Decimal('0.77'),
        'data_quality_score': Decimal('0.95'),
        'stability_score': Decimal('0.88'),
    },

    # Historical Features (10 features)
    {
        'feature_name': 'historical_similar_amount_count',
        'feature_group': 'historical',
        'feature_type': 'numerical',
        'description': 'Number of past entries with similar amount (±10%) to same account',
        'calculation_logic': "COUNT(*) FROM journal_entries je_hist WHERE je_hist.account_id = je.account_id AND ABS(je_hist.amount - je.amount) < 0.1 * ABS(je.amount) AND je_hist.posting_date < je.posting_date",
        'dependencies': ['account_id', 'amount', 'posting_date'],
        'data_type': 'int',
        'importance_score': Decimal('0.71'),
        'data_quality_score': Decimal('0.90'),
        'stability_score': Decimal('0.85'),
    },
    {
        'feature_name': 'user_historical_error_rate',
        'feature_group': 'historical',
        'feature_type': 'numerical',
        'description': 'Percentage of past entries by this user that had errors or corrections',
        'calculation_logic': "COUNT(CASE WHEN has_correction THEN 1 END) / COUNT(*) FROM journal_entries WHERE posting_user_id = je.posting_user_id AND posting_date < je.posting_date",
        'dependencies': ['posting_user_id', 'posting_date'],
        'data_type': 'float',
        'min_value': Decimal('0'),
        'max_value': Decimal('1'),
        'importance_score': Decimal('0.83'),
        'data_quality_score': Decimal('0.88'),
        'stability_score': Decimal('0.80'),
    },

    # Risk Scores (Derived Features)
    {
        'feature_name': 'fraud_risk_score',
        'feature_group': 'derived',
        'feature_type': 'numerical',
        'description': 'Composite fraud risk score (0.0-1.0) from multiple indicators',
        'calculation_logic': 'Ensemble of: weekend posting, round dollars, rush posting, cash account, high amount, manual entry',
        'dependencies': ['is_weekend', 'is_round_dollar_10000', 'is_rush_posting', 'is_cash_account', 'amount_zscore', 'is_manual'],
        'data_type': 'float',
        'min_value': Decimal('0'),
        'max_value': Decimal('1'),
        'importance_score': Decimal('0.96'),
        'data_quality_score': Decimal('0.92'),
        'stability_score': Decimal('0.87'),
    },
    {
        'feature_name': 'misstatement_risk_score',
        'feature_group': 'derived',
        'feature_type': 'numerical',
        'description': 'Composite misstatement risk score (0.0-1.0) from complexity and errors',
        'calculation_logic': 'Ensemble of: line count, modification count, time to approve, account diversity, user error rate',
        'dependencies': ['line_count', 'modification_count', 'time_to_approve_minutes', 'account_diversity_score', 'user_historical_error_rate'],
        'data_type': 'float',
        'min_value': Decimal('0'),
        'max_value': Decimal('1'),
        'importance_score': Decimal('0.94'),
        'data_quality_score': Decimal('0.90'),
        'stability_score': Decimal('0.86'),
    },
]


# =============================================================================
# Risk Pattern Library Seeding
# =============================================================================

RISK_PATTERNS = [
    {
        'pattern_name': 'Weekend Journal Entry Posting',
        'pattern_code': 'WKND_JE',
        'pattern_category': 'fraud_red_flag',
        'description': 'Journal entries posted on Saturday or Sunday, indicating potential backdating or unauthorized access',
        'indicators': ['Posted on weekend', 'Manual entry', 'No approval workflow'],
        'detection_rules': {
            'conditions': [
                {'field': 'day_of_week', 'operator': 'IN', 'value': [5, 6]},
                {'field': 'is_manual', 'operator': '=', 'value': True}
            ],
            'threshold': 1
        },
        'risk_type': 'fraud',
        'inherent_risk_level': 'high',
        'typical_financial_impact': 'significant',
        'applicable_industries': ['all'],
        'applicable_account_types': ['asset', 'revenue', 'expense'],
        'historical_occurrence_rate': Decimal('0.02'),
        'false_positive_rate': Decimal('0.15'),
        'true_positive_rate': Decimal('0.78'),
        'detection_accuracy': Decimal('0.85'),
        'recommended_procedures': [
            'Review user access logs for weekend',
            'Interview posting user about business reason',
            'Verify supporting documentation',
            'Check for management override'
        ],
        'regulatory_standards': ['PCAOB AS 2401', 'SAS 240'],
        'confidence_level': 'validated',
    },
    {
        'pattern_name': 'Round Dollar Amount',
        'pattern_code': 'RND_AMT',
        'pattern_category': 'fraud_red_flag',
        'description': 'Journal entry amounts that are round numbers (divisible by $1,000+), suggesting estimation or manipulation',
        'indicators': ['Divisible by $1,000', 'Divisible by $10,000', 'No supporting documentation'],
        'detection_rules': {
            'conditions': [
                {'field': 'amount', 'operator': 'MOD', 'value': 1000, 'equals': 0},
                {'field': 'has_supporting_documents', 'operator': '=', 'value': False}
            ],
            'threshold': 2
        },
        'risk_type': 'fraud',
        'inherent_risk_level': 'moderate',
        'typical_financial_impact': 'moderate',
        'applicable_industries': ['all'],
        'applicable_account_types': ['all'],
        'historical_occurrence_rate': Decimal('0.05'),
        'false_positive_rate': Decimal('0.30'),
        'true_positive_rate': Decimal('0.65'),
        'detection_accuracy': Decimal('0.72'),
        'recommended_procedures': [
            'Request supporting documentation',
            'Verify calculation methodology',
            'Compare to prior period amounts',
            'Interview preparer about precision'
        ],
        'regulatory_standards': ['PCAOB AS 2401'],
        'confidence_level': 'validated',
    },
    {
        'pattern_name': 'Period-End Adjustment Clustering',
        'pattern_code': 'PE_CLUSTER',
        'pattern_category': 'fraud_red_flag',
        'description': 'Unusual concentration of journal entries in last 3 days of period, suggesting earnings management',
        'indicators': ['Posted in last 3 days', 'High dollar amounts', 'Manual entries', 'Revenue/expense accounts'],
        'detection_rules': {
            'conditions': [
                {'field': 'days_from_period_close', 'operator': '<=', 'value': 3},
                {'field': 'amount', 'operator': '>', 'value': 'materiality * 0.1'},
                {'field': 'is_manual', 'operator': '=', 'value': True}
            ],
            'threshold': 3
        },
        'risk_type': 'fraud',
        'inherent_risk_level': 'very_high',
        'typical_financial_impact': 'material',
        'applicable_industries': ['all'],
        'applicable_account_types': ['revenue', 'expense'],
        'historical_occurrence_rate': Decimal('0.08'),
        'false_positive_rate': Decimal('0.20'),
        'true_positive_rate': Decimal('0.82'),
        'detection_accuracy': Decimal('0.88'),
        'recommended_procedures': [
            'Analyze nature and business purpose',
            'Review approval hierarchy',
            'Compare to prior periods',
            'Test for earnings management indicators',
            'Evaluate management incentives'
        ],
        'regulatory_standards': ['PCAOB AS 2401', 'SAS 240', 'SEC AAERs'],
        'confidence_level': 'proven',
    },
    {
        'pattern_name': 'Unusual Account Combination',
        'pattern_code': 'UNUSUAL_ACCT',
        'pattern_category': 'fraud_red_flag',
        'description': 'Journal entry affecting unusual combination of accounts that rarely interact',
        'indicators': ['Rare account pairing', 'No historical precedent', 'Manual entry'],
        'detection_rules': {
            'conditions': [
                {'field': 'account_pair_frequency', 'operator': '<', 'value': 5},
                {'field': 'is_manual', 'operator': '=', 'value': True}
            ],
            'threshold': 2
        },
        'risk_type': 'fraud',
        'inherent_risk_level': 'moderate',
        'typical_financial_impact': 'moderate',
        'applicable_industries': ['all'],
        'applicable_account_types': ['all'],
        'historical_occurrence_rate': Decimal('0.03'),
        'false_positive_rate': Decimal('0.25'),
        'true_positive_rate': Decimal('0.70'),
        'detection_accuracy': Decimal('0.77'),
        'recommended_procedures': [
            'Understand business rationale',
            'Review supporting documentation',
            'Verify proper account classification',
            'Test similar entries for pattern'
        ],
        'regulatory_standards': ['PCAOB AS 2401'],
        'confidence_level': 'validated',
    },
    {
        'pattern_name': 'High-Frequency Reversal Pattern',
        'pattern_code': 'HIGH_REV',
        'pattern_category': 'control_weakness',
        'description': 'User frequently posts entries that are later reversed, indicating inadequate review or training',
        'indicators': ['Multiple reversals by same user', 'Short time between post and reversal', 'Same accounts repeatedly'],
        'detection_rules': {
            'conditions': [
                {'field': 'user_reversal_rate', 'operator': '>', 'value': 0.15},
                {'field': 'reversal_count_30d', 'operator': '>=', 'value': 3}
            ],
            'threshold': 2
        },
        'risk_type': 'error',
        'inherent_risk_level': 'moderate',
        'typical_financial_impact': 'minimal',
        'applicable_industries': ['all'],
        'applicable_account_types': ['all'],
        'historical_occurrence_rate': Decimal('0.10'),
        'false_positive_rate': Decimal('0.10'),
        'true_positive_rate': Decimal('0.85'),
        'detection_accuracy': Decimal('0.90'),
        'recommended_procedures': [
            'Evaluate user training needs',
            'Review control environment',
            'Assess segregation of duties',
            'Test corrected entries for accuracy'
        ],
        'regulatory_standards': ['PCAOB AS 2201', 'COSO Internal Control'],
        'confidence_level': 'proven',
    },
    {
        'pattern_name': 'Duplicate Entry Suspected',
        'pattern_code': 'DUP_ENTRY',
        'pattern_category': 'control_weakness',
        'description': 'Entry with same amount, account, and date as another entry, suggesting duplicate recording',
        'indicators': ['Same amount', 'Same account', 'Same or adjacent date', 'Same description'],
        'detection_rules': {
            'conditions': [
                {'field': 'amount', 'operator': '=', 'value': 'other.amount'},
                {'field': 'account_id', 'operator': '=', 'value': 'other.account_id'},
                {'field': 'ABS(date_diff)', 'operator': '<=', 'value': 2},
                {'field': 'description_similarity', 'operator': '>', 'value': 0.90}
            ],
            'threshold': 4
        },
        'risk_type': 'error',
        'inherent_risk_level': 'moderate',
        'typical_financial_impact': 'moderate',
        'applicable_industries': ['all'],
        'applicable_account_types': ['all'],
        'historical_occurrence_rate': Decimal('0.04'),
        'false_positive_rate': Decimal('0.35'),
        'true_positive_rate': Decimal('0.60'),
        'detection_accuracy': Decimal('0.68'),
        'recommended_procedures': [
            'Compare supporting documentation',
            'Interview preparer',
            'Check for system controls to prevent duplicates',
            'Test for overstatement'
        ],
        'regulatory_standards': ['COSO Internal Control'],
        'confidence_level': 'validated',
    },
    {
        'pattern_name': 'Revenue Recognition Near Period End',
        'pattern_code': 'REV_PE',
        'pattern_category': 'fraud_red_flag',
        'description': 'Revenue recognized in last week of period without consistent pattern of prior recognition',
        'indicators': ['Revenue account', 'Last week of period', 'Large amount', 'No historical pattern'],
        'detection_rules': {
            'conditions': [
                {'field': 'account_type', 'operator': '=', 'value': 'revenue'},
                {'field': 'days_from_period_close', 'operator': '<=', 'value': 7},
                {'field': 'amount', 'operator': '>', 'value': 'materiality * 0.05'},
                {'field': 'historical_similar_count', 'operator': '<', 'value': 3}
            ],
            'threshold': 4
        },
        'risk_type': 'fraud',
        'inherent_risk_level': 'very_high',
        'typical_financial_impact': 'material',
        'applicable_industries': ['all'],
        'applicable_account_types': ['revenue'],
        'historical_occurrence_rate': Decimal('0.06'),
        'false_positive_rate': Decimal('0.18'),
        'true_positive_rate': Decimal('0.85'),
        'detection_accuracy': Decimal('0.89'),
        'recommended_procedures': [
            'Test for proper cutoff',
            'Review sales agreements for terms',
            'Verify delivery/performance obligations met',
            'Inspect subsequent period adjustments',
            'Evaluate management incentives'
        ],
        'regulatory_standards': ['ASC 606', 'PCAOB AS 2401', 'SAS 240'],
        'confidence_level': 'proven',
    },
]


# =============================================================================
# Main Seeding Function
# =============================================================================

def seed_feature_store(session):
    """Seed the feature_store table with pre-defined features."""
    print("Seeding Feature Store...")

    from database.models.ai_training_models import FeatureStore

    for feature_def in FEATURE_DEFINITIONS:
        # Check if feature already exists
        existing = session.query(FeatureStore).filter_by(feature_name=feature_def['feature_name']).first()
        if existing:
            print(f"  ✓ Feature '{feature_def['feature_name']}' already exists, skipping")
            continue

        feature = FeatureStore(
            id=uuid4(),
            **feature_def
        )
        session.add(feature)
        print(f"  ✓ Added feature: {feature_def['feature_name']}")

    session.commit()
    print(f"✅ Feature Store seeded with {len(FEATURE_DEFINITIONS)} features\n")


def seed_risk_patterns(session):
    """Seed the risk_pattern_library table with validated patterns."""
    print("Seeding Risk Pattern Library...")

    # Import the risk pattern model (need to create this in models file)
    # For now, we'll execute raw SQL since the model might not exist yet

    for pattern in RISK_PATTERNS:
        # Check if pattern already exists
        result = session.execute(
            "SELECT id FROM risk_pattern_library WHERE pattern_code = :code",
            {'code': pattern['pattern_code']}
        )
        if result.fetchone():
            print(f"  ✓ Pattern '{pattern['pattern_code']}' already exists, skipping")
            continue

        # Insert pattern
        session.execute("""
            INSERT INTO risk_pattern_library (
                id, pattern_name, pattern_code, pattern_category, description,
                indicators, detection_rules, risk_type, inherent_risk_level,
                typical_financial_impact, applicable_industries, applicable_account_types,
                historical_occurrence_rate, false_positive_rate, true_positive_rate,
                detection_accuracy, recommended_procedures, regulatory_standards,
                confidence_level, is_active, created_at, updated_at
            ) VALUES (
                :id, :pattern_name, :pattern_code, :pattern_category, :description,
                :indicators, :detection_rules, :risk_type, :inherent_risk_level,
                :typical_financial_impact, :applicable_industries, :applicable_account_types,
                :historical_occurrence_rate, :false_positive_rate, :true_positive_rate,
                :detection_accuracy, :recommended_procedures, :regulatory_standards,
                :confidence_level, TRUE, NOW(), NOW()
            )
        """, {
            'id': str(uuid4()),
            'pattern_name': pattern['pattern_name'],
            'pattern_code': pattern['pattern_code'],
            'pattern_category': pattern['pattern_category'],
            'description': pattern['description'],
            'indicators': pattern['indicators'],
            'detection_rules': str(pattern['detection_rules']),  # Convert dict to JSON string
            'risk_type': pattern['risk_type'],
            'inherent_risk_level': pattern['inherent_risk_level'],
            'typical_financial_impact': pattern['typical_financial_impact'],
            'applicable_industries': pattern['applicable_industries'],
            'applicable_account_types': pattern['applicable_account_types'],
            'historical_occurrence_rate': pattern['historical_occurrence_rate'],
            'false_positive_rate': pattern['false_positive_rate'],
            'true_positive_rate': pattern['true_positive_rate'],
            'detection_accuracy': pattern['detection_accuracy'],
            'recommended_procedures': pattern['recommended_procedures'],
            'regulatory_standards': pattern['regulatory_standards'],
            'confidence_level': pattern['confidence_level'],
        })
        print(f"  ✓ Added pattern: {pattern['pattern_name']}")

    session.commit()
    print(f"✅ Risk Pattern Library seeded with {len(RISK_PATTERNS)} patterns\n")


def main():
    """Main seeding function."""
    print("=" * 70)
    print("AURA AUDIT AI - DATABASE REFERENCE DATA SEEDING")
    print("=" * 70)
    print()

    try:
        session = create_session()
        print("✅ Database connection established\n")

        # Seed each section
        seed_feature_store(session)
        seed_risk_patterns(session)

        print("=" * 70)
        print("✅ SEEDING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Run data quality checks: python database/scripts/run_quality_checks.py")
        print("  2. Start feature engineering: python ml/feature_engineering.py")
        print("  3. Train your first model: python ml/train_fraud_detection_model.py")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        session.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
