# ADR-0001: AI-First Tax Preparation Engine - Context & Architecture

**Status**: Proposed
**Date**: 2025-11-08
**Authors**: Engineering Team
**Deciders**: Product Architecture, Engineering Leadership

---

## Context

Aura Audit AI (Project Atlas) is expanding from audit and compliance services into tax preparation. This ADR documents the architectural decisions for building an AI-first tax preparation feature that achieves functional parity with leading solutions (CCH Axcess Tax, UltraTax) while leveraging our existing platform capabilities.

### Business Objectives

1. **CPA Firm Enablement**: Provide CPAs with modern, AI-assisted tax preparation tools integrated with audit workflows
2. **Workflow Efficiency**: Auto-populate returns from source documents (W-2, 1099s, K-1s, brokerage statements) using OCR and intelligent mapping
3. **Quality & Compliance**: Built-in cross-checks, variance detection, anomaly flagging, and audit trails
4. **Scalability**: Federal + multi-state expansion; individual (1040) → corporate (1120, 1120-S, 1065)
5. **Integration**: Seamless data flow from accounting systems (QuickBooks, Xero) and audit engagements

### Technical Constraints

1. **Existing Stack**: Python 3.11+, FastAPI, PostgreSQL 15, Redis, MinIO, OpenAI GPT-4
2. **Architecture**: Microservices (24 existing services), event-driven (Redis pub/sub), async-first
3. **Security**: RBAC, field-level encryption (SSNs/EINs), audit logging, SOC 2/GLBA alignment
4. **Performance**: < 2 min p95 for 200-page document packet end-to-end processing
5. **Accuracy**: ≥95% OCR classification, ≥98% field extraction for core documents
6. **Clean Room**: No proprietary vendor schemas; replicate behavior via IRS concepts only

---

## Decision

We will build the tax preparation engine as a **new microservice cluster** integrated into the existing Atlas platform, following these architectural principles:

### 1. Service Architecture

**Core Services** (New):

- **`tax-ocr-intake`** (Port 8025): Document upload, classification, OCR, table extraction
- **`tax-engine`** (Port 8026): Tax computation engine (TCE), rules engine, calculations
- **`tax-forms`** (Port 8027): Form schemas, rendering, PDF generation, e-file packaging
- **`tax-review`** (Port 8028): Review workbench, human-in-the-loop queues, variance analysis

**Supporting Services** (Existing, Reused):

- **`llm`**: AI-powered field extraction, deduction suggestions, natural language explanations
- **`accounting-integrations`**: Import financial data from QuickBooks/Xero/NetSuite
- **`security`**: Encryption utilities, key management
- **`identity`**: Authentication, RBAC
- **`reporting`**: PDF assembly for filing packages

### 2. Data Architecture

**Tax Data Schema (TDS)** - Canonical representation stored in PostgreSQL:

```python
{
  "taxReturnId": "UUID",
  "year": 2024,
  "filingStatus": "MFJ",
  "taxpayer": {"name": "...", "ssnEnc": "...", "dob": "..."},
  "income": {
    "w2": [{"ein": "...", "wages": 12345.67, "withholdingFed": 1234.56,
            "sourceId": "doc:W2#1", "confidence": 0.997}],
    "1099Int": [...],
    "1099B": [{"broker": "...", "proceeds": 123456.78, "basis": 120000.00,
               "lots": [...], "sourceId": "doc:1099-B#1", "confidence": 0.965}]
  },
  "deductions": {"mortgageInterest": 9876.54, "stateTaxes": 10000},
  "credits": {"childTaxCredit": 2000},
  "k1": {"partnership": [...], "scorp": [...]},
  "carryovers": {"capLoss": 3000},
  "provenance": [
    {"field": "income.w2[0].wages", "docRef": "doc:W2#1@page1:box1",
     "ocrModel": "gpt-4-vision", "mappingRule": "M-W2-Box1"}
  ],
  "reviewFlags": [
    {"code": "VARIANCE_PY", "severity": "medium",
     "message": "Mortgage interest decreased 85% vs PY"}
  ]
}
```

**Database Tables**:

- `tax_returns` - Main entity with calculated fields
- `tax_documents` - Ingested source documents (PDFs) with classification
- `tax_document_pages` - Individual pages with OCR metadata
- `tax_extracted_fields` - Raw OCR extractions with confidence scores
- `tax_forms` - Generated IRS forms (1040, schedules) as JSONB + PDF
- `tax_deductions` - Itemized/standard deductions
- `tax_credits` - Tax credits applied
- `tax_carryovers` - Capital losses, NOLs, passive losses
- `tax_review_flags` - Issues requiring human review
- `tax_provenance` - Full audit trail (field → source doc → rule)
- `prior_year_returns` - Historical data for variance analysis

### 3. Document Processing Pipeline

**OCR & Extraction Flow**:

```
1. Upload (PDF/TIFF/JPG) → MinIO storage
2. Page splitting → Individual images
3. Classification (W-2, 1099-INT, 1099-B, K-1, etc.)
   - Use GPT-4 Vision API with few-shot examples
   - Confidence threshold: ≥0.95 auto-classify, <0.95 → human review
4. OCR + Table Extraction
   - Layout-aware parsing (detect boxes, tables, key-value pairs)
   - Bounding box coordinates for each field
5. Field Extraction
   - Structured prompts per document type
   - JSON output with confidence per field
   - Example: W-2 → {box1_wages: 50000.00, confidence: 0.997}
6. Mapping to TDS
   - Deterministic rule catalog: "W2.box1 → income.w2[].wages"
   - Store provenance: TDS field → (doc_id, page, box, rule_id)
7. Validation & Confidence Gating
   - ≥0.98: Auto-accept
   - 0.80-0.98: Route to review queue with doc snippet
   - <0.80: Reject, require manual entry
8. Publish Event: `tax.document.processed`
```

**Document Classification Logic**:

```python
async def classify_document(image_url: str) -> DocumentClassification:
    """
    Use GPT-4 Vision to classify tax document type
    """
    llm_client = ServiceClient("llm")

    response = await llm_client.post("/vision/analyze", json={
        "image_url": image_url,
        "prompt": """
        Classify this tax document. Return JSON:
        {
          "type": "W-2" | "1099-INT" | "1099-DIV" | "1099-B" | "1099-R" |
                  "1099-MISC" | "1099-NEC" | "1098" | "5498" | "K-1-1065" |
                  "K-1-1120S" | "SSA-1099" | "1099-G" | "1095-A" | "other",
          "confidence": 0.0-1.0,
          "tax_year": 2024
        }

        Look for:
        - Form title (top of page)
        - IRS form number
        - Boxes/fields characteristic of each type
        """,
        "response_format": {"type": "json_object"}
    })

    return DocumentClassification(**response["data"])
```

### 4. Tax Computation Engine (TCE)

**Design Principles**:

- **Deterministic**: Same inputs → same outputs (unit testable)
- **Explainable**: Every computed value traces back to inputs + rules
- **Modular**: Plug-in state modules, year-specific rule sets
- **Auditable**: Immutable calculation logs

**Architecture**:

```python
class TaxComputationEngine:
    """
    Federal + State tax calculations

    V1: Individual (Form 1040)
    V2: Corporate (1120, 1120-S), Partnership (1065)
    """

    async def compute_return(
        self,
        tds: TaxDataSchema,
        tax_year: int,
        state: Optional[str] = None
    ) -> ComputationResult:
        """
        Run full tax calculation pipeline
        """
        # Federal calculation
        federal = await self._compute_federal_1040(tds, tax_year)

        # State calculation (if applicable)
        state_result = None
        if state:
            state_result = await self._compute_state(
                state, tax_year, federal.agi, federal.taxable_income
            )

        # Generate explanation graph
        explanation = self._build_explanation_graph(federal, state_result)

        return ComputationResult(
            federal=federal,
            state=state_result,
            explanation=explanation
        )

    async def _compute_federal_1040(
        self,
        tds: TaxDataSchema,
        tax_year: int
    ) -> Federal1040Result:
        """
        Form 1040 calculation with schedules
        """
        # Load year-specific rules
        rules = await self._load_rules(tax_year)

        # Line-by-line calculation
        gross_income = self._compute_gross_income(tds.income, rules)
        adjustments = self._compute_adjustments(tds, rules)
        agi = gross_income - adjustments

        deductions = self._compute_deductions(tds, agi, rules)
        qbi_deduction = self._compute_qbi_199a(tds, agi, rules)
        taxable_income = max(0, agi - deductions - qbi_deduction)

        # Tax calculation (brackets)
        income_tax = self._compute_tax_brackets(
            taxable_income, tds.filing_status, rules
        )

        # AMT
        amt = self._compute_amt(tds, agi, rules)

        # Credits
        credits = self._compute_credits(tds, income_tax, rules)

        # Self-employment tax
        se_tax = self._compute_schedule_se(tds, rules)

        # NIIT (Net Investment Income Tax)
        niit = self._compute_niit(tds, agi, rules)

        total_tax = max(income_tax, amt) + se_tax + niit - credits

        # Withholding & payments
        withholding = self._sum_withholding(tds.income)
        estimated_payments = tds.payments.estimated

        # Refund or amount due
        balance = total_tax - withholding - estimated_payments

        return Federal1040Result(
            gross_income=gross_income,
            agi=agi,
            taxable_income=taxable_income,
            income_tax=income_tax,
            amt=amt,
            se_tax=se_tax,
            niit=niit,
            credits=credits,
            total_tax=total_tax,
            withholding=withholding,
            balance=balance,
            # Explanation graph for explainability
            calculation_graph=self._graph
        )
```

**Rules Engine**:

```python
class TaxRules:
    """
    Year-specific tax rules (brackets, limits, phase-outs)
    """

    def __init__(self, tax_year: int):
        self.year = tax_year
        self.rules = self._load_rules_from_db(tax_year)

    @property
    def standard_deduction(self) -> Dict[FilingStatus, Decimal]:
        # 2024 values
        return {
            FilingStatus.SINGLE: Decimal("14600"),
            FilingStatus.MFJ: Decimal("29200"),
            FilingStatus.MFS: Decimal("14600"),
            FilingStatus.HOH: Decimal("21900")
        }

    @property
    def tax_brackets(self) -> Dict[FilingStatus, List[TaxBracket]]:
        # 2024 brackets (indexed for inflation)
        return {
            FilingStatus.SINGLE: [
                TaxBracket(min=0, max=11600, rate=Decimal("0.10")),
                TaxBracket(min=11600, max=47150, rate=Decimal("0.12")),
                TaxBracket(min=47150, max=100525, rate=Decimal("0.22")),
                TaxBracket(min=100525, max=191950, rate=Decimal("0.24")),
                TaxBracket(min=191950, max=243725, rate=Decimal("0.32")),
                TaxBracket(min=243725, max=609350, rate=Decimal("0.35")),
                TaxBracket(min=609350, max=None, rate=Decimal("0.37")),
            ],
            # ... other filing statuses
        }

    @property
    def qbi_threshold(self) -> Dict[FilingStatus, Decimal]:
        # §199A QBI deduction phase-out thresholds
        return {
            FilingStatus.SINGLE: Decimal("191950"),
            FilingStatus.MFJ: Decimal("383900")
        }
```

### 5. Forms Schema & Rendering

**Schema-Driven Forms**:

```python
# Configuration, not code
FORM_1040_SCHEMA = {
    "form": "1040",
    "year": 2024,
    "lines": [
        {
            "line": "1a",
            "label": "Total amount from Form(s) W-2, box 1",
            "source": "sum(income.w2[*].wages)",
            "type": "currency"
        },
        {
            "line": "1b",
            "label": "Household employee wages not reported on Form(s) W-2",
            "source": "income.household_wages",
            "type": "currency"
        },
        # ... 83 more lines
        {
            "line": "24",
            "label": "Total tax",
            "source": "computation.total_tax",
            "type": "currency",
            "computed": true
        }
    ],
    "schedules": ["A", "B", "C", "D", "E", "SE"]
}
```

**Two-Way Binding**:

```
User edits Form 1040, Line 1a → Updates TDS → Re-compute → Update all dependent lines
```

