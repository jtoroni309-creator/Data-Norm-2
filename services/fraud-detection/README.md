## Fraud Detection Service

AI-powered fraud detection with bank account integration and real-time transaction monitoring for the Aura Audit AI platform.

## Overview

The Fraud Detection service provides comprehensive fraud monitoring capabilities using advanced machine learning models, rule-based detection, and anomaly detection to identify suspicious financial transactions in real-time.

### Key Features

- **AI-Powered Detection**: Ensemble ML models (Random Forest, XGBoost, Isolation Forest)
- **Bank Integration**: Seamless connection to customer bank accounts via Plaid API
- **Real-Time Monitoring**: Continuous transaction analysis with instant alerts
- **Rule-Based Detection**: Configurable rules for velocity checks, thresholds, and patterns
- **Anomaly Detection**: Isolation Forest algorithm for detecting unusual patterns
- **Case Management**: Complete fraud case workflow from detection to resolution
- **Admin Controls**: Feature flags to enable/disable per customer
- **Comprehensive Alerts**: Email, SMS, and webhook notifications
- **Compliance**: Audit trail and reporting for regulatory requirements

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Admin Portal UI                           │
│                (Feature Flag Management)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│              Fraud Detection Service (FastAPI)               │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐│
│  │  Plaid API  │  │  ML Models  │  │  Rule Engine         ││
│  │ Integration │  │  - RF       │  │  - Velocity          ││
│  │             │  │  - XGBoost  │  │  - Thresholds        ││
│  │             │  │  - IsoForest│  │  - Patterns          ││
│  └─────────────┘  └─────────────┘  └──────────────────────┘│
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │          Transaction Analysis Pipeline                   ││
│  │  1. Feature Extraction                                   ││
│  │  2. ML Prediction                                        ││
│  │  3. Rule Checking                                        ││
│  │  4. Risk Scoring                                         ││
│  │  5. Alert Generation                                     ││
│  └─────────────────────────────────────────────────────────┘│
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                    PostgreSQL Database                        │
│  - Bank Accounts    - Transactions    - Fraud Cases          │
│  - Alerts           - Rules           - ML Models             │
│  - Feature Flags    - Patterns        - Activity Log         │
└───────────────────────────────────────────────────────────────┘
```

## ML Models

### Ensemble Architecture

The service uses an ensemble of three complementary models:

#### 1. Random Forest Classifier (35% weight)
- **Purpose**: Pattern-based fraud classification
- **Features**: 30+ transaction features
- **Strengths**: Handles non-linear relationships, robust to outliers
- **Training**: Supervised learning on labeled fraud data

#### 2. XGBoost Classifier (35% weight)
- **Purpose**: Gradient boosting for improved accuracy
- **Features**: Same 30+ transaction features
- **Strengths**: High performance, handles imbalanced data well
- **Training**: Boosted decision trees with fraud labels

#### 3. Isolation Forest (20% weight)
- **Purpose**: Anomaly detection for unknown fraud patterns
- **Method**: Unsupervised learning
- **Strengths**: Detects novel fraud patterns, no labeled data needed
- **Training**: Learns normal transaction behavior

#### 4. Rule-Based Scoring (10% weight)
- **Purpose**: Fallback and explainability
- **Method**: Heuristic rules based on fraud indicators
- **Strengths**: Transparent, interpretable, always available

### Feature Engineering

The system extracts 30+ features from each transaction:

**Amount Features**:
- Raw amount
- Log-transformed amount
- Round amount indicator
- Large amount flag
- Deviation from average

**Temporal Features**:
- Hour of day
- Day of week
- Weekend indicator
- Night time indicator

**Velocity Features**:
- Transaction count (1h, 24h, 7d)
- Total amount (24h)
- Average amount (7d)
- Unique merchants (24h)

**Geographic Features**:
- Foreign location indicator
- Location consistency
- Distance from previous transaction

**Merchant Features**:
- Merchant presence
- Merchant name length
- Category analysis
- Payment channel (online/in-store)

## API Reference

### Health Check

```http
GET /health
```

Returns service health status.

### Bank Account Management

#### Create Link Token (Step 1)
```http
POST /plaid/link-token
Content-Type: application/json

{
  "user_id": "uuid"
}
```

Returns Plaid Link token for frontend integration.

#### Exchange Public Token (Step 2)
```http
POST /plaid/exchange-token
Content-Type: application/json

{
  "public_token": "public-sandbox-xxx",
  "account_id": "account_id",
  "institution_id": "ins_123",
  "institution_name": "Chase",
  "customer_id": "uuid"
}
```

Exchanges public token for access token and creates bank account connection.

#### List Bank Accounts
```http
GET /bank-accounts?customer_id={uuid}&skip=0&limit=100
```

#### Get Bank Account
```http
GET /bank-accounts/{account_id}
```

#### Update Bank Account
```http
PATCH /bank-accounts/{account_id}
Content-Type: application/json

