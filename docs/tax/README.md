# Tax Preparation Engine - Documentation

## Overview

The Tax Preparation Engine is an AI-first tax preparation system integrated into the Aura Audit AI platform. It provides CPA firms with modern tools for tax return preparation, combining OCR document intake, intelligent computation, and quality review workflows.

## Architecture

### Services

The tax preparation engine consists of 4 microservices:

1. **tax-ocr-intake** (Port 8025)
   - Document upload and classification
   - OCR processing with GPT-4 Vision
   - Field extraction and confidence scoring
   - Review flag generation

2. **tax-engine** (Port 8026)
   - Tax computation for Form 1040 (V1)
   - Federal tax calculations (brackets, AMT, NIIT, SE tax, QBI)
   - Explainability graph generation
   - State tax modules (V2)

3. **tax-forms** (Port 8027)
   - IRS form schema management
   - PDF generation for filing packages
   - MeF XML generation for e-file
   - Validation layer

4. **tax-review** (Port 8028)
   - Review workbench backend
   - Variance detection vs prior year
   - Cross-form reconciliation
   - Anomaly detection with AI

### Data Model

#### Tax Data Schema (TDS)

The canonical representation of a tax return, stored as JSONB in PostgreSQL:

```json
{
  "taxReturnId": "UUID",
  "year": 2024,
  "filingStatus": "married_joint",
  "taxpayer": {
    "name": "John Doe",
    "ssnEnc": "ENCRYPTED",
    "dob": "1980-01-01"
  },
  "income": {
    "w2": [{
      "ein": "12-3456789",
      "wages": 75000.00,
      "withholdingFed": 8500.00,
      "sourceId": "doc:W2#1",
      "confidence": 0.997
    }],
    "1099Int": [],
    "1099B": []
  },
  "deductions": {
    "standard": 29200.00
  },
  "credits": {
    "childTaxCredit": 4000.00
  },
  "provenance": [{
    "field": "income.w2[0].wages",
    "docRef": "doc:W2#1@page1:box1",
    "ocrModel": "gpt-4-vision-preview",
    "mappingRule": "M-W2-Box1"
  }]
}
```

#### Database Tables

See `db/migrations/0003_tax_preparation.sql` for full schema.

Key tables:
- `tax_returns` - Main return entity with TDS
- `tax_documents` - Source documents (W-2, 1099s)
- `tax_document_pages` - OCR results per page
- `tax_extracted_fields` - Raw field extractions
- `tax_forms` - Generated IRS forms
- `tax_provenance` - Audit trail
- `tax_review_flags` - Issues for human review
- `tax_rules` - Tax rules catalog by year

### Workflow

#### End-to-End Tax Return Flow

```
1. Document Upload
   └─> tax-ocr-intake receives PDF packet

2. OCR & Classification
   └─> GPT-4 Vision classifies each page
   └─> Extracts fields with confidence scores
   └─> Maps to TDS with provenance

3. Review Low-Confidence Fields
   └─> tax-review generates flags for <0.98 confidence
   └─> CPA reviews in workbench, accepts/overrides

4. Tax Calculation
   └─> tax-engine computes federal tax
   └─> Applies 2024 rules (brackets, AMT, credits)
   └─> Builds explainability graph

5. Variance Check
   └─> tax-review compares vs prior year
   └─> Flags significant changes (>50% default)

6. Form Generation
   └─> tax-forms renders Form 1040 + schedules
   └─> Generates PDF filing package

7. E-file Validation
   └─> tax-forms validates against IRS business rules
   └─> Generates MeF XML

8. E-file Submission
   └─> (V2) Submit to IRS via MeF gateway
```

## API Documentation

### Tax OCR Intake

```bash
# Upload document
POST /v1/returns/{tax_return_id}/documents/upload
Content-Type: multipart/form-data
Body: file (PDF/TIFF/JPG/PNG)

# Trigger ingestion
POST /v1/documents/{document_id}/ingest

# Get extraction
GET /v1/documents/{document_id}/extraction
```

### Tax Engine

```bash
# Calculate tax
POST /v1/returns/{tax_return_id}/calculate

# Explain calculation
POST /v1/returns/{tax_return_id}/explain/1040.line24

# Get tax rules
GET /v1/rules/2024?jurisdiction=federal
```

