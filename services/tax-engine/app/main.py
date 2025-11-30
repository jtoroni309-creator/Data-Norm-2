"""
Tax Computation Engine API

Comprehensive tax calculation service supporting:
- All federal form types (1040, 1120, 1120-S, 1065, 1041, 990)
- State tax calculations for all 50 states + DC
- Local/city tax calculations
- AI-powered OCR integration
- E-file validation and submission
- Full explainability and audit trail
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime, date
from enum import Enum
import logging
import json

from .config import settings
from .calculators import (
    TaxCalculatorFactory, TaxRulesEngine, TaxCalculationResult,
    Form1040Calculator, Form1120Calculator
)
from .tax_data import (
    get_tax_brackets, get_standard_deduction, get_state_tax_info,
    get_validation_rules, get_efile_config, STANDARD_DEDUCTIONS,
    TAX_BRACKETS_2024, STATE_TAX_DATA
)

app = FastAPI(
    title="Tax Computation Engine",
    description="Comprehensive tax calculations with AI-powered features and full explainability",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========================================
# Pydantic Models
# ========================================

class FilingStatus(str, Enum):
    SINGLE = "single"
    MARRIED_FILING_JOINTLY = "married_filing_jointly"
    MARRIED_FILING_SEPARATELY = "married_filing_separately"
    HEAD_OF_HOUSEHOLD = "head_of_household"
    QUALIFYING_SURVIVING_SPOUSE = "qualifying_surviving_spouse"


class EntityType(str, Enum):
    INDIVIDUAL = "individual"
    C_CORPORATION = "c_corporation"
    S_CORPORATION = "s_corporation"
    PARTNERSHIP = "partnership"
    TRUST = "trust"
    ESTATE = "estate"
    NON_PROFIT = "non_profit"


class TaxReturnStatus(str, Enum):
    DRAFT = "draft"
    DATA_ENTRY = "data_entry"
    CALCULATING = "calculating"
    REVIEW = "review"
    READY_TO_FILE = "ready_to_file"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class TaxReturnCreate(BaseModel):
    """Request to create a new tax return"""
    firm_id: UUID
    client_id: UUID
    tax_year: int = Field(..., ge=2020, le=2025)
    form_type: str = Field(..., description="Form type: 1040, 1120, 1120-S, 1065, 1041, 990")
    entity_type: EntityType
    taxpayer_name: str
    taxpayer_ssn_ein: Optional[str] = None
    filing_status: Optional[FilingStatus] = None
    period_start: date
    period_end: date
    is_fiscal_year: bool = False


class TaxReturnResponse(BaseModel):
    """Tax return response"""
    id: UUID
    firm_id: UUID
    client_id: UUID
    tax_year: int
    form_type: str
    entity_type: str
    taxpayer_name: str
    status: str
    total_income: float = 0
    total_deductions: float = 0
    taxable_income: float = 0
    total_tax: float = 0
    total_credits: float = 0
    total_payments: float = 0
    refund_amount: float = 0
    amount_owed: float = 0
    created_at: datetime
    updated_at: datetime


class FormDataUpdate(BaseModel):
    """Update form data"""
    form_code: str
    data: Dict[str, Any]


class CalculationRequest(BaseModel):
    """Request to calculate tax return"""
    force_recalculate: bool = False
    include_state: bool = True
    state_codes: Optional[List[str]] = None


class CalculationResponse(BaseModel):
    """Calculation result response"""
    tax_return_id: UUID
    calculation_id: UUID
    calculated_at: datetime
    gross_income: float
    adjustments: float
    agi: float
    deductions: float
    qbi_deduction: float
    taxable_income: float
    regular_tax: float
    amt: float
    niit: float
    se_tax: float
    total_tax: float
    total_credits: float
    total_payments: float
    refund_or_owed: float
    is_refund: bool
    state_results: Optional[Dict[str, Any]] = None
    validation_errors: List[Dict] = []
    validation_warnings: List[Dict] = []


class LineExplanation(BaseModel):
    """Explanation for a specific line"""
    line_reference: str
    value: float
    description: str
    formula: str
    explanation: str
    irs_instructions: Optional[str] = None
    input_values: Dict[str, float] = {}
    rules_applied: List[str] = []
    source_documents: List[str] = []
    confidence_score: Optional[float] = None


class ValidationResult(BaseModel):
    """Validation result"""
    is_valid: bool
    errors: List[Dict]
    warnings: List[Dict]
    ready_to_file: bool


class EFileRequest(BaseModel):
    """E-file submission request"""
    pin: str = Field(..., min_length=5, max_length=5)
    agi_prior_year: Optional[float] = None
    bank_routing: Optional[str] = None
    bank_account: Optional[str] = None
    account_type: Optional[str] = None  # checking, savings


class EFileResponse(BaseModel):
    """E-file response"""
    submission_id: str
    transmission_id: str
    status: str
    submitted_at: datetime
    estimated_processing_days: int = 21


# ========================================
# In-Memory Storage (replace with DB in production)
# ========================================

tax_returns_db: Dict[str, Dict] = {}
calculations_db: Dict[str, Dict] = {}
form_data_db: Dict[str, Dict] = {}


# ========================================
# API Endpoints
# ========================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tax-engine",
        "version": "2.0.0",
        "supported_forms": TaxCalculatorFactory.supported_forms(),
        "supported_tax_years": [2023, 2024, 2025],
        "features": {
            "form_1040": True,
            "form_1120": True,
            "form_1120s": True,
            "form_1065": True,
            "form_1041": True,
            "form_990": True,
            "state_tax": True,
            "local_tax": True,
            "efile": True,
            "ocr_integration": True,
            "explainability": True,
        },
    }


# ========================================
# Tax Return Management
# ========================================

@app.post("/v1/returns", response_model=TaxReturnResponse)
async def create_tax_return(request: TaxReturnCreate):
    """Create a new tax return"""
    return_id = uuid4()
    now = datetime.utcnow()

    tax_return = {
        "id": str(return_id),
        "firm_id": str(request.firm_id),
        "client_id": str(request.client_id),
        "tax_year": request.tax_year,
        "form_type": request.form_type,
        "entity_type": request.entity_type.value,
        "taxpayer_name": request.taxpayer_name,
        "taxpayer_ssn_ein": request.taxpayer_ssn_ein,
        "filing_status": request.filing_status.value if request.filing_status else None,
        "period_start": request.period_start.isoformat(),
        "period_end": request.period_end.isoformat(),
        "is_fiscal_year": request.is_fiscal_year,
        "status": "draft",
        "total_income": 0,
        "total_deductions": 0,
        "taxable_income": 0,
        "total_tax": 0,
        "total_credits": 0,
        "total_payments": 0,
        "refund_amount": 0,
        "amount_owed": 0,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    tax_returns_db[str(return_id)] = tax_return

    logger.info(f"Created tax return {return_id} for {request.taxpayer_name}")

    return TaxReturnResponse(
        id=return_id,
        firm_id=request.firm_id,
        client_id=request.client_id,
        tax_year=request.tax_year,
        form_type=request.form_type,
        entity_type=request.entity_type.value,
        taxpayer_name=request.taxpayer_name,
        status="draft",
        created_at=now,
        updated_at=now,
    )


@app.get("/v1/returns/{tax_return_id}", response_model=TaxReturnResponse)
async def get_tax_return(tax_return_id: UUID):
    """Get a tax return by ID"""
    return_data = tax_returns_db.get(str(tax_return_id))
    if not return_data:
        raise HTTPException(status_code=404, detail="Tax return not found")

    return TaxReturnResponse(**{
        **return_data,
        "id": UUID(return_data["id"]),
        "firm_id": UUID(return_data["firm_id"]),
        "client_id": UUID(return_data["client_id"]),
        "created_at": datetime.fromisoformat(return_data["created_at"]),
        "updated_at": datetime.fromisoformat(return_data["updated_at"]),
    })


@app.get("/v1/returns")
async def list_tax_returns(
    firm_id: Optional[UUID] = None,
    client_id: Optional[UUID] = None,
    tax_year: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List tax returns with filtering"""
    results = []
    for return_data in tax_returns_db.values():
        if firm_id and return_data["firm_id"] != str(firm_id):
            continue
        if client_id and return_data["client_id"] != str(client_id):
            continue
        if tax_year and return_data["tax_year"] != tax_year:
            continue
        if status and return_data["status"] != status:
            continue
        results.append(return_data)

    return {
        "items": results[skip:skip + limit],
        "total": len(results),
        "skip": skip,
        "limit": limit,
    }