{
  "account_name": "Updated Name",
  "monitoring_enabled": true,
  "alert_threshold_amount": 10000.00
}
```

#### Sync Transactions
```http
POST /bank-accounts/{account_id}/sync
```

Manually trigger transaction synchronization.

### Transaction Management

#### List Transactions
```http
GET /transactions?customer_id={uuid}&flagged_only=false&min_fraud_score=0.5&start_date=2024-01-01&end_date=2024-12-31
```

Query Parameters:
- `customer_id`: Filter by customer (required)
- `bank_account_id`: Filter by account
- `flagged_only`: Show only flagged transactions
- `min_fraud_score`: Minimum fraud score (0.0-1.0)
- `start_date`: Start date (ISO format)
- `end_date`: End date (ISO format)
- `skip`: Pagination offset
- `limit`: Results per page

#### Get Transaction Analysis
```http
GET /transactions/{transaction_id}
```

Returns detailed fraud analysis including:
- Fraud score and risk level
- Model predictions
- Feature importance
- Triggered rules
- Recommendation

#### Batch Analysis
```http
POST /transactions/analyze-batch
Content-Type: application/json

{
  "transaction_ids": ["uuid1", "uuid2", "uuid3"],
  "force_reanalysis": false
}
```

Analyze multiple transactions in batch.

### Fraud Case Management

#### Create Case
```http
POST /fraud-cases?user_id={uuid}
Content-Type: application/json

{
  "customer_id": "uuid",
  "bank_account_id": "uuid",
  "transaction_id": "uuid",
  "title": "Suspicious Transaction",
  "description": "Large unusual transaction detected",
  "severity": "high",
  "fraud_type": "suspicious_transaction",
  "estimated_loss_amount": 5000.00
}
```

#### List Cases
```http
GET /fraud-cases?customer_id={uuid}&status=open&severity=high
```

#### Get Case
```http
GET /fraud-cases/{case_id}
```

#### Update Case
```http
PATCH /fraud-cases/{case_id}?user_id={uuid}
Content-Type: application/json

{
  "status": "investigating",
  "assigned_to": "user_uuid",
  "investigation_notes": "Investigation started",
  "severity": "critical"
}
```

#### Get Case Activities
```http
GET /fraud-cases/{case_id}/activities
```

#### Add Case Activity
```http
POST /fraud-cases/{case_id}/activities?user_id={uuid}
Content-Type: application/json

{
  "activity_type": "note_added",
  "description": "Contacted customer for verification",
  "details": {}
}
```

### Fraud Alerts

#### List Alerts
```http
GET /alerts?status=new&severity=critical&skip=0&limit=100
```

#### Update Alert
```http
PATCH /alerts/{alert_id}?user_id={uuid}
Content-Type: application/json

{
  "status": "acknowledged",
  "resolution_action": "False positive - customer verified"
}
```

### Feature Flags

#### Get Feature Flag
```http
GET /feature-flags/{customer_id}
```

#### Update Feature Flag
```http
PATCH /feature-flags/{customer_id}?user_id={uuid}
Content-Type: application/json

{
  "is_enabled": true,
  "real_time_monitoring": true,
  "ml_detection": true,
  "rule_based_detection": true,
  "anomaly_detection": true,
  "alert_email": true,
  "alert_sms": false,
  "alert_webhook": true,
  "webhook_url": "https://your-domain.com/webhook",
  "min_alert_severity": "medium",
  "auto_case_creation_threshold": 0.85,
  "daily_transaction_limit": 1000,
  "high_risk_amount_threshold": 5000.00
}
```

### Statistics

#### Get Statistics
```http
GET /statistics?customer_id={uuid}&start_date=2024-01-01&end_date=2024-12-31
```

Returns:
- Total transactions
- Flagged transactions
- Total cases
- Open/resolved cases
- Total alerts
- Average fraud score
- Total potential loss

#### Get Dashboard Metrics
```http
GET /dashboard
```

Returns real-time metrics for admin dashboard.

### Webhooks

#### Plaid Webhook
```http
POST /webhooks/plaid
Content-Type: application/json

{
  "webhook_type": "TRANSACTIONS",
  "webhook_code": "DEFAULT_UPDATE",
  "item_id": "item_123",
  "new_transactions": 5
}
```

Handles real-time updates from Plaid.

## Configuration

### Environment Variables

```bash
# Application
APP_NAME=Fraud Detection Service
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/aura_fraud_detection

# Redis
REDIS_URL=redis://redis:6379/3

# Plaid API
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENVIRONMENT=production  # sandbox, development, production
PLAID_WEBHOOK_URL=https://your-domain.com/webhooks/plaid

# Encryption
ENCRYPTION_KEY=your-32-byte-encryption-key

# Azure
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_STORAGE_CONTAINER=ml-models

# Fraud Detection
DEFAULT_FRAUD_THRESHOLD=0.75
HIGH_RISK_THRESHOLD=0.90
AUTO_CASE_CREATION_THRESHOLD=0.85
LARGE_TRANSACTION_AMOUNT=10000.00

# Velocity Limits
MAX_TRANSACTIONS_PER_HOUR=10
VELOCITY_CHECK_WINDOW_MINUTES=60

# Notifications
SENDGRID_API_KEY=your_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token

