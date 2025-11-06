# Aura Audit AI - Architecture Documentation

**Version**: 2.0
**Last Updated**: November 6, 2025
**Status**: Production-Ready

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Microservices](#microservices)
4. [API Gateway](#api-gateway)
5. [Service Communication](#service-communication)
6. [Event Bus](#event-bus)
7. [Authentication & Authorization](#authentication--authorization)
8. [Database Architecture](#database-architecture)
9. [Frontend Applications](#frontend-applications)
10. [Security](#security)
11. [Deployment](#deployment)
12. [Development Guide](#development-guide)

---

## Overview

Aura Audit AI is an enterprise-grade audit platform built on a microservices architecture. The platform consists of **24 microservices**, **3 frontend applications**, and comprehensive infrastructure for CPA firm audit workflows.

### Key Features

- **AI-Powered Compliance**: Automated checking against PCAOB, GAAP, GAAS, SEC, and AICPA standards
- **Microservices Architecture**: 24 independent, scalable services
- **API Gateway**: Centralized request routing with rate limiting and circuit breaker
- **Event-Driven**: Redis-based event bus for service coordination
- **SOC 2 Compliant**: Enterprise-grade security with encryption, audit logging, and RLS
- **Multi-Tenant**: Row-level security with organization isolation

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐         │
│  │ Next.js App │  │ Admin Portal │  │ Client Portal │         │
│  └─────────────┘  └──────────────┘  └───────────────┘         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (Port 8000)                   │
│  • Request Routing      • Rate Limiting                          │
│  • Circuit Breaker      • Authentication Middleware              │
│  • Request/Response Logging                                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
┌────────────────┐  ┌────────────┐  ┌──────────────┐
│  24 Backend    │  │   Event    │  │  Service     │
│  Microservices │◄─┤    Bus     │  │  Registry    │
│                │  │  (Redis)   │  │              │
└────────┬───────┘  └────────────┘  └──────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                          │
│  ┌─────────────┐  ┌────────┐  ┌────────┐  ┌──────────┐        │
│  │ PostgreSQL  │  │ Redis  │  │ MinIO  │  │ Airflow  │        │
│  │ (pgvector)  │  │ Cache  │  │   S3   │  │  DAGs    │        │
│  └─────────────┘  └────────┘  └────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Microservices

### Core Services

| Port | Service | Purpose |
|------|---------|---------|
| 8000 | **API Gateway** | Request routing, rate limiting, circuit breaker |
| 8001 | **Ingestion** | EDGAR/XBRL/PBC data ingestion |
| 8002 | **Normalize** | Trial balance mapping (rules + ML) |
| 8003 | **Analytics** | JE testing, anomaly detection, ratios |
| 8004 | **LLM** | RAG retrieval, OpenAI chat, embeddings |
| 8005 | **Engagement** | Engagement CRUD, state machine, binder |
| 8006 | **Disclosures** | AI disclosure drafting |
| 8007 | **Reporting** | PDF generation, e-signature, WORM storage |
| 8008 | **QC** | Quality control gates, review workflows |
| 8009 | **Identity** | Authentication, JWT, RBAC, user management |
| 8010 | **Connectors** | ERP integrations (QBO, Xero, NetSuite) |
| 8011 | **Reg A/B Audit** | CMBS loan audits with AI compliance |

### Supporting Services

| Port | Service | Purpose |
|------|---------|---------|
| 8012 | **Audit Planning** | PCAOB AS 2110 risk assessment |
| 8013 | **Accounting Integrations** | QuickBooks/Xero OAuth flows |
| 8014 | **Data Anonymization** | PII redaction, data masking |
| 8015 | **Financial Analysis** | Financial metrics, KPIs, dashboards |
| 8016 | **Fraud Detection** | Anomaly detection, bank integration |
| 8017 | **Related Party** | Related party transaction tracking |
| 8018 | **Sampling** | Audit sampling strategies |
| 8019 | **Security** | SOC 2 compliance, encryption, key mgmt |
| 8020 | **Subsequent Events** | Post-balance-sheet events |
| 8021 | **Substantive Testing** | Detailed audit procedures |
| 8022 | **Training Data** | ML model training data management |
| 8023 | **E&O Insurance** | E&O insurance integration |
| 8024 | **Estimates Evaluation** | Valuation estimates review |

---

## API Gateway

### Features

- **Request Routing**: Routes requests to appropriate microservices based on path prefix
- **Rate Limiting**: Token bucket algorithm (120 requests/minute per client)
- **Circuit Breaker**: Automatic failure detection and recovery
- **Health Checks**: Aggregated health status of all services
- **Request Logging**: Comprehensive request/response logging

### Route Mapping

```yaml
/auth/*              → Identity Service (8009)
/ingestion/*         → Ingestion Service (8001)
/engagements/*       → Engagement Service (8005)
/analytics/*         → Analytics Service (8003)
/reports/*           → Reporting Service (8007)
# ... (see gateway/app/main.py for complete mapping)
```

### Usage

```bash
# All requests go through the gateway
curl http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "..."}'

# Gateway automatically routes to identity service
# Gateway handles rate limiting, circuit breaking, logging
```

### Monitoring

```bash
# Check gateway health
GET /health

# Check all services health
GET /health/services

# Get gateway metrics
GET /metrics
```

---

## Service Communication

### ServiceClient Library

All services use the `ServiceClient` library for inter-service communication.

**Location**: `lib/service_client/`

#### Features

- **Service Discovery**: Automatic service URL resolution
- **Circuit Breaker**: Fault tolerance with automatic recovery
- **Retry Logic**: Exponential backoff (3 attempts)
- **Authentication**: Automatic token propagation
- **Health Checks**: Service health monitoring

#### Usage Example

```python
from service_client import ServiceClient

# Initialize client for identity service
identity_client = ServiceClient(
    service_name="identity",
    timeout=10.0,
    auth_token=user_token
)

# Call identity service to validate token
try:
    user_data = await identity_client.get("/auth/me")
    print(f"User: {user_data['email']}")

except ServiceUnavailableError:
    # Service is down, circuit breaker open
    print("Identity service unavailable")

except ServiceTimeoutError:
    # Request timed out (will auto-retry)
    print("Request timed out")
```

#### Installation

Add to your service's `Dockerfile`:

```dockerfile
# Copy shared service client library
COPY ../../lib/service_client /tmp/service_client
RUN pip install --no-cache-dir /tmp/service_client
```

---

## Event Bus

### Overview

Redis Pub/Sub based event system for asynchronous service coordination.

**Location**: `lib/event_bus/`

### Event Flow

```
Engagement Service          Event Bus (Redis)       Reporting Service
       │                          │                         │
       ├─ publish()               │                         │
       │  "engagement.finalized"  │                         │
       │─────────────────────────>│                         │
       │                          │                         │
       │                          ├─ broadcast              │
       │                          │─────────────────────────>│
       │                          │                         │
       │                          │    subscribe()          │
       │                          │    handle_event()       │
       │                          │    generate_report()    │
```

### Event Types

**Defined in**: `lib/event_bus/schemas.py`

- `EngagementCreatedEvent`: New engagement created
- `EngagementFinalizedEvent`: Engagement finalized, trigger report
- `TrialBalanceUploadedEvent`: TB uploaded, trigger normalization
- `AccountsMappedEvent`: Accounts mapped, trigger analytics
- `AnalyticsCompletedEvent`: Analytics done, trigger disclosures
- `ReportGeneratedEvent`: Report generated
- `UserInvitedEvent`: User invited, trigger email
- `QPCReviewRequestedEvent`: QC review requested

### Usage Example

#### Publishing Events

```python
from event_bus import get_event_bus, EngagementFinalizedEvent
from uuid import uuid4

# Get event bus instance
event_bus = await get_event_bus()

# Create event
event = EngagementFinalizedEvent(
    event_id=str(uuid4()),
    service="engagement",
    user_id=current_user_id,
    organization_id=org_id,
    engagement_id=engagement_id,
    finalized_by=current_user_id,
    report_required=True
)

# Publish to channel
await event_bus.publish("engagement.finalized", event)
```

#### Subscribing to Events

```python
from event_bus import get_event_bus, EngagementFinalizedEvent

# Event handler
async def handle_engagement_finalized(event: EngagementFinalizedEvent):
    logger.info(f"Engagement {event.engagement_id} finalized")

    # Generate report
    await generate_report(
        engagement_id=event.engagement_id,
        finalized_by=event.finalized_by
    )

# Subscribe to events
event_bus = await get_event_bus()
await event_bus.subscribe(
    "engagement.finalized",
    EngagementFinalizedEvent,
    handle_engagement_finalized
)

# Start listening (non-blocking)
await event_bus.start_listening()
```

### Features

- **Automatic Retry**: Failed events retry with exponential backoff
- **Dead Letter Queue**: Failed events after max retries go to DLQ
- **Event Persistence**: Events stored in Redis for audit trail (7 days)
- **Type Safety**: Pydantic schemas for all events

---

## Authentication & Authorization

### JWT Token Flow

```
Client                 API Gateway         Identity Service
  │                         │                      │
  ├─ POST /auth/login       │                      │
  │─────────────────────────>                      │
  │                         ├─ forward             │
  │                         │─────────────────────>│
  │                         │                      ├─ validate credentials
  │                         │                      ├─ generate JWT
  │                         │<─────────────────────┤
  │<─────────────────────────                      │
  │  {access_token: "..."}                         │
  │                                                 │
  ├─ GET /engagements                              │
  │  Authorization: Bearer <token>                 │
  │─────────────────────────>                      │
  │                         ├─ forward with token  │
  │                         │─────────────────────>│
  │                         │                      ├─ validate token
  │                         │                      ├─ return user info
  │                         │<─────────────────────┤
  │                         ├─ forward to          │
  │                         │   engagement service │
```

### JWT Secret Validation

**CRITICAL**: JWT secrets are validated on startup.

```python
# services/identity/app/config.py

@field_validator('JWT_SECRET')
def validate_jwt_secret(cls, v: str) -> str:
    """Validate JWT secret strength in production"""
    is_production = os.getenv("ENVIRONMENT") == "production"

    if is_production:
        # Forbidden secrets
        if v in ["dev-secret", "change-me"]:
            raise ValueError("Cannot use default JWT secret in production!")

        # Minimum length
        if len(v) < 32:
            raise ValueError("JWT secret must be 32+ characters")

    return v
```

**Generate secure secret**:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

### Role-Based Access Control (RBAC)

#### Roles

- `partner`: Full access, can invite, manage firm
- `manager`: Can create/edit engagements, invite staff
- `senior`: Can create/edit engagements, limited team
- `staff`: Can edit assigned engagements only
- `qc_reviewer`: Can review and approve
- `client_contact`: Limited access (upload PBC, view engagement)

#### Usage

```python
from fastapi import Depends
from services.identity.app.auth import get_current_user, require_role

@app.post("/engagements")
async def create_engagement(
    data: EngagementCreate,
    user: User = Depends(require_role([RoleEnum.PARTNER, RoleEnum.MANAGER]))
):
    # Only partners and managers can create engagements
    ...
```

---

## Database Architecture

### PostgreSQL with pgvector

**Connection**: `postgresql://atlas:atlas_secret@db:5432/atlas`

### Schema

- **Core**: organizations, users, engagements, engagement_team_members
- **Data**: filings, facts, chart_of_accounts, trial_balances, journal_entries
- **Reg A/B**: cmbs_deals, reg_ab_workpapers, compliance_checks, cpa_signoffs
- **Identity**: user_invitations, user_permissions, login_audit_logs

### Advanced Features

#### Row-Level Security (RLS)

```sql
-- Enable RLS on sensitive tables
ALTER TABLE engagements ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their organization's engagements
CREATE POLICY engagement_org_policy ON engagements
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
```

**Usage in code**:

```python
from services.engagement.app.database import set_rls_context

# Set RLS context before queries
await set_rls_context(db, user_id=current_user.id)

# Now all queries automatically filtered by organization
engagements = await db.execute(select(Engagement))
```

#### pgvector for Embeddings

```python
from services.llm.app.models import DocumentChunk

# Store embeddings
chunk = DocumentChunk(
    text="Accounting policies for revenue recognition...",
    embedding=openai_embedding,  # 1536-dim vector
    source="GAAP_ASC_606.pdf"
)

# Vector similarity search
query = """
SELECT * FROM document_chunks
ORDER BY embedding <-> :query_embedding
LIMIT 5
"""
results = await db.execute(query, {"query_embedding": query_embedding})
```

### Migrations

**Location**: `db/migrations/`

- `0001_init.sql`: Core schema
- `0002_reg_ab_audit.sql`: Regulation A/B audit

**Apply migrations**:

```bash
docker-compose up db  # Migrations run automatically on startup
```

---

## Frontend Applications

### 1. Main Frontend (Next.js)

**Location**: `frontend/`
**Port**: 5173
**Stack**: Next.js 14, React 18, TypeScript, Tailwind CSS

**Features**:
- Engagement management (CRUD)
- Analytics dashboard (JE tests, anomalies, ratios)
- Account mapping interface
- Quality control dashboard
- Report generation & download

### 2. Admin Portal (Vite + React)

**Location**: `admin-portal/`
**Port**: 3001
**Stack**: Vite, React, TypeScript, Tailwind

**Features**:
- Customer management
- License management
- Usage analytics & metrics
- Invoicing & billing
- Support tickets

### 3. Client Portal (Vite + React)

**Location**: `client-portal/`
**Port**: 3002
**Stack**: Vite, React, TypeScript

**Features**:
- Document uploads (PBC)
- Engagement status tracking
- Review notes collaboration
- Confirmation requests
- Report downloads

### API Client

All frontends use a centralized API client:

```typescript
// frontend/src/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000
});

// Automatic token injection
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Usage
const engagements = await api.engagements.list();
```

---

## Security

### Encryption

**Security Service** (Port 8019) provides:

- **Field Encryption**: AES-256-GCM with key rotation
- **Key Management**: Master key with derived keys per purpose
- **Audit Logging**: Encrypted audit trail with chain verification

```python
from services.security.app.encryption import EncryptionService

encryption = EncryptionService(master_key=os.getenv("MASTER_KEY"))

# Encrypt sensitive data
encrypted_ssn = encryption.encrypt_field(ssn, KeyPurpose.PII)

# Decrypt
ssn = encryption.decrypt_field(encrypted_ssn, KeyPurpose.PII)
```

### WORM Storage

**Reporting Service** uses MinIO Object Lock for immutable storage:

```python
# Store report with 7-year retention
await s3_client.put_object(
    Bucket="atlas-worm",
    Key=f"reports/{report_id}.pdf",
    Body=pdf_bytes,
    ObjectLockMode="GOVERNANCE",
    ObjectLockRetainUntilDate=datetime.utcnow() + timedelta(days=2555)  # 7 years
)
```

### Email Service

**Identity Service** supports multiple email providers:

- **SendGrid**: Production-ready, high deliverability
- **AWS SES**: Cost-effective, requires verification
- **SMTP**: Generic SMTP server support

**Configuration**:

```bash
# SendGrid
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxx

# AWS SES
EMAIL_PROVIDER=aws_ses
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# SMTP
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
```

---

## Deployment

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api-gateway

# Restart service
docker-compose restart api-analytics

# Scale service
docker-compose up -d --scale api-analytics=3

# Stop all
docker-compose down
```

### Environment Variables

**Critical**:

```bash
# .env file
ENVIRONMENT=production  # Enables strict validation

# JWT (MUST CHANGE FOR PRODUCTION)
JWT_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')

# Database
DATABASE_URL=postgresql://atlas:${DB_PASSWORD}@db:5432/atlas

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Email
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxx
EMAIL_FROM=noreply@yourdomain.com
```

### Health Checks

```bash
# Gateway health
curl http://localhost:8000/health

# All services health
curl http://localhost:8000/health/services | jq

# Individual service
curl http://localhost:8009/health  # Identity service
```

---

## Development Guide

### Setup

```bash
# Clone repository
git clone https://github.com/your-org/aura-audit-ai.git
cd aura-audit-ai

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Start infrastructure
docker-compose up -d db redis minio

# Start services (choose one)
docker-compose up -d api-gateway api-identity api-engagement

# OR start all services
docker-compose up -d
```

### Adding a New Service

1. **Create service directory**:

```bash
mkdir -p services/my-service/app
cd services/my-service
```

2. **Create FastAPI app**:

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(title="My Service")

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

3. **Add requirements.txt**:

```
fastapi==0.110.0
uvicorn[standard]==0.27.0
```

4. **Create Dockerfile**:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

5. **Add to docker-compose.yml**:

```yaml
api-my-service:
  build:
    context: ./services/my-service
  ports:
    - "8025:8000"
  depends_on:
    - db
    - redis
  networks:
    - atlas-network
```

6. **Add to API Gateway** (`services/gateway/app/main.py`):

```python
SERVICE_REGISTRY = {
    # ...
    "my-service": {"url": "http://api-my-service:8000", "health": "/health"},
}

ROUTE_MAP = {
    # ...
    "/my-service": "my-service",
}
```

### Testing

```bash
# Run tests for a service
cd services/identity
pytest tests/ -v --cov=app

# Run all tests
pytest services/*/tests/ -v

# Test coverage
pytest --cov=services --cov-report=html
```

### Code Quality

Pre-commit hooks automatically run:

- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Linting
- **Mypy**: Type checking
- **Bandit**: Security scanning

```bash
# Run manually
pre-commit run --all-files

# Format code
black services/
isort services/

# Type check
mypy services/identity/app/
```

---

## Best Practices

### 1. Service Communication

✅ **DO**: Use ServiceClient for inter-service calls

```python
from service_client import ServiceClient

client = ServiceClient("identity", auth_token=token)
user = await client.get("/auth/me")
```

❌ **DON'T**: Make direct HTTP calls

```python
# Bad - no retry, no circuit breaker
response = httpx.get("http://api-identity:8000/auth/me")
```

### 2. Event Publishing

✅ **DO**: Publish events for async coordination

```python
await event_bus.publish("engagement.finalized", event)
```

❌ **DON'T**: Use synchronous service calls for non-critical workflows

### 3. Authentication

✅ **DO**: Always validate JWT tokens via Identity service

```python
from services.identity.app.auth import get_current_user

@app.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    ...
```

❌ **DON'T**: Decode JWT manually without validation

### 4. Database

✅ **DO**: Use RLS for multi-tenant isolation

```python
await set_rls_context(db, user_id=current_user.id)
```

❌ **DON'T**: Filter by organization_id manually in every query

---

## Troubleshooting

### Gateway Returns 503

**Symptom**: `{"detail": "Service unavailable"}`

**Causes**:
1. Backend service is down
2. Circuit breaker is open

**Solution**:

```bash
# Check service health
curl http://localhost:8000/health/services

# Check service logs
docker-compose logs api-identity

# Restart service
docker-compose restart api-identity
```

### Events Not Being Processed

**Symptom**: Events published but handlers not executing

**Causes**:
1. Event bus not listening
2. Handler not registered
3. Redis connection issue

**Solution**:

```bash
# Check Redis
docker-compose logs redis
redis-cli ping

# Check event bus logs
# Ensure start_listening() was called

# Check DLQ for failed events
from event_bus import get_event_bus
event_bus = await get_event_bus()
dlq_messages = await event_bus.get_dlq_messages("engagement.finalized")
```

### JWT Token Invalid

**Symptom**: `401 Unauthorized`

**Causes**:
1. Token expired (8 hour TTL)
2. JWT secret changed
3. Token format invalid

**Solution**:

```python
# Decode token to inspect
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)  # Check expiration

# Refresh token
response = await api.auth.refreshToken()
```

---

## Support

- **Documentation**: `/docs` (this file)
- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Issues**: Create GitHub issue
- **Email**: support@aura-audit.ai

---

## License

Proprietary - Aura Audit AI © 2025