### Tax Forms

```bash
# Generate forms
POST /v1/returns/{tax_return_id}/forms/generate
Body: {"form_codes": ["1040", "Schedule A", "Schedule D"]}

# Generate e-file XML
POST /v1/returns/{tax_return_id}/efile/generate

# Validate for e-file
POST /v1/returns/{tax_return_id}/efile/validate
```

### Tax Review

```bash
# Get review queue
GET /v1/review-queue?status=pending&severity=high

# Resolve review item
POST /v1/review-items/{item_id}/resolve
Body: {
  "action": "override",
  "override_value": "50000.00",
  "notes": "Confirmed with W-2"
}

# Run variance check
POST /v1/returns/{tax_return_id}/variance-check

# Run anomaly detection
POST /v1/returns/{tax_return_id}/anomaly-detection
```

## Configuration

### Feature Flags

Set in each service's environment:

- `FEATURE_TAX_OCR_V1` - Enable OCR features
- `FEATURE_AI_CLASSIFICATION` - Use AI for document classification
- `FEATURE_TAX_ENGINE_V1` - Enable tax calculations
- `FEATURE_1040_CALCULATION` - Enable Form 1040 calculations
- `FEATURE_STATE_TAX` - Enable state tax (V2)
- `FEATURE_VARIANCE_DETECTION` - Enable prior year comparison

### Environment Variables

Required for all services:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/atlas
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-secret-key
ENCRYPTION_KEY=fernet-encryption-key
```

Service-specific:

```bash
# tax-ocr-intake
LLM_SERVICE_URL=http://api-llm:8000
STORAGE_ENDPOINT=minio:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin

# tax-engine
TAX_YEAR_DEFAULT=2024

# tax-forms
STORAGE_BUCKET=tax-forms

# tax-review
VARIANCE_THRESHOLD_PCT=50.0
```

## Security

### PII Protection

- **Field-level encryption**: SSN/EIN encrypted with Fernet (AES-128)
- **Redaction**: PII automatically redacted from logs
- **Access control**: RBAC enforced on all endpoints
- **Audit logging**: Every access to PII logged with user/IP/timestamp

### RBAC Roles

- `partner` - Full access
- `manager` - Create/edit returns, assign staff
- `senior` - Create/edit assigned returns
- `staff` - Edit assigned returns only
- `qc_reviewer` - Review and approve returns

## Testing

### Unit Tests

```bash
# Run all tests
pytest services/tax-*/tests/ -v

# Run with coverage
pytest services/tax-*/tests/ --cov=app --cov-report=html
```

### Integration Tests

```bash
# End-to-end workflow
pytest tests/integration/test_tax_workflow.py -v
```

### Test Data

Sample documents available in `tests/fixtures/tax-documents/`:
- W-2 samples
- 1099-INT/DIV/B samples
- K-1 samples

## Deployment

### Docker Compose

Services are included in `docker-compose.yml`:

```bash
# Start all services
docker-compose up tax-ocr-intake tax-engine tax-forms tax-review

# Or start individually
docker-compose up tax-ocr-intake
```

### Kubernetes (Future)

Helm charts will be provided in `infra/helm/tax-preparation/`.

## Roadmap

### V1 (Current)
- ✅ Database schema
- ✅ Service skeletons
- ⏳ OCR pipeline implementation
- ⏳ Form 1040 calculation engine
- ⏳ Review workbench
- ⏳ PDF form generation

### V2 (Q2 2025)
- State tax modules (CA, NY, TX, FL priority)
- Corporate returns (1120, 1120-S)
- Partnership returns (1065)
- IRS e-file submission
- Amended returns (1040-X)

### V3 (Q3 2025)
- Multi-year trend analysis
- Tax planning ("what-if" scenarios)
- Mobile app for document capture
- Client self-service portal

## Support

### Documentation
- ADR-0001: Architecture context and decisions (`docs/tax/ADR-0001-context.md`)
- Database schema: `db/migrations/0003_tax_preparation.sql`
- API specs: OpenAPI available at each service's `/docs`

### Issues
Report issues at: https://github.com/jtoroni309-creator/Data-Norm-2/issues

### Contact
Engineering team: tax-prep-team@example.com
