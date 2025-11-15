# Azure AI/ML Training Environment - Setup Guide

Complete guide to setting up the CPA-level AI training environment on Azure.

## Prerequisites

### Required
- Azure subscription with Owner or Contributor role
- Azure OpenAI Service access (requires application approval from Microsoft)
- Python 3.11 or higher
- Terraform 1.5+
- Azure CLI 2.50+
- Docker (for local development)
- Git

### Recommended
- 16+ GB RAM for local development
- GPU for local model training (optional)
- Visual Studio Code with Python and Azure extensions

## Step 1: Azure Resource Deployment

### 1.1 Login to Azure

```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### 1.2 Deploy Infrastructure with Terraform

```bash
cd azure-ai-ml/deployment/terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Deploy infrastructure
terraform apply

# Save output values
terraform output > ../../.terraform-outputs.json
```

This will create:
- Azure Machine Learning Workspace
- Azure OpenAI Service
- Azure PostgreSQL Flexible Server
- Azure Storage Account
- Azure Cognitive Search
- Azure AI Document Intelligence
- Azure Key Vault
- Virtual Network (if network isolation enabled)

**Deployment time**: 30-45 minutes

### 1.3 Verify Deployment

```bash
# List resources
az resource list --resource-group rg-aura-ml-prod

# Verify ML workspace
az ml workspace show --name aura-ml-workspace --resource-group rg-aura-ml-prod
```

## Step 2: Configure Azure OpenAI

### 2.1 Deploy Models

Azure OpenAI models are deployed via Terraform, but verify:

```bash
# List deployments
az cognitiveservices account deployment list \
  --name oai-aura-ml-prod \
  --resource-group rg-aura-ml-prod
```

You should see:
- `gpt-4-turbo` (100 TPM capacity)
- `text-embedding-3-large` (50 TPM capacity)

### 2.2 Get API Keys

```bash
# Get OpenAI endpoint
az cognitiveservices account show \
  --name oai-aura-ml-prod \
  --resource-group rg-aura-ml-prod \
  --query "properties.endpoint" -o tsv

# Get API key
az cognitiveservices account keys list \
  --name oai-aura-ml-prod \
  --resource-group rg-aura-ml-prod \
  --query "key1" -o tsv
```

## Step 3: Configure PostgreSQL Database

### 3.1 Get Connection Details

```bash
# Get PostgreSQL host
az postgres flexible-server show \
  --resource-group rg-aura-ml-prod \
  --name psql-aura-ml-prod \
  --query "fullyQualifiedDomainName" -o tsv

# Get password from Key Vault
az keyvault secret show \
  --vault-name kv-aura-ml-prod \
  --name postgres-password \
  --query "value" -o tsv
```

### 3.2 Initialize Database

```bash
# Connect to database
psql "host=psql-aura-ml-prod.postgres.database.azure.com \
      port=5432 \
      dbname=aura_ml_training \
      user=auradmin \
      sslmode=require"

# Create extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

# Run migrations (if you have migration scripts)
# psql ... < database/migrations/001_comprehensive_ai_training_schema.sql
```

## Step 4: Python Environment Setup

### 4.1 Create Virtual Environment

```bash
cd azure-ai-ml

# Create venv
python3.11 -m venv venv

# Activate
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 4.2 Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import azure.ai.ml; print('Azure ML SDK installed successfully')"
python -c "import openai; print('OpenAI SDK installed successfully')"
```

### 4.3 Configure Environment Variables

```bash
# Copy example .env file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

Fill in all required values from Terraform outputs:

```ini
AZURE_SUBSCRIPTION_ID=<from terraform output>
AZURE_OPENAI_ENDPOINT=<from terraform output>
AZURE_OPENAI_API_KEY=<from az cognitiveservices>
AZURE_STORAGE_ACCOUNT_NAME=<from terraform output>
AZURE_POSTGRES_HOST=<from terraform output>
# ... etc
```

## Step 5: Verify Setup

### 5.1 Test Azure Connections

```bash
# Test script
python << EOF
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from config import settings

# Test ML workspace connection
credential = DefaultAzureCredential()
ml_client = MLClient(
    credential,
    settings.AZURE_SUBSCRIPTION_ID,
    settings.AZURE_RESOURCE_GROUP,
    settings.AZUREML_WORKSPACE_NAME,
)

print(f"✓ Connected to ML workspace: {ml_client.workspace_name}")

# Test OpenAI
import openai
openai.api_type = "azure"
openai.api_base = settings.AZURE_OPENAI_ENDPOINT
openai.api_key = settings.AZURE_OPENAI_API_KEY

response = openai.ChatCompletion.create(
    engine=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
    messages=[{"role": "user", "content": "Say 'OK' if you're working"}],
    max_tokens=5,
)
print(f"✓ Azure OpenAI response: {response.choices[0].message.content}")

print("\n✓ All Azure services configured successfully!")
EOF
```

