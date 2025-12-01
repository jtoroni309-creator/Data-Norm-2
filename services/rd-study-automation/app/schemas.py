"""
Pydantic schemas for R&D Study Automation Service API validation.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from .models import (
    StudyStatus, EntityType, CreditMethod, QualificationStatus,
    QRECategory, DocumentType, ConfidenceLevel, RiskFlag, UserRole
)


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True
    )


class PaginatedResponse(BaseSchema):
    """Standard paginated response."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


class ErrorResponse(BaseSchema):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


# =============================================================================
# STUDY SCHEMAS
# =============================================================================

class StudyCreate(BaseSchema):
    """Create a new R&D study."""
    name: str = Field(..., min_length=1, max_length=500)
    client_id: Optional[Union[UUID, str]] = None  # Optional - will be generated if not provided
    client_name: Optional[str] = None  # Human-readable client name for display
    engagement_id: Optional[UUID] = None
    tax_year: int = Field(..., ge=2000, le=2100)
    entity_type: EntityType
    entity_name: str = Field(..., min_length=1, max_length=500)
    ein: Optional[str] = Field(None, pattern=r"^\d{2}-\d{7}$")
    fiscal_year_start: Optional[date] = None  # Will default based on tax_year
    fiscal_year_end: Optional[date] = None  # Will default based on tax_year
    is_short_year: bool = False
    short_year_days: Optional[int] = None
    is_controlled_group: bool = False
    controlled_group_name: Optional[str] = None
    aggregation_method: Optional[str] = None
    states: List[str] = Field(default_factory=list)
    primary_state: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("states")
    @classmethod
    def validate_states(cls, v):
        valid_states = {
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
        }
        for state in v:
            if state.upper() not in valid_states:
                raise ValueError(f"Invalid state code: {state}")
        return [s.upper() for s in v]


class StudyUpdate(BaseSchema):
    """Update an existing R&D study."""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    entity_name: Optional[str] = Field(None, min_length=1, max_length=500)
    fiscal_year_start: Optional[date] = None
    fiscal_year_end: Optional[date] = None
    is_short_year: Optional[bool] = None
    short_year_days: Optional[int] = None
    is_controlled_group: Optional[bool] = None
    controlled_group_name: Optional[str] = None
    aggregation_method: Optional[str] = None
    states: Optional[List[str]] = None
    primary_state: Optional[str] = None
    selected_method: Optional[CreditMethod] = None
    method_selection_reason: Optional[str] = None
    notes: Optional[str] = None
    assumptions: Optional[List[Dict[str, Any]]] = None
    limitations: Optional[List[Dict[str, Any]]] = None


class StudyStatusTransition(BaseSchema):
    """Transition study to new status."""
    new_status: StudyStatus
    notes: Optional[str] = None


class StudyCPAApproval(BaseSchema):
    """CPA approval for study."""
    approved: bool
    notes: Optional[str] = None


class StudySummary(BaseSchema):
    """Summary view of a study."""
    id: UUID
    name: str
    client_id: UUID
    tax_year: int
    entity_name: str
    entity_type: EntityType
    status: StudyStatus
    total_qre: Decimal
    federal_credit_final: Decimal
    total_state_credits: Decimal
    total_credits: Decimal
    has_open_flags: bool
    cpa_approved: bool
    created_at: datetime


