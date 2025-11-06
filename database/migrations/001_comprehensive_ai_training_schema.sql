-- =====================================================
-- AURA AUDIT AI - COMPREHENSIVE DATABASE SCHEMA
-- Enhanced for Superior AI Training & Audit Intelligence
-- =====================================================
-- Design Principles:
-- 1. Capture extensive variables for pattern recognition
-- 2. Enable temporal analysis and trend detection
-- 3. Support graph relationships and entity networks
-- 4. Track data quality and lineage end-to-end
-- 5. Enable continuous learning from human feedback
-- 6. Support real-time feature engineering
-- 7. Maintain compliance with audit standards
-- =====================================================

-- =====================================================
-- SECTION 1: ENHANCED TRANSACTION & FINANCIAL DATA
-- Purpose: Capture granular transaction details for AI training
-- =====================================================

-- Enhanced journal entry metadata for pattern detection
CREATE TABLE IF NOT EXISTS journal_entry_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,

    -- Temporal features
    time_of_day_category VARCHAR(20) CHECK (time_of_day_category IN ('morning', 'afternoon', 'evening', 'night', 'unknown')),
    day_of_week INTEGER CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Monday, 6=Sunday
    day_of_month INTEGER CHECK (day_of_month BETWEEN 1 AND 31),
    week_of_year INTEGER CHECK (week_of_year BETWEEN 1 AND 53),
    quarter INTEGER CHECK (quarter BETWEEN 1 AND 4),
    is_month_end BOOLEAN DEFAULT FALSE,
    is_quarter_end BOOLEAN DEFAULT FALSE,
    is_year_end BOOLEAN DEFAULT FALSE,
    days_from_period_close INTEGER,
    is_holiday BOOLEAN DEFAULT FALSE,
    business_day_of_month INTEGER,

    -- Behavioral features
    posting_user_id UUID REFERENCES users(id),
    approving_user_id UUID REFERENCES users(id),
    modified_count INTEGER DEFAULT 0, -- How many times edited
    time_to_approve_seconds INTEGER, -- Time from creation to approval
    is_rush_posting BOOLEAN DEFAULT FALSE, -- Posted in last 3 days of period

    -- Transaction characteristics
    line_count INTEGER NOT NULL,
    account_diversity_score DECIMAL(5,4), -- How many different accounts used
    debit_credit_balance_check BOOLEAN DEFAULT TRUE,
    has_foreign_currency BOOLEAN DEFAULT FALSE,
    currency_count INTEGER DEFAULT 1,
    max_line_amount DECIMAL(20,2),
    min_line_amount DECIMAL(20,2),
    avg_line_amount DECIMAL(20,2),
    std_dev_line_amount DECIMAL(20,2),

    -- Anomaly indicators
    is_round_dollar BOOLEAN DEFAULT FALSE,
    round_dollar_divisor INTEGER, -- 100, 1000, 10000, etc.
    is_statistical_outlier BOOLEAN DEFAULT FALSE,
    outlier_zscore DECIMAL(10,4),
    is_duplicate_suspected BOOLEAN DEFAULT FALSE,
    duplicate_similarity_score DECIMAL(5,4),

    -- Relationships
    has_supporting_documents BOOLEAN DEFAULT FALSE,
    document_count INTEGER DEFAULT 0,
    has_approval_workflow BOOLEAN DEFAULT FALSE,
    linked_procedure_count INTEGER DEFAULT 0,

    -- Risk indicators
    fraud_risk_score DECIMAL(5,4) CHECK (fraud_risk_score BETWEEN 0 AND 1),
    misstatement_risk_score DECIMAL(5,4) CHECK (misstatement_risk_score BETWEEN 0 AND 1),
    complexity_score DECIMAL(5,4) CHECK (complexity_score BETWEEN 0 AND 1),

    -- ML features
    features JSONB, -- Flexible storage for derived features
    embedding_vector VECTOR(1536), -- For similarity search

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(journal_entry_id)
);

CREATE INDEX idx_je_metadata_time_patterns ON journal_entry_metadata(day_of_week, time_of_day_category, is_month_end);
CREATE INDEX idx_je_metadata_risk_scores ON journal_entry_metadata(fraud_risk_score DESC, misstatement_risk_score DESC);
CREATE INDEX idx_je_metadata_anomalies ON journal_entry_metadata(is_round_dollar, is_statistical_outlier, is_duplicate_suspected);
CREATE INDEX idx_je_metadata_embedding ON journal_entry_metadata USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

-- Transaction sequence analysis for pattern detection
CREATE TABLE IF NOT EXISTS transaction_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,

    -- Sequence identification
    sequence_type VARCHAR(50) NOT NULL, -- 'recurring', 'batch', 'adjustment_chain', 'reversal_pair'
    sequence_identifier VARCHAR(255), -- Unique identifier for the sequence

    -- Sequence members
    journal_entry_ids UUID[] NOT NULL, -- Array of JE IDs in sequence
    entry_count INTEGER NOT NULL,

    -- Temporal analysis
    first_entry_date TIMESTAMPTZ NOT NULL,
    last_entry_date TIMESTAMPTZ NOT NULL,
    frequency_days DECIMAL(10,2), -- Average days between entries
    is_regular_frequency BOOLEAN DEFAULT FALSE,

    -- Amount analysis
    total_amount DECIMAL(20,2) NOT NULL,
    avg_amount DECIMAL(20,2),
    amount_variance DECIMAL(20,2), -- Variance in amounts
    is_consistent_amount BOOLEAN DEFAULT FALSE,

    -- Pattern characteristics
    accounts_involved VARCHAR(255)[], -- Account codes in the pattern
    is_automated BOOLEAN DEFAULT FALSE,
    source_system VARCHAR(100),

    -- Risk assessment
    is_suspicious BOOLEAN DEFAULT FALSE,
    suspicion_reasons TEXT[],
    requires_testing BOOLEAN DEFAULT FALSE,

    -- AI insights
    pattern_confidence DECIMAL(5,4) CHECK (pattern_confidence BETWEEN 0 AND 1),
    detected_by_model VARCHAR(100),
    detection_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_txn_sequences_engagement ON transaction_sequences(engagement_id);
CREATE INDEX idx_txn_sequences_type ON transaction_sequences(sequence_type);
CREATE INDEX idx_txn_sequences_suspicious ON transaction_sequences(is_suspicious, requires_testing);

-- Account balance history for trend analysis
CREATE TABLE IF NOT EXISTS account_balance_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES chart_of_accounts(id) ON DELETE CASCADE,

    -- Period identification
    period_date DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
    fiscal_year INTEGER NOT NULL,
    fiscal_period INTEGER NOT NULL,

    -- Balance information
    opening_balance DECIMAL(20,2) NOT NULL,
    closing_balance DECIMAL(20,2) NOT NULL,
    period_change DECIMAL(20,2) NOT NULL,
    period_change_percent DECIMAL(10,4),

    -- Activity metrics
    debit_count INTEGER DEFAULT 0,
    credit_count INTEGER DEFAULT 0,
    total_debits DECIMAL(20,2) DEFAULT 0,
    total_credits DECIMAL(20,2) DEFAULT 0,
    net_change DECIMAL(20,2) NOT NULL,

    -- Statistical features
    avg_transaction_size DECIMAL(20,2),
    max_transaction_size DECIMAL(20,2),
    min_transaction_size DECIMAL(20,2),
    std_dev_transaction_size DECIMAL(20,2),

    -- Trend indicators
    moving_avg_3_period DECIMAL(20,2),
    moving_avg_6_period DECIMAL(20,2),
    moving_avg_12_period DECIMAL(20,2),
    trend_direction VARCHAR(20) CHECK (trend_direction IN ('increasing', 'decreasing', 'stable', 'volatile')),
    volatility_score DECIMAL(5,4),

    -- Anomaly detection
    is_anomalous BOOLEAN DEFAULT FALSE,
    anomaly_score DECIMAL(5,4),
    expected_balance DECIMAL(20,2),
    variance_from_expected DECIMAL(20,2),

    -- Comparative analysis
    prior_period_balance DECIMAL(20,2),
    year_over_year_change DECIMAL(20,2),
    year_over_year_change_percent DECIMAL(10,4),
    industry_benchmark_balance DECIMAL(20,2),
    variance_from_benchmark_percent DECIMAL(10,4),

    -- Metadata
    data_quality_score DECIMAL(5,4) CHECK (data_quality_score BETWEEN 0 AND 1),
    completeness_score DECIMAL(5,4) CHECK (completeness_score BETWEEN 0 AND 1),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(engagement_id, account_id, period_date, period_type)
);

CREATE INDEX idx_acct_balance_history_engagement_account ON account_balance_history(engagement_id, account_id, period_date DESC);
CREATE INDEX idx_acct_balance_history_anomalies ON account_balance_history(is_anomalous, anomaly_score DESC);
CREATE INDEX idx_acct_balance_history_trends ON account_balance_history(trend_direction, volatility_score DESC);

