/*
 * Migration 010: AI Enhancements
 *
 * Adds database tables for:
 * 1. Real-Time Feedback Loop
 * 2. Industry-Specific Models
 * 3. Intelligent Sampling
 * 4. Chat Interface
 * 5. AI Explainability
 *
 * Author: Claude AI
 * Date: 2024
 */

-- ============================================================================
-- 1. AI FEEDBACK LOOP TABLES
-- ============================================================================

-- CPA feedback on AI predictions
CREATE TABLE IF NOT EXISTS ai_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Model info
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    prediction_id VARCHAR(100) NOT NULL UNIQUE,

    -- Input/Output
    input_data JSONB NOT NULL,
    ai_prediction JSONB NOT NULL,
    ai_confidence FLOAT NOT NULL CHECK (ai_confidence >= 0 AND ai_confidence <= 1),

    -- Feedback
    feedback_type VARCHAR(20) NOT NULL CHECK (feedback_type IN ('approval', 'correction', 'rejection', 'modification')),
    cpa_correction JSONB,

    -- CPA info
    cpa_id UUID NOT NULL REFERENCES users(id),
    cpa_role VARCHAR(20) NOT NULL CHECK (cpa_role IN ('partner', 'manager', 'senior', 'staff')),
    expert_weight FLOAT NOT NULL DEFAULT 1.0,

    -- Context
    engagement_id UUID REFERENCES engagements(id),
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_for_training BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_ai_feedback_model ON ai_feedback(model_name, created_at);
CREATE INDEX idx_ai_feedback_type ON ai_feedback(feedback_type);
CREATE INDEX idx_ai_feedback_cpa ON ai_feedback(cpa_id, created_at);
CREATE INDEX idx_ai_feedback_engagement ON ai_feedback(engagement_id);
CREATE INDEX idx_ai_feedback_pending_training ON ai_feedback(processed_for_training) WHERE processed_for_training = FALSE;

-- Model version registry
CREATE TABLE IF NOT EXISTS model_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Model identification
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,

    -- Status
    is_active BOOLEAN DEFAULT FALSE,
    is_ab_test BOOLEAN DEFAULT FALSE,
    ab_test_traffic_pct FLOAT CHECK (ab_test_traffic_pct >= 0 AND ab_test_traffic_pct <= 100),

    -- Performance metrics
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    baseline_accuracy FLOAT,

    -- Training info
    training_samples INTEGER,
    validation_samples INTEGER,
    training_duration_seconds INTEGER,
    training_cost_usd FLOAT,

    -- Storage
    model_uri VARCHAR(500),
    model_size_mb FLOAT,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT,

    UNIQUE(model_name, version)
);

CREATE INDEX idx_model_version_active ON model_versions(model_name, is_active);
CREATE INDEX idx_model_version_created ON model_versions(created_at DESC);

-- Feedback training queue
CREATE TABLE IF NOT EXISTS feedback_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    feedback_id UUID NOT NULL REFERENCES ai_feedback(id),
    model_name VARCHAR(100) NOT NULL,
    priority FLOAT NOT NULL DEFAULT 1.0,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'training', 'trained', 'failed')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,

    -- Result
    model_version_trained VARCHAR(50),
    error_message TEXT
);

CREATE INDEX idx_feedback_queue_status ON feedback_queue(status, priority DESC);
CREATE INDEX idx_feedback_queue_model ON feedback_queue(model_name, status);

-- Expert profiles for weighting
CREATE TABLE IF NOT EXISTS expert_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL UNIQUE REFERENCES users(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('partner', 'manager', 'senior', 'staff')),

    -- Expertise areas
    industries JSONB, -- ["SaaS", "Manufacturing", ...]
    specializations JSONB, -- ["ASC 606", "ASC 842", ...]

    -- Performance metrics
    total_feedback_given INTEGER DEFAULT 0,
    accuracy_of_feedback FLOAT,
    avg_feedback_time_seconds INTEGER,

    -- Weighting
    custom_weight FLOAT,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_expert_profiles_user ON expert_profiles(user_id);

-- Model performance metrics (time series)
CREATE TABLE IF NOT EXISTS model_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,

    -- Time period
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,

    -- Metrics
    total_predictions INTEGER NOT NULL,
    correct_predictions INTEGER NOT NULL,
    accuracy FLOAT NOT NULL,

    -- By feedback type
    approvals INTEGER DEFAULT 0,
    corrections INTEGER DEFAULT 0,
    rejections INTEGER DEFAULT 0,
    modifications INTEGER DEFAULT 0,

    -- Confidence analysis
    avg_confidence FLOAT,
    avg_confidence_when_correct FLOAT,
    avg_confidence_when_incorrect FLOAT,

    -- User engagement
    unique_users INTEGER,
    avg_time_to_feedback_seconds INTEGER
);

CREATE INDEX idx_model_perf_metrics ON model_performance_metrics(model_name, measured_at DESC);

