# Regulation A/B Audit Service

AI-powered CMBS (Commercial Mortgage-Backed Securities) loan audit service with automated compliance checking, workpaper generation, and CPA review workflow.

## Overview

This service provides comprehensive Regulation A/B audit capabilities for CMBS loans, ensuring compliance with:

- **PCAOB** (Public Company Accounting Oversight Board) Standards
- **GAAP** (Generally Accepted Accounting Principles)
- **GAAS** (Generally Accepted Auditing Standards)
- **SEC** (Securities and Exchange Commission) Regulation AB
- **AICPA** (American Institute of CPAs) Attestation Standards

## Features

### 🔐 Admin-Controlled Feature Toggle
- Enable/disable the feature per organization through admin portal
- Granular control over AI features, notifications, and workflow settings
- Configurable retention policies and compliance check levels

### 🤖 AI-Powered Compliance Engine
- Automated compliance checking against all major regulatory standards
- GPT-4 Turbo powered analysis with confidence scoring
- Real-time risk assessment and remediation recommendations
- Comprehensive evidence tracking and audit trail

### 📄 Automated Workpaper Generation
- AI generates complete audit workpapers for each CMBS deal
- Includes cash flow analysis, property valuation, servicer assessment
- Compliance summaries and risk assessments
- Professional HTML and PDF output

### 📊 Intelligent Report Generation
- Comprehensive Regulation A/B audit reports
- Executive summaries with key metrics and findings
- Detailed compliance assessments by standard
- Professional formatting ready for CPA review

### ✍️ CPA Review & Sign-Off Workflow
- Dedicated CPA portal for workpaper review
- Digital signature capability with audit trail
- Support for dual sign-off requirements
- Revision request and approval tracking

### 👥 Dual Portal Architecture
- **Client Portal**: CMBS deal submission and progress tracking
- **CPA Firm Portal**: Workpaper review, report approval, sign-off

## Architecture

### Service Structure

```
services/reg-ab-audit/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application
│   ├── models.py                    # SQLAlchemy models
│   ├── schemas.py                   # Pydantic schemas
│   ├── config.py                    # Configuration settings
│   ├── database.py                  # Database connection
│   ├── ai_compliance_engine.py      # AI compliance checking
│   ├── workpaper_generator.py       # Workpaper generation
│   └── report_generator.py          # Report generation
├── Dockerfile
├── requirements.txt
└── README.md
```

### Database Schema

See `db/migrations/0002_reg_ab_audit.sql` for complete schema including:

- `reg_ab_feature_flags` - Feature toggle configuration
- `reg_ab_audit_engagements` - Audit engagements
- `cmbs_deals` - CMBS deals for audit
- `compliance_checks` - AI compliance check results
- `reg_ab_workpapers` - Generated workpapers
- `reg_ab_audit_reports` - Final audit reports
- `cpa_signoffs` - CPA sign-off records
- `compliance_rules_library` - Rule definitions (pre-seeded)

## API Endpoints

### Feature Flag Management (Admin)

```
GET    /api/feature-flags/{organization_id}     # Get feature flags
PATCH  /api/feature-flags/{organization_id}     # Update feature flags
```

### Audit Engagements

```
GET    /api/engagements                         # List engagements
POST   /api/engagements                         # Create engagement
GET    /api/engagements/{id}                    # Get engagement
PATCH  /api/engagements/{id}                    # Update engagement
```

### CMBS Deals (Client Portal)

```
GET    /api/engagements/{id}/deals              # List deals
POST   /api/engagements/{id}/deals              # Create deal (triggers AI)
GET    /api/deals/{id}                          # Get deal
```

### Compliance Checks

```
GET    /api/engagements/{id}/compliance-checks  # List checks
```

### Workpapers (CPA Portal)

```
GET    /api/engagements/{id}/workpapers         # List workpapers
GET    /api/workpapers/{id}                     # Get workpaper
POST   /api/workpapers/{id}/review              # Review workpaper
```

### Reports

```
GET    /api/engagements/{id}/reports            # List reports
GET    /api/reports/{id}                        # Get report
```

### CPA Sign-Off

```
POST   /api/reports/{id}/signoff                # Create sign-off
GET    /api/engagements/{id}/signoffs           # List sign-offs
```

### Dashboard

```
GET    /api/dashboard/metrics                   # Get dashboard metrics
```

## Workflow

### 1. Admin Enablement
1. Admin accesses admin portal
2. Searches for organization
3. Enables Regulation A/B audit feature
4. Configures AI settings, notifications, retention

### 2. Client Submission
1. Client logs into client portal
2. Selects active audit engagement
3. Submits CMBS deal information:
   - Deal identification (name, number, CUSIP)
   - Financial details (balance, interest rate)
   - Property information
   - Servicer details
   - Performance metrics (DSCR, LTV, occupancy)
4. System automatically triggers AI processing

### 3. AI Processing (Background)
1. **Compliance Checking**
   - Runs all applicable compliance rules
   - Analyzes deal against PCAOB, GAAP, GAAS, SEC, AICPA standards
   - Generates findings, recommendations, remediation steps
   - Calculates confidence scores and risk levels

2. **Workpaper Generation**
   - Generates 6 types of workpapers per deal:
     - Cash Flow Analysis
     - Property Valuation Review
     - Servicer Assessment
     - Compliance Summary
     - Risk Assessment
     - Disclosure Review
   - Creates structured content with evidence references
   - Renders professional HTML output

3. **Report Generation** (when all deals processed)
   - Aggregates all compliance checks and workpapers
   - Generates comprehensive audit report
   - Includes executive summary, findings, recommendations
   - Calculates portfolio-level statistics and risk assessment

4. **CPA Notification**
   - Notifies assigned CPA that audit is ready for review
   - Updates engagement status to "CPA Review"

