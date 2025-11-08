"""
Disclosure Checklist Service
Manages GAAP disclosure requirements and tracks completion
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, Date, DateTime, Boolean, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from enum import Enum as PyEnum
import jinja2

from .database import Base

logger = logging.getLogger(__name__)


class ASCTopicCategory(str, PyEnum):
    """ASC topic categories"""
    PRESENTATION = "presentation"
    ASSETS = "assets"
    LIABILITIES = "liabilities"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSES = "expenses"
    BROAD_TRANSACTIONS = "broad_transactions"
    INDUSTRY_SPECIFIC = "industry_specific"


class DisclosureRequirementLevel(str, PyEnum):
    """Requirement levels"""
    REQUIRED = "required"
    CONDITIONAL = "conditional"
    RECOMMENDED = "recommended"
    INDUSTRY_SPECIFIC = "industry_specific"


class ASCTopic(Base):
    """ASC topic"""
    __tablename__ = "asc_topics"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    topic_number = Column(String(20), nullable=False, unique=True)
    topic_name = Column(String(255), nullable=False)
    category = Column(SQLEnum(ASCTopicCategory), nullable=False)
    description = Column(Text)
    effective_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class DisclosureRequirement(Base):
    """Disclosure requirement"""
    __tablename__ = "disclosure_requirements"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    asc_topic_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.asc_topics.id"))
    requirement_code = Column(String(50), nullable=False)
    requirement_title = Column(String(500), nullable=False)
    requirement_description = Column(Text, nullable=False)
    requirement_level = Column(SQLEnum(DisclosureRequirementLevel), nullable=False)
    applies_to_public = Column(Boolean, default=True)
    applies_to_private = Column(Boolean, default=True)
    applies_to_nonprofit = Column(Boolean, default=False)
    condition_description = Column(Text)
    materiality_threshold = Column(String(100))
    disclosure_template = Column(Text)
    example_disclosure = Column(Text)
    position_order = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class EngagementDisclosureChecklist(Base):
    """Engagement disclosure tracking"""
    __tablename__ = "engagement_disclosure_checklist"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    engagement_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.engagements.id"))
    disclosure_requirement_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.disclosure_requirements.id"))
    is_applicable = Column(Boolean)
    applicability_reason = Column(Text)
    is_complete = Column(Boolean, default=False)
    completion_status = Column(String(50))
    draft_disclosure = Column(Text)
    final_disclosure = Column(Text)
    note_reference = Column(String(100))
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text)
    requires_revision = Column(Boolean, default=False)
    created_by = Column(PGUUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class FinancialStatementNoteTemplate(Base):
    """Note template"""
    __tablename__ = "financial_statement_note_templates"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    asc_topic_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.asc_topics.id"))
    note_title = Column(String(255), nullable=False)
    note_number = Column(String(20))
    note_category = Column(String(100))
    template_content = Column(Text, nullable=False)
    template_description = Column(Text)
    typical_position_order = Column(Integer)
    is_standard = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(PGUUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class DisclosureChecklistService:
    """Service for managing disclosure checklist"""

    def __init__(self, db: AsyncSession):
        """
        Initialize disclosure checklist service

        Args:
            db: Database session
        """
        self.db = db
        self.template_env = jinja2.Environment(autoescape=True)

    async def initialize_checklist(
        self,
        engagement_id: UUID,
        entity_type: str = 'private',  # 'public', 'private', 'nonprofit'
        user_id: Optional[UUID] = None
    ) -> Dict[str, int]:
        """
        Initialize disclosure checklist for engagement

        Args:
            engagement_id: Engagement ID
            entity_type: Type of entity (public, private, nonprofit)
            user_id: User initializing checklist

        Returns:
            Dictionary with counts of requirements added
        """
        logger.info(f"Initializing disclosure checklist for engagement {engagement_id}")

        # Get all active disclosure requirements applicable to this entity type
        query = select(DisclosureRequirement).where(
            DisclosureRequirement.is_active == True
        )

        if entity_type == 'public':
            query = query.where(DisclosureRequirement.applies_to_public == True)
        elif entity_type == 'private':
            query = query.where(DisclosureRequirement.applies_to_private == True)
        elif entity_type == 'nonprofit':
            query = query.where(DisclosureRequirement.applies_to_nonprofit == True)

        result = await self.db.execute(query)
        requirements = result.scalars().all()

        # Create checklist items
        counts = {
            'total': 0,
            'required': 0,
            'conditional': 0,
            'recommended': 0
        }

        for req in requirements:
            # Check if already exists
            existing = await self.db.execute(
                select(EngagementDisclosureChecklist).where(
                    EngagementDisclosureChecklist.engagement_id == engagement_id,
                    EngagementDisclosureChecklist.disclosure_requirement_id == req.id
                )
            )
            if existing.scalar_one_or_none():
                continue

            # Create checklist item
            checklist_item = EngagementDisclosureChecklist(
                engagement_id=engagement_id,
                disclosure_requirement_id=req.id,
                is_applicable=None,  # To be determined
                completion_status='not_started',
                created_by=user_id
            )

            self.db.add(checklist_item)
            counts['total'] += 1

            if req.requirement_level == DisclosureRequirementLevel.REQUIRED:
                counts['required'] += 1
            elif req.requirement_level == DisclosureRequirementLevel.CONDITIONAL:
                counts['conditional'] += 1
            elif req.requirement_level == DisclosureRequirementLevel.RECOMMENDED:
                counts['recommended'] += 1

        await self.db.commit()
        logger.info(f"Initialized {counts['total']} disclosure requirements for engagement {engagement_id}")

        return counts

    async def mark_disclosure_applicability(
        self,
        checklist_item_id: UUID,
        is_applicable: bool,
        reason: str,
        user_id: Optional[UUID] = None
    ) -> EngagementDisclosureChecklist:
        """
        Mark whether a disclosure requirement applies to this engagement

        Args:
            checklist_item_id: Checklist item ID
            is_applicable: Whether requirement applies
            reason: Reason for applicability determination
            user_id: User making determination

        Returns:
            Updated checklist item
        """
        item = await self.db.get(EngagementDisclosureChecklist, checklist_item_id)
        if not item:
            raise ValueError(f"Checklist item {checklist_item_id} not found")

        item.is_applicable = is_applicable
        item.applicability_reason = reason
        item.completion_status = 'not_applicable' if not is_applicable else 'not_started'

        await self.db.commit()
        await self.db.refresh(item)

        logger.info(f"Marked disclosure {checklist_item_id} as {'applicable' if is_applicable else 'not applicable'}")
        return item

    async def draft_disclosure(
        self,
        checklist_item_id: UUID,
        template_variables: Dict[str, Any],
        user_id: Optional[UUID] = None
    ) -> str:
        """
        Generate disclosure draft from template

        Args:
            checklist_item_id: Checklist item ID
            template_variables: Variables to populate template
            user_id: User drafting disclosure

        Returns:
            Drafted disclosure text (HTML)
        """
        # Get checklist item and requirement
        item = await self.db.get(EngagementDisclosureChecklist, checklist_item_id)
        if not item:
            raise ValueError(f"Checklist item {checklist_item_id} not found")

        requirement = await self.db.get(DisclosureRequirement, item.disclosure_requirement_id)
        if not requirement or not requirement.disclosure_template:
            raise ValueError(f"No template found for requirement")

        # Render template
        jinja_template = self.template_env.from_string(requirement.disclosure_template)
        drafted_text = jinja_template.render(**template_variables)

        # Save draft
        item.draft_disclosure = drafted_text
        item.completion_status = 'in_progress'

        await self.db.commit()
        await self.db.refresh(item)

        logger.info(f"Drafted disclosure for checklist item {checklist_item_id}")
        return drafted_text

    async def finalize_disclosure(
        self,
        checklist_item_id: UUID,
        final_text: str,
        note_reference: str,
        user_id: Optional[UUID] = None
    ) -> EngagementDisclosureChecklist:
        """
        Finalize disclosure after review

        Args:
            checklist_item_id: Checklist item ID
            final_text: Final approved disclosure text
            note_reference: Which note this appears in (e.g., "Note 2")
            user_id: User finalizing

        Returns:
            Updated checklist item
        """
        item = await self.db.get(EngagementDisclosureChecklist, checklist_item_id)
        if not item:
            raise ValueError(f"Checklist item {checklist_item_id} not found")

        item.final_disclosure = final_text
        item.note_reference = note_reference
        item.is_complete = True
        item.completion_status = 'complete'
        item.reviewed_by = user_id
        item.reviewed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(item)

        logger.info(f"Finalized disclosure {checklist_item_id} in {note_reference}")
        return item

    async def get_checklist_summary(self, engagement_id: UUID) -> Dict[str, Any]:
        """
        Get disclosure checklist summary

        Args:
            engagement_id: Engagement ID

        Returns:
            Summary statistics
        """
        query = text("""
            SELECT
                COUNT(*) AS total_requirements,
                COUNT(CASE WHEN is_applicable = TRUE THEN 1 END) AS applicable_requirements,
                COUNT(CASE WHEN is_applicable = TRUE AND is_complete = TRUE THEN 1 END) AS completed_requirements,
                COUNT(CASE WHEN is_applicable = TRUE AND is_complete = FALSE THEN 1 END) AS incomplete_requirements,
                COUNT(CASE WHEN is_applicable IS NULL THEN 1 END) AS undetermined_requirements,
                ROUND(
                    100.0 * COUNT(CASE WHEN is_applicable = TRUE AND is_complete = TRUE THEN 1 END) /
                    NULLIF(COUNT(CASE WHEN is_applicable = TRUE THEN 1 END), 0),
                    2
                ) AS completion_percentage
            FROM atlas.engagement_disclosure_checklist
            WHERE engagement_id = :engagement_id
        """)

        result = await self.db.execute(query, {"engagement_id": engagement_id})
        row = result.fetchone()

        if not row:
            return {
                'total_requirements': 0,
                'applicable_requirements': 0,
                'completed_requirements': 0,
                'incomplete_requirements': 0,
                'undetermined_requirements': 0,
                'completion_percentage': 0.0
            }

        return {
            'total_requirements': row[0],
            'applicable_requirements': row[1],
            'completed_requirements': row[2],
            'incomplete_requirements': row[3],
            'undetermined_requirements': row[4],
            'completion_percentage': float(row[5]) if row[5] else 0.0
        }

    async def get_incomplete_disclosures(
        self,
        engagement_id: UUID,
        requirement_level: Optional[DisclosureRequirementLevel] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of incomplete disclosures

        Args:
            engagement_id: Engagement ID
            requirement_level: Optional filter by requirement level

        Returns:
            List of incomplete disclosure requirements
        """
        query = text("""
            SELECT
                edc.id,
                dr.requirement_code,
                dr.requirement_title,
                dr.requirement_level,
                dr.requirement_description,
                asc.topic_number,
                asc.topic_name,
                edc.completion_status,
                edc.applicability_reason
            FROM atlas.engagement_disclosure_checklist edc
            JOIN atlas.disclosure_requirements dr ON dr.id = edc.disclosure_requirement_id
            JOIN atlas.asc_topics asc ON asc.id = dr.asc_topic_id
            WHERE edc.engagement_id = :engagement_id
            AND edc.is_applicable = TRUE
            AND edc.is_complete = FALSE
            ORDER BY dr.requirement_level, asc.topic_number, dr.position_order
        """)

        result = await self.db.execute(query, {"engagement_id": engagement_id})
        rows = result.fetchall()

        incomplete = []
        for row in rows:
            if requirement_level and row[3] != requirement_level.value:
                continue

            incomplete.append({
                'checklist_item_id': row[0],
                'requirement_code': row[1],
                'requirement_title': row[2],
                'requirement_level': row[3],
                'requirement_description': row[4],
                'asc_topic_number': row[5],
                'asc_topic_name': row[6],
                'completion_status': row[7],
                'applicability_reason': row[8]
            })

        return incomplete

    async def get_note_template(
        self,
        asc_topic_number: str,
        note_category: Optional[str] = None
    ) -> Optional[FinancialStatementNoteTemplate]:
        """
        Get note template by ASC topic

        Args:
            asc_topic_number: ASC topic number (e.g., '606', '842')
            note_category: Optional category filter

        Returns:
            Note template or None
        """
        query = select(FinancialStatementNoteTemplate).join(
            ASCTopic,
            ASCTopic.id == FinancialStatementNoteTemplate.asc_topic_id
        ).where(
            ASCTopic.topic_number == asc_topic_number,
            FinancialStatementNoteTemplate.is_active == True
        )

        if note_category:
            query = query.where(FinancialStatementNoteTemplate.note_category == note_category)

        query = query.order_by(FinancialStatementNoteTemplate.typical_position_order)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def generate_complete_notes(
        self,
        engagement_id: UUID,
        template_variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate complete set of financial statement notes

        Args:
            engagement_id: Engagement ID
            template_variables: Global variables for all templates

        Returns:
            List of generated notes with titles and content
        """
        # Get all completed disclosures
        query = text("""
            SELECT
                edc.note_reference,
                edc.final_disclosure,
                dr.requirement_title,
                asc.topic_name,
                dr.position_order
            FROM atlas.engagement_disclosure_checklist edc
            JOIN atlas.disclosure_requirements dr ON dr.id = edc.disclosure_requirement_id
            JOIN atlas.asc_topics asc ON asc.id = dr.asc_topic_id
            WHERE edc.engagement_id = :engagement_id
            AND edc.is_complete = TRUE
            AND edc.final_disclosure IS NOT NULL
            ORDER BY edc.note_reference, dr.position_order
        """)

        result = await self.db.execute(query, {"engagement_id": engagement_id})
        rows = result.fetchall()

        # Group by note reference
        notes_by_reference = {}
        for row in rows:
            note_ref = row[0] or "Uncategorized"
            if note_ref not in notes_by_reference:
                notes_by_reference[note_ref] = {
                    'note_reference': note_ref,
                    'note_title': row[3],  # Topic name
                    'disclosures': []
                }
            notes_by_reference[note_ref]['disclosures'].append({
                'title': row[2],
                'content': row[1]
            })

        # Convert to list
        notes = list(notes_by_reference.values())

        logger.info(f"Generated {len(notes)} complete notes for engagement {engagement_id}")
        return notes
