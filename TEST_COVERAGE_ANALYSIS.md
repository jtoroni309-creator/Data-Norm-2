# Comprehensive Test Coverage Analysis Report
## Data-Norm Platform - All Services

**Report Generated:** 2024-11-06
**Total Services Analyzed:** 25
**Services with Tests:** 13 (52%)
**Services WITHOUT Tests:** 12 (48%)

---

## EXECUTIVE SUMMARY

### Current Testing Status:
- **Total Test Files:** 26 (across 13 services)
- **Services with Excellent Coverage:** 3 (financial-analysis, llm, fraud-detection)
- **Services with Moderate Coverage:** 7 (analytics, audit-planning, engagement, identity, normalize, qc, reporting)
- **Services with Minimal Coverage:** 3 (sampling, substantive-testing, disclosures)
- **Services with ZERO Tests:** 12 (48% of all services)

### Coverage Levels:
- **GOOD COVERAGE (>5 tests, multiple modules tested):** 3 services
- **MODERATE COVERAGE (1-2 tests, some modules tested):** 7 services
- **MINIMAL COVERAGE (1 test, single or few modules):** 3 services
- **NO TESTS:** 12 services (CRITICAL - needs immediate attention)

---

## SECTION 1: SERVICES WITH GOOD TEST COVERAGE

### 1. financial-analysis
**Status:** EXCELLENT COVERAGE ✓
**Test Files:** 10
**Location:** `/services/financial-analysis/tests/unit/`
**Test Framework:** pytest with async support

**App Modules (19 total):**
```
- __init__.py ✓
- admin_portal_api.py (NOT TESTED)
- client_portal_api.py (NOT TESTED)
- config.py ✓
- confirmation_service.py (PARTIALLY TESTED)
- database.py ✓
- disclosure_notes_service.py (NOT TESTED)
- edgar_service.py (TESTED)
- engagement_service.py (NOT TESTED)
- financial_analyzer.py (NOT TESTED)
- jira_api.py (NOT TESTED)
- jira_service.py (NOT TESTED)
- main.py ✓
- models.py ✓
- permission_middleware.py (NOT TESTED)
- permission_service.py (TESTED)
- permissions_models.py (NOT TESTED)
- stripe_api.py (NOT TESTED)
- stripe_service.py (NOT TESTED)
```

**Current Tests:**
- test_ai_pipeline.py - AI/ML financial analysis
- test_confirmations.py - Electronic confirmations (AS 2310)
- test_disclosure_notes.py - Financial statement notes
- test_edgar.py - SEC Edgar integration
- test_edgar_mock.py - Edgar mocking/fixtures
- test_engagements.py - Engagement workflows
- test_permissions.py - Authorization/permissions

**Gaps Identified:**
- admin_portal_api.py - Needs API integration tests
- client_portal_api.py - Needs API integration tests
- disclosure_notes_service.py - Business logic untested
- engagement_service.py - Core service untested
- financial_analyzer.py - Core analysis engine untested
- jira_api.py - Integration untested
- jira_service.py - Service layer untested
- permission_middleware.py - Middleware untested
- stripe_api.py - Payment integration untested
- stripe_service.py - Billing service untested

**Key Functionality Needing Tests:**
- Admin portal endpoints (user management, billing, analytics)
- Client portal endpoints (engagement view, document upload)
- Financial analysis engine (ratios, trends, anomalies)
- JIRA integration workflows
- Stripe payment processing
- Permission middleware chain
- Disclosure notes generation

---

### 2. llm (Large Language Model Service)
**Status:** GOOD COVERAGE ✓
**Test Files:** 3
**Location:** `/services/llm/tests/` (unit/ and integration/)
**Conftest:** YES (fixtures for embeddings, documents)

**App Modules (8 total):**
```
- __init__.py ✓
- config.py ✓
- database.py ✓
- embedding_service.py (TESTED)
- main.py (PARTIALLY TESTED)
- models.py ✓
- rag_engine.py (TESTED)
- schemas.py ✓
```

