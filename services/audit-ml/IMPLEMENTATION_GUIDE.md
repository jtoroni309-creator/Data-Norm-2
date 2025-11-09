# Audit ML Service - Implementation Guide

## Quick Start

### 1. Installation

```bash
cd services/audit-ml
pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/atlas

# Azure Storage (for model storage)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER=audit-ml-models

# Model Configuration
AUDIT_ML_TARGET_ACCURACY=0.99
AUDIT_ML_MIN_DATA_QUALITY_SCORE=0.9
AUDIT_ML_LOG_LEVEL=INFO
```

### 3. Initial Training

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.audit_ml.app import AuditTrainingPipeline

# Create database session
engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)
session = Session()

# Initialize pipeline
pipeline = AuditTrainingPipeline(db_session=session)

# Run full training
results = pipeline.run_full_training_pipeline(
    engagement_ids=None,  # Use all available engagements
    evaluation_mode=True  # Run CPA benchmark evaluation
)

print(f"Training complete!")
print(f"Meets 99% target: {results['meets_99_percent_target']}")
print(f"Overall status: {results['overall_status']}")
```

## Step-by-Step Implementation

### Step 1: Prepare Training Data

#### 1.1 Ensure High-Quality Labels

```sql
-- Verify labeled data exists
SELECT COUNT(*)
FROM training_labels tl
INNER JOIN journal_entries je ON tl.entity_id = je.id
WHERE tl.entity_type = 'journal_entry'
  AND tl.is_validated = true
  AND tl.agreement_score >= 0.8;
```

Expected: At least 1,000 labeled examples per class.

#### 1.2 Generate Labels (if needed)

```python
from database.models.ai_training_models import TrainingLabel
from uuid import uuid4

# Create training labels for journal entries
for journal_entry in journal_entries:
    label = TrainingLabel(
        id=uuid4(),
        entity_type='journal_entry',
        entity_id=journal_entry.id,
        engagement_id=journal_entry.engagement_id,
        label_type='anomaly_classification',
        label_value='normal',  # or 'anomalous'
        label_confidence=0.95,
        source_type='human_expert',
        labeler_user_id=cpa_user_id,
        labeler_role='partner',
        is_validated=True,
        agreement_score=1.0
    )
    session.add(label)

session.commit()
```

### Step 2: Feature Engineering

#### 2.1 Create Journal Entry Metadata

```python
from database.models.ai_training_models import JournalEntryMetadata
from uuid import uuid4
from decimal import Decimal

# For each journal entry, create metadata
for journal_entry in journal_entries:
    metadata = JournalEntryMetadata(
        id=uuid4(),
        journal_entry_id=journal_entry.id,

        # Temporal features
        day_of_week=journal_entry.entry_date.weekday(),
        day_of_month=journal_entry.entry_date.day,
        quarter=(journal_entry.entry_date.month - 1) // 3 + 1,
        is_month_end=(journal_entry.entry_date.day >= 28),
        is_quarter_end=journal_entry.entry_date.month in [3, 6, 9, 12],
        is_year_end=(journal_entry.entry_date.month == 12 and journal_entry.entry_date.day == 31),

        # Transaction characteristics
        line_count=len(journal_entry.lines),
        has_foreign_currency=False,
        currency_count=1,

        # Documentation
        has_supporting_documents=len(journal_entry.documents) > 0,
        document_count=len(journal_entry.documents),

        # Risk scores (to be computed)
        fraud_risk_score=Decimal('0.0'),
        misstatement_risk_score=Decimal('0.0'),
        complexity_score=Decimal('0.0')
    )

    session.add(metadata)

session.commit()
```

### Step 3: Train Models

#### 3.1 Extract Training Data

```python
from services.audit_ml.app import AuditTrainingPipeline

pipeline = AuditTrainingPipeline(db_session=session)

# Extract high-quality training data
raw_data = pipeline.extract_training_data_from_engagements(
    engagement_ids=None,  # All engagements
    date_range=None,      # All dates
    min_quality_score=0.9  # High quality only
)

print(f"Extracted {len(raw_data)} training examples")
```

#### 3.2 Prepare Datasets

```python
# Prepare train/val/test splits
dataset_dict = pipeline.prepare_training_dataset(
    raw_data=raw_data,
    dataset_name=f"audit_training_{datetime.now().strftime('%Y%m%d')}",
    purpose='journal_anomaly_detection'
)

print(f"Train: {len(dataset_dict['train'][0])} examples")
print(f"Val: {len(dataset_dict['val'][0])} examples")
print(f"Test: {len(dataset_dict['test'][0])} examples")
```

#### 3.3 Train All Models

```python
# Train models
training_results = pipeline.train_all_models(dataset_dict)