-- Financial ratios with time-series tracking
CREATE TABLE IF NOT EXISTS financial_ratios_timeseries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,

    -- Period identification
    period_date DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('monthly', 'quarterly', 'yearly')),
    fiscal_year INTEGER NOT NULL,
    fiscal_period INTEGER NOT NULL,

    -- Liquidity ratios
    current_ratio DECIMAL(10,4),
    quick_ratio DECIMAL(10,4),
    cash_ratio DECIMAL(10,4),
    working_capital DECIMAL(20,2),
    working_capital_ratio DECIMAL(10,4),

    -- Profitability ratios
    gross_profit_margin DECIMAL(10,4),
    operating_profit_margin DECIMAL(10,4),
    net_profit_margin DECIMAL(10,4),
    return_on_assets DECIMAL(10,4),
    return_on_equity DECIMAL(10,4),
    return_on_invested_capital DECIMAL(10,4),
    ebitda_margin DECIMAL(10,4),

    -- Leverage ratios
    debt_to_equity DECIMAL(10,4),
    debt_to_assets DECIMAL(10,4),
    equity_multiplier DECIMAL(10,4),
    interest_coverage DECIMAL(10,4),
    debt_service_coverage DECIMAL(10,4),

    -- Efficiency ratios
    asset_turnover DECIMAL(10,4),
    inventory_turnover DECIMAL(10,4),
    receivables_turnover DECIMAL(10,4),
    payables_turnover DECIMAL(10,4),
    days_sales_outstanding DECIMAL(10,2),
    days_inventory_outstanding DECIMAL(10,2),
    days_payables_outstanding DECIMAL(10,2),
    cash_conversion_cycle DECIMAL(10,2),

    -- Market ratios (if applicable)
    earnings_per_share DECIMAL(10,4),
    price_to_earnings DECIMAL(10,4),
    price_to_book DECIMAL(10,4),
    dividend_yield DECIMAL(10,4),

    -- Growth metrics
    revenue_growth_rate DECIMAL(10,4),
    earnings_growth_rate DECIMAL(10,4),
    asset_growth_rate DECIMAL(10,4),

    -- Custom ratios
    custom_ratio_1_name VARCHAR(100),
    custom_ratio_1_value DECIMAL(10,4),
    custom_ratio_2_name VARCHAR(100),
    custom_ratio_2_value DECIMAL(10,4),

    -- Trend analysis
    ratios_trend_score DECIMAL(5,4), -- Overall health trend
    deterioration_flags TEXT[], -- Which ratios are deteriorating
    improvement_flags TEXT[], -- Which ratios are improving

    -- Comparative analysis
    industry_percentile DECIMAL(5,2), -- Percentile ranking vs industry
    peer_comparison_score DECIMAL(5,4), -- -1 to 1, relative to peers

    -- Risk indicators
    going_concern_risk_score DECIMAL(5,4) CHECK (going_concern_risk_score BETWEEN 0 AND 1),
    liquidity_risk_level VARCHAR(20) CHECK (liquidity_risk_level IN ('low', 'medium', 'high', 'critical')),
    solvency_risk_level VARCHAR(20) CHECK (solvency_risk_level IN ('low', 'medium', 'high', 'critical')),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(engagement_id, period_date, period_type)
);

CREATE INDEX idx_financial_ratios_ts_engagement ON financial_ratios_timeseries(engagement_id, period_date DESC);
CREATE INDEX idx_financial_ratios_ts_risk ON financial_ratios_timeseries(going_concern_risk_score DESC, liquidity_risk_level);

-- =====================================================
-- SECTION 2: AI TRAINING INFRASTRUCTURE
-- Purpose: Support model training, feature engineering, and continuous learning
-- =====================================================

-- Feature store for ML models
CREATE TABLE IF NOT EXISTS feature_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Feature identification
    feature_name VARCHAR(255) NOT NULL UNIQUE,
    feature_group VARCHAR(100) NOT NULL, -- 'transaction', 'account', 'entity', 'temporal', 'behavioral'
    feature_type VARCHAR(50) NOT NULL CHECK (feature_type IN ('numerical', 'categorical', 'boolean', 'text', 'embedding', 'derived')),

    -- Feature definition
    description TEXT NOT NULL,
    calculation_logic TEXT NOT NULL, -- SQL or formula
    dependencies TEXT[], -- Other features this depends on

    -- Data type and constraints
    data_type VARCHAR(50) NOT NULL, -- 'float', 'int', 'string', 'array', 'vector'
    min_value DECIMAL(20,4),
    max_value DECIMAL(20,4),
    allowed_values TEXT[], -- For categorical features
    is_nullable BOOLEAN DEFAULT FALSE,

    -- Feature statistics
    mean_value DECIMAL(20,4),
    std_dev DECIMAL(20,4),
    percentile_25 DECIMAL(20,4),
    percentile_50 DECIMAL(20,4),
    percentile_75 DECIMAL(20,4),
    percentile_95 DECIMAL(20,4),
    percentile_99 DECIMAL(20,4),
    missing_rate DECIMAL(5,4),

    -- Feature importance
    importance_score DECIMAL(5,4) CHECK (importance_score BETWEEN 0 AND 1),
    importance_rank INTEGER,
    models_using_feature TEXT[], -- Which models use this feature

    -- Feature quality
    data_quality_score DECIMAL(5,4) CHECK (data_quality_score BETWEEN 0 AND 1),
    stability_score DECIMAL(5,4) CHECK (stability_score BETWEEN 0 AND 1), -- How stable over time
    correlation_with_target DECIMAL(10,4), -- -1 to 1

    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    deprecated_date TIMESTAMPTZ,
    replacement_feature_id UUID REFERENCES feature_store(id),

    -- Metadata
    created_by UUID REFERENCES users(id),
    last_updated_by UUID REFERENCES users(id),
    tags TEXT[],

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feature_store_group_type ON feature_store(feature_group, feature_type);
CREATE INDEX idx_feature_store_importance ON feature_store(importance_score DESC);
CREATE INDEX idx_feature_store_active ON feature_store(is_active, deprecated_date);

-- Training dataset definitions
CREATE TABLE IF NOT EXISTS training_datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Dataset identification
    dataset_name VARCHAR(255) NOT NULL,
    dataset_version VARCHAR(50) NOT NULL,
    dataset_type VARCHAR(50) NOT NULL CHECK (dataset_type IN ('training', 'validation', 'test', 'production')),

    -- Purpose and scope
    purpose VARCHAR(100) NOT NULL, -- 'fraud_detection', 'misstatement_risk', 'account_mapping', 'disclosure_generation'
    description TEXT,

    -- Data selection criteria
    engagement_criteria JSONB, -- Filters for engagement selection
    date_range_start DATE,
    date_range_end DATE,
    included_engagement_ids UUID[],
    excluded_engagement_ids UUID[],

    -- Features and labels
    feature_names TEXT[] NOT NULL, -- Features included in this dataset
    label_column VARCHAR(255), -- Target variable name
    label_type VARCHAR(50) CHECK (label_type IN ('binary', 'multiclass', 'regression', 'multilabel')),
    class_distribution JSONB, -- For classification tasks

    -- Dataset statistics
    row_count INTEGER NOT NULL,
    positive_class_count INTEGER, -- For binary classification
    negative_class_count INTEGER,
    class_balance_ratio DECIMAL(5,4),
    feature_count INTEGER NOT NULL,

    -- Data quality
    completeness_score DECIMAL(5,4) CHECK (completeness_score BETWEEN 0 AND 1),
    quality_score DECIMAL(5,4) CHECK (quality_score BETWEEN 0 AND 1),
    has_duplicates BOOLEAN DEFAULT FALSE,
    duplicate_count INTEGER DEFAULT 0,

    -- Storage information
    storage_location TEXT NOT NULL, -- S3/MinIO path or table name
    storage_format VARCHAR(50) NOT NULL, -- 'parquet', 'csv', 'table', 'delta'
    file_size_mb DECIMAL(10,2),
    compression_type VARCHAR(50),

    -- Versioning and lineage
    parent_dataset_id UUID REFERENCES training_datasets(id),
    is_latest_version BOOLEAN DEFAULT TRUE,

    -- Usage tracking
    model_count INTEGER DEFAULT 0, -- How many models trained on this
    last_used_date TIMESTAMPTZ,

    -- Metadata
    created_by UUID REFERENCES users(id),
    tags TEXT[],
    notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(dataset_name, dataset_version)
);

CREATE INDEX idx_training_datasets_purpose ON training_datasets(purpose, is_latest_version);
CREATE INDEX idx_training_datasets_type ON training_datasets(dataset_type, created_at DESC);

-- Training labels for supervised learning
CREATE TABLE IF NOT EXISTS training_labels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Label identification
    entity_type VARCHAR(100) NOT NULL, -- 'journal_entry', 'account', 'disclosure', 'anomaly'
    entity_id UUID NOT NULL, -- ID of the entity being labeled
    engagement_id UUID REFERENCES engagements(id) ON DELETE CASCADE,

    -- Label information
    label_type VARCHAR(100) NOT NULL, -- 'is_fraud', 'is_error', 'risk_level', 'materiality', 'account_type'
    label_value TEXT NOT NULL, -- Actual label value
    label_confidence DECIMAL(5,4) CHECK (label_confidence BETWEEN 0 AND 1),

    -- Label source
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('human_expert', 'model_prediction', 'rule_based', 'peer_review', 'regulatory')),
    labeler_user_id UUID REFERENCES users(id),
    labeler_role VARCHAR(50), -- 'partner', 'senior', 'ml_engineer'
    labeling_method VARCHAR(100), -- 'manual_review', 'automated_rule', 'consensus'

    -- Quality and validation
    is_validated BOOLEAN DEFAULT FALSE,
    validation_date TIMESTAMPTZ,
    validated_by UUID REFERENCES users(id),
    validation_method VARCHAR(100),

    -- Multi-labeler consensus
    total_labelers INTEGER DEFAULT 1,
    agreement_count INTEGER DEFAULT 1,
    agreement_score DECIMAL(5,4) CHECK (agreement_score BETWEEN 0 AND 1),
    alternative_labels JSONB, -- Other label suggestions

    -- Context information
    labeling_context JSONB, -- Additional context used for labeling
    evidence_ids UUID[], -- Supporting evidence references
    rationale TEXT, -- Why this label was applied

    -- Temporal information
    label_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    effective_date DATE, -- When this label becomes effective
    expiration_date DATE, -- If label has temporal validity

    -- Usage tracking
    used_in_training BOOLEAN DEFAULT FALSE,
    training_dataset_ids UUID[], -- Which datasets include this label
    model_versions_trained TEXT[], -- Which model versions used this

    -- Metadata
    tags TEXT[],
    notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_training_labels_entity ON training_labels(entity_type, entity_id);