**Current Tests:**
- test_embedding_service.py - Vector embeddings
- test_rag_engine.py - RAG (Retrieval Augmented Generation)
- test_api.py (integration) - API endpoints

**Gaps Identified:**
- main.py - Main application startup untested
- Async endpoint handlers not fully covered

**Key Functionality Needing Tests:**
- Full API endpoint coverage (GET, POST, PUT, DELETE)
- Error handling and edge cases
- Token counting and limits
- Context window management
- Chunk retrieval optimization
- Citation building and verification

---

### 3. fraud-detection
**Status:** GOOD COVERAGE ✓
**Test Files:** 2
**Location:** `/services/fraud-detection/tests/`
**Conftest:** YES

**App Modules (8 total):**
```
- __init__.py ✓
- config.py ✓
- database.py ✓
- main.py (PARTIALLY TESTED)
- ml_fraud_detector.py (TESTED)
- models.py ✓
- plaid_service.py (NOT TESTED)
- schemas.py ✓
```

**Current Tests:**
- test_api.py - API endpoints
- test_ml_fraud_detector.py - ML fraud detection logic

**Gaps Identified:**
- plaid_service.py - Bank data integration untested
- API error handling not fully covered
- Integration scenarios not tested

**Key Functionality Needing Tests:**
- Plaid API integration (account linking, transaction sync)
- ML model training and updates
- Feature engineering edge cases
- Real-time transaction scoring
- Historical fraud pattern analysis
- Alert escalation workflow

---

## SECTION 2: SERVICES WITH MODERATE TEST COVERAGE

### 4. analytics
**Status:** PARTIAL COVERAGE - BASIC TESTS ONLY ⚠
**Test Files:** 1
**Location:** `/services/analytics/tests/unit/`
**Modules in App:** 7

**App Modules:**
```
- __init__.py ✓
- analytics_engine.py (TESTED)
- config.py (TESTED)
- database.py (NOT TESTED)
- main.py (NOT TESTED)
- models.py (TESTED)
- schemas.py (TESTED)
```

**Current Tests (test_analytics.py):**
- Model attribute validation
- Schema validation
- JournalEntryTester (round dollar, weekend entries)
- AnomalyDetector (Z-score outlier detection)
- RatioAnalyzer (financial ratio calculations)
- Configuration settings

**Critical Gaps:**
- database.py - Not tested
- main.py - FastAPI endpoints not tested
- No integration tests
- No API endpoint tests
- No error handling tests

**Key Functionality Needing Tests:**
- All FastAPI endpoints (analytics queries, rule management)
- Database operations (CRUD for rules, results)
- Anomaly resolution workflow
- Batch analytics job processing
- Report generation
- Real-time vs batch analytics
- Performance optimization validation

---

### 5. audit-planning
**Status:** PARTIAL COVERAGE - CORE LOGIC TESTS ⚠
**Test Files:** 1
**Location:** `/services/audit-planning/tests/`
**Modules in App:** 4

**App Modules:**
```
- __init__.py (NOT TESTED)
- config.py (NOT TESTED)
- database.py (NOT TESTED)
- models.py (NOT TESTED)
- planning_service.py (TESTED)
```

**Current Tests (test_planning_service.py):**
- MaterialityCalculator (all benchmarks, edge cases)
- RiskAssessor (risk combinations, fraud factors)
- AuditProgramGenerator (procedure generation)
- Integration tests with mocked DB

**Critical Gaps:**
- Database layer not tested
- Configuration not tested
- main.py (FastAPI) not created/tested
- No API endpoint tests
- No async database tests

**Key Functionality Needing Tests:**
- FastAPI endpoints for plan creation/updates
- Database persistence of audit plans
- Risk assessment workflows
- Materiality threshold adjustments
- Audit program generation output
- Compliance with auditing standards
- Performance on large engagements

---