# Feature Flags
ENABLE_ML_MODELS=true
ENABLE_REAL_TIME_MONITORING=true
ENABLE_ANOMALY_DETECTION=true
```

## Deployment

### Docker

```bash
# Build image
docker build -t fraud-detection:latest .

# Run container
docker run -d \
  --name fraud-detection \
  -p 8000:8000 \
  --env-file .env \
  fraud-detection:latest
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fraud-detection
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: fraud-detection
        image: fraud-detection:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: 500m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## Fraud Detection Workflow

### 1. Bank Account Connection

```
User -> Plaid Link -> Exchange Token -> Bank Account Created -> Sync Begins
```

### 2. Transaction Monitoring

```
Plaid Webhook -> Transaction Sync -> Feature Extraction -> ML Prediction -> Risk Scoring -> Alert/Case Creation
```

### 3. Fraud Case Workflow

```
Detection -> Open Case -> Investigation -> Resolution -> Closure
    ↓           ↓              ↓              ↓            ↓
  Alert    Acknowledged   In Progress    Resolved    Closed
```

## Admin Portal Integration

The service is fully integrated with the Admin Portal for easy management:

### Customer Detail Page

Navigate to: **Admin Portal -> Customers -> [Customer] -> Fraud Detection Tab**

Features:
- **Enable/Disable Toggle**: Turn fraud detection on/off per customer
- **Statistics Dashboard**: Real-time fraud metrics
- **Detection Methods**: Configure ML, rules, anomaly detection
- **Alert Configuration**: Set up email, SMS, webhook alerts
- **Thresholds**: Customize sensitivity and limits

## Testing

### Run All Tests

```bash
pytest tests/ -v --cov=app
```

### Run Specific Test Categories

```bash
# ML fraud detector tests
pytest tests/test_ml_fraud_detector.py -v

# API integration tests
pytest tests/test_api.py -v
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Performance Considerations

### Transaction Analysis Speed

- **Single Transaction**: ~50-200ms
- **Batch (100 transactions)**: ~5-10 seconds
- **Real-time monitoring**: <100ms overhead

### Scaling

- **Database**: Connection pooling (20 connections, 40 max overflow)
- **Redis**: Caching for high-frequency lookups
- **Horizontal Scaling**: Stateless service, scale replicas as needed
- **Async Processing**: Background tasks for transaction sync

### Optimization Tips

1. **Enable Redis caching** for feature statistics
2. **Batch process** historical transactions during off-hours
3. **Tune ML model thresholds** based on false positive rate
4. **Use database indexes** on transaction_date, fraud_score, customer_id
5. **Configure appropriate alerting thresholds** to avoid noise

## Security

### Data Protection

- **Encryption at Rest**: All sensitive data encrypted in database
- **Encryption in Transit**: TLS 1.2+ for all API calls
- **Token Encryption**: Plaid access tokens encrypted with Fernet
- **Key Management**: Azure Key Vault for production secrets

### Access Control

- **JWT Authentication**: All endpoints require valid JWT
- **Customer Isolation**: Multi-tenant data isolation
- **Role-Based Access**: Admin-only feature flag management

### Compliance

- **PCI-DSS**: No card data stored, only transaction metadata
- **GDPR**: Data retention policies, right to deletion
- **SOC 2**: Audit trail for all fraud cases
- **Audit Logging**: Complete activity history

## Monitoring

### Health Checks

```bash
# Service health
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/health/db

# Redis connectivity
curl http://localhost:8000/health/redis
```

### Metrics

Key metrics to monitor:
- Transaction analysis rate (txn/sec)
- Fraud detection rate (%)
- False positive rate (%)
- Alert response time
- Case resolution time
- Model prediction latency

### Logging

Structured JSON logging with levels:
- **ERROR**: Critical failures
- **WARNING**: Degraded performance
- **INFO**: Normal operations
- **DEBUG**: Detailed debugging (development only)

## Troubleshooting

### Common Issues

#### Plaid Connection Fails

```bash
# Check environment
echo $PLAID_CLIENT_ID
echo $PLAID_ENVIRONMENT

# Verify credentials
curl -X POST https://sandbox.plaid.com/link/token/create \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": "'$PLAID_CLIENT_ID'",
    "secret": "'$PLAID_SECRET'"
  }'
```

#### ML Models Not Loading

```bash
# Check model storage connection
echo $AZURE_STORAGE_CONNECTION_STRING

# Verify models exist
az storage blob list \
  --container-name ml-models \
  --prefix fraud_detection/
```

#### High False Positive Rate

Adjust thresholds in feature flags:
- Increase `auto_case_creation_threshold` (0.85 → 0.90)
- Increase `high_risk_amount_threshold` ($5000 → $10000)
- Set `min_alert_severity` to "high" instead of "medium"

## Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/aura-audit-ai

# Install dependencies
cd services/fraud-detection
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Code Style

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint
flake8 app/ tests/

# Type check
mypy app/
```

## License

Copyright © 2024 Aura Audit AI. All rights reserved.

## Support

For issues or questions:
- GitHub Issues: https://github.com/your-org/aura-audit-ai/issues
- Email: support@auraaudit.ai
- Documentation: https://docs.auraaudit.ai/fraud-detection
