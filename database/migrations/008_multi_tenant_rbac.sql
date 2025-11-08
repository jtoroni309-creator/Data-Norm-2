-- ========================================
-- MULTI-TENANT RBAC SYSTEM
-- CPA Firms → Clients → Users → Roles → Permissions
-- ========================================

SET search_path TO atlas;

-- ========================================
-- 1. CPA FIRMS (Top-Level Tenants)
-- ========================================

CREATE TYPE firm_subscription_tier AS ENUM (
    'trial',           -- 30-day trial
    'starter',         -- Up to 10 clients
    'professional',    -- Up to 50 clients
    'enterprise'       -- Unlimited clients
);

CREATE TYPE firm_status AS ENUM (
    'active',
    'suspended',
    'trial_expired',
    'canceled'
);

CREATE TABLE IF NOT EXISTS cpa_firms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Firm information
    firm_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    ein VARCHAR(20),  -- Employer Identification Number

    -- Contact information
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255) NOT NULL,
    primary_contact_phone VARCHAR(50),

    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',

    -- Subscription
    subscription_tier firm_subscription_tier DEFAULT 'trial',
    subscription_status firm_status DEFAULT 'active',
    trial_start_date DATE,
    trial_end_date DATE,
    subscription_start_date DATE,
    max_clients INTEGER DEFAULT 10,
    max_users INTEGER DEFAULT 5,

    -- Branding
    logo_url TEXT,
    primary_color VARCHAR(7),  -- Hex color
    secondary_color VARCHAR(7),

    -- Settings
    default_engagement_partner VARCHAR(255),
    require_two_factor_auth BOOLEAN DEFAULT FALSE,
    session_timeout_minutes INTEGER DEFAULT 30,
    password_expiry_days INTEGER DEFAULT 90,

    -- Features enabled for firm
    enable_edgar_scraper BOOLEAN DEFAULT TRUE,
    enable_ai_assistant BOOLEAN DEFAULT TRUE,
    enable_analytics BOOLEAN DEFAULT TRUE,
    enable_client_portal BOOLEAN DEFAULT TRUE,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,

    CONSTRAINT unique_firm_name UNIQUE(firm_name)
);

CREATE INDEX idx_cpa_firms_status ON cpa_firms(subscription_status);
CREATE INDEX idx_cpa_firms_active ON cpa_firms(is_active);

COMMENT ON TABLE cpa_firms IS 'CPA firms using the platform (top-level tenants)';

-- ========================================
-- 2. CLIENTS (Belong to CPA Firms)
-- ========================================

CREATE TYPE client_status AS ENUM (
    'active',
    'inactive',
    'onboarding',
    'terminated'
);

CREATE TYPE client_entity_type AS ENUM (
    'c_corporation',
    's_corporation',
    'llc',
    'partnership',
    'sole_proprietorship',
    'nonprofit',
    'government',
    'other'
);

CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cpa_firm_id UUID NOT NULL REFERENCES cpa_firms(id) ON DELETE CASCADE,

    -- Client information
    client_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    ein VARCHAR(20),
    entity_type client_entity_type,

    -- Contact information
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255),
    primary_contact_phone VARCHAR(50),

    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',

    -- Fiscal information
    fiscal_year_end VARCHAR(5),  -- MM-DD format (e.g., "12-31")
    industry_code VARCHAR(10),   -- NAICS code

    -- Status
    client_status client_status DEFAULT 'onboarding',
    onboarding_completed_at TIMESTAMPTZ,

    -- Client portal settings
    portal_enabled BOOLEAN DEFAULT TRUE,
    portal_custom_domain VARCHAR(255),
    portal_logo_url TEXT,

    -- Feature flags for this client's portal
    allow_document_upload BOOLEAN DEFAULT TRUE,
    allow_confirmation_response BOOLEAN DEFAULT TRUE,
    allow_data_export BOOLEAN DEFAULT FALSE,
    allow_report_download BOOLEAN DEFAULT TRUE,
    allow_messaging BOOLEAN DEFAULT TRUE,
    allow_financial_view BOOLEAN DEFAULT TRUE,

    -- Engagement defaults
    default_engagement_type VARCHAR(50) DEFAULT 'audit',

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,

    CONSTRAINT unique_client_per_firm UNIQUE(cpa_firm_id, client_name)
);

CREATE INDEX idx_clients_firm ON clients(cpa_firm_id);
CREATE INDEX idx_clients_status ON clients(client_status);
CREATE INDEX idx_clients_active ON clients(is_active);

COMMENT ON TABLE clients IS 'Clients of CPA firms';