CREATE INDEX idx_training_labels_type ON training_labels(label_type, label_value);
CREATE INDEX idx_training_labels_engagement ON training_labels(engagement_id);
CREATE INDEX idx_training_labels_validated ON training_labels(is_validated, validation_date);
CREATE INDEX idx_training_labels_source ON training_labels(source_type, labeler_user_id);

-- Model experiments tracking
CREATE TABLE IF NOT EXISTS model_experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Experiment identification
    experiment_name VARCHAR(255) NOT NULL,
    experiment_number INTEGER NOT NULL, -- Auto-incrementing experiment number
    model_type VARCHAR(100) NOT NULL, -- 'fraud_detection', 'risk_assessment', 'account_mapping', 'disclosure_generator'

    -- Model architecture
    algorithm VARCHAR(100) NOT NULL, -- 'xgboost', 'random_forest', 'neural_network', 'transformer', 'gpt-4'
    framework VARCHAR(50), -- 'scikit-learn', 'tensorflow', 'pytorch', 'openai'
    model_architecture JSONB, -- Detailed architecture config
    hyperparameters JSONB NOT NULL,

    -- Training configuration
    training_dataset_id UUID REFERENCES training_datasets(id),
    validation_dataset_id UUID REFERENCES training_datasets(id),
    test_dataset_id UUID REFERENCES training_datasets(id),
    features_used TEXT[] NOT NULL,
    feature_count INTEGER NOT NULL,

    -- Training execution
    training_start_time TIMESTAMPTZ,
    training_end_time TIMESTAMPTZ,
    training_duration_seconds INTEGER,
    epochs INTEGER,
    batch_size INTEGER,
    learning_rate DECIMAL(10,8),
    early_stopping_enabled BOOLEAN DEFAULT FALSE,
    stopped_early BOOLEAN DEFAULT FALSE,

    -- Model performance metrics
    -- Classification metrics
    accuracy DECIMAL(10,6),
    precision_score DECIMAL(10,6),
    recall_score DECIMAL(10,6),
    f1_score DECIMAL(10,6),
    roc_auc DECIMAL(10,6),
    pr_auc DECIMAL(10,6),

    -- Regression metrics
    mae DECIMAL(20,6), -- Mean Absolute Error
    mse DECIMAL(20,6), -- Mean Squared Error
    rmse DECIMAL(20,6), -- Root Mean Squared Error
    r2_score DECIMAL(10,6),

    -- Business metrics
    false_positive_rate DECIMAL(10,6),
    false_negative_rate DECIMAL(10,6),
    true_positive_count INTEGER,
    false_positive_count INTEGER,
    true_negative_count INTEGER,
    false_negative_count INTEGER,

    -- Feature importance
    feature_importance JSONB, -- Feature name -> importance score
    top_10_features TEXT[],

    -- Model artifacts
    model_artifact_uri TEXT, -- MLflow or S3 location
    checkpoint_uri TEXT,
    tensorboard_uri TEXT,

    -- Comparison with baseline
    baseline_model_id UUID REFERENCES model_experiments(id),
    improvement_over_baseline DECIMAL(10,6),
    is_best_model BOOLEAN DEFAULT FALSE,

    -- Production readiness
    is_production_ready BOOLEAN DEFAULT FALSE,
    passed_validation BOOLEAN DEFAULT FALSE,
    deployed_to_production BOOLEAN DEFAULT FALSE,
    deployment_date TIMESTAMPTZ,

    -- Resource utilization
    gpu_hours DECIMAL(10,2),
    cpu_hours DECIMAL(10,2),
    memory_peak_gb DECIMAL(10,2),
    training_cost_usd DECIMAL(10,2),

    -- Metadata
    researcher_id UUID REFERENCES users(id),
    tags TEXT[],
    notes TEXT,
    git_commit_hash VARCHAR(40),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(experiment_name, experiment_number)
);

CREATE INDEX idx_model_experiments_type ON model_experiments(model_type, f1_score DESC);
CREATE INDEX idx_model_experiments_best ON model_experiments(is_best_model, is_production_ready);
CREATE INDEX idx_model_experiments_performance ON model_experiments(roc_auc DESC, f1_score DESC);

-- Model predictions and confidence tracking
CREATE TABLE IF NOT EXISTS model_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Prediction identification
    model_experiment_id UUID REFERENCES model_experiments(id),
    model_version VARCHAR(50) NOT NULL,

    -- Entity being predicted
    entity_type VARCHAR(100) NOT NULL, -- 'journal_entry', 'account', 'disclosure', 'risk'
    entity_id UUID NOT NULL,
    engagement_id UUID REFERENCES engagements(id) ON DELETE CASCADE,

    -- Prediction details
    prediction_type VARCHAR(100) NOT NULL, -- 'fraud_probability', 'risk_score', 'account_classification', 'disclosure_text'
    predicted_value TEXT NOT NULL,
    prediction_confidence DECIMAL(5,4) CHECK (prediction_confidence BETWEEN 0 AND 1),
    prediction_probabilities JSONB, -- Full probability distribution for multi-class

    -- Model explanation (XAI - Explainable AI)
    feature_contributions JSONB, -- SHAP values or feature importance for this prediction
    top_influencing_features TEXT[], -- Top 5-10 features
    explanation_text TEXT, -- Human-readable explanation

    -- Prediction context
    input_features JSONB NOT NULL, -- Features used for this prediction
    prediction_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    inference_time_ms INTEGER, -- How long inference took

    -- Validation and feedback
    actual_value TEXT, -- Ground truth once known
    is_correct BOOLEAN, -- True if prediction matches actual
    prediction_error DECIMAL(20,6), -- For regression tasks

    -- Human feedback
    feedback_received BOOLEAN DEFAULT FALSE,
    feedback_date TIMESTAMPTZ,
    feedback_user_id UUID REFERENCES users(id),
    feedback_type VARCHAR(50) CHECK (feedback_type IN ('correct', 'incorrect', 'partially_correct', 'unsure')),
    feedback_comments TEXT,

    -- Impact tracking
    action_taken VARCHAR(100), -- What action was taken based on prediction
    action_date TIMESTAMPTZ,
    action_user_id UUID REFERENCES users(id),

    -- Model monitoring
    is_anomalous_prediction BOOLEAN DEFAULT FALSE, -- Drift detection
    drift_score DECIMAL(5,4),
    requires_review BOOLEAN DEFAULT FALSE,
    reviewed BOOLEAN DEFAULT FALSE,
    review_date TIMESTAMPTZ,
    reviewer_id UUID REFERENCES users(id),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_model_predictions_entity ON model_predictions(entity_type, entity_id);
CREATE INDEX idx_model_predictions_model ON model_predictions(model_experiment_id, prediction_timestamp DESC);
CREATE INDEX idx_model_predictions_engagement ON model_predictions(engagement_id);
CREATE INDEX idx_model_predictions_feedback ON model_predictions(feedback_received, is_correct);
CREATE INDEX idx_model_predictions_review ON model_predictions(requires_review, reviewed);

-- Human feedback loop for continuous learning
CREATE TABLE IF NOT EXISTS human_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Feedback identification
    feedback_type VARCHAR(100) NOT NULL, -- 'model_correction', 'label_validation', 'feature_suggestion', 'false_positive', 'false_negative'
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    engagement_id UUID REFERENCES engagements(id) ON DELETE CASCADE,

    -- User providing feedback
    user_id UUID NOT NULL REFERENCES users(id),
    user_role VARCHAR(50) NOT NULL,
    user_expertise_level VARCHAR(50) CHECK (user_expertise_level IN ('junior', 'senior', 'manager', 'partner', 'expert')),

    -- Original prediction (if applicable)
    original_prediction_id UUID REFERENCES model_predictions(id),
    original_value TEXT,
    original_confidence DECIMAL(5,4),

    -- Corrected information
    corrected_value TEXT,
    correction_confidence DECIMAL(5,4) CHECK (correction_confidence BETWEEN 0 AND 1),
    correction_rationale TEXT NOT NULL,
    supporting_evidence_ids UUID[],

    -- Feedback details
    feedback_context JSONB, -- Additional context
    is_critical_feedback BOOLEAN DEFAULT FALSE, -- High-priority correction
    requires_model_retrain BOOLEAN DEFAULT FALSE,

    -- Processing status
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'incorporated', 'rejected', 'deferred')),
    reviewed_by UUID REFERENCES users(id),
    review_date TIMESTAMPTZ,
    review_notes TEXT,

    -- Impact tracking
    incorporated_in_dataset_id UUID REFERENCES training_datasets(id),
    incorporated_in_model_version VARCHAR(50),
    incorporation_date TIMESTAMPTZ,

    -- Quality scoring
    feedback_quality_score DECIMAL(5,4) CHECK (feedback_quality_score BETWEEN 0 AND 1),
    agreement_with_other_experts DECIMAL(5,4),

    -- Metadata
    tags TEXT[],

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_human_feedback_entity ON human_feedback(entity_type, entity_id);
CREATE INDEX idx_human_feedback_user ON human_feedback(user_id, created_at DESC);
CREATE INDEX idx_human_feedback_status ON human_feedback(status, requires_model_retrain);
CREATE INDEX idx_human_feedback_engagement ON human_feedback(engagement_id);

-- =====================================================
-- SECTION 3: DATA QUALITY & LINEAGE
-- Purpose: Track data quality, transformations, and end-to-end lineage
-- =====================================================

