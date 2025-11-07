"""
Firm Management Service
Manages CPA firms, subscription, and firm-level settings
"""
import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from enum import Enum as PyEnum

from sqlalchemy import select, update, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, Date, DateTime, Boolean, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID, INET

from .database import Base

logger = logging.getLogger(__name__)


class FirmSubscriptionTier(str, PyEnum):
    """Subscription tiers"""
    TRIAL = "trial"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class FirmStatus(str, PyEnum):
    """Firm status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL_EXPIRED = "trial_expired"
    CANCELED = "canceled"


class CPAFirm(Base):
    """CPA Firm model"""
    __tablename__ = "cpa_firms"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    firm_name = Column(String(255), nullable=False, unique=True)
    legal_name = Column(String(255))
    ein = Column(String(20))

    primary_contact_name = Column(String(255))
    primary_contact_email = Column(String(255), nullable=False)
    primary_contact_phone = Column(String(50))

    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(100), default='USA')

    subscription_tier = Column(SQLEnum(FirmSubscriptionTier), default=FirmSubscriptionTier.TRIAL)
    subscription_status = Column(SQLEnum(FirmStatus), default=FirmStatus.ACTIVE)
    trial_start_date = Column(Date)
    trial_end_date = Column(Date)
    subscription_start_date = Column(Date)
    max_clients = Column(Integer, default=10)
    max_users = Column(Integer, default=5)

    logo_url = Column(Text)
    primary_color = Column(String(7))
    secondary_color = Column(String(7))

    default_engagement_partner = Column(String(255))
    require_two_factor_auth = Column(Boolean, default=False)
    session_timeout_minutes = Column(Integer, default=30)
    password_expiry_days = Column(Integer, default=90)

    enable_edgar_scraper = Column(Boolean, default=True)
    enable_ai_assistant = Column(Boolean, default=True)
    enable_analytics = Column(Boolean, default=True)
    enable_client_portal = Column(Boolean, default=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    created_by = Column(PGUUID(as_uuid=True))


class FirmManagementService:
    """Service for managing CPA firms"""

    # Subscription tier limits
    TIER_LIMITS = {
        FirmSubscriptionTier.TRIAL: {"max_clients": 2, "max_users": 3, "duration_days": 30},
        FirmSubscriptionTier.STARTER: {"max_clients": 10, "max_users": 5, "price_monthly": 99},
        FirmSubscriptionTier.PROFESSIONAL: {"max_clients": 50, "max_users": 25, "price_monthly": 299},
        FirmSubscriptionTier.ENTERPRISE: {"max_clients": 999999, "max_users": 999999, "price_monthly": 999}
    }

    def __init__(self, db: AsyncSession):
        """
        Initialize firm management service

        Args:
            db: Database session
        """
        self.db = db

    async def create_firm(
        self,
        firm_name: str,
        primary_contact_email: str,
        primary_contact_name: Optional[str] = None,
        legal_name: Optional[str] = None,
        start_trial: bool = True,
        created_by_user_id: Optional[UUID] = None
    ) -> CPAFirm:
        """
        Create new CPA firm

        Args:
            firm_name: Firm name
            primary_contact_email: Primary contact email
            primary_contact_name: Primary contact name
            legal_name: Legal entity name
            start_trial: Start 30-day trial
            created_by_user_id: User creating firm

        Returns:
            Created CPAFirm
        """
        logger.info(f"Creating CPA firm: {firm_name}")

        # Check if firm name already exists
        existing = await self.db.execute(
            select(CPAFirm).where(CPAFirm.firm_name == firm_name)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Firm '{firm_name}' already exists")

        # Create firm
        firm = CPAFirm(
            firm_name=firm_name,
            legal_name=legal_name or firm_name,
            primary_contact_email=primary_contact_email,
            primary_contact_name=primary_contact_name,
            created_by=created_by_user_id
        )

        if start_trial:
            firm.subscription_tier = FirmSubscriptionTier.TRIAL
            firm.subscription_status = FirmStatus.ACTIVE
            firm.trial_start_date = date.today()
            firm.trial_end_date = date.today() + timedelta(days=30)
            firm.max_clients = self.TIER_LIMITS[FirmSubscriptionTier.TRIAL]["max_clients"]
            firm.max_users = self.TIER_LIMITS[FirmSubscriptionTier.TRIAL]["max_users"]

        self.db.add(firm)
        await self.db.commit()
        await self.db.refresh(firm)

        await self._audit_log(
            user_id=created_by_user_id,
            action="firm.create",
            resource_type="firm",
            resource_id=firm.id,
            description=f"Created firm '{firm_name}'"
        )

        logger.info(f"Created firm {firm.id}: {firm_name}")
        return firm

    async def update_firm(
        self,
        firm_id: UUID,
        updates: Dict[str, Any],
        updated_by_user_id: Optional[UUID] = None
    ) -> CPAFirm:
        """
        Update firm details

        Args:
            firm_id: Firm ID
            updates: Dictionary of fields to update
            updated_by_user_id: User making update

        Returns:
            Updated firm
        """
        firm = await self.db.get(CPAFirm, firm_id)
        if not firm:
            raise ValueError(f"Firm {firm_id} not found")

        # Track changes for audit log
        changes = {}
        for field, new_value in updates.items():
            old_value = getattr(firm, field, None)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}
                setattr(firm, field, new_value)

        firm.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(firm)

        if changes:
            await self._audit_log(
                user_id=updated_by_user_id,
                action="firm.update",
                resource_type="firm",
                resource_id=firm.id,
                description=f"Updated firm '{firm.firm_name}'",
                changes=changes
            )

        logger.info(f"Updated firm {firm_id}: {len(changes)} changes")
        return firm

    async def upgrade_subscription(
        self,
        firm_id: UUID,
        new_tier: FirmSubscriptionTier,
        user_id: Optional[UUID] = None
    ) -> CPAFirm:
        """
        Upgrade firm subscription tier

        Args:
            firm_id: Firm ID
            new_tier: New subscription tier
            user_id: User performing upgrade

        Returns:
            Updated firm
        """
        firm = await self.db.get(CPAFirm, firm_id)
        if not firm:
            raise ValueError(f"Firm {firm_id} not found")

        if new_tier == FirmSubscriptionTier.TRIAL:
            raise ValueError("Cannot downgrade to trial")

        old_tier = firm.subscription_tier
        firm.subscription_tier = new_tier
        firm.subscription_status = FirmStatus.ACTIVE
        firm.subscription_start_date = date.today()
        firm.max_clients = self.TIER_LIMITS[new_tier]["max_clients"]
        firm.max_users = self.TIER_LIMITS[new_tier]["max_users"]

        # Clear trial dates if upgrading from trial
        if old_tier == FirmSubscriptionTier.TRIAL:
            firm.trial_end_date = None

        await self.db.commit()
        await self.db.refresh(firm)

        await self._audit_log(
            user_id=user_id,
            action="firm.upgrade_subscription",
            resource_type="firm",
            resource_id=firm.id,
            description=f"Upgraded subscription from {old_tier.value} to {new_tier.value}",
            changes={"tier": {"old": old_tier.value, "new": new_tier.value}}
        )

        logger.info(f"Upgraded firm {firm_id} from {old_tier.value} to {new_tier.value}")
        return firm

    async def check_trial_expiration(self, firm_id: UUID) -> Dict[str, Any]:
        """
        Check if trial has expired

        Args:
            firm_id: Firm ID

        Returns:
            Dictionary with trial status
        """
        firm = await self.db.get(CPAFirm, firm_id)
        if not firm:
            raise ValueError(f"Firm {firm_id} not found")

        if firm.subscription_tier != FirmSubscriptionTier.TRIAL:
            return {
                "is_trial": False,
                "is_expired": False,
                "days_remaining": None
            }

        today = date.today()
        is_expired = firm.trial_end_date < today if firm.trial_end_date else False
        days_remaining = (firm.trial_end_date - today).days if firm.trial_end_date else 0

        # Auto-suspend if expired
        if is_expired and firm.subscription_status == FirmStatus.ACTIVE:
            firm.subscription_status = FirmStatus.TRIAL_EXPIRED
            await self.db.commit()
            logger.warning(f"Firm {firm_id} trial expired, status set to TRIAL_EXPIRED")

        return {
            "is_trial": True,
            "is_expired": is_expired,
            "trial_end_date": firm.trial_end_date,
            "days_remaining": max(0, days_remaining)
        }

    async def check_limits(self, firm_id: UUID) -> Dict[str, Any]:
        """
        Check if firm is within subscription limits

        Args:
            firm_id: Firm ID

        Returns:
            Dictionary with limit status
        """
        firm = await self.db.get(CPAFirm, firm_id)
        if not firm:
            raise ValueError(f"Firm {firm_id} not found")

        # Count current usage
        client_count = await self.db.execute(
            select(func.count()).select_from(text("atlas.clients")).where(
                text("cpa_firm_id = :firm_id AND is_active = TRUE"),
                {"firm_id": firm_id}
            )
        )
        current_clients = client_count.scalar() or 0

        user_count = await self.db.execute(
            select(func.count()).select_from(text("atlas.users")).where(
                text("cpa_firm_id = :firm_id AND is_active = TRUE"),
                {"firm_id": firm_id}
            )
        )
        current_users = user_count.scalar() or 0

        return {
            "clients": {
                "current": current_clients,
                "max": firm.max_clients,
                "available": firm.max_clients - current_clients,
                "at_limit": current_clients >= firm.max_clients
            },
            "users": {
                "current": current_users,
                "max": firm.max_users,
                "available": firm.max_users - current_users,
                "at_limit": current_users >= firm.max_users
            }
        }

    async def update_branding(
        self,
        firm_id: UUID,
        logo_url: Optional[str] = None,
        primary_color: Optional[str] = None,
        secondary_color: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> CPAFirm:
        """
        Update firm branding

        Args:
            firm_id: Firm ID
            logo_url: Logo URL
            primary_color: Primary brand color (hex)
            secondary_color: Secondary brand color (hex)
            user_id: User making update

        Returns:
            Updated firm
        """
        updates = {}
        if logo_url is not None:
            updates["logo_url"] = logo_url
        if primary_color is not None:
            updates["primary_color"] = primary_color
        if secondary_color is not None:
            updates["secondary_color"] = secondary_color

        return await self.update_firm(firm_id, updates, user_id)

    async def get_firm_dashboard(self, firm_id: UUID) -> Dict[str, Any]:
        """
        Get comprehensive firm dashboard

        Args:
            firm_id: Firm ID

        Returns:
            Dashboard data
        """
        # Get firm details
        firm = await self.db.get(CPAFirm, firm_id)
        if not firm:
            raise ValueError(f"Firm {firm_id} not found")

        # Get metrics from view
        query = text("""
            SELECT
                total_clients,
                total_users,
                total_engagements,
                active_engagements,
                completed_engagements
            FROM atlas.firm_dashboard_metrics
            WHERE firm_id = :firm_id
        """)

        result = await self.db.execute(query, {"firm_id": firm_id})
        metrics = result.fetchone()

        # Get trial and limits
        trial_status = await self.check_trial_expiration(firm_id)
        limits = await self.check_limits(firm_id)

        return {
            "firm": {
                "id": str(firm.id),
                "name": firm.firm_name,
                "subscription_tier": firm.subscription_tier.value,
                "subscription_status": firm.subscription_status.value
            },
            "trial": trial_status,
            "limits": limits,
            "metrics": {
                "total_clients": metrics[0] if metrics else 0,
                "total_users": metrics[1] if metrics else 0,
                "total_engagements": metrics[2] if metrics else 0,
                "active_engagements": metrics[3] if metrics else 0,
                "completed_engagements": metrics[4] if metrics else 0
            }
        }

    async def suspend_firm(
        self,
        firm_id: UUID,
        reason: str,
        user_id: Optional[UUID] = None
    ) -> CPAFirm:
        """
        Suspend firm (admin action)

        Args:
            firm_id: Firm ID
            reason: Suspension reason
            user_id: User performing suspension

        Returns:
            Updated firm
        """
        firm = await self.db.get(CPAFirm, firm_id)
        if not firm:
            raise ValueError(f"Firm {firm_id} not found")

        firm.subscription_status = FirmStatus.SUSPENDED
        firm.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(firm)

        await self._audit_log(
            user_id=user_id,
            action="firm.suspend",
            resource_type="firm",
            resource_id=firm.id,
            description=f"Suspended firm: {reason}"
        )

        logger.warning(f"Suspended firm {firm_id}: {reason}")
        return firm

    async def _audit_log(
        self,
        action: str,
        resource_type: str,
        resource_id: UUID,
        user_id: Optional[UUID] = None,
        description: Optional[str] = None,
        changes: Optional[Dict] = None
    ):
        """Create audit log entry"""
        query = text("""
            INSERT INTO atlas.audit_log (
                user_id, action, resource_type, resource_id, description, changes
            ) VALUES (
                :user_id, :action, :resource_type, :resource_id, :description, :changes
            )
        """)

        await self.db.execute(query, {
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "description": description,
            "changes": changes
        })
        await self.db.commit()
