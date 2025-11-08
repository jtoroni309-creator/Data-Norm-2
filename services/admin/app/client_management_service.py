"""
Client Management Service
Manages clients and client portal configuration
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ClientManagementService:
    """Service for managing clients and client portal"""

    def __init__(self, db: AsyncSession):
        """
        Initialize client management service

        Args:
            db: Database session
        """
        self.db = db

    async def create_client(
        self,
        cpa_firm_id: UUID,
        client_name: str,
        primary_contact_email: str,
        primary_contact_name: Optional[str] = None,
        entity_type: Optional[str] = None,
        fiscal_year_end: Optional[str] = None,
        enable_portal: bool = True,
        created_by_user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Create new client

        Args:
            cpa_firm_id: CPA firm ID
            client_name: Client name
            primary_contact_email: Primary contact email
            primary_contact_name: Primary contact name
            entity_type: Entity type (c_corporation, llc, etc.)
            fiscal_year_end: Fiscal year end (MM-DD format)
            enable_portal: Enable client portal
            created_by_user_id: User creating client

        Returns:
            Created client
        """
        logger.info(f"Creating client: {client_name} for firm {cpa_firm_id}")

        # Check firm limits
        limits_query = text("""
            SELECT
                (SELECT COUNT(*) FROM atlas.clients WHERE cpa_firm_id = :firm_id AND is_active = TRUE) as current_clients,
                max_clients
            FROM atlas.cpa_firms
            WHERE id = :firm_id
        """)

        result = await self.db.execute(limits_query, {"firm_id": cpa_firm_id})
        limits = result.fetchone()

        if limits and limits[0] >= limits[1]:
            raise ValueError("Firm has reached maximum client limit")

        # Check if client name already exists for this firm
        existing_query = text("""
            SELECT id FROM atlas.clients
            WHERE cpa_firm_id = :firm_id AND client_name = :client_name
        """)

        existing = await self.db.execute(existing_query, {
            "firm_id": cpa_firm_id,
            "client_name": client_name
        })

        if existing.scalar_one_or_none():
            raise ValueError(f"Client '{client_name}' already exists for this firm")

        # Create client
        insert_query = text("""
            INSERT INTO atlas.clients (
                cpa_firm_id, client_name, primary_contact_name, primary_contact_email,
                entity_type, fiscal_year_end, portal_enabled, client_status, created_by
            ) VALUES (
                :cpa_firm_id, :client_name, :primary_contact_name, :primary_contact_email,
                :entity_type, :fiscal_year_end, :portal_enabled, 'onboarding', :created_by
            )
            RETURNING id
        """)

        result = await self.db.execute(insert_query, {
            "cpa_firm_id": cpa_firm_id,
            "client_name": client_name,
            "primary_contact_name": primary_contact_name,
            "primary_contact_email": primary_contact_email,
            "entity_type": entity_type,
            "fiscal_year_end": fiscal_year_end,
            "portal_enabled": enable_portal,
            "created_by": created_by_user_id
        })

        client_id = result.scalar_one()
        await self.db.commit()

        # Audit log
        await self._audit_log(
            user_id=created_by_user_id,
            action="client.create",
            resource_type="client",
            resource_id=client_id,
            description=f"Created client '{client_name}'",
            firm_id=cpa_firm_id
        )

        logger.info(f"Created client {client_id}: {client_name}")

        return {
            "client_id": str(client_id),
            "client_name": client_name,
            "portal_enabled": enable_portal
        }

    async def update_client(
        self,
        client_id: UUID,
        updates: Dict[str, Any],
        updated_by_user_id: Optional[UUID] = None
    ):
        """
        Update client details

        Args:
            client_id: Client ID
            updates: Fields to update
            updated_by_user_id: User making update
        """
        # Build dynamic update query
        set_clauses = []
        params = {"client_id": client_id}

        allowed_fields = [
            'client_name', 'legal_name', 'ein', 'entity_type',
            'primary_contact_name', 'primary_contact_email', 'primary_contact_phone',
            'address_line1', 'address_line2', 'city', 'state', 'zip_code', 'country',
            'fiscal_year_end', 'industry_code', 'client_status'
        ]

        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = :{field}")
                params[field] = value

        if not set_clauses:
            return

        set_clauses.append("updated_at = NOW()")

        update_query = text(f"""
            UPDATE atlas.clients
            SET {', '.join(set_clauses)}
            WHERE id = :client_id
        """)

        await self.db.execute(update_query, params)
        await self.db.commit()

        await self._audit_log(
            user_id=updated_by_user_id,
            action="client.update",
            resource_type="client",
            resource_id=client_id,
            description=f"Updated client {client_id}",
            changes=updates
        )

        logger.info(f"Updated client {client_id}")

    async def configure_portal_features(
        self,
        client_id: UUID,
        allow_document_upload: Optional[bool] = None,
        allow_confirmation_response: Optional[bool] = None,
        allow_data_export: Optional[bool] = None,
        allow_report_download: Optional[bool] = None,
        allow_messaging: Optional[bool] = None,
        allow_financial_view: Optional[bool] = None,
        configured_by_user_id: Optional[UUID] = None
    ):
        """
        Configure client portal features (feature flags)

        Args:
            client_id: Client ID
            allow_document_upload: Allow document uploads
            allow_confirmation_response: Allow confirmation responses
            allow_data_export: Allow data exports
            allow_report_download: Allow report downloads
            allow_messaging: Allow messaging
            allow_financial_view: Allow viewing financial data
            configured_by_user_id: User configuring features
        """
        logger.info(f"Configuring portal features for client {client_id}")

        updates = {}
        if allow_document_upload is not None:
            updates["allow_document_upload"] = allow_document_upload
        if allow_confirmation_response is not None:
            updates["allow_confirmation_response"] = allow_confirmation_response
        if allow_data_export is not None:
            updates["allow_data_export"] = allow_data_export
        if allow_report_download is not None:
            updates["allow_report_download"] = allow_report_download
        if allow_messaging is not None:
            updates["allow_messaging"] = allow_messaging
        if allow_financial_view is not None:
            updates["allow_financial_view"] = allow_financial_view

        if not updates:
            return

        # Build update query
        set_clauses = [f"{field} = :{field}" for field in updates.keys()]
        set_clauses.append("updated_at = NOW()")

        params = {"client_id": client_id, **updates}

        update_query = text(f"""
            UPDATE atlas.clients
            SET {', '.join(set_clauses)}
            WHERE id = :client_id
        """)

        await self.db.execute(update_query, params)
        await self.db.commit()

        await self._audit_log(
            user_id=configured_by_user_id,
            action="client.configure_portal",
            resource_type="client",
            resource_id=client_id,
            description=f"Configured portal features for client {client_id}",
            changes=updates
        )

        logger.info(f"Configured {len(updates)} portal features for client {client_id}")

    async def enable_portal(
        self,
        client_id: UUID,
        custom_domain: Optional[str] = None,
        logo_url: Optional[str] = None,
        enabled_by_user_id: Optional[UUID] = None
    ):
        """
        Enable client portal

        Args:
            client_id: Client ID
            custom_domain: Custom domain for portal
            logo_url: Client logo URL
            enabled_by_user_id: User enabling portal
        """
        update_query = text("""
            UPDATE atlas.clients
            SET
                portal_enabled = TRUE,
                portal_custom_domain = :custom_domain,
                portal_logo_url = :logo_url,
                updated_at = NOW()
            WHERE id = :client_id
        """)

        await self.db.execute(update_query, {
            "client_id": client_id,
            "custom_domain": custom_domain,
            "logo_url": logo_url
        })

        await self.db.commit()

        await self._audit_log(
            user_id=enabled_by_user_id,
            action="client.enable_portal",
            resource_type="client",
            resource_id=client_id,
            description=f"Enabled portal for client {client_id}"
        )

        logger.info(f"Enabled portal for client {client_id}")

    async def disable_portal(
        self,
        client_id: UUID,
        disabled_by_user_id: Optional[UUID] = None
    ):
        """
        Disable client portal

        Args:
            client_id: Client ID
            disabled_by_user_id: User disabling portal
        """
        update_query = text("""
            UPDATE atlas.clients
            SET portal_enabled = FALSE, updated_at = NOW()
            WHERE id = :client_id
        """)

        await self.db.execute(update_query, {"client_id": client_id})
        await self.db.commit()

        await self._audit_log(
            user_id=disabled_by_user_id,
            action="client.disable_portal",
            resource_type="client",
            resource_id=client_id,
            description=f"Disabled portal for client {client_id}"
        )

        logger.info(f"Disabled portal for client {client_id}")

    async def get_portal_configuration(self, client_id: UUID) -> Dict[str, Any]:
        """
        Get client portal configuration

        Args:
            client_id: Client ID

        Returns:
            Portal configuration
        """
        query = text("""
            SELECT
                portal_enabled,
                portal_custom_domain,
                portal_logo_url,
                allow_document_upload,
                allow_confirmation_response,
                allow_data_export,
                allow_report_download,
                allow_messaging,
                allow_financial_view
            FROM atlas.clients
            WHERE id = :client_id
        """)

        result = await self.db.execute(query, {"client_id": client_id})
        row = result.fetchone()

        if not row:
            raise ValueError(f"Client {client_id} not found")

        return {
            "portal_enabled": row[0],
            "portal_custom_domain": row[1],
            "portal_logo_url": row[2],
            "features": {
                "document_upload": row[3],
                "confirmation_response": row[4],
                "data_export": row[5],
                "report_download": row[6],
                "messaging": row[7],
                "financial_view": row[8]
            }
        }

    async def list_firm_clients(
        self,
        firm_id: UUID,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all clients for a firm

        Args:
            firm_id: Firm ID
            include_inactive: Include inactive clients

        Returns:
            List of clients
        """
        query = text("""
            SELECT
                c.id,
                c.client_name,
                c.entity_type,
                c.client_status,
                c.portal_enabled,
                c.fiscal_year_end,
                COUNT(DISTINCT e.id) as engagement_count,
                COUNT(DISTINCT u.id) as user_count
            FROM atlas.clients c
            LEFT JOIN atlas.engagements e ON e.client_id = c.id
            LEFT JOIN atlas.users u ON u.client_id = c.id AND u.is_active = TRUE
            WHERE c.cpa_firm_id = :firm_id
            AND (:include_inactive = TRUE OR c.is_active = TRUE)
            GROUP BY c.id, c.client_name, c.entity_type, c.client_status, c.portal_enabled, c.fiscal_year_end
            ORDER BY c.client_name
        """)

        result = await self.db.execute(query, {
            "firm_id": firm_id,
            "include_inactive": include_inactive
        })

        clients = []
        for row in result.fetchall():
            clients.append({
                "client_id": str(row[0]),
                "client_name": row[1],
                "entity_type": row[2],
                "status": row[3],
                "portal_enabled": row[4],
                "fiscal_year_end": row[5],
                "engagement_count": row[6],
                "user_count": row[7]
            })

        return clients

    async def get_client_dashboard(self, client_id: UUID) -> Dict[str, Any]:
        """
        Get client dashboard (for client portal)

        Args:
            client_id: Client ID

        Returns:
            Dashboard data
        """
        # Get client details
        client_query = text("""
            SELECT
                c.client_name,
                c.entity_type,
                c.fiscal_year_end,
                c.portal_enabled,
                f.firm_name,
                f.primary_contact_name as firm_contact_name,
                f.primary_contact_email as firm_contact_email
            FROM atlas.clients c
            JOIN atlas.cpa_firms f ON f.id = c.cpa_firm_id
            WHERE c.id = :client_id
        """)

        result = await self.db.execute(client_query, {"client_id": client_id})
        client_row = result.fetchone()

        if not client_row:
            raise ValueError(f"Client {client_id} not found")

        # Get engagements
        engagements_query = text("""
            SELECT
                id,
                engagement_type,
                fiscal_year_end,
                status,
                current_phase
            FROM atlas.engagements
            WHERE client_id = :client_id
            ORDER BY fiscal_year_end DESC
            LIMIT 10
        """)

        result = await self.db.execute(engagements_query, {"client_id": client_id})
        engagements = []
        for row in result.fetchall():
            engagements.append({
                "engagement_id": str(row[0]),
                "engagement_type": row[1],
                "fiscal_year_end": row[2].isoformat() if row[2] else None,
                "status": row[3],
                "current_phase": row[4]
            })

        # Get pending items (confirmations, document requests)
        pending_query = text("""
            SELECT
                'confirmation' as item_type,
                c.id,
                c.confirmation_type,
                c.entity_name,
                c.amount
            FROM atlas.confirmations c
            JOIN atlas.engagements e ON e.id = c.engagement_id
            WHERE e.client_id = :client_id
            AND c.status = 'sent'

            UNION ALL

            SELECT
                'document_request' as item_type,
                NULL as id,
                NULL as confirmation_type,
                'Documents needed' as entity_name,
                NULL as amount
            FROM atlas.engagements e
            WHERE e.client_id = :client_id
            AND e.status = 'in_progress'
            LIMIT 1
        """)

        result = await self.db.execute(pending_query, {"client_id": client_id})
        pending_items = []
        for row in result.fetchall():
            item = {"type": row[0]}
            if row[0] == 'confirmation':
                item.update({
                    "id": str(row[1]),
                    "confirmation_type": row[2],
                    "entity_name": row[3],
                    "amount": float(row[4]) if row[4] else None
                })
            pending_items.append(item)

        return {
            "client": {
                "name": client_row[0],
                "entity_type": client_row[1],
                "fiscal_year_end": client_row[2]
            },
            "cpa_firm": {
                "name": client_row[4],
                "contact_name": client_row[5],
                "contact_email": client_row[6]
            },
            "engagements": engagements,
            "pending_items": pending_items,
            "portal_enabled": client_row[3]
        }

    async def _audit_log(
        self,
        action: str,
        resource_type: str,
        resource_id: UUID,
        user_id: Optional[UUID] = None,
        description: Optional[str] = None,
        changes: Optional[Dict] = None,
        firm_id: Optional[UUID] = None
    ):
        """Create audit log entry"""
        query = text("""
            INSERT INTO atlas.audit_log (
                user_id, cpa_firm_id, action, resource_type,
                resource_id, description, changes
            ) VALUES (
                :user_id, :firm_id, :action, :resource_type,
                :resource_id, :description, :changes
            )
        """)

        await self.db.execute(query, {
            "user_id": user_id,
            "firm_id": firm_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "description": description,
            "changes": changes
        })
        await self.db.commit()