-- Data quality metrics at the table level
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Target identification
    schema_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100), -- NULL for table-level metrics

    -- Measurement period
    measurement_date DATE NOT NULL DEFAULT CURRENT_DATE,
    measurement_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Completeness metrics
    total_row_count BIGINT NOT NULL,
    non_null_count BIGINT,
    null_count BIGINT,
    null_percentage DECIMAL(5,4),
    completeness_score DECIMAL(5,4) CHECK (completeness_score BETWEEN 0 AND 1),

    -- Accuracy metrics
    valid_value_count BIGINT,
    invalid_value_count BIGINT,
    validation_rule TEXT, -- The validation rule applied
    accuracy_score DECIMAL(5,4) CHECK (accuracy_score BETWEEN 0 AND 1),

    -- Consistency metrics
    duplicate_count BIGINT,
    unique_value_count BIGINT,
    consistency_score DECIMAL(5,4) CHECK (consistency_score BETWEEN 0 AND 1),

    -- Timeliness metrics
    latest_record_timestamp TIMESTAMPTZ,
    oldest_record_timestamp TIMESTAMPTZ,
    avg_data_age_days DECIMAL(10,2),
    stale_record_count BIGINT, -- Records older than threshold
    timeliness_score DECIMAL(5,4) CHECK (timeliness_score BETWEEN 0 AND 1),

    -- Data distribution (for numerical columns)
    min_value DECIMAL(20,4),
    max_value DECIMAL(20,4),
    mean_value DECIMAL(20,4),
    median_value DECIMAL(20,4),
    std_dev DECIMAL(20,4),
    quartile_25 DECIMAL(20,4),
    quartile_75 DECIMAL(20,4),

    -- Anomaly detection
    outlier_count BIGINT,
    outlier_percentage DECIMAL(5,4),
    anomaly_threshold DECIMAL(20,4),

    -- Overall quality
    overall_quality_score DECIMAL(5,4) CHECK (overall_quality_score BETWEEN 0 AND 1),
    quality_grade VARCHAR(2) CHECK (quality_grade IN ('A', 'B', 'C', 'D', 'F')),
    issues_detected TEXT[],

    -- Thresholds and SLAs
    expected_completeness_threshold DECIMAL(5,4),
    expected_accuracy_threshold DECIMAL(5,4),
    meets_sla BOOLEAN DEFAULT TRUE,
    sla_violations TEXT[],

    -- Alerting
    requires_attention BOOLEAN DEFAULT FALSE,
    alert_sent BOOLEAN DEFAULT FALSE,
    alert_sent_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dq_metrics_table ON data_quality_metrics(schema_name, table_name, measurement_date DESC);
CREATE INDEX idx_dq_metrics_quality ON data_quality_metrics(overall_quality_score, meets_sla);
CREATE INDEX idx_dq_metrics_alerts ON data_quality_metrics(requires_attention, alert_sent);

-- Data transformation tracking
CREATE TABLE IF NOT EXISTS data_transformations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Transformation identification
    transformation_name VARCHAR(255) NOT NULL,
    transformation_type VARCHAR(100) NOT NULL, -- 'etl', 'normalization', 'aggregation', 'enrichment', 'validation', 'feature_engineering'
    transformation_version VARCHAR(50) NOT NULL,

    -- Source and target
    source_schema VARCHAR(100),
    source_table VARCHAR(100),
    source_columns TEXT[],
    target_schema VARCHAR(100),
    target_table VARCHAR(100),
    target_columns TEXT[],

    -- Transformation logic
    transformation_sql TEXT, -- SQL logic if applicable
    transformation_code TEXT, -- Python/other code if applicable
    transformation_rules JSONB, -- Structured rules

    -- Execution tracking
    execution_id UUID NOT NULL, -- Unique ID for this execution
    execution_start_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_end_time TIMESTAMPTZ,
    execution_duration_seconds INTEGER,
    execution_status VARCHAR(50) DEFAULT 'running' CHECK (execution_status IN ('running', 'success', 'failed', 'partial', 'cancelled')),

    -- Data volume
    input_row_count BIGINT,
    output_row_count BIGINT,
    inserted_row_count BIGINT,
    updated_row_count BIGINT,
    deleted_row_count BIGINT,
    rejected_row_count BIGINT,

    -- Data quality impact
    quality_score_before DECIMAL(5,4),
    quality_score_after DECIMAL(5,4),
    quality_improvement DECIMAL(5,4),

    -- Error handling
    error_count INTEGER DEFAULT 0,
    error_messages TEXT[],
    rejected_records_location TEXT, -- Where rejected records are stored

    -- Performance metrics
    records_per_second DECIMAL(10,2),
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_mb DECIMAL(10,2),

    -- Lineage
    parent_transformation_id UUID REFERENCES data_transformations(id),
    triggered_by VARCHAR(100), -- 'schedule', 'event', 'manual', 'api'
    triggered_by_user_id UUID REFERENCES users(id),

    -- Metadata
    tags TEXT[],
    notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_data_transformations_name ON data_transformations(transformation_name, execution_start_time DESC);
CREATE INDEX idx_data_transformations_status ON data_transformations(execution_status, execution_start_time DESC);
CREATE INDEX idx_data_transformations_lineage ON data_transformations(parent_transformation_id);

-- End-to-end data lineage tracking
CREATE TABLE IF NOT EXISTS data_lineage_graph (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Node identification
    node_type VARCHAR(100) NOT NULL, -- 'source', 'table', 'view', 'transformation', 'model', 'report', 'api'
    node_identifier VARCHAR(500) NOT NULL, -- Unique identifier for the node
    node_name VARCHAR(255) NOT NULL,

    -- Node details
    schema_name VARCHAR(100),
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    node_metadata JSONB,

    -- Relationships (edges in the graph)
    parent_node_ids UUID[], -- Direct upstream dependencies
    child_node_ids UUID[], -- Direct downstream dependencies

    -- Lineage level
    distance_from_source INTEGER DEFAULT 0, -- How many hops from original source
    distance_to_target INTEGER, -- How many hops to final output

    -- Data flow
    data_flow_direction VARCHAR(50) CHECK (data_flow_direction IN ('upstream', 'downstream', 'bidirectional')),
    estimated_data_volume_gb DECIMAL(10,2),
    refresh_frequency VARCHAR(50), -- 'real-time', 'hourly', 'daily', 'weekly', 'on-demand'

    -- Criticality
    criticality_level VARCHAR(50) CHECK (criticality_level IN ('low', 'medium', 'high', 'critical')),
    downstream_impact_count INTEGER, -- How many downstream nodes depend on this
    is_in_production BOOLEAN DEFAULT FALSE,

    -- Quality and monitoring
    data_quality_score DECIMAL(5,4) CHECK (data_quality_score BETWEEN 0 AND 1),
    last_update_timestamp TIMESTAMPTZ,
    is_stale BOOLEAN DEFAULT FALSE,
    staleness_threshold_hours INTEGER,

    -- Owner and governance
    owner_user_id UUID REFERENCES users(id),
    steward_user_id UUID REFERENCES users(id),
    classification VARCHAR(50), -- 'public', 'internal', 'confidential', 'restricted'
    compliance_tags TEXT[], -- 'PII', 'GDPR', 'SOC2', 'PCAOB'

    -- Versioning
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    deprecated_date TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(node_type, node_identifier)
);

CREATE INDEX idx_data_lineage_node ON data_lineage_graph(node_type, node_identifier);
CREATE INDEX idx_data_lineage_parents ON data_lineage_graph USING GIN(parent_node_ids);
CREATE INDEX idx_data_lineage_children ON data_lineage_graph USING GIN(child_node_ids);
CREATE INDEX idx_data_lineage_criticality ON data_lineage_graph(criticality_level, downstream_impact_count DESC);

-- =====================================================
-- SECTION 4: ADVANCED ANALYTICS & BENCHMARKING
-- Purpose: Industry benchmarks, peer comparisons, and advanced analytics
-- =====================================================

-- Industry benchmarks for comparative analysis
CREATE TABLE IF NOT EXISTS industry_benchmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Industry classification
    industry_sector VARCHAR(100) NOT NULL, -- 'Technology', 'Healthcare', 'Manufacturing', 'Financial Services', etc.
    industry_subsector VARCHAR(100), -- More granular classification
    naics_code VARCHAR(10), -- North American Industry Classification System
    sic_code VARCHAR(10), -- Standard Industrial Classification

    -- Company size classification
    size_category VARCHAR(50) NOT NULL CHECK (size_category IN ('micro', 'small', 'medium', 'large', 'enterprise')),
    revenue_range_min DECIMAL(20,2),
    revenue_range_max DECIMAL(20,2),
    employee_range_min INTEGER,
    employee_range_max INTEGER,

    -- Benchmark period
    benchmark_period DATE NOT NULL,
    period_type VARCHAR(20) CHECK (period_type IN ('monthly', 'quarterly', 'yearly')),
    fiscal_year INTEGER,

    -- Financial benchmarks
    avg_current_ratio DECIMAL(10,4),
    avg_quick_ratio DECIMAL(10,4),
    avg_debt_to_equity DECIMAL(10,4),
    avg_gross_margin DECIMAL(10,4),
    avg_operating_margin DECIMAL(10,4),
    avg_net_margin DECIMAL(10,4),
    avg_roa DECIMAL(10,4),
    avg_roe DECIMAL(10,4),
    avg_asset_turnover DECIMAL(10,4),
    avg_inventory_turnover DECIMAL(10,4),
    avg_receivables_turnover DECIMAL(10,4),

    -- Distribution statistics (percentiles)
    current_ratio_p25 DECIMAL(10,4),
    current_ratio_p50 DECIMAL(10,4),
    current_ratio_p75 DECIMAL(10,4),
    gross_margin_p25 DECIMAL(10,4),
    gross_margin_p50 DECIMAL(10,4),
    gross_margin_p75 DECIMAL(10,4),
    roe_p25 DECIMAL(10,4),
    roe_p50 DECIMAL(10,4),
    roe_p75 DECIMAL(10,4),

    -- Operational benchmarks
    avg_revenue_per_employee DECIMAL(20,2),
    avg_days_sales_outstanding DECIMAL(10,2),
    avg_days_inventory_outstanding DECIMAL(10,2),
    avg_cash_conversion_cycle DECIMAL(10,2),

    -- Growth benchmarks
    avg_revenue_growth_rate DECIMAL(10,4),
    avg_earnings_growth_rate DECIMAL(10,4),
    avg_employee_growth_rate DECIMAL(10,4),

    -- Risk indicators
    avg_bankruptcy_risk_score DECIMAL(5,4),
    avg_fraud_prevalence_rate DECIMAL(5,4),
    avg_restatement_rate DECIMAL(5,4),

    -- Sample statistics
    sample_size INTEGER NOT NULL, -- Number of companies in benchmark
    data_source VARCHAR(255), -- 'SEC EDGAR', 'Bloomberg', 'S&P Capital IQ', 'Internal Database'
    confidence_level DECIMAL(5,4), -- Statistical confidence

    -- Metadata
    created_by UUID REFERENCES users(id),
    last_updated_by UUID REFERENCES users(id),
    data_quality_score DECIMAL(5,4) CHECK (data_quality_score BETWEEN 0 AND 1),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(industry_sector, industry_subsector, size_category, benchmark_period)
);