class StudyResponse(BaseSchema):
    """Full study response."""
    id: UUID
    firm_id: UUID
    client_id: UUID
    engagement_id: Optional[UUID]
    name: str
    tax_year: int
    study_type: str
    entity_type: EntityType
    entity_name: str
    ein: Optional[str]
    fiscal_year_start: date
    fiscal_year_end: date
    is_short_year: bool
    short_year_days: Optional[int]
    is_controlled_group: bool
    controlled_group_id: Optional[UUID]
    controlled_group_name: Optional[str]
    aggregation_method: Optional[str]
    status: StudyStatus
    status_history: List[Dict[str, Any]]
    recommended_method: Optional[CreditMethod]
    selected_method: Optional[CreditMethod]
    method_selection_reason: Optional[str]
    states: List[str]
    primary_state: Optional[str]
    ai_risk_score: Optional[float]
    ai_opportunity_score: Optional[float]
    ai_suggested_areas: Optional[Dict[str, Any]] = None
    ai_analysis_summary: Optional[str]
    total_qre: Decimal
    federal_credit_regular: Decimal
    federal_credit_asc: Decimal
    federal_credit_final: Decimal
    total_state_credits: Decimal
    total_credits: Decimal
    prior_credit_carryforward: Decimal
    risk_flags: List[Dict[str, Any]]
    has_open_flags: bool
    rules_version: Optional[str]
    notes: Optional[str]
    assumptions: List[Dict[str, Any]]
    limitations: List[Dict[str, Any]]
    requires_cpa_approval: bool
    cpa_approved: bool
    cpa_approved_by: Optional[UUID]
    cpa_approved_at: Optional[datetime]
    cpa_approval_notes: Optional[str]
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    finalized_at: Optional[datetime]
    locked_at: Optional[datetime]


# =============================================================================
# INTAKE/SCOPING SCHEMAS
# =============================================================================

class IntakeWizardStep1(BaseSchema):
    """Step 1: Basic study information."""
    client_id: UUID
    name: str
    tax_year: int
    entity_type: EntityType
    entity_name: str
    ein: Optional[str] = None
    fiscal_year_start: date
    fiscal_year_end: date
    is_short_year: bool = False
    short_year_days: Optional[int] = None


class IntakeWizardStep2(BaseSchema):
    """Step 2: Controlled group and aggregation."""
    is_controlled_group: bool = False
    controlled_group_name: Optional[str] = None
    related_entities: List[Dict[str, Any]] = Field(default_factory=list)
    aggregation_method: Optional[str] = None  # standalone, aggregated, allocated


class IntakeWizardStep3(BaseSchema):
    """Step 3: State nexus."""
    states: List[str] = Field(default_factory=list)
    primary_state: Optional[str] = None
    state_activities: Dict[str, List[str]] = Field(default_factory=dict)  # {state: [activities]}


class IntakeWizardStep4(BaseSchema):
    """Step 4: Business areas and initial scoping."""
    industry: str
    industry_naics: Optional[str] = None
    business_description: str
    rd_activities_description: str
    departments_involved: List[str] = Field(default_factory=list)
    estimated_rd_headcount: Optional[int] = None
    estimated_rd_spend: Optional[Decimal] = None


class IntakeWizardComplete(BaseSchema):
    """Complete intake wizard submission."""
    step1: IntakeWizardStep1
    step2: IntakeWizardStep2
    step3: IntakeWizardStep3
    step4: IntakeWizardStep4


class AIScopingResult(BaseSchema):
    """AI scoping analysis result."""
    suggested_qualifying_areas: List[Dict[str, Any]]
    risk_opportunity_map: Dict[str, Any]
    estimated_credit_range: Dict[str, Decimal]
    recommended_focus_areas: List[str]
    potential_issues: List[Dict[str, Any]]
    confidence_score: float


# =============================================================================
# PROJECT SCHEMAS
# =============================================================================

class ProjectCreate(BaseSchema):
    """Create a new R&D project."""
    name: str = Field(..., min_length=1, max_length=500)
    code: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    department: Optional[str] = None
    business_component: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_ongoing: bool = True


class ProjectUpdate(BaseSchema):
    """Update an existing project."""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    code: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    business_component: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_ongoing: Optional[bool] = None
    qualification_status: Optional[QualificationStatus] = None


class ProjectQualificationOverride(BaseSchema):
    """CPA override for project qualification."""
    override_status: QualificationStatus
    reason: str = Field(..., min_length=10)


class FourPartTestResult(BaseSchema):
    """Result of Federal 4-part test evaluation."""
    permitted_purpose: Dict[str, Any]
    technological_nature: Dict[str, Any]
    elimination_of_uncertainty: Dict[str, Any]
    process_of_experimentation: Dict[str, Any]
    overall_score: float
    overall_confidence: ConfidenceLevel
    qualification_status: QualificationStatus
    evidence_summary: List[Dict[str, Any]]
    risk_factors: List[Dict[str, Any]]
    narrative: str