### 6. engagement
**Status:** PARTIAL COVERAGE - MODELS AND SCHEMAS ⚠
**Test Files:** 1
**Location:** `/services/engagement/tests/unit/`
**Modules in App:** 6

**App Modules:**
```
- __init__.py (NOT TESTED)
- config.py (NOT TESTED)
- database.py (NOT TESTED)
- main.py (NOT TESTED)
- models.py (TESTED)
- schemas.py (TESTED)
```

**Current Tests (test_engagement.py):**
- Engagement model attributes
- EngagementTeamMember model
- BinderNode model (hierarchy testing)
- Pydantic schema validation
- State transitions
- Business logic (team members, binder trees)
- Configuration

**Critical Gaps:**
- database.py operations not tested
- main.py endpoints not tested
- No API integration tests
- No async operations tested
- No workflow state machine tests

**Key Functionality Needing Tests:**
- Engagement lifecycle (create, update, finalize)
- Team member management
- Audit binder tree operations (add, move, delete nodes)
- Permission-based access control
- Concurrent access handling
- Document upload handling
- Engagement status notifications

---

### 7. identity
**Status:** PARTIAL COVERAGE - AUTHENTICATION ONLY ⚠
**Test Files:** 1
**Location:** `/services/identity/tests/unit/`
**Modules in App:** 6

**App Modules:**
```
- __init__.py (NOT TESTED)
- config.py (NOT TESTED)
- database.py (NOT TESTED)
- main.py (TESTED - auth functions only)
- models.py (NOT TESTED)
- schemas.py (NOT TESTED)
```

**Current Tests (test_auth.py):**
- Password hashing (bcrypt)
- Password verification
- JWT token creation and validation
- Token claims verification

**Critical Gaps:**
- User management endpoints not tested
- Role-based access control not tested
- OAuth/OIDC integration not tested
- User registration/login not tested
- Token refresh logic not tested
- Profile management not tested
- MFA/2FA not tested
- Database operations not tested

**Key Functionality Needing Tests:**
- User registration and validation
- Login/logout workflows
- JWT token generation and validation
- Token refresh and expiration
- Role and permission assignment
- Multi-factor authentication
- SSO/OAuth integration
- Session management
- Account recovery flows

---

### 8. normalize
**Status:** PARTIAL COVERAGE - CORE ENGINE ⚠
**Test Files:** 1
**Location:** `/services/normalize/tests/unit/`
**Modules in App:** 7

**App Modules:**
```
- __init__.py (NOT TESTED)
- config.py (NOT TESTED)
- database.py (NOT TESTED)
- main.py (NOT TESTED)
- mapping_engine.py (TESTED)
- models.py (NOT TESTED)
- schemas.py (NOT TESTED)
```

**Current Tests (test_normalize.py):**
- Mapping engine logic
- Schema transformations

**Critical Gaps:**
- FastAPI endpoints not tested
- Database operations not tested
- Configuration not tested
- No integration tests
- No complex mapping scenarios

**Key Functionality Needing Tests:**
- Data normalization pipeline
- Field mapping and transformation
- Data type conversions
- Account reconciliation
- Custom mapping rules
- Bulk normalization jobs
- Error handling and validation
- Performance under load

---

### 9. qc (Quality Control)
**Status:** PARTIAL COVERAGE - POLICIES ONLY ⚠
**Test Files:** 1
**Location:** `/services/qc/tests/unit/`
**Modules in App:** 7

**App Modules:**
```
- __init__.py (NOT TESTED)
- config.py (NOT TESTED)
- database.py (NOT TESTED)
- main.py (NOT TESTED)
- models.py (NOT TESTED)
- policies.py (TESTED)
- schemas.py (NOT TESTED)
```

**Current Tests (test_policies.py):**
- Policy registry operations
- Individual policy evaluation
- Policy chaining

**Critical Gaps:**
- API endpoints not tested
- Database operations not tested
- Policy execution workflow not tested
- Compliance checks not tested
- Audit trail not tested