CREATE INDEX idx_industry_benchmarks_sector ON industry_benchmarks(industry_sector, industry_subsector, benchmark_period DESC);
CREATE INDEX idx_industry_benchmarks_size ON industry_benchmarks(size_category, fiscal_year DESC);
CREATE INDEX idx_industry_benchmarks_naics ON industry_benchmarks(naics_code, benchmark_period DESC);

-- External data integration (market data, news, economic indicators)
CREATE TABLE IF NOT EXISTS external_data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source identification
    source_name VARCHAR(255) NOT NULL,
    source_type VARCHAR(100) NOT NULL, -- 'market_data', 'news', 'economic_indicators', 'regulatory_filings', 'social_media', 'credit_ratings'
    source_url TEXT,
    api_endpoint TEXT,

    -- Entity linkage
    entity_type VARCHAR(100), -- 'organization', 'engagement', 'industry'
    entity_id UUID,
    engagement_id UUID REFERENCES engagements(id) ON DELETE CASCADE,

    -- Data content
    data_category VARCHAR(100) NOT NULL, -- 'stock_price', 'earnings_announcement', 'credit_rating_change', 'news_sentiment', 'macro_indicator'
    data_timestamp TIMESTAMPTZ NOT NULL,
    data_value JSONB NOT NULL, -- Flexible storage for various data types

    -- Structured fields (for common use cases)
    numeric_value DECIMAL(20,4),
    text_value TEXT,
    sentiment_score DECIMAL(5,4) CHECK (sentiment_score BETWEEN -1 AND 1), -- -1 (negative) to 1 (positive)

    -- Relevance and impact
    relevance_score DECIMAL(5,4) CHECK (relevance_score BETWEEN 0 AND 1),
    impact_level VARCHAR(50) CHECK (impact_level IN ('low', 'medium', 'high', 'critical')),
    risk_indicator VARCHAR(50), -- 'positive', 'negative', 'neutral', 'mixed'

    -- Processing status
    is_processed BOOLEAN DEFAULT FALSE,
    processed_date TIMESTAMPTZ,
    incorporated_in_analysis BOOLEAN DEFAULT FALSE,
    analysis_ids UUID[], -- References to analyses that used this data

    -- Data quality
    data_quality_score DECIMAL(5,4) CHECK (data_quality_score BETWEEN 0 AND 1),
    confidence_score DECIMAL(5,4) CHECK (confidence_score BETWEEN 0 AND 1),
    source_credibility VARCHAR(50) CHECK (source_credibility IN ('low', 'medium', 'high', 'verified')),

    -- Metadata
    tags TEXT[],
    notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_external_data_type ON external_data_sources(source_type, data_category, data_timestamp DESC);
CREATE INDEX idx_external_data_entity ON external_data_sources(entity_type, entity_id);
CREATE INDEX idx_external_data_engagement ON external_data_sources(engagement_id);
CREATE INDEX idx_external_data_sentiment ON external_data_sources(sentiment_score, impact_level);

-- Peer company analysis
CREATE TABLE IF NOT EXISTS peer_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Target company (the one being audited)
    target_organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    target_engagement_id UUID REFERENCES engagements(id) ON DELETE CASCADE,

    -- Peer company
    peer_company_name VARCHAR(255) NOT NULL,
    peer_ticker_symbol VARCHAR(10),
    peer_cik VARCHAR(10), -- SEC CIK number
    peer_organization_id UUID REFERENCES organizations(id), -- If peer is also a client

    -- Similarity metrics
    similarity_score DECIMAL(5,4) CHECK (similarity_score BETWEEN 0 AND 1), -- Overall similarity
    industry_similarity DECIMAL(5,4) CHECK (industry_similarity BETWEEN 0 AND 1),
    size_similarity DECIMAL(5,4) CHECK (size_similarity BETWEEN 0 AND 1),
    business_model_similarity DECIMAL(5,4) CHECK (business_model_similarity BETWEEN 0 AND 1),

    -- Peer characteristics
    peer_industry_sector VARCHAR(100),
    peer_industry_subsector VARCHAR(100),
    peer_revenue DECIMAL(20,2),
    peer_employee_count INTEGER,
    peer_market_cap DECIMAL(20,2),
    peer_fiscal_year_end VARCHAR(10), -- MM-DD format

    -- Comparison basis
    comparison_period DATE NOT NULL,
    selection_method VARCHAR(100), -- 'manual', 'algorithm', 'industry_standard', 'regulatory_requirement'
    selection_rationale TEXT,

    -- Usage tracking
    is_active_peer BOOLEAN DEFAULT TRUE,
    used_in_analyses INTEGER DEFAULT 0,
    last_used_date TIMESTAMPTZ,

    -- Metadata
    added_by UUID REFERENCES users(id),
    tags TEXT[],
    notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_peer_companies_target ON peer_companies(target_organization_id, is_active_peer);
CREATE INDEX idx_peer_companies_engagement ON peer_companies(target_engagement_id);
CREATE INDEX idx_peer_companies_similarity ON peer_companies(similarity_score DESC);

-- Entity relationship networks (for fraud detection)
CREATE TABLE IF NOT EXISTS entity_networks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Network identification
    network_id UUID NOT NULL, -- Groups related entities
    network_type VARCHAR(100) NOT NULL, -- 'vendor_network', 'employee_network', 'related_party', 'shell_company_network'

    -- Entities in relationship
    entity_1_type VARCHAR(100) NOT NULL, -- 'organization', 'user', 'vendor', 'account', 'address', 'bank_account'
    entity_1_id VARCHAR(255) NOT NULL,
    entity_1_name VARCHAR(255),

    entity_2_type VARCHAR(100) NOT NULL,
    entity_2_id VARCHAR(255) NOT NULL,
    entity_2_name VARCHAR(255),

    -- Relationship details
    relationship_type VARCHAR(100) NOT NULL, -- 'owns', 'controls', 'employed_by', 'transacts_with', 'shares_address', 'shares_bank_account'
    relationship_strength DECIMAL(5,4) CHECK (relationship_strength BETWEEN 0 AND 1), -- 0 (weak) to 1 (strong)
    relationship_confidence DECIMAL(5,4) CHECK (relationship_confidence BETWEEN 0 AND 1),

    -- Temporal aspects
    relationship_start_date DATE,
    relationship_end_date DATE,
    is_current BOOLEAN DEFAULT TRUE,

    -- Evidence
    evidence_count INTEGER DEFAULT 0,
    evidence_types TEXT[], -- 'transaction', 'document', 'public_record', 'declaration'
    evidence_references JSONB, -- Links to supporting evidence

    -- Risk indicators
    is_suspicious BOOLEAN DEFAULT FALSE,
    risk_score DECIMAL(5,4) CHECK (risk_score BETWEEN 0 AND 1),
    risk_reasons TEXT[], -- Why this relationship is suspicious

    -- Related party designation (for audit purposes)
    is_related_party BOOLEAN DEFAULT FALSE,
    related_party_type VARCHAR(100), -- 'subsidiary', 'affiliate', 'joint_venture', 'key_management', 'close_family'
    requires_disclosure BOOLEAN DEFAULT FALSE,

    -- Network analysis
    centrality_score DECIMAL(10,6), -- How central this node is in the network
    clustering_coefficient DECIMAL(5,4), -- How connected the neighbors are
    degree_in INTEGER, -- Incoming connections
    degree_out INTEGER, -- Outgoing connections

    -- Detection and tracking
    detected_by_model VARCHAR(100),
    detection_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    reviewed BOOLEAN DEFAULT FALSE,
    review_date TIMESTAMPTZ,
    reviewer_id UUID REFERENCES users(id),
    review_outcome VARCHAR(100), -- 'legitimate', 'suspicious', 'fraudulent', 'requires_further_investigation'

    -- Metadata
    engagement_id UUID REFERENCES engagements(id) ON DELETE CASCADE,
    tags TEXT[],
    notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_entity_networks_network ON entity_networks(network_id);
CREATE INDEX idx_entity_networks_entities ON entity_networks(entity_1_type, entity_1_id, entity_2_type, entity_2_id);
CREATE INDEX idx_entity_networks_engagement ON entity_networks(engagement_id);
CREATE INDEX idx_entity_networks_risk ON entity_networks(is_suspicious, risk_score DESC);
CREATE INDEX idx_entity_networks_related_party ON entity_networks(is_related_party, requires_disclosure);

-- =====================================================
-- SECTION 5: AUDIT INTELLIGENCE & PATTERN RECOGNITION
-- Purpose: Learn from historical audits to improve future performance
-- =====================================================