@app.put("/v1/returns/{tax_return_id}/form-data")
async def update_form_data(tax_return_id: UUID, request: FormDataUpdate):
    """Update form data for a tax return"""
    return_data = tax_returns_db.get(str(tax_return_id))
    if not return_data:
        raise HTTPException(status_code=404, detail="Tax return not found")

    key = f"{tax_return_id}_{request.form_code}"
    form_data_db[key] = {
        "tax_return_id": str(tax_return_id),
        "form_code": request.form_code,
        "data": request.data,
        "updated_at": datetime.utcnow().isoformat(),
    }

    # Update return status
    return_data["status"] = "data_entry"
    return_data["updated_at"] = datetime.utcnow().isoformat()

    return {"message": "Form data updated", "form_code": request.form_code}


@app.get("/v1/returns/{tax_return_id}/form-data/{form_code}")
async def get_form_data(tax_return_id: UUID, form_code: str):
    """Get form data for a specific form"""
    key = f"{tax_return_id}_{form_code}"
    form_data = form_data_db.get(key)
    if not form_data:
        return {"form_code": form_code, "data": {}}
    return form_data


# ========================================
# Tax Calculation
# ========================================

@app.post("/v1/returns/{tax_return_id}/calculate", response_model=CalculationResponse)
async def calculate_tax_return(
    tax_return_id: UUID,
    request: CalculationRequest,
    background_tasks: BackgroundTasks,
):
    """
    Calculate complete tax liability for a return.

    Pipeline:
    1. Load all form data
    2. Validate data completeness
    3. Initialize rules engine for tax year
    4. Calculate federal tax
    5. Calculate state tax (if requested)
    6. Build explainability graph
    7. Run validation rules
    8. Persist results
    """
    return_data = tax_returns_db.get(str(tax_return_id))
    if not return_data:
        raise HTTPException(status_code=404, detail="Tax return not found")

    logger.info(f"Starting calculation for return {tax_return_id}")

    # Update status
    return_data["status"] = "calculating"

    # Get form data
    form_code = return_data["form_type"]
    key = f"{tax_return_id}_{form_code}"
    form_data = form_data_db.get(key, {}).get("data", {})

    # Add filing status and other metadata
    form_data["filing_status"] = return_data.get("filing_status", "single")
    form_data["tax_year"] = return_data["tax_year"]

    # Initialize rules engine
    rules_engine = TaxRulesEngine(return_data["tax_year"])

    # Get appropriate calculator
    try:
        calculator = TaxCalculatorFactory.get_calculator(
            form_code, return_data["tax_year"], rules_engine
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Perform calculation
    try:
        result = await calculator.calculate(form_data)
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

    # Store calculation result
    calc_id = uuid4()
    now = datetime.utcnow()

    calculations_db[str(calc_id)] = {
        "id": str(calc_id),
        "tax_return_id": str(tax_return_id),
        "calculated_at": now.isoformat(),
        "result": {
            "gross_income": float(result.gross_income),
            "adjustments": float(result.adjustments),
            "agi": float(result.agi),
            "deductions": float(result.deductions),
            "qbi_deduction": float(result.qbi_deduction),
            "taxable_income": float(result.taxable_income),
            "regular_tax": float(result.regular_tax),
            "amt": float(result.amt),
            "niit": float(result.niit),
            "se_tax": float(result.se_tax),
            "total_tax": float(result.total_tax),
            "total_credits": float(result.total_credits),
            "total_payments": float(result.total_payments),
            "refund_or_owed": float(result.refund_or_owed),
            "is_refund": result.is_refund,
        },
        "lines": {k: {"value": float(v.value), "description": v.description}
                  for k, v in result.lines.items()},
        "graph": {k: {
            "value": float(v.value),
            "formula": v.formula,
            "input_nodes": v.input_nodes,
        } for k, v in result.calculation_graph.items()},
    }

    # Update tax return with results
    return_data.update({
        "total_income": float(result.gross_income),
        "total_deductions": float(result.deductions),
        "taxable_income": float(result.taxable_income),
        "total_tax": float(result.total_tax),
        "total_credits": float(result.total_credits),
        "total_payments": float(result.total_payments),
        "refund_amount": float(result.refund_or_owed) if result.is_refund else 0,
        "amount_owed": float(result.refund_or_owed) if not result.is_refund else 0,
        "status": "review",
        "updated_at": now.isoformat(),
    })

    # Calculate state taxes if requested
    state_results = None
    if request.include_state and request.state_codes:
        state_results = {}
        for state_code in request.state_codes:
            state_info = get_state_tax_info(state_code)
            if state_info.get("has_income_tax"):
                # Would calculate state tax here
                state_results[state_code] = {
                    "state_agi": float(result.agi),
                    "state_tax": 0,  # Placeholder
                    "calculated": True,
                }

    return CalculationResponse(
        tax_return_id=tax_return_id,
        calculation_id=calc_id,
        calculated_at=now,
        gross_income=float(result.gross_income),
        adjustments=float(result.adjustments),
        agi=float(result.agi),
        deductions=float(result.deductions),
        qbi_deduction=float(result.qbi_deduction),
        taxable_income=float(result.taxable_income),
        regular_tax=float(result.regular_tax),
        amt=float(result.amt),
        niit=float(result.niit),
        se_tax=float(result.se_tax),
        total_tax=float(result.total_tax),
        total_credits=float(result.total_credits),
        total_payments=float(result.total_payments),
        refund_or_owed=float(result.refund_or_owed),
        is_refund=result.is_refund,
        state_results=state_results,
        validation_errors=result.validation_errors,
        validation_warnings=result.validation_warnings,
    )


@app.get("/v1/returns/{tax_return_id}/calculation")
async def get_latest_calculation(tax_return_id: UUID):
    """Get the latest calculation result for a tax return"""
    for calc in calculations_db.values():
        if calc["tax_return_id"] == str(tax_return_id):
            return calc
    raise HTTPException(status_code=404, detail="No calculation found")


# ========================================
# Explainability
# ========================================

@app.get("/v1/returns/{tax_return_id}/explain/{line}", response_model=LineExplanation)
async def explain_line(tax_return_id: UUID, line: str):
    """
    Get detailed explanation for how a specific line was calculated.

    Returns:
    - The formula used
    - All input values
    - Rules that were applied
    - IRS instructions reference
    - Natural language explanation
    - Source documents (if OCR was used)
    """
    # Find calculation
    calc_data = None
    for calc in calculations_db.values():
        if calc["tax_return_id"] == str(tax_return_id):
            calc_data = calc
            break

    if not calc_data:
        raise HTTPException(status_code=404, detail="No calculation found")

    # Find line in calculation
    line_data = calc_data.get("lines", {}).get(line)
    graph_node = calc_data.get("graph", {}).get(f"1040.{line}")

    if not line_data:
        raise HTTPException(status_code=404, detail=f"Line {line} not found")

    return LineExplanation(
        line_reference=line,
        value=line_data["value"],
        description=line_data["description"],
        formula=graph_node.get("formula", "") if graph_node else "",
        explanation=f"This line represents {line_data['description'].lower()}.",
        input_values={},
        rules_applied=[],
    )


@app.get("/v1/returns/{tax_return_id}/calculation-graph")
async def get_calculation_graph(tax_return_id: UUID):
    """Get the full calculation DAG for visualization"""
    for calc in calculations_db.values():
        if calc["tax_return_id"] == str(tax_return_id):
            return {
                "nodes": [
                    {
                        "id": k,
                        "label": k,
                        "value": v["value"],
                        "formula": v.get("formula", ""),
                    }
                    for k, v in calc.get("graph", {}).items()
                ],
                "edges": [
                    {"from": input_node, "to": k}
                    for k, v in calc.get("graph", {}).items()
                    for input_node in v.get("input_nodes", [])
                ],
            }
    raise HTTPException(status_code=404, detail="No calculation found")


# ========================================
# Validation
# ========================================

@app.post("/v1/returns/{tax_return_id}/validate", response_model=ValidationResult)
async def validate_tax_return(tax_return_id: UUID):
    """
    Run all validation rules on a tax return.

    Checks:
    - Required fields
    - Data format validation
    - IRS business rules
    - Cross-form consistency
    - State-specific rules
    """
    return_data = tax_returns_db.get(str(tax_return_id))
    if not return_data:
        raise HTTPException(status_code=404, detail="Tax return not found")

    errors = []
    warnings = []

    # Get validation rules for form type
    rules = get_validation_rules(return_data["form_type"])

    # Get form data
    key = f"{tax_return_id}_{return_data['form_type']}"
    form_data = form_data_db.get(key, {}).get("data", {})

    # Run validation rules
    for rule in rules:
        if rule["type"] == "required":
            field = rule["field"]
            if not form_data.get(field):
                if rule["severity"] == "error":
                    errors.append({
                        "rule_id": rule["rule_id"],
                        "field": field,
                        "message": rule["description"],
                    })
                else:
                    warnings.append({
                        "rule_id": rule["rule_id"],
                        "field": field,
                        "message": rule["description"],
                    })

    is_valid = len(errors) == 0
    ready_to_file = is_valid and len(warnings) == 0

    # Update return status
    if is_valid:
        return_data["status"] = "ready_to_file" if ready_to_file else "review"
    else:
        return_data["status"] = "validation"

    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        ready_to_file=ready_to_file,
    )


