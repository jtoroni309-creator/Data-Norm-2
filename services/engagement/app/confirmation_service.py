"""
Confirmation Service
Manages external confirmations for A/R, bank, attorney, and other confirmations
"""
import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
import jinja2

from sqlalchemy import select, update, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Engagement
from .database import Base
from .config import settings

logger = logging.getLogger(__name__)


# SQLAlchemy models for confirmations
from sqlalchemy import Column, String, Date, DateTime, Numeric, Boolean, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum


class ConfirmationType(str, PyEnum):
    """Confirmation types"""
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    ACCOUNTS_PAYABLE = "accounts_payable"
    BANK = "bank"
    ATTORNEY = "attorney"
    DEBT = "debt"
    INVENTORY_CONSIGNMENT = "inventory_consignment"
    OTHER = "other"


class ConfirmationStatus(str, PyEnum):
    """Confirmation status"""
    NOT_SENT = "not_sent"
    SENT = "sent"
    RECEIVED = "received"
    EXCEPTION = "exception"
    RESOLVED = "resolved"
    ALTERNATIVE_PROCEDURES = "alternative_procedures"


class ConfirmationResponseType(str, PyEnum):
    """Response type"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    BLANK = "blank"


class Confirmation(Base):
    """Confirmation tracking"""
    __tablename__ = "confirmations"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    engagement_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.engagements.id", ondelete="CASCADE"), nullable=False)
    confirmation_type = Column(SQLEnum(ConfirmationType), nullable=False)

    # Entity details
    entity_name = Column(String(255), nullable=False)
    entity_contact = Column(String(255))
    entity_email = Column(String(255))
    entity_address = Column(Text)

    # Confirmation details
    confirmation_date = Column(Date)
    as_of_date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 2))
    account_number = Column(String(100))

    # Status
    status = Column(SQLEnum(ConfirmationStatus), nullable=False, default=ConfirmationStatus.NOT_SENT)
    response_type = Column(SQLEnum(ConfirmationResponseType))
    sent_date = Column(Date)
    received_date = Column(Date)
    follow_up_count = Column(Integer, default=0)

    # Response
    confirmed_amount = Column(Numeric(18, 2))
    difference_amount = Column(Numeric(18, 2))
    has_exception = Column(Boolean, default=False)
    exception_description = Column(Text)
    exception_resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text)

    # Alternative procedures
    alternative_procedures_performed = Column(Boolean, default=False)
    alternative_procedures_description = Column(Text)
    alternative_procedures_workpaper_id = Column(PGUUID(as_uuid=True))

    # Documents
    confirmation_letter_s3_uri = Column(Text)
    response_document_s3_uri = Column(Text)
    workpaper_id = Column(PGUUID(as_uuid=True))

    # Audit trail
    created_by = Column(PGUUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))


class ConfirmationTemplate(Base):
    """Confirmation letter templates"""
    __tablename__ = "confirmation_templates"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    confirmation_type = Column(SQLEnum(ConfirmationType), nullable=False)
    template_name = Column(String(255), nullable=False)
    template_description = Column(Text)

    subject_line = Column(String(500))
    body_template = Column(Text, nullable=False)

    requires_signature = Column(Boolean, default=True)
    response_deadline_days = Column(Integer, default=14)
    follow_up_frequency_days = Column(Integer, default=7)
    max_follow_ups = Column(Integer, default=2)

    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    created_by = Column(PGUUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ConfirmationException(Base):
    """Confirmation exceptions"""
    __tablename__ = "confirmation_exceptions"
    __table_args__ = {"schema": "atlas"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    confirmation_id = Column(PGUUID(as_uuid=True), ForeignKey("atlas.confirmations.id", ondelete="CASCADE"), nullable=False)

    exception_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    amount_difference = Column(Numeric(18, 2))

    disposition = Column(String(100))
    disposition_notes = Column(Text)
    requires_adjustment = Column(Boolean, default=False)
    adjustment_amount = Column(Numeric(18, 2))

    resolved_by = Column(PGUUID(as_uuid=True))
    resolved_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ConfirmationService:
    """Service for managing confirmations"""

    def __init__(self, db: AsyncSession):
        """
        Initialize confirmation service

        Args:
            db: Database session
        """
        self.db = db
        self.template_env = jinja2.Environment(autoescape=True)

    async def create_confirmation(
        self,
        engagement_id: UUID,
        confirmation_type: ConfirmationType,
        entity_name: str,
        amount: float,
        as_of_date: date,
        entity_email: Optional[str] = None,
        entity_contact: Optional[str] = None,
        entity_address: Optional[str] = None,
        account_number: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> Confirmation:
        """
        Create a new confirmation request

        Args:
            engagement_id: Engagement ID
            confirmation_type: Type of confirmation
            entity_name: Name of entity to confirm
            amount: Amount to confirm
            as_of_date: Date as of which confirmation is requested
            entity_email: Entity email address
            entity_contact: Contact person
            entity_address: Mailing address
            account_number: Account number (for bank confirmations)
            user_id: User creating the confirmation

        Returns:
            Created Confirmation object
        """
        confirmation = Confirmation(
            engagement_id=engagement_id,
            confirmation_type=confirmation_type,
            entity_name=entity_name,
            amount=amount,
            as_of_date=as_of_date,
            entity_email=entity_email,
            entity_contact=entity_contact,
            entity_address=entity_address,
            account_number=account_number,
            status=ConfirmationStatus.NOT_SENT,
            created_by=user_id
        )

        self.db.add(confirmation)
        await self.db.commit()
        await self.db.refresh(confirmation)

        logger.info(f"Created confirmation {confirmation.id} for {entity_name}")
        return confirmation

    async def generate_confirmation_letter(
        self,
        confirmation_id: UUID,
        template_id: Optional[UUID] = None
    ) -> str:
        """
        Generate confirmation letter HTML from template

        Args:
            confirmation_id: Confirmation ID
            template_id: Optional template ID (uses default if not specified)

        Returns:
            HTML content of confirmation letter
        """
        # Get confirmation
        confirmation = await self.db.get(Confirmation, confirmation_id)
        if not confirmation:
            raise ValueError(f"Confirmation {confirmation_id} not found")

        # Get engagement
        engagement = await self.db.get(Engagement, confirmation.engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {confirmation.engagement_id} not found")

        # Fetch client information from atlas.clients table
        client_query = text("""
            SELECT
                client_name,
                primary_contact_name,
                primary_contact_email,
                address_line1,
                address_line2,
                city,
                state,
                zip_code
            FROM atlas.clients
            WHERE id = :client_id
        """)
        client_result = await self.db.execute(client_query, {"client_id": engagement.client_id})
        client = client_result.fetchone()

        # Default client info if not found
        if client:
            client_company_name = client[0] or "Client Company"
            client_contact_name = client[1] or "Management"
            client_contact_title = "Primary Contact"  # Default title
        else:
            client_company_name = "Client Company"
            client_contact_name = "Management"
            client_contact_title = "Primary Contact"

        # Get template
        if template_id:
            template = await self.db.get(ConfirmationTemplate, template_id)
        else:
            # Get default template for this type
            query = select(ConfirmationTemplate).where(
                ConfirmationTemplate.confirmation_type == confirmation.confirmation_type,
                ConfirmationTemplate.is_default == True,
                ConfirmationTemplate.is_active == True
            )
            result = await self.db.execute(query)
            template = result.scalar_one_or_none()

        if not template:
            raise ValueError(f"No template found for {confirmation.confirmation_type}")

        # Build auditor address from settings
        auditor_address_parts = [settings.AUDITOR_FIRM_ADDRESS_LINE1]
        if settings.AUDITOR_FIRM_ADDRESS_LINE2:
            auditor_address_parts.append(settings.AUDITOR_FIRM_ADDRESS_LINE2)
        auditor_address_parts.append(f"{settings.AUDITOR_FIRM_CITY}, {settings.AUDITOR_FIRM_STATE} {settings.AUDITOR_FIRM_POSTAL_CODE}")
        auditor_address = "\n".join(auditor_address_parts)

        # Prepare template variables
        context = {
            'entity_name': confirmation.entity_name,
            'entity_contact': confirmation.entity_contact or 'Sir/Madam',
            'entity_address': confirmation.entity_address,
            'as_of_date': confirmation.as_of_date.strftime('%B %d, %Y'),
            'amount': f"${confirmation.amount:,.2f}" if confirmation.amount else "N/A",
            'account_number': confirmation.account_number or "N/A",
            'client_company_name': client_company_name,
            'client_contact_name': client_contact_name,
            'client_contact_title': client_contact_title,
            'auditor_firm_name': settings.AUDITOR_FIRM_NAME,
            'auditor_address': auditor_address,
        }

        # Render template
        jinja_template = self.template_env.from_string(template.body_template)
        html_content = jinja_template.render(**context)

        logger.info(f"Generated confirmation letter for {confirmation.id}")
        return html_content

    async def mark_confirmation_sent(
        self,
        confirmation_id: UUID,
        sent_date: Optional[date] = None,
        confirmation_letter_s3_uri: Optional[str] = None
    ) -> Confirmation:
        """
        Mark confirmation as sent

        Args:
            confirmation_id: Confirmation ID
            sent_date: Date sent (default today)
            confirmation_letter_s3_uri: S3 URI of sent letter

        Returns:
            Updated Confirmation
        """
        confirmation = await self.db.get(Confirmation, confirmation_id)
        if not confirmation:
            raise ValueError(f"Confirmation {confirmation_id} not found")

        confirmation.status = ConfirmationStatus.SENT
        confirmation.sent_date = sent_date or date.today()
        if confirmation_letter_s3_uri:
            confirmation.confirmation_letter_s3_uri = confirmation_letter_s3_uri

        await self.db.commit()
        await self.db.refresh(confirmation)

        logger.info(f"Marked confirmation {confirmation_id} as sent")
        return confirmation

    async def record_confirmation_response(
        self,
        confirmation_id: UUID,
        confirmed_amount: float,
        received_date: Optional[date] = None,
        response_document_s3_uri: Optional[str] = None,
        response_type: ConfirmationResponseType = ConfirmationResponseType.POSITIVE
    ) -> Confirmation:
        """
        Record confirmation response

        Args:
            confirmation_id: Confirmation ID
            confirmed_amount: Amount confirmed by respondent
            received_date: Date response received
            response_document_s3_uri: S3 URI of response document
            response_type: Type of response

        Returns:
            Updated Confirmation
        """
        confirmation = await self.db.get(Confirmation, confirmation_id)
        if not confirmation:
            raise ValueError(f"Confirmation {confirmation_id} not found")

        confirmation.status = ConfirmationStatus.RECEIVED
        confirmation.confirmed_amount = confirmed_amount
        confirmation.received_date = received_date or date.today()
        confirmation.response_type = response_type

        if response_document_s3_uri:
            confirmation.response_document_s3_uri = response_document_s3_uri

        # Calculate difference
        if confirmation.amount and confirmed_amount:
            difference = abs(float(confirmation.amount) - confirmed_amount)
            if difference > 0.01:  # More than 1 cent difference
                confirmation.has_exception = True
                confirmation.difference_amount = difference
                confirmation.status = ConfirmationStatus.EXCEPTION

        await self.db.commit()
        await self.db.refresh(confirmation)

        logger.info(f"Recorded response for confirmation {confirmation_id}")
        return confirmation

    async def create_exception(
        self,
        confirmation_id: UUID,
        exception_type: str,
        description: str,
        amount_difference: Optional[float] = None
    ) -> ConfirmationException:
        """
        Create confirmation exception

        Args:
            confirmation_id: Confirmation ID
            exception_type: Type of exception (timing, amount, existence, other)
            description: Exception description
            amount_difference: Amount difference if applicable

        Returns:
            Created ConfirmationException
        """
        exception = ConfirmationException(
            confirmation_id=confirmation_id,
            exception_type=exception_type,
            description=description,
            amount_difference=amount_difference
        )

        self.db.add(exception)

        # Update confirmation
        confirmation = await self.db.get(Confirmation, confirmation_id)
        confirmation.has_exception = True
        confirmation.exception_description = description

        await self.db.commit()
        await self.db.refresh(exception)

        logger.info(f"Created exception for confirmation {confirmation_id}")
        return exception

    async def perform_alternative_procedures(
        self,
        confirmation_id: UUID,
        procedures_description: str,
        workpaper_id: Optional[UUID] = None
    ) -> Confirmation:
        """
        Record alternative procedures performed

        Args:
            confirmation_id: Confirmation ID
            procedures_description: Description of alternative procedures
            workpaper_id: Reference to workpaper documenting procedures

        Returns:
            Updated Confirmation
        """
        confirmation = await self.db.get(Confirmation, confirmation_id)
        if not confirmation:
            raise ValueError(f"Confirmation {confirmation_id} not found")

        confirmation.status = ConfirmationStatus.ALTERNATIVE_PROCEDURES
        confirmation.alternative_procedures_performed = True
        confirmation.alternative_procedures_description = procedures_description
        confirmation.alternative_procedures_workpaper_id = workpaper_id

        await self.db.commit()
        await self.db.refresh(confirmation)

        logger.info(f"Recorded alternative procedures for confirmation {confirmation_id}")
        return confirmation

    async def get_confirmation_summary(self, engagement_id: UUID) -> Dict[str, Any]:
        """
        Get confirmation summary statistics

        Args:
            engagement_id: Engagement ID

        Returns:
            Dictionary with summary statistics
        """
        query = select(Confirmation).where(Confirmation.engagement_id == engagement_id)
        result = await self.db.execute(query)
        confirmations = result.scalars().all()

        summary = {
            'total': len(confirmations),
            'by_type': {},
            'by_status': {},
            'response_rate': 0.0,
            'exception_count': sum(1 for c in confirmations if c.has_exception),
            'alternative_procedures_count': sum(1 for c in confirmations if c.alternative_procedures_performed)
        }

        # Count by type
        for conf_type in ConfirmationType:
            summary['by_type'][conf_type.value] = sum(
                1 for c in confirmations if c.confirmation_type == conf_type
            )

        # Count by status
        for status in ConfirmationStatus:
            summary['by_status'][status.value] = sum(
                1 for c in confirmations if c.status == status
            )

        # Calculate response rate
        sent_count = sum(1 for c in confirmations if c.status in [ConfirmationStatus.SENT, ConfirmationStatus.RECEIVED, ConfirmationStatus.EXCEPTION, ConfirmationStatus.RESOLVED])
        received_count = sum(1 for c in confirmations if c.status in [ConfirmationStatus.RECEIVED, ConfirmationStatus.EXCEPTION, ConfirmationStatus.RESOLVED])

        if sent_count > 0:
            summary['response_rate'] = round(100.0 * received_count / sent_count, 2)

        return summary

    async def get_pending_follow_ups(self, engagement_id: UUID, days_threshold: int = 14) -> List[Confirmation]:
        """
        Get confirmations needing follow-up

        Args:
            engagement_id: Engagement ID
            days_threshold: Number of days after which follow-up is needed

        Returns:
            List of confirmations needing follow-up
        """
        cutoff_date = date.today() - timedelta(days=days_threshold)

        query = select(Confirmation).where(
            Confirmation.engagement_id == engagement_id,
            Confirmation.status == ConfirmationStatus.SENT,
            Confirmation.sent_date <= cutoff_date
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())
