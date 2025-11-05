# Aura Audit AI (Project Atlas)

> **Enterprise-grade, cloud-native audit platform for CPA firms**
>
> Production SaaS audit suite with PCAOB/AICPA/SEC compliance, human-in-the-loop governance, and UX parity with Thomson Reuters, CCH Axcess, and Caseware.

## 🎯 Overview

**Aura Audit AI** automates end-to-end audit engagements:
- **Ingest**: EDGAR filings, XBRL, client trial balances, PBC documents
- **Normalize**: Taxonomy-aware mapping to firm chart of accounts
- **Analyze**: Journal entry testing, ratio analysis, anomaly detection
- **Draft**: AI-powered disclosure notes with citations and confidence scores
- **Manage**: Cloud binder, workpapers, review notes, role-based workflows
- **Finalize**: QC gates, partner e-signature, immutable WORM storage (7-year retention)

### Key Differentiators
✅ **Human-in-the-loop**: No automated report issuance; partner approval required
✅ **Immutable audit trail**: WORM storage with SHA-256 hashing and lineage tracking
✅ **Compliance-first**: PCAOB AS 1000/1215, AICPA SAS 142/145, SEC 17 CFR 210.2-06
✅ **Enterprise connectors**: QuickBooks, NetSuite, Xero, Sage, SAP, Oracle, Workday, ADP
✅ **AI governance**: Citations, confidence scores, contradiction detection, model versioning

---

## 🚀 Quick Start

### Prerequisites
- Docker 24+ and Docker Compose v2
- Node.js 20+ (for frontend dev)
- Python 3.11+ (for backend dev)
- AWS or Azure account (for production deployment)

### Local Development

1. **Clone and setup environment**:
```bash
cd /home/user/Data-Norm-2
cp .env.example .env
# Edit .env with your credentials
```

2. **Start all services**:
```bash
docker compose up -d
```

This starts:
- **PostgreSQL 15** (port 5432) with pgvector extension
- **Redis** (port 6379) for caching/queues
- **MinIO** (port 9000) for S3-compatible object storage
- **Airflow** (port 8080) for orchestration
- **10 FastAPI services** (ports 8001-8010)
- **React frontend** (port 5173)

3. **Initialize database**:
```bash
docker compose exec db psql -U atlas -d atlas -f /docker-entrypoint-initdb.d/0001_init.sql
```

4. **Access applications**:
- **Frontend**: http://localhost:5173
- **API Gateway**: http://localhost:8000
- **Airflow**: http://localhost:8080 (admin/admin)
- **API Docs**: http://localhost:8000/docs

### Run Tests
```bash
# Unit tests
docker compose exec -T api-ingestion pytest /app/tests/unit -v

# Integration tests
docker compose exec -T api-ingestion pytest /app/tests/integration -v

# E2E tests
cd tests/e2e
npm install
npx playwright test
```

---

## 📐 Architecture

**Pattern**: Microservices + Event-driven + CQRS
**Stack**: FastAPI (Python 3.11), React 18, PostgreSQL 15, Airflow, Terraform

### Core Services (10)

| Service | Port | Purpose |
|---------|------|---------|
| `ingestion` | 8001 | EDGAR/XBRL fetching, PBC uploads |
| `normalize` | 8002 | Taxonomy mapping, COA alignment |
| `analytics` | 8003 | JE testing, ratios, anomalies |
| `llm` | 8004 | RAG inference, schema-constrained JSON |
| `engagement` | 8005 | Binder, workpapers, review notes |
| `disclosures` | 8006 | Note drafting with citations |
| `reporting` | 8007 | PDF assembly, e-signature |
| `qc` | 8008 | Policy gates, blocking checks |
| `identity` | 8009 | OIDC/SSO, RBAC, RLS |
| `connectors` | 8010 | ERP/payroll integrations |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for diagrams and flows.

---

## 🔒 Security & Compliance

### Standards Coverage
- **PCAOB**: AS 1000 (independence), AS 1215 (audit documentation)
- **AICPA**: SAS 142 (audit evidence), SAS 145 (risk assessment)
- **SEC**: 17 CFR 210.2-06 (7-year retention)

### Security Features
- **Authentication**: OIDC (Azure AD / Okta / Auth0)
- **Authorization**: RBAC + engagement-level RLS
- **Encryption**: TLS 1.3 in transit; AES-256 at rest (KMS)
- **Immutability**: S3 Object Lock (Compliance mode) or Azure Blob Legal Hold
- **Audit trail**: All actions logged with user/timestamp/source
- **Secrets**: Vault integration; no secrets in code

See [docs/SECURITY.md](docs/SECURITY.md) for STRIDE threat model.

---

## 📚 Documentation

- [Architecture Diagrams](docs/ARCHITECTURE.md) - System context, containers, sequences
- [Security & STRIDE](docs/SECURITY.md) - Threat model + mitigations
- [QA & QC](docs/QA-QC.md) - Test strategy, data quality, audit trail
- [UX Parity Matrix](docs/PARITY.md) - Benchmark comparison (TR, CCH, Caseware)
- [Figma Brief](docs/FIGMA-BRIEF.md) - Design system, IA, component library
- [API Reference](http://localhost:8000/docs) - OpenAPI/Swagger docs
- [ADRs](docs/adr/) - Architecture decision records

---

## 🚢 Production Deployment

See `infra/aws/` or `infra/azure/` for Terraform configurations.

```bash
cd infra/aws
terraform init
terraform plan -var-file=prod.tfvars
terraform apply -var-file=prod.tfvars
```

---

**Built with 🔍 by the Aura Audit AI team**