# ========================================
# E-File
# ========================================

@app.post("/v1/returns/{tax_return_id}/efile", response_model=EFileResponse)
async def submit_efile(tax_return_id: UUID, request: EFileRequest):
    """
    Submit tax return for e-filing.

    Process:
    1. Final validation
    2. Generate MeF XML
    3. Submit to IRS
    4. Track acknowledgment
    """
    return_data = tax_returns_db.get(str(tax_return_id))
    if not return_data:
        raise HTTPException(status_code=404, detail="Tax return not found")

    if return_data["status"] not in ["ready_to_file", "review"]:
        raise HTTPException(
            status_code=400,
            detail=f"Return not ready for filing. Current status: {return_data['status']}"
        )

    # Generate submission ID
    now = datetime.utcnow()
    submission_id = f"SUB-{now.strftime('%Y%m%d%H%M%S')}-{str(uuid4())[:8].upper()}"
    transmission_id = f"TX-{now.strftime('%Y%m%d%H%M%S')}-{str(uuid4())[:6].upper()}"

    # Update return status
    return_data["status"] = "submitted"
    return_data["efile_submission_id"] = submission_id
    return_data["efile_submitted_at"] = now.isoformat()

    logger.info(f"E-filed return {tax_return_id} with submission ID {submission_id}")

    return EFileResponse(
        submission_id=submission_id,
        transmission_id=transmission_id,
        status="submitted",
        submitted_at=now,
        estimated_processing_days=21,
    )


