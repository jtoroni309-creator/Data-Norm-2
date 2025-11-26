# Create requirements.txt for all 10 new AI services

$services = @(
    "ai-agent-builder",
    "ai-testing",
    "control-points-engine",
    "document-intelligence",
    "full-population-analysis",
    "gl-monitor",
    "predictive-failure",
    "risk-monitor",
    "sox-automation",
    "variance-intelligence"
)

$requirements = @"
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1

# Logging
loguru==0.7.2

# Machine Learning (for AI services)
scikit-learn==1.4.0
numpy==1.26.3
pandas==2.2.0
joblib==1.3.2

# Azure Storage
azure-storage-blob==12.19.0
azure-identity==1.15.0

# Utilities
python-multipart==0.0.6
python-dateutil==2.8.2
httpx==0.26.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
"@

foreach ($service in $services) {
    $path = "C:\Users\jtoroni\Data Norm\Data-Norm-2\services\$service\requirements.txt"
    Set-Content -Path $path -Value $requirements
    Write-Host "Created requirements.txt for $service"
}