-- ========================================
-- 3. ROLES & PERMISSIONS
-- ========================================

CREATE TYPE role_type AS ENUM (
    'platform_admin',     -- Super admin
    'firm_admin',         -- Manages CPA firm
    'firm_partner',       -- CPA firm partner
    'firm_manager',       -- CPA firm manager
    'firm_senior',        -- Senior accountant
    'firm_staff',         -- Staff accountant
    'client_admin',       -- Client administrator
    'client_finance',     -- Client CFO/Controller
    'client_viewer'       -- Client read-only
);

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    role_type role_type NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    role_description TEXT,

    -- Scope
    is_firm_role BOOLEAN DEFAULT TRUE,    -- CPA firm role
    is_client_role BOOLEAN DEFAULT FALSE, -- Client role

    -- Hierarchy (for approval chains)
    approval_level INTEGER,  -- Higher = more authority (Partner=100, Manager=75, Senior=50, Staff=25)

    is_system_role BOOLEAN DEFAULT TRUE,  -- System-defined vs custom
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_roles_type ON roles(role_type);
CREATE INDEX idx_roles_firm ON roles(is_firm_role);
CREATE INDEX idx_roles_client ON roles(is_client_role);

COMMENT ON TABLE roles IS 'System and custom roles';

-- Seed system roles
INSERT INTO roles (role_type, role_name, role_description, is_firm_role, is_client_role, approval_level) VALUES
-- Platform admin
('platform_admin', 'Platform Administrator', 'Super admin with full system access', FALSE, FALSE, 1000),

-- CPA firm roles
('firm_admin', 'Firm Administrator', 'Manages firm settings, users, and clients', TRUE, FALSE, 90),
('firm_partner', 'Partner', 'Engagement partner with final approval authority', TRUE, FALSE, 100),
('firm_manager', 'Manager', 'Manages engagements and supervises staff', TRUE, FALSE, 75),
('firm_senior', 'Senior Accountant', 'Performs reviews and complex procedures', TRUE, FALSE, 50),
('firm_staff', 'Staff Accountant', 'Performs fieldwork and testing', TRUE, FALSE, 25),

-- Client roles
('client_admin', 'Client Administrator', 'Manages client users and portal settings', FALSE, TRUE, 100),
('client_finance', 'Finance Manager', 'Uploads data, responds to requests, approvals', FALSE, TRUE, 75),
('client_viewer', 'Viewer', 'Read-only access to engagement information', FALSE, TRUE, 0);

-- Permission resources
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    permission_name VARCHAR(100) NOT NULL UNIQUE,
    permission_description TEXT,

    -- Resource and action
    resource_type VARCHAR(50) NOT NULL,  -- 'engagement', 'workpaper', 'client', 'user', etc.
    action VARCHAR(50) NOT NULL,         -- 'create', 'read', 'update', 'delete', 'approve', etc.

    -- Scope
    is_firm_permission BOOLEAN DEFAULT TRUE,
    is_client_permission BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_permissions_resource ON permissions(resource_type);
CREATE INDEX idx_permissions_action ON permissions(action);

COMMENT ON TABLE permissions IS 'Granular permissions for resources and actions';

-- Seed core permissions
INSERT INTO permissions (permission_name, permission_description, resource_type, action, is_firm_permission, is_client_permission) VALUES
-- Engagement permissions (firm)
('engagement.create', 'Create new engagements', 'engagement', 'create', TRUE, FALSE),
('engagement.read', 'View engagements', 'engagement', 'read', TRUE, TRUE),
('engagement.update', 'Update engagement details', 'engagement', 'update', TRUE, FALSE),
('engagement.delete', 'Delete engagements', 'engagement', 'delete', TRUE, FALSE),
('engagement.approve', 'Approve engagements for issuance', 'engagement', 'approve', TRUE, FALSE),

-- Workpaper permissions (firm)
('workpaper.create', 'Create workpapers', 'workpaper', 'create', TRUE, FALSE),
('workpaper.read', 'View workpapers', 'workpaper', 'read', TRUE, FALSE),
('workpaper.update', 'Edit workpapers', 'workpaper', 'update', TRUE, FALSE),
('workpaper.review', 'Review and approve workpapers', 'workpaper', 'review', TRUE, FALSE),

-- Client management (firm)
('client.create', 'Add new clients', 'client', 'create', TRUE, FALSE),
('client.read', 'View client information', 'client', 'read', TRUE, TRUE),
('client.update', 'Update client details', 'client', 'update', TRUE, FALSE),
('client.delete', 'Delete clients', 'client', 'delete', TRUE, FALSE),
('client.configure_portal', 'Configure client portal settings', 'client', 'configure_portal', TRUE, FALSE),

