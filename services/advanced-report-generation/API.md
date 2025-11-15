# Advanced Report Generation API Reference

Complete API documentation for the Advanced Report Generation Service.

## Base URL

```
http://localhost:8019
```

Production: `https://api.aura-audit.ai/report-generation`

## Authentication

All requests require an API key in the header:

```http
X-API-Key: your-api-key-here
```

## Rate Limits

- **Standard tier**: 100 requests/hour
- **Premium tier**: 1000 requests/hour
- **Enterprise tier**: Unlimited

## Response Format

All endpoints return JSON with the following structure:

### Success Response

```json
{
  "data": { ... },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid engagement_id format",
    "details": { ... }
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Endpoints

### 1. Generate Report

Generate an audit report using advanced AI techniques.

**Endpoint:** `POST /reports/generate`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `engagement_id` | string (UUID) | Yes | Engagement identifier |
| `report_type` | enum | No | Type of report (default: `audit_report`) |
| `entity_type` | enum | No | Entity type (default: `private_company`) |
| `framework` | string | No | Accounting framework (default: `GAAP`) |
| `generation_method` | enum | No | Generation method (default: `hybrid`) |
| `enable_constitutional_ai` | boolean | No | Enable constitutional AI (default: `true`) |
| `enable_multi_agent` | boolean | No | Enable multi-agent system (default: `true`) |
| `enable_self_consistency` | boolean | No | Enable self-consistency (default: `false`) |
| `self_consistency_samples` | integer | No | Number of samples for voting (default: `5`) |
| `template_id` | string (UUID) | No | Custom template ID |
| `additional_context` | object | No | Additional context for generation |

**Enums:**

- `report_type`: `audit_report`, `review_report`, `compilation_report`, `attestation_report`
- `entity_type`: `public_company`, `private_company`, `non_profit`, `government`
- `generation_method`: `constitutional_ai`, `multi_agent`, `self_consistency`, `hybrid`

**Example Request:**

```bash
curl -X POST http://localhost:8019/reports/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "engagement_id": "550e8400-e29b-41d4-a716-446655440000",
    "report_type": "audit_report",
    "entity_type": "private_company",
    "framework": "GAAP",
    "generation_method": "hybrid",
    "enable_constitutional_ai": true,
    "enable_multi_agent": true
  }'
```

**Response:** `200 OK`

```json
{
  "report_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "status": "draft",
  "report_number": null,
  "report": {
    "title": "Independent Auditor's Report",
    "entity_name": "Acme Corporation",
    "report_date": "2024-12-31",
    "opinion_type": "unmodified",
    "sections": [
      {
        "name": "Opinion",
        "content": "In our opinion, the financial statements present fairly, in all material respects, the financial position of Acme Corporation as of December 31, 2024...",
        "citations": ["AS 3101.08", "AU-C 700.15"]
      },
      {
        "name": "Basis for Opinion",
        "content": "We conducted our audit in accordance with the standards of the Public Company Accounting Oversight Board (United States)...",
        "citations": ["AS 3101.11", "AS 2101"]
      }
    ],
    "signature": "Smith & Associates, LLP\nCertified Public Accountants\nJanuary 15, 2025"
  },
  "compliance_score": 0.985,
  "compliance_validated": true,
  "violations": [],
  "generation_time_seconds": 45,
  "tokens_used": 12500,
  "agents_used": ["opinion", "basis", "compliance", "editor"],
  "pdf_url": null,
  "docx_url": null
}
```

---

### 2. Get Report

Retrieve a generated report by ID.

**Endpoint:** `GET /reports/{report_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `report_id` | string (UUID) | Report identifier |

**Example Request:**

```bash
curl -X GET http://localhost:8019/reports/7c9e6679-7425-40de-944b-e07fc1f90ae7 \
  -H "X-API-Key: your-api-key"
```

**Response:** `200 OK`

```json
{
  "report_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "engagement_id": "550e8400-e29b-41d4-a716-446655440000",
  "report_type": "audit_report",
  "entity_name": "Acme Corporation",
  "report_date": "2024-12-31",
  "opinion_type": "unmodified",
  "status": "draft",
  "compliance_score": 0.985,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 3. Approve Report

Approve a report for issuance.

**Endpoint:** `PUT /reports/{report_id}/approve`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `approved_by` | string (UUID) | Yes | User ID of approver |

**Example Request:**

```bash
curl -X PUT http://localhost:8019/reports/7c9e6679-7425-40de-944b-e07fc1f90ae7/approve \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "approved_by": "partner_user_id"
  }'
