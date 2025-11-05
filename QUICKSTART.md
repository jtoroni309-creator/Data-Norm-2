# Aura Audit AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Docker 24+ and Docker Compose v2
- 8GB RAM minimum (16GB recommended)
- 20GB disk space

### Step 1: Clone & Configure

```bash
cd /home/user/Data-Norm-2
cp .env.example .env
```

Edit `.env` if needed (default values work for local dev).

### Step 2: Start All Services

```bash
docker compose up -d
```

This starts:
- PostgreSQL (with pgvector)
- Redis
- MinIO (S3-compatible storage)
- 10 FastAPI microservices
- Airflow
- React frontend

Wait ~60 seconds for all services to be healthy.

### Step 3: Initialize Database

```bash
docker compose exec db psql -U atlas -d atlas -f /docker-entrypoint-initdb.d/0001_init.sql
```

### Step 4: Access Applications

Open in your browser:

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8001/docs (Ingestion Service)
- **Airflow**: http://localhost:8080 (admin/admin)
- **MinIO Console**: http://localhost:9001 (minio/minio123)

### Step 5: Test the System

```bash
# Health check all services
for port in {8001..8010}; do
    echo "Service on port $port:"
    curl -s http://localhost:$port/health | jq
done

# Run unit tests
docker compose exec api-ingestion pytest /app/tests/unit -v

# Fetch sample EDGAR data (Apple Inc.)
curl "http://localhost:8001/edgar/company-facts?cik=320193&form=10-K" | jq
```

### Step 6: Explore Features

#### Import a Trial Balance

```bash
# Upload sample TB file
curl -X POST http://localhost:8001/trial-balance/import \
    -F "engagement_id=$(uuidgen)" \
    -F "file=@sample_tb.xlsx" \
    -F "period_end_date=2023-12-31"
```

#### Generate AI Disclosure

```bash
curl -X POST http://localhost:8006/disclosures/draft \
    -H "Content-Type: application/json" \
    -d '{
        "engagement_id": "'"$(uuidgen)"'",
        "section": "revenue_recognition"
    }' | jq
```

## 📚 Next Steps

- **Documentation**: See `docs/` for architecture, security, and compliance
- **OpenAPI Spec**: See `openapi/atlas.yaml` for complete API reference
- **Deployment**: See `infra/aws/` for Terraform production deployment

## 🐛 Troubleshooting

### Services won't start

```bash
# Check logs
docker compose logs -f

# Restart specific service
docker compose restart api-ingestion
```

### Database connection errors

```bash
# Verify database is ready
docker compose exec db pg_isready -U atlas

# Check database connection
docker compose exec db psql -U atlas -d atlas -c "\dt atlas.*"
```

### Port conflicts

If ports are already in use, edit `docker-compose.yml` to change port mappings.

## 🛑 Stop Everything

```bash
docker compose down

# With data cleanup
docker compose down -v
```

## 🚢 Production Deployment

For production deployment to AWS/Azure:

```bash
cd infra/aws
terraform init
terraform plan -var-file=prod.tfvars
terraform apply -var-file=prod.tfvars
```

See `docs/ARCHITECTURE.md` for detailed deployment guide.

---

**Need Help?** Open an issue or email support@aura-audit.ai