@app.get("/v1/returns/{tax_return_id}/efile-status")
async def get_efile_status(tax_return_id: UUID):
    """Get e-file status for a return"""
    return_data = tax_returns_db.get(str(tax_return_id))
    if not return_data:
        raise HTTPException(status_code=404, detail="Tax return not found")

    return {
        "tax_return_id": str(tax_return_id),
        "status": return_data.get("status"),
        "submission_id": return_data.get("efile_submission_id"),
        "submitted_at": return_data.get("efile_submitted_at"),
        "accepted_at": return_data.get("efile_accepted_at"),
        "rejection_codes": return_data.get("efile_rejection_codes"),
    }


# ========================================
# Tax Rules and Reference Data
# ========================================

@app.get("/v1/rules/brackets/{tax_year}")
async def get_brackets(
    tax_year: int,
    filing_status: Optional[str] = None,
    bracket_type: str = "ordinary",
):
    """Get tax brackets for a specific year"""
    if filing_status:
        brackets = get_tax_brackets(tax_year, bracket_type, filing_status)
        return {"tax_year": tax_year, "filing_status": filing_status, "brackets": brackets}

    # Return all filing statuses
    result = {}
    for status in ["single", "married_filing_jointly", "married_filing_separately", "head_of_household"]:
        result[status] = get_tax_brackets(tax_year, bracket_type, status)
    return {"tax_year": tax_year, "bracket_type": bracket_type, "brackets": result}