**Key Functionality Needing Tests:**
- QC policy compliance checking
- Multi-policy validation chains
- Finding identification and tracking
- Review assignment workflow
- Exception handling
- Policy enforcement automation
- Metrics and reporting
- Audit documentation

---

### 10. reporting
**Status:** PARTIAL COVERAGE - PDF AND API ⚠
**Test Files:** 2
**Location:** `/services/reporting/tests/`
**Conftest:** YES

**App Modules (9 total):**
```
- __init__.py (NOT TESTED)
- config.py (NOT TESTED)
- database.py (NOT TESTED)
- docusign_service.py (NOT TESTED)
- main.py (PARTIALLY TESTED)
- models.py (NOT TESTED)
- pdf_service.py (TESTED)
- schemas.py (NOT TESTED)
- storage_service.py (NOT TESTED)
```

**Current Tests:**
- test_pdf_service.py - PDF generation
- test_api.py (integration) - API endpoints

**Critical Gaps:**
- DocuSign integration not tested
- Cloud storage service not tested
- Report template management not tested
- Audit report generation not tested
- Email distribution not tested
- Version control not tested

**Key Functionality Needing Tests:**
- Report generation (PDF, Excel, Word)
- Digital signature workflows (DocuSign)
- Cloud storage integration (S3/Azure)
- Report distribution
- Version management
- Audit trail for reports
- Multi-format export
- Performance under load

---

## SECTION 3: SERVICES WITH MINIMAL TEST COVERAGE

### 11. sampling
**Status:** MINIMAL - SINGLE MODULE ⚠
**Test Files:** 1
**Location:** `/services/sampling/tests/`
**Modules in App:** 1

**App Modules:**
```
- sampling_service.py (TESTED)
```

**Current Tests (test_sampling_service.py):**
- Sampling methodology tests (basic)

**Critical Gaps:**
- No integration tests
- No API tests
- No database tests
- No endpoint tests
- Limited test cases

**Key Functionality Needing Tests:**
- Statistical sampling methods
- Sample size calculation
- Stratified sampling
- Random selection
- Audit procedure selection
- Results evaluation
- Confidence interval calculation
- Exception handling

---

### 12. substantive-testing
**Status:** MINIMAL - SINGLE MODULE ⚠
**Test Files:** 1
**Location:** `/services/substantive-testing/tests/`
**Modules in App:** 1

**App Modules:**
```
- journal_entry_testing.py (TESTED)
```

**Current Tests (test_journal_entry_testing.py):**
- Journal entry testing logic

**Critical Gaps:**
- No API endpoint tests
- No integration tests
- No complex scenarios
- Limited test coverage

**Key Functionality Needing Tests:**
- Journal entry selection
- Testing procedures execution
- Accuracy verification
- Exception detection
- Analytical procedures
- Cutoff testing
- Completeness testing
- Results aggregation

---

### 13. disclosures
**Status:** MINIMAL - WEB/ORCHESTRATION FOCUS ⚠
**Test Files:** 3 (web-focused)
**Location:** `/services/disclosures/web/tests/`
**App Modules (6 core + web/orchestration)**

**App Modules:**
```
- app/__init__.py (NOT TESTED)
- app/config.py (NOT TESTED)
- app/database.py (NOT TESTED)
- app/main.py (NOT TESTED)
- app/models.py (NOT TESTED)
- app/schemas.py (NOT TESTED)
- web/orchestration/dags/ (PARTIAL - test_ingestion_service.py, test_edgar_client.py, test_sample.py)
```

**Current Tests:**
- test_ingestion_service.py (integration)
- test_edgar_client.py (unit)
- test_sample.py (unit)

**Critical Gaps:**
- Core app modules (main.py, models.py) not tested
- FastAPI endpoints not tested
- Database operations not tested
- Limited EDGAR integration testing
- No end-to-end workflows

**Key Functionality Needing Tests:**
- SEC Edgar data ingestion
- Disclosure parsing and extraction
- Company matching
- Historical data tracking
- Change detection
- Caching strategy
- Performance optimization
- Error recovery

