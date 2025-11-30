"""Main FastAPI application for Reporting Service"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import time

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import init_db, close_db, get_db
from .models import (
    ReportTemplate,
    Report,
    ReportSection,
    SignatureEnvelope,
    ReportSchedule,
    ReportType,
    ReportStatus,
    SignatureStatus,
    TemplateType
)
from .schemas import (
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportTemplateResponse,
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    SignatureEnvelopeCreate,
    SignatureEnvelopeResponse,
    ReportScheduleCreate,
    ReportScheduleUpdate,
    ReportScheduleResponse,
    ReportingStats,
    HTMLToPDFRequest,
    PDFGenerationOptions,
    # Compliance Report Schemas
    CompilationReportRequest,
    ReviewReportRequest,
    AuditReportRequest,
    ManagementRepLetterRequest,
    CoverLetterRequest,
    NotesRequest,
    CompletePackageRequest,
    ComplianceReportResponse,
    CompletePackageResponse
)
from .pdf_service import pdf_service
from .docusign_service import docusign_service
from .storage_service import storage_service
from .compliance_report_generator import (
    compliance_report_generator,
    complete_package_generator,
    EngagementType,
    OpinionType,
    EntityType,
    FinancialFramework
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} service v{settings.VERSION}")
    await init_db()
    logger.info("Reporting service ready")

    yield

    # Shutdown
    logger.info("Shutting down Reporting service")
    await close_db()


app = FastAPI(
    title="Aura Audit AI - Reporting Service",
    description="Report generation, PDF creation, and e-signature management",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# Dependency: User Authentication
# ========================================

async def get_current_user_id() -> UUID:
    """
    Get current user ID from JWT token
    TODO: Implement actual JWT validation
    """
    return UUID("00000000-0000-0000-0000-000000000001")


# ========================================
# Health Check
# ========================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION
    }


# ========================================
# Report Templates
# ========================================

@app.post("/templates", response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: ReportTemplateCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create new report template"""
    db_template = ReportTemplate(
        **template.model_dump(),
        created_by=user_id
    )
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)

    logger.info(f"Created template {db_template.id}: {db_template.name}")

    return ReportTemplateResponse.model_validate(db_template)


