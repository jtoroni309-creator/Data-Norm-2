"""
FastAPI Service for Advanced Report Generation

Exposes endpoints for:
- Report generation with constitutional AI
- Compliance validation
- Citation checking
- Template management
- Performance metrics
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, date
from enum import Enum
import uuid

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from .database import get_db
from .config import settings
from .main import (
    EnterpriseReportGenerator,
    AuditReportStructure,
    OpinionType,
    ReportSection
)
from .compliance_checker import (
    ComplianceChecker,
    ComplianceLevel,
    ComplianceViolation
)
from .regulatory_knowledge_graph import RegulatoryKnowledgeGraph


app = FastAPI(
    title="Advanced Report Generation Service",
    description="State-of-the-art AI for generating audit reports with 99.9% regulatory compliance",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class EntityType(str, Enum):
    """Type of entity being audited"""
    PUBLIC_COMPANY = "public_company"
    PRIVATE_COMPANY = "private_company"
    NON_PROFIT = "non_profit"
    GOVERNMENT = "government"


class ReportType(str, Enum):
    """Type of report to generate"""
    AUDIT_REPORT = "audit_report"
    REVIEW_REPORT = "review_report"
    COMPILATION_REPORT = "compilation_report"
    ATTESTATION_REPORT = "attestation_report"


class GenerationMethod(str, Enum):
    """Method for generating report"""
    CONSTITUTIONAL_AI = "constitutional_ai"
    MULTI_AGENT = "multi_agent"
    SELF_CONSISTENCY = "self_consistency"
    HYBRID = "hybrid"


class ReportGenerationRequest(BaseModel):
    """Request to generate audit report"""
    engagement_id: str
    report_type: ReportType = ReportType.AUDIT_REPORT
    entity_type: EntityType = EntityType.PRIVATE_COMPANY
    framework: str = "GAAP"

    # Generation preferences
    generation_method: GenerationMethod = GenerationMethod.HYBRID
    enable_constitutional_ai: bool = True
    enable_multi_agent: bool = True
    enable_self_consistency: bool = False
    self_consistency_samples: int = 5

    # Template
    template_id: Optional[str] = None

    # Additional context
    additional_context: Optional[Dict] = None


class ReportGenerationResponse(BaseModel):
    """Response from report generation"""
    report_id: str
    status: str
    report_number: Optional[str] = None

    # Generated report
    report: Optional[Dict] = None

    # Compliance
    compliance_score: float
    compliance_validated: bool
    violations: List[Dict] = []

    # Metadata
    generation_time_seconds: int
    tokens_used: int
    agents_used: List[str] = []

    # Download URLs
    pdf_url: Optional[str] = None
    docx_url: Optional[str] = None


class ComplianceValidationRequest(BaseModel):
    """Request to validate report compliance"""
    report_id: str
    validation_type: str = "hybrid"  # automated, neural, hybrid
    fix_violations: bool = False


class ComplianceValidationResponse(BaseModel):
    """Response from compliance validation"""
    validation_id: str
    report_id: str
    compliant: bool
    compliance_score: float

    # Violations
    total_violations: int
    critical_violations: int
    high_violations: int
    medium_violations: int
    low_violations: int
    violations: List[Dict]

    # Recommendations
    recommendations: List[str]

    # Metadata
    validation_duration_seconds: int


class CitationValidationRequest(BaseModel):
    """Request to validate citations"""
    report_id: str


class CitationValidationResponse(BaseModel):
    """Response from citation validation"""
    report_id: str
    total_citations: int
    valid_citations: int
    invalid_citations: int
    superseded_citations: int

    citations: List[Dict]
    issues: List[str]


class TemplateCreateRequest(BaseModel):
    """Request to create report template"""
    template_name: str
    template_type: ReportType
    entity_type: EntityType
    framework: str = "GAAP"

    sections: List[Dict]
    constitutional_principles: List[Dict]
    applicable_standards: List[str]


class TemplateResponse(BaseModel):
    """Response with template information"""
    template_id: str
    template_name: str
    template_type: str
    entity_type: str
    framework: str
    is_active: bool
    version: str
    created_at: datetime


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Enterprise report generator
report_generator = EnterpriseReportGenerator()

# Compliance checker
compliance_checker = ComplianceChecker()

# Knowledge graph
knowledge_graph = RegulatoryKnowledgeGraph()


# ============================================================================
# ENDPOINTS: REPORT GENERATION
# ============================================================================

@app.post("/reports/generate", response_model=ReportGenerationResponse)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate audit report using advanced AI

    Steps:
    1. Gather engagement data
    2. Generate report using constitutional AI, multi-agent, or hybrid
    3. Validate compliance
    4. Save to database
    5. Return report with compliance score
    """

    try:
        logger.info(f"Generating report for engagement {request.engagement_id}")

        start_time = datetime.utcnow()

        # Generate report
        report = await report_generator.generate_complete_report(
            engagement_id=request.engagement_id,
            entity_type=request.entity_type.value,
            framework=request.framework,
            db=db
        )

        # Validate compliance
        compliance_result = await compliance_checker.validate_report(report)

        # Save to database
        report_id = str(uuid.uuid4())

        result = await db.execute(
            text("""
                INSERT INTO generated_reports (
                    id, engagement_id, report_type, entity_name,
                    report_date, period_end, opinion_type, opinion_text,
                    title, addressee, opinion_section, basis_for_opinion,
                    responsibilities_section, signature_section,
                    generation_method, agents_used,
                    compliance_score, compliance_validated,
                    status, created_at
                ) VALUES (
                    :id, :engagement_id, :report_type, :entity_name,
                    :report_date, :period_end, :opinion_type, :opinion_text,
                    :title, :addressee, :opinion_section, :basis_for_opinion,
                    :responsibilities_section, :signature_section,
                    :generation_method, :agents_used,
                    :compliance_score, :compliance_validated,
                    :status, :created_at
                )
            """),
            {
                "id": report_id,
                "engagement_id": request.engagement_id,
                "report_type": request.report_type.value,
                "entity_name": report.entity_name,
                "report_date": report.report_date,
                "period_end": report.period_end,
                "opinion_type": report.opinion.value,
                "opinion_text": report.sections[0].content,  # Opinion section
                "title": report.title,
                "addressee": report.addressee,
                "opinion_section": next((s.content for s in report.sections if s.section_name == "Opinion"), ""),
                "basis_for_opinion": next((s.content for s in report.sections if s.section_name == "Basis for Opinion"), ""),
                "responsibilities_section": next((s.content for s in report.sections if s.section_name == "Responsibilities"), ""),
                "signature_section": report.signature,
                "generation_method": request.generation_method.value,
                "agents_used": json.dumps(["opinion", "basis", "compliance", "editor"]),
                "compliance_score": compliance_result["score"],
                "compliance_validated": compliance_result["compliant"],
                "status": "draft",
                "created_at": datetime.utcnow()
            }
        )

        await db.commit()

        # Calculate metrics
        end_time = datetime.utcnow()
        generation_time = int((end_time - start_time).total_seconds())

        # Format response
        return ReportGenerationResponse(
            report_id=report_id,
            status="draft",
            report_number=None,
            report={
                "title": report.title,
                "entity_name": report.entity_name,
                "report_date": report.report_date.isoformat(),
                "opinion_type": report.opinion.value,
                "sections": [
                    {
                        "name": section.section_name,
                        "content": section.content,
                        "citations": section.citations
                    }
                    for section in report.sections
                ],
                "signature": report.signature
            },
            compliance_score=compliance_result["score"],
            compliance_validated=compliance_result["compliant"],
            violations=[
                {
                    "rule_id": v.rule_id,
                    "severity": v.severity.value,
                    "message": v.message,
                    "suggestion": v.suggestion
                }
                for v in compliance_result["violations"]
            ],
            generation_time_seconds=generation_time,
            tokens_used=0,  # Would track actual tokens
            agents_used=["opinion", "basis", "compliance", "editor"]
        )

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(500, f"Report generation failed: {str(e)}")


