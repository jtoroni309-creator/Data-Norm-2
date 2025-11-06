"""
Accounting Integrations REST API

FastAPI application providing endpoints for managing accounting software integrations,
data synchronization, and normalized financial data access.

Endpoints:
- OAuth connection flow
- Data sync management
- Chart of accounts mapping
- Normalized financial data
- Webhook handlers
"""

import logging
import os
import secrets
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, Header, Depends, Query
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

# Import services
from .quickbooks_integration import (
    QuickBooksIntegrationService,
    QuickBooksConfig,
    IntegrationProvider,
    IntegrationStatus,
    DataType
)
from .xero_integration import XeroIntegrationService, XeroConfig
from .integration_manager import (
    IntegrationManagerService,
    AccountMappingService,
    StandardAccountType,
    StandardAccountCategory
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== FastAPI App ====================

app = FastAPI(
    title="Accounting Integrations API",
    description="Integrate with QuickBooks, Xero, and other accounting software",
    version="1.0.0"
)


# ==================== Dependency Injection ====================

def get_integration_manager() -> IntegrationManagerService:
    """Get integration manager service (singleton)"""
    if not hasattr(app.state, "integration_manager"):
        # Initialize QuickBooks service
        qb_config = QuickBooksConfig(
            client_id=os.environ.get("QUICKBOOKS_CLIENT_ID", ""),
            client_secret=os.environ.get("QUICKBOOKS_CLIENT_SECRET", ""),
            redirect_uri=os.environ.get("QUICKBOOKS_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/quickbooks/callback"),
            environment=os.environ.get("QUICKBOOKS_ENVIRONMENT", "sandbox")
        )
        qb_service = QuickBooksIntegrationService(config=qb_config)

        # Initialize Xero service
        xero_config = XeroConfig(
            client_id=os.environ.get("XERO_CLIENT_ID", ""),
            client_secret=os.environ.get("XERO_CLIENT_SECRET", ""),
            redirect_uri=os.environ.get("XERO_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/xero/callback")
        )
        xero_service = XeroIntegrationService(config=xero_config)

        # Initialize integration manager
        mapping_service = AccountMappingService()
        app.state.integration_manager = IntegrationManagerService(
            quickbooks_service=qb_service,
            xero_service=xero_service,
            mapping_service=mapping_service
        )

    return app.state.integration_manager


# ==================== Request/Response Models ====================

class ConnectionInitRequest(BaseModel):
    """Request to initiate OAuth connection"""
    provider: str  # quickbooks_online, xero
    tenant_id: UUID


class ConnectionInitResponse(BaseModel):
    """Response with authorization URL"""
    authorization_url: str
    state: str
    provider: str


class ConnectionCallback(BaseModel):
    """OAuth callback parameters"""
    code: str
    state: str
    realm_id: Optional[str] = None  # QuickBooks only


class ConnectionResponse(BaseModel):
    """Integration connection response"""
    id: str
    tenant_id: str
    provider: str
    status: str
    company_name: Optional[str] = None
    connected_at: str
    last_sync_at: Optional[str] = None


class SyncRequest(BaseModel):
    """Request to sync data"""
    connection_id: UUID
    data_types: Optional[List[str]] = None  # None = sync all configured


class SyncJobResponse(BaseModel):
    """Sync job response"""
    id: str
    connection_id: str
    data_type: str
    status: str
    records_synced: int
    records_failed: int
    started_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class AccountMappingRequest(BaseModel):
    """Request to override account mapping"""
    mapping_id: UUID
    standard_account_type: StandardAccountType
    standard_account_category: StandardAccountCategory


class WebhookPayload(BaseModel):
    """Generic webhook payload"""
    provider: str
    payload: Dict


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "accounting-integrations"}


# ==================== OAuth Connection Flow ====================

