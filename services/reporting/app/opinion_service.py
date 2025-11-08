"""
Opinion Service
Generates audit, review, and compilation reports with appropriate opinions
"""
import logging
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from enum import Enum as PyEnum

from sqlalchemy import select, Column, String, Date, DateTime, Boolean, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import jinja2

from .database import Base

logger = logging.getLogger(__name__)


class OpinionType(str, PyEnum):
    """Opinion types"""
    UNQUALIFIED = "unqualified"
    QUALIFIED_SCOPE = "qualified_scope"
    QUALIFIED_GAAP = "qualified_gaap"
    ADVERSE = "adverse"
    DISCLAIMER = "disclaimer"
    REVIEW_STANDARD = "review_standard"
    REVIEW_DEPARTURE = "review_departure"
    COMPILATION_STANDARD = "compilation_standard"
    COMPILATION_NOINDEPENDENCE = "compilation_noindependence"


class ReportSectionType(str, PyEnum):
    """Report section types"""
    OPINION = "opinion"
    BASIS_FOR_OPINION = "basis_for_opinion"
    EMPHASIS_OF_MATTER = "emphasis_of_matter"
    OTHER_MATTER = "other_matter"
    RESPONSIBILITIES_MANAGEMENT = "responsibilities_management"
    RESPONSIBILITIES_AUDITOR = "responsibilities_auditor"
    KEY_AUDIT_MATTERS = "key_audit_matters"
    GOING_CONCERN = "going_concern"
    OTHER_INFORMATION = "other_information"