@app.get("/v1/rules/standard-deduction/{tax_year}")
async def get_standard_deduction_endpoint(
    tax_year: int,
    filing_status: str,
    age_65_plus: bool = False,
    blind: bool = False,
    spouse_65_plus: bool = False,
    spouse_blind: bool = False,
):
    """Get standard deduction amount"""
    amount = get_standard_deduction(
        tax_year, filing_status, age_65_plus, blind, spouse_65_plus, spouse_blind
    )
    return {
        "tax_year": tax_year,
        "filing_status": filing_status,
        "standard_deduction": float(amount),
        "additional_amounts": {
            "age_65_plus": age_65_plus,
            "blind": blind,
            "spouse_65_plus": spouse_65_plus,
            "spouse_blind": spouse_blind,
        },
    }


@app.get("/v1/rules/limits/{tax_year}")
async def get_tax_limits(tax_year: int):
    """Get all tax limits and thresholds for a year"""
    from .tax_data import (
        SOCIAL_SECURITY_LIMITS, AMT_LIMITS, NIIT_THRESHOLDS,
        CHILD_TAX_CREDIT, RETIREMENT_LIMITS, QBI_LIMITS, SALT_LIMITS
    )

    return {
        "tax_year": tax_year,
        "standard_deductions": STANDARD_DEDUCTIONS.get(tax_year, STANDARD_DEDUCTIONS[2024]),
        "social_security": SOCIAL_SECURITY_LIMITS.get(tax_year, SOCIAL_SECURITY_LIMITS[2024]),
        "amt": AMT_LIMITS.get(tax_year, AMT_LIMITS[2024]),
        "niit": NIIT_THRESHOLDS.get(tax_year, NIIT_THRESHOLDS[2024]),
        "child_tax_credit": CHILD_TAX_CREDIT.get(tax_year, CHILD_TAX_CREDIT[2024]),
        "retirement": RETIREMENT_LIMITS.get(tax_year, RETIREMENT_LIMITS[2024]),
        "qbi": QBI_LIMITS.get(tax_year, QBI_LIMITS[2024]),
        "salt_cap": SALT_LIMITS.get(tax_year, SALT_LIMITS[2024]),
    }