### 4. CPA Review
1. CPA logs into CPA portal
2. Reviews auto-generated workpapers
3. For each workpaper:
   - Approve (moves to approved status)
   - Request revision (with notes)
4. Reviews final audit report
5. Signs off on report with:
   - CPA license information
   - Digital signature
   - Review notes
   - Attestation

### 5. Finalization
1. System verifies all requirements met:
   - All workpapers approved
   - CPA sign-off received
   - Optional: Dual sign-off if required
2. Updates engagement status to "Finalized"
3. Notifies client that audit is complete
4. Makes final report available to client

## Compliance Rules Library

Pre-seeded with critical compliance rules:

### PCAOB
- AS 1215: Audit Documentation
- AS 2401: Consideration of Fraud
- AS 1105: Audit Evidence

### GAAP
- ASC 860: Transfers and Servicing
- ASC 820: Fair Value Measurement
- ASC 310: Receivables - Loan Impairment

### SEC Regulation AB
- Item 1100: General Disclosure
- Item 1111: Asset Pool Characteristics
- Item 1112: Delinquency and Loss Information
- Item 1113: Servicer Information

### AICPA
- AT-C Section 205: Examination Engagements
- AT-C Section 210: Review Engagements

### GAAS
- AU-C Section 500: Audit Evidence
- AU-C Section 315: Understanding Entity and Risk Assessment
- AU-C Section 540: Auditing Accounting Estimates

## Configuration

### Environment Variables

```bash
# Application
PORT=8011
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://atlas:atlas_secret@localhost:5432/atlas

# OpenAI API
OPENAI_API_KEY=sk-your-api-key-here
AI_MODEL_VERSION=gpt-4-turbo
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=4000

# Storage (S3/MinIO)
STORAGE_ENDPOINT=http://localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_BUCKET=reg-ab-audit

# Redis
REDIS_URL=redis://localhost:6379/0

# Feature Flags
ENABLE_AI_COMPLIANCE=true
ENABLE_AUTO_WORKPAPERS=true
ENABLE_AUTO_REPORTS=true
MIN_CONFIDENCE_THRESHOLD=0.7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173
```

## Deployment

### Docker Compose

```bash
# Start all services including reg-ab-audit
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f api-reg-ab-audit
```

### Standalone

```bash
cd services/reg-ab-audit

# Install dependencies
pip install -r requirements.txt

# Run database migrations
psql -U atlas -d atlas -f ../../db/migrations/0002_reg_ab_audit.sql

# Start service
uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload
```

## Frontend Integration

### Admin Portal

```typescript
// /frontend/src/app/admin/reg-ab-audit/page.tsx
import { RegABAuditSettings } from '@/components/admin/reg-ab-audit-settings';

// Use the settings component
<RegABAuditSettings organizationId={orgId} />
```

### Client Portal

```typescript
// /client-portal/src/pages/RegABAudit.tsx
// Pre-built page for CMBS deal submission and tracking
```

### API Client Configuration

```typescript
// Add to API configuration
const REG_AB_API_URL = process.env.NEXT_PUBLIC_REG_AB_API_URL || 'http://localhost:8011';
```

## Security

### Authentication
- JWT-based authentication via Authorization header
- Role-based access control (Partner, Manager, Senior, Staff, Client)

### Authorization
- Row-level security on sensitive tables
- Organization-scoped data access
- Feature flag enforcement

### Audit Trail
- Complete audit trail of all actions
- IP address and user agent tracking
- Change tracking (before/after states)

### Data Retention
- Configurable retention period (default 7 years per SEC requirements)
- Immutable storage with SHA-256 hashing
- WORM (Write Once Read Many) compliance

## AI Model Details

### Compliance Engine
- **Model**: GPT-4 Turbo
- **Temperature**: 0.2 (low for consistency)
- **Max Tokens**: 4000
- **Format**: JSON structured output
- **Confidence Threshold**: 0.7 (configurable)

### Prompt Engineering
- Detailed context with deal information
- Specific regulatory requirements
- Structured output format
- Expert system persona
- Evidence-based reasoning

### Quality Assurance
- Confidence scoring on all AI outputs
- Manual review flagging for low confidence
- CPA review required for all outputs
- Continuous improvement via feedback loop

## Monitoring & Observability

### Health Checks
```
GET /health
```

Returns service health status and version.

### Metrics
- Engagement processing time
- AI processing duration
- Compliance check pass/fail rates
- Workpaper generation success rate
- CPA review completion time

### Logging
- Structured logging with context
- Error tracking with stack traces
- API request/response logging
- Background task monitoring

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_compliance_engine.py
```

## Troubleshooting

### Common Issues

**Service won't start**
- Check DATABASE_URL is correct
- Ensure database migrations have run
- Verify OPENAI_API_KEY is set

**AI processing fails**
- Check OpenAI API key and quota
- Review API error logs
- Verify model version is available

**No workpapers generated**
- Check background task logs
- Verify auto_workpaper_generation is enabled
- Ensure compliance checks completed

**CPA can't sign off**
- Verify user has Partner or Manager role
- Check CPA license information is complete
- Ensure all workpapers are approved

## Future Enhancements

- [ ] Integration with document management systems
- [ ] Advanced analytics dashboard
- [ ] Machine learning for anomaly detection
- [ ] Multi-language support
- [ ] Mobile app for CPA review
- [ ] Automated regulatory updates
- [ ] Integration with third-party data sources
- [ ] Advanced collaboration features
- [ ] Custom workpaper templates
- [ ] Batch processing for large portfolios

## Support

For issues or questions:
1. Check this README
2. Review service logs
3. Check API documentation at `/docs`
4. Contact development team

## License

Proprietary - Aura Audit AI

## Version

1.0.0 - Initial Release
