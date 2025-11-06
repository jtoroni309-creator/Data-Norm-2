# Training Data Management Guide

## Overview

This guide explains how to safely ingest, anonymize, and use non-public financial statements for AI model training while maintaining complete data privacy.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Data Ingestion](#data-ingestion)
3. [Anonymization Process](#anonymization-process)
4. [Data Quality Assessment](#data-quality-assessment)
5. [Training Dataset Creation](#training-dataset-creation)
6. [Model Training Integration](#model-training-integration)
7. [Data Lineage Tracking](#data-lineage-tracking)
8. [Best Practices](#best-practices)

---

## Quick Start

### Installation

```bash
cd services/data-anonymization
pip install -r requirements.txt

cd ../training-data
pip install -r requirements.txt
```

### Initialize Services

```python
from services.data_anonymization.app import DataAnonymizationService, AnonymizationLevel
from services.training_data.app import TrainingDataService, StatementType, DataSource
from services.security.app import EncryptionService, AuditLogService

# Initialize security services
encryption_service = EncryptionService()
audit_log_service = AuditLogService(encryption_service)

# Initialize anonymization
anonymization_service = DataAnonymizationService(
    encryption_service=encryption_service,
    audit_log_service=audit_log_service,
    tokenization_secret="your_secret_key_from_env"
)

# Initialize training data management
training_data_service = TrainingDataService(
    anonymization_service=anonymization_service,
    encryption_service=encryption_service,
    audit_log_service=audit_log_service
)
```

---

## Data Ingestion

### Step 1: Prepare Financial Statement

```python
# Example: Balance sheet from client
balance_sheet = {
    # Company identifiers (will be removed)
    "company_name": "TechStartup LLC",
    "ein": "98-7654321",
    "address": "456 Innovation Dr, Austin, TX 78701",
    "contact_email": "cfo@techstartup.com",
    "website": "https://www.techstartup.com",
    "ceo_name": "Alice Johnson",
    "cfo_name": "Bob Williams",

    # Financial data (will be preserved)
    "fiscal_year": 2024,
    "reporting_period": "2024-12-31",
    "total_assets": 15000000,
    "current_assets": 8000000,
    "cash": 3000000,
    "accounts_receivable": 2500000,
    "inventory": 2500000,
    "total_liabilities": 9000000,
    "current_liabilities": 5000000,
    "accounts_payable": 2000000,
    "short_term_debt": 3000000,
    "long_term_debt": 4000000,
    "total_equity": 6000000,
    "common_stock": 5000000,
    "retained_earnings": 1000000,

    # Financial ratios
    "current_ratio": 1.6,
    "debt_to_equity": 1.5,
    "return_on_assets": 0.033,
    "return_on_equity": 0.083,
}
```

### Step 2: Ingest with Automatic Anonymization

```python
# Ingest financial statement
training_data_id = await training_data_service.ingest_financial_statement(
    statement_data=balance_sheet,
    statement_type=StatementType.BALANCE_SHEET,
    source=DataSource.CLIENT_UPLOAD,
    metadata={
        "industry": "technology",
        "company_size": "small",
        "fiscal_year": 2024,
        "notes": "Client provided for AI improvement"
    },
    tenant_id=tenant_id,
    user_id=user_id
)

print(f"Training data ingested: {training_data_id}")
print(f"Status: Automatically anonymized and validated")
```

**What Happens:**
1. Original statement encrypted and stored securely
2. Statement automatically anonymized
3. Anonymization validated (no PII remains)
4. Data quality assessed
5. Training data record created

---

## Anonymization Process

### Anonymization Levels

```python
from services.data_anonymization.app import AnonymizationLevel

# FULL anonymization (recommended for AI training)
anonymized = anonymization_service.anonymize_financial_statement(
    statement=balance_sheet,
    level=AnonymizationLevel.FULL,
    tenant_id=tenant_id,
    user_id=user_id
)

# Result:
{
    "company_name": "[COMPANY_NAME_a3f9d2b1]",
    "ein": "[TAX_ID_c4a7b3e1]",
    "address": "[ADDRESS_f7e2d9a4]",
    "contact_email": "[EMAIL_b8d3f1c6]",
    "website": "[URL_d1f5b8e3]",
    "ceo_name": "[PERSON_NAME_c7d9e2a5]",
    "cfo_name": "[PERSON_NAME_f3a8d1c4]",

    # Financial data unchanged
    "total_assets": 15000000,
    "total_liabilities": 9000000,
    # ... all financial data preserved

    "_anonymization": {
        "level": "full",
        "anonymized_at": "2025-01-06T12:00:00Z",
        "pii_types_removed": ["company_name", "tax_id", "email", "url", "address", "person_name"],
        "pii_count": 7
    }
}
```

### Validate Anonymization

```python
# Validate no PII remains
validation_result = anonymization_service.validate_anonymization(anonymized)

if validation_result["is_valid"]:
    print("✓ Anonymization successful - no PII detected")
else:
    print(f"✗ Issues found: {validation_result['issues']}")
    # Do not use for training
```

---

## Data Quality Assessment

### Automatic Quality Assessment

Every ingested statement is automatically assessed:

```python
# Quality assessment is done automatically during ingestion
# Access it from the training data record

training_record = training_data_service._training_data[training_data_id]
quality = training_record["quality_assessment"]

print(f"Overall Quality: {quality['overall_quality']}")
# Output: "excellent", "good", "fair", or "poor"

print(f"Completeness: {quality['completeness_score']}")
# Output: 0.0 to 1.0 (percentage of fields populated)

print(f"Consistency Issues: {quality['consistency_issues']}")
# Output: List of any mathematical inconsistencies
```

### Quality Criteria

| Quality Level | Completeness | Consistency | Use for Training |
|--------------|--------------|-------------|------------------|
| **Excellent** | ≥ 90% | No issues | ✓ Recommended |
| **Good** | ≥ 75% | Minor issues | ✓ Acceptable |
| **Fair** | ≥ 50% | Some issues | ⚠️ Review first |
| **Poor** | < 50% | Major issues | ✗ Do not use |

---

## Training Dataset Creation

### Step 1: Approve Training Data

Before using data for training, it must be approved:

```python
# Admin/Data scientist approves data
approved = await training_data_service.approve_for_training(
    training_data_id=training_data_id,
    approver_user_id=admin_user_id
)

if approved:
    print("✓ Training data approved")
else:
    print("✗ Approval failed (quality too low or anonymization invalid)")
```

### Step 2: Create Training Dataset

Combine multiple approved statements into a dataset:

```python
# Collect training data IDs
training_data_ids = [
    "550e8400-e29b-41d4-a716-446655440000",
    "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
    # ... more IDs
]

# Create dataset
dataset_id = training_data_service.create_training_dataset(
    dataset_name="financial_statements_2024_q4",
    training_data_ids=training_data_ids,
    purpose="fraud_detection_model_training",
    creator_user_id=data_scientist_user_id,
    filters={
        "date_range": {"start": "2024-10-01", "end": "2024-12-31"},
        "quality": ["excellent", "good"],
        "statement_types": ["balance_sheet", "income_statement"]
    }
)

print(f"Training dataset created: {dataset_id}")
```

### Step 3: Retrieve Dataset for Training

```python
# Get dataset for model training
dataset = training_data_service.get_training_dataset(dataset_id)

print(f"Dataset: {dataset['name']}")
print(f"Statements: {dataset['training_data_count']}")

# Access anonymized data
training_data = dataset['data']  # List of anonymized financial statements

# Use for model training
# train_model(training_data)
```

---

## Model Training Integration

### Example: Fraud Detection Model

```python
import torch
from torch.utils.data import Dataset, DataLoader

class FinancialStatementDataset(Dataset):
    def __init__(self, dataset_id, training_data_service):
        # Load training dataset
        dataset = training_data_service.get_training_dataset(dataset_id)
        self.statements = dataset['data']

    def __len__(self):
        return len(self.statements)

    def __getitem__(self, idx):
        statement = self.statements[idx]

        # Extract features (financial data only, no PII)
        features = {
            'total_assets': statement['total_assets'],
            'total_liabilities': statement['total_liabilities'],
            'revenue': statement['revenue'],
            'net_income': statement['net_income'],
            'current_ratio': statement['current_ratio'],
            'debt_to_equity': statement['debt_to_equity'],
            # ... more features
        }

        # Convert to tensor
        feature_vector = torch.tensor(list(features.values()), dtype=torch.float32)

        return feature_vector

# Create dataset and dataloader
dataset = FinancialStatementDataset(dataset_id, training_data_service)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Train model
model = FraudDetectionModel()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(100):
    for batch in dataloader:
        # Training loop
        optimizer.zero_grad()
        outputs = model(batch)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

# Track model training
training_data_service.track_model_training(
    dataset_id=dataset_id,
    model_id="fraud_detector_v2.1",
    model_name="Financial Statement Fraud Detector",
    training_metadata={
        "epochs": 100,
        "batch_size": 32,
        "learning_rate": 0.001,
        "architecture": "neural_network",
        "performance": {
            "accuracy": 0.94,
            "precision": 0.92,
            "recall": 0.90,
            "f1_score": 0.91
        }
    }
)
```

---

## Data Lineage Tracking

### Generate Lineage Report

```python
# Generate complete data lineage for a model
lineage_report = training_data_service.generate_data_lineage_report(
    model_id="fraud_detector_v2.1"
)

print(f"Model: {lineage_report['model_id']}")
print(f"Total Training Statements: {lineage_report['total_training_statements']}")
print(f"Datasets Used: {len(lineage_report['datasets_used'])}")
print(f"Sources: {lineage_report['sources_breakdown']}")
print(f"Quality: {lineage_report['quality_breakdown']}")

# Example output:
{
    "model_id": "fraud_detector_v2.1",
    "datasets_used": [
        {
            "dataset_id": "dataset_001",
            "dataset_name": "financial_statements_2024_q4",
            "data_count": 1000,
            "trained_at": "2025-01-06T12:00:00Z"
        }
    ],
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

### Privacy Verification

```python
# Verify no PII in training data
for statement in dataset['data']:
    validation = anonymization_service.validate_anonymization(statement)
    assert validation["is_valid"], "PII detected in training data!"

print("✓ All training data verified: No PII present")
```

---

## Best Practices

### 1. Data Collection

**DO:**
- ✅ Collect diverse financial statements (various industries, sizes, years)
- ✅ Include both "normal" and "anomalous" examples
- ✅ Document data source and collection method
- ✅ Obtain proper consent for AI training use

**DON'T:**
- ❌ Use data without consent
- ❌ Collect from public sources without verification
- ❌ Include data without quality assessment
- ❌ Mix public and confidential data without proper labeling

### 2. Anonymization

**DO:**
- ✅ Always use `AnonymizationLevel.FULL` for AI training
- ✅ Validate every anonymized statement
- ✅ Review validation failures manually
- ✅ Re-anonymize if validation fails

**DON'T:**
- ❌ Skip anonymization for "internal use"
- ❌ Use `AnonymizationLevel.PARTIAL` for ML training
- ❌ Ignore validation failures
- ❌ Modify anonymized data manually

### 3. Quality Control

**DO:**
- ✅ Assess data quality before approval
- ✅ Set minimum quality standards (e.g., "good" or better)
- ✅ Review "fair" quality data manually
- ✅ Document quality issues

**DON'T:**
- ❌ Approve "poor" quality data for training
- ❌ Skip quality assessment
- ❌ Train on incomplete data
- ❌ Ignore consistency issues

### 4. Dataset Management

**DO:**
- ✅ Create separate datasets for different purposes
- ✅ Version datasets (v1, v2, etc.)
- ✅ Document dataset composition
- ✅ Track which models use which datasets

**DON'T:**
- ❌ Mix training, validation, and test data
- ❌ Reuse datasets without versioning
- ❌ Share datasets without anonymization verification
- ❌ Lose track of data lineage

### 5. Model Training

**DO:**
- ✅ Track all training metadata
- ✅ Document model performance
- ✅ Generate lineage reports
- ✅ Verify anonymization before training

**DON'T:**
- ❌ Train without tracking lineage
- ❌ Skip anonymization validation
- ❌ Use original (non-anonymized) data
- ❌ Forget to log training operations

### 6. Compliance

**DO:**
- ✅ Maintain complete audit trail
- ✅ Regular privacy reviews
- ✅ Document data retention policies
- ✅ Provide data lineage on request

**DON'T:**
- ❌ Skip audit logging
- ❌ Delete without retention policy
- ❌ Lose track of data sources
- ❌ Fail to document privacy controls

---

## Statistics & Reporting

### Get Training Data Statistics

```python
stats = training_data_service.get_statistics()

print(f"Total Statements: {stats['total_statements']}")
print(f"Approved for Training: {stats['approved_for_training']}")
print(f"Total Datasets: {stats['total_datasets']}")
print(f"Status Breakdown: {stats['status_breakdown']}")
print(f"Quality Breakdown: {stats['quality_breakdown']}")
print(f"Source Breakdown: {stats['source_breakdown']}")
```

### Generate Anonymization Report

```python
from datetime import datetime, timedelta

# Generate report for last quarter
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=90)

report = anonymization_service.generate_anonymization_report(
    tenant_id=tenant_id,
    start_date=start_date,
    end_date=end_date
)

print(f"Statements Anonymized: {report['statistics']['total_statements_anonymized']}")
print(f"PII Instances Removed: {report['statistics']['pii_instances_removed']}")
print(f"PII Breakdown: {report['pii_breakdown']}")
```

---

## Troubleshooting

### Issue: Anonymization Validation Fails

**Symptoms:** `validation_result["is_valid"] == False`

**Solution:**
```python
# Check what PII was detected
issues = validation_result["issues"]
for issue in issues:
    print(f"Type: {issue['type']}, Count: {issue['count']}")
    if 'examples' in issue:
        print(f"Examples: {issue['examples']}")

# Re-anonymize with stricter settings
# Or manually review and fix
```

### Issue: Poor Data Quality

**Symptoms:** `quality_assessment["overall_quality"] == "poor"`

**Solution:**
```python
# Review specific issues
quality = training_record["quality_assessment"]
print(f"Completeness: {quality['completeness_score']}")
print(f"Issues: {quality['consistency_issues']}")

# Either:
# 1. Fix data issues and re-ingest
# 2. Reject data for training
# 3. Use with caution (document limitations)
```

### Issue: Cannot Approve for Training

**Symptoms:** `approve_for_training()` returns `False`

**Solution:**
```python
# Check why approval failed
if quality == "poor":
    print("Reason: Data quality too low")
elif not anonymization_validation["is_valid"]:
    print("Reason: Anonymization validation failed")

# Fix underlying issue before re-attempting approval
```

---

## Security Considerations

1. **Access Control**: Only authorized users can:
   - Ingest training data
   - Approve for training
   - Access original (non-anonymized) data
   - De-anonymize data

2. **Encryption**:
   - Original statements encrypted at rest
   - Token mappings encrypted
   - Secure key management

3. **Audit Logging**:
   - All operations logged
   - User attribution
   - Timestamp tracking
   - Compliance reporting

4. **Data Retention**:
   - Original data: Per company policy
   - Anonymized data: Available for training
   - Token mappings: Retained for reversibility
   - Audit logs: 7 years (compliance)

---

## Support

For questions or issues:

- **Technical Support**: support@auraauditai.com
- **Data Privacy**: privacy@auraauditai.com
- **Documentation**: https://docs.auraauditai.com

---

**Version**: 1.0.0
**Last Updated**: 2025-01-06