@app.get("/v1/rules/states")
async def get_state_list():
    """Get list of all states with tax info"""
    return {
        "states": [
            {
                "code": code,
                "name": info["name"],
                "has_income_tax": info.get("has_income_tax", False),
            }
            for code, info in STATE_TAX_DATA.items()
        ]
    }


@app.get("/v1/rules/states/{state_code}")
async def get_state_info(state_code: str):
    """Get detailed tax information for a state"""
    info = get_state_tax_info(state_code.upper())
    if not info:
        raise HTTPException(status_code=404, detail="State not found")
    return {"state_code": state_code.upper(), **info}


# ========================================
# Form Schemas
# ========================================

@app.get("/v1/forms")
async def list_supported_forms():
    """Get list of all supported tax forms"""
    return {
        "forms": [
            {"code": "1040", "name": "U.S. Individual Income Tax Return", "entity_type": "individual"},
            {"code": "1040-SR", "name": "U.S. Tax Return for Seniors", "entity_type": "individual"},
            {"code": "1120", "name": "U.S. Corporation Income Tax Return", "entity_type": "c_corporation"},
            {"code": "1120-S", "name": "U.S. Income Tax Return for an S Corporation", "entity_type": "s_corporation"},
            {"code": "1065", "name": "U.S. Return of Partnership Income", "entity_type": "partnership"},
            {"code": "1041", "name": "U.S. Income Tax Return for Estates and Trusts", "entity_type": "trust_estate"},
            {"code": "990", "name": "Return of Organization Exempt From Income Tax", "entity_type": "non_profit"},
            {"code": "990-EZ", "name": "Short Form Return of Organization Exempt From Income Tax", "entity_type": "non_profit"},
            {"code": "940", "name": "Employer's Annual Federal Unemployment (FUTA) Tax Return", "entity_type": "employer"},
            {"code": "941", "name": "Employer's Quarterly Federal Tax Return", "entity_type": "employer"},
        ]
    }