print("Training Results:")
for model_name, metrics in training_results.items():
    if model_name != 'model_paths':
        print(f"\n{model_name}:")
        print(f"  Accuracy: {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall: {metrics['recall']:.4f}")
```

### Step 4: Evaluate Against CPA Benchmark

```python
X_test, y_test = dataset_dict['test']

# Evaluate against CPA decisions
benchmark_results = pipeline.evaluate_models_against_cpa_benchmark(
    test_data=X_test,
    cpa_labels=y_test,
    model_name='journal_anomaly'
)

print(f"\nCPA Benchmark Evaluation:")
print(f"Agreement Rate: {benchmark_results['cpa_agreement_rate']:.2%}")
print(f"Meets 99% Target: {benchmark_results['meets_99_percent_target']}")
print(f"Cases Tested: {benchmark_results['cases_tested']}")
print(f"Cases Agreed: {benchmark_results['cases_agreed']}")
print(f"Cases Disagreed: {benchmark_results['cases_disagreed']}")
```

### Step 5: PCAOB Compliance Verification

```python
from services.audit_ml.app import pcaob_compliance_scorer

# Comprehensive compliance check
engagement_data = {
    'engagement_id': engagement_id,

    'evidence_data': {
        'source_type': 'external',
        'evidence_types': ['confirmation', 'inspection'],
        'corroboration_count': 3,
        'is_independent_source': True,
        'evidence_age_days': 15,
        'has_documentation': True
    },

    'fraud_procedures': {
        'fraud_brainstorming_conducted': True,
        'fraud_brainstorming_participants': 5,
        'pressure_factors_assessed': True,
        'opportunity_factors_assessed': True,
        'rationalization_assessed': True,
        'revenue_fraud_risk_assessed': True,
        'management_override_procedures': True,
        'override_procedures_performed': [
            'journal_entry_testing',
            'accounting_estimates_review',
            'unusual_transactions'
        ]
    },

    'going_concern_data': {
        'going_concern_indicators_assessed': [
            'negative_working_capital',
            'negative_cash_flows',
            'loan_defaults',
            'debt_covenant_violations',
            'operating_losses'
        ],
        'substantial_doubt_determination_documented': True,
        'management_plans_evaluated': True,
        'plan_elements_evaluated': ['borrow_money', 'reduce_operations'],
        'mitigating_factors_considered': True,
        'disclosure_adequacy_assessed': True
    }
}

compliance_report = pcaob_compliance_scorer.comprehensive_compliance_report(engagement_data)

print(f"\nPCAOB Compliance Report:")
print(f"Overall Score: {compliance_report['overall_compliance_score']:.2%}")
print(f"All Standards Met: {compliance_report['all_standards_met']}")
print(f"Critical Issues: {compliance_report['critical_issues_count']}")
print(f"Assessment: {compliance_report['overall_assessment']}")
print(f"Recommendation: {compliance_report['recommendation']}")
```

### Step 6: Deploy Models

```python
# Save trained models
from services.audit_ml.app import audit_model_trainer

model_paths = audit_model_trainer.save_models(output_dir="./models")

print("\nModels saved to:")
for name, path in model_paths.items():
    print(f"  {name}: {path}")

# Upload to Azure (if configured)
if settings.MODEL_STORAGE_TYPE == 'azure':
    # Models automatically uploaded during save
    print("\n✓ Models uploaded to Azure Blob Storage")
```

### Step 7: Make Predictions

```python
import joblib
import pandas as pd

# Load model
model = joblib.load('./models/journal_anomaly_model.pkl')
scaler = joblib.load('./models/journal_anomaly_scaler.pkl')

# Prepare new journal entry for prediction
new_entry_features = extract_cpa_level_features(
    journal_entries=pd.DataFrame([new_journal_entry]),
    financial_statements=financial_data
)

# Scale and predict
X_scaled = scaler.transform(new_entry_features)
prediction = model.predict(X_scaled)[0]
confidence = model.predict_proba(X_scaled)[0].max()

print(f"\nPrediction: {prediction}")
print(f"Confidence: {confidence:.2%}")

if prediction == 1:  # Anomalous
    print("⚠️ ANOMALY DETECTED - Requires investigation")
else:
    print("✓ Normal entry")
```

## Continuous Learning Setup

### Step 8: Implement Feedback Loop

```python
# Collect CPA feedback
from database.models.ai_training_models import HumanFeedback

feedback = HumanFeedback(
    id=uuid4(),
    feedback_type='prediction_correction',
    entity_type='journal_entry',
    entity_id=journal_entry_id,
    engagement_id=engagement_id,
    user_id=cpa_user_id,
    user_role='partner',
    user_expertise_level='expert',
    original_prediction_id=prediction_id,
    original_value='normal',
    original_confidence=Decimal('0.85'),
    corrected_value='anomalous',
    correction_confidence=Decimal('0.95'),
    correction_rationale='Entry posted after hours with round amounts',
    is_critical_feedback=True,
    requires_model_retrain=True,
    status='pending'
)