-- User management (firm)
('user.create', 'Add new users', 'user', 'create', TRUE, TRUE),
('user.read', 'View users', 'user', 'read', TRUE, TRUE),
('user.update', 'Update user details', 'user', 'update', TRUE, TRUE),
('user.delete', 'Delete users', 'user', 'delete', TRUE, TRUE),
('user.manage_permissions', 'Manage user permissions', 'user', 'manage_permissions', TRUE, FALSE),

-- Document permissions (both)
('document.upload', 'Upload documents', 'document', 'upload', TRUE, TRUE),
('document.read', 'View documents', 'document', 'read', TRUE, TRUE),
('document.delete', 'Delete documents', 'document', 'delete', TRUE, TRUE),

-- Report permissions (firm)
('report.create', 'Generate reports', 'report', 'create', TRUE, FALSE),
('report.read', 'View reports', 'report', 'read', TRUE, TRUE),
('report.approve', 'Approve reports for issuance', 'report', 'approve', TRUE, FALSE),
('report.issue', 'Issue final reports', 'report', 'issue', TRUE, FALSE),

-- Confirmation permissions (firm and client)
('confirmation.create', 'Create confirmations', 'confirmation', 'create', TRUE, FALSE),
('confirmation.respond', 'Respond to confirmations', 'confirmation', 'respond', FALSE, TRUE),

-- Data upload (client)
('data.upload_trial_balance', 'Upload trial balance', 'data', 'upload_trial_balance', FALSE, TRUE),
('data.upload_supporting', 'Upload supporting documents', 'data', 'upload_supporting', FALSE, TRUE),
('data.export', 'Export data', 'data', 'export', TRUE, TRUE),

-- Firm settings (firm admin only)
('firm.update_settings', 'Update firm settings', 'firm', 'update_settings', TRUE, FALSE),
('firm.manage_subscription', 'Manage subscription', 'firm', 'manage_subscription', TRUE, FALSE),
('firm.view_billing', 'View billing information', 'firm', 'view_billing', TRUE, FALSE);

-- Role-Permission mapping
CREATE TABLE IF NOT EXISTS role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_role_permission UNIQUE(role_id, permission_id)
);

CREATE INDEX idx_role_permissions_role ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission ON role_permissions(permission_id);

COMMENT ON TABLE role_permissions IS 'Maps permissions to roles';

-- Seed role-permission mappings for firm roles
DO $$
DECLARE
    partner_role_id UUID;
    manager_role_id UUID;
    senior_role_id UUID;
    staff_role_id UUID;
    firm_admin_role_id UUID;
BEGIN
    -- Get role IDs
    SELECT id INTO partner_role_id FROM roles WHERE role_type = 'firm_partner';
    SELECT id INTO manager_role_id FROM roles WHERE role_type = 'firm_manager';
    SELECT id INTO senior_role_id FROM roles WHERE role_type = 'firm_senior';
    SELECT id INTO staff_role_id FROM roles WHERE role_type = 'firm_staff';
    SELECT id INTO firm_admin_role_id FROM roles WHERE role_type = 'firm_admin';

    -- Partner: All permissions
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT partner_role_id, id FROM permissions WHERE is_firm_permission = TRUE;

    -- Manager: Most permissions except firm settings
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT manager_role_id, id FROM permissions
    WHERE is_firm_permission = TRUE
    AND permission_name NOT LIKE 'firm.%';

    -- Senior: Engagement and workpaper permissions
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT senior_role_id, id FROM permissions
    WHERE permission_name IN (
        'engagement.read', 'engagement.update',
        'workpaper.create', 'workpaper.read', 'workpaper.update', 'workpaper.review',
        'client.read',
        'document.upload', 'document.read',
        'report.read'
    );

    -- Staff: Limited permissions
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT staff_role_id, id FROM permissions
    WHERE permission_name IN (
        'engagement.read',
        'workpaper.create', 'workpaper.read', 'workpaper.update',
        'client.read',
        'document.upload', 'document.read'
    );

    -- Firm Admin: User and firm management
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT firm_admin_role_id, id FROM permissions
    WHERE is_firm_permission = TRUE;
END $$;

-- Seed role-permission mappings for client roles
DO $$
DECLARE
    client_admin_role_id UUID;
    client_finance_role_id UUID;
    client_viewer_role_id UUID;
