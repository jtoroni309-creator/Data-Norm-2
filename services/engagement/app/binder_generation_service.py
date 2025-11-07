"""
Binder Generation Service
Automatically generates standard audit binder structure for engagements
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from .database import Base
from .models import Engagement

logger = logging.getLogger(__name__)


class BinderNode(Base):
    """Binder node (section or workpaper)"""
    __tablename__ = "binder_nodes"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.engagements.id"))
    parent_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.binder_nodes.id"))

    node_type = Column(String(50), nullable=False)  # 'section', 'workpaper'
    section_code = Column(String(20))  # e.g., 'A', 'B-100'
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # Workpaper details
    workpaper_template_id = Column(PGUUID(as_uuid=True))
    content = Column(Text)  # JSON or HTML content
    content_s3_uri = Column(Text)  # For large files

    # Status
    status = Column(String(50), default='not_started')  # 'not_started', 'in_progress', 'complete', 'reviewed'
    is_required = Column(Boolean, default=True)
    is_applicable = Column(Boolean, default=True)

    # Tracking
    assigned_to = Column(PGUUID(as_uuid=True))
    completed_by = Column(PGUUID(as_uuid=True))
    completed_at = Column(DateTime(timezone=True))
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))

    # Position
    position_order = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class BinderGenerationService:
    """Service for generating audit binders"""

    def __init__(self, db: AsyncSession):
        """
        Initialize binder generation service

        Args:
            db: Database session
        """
        self.db = db

    async def generate_standard_binder(
        self,
        engagement_id: UUID,
        engagement_type: str = 'audit',
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Generate standard binder structure for engagement

        Args:
            engagement_id: Engagement ID
            engagement_type: Type of engagement ('audit', 'review', 'compilation')
            user_id: User generating binder

        Returns:
            Dictionary with counts of nodes created
        """
        logger.info(f"Generating standard {engagement_type} binder for engagement {engagement_id}")

        # Get engagement
        engagement = await self.db.get(Engagement, engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        # Get binder structure template
        structure = await self._get_binder_structure_template(engagement_type)

        if not structure:
            raise ValueError(f"No binder structure template found for {engagement_type}")

        # Create binder structure
        counts = {
            'sections': 0,
            'workpapers': 0,
            'total_nodes': 0
        }

        # Group by section
        sections_map = {}
        for row in structure:
            section_code = row['section_code']
            if section_code not in sections_map:
                sections_map[section_code] = {
                    'section_name': row['section_name'],
                    'section_description': row['section_description'],
                    'position_order': row['section_position_order'],
                    'workpapers': []
                }

            if row['workpaper_code']:
                sections_map[section_code]['workpapers'].append({
                    'workpaper_code': row['workpaper_code'],
                    'workpaper_title': row['workpaper_title'],
                    'workpaper_description': row['workpaper_description'],
                    'template_id': row['template_id'],
                    'is_required': row['is_required'],
                    'position_order': row['workpaper_position_order']
                })

        # Create section and workpaper nodes
        for section_code, section_data in sections_map.items():
            # Create section node
            section_node = BinderNode(
                engagement_id=engagement_id,
                parent_id=None,
                node_type='section',
                section_code=section_code,
                title=f"{section_code} - {section_data['section_name']}",
                description=section_data['section_description'],
                status='not_started',
                position_order=section_data['position_order']
            )
            self.db.add(section_node)
            await self.db.flush()  # Get ID for parent reference
            counts['sections'] += 1
            counts['total_nodes'] += 1

            # Create workpaper nodes
            for wp in section_data['workpapers']:
                workpaper_node = BinderNode(
                    engagement_id=engagement_id,
                    parent_id=section_node.id,
                    node_type='workpaper',
                    section_code=wp['workpaper_code'],
                    title=wp['workpaper_title'],
                    description=wp['workpaper_description'],
                    workpaper_template_id=wp['template_id'],
                    status='not_started',
                    is_required=wp['is_required'],
                    position_order=wp['position_order']
                )
                self.db.add(workpaper_node)
                counts['workpapers'] += 1
                counts['total_nodes'] += 1

        await self.db.commit()

        logger.info(f"Generated binder with {counts['sections']} sections and {counts['workpapers']} workpapers")
        return counts

    async def instantiate_workpaper(
        self,
        node_id: UUID,
        template_variables: Optional[Dict[str, Any]] = None,
        user_id: Optional[UUID] = None
    ) -> BinderNode:
        """
        Instantiate workpaper from template

        Args:
            node_id: Binder node ID
            template_variables: Variables to populate template
            user_id: User instantiating

        Returns:
            Updated node with instantiated content
        """
        node = await self.db.get(BinderNode, node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        if node.node_type != 'workpaper':
            raise ValueError(f"Node {node_id} is not a workpaper")

        if not node.workpaper_template_id:
            raise ValueError(f"Node {node_id} has no template")

        # Get template
        template = await self._get_workpaper_template(node.workpaper_template_id)
        if not template:
            raise ValueError(f"Template {node.workpaper_template_id} not found")

        # Render template content
        import jinja2
        template_env = jinja2.Environment(autoescape=True)

        variables = template_variables or {}
        # Add engagement context
        engagement = await self.db.get(Engagement, node.engagement_id)
        variables.update({
            'client_name': engagement.client_name,
            'engagement_type': engagement.engagement_type,
            'fiscal_year_end': engagement.fiscal_year_end,
            'engagement_partner': engagement.engagement_partner
        })

        try:
            jinja_template = template_env.from_string(template['content'])
            rendered_content = jinja_template.render(**variables)

            node.content = rendered_content
            node.status = 'in_progress'
            node.assigned_to = user_id

            await self.db.commit()
            await self.db.refresh(node)

            logger.info(f"Instantiated workpaper {node_id} from template")
            return node

        except Exception as e:
            logger.error(f"Failed to instantiate workpaper: {e}")
            raise

    async def mark_workpaper_complete(
        self,
        node_id: UUID,
        user_id: UUID
    ) -> BinderNode:
        """
        Mark workpaper as complete

        Args:
            node_id: Node ID
            user_id: User completing workpaper

        Returns:
            Updated node
        """
        node = await self.db.get(BinderNode, node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        node.status = 'complete'
        node.completed_by = user_id
        node.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(node)

        logger.info(f"Marked workpaper {node_id} as complete")

        # Check if section is complete
        await self._update_section_status(node.parent_id)

        return node

    async def mark_workpaper_reviewed(
        self,
        node_id: UUID,
        user_id: UUID,
        review_notes: Optional[str] = None
    ) -> BinderNode:
        """
        Mark workpaper as reviewed

        Args:
            node_id: Node ID
            user_id: User reviewing
            review_notes: Optional review notes

        Returns:
            Updated node
        """
        node = await self.db.get(BinderNode, node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        if node.status != 'complete':
            raise ValueError(f"Workpaper must be complete before review")

        node.status = 'reviewed'
        node.reviewed_by = user_id
        node.reviewed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(node)

        logger.info(f"Marked workpaper {node_id} as reviewed")
        return node

    async def get_binder_summary(self, engagement_id: UUID) -> Dict[str, Any]:
        """
        Get binder completion summary

        Args:
            engagement_id: Engagement ID

        Returns:
            Summary statistics
        """
        query = text("""
            SELECT
                COUNT(*) FILTER (WHERE node_type = 'section') AS total_sections,
                COUNT(*) FILTER (WHERE node_type = 'workpaper') AS total_workpapers,
                COUNT(*) FILTER (WHERE node_type = 'workpaper' AND is_required = TRUE) AS required_workpapers,
                COUNT(*) FILTER (WHERE node_type = 'workpaper' AND status = 'complete') AS completed_workpapers,
                COUNT(*) FILTER (WHERE node_type = 'workpaper' AND status = 'reviewed') AS reviewed_workpapers,
                COUNT(*) FILTER (WHERE node_type = 'workpaper' AND is_required = TRUE AND status NOT IN ('complete', 'reviewed')) AS incomplete_required,
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE node_type = 'workpaper' AND status IN ('complete', 'reviewed')) /
                    NULLIF(COUNT(*) FILTER (WHERE node_type = 'workpaper' AND is_required = TRUE), 0),
                    2
                ) AS completion_percentage
            FROM atlas.binder_nodes
            WHERE engagement_id = :engagement_id
        """)

        result = await self.db.execute(query, {"engagement_id": engagement_id})
        row = result.fetchone()

        if not row:
            return {
                'total_sections': 0,
                'total_workpapers': 0,
                'required_workpapers': 0,
                'completed_workpapers': 0,
                'reviewed_workpapers': 0,
                'incomplete_required': 0,
                'completion_percentage': 0.0
            }

        return {
            'total_sections': row[0] or 0,
            'total_workpapers': row[1] or 0,
            'required_workpapers': row[2] or 0,
            'completed_workpapers': row[3] or 0,
            'reviewed_workpapers': row[4] or 0,
            'incomplete_required': row[5] or 0,
            'completion_percentage': float(row[6]) if row[6] else 0.0
        }

    async def get_incomplete_workpapers(
        self,
        engagement_id: UUID,
        section_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of incomplete workpapers

        Args:
            engagement_id: Engagement ID
            section_code: Optional filter by section

        Returns:
            List of incomplete workpapers
        """
        query_str = """
            SELECT
                bn.id,
                bn.section_code,
                bn.title,
                bn.description,
                bn.status,
                bn.is_required,
                bn.assigned_to,
                parent.section_code AS parent_section_code,
                parent.title AS parent_section_title
            FROM atlas.binder_nodes bn
            LEFT JOIN atlas.binder_nodes parent ON parent.id = bn.parent_id
            WHERE bn.engagement_id = :engagement_id
            AND bn.node_type = 'workpaper'
            AND bn.status NOT IN ('complete', 'reviewed')
            AND bn.is_required = TRUE
        """

        if section_code:
            query_str += " AND parent.section_code = :section_code"

        query_str += " ORDER BY parent.position_order, bn.position_order"

        params = {"engagement_id": engagement_id}
        if section_code:
            params["section_code"] = section_code

        result = await self.db.execute(text(query_str), params)
        rows = result.fetchall()

        incomplete = []
        for row in rows:
            incomplete.append({
                'node_id': row[0],
                'workpaper_code': row[1],
                'title': row[2],
                'description': row[3],
                'status': row[4],
                'is_required': row[5],
                'assigned_to': row[6],
                'section_code': row[7],
                'section_title': row[8]
            })

        return incomplete

    async def _get_binder_structure_template(self, engagement_type: str) -> List[Dict[str, Any]]:
        """Get binder structure template from database"""
        query = text("""
            SELECT
                bst.section_code,
                bst.section_name,
                bst.section_description,
                bst.position_order AS section_position_order,
                wpt.workpaper_code,
                wpt.workpaper_title,
                wpt.workpaper_description,
                wpt.template_content,
                wpt.id AS template_id,
                wpt.is_required,
                wpt.position_order AS workpaper_position_order
            FROM atlas.binder_structure_templates bst
            LEFT JOIN atlas.workpaper_templates wpt
                ON wpt.section_code = bst.section_code
                AND wpt.engagement_type = bst.engagement_type
            WHERE bst.engagement_type = :engagement_type
            AND bst.is_active = TRUE
            ORDER BY bst.position_order, wpt.position_order
        """)

        result = await self.db.execute(query, {"engagement_type": engagement_type})
        rows = result.fetchall()

        return [
            {
                'section_code': row[0],
                'section_name': row[1],
                'section_description': row[2],
                'section_position_order': row[3],
                'workpaper_code': row[4],
                'workpaper_title': row[5],
                'workpaper_description': row[6],
                'template_content': row[7],
                'template_id': row[8],
                'is_required': row[9],
                'workpaper_position_order': row[10]
            }
            for row in rows
        ]

    async def _get_workpaper_template(self, template_id: UUID) -> Optional[Dict[str, Any]]:
        """Get workpaper template by ID"""
        query = text("""
            SELECT
                id,
                workpaper_code,
                workpaper_title,
                template_content
            FROM atlas.workpaper_templates
            WHERE id = :template_id
        """)

        result = await self.db.execute(query, {"template_id": template_id})
        row = result.fetchone()

        if not row:
            return None

        return {
            'id': row[0],
            'code': row[1],
            'title': row[2],
            'content': row[3]
        }

    async def _update_section_status(self, section_id: UUID):
        """Update section status based on workpaper completion"""
        if not section_id:
            return

        # Get all workpapers in section
        query = text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status IN ('complete', 'reviewed')) AS completed
            FROM atlas.binder_nodes
            WHERE parent_id = :section_id
            AND node_type = 'workpaper'
            AND is_required = TRUE
        """)

        result = await self.db.execute(query, {"section_id": section_id})
        row = result.fetchone()

        if row and row[0] > 0:
            section = await self.db.get(BinderNode, section_id)
            if section:
                if row[1] == row[0]:
                    section.status = 'complete'
                elif row[1] > 0:
                    section.status = 'in_progress'
                else:
                    section.status = 'not_started'

                await self.db.commit()
                logger.info(f"Updated section {section_id} status to {section.status}")
