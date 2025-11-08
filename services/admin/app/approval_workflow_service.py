"""
Approval Workflow Service
Manages multi-level approval workflows with configurable chains
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from enum import Enum as PyEnum

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ApprovalStatus(str, PyEnum):
    """Approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"


class ApprovalWorkflowService:
    """Service for managing approval workflows"""

    def __init__(self, db: AsyncSession):
        """
        Initialize approval workflow service

        Args:
            db: Database session
        """
        self.db = db

    async def create_approval_chain(
        self,
        firm_id: UUID,
        chain_name: str,
        resource_type: str,
        approval_levels: List[Dict[str, Any]],
        created_by_user_id: Optional[UUID] = None
    ) -> UUID:
        """
        Create approval chain

        Args:
            firm_id: Firm ID
            chain_name: Chain name
            resource_type: Resource type ('workpaper', 'report', 'engagement')
            approval_levels: List of approval levels
                Example: [
                    {"level": 1, "role_id": "senior_role_uuid", "required": True},
                    {"level": 2, "role_id": "manager_role_uuid", "required": True},
                    {"level": 3, "role_id": "partner_role_uuid", "required": True}
                ]
            created_by_user_id: User creating chain

        Returns:
            Approval chain ID
        """
        logger.info(f"Creating approval chain '{chain_name}' for firm {firm_id}")

        import json

        insert_query = text("""
            INSERT INTO atlas.approval_chains (
                cpa_firm_id, chain_name, resource_type, approval_levels
            ) VALUES (
                :firm_id, :chain_name, :resource_type, :approval_levels::jsonb
            )
            RETURNING id
        """)

        result = await self.db.execute(insert_query, {
            "firm_id": firm_id,
            "chain_name": chain_name,
            "resource_type": resource_type,
            "approval_levels": json.dumps(approval_levels)
        })

        chain_id = result.scalar_one()
        await self.db.commit()

        logger.info(f"Created approval chain {chain_id}")
        return chain_id

    async def request_approval(
        self,
        approval_chain_id: UUID,
        resource_type: str,
        resource_id: UUID,
        requested_by_user_id: UUID,
        request_description: Optional[str] = None
    ) -> UUID:
        """
        Submit approval request

        Args:
            approval_chain_id: Approval chain ID
            resource_type: Resource type
            resource_id: Resource ID
            requested_by_user_id: User requesting approval
            request_description: Description of request

        Returns:
            Approval request ID
        """
        logger.info(f"Creating approval request for {resource_type} {resource_id}")

        insert_query = text("""
            INSERT INTO atlas.approval_requests (
                approval_chain_id, resource_type, resource_id,
                requested_by, request_description
            ) VALUES (
                :chain_id, :resource_type, :resource_id,
                :requested_by, :description
            )
            RETURNING id
        """)

        result = await self.db.execute(insert_query, {
            "chain_id": approval_chain_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "requested_by": requested_by_user_id,
            "description": request_description
        })

        request_id = result.scalar_one()
        await self.db.commit()

        logger.info(f"Created approval request {request_id}")
        return request_id

    async def approve(
        self,
        approval_request_id: UUID,
        approver_user_id: UUID,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve request

        Args:
            approval_request_id: Approval request ID
            approver_user_id: User approving
            notes: Optional approval notes

        Returns:
            Updated approval status
        """
        logger.info(f"Processing approval for request {approval_request_id} by user {approver_user_id}")

        # Get current request status
        request_query = text("""
            SELECT
                ar.id,
                ar.current_approval_level,
                ar.overall_status,
                ac.approval_levels
            FROM atlas.approval_requests ar
            JOIN atlas.approval_chains ac ON ac.id = ar.approval_chain_id
            WHERE ar.id = :request_id
        """)

        result = await self.db.execute(request_query, {"request_id": approval_request_id})
        row = result.fetchone()

        if not row:
            raise ValueError(f"Approval request {approval_request_id} not found")

        current_level = row[1]
        approval_levels = row[3]

        # Verify approver has correct role for this level
        import json
        levels = json.loads(approval_levels) if isinstance(approval_levels, str) else approval_levels

        current_level_config = next((l for l in levels if l['level'] == current_level), None)
        if not current_level_config:
            raise ValueError(f"No configuration for approval level {current_level}")

        # Check if approver has required role
        role_check_query = text("""
            SELECT COUNT(*) > 0
            FROM atlas.user_roles
            WHERE user_id = :user_id AND role_id = :role_id
        """)

        result = await self.db.execute(role_check_query, {
            "user_id": approver_user_id,
            "role_id": current_level_config['role_id']
        })

        has_role = result.scalar()
        if not has_role:
            raise ValueError(f"User does not have required role for approval level {current_level}")

        # Record approval action
        action_insert_query = text("""
            INSERT INTO atlas.approval_actions (
                approval_request_id, approval_level, approver_id, action, action_notes
            ) VALUES (
                :request_id, :approval_level, :approver_id, 'approved', :notes
            )
        """)

        await self.db.execute(action_insert_query, {
            "request_id": approval_request_id,
            "approval_level": current_level,
            "approver_id": approver_user_id,
            "notes": notes
        })

        # Advance to next level or complete
        next_level = current_level + 1
        max_level = max(l['level'] for l in levels)

        if next_level > max_level:
            # All levels approved - mark as complete
            update_query = text("""
                UPDATE atlas.approval_requests
                SET overall_status = 'approved', completed_at = NOW()
                WHERE id = :request_id
            """)

            overall_status = 'approved'
            logger.info(f"Approval request {approval_request_id} fully approved")
        else:
            # Advance to next level
            update_query = text("""
                UPDATE atlas.approval_requests
                SET current_approval_level = :next_level
                WHERE id = :request_id
            """)

            overall_status = 'pending'
            logger.info(f"Approval request {approval_request_id} advanced to level {next_level}")

        await self.db.execute(update_query, {
            "request_id": approval_request_id,
            "next_level": next_level
        })

        await self.db.commit()

        return {
            "approval_request_id": str(approval_request_id),
            "current_level": next_level if next_level <= max_level else max_level,
            "overall_status": overall_status,
            "approved_by": str(approver_user_id),
            "approved_at": datetime.utcnow().isoformat()
        }

    async def reject(
        self,
        approval_request_id: UUID,
        rejector_user_id: UUID,
        rejection_reason: str
    ) -> Dict[str, Any]:
        """
        Reject request

        Args:
            approval_request_id: Approval request ID
            rejector_user_id: User rejecting
            rejection_reason: Reason for rejection

        Returns:
            Updated approval status
        """
        logger.info(f"Rejecting approval request {approval_request_id}")

        # Get current level
        request_query = text("""
            SELECT current_approval_level
            FROM atlas.approval_requests
            WHERE id = :request_id
        """)

        result = await self.db.execute(request_query, {"request_id": approval_request_id})
        current_level = result.scalar()

        # Record rejection action
        action_insert_query = text("""
            INSERT INTO atlas.approval_actions (
                approval_request_id, approval_level, approver_id, action, action_notes
            ) VALUES (
                :request_id, :approval_level, :approver_id, 'rejected', :notes
            )
        """)

        await self.db.execute(action_insert_query, {
            "request_id": approval_request_id,
            "approval_level": current_level,
            "approver_id": rejector_user_id,
            "notes": rejection_reason
        })

        # Update request status
        update_query = text("""
            UPDATE atlas.approval_requests
            SET overall_status = 'rejected', completed_at = NOW()
            WHERE id = :request_id
        """)

        await self.db.execute(update_query, {"request_id": approval_request_id})
        await self.db.commit()

        logger.info(f"Approval request {approval_request_id} rejected: {rejection_reason}")

        return {
            "approval_request_id": str(approval_request_id),
            "overall_status": "rejected",
            "rejected_by": str(rejector_user_id),
            "rejection_reason": rejection_reason
        }

    async def delegate(
        self,
        approval_request_id: UUID,
        delegator_user_id: UUID,
        delegatee_user_id: UUID,
        delegation_notes: Optional[str] = None
    ):
        """
        Delegate approval to another user

        Args:
            approval_request_id: Approval request ID
            delegator_user_id: User delegating
            delegatee_user_id: User receiving delegation
            delegation_notes: Optional notes
        """
        logger.info(f"Delegating approval request {approval_request_id} to user {delegatee_user_id}")

        # Get current level
        request_query = text("""
            SELECT current_approval_level
            FROM atlas.approval_requests
            WHERE id = :request_id
        """)

        result = await self.db.execute(request_query, {"request_id": approval_request_id})
        current_level = result.scalar()

        # Record delegation action
        action_insert_query = text("""
            INSERT INTO atlas.approval_actions (
                approval_request_id, approval_level, approver_id,
                action, action_notes, delegated_to
            ) VALUES (
                :request_id, :approval_level, :approver_id,
                'delegated', :notes, :delegated_to
            )
        """)

        await self.db.execute(action_insert_query, {
            "request_id": approval_request_id,
            "approval_level": current_level,
            "approver_id": delegator_user_id,
            "notes": delegation_notes,
            "delegated_to": delegatee_user_id
        })

        await self.db.commit()

        logger.info(f"Delegated approval request {approval_request_id} from {delegator_user_id} to {delegatee_user_id}")

    async def get_pending_approvals(
        self,
        user_id: UUID,
        resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get pending approvals for user

        Args:
            user_id: User ID
            resource_type: Optional filter by resource type

        Returns:
            List of pending approvals
        """
        query = text("""
            SELECT
                ar.id,
                ar.resource_type,
                ar.resource_id,
                ar.current_approval_level,
                ar.requested_by,
                ar.requested_at,
                ar.request_description,
                u.email as requester_email,
                u.first_name || ' ' || u.last_name as requester_name
            FROM atlas.approval_requests ar
            JOIN atlas.approval_chains ac ON ac.id = ar.approval_chain_id
            JOIN atlas.users u ON u.id = ar.requested_by
            WHERE ar.overall_status = 'pending'
            AND EXISTS (
                SELECT 1 FROM atlas.user_roles ur
                WHERE ur.user_id = :user_id
                AND ur.role_id IN (
                    SELECT (level_config->>'role_id')::uuid
                    FROM jsonb_array_elements(ac.approval_levels) as level_config
                    WHERE (level_config->>'level')::int = ar.current_approval_level
                )
            )
            AND (:resource_type IS NULL OR ar.resource_type = :resource_type)
            ORDER BY ar.requested_at
        """)

        result = await self.db.execute(query, {
            "user_id": user_id,
            "resource_type": resource_type
        })

        approvals = []
        for row in result.fetchall():
            approvals.append({
                "approval_request_id": str(row[0]),
                "resource_type": row[1],
                "resource_id": str(row[2]),
                "approval_level": row[3],
                "requested_by": str(row[4]),
                "requested_at": row[5].isoformat() if row[5] else None,
                "description": row[6],
                "requester_email": row[7],
                "requester_name": row[8]
            })

        return approvals

    async def get_approval_history(
        self,
        resource_type: str,
        resource_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Get approval history for resource

        Args:
            resource_type: Resource type
            resource_id: Resource ID

        Returns:
            Approval history
        """
        query = text("""
            SELECT
                aa.approval_level,
                aa.approver_id,
                u.email as approver_email,
                u.first_name || ' ' || u.last_name as approver_name,
                aa.action,
                aa.action_notes,
                aa.action_at,
                aa.delegated_to,
                u2.email as delegatee_email
            FROM atlas.approval_requests ar
            JOIN atlas.approval_actions aa ON aa.approval_request_id = ar.id
            JOIN atlas.users u ON u.id = aa.approver_id
            LEFT JOIN atlas.users u2 ON u2.id = aa.delegated_to
            WHERE ar.resource_type = :resource_type
            AND ar.resource_id = :resource_id
            ORDER BY aa.action_at
        """)

        result = await self.db.execute(query, {
            "resource_type": resource_type,
            "resource_id": resource_id
        })

        history = []
        for row in result.fetchall():
            entry = {
                "approval_level": row[0],
                "approver_id": str(row[1]),
                "approver_email": row[2],
                "approver_name": row[3],
                "action": row[4],
                "notes": row[5],
                "action_at": row[6].isoformat() if row[6] else None
            }

            if row[7]:  # Delegated
                entry["delegated_to"] = str(row[7])
                entry["delegatee_email"] = row[8]

            history.append(entry)

        return history

    async def get_default_approval_chain(
        self,
        firm_id: UUID,
        resource_type: str
    ) -> Optional[UUID]:
        """
        Get default approval chain for resource type

        Args:
            firm_id: Firm ID
            resource_type: Resource type

        Returns:
            Approval chain ID or None
        """
        query = text("""
            SELECT id
            FROM atlas.approval_chains
            WHERE cpa_firm_id = :firm_id
            AND resource_type = :resource_type
            AND is_active = TRUE
            ORDER BY created_at
            LIMIT 1
        """)

        result = await self.db.execute(query, {
            "firm_id": firm_id,
            "resource_type": resource_type
        })

        return result.scalar_one_or_none()
