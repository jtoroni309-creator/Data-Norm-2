# SOC Copilot - API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Interactive API Docs

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Table of Contents

1. [Predictive Analytics API](#predictive-analytics-api)
2. [Natural Language Query API](#natural-language-query-api)
3. [Smart Sampling API](#smart-sampling-api)
4. [Client Portal API](#client-portal-api)
5. [Penetration Testing API](#penetration-testing-api)

---

## Predictive Analytics API

### Train ML Model

**POST** `/api/v1/predictive-analytics/train-model`

Train a machine learning model for control failure prediction.

**Request:**
```json
{
  "model_type": "random_forest"
}
```

**Response:**
```json
{
  "model_type": "random_forest",
  "training_samples": 160,
  "test_samples": 40,
  "train_accuracy": 0.8875,
  "test_accuracy": 0.8500,
  "precision": 0.8400,
  "recall": 0.8600,
  "f1_score": 0.8500,
  "cv_mean": 0.8450,
  "cv_std": 0.0250,
  "feature_importance": {
    "past_failure_rate": 0.35,
    "evidence_completeness_rate": 0.25,
    "deviation_count_30d": 0.20,
    "tech_complexity_score": 0.10,
    "automation_level": 0.10
  },
  "trained_at": "2025-01-21T15:30:00Z"
}
```

---

### Predict Control Failure

**GET** `/api/v1/predictive-analytics/controls/{control_id}/predict`

Predict probability of control failure for a specific control.

**Response:**
```json
{
  "control_id": "12345678-1234-5678-1234-567812345678",
  "failure_probability": 0.85,
  "risk_score": 85,
  "risk_level": "CRITICAL",
  "confidence_interval": {
    "lower": 0.75,
    "upper": 0.95
  },
  "risk_factors": [
    {
      "factor": "past_failure_rate",
      "value": 0.45,
      "importance": 0.35,
      "contribution_score": 0.1575
    },
    {
      "factor": "evidence_completeness_rate",
      "value": 0.60,
      "importance": 0.25,
      "contribution_score": 0.1500
    }
  ],
  "recommendations": [
    "URGENT: Schedule immediate review with CPA Partner",
    "Review control design - high historical failure rate indicates design flaw",
    "Request missing evidence immediately - completeness below target"
  ],
  "estimated_remediation_hours": 40.0,
  "prediction_timestamp": "2025-01-21T15:35:00Z",
  "model_used": "random_forest"
}
```

---

### Get At-Risk Controls

**GET** `/api/v1/predictive-analytics/engagements/{engagement_id}/at-risk-controls?top_n=10`

Get top N highest-risk controls for an engagement.

**Response:**
```json
[
  {
    "control_id": "12345678-1234-5678-1234-567812345678",
    "control_code": "CC6.1",
    "control_name": "Logical Access - User Provisioning",
    "risk_score": 85,
    "risk_level": "CRITICAL",
    "failure_probability": 0.85,
    "top_risk_factor": "High past failure rate (45%)"
  },
  {
    "control_id": "22345678-1234-5678-1234-567812345678",
    "control_code": "CC7.2",
    "control_name": "System Monitoring - Security Event Detection",
    "risk_score": 72,
    "risk_level": "HIGH",
    "failure_probability": 0.72,
    "top_risk_factor": "Missing evidence (60% completeness)"
  }
]
```

---

## Natural Language Query API

### Execute Natural Language Query

**POST** `/api/v1/nl-query/execute`

Execute a natural language question about audit data.

**Request:**
```json
{
  "user_query": "Show me all failed controls in Q4 2024",
  "engagement_id": "12345678-1234-5678-1234-567812345678"
}
```

**Response:**
```json
{
  "success": true,
  "user_query": "Show me all failed controls in Q4 2024",
  "interpreted_intent": "Filtering controls by failure status and time period",
  "sql_generated": "SELECT DISTINCT c.control_id, c.control_name, c.control_type, COUNT(tr.id) as failed_test_count FROM soc_copilot.controls c JOIN soc_copilot.test_plans tp ON c.id = tp.control_id JOIN soc_copilot.test_results tr ON tp.id = tr.test_plan_id WHERE tr.passed = false AND tr.test_date >= '2024-10-01' AND tr.test_date <= '2024-12-31' GROUP BY c.id ORDER BY failed_test_count DESC",
  "results_count": 5,
  "results": [
    {
      "control_id": "CC6.1",
      "control_name": "User Access Provisioning",
      "control_type": "MANUAL",
      "failed_test_count": 3
    },
    {
      "control_id": "CC7.2",
      "control_name": "Security Monitoring",
      "control_type": "AUTOMATED",
      "failed_test_count": 2
    }
  ],
  "summary": "Found 5 controls that failed testing in Q4 2024. The most problematic control is User Access Provisioning (CC6.1) with 3 failed tests, indicating a potential design or operating effectiveness issue.",
  "execution_time_ms": 245
}
```

---

### Get Query Suggestions

**GET** `/api/v1/nl-query/suggestions`

Get suggested queries/templates.

**Response:**
```json
[
  {
    "template_name": "failed_controls",
    "description": "List all controls that failed testing",
    "example_question": "Show me all failed controls"
  },
  {
    "template_name": "high_risk_deviations",
    "description": "List high and critical severity deviations",
    "example_question": "Show me all high-risk deviations"
  },
  {
    "template_name": "missing_evidence",
    "description": "Identify missing or incomplete evidence",
    "example_question": "What evidence is missing or incomplete?"
  }
]
```

---

### Common Query Examples

**Example 1: Failed Controls**
```
Query: "Show me all failed controls"
Returns: List of controls that failed testing with failure counts
```

**Example 2: At-Risk Controls**
```
Query: "Which controls are at risk of failing?"
Returns: Controls predicted to fail based on ML model
```

**Example 3: Missing Evidence**
```
Query: "What evidence is missing or incomplete?"
Returns: Evidence with PENDING or INCOMPLETE status
```

**Example 4: Overdue Requests**
```
Query: "Which evidence requests are overdue from the client?"
Returns: Evidence requests past due date with days overdue
```

**Example 5: Security Controls Summary**
```
Query: "Summarize all security controls (CC6 and CC7)"
Returns: Aggregated stats for CC6 and CC7 control objectives
```

---

## Smart Sampling API

### Calculate Sample Size

**POST** `/api/v1/sampling/calculate-sample-size`

Calculate required sample size using statistical formulas.

**Request:**
```json
{
  "population_size": 1000,
  "confidence_level": 95.0,
  "tolerable_error_rate": 5.0,
  "expected_error_rate": 2.0,
  "method": "RANDOM"
}
```

**Response:**
```json
{
  "population_size": 1000,
  "confidence_level": 95.0,
  "tolerable_error_rate": 5.0,
  "expected_error_rate": 2.0,
  "sampling_method": "RANDOM",
  "calculated_sample_size": 73,
  "adjusted_sample_size": 68,
  "recommended_sample_size": 68,
  "minimum_sample_size": 25,
  "sampling_percentage": 6.8,
  "statistical_metrics": {
    "z_score": 1.96,
    "precision": 0.0324,
    "risk_of_incorrect_acceptance": 0.05,
    "risk_of_incorrect_rejection": 0.10
  },
  "calculated_at": "2025-01-21T16:00:00Z"
}
```

---

### AI-Optimize Sample Size

**POST** `/api/v1/sampling/ai-optimize`

Use AI to recommend optimal sample size based on risk factors.

**Request:**
```json
{
  "population_size": 500,
  "control_info": {
    "control_name": "Multi-Factor Authentication Enforcement",
    "control_type": "AUTOMATED",
    "criticality": "HIGH",
    "technology": "Okta"
  },
  "historical_data": {
    "past_failure_rate": 0.15,
    "past_sample_sizes": [25, 30, 35],
    "deviations_found": 3
  }
}
```

**Response:**
```json
{
  "population_size": 500,
  "confidence_level": 99.0,
  "tolerable_error_rate": 3.0,
  "expected_error_rate": 15.0,
  "sampling_method": "AI_OPTIMIZED",
  "calculated_sample_size": 120,
  "recommended_sample_size": 120,
  "sampling_percentage": 24.0,
  "ai_recommended_size": 120,
  "ai_rationale": "Given the high criticality control, elevated historical failure rate (15%), and automated nature requiring trust in technology, recommend larger sample (120) with higher confidence (99%) and lower tolerance (3%) to ensure robust conclusion. Historical deviations suggest control effectiveness issues requiring thorough testing.",
  "ai_risk_factors": [
    "Historical failure rate of 15% significantly above expected",
    "HIGH criticality control protecting critical authentication",
    "Automated control requires validation of technology effectiveness",
    "Past deviations indicate potential ongoing issues"
  ],
  "calculated_at": "2025-01-21T16:05:00Z"
}
```

---

### Adaptive Sampling Adjustment

**POST** `/api/v1/sampling/adaptive-adjustment`

Evaluate if sample size should be adjusted based on errors found during testing.

**Request:**
```json
{
  "initial_sample_size": 50,
  "errors_found": 5,
  "tests_completed": 30,
  "tolerable_error_rate": 5.0
}
```

**Response (High Error Rate):**
```json
{
  "adjustment_needed": true,
  "adjustment_trigger": "HIGH_ERROR_RATE",
  "current_error_rate": 16.67,
  "tolerable_error_rate": 5.0,
  "original_sample_size": 50,
  "additional_samples_needed": 25,
  "new_total_sample_size": 75,
  "rationale": "Error rate (16.7%) exceeds tolerance (5.0%). Expanding sample to improve statistical confidence.",
  "requires_cpa_approval": true,
  "calculated_at": "2025-01-21T16:10:00Z"
}
```

**Response (Within Tolerance):**
```json
{
  "adjustment_needed": false,
  "observation": "WITHIN_TOLERANCE",
  "current_error_rate": 4.0,
  "tolerable_error_rate": 5.0,
  "note": "Error rate within acceptable range. Continue with original sample plan.",
  "calculated_at": "2025-01-21T16:10:00Z"
}
```

---

### Calculate Sampling Results

**POST** `/api/v1/sampling/calculate-results`

Calculate statistical results after sampling is completed.

**Request:**
```json
{
  "sample_size": 50,
  "errors_found": 2,
  "confidence_level": 95.0
}
```

**Response:**
```json
{
  "sample_size": 50,
  "errors_found": 2,
  "error_rate": 4.0,
  "confidence_level": 95.0,
  "upper_confidence_limit": 9.76,
  "lower_confidence_limit": 1.24,
  "confidence_interval": "1.24% - 9.76%",
  "precision": 4.26,
  "conclusion": "PASS - Error rate within acceptable limits",
  "calculated_at": "2025-01-21T16:15:00Z"
}
```

---

### List Sampling Methods

**GET** `/api/v1/sampling/methods`

Get available sampling methods with descriptions.

**Response:**
```json
{
  "RANDOM": {
    "name": "Simple Random Sampling",
    "description": "Pure random selection from population",
    "best_for": "Homogeneous populations"
  },
  "STRATIFIED": {
    "name": "Stratified Sampling",
    "description": "Proportional representation from strata",
    "best_for": "Heterogeneous populations with clear groups"
  },
  "AI_OPTIMIZED": {
    "name": "AI-Optimized Sampling",
    "description": "AI recommends optimal method and size",
    "best_for": "All scenarios - uses risk-based intelligence"
  }
}
```

---

## Client Portal API

### Client Dashboard

**GET** `/api/v1/client-portal/client-view/dashboard`

Get client dashboard data (requires client authentication).

**Response:**
```json
{
  "pending_requests": 7,
  "overdue_requests": 2,
  "recent_uploads": 12,
  "pending_auditor_review": 3,
  "upcoming_deadlines": [
    {
      "request_title": "Q4 User Access Review Evidence",
      "due_date": "2025-01-25",
      "priority": "HIGH"
    }
  ],
  "recent_activity": [
    {
      "timestamp": "2025-01-21T10:00:00Z",
      "action": "Evidence accepted",
      "request": "Backup logs for December 2024"
    }
  ]
}
```

---

### Upload Evidence

**POST** `/api/v1/client-portal/client-view/evidence-requests/{request_id}/upload`

Upload evidence file in response to auditor request.

**Request:**
- **Content-Type:** `multipart/form-data`
- **file:** Evidence file (PDF, XLSX, PNG, JPG, MP4, ZIP)
- **client_notes:** Optional notes

**Response:**
```json
{
  "id": "12345678-1234-5678-1234-567812345678",
  "evidence_request_id": "22345678-1234-5678-1234-567812345678",
  "filename": "mfa-status-report-dec2024.pdf",
  "file_size_bytes": 2458624,
  "client_notes": "MFA status report exported from Okta on 2024-12-31",
  "uploaded_at": "2025-01-21T16:30:00Z",
  "verification_status": "PENDING",
  "auditor_feedback": null
}
```

---

## Integration Examples

### Frontend Integration

**React Example (NL Query):**
```typescript
import axios from 'axios';

const executeQuery = async (userQuery: string) => {
  try {
    const response = await axios.post('/api/v1/nl-query/execute', {
      user_query: userQuery
    });

    if (response.data.success) {
      console.log('Results:', response.data.results);
      console.log('Summary:', response.data.summary);
    }
  } catch (error) {
    console.error('Query failed:', error);
  }
};

// Usage
executeQuery("Show me all failed controls");
```

**React Example (Predictive Analytics):**
```typescript
const getPrediction = async (controlId: string) => {
  try {
    const response = await axios.get(
      `/api/v1/predictive-analytics/controls/${controlId}/predict`
    );

    console.log(`Risk Score: ${response.data.risk_score}/100`);
    console.log(`Risk Level: ${response.data.risk_level}`);
    console.log('Recommendations:', response.data.recommendations);
  } catch (error) {
    console.error('Prediction failed:', error);
  }
};
```

**React Example (Smart Sampling):**
```typescript
const calculateSample = async (populationSize: number) => {
  try {
    const response = await axios.post('/api/v1/sampling/calculate-sample-size', {
      population_size: populationSize,
      confidence_level: 95.0,
      tolerable_error_rate: 5.0,
      expected_error_rate: 2.0,
      method: "RANDOM"
    });

    console.log(`Recommended Sample: ${response.data.recommended_sample_size}`);
    console.log(`Sampling %: ${response.data.sampling_percentage}%`);
  } catch (error) {
    console.error('Calculation failed:', error);
  }
};
```

---

## Error Responses

All endpoints return standard error responses:

**400 Bad Request:**
```json
{
  "detail": "Validation error: population_size must be >= 1"
}
```

**404 Not Found:**
```json
{
  "detail": "Control 12345678-1234-5678-1234-567812345678 not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Prediction failed: Model not trained"
}
```

---

## Rate Limits

- **Standard endpoints:** 100 requests/minute
- **AI endpoints (NL query, predictions):** 30 requests/minute
- **File uploads:** 10 requests/minute

---

## Authentication

All endpoints require JWT authentication via Bearer token:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Websocket Endpoints (Future)

Real-time updates for:
- Continuous control monitoring
- Live query results
- Evidence upload status

**Coming Soon**

---

**Last Updated:** January 21, 2025
**Version:** 1.0.0