@app.get("/templates", response_model=List[ReportTemplateResponse])
async def list_templates(
    report_type: Optional[ReportType] = None,
    template_type: Optional[TemplateType] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List report templates"""
    query = select(ReportTemplate).where(ReportTemplate.is_active == is_active)

    if report_type:
        query = query.where(ReportTemplate.report_type == report_type)

    if template_type:
        query = query.where(ReportTemplate.template_type == template_type)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    templates = result.scalars().all()

    return [ReportTemplateResponse.model_validate(t) for t in templates]


@app.get("/templates/{template_id}", response_model=ReportTemplateResponse)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get template by ID"""
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return ReportTemplateResponse.model_validate(template)


@app.patch("/templates/{template_id}", response_model=ReportTemplateResponse)
async def update_template(
    template_id: UUID,
    update: ReportTemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update template"""
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)

    return ReportTemplateResponse.model_validate(template)


@app.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete template (soft delete)"""
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.is_active = False
    await db.commit()


# ========================================
# Reports
# ========================================

@app.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report: ReportCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create new report"""
    db_report = Report(
        **report.model_dump(),
        status=ReportStatus.DRAFT,
        created_by=user_id
    )
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)

    logger.info(f"Created report {db_report.id}: {db_report.title}")

    return ReportResponse.model_validate(db_report)


@app.get("/reports", response_model=List[ReportResponse])
async def list_reports(
    engagement_id: Optional[UUID] = None,
    report_type: Optional[ReportType] = None,
    status_filter: Optional[ReportStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List reports"""
    query = select(Report)

    if engagement_id:
        query = query.where(Report.engagement_id == engagement_id)

    if report_type:
        query = query.where(Report.report_type == report_type)

    if status_filter:
        query = query.where(Report.status == status_filter)

    query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    reports = result.scalars().all()

    return [ReportResponse.model_validate(r) for r in reports]


@app.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get report by ID"""
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportResponse.model_validate(report)


@app.post("/reports/generate", response_model=ReportGenerateResponse)
async def generate_report(
    request: ReportGenerateRequest,
    background_tasks: BackgroundTasks,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Generate PDF report"""
    # Get report
    result = await db.execute(
        select(Report).where(Report.id == request.report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Check if already generated
    if report.status == ReportStatus.GENERATED and not request.regenerate:
        return ReportGenerateResponse(
            report_id=report.id,
            status=report.status,
            file_path=report.file_path,
            file_size=report.file_size,
            generation_duration_ms=report.generation_duration_ms,
            message="Report already generated"
        )

    # Update status
    report.status = ReportStatus.GENERATING
    report.generation_started_at = func.now()
    await db.commit()

    # Generate report in background
    background_tasks.add_task(
        _generate_report_task,
        report_id=report.id,
        user_id=user_id
    )

    return ReportGenerateResponse(
        report_id=report.id,
        status=ReportStatus.GENERATING,
        message="Report generation started"
    )


async def _generate_report_task(report_id: UUID, user_id: UUID):
    """Background task to generate report"""
    from .database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            start_time = time.time()

            # Get report with template
            result = await db.execute(
                select(Report).where(Report.id == report_id)
            )
            report = result.scalar_one()

            # Get template if specified
            template_html = None
            if report.template_id:
                template_result = await db.execute(
                    select(ReportTemplate).where(ReportTemplate.id == report.template_id)
                )
                template = template_result.scalar_one_or_none()
                if template:
                    # Render template with report data
                    template_html = pdf_service.render_template(
                        template.html_content,
                        report.report_data
                    )

            # Use template HTML or default
            html_content = template_html or report.report_data.get('html_content', '<h1>Report</h1>')

            # Generate PDF
            pdf_bytes = pdf_service.generate_from_html(
                html_content,
                options=PDFGenerationOptions(
                    enable_watermark=report.has_watermark,
                    watermark_text=report.watermark_text
                )
            )

            # Add metadata
            pdf_bytes = pdf_service.add_metadata(
                pdf_bytes,
                title=report.title,
                author="Aura Audit AI",
                subject=f"{report.report_type.value} Report"
            )

            # Compute hash
            file_hash = pdf_service.compute_hash(pdf_bytes)

            # Upload to storage
            file_name = f"{report.id}_{report.title.replace(' ', '_')}.pdf"
            storage_path = await storage_service.upload_report(
                pdf_bytes,
                file_name,
                metadata={
                    'report_id': str(report.id),
                    'engagement_id': str(report.engagement_id),
                    'report_type': report.report_type.value,
                    'created_by': str(user_id)
                }
            )

            # Update report
            generation_time = int((time.time() - start_time) * 1000)

            report.status = ReportStatus.GENERATED
            report.file_name = file_name
            report.file_path = storage_path
            report.file_size = len(pdf_bytes)
            report.file_hash = file_hash
            report.generation_completed_at = func.now()
            report.generation_duration_ms = generation_time

            await db.commit()

            logger.info(f"Report {report_id} generated in {generation_time}ms")

        except Exception as e:
            logger.error(f"Report generation failed: {e}", exc_info=True)

            # Update error status
            result = await db.execute(
                select(Report).where(Report.id == report_id)
            )
            report = result.scalar_one()
            report.status = ReportStatus.FAILED
            report.generation_error = str(e)
            await db.commit()


@app.get("/reports/{report_id}/download")
async def download_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Download report PDF"""
    import io

    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.file_path:
        raise HTTPException(status_code=400, detail="Report not yet generated")

    # Download from storage
    pdf_bytes = await storage_service.download_report(report.file_path)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{report.file_name}"'
        }
    )


@app.post("/reports/{report_id}/finalize", response_model=ReportResponse)
async def finalize_report(
    report_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Finalize report (upload to WORM storage for immutability)
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.file_path:
        raise HTTPException(status_code=400, detail="Report not yet generated")

    if report.status != ReportStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Report must be approved before finalization"
        )

    # Download current report
    pdf_bytes = await storage_service.download_report(report.file_path)

    # Upload to WORM storage
    from datetime import datetime

    file_name = f"FINAL_{report.file_name}"
    worm_path = await storage_service.upload_to_worm(
        pdf_bytes,
        file_name,
        metadata={
            'report_id': str(report.id),
            'finalized_by': str(user_id),
            'finalized_at': datetime.now().isoformat()
        }
    )

    # Update report
    report.worm_file_path = worm_path
    report.finalized_at = func.now()
    report.status = ReportStatus.FINALIZED

    await db.commit()
    await db.refresh(report)

    logger.info(f"Report {report_id} finalized to WORM storage")

    return ReportResponse.model_validate(report)


# ========================================
# E-Signatures
# ========================================

@app.post("/signatures", response_model=SignatureEnvelopeResponse, status_code=status.HTTP_201_CREATED)
async def create_signature_envelope(
    envelope: SignatureEnvelopeCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create e-signature envelope"""
    # Get report
    result = await db.execute(
        select(Report).where(Report.id == envelope.report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.file_path:
        raise HTTPException(status_code=400, detail="Report not yet generated")

    # Download report PDF
    pdf_bytes = await storage_service.download_report(report.file_path)

    # Create DocuSign envelope
    docusign_result = await docusign_service.create_envelope(
        document_bytes=pdf_bytes,
        document_name=report.file_name,
        subject=envelope.subject,
        message=envelope.message or "",
        signers=envelope.signers,
        expires_in_days=envelope.expires_in_days,
        send_immediately=envelope.send_immediately
    )

    # Create signature envelope record
    db_envelope = SignatureEnvelope(
        report_id=envelope.report_id,
        docusign_envelope_id=docusign_result['envelope_id'],
        subject=envelope.subject,
        message=envelope.message,
        signers=[s.model_dump() for s in envelope.signers],
        status=SignatureStatus.SENT if envelope.send_immediately else SignatureStatus.PENDING,
        sent_at=func.now() if envelope.send_immediately else None,
        created_by=user_id
    )

    db.add(db_envelope)
    await db.commit()
    await db.refresh(db_envelope)

    logger.info(f"Created signature envelope {db_envelope.id} for report {envelope.report_id}")

    return SignatureEnvelopeResponse.model_validate(db_envelope)


@app.get("/signatures/{envelope_id}", response_model=SignatureEnvelopeResponse)
async def get_signature_envelope(
    envelope_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get signature envelope"""
    result = await db.execute(
        select(SignatureEnvelope).where(SignatureEnvelope.id == envelope_id)
    )
    envelope = result.scalar_one_or_none()

    if not envelope:
        raise HTTPException(status_code=404, detail="Envelope not found")

    return SignatureEnvelopeResponse.model_validate(envelope)


# ========================================
# Statistics
# ========================================

@app.get("/stats", response_model=ReportingStats)
async def get_reporting_stats(db: AsyncSession = Depends(get_db)):
    """Get reporting statistics"""
    # Total reports
    total_count = await db.execute(select(func.count()).select_from(Report))
    total_reports = total_count.scalar()

    # Reports by type
    reports_by_type = {}
    for report_type in ReportType:
        count = await db.execute(
            select(func.count()).select_from(Report).where(Report.report_type == report_type)
        )
        reports_by_type[report_type.value] = count.scalar()

    # Reports by status
    reports_by_status = {}
    for report_status in ReportStatus:
        count = await db.execute(
            select(func.count()).select_from(Report).where(Report.status == report_status)
        )
        reports_by_status[report_status.value] = count.scalar()

    # Templates
    template_count = await db.execute(select(func.count()).select_from(ReportTemplate))
    total_templates = template_count.scalar()

    active_template_count = await db.execute(
        select(func.count()).select_from(ReportTemplate).where(ReportTemplate.is_active == True)
    )
    active_templates = active_template_count.scalar()

    # Signatures
    pending_sigs = await db.execute(
        select(func.count()).select_from(SignatureEnvelope).where(
            SignatureEnvelope.status.in_([SignatureStatus.PENDING, SignatureStatus.SENT])
        )
    )
    pending_signatures = pending_sigs.scalar()

    completed_sigs = await db.execute(
        select(func.count()).select_from(SignatureEnvelope).where(
            SignatureEnvelope.status == SignatureStatus.COMPLETED
        )
    )
    completed_signatures = completed_sigs.scalar()

    # Average generation time
    avg_time = await db.execute(
        select(func.avg(Report.generation_duration_ms)).where(
            Report.generation_duration_ms.isnot(None)
        )
    )
    avg_generation_time_ms = float(avg_time.scalar() or 0)

    # Total storage
    total_storage = await db.execute(
        select(func.sum(Report.file_size)).where(Report.file_size.isnot(None))
    )
    total_storage_bytes = int(total_storage.scalar() or 0)

    return ReportingStats(
        total_reports=total_reports,
        reports_by_type=reports_by_type,
        reports_by_status=reports_by_status,
        total_templates=total_templates,
        active_templates=active_templates,
        pending_signatures=pending_signatures,
        completed_signatures=completed_signatures,
        avg_generation_time_ms=avg_generation_time_ms,
        total_storage_bytes=total_storage_bytes
    )


# ========================================
# Compliance Report Generation (AICPA/PCAOB/GAAP)
# ========================================

@app.post("/compliance/compilation", response_model=ComplianceReportResponse)
async def generate_compilation_report(request: CompilationReportRequest):
    """
    Generate Compilation Report per SSARS AR-C 80.

    Standards Compliance:
    - SSARS AR-C 80: Compilation Engagements
    - AICPA Professional Standards
    """
    try:
        context_dict = request.context.model_dump()
        if request.context.additional_data:
            context_dict.update(request.context.additional_data)

        html_content = compliance_report_generator.generate_compilation_report(
            context=context_dict,
            opinion_type=OpinionType(request.opinion_type.value),
            framework=FinancialFramework(request.framework.value)
        )

        return ComplianceReportResponse(
            html_content=html_content,
            report_type="compilation",
            generated_at=datetime.now(),
            standards_compliance=["AICPA SSARS AR-C 80", "GAAP"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Compilation report generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate compilation report")


@app.post("/compliance/review", response_model=ComplianceReportResponse)
async def generate_review_report(request: ReviewReportRequest):
    """
    Generate Review Report per SSARS AR-C 90.

    Standards Compliance:
    - SSARS AR-C 90: Review of Financial Statements
    - AICPA Professional Standards
    """
    try:
        context_dict = request.context.model_dump()
        if request.context.additional_data:
            context_dict.update(request.context.additional_data)

        html_content = compliance_report_generator.generate_review_report(
            context=context_dict,
            opinion_type=OpinionType(request.opinion_type.value),
            framework=FinancialFramework(request.framework.value),
            emphasis_paragraphs=request.emphasis_paragraphs
        )

        return ComplianceReportResponse(
            html_content=html_content,
            report_type="review",
            generated_at=datetime.now(),
            standards_compliance=["AICPA SSARS AR-C 90", "GAAP"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Review report generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate review report")


@app.post("/compliance/audit", response_model=ComplianceReportResponse)
async def generate_audit_report(request: AuditReportRequest):
    """
    Generate Audit Report per AU-C 700 / PCAOB AS 3101.

    Standards Compliance:
    - GAAS AU-C 700: Forming an Opinion and Reporting
    - PCAOB AS 3101: The Auditor's Report (public companies)
    - AU-C 570: Going Concern
    - AU-C 260: Communications with Those Charged with Governance
    """
    try:
        context_dict = request.context.model_dump()
        if request.context.additional_data:
            context_dict.update(request.context.additional_data)

        # Convert key audit matters to dict format
        key_audit_matters = None
        if request.key_audit_matters:
            key_audit_matters = [kam.model_dump() for kam in request.key_audit_matters]

        html_content = compliance_report_generator.generate_audit_report(
            context=context_dict,
            opinion_type=OpinionType(request.opinion_type.value),
            entity_type=EntityType(request.entity_type.value),
            framework=FinancialFramework(request.framework.value),
            going_concern=request.going_concern,
            key_audit_matters=key_audit_matters,
            emphasis_paragraphs=request.emphasis_paragraphs,
            other_matter_paragraphs=request.other_matter_paragraphs
        )

        standards = ["GAAS AU-C 700", "AICPA", "GAAP"]
        if request.entity_type.value == "public_company":
            standards.append("PCAOB AS 3101")
            standards.append("SEC")

        return ComplianceReportResponse(
            html_content=html_content,
            report_type="audit",
            generated_at=datetime.now(),
            standards_compliance=standards
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audit report generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audit report")


@app.post("/compliance/management-rep-letter", response_model=ComplianceReportResponse)
async def generate_management_rep_letter(request: ManagementRepLetterRequest):
    """
    Generate Management Representation Letter per AU-C 580 / AS 2805.

    Standards Compliance:
    - AU-C 580: Written Representations
    - PCAOB AS 2805: Management Representations
    """
    try:
        context_dict = request.context.model_dump()
        if request.context.additional_data:
            context_dict.update(request.context.additional_data)

        html_content = compliance_report_generator.generate_management_rep_letter(
            context=context_dict,
            engagement_type=EngagementType(request.engagement_type.value),
            include_fraud_representations=request.include_fraud_representations,
            include_going_concern=request.include_going_concern,
            additional_representations=request.additional_representations
        )

        return ComplianceReportResponse(
            html_content=html_content,
            report_type="management_rep_letter",
            generated_at=datetime.now(),
            standards_compliance=["AU-C 580", "AS 2805", "AICPA"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Management rep letter generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate management representation letter")


@app.post("/compliance/cover-letter", response_model=ComplianceReportResponse)
async def generate_cover_letter(request: CoverLetterRequest):
    """
    Generate Cover Letter for financial statement package.
    """
    try:
        context_dict = request.context.model_dump()
        if request.context.additional_data:
            context_dict.update(request.context.additional_data)

        html_content = compliance_report_generator.generate_cover_letter(
            context=context_dict,
            engagement_type=EngagementType(request.engagement_type.value),
            include_deliverables_list=request.include_deliverables_list
        )

        return ComplianceReportResponse(
            html_content=html_content,
            report_type="cover_letter",
            generated_at=datetime.now(),
            standards_compliance=["Professional Standards"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate cover letter")


@app.post("/compliance/notes", response_model=ComplianceReportResponse)
async def generate_notes_to_financial_statements(request: NotesRequest):
    """
    Generate Notes to Financial Statements per FASB ASC.

    Standards Compliance:
    - FASB ASC 205-10: Presentation of Financial Statements
    - FASB ASC 235: Notes to Financial Statements
    - FASB ASC 275: Risks and Uncertainties
    - FASB ASC 450: Contingencies
    - FASB ASC 606: Revenue from Contracts with Customers
    - FASB ASC 842: Leases
    """
    try:
        context_dict = request.context.model_dump()
        if request.context.additional_data:
            context_dict.update(request.context.additional_data)

        html_content = compliance_report_generator.generate_notes_to_financial_statements(
            context=context_dict,
            framework=FinancialFramework(request.framework.value),
            disclosure_selections=request.disclosure_selections
        )

        return ComplianceReportResponse(
            html_content=html_content,
            report_type="notes_to_financial_statements",
            generated_at=datetime.now(),
            standards_compliance=["FASB ASC", "GAAP", "SEC Regulation S-X"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Notes generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate notes to financial statements")


@app.post("/compliance/complete-package", response_model=CompletePackageResponse)
async def generate_complete_package(request: CompletePackageRequest):
    """
    Generate Complete Financial Statement Package.

    Includes:
    - Cover Letter
    - Accountant's Report (Compilation/Review/Audit)
    - Notes to Financial Statements
    - Management Representation Letter

    Standards Compliance:
    - AICPA Professional Standards
    - PCAOB Auditing Standards (public companies)
    - FASB ASC / GAAP
    - SEC Regulations (public companies)
    """
    try:
        sections = complete_package_generator.generate_complete_package(
            context=request.context,
            engagement_type=EngagementType(request.engagement_type.value),
            opinion_type=OpinionType(request.opinion_type.value),
            entity_type=EntityType(request.entity_type.value),
            framework=FinancialFramework(request.framework.value),
            include_sections=request.include_sections
        )

        standards = ["AICPA", "GAAP", "FASB ASC"]
        if request.entity_type.value == "public_company":
            standards.extend(["PCAOB", "SEC"])

        return CompletePackageResponse(
            sections=sections,
            engagement_type=request.engagement_type.value,
            generated_at=datetime.now(),
            standards_compliance=standards
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Complete package generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate complete package")


@app.get("/compliance/standards")
async def get_supported_standards():
    """
    Get list of supported professional standards for report generation.
    """
    return {
        "compilation_standards": [
            "SSARS AR-C 80 - Compilation Engagements"
        ],
        "review_standards": [
            "SSARS AR-C 90 - Review of Financial Statements"
        ],
        "audit_standards": [
            "GAAS AU-C 700 - Forming an Opinion and Reporting",
            "GAAS AU-C 570 - Going Concern",
            "GAAS AU-C 580 - Written Representations",
            "GAAS AU-C 260 - Communications with Those Charged with Governance",
            "PCAOB AS 3101 - The Auditor's Report on an Audit of Financial Statements",
            "PCAOB AS 2401 - Consideration of Fraud",
            "PCAOB AS 2415 - Consideration of an Entity's Ability to Continue as a Going Concern",
            "PCAOB AS 2805 - Management Representations",
            "PCAOB AS 1301 - Communications with Audit Committees"
        ],
        "financial_reporting_standards": [
            "FASB ASC 205-10 - Presentation of Financial Statements",
            "FASB ASC 235 - Notes to Financial Statements",
            "FASB ASC 275 - Risks and Uncertainties",
            "FASB ASC 450 - Contingencies",
            "FASB ASC 606 - Revenue from Contracts with Customers",
            "FASB ASC 842 - Leases",
            "FASB ASC 820 - Fair Value Measurement",
            "FASB ASC 740 - Income Taxes"
        ],
        "sec_standards": [
            "Regulation S-X - Form and Content of Financial Statements",
            "Regulation S-K - Disclosure Requirements"
        ],
        "supported_frameworks": [
            "U.S. GAAP",
            "IFRS",
            "Tax Basis",
            "Cash Basis",
            "Regulatory Basis"
        ],
        "opinion_types": {
            "audit": ["Unmodified", "Qualified (Scope)", "Qualified (GAAP)", "Adverse", "Disclaimer"],
            "review": ["Unmodified", "Modified"],
            "compilation": ["Standard", "No Independence", "Omit Disclosures"]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