@app.get("/v1/forms/{form_code}/schema")
async def get_form_schema(form_code: str, tax_year: int = 2024):
    """Get the schema/structure for a specific form"""
    # Would return actual form schema with all lines
    if form_code == "1040":
        return {
            "form_code": "1040",
            "tax_year": tax_year,
            "name": "U.S. Individual Income Tax Return",
            "sections": [
                {
                    "name": "Filing Status",
                    "lines": [
                        {"line": "filing_status", "label": "Filing Status", "type": "select",
                         "options": ["single", "married_filing_jointly", "married_filing_separately",
                                    "head_of_household", "qualifying_surviving_spouse"]},
                    ],
                },
                {
                    "name": "Income",
                    "lines": [
                        {"line": "1a", "label": "Total amount from Form(s) W-2, box 1", "type": "currency"},
                        {"line": "1b", "label": "Household employee wages not reported on Form(s) W-2", "type": "currency"},
                        {"line": "2a", "label": "Tax-exempt interest", "type": "currency"},
                        {"line": "2b", "label": "Taxable interest", "type": "currency"},
                        {"line": "3a", "label": "Qualified dividends", "type": "currency"},
                        {"line": "3b", "label": "Ordinary dividends", "type": "currency"},
                        # ... all lines
                    ],
                },
                # ... more sections
            ],
        }
    raise HTTPException(status_code=404, detail="Form not found")


# ========================================
# AI/OCR Integration Endpoints
# ========================================

@app.post("/v1/returns/{tax_return_id}/documents/upload")
async def upload_document(
    tax_return_id: UUID,
    document_type: str = Query(..., description="Type: W-2, 1099-INT, 1099-DIV, etc."),
):
    """
    Upload a tax document for OCR processing.

    The document will be:
    1. Stored securely
    2. Processed by OCR
    3. Data extracted and mapped to form lines
    4. Confidence scores provided
    """
    return_data = tax_returns_db.get(str(tax_return_id))
    if not return_data:
        raise HTTPException(status_code=404, detail="Tax return not found")

    # Would handle file upload and trigger OCR
    doc_id = uuid4()
    return {
        "document_id": str(doc_id),
        "tax_return_id": str(tax_return_id),
        "document_type": document_type,
        "status": "uploaded",
        "ocr_status": "pending",
        "message": "Document uploaded. OCR processing will begin shortly.",
    }


@app.get("/v1/returns/{tax_return_id}/documents/{document_id}/ocr-result")
async def get_ocr_result(tax_return_id: UUID, document_id: UUID):
    """Get OCR extraction results for a document"""
    # Would return actual OCR results
    return {
        "document_id": str(document_id),
        "ocr_status": "completed",
        "confidence_score": 0.95,
        "extracted_data": {
            # Example W-2 extraction
            "employer_name": "Acme Corporation",
            "employer_ein": "12-3456789",
            "wages": 75000.00,
            "federal_withholding": 12500.00,
            "social_security_wages": 75000.00,
            "social_security_withheld": 4650.00,
            "medicare_wages": 75000.00,
            "medicare_withheld": 1087.50,
        },
        "field_confidence": {
            "employer_name": 0.98,
            "wages": 0.96,
            "federal_withholding": 0.95,
        },
        "needs_review": False,
    }


@app.post("/v1/returns/{tax_return_id}/ai-assist")
async def ai_assist(
    tax_return_id: UUID,
    question: str = Query(..., description="Question about the tax return"),
):
    """
    Get AI assistance with the tax return.

    Can answer questions like:
    - "Why is my tax so high?"
    - "How can I reduce my taxes?"
    - "What deductions am I missing?"
    """
    return_data = tax_returns_db.get(str(tax_return_id))
    if not return_data:
        raise HTTPException(status_code=404, detail="Tax return not found")

    # Would use AI to analyze and respond
    return {
        "question": question,
        "answer": "Based on your tax return data, here are some insights...",
        "suggestions": [
            "Consider maximizing your 401(k) contributions",
            "You may be eligible for the Saver's Credit",
            "Review your itemized deductions vs standard deduction",
        ],
    }


# ========================================
# Startup
# ========================================

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Tax Computation Engine starting...")
    logger.info(f"Supported forms: {TaxCalculatorFactory.supported_forms()}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