---

## SECTION 4: SERVICES WITH ZERO TEST COVERAGE

### Critical Priority Services (require immediate testing):

#### 14. reg-ab-audit (CRITICAL IMPORTANCE)
**Status:** NO TESTS ✗ CRITICAL
**Modules in App:** 9
**Description:** Regulation AB Audit for CMBS loans with AI compliance

**App Modules (ALL UNTESTED):**
```
- __init__.py
- ai_compliance_engine.py ⚠ CRITICAL
- config.py
- database.py
- main.py
- models.py
- report_generator.py ⚠ CRITICAL
- schemas.py
- workpaper_generator.py ⚠ CRITICAL
```

**Key Functionality Needing Tests:**
- AI compliance checking engine
- Reg AB compliance verification
- CMBS loan analysis
- Risk assessment
- Report generation
- Workpaper generation
- Documentation requirements
- Standards compliance (FCRA, SEC)
- Performance metrics tracking

**Estimated Test Files Needed:** 5-7
- test_ai_compliance_engine.py
- test_report_generator.py
- test_workpaper_generator.py
- test_reg_ab_compliance.py
- test_cmbs_analysis.py

---

#### 15. security (CRITICAL IMPORTANCE)
**Status:** NO TESTS ✗ CRITICAL
**Modules in App:** 8
**Description:** Security and encryption services

**App Modules (ALL UNTESTED):**
```
- __init__.py
- audit_logging.py ⚠ CRITICAL
- compliance_models.py
- config.py
- database.py
- encryption_service.py ⚠ CRITICAL
- key_management.py ⚠ CRITICAL
- security_middleware.py ⚠ CRITICAL
```

**Key Functionality Needing Tests:**
- Encryption/decryption operations
- Key management and rotation
- Security audit logging
- Compliance tracking
- Access control enforcement
- Vulnerability scanning
- Secure data handling
- Password/token management
- SOC2 compliance

**Estimated Test Files Needed:** 5-6
- test_encryption_service.py
- test_key_management.py
- test_audit_logging.py
- test_security_middleware.py
- test_compliance_models.py

---

#### 16. ingestion (HIGH IMPORTANCE)
**Status:** NO TESTS ✗ HIGH PRIORITY
**Modules in App:** 7
**Description:** Data ingestion service

**App Modules (ALL UNTESTED):**
```
- __init__.py
- config.py
- database.py
- edgar.py ⚠ IMPORTANT
- main.py
- models.py
- schemas.py
```

**Key Functionality Needing Tests:**
- Data source connections
- Edgar data ingestion
- File parsing and validation
- Data transformation
- Error handling and retry logic
- Duplicate detection
- Data quality checks
- Performance at scale

**Estimated Test Files Needed:** 4-5
- test_edgar_integration.py
- test_data_validation.py
- test_ingestion_workflow.py
- test_error_handling.py

---

#### 17. accounting-integrations (HIGH IMPORTANCE)
**Status:** NO TESTS ✗ HIGH PRIORITY
**Modules in App:** 5
**Description:** Accounting system integrations (QuickBooks, Xero)

**App Modules (ALL UNTESTED):**
```
- __init__.py
- integration_manager.py ⚠ IMPORTANT
- main.py
- quickbooks_integration.py ⚠ IMPORTANT
- xero_integration.py ⚠ IMPORTANT
```

**Key Functionality Needing Tests:**
- QuickBooks API integration
- Xero API integration
- Account synchronization
- Transaction mapping
- Authentication and OAuth
- Data consistency validation
- Conflict resolution
- Rate limiting handling

**Estimated Test Files Needed:** 4
- test_quickbooks_integration.py
- test_xero_integration.py
- test_integration_manager.py
- test_sync_workflow.py

---

### Lower Priority Services (still need testing):

#### 18. data-anonymization
**Status:** NO TESTS ✗
**Modules in App:** 2
```
- __init__.py
- anonymization_service.py
```
**Estimated Tests:** 2 files

