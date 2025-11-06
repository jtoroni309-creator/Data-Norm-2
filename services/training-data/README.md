# Training Data Management Service

Securely manage non-public financial statements for AI model training with automatic anonymization and complete data lineage tracking.

## Features

### 🔐 Privacy-First Architecture
- **Automatic Anonymization**: All PII removed before training
- **Encrypted Storage**: Original statements encrypted at rest (AES-256-GCM)
- **Validation**: Every statement validated for remaining PII
- **Audit Trail**: Complete lineage from source to model

### 📊 Data Quality Management
- **Automatic Assessment**: Completeness, consistency, accuracy checks
- **Quality Scoring**: Excellent, Good, Fair, Poor ratings
- **Validation**: Balance sheet equations, ratio reasonableness
- **Approval Workflow**: Human review before training use

### 🎯 Training Dataset Preparation
- **Dataset Creation**: Combine approved statements into training sets
- **Filtering**: By date, quality, statement type, industry
- **Versioning**: Track dataset versions and changes
- **Model Tracking**: Link datasets to trained models

### 📈 Complete Data Lineage
- **Source Tracking**: Know where every statement came from
- **Usage Tracking**: Which models used which data
- **Quality Metrics**: Quality breakdown by dataset
- **Compliance Reporting**: Generate lineage reports on demand

## Installation

```bash
cd services/training-data
pip install -r requirements.txt
```

## Quick Start

### Initialize Services

```python
from services.data_anonymization.app import DataAnonymizationService
from services.training_data.app import (
    TrainingDataService,
    StatementType,
    DataSource,
    DataQuality
)
from services.security.app import EncryptionService, AuditLogService

# Initialize security
encryption_service = EncryptionService()
audit_log_service = AuditLogService(encryption_service)

# Initialize anonymization
anonymization_service = DataAnonymizationService(
    encryption_service=encryption_service,
    audit_log_service=audit_log_service
)

# Initialize training data management
training_data_service = TrainingDataService(
    anonymization_service=anonymization_service,
    encryption_service=encryption_service,
    audit_log_service=audit_log_service
)
```

### Ingest Financial Statement

```python
# Example: Balance sheet from client
balance_sheet = {
    # Company identifiers (will be anonymized)
    "company_name": "TechStartup LLC",
    "ein": "98-7654321",
    "contact_email": "cfo@techstartup.com",

    # Financial data (will be preserved)
    "fiscal_year": 2024,
    "total_assets": 15000000,
    "total_liabilities": 9000000,
    "total_equity": 6000000,
    "revenue": 25000000,
    "net_income": 1000000,
    "current_ratio": 1.6,
    "debt_to_equity": 1.5,
}

# Ingest with automatic anonymization
training_data_id = await training_data_service.ingest_financial_statement(
    statement_data=balance_sheet,
    statement_type=StatementType.BALANCE_SHEET,
    source=DataSource.CLIENT_UPLOAD,
    metadata={
        "industry": "technology",
        "company_size": "small",
        "fiscal_year": 2024
    },
    tenant_id=tenant_id,
    user_id=user_id
)

print(f"Ingested and anonymized: {training_data_id}")
# Output: Ingested and anonymized: 550e8400-e29b-41d4-a716-446655440000
```

### Check Quality Assessment

```python
# Access training data record
record = training_data_service._training_data[training_data_id]

# Review quality assessment
quality = record["quality_assessment"]
print(f"Quality: {quality['overall_quality']}")
# Output: Quality: excellent

print(f"Completeness: {quality['completeness_score']}")
# Output: Completeness: 0.95

# Review anonymization
print(f"PII Removed: {record['anonymization_validation']['pii_count']}")
# Output: PII Removed: 3
```

### Approve for Training

```python
# Admin/Data scientist approves
approved = await training_data_service.approve_for_training(
    training_data_id=training_data_id,
    approver_user_id=admin_user_id
)

if approved:
    print("✓ Approved for AI training")
```

### Create Training Dataset

```python
# Collect approved training data IDs
training_data_ids = [
    "550e8400-e29b-41d4-a716-446655440000",
    "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    # ... 998 more statements
]

# Create dataset
dataset_id = training_data_service.create_training_dataset(
    dataset_name="financial_statements_2024_q4",
    training_data_ids=training_data_ids,
    purpose="fraud_detection_model_training",
    creator_user_id=data_scientist_user_id,
    filters={
        "date_range": {"start": "2024-10-01", "end": "2024-12-31"},
        "quality": ["excellent", "good"]
    }
)

print(f"Dataset created: {dataset_id}")
# Output: Dataset created with 1000 anonymized statements
```

### Use for Model Training

```python
# Retrieve dataset
dataset = training_data_service.get_training_dataset(dataset_id)

# Access anonymized training data
training_statements = dataset['data']  # List of 1000 anonymized statements

# Extract features for ML (financial data only, no PII)
features = []
for statement in training_statements:
    features.append({
        'total_assets': statement['total_assets'],
        'total_liabilities': statement['total_liabilities'],
        'revenue': statement['revenue'],
        'net_income': statement['net_income'],
        'current_ratio': statement['current_ratio'],
        'debt_to_equity': statement['debt_to_equity'],
    })

# Train model
model = train_fraud_detection_model(features)

# Track model training
training_data_service.track_model_training(
    dataset_id=dataset_id,
    model_id="fraud_detector_v2.1",
    model_name="Financial Statement Fraud Detector",
    training_metadata={
        "epochs": 100,
        "accuracy": 0.94,
        "precision": 0.92
    }
)
```

### Generate Data Lineage Report