-- Historical audit findings patterns
CREATE TABLE IF NOT EXISTS historical_audit_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Audit identification
    historical_engagement_id UUID, -- May reference old engagement or be external
    audit_firm_name VARCHAR(255),
    audit_year INTEGER NOT NULL,
    audit_quarter INTEGER,

    -- Client information
    client_organization_id UUID REFERENCES organizations(id),
    client_name VARCHAR(255) NOT NULL,
    client_industry VARCHAR(100),
    client_size_category VARCHAR(50),
    client_revenue DECIMAL(20,2),

    -- Finding details
    finding_type VARCHAR(100) NOT NULL, -- 'material_weakness', 'significant_deficiency', 'control_deficiency', 'misstatement', 'fraud', 'going_concern'
    finding_category VARCHAR(100), -- 'revenue_recognition', 'inventory', 'internal_controls', 'disclosure', 'related_party'
    finding_severity VARCHAR(50) CHECK (finding_severity IN ('low', 'moderate', 'significant', 'material', 'critical')),

    -- Description
    finding_title VARCHAR(500) NOT NULL,
    finding_description TEXT NOT NULL,
    finding_impact_description TEXT,

    -- Financial impact
    financial_impact_amount DECIMAL(20,2),
    percentage_of_revenue DECIMAL(10,4),
    percentage_of_assets DECIMAL(10,4),
    is_material BOOLEAN DEFAULT FALSE,
    materiality_threshold DECIMAL(20,2),

    -- Root cause
    root_cause TEXT,
    root_cause_category VARCHAR(100), -- 'process_failure', 'control_failure', 'human_error', 'fraud', 'system_error', 'management_override'

    -- Accounts affected
    affected_account_types TEXT[], -- 'revenue', 'inventory', 'receivables', etc.
    affected_accounts JSONB, -- Specific account details

    -- Detection method
    detected_by VARCHAR(100), -- 'internal_audit', 'external_audit', 'management', 'whistleblower', 'regulatory_exam', 'ai_model'
    detection_method VARCHAR(255), -- Specific method or test that found it

    -- Remediation
    remediation_actions TEXT[],
    remediation_status VARCHAR(50) CHECK (remediation_status IN ('open', 'in_progress', 'remediated', 'monitoring', 'accepted_risk')),
    remediation_date DATE,
    remediation_cost DECIMAL(20,2),

    -- Recurrence
    is_recurring BOOLEAN DEFAULT FALSE, -- Did this issue occur before?
    previous_occurrence_ids UUID[], -- References to previous similar findings
    recurrence_count INTEGER DEFAULT 0,

    -- Learning value
    learning_importance DECIMAL(5,4) CHECK (learning_importance BETWEEN 0 AND 1),
    applicable_to_industries TEXT[], -- Which industries should learn from this
    applicable_to_account_types TEXT[],

    -- Similar pattern matching
    pattern_signature VARCHAR(500), -- Hash or signature for similarity matching
    embedding_vector VECTOR(1536), -- For semantic similarity search

    -- Regulatory reporting
    reported_to_regulators BOOLEAN DEFAULT FALSE,
    regulatory_bodies TEXT[], -- 'SEC', 'PCAOB', 'AICPA', etc.
    public_disclosure_required BOOLEAN DEFAULT FALSE,

    -- Data source
    data_source VARCHAR(255), -- 'internal_database', 'sec_filings', 'pcaob_inspections', 'manual_entry'
    source_document_url TEXT,
    confidence_score DECIMAL(5,4) CHECK (confidence_score BETWEEN 0 AND 1),

    -- Metadata
    created_by UUID REFERENCES users(id),
    tags TEXT[],
    notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_historical_findings_year ON historical_audit_findings(audit_year DESC, finding_severity);
CREATE INDEX idx_historical_findings_type ON historical_audit_findings(finding_type, finding_category);
CREATE INDEX idx_historical_findings_client ON historical_audit_findings(client_organization_id, audit_year DESC);
CREATE INDEX idx_historical_findings_material ON historical_audit_findings(is_material, financial_impact_amount DESC);
CREATE INDEX idx_historical_findings_embedding ON historical_audit_findings USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_historical_findings_industry ON historical_audit_findings USING GIN(applicable_to_industries);

-- Audit risk assessment patterns
CREATE TABLE IF NOT EXISTS risk_pattern_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Risk pattern identification
    pattern_name VARCHAR(255) NOT NULL UNIQUE,
    pattern_code VARCHAR(50) UNIQUE,
    pattern_category VARCHAR(100) NOT NULL, -- 'fraud_red_flag', 'going_concern_indicator', 'control_weakness', 'account_risk'

    -- Pattern description
    description TEXT NOT NULL,
    indicators TEXT[] NOT NULL, -- List of indicators that suggest this pattern

    -- Detection logic
    detection_rules JSONB NOT NULL, -- Structured rules for automatic detection
    sql_query TEXT, -- SQL query to detect this pattern
    required_data_elements TEXT[], -- What data is needed to detect this

    -- Risk characteristics
    risk_type VARCHAR(100) NOT NULL, -- 'fraud', 'error', 'going_concern', 'disclosure', 'valuation'
    inherent_risk_level VARCHAR(50) CHECK (inherent_risk_level IN ('low', 'moderate', 'high', 'very_high')),
    typical_financial_impact VARCHAR(50), -- 'minimal', 'moderate', 'significant', 'material'

    -- Industry applicability
    applicable_industries TEXT[],
    applicable_account_types TEXT[],
    applicable_transaction_types TEXT[],

    -- Statistical information
    historical_occurrence_rate DECIMAL(10,6), -- How often this pattern appears
    false_positive_rate DECIMAL(10,6),
    true_positive_rate DECIMAL(10,6),
    detection_accuracy DECIMAL(5,4) CHECK (detection_accuracy BETWEEN 0 AND 1),

    -- Audit response
    recommended_procedures TEXT[], -- What audit procedures to perform
    recommended_sample_size INTEGER,
    estimated_testing_hours DECIMAL(10,2),

    -- Regulatory references
    regulatory_standards TEXT[], -- 'PCAOB AS 2401', 'SAS 145', etc.
    regulatory_requirements TEXT,

    -- Learning and evolution
    pattern_version INTEGER DEFAULT 1,
    times_detected INTEGER DEFAULT 0,
    times_confirmed INTEGER DEFAULT 0, -- True positives
    times_false_alarm INTEGER DEFAULT 0, -- False positives
    last_detected_date TIMESTAMPTZ,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    confidence_level VARCHAR(50) CHECK (confidence_level IN ('experimental', 'validated', 'proven', 'deprecated')),

    -- Metadata
    created_by UUID REFERENCES users(id),
    last_updated_by UUID REFERENCES users(id),
    tags TEXT[],
    references TEXT[], -- Academic papers, articles, case studies

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_patterns_category ON risk_pattern_library(pattern_category, is_active);
CREATE INDEX idx_risk_patterns_risk_type ON risk_pattern_library(risk_type, inherent_risk_level);
CREATE INDEX idx_risk_patterns_accuracy ON risk_pattern_library(detection_accuracy DESC, confidence_level);
CREATE INDEX idx_risk_patterns_industries ON risk_pattern_library USING GIN(applicable_industries);

-- Pattern detection instances
CREATE TABLE IF NOT EXISTS detected_risk_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Pattern and engagement
    risk_pattern_id UUID NOT NULL REFERENCES risk_pattern_library(id),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,

    -- Detection details
    detected_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    detected_by_model VARCHAR(100),
    detection_confidence DECIMAL(5,4) CHECK (detection_confidence BETWEEN 0 AND 1),

    -- Evidence
    evidence_entity_type VARCHAR(100), -- 'journal_entry', 'account', 'transaction_sequence', 'ratio'
    evidence_entity_ids UUID[],
    evidence_description TEXT,
    supporting_data JSONB,

    -- Assessment
    assessed_risk_level VARCHAR(50) CHECK (assessed_risk_level IN ('low', 'moderate', 'high', 'very_high')),
    likelihood DECIMAL(5,4) CHECK (likelihood BETWEEN 0 AND 1),
    potential_impact DECIMAL(20,2),

    -- Response
    response_required BOOLEAN DEFAULT TRUE,
    response_status VARCHAR(50) DEFAULT 'pending' CHECK (response_status IN ('pending', 'planned', 'in_progress', 'completed', 'not_required')),
    assigned_to_user_id UUID REFERENCES users(id),
    procedures_performed TEXT[],

    -- Outcome
    is_confirmed BOOLEAN, -- NULL if not yet investigated, TRUE/FALSE after investigation
    confirmation_date TIMESTAMPTZ,
    confirmed_by_user_id UUID REFERENCES users(id),
    actual_finding_id UUID REFERENCES historical_audit_findings(id), -- If it led to actual finding

    -- False positive analysis
    is_false_positive BOOLEAN,
    false_positive_reason TEXT,

    -- Resolution
    resolution_date TIMESTAMPTZ,
    resolution_summary TEXT,
    hours_spent DECIMAL(10,2),

    -- Feedback loop
    feedback_to_model BOOLEAN DEFAULT FALSE, -- Whether this was used to improve the model
    model_improvement_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_detected_patterns_engagement ON detected_risk_patterns(engagement_id, detected_date DESC);
CREATE INDEX idx_detected_patterns_pattern ON detected_risk_patterns(risk_pattern_id, is_confirmed);
CREATE INDEX idx_detected_patterns_status ON detected_risk_patterns(response_status, assigned_to_user_id);
CREATE INDEX idx_detected_patterns_confirmed ON detected_risk_patterns(is_confirmed, is_false_positive);