class ProjectResponse(BaseSchema):
    """Full project response."""
    id: UUID
    study_id: UUID
    name: str
    code: Optional[str]
    description: Optional[str]
    department: Optional[str]
    business_component: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    is_ongoing: bool
    qualification_status: QualificationStatus
    permitted_purpose_score: Optional[float]
    permitted_purpose_narrative: Optional[str]
    technological_nature_score: Optional[float]
    technological_nature_narrative: Optional[str]
    uncertainty_score: Optional[float]
    uncertainty_narrative: Optional[str]
    experimentation_score: Optional[float]
    experimentation_narrative: Optional[str]
    overall_score: Optional[float]
    overall_confidence: Optional[ConfidenceLevel]
    qualification_narrative: Optional[str]
    state_qualifications: Dict[str, Any]
    cpa_reviewed: bool
    cpa_override_status: Optional[QualificationStatus]
    cpa_override_reason: Optional[str]
    risk_flags: List[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]


class ProjectSummary(BaseSchema):
    """Summary view of a project."""
    id: UUID
    name: str
    code: Optional[str]
    department: Optional[str]
    qualification_status: QualificationStatus
    overall_score: Optional[float]
    cpa_reviewed: bool
    has_risk_flags: bool


# =============================================================================
# EMPLOYEE SCHEMAS
# =============================================================================

class EmployeeCreate(BaseSchema):
    """Create a new employee record."""
    employee_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=300)
    title: Optional[str] = None
    department: Optional[str] = None
    state: Optional[str] = Field(None, min_length=2, max_length=2, description="2-letter state code")
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    total_wages: Decimal = Field(default=Decimal("0"))
    w2_wages: Decimal = Field(default=Decimal("0"))
    bonus: Decimal = Field(default=Decimal("0"))
    stock_compensation: Decimal = Field(default=Decimal("0"))
    qualified_time_percentage: float = Field(default=0, ge=0, le=100)
    qualified_time_source: Optional[str] = Field(None, description="Source: time_study, project_records, manager_estimate")
    project_id: Optional[UUID] = Field(None, description="Primary project assignment")


class EmployeeUpdate(BaseSchema):
    """Update an existing employee."""
    employee_id: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    total_wages: Optional[Decimal] = None
    w2_wages: Optional[Decimal] = None
    bonus: Optional[Decimal] = None
    qualified_time_percentage: Optional[float] = None
    qualified_time_source: Optional[str] = None
    role_category: Optional[str] = None


class EmployeeTimeAdjustment(BaseSchema):
    """CPA adjustment for employee qualified time."""
    adjusted_percentage: float = Field(..., ge=0, le=100)
    reason: str = Field(..., min_length=10)


class EmployeeResponse(BaseSchema):
    """Full employee response."""
    id: UUID
    study_id: UUID
    employee_id: Optional[str]
    name: str
    title: Optional[str]
    department: Optional[str]
    hire_date: Optional[date]
    termination_date: Optional[date]
    total_wages: Decimal
    w2_wages: Decimal
    bonus: Decimal
    stock_compensation: Decimal
    qualified_time_percentage: float
    qualified_time_source: Optional[str]
    qualified_time_confidence: Optional[ConfidenceLevel]
    qualified_wages: Decimal
    role_category: Optional[str]
    rd_role_description: Optional[str]
    employee_narrative: Optional[str]
    narrative_confidence: Optional[float]
    cpa_reviewed: bool
    cpa_adjusted_percentage: Optional[float]
    cpa_adjustment_reason: Optional[str]
    risk_flags: List[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]


class ProjectEmployeeAllocationCreate(BaseSchema):
    """Allocate employee time to project."""
    employee_id: UUID
    allocation_percentage: float = Field(..., ge=0, le=100)
    source: Optional[str] = None


# =============================================================================
# QRE SCHEMAS
# =============================================================================