```python
# Generate complete lineage for a model
lineage = training_data_service.generate_data_lineage_report(
    model_id="fraud_detector_v2.1"
)

print(f"Model: {lineage['model_id']}")
print(f"Training Statements: {lineage['total_training_statements']}")
print(f"Sources: {lineage['sources_breakdown']}")
print(f"Quality: {lineage['quality_breakdown']}")

# Example output:
{
    "model_id": "fraud_detector_v2.1",
    "total_training_statements": 1000,
    "sources_breakdown": {
        "client_upload": 800,
        "manual_entry": 200
    },
    "quality_breakdown": {
        "excellent": 750,
        "good": 200,
        "fair": 50
    }
}
```

## Data Quality Levels

| Quality | Completeness | Consistency | Recommendation |
|---------|--------------|-------------|----------------|
| **Excellent** | ≥ 90% | No issues | ✅ Use for training |
| **Good** | ≥ 75% | Minor issues | ✅ Use for training |
| **Fair** | ≥ 50% | Some issues | ⚠️ Review first |
| **Poor** | < 50% | Major issues | ❌ Do not use |

## Statement Types

```python
from services.training_data.app import StatementType

StatementType.BALANCE_SHEET          # Assets, liabilities, equity
StatementType.INCOME_STATEMENT       # Revenue, expenses, net income
StatementType.CASH_FLOW              # Operating, investing, financing
StatementType.STATEMENT_OF_EQUITY    # Changes in equity
StatementType.NOTES                  # Notes to financial statements
StatementType.COMPLETE_PACKAGE       # Complete set
```

## Data Sources

```python
from services.training_data.app import DataSource

DataSource.CLIENT_UPLOAD      # Uploaded by clients
DataSource.MANUAL_ENTRY       # Manually entered
DataSource.API_IMPORT         # Imported via API
DataSource.BULK_IMPORT        # Bulk import
DataSource.PUBLIC_FILINGS     # SEC EDGAR, etc.
```

## Workflow

```
1. Ingest
   ↓
   • Validate structure
   • Encrypt original
   • Store securely

2. Anonymize
   ↓
   • Remove all PII
   • Validate anonymization
   • Preserve financial data

3. Assess Quality
   ↓
   • Check completeness
   • Verify consistency
   • Assign quality score

4. Approve
   ↓
   • Human review
   • Quality check
   • Approval by admin/data scientist

5. Create Dataset
   ↓
   • Combine approved statements
   • Apply filters
   • Version dataset

6. Train Model
   ↓
   • Use anonymized data only
   • Track lineage
   • Document performance

7. Report
   ↓
   • Generate lineage reports
   • Compliance documentation
   • Audit trail
```

## Privacy Guarantees

### What We Guarantee

✅ **No PII in Training Data**
- Every statement automatically anonymized
- Validation before training approval
- Manual review for high-risk data

✅ **Original Data Protected**
- Encrypted at rest (AES-256-GCM)
- Access-controlled
- Audit-logged

✅ **Complete Traceability**
- Know which statements trained which models
- Track data sources and quality
- Generate compliance reports

✅ **Reversibility Controlled**
- Only authorized users can de-anonymize
- Requires MFA
- Full audit trail

### What We Remove

- Company names, tax IDs
- Email addresses, phone numbers
- Personal names (officers, directors)
- Addresses, URLs
- Account numbers, customer IDs
- All other identifying information

### What We Preserve

- All financial amounts
- Financial ratios
- Time periods
- Industry classifications (anonymized)
- Transaction patterns
- Accounting relationships

## Statistics & Reporting

```python
# Get overall statistics
stats = training_data_service.get_statistics()

print(f"Total Statements: {stats['total_statements']}")
print(f"Approved: {stats['approved_for_training']}")
print(f"Datasets: {stats['total_datasets']}")
print(f"Status: {stats['status_breakdown']}")
print(f"Quality: {stats['quality_breakdown']}")
print(f"Sources: {stats['source_breakdown']}")
```

## Validation

### Balance Sheet Validation

```python
from services.training_data.app import FinancialStatementValidator

validator = FinancialStatementValidator()

# Validate balance sheet equation
errors = validator.validate_balance_sheet(balance_sheet)
if errors:
    print(f"Validation errors: {errors}")
else:
    print("✓ Balance sheet valid")
```

### Income Statement Validation

```python
errors = validator.validate_income_statement(income_statement)
if errors:
    print(f"Validation errors: {errors}")
else:
    print("✓ Income statement valid")
```

## Best Practices

### 1. Data Collection
- ✅ Obtain proper consent for AI training use
- ✅ Document data source and collection method
- ✅ Include diverse statements (industries, sizes, years)
- ✅ Mix normal and anomalous examples

### 2. Quality Control
- ✅ Set minimum quality standards
- ✅ Review "fair" quality data manually
- ✅ Document quality issues
- ✅ Don't approve "poor" quality data

### 3. Anonymization
- ✅ Always use full anonymization for training
- ✅ Validate every statement
- ✅ Review validation failures manually
- ✅ Re-anonymize if validation fails

### 4. Dataset Management
- ✅ Create separate datasets for different purposes
- ✅ Version datasets
- ✅ Document composition
- ✅ Track model usage

### 5. Compliance
- ✅ Maintain complete audit trail
- ✅ Regular privacy reviews
- ✅ Document retention policies
- ✅ Provide lineage on request

## Documentation

- **[Training Data Guide](TRAINING_DATA_GUIDE.md)**: Complete usage guide
- **[Data Privacy Guarantee](../data-anonymization/DATA_PRIVACY_GUARANTEE.md)**: Privacy documentation
- **[API Reference](docs/API.md)**: API documentation

## Testing

```bash
pytest tests/ -v --cov=app
```

## Support

- **Technical**: support@auraauditai.com
- **Privacy**: privacy@auraauditai.com
- **Documentation**: https://docs.auraauditai.com

## Version

**1.0.0** - 2025-01-06