-- Materiality calculations and tracking
CREATE TABLE IF NOT EXISTS materiality_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Engagement reference
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,

    -- Assessment period
    assessment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    fiscal_year INTEGER NOT NULL,
    fiscal_period INTEGER,

    -- Materiality basis
    materiality_basis VARCHAR(100) NOT NULL, -- 'revenue', 'assets', 'net_income', 'equity', 'custom'
    basis_amount DECIMAL(20,2) NOT NULL,

    -- Overall materiality
    overall_materiality DECIMAL(20,2) NOT NULL,
    overall_materiality_percentage DECIMAL(5,4), -- Percentage of basis
    calculation_method VARCHAR(255), -- 'fixed_percentage', 'sliding_scale', 'rule_of_thumb', 'ai_recommended'

    -- Performance materiality
    performance_materiality DECIMAL(20,2) NOT NULL,
    performance_materiality_percentage DECIMAL(5,4), -- Typically 50-75% of overall materiality

    -- Specific materiality (for specific classes of transactions)
    specific_materiality_items JSONB, -- Array of {account_type, amount, rationale}

    -- Trivial threshold (clearly trivial/posting threshold)
    trivial_threshold DECIMAL(20,2) NOT NULL,
    trivial_threshold_percentage DECIMAL(5,4), -- Typically 3-5% of overall materiality

    -- Qualitative factors considered
    qualitative_factors TEXT[], -- 'regulatory_scrutiny', 'public_interest', 'debt_covenants', 'trend_reversal', etc.
    qualitative_adjustments DECIMAL(20,2), -- Adjustment amount due to qualitative factors

    -- Risk assessment impact
    fraud_risk_level VARCHAR(50),
    control_risk_level VARCHAR(50),
    inherent_risk_level VARCHAR(50),
    risk_adjustment_amount DECIMAL(20,2),

    -- Industry benchmarking
    industry_benchmark_percentage DECIMAL(5,4),
    variance_from_benchmark DECIMAL(5,4),
    benchmark_justification TEXT,

    -- AI recommendations
    ai_recommended_materiality DECIMAL(20,2),
    ai_recommendation_rationale TEXT,
    ai_confidence_score DECIMAL(5,4) CHECK (ai_confidence_score BETWEEN 0 AND 1),
    human_override BOOLEAN DEFAULT FALSE,
    override_reason TEXT,

    -- Approval workflow
    calculated_by_user_id UUID REFERENCES users(id),
    reviewed_by_user_id UUID REFERENCES users(id),
    approved_by_user_id UUID REFERENCES users(id), -- Must be partner
    approval_date TIMESTAMPTZ,

    -- Documentation
    supporting_documentation_ids UUID[],
    calculation_workpaper TEXT,
    notes TEXT,

    -- Tracking
    is_current BOOLEAN DEFAULT TRUE,
    superseded_by_id UUID REFERENCES materiality_assessments(id),
    revision_number INTEGER DEFAULT 1,
    revision_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(engagement_id, assessment_date)
);

CREATE INDEX idx_materiality_engagement ON materiality_assessments(engagement_id, is_current);
CREATE INDEX idx_materiality_date ON materiality_assessments(assessment_date DESC, fiscal_year DESC);
CREATE INDEX idx_materiality_approval ON materiality_assessments(approval_date, approved_by_user_id);

-- =====================================================
-- SECTION 6: DATA PIPELINE ORCHESTRATION
-- Purpose: Track pipeline execution, dependencies, and health
-- =====================================================

-- Pipeline job definitions
CREATE TABLE IF NOT EXISTS pipeline_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Job identification
    job_name VARCHAR(255) NOT NULL UNIQUE,
    job_type VARCHAR(100) NOT NULL, -- 'ingestion', 'normalization', 'transformation', 'enrichment', 'ml_training', 'reporting'
    job_description TEXT,

    -- Job configuration
    job_config JSONB NOT NULL,
    parameters JSONB,
    environment VARCHAR(50) DEFAULT 'production' CHECK (environment IN ('development', 'staging', 'production')),

    -- Schedule
    schedule_type VARCHAR(50) NOT NULL CHECK (schedule_type IN ('cron', 'interval', 'event_driven', 'manual')),
    cron_expression VARCHAR(100), -- For cron-based schedules
    interval_minutes INTEGER, -- For interval-based schedules
    event_triggers TEXT[], -- For event-driven jobs

    -- Dependencies
    depends_on_job_ids UUID[], -- Jobs that must complete before this one
    blocks_job_ids UUID[], -- Jobs that wait for this one

    -- Execution settings
    timeout_minutes INTEGER DEFAULT 60,
    max_retries INTEGER DEFAULT 3,
    retry_delay_minutes INTEGER DEFAULT 5,
    failure_notification_emails TEXT[],

    -- Resource requirements
    cpu_cores INTEGER,
    memory_gb INTEGER,
    gpu_required BOOLEAN DEFAULT FALSE,
    estimated_duration_minutes INTEGER,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_paused BOOLEAN DEFAULT FALSE,
    last_execution_status VARCHAR(50),
    last_execution_time TIMESTAMPTZ,
    next_scheduled_time TIMESTAMPTZ,

    -- Performance tracking
    avg_duration_minutes DECIMAL(10,2),
    success_rate DECIMAL(5,4),
    total_executions INTEGER DEFAULT 0,
    successful_executions INTEGER DEFAULT 0,
    failed_executions INTEGER DEFAULT 0,

    -- Owner and alerts
    owner_user_id UUID REFERENCES users(id),
    alert_on_failure BOOLEAN DEFAULT TRUE,
    alert_on_success BOOLEAN DEFAULT FALSE,

    -- Metadata
    tags TEXT[],
    documentation_url TEXT,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pipeline_jobs_type ON pipeline_jobs(job_type, is_active);
CREATE INDEX idx_pipeline_jobs_schedule ON pipeline_jobs(next_scheduled_time, is_active, is_paused);
CREATE INDEX idx_pipeline_jobs_dependencies ON pipeline_jobs USING GIN(depends_on_job_ids);

-- Pipeline job executions
CREATE TABLE IF NOT EXISTS pipeline_job_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Job reference
    pipeline_job_id UUID NOT NULL REFERENCES pipeline_jobs(id),
    job_name VARCHAR(255) NOT NULL,

    -- Execution identification
    execution_number INTEGER NOT NULL, -- Auto-increment per job
    run_id VARCHAR(100) NOT NULL UNIQUE, -- Unique identifier for this run

    -- Trigger information
    triggered_by VARCHAR(100) NOT NULL, -- 'schedule', 'event', 'manual', 'dependency_completion', 'retry'
    triggered_by_user_id UUID REFERENCES users(id),
    trigger_event_id VARCHAR(255), -- If event-driven

    -- Execution timing
    scheduled_start_time TIMESTAMPTZ,
    actual_start_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMPTZ,
    duration_seconds INTEGER,

    -- Status tracking
    status VARCHAR(50) DEFAULT 'running' CHECK (status IN ('queued', 'running', 'success', 'failed', 'cancelled', 'timeout', 'partial_success')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),
    current_step VARCHAR(255),

    -- Input/Output
    input_parameters JSONB,
    input_record_count BIGINT,
    output_record_count BIGINT,
    processed_record_count BIGINT,
    failed_record_count BIGINT,

    -- Error handling
    error_count INTEGER DEFAULT 0,
    error_message TEXT,
    error_stack_trace TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries_reached BOOLEAN DEFAULT FALSE,

    -- Resource utilization
    cpu_usage_avg_percent DECIMAL(5,2),
    memory_usage_avg_mb DECIMAL(10,2),
    memory_usage_peak_mb DECIMAL(10,2),
    disk_read_mb DECIMAL(10,2),
    disk_write_mb DECIMAL(10,2),
    network_io_mb DECIMAL(10,2),

    -- Logs and artifacts
    log_location TEXT, -- S3/MinIO path to detailed logs
    artifact_location TEXT, -- Output artifacts location
    checkpoint_location TEXT, -- For resumable jobs

    -- Lineage
    upstream_execution_ids UUID[], -- Executions this depended on
    downstream_execution_ids UUID[], -- Executions triggered by this

    -- Data quality impact
    data_quality_before DECIMAL(5,4),
    data_quality_after DECIMAL(5,4),
    quality_improvement DECIMAL(5,4),

    -- Alerting
    alerts_sent BOOLEAN DEFAULT FALSE,
    alert_sent_to TEXT[],
    alert_timestamp TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pipeline_executions_job ON pipeline_job_executions(pipeline_job_id, actual_start_time DESC);
CREATE INDEX idx_pipeline_executions_status ON pipeline_job_executions(status, actual_start_time DESC);
CREATE INDEX idx_pipeline_executions_run_id ON pipeline_job_executions(run_id);
CREATE INDEX idx_pipeline_executions_date ON pipeline_job_executions(actual_start_time DESC);