-- A/B tests
CREATE TABLE IF NOT EXISTS ab_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    model_name VARCHAR(100) NOT NULL,
    version_a VARCHAR(50) NOT NULL, -- Control
    version_b VARCHAR(50) NOT NULL, -- Treatment

    -- Test configuration
    traffic_split FLOAT NOT NULL CHECK (traffic_split >= 0 AND traffic_split <= 1),
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'stopped')),

    -- Results
    version_a_predictions INTEGER DEFAULT 0,
    version_a_correct INTEGER DEFAULT 0,
    version_a_accuracy FLOAT,

    version_b_predictions INTEGER DEFAULT 0,
    version_b_correct INTEGER DEFAULT 0,
    version_b_accuracy FLOAT,

    -- Statistical significance
    p_value FLOAT,
    is_significant BOOLEAN,
    winner VARCHAR(50),

    -- Decision
    decision VARCHAR(20) CHECK (decision IN ('promote', 'rollback', 'continue')),
    decided_at TIMESTAMP,
    decided_by VARCHAR(100)
);

CREATE INDEX idx_ab_tests_model ON ab_tests(model_name, status);

-- ============================================================================
-- 2. INDUSTRY-SPECIFIC MODELS
-- ============================================================================

-- Industry classifications
CREATE TABLE IF NOT EXISTS company_industry_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    organization_id UUID NOT NULL REFERENCES organizations(id),

    -- Industry
    industry VARCHAR(50) NOT NULL CHECK (industry IN ('SaaS', 'Manufacturing', 'Healthcare', 'Financial Services', 'Real Estate', 'General')),
    naics_code VARCHAR(10),
    sic_code VARCHAR(10),

    -- Classification confidence
    classification_method VARCHAR(50), -- 'naics', 'sic', 'ai', 'manual'
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),

    -- Metadata
    classified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    classified_by VARCHAR(100),

    UNIQUE(organization_id)
);

CREATE INDEX idx_industry_classification ON company_industry_classifications(industry);

-- Industry model routing
CREATE TABLE IF NOT EXISTS industry_model_routing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    engagement_id UUID NOT NULL REFERENCES engagements(id),
    industry VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,

    -- Routing metadata
    routed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    routing_reason TEXT,

    UNIQUE(engagement_id)
);

-- ============================================================================
-- 3. INTELLIGENT SAMPLING
-- ============================================================================

-- Transaction risk assessments
CREATE TABLE IF NOT EXISTS transaction_risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    engagement_id UUID NOT NULL REFERENCES engagements(id),
    journal_entry_id UUID REFERENCES journal_entries(id),

    -- Risk scoring
    risk_score FLOAT NOT NULL CHECK (risk_score >= 0 AND risk_score <= 1),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('very_high', 'high', 'medium', 'low', 'very_low')),

    -- Risk factors
    risk_factors JSONB NOT NULL, -- ["manual_entry", "round_dollar", ...]
    anomaly_indicators JSONB, -- ["statistical_anomaly", "benford_violation", ...]

    -- Sampling decision
    selected_for_sample BOOLEAN DEFAULT FALSE,
    selection_reason TEXT,

    -- Metadata
    assessed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assessed_by_model VARCHAR(100)
);

CREATE INDEX idx_txn_risk_engagement ON transaction_risk_assessments(engagement_id, risk_level);
CREATE INDEX idx_txn_risk_selected ON transaction_risk_assessments(selected_for_sample) WHERE selected_for_sample = TRUE;

-- Sampling plans
CREATE TABLE IF NOT EXISTS sampling_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    engagement_id UUID NOT NULL REFERENCES engagements(id),
    account_name VARCHAR(200) NOT NULL,
    account_type VARCHAR(50) NOT NULL,

    -- Population
    population_size INTEGER NOT NULL,
    total_population_amount NUMERIC(20, 2) NOT NULL,

    -- Sample
    sample_size INTEGER NOT NULL,
    total_sample_amount NUMERIC(20, 2) NOT NULL,
    sample_coverage_pct FLOAT NOT NULL,

    -- Risk stratification
    high_risk_count INTEGER NOT NULL,
    medium_risk_count INTEGER NOT NULL,
    low_risk_count INTEGER NOT NULL,

    -- Methodology
    sampling_methodology TEXT NOT NULL,
    risk_rationale TEXT NOT NULL,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_sampling_plans_engagement ON sampling_plans(engagement_id);

-- ============================================================================
-- 4. CHAT INTERFACE
-- ============================================================================

-- Chat conversations
CREATE TABLE IF NOT EXISTS chat_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    engagement_id UUID NOT NULL REFERENCES engagements(id),
    user_id UUID NOT NULL REFERENCES users(id),

    -- Conversation metadata
    title VARCHAR(200),
    message_count INTEGER DEFAULT 0,

    -- Metadata
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    archived BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_chat_convos_engagement ON chat_conversations(engagement_id, last_message_at DESC);
CREATE INDEX idx_chat_convos_user ON chat_conversations(user_id, last_message_at DESC);