class QRECreate(BaseSchema):
    """Create a new QRE record."""
    category: QRECategory
    subcategory: Optional[str] = None
    project_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    gross_amount: Decimal
    qualified_percentage: float = Field(default=100, ge=0, le=100)

    # For wages
    is_w2_wages: bool = True

    # For supplies
    supply_description: Optional[str] = None
    supply_vendor: Optional[str] = None
    gl_account: Optional[str] = None

    # For contract research
    contractor_name: Optional[str] = None
    contractor_ein: Optional[str] = None
    is_qualified_research_org: bool = False
    contract_percentage: float = Field(default=65, ge=0, le=100)

    # Source
    source_reference: Optional[str] = None


class QREUpdate(BaseSchema):
    """Update an existing QRE."""
    category: Optional[QRECategory] = None
    project_id: Optional[UUID] = None
    gross_amount: Optional[Decimal] = None
    qualified_percentage: Optional[float] = None
    supply_description: Optional[str] = None
    contractor_name: Optional[str] = None
    source_reference: Optional[str] = None


class QREAdjustment(BaseSchema):
    """CPA adjustment for QRE."""
    adjusted_amount: Decimal
    reason: str = Field(..., min_length=10)


class QREResponse(BaseSchema):
    """Full QRE response."""
    id: UUID
    study_id: UUID
    project_id: Optional[UUID]
    employee_id: Optional[UUID]
    category: QRECategory
    subcategory: Optional[str]
    is_w2_wages: bool
    supply_description: Optional[str]
    supply_vendor: Optional[str]
    gl_account: Optional[str]
    contractor_name: Optional[str]
    contractor_ein: Optional[str]
    is_qualified_research_org: bool
    contract_percentage: float
    gross_amount: Decimal
    qualified_percentage: float
    qualified_amount: Decimal
    state_allocation: Dict[str, Decimal]
    source_reference: Optional[str]
    ai_confidence: Optional[float]
    ai_classification_reason: Optional[str]
    cpa_reviewed: bool
    cpa_adjusted_amount: Optional[Decimal]
    cpa_adjustment_reason: Optional[str]
    risk_flags: List[Dict[str, Any]]
    created_at: datetime


class QRESummary(BaseSchema):
    """Summary of QREs by category."""
    category: QRECategory
    count: int
    gross_total: Decimal
    qualified_total: Decimal
    average_qualification_rate: float


# =============================================================================
# CALCULATION SCHEMAS
# =============================================================================

class CalculationRequest(BaseSchema):
    """Request to run credit calculation."""
    method: Optional[CreditMethod] = None  # If None, calculate both
    include_states: bool = True
    base_period_data: Optional[Dict[int, Dict[str, Decimal]]] = None  # Override base period


class CalculationStep(BaseSchema):
    """Individual calculation step for audit trail."""
    step_number: int
    description: str
    formula: str
    inputs: Dict[str, Any]
    result: Any
    notes: Optional[str] = None


class FederalCalculationResult(BaseSchema):
    """Federal R&D credit calculation result."""
    method: CreditMethod
    total_qre_wages: Decimal
    total_qre_supplies: Decimal
    total_qre_contract: Decimal
    total_qre_basic_research: Decimal
    total_qre: Decimal
    base_period_data: Dict[str, Any]
    base_amount: Decimal
    fixed_base_percentage: Optional[float]
    average_annual_gross_receipts: Optional[Decimal]
    credit_rate: float
    excess_qre: Decimal
    calculated_credit: Decimal
    section_280c_reduction: Decimal
    controlled_group_allocation: float
    final_credit: Decimal
    is_qualified_small_business: bool
    payroll_tax_offset_amount: Decimal
    calculation_steps: List[CalculationStep]


class StateCalculationResult(BaseSchema):
    """State R&D credit calculation result."""
    state_code: str
    state_name: str
    rules_version: str
    state_total_qre: Decimal
    state_credit_rate: float
    state_base_amount: Decimal
    state_excess_qre: Decimal
    calculated_credit: Decimal
    state_adjustments: Dict[str, Any]
    final_credit: Decimal
    carryforward_years: Optional[int]
    calculation_steps: List[CalculationStep]


