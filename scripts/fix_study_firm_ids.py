"""
Fix R&D Study firm_id values.

The rd-study-automation service was using a default fallback firm_id when the JWT
token didn't contain the firm_id claim (because it was looking for "firm_id" but
the identity service puts "cpa_firm_id" in the token).

The wrong default firm_id was: ca3f0a9d-b57a-56fa-8451-996da4c04a26
(calculated from uuid5(NAMESPACE_DNS, "aura-audit-ai.toroniandcompany.com"))

Run the following SQL in Supabase SQL Editor to fix:
"""

# The wrong default firm_id that was being used
DEFAULT_WRONG_FIRM_ID = "ca3f0a9d-b57a-56fa-8451-996da4c04a26"

FIX_SQL = f"""
-- ============================================================================
-- STEP 1: Check which studies have the wrong firm_id
-- ============================================================================
SELECT
    s.id as study_id,
    s.name as study_name,
    s.entity_name,
    s.firm_id as current_wrong_firm_id,
    s.created_by,
    u.email as created_by_email,
    u.cpa_firm_id as correct_firm_id,
    f.firm_name as correct_firm_name
FROM atlas.rd_studies s
LEFT JOIN atlas.users u ON s.created_by = u.id
LEFT JOIN atlas.cpa_firms f ON u.cpa_firm_id = f.id
WHERE s.firm_id = '{DEFAULT_WRONG_FIRM_ID}'::uuid
ORDER BY s.created_at DESC;

-- ============================================================================
-- STEP 2: Update studies to use the correct firm_id from the creator's user record
-- ============================================================================
UPDATE atlas.rd_studies s
SET firm_id = u.cpa_firm_id
FROM atlas.users u
WHERE s.created_by = u.id
  AND s.firm_id = '{DEFAULT_WRONG_FIRM_ID}'::uuid
  AND u.cpa_firm_id IS NOT NULL;

-- ============================================================================
-- STEP 3: Verify the fix - show studies grouped by firm
-- ============================================================================
SELECT
    f.firm_name,
    f.id as firm_id,
    COUNT(s.id) as study_count
FROM atlas.rd_studies s
LEFT JOIN atlas.cpa_firms f ON s.firm_id = f.id
GROUP BY f.id, f.firm_name
ORDER BY study_count DESC;

-- ============================================================================
-- STEP 4: Detailed verification - list some studies with their firms
-- ============================================================================
SELECT
    s.id as study_id,
    s.name as study_name,
    s.entity_name,
    s.firm_id,
    f.firm_name
FROM atlas.rd_studies s
LEFT JOIN atlas.cpa_firms f ON s.firm_id = f.id
ORDER BY s.created_at DESC
LIMIT 20;
"""

print("="*80)
print("SQL to run in Supabase SQL Editor to fix R&D Study firm_id values")
print("="*80)
print(FIX_SQL)
print("="*80)
