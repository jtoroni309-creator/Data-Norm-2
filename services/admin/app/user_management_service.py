"""
User Management and Permissions Service
Manages users, roles, and permissions with RBAC
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Set
from uuid import UUID
import hashlib
import secrets

from sqlalchemy import select, text, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UserManagementService:
    """Service for managing users and permissions"""

    def __init__(self, db: AsyncSession):
        """
        Initialize user management service

        Args:
            db: Database session
        """
        self.db = db

    async def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        cpa_firm_id: Optional[UUID] = None,
        client_id: Optional[UUID] = None,
        role_ids: Optional[List[UUID]] = None,
        send_invitation: bool = True,
        created_by_user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Create new user

        Args:
            email: User email
            first_name: First name
            last_name: Last name
            cpa_firm_id: CPA firm ID (for firm users)
            client_id: Client ID (for client users)
            role_ids: List of role IDs to assign
            send_invitation: Send invitation email
            created_by_user_id: User creating this user

        Returns:
            Created user with temporary password
        """
        logger.info(f"Creating user: {email}")

        # Validate firm/client association
        if not cpa_firm_id and not client_id:
            raise ValueError("User must belong to either a firm or client")

        # Check if email already exists
        existing = await self.db.execute(
            text("SELECT id FROM atlas.users WHERE email = :email"),
            {"email": email}
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"User with email '{email}' already exists")

        # Check firm limits if adding firm user
        if cpa_firm_id and not client_id:
            limits_query = text("""
                SELECT
                    (SELECT COUNT(*) FROM atlas.users WHERE cpa_firm_id = :firm_id AND is_active = TRUE) as current_users,
                    max_users
                FROM atlas.cpa_firms
                WHERE id = :firm_id
            """)
            result = await self.db.execute(limits_query, {"firm_id": cpa_firm_id})
            limits = result.fetchone()
            if limits and limits[0] >= limits[1]:
                raise ValueError("Firm has reached maximum user limit")

        # Generate temporary password
        temp_password = secrets.token_urlsafe(16)
        password_hash = self._hash_password(temp_password)

        # Create user
        user_id = UUID(int=secrets.randbits(128))
        insert_query = text("""
            INSERT INTO atlas.users (
                id, email, first_name, last_name, cpa_firm_id, client_id,
                password_hash, require_password_change, created_by
            ) VALUES (
                :id, :email, :first_name, :last_name, :cpa_firm_id, :client_id,
                :password_hash, TRUE, :created_by
            )
            RETURNING id
        """)

        await self.db.execute(insert_query, {
            "id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "cpa_firm_id": cpa_firm_id,
            "client_id": client_id,
            "password_hash": password_hash,
            "created_by": created_by_user_id
        })

        # Assign roles
        if role_ids:
            for role_id in role_ids:
                await self.assign_role(user_id, role_id, client_id, created_by_user_id)

        await self.db.commit()

        # Audit log
        await self._audit_log(
            user_id=created_by_user_id,
            action="user.create",
            resource_type="user",
            resource_id=user_id,
            description=f"Created user {email}",
            firm_id=cpa_firm_id,
            client_id=client_id
        )

        logger.info(f"Created user {user_id}: {email}")

        return {
            "user_id": str(user_id),
            "email": email,
            "temporary_password": temp_password if not send_invitation else None,
            "require_password_change": True
        }

    async def assign_role(
        self,
        user_id: UUID,
        role_id: UUID,
        client_id: Optional[UUID] = None,
        granted_by: Optional[UUID] = None
    ):
        """
        Assign role to user

        Args:
            user_id: User ID
            role_id: Role ID
            client_id: Optional client scope
            granted_by: User granting role
        """
        # Check if already assigned
        check_query = text("""
            SELECT id FROM atlas.user_roles
            WHERE user_id = :user_id
            AND role_id = :role_id
            AND (client_id = :client_id OR (client_id IS NULL AND :client_id IS NULL))
        """)

        existing = await self.db.execute(check_query, {
            "user_id": user_id,
            "role_id": role_id,
            "client_id": client_id
        })

        if existing.scalar_one_or_none():
            logger.warning(f"Role {role_id} already assigned to user {user_id}")
            return

        # Assign role
        insert_query = text("""
            INSERT INTO atlas.user_roles (user_id, role_id, client_id, granted_by)
            VALUES (:user_id, :role_id, :client_id, :granted_by)
        """)

        await self.db.execute(insert_query, {
            "user_id": user_id,
            "role_id": role_id,
            "client_id": client_id,
            "granted_by": granted_by
        })

        await self.db.commit()

        logger.info(f"Assigned role {role_id} to user {user_id}")

    async def revoke_role(
        self,
        user_id: UUID,
        role_id: UUID,
        client_id: Optional[UUID] = None
    ):
        """
        Revoke role from user

        Args:
            user_id: User ID
            role_id: Role ID
            client_id: Optional client scope
        """
        delete_query = text("""
            DELETE FROM atlas.user_roles
            WHERE user_id = :user_id
            AND role_id = :role_id
            AND (client_id = :client_id OR (client_id IS NULL AND :client_id IS NULL))
        """)

        await self.db.execute(delete_query, {
            "user_id": user_id,
            "role_id": role_id,
            "client_id": client_id
        })

        await self.db.commit()

        logger.info(f"Revoked role {role_id} from user {user_id}")

    async def check_permission(
        self,
        user_id: UUID,
        permission_name: str,
        client_id: Optional[UUID] = None
    ) -> bool:
        """
        Check if user has permission

        Args:
            user_id: User ID
            permission_name: Permission name (e.g., 'engagement.create')
            client_id: Optional client context

        Returns:
            True if user has permission
        """
        query = text("""
            SELECT COUNT(*) > 0 as has_permission
            FROM atlas.user_permissions_view
            WHERE user_id = :user_id
            AND permission_name = :permission_name
            AND (
                :client_id IS NULL
                OR client_id = :client_id
                OR client_id IS NULL  -- Global permissions
            )
        """)

        result = await self.db.execute(query, {
            "user_id": user_id,
            "permission_name": permission_name,
            "client_id": client_id
        })

        row = result.fetchone()
        return bool(row[0]) if row else False

    async def get_user_permissions(
        self,
        user_id: UUID,
        client_id: Optional[UUID] = None
    ) -> List[str]:
        """
        Get all permissions for user

        Args:
            user_id: User ID
            client_id: Optional client context

        Returns:
            List of permission names
        """
        query = text("""
            SELECT DISTINCT permission_name
            FROM atlas.user_permissions_view
            WHERE user_id = :user_id
            AND (
                :client_id IS NULL
                OR client_id = :client_id
                OR client_id IS NULL
            )
            ORDER BY permission_name
        """)

        result = await self.db.execute(query, {
            "user_id": user_id,
            "client_id": client_id
        })

        return [row[0] for row in result.fetchall()]

    async def get_user_roles(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all roles for user

        Args:
            user_id: User ID

        Returns:
            List of roles with details
        """
        query = text("""
            SELECT
                r.id,
                r.role_type,
                r.role_name,
                r.role_description,
                r.approval_level,
                ur.client_id,
                c.client_name
            FROM atlas.user_roles ur
            JOIN atlas.roles r ON r.id = ur.role_id
            LEFT JOIN atlas.clients c ON c.id = ur.client_id
            WHERE ur.user_id = :user_id
            ORDER BY r.approval_level DESC
        """)

        result = await self.db.execute(query, {"user_id": user_id})

        roles = []
        for row in result.fetchall():
            roles.append({
                "role_id": str(row[0]),
                "role_type": row[1],
                "role_name": row[2],
                "role_description": row[3],
                "approval_level": row[4],
                "client_id": str(row[5]) if row[5] else None,
                "client_name": row[6]
            })

        return roles

    async def list_firm_users(
        self,
        firm_id: UUID,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all users in a firm

        Args:
            firm_id: Firm ID
            include_inactive: Include inactive users

        Returns:
            List of users
        """
        query = text("""
            SELECT
                u.id,
                u.email,
                u.first_name,
                u.last_name,
                u.is_active,
                u.last_login_at,
                STRING_AGG(DISTINCT r.role_name, ', ') as roles
            FROM atlas.users u
            LEFT JOIN atlas.user_roles ur ON ur.user_id = u.id
            LEFT JOIN atlas.roles r ON r.id = ur.role_id
            WHERE u.cpa_firm_id = :firm_id
            AND (:include_inactive = TRUE OR u.is_active = TRUE)
            GROUP BY u.id, u.email, u.first_name, u.last_name, u.is_active, u.last_login_at
            ORDER BY u.last_name, u.first_name
        """)

        result = await self.db.execute(query, {
            "firm_id": firm_id,
            "include_inactive": include_inactive
        })

        users = []
        for row in result.fetchall():
            users.append({
                "user_id": str(row[0]),
                "email": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "is_active": row[4],
                "last_login": row[5].isoformat() if row[5] else None,
                "roles": row[6]
            })

        return users

    async def list_client_users(
        self,
        client_id: UUID,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all users for a client

        Args:
            client_id: Client ID
            include_inactive: Include inactive users

        Returns:
            List of users
        """
        query = text("""
            SELECT
                u.id,
                u.email,
                u.first_name,
                u.last_name,
                u.is_active,
                u.last_login_at,
                STRING_AGG(DISTINCT r.role_name, ', ') as roles
            FROM atlas.users u
            LEFT JOIN atlas.user_roles ur ON ur.user_id = u.id
            LEFT JOIN atlas.roles r ON r.id = ur.role_id
            WHERE u.client_id = :client_id
            AND (:include_inactive = TRUE OR u.is_active = TRUE)
            GROUP BY u.id, u.email, u.first_name, u.last_name, u.is_active, u.last_login_at
            ORDER BY u.last_name, u.first_name
        """)

        result = await self.db.execute(query, {
            "client_id": client_id,
            "include_inactive": include_inactive
        })

        users = []
        for row in result.fetchall():
            users.append({
                "user_id": str(row[0]),
                "email": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "is_active": row[4],
                "last_login": row[5].isoformat() if row[5] else None,
                "roles": row[6]
            })

        return users

    async def deactivate_user(
        self,
        user_id: UUID,
        deactivated_by: Optional[UUID] = None
    ):
        """
        Deactivate user

        Args:
            user_id: User ID
            deactivated_by: User performing deactivation
        """
        update_query = text("""
            UPDATE atlas.users
            SET is_active = FALSE, updated_at = NOW()
            WHERE id = :user_id
        """)

        await self.db.execute(update_query, {"user_id": user_id})
        await self.db.commit()

        await self._audit_log(
            user_id=deactivated_by,
            action="user.deactivate",
            resource_type="user",
            resource_id=user_id,
            description=f"Deactivated user {user_id}"
        )

        logger.info(f"Deactivated user {user_id}")

    async def reactivate_user(
        self,
        user_id: UUID,
        reactivated_by: Optional[UUID] = None
    ):
        """
        Reactivate user

        Args:
            user_id: User ID
            reactivated_by: User performing reactivation
        """
        update_query = text("""
            UPDATE atlas.users
            SET is_active = TRUE, updated_at = NOW()
            WHERE id = :user_id
        """)

        await self.db.execute(update_query, {"user_id": user_id})
        await self.db.commit()

        await self._audit_log(
            user_id=reactivated_by,
            action="user.reactivate",
            resource_type="user",
            resource_id=user_id,
            description=f"Reactivated user {user_id}"
        )

        logger.info(f"Reactivated user {user_id}")

    async def update_user(
        self,
        user_id: UUID,
        updates: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ):
        """
        Update user details

        Args:
            user_id: User ID
            updates: Fields to update
            updated_by: User making update
        """
        # Build dynamic update query
        set_clauses = []
        params = {"user_id": user_id}

        for field, value in updates.items():
            if field in ['first_name', 'last_name', 'phone', 'email']:
                set_clauses.append(f"{field} = :{field}")
                params[field] = value

        if not set_clauses:
            return

        set_clauses.append("updated_at = NOW()")

        update_query = text(f"""
            UPDATE atlas.users
            SET {', '.join(set_clauses)}
            WHERE id = :user_id
        """)

        await self.db.execute(update_query, params)
        await self.db.commit()

        await self._audit_log(
            user_id=updated_by,
            action="user.update",
            resource_type="user",
            resource_id=user_id,
            description=f"Updated user {user_id}",
            changes=updates
        )

        logger.info(f"Updated user {user_id}")

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (simplified for demo)"""
        return hashlib.sha256(password.encode()).hexdigest()

    async def _audit_log(
        self,
        action: str,
        resource_type: str,
        resource_id: UUID,
        user_id: Optional[UUID] = None,
        description: Optional[str] = None,
        changes: Optional[Dict] = None,
        firm_id: Optional[UUID] = None,
        client_id: Optional[UUID] = None
    ):
        """Create audit log entry"""
        query = text("""
            INSERT INTO atlas.audit_log (
                user_id, cpa_firm_id, client_id, action, resource_type,
                resource_id, description, changes
            ) VALUES (
                :user_id, :firm_id, :client_id, :action, :resource_type,
                :resource_id, :description, :changes
            )
        """)

        await self.db.execute(query, {
            "user_id": user_id,
            "firm_id": firm_id,
            "client_id": client_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "description": description,
            "changes": changes
        })
        await self.db.commit()

    async def get_available_roles(
        self,
        is_firm_role: Optional[bool] = None,
        is_client_role: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available roles

        Args:
            is_firm_role: Filter for firm roles
            is_client_role: Filter for client roles

        Returns:
            List of roles
        """
        conditions = ["is_active = TRUE"]
        params = {}

        if is_firm_role is not None:
            conditions.append("is_firm_role = :is_firm_role")
            params["is_firm_role"] = is_firm_role

        if is_client_role is not None:
            conditions.append("is_client_role = :is_client_role")
            params["is_client_role"] = is_client_role

        query = text(f"""
            SELECT
                id,
                role_type,
                role_name,
                role_description,
                approval_level,
                is_firm_role,
                is_client_role
            FROM atlas.roles
            WHERE {' AND '.join(conditions)}
            ORDER BY approval_level DESC, role_name
        """)

        result = await self.db.execute(query, params)

        roles = []
        for row in result.fetchall():
            roles.append({
                "role_id": str(row[0]),
                "role_type": row[1],
                "role_name": row[2],
                "role_description": row[3],
                "approval_level": row[4],
                "is_firm_role": row[5],
                "is_client_role": row[6]
            })

        return roles