BEGIN
    SELECT id INTO client_admin_role_id FROM roles WHERE role_type = 'client_admin';
    SELECT id INTO client_finance_role_id FROM roles WHERE role_type = 'client_finance';
    SELECT id INTO client_viewer_role_id FROM roles WHERE role_type = 'client_viewer';

    -- Client Admin: All client permissions
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT client_admin_role_id, id FROM permissions WHERE is_client_permission = TRUE;

    -- Client Finance: Upload and respond
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT client_finance_role_id, id FROM permissions
    WHERE permission_name IN (
        'engagement.read',
        'client.read',
        'document.upload', 'document.read',
        'confirmation.respond',
        'data.upload_trial_balance', 'data.upload_supporting'
    );

    -- Client Viewer: Read-only
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT client_viewer_role_id, id FROM permissions
    WHERE permission_name IN (
        'engagement.read',
        'client.read',
        'document.read',
        'report.read'
    );
END $$;

-- ========================================
-- 4. USERS (Enhanced)
-- ========================================

-- Update existing users table if it exists, or create new
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Association
    cpa_firm_id UUID REFERENCES cpa_firms(id) ON DELETE CASCADE,
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,

    -- User information
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),

    -- Authentication
    password_hash VARCHAR(255),
    require_password_change BOOLEAN DEFAULT FALSE,
    last_password_change TIMESTAMPTZ,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,

    -- Two-factor authentication
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),

    -- Session
    last_login_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,

    CONSTRAINT user_must_belong_to_firm_or_client CHECK (
        (cpa_firm_id IS NOT NULL AND client_id IS NULL) OR
        (cpa_firm_id IS NULL AND client_id IS NOT NULL) OR
        (cpa_firm_id IS NOT NULL AND client_id IS NOT NULL)
    )
);

CREATE INDEX idx_users_firm ON users(cpa_firm_id);
CREATE INDEX idx_users_client ON users(client_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

COMMENT ON TABLE users IS 'Platform users (CPA firm staff and client users)';

-- User-Role assignments
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,

    -- Optional scope (assign role for specific client)
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,

    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_user_role_client UNIQUE(user_id, role_id, client_id)
);

CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_user_roles_role ON user_roles(role_id);
CREATE INDEX idx_user_roles_client ON user_roles(client_id);

COMMENT ON TABLE user_roles IS 'Maps users to roles with optional client scope';

-- ========================================
-- 5. APPROVAL WORKFLOWS
-- ========================================

CREATE TYPE approval_status AS ENUM (
    'pending',
    'approved',
    'rejected',
    'delegated'
);

CREATE TABLE IF NOT EXISTS approval_chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cpa_firm_id UUID NOT NULL REFERENCES cpa_firms(id) ON DELETE CASCADE,

    chain_name VARCHAR(255) NOT NULL,
    chain_description TEXT,

    -- What requires this approval chain
    resource_type VARCHAR(50) NOT NULL,  -- 'workpaper', 'report', 'engagement', etc.

    -- Ordered list of approval levels
    approval_levels JSONB NOT NULL,  -- [{"level": 1, "role_id": "uuid", "required": true}, ...]

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_approval_chains_firm ON approval_chains(cpa_firm_id);
CREATE INDEX idx_approval_chains_resource ON approval_chains(resource_type);

COMMENT ON TABLE approval_chains IS 'Configurable approval workflows';

CREATE TABLE IF NOT EXISTS approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    approval_chain_id UUID NOT NULL REFERENCES approval_chains(id),

    -- What needs approval
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID NOT NULL,

    -- Request details
    requested_by UUID NOT NULL REFERENCES users(id),
    requested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    request_description TEXT,

    -- Current status
    current_approval_level INTEGER DEFAULT 1,
    overall_status approval_status DEFAULT 'pending',

    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_approval_requests_chain ON approval_requests(approval_chain_id);
CREATE INDEX idx_approval_requests_resource ON approval_requests(resource_type, resource_id);
CREATE INDEX idx_approval_requests_status ON approval_requests(overall_status);

COMMENT ON TABLE approval_requests IS 'Approval requests for resources';

CREATE TABLE IF NOT EXISTS approval_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    approval_request_id UUID NOT NULL REFERENCES approval_requests(id) ON DELETE CASCADE,

    approval_level INTEGER NOT NULL,
    approver_id UUID NOT NULL REFERENCES users(id),

    action approval_status NOT NULL,
    action_notes TEXT,
    action_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Delegation
    delegated_to UUID REFERENCES users(id),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_approval_actions_request ON approval_actions(approval_request_id);
CREATE INDEX idx_approval_actions_approver ON approval_actions(approver_id);