**PDF Generation**:

- Use existing `reporting` service (WeasyPrint)
- IRS-approved PDF templates with field overlays
- Include barcode (2D) for e-file association

### 6. Review Workbench & Human-in-the-Loop

**Review Queue**:

```python
class ReviewFlag:
    """
    Issues requiring human review
    """
    code: str  # "LOW_CONFIDENCE", "VARIANCE_PY", "MISSING_DOC", etc.
    severity: str  # "low", "medium", "high", "critical"
    message: str
    field_path: str  # "income.w2[0].wages"
    source_doc_snippet: str  # S3 URL to cropped image
    suggested_value: Optional[Decimal]
    confidence: Optional[float]

    # User actions
    resolved: bool = False
    resolution: Optional[str]  # "accept", "override", "reject"
    override_value: Optional[Decimal]
    resolved_by: Optional[UUID]
    resolved_at: Optional[datetime]
```

**Variance Detection**:

```python
async def detect_variances(
    current_year: TaxDataSchema,
    prior_year: Optional[TaxDataSchema]
) -> List[ReviewFlag]:
    """
    Compare current vs prior year and flag anomalies
    """
    flags = []

    if not prior_year:
        return flags

    # Mortgage interest variance
    current_mtg = current_year.deductions.mortgage_interest
    prior_mtg = prior_year.deductions.mortgage_interest

    if prior_mtg > 0:
        variance_pct = abs(current_mtg - prior_mtg) / prior_mtg

        if variance_pct > 0.50:  # 50% change threshold
            flags.append(ReviewFlag(
                code="VARIANCE_PY",
                severity="medium",
                message=f"Mortgage interest changed {variance_pct:.0%} vs prior year",
                field_path="deductions.mortgage_interest"
            ))

    # Missing documents (had 1099-INT last year, none this year)
    if len(prior_year.income.int_1099) > 0 and len(current_year.income.int_1099) == 0:
        flags.append(ReviewFlag(
            code="MISSING_DOC",
            severity="high",
            message="Had 1099-INT in prior year but none received this year",
            field_path="income.int_1099"
        ))

    return flags
```

**UI Workflow**:

1. Reviewer opens workbench → sees list of flagged returns
2. Click return → see side-by-side:
   - Left: Source document snippet (highlighted field)
   - Right: Extracted value with confidence score
3. Actions: Accept | Override (enter value) | Reject (delete)
4. On override → re-compute entire return → update all forms
5. Lock return when complete

### 7. E-file Abstraction

**MeF-Ready Packaging** (Federal):

```python
class EFileService:
    """
    IRS Modernized e-File (MeF) abstraction
    """

    async def validate_for_efile(self, tax_return_id: UUID) -> ValidationResult:
        """
        Pre-flight validation checks
        """
        errors = []

        # Required fields
        if not return.taxpayer_ssn:
            errors.append("SSN is required for e-file")

        # Cross-form reconciliation
        w2_total = sum(w2.wages for w2 in return.income.w2)
        form_1040_line_1 = return.forms["1040"].lines["1a"]

        if w2_total != form_1040_line_1:
            errors.append("W-2 total does not match Form 1040, Line 1a")

        # IRS business rules (800+ rules)
        await self._run_irs_business_rules(return, errors)

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    async def generate_mef_xml(self, tax_return_id: UUID) -> str:
        """
        Generate IRS MeF XML (Schema 1040-2024v1.0)
        """
        return_data = await self._load_return(tax_return_id)

        xml = {
            "Return": {
                "@xmlns": "http://www.irs.gov/efile",
                "@returnVersion": "2024v1.0",
                "ReturnHeader": {
                    "ReturnTs": datetime.utcnow().isoformat(),
                    "TaxYr": return_data.tax_year,
                    "Filer": {
                        "PrimarySSN": return_data.taxpayer.ssn,
                        "Name": return_data.taxpayer.name
                    }
                },
                "ReturnData": {
                    "IRS1040": self._build_1040_xml(return_data)
                }
            }
        }

        return xmltodict.unparse(xml, pretty=True)

    async def submit_efile(self, tax_return_id: UUID) -> EFileResult:
        """
        Submit to IRS via MeF API

        Requires:
        - IRS ETIN (Electronic Transmitter Identification Number)
        - Digital signature (X.509 certificate)
        """
        # 1. Validate
        validation = await self.validate_for_efile(tax_return_id)
        if not validation.valid:
            raise ValueError(f"E-file validation failed: {validation.errors}")

        # 2. Generate XML
        xml = await self.generate_mef_xml(tax_return_id)

        # 3. Sign with ERO certificate
        signed_xml = await self._sign_xml(xml)

        # 4. Submit to IRS MeF Gateway
        # (Placeholder - requires IRS ETIN registration)

        return EFileResult(
            status="submitted",
            confirmation_number="IRS-CONF-123456",
            submitted_at=datetime.utcnow()
        )
```