class CalculationComparison(BaseSchema):
    """Comparison of Regular vs ASC methods."""
    regular_credit: Decimal
    asc_credit: Decimal
    difference: Decimal
    recommended_method: CreditMethod
    recommendation_reason: str


class FullCalculationResponse(BaseSchema):
    """Complete calculation response."""
    study_id: UUID
    calculated_at: datetime
    federal_regular: Optional[FederalCalculationResult]
    federal_asc: Optional[FederalCalculationResult]
    comparison: Optional[CalculationComparison]
    state_calculations: List[StateCalculationResult]
    total_federal_credit: Decimal
    total_state_credits: Decimal
    total_credits: Decimal
    recommended_method: CreditMethod


# =============================================================================
# DOCUMENT SCHEMAS
# =============================================================================

class DocumentUpload(BaseSchema):
    """Document upload request."""
    document_type: Optional[DocumentType] = None
    description: Optional[str] = None


class DocumentProcessingStatus(BaseSchema):
    """Document processing status."""
    id: UUID
    filename: str
    status: str
    progress: float  # 0-100
    current_step: Optional[str] = None
    error: Optional[str] = None


class DocumentResponse(BaseSchema):
    """Full document response."""
    id: UUID
    study_id: UUID
    filename: str
    original_filename: str
    file_size: Optional[int]
    mime_type: Optional[str]
    document_type: Optional[DocumentType]
    ai_document_type: Optional[DocumentType]
    processing_status: str
    ocr_completed: bool
    ocr_confidence: Optional[float]
    ai_extracted_data: Dict[str, Any]
    extracted_tables: List[Dict[str, Any]]
    identified_employees: List[Dict[str, Any]]
    identified_projects: List[Dict[str, Any]]
    missing_fields: List[str]
    follow_up_questions: List[Dict[str, Any]]
    uploaded_at: datetime
    processed_at: Optional[datetime]


class DataIngestionResult(BaseSchema):
    """Result of AI data ingestion."""
    documents_processed: int
    employees_identified: int
    projects_identified: int
    qres_extracted: int
    confidence_score: float
    missing_data: List[Dict[str, Any]]
    follow_up_questions: List[Dict[str, Any]]
    warnings: List[str]


# =============================================================================
# INTERVIEW SCHEMAS
# =============================================================================

class InterviewCreate(BaseSchema):
    """Create a new interview."""
    interview_type: str
    interviewee_name: Optional[str] = None
    interviewee_title: Optional[str] = None
    interviewee_employee_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None


class InterviewMessage(BaseSchema):
    """Single interview message."""
    role: str  # user, assistant, system
    content: str
    timestamp: Optional[datetime] = None


class InterviewContinue(BaseSchema):
    """Continue an interview session."""
    message: str


class InterviewResponse(BaseSchema):
    """Full interview response."""
    id: UUID
    study_id: UUID
    interview_type: str
    interviewee_name: Optional[str]
    interviewee_title: Optional[str]
    status: str
    interview_mode: str
    transcript: List[Dict[str, Any]]
    summary: Optional[str]
    extracted_projects: List[Dict[str, Any]]
    extracted_activities: List[Dict[str, Any]]
    extracted_time_allocations: List[Dict[str, Any]]
    overall_confidence: Optional[float]
    needs_follow_up: bool
    follow_up_topics: List[str]
    created_at: datetime
    completed_at: Optional[datetime]


class AIInterviewQuestion(BaseSchema):
    """AI-generated interview question."""
    question: str
    category: str  # project, activity, time, uncertainty, experimentation
    priority: int
    context: Optional[str] = None


# =============================================================================
# NARRATIVE SCHEMAS
# =============================================================================

class NarrativeGenerateRequest(BaseSchema):
    """Request to generate narratives."""
    narrative_types: List[str]  # executive_summary, project, employee, qualification
    entity_ids: Optional[List[UUID]] = None  # For project/employee narratives
    regenerate: bool = False  # Force regeneration


