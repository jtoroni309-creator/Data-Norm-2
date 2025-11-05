# QA & Quality Control

## Test Strategy

### Unit Tests (pytest)
- **Target**: 85% coverage
- **Scope**: Business logic, validation, schema constraints
- **Run**: `pytest tests/unit -v --cov=app`

### Integration Tests
- **Target**: 70% coverage
- **Scope**: Service-to-service, database interactions
- **Run**: `pytest tests/integration -v`

### E2E Tests (Playwright)
- **Critical Paths**:
  1. Import TB → View in binder
  2. Run JE analytics → Flag anomalies
  3. Generate disclosure → Review citations
  4. QC pass → Partner e-sign → Lock binder
  5. Verify WORM URI + hash

- **Run**: `cd tests/e2e && npx playwright test`

## Data Quality (Great Expectations)

### TB Suite (`orchestration/gx/tb_suite.json`)
- Debits = Credits (within 0.01 tolerance)
- No null account codes
- All account codes match COA regex
- Balance amounts sum to zero

### XBRL Suite (`orchestration/gx/xbrl_suite.json`)
- All concepts in us-gaap taxonomy
- Dates within fiscal year
- No negative values for non-negative concepts

## QC Policies (Blocking)

| Policy Code | Standard | Check |
|-------------|----------|-------|
| AS1215_DOCUMENTATION | PCAOB AS 1215 | All procedures have workpapers |
| SAS142_EVIDENCE | AICPA SAS 142 | Material accounts have evidence |
| SAS145_RISK_ASSESSMENT | AICPA SAS 145 | All risks have linked procedures |
| PARTNER_SIGN_OFF | Firm Policy | Partner e-signature exists |
| QC_REVIEW_COMPLETE | Firm Policy | No open blocking review notes |

**Implementation**: `services/qc/app/policies.py`

## Audit Trail Testing

Verify immutability:
```sql
-- Check binder version integrity
SELECT 
    binder_version_id,
    content_hash,
    worm_uri,
    locked_at,
    retention_until
FROM binder_versions
WHERE engagement_id = '<uuid>'
  AND is_final = true;

-- Verify WORM object exists and is locked
-- (AWS CLI)
aws s3api head-object \
    --bucket atlas-worm \
    --key <path> \
    --query 'ObjectLockMode'
```