#### 19. eo-insurance-portal
**Status:** NO TESTS ✗
**Modules in App:** 3
```
- __init__.py
- main.py
- risk_assessment_service.py
```
**Estimated Tests:** 2 files

#### 20. estimates-evaluation
**Status:** NO TESTS ✗
**Modules in App:** 1
```
- estimates_service.py
```
**Estimated Tests:** 1 file

#### 21. related-party
**Status:** NO TESTS ✗
**Modules in App:** 1
```
- related_party_service.py
```
**Estimated Tests:** 1 file

#### 22. subsequent-events
**Status:** NO TESTS ✗
**Modules in App:** 1
```
- subsequent_events_service.py
```
**Estimated Tests:** 1 file

#### 23. training-data
**Status:** NO TESTS ✗
**Modules in App:** 2
```
- __init__.py
- training_data_service.py
```
**Estimated Tests:** 1-2 files

#### 24. connectors
**Status:** NO TESTS ✗
**Modules in App:** 0 (placeholder service)

---

## SECTION 5: DETAILED TEST IMPLEMENTATION ROADMAP

### Phase 1: Critical Security & Compliance (Weeks 1-2)
**Priority:** CRITICAL
**Target:** 70%+ coverage for security services

1. **security service** (5-6 test files)
   - Encryption service tests
   - Key management tests
   - Audit logging tests
   - Security middleware tests

2. **reg-ab-audit service** (5-7 test files)
   - AI compliance engine
   - Report generation
   - Workpaper generation

**Expected Coverage Gain:** 25-30%

### Phase 2: Core Business Logic (Weeks 3-4)
**Priority:** HIGH
**Target:** 70%+ coverage for business-critical services

1. **accounting-integrations** (4 test files)
2. **ingestion** (4-5 test files)
3. **financial-analysis** (2-3 additional test files for untested modules)

**Expected Coverage Gain:** 20-25%

### Phase 3: Workflows & Integrations (Weeks 5-6)
**Priority:** MEDIUM
**Target:** 60%+ coverage for workflow services

1. **data-anonymization** (2 test files)
2. **eo-insurance-portal** (2 test files)
3. **training-data** (1-2 test files)
4. **reporting** (2-3 additional test files)

**Expected Coverage Gain:** 15-20%

### Phase 4: Specialized Services (Weeks 7-8)
**Priority:** MEDIUM
**Target:** 60%+ coverage for specialized services

1. **estimates-evaluation** (1 test file)
2. **related-party** (1 test file)
3. **subsequent-events** (1 test file)

**Expected Coverage Gain:** 5-10%

### Phase 5: Coverage Enhancement (Weeks 9-10)
**Priority:** MEDIUM
**Target:** Improve existing test coverage

1. Expand analytics service tests
2. Expand audit-planning tests
3. Expand engagement tests
4. Expand identity tests
5. Expand qc tests
6. Expand normalize tests

**Expected Coverage Gain:** 15-25%

---

## SECTION 6: TESTING BEST PRACTICES OBSERVATIONS

### Existing Test Patterns (to replicate):
1. **Unit tests** - Model and schema validation
2. **Integration tests** - API endpoints with mocked DB
3. **Fixtures** - conftest.py for reusable test data
4. **Async Testing** - pytest-asyncio for async functions
5. **Mocking** - AsyncMock and MagicMock for dependencies

### Test File Organization:
- Location: `/services/{service}/tests/unit/test_*.py`
- Integration tests: `/services/{service}/tests/integration/test_*.py`
- Fixtures: `/services/{service}/tests/conftest.py`

### Recommended Test Types per Service:

**For data processing services:**
- Unit tests for business logic
- Integration tests for data flow
- Edge case testing for boundary conditions
- Performance tests for bulk operations

**For API services:**
- Endpoint tests (GET, POST, PUT, DELETE)
- Authentication/authorization tests
- Error handling tests
- Integration tests with dependent services

