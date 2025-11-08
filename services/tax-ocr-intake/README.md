# Tax OCR Intake Service

AI-powered document intake and OCR for tax preparation.

## Features

- **Document Upload**: PDF, TIFF, JPG, PNG support
- **AI Classification**: GPT-4 Vision powered document type detection (W-2, 1099 variants, K-1, etc.)
- **OCR Processing**: Layout-aware OCR with confidence scoring
- **Field Extraction**: Structured extraction per document type
- **Review Queues**: Human-in-the-loop for low-confidence fields
- **Provenance Tracking**: Full audit trail from source document to TDS field

## Supported Document Types

- W-2 (Wage and Tax Statement)
- 1099-INT, 1099-DIV, 1099-B, 1099-R, 1099-MISC, 1099-NEC
- 1098 (Mortgage Interest)
- K-1 (Partnership, S-Corp, Trust/Estate)
- SSA-1099 (Social Security Benefits)
- 1095-A/B/C (Health Insurance)
- Brokerage statements
- Property tax statements
- Charitable receipts

## API Endpoints

### Document Upload
```bash
POST /v1/returns/{tax_return_id}/documents/upload
```

### Document Ingestion
```bash
POST /v1/documents/{document_id}/ingest
GET /v1/documents/{document_id}/ingest/status
```

### Field Extraction
```bash
GET /v1/documents/{document_id}/extraction
```

### Review Flags
```bash
GET /v1/returns/{tax_return_id}/review-flags
POST /v1/review-flags/{flag_id}/resolve
```

## Configuration

Environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `LLM_SERVICE_URL`: LLM service URL
- `STORAGE_ENDPOINT`: MinIO/S3 endpoint
- `STORAGE_ACCESS_KEY`: Storage access key
- `STORAGE_SECRET_KEY`: Storage secret key
- `FEATURE_TAX_OCR_V1`: Enable OCR features (default: true)
- `FEATURE_AUTO_ACCEPT_THRESHOLD`: Auto-accept threshold (default: 0.98)

## Running Locally

```bash
cd services/tax-ocr-intake
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8025
```

## Running with Docker

```bash
docker build -t tax-ocr-intake .
docker run -p 8025:8000 tax-ocr-intake
```

## Testing

```bash
pytest tests/ -v --cov=app
```
