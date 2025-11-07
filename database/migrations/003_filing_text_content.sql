-- =====================================================
-- FILING TEXT CONTENT & DISCLOSURES
-- Purpose: Store narrative content from SEC filings for AI training
-- =====================================================

SET search_path TO atlas;

-- Filing sections (extracted narrative content)
CREATE TABLE IF NOT EXISTS filing_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filing_id UUID NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    section_type VARCHAR(100) NOT NULL,
    section_title VARCHAR(500),
    content TEXT NOT NULL,
    content_length INTEGER NOT NULL,
    word_count INTEGER,
    s3_uri TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_filing_sections_filing ON filing_sections(filing_id);
CREATE INDEX idx_filing_sections_type ON filing_sections(section_type);
CREATE INDEX idx_filing_sections_search ON filing_sections USING gin(to_tsvector('english', content));

COMMENT ON TABLE filing_sections IS 'Extracted sections from SEC filings (MD&A, Risk Factors, etc.)';

-- Financial statement notes
CREATE TABLE IF NOT EXISTS filing_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filing_id UUID NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    note_number VARCHAR(10) NOT NULL,
    note_title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_length INTEGER NOT NULL,
    word_count INTEGER,
    s3_uri TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_filing_notes_filing ON filing_notes(filing_id);
CREATE INDEX idx_filing_notes_number ON filing_notes(note_number);
CREATE INDEX idx_filing_notes_search ON filing_notes USING gin(to_tsvector('english', content));

COMMENT ON TABLE filing_notes IS 'Individual notes to financial statements';

-- Risk factors
CREATE TABLE IF NOT EXISTS filing_risk_factors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filing_id UUID NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    risk_text TEXT NOT NULL,
    risk_category VARCHAR(100),
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    embedding_vector VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_filing_risk_factors_filing ON filing_risk_factors(filing_id);
CREATE INDEX idx_filing_risk_factors_category ON filing_risk_factors(risk_category);
CREATE INDEX idx_filing_risk_factors_embedding ON filing_risk_factors USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);

COMMENT ON TABLE filing_risk_factors IS 'Extracted risk factors from Item 1A';

-- Accounting policies
CREATE TABLE IF NOT EXISTS filing_accounting_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filing_id UUID NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    policy_type VARCHAR(100),
    policy_title VARCHAR(500),
    content TEXT NOT NULL,
    content_length INTEGER NOT NULL,
    s3_uri TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_filing_accounting_policies_filing ON filing_accounting_policies(filing_id);
CREATE INDEX idx_filing_accounting_policies_type ON filing_accounting_policies(policy_type);

COMMENT ON TABLE filing_accounting_policies IS 'Significant accounting policies from Note 1';

-- Full text content (for document embeddings and search)
CREATE TABLE IF NOT EXISTS filing_full_text (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filing_id UUID NOT NULL REFERENCES filings(id) ON DELETE CASCADE UNIQUE,
    full_text TEXT NOT NULL,
    text_length INTEGER NOT NULL,
    word_count INTEGER NOT NULL,
    page_count INTEGER,
    s3_uri TEXT,
    processed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_filing_full_text_filing ON filing_full_text(filing_id);
CREATE INDEX idx_filing_full_text_search ON filing_full_text USING gin(to_tsvector('english', full_text));

COMMENT ON TABLE filing_full_text IS 'Complete cleaned text from filings for full-text search and embeddings';

-- Add columns to filings table for text processing status
ALTER TABLE filings ADD COLUMN IF NOT EXISTS text_extracted BOOLEAN DEFAULT FALSE;
ALTER TABLE filings ADD COLUMN IF NOT EXISTS text_extraction_date TIMESTAMPTZ;
ALTER TABLE filings ADD COLUMN IF NOT EXISTS sections_count INTEGER DEFAULT 0;
ALTER TABLE filings ADD COLUMN IF NOT EXISTS notes_count INTEGER DEFAULT 0;
ALTER TABLE filings ADD COLUMN IF NOT EXISTS risks_count INTEGER DEFAULT 0;

CREATE INDEX idx_filings_text_extracted ON filings(text_extracted);

-- Update filing enum to include more form types
DO $$
BEGIN
    -- Add more filing types if they don't exist
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'filing_form') THEN
        CREATE TYPE filing_form AS ENUM (
            '10-K', '10-Q', '20-F', '40-F', '6-K', '8-K',
            'DEF-14A', 'S-1', 'S-3', 'S-4', 'S-8', '3', '4', '5'
        );
    END IF;
END $$;

-- Section type enum
CREATE TYPE IF NOT EXISTS section_type AS ENUM (
    'business',
    'risk_factors',
    'properties',
    'legal_proceedings',
    'mda',
    'financial_statements',
    'changes_disagreements',
    'controls_procedures',
    'directors_officers',
    'executive_compensation',
    'security_ownership',
    'related_party',
    'exhibits',
    'market_risk',
    'other'
);

-- AI training dataset view
CREATE OR REPLACE VIEW ai_training_disclosures AS
SELECT
    f.id as filing_id,
    f.cik,
    f.ticker,
    f.company_name,
    f.form,
    f.filing_date,
    fs.section_type,
    fs.section_title,
    fs.content,
    fs.content_length,
    fs.word_count
FROM filings f
JOIN filing_sections fs ON fs.filing_id = f.id
WHERE fs.content_length > 100
ORDER BY f.filing_date DESC;

COMMENT ON VIEW ai_training_disclosures IS 'Clean dataset of disclosure text for AI/LLM training';

-- Notes training dataset view
CREATE OR REPLACE VIEW ai_training_notes AS
SELECT
    f.id as filing_id,
    f.cik,
    f.ticker,
    f.company_name,
    f.form,
    f.filing_date,
    fn.note_number,
    fn.note_title,
    fn.content,
    fn.content_length
FROM filings f
JOIN filing_notes fn ON fn.filing_id = f.id
WHERE fn.content_length > 100
ORDER BY f.filing_date DESC, fn.note_number;

COMMENT ON VIEW ai_training_notes IS 'Financial statement notes for AI training';

-- Risk factors training dataset
CREATE OR REPLACE VIEW ai_training_risks AS
SELECT
    f.id as filing_id,
    f.cik,
    f.ticker,
    f.company_name,
    f.form,
    f.filing_date,
    fr.risk_text,
    fr.risk_category,
    fr.severity
FROM filings f
JOIN filing_risk_factors fr ON fr.filing_id = f.id
ORDER BY f.filing_date DESC;

COMMENT ON VIEW ai_training_risks IS 'Risk factors for AI training';
