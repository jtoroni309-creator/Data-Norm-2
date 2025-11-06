"""
Permission Service - Multi-Tenant RBAC Implementation

Implements role-based access control with tenant isolation.
Provides secure permission checking and audit logging.

Key Features:
- Tenant isolation (row-level security)
- Role-based permissions (RBAC)
- Permission inheritance (hierarchical)
- Audit logging (all actions tracked)
- Secure by default (deny unless explicitly allowed)
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .permissions_models import (
    ROLE_PERMISSIONS,
    AuditAction,
    AuditLog,
    ClientAccess,
    InvitationStatus,
    PermissionScope,
    Tenant,
    TenantStatus,
    User,
    UserInvitation,
    UserPermission,
    UserRole,
)


class PermissionService:
    """
    Service for managing multi-tenant permissions and access control.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========================================================================
    # TENANT MANAGEMENT (Platform Admin Only)
    # ========================================================================

    async def create_tenant(
        self,
        firm_name: str,
        firm_ein: str,
        primary_contact_email: str,
        created_by_user_id: UUID,
        subscription_tier: str = "Trial",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a new CPA firm tenant (Platform Admin only).

        Args:
            firm_name: Name of the CPA firm
            firm_ein: Employer Identification Number
            primary_contact_email: Primary contact email
            created_by_user_id: Platform admin creating the tenant
            subscription_tier: Subscription tier (Trial, Basic, Professional, Enterprise)
            **kwargs: Additional tenant fields

        Returns:
            Tenant details
        """
        # Verify platform admin permission
        await self._require_permission(
            user_id=created_by_user_id,
            scope=PermissionScope.PLATFORM_TENANTS,
        )

        # Create tenant
        tenant = Tenant(
            firm_name=firm_name,
            firm_ein=firm_ein,
            primary_contact_email=primary_contact_email,
            created_by=created_by_user_id,
            subscription_tier=subscription_tier,
            status=TenantStatus.TRIAL,
            trial_ends_at=datetime.utcnow() + timedelta(days=30),
            **kwargs,
        )

        self.session.add(tenant)
        await self.session.flush()

        # Log action
        await self._log_audit(
            user_id=created_by_user_id,
            tenant_id=tenant.id,
            action=AuditAction.TENANT_CREATED,
            resource_type="tenant",
            resource_id=tenant.id,
            description=f"Created tenant: {firm_name}",
        )

        await self.session.commit()

        return {
            "id": str(tenant.id),
            "firm_name": tenant.firm_name,
            "firm_ein": tenant.firm_ein,
            "status": tenant.status.value,
            "subscription_tier": tenant.subscription_tier,
            "trial_ends_at": tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None,
            "created_at": tenant.created_at.isoformat(),
        }

    async def list_tenants(
        self,
        user_id: UUID,
        status: Optional[TenantStatus] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all tenants (Platform Admin only).

        Args:
            user_id: Platform admin user ID
            status: Optional status filter

        Returns:
            List of tenants
        """
        # Verify platform admin permission
        await self._require_permission(
            user_id=user_id,
            scope=PermissionScope.PLATFORM_TENANTS,
        )

        # Build query
        query = select(Tenant).where(Tenant.deleted_at.is_(None))

        if status:
            query = query.where(Tenant.status == status)

        result = await self.session.execute(query.order_by(Tenant.created_at.desc()))
        tenants = result.scalars().all()

        return [
            {
                "id": str(tenant.id),
                "firm_name": tenant.firm_name,
                "status": tenant.status.value,
                "subscription_tier": tenant.subscription_tier,
                "created_at": tenant.created_at.isoformat(),
            }
            for tenant in tenants
        ]

    async def update_tenant_status(
        self,
        user_id: UUID,
        tenant_id: UUID,
        status: TenantStatus,
    ) -> Dict[str, Any]:
        """
        Update tenant status (Platform Admin only).

        Args:
            user_id: Platform admin user ID
            tenant_id: Tenant to update
            status: New status

        Returns:
            Updated tenant details
        """
        # Verify platform admin permission
        await self._require_permission(
            user_id=user_id,
            scope=PermissionScope.PLATFORM_TENANTS,
        )

        # Get tenant
        tenant = await self._get_tenant(tenant_id)
        old_status = tenant.status

        # Update status
        tenant.status = status
        await self.session.flush()

        # Log action
        await self._log_audit(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditAction.TENANT_UPDATED,
            resource_type="tenant",
            resource_id=tenant_id,
            changes={"status": {"old": old_status.value, "new": status.value}},
            description=f"Updated tenant status: {old_status.value} → {status.value}",
        )

        await self.session.commit()

        return {
            "id": str(tenant.id),
            "firm_name": tenant.firm_name,
            "status": tenant.status.value,
        }

    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================

    async def create_user(
        self,
        email: str,
        role: UserRole,
        tenant_id: Optional[UUID],
        created_by_user_id: UUID,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a new user (Firm Admin or Platform Admin).

        Args:
            email: User email
            role: User role
            tenant_id: Tenant ID (required for non-platform admins)
            created_by_user_id: User creating this user
            first_name: First name
            last_name: Last name
            **kwargs: Additional user fields

        Returns:
            User details
        """
        # Verify permission to create users
        if role == UserRole.PLATFORM_ADMIN:
            # Only platform admins can create platform admins
            await self._require_permission(
                user_id=created_by_user_id,
                scope=PermissionScope.PLATFORM_ALL,
            )
        else:
            # Firm admins can create firm users
            await self._require_permission(
                user_id=created_by_user_id,
                scope=PermissionScope.FIRM_USERS,
                tenant_id=tenant_id,
            )

        # Validate tenant_id for non-platform admins
        if role != UserRole.PLATFORM_ADMIN and not tenant_id:
            raise ValueError("tenant_id required for non-platform admin users")

        # Create user
        user = User(
            email=email,
            role=role,
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            created_by=created_by_user_id,
            **kwargs,
        )

        self.session.add(user)
        await self.session.flush()

        # Log action
        await self._log_audit(
            user_id=created_by_user_id,
            tenant_id=tenant_id,
            action=AuditAction.USER_CREATED,
            resource_type="user",
            resource_id=user.id,
            description=f"Created user: {email} with role {role.value}",
        )

        await self.session.commit()

        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            "created_at": user.created_at.isoformat(),
        }

    async def update_user_role(
        self,
        user_id: UUID,
        target_user_id: UUID,
        new_role: UserRole,
    ) -> Dict[str, Any]:
        """
        Update user role (Firm Admin or Platform Admin only).

        Args:
            user_id: User making the change
            target_user_id: User to update
            new_role: New role

        Returns:
            Updated user details
        """
        # Get target user
        target_user = await self._get_user(target_user_id)
        old_role = target_user.role

        # Verify permission
        await self._require_permission(
            user_id=user_id,
            scope=PermissionScope.FIRM_USERS,
            tenant_id=target_user.tenant_id,
        )

        # Update role
        target_user.role = new_role
        await self.session.flush()

        # Log action
        await self._log_audit(
            user_id=user_id,
            tenant_id=target_user.tenant_id,
            action=AuditAction.ROLE_CHANGED,
            resource_type="user",
            resource_id=target_user_id,
            changes={"role": {"old": old_role.value, "new": new_role.value}},
            description=f"Changed role: {old_role.value} → {new_role.value}",
        )

        await self.session.commit()

        return {
            "id": str(target_user.id),
            "email": target_user.email,
            "role": target_user.role.value,
        }

    async def list_users(
        self,
        user_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> List[Dict[str, Any]]:
        """
        List users in a tenant.

        Args:
            user_id: User requesting the list
            tenant_id: Tenant to list users for (required for non-platform admins)

        Returns:
            List of users
        """
        # Get requesting user
        requesting_user = await self._get_user(user_id)

        # Determine which tenant to query
        if requesting_user.role == UserRole.PLATFORM_ADMIN:
            # Platform admin can list all users or specific tenant
            query_tenant_id = tenant_id
        else:
            # Others can only list their own tenant
            query_tenant_id = requesting_user.tenant_id

        # Build query
        query = select(User).where(
            and_(
                User.deleted_at.is_(None),
                User.is_active == True,
            )
        )

        if query_tenant_id:
            query = query.where(User.tenant_id == query_tenant_id)

        result = await self.session.execute(query.order_by(User.created_at.desc()))
        users = result.scalars().all()

        return [
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ]

    # ========================================================================
    # INVITATION SYSTEM
    # ========================================================================

    async def invite_user(
        self,
        inviting_user_id: UUID,
        email: str,
        role: UserRole,
        tenant_id: UUID,
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Invite a new user to the platform.

        Creates a secure invitation link that expires in 7 days.

        Args:
            inviting_user_id: User sending the invitation
            email: Email to invite
            role: Role for the new user
            tenant_id: Tenant to invite to
            message: Optional message to include

        Returns:
            Invitation details
        """
        # Verify permission to invite users
        await self._require_permission(
            user_id=inviting_user_id,
            scope=PermissionScope.FIRM_USERS,
            tenant_id=tenant_id,
        )

        # Check if user already exists
        existing_user = await self._get_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Generate secure token
        invitation_token = secrets.token_urlsafe(32)

        # Create invitation
        invitation = UserInvitation(
            email=email,
            role=role,
            tenant_id=tenant_id,
            invitation_token=invitation_token,
            invited_by=inviting_user_id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            message=message,
        )

        self.session.add(invitation)
        await self.session.flush()

        # Log action
        await self._log_audit(
            user_id=inviting_user_id,
            tenant_id=tenant_id,
            action=AuditAction.USER_INVITED,
            resource_type="invitation",
            resource_id=invitation.id,
            description=f"Invited {email} as {role.value}",
        )

        await self.session.commit()

        return {
            "id": str(invitation.id),
            "email": invitation.email,
            "role": invitation.role.value,
            "invitation_token": invitation.invitation_token,
            "expires_at": invitation.expires_at.isoformat(),
            "invitation_url": f"https://your-platform.com/accept-invitation?token={invitation_token}",
        }

    async def accept_invitation(
        self,
        invitation_token: str,
        first_name: str,
        last_name: str,
        password: str,
    ) -> Dict[str, Any]:
        """
        Accept a user invitation and create account.

        Args:
            invitation_token: Invitation token from email
            first_name: User's first name
            last_name: User's last name
            password: User's password

        Returns:
            Created user details
        """
        # Find invitation
        query = select(UserInvitation).where(
            and_(
                UserInvitation.invitation_token == invitation_token,
                UserInvitation.status == InvitationStatus.PENDING,
            )
        )
        result = await self.session.execute(query)
        invitation = result.scalar_one_or_none()

        if not invitation:
            raise ValueError("Invalid invitation token")

        # Check expiry
        if invitation.expires_at < datetime.utcnow():
            invitation.status = InvitationStatus.EXPIRED
            await self.session.commit()
            raise ValueError("Invitation has expired")

        # Create user (password should be hashed in real implementation)
        user = User(
            email=invitation.email,
            first_name=first_name,
            last_name=last_name,
            role=invitation.role,
            tenant_id=invitation.tenant_id,
            password_hash=password,  # TODO: Hash password with bcrypt
            email_verified=True,
            email_verified_at=datetime.utcnow(),
        )

        self.session.add(user)
        await self.session.flush()

        # Update invitation
        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = datetime.utcnow()
        invitation.user_id = user.id

        # Log action
        await self._log_audit(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action=AuditAction.USER_CREATED,
            resource_type="user",
            resource_id=user.id,
            description=f"User accepted invitation: {user.email}",
        )

        await self.session.commit()

        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "tenant_id": str(user.tenant_id),
        }

    # ========================================================================
    # CLIENT ACCESS MANAGEMENT
    # ========================================================================

    async def grant_client_access(
        self,
        granting_user_id: UUID,
        client_email: str,
        tenant_id: UUID,
        engagement_ids: Optional[List[UUID]] = None,
        can_view_financials: bool = True,
        can_upload_documents: bool = True,
        can_manage_integrations: bool = True,
        access_expires_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Grant a client access to the client portal.

        Args:
            granting_user_id: Firm user granting access
            client_email: Client's email
            tenant_id: Firm's tenant ID
            engagement_ids: Specific engagements to grant access to (None = all)
            can_view_financials: Can view financial data
            can_upload_documents: Can upload documents
            can_manage_integrations: Can manage integrations
            access_expires_at: Optional expiry date

        Returns:
            Client access details and invitation
        """
        # Verify permission to grant client access
        await self._require_permission(
            user_id=granting_user_id,
            scope=PermissionScope.FIRM_CLIENTS,
            tenant_id=tenant_id,
        )

        # Check if client user exists
        client_user = await self._get_user_by_email(client_email)

        if not client_user:
            # Create invitation for new client
            invitation = await self.invite_user(
                inviting_user_id=granting_user_id,
                email=client_email,
                role=UserRole.CLIENT,
                tenant_id=tenant_id,
                message="You've been invited to access your audit documents and data.",
            )
            client_user_id = None
            needs_registration = True
        else:
            client_user_id = client_user.id
            needs_registration = False

        # Create client access record
        client_access = ClientAccess(
            user_id=client_user_id if client_user_id else uuid4(),  # Temporary ID if pending
            tenant_id=tenant_id,
            granted_by=granting_user_id,
            engagement_ids={"engagement_ids": [str(eid) for eid in engagement_ids]} if engagement_ids else None,
            can_view_financials=can_view_financials,
            can_upload_documents=can_upload_documents,
            can_manage_integrations=can_manage_integrations,
            access_expires_at=access_expires_at,
        )

        self.session.add(client_access)
        await self.session.flush()

        # Log action
        await self._log_audit(
            user_id=granting_user_id,
            tenant_id=tenant_id,
            action=AuditAction.CLIENT_ACCESS_GRANTED,
            resource_type="client_access",
            resource_id=client_access.id,
            description=f"Granted client access to {client_email}",
        )

        await self.session.commit()

        result = {
            "id": str(client_access.id),
            "client_email": client_email,
            "access_granted_at": client_access.access_granted_at.isoformat(),
            "can_view_financials": can_view_financials,
            "can_upload_documents": can_upload_documents,
            "can_manage_integrations": can_manage_integrations,
            "needs_registration": needs_registration,
        }

        if needs_registration:
            result["invitation"] = invitation

        return result

    async def revoke_client_access(
        self,
        revoking_user_id: UUID,
        client_access_id: UUID,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Revoke a client's access to the portal.

        Args:
            revoking_user_id: User revoking access
            client_access_id: Client access to revoke
            reason: Reason for revocation

        Returns:
            Revocation confirmation
        """
        # Get client access
        query = select(ClientAccess).where(ClientAccess.id == client_access_id)
        result = await self.session.execute(query)
        client_access = result.scalar_one_or_none()

        if not client_access:
            raise ValueError("Client access not found")

        # Verify permission
        await self._require_permission(
            user_id=revoking_user_id,
            scope=PermissionScope.FIRM_CLIENTS,
            tenant_id=client_access.tenant_id,
        )

        # Revoke access
        client_access.revoked_at = datetime.utcnow()
        client_access.revoked_by = revoking_user_id
        client_access.revocation_reason = reason

        # Log action
        await self._log_audit(
            user_id=revoking_user_id,
            tenant_id=client_access.tenant_id,
            action=AuditAction.CLIENT_ACCESS_REVOKED,
            resource_type="client_access",
            resource_id=client_access_id,
            description=f"Revoked client access: {reason}",
        )

        await self.session.commit()

        return {
            "id": str(client_access.id),
            "revoked_at": client_access.revoked_at.isoformat(),
            "reason": reason,
        }

    # ========================================================================
    # PERMISSION CHECKING
    # ========================================================================

    async def check_permission(
        self,
        user_id: UUID,
        scope: PermissionScope,
        tenant_id: Optional[UUID] = None,
        resource_id: Optional[UUID] = None,
    ) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            user_id: User to check
            scope: Permission scope to check
            tenant_id: Optional tenant context
            resource_id: Optional resource ID

        Returns:
            True if user has permission, False otherwise
        """
        # Get user
        user = await self._get_user(user_id)

        # Check if user is active
        if not user.is_active or user.deleted_at:
            return False

        # Tenant isolation check (except for platform admins)
        if user.role != UserRole.PLATFORM_ADMIN and tenant_id:
            if user.tenant_id != tenant_id:
                return False

        # Check role-based permissions
        role_permissions = ROLE_PERMISSIONS.get(user.role, [])
        if scope in role_permissions:
            return True

        # Check user-specific permissions
        query = select(UserPermission).where(
            and_(
                UserPermission.user_id == user_id,
                UserPermission.scope == scope,
                UserPermission.granted == True,
            )
        )

        if resource_id:
            query = query.where(UserPermission.resource_id == resource_id)

        result = await self.session.execute(query)
        user_permission = result.scalar_one_or_none()

        if user_permission:
            # Check expiry
            if user_permission.expires_at and user_permission.expires_at < datetime.utcnow():
                return False
            return True

        return False

    async def _require_permission(
        self,
        user_id: UUID,
        scope: PermissionScope,
        tenant_id: Optional[UUID] = None,
    ) -> None:
        """
        Require a permission or raise an exception.

        Args:
            user_id: User to check
            scope: Required permission scope
            tenant_id: Optional tenant context

        Raises:
            PermissionError: If user does not have permission
        """
        has_permission = await self.check_permission(
            user_id=user_id,
            scope=scope,
            tenant_id=tenant_id,
        )

        if not has_permission:
            raise PermissionError(f"User does not have permission: {scope.value}")

    # ========================================================================
    # AUDIT LOGGING
    # ========================================================================

    async def _log_audit(
        self,
        user_id: UUID,
        action: AuditAction,
        tenant_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        changes: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
    ) -> None:
        """
        Log an audit event.

        Args:
            user_id: User performing the action
            action: Type of action
            tenant_id: Optional tenant context
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            changes: Changes made (before/after)
            description: Human-readable description
            ip_address: IP address of user
            success: Whether action succeeded
        """
        audit_log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            description=description,
            ip_address=ip_address,
            success=success,
        )

        self.session.add(audit_log)
        await self.session.flush()

    async def get_audit_logs(
        self,
        user_id: UUID,
        tenant_id: Optional[UUID] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs (Firm Admin or Platform Admin).

        Args:
            user_id: User requesting logs
            tenant_id: Filter by tenant
            action: Filter by action type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of logs to return

        Returns:
            List of audit logs
        """
        # Verify permission
        user = await self._get_user(user_id)
        if user.role == UserRole.PLATFORM_ADMIN:
            # Platform admin can see all logs
            pass
        elif user.role == UserRole.FIRM_ADMIN:
            # Firm admin can see their tenant's logs
            tenant_id = user.tenant_id
        else:
            raise PermissionError("Only admins can view audit logs")

        # Build query
        query = select(AuditLog)

        if tenant_id:
            query = query.where(AuditLog.tenant_id == tenant_id)

        if action:
            query = query.where(AuditLog.action == action)

        if start_date:
            query = query.where(AuditLog.timestamp >= start_date)

        if end_date:
            query = query.where(AuditLog.timestamp <= end_date)

        query = query.order_by(AuditLog.timestamp.desc()).limit(limit)

        result = await self.session.execute(query)
        logs = result.scalars().all()

        return [
            {
                "id": str(log.id),
                "action": log.action.value,
                "timestamp": log.timestamp.isoformat(),
                "user_id": str(log.user_id) if log.user_id else None,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id) if log.resource_id else None,
                "description": log.description,
                "success": log.success,
            }
            for log in logs
        ]

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    async def _get_user(self, user_id: UUID) -> User:
        """Get user by ID or raise exception."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User not found: {user_id}")
        return user

    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def _get_tenant(self, tenant_id: UUID) -> Tenant:
        """Get tenant by ID or raise exception."""
        result = await self.session.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")
        return tenant