```

**Response:** `200 OK`

```json
{
  "message": "Report approved",
  "report_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```

---

### 4. Issue Report

Issue (finalize) an approved report. Generates report number.

**Endpoint:** `PUT /reports/{report_id}/issue`

**Example Request:**

```bash
curl -X PUT http://localhost:8019/reports/7c9e6679-7425-40de-944b-e07fc1f90ae7/issue \
  -H "X-API-Key: your-api-key"
```

**Response:** `200 OK`

```json
{
  "message": "Report issued",
  "report_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "report_number": "AR-20240115-A3B2C1D4"
}
```

---

### 5. Validate Compliance

Validate report against 500+ regulatory compliance rules.

**Endpoint:** `POST /compliance/validate`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `report_id` | string (UUID) | Yes | Report identifier |
| `validation_type` | enum | No | Validation type (default: `hybrid`) |
| `fix_violations` | boolean | No | Auto-fix violations (default: `false`) |

**Validation Types:**
- `automated`: Rule-based validation only
- `neural`: GPT-4 based validation only
- `hybrid`: Both automated + neural (recommended)

**Example Request:**

```bash
curl -X POST http://localhost:8019/compliance/validate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "report_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "validation_type": "hybrid",
    "fix_violations": false
  }'
```

**Response:** `200 OK`

```json
{
  "validation_id": "9f8e7d6c-5b4a-3210-cdef-1234567890ab",
  "report_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "compliant": true,
  "compliance_score": 0.985,
  "total_violations": 2,
  "critical_violations": 0,
  "high_violations": 0,
  "medium_violations": 2,
  "low_violations": 0,
  "violations": [
    {
      "rule_id": "AS3101_015",
      "severity": "MEDIUM",
      "section": "Basis for Opinion",
      "message": "Audit scope description could be more specific",
      "suggestion": "Include reference to PCAOB standards paragraph 11",
      "regulatory_source": "PCAOB AS 3101.11"
    },
    {
      "rule_id": "AS2415_002",
      "severity": "MEDIUM",
      "section": "Opinion",
      "message": "Consider adding going concern emphasis",
      "suggestion": "Add emphasis-of-matter paragraph if substantial doubt exists",
      "regulatory_source": "PCAOB AS 2415.05"
    }
  ],
  "recommendations": [
    "Add more specific audit scope description referencing PCAOB standards",
    "Consider adding emphasis-of-matter paragraph for going concern if applicable"
  ],
  "validation_duration_seconds": 8
}
```

---

### 6. Get Compliance Rules

Get all 500+ compliance rules.

**Endpoint:** `GET /compliance/rules`

**Example Request:**

```bash
curl -X GET http://localhost:8019/compliance/rules \
  -H "X-API-Key: your-api-key"
```

**Response:** `200 OK`

```json
{
  "total_rules": 523,
  "rules": [
    {
      "rule_id": "AS3101_001",
      "name": "Title must include 'Independent'",
      "severity": "CRITICAL",
      "source": "PCAOB AS 3101.05"
    },
    {
      "rule_id": "AS3101_002",
      "name": "Report must be addressed to shareholders",
      "severity": "HIGH",
      "source": "PCAOB AS 3101.06"
    }
  ]
}
```

---

### 7. Validate Citations

Validate all citations in a report.

**Endpoint:** `POST /citations/validate`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `report_id` | string (UUID) | Yes | Report identifier |

**Example Request:**

```bash
curl -X POST http://localhost:8019/citations/validate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "report_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
  }'
```

**Response:** `200 OK`

```json
{
  "report_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "total_citations": 15,
  "valid_citations": 14,
  "invalid_citations": 0,
  "superseded_citations": 1,
  "citations": [
    {
      "citation_text": "[AS 3101.08]",
      "citation_type": "pcaob_standard",
      "section": "Opinion",
      "valid": true,
      "current": true,
      "superseded_by": null
    },
    {
      "citation_text": "[AS 2110]",
      "citation_type": "pcaob_standard",
      "section": "Basis",
      "valid": true,
      "current": false,
      "superseded_by": "AS 2110 (Revised 2023)"
    }
  ],
  "issues": [
    "Citation [AS 2110] is superseded by [AS 2110 (Revised 2023)]"
  ]
}
```

---

### 8. Create Template

Create a new report template.

**Endpoint:** `POST /templates`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template_name` | string | Yes | Template name |
| `template_type` | enum | Yes | Report type |
| `entity_type` | enum | Yes | Entity type |
| `framework` | string | No | Accounting framework (default: `GAAP`) |
| `sections` | array | Yes | Template sections |
| `constitutional_principles` | array | Yes | AI principles |
| `applicable_standards` | array | Yes | Regulatory standards |

**Example Request:**

```bash
curl -X POST http://localhost:8019/templates \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "template_name": "Standard Private Company Audit",
    "template_type": "audit_report",
    "entity_type": "private_company",
    "framework": "GAAP",
    "sections": [
      {
        "name": "Opinion",
        "required": true,
        "principles": ["AS_3101_P1"]
      }
    ],
    "constitutional_principles": [
      {
        "principle_id": "AS_3101_P1",
        "principle_name": "Opinion must be clearly stated",
        "regulatory_source": "PCAOB AS 3101.08"
      }
    ],
    "applicable_standards": ["AS_3101", "AU-C_700"]
  }'