class NarrativeUpdate(BaseSchema):
    """Update/edit a narrative."""
    content: str
    edit_reason: Optional[str] = None


class NarrativeResponse(BaseSchema):
    """Full narrative response."""
    id: UUID
    study_id: UUID
    narrative_type: str
    entity_id: Optional[UUID]
    entity_type: Optional[str]
    title: Optional[str]
    content: str
    content_html: Optional[str]
    evidence_citations: List[Dict[str, Any]]
    ai_generated: bool
    ai_confidence: Optional[float]
    reviewed: bool
    cpa_edited: bool
    cpa_edited_content: Optional[str]
    version: int
    created_at: datetime
    updated_at: Optional[datetime]


# =============================================================================
# EVIDENCE SCHEMAS
# =============================================================================

class EvidenceCreate(BaseSchema):
    """Create evidence item."""
    project_id: UUID
    evidence_type: str
    title: str
    description: Optional[str] = None
    source_document_id: Optional[UUID] = None
    source_interview_id: Optional[UUID] = None
    external_url: Optional[str] = None
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    source_excerpt: Optional[str] = None
    relevant_to_permitted_purpose: bool = False
    relevant_to_technological_nature: bool = False
    relevant_to_uncertainty: bool = False
    relevant_to_experimentation: bool = False


class EvidenceResponse(BaseSchema):
    """Full evidence response."""
    id: UUID
    project_id: UUID
    evidence_type: str
    title: str
    description: Optional[str]
    source_excerpt: Optional[str]
    relevant_to_permitted_purpose: bool
    relevant_to_technological_nature: bool
    relevant_to_uncertainty: bool
    relevant_to_experimentation: bool
    evidence_strength: Optional[ConfidenceLevel]
    ai_relevance_score: Optional[float]
    created_at: datetime


# =============================================================================
# REVIEW CONSOLE SCHEMAS
# =============================================================================

class ReviewItem(BaseSchema):
    """Item requiring CPA review."""
    id: UUID
    entity_type: str  # project, employee, qre, narrative
    entity_id: UUID
    title: str
    description: str
    confidence: Optional[ConfidenceLevel]
    risk_flags: List[str]
    suggested_action: str
    evidence_count: int


class ReviewDecision(BaseSchema):
    """CPA review decision."""
    decision: str  # accept, reject, adjust
    adjustment_value: Optional[Any] = None
    reason: Optional[str] = None


class ReviewQueueResponse(BaseSchema):
    """Review queue for CPA."""
    study_id: UUID
    total_items: int
    reviewed_items: int
    pending_items: int
    high_priority_items: int
    items: List[ReviewItem]


class RiskFlagResponse(BaseSchema):
    """Risk flag for review."""
    id: str
    flag_type: RiskFlag
    severity: str  # high, medium, low
    entity_type: str
    entity_id: UUID
    description: str
    suggested_resolution: str
    resolved: bool
    resolved_by: Optional[UUID]
    resolved_at: Optional[datetime]


# =============================================================================
# OUTPUT GENERATION SCHEMAS
# =============================================================================

class OutputGenerationRequest(BaseSchema):
    """Request to generate output files."""
    output_types: List[str]  # pdf_study, excel_workbook, form_6765, state_forms
    include_draft_watermark: bool = True
    include_appendices: bool = True


class OutputFileResponse(BaseSchema):
    """Generated output file."""
    id: UUID
    study_id: UUID
    file_type: str
    filename: str
    file_size: int
    version: int
    is_final: bool
    download_url: str
    generated_at: datetime