@app.post("/api/v1/integrations/connect", response_model=ConnectionInitResponse)
async def initiate_connection(
    request: ConnectionInitRequest,
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """
    Initiate OAuth connection to accounting software

    Returns authorization URL for user to complete OAuth flow.
    """
    try:
        # Generate random state for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store tenant_id with state (in production, use Redis/database)
        if not hasattr(app.state, "oauth_states"):
            app.state.oauth_states = {}
        app.state.oauth_states[state] = {
            "tenant_id": str(request.tenant_id),
            "provider": request.provider
        }

        # Generate authorization URL
        if request.provider == "quickbooks_online":
            auth_url = manager.quickbooks_service.generate_authorization_url(state)
            return ConnectionInitResponse(
                authorization_url=auth_url,
                state=state,
                provider=request.provider
            )

        elif request.provider == "xero":
            auth_url, code_verifier = manager.xero_service.generate_authorization_url(state)
            return ConnectionInitResponse(
                authorization_url=auth_url,
                state=state,
                provider=request.provider
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider: {request.provider}"
            )

    except Exception as e:
        logger.error(f"Failed to initiate connection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/integrations/quickbooks/callback")
async def quickbooks_callback(
    code: str = Query(...),
    state: str = Query(...),
    realmId: str = Query(...),
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """
    QuickBooks OAuth callback endpoint

    Handles redirect from QuickBooks after user authorization.
    """
    try:
        # Retrieve tenant_id from state
        oauth_states = getattr(app.state, "oauth_states", {})
        state_data = oauth_states.get(state)

        if not state_data:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        tenant_id = UUID(state_data["tenant_id"])

        # Exchange authorization code for access token
        connection = await manager.quickbooks_service.exchange_authorization_code(
            authorization_code=code,
            realm_id=realmId,
            tenant_id=tenant_id
        )

        # Schedule automatic sync
        await manager.schedule_sync(connection.id)

        # Clean up state
        del oauth_states[state]

        # Redirect to success page (customize as needed)
        return RedirectResponse(
            url=f"/integrations/success?connection_id={connection.id}",
            status_code=303
        )

    except Exception as e:
        logger.error(f"QuickBooks callback failed: {str(e)}")
        return RedirectResponse(
            url=f"/integrations/error?message={str(e)}",
            status_code=303
        )


@app.get("/api/v1/integrations/xero/callback")
async def xero_callback(
    code: str = Query(...),
    state: str = Query(...),
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """
    Xero OAuth callback endpoint

    Handles redirect from Xero after user authorization.
    """
    try:
        oauth_states = getattr(app.state, "oauth_states", {})
        state_data = oauth_states.get(state)

        if not state_data:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        tenant_id = UUID(state_data["tenant_id"])

        # Exchange authorization code for access token
        connection = await manager.xero_service.exchange_authorization_code(
            authorization_code=code,
            state=state,
            tenant_id=tenant_id
        )

        # Schedule automatic sync
        await manager.schedule_sync(connection.id)

        # Clean up state
        del oauth_states[state]

        return RedirectResponse(
            url=f"/integrations/success?connection_id={connection.id}",
            status_code=303
        )

    except Exception as e:
        logger.error(f"Xero callback failed: {str(e)}")
        return RedirectResponse(
            url=f"/integrations/error?message={str(e)}",
            status_code=303
        )


# ==================== Connection Management ====================

@app.get("/api/v1/integrations/connections/{tenant_id}", response_model=List[ConnectionResponse])
async def get_connections(
    tenant_id: UUID,
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Get all integrations for a tenant"""
    try:
        connections = []

        # Get QuickBooks connections
        if manager.quickbooks_service:
            qb_connections = manager.quickbooks_service.get_connections_by_tenant(tenant_id)
            for conn in qb_connections:
                connections.append(ConnectionResponse(
                    id=str(conn.id),
                    tenant_id=str(conn.tenant_id),
                    provider=conn.provider.value,
                    status=conn.status.value,
                    company_name=conn.company_name,
                    connected_at=conn.connected_at.isoformat(),
                    last_sync_at=conn.last_sync_at.isoformat() if conn.last_sync_at else None
                ))

        # Get Xero connections
        if manager.xero_service:
            xero_connections = manager.xero_service.get_connections_by_tenant(tenant_id)
            for conn in xero_connections:
                connections.append(ConnectionResponse(
                    id=str(conn.id),
                    tenant_id=str(conn.tenant_id),
                    provider="xero",
                    status=conn.status,
                    company_name=conn.organization_name,
                    connected_at=conn.connected_at.isoformat(),
                    last_sync_at=conn.last_sync_at.isoformat() if conn.last_sync_at else None
                ))

        return connections

    except Exception as e:
        logger.error(f"Failed to get connections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/integrations/connections/{connection_id}/status")
async def get_connection_status(
    connection_id: UUID,
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Get detailed connection status including recent sync jobs"""
    try:
        status = manager.get_integration_status(connection_id)

        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Connection not found")

        return status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get connection status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/integrations/connections/{connection_id}")
async def disconnect(
    connection_id: UUID,
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Disconnect integration"""
    try:
        # Try QuickBooks
        if manager.quickbooks_service:
            connection = manager.quickbooks_service.get_connection(connection_id)
            if connection:
                await manager.quickbooks_service.disconnect(connection_id)
                manager.cancel_sync_schedule(connection_id)
                return {"message": "Connection disconnected successfully"}

        # Try Xero
        if manager.xero_service:
            connection = manager.xero_service.get_connection(connection_id)
            if connection:
                await manager.xero_service.disconnect(connection_id)
                manager.cancel_sync_schedule(connection_id)
                return {"message": "Connection disconnected successfully"}

        raise HTTPException(status_code=404, detail="Connection not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disconnect: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Data Synchronization ====================

@app.post("/api/v1/integrations/sync", response_model=List[SyncJobResponse])
async def sync_data(
    request: SyncRequest,
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Trigger data synchronization"""
    try:
        jobs = await manager.sync_data(
            connection_id=request.connection_id,
            data_types=request.data_types
        )

        return [
            SyncJobResponse(
                id=str(job.id),
                connection_id=str(job.connection_id),
                data_type=job.data_type.value,
                status=job.status.value,
                records_synced=job.records_synced,
                records_failed=job.records_failed,
                started_at=job.started_at.isoformat(),
                completed_at=job.completed_at.isoformat() if job.completed_at else None,
                error_message=job.error_message
            )
            for job in jobs
        ]

    except Exception as e:
        logger.error(f"Data sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/integrations/sync/{job_id}", response_model=SyncJobResponse)
async def get_sync_job(
    job_id: UUID,
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Get sync job status"""
    try:
        # Try QuickBooks
        if manager.quickbooks_service:
            job = manager.quickbooks_service.get_sync_job(job_id)
            if job:
                return SyncJobResponse(
                    id=str(job.id),
                    connection_id=str(job.connection_id),
                    data_type=job.data_type.value,
                    status=job.status.value,
                    records_synced=job.records_synced,
                    records_failed=job.records_failed,
                    started_at=job.started_at.isoformat(),
                    completed_at=job.completed_at.isoformat() if job.completed_at else None,
                    error_message=job.error_message
                )

        raise HTTPException(status_code=404, detail="Sync job not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sync job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Chart of Accounts Mapping ====================

@app.get("/api/v1/integrations/mappings/{connection_id}")
async def get_account_mappings(
    connection_id: UUID,
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Get chart of accounts mappings"""
    try:
        mappings = manager.mapping_service.get_mappings_by_connection(connection_id)

        return [
            {
                "id": str(m.id),
                "provider_account_id": m.provider_account_id,
                "provider_account_name": m.provider_account_name,
                "provider_account_type": m.provider_account_type,
                "standard_account_type": m.standard_account_type.value,
                "standard_account_category": m.standard_account_category.value,
                "confidence_score": m.confidence_score,
                "is_manual_override": m.is_manual_override
            }
            for m in mappings
        ]

    except Exception as e:
        logger.error(f"Failed to get mappings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/integrations/mappings/{connection_id}/review")
async def get_low_confidence_mappings(
    connection_id: UUID,
    threshold: float = Query(0.7, ge=0.0, le=1.0),
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Get low-confidence mappings for manual review"""
    try:
        mappings = manager.mapping_service.get_low_confidence_mappings(
            connection_id,
            threshold
        )

        return [
            {
                "id": str(m.id),
                "provider_account_name": m.provider_account_name,
                "provider_account_type": m.provider_account_type,
                "standard_account_type": m.standard_account_type.value,
                "confidence_score": m.confidence_score
            }
            for m in mappings
        ]

    except Exception as e:
        logger.error(f"Failed to get low-confidence mappings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/integrations/mappings/override")
async def override_mapping(
    request: AccountMappingRequest,
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Manually override account mapping"""
    try:
        mapping = manager.mapping_service.manual_override_mapping(
            mapping_id=request.mapping_id,
            standard_account_type=request.standard_account_type,
            standard_account_category=request.standard_account_category
        )

        return {
            "id": str(mapping.id),
            "provider_account_name": mapping.provider_account_name,
            "standard_account_type": mapping.standard_account_type.value,
            "standard_account_category": mapping.standard_account_category.value,
            "confidence_score": mapping.confidence_score,
            "is_manual_override": mapping.is_manual_override
        }

    except Exception as e:
        logger.error(f"Failed to override mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Normalized Financial Data ====================

@app.get("/api/v1/integrations/data/{connection_id}/chart-of-accounts")
async def get_normalized_chart_of_accounts(
    connection_id: UUID,
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Get normalized chart of accounts"""
    try:
        accounts = await manager.get_normalized_chart_of_accounts(connection_id)

        return [
            {
                "id": acc.id,
                "name": acc.name,
                "account_number": acc.account_number,
                "standard_type": acc.standard_type.value,
                "standard_category": acc.standard_category.value,
                "current_balance": acc.current_balance,
                "active": acc.active
            }
            for acc in accounts
        ]

    except Exception as e:
        logger.error(f"Failed to get normalized chart of accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/integrations/data/{connection_id}/balance-sheet")
async def get_normalized_balance_sheet(
    connection_id: UUID,
    date: Optional[str] = Query(None),
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Get normalized balance sheet"""
    try:
        date_obj = datetime.fromisoformat(date) if date else None
        statement = await manager.get_normalized_balance_sheet(connection_id, date_obj)

        return {
            "statement_type": statement.statement_type,
            "period_end": statement.period_end.isoformat(),
            "total_assets": statement.total_assets,
            "total_liabilities": statement.total_liabilities,
            "total_equity": statement.total_equity,
            "line_items": statement.line_items,
            "currency": statement.currency,
            "synced_at": statement.synced_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get normalized balance sheet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Webhooks ====================

@app.post("/api/v1/integrations/webhooks/quickbooks")
async def quickbooks_webhook(
    request: Request,
    intuit_signature: str = Header(None),
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Handle QuickBooks webhook"""
    try:
        body = await request.body()
        payload = await request.json()

        webhook_token = os.environ.get("QUICKBOOKS_WEBHOOK_TOKEN", "")

        # Verify signature
        if not manager.quickbooks_service.verify_webhook_signature(
            payload=body.decode("utf-8"),
            signature=intuit_signature,
            webhook_token=webhook_token
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Process webhook
        result = await manager.quickbooks_service.handle_webhook(
            payload=payload,
            signature=intuit_signature,
            webhook_token=webhook_token
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QuickBooks webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/integrations/webhooks/xero")
async def xero_webhook(
    request: Request,
    x_xero_signature: str = Header(None),
    manager: IntegrationManagerService = Depends(get_integration_manager)
):
    """Handle Xero webhook"""
    try:
        body = await request.body()

        webhook_key = os.environ.get("XERO_WEBHOOK_KEY", "")

        # Verify signature
        if not manager.xero_service.verify_webhook_signature(
            payload=body.decode("utf-8"),
            signature=x_xero_signature,
            webhook_key=webhook_key
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Process webhook (would implement similar to QuickBooks)
        return {"status": "received"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Xero webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Accounting Integrations API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Accounting Integrations API shutting down...")

    if hasattr(app.state, "integration_manager"):
        manager = app.state.integration_manager
        if manager.quickbooks_service:
            await manager.quickbooks_service.close()
        if manager.xero_service:
            await manager.xero_service.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