### 8. AI Assistance Features

**A. Suggested Completion**:

```python
async def suggest_missing_fields(tds: TaxDataSchema) -> List[Suggestion]:
    """
    Use AI to suggest values for missing fields based on context
    """
    llm_client = ServiceClient("llm")

    prompt = f"""
    Tax return partially completed. Suggest missing fields:

    Provided:
    - W-2 wages: ${tds.income.w2_total}
    - Mortgage interest: ${tds.deductions.mortgage_interest}

    Missing:
    - State/local tax deduction
    - Charitable contributions

    Based on taxpayer profile (middle-income, homeowner), suggest reasonable values.
    Return JSON with confidence scores.
    """

    response = await llm_client.post("/chat", json={"prompt": prompt})
    return parse_suggestions(response)
```

**B. Natural Language Explanations**:

```python
@app.post("/tax-returns/{id}/explain")
async def explain_calculation(
    tax_return_id: UUID,
    line: str,  # "1040.line24"
    db: AsyncSession = Depends(get_db)
):
    """
    Explain how a line was calculated
    """
    return_data = await get_return(tax_return_id, db)

    # Build provenance chain
    provenance = return_data.provenance.filter(field=line)

    # Generate natural language explanation
    llm_client = ServiceClient("llm")

    response = await llm_client.post("/chat", json={
        "prompt": f"""
        Explain how Form 1040, Line 24 (Total Tax) was calculated:

        Components:
        - Income tax: ${return_data.income_tax}
        - AMT: ${return_data.amt}
        - Self-employment tax: ${return_data.se_tax}
        - Net Investment Income Tax: ${return_data.niit}
        - Credits: -${return_data.credits}

        Total: ${return_data.total_tax}

        Provide a clear, 2-3 sentence explanation suitable for a taxpayer.
        Do not provide tax advice. State facts only.
        """
    })

    return {
        "line": line,
        "value": return_data.total_tax,
        "explanation": response["content"],
        "provenance": provenance
    }
```

**C. Policy Guardrails**:

```python
SYSTEM_PROMPT = """
You are a tax calculation assistant. You provide factual information about tax calculations.

IMPORTANT GUARDRAILS:
- Never provide tax advice or legal opinions
- Never tell users what they "should" do
- Only explain calculations and cite IRS publications
- Always include disclaimer: "This is not tax advice. Consult a licensed tax professional."
- Do not fabricate values or make assumptions
- When uncertain, route to human review
"""
```

### 9. Security & PII Protection

**Field-Level Encryption**:

```python
from cryptography.fernet import Fernet

class TaxReturn(Base):
    __tablename__ = "tax_returns"

    taxpayer_ssn = Column(Text)  # Encrypted at rest
    spouse_ssn = Column(Text)    # Encrypted at rest

    @property
    def taxpayer_ssn(self) -> str:
        encrypted = self.__dict__.get("_taxpayer_ssn")
        if encrypted and cipher_suite:
            return cipher_suite.decrypt(encrypted.encode()).decode()
        return None

    @taxpayer_ssn.setter
    def taxpayer_ssn(self, value: str):
        if value and cipher_suite:
            self.__dict__["_taxpayer_ssn"] = cipher_suite.encrypt(
                value.encode()
            ).decode()
```

**Audit Logging**:

