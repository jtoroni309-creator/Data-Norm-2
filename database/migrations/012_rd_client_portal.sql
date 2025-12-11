-- ========================================
-- R&D CLIENT PORTAL TABLES
-- Tables for R&D tax credit client portal user management
-- ========================================

SET search_path TO atlas;

-- ========================================
-- 1. R&D CLIENT ROLE ENUM
-- ========================================

DO $$ BEGIN
    CREATE TYPE rd_client_role AS ENUM (
        'primary',      -- Main contact invited by CPA
        'team_member'   -- Team member invited by primary user
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ========================================
-- 2. R&D CLIENT USERS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS rd_client_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic info
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(200) NOT NULL,
    company_name VARCHAR(200),
    hashed_password VARCHAR(255),  -- Nullable until they set password
    phone VARCHAR(50),

    -- Role
    role rd_client_role NOT NULL DEFAULT 'primary',

    -- Links
    study_id UUID NOT NULL,  -- Link to rd_studies table
    firm_id UUID REFERENCES cpa_firms(id),  -- CPA firm that manages this client

    -- Who invited them
    invited_by_user_id UUID,  -- CPA user who sent invitation
    invited_by_rd_client_id UUID REFERENCES rd_client_users(id),  -- Primary user who invited team member

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,

    -- Security
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rd_client_users_email ON rd_client_users(email);
CREATE INDEX IF NOT EXISTS idx_rd_client_users_study_id ON rd_client_users(study_id);
CREATE INDEX IF NOT EXISTS idx_rd_client_users_firm_id ON rd_client_users(firm_id);
CREATE INDEX IF NOT EXISTS idx_rd_client_users_role ON rd_client_users(role);
CREATE INDEX IF NOT EXISTS idx_rd_client_users_active ON rd_client_users(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE rd_client_users IS 'R&D Client Portal users - clients who provide documentation for R&D tax credit studies';
COMMENT ON COLUMN rd_client_users.role IS 'primary = invited by CPA, team_member = invited by primary user';
COMMENT ON COLUMN rd_client_users.study_id IS 'Links to atlas.rd_studies table';

-- ========================================
-- 3. R&D CLIENT INVITATIONS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS rd_client_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Invitation details
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    company_name VARCHAR(200),
    role rd_client_role NOT NULL DEFAULT 'primary',

    -- Links
    study_id UUID NOT NULL,  -- Link to rd_studies
    firm_id UUID REFERENCES cpa_firms(id),

    -- Who sent the invitation
    invited_by_user_id UUID,  -- CPA user (for primary invitations)
    invited_by_rd_client_id UUID REFERENCES rd_client_users(id),  -- Primary user (for team invitations)

    -- Token for registration
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    accepted_at TIMESTAMPTZ,
    is_expired BOOLEAN DEFAULT FALSE,

    -- Optional message from inviter
    invitation_message TEXT,

    -- Tracking
    email_sent_at TIMESTAMPTZ,
    email_opened_at TIMESTAMPTZ,
    resent_count INTEGER DEFAULT 0,
    last_resent_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rd_client_invitations_email ON rd_client_invitations(email);
CREATE INDEX IF NOT EXISTS idx_rd_client_invitations_token ON rd_client_invitations(token);
CREATE INDEX IF NOT EXISTS idx_rd_client_invitations_study_id ON rd_client_invitations(study_id);
CREATE INDEX IF NOT EXISTS idx_rd_client_invitations_firm_id ON rd_client_invitations(firm_id);
CREATE INDEX IF NOT EXISTS idx_rd_client_invitations_pending ON rd_client_invitations(accepted_at) WHERE accepted_at IS NULL AND is_expired = FALSE;

COMMENT ON TABLE rd_client_invitations IS 'Invitations for R&D Client Portal access';
COMMENT ON COLUMN rd_client_invitations.token IS 'Secure token for invitation link';
COMMENT ON COLUMN rd_client_invitations.expires_at IS 'Invitation expires 30 days after creation';

-- ========================================
-- 4. R&D CLIENT DOCUMENTS TABLE
-- ========================================
-- Documents uploaded by clients for PA and other state requirements

CREATE TABLE IF NOT EXISTS rd_client_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Links
    study_id UUID NOT NULL,
    uploaded_by_id UUID REFERENCES rd_client_users(id),

    -- Document info
    filename VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(100),
    file_size BIGINT,

    -- Document classification
    document_type VARCHAR(50) NOT NULL,  -- w2, 1099, invoice, contract, other
    document_category VARCHAR(100),  -- wages, contractor, supplies, etc.
    tax_year INTEGER,

    -- State-specific
    state_code VARCHAR(2),  -- PA, CA, etc.

    -- OCR/AI Processing
    processing_status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed
    ocr_text TEXT,
    extracted_data JSONB,
    ai_analysis JSONB,
    ocr_confidence DECIMAL(5,2),

    -- Storage
    storage_path TEXT,
    storage_provider VARCHAR(50) DEFAULT 'azure_blob',

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rd_client_documents_study_id ON rd_client_documents(study_id);
CREATE INDEX IF NOT EXISTS idx_rd_client_documents_uploaded_by ON rd_client_documents(uploaded_by_id);
CREATE INDEX IF NOT EXISTS idx_rd_client_documents_type ON rd_client_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_rd_client_documents_state ON rd_client_documents(state_code);
CREATE INDEX IF NOT EXISTS idx_rd_client_documents_processing ON rd_client_documents(processing_status);

COMMENT ON TABLE rd_client_documents IS 'Documents uploaded by R&D clients for tax credit documentation';

-- ========================================
-- 5. PA DOCUMENT PACKAGES TABLE
-- ========================================
-- Pennsylvania-specific documentation packages

CREATE TABLE IF NOT EXISTS rd_pa_document_packages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Links
    study_id UUID NOT NULL,
    created_by_id UUID,  -- CPA user who created the package

    -- Package info
    package_status VARCHAR(50) DEFAULT 'draft',  -- draft, pending_review, approved, submitted
    tax_year INTEGER NOT NULL,

    -- Document counts
    w2_count INTEGER DEFAULT 0,
    form_1099_count INTEGER DEFAULT 0,
    invoice_count INTEGER DEFAULT 0,

    -- Totals from documents
    total_pa_wages DECIMAL(15,2) DEFAULT 0,
    total_pa_contractor DECIMAL(15,2) DEFAULT 0,
    total_pa_supplies DECIMAL(15,2) DEFAULT 0,

    -- Reconciliation
    calculated_pa_wages DECIMAL(15,2),
    calculated_pa_contractor DECIMAL(15,2),
    calculated_pa_supplies DECIMAL(15,2),

    reconciliation_status VARCHAR(50),  -- matched, variance_detected, not_reconciled
    reconciliation_notes TEXT,
    variance_details JSONB,

    -- Approval workflow
    submitted_at TIMESTAMPTZ,
    reviewed_at TIMESTAMPTZ,
    reviewed_by UUID,
    approval_notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rd_pa_packages_study_id ON rd_pa_document_packages(study_id);
CREATE INDEX IF NOT EXISTS idx_rd_pa_packages_status ON rd_pa_document_packages(package_status);
CREATE INDEX IF NOT EXISTS idx_rd_pa_packages_year ON rd_pa_document_packages(tax_year);

COMMENT ON TABLE rd_pa_document_packages IS 'Pennsylvania R&D tax credit documentation packages';

-- ========================================
-- 6. TRIGGER FOR updated_at
-- ========================================

CREATE OR REPLACE FUNCTION update_rd_client_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_rd_client_users_updated ON rd_client_users;
CREATE TRIGGER trg_rd_client_users_updated
    BEFORE UPDATE ON rd_client_users
    FOR EACH ROW
    EXECUTE FUNCTION update_rd_client_updated_at();

DROP TRIGGER IF EXISTS trg_rd_client_documents_updated ON rd_client_documents;
CREATE TRIGGER trg_rd_client_documents_updated
    BEFORE UPDATE ON rd_client_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_rd_client_updated_at();

DROP TRIGGER IF EXISTS trg_rd_pa_packages_updated ON rd_pa_document_packages;
CREATE TRIGGER trg_rd_pa_packages_updated
    BEFORE UPDATE ON rd_pa_document_packages
    FOR EACH ROW
    EXECUTE FUNCTION update_rd_client_updated_at();

-- ========================================
-- 7. ROW LEVEL SECURITY (RLS) POLICIES
-- ========================================

-- Enable RLS on tables
ALTER TABLE rd_client_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE rd_client_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE rd_client_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE rd_pa_document_packages ENABLE ROW LEVEL SECURITY;

-- R&D Client Users - Users can see their own record and team members in same study
CREATE POLICY rd_client_users_select ON rd_client_users
    FOR SELECT
    USING (
        id = current_setting('app.user_id', TRUE)::UUID
        OR study_id IN (
            SELECT study_id FROM rd_client_users
            WHERE id = current_setting('app.user_id', TRUE)::UUID
        )
        OR firm_id = current_setting('app.firm_id', TRUE)::UUID  -- CPA firm access
    );

CREATE POLICY rd_client_users_update ON rd_client_users
    FOR UPDATE
    USING (
        id = current_setting('app.user_id', TRUE)::UUID
        OR firm_id = current_setting('app.firm_id', TRUE)::UUID
    );

-- R&D Client Invitations - CPA firms can manage their invitations
CREATE POLICY rd_client_invitations_all ON rd_client_invitations
    FOR ALL
    USING (firm_id = current_setting('app.firm_id', TRUE)::UUID);

-- R&D Client Documents - Study-level access
CREATE POLICY rd_client_documents_all ON rd_client_documents
    FOR ALL
    USING (
        study_id IN (
            SELECT study_id FROM rd_client_users
            WHERE id = current_setting('app.user_id', TRUE)::UUID
        )
        OR EXISTS (
            SELECT 1 FROM rd_client_users rcu
            WHERE rcu.study_id = rd_client_documents.study_id
            AND rcu.firm_id = current_setting('app.firm_id', TRUE)::UUID
        )
    );

-- PA Document Packages - CPA firm access
CREATE POLICY rd_pa_packages_all ON rd_pa_document_packages
    FOR ALL
    USING (
        created_by_id = current_setting('app.user_id', TRUE)::UUID
        OR EXISTS (
            SELECT 1 FROM rd_client_users rcu
            WHERE rcu.study_id = rd_pa_document_packages.study_id
            AND rcu.firm_id = current_setting('app.firm_id', TRUE)::UUID
        )
    );

-- ========================================
-- 8. GRANT PERMISSIONS
-- ========================================

-- Application role permissions (adjust role name as needed)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'aura_app') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON rd_client_users TO aura_app;
        GRANT SELECT, INSERT, UPDATE, DELETE ON rd_client_invitations TO aura_app;
        GRANT SELECT, INSERT, UPDATE, DELETE ON rd_client_documents TO aura_app;
        GRANT SELECT, INSERT, UPDATE, DELETE ON rd_pa_document_packages TO aura_app;
    END IF;
END $$;

-- ========================================
-- MIGRATION COMPLETE
-- ========================================
SELECT 'R&D Client Portal migration completed successfully' AS status;