class Form6765Data(BaseSchema):
    """Data for Form 6765 generation."""
    # Section A - Regular Credit
    line_1_paid_or_incurred: Decimal
    line_2_basic_research: Decimal
    line_3_qualified_org_payments: Decimal
    line_4_energy_research: Decimal
    line_5_total: Decimal
    line_6_through_8_base_period: Dict[str, Decimal]
    line_9_fixed_base_percentage: float
    line_10_average_gross_receipts: Decimal
    line_11_multiply_line_9_10: Decimal
    line_12_base_amount: Decimal
    line_13_subtract: Decimal
    line_14_smaller_line_5_or_half: Decimal
    line_15_subtract: Decimal
    line_16_credit_rate: float
    line_17_credit: Decimal

    # Section B - Alternative Simplified Credit
    line_24_qre_current: Decimal
    line_25_26_27_prior_years: Dict[str, Decimal]
    line_28_average: Decimal
    line_29_multiply: Decimal
    line_30_subtract: Decimal
    line_31_credit: Decimal

    # Section C - Current Year Credit
    line_32_regular_or_asc: Decimal
    line_33_280c_election: Decimal
    line_34_current_year_credit: Decimal


class TaxPreparerSummary(BaseSchema):
    """Summary for tax preparer."""
    study_id: UUID
    tax_year: int
    entity_name: str
    entity_type: EntityType
    ein: Optional[str]

    # Federal credit
    federal_method: CreditMethod
    federal_credit: Decimal
    form_6765_lines: Dict[str, Any]

    # State credits
    state_credits: Dict[str, Decimal]

    # Carryforward/back
    credit_carryforward: Decimal
    credit_carryback: Decimal

    # Key metrics
    total_qre: Decimal
    qre_breakdown: Dict[str, Decimal]
    effective_credit_rate: float

    # Sources and notes
    key_assumptions: List[str]
    limitations: List[str]
    preparer_notes: Optional[str]


# =============================================================================
# BENCHMARK SCHEMAS
# =============================================================================

class BenchmarkData(BaseSchema):
    """Industry benchmark data."""
    industry: str
    naics_code: Optional[str]
    rd_intensity_median: float  # R&D spend as % of revenue
    rd_intensity_percentile_25: float
    rd_intensity_percentile_75: float
    credit_as_percentage_of_qre_median: float
    typical_qre_breakdown: Dict[str, float]  # {wages: 70, supplies: 15, contract: 15}
    sample_size: int


class SanityCheckResult(BaseSchema):
    """Result of sanity check."""
    check_name: str
    passed: bool
    expected_range: Optional[Dict[str, Any]]
    actual_value: Any
    deviation: Optional[float]
    severity: str  # info, warning, error
    message: str


class BenchmarkAnalysis(BaseSchema):
    """Full benchmark analysis."""
    study_id: UUID
    industry: str
    benchmark_data: BenchmarkData
    study_metrics: Dict[str, Any]
    comparisons: List[Dict[str, Any]]
    sanity_checks: List[SanityCheckResult]
    overall_assessment: str
    recommendations: List[str]


# =============================================================================
# AUDIT TRAIL SCHEMAS
# =============================================================================

class AuditLogResponse(BaseSchema):
    """Audit log entry."""
    id: UUID
    study_id: UUID
    action: str
    entity_type: str
    entity_id: Optional[UUID]
    previous_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    change_summary: Optional[str]
    user_id: UUID
    user_email: Optional[str]
    created_at: datetime


class AuditTrailQuery(BaseSchema):
    """Query parameters for audit trail."""
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    action: Optional[str] = None
    user_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    page_size: int = 50


# =============================================================================
# TEAM SCHEMAS
# =============================================================================

class TeamMemberAdd(BaseSchema):
    """Add team member to study."""
    user_id: UUID
    role: UserRole
    can_approve: bool = False
    can_edit: bool = True


class TeamMemberResponse(BaseSchema):
    """Team member response."""
    id: UUID
    study_id: UUID
    user_id: UUID
    role: UserRole
    can_approve: bool
    can_edit: bool
    can_view: bool
    assigned_at: datetime


# =============================================================================
# MULTI-YEAR SCHEMAS
# =============================================================================

class MultiYearStudyCreate(BaseSchema):
    """Create multi-year study."""
    base_study_id: UUID
    additional_years: List[int]
    copy_projects: bool = True
    copy_employees: bool = True


class AmendedStudyCreate(BaseSchema):
    """Create amended study."""
    original_study_id: UUID
    amendment_reason: str
    changes_description: str