```python
@app.get("/tax-returns/{id}")
async def get_tax_return(
    tax_return_id: UUID,
    user: User = Depends(get_current_user)
):
    # Log every access to PII
    logger.info(
        "Tax return accessed",
        extra={
            "user_id": str(user.id),
            "user_role": user.role.value,
            "tax_return_id": str(tax_return_id),
            "action": "view",
            "ip_address": request.client.host,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    return await tax_return_service.get(tax_return_id, user)
```

**PII Redaction in Logs**:

```python
import re

def redact_pii(message: str) -> str:
    """
    Redact SSNs, EINs from log messages
    """
    # SSN pattern: 123-45-6789
    message = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****', message)

    # EIN pattern: 12-3456789
    message = re.sub(r'\b\d{2}-\d{7}\b', '**-*******', message)

    return message
```

### 10. Event-Driven Coordination

**Event Schemas**:

```python
class TaxDocumentUploadedEvent(BaseEvent):
    event_type: str = "tax.document.uploaded"
    tax_return_id: UUID
    document_id: UUID
    file_url: str
    page_count: int

class TaxDocumentProcessedEvent(BaseEvent):
    event_type: str = "tax.document.processed"
    tax_return_id: UUID
    document_id: UUID
    document_type: str  # "W-2", "1099-INT", etc.
    extracted_fields: Dict[str, Any]
    confidence_avg: float

class TaxCalculationCompletedEvent(BaseEvent):
    event_type: str = "tax.calculation.completed"
    tax_return_id: UUID
    total_tax: Decimal
    balance: Decimal  # Refund (negative) or amount due (positive)

class TaxReturnFiledEvent(BaseEvent):
    event_type: str = "tax.return.filed"
    tax_return_id: UUID
    irs_confirmation_number: str
    filed_at: datetime
```

**Event Flow**:

```
1. User uploads PDF → Publish: tax.document.uploaded
2. tax-ocr-intake subscribes → OCR → Publish: tax.document.processed
3. tax-engine subscribes → Compute → Publish: tax.calculation.completed
4. tax-forms subscribes → Generate PDFs → Publish: tax.forms.generated
5. tax-review subscribes → Check flags → Notify reviewers
```

---

## Consequences

### Positive

1. **Leverages Existing Infrastructure**: Reuses auth, encryption, event bus, LLM, accounting integrations
2. **Modular & Scalable**: Each service can scale independently; state modules plug in easily
3. **Auditable & Compliant**: Full provenance trail; field-level encryption; RBAC; immutable logs
4. **AI-First**: OCR, extraction, deduction suggestions, explanations all AI-powered
5. **Clean Room**: No vendor lock-in; IRS-centric schemas; portable
6. **Testable**: Deterministic calculations; unit test vectors against IRS examples
7. **Incremental Rollout**: Feature flags enable beta testing with select firms

### Negative

1. **Complexity**: 4 new services + extensive rule catalog + 50+ state modules
2. **IRS Compliance Burden**: MeF certification, ETIN registration, annual schema updates
3. **Accuracy Stakes**: Tax errors have legal/financial consequences; requires exhaustive testing
4. **State Tax Variability**: 50 state tax codes with unique rules (phase-in over V2-V5)
5. **OCR Error Risk**: Low-quality scans, handwritten docs may require extensive human review

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| **OCR accuracy < 95%** | Extensive training data; confidence gating; human review queues |
| **Tax calculation errors** | 1000+ unit tests with IRS test vectors; external CPA review |
| **Security breach (PII leak)** | Field-level encryption; audit logs; SOC 2 Type II; penetration testing |
| **IRS schema changes** | Abstraction layer; annual schema update process |
| **Performance (2+ min processing)** | Async pipeline; parallel OCR; caching; horizontal scaling |
| **Scope creep (state taxes)** | V1 = federal only; state modules in V2+ |

---

## Implementation Plan

### Phase 1: Foundation (Weeks 1-2)

- [ ] Database migrations (`0003_tax_preparation.sql`)
- [ ] Service skeletons (health endpoints, OpenAPI specs)
- [ ] Feature flags: `tax.ocr.v1`, `tax.engine.v1`, `tax.forms.v1`
- [ ] CI/CD updates (add 4 services to test matrix)