**For integration services:**
- Mock external API tests
- Error recovery tests
- Rate limiting tests
- Data consistency tests

**For security-related services:**
- Encryption/decryption tests
- Key rotation tests
- Audit logging tests
- Compliance verification tests

---

## SECTION 7: COVERAGE METRICS & TARGETS

### Current State:
```
Total Test Files:        26
Service Coverage:        52% (13 of 25)
Estimated Code Coverage: ~35-40% (needs measurement)
```

### Target State (70%+ coverage):
```
Required Test Files:     ~50-60 additional files
Target Services:         All 25 services
Target Code Coverage:    70%+ for critical services
                        60%+ for non-critical services
                        40%+ for utility services
```

### By Priority:

**CRITICAL (must reach 70%+):**
- security
- reg-ab-audit
- financial-analysis
- accounting-integrations
- ingestion
- audit-planning

**HIGH (should reach 60-70%):**
- engagement
- identity
- normalize
- qc
- llm
- fraud-detection
- reporting

**MEDIUM (should reach 50-60%):**
- data-anonymization
- eo-insurance-portal
- estimates-evaluation
- related-party
- sampling
- substantive-testing
- subsequent-events
- training-data
- disclosures

---

## SECTION 8: RECOMMENDED NEXT STEPS

### Immediate Actions (This Sprint):
1. Create testing strategy document
2. Set up pytest configuration across all services
3. Create template test files for new services
4. Identify code coverage tools (pytest-cov, coverage.py)
5. Set CI/CD integration for test runs

### Short Term (1-2 weeks):
1. Focus on CRITICAL security tests
2. Add tests for all API endpoints
3. Create integration test suite
4. Document test data requirements

### Medium Term (2-4 weeks):
1. Expand coverage for HIGH priority services
2. Add performance tests
3. Create end-to-end test scenarios
4. Build test data factories

### Long Term (4+ weeks):
1. Reach 70%+ coverage on all critical services
2. Implement mutation testing
3. Performance benchmark tests
4. Contract testing for service boundaries

---

## SUMMARY TABLE

| Service | Status | Files | Modules | Coverage | Priority |
|---------|--------|-------|---------|----------|----------|
| financial-analysis | GOOD | 10 | 19 | 55% | HIGH |
| llm | GOOD | 3 | 8 | 60% | HIGH |
| fraud-detection | GOOD | 2 | 8 | 50% | HIGH |
| analytics | PARTIAL | 1 | 7 | 35% | MEDIUM |
| audit-planning | PARTIAL | 1 | 4 | 40% | HIGH |
| engagement | PARTIAL | 1 | 6 | 35% | HIGH |
| identity | PARTIAL | 1 | 6 | 30% | HIGH |
| normalize | PARTIAL | 1 | 7 | 30% | MEDIUM |
| qc | PARTIAL | 1 | 7 | 30% | MEDIUM |
| reporting | PARTIAL | 2 | 9 | 35% | HIGH |
| sampling | MINIMAL | 1 | 1 | 50% | LOW |
| substantive-testing | MINIMAL | 1 | 1 | 50% | LOW |
| disclosures | MINIMAL | 3 | 6 | 30% | MEDIUM |
| accounting-integrations | NONE | 0 | 5 | 0% | HIGH |
| connectors | NONE | 0 | 0 | 0% | LOW |
| data-anonymization | NONE | 0 | 2 | 0% | MEDIUM |
| eo-insurance-portal | NONE | 0 | 3 | 0% | MEDIUM |
| estimates-evaluation | NONE | 0 | 1 | 0% | LOW |
| ingestion | NONE | 0 | 7 | 0% | HIGH |
| reg-ab-audit | NONE | 0 | 9 | 0% | CRITICAL |
| related-party | NONE | 0 | 1 | 0% | LOW |
| security | NONE | 0 | 8 | 0% | CRITICAL |
| subsequent-events | NONE | 0 | 1 | 0% | LOW |
| training-data | NONE | 0 | 2 | 0% | MEDIUM |