class OpinionTemplate(Base):
    """Opinion template"""
    __tablename__ = "opinion_templates"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    template_name = Column(String(255), nullable=False)
    opinion_type = Column(SQLEnum(OpinionType), nullable=False)
    engagement_type = Column(String(50), nullable=False)
    opinion_paragraph = Column(Text, nullable=False)
    basis_paragraph = Column(Text)
    responsibilities_management_paragraph = Column(Text)
    responsibilities_auditor_paragraph = Column(Text)
    emphasis_of_matter_template = Column(Text)
    other_matter_template = Column(Text)
    going_concern_template = Column(Text)
    report_title = Column(String(255), nullable=False)
    addressee_default = Column(String(255))
    applies_to_public = Column(Boolean, default=True)
    applies_to_private = Column(Boolean, default=True)
    applies_to_nonprofit = Column(Boolean, default=False)
    is_standard = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(PGUUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class ReportModification(Base):
    """Report modification paragraph"""
    __tablename__ = "report_modifications"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    modification_type = Column(SQLEnum(ReportSectionType), nullable=False)
    modification_name = Column(String(255), nullable=False)
    modification_reason = Column(String(500))
    paragraph_template = Column(Text, nullable=False)
    position_order = Column(Integer)
    is_standard = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class EngagementReport(Base):
    """Engagement report"""
    __tablename__ = "engagement_reports"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    engagement_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.engagements.id"))
    report_type = Column(String(50), nullable=False)
    opinion_type = Column(SQLEnum(OpinionType), nullable=False)
    report_title = Column(String(255), nullable=False)
    report_date = Column(Date, nullable=False)
    addressee = Column(Text, nullable=False)
    opinion_paragraph = Column(Text, nullable=False)
    basis_paragraph = Column(Text)
    responsibilities_management_paragraph = Column(Text)
    responsibilities_auditor_paragraph = Column(Text)
    emphasis_of_matter_paragraph = Column(Text)
    other_matter_paragraph = Column(Text)
    going_concern_paragraph = Column(Text)
    firm_name = Column(String(255), nullable=False)
    firm_address = Column(Text)
    partner_name = Column(String(255))
    partner_title = Column(String(100))
    status = Column(String(50), default='draft')
    draft_number = Column(Integer, default=1)
    drafted_by = Column(PGUUID(as_uuid=True))
    drafted_at = Column(DateTime(timezone=True))
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    approved_by = Column(PGUUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    issued_at = Column(DateTime(timezone=True))
    draft_document_s3_uri = Column(Text)
    final_document_s3_uri = Column(Text)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class OpinionService:
    """Service for generating audit and attest opinions"""

    def __init__(self, db: AsyncSession):
        """
        Initialize opinion service

        Args:
            db: Database session
        """
        self.db = db
        self.template_env = jinja2.Environment(autoescape=True)

    async def generate_report_draft(
        self,
        engagement_id: UUID,
        opinion_type: OpinionType,
        report_date: date,
        template_variables: Dict[str, Any],
        user_id: Optional[UUID] = None,
        modifications: Optional[List[str]] = None
    ) -> EngagementReport:
        """
        Generate report draft

        Args:
            engagement_id: Engagement ID
            opinion_type: Type of opinion
            report_date: Report date
            template_variables: Variables for template rendering
            user_id: User generating report
            modifications: List of modification names to include

        Returns:
            Created EngagementReport
        """
        logger.info(f"Generating {opinion_type.value} report draft for engagement {engagement_id}")

        # Get engagement details
        from .models import Engagement
        engagement = await self.db.get(Engagement, engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        # Determine engagement type from opinion type
        if opinion_type in [OpinionType.UNQUALIFIED, OpinionType.QUALIFIED_SCOPE, OpinionType.QUALIFIED_GAAP, OpinionType.ADVERSE, OpinionType.DISCLAIMER]:
            engagement_type = 'audit'
        elif opinion_type in [OpinionType.REVIEW_STANDARD, OpinionType.REVIEW_DEPARTURE]:
            engagement_type = 'review'
        else:
            engagement_type = 'compilation'

        # Get opinion template
        template = await self._get_opinion_template(opinion_type, engagement_type)
        if not template:
            raise ValueError(f"No template found for {opinion_type.value}")

        # Merge default variables
        full_variables = {
            'client_name': engagement.client_name,
            'balance_sheet_date': template_variables.get('balance_sheet_date', report_date.strftime('%B %d, %Y')),
            'report_date': report_date.strftime('%B %d, %Y'),
            **template_variables
        }

        # Render opinion paragraph
        opinion_paragraph = self._render_template(template.opinion_paragraph, full_variables)
        basis_paragraph = self._render_template(template.basis_paragraph, full_variables) if template.basis_paragraph else None
        mgmt_paragraph = self._render_template(template.responsibilities_management_paragraph, full_variables) if template.responsibilities_management_paragraph else None
        auditor_paragraph = self._render_template(template.responsibilities_auditor_paragraph, full_variables) if template.responsibilities_auditor_paragraph else None

        # Add modifications if requested
        emphasis_paragraph = None
        other_matter_paragraph = None
        going_concern_paragraph = None

        if modifications:
            for mod_name in modifications:
                mod = await self._get_modification(mod_name)
                if not mod:
                    logger.warning(f"Modification {mod_name} not found")
                    continue

                rendered = self._render_template(mod.paragraph_template, full_variables)

                if mod.modification_type == ReportSectionType.EMPHASIS_OF_MATTER:
                    emphasis_paragraph = rendered
                elif mod.modification_type == ReportSectionType.OTHER_MATTER:
                    other_matter_paragraph = rendered
                elif mod.modification_type == ReportSectionType.GOING_CONCERN:
                    going_concern_paragraph = rendered

        # Create report
        report = EngagementReport(
            engagement_id=engagement_id,
            report_type=engagement_type,
            opinion_type=opinion_type,
            report_title=template.report_title,
            report_date=report_date,
            addressee=template.addressee_default or "Board of Directors and Shareholders",
            opinion_paragraph=opinion_paragraph,
            basis_paragraph=basis_paragraph,
            responsibilities_management_paragraph=mgmt_paragraph,
            responsibilities_auditor_paragraph=auditor_paragraph,
            emphasis_of_matter_paragraph=emphasis_paragraph,
            other_matter_paragraph=other_matter_paragraph,
            going_concern_paragraph=going_concern_paragraph,
            firm_name=template_variables.get('firm_name', 'Aura Audit AI'),
            firm_address=template_variables.get('firm_address'),
            partner_name=template_variables.get('partner_name'),
            partner_title=template_variables.get('partner_title', 'Partner'),
            status='draft',
            draft_number=await self._get_next_draft_number(engagement_id),
            drafted_by=user_id,
            drafted_at=datetime.utcnow()
        )

        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)

        logger.info(f"Created report draft {report.id} for engagement {engagement_id}")
        return report

    async def approve_report(
        self,
        report_id: UUID,
        user_id: UUID
    ) -> EngagementReport:
        """
        Approve report for issuance

        Args:
            report_id: Report ID
            user_id: User approving

        Returns:
            Updated report
        """
        report = await self.db.get(EngagementReport, report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        report.status = 'approved'
        report.approved_by = user_id
        report.approved_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(report)

        logger.info(f"Approved report {report_id}")
        return report

    async def issue_report(
        self,
        report_id: UUID,
        final_document_s3_uri: str
    ) -> EngagementReport:
        """
        Issue final report

        Args:
            report_id: Report ID
            final_document_s3_uri: S3 URI of final signed PDF

        Returns:
            Updated report
        """
        report = await self.db.get(EngagementReport, report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        if report.status != 'approved':
            raise ValueError(f"Report must be approved before issuance")

        report.status = 'issued'
        report.issued_at = datetime.utcnow()
        report.final_document_s3_uri = final_document_s3_uri

        await self.db.commit()
        await self.db.refresh(report)

        logger.info(f"Issued report {report_id}")
        return report

    async def generate_complete_report_html(
        self,
        report_id: UUID
    ) -> str:
        """
        Generate complete HTML report

        Args:
            report_id: Report ID

        Returns:
            Complete HTML report
        """
        report = await self.db.get(EngagementReport, report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        # Build complete report HTML
        html_parts = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="UTF-8">',
            '<title>Independent Auditor\'s Report</title>',
            '<style>',
            'body { font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 1.6; margin: 1in; }',
            'h3 { font-size: 12pt; font-weight: bold; margin-top: 20px; }',
            'p { margin: 10px 0; text-align: justify; }',
            'ul { margin: 10px 0 10px 30px; }',
            '.header { text-align: center; font-weight: bold; font-size: 14pt; margin-bottom: 30px; }',
            '.signature { margin-top: 40px; }',
            '</style>',
            '</head>',
            '<body>',

            # Header
            f'<div class="header">{report.report_title}</div>',
            f'<p>{report.addressee}<br>{await self._get_client_address(report.engagement_id)}</p>',

            # Opinion paragraph
            report.opinion_paragraph,

            # Basis for opinion
            report.basis_paragraph or '',

            # Emphasis of matter
            report.emphasis_of_matter_paragraph or '',

            # Going concern
            report.going_concern_paragraph or '',

            # Responsibilities
            report.responsibilities_management_paragraph or '',
            report.responsibilities_auditor_paragraph or '',

            # Other matter
            report.other_matter_paragraph or '',

            # Signature block
            '<div class="signature">',
            f'<p>{report.firm_name}<br>',
            f'{report.firm_address or ""}</p>',
            f'<p>{report.partner_name or ""}<br>',
            f'{report.partner_title or ""}</p>',
            f'<p>{report.report_date.strftime("%B %d, %Y")}</p>',
            '</div>',

            '</body>',
            '</html>'
        ]

        return '\n'.join(html_parts)

    async def _get_opinion_template(
        self,
        opinion_type: OpinionType,
        engagement_type: str
    ) -> Optional[OpinionTemplate]:
        """Get opinion template"""
        query = select(OpinionTemplate).where(
            OpinionTemplate.opinion_type == opinion_type,
            OpinionTemplate.engagement_type == engagement_type,
            OpinionTemplate.is_active == True
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_modification(self, modification_name: str) -> Optional[ReportModification]:
        """Get report modification"""
        query = select(ReportModification).where(
            ReportModification.modification_name == modification_name,
            ReportModification.is_active == True
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_next_draft_number(self, engagement_id: UUID) -> int:
        """Get next draft number for engagement"""
        query = select(EngagementReport).where(
            EngagementReport.engagement_id == engagement_id
        ).order_by(EngagementReport.draft_number.desc())

        result = await self.db.execute(query)
        latest = result.scalar_one_or_none()

        return (latest.draft_number + 1) if latest else 1

    async def _get_client_address(self, engagement_id: UUID) -> str:
        """Get client address from engagement"""
        from .models import Engagement
        engagement = await self.db.get(Engagement, engagement_id)
        # This would come from client/entity table in real implementation
        return engagement.client_name if engagement else ""

    def _render_template(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Render Jinja2 template"""
        if not template_str:
            return ""

        try:
            template = self.template_env.from_string(template_str)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return template_str  # Return unrendered template on error