### 5.2 Test Database Connection

```bash
python << EOF
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from config import settings

async def test_db():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        result = await conn.execute("SELECT version()")
        version = result.scalar()
        print(f"✓ PostgreSQL version: {version}")

asyncio.run(test_db())
EOF
```

## Step 6: Data Collection

### 6.1 Configure EDGAR Scraper

Edit `data-acquisition/edgar-scraper/edgar_scraper.py` if needed (default configuration should work).

### 6.2 Scrape Initial Dataset

**Warning**: This will take several days to scrape 500,000+ companies.

```bash
# Test with single company first
python data-acquisition/edgar-scraper/edgar_scraper.py \
  --ticker AAPL \
  --start-date 2020-01-01

# Verify output
ls -lh data/edgar/

# Scrape S&P 500 (takes ~2-3 days)
python data-acquisition/edgar-scraper/edgar_scraper.py \
  --sp500 \
  --start-date 2015-01-01

# Or scrape in batches
python data-acquisition/edgar-scraper/batch_scraper.py \
  --start-cik 0000000001 \
  --end-cik 0001000000 \
  --parallel 10
```

### 6.3 Upload to Azure Blob Storage

Data is automatically uploaded during scraping if Azure Storage is configured.

Verify:

```bash
az storage blob list \
  --account-name <your-storage-account> \
  --container-name edgar-filings \
  --num-results 10
```

## Step 7: Knowledge Base Setup

### 7.1 Load GAAP Standards

```bash
# Download GAAP codification (requires FASB subscription)
# Place files in knowledge-base/gaap-codification/

# Index in Azure Cognitive Search
python knowledge-base/index_gaap_standards.py
```

### 7.2 Load PCAOB Standards

```bash
# Download from PCAOB website
python knowledge-base/download_pcaob_standards.py

# Index
python knowledge-base/index_pcaob_standards.py
```

### 7.3 Verify Knowledge Base

```bash
# Test search
python knowledge-base/test_search.py --query "revenue recognition ASC 606"
```

## Step 8: Model Training

### 8.1 Train Audit Opinion Model

```bash
# Ensure training data is available
python training-pipelines/audit-opinion-model/prepare_training_data.py

# Start training (uses Azure ML compute)
python training-pipelines/audit-opinion-model/train_audit_opinion_model.py

# Monitor in Azure ML Studio
az ml job show --name <job-id> --web
```

**Training time**: 8-24 hours depending on compute tier

### 8.2 Train Other Models

```bash
# Disclosure model
python training-pipelines/disclosure-model/train.py

# Work paper model
python training-pipelines/workpaper-model/train.py

# Materiality model
python training-pipelines/materiality-model/train.py
```

## Step 9: Model Evaluation

### 9.1 Run CPA Benchmark Tests

```bash
cd evaluation/cpa-benchmark-tests

# Run comprehensive evaluation
python run_evaluation.py --model audit-opinion --test-set cpa_benchmark_10k.jsonl

# View results
cat results/evaluation_report.json
```

### 9.2 Human Expert Review

```bash
# Generate test cases for CPA review
python evaluation/human-evaluation/generate_test_cases.py --count 100

# Export for review
python evaluation/human-evaluation/export_for_review.py --output review_cases.xlsx

# After CPAs complete review, import results
python evaluation/human-evaluation/import_review_results.py --input completed_reviews.xlsx
```

## Step 10: Model Deployment

### 10.1 Register Model

```bash
# Models are auto-registered during training if they meet target accuracy
# Verify in Azure ML Model Registry

az ml model list --workspace-name aura-ml-workspace
```

### 10.2 Deploy to Endpoint

```bash
# Create managed online endpoint
az ml online-endpoint create --name audit-opinion-endpoint -f deployment/endpoints/audit-opinion.yml

# Deploy model
az ml online-deployment create --name production --endpoint audit-opinion-endpoint -f deployment/deployments/production.yml

# Test endpoint
az ml online-endpoint invoke --name audit-opinion-endpoint --request-file test_request.json
```

## Step 11: Integration with Main Platform

### 11.1 Configure API Gateway

The main Aura Audit platform (in `/services/`) should be configured to call the ML endpoints:

```python
# In services/engagement/app/config.py
ML_API_BASE_URL = "https://audit-opinion-endpoint.azureml.net"
ML_API_KEY = "<from Azure ML>"
```

### 11.2 Test Integration

```bash
# From main platform root
cd /home/user/Data-Norm-2

# Test ML integration
pytest tests/integration/test_ml_integration.py
```

## Monitoring and Maintenance

### Daily Tasks
```bash
# Check scraper status
python data-acquisition/edgar-scraper/check_status.py

# Monitor model performance
az ml job list --workspace-name aura-ml-workspace --query "[?status=='Running']"
```

### Weekly Tasks
```bash
# Retrain models with new data
python training-pipelines/retrain_all_models.py

# Review model drift
python monitoring/check_model_drift.py

# Update knowledge base
python knowledge-base/update_standards.py
```

### Monthly Tasks
```bash
# Full evaluation against CPA benchmarks
python evaluation/monthly_evaluation.py

# Generate performance report
python reporting/generate_monthly_report.py

# Review and update model registry
python mlops/cleanup_old_models.py
```

## Cost Optimization

### Estimated Monthly Costs

| Service | Configuration | Est. Cost |
|---------|--------------|-----------|
| Azure ML | 10x NC24s_v3 GPU (8hrs/day) | $20,000 |
| Azure OpenAI | 50M tokens/month | $15,000 |
| PostgreSQL | Business Critical 32 vCPU | $3,500 |
| Storage | 50 TB Premium | $2,500 |
| Cognitive Search | Standard, 5 replicas | $1,500 |
| **Total** | | **~$61,200/month** |

### Cost Reduction Tips

1. **Use Azure Spot VMs** for non-critical training (50-90% discount)
   ```bash
   # In training config
   compute.spot_instances = True
   compute.spot_max_price = 0.5  # $/hour
   ```

2. **Schedule Compute** - Shutdown during off-hours
   ```bash
   az ml compute update --name gpu-cluster --min-instances 0
   ```

3. **Cache OpenAI Responses** - Implement aggressive caching
   ```python
   # Already implemented in LLM service
   ENABLE_LLM_CACHE = True
   CACHE_TTL = 7200  # 2 hours
   ```

4. **Use Reserved Instances** - 30-60% savings for 1-3 year commitment

## Troubleshooting

### Issue: "OpenAI quota exceeded"
```bash
# Check quota
az cognitiveservices account list-usage \
  --name oai-aura-ml-prod \
  --resource-group rg-aura-ml-prod

# Increase quota (submit request to Microsoft)
az support tickets create ...
```

### Issue: "PostgreSQL connection timeout"
```bash
# Check network rules
az postgres flexible-server firewall-rule list \
  --resource-group rg-aura-ml-prod \
  --name psql-aura-ml-prod

# Add your IP
az postgres flexible-server firewall-rule create \
  --resource-group rg-aura-ml-prod \
  --name psql-aura-ml-prod \
  --rule-name AllowMyIP \
  --start-ip-address <your-ip> \
  --end-ip-address <your-ip>
```

### Issue: "Model training fails with OOM"
```bash
# Increase batch size / reduce model size
# Or use larger compute
az ml compute update --name gpu-cluster --size Standard_NC24s_v3
```

## Security Best Practices

1. **Rotate secrets every 90 days**
   ```bash
   python security/rotate_secrets.py
   ```

2. **Enable audit logging**
   ```bash
   az monitor diagnostic-settings create ...
   ```

3. **Use Managed Identities** instead of service principals
   ```python
   from azure.identity import ManagedIdentityCredential
   credential = ManagedIdentityCredential()
   ```

4. **Implement RBAC**
   ```bash
   az role assignment create \
     --assignee user@domain.com \
     --role "Machine Learning Data Scientist" \
     --scope /subscriptions/.../resourceGroups/rg-aura-ml-prod
   ```

## Support

- **Technical Issues**: ml-support@aura-audit.ai
- **CPA Expert Review**: cpa-review@aura-audit.ai
- **Azure Support**: Open ticket in Azure Portal
- **Documentation**: https://docs.azure.com/en-us/azure/machine-learning/

## Next Steps

After setup is complete:

1. ✓ Deploy infrastructure
2. ✓ Scrape initial dataset (500K+ companies)
3. ✓ Build knowledge base
4. ✓ Train models
5. ✓ Evaluate against CPA benchmarks
6. ✓ Deploy to production
7. → Monitor and iterate

For questions, refer to the main [README.md](README.md) or contact the ML team.