### Phase 2: OCR Pipeline (Weeks 3-5)

- [ ] Document upload endpoint
- [ ] GPT-4 Vision classification (W-2, 1099 variants, K-1)
- [ ] Field extraction with confidence scoring
- [ ] Mapping to TDS with provenance
- [ ] Review queue for low-confidence fields
- [ ] Unit + integration tests (accuracy benchmarks)

### Phase 3: Tax Engine (Weeks 6-9)

- [ ] Rules engine (2024 tax year data)
- [ ] Form 1040 calculation (line-by-line)
- [ ] Schedules A, B, C, D, E, SE
- [ ] AMT, NIIT, QBI §199A
- [ ] Credits (child tax, EITC, etc.)
- [ ] Carryovers (capital loss, NOL)
- [ ] 1000+ unit tests with IRS examples

### Phase 4: Forms & E-file (Weeks 10-12)

- [ ] Form schemas (1040, schedules)
- [ ] PDF rendering (IRS-compliant templates)
- [ ] Two-way binding (form ↔ TDS)
- [ ] E-file XML generation (MeF schema)
- [ ] Validation layer (800+ IRS business rules)
- [ ] Preflight checks

### Phase 5: Review Workbench (Weeks 13-14)

- [ ] Review flag generation (variance, missing docs)
- [ ] UI for side-by-side doc review
- [ ] Accept/override/reject workflow
- [ ] Prior year import (PDF → AI parsing)
- [ ] Anomaly detection

### Phase 6: Security & Hardening (Weeks 15-16)

- [ ] SSN/EIN encryption audit
- [ ] PII redaction in logs
- [ ] RBAC enforcement (partner/manager/staff roles)
- [ ] Audit log completeness
- [ ] Penetration testing
- [ ] SOC 2 control mapping

### Phase 7: Testing & Benchmarks (Weeks 17-18)

- [ ] Accuracy harness (OCR, extraction, calculation)
- [ ] Performance benchmarks (200-page packet < 2 min)
- [ ] Load testing (100 concurrent users)
- [ ] Synthetic test data (100 sample returns)
- [ ] External CPA review (calculation validation)

### Phase 8: Documentation & Rollout (Weeks 19-20)

- [ ] API documentation (OpenAPI)
- [ ] User guides (CPA workflow)
- [ ] Runbook (troubleshooting)
- [ ] Training materials
- [ ] Beta rollout (5 pilot firms)
- [ ] Observability dashboards (Grafana)
- [ ] Metrics: OCR accuracy, processing time, error rate

---

## Future Enhancements (V2+)

1. **State Tax Modules**: 50 states + DC (prioritize by firm demand: CA, NY, TX, FL)
2. **Corporate Returns**: 1120, 1120-S, 1065
3. **Multi-Year Comparison**: 3-year trend analysis
4. **Tax Planning**: "What-if" scenarios for tax optimization
5. **IRS Notice Response**: AI-assisted response to CP notices
6. **Amended Returns**: 1040-X workflow
7. **Extensions**: Automatic Form 4868 generation
8. **Client Portal Integration**: Self-service doc upload
9. **Mobile App**: Tax doc capture via phone camera
10. **International**: FBAR (FinCEN 114), Form 8938

---

## References

- **IRS Publications**: Pub 17 (Individual Taxes), Pub 542 (Corporate Taxes)
- **IRS Forms**: 1040, 1120, 1065, schedules A-SE
- **MeF Schemas**: https://www.irs.gov/e-file-providers/modernized-e-file-mef-schemas
- **Tax Law**: IRC (Internal Revenue Code), Treasury Regulations
- **Compliance**: SOC 2, GLBA, IRS Circular 230
- **Existing Code**: `/services/accounting-integrations`, `/lib/event_bus`, `/services/llm`

---

## Approval

- [ ] Product Architecture Review
- [ ] Engineering Lead Sign-off
- [ ] Security Review
- [ ] Compliance Review (Legal, CPA)
- [ ] Budget Approval (OpenAI API costs, IRS ETIN fees)