session.add(feedback)
session.commit()
```

### Step 9: Retrain with Feedback

```python
# Query recent feedback
feedback_query = """
SELECT
    f.*,
    je.*,
    jem.*
FROM human_feedback f
INNER JOIN journal_entries je ON f.entity_id = je.id
INNER JOIN journal_entry_metadata jem ON je.id = jem.journal_entry_id
WHERE f.status = 'pending'
  AND f.requires_model_retrain = true
  AND f.feedback_quality_score >= 0.8
"""

feedback_data = pd.read_sql(feedback_query, session.bind)

# Prepare feedback for retraining
feedback_examples = prepare_feedback_dataset(feedback_data)

# Update model with feedback
update_results = pipeline.integrate_cpa_feedback(
    model_name='journal_anomaly',
    feedback_examples=feedback_examples
)

print(f"\nContinuous Learning Results:")
print(f"Feedback samples used: {update_results['feedback_samples_used']}")
print(f"Updated accuracy: {update_results['accuracy']:.4f}")
print(f"Model version: {update_results['model_version']}")
```

### Step 10: Active Learning

```python
# Get unlabeled data
unlabeled_query = """
SELECT
    je.*,
    jem.*
FROM journal_entries je
INNER JOIN journal_entry_metadata jem ON je.id = jem.journal_entry_id
LEFT JOIN training_labels tl ON tl.entity_id = je.id
WHERE tl.id IS NULL
  AND je.entry_date >= CURRENT_DATE - INTERVAL '30 days'
"""

unlabeled_data = pd.read_sql(unlabeled_query, session.bind)

# Identify high-value examples for CPA review
priority_examples = pipeline.implement_active_learning(
    model_name='journal_anomaly',
    unlabeled_data=unlabeled_data,
    n_samples=100
)

print(f"\nActive Learning Results:")
print(f"Identified {len(priority_examples)} examples for CPA review")
print(f"High priority: {sum(1 for e in priority_examples if e['priority'] == 'high')}")
print(f"Medium priority: {sum(1 for e in priority_examples if e['priority'] == 'medium')}")
```

## Production Deployment

### Monitoring Setup

```python
from services.audit_ml.app.config import settings

# Enable monitoring
settings.DRIFT_DETECTION_ENABLED = True
settings.PERFORMANCE_MONITORING_ENABLED = True
settings.ALERT_ON_ACCURACY_DROP = 0.05  # 5% drop triggers alert
```

### API Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Audit ML API", version="1.0.0")

class PredictionRequest(BaseModel):
    journal_entry_id: str
    features: dict

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    explanation: str
    requires_investigation: bool

@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make prediction on journal entry."""

    # Load model
    model = joblib.load('./models/journal_anomaly_model.pkl')
    scaler = joblib.load('./models/journal_anomaly_scaler.pkl')

    # Prepare features
    features_df = pd.DataFrame([request.features])
    X_scaled = scaler.transform(features_df)

    # Predict
    prediction = model.predict(X_scaled)[0]
    confidence = model.predict_proba(X_scaled)[0].max()

    return PredictionResponse(
        prediction='anomalous' if prediction == 1 else 'normal',
        confidence=confidence,
        explanation=generate_explanation(features_df, prediction),
        requires_investigation=(prediction == 1 and confidence >= 0.8)
    )
```

## Troubleshooting

### Issue: Low Training Accuracy

**Solution**:
1. Check data quality: `SELECT AVG(agreement_score) FROM training_labels`
2. Verify sufficient examples: Minimum 100 per class
3. Review feature engineering: Ensure all 200+ features computed
4. Try different hyperparameters

### Issue: Model-CPA Disagreement

**Solution**:
1. Analyze disagreement cases for patterns
2. Collect more labeled examples for difficult cases
3. Use active learning to prioritize labeling efforts
4. Consider ensemble weighting adjustment

### Issue: PCAOB Compliance Failures

**Solution**:
1. Review specific standard requirements
2. Ensure all procedures documented
3. Verify evidence quality and sufficiency
4. Consult PCAOB guidance for interpretation

## Next Steps

1. **Production Deployment**: Deploy to Azure/AWS
2. **API Development**: Build RESTful API endpoints
3. **UI Integration**: Integrate with audit platform UI
4. **Monitoring Dashboard**: Create real-time monitoring
5. **A/B Testing**: Compare AI vs traditional methods
6. **Scale Training**: Distribute training across GPUs

## Support

For technical support:
- Email: ml-team@yourcompany.com
- Slack: #audit-ml-support
- Documentation: https://docs.yourcompany.com/audit-ml

---

**Last Updated**: January 9, 2025