-- Chat messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    conversation_id UUID NOT NULL REFERENCES chat_conversations(id) ON DELETE CASCADE,

    -- Message
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,

    -- Citations
    citations JSONB,

    -- AI metadata (for assistant messages)
    model_used VARCHAR(100),
    tokens_used INTEGER,
    latency_ms INTEGER,
    sql_generated TEXT,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_messages_conversation ON chat_messages(conversation_id, created_at);

-- Chat feedback (thumbs up/down)
CREATE TABLE IF NOT EXISTS chat_message_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),

    -- Feedback
    helpful BOOLEAN NOT NULL,
    feedback_text TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(message_id, user_id)
);

-- ============================================================================
-- 5. AI EXPLAINABILITY
-- ============================================================================

-- Decision explanations
CREATE TABLE IF NOT EXISTS ai_decision_explanations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Decision
    decision_type VARCHAR(50) NOT NULL, -- 'audit_opinion', 'materiality', 'risk_assessment', etc.
    prediction_id VARCHAR(100) NOT NULL UNIQUE,
    engagement_id UUID REFERENCES engagements(id),

    -- The decision
    decision VARCHAR(200) NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),

    -- Factors (SHAP values)
    top_positive_factors JSONB NOT NULL, -- [{factor, impact, explanation}, ...]
    top_negative_factors JSONB NOT NULL,

    -- Context
    similar_cases JSONB, -- [{company, similarity, decision}, ...]
    alternative_scenarios JSONB, -- [{scenario, decision, probability}, ...]

    -- Compliance
    citations JSONB, -- [{standard, paragraph, text}, ...]

    -- Summary
    summary TEXT NOT NULL,
    cpa_guidance TEXT NOT NULL,

    -- Visualization
    feature_importance JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_explanations_engagement ON ai_decision_explanations(engagement_id);
CREATE INDEX idx_explanations_type ON ai_decision_explanations(decision_type);

-- Explanation feedback
CREATE TABLE IF NOT EXISTS explanation_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    explanation_id UUID NOT NULL REFERENCES ai_decision_explanations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),

    -- Feedback
    helpful BOOLEAN NOT NULL,
    clear BOOLEAN,
    complete BOOLEAN,
    comments TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(explanation_id, user_id)
);

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

-- Daily model performance summary
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_model_performance AS
SELECT
    model_name,
    model_version,
    DATE(created_at) as date,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN feedback_type = 'approval' THEN 1 ELSE 0 END) as approvals,
    SUM(CASE WHEN feedback_type IN ('correction', 'modification') THEN 1 ELSE 0 END) as corrections,
    AVG(ai_confidence) as avg_confidence,
    AVG(expert_weight) as avg_expert_weight
FROM ai_feedback
GROUP BY model_name, model_version, DATE(created_at);

CREATE UNIQUE INDEX idx_mv_daily_model_perf ON mv_daily_model_performance(model_name, model_version, date);

-- Industry model performance
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_industry_model_performance AS
SELECT
    cic.industry,
    af.model_name,
    af.model_version,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN af.feedback_type = 'approval' THEN 1 ELSE 0 END) as approvals,
    CAST(SUM(CASE WHEN af.feedback_type = 'approval' THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) as accuracy
FROM ai_feedback af
JOIN engagements e ON af.engagement_id = e.id
JOIN company_industry_classifications cic ON e.organization_id = cic.organization_id
GROUP BY cic.industry, af.model_name, af.model_version;

CREATE UNIQUE INDEX idx_mv_industry_model_perf ON mv_industry_model_performance(industry, model_name, model_version);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to refresh materialized views (call daily)
CREATE OR REPLACE FUNCTION refresh_ai_metrics() RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_model_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_industry_model_performance;
END;
$$ LANGUAGE plpgsql;

-- Function to update conversation message count
CREATE OR REPLACE FUNCTION update_conversation_message_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_conversations
    SET message_count = message_count + 1,
        last_message_at = NEW.created_at
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_conversation_count
AFTER INSERT ON chat_messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_message_count();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE ai_feedback IS 'CPA feedback on AI predictions for continuous learning';
COMMENT ON TABLE model_versions IS 'Registry of all model versions with performance metrics';
COMMENT ON TABLE feedback_queue IS 'Queue of feedback items for nightly retraining';
COMMENT ON TABLE ab_tests IS 'A/B tests comparing model versions';
COMMENT ON TABLE transaction_risk_assessments IS 'Risk scores for intelligent sampling';
COMMENT ON TABLE sampling_plans IS 'Audit sampling plans with AI-based selection';
COMMENT ON TABLE chat_conversations IS 'AI chat conversations per engagement';
COMMENT ON TABLE chat_messages IS 'Individual messages in chat conversations';
COMMENT ON TABLE ai_decision_explanations IS 'Explainability data for AI decisions (SHAP values)';

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant appropriate permissions (adjust as needed for your security model)
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO atlas;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO atlas;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO atlas;