```

**Response:** `201 Created`

```json
{
  "template_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "template_name": "Standard Private Company Audit",
  "template_type": "audit_report",
  "entity_type": "private_company",
  "framework": "GAAP",
  "is_active": true,
  "version": "1.0",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 9. List Templates

List all available templates.

**Endpoint:** `GET /templates`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template_type` | enum | No | Filter by report type |
| `entity_type` | enum | No | Filter by entity type |

**Example Request:**

```bash
curl -X GET "http://localhost:8019/templates?template_type=audit_report&entity_type=private_company" \
  -H "X-API-Key: your-api-key"
```

**Response:** `200 OK`

```json
{
  "total": 5,
  "templates": [
    {
      "template_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "template_name": "Standard Private Company Audit",
      "template_type": "audit_report",
      "entity_type": "private_company",
      "framework": "GAAP",
      "version": "1.0",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### 10. Performance Metrics

Get performance metrics over time.

**Endpoint:** `GET /metrics/performance`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | date (YYYY-MM-DD) | No | Start date |
| `end_date` | date (YYYY-MM-DD) | No | End date |

**Example Request:**

```bash
curl -X GET "http://localhost:8019/metrics/performance?start_date=2024-01-01&end_date=2024-12-31" \
  -H "X-API-Key: your-api-key"
```

**Response:** `200 OK`

```json
{
  "metrics": [
    {
      "date": "2024-01-15",
      "total_reports": 45,
      "avg_compliance_score": 0.982,
      "avg_generation_time": 42,
      "issued_reports": 38
    }
  ]
}
```

---

### 11. Violation Metrics

Get top compliance violations.

**Endpoint:** `GET /metrics/violations`

**Example Request:**

```bash
curl -X GET http://localhost:8019/metrics/violations \
  -H "X-API-Key: your-api-key"
```

**Response:** `200 OK`

```json
{
  "top_violations": [
    {
      "rule_id": "AS3101_015",
      "rule_name": "Audit scope must be specific",
      "regulatory_source": "PCAOB AS 3101.11",
      "severity": "MEDIUM",
      "count": 23
    }
  ]
}
```

---

### 12. Health Check

Service health check.

**Endpoint:** `GET /health`

**Example Request:**

```bash
curl -X GET http://localhost:8019/health
```

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "service": "Advanced Report Generation",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| `INVALID_ENGAGEMENT_ID` | Invalid engagement ID format | Engagement ID must be valid UUID |
| `ENGAGEMENT_NOT_FOUND` | Engagement not found | Specified engagement does not exist |
| `REPORT_NOT_FOUND` | Report not found | Specified report does not exist |
| `TEMPLATE_NOT_FOUND` | Template not found | Specified template does not exist |
| `VALIDATION_ERROR` | Validation failed | Request validation failed |
| `GENERATION_FAILED` | Report generation failed | Report generation encountered an error |
| `COMPLIANCE_CHECK_FAILED` | Compliance validation failed | Compliance check encountered an error |
| `UNAUTHORIZED` | Unauthorized | Invalid or missing API key |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error | Unexpected server error |

---

## Webhooks

Configure webhooks to receive notifications for report events.

### Events

- `report.generated` - Report generation completed
- `report.approved` - Report approved
- `report.issued` - Report issued
- `compliance.validated` - Compliance validation completed
- `compliance.violation_detected` - Critical violation detected

### Webhook Payload

```json
{
  "event": "report.generated",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "report_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "engagement_id": "550e8400-e29b-41d4-a716-446655440000",
    "compliance_score": 0.985,
    "status": "draft"
  }
}
```

---

## SDK Examples

### Python

```python
from aura_report_gen import ReportGenerationClient

client = ReportGenerationClient(api_key="your-api-key")

# Generate report
report = await client.generate_report(
    engagement_id="550e8400-e29b-41d4-a716-446655440000",
    report_type="audit_report",
    generation_method="hybrid"
)

# Validate compliance
validation = await client.validate_compliance(
    report_id=report.report_id,
    validation_type="hybrid"
)

if validation.compliant:
    # Approve and issue
    await client.approve_report(report.report_id, approved_by="partner_id")
    result = await client.issue_report(report.report_id)
    print(f"Report issued: {result.report_number}")
```

### JavaScript/TypeScript

```typescript
import { ReportGenerationClient } from '@aura/report-generation';

const client = new ReportGenerationClient({ apiKey: 'your-api-key' });

// Generate report
const report = await client.generateReport({
  engagementId: '550e8400-e29b-41d4-a716-446655440000',
  reportType: 'audit_report',
  generationMethod: 'hybrid'
});

// Validate compliance
const validation = await client.validateCompliance({
  reportId: report.reportId,
  validationType: 'hybrid'
});

if (validation.compliant) {
  // Approve and issue
  await client.approveReport(report.reportId, { approvedBy: 'partner_id' });
  const result = await client.issueReport(report.reportId);
  console.log(`Report issued: ${result.reportNumber}`);
}
```

---

## Support

For API support:
- Email: api-support@aura-audit.ai
- Documentation: https://docs.aura-audit.ai
- Status Page: https://status.aura-audit.ai
