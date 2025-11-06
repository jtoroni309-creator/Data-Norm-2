# Reporting Service

The Reporting Service provides comprehensive report generation, PDF creation, and e-signature management for the Aura Audit AI platform.

## Features

### Core Capabilities
- **PDF Generation**: Convert HTML templates to professional PDF reports using ReportLab and WeasyPrint
- **Template Management**: Create, manage, and version report templates with Jinja2 templating
- **E-Signature Integration**: DocuSign integration for electronic signatures
- **WORM Storage**: Immutable storage for final reports (7-year audit compliance)
- **Watermarking**: Automatic watermarking for draft reports
- **Cloud Storage**: Support for S3, MinIO, and Azure Blob Storage

### Report Types
- Audit Reports
- Financial Statements
- Management Letters
- Internal Control Reports
- Workpaper Summaries
- Analytics Summaries
- QC Review Reports
- Custom Reports

### E-Signature Features
- Multiple signers with routing order
- Embedded signing within application
- Envelope status tracking
- Automatic signed document retrieval
- DocuSign certificate of completion

## Architecture

### Technology Stack
- **FastAPI**: Async web framework
- **ReportLab**: Low-level PDF generation
- **WeasyPrint**: HTML to PDF conversion
- **Jinja2**: Template rendering
- **DocuSign**: E-signature integration
- **PostgreSQL**: Database for metadata
- **S3/Azure Blob**: Cloud storage for PDFs

### Database Models

#### ReportTemplate
Stores reusable report templates:
- Template content (HTML/CSS)
- Jinja2 template variables
- Header/footer templates
- Configuration (page size, margins)
- Version control

#### Report
Generated report instances:
- Report data and metadata
- Generation status
- File location (S3/Azure)
- WORM storage path (for finalized reports)
- Version history
- Approval workflow

#### SignatureEnvelope
E-signature tracking:
- DocuSign envelope ID
- Signer information
- Status tracking
- Signed document location

#### ReportSchedule
Automated report generation:
- Cron-based scheduling
- Template configuration
- Notification settings

## API Endpoints

### Report Templates

```
POST   /templates                Create template
GET    /templates                List templates
GET    /templates/{id}           Get template
PATCH  /templates/{id}           Update template
DELETE /templates/{id}           Delete template
```

### Reports

```
POST   /reports                  Create report
GET    /reports                  List reports
GET    /reports/{id}             Get report
POST   /reports/generate         Generate PDF
GET    /reports/{id}/download    Download PDF
POST   /reports/{id}/finalize    Finalize to WORM storage
```

### E-Signatures

```
POST   /signatures               Create signature envelope
GET    /signatures/{id}          Get envelope status
```

### Statistics

```
GET    /stats                    Get reporting statistics
```

## Configuration

Environment variables (`.env`):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://atlas:password@db:5432/atlas

# Storage (S3/MinIO)
STORAGE_BACKEND=s3
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minio
S3_SECRET_KEY=minio123
S3_BUCKET=reports
S3_WORM_BUCKET=atlas-worm

# Or Azure Storage
STORAGE_BACKEND=azure
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER=reports
AZURE_WORM_CONTAINER=atlas-worm

# DocuSign
DOCUSIGN_INTEGRATION_KEY=...
DOCUSIGN_USER_ID=...
DOCUSIGN_ACCOUNT_ID=...
DOCUSIGN_BASE_PATH=https://demo.docusign.net/restapi

# PDF Settings
PDF_DPI=300
PDF_PAGE_SIZE=LETTER
PDF_COMPRESSION=true
WATERMARK_TEXT=CONFIDENTIAL
WATERMARK_ENABLED=true

# Compliance
REPORT_RETENTION_DAYS=2555  # 7 years
```

## Usage Examples

### Creating a Template

```python
import httpx

async with httpx.AsyncClient() as client:
    template = {
        "name": "Annual Audit Report",
        "report_type": "audit_report",
        "template_type": "custom",
        "html_content": """
        <html>
        <head><title>{{ client_name }} - Audit Report</title></head>
        <body>
            <h1>{{ client_name }}</h1>
            <h2>Fiscal Year {{ fiscal_year }}</h2>
            <div>{{ opinion_section }}</div>
            <div>{{ financial_statements }}</div>
        </body>
        </html>
        """,
        "css_content": "body { font-family: Arial; font-size: 11pt; }"
    }

    response = await client.post("http://localhost:8000/templates", json=template)
    print(f"Created template: {response.json()['id']}")
```

### Generating a Report

```python
# 1. Create report
report = {
    "engagement_id": "...",
    "report_type": "audit_report",
    "title": "ABC Corp Annual Audit 2024",
    "template_id": "...",
    "report_data": {
        "client_name": "ABC Corporation",
        "fiscal_year": "2024",
        "opinion_section": "<p>In our opinion, the financial statements...</p>",
        "financial_statements": "<table>...</table>"
    },
    "fiscal_year": "2024",
    "has_watermark": True
}