COMMENT ON TABLE approval_actions IS 'Individual approval actions';

-- ========================================
-- 6. AUDIT LOG
-- ========================================

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Who
    user_id UUID REFERENCES users(id),
    user_email VARCHAR(255),

    -- Where
    cpa_firm_id UUID REFERENCES cpa_firms(id),
    client_id UUID REFERENCES clients(id),

    -- What
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,

    -- Details
    description TEXT,
    changes JSONB,  -- Before/after values

    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_firm ON audit_log(cpa_firm_id);
CREATE INDEX idx_audit_log_client ON audit_log(client_id);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);

COMMENT ON TABLE audit_log IS 'Comprehensive audit trail of all actions';

-- ========================================
-- 7. ROW-LEVEL SECURITY POLICIES
-- ========================================

-- Enable RLS on key tables
ALTER TABLE engagements ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Engagements: Users can only see engagements for their firm's clients
CREATE POLICY engagement_firm_isolation ON engagements
    FOR ALL
    USING (
        client_id IN (
            SELECT c.id FROM clients c
            WHERE c.cpa_firm_id = current_setting('app.current_firm_id')::UUID
        )
    );

-- Clients: Users can only see clients of their firm
CREATE POLICY client_firm_isolation ON clients
    FOR ALL
    USING (cpa_firm_id = current_setting('app.current_firm_id')::UUID);

-- Users: Firm users see firm users, client users see their client users
CREATE POLICY user_firm_isolation ON users
    FOR ALL
    USING (
        cpa_firm_id = current_setting('app.current_firm_id')::UUID
        OR
        client_id = current_setting('app.current_client_id')::UUID
    );

-- ========================================
-- 8. VIEWS
-- ========================================

-- User permissions view (flattened)
CREATE OR REPLACE VIEW user_permissions_view AS
SELECT
    u.id AS user_id,
    u.email,
    u.cpa_firm_id,
    u.client_id,
    r.role_type,
    r.role_name,
    p.permission_name,
    p.resource_type,
    p.action
FROM users u
JOIN user_roles ur ON ur.user_id = u.id
JOIN roles r ON r.id = ur.role_id
JOIN role_permissions rp ON rp.role_id = r.id
JOIN permissions p ON p.id = rp.permission_id
WHERE u.is_active = TRUE
AND r.is_active = TRUE;

COMMENT ON VIEW user_permissions_view IS 'Flattened view of user permissions';

-- Firm dashboard metrics
CREATE OR REPLACE VIEW firm_dashboard_metrics AS
SELECT
    f.id AS firm_id,
    f.firm_name,
    f.subscription_tier,
    COUNT(DISTINCT c.id) AS total_clients,
    COUNT(DISTINCT u.id) AS total_users,
    COUNT(DISTINCT e.id) AS total_engagements,
    COUNT(DISTINCT e.id) FILTER (WHERE e.status = 'in_progress') AS active_engagements,
    COUNT(DISTINCT e.id) FILTER (WHERE e.status = 'complete') AS completed_engagements
FROM cpa_firms f
LEFT JOIN clients c ON c.cpa_firm_id = f.id AND c.is_active = TRUE
LEFT JOIN users u ON u.cpa_firm_id = f.id AND u.is_active = TRUE
LEFT JOIN engagements e ON e.client_id = c.id
WHERE f.is_active = TRUE
GROUP BY f.id, f.firm_name, f.subscription_tier;

COMMENT ON VIEW firm_dashboard_metrics IS 'Dashboard metrics for CPA firms';

-- Client portal access summary
CREATE OR REPLACE VIEW client_portal_access AS
SELECT
    c.id AS client_id,
    c.client_name,
    c.cpa_firm_id,
    c.portal_enabled,
    c.allow_document_upload,
    c.allow_confirmation_response,
    c.allow_data_export,
    c.allow_report_download,
    c.allow_messaging,
    c.allow_financial_view,
    COUNT(DISTINCT u.id) AS total_client_users,
    COUNT(DISTINCT u.id) FILTER (WHERE u.is_active = TRUE) AS active_client_users
FROM clients c
LEFT JOIN users u ON u.client_id = c.id
WHERE c.is_active = TRUE
GROUP BY c.id, c.client_name, c.cpa_firm_id, c.portal_enabled,
    c.allow_document_upload, c.allow_confirmation_response,
    c.allow_data_export, c.allow_report_download,
    c.allow_messaging, c.allow_financial_view;

COMMENT ON VIEW client_portal_access IS 'Client portal configuration and user counts';
