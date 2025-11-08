"""
Engagement Workflow Service
Orchestrates complete engagement lifecycle from creation to report issuance
"""
import logging
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from enum import Enum as PyEnum

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Engagement
from .binder_generation_service import BinderGenerationService
from .confirmation_service import ConfirmationService
from .database import Base

logger = logging.getLogger(__name__)


class EngagementPhase(str, PyEnum):
    """Engagement workflow phases"""
    PLANNING = "planning"
    RISK_ASSESSMENT = "risk_assessment"
    FIELDWORK = "fieldwork"
    CONFIRMATIONS = "confirmations"
    ANALYTICAL_PROCEDURES = "analytical_procedures"
    DISCLOSURE_DRAFTING = "disclosure_drafting"
    REPORTING = "reporting"
    REVIEW = "review"
    FINALIZATION = "finalization"
    COMPLETE = "complete"


class EngagementWorkflowService:
    """Service for managing complete engagement workflow"""

    def __init__(self, db: AsyncSession):
        """
        Initialize engagement workflow service

        Args:
            db: Database session
        """
        self.db = db
        self.binder_service = BinderGenerationService(db)
        self.confirmation_service = ConfirmationService(db)

    async def create_engagement_with_workflow(
        self,
            client_name: str,
        engagement_type: str,
        fiscal_year_end: date,
        engagement_partner: str,
        entity_type: str = 'private',
        user_id: Optional[UUID] = None
    ) -> Tuple[Engagement, Dict[str, Any]]:
        """
        Create engagement and initialize complete workflow

        Args:
            client_name: Client company name
            engagement_type: Type ('audit', 'review', 'compilation')
            fiscal_year_end: Fiscal year end date
            engagement_partner: Partner name
            entity_type: Entity type ('public', 'private', 'nonprofit')
            user_id: User creating engagement

        Returns:
            Tuple of (Engagement, initialization summary)
        """
        logger.info(f"Creating {engagement_type} engagement for {client_name}")

        # Create engagement
        engagement = Engagement(
            client_name=client_name,
            engagement_type=engagement_type,
            fiscal_year_end=fiscal_year_end,
            engagement_partner=engagement_partner,
            status='planning',
            current_phase='planning',
            created_by=user_id
        )

        self.db.add(engagement)
        await self.db.commit()
        await self.db.refresh(engagement)

        summary = {
            'engagement_id': engagement.id,
            'client_name': client_name,
            'engagement_type': engagement_type
        }

        # Initialize binder structure
        logger.info(f"Generating binder structure for engagement {engagement.id}")
        binder_counts = await self.binder_service.generate_standard_binder(
            engagement.id,
            engagement_type,
            user_id
        )
        summary['binder'] = binder_counts

        # Initialize disclosure checklist (if audit or review)
        if engagement_type in ['audit', 'review']:
            logger.info(f"Initializing disclosure checklist for engagement {engagement.id}")
            # Import here to avoid circular dependency
            from services.reporting.app.disclosure_checklist_service import DisclosureChecklistService
            disclosure_service = DisclosureChecklistService(self.db)
            disclosure_counts = await disclosure_service.initialize_checklist(
                engagement.id,
                entity_type,
                user_id
            )
            summary['disclosures'] = disclosure_counts

        logger.info(f"Created engagement {engagement.id} with complete workflow")
        return engagement, summary

    async def advance_to_next_phase(
        self,
        engagement_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Engagement:
        """
        Advance engagement to next workflow phase

        Args:
            engagement_id: Engagement ID
            user_id: User advancing phase

        Returns:
            Updated engagement
        """
        engagement = await self.db.get(Engagement, engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        # Verify current phase is complete
        phase_complete = await self._verify_phase_complete(engagement)
        if not phase_complete:
            raise ValueError(f"Current phase '{engagement.current_phase}' is not complete")

        # Determine next phase
        current_phase = EngagementPhase(engagement.current_phase)
        phase_sequence = list(EngagementPhase)
        current_index = phase_sequence.index(current_phase)

        if current_index < len(phase_sequence) - 1:
            next_phase = phase_sequence[current_index + 1]
            engagement.current_phase = next_phase.value

            if next_phase == EngagementPhase.COMPLETE:
                engagement.status = 'complete'
            else:
                engagement.status = 'in_progress'

            await self.db.commit()
            await self.db.refresh(engagement)

            logger.info(f"Advanced engagement {engagement_id} to phase {next_phase.value}")
        else:
            logger.warning(f"Engagement {engagement_id} already at final phase")

        return engagement

    async def get_engagement_dashboard(self, engagement_id: UUID) -> Dict[str, Any]:
        """
        Get comprehensive engagement dashboard

        Args:
            engagement_id: Engagement ID

        Returns:
            Dashboard data with all key metrics
        """
        engagement = await self.db.get(Engagement, engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        dashboard = {
            'engagement': {
                'id': str(engagement.id),
                'client_name': engagement.client_name,
                'engagement_type': engagement.engagement_type,
                'fiscal_year_end': engagement.fiscal_year_end.isoformat(),
                'status': engagement.status,
                'current_phase': engagement.current_phase
            }
        }

        # Binder summary
        binder_summary = await self.binder_service.get_binder_summary(engagement_id)
        dashboard['binder'] = binder_summary

        # Confirmation summary
        confirmation_summary = await self.confirmation_service.get_confirmation_summary(engagement_id)
        dashboard['confirmations'] = confirmation_summary

        # Disclosure checklist summary (if applicable)
        if engagement.engagement_type in ['audit', 'review']:
            from services.reporting.app.disclosure_checklist_service import DisclosureChecklistService
            disclosure_service = DisclosureChecklistService(self.db)
            disclosure_summary = await disclosure_service.get_checklist_summary(engagement_id)
            dashboard['disclosures'] = disclosure_summary

        # Overall completion
        dashboard['overall_completion'] = await self._calculate_overall_completion(engagement_id, engagement.engagement_type)

        return dashboard

    async def get_engagement_blockers(self, engagement_id: UUID) -> List[Dict[str, Any]]:
        """
        Identify items blocking engagement completion

        Args:
            engagement_id: Engagement ID

        Returns:
            List of blocking items
        """
        engagement = await self.db.get(Engagement, engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        blockers = []

        # Check incomplete required workpapers
        incomplete_workpapers = await self.binder_service.get_incomplete_workpapers(engagement_id)
        for wp in incomplete_workpapers:
            blockers.append({
                'type': 'workpaper',
                'severity': 'high' if wp['is_required'] else 'medium',
                'description': f"Required workpaper not complete: {wp['title']}",
                'section': wp['section_title'],
                'item_id': wp['node_id']
            })

        # Check unresolved confirmation exceptions
        query = text("""
            SELECT id, entity_name, confirmation_type, exception_description
            FROM atlas.confirmations
            WHERE engagement_id = :engagement_id
            AND has_exception = TRUE
            AND exception_resolved = FALSE
        """)
        result = await self.db.execute(query, {"engagement_id": engagement_id})
        for row in result.fetchall():
            blockers.append({
                'type': 'confirmation_exception',
                'severity': 'high',
                'description': f"Unresolved confirmation exception: {row[1]} ({row[2]})",
                'details': row[3],
                'item_id': row[0]
            })

        # Check incomplete required disclosures
        if engagement.engagement_type in ['audit', 'review']:
            from services.reporting.app.disclosure_checklist_service import DisclosureChecklistService
            disclosure_service = DisclosureChecklistService(self.db)
            from services.reporting.app.disclosure_checklist_service import DisclosureRequirementLevel

            incomplete_disclosures = await disclosure_service.get_incomplete_disclosures(
                engagement_id,
                DisclosureRequirementLevel.REQUIRED
            )
            for disc in incomplete_disclosures:
                blockers.append({
                    'type': 'disclosure',
                    'severity': 'high',
                    'description': f"Required disclosure incomplete: {disc['requirement_title']}",
                    'asc_topic': disc['asc_topic_number'],
                    'item_id': disc['checklist_item_id']
                })

        # Check confirmations not sent
        query = text("""
            SELECT id, entity_name, confirmation_type
            FROM atlas.confirmations
            WHERE engagement_id = :engagement_id
            AND status = 'not_sent'
        """)
        result = await self.db.execute(query, {"engagement_id": engagement_id})
        for row in result.fetchall():
            blockers.append({
                'type': 'confirmation_not_sent',
                'severity': 'medium',
                'description': f"Confirmation not sent: {row[1]} ({row[2]})",
                'item_id': row[0]
            })

        logger.info(f"Found {len(blockers)} blockers for engagement {engagement_id}")
        return blockers

    async def generate_final_report_draft(
        self,
        engagement_id: UUID,
        opinion_type: str,
        report_date: date,
        template_variables: Dict[str, Any],
        user_id: Optional[UUID] = None
    ) -> UUID:
        """
        Generate final report draft

        Args:
            engagement_id: Engagement ID
            opinion_type: Opinion type
            report_date: Report date
            template_variables: Variables for report
            user_id: User generating report

        Returns:
            Report ID
        """
        engagement = await self.db.get(Engagement, engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        # Verify no critical blockers
        blockers = await self.get_engagement_blockers(engagement_id)
        critical_blockers = [b for b in blockers if b['severity'] == 'high']

        if critical_blockers:
            raise ValueError(f"Cannot generate report: {len(critical_blockers)} critical blockers exist")

        # Generate report
        from services.reporting.app.opinion_service import OpinionService, OpinionType
        opinion_service = OpinionService(self.db)

        report = await opinion_service.generate_report_draft(
            engagement_id,
            OpinionType(opinion_type),
            report_date,
            template_variables,
            user_id
        )

        logger.info(f"Generated report draft {report.id} for engagement {engagement_id}")
        return report.id

    async def _verify_phase_complete(self, engagement: Engagement) -> bool:
        """Verify current phase requirements are met"""
        current_phase = EngagementPhase(engagement.current_phase)

        if current_phase == EngagementPhase.PLANNING:
            # Check planning workpapers complete
            incomplete = await self.binder_service.get_incomplete_workpapers(
                engagement.id,
                section_code='A'
            )
            return len(incomplete) == 0

        elif current_phase == EngagementPhase.CONFIRMATIONS:
            # Check confirmations sent/received
            query = text("""
                SELECT COUNT(*)
                FROM atlas.confirmations
                WHERE engagement_id = :engagement_id
                AND status = 'not_sent'
            """)
            result = await self.db.execute(query, {"engagement_id": engagement.id})
            count = result.scalar()
            return count == 0

        elif current_phase == EngagementPhase.DISCLOSURE_DRAFTING:
            # Check required disclosures complete
            if engagement.engagement_type in ['audit', 'review']:
                from services.reporting.app.disclosure_checklist_service import DisclosureChecklistService
                disclosure_service = DisclosureChecklistService(self.db)
                summary = await disclosure_service.get_checklist_summary(engagement.id)
                return summary['incomplete_requirements'] == 0
            return True

        elif current_phase == EngagementPhase.FIELDWORK:
            # Check core fieldwork sections complete (B-G)
            for section in ['B', 'C', 'D', 'E', 'F', 'G']:
                incomplete = await self.binder_service.get_incomplete_workpapers(
                    engagement.id,
                    section_code=section
                )
                if len(incomplete) > 0:
                    return False
            return True

        # Default: allow advancement
        return True

    async def _calculate_overall_completion(
        self,
        engagement_id: UUID,
        engagement_type: str
    ) -> float:
        """Calculate overall engagement completion percentage"""
        weights = {
            'binder': 0.40,
            'confirmations': 0.20,
            'disclosures': 0.20 if engagement_type in ['audit', 'review'] else 0.0,
            'other': 0.20
        }

        # Binder completion
        binder_summary = await self.binder_service.get_binder_summary(engagement_id)
        binder_pct = binder_summary.get('completion_percentage', 0.0)

        # Confirmation completion
        confirmation_summary = await self.confirmation_service.get_confirmation_summary(engagement_id)
        if confirmation_summary['total'] > 0:
            conf_pct = (confirmation_summary['by_status'].get('received', 0) +
                       confirmation_summary['by_status'].get('resolved', 0) +
                       confirmation_summary['alternative_procedures_count']) / confirmation_summary['total'] * 100
        else:
            conf_pct = 100.0  # No confirmations = complete

        # Disclosure completion
        if engagement_type in ['audit', 'review']:
            from services.reporting.app.disclosure_checklist_service import DisclosureChecklistService
            disclosure_service = DisclosureChecklistService(self.db)
            disclosure_summary = await disclosure_service.get_checklist_summary(engagement_id)
            disc_pct = disclosure_summary.get('completion_percentage', 0.0)
        else:
            disc_pct = 100.0

        # Weighted average
        overall = (
            binder_pct * weights['binder'] +
            conf_pct * weights['confirmations'] +
            disc_pct * weights['disclosures'] +
            100.0 * weights['other']  # Placeholder for other items
        )

        return round(overall, 2)


# Import at bottom to avoid circular dependency
from typing import Tuple