response = await client.post("http://localhost:8000/reports", json=report)
report_id = response.json()["id"]

# 2. Generate PDF
generate_request = {
    "report_id": report_id,
    "regenerate": False
}

response = await client.post("http://localhost:8000/reports/generate", json=generate_request)
print(f"Generation status: {response.json()['status']}")

# 3. Download PDF (once generated)
response = await client.get(f"http://localhost:8000/reports/{report_id}/download")
with open("report.pdf", "wb") as f:
    f.write(response.content)
```

### Sending for E-Signature

```python
envelope = {
    "report_id": report_id,
    "subject": "Please sign the audit report",
    "message": "Please review and sign the attached audit report for fiscal year 2024.",
    "signers": [
        {
            "name": "Partner Name",
            "email": "partner@firm.com",
            "routing_order": 1,
            "role": "signer"
        },
        {
            "name": "Manager Name",
            "email": "manager@firm.com",
            "routing_order": 2,
            "role": "signer"
        }
    ],
    "expires_in_days": 30,
    "send_immediately": True
}

response = await client.post("http://localhost:8000/signatures", json=envelope)
envelope_id = response.json()["id"]
print(f"Envelope sent: {envelope_id}")
```

### Finalizing to WORM Storage

```python
# After report is approved, finalize to immutable storage
response = await client.post(f"http://localhost:8000/reports/{report_id}/finalize")

report = response.json()
print(f"WORM path: {report['worm_file_path']}")
print(f"Finalized at: {report['finalized_at']}")
```

## Performance

### Typical Response Times
- **Template Creation**: 50-100ms
- **Report Creation**: 50-100ms
- **PDF Generation**: 2-5 seconds (depends on complexity)
- **E-Signature Creation**: 1-2 seconds (DocuSign API)
- **Download**: 500ms-2s (depends on file size)

### Optimization Tips
- **Caching**: Templates are cached for faster rendering
- **Compression**: PDFs are compressed by default (20-40% size reduction)
- **Async**: Background tasks for PDF generation don't block API
- **Storage**: Use CDN/presigned URLs for faster downloads

## Testing

### Run Unit Tests
```bash
cd services/reporting
pytest tests/unit/ -v
```

### Run Integration Tests
```bash
pytest tests/integration/ -v
```

### Run All Tests with Coverage
```bash
pytest tests/ -v --cov=app --cov-report=html
```

## Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn app.main:app --reload --port 8000
```

### Docker
```bash
docker build -t aura-reporting-service .
docker run -p 8000:8000 --env-file .env aura-reporting-service
```

## Production Considerations

### WORM Storage
- Reports are automatically uploaded to WORM storage when finalized
- WORM storage has 7-year retention (audit compliance)
- Cannot be deleted or modified
- Verify compliance with regulatory requirements

### DocuSign Configuration
- Use production DocuSign account (not demo)
- Configure webhook for status updates
- Implement RSA key authentication (JWT)
- Monitor envelope quota limits

### Security
- Store DocuSign private key securely (Azure Key Vault/AWS Secrets Manager)
- Use signed URLs for downloads (don't expose direct storage paths)
- Validate all template HTML (prevent XSS)
- Implement rate limiting for PDF generation
- Enable encryption for PDF storage

### Monitoring
- Track PDF generation times
- Monitor storage usage
- Alert on failed generations
- Track DocuSign quota usage
- Monitor WORM storage compliance

### Scaling
- Use Redis for template caching
- Offload PDF generation to worker queue (Celery/Bull)
- Use CDN for PDF downloads
- Implement pagination for list endpoints
- Archive old reports to cold storage

## Troubleshooting

### PDF Generation Fails
```bash
# Check WeasyPrint dependencies
weasyprint --version

# Check template rendering
# Use /templates/{id} endpoint to verify HTML
```

### DocuSign Errors
```bash
# Verify credentials
echo $DOCUSIGN_INTEGRATION_KEY
echo $DOCUSIGN_ACCOUNT_ID

# Check API access
curl -X GET https://demo.docusign.net/restapi/v2.1/accounts/$DOCUSIGN_ACCOUNT_ID
```

### Storage Upload Fails
```bash
# S3/MinIO
aws s3 ls s3://$S3_BUCKET --endpoint-url $S3_ENDPOINT

# Azure
az storage container list --connection-string "$AZURE_STORAGE_CONNECTION_STRING"
```

### WORM Storage Issues
```bash
# Verify Object Lock is enabled (S3)
aws s3api get-object-lock-configuration --bucket $S3_WORM_BUCKET

# Verify immutability policy (Azure)
az storage container immutability-policy show --account-name ... --container-name atlas-worm
```

## License

Copyright © 2024 Aura Audit AI. All rights reserved.
