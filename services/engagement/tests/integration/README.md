# Engagement Service - Integration Tests

## Overview

This directory contains end-to-end integration tests that verify the complete engagement workflow and ensure proper data flow through all services.

## Test Coverage

### 1. Complete Engagement Workflow (`TestEngagementWorkflow`)

**Tests the core audit engagement lifecycle:**

```
Draft → Planning → Fieldwork → Review → Finalized
```

- **`test_complete_engagement_lifecycle`**: Verifies the complete workflow from creation to finalization
  - Creates engagement in DRAFT status
  - Transitions through all valid states
  - Verifies finalization gates (QC and signature) block invalid finalization

- **`test_invalid_state_transition`**: Ensures invalid transitions are rejected
  - Example: Cannot jump from DRAFT directly to REVIEW
  - Validates state machine enforcement

- **`test_backward_transitions`**: Tests backward state transitions
  - Example: REVIEW → FIELDWORK (allowed for rework)
  - Validates bidirectional transitions where appropriate

### 2. QC Gates (`TestQCGates`)

**Tests Quality Control gates block finalization:**

- **`test_finalization_blocked_by_failed_qc_policy`**:
  - Creates blocking QC policy
  - Sets QC check status to 'failed'
  - Verifies finalization is blocked
  - Confirms error message lists failed policies

- **`test_finalization_allowed_with_passed_qc_policies`**:
  - Creates blocking QC policy
  - Sets QC check status to 'passed'
  - Creates required partner signature
  - Verifies finalization succeeds
  - Confirms engagement is locked after finalization

**QC Policy Attributes Tested:**
- `is_blocking=TRUE`: Policy must pass for finalization
- `status='passed'`: QC check passed successfully
- `status='waived'`: QC check waived by authorized user
- `status='failed'`: QC check failed, blocks finalization

### 3. Partner Signature Gate (`TestPartnerSignatureGate`)

**Tests partner signature requirement for finalization:**

- **`test_finalization_blocked_without_partner_signature`**:
  - QC checks pass
  - No signature envelope exists
  - Verifies finalization is blocked

- **`test_finalization_blocked_with_pending_signature`**:
  - QC checks pass
  - Signature envelope exists but status is 'pending'
  - Verifies finalization is blocked
  - Only 'completed' signatures allow finalization

**Signature Requirements:**
- Report types checked: `audit_opinion`, `review_opinion`, `compilation_report`
- Signature status must be: `completed`
- Latest signature envelope for engagement is used

### 4. Engagement Locking (`TestEngagementLocking`)

**Tests engagement locking on finalization:**

- **`test_engagement_locked_on_finalization`**:
  - Verifies `locked_at` timestamp is set
  - Verifies `locked_by` user_id is recorded

- **`test_finalized_engagement_cannot_transition`**:
  - FINALIZED is terminal state
  - No transitions allowed from FINALIZED
  - Validates immutability of finalized engagements

## Running the Tests

### Prerequisites

1. Test database must be available:
   ```bash
   # Database: atlas_test
   # URL: postgresql+asyncpg://atlas:atlas_secret@db:5432/atlas_test
   ```

2. Install test dependencies:
   ```bash
   pip install pytest pytest-asyncio httpx
   ```

### Run All Integration Tests

```bash
# From engagement service directory
pytest tests/integration/ -v

# Run specific test class
pytest tests/integration/test_engagement_workflow.py::TestEngagementWorkflow -v

# Run specific test
pytest tests/integration/test_engagement_workflow.py::TestQCGates::test_finalization_blocked_by_failed_qc_policy -v
```

### Run with Coverage

```bash
pytest tests/integration/ --cov=app --cov-report=html
```

## Test Data Setup

Each test uses fixtures to create clean test data:

- **`test_db`**: Creates isolated test database session
- **`test_client`**: FastAPI test client with database override
- **`test_data`**: Creates:
  - Test user (manager role)
  - Partner user (partner role)
  - Test client company
  - Returns IDs for use in tests

## Database Schema Requirements

Tests expect the following tables to exist:

- `atlas.engagements` - Core engagement data
- `atlas.qc_policies` - QC policy definitions
- `atlas.qc_checks` - QC check execution results
- `atlas.reports` - Generated reports
- `atlas.signature_envelopes` - E-signature tracking
- `atlas.clients` - Client information
- `atlas.users` - User accounts

## Integration Points Tested

### Cross-Service Data Flow

1. **Engagement → QC Service**
   - Engagement ID used to query QC checks
   - Blocking policies must pass before finalization

2. **Engagement → Reporting Service**
   - Report existence verified for finalization
   - Signature completion checked

3. **Engagement → Identity Service**
   - User authentication via headers
   - Row-level security context

## Business Rules Validated

### State Transitions

| From | To | Valid? | Notes |
|------|-----|--------|-------|
| DRAFT | PLANNING | ✅ | Initial planning |
| DRAFT | REVIEW | ❌ | Cannot skip stages |
| PLANNING | FIELDWORK | ✅ | Begin audit work |
| PLANNING | DRAFT | ✅ | Return for changes |
| FIELDWORK | REVIEW | ✅ | Begin review |
| FIELDWORK | PLANNING | ✅ | Return for planning changes |
| REVIEW | FINALIZED | ✅ | Complete (with gates passed) |
| REVIEW | FIELDWORK | ✅ | Return for additional work |
| FINALIZED | * | ❌ | Terminal state |

### Finalization Gates

An engagement can only be finalized if:

1. ✅ **All blocking QC policies pass**
   - Status must be 'passed' or 'waived'
   - Active policies only

2. ✅ **Partner signature is completed**
   - Report type is opinion/compilation
   - Signature envelope status is 'completed'

3. ✅ **Engagement is in REVIEW status**
   - Cannot finalize from other states

### Post-Finalization

When finalized:
- `status` = 'finalized'
- `locked_at` = current timestamp
- `locked_by` = user ID who finalized
- No further state transitions allowed

## Expected Test Results

All tests should pass if:
- Database schema is correct
- QC gates implementation is correct (lines 321-366 in main.py)
- State machine logic is correct (lines 305-317 in main.py)
- Engagement locking works (lines 368-370 in main.py)

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Ensure test database exists: `atlas_test`
   - Check database credentials
   - Verify database server is running

2. **Table does not exist**
   - Run migrations: `alembic upgrade head`
   - Check schema is 'atlas'

3. **QC gates not blocking**
   - Verify QC implementation in `main.py` lines 321-343
   - Check SQL queries against actual schema

4. **Signature gates not blocking**
   - Verify signature implementation in `main.py` lines 345-366
   - Check report_type values match enum

## Future Enhancements

- [ ] Add tests for team member permissions
- [ ] Add tests for binder tree operations during workflow
- [ ] Add tests for audit trail logging
- [ ] Add performance tests for large engagements
- [ ] Add tests for concurrent state transitions
- [ ] Add tests for RLS (Row-Level Security) enforcement

## Related Documentation

- [Engagement Service API](../../README.md)
- [QC Service Documentation](../../../qc/README.md)
- [Reporting Service Documentation](../../../reporting/README.md)
- [State Machine Design](../../docs/state-machine.md)