-- Pipeline health monitoring
CREATE TABLE IF NOT EXISTS pipeline_health_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Metric identification
    metric_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
    metric_hour INTEGER CHECK (metric_hour BETWEEN 0 AND 23),

    -- Pipeline reference
    pipeline_job_id UUID REFERENCES pipeline_jobs(id),
    job_type VARCHAR(100),

    -- Execution metrics
    total_executions INTEGER NOT NULL DEFAULT 0,
    successful_executions INTEGER NOT NULL DEFAULT 0,
    failed_executions INTEGER NOT NULL DEFAULT 0,
    cancelled_executions INTEGER NOT NULL DEFAULT 0,

    -- Performance metrics
    avg_duration_seconds DECIMAL(10,2),
    min_duration_seconds INTEGER,
    max_duration_seconds INTEGER,
    p50_duration_seconds DECIMAL(10,2),
    p95_duration_seconds DECIMAL(10,2),
    p99_duration_seconds DECIMAL(10,2),

    -- Throughput metrics
    total_records_processed BIGINT,
    avg_records_per_second DECIMAL(10,2),
    total_data_volume_mb DECIMAL(20,2),
    avg_throughput_mbps DECIMAL(10,2),

    -- Error metrics
    total_errors INTEGER,
    unique_error_types INTEGER,
    most_common_error TEXT,
    error_rate DECIMAL(5,4),

    -- Resource metrics
    avg_cpu_usage_percent DECIMAL(5,2),
    avg_memory_usage_mb DECIMAL(10,2),
    peak_memory_usage_mb DECIMAL(10,2),

    -- SLA metrics
    sla_target_duration_seconds INTEGER,
    sla_compliance_rate DECIMAL(5,4), -- Percentage of runs meeting SLA
    sla_violations INTEGER,

    -- Health score
    overall_health_score DECIMAL(5,4) CHECK (overall_health_score BETWEEN 0 AND 1),
    reliability_score DECIMAL(5,4) CHECK (reliability_score BETWEEN 0 AND 1),
    performance_score DECIMAL(5,4) CHECK (performance_score BETWEEN 0 AND 1),
    efficiency_score DECIMAL(5,4) CHECK (efficiency_score BETWEEN 0 AND 1),

    -- Alerting
    health_status VARCHAR(50) CHECK (health_status IN ('healthy', 'warning', 'critical', 'unknown')),
    requires_attention BOOLEAN DEFAULT FALSE,
    attention_reasons TEXT[],

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pipeline_health_job ON pipeline_health_metrics(pipeline_job_id, metric_date DESC);
CREATE INDEX idx_pipeline_health_timestamp ON pipeline_health_metrics(metric_timestamp DESC);
CREATE INDEX idx_pipeline_health_status ON pipeline_health_metrics(health_status, requires_attention);

-- =====================================================
-- SECTION 7: ADDITIONAL INDEXES AND OPTIMIZATIONS
-- =====================================================

-- Add trigger for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update trigger to all tables with updated_at column
CREATE TRIGGER update_journal_entry_metadata_updated_at BEFORE UPDATE ON journal_entry_metadata FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transaction_sequences_updated_at BEFORE UPDATE ON transaction_sequences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_account_balance_history_updated_at BEFORE UPDATE ON account_balance_history FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_financial_ratios_timeseries_updated_at BEFORE UPDATE ON financial_ratios_timeseries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_feature_store_updated_at BEFORE UPDATE ON feature_store FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_training_datasets_updated_at BEFORE UPDATE ON training_datasets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_training_labels_updated_at BEFORE UPDATE ON training_labels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_model_experiments_updated_at BEFORE UPDATE ON model_experiments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_model_predictions_updated_at BEFORE UPDATE ON model_predictions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_human_feedback_updated_at BEFORE UPDATE ON human_feedback FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_external_data_sources_updated_at BEFORE UPDATE ON external_data_sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_peer_companies_updated_at BEFORE UPDATE ON peer_companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_entity_networks_updated_at BEFORE UPDATE ON entity_networks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_historical_audit_findings_updated_at BEFORE UPDATE ON historical_audit_findings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_risk_pattern_library_updated_at BEFORE UPDATE ON risk_pattern_library FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_detected_risk_patterns_updated_at BEFORE UPDATE ON detected_risk_patterns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_materiality_assessments_updated_at BEFORE UPDATE ON materiality_assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pipeline_jobs_updated_at BEFORE UPDATE ON pipeline_jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pipeline_job_executions_updated_at BEFORE UPDATE ON pipeline_job_executions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_data_lineage_graph_updated_at BEFORE UPDATE ON data_lineage_graph FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_industry_benchmarks_updated_at BEFORE UPDATE ON industry_benchmarks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SECTION 8: MATERIALIZED VIEWS FOR PERFORMANCE
-- =====================================================

-- Materialized view for quick engagement metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_engagement_metrics AS
SELECT
    e.id AS engagement_id,
    e.organization_id,
    e.client_name,
    e.state AS engagement_state,
    COUNT(DISTINCT je.id) AS total_journal_entries,
    COUNT(DISTINCT CASE WHEN jem.is_round_dollar THEN je.id END) AS round_dollar_entries,
    COUNT(DISTINCT CASE WHEN jem.is_statistical_outlier THEN je.id END) AS outlier_entries,
    COUNT(DISTINCT a.id) AS total_anomalies,
    COUNT(DISTINCT CASE WHEN a.severity IN ('high', 'critical') THEN a.id END) AS high_severity_anomalies,
    COUNT(DISTINCT mp.id) AS total_predictions,
    AVG(mp.prediction_confidence) AS avg_prediction_confidence,
    COUNT(DISTINCT CASE WHEN mp.feedback_received THEN mp.id END) AS predictions_with_feedback,
    COUNT(DISTINCT drp.id) AS detected_risk_patterns,
    COUNT(DISTINCT CASE WHEN drp.is_confirmed THEN drp.id END) AS confirmed_risk_patterns,
    MAX(je.created_at) AS last_journal_entry_date,
    MAX(a.created_at) AS last_anomaly_date
FROM engagements e
LEFT JOIN journal_entries je ON je.engagement_id = e.id
LEFT JOIN journal_entry_metadata jem ON jem.journal_entry_id = je.id
LEFT JOIN anomalies a ON a.engagement_id = e.id
LEFT JOIN model_predictions mp ON mp.engagement_id = e.id
LEFT JOIN detected_risk_patterns drp ON drp.engagement_id = e.id
GROUP BY e.id, e.organization_id, e.client_name, e.state;

CREATE UNIQUE INDEX idx_mv_engagement_metrics_id ON mv_engagement_metrics(engagement_id);

-- Materialized view for model performance tracking
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_model_performance AS
SELECT
    me.model_type,
    me.algorithm,
    COUNT(*) AS total_experiments,
    MAX(me.f1_score) AS best_f1_score,
    MAX(me.roc_auc) AS best_roc_auc,
    AVG(me.f1_score) AS avg_f1_score,
    AVG(me.roc_auc) AS avg_roc_auc,
    COUNT(CASE WHEN me.is_production_ready THEN 1 END) AS production_ready_count,
    COUNT(CASE WHEN me.deployed_to_production THEN 1 END) AS deployed_count,
    MAX(me.created_at) AS last_experiment_date,
    COUNT(DISTINCT mp.id) AS total_predictions,
    AVG(CASE WHEN mp.is_correct IS NOT NULL THEN
        CASE WHEN mp.is_correct THEN 1.0 ELSE 0.0 END
    END) AS production_accuracy
FROM model_experiments me
LEFT JOIN model_predictions mp ON mp.model_experiment_id = me.id
GROUP BY me.model_type, me.algorithm;

CREATE INDEX idx_mv_model_performance_type ON mv_model_performance(model_type);

-- Comments for documentation
COMMENT ON TABLE journal_entry_metadata IS 'Enhanced metadata capturing granular transaction patterns, temporal features, and behavioral characteristics for AI training';
COMMENT ON TABLE transaction_sequences IS 'Identifies and tracks recurring transaction patterns, batch processes, and sequences for anomaly detection';
COMMENT ON TABLE account_balance_history IS 'Time-series tracking of account balances with trend analysis, statistical features, and anomaly detection';
COMMENT ON TABLE financial_ratios_timeseries IS 'Comprehensive financial ratio tracking over time for trend analysis and benchmarking';
COMMENT ON TABLE feature_store IS 'Centralized feature repository for ML models with statistics, importance scores, and versioning';
COMMENT ON TABLE training_datasets IS 'Dataset definitions and metadata for model training with versioning and lineage tracking';
COMMENT ON TABLE training_labels IS 'Supervised learning labels with confidence scores, validation, and multi-labeler consensus';
COMMENT ON TABLE model_experiments IS 'Comprehensive tracking of ML experiments including hyperparameters, performance metrics, and artifacts';
COMMENT ON TABLE model_predictions IS 'Real-time prediction tracking with confidence scores, explainability, and feedback loop';
COMMENT ON TABLE human_feedback IS 'Captures expert feedback on model predictions for continuous learning and improvement';
COMMENT ON TABLE data_quality_metrics IS 'Comprehensive data quality tracking at table and column level with SLA monitoring';
COMMENT ON TABLE data_transformations IS 'Tracks all data transformations with execution metrics, lineage, and quality impact';
COMMENT ON TABLE data_lineage_graph IS 'End-to-end data lineage as a graph with upstream/downstream relationships and criticality';
COMMENT ON TABLE industry_benchmarks IS 'Industry-specific financial and operational benchmarks for comparative analysis';
COMMENT ON TABLE external_data_sources IS 'Integration of external data (market, news, economic) for enriched context';
COMMENT ON TABLE peer_companies IS 'Peer company identification and similarity metrics for comparative analysis';
COMMENT ON TABLE entity_networks IS 'Graph relationships between entities for fraud detection and related party identification';
COMMENT ON TABLE historical_audit_findings IS 'Historical audit findings patterns for learning and improving future audits';
COMMENT ON TABLE risk_pattern_library IS 'Reusable risk patterns with detection logic, accuracy metrics, and recommended procedures';
COMMENT ON TABLE detected_risk_patterns IS 'Instances of risk patterns detected in engagements with tracking and outcomes';
COMMENT ON TABLE materiality_assessments IS 'Materiality calculations with AI recommendations, qualitative factors, and approval tracking';
COMMENT ON TABLE pipeline_jobs IS 'Data pipeline job definitions with schedules, dependencies, and performance tracking';
COMMENT ON TABLE pipeline_job_executions IS 'Detailed execution logs for pipeline jobs with metrics and lineage';
COMMENT ON TABLE pipeline_health_metrics IS 'Aggregated health metrics for data pipelines with SLA tracking and alerting';

-- Grant permissions (adjust as needed for your roles)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO atlas_app;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO atlas_app;

-- =====================================================
-- END OF SCHEMA
-- =====================================================
