-- R&D Study Automation Service Database Initialization
-- This script runs when the PostgreSQL container is first created

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schema
CREATE SCHEMA IF NOT EXISTS rd_study;

-- Grant permissions
GRANT ALL ON SCHEMA rd_study TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA rd_study TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA rd_study TO postgres;

-- Set search path
ALTER DATABASE rd_study_automation SET search_path TO rd_study, public;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'R&D Study Automation database initialized successfully';
END $$;