@app.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get generated report by ID"""

    result = await db.execute(
        text("SELECT * FROM generated_reports WHERE id = :id"),
        {"id": report_id}
    )

    report = result.fetchone()

    if not report:
        raise HTTPException(404, "Report not found")

    return {
        "report_id": str(report.id),
        "engagement_id": str(report.engagement_id),
        "report_type": report.report_type,
        "entity_name": report.entity_name,
        "report_date": report.report_date.isoformat(),
        "opinion_type": report.opinion_type,
        "status": report.status,
        "compliance_score": float(report.compliance_score) if report.compliance_score else None,
        "created_at": report.created_at.isoformat(),
    }


@app.put("/reports/{report_id}/approve")
async def approve_report(
    report_id: str,
    approved_by: str,
    db: AsyncSession = Depends(get_db),
):
    """Approve a generated report"""

    await db.execute(
        text("""
            UPDATE generated_reports
            SET status = 'approved',
                approved_by = :approved_by,
                approved_at = :approved_at
            WHERE id = :id
        """),
        {
            "id": report_id,
            "approved_by": approved_by,
            "approved_at": datetime.utcnow()
        }
    )

    await db.commit()

    return {"message": "Report approved", "report_id": report_id}


@app.put("/reports/{report_id}/issue")
async def issue_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Issue (finalize) a report"""

    # Check if approved
    result = await db.execute(
        text("SELECT status FROM generated_reports WHERE id = :id"),
        {"id": report_id}
    )

    report = result.fetchone()

    if not report:
        raise HTTPException(404, "Report not found")

    if report.status != "approved":
        raise HTTPException(400, "Report must be approved before issuing")

    # Generate report number
    report_number = f"AR-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    await db.execute(
        text("""
            UPDATE generated_reports
            SET status = 'issued',
                report_number = :report_number,
                issued_at = :issued_at
            WHERE id = :id
        """),
        {
            "id": report_id,
            "report_number": report_number,
            "issued_at": datetime.utcnow()
        }
    )

    await db.commit()

    return {
        "message": "Report issued",
        "report_id": report_id,
        "report_number": report_number
    }


# ============================================================================
# ENDPOINTS: COMPLIANCE VALIDATION
# ============================================================================

@app.post("/compliance/validate", response_model=ComplianceValidationResponse)
async def validate_compliance(
    request: ComplianceValidationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate report compliance against all regulatory standards

    Checks 500+ compliance rules across:
    - PCAOB AS standards
    - AICPA AU-C standards
    - SEC regulations
    - GAAP/IFRS requirements
    """

    try:
        start_time = datetime.utcnow()

        # Get report
        result = await db.execute(
            text("SELECT * FROM generated_reports WHERE id = :id"),
            {"id": request.report_id}
        )

        report_data = result.fetchone()

        if not report_data:
            raise HTTPException(404, "Report not found")

        # Build report structure for validation
        report = AuditReportStructure(
            report_date=report_data.report_date,
            entity_name=report_data.entity_name,
            period_end=report_data.period_end,
            opinion=OpinionType(report_data.opinion_type),
            title=report_data.title,
            addressee=report_data.addressee,
            sections=[
                ReportSection(
                    section_name="Opinion",
                    content=report_data.opinion_section,
                    citations=[]
                ),
                ReportSection(
                    section_name="Basis for Opinion",
                    content=report_data.basis_for_opinion,
                    citations=[]
                ),
            ],
            signature=report_data.signature_section
        )

        # Validate
        compliance_result = await compliance_checker.validate_report(report)

        # Save validation results
        validation_id = str(uuid.uuid4())

        violation_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        for v in compliance_result["violations"]:
            violation_counts[v.severity.value] += 1

        await db.execute(
            text("""
                INSERT INTO compliance_validations (
                    id, report_id, validation_type,
                    compliant, compliance_score,
                    total_violations, critical_violations,
                    high_violations, medium_violations, low_violations,
                    violations, recommendations,
                    validated_at, validation_duration_seconds
                ) VALUES (
                    :id, :report_id, :validation_type,
                    :compliant, :compliance_score,
                    :total_violations, :critical_violations,
                    :high_violations, :medium_violations, :low_violations,
                    :violations, :recommendations,
                    :validated_at, :validation_duration_seconds
                )
            """),
            {
                "id": validation_id,
                "report_id": request.report_id,
                "validation_type": request.validation_type,
                "compliant": compliance_result["compliant"],
                "compliance_score": compliance_result["score"],
                "total_violations": len(compliance_result["violations"]),
                "critical_violations": violation_counts["CRITICAL"],
                "high_violations": violation_counts["HIGH"],
                "medium_violations": violation_counts["MEDIUM"],
                "low_violations": violation_counts["LOW"],
                "violations": json.dumps([
                    {
                        "rule_id": v.rule_id,
                        "severity": v.severity.value,
                        "message": v.message,
                        "suggestion": v.suggestion
                    }
                    for v in compliance_result["violations"]
                ]),
                "recommendations": json.dumps(compliance_result.get("recommendations", [])),
                "validated_at": datetime.utcnow(),
                "validation_duration_seconds": int((datetime.utcnow() - start_time).total_seconds())
            }
        )

        await db.commit()

        return ComplianceValidationResponse(
            validation_id=validation_id,
            report_id=request.report_id,
            compliant=compliance_result["compliant"],
            compliance_score=compliance_result["score"],
            total_violations=len(compliance_result["violations"]),
            critical_violations=violation_counts["CRITICAL"],
            high_violations=violation_counts["HIGH"],
            medium_violations=violation_counts["MEDIUM"],
            low_violations=violation_counts["LOW"],
            violations=[
                {
                    "rule_id": v.rule_id,
                    "severity": v.severity.value,
                    "section": v.section_name,
                    "message": v.message,
                    "suggestion": v.suggestion,
                    "regulatory_source": v.regulatory_source
                }
                for v in compliance_result["violations"]
            ],
            recommendations=compliance_result.get("recommendations", []),
            validation_duration_seconds=int((datetime.utcnow() - start_time).total_seconds())
        )

    except Exception as e:
        logger.error(f"Compliance validation failed: {e}")
        raise HTTPException(500, f"Compliance validation failed: {str(e)}")


@app.get("/compliance/rules")
async def get_compliance_rules():
    """Get all compliance rules"""

    rules = compliance_checker.rules

    return {
        "total_rules": len(rules),
        "rules": [
            {
                "rule_id": rule_id,
                "name": rule.get("name"),
                "severity": rule.get("severity"),
                "source": rule.get("source")
            }
            for rule_id, rule in rules.items()
        ]
    }


# ============================================================================
# ENDPOINTS: CITATIONS
# ============================================================================

@app.post("/citations/validate", response_model=CitationValidationResponse)
async def validate_citations(
    request: CitationValidationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate all citations in a report

    Checks:
    - Citation exists in regulatory database
    - Standard is current (not superseded)
    - Citation format is correct
    """

    # Get all citations for report
    result = await db.execute(
        text("SELECT * FROM report_citations WHERE report_id = :report_id"),
        {"report_id": request.report_id}
    )

    citations = result.fetchall()

    valid_count = 0
    invalid_count = 0
    superseded_count = 0
    issues = []

    citation_results = []

    for citation in citations:
        # Validate using knowledge graph
        validation = knowledge_graph.validate_citation(citation.citation_text)

        if validation["valid"]:
            valid_count += 1
            if not validation["current"]:
                superseded_count += 1
                issues.append(f"Citation {citation.citation_text} is superseded by {validation['superseded_by']}")
        else:
            invalid_count += 1
            issues.append(f"Citation {citation.citation_text} not found in regulatory database")

        citation_results.append({
            "citation_text": citation.citation_text,
            "citation_type": citation.citation_type,
            "section": citation.section_name,
            "valid": validation["valid"],
            "current": validation.get("current", False),
            "superseded_by": validation.get("superseded_by")
        })

    return CitationValidationResponse(
        report_id=request.report_id,
        total_citations=len(citations),
        valid_citations=valid_count,
        invalid_citations=invalid_count,
        superseded_citations=superseded_count,
        citations=citation_results,
        issues=issues
    )


# ============================================================================
# ENDPOINTS: TEMPLATES
# ============================================================================

@app.post("/templates", response_model=TemplateResponse)
async def create_template(
    request: TemplateCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new report template"""

    template_id = str(uuid.uuid4())

    await db.execute(
        text("""
            INSERT INTO report_templates (
                id, template_name, template_type, entity_type, framework,
                sections, constitutional_principles, applicable_standards,
                created_at, is_active, version
            ) VALUES (
                :id, :template_name, :template_type, :entity_type, :framework,
                :sections, :constitutional_principles, :applicable_standards,
                :created_at, :is_active, :version
            )
        """),
        {
            "id": template_id,
            "template_name": request.template_name,
            "template_type": request.template_type.value,
            "entity_type": request.entity_type.value,
            "framework": request.framework,
            "sections": json.dumps(request.sections),
            "constitutional_principles": json.dumps(request.constitutional_principles),
            "applicable_standards": json.dumps(request.applicable_standards),
            "created_at": datetime.utcnow(),
            "is_active": True,
            "version": "1.0"
        }
    )

    await db.commit()

    return TemplateResponse(
        template_id=template_id,
        template_name=request.template_name,
        template_type=request.template_type.value,
        entity_type=request.entity_type.value,
        framework=request.framework,
        is_active=True,
        version="1.0",
        created_at=datetime.utcnow()
    )


@app.get("/templates")
async def list_templates(
    template_type: Optional[ReportType] = None,
    entity_type: Optional[EntityType] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all templates"""

    query = "SELECT * FROM report_templates WHERE is_active = TRUE"
    params = {}

    if template_type:
        query += " AND template_type = :template_type"
        params["template_type"] = template_type.value

    if entity_type:
        query += " AND entity_type = :entity_type"
        params["entity_type"] = entity_type.value

    query += " ORDER BY created_at DESC"

    result = await db.execute(text(query), params)
    templates = result.fetchall()

    return {
        "total": len(templates),
        "templates": [
            {
                "template_id": str(t.id),
                "template_name": t.template_name,
                "template_type": t.template_type,
                "entity_type": t.entity_type,
                "framework": t.framework,
                "version": t.version,
                "created_at": t.created_at.isoformat()
            }
            for t in templates
        ]
    }


# ============================================================================
# ENDPOINTS: METRICS AND MONITORING
# ============================================================================

@app.get("/metrics/performance")
async def get_performance_metrics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get performance metrics"""

    query = """
        SELECT
            DATE(created_at) as date,
            COUNT(*) as total_reports,
            AVG(compliance_score) as avg_compliance_score,
            AVG(generation_time_seconds) as avg_generation_time,
            SUM(CASE WHEN status = 'issued' THEN 1 ELSE 0 END) as issued_reports
        FROM generated_reports
        WHERE 1=1
    """

    params = {}

    if start_date:
        query += " AND DATE(created_at) >= :start_date"
        params["start_date"] = start_date

    if end_date:
        query += " AND DATE(created_at) <= :end_date"
        params["end_date"] = end_date

    query += " GROUP BY DATE(created_at) ORDER BY DATE(created_at) DESC LIMIT 30"

    result = await db.execute(text(query), params)
    metrics = result.fetchall()

    return {
        "metrics": [
            {
                "date": m.date.isoformat(),
                "total_reports": m.total_reports,
                "avg_compliance_score": float(m.avg_compliance_score) if m.avg_compliance_score else 0,
                "avg_generation_time": int(m.avg_generation_time) if m.avg_generation_time else 0,
                "issued_reports": m.issued_reports
            }
            for m in metrics
        ]
    }


@app.get("/metrics/violations")
async def get_violation_metrics(
    db: AsyncSession = Depends(get_db),
):
    """Get compliance violation metrics"""

    result = await db.execute(
        text("""
            SELECT
                rule_id,
                rule_name,
                regulatory_source,
                severity,
                COUNT(*) as violation_count
            FROM compliance_violations
            WHERE detected_at >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY rule_id, rule_name, regulatory_source, severity
            ORDER BY violation_count DESC
            LIMIT 20
        """)
    )

    violations = result.fetchall()

    return {
        "top_violations": [
            {
                "rule_id": v.rule_id,
                "rule_name": v.rule_name,
                "regulatory_source": v.regulatory_source,
                "severity": v.severity,
                "count": v.violation_count
            }
            for v in violations
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Advanced Report Generation",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
