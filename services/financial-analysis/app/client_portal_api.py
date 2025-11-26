"""
Client Portal API Endpoints

FastAPI routes for the client-facing portal including:
- OAuth2 authentication (Microsoft 365, Google Business)
- Integration management (QuickBooks, Xero, ADP, Plaid, etc.)
- Document upload and management
- Progress tracking
- AI assistant
- Dashboard statistics
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db as get_async_session
from .permission_service import PermissionService
from .permissions_models import PermissionScope, User, UserRole

router = APIRouter(prefix="/api/client-portal", tags=["Client Portal"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class OAuthInitiateResponse(BaseModel):
    """OAuth initiation response"""

    authUrl: str
    state: str


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request"""

    code: str
    redirectUri: str


class AuthResponse(BaseModel):
    """Authentication response"""

    accessToken: str
    refreshToken: str
    expiresAt: str
    user: dict


class IntegrationConnectionRequest(BaseModel):
    """Integration connection request"""

    integrationType: str


class IntegrationConnectionResponse(BaseModel):
    """Integration connection response"""

    id: str
    integrationType: str
    status: str
    connectedAt: str
    lastSyncAt: Optional[str]
    dataCategories: List[str]


class DocumentUploadResponse(BaseModel):
    """Document upload response"""

    id: str
    fileName: str
    fileSize: int
    fileType: str
    category: str
    uploadedAt: str
    status: str
    aiExtracted: Optional[dict]


class ProgressResponse(BaseModel):
    """Progress tracking response"""

    overall: int
    categories: List[dict]
    lastUpdated: str


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics"""

    documentsUploaded: int
    documentsRequired: int
    integrationsConnected: int
    integrationsAvailable: int
    overallProgress: int
    nextDeadline: Optional[dict]


class ChatMessageRequest(BaseModel):
    """Chat message request"""

    message: str
    engagementId: Optional[str]


class ChatMessageResponse(BaseModel):
    """Chat message response"""

    id: str
    role: str
    content: str
    timestamp: str
    attachments: Optional[List[dict]]


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================


@router.post("/auth/microsoft/authorize", response_model=OAuthInitiateResponse)
async def initiate_microsoft_oauth():
    """
    Initiate Microsoft 365 OAuth flow.

    Returns authorization URL with state parameter.
    """
    state = str(uuid4())

    # In production, use actual Microsoft OAuth endpoints
    auth_url = (
        f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        f"?client_id={{MICROSOFT_CLIENT_ID}}"
        f"&response_type=code"
        f"&redirect_uri={{REDIRECT_URI}}"
        f"&response_mode=query"
        f"&scope=openid%20email%20profile%20User.Read"
        f"&state={state}"
    )

    return OAuthInitiateResponse(authUrl=auth_url, state=state)


@router.post("/auth/google/authorize", response_model=OAuthInitiateResponse)
async def initiate_google_oauth():
    """
    Initiate Google Business OAuth flow.

    Returns authorization URL with state parameter.
    """
    state = str(uuid4())

    # In production, use actual Google OAuth endpoints
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={{GOOGLE_CLIENT_ID}}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&redirect_uri={{REDIRECT_URI}}"
        f"&state={state}"
        f"&access_type=offline"
    )

    return AuthResponse(authUrl=auth_url, state=state)


@router.post("/auth/microsoft/callback", response_model=AuthResponse)
async def handle_microsoft_callback(
    request: OAuthCallbackRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Handle Microsoft OAuth callback.

    Exchanges authorization code for access token.
    """
    # In production:
    # 1. Exchange code for access token with Microsoft
    # 2. Get user info from Microsoft Graph API
    # 3. Create or update user in database
    # 4. Generate JWT tokens

    # Mock implementation
    access_token = "mock_access_token"
    refresh_token = "mock_refresh_token"
    expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()

    user_data = {
        "id": str(uuid4()),
        "email": "user@company.com",
        "firstName": "John",
        "lastName": "Doe",
        "role": "client",
    }

    return AuthResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresAt=expires_at,
        user=user_data,
    )


@router.post("/auth/google/callback", response_model=AuthResponse)
async def handle_google_callback(
    request: OAuthCallbackRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Handle Google OAuth callback.

    Exchanges authorization code for access token.
    """
    # In production:
    # 1. Exchange code for access token with Google
    # 2. Get user info from Google People API
    # 3. Create or update user in database
    # 4. Generate JWT tokens

    # Mock implementation
    access_token = "mock_access_token"
    refresh_token = "mock_refresh_token"
    expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()

    user_data = {
        "id": str(uuid4()),
        "email": "user@company.com",
        "firstName": "Jane",
        "lastName": "Smith",
        "role": "client",
    }

    return AuthResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresAt=expires_at,
        user=user_data,
    )


# ============================================================================
# INTEGRATION ENDPOINTS
# ============================================================================


@router.get("/integrations/available")
async def get_available_integrations():
    """
    Get list of available integrations.

    Returns all integration types that can be connected.
    """
    integrations = [
        {
            "id": "quickbooks",
            "type": "quickbooks",
            "name": "QuickBooks Online",
            "description": "Automatically sync your financial statements, general ledger, and transaction data",
            "icon": "/icons/quickbooks.svg",
            "status": "not_connected",
            "dataCategories": ["Financial Statements", "General Ledger", "Transactions"],
        },
        {
            "id": "xero",
            "type": "xero",
            "name": "Xero",
            "description": "Connect your Xero account to import financial data and reports",
            "icon": "/icons/xero.svg",
            "status": "not_connected",
            "dataCategories": ["Financial Statements", "Bank Transactions", "Invoices"],
        },
        {
            "id": "adp",
            "type": "adp",
            "name": "ADP Workforce",
            "description": "Connect ADP to sync payroll data, tax filings, and employee information",
            "icon": "/icons/adp.svg",
            "status": "not_connected",
            "dataCategories": ["Payroll Data", "Tax Filings", "Employee Records"],
        },
        {
            "id": "gusto",
            "type": "gusto",
            "name": "Gusto",
            "description": "Import payroll information, benefits, and contractor payments",
            "icon": "/icons/gusto.svg",
            "status": "not_connected",
            "dataCategories": ["Payroll", "Benefits", "Contractors"],
        },
        {
            "id": "plaid",
            "type": "plaid",
            "name": "Bank Account (Plaid)",
            "description": "Securely connect your bank accounts for fraud monitoring",
            "icon": "/icons/plaid.svg",
            "status": "not_connected",
            "dataCategories": ["Bank Transactions", "Account Balances", "Fraud Detection"],
        },
    ]

    return integrations


@router.get("/integrations/connected", response_model=List[IntegrationConnectionResponse])
async def get_connected_integrations():
    """
    Get user's connected integrations.

    Returns all active integration connections.
    """
    # Mock connected integrations
    connections = [
        IntegrationConnectionResponse(
            id=str(uuid4()),
            integrationType="quickbooks",
            status="active",
            connectedAt=datetime.utcnow().isoformat(),
            lastSyncAt=(datetime.utcnow() - timedelta(hours=2)).isoformat(),
            dataCategories=["Financial Statements", "General Ledger", "Transactions"],
        ),
        IntegrationConnectionResponse(
            id=str(uuid4()),
            integrationType="plaid",
            status="active",
            connectedAt=datetime.utcnow().isoformat(),
            lastSyncAt=(datetime.utcnow() - timedelta(hours=1)).isoformat(),
            dataCategories=["Bank Transactions", "Account Balances"],
        ),
    ]

    return connections


@router.post("/integrations/{integration_type}/connect")
async def initiate_integration_connection(integration_type: str):
    """
    Initiate integration connection.

    Returns OAuth URL or connection instructions.
    """
    state = str(uuid4())

    oauth_urls = {
        "quickbooks": "https://appcenter.intuit.com/connect/oauth2",
        "xero": "https://login.xero.com/identity/connect/authorize",
        "adp": "https://accounts.adp.com/auth/oauth/v2/authorize",
        "gusto": "https://api.gusto.com/oauth/authorize",
    }

    if integration_type in oauth_urls:
        auth_url = f"{oauth_urls[integration_type]}?client_id={{CLIENT_ID}}&state={state}"
        return {"authUrl": auth_url, "state": state}

    elif integration_type == "plaid":
        # Plaid uses Link Token
        link_token = "link-sandbox-" + str(uuid4())
        return {"linkToken": link_token}

    raise HTTPException(status_code=404, detail="Integration type not found")


@router.post("/integrations/{integration_type}/callback", response_model=IntegrationConnectionResponse)
async def handle_integration_callback(integration_type: str, code: str, state: str):
    """
    Handle integration OAuth callback.

    Exchanges code for access token and creates connection.
    """
    # In production:
    # 1. Verify state parameter
    # 2. Exchange code for access token
    # 3. Test connection
    # 4. Store connection in database
    # 5. Initiate first sync

    return IntegrationConnectionResponse(
        id=str(uuid4()),
        integrationType=integration_type,
        status="active",
        connectedAt=datetime.utcnow().isoformat(),
        lastSyncAt=None,
        dataCategories=["Data Category 1", "Data Category 2"],
    )


@router.post("/integrations/{connection_id}/sync")
async def sync_integration(connection_id: str):
    """
    Trigger manual integration sync.

    Initiates data sync from integration source.
    """
    # In production: Queue sync job in background
    return {"status": "syncing", "message": "Sync initiated successfully"}


@router.delete("/integrations/{connection_id}")
async def disconnect_integration(connection_id: str):
    """
    Disconnect integration.

    Removes connection and stops syncing.
    """
    # In production:
    # 1. Revoke OAuth tokens
    # 2. Delete connection from database
    # 3. Archive synced data (optional)

    return {"status": "disconnected", "message": "Integration disconnected successfully"}


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    engagementId: Optional[str] = Form(None),
):
    """
    Upload document with AI extraction.

    Accepts file upload, stores document, and triggers AI processing.
    """
    # In production:
    # 1. Validate file type and size
    # 2. Scan for viruses
    # 3. Upload to cloud storage (S3, Azure Blob)
    # 4. Create database record
    # 5. Queue AI extraction job
    # 6. Return document metadata

    document_id = str(uuid4())

    # Mock AI extraction
    ai_extracted = {
        "documentType": "bank_statement",
        "confidence": 0.95,
        "keyData": {
            "accountNumber": "****1234",
            "statementDate": "2024-12-31",
            "beginningBalance": 15000.00,
            "endingBalance": 18500.00,
        },
    }

    return DocumentUploadResponse(
        id=document_id,
        fileName=file.filename or "document.pdf",
        fileSize=0,  # Would be actual file size
        fileType=file.content_type or "application/pdf",
        category=category,
        uploadedAt=datetime.utcnow().isoformat(),
        status="processing",
        aiExtracted=ai_extracted,
    )


@router.get("/documents")
async def get_documents(engagementId: Optional[str] = None):
    """
    Get all documents for client.

    Optionally filtered by engagement ID.
    """
    # Mock documents
    documents = [
        {
            "id": str(uuid4()),
            "fileName": "Bank_Statement_Dec_2024.pdf",
            "fileSize": 245000,
            "fileType": "application/pdf",
            "category": "bank_statements",
            "uploadedAt": datetime.utcnow().isoformat(),
            "status": "ready",
        },
        {
            "id": str(uuid4()),
            "fileName": "Financial_Statements_2024.xlsx",
            "fileSize": 450000,
            "fileType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "category": "financial_statements",
            "uploadedAt": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "status": "ready",
        },
    ]

    return documents


@router.get("/documents/requirements/{engagement_id}")
async def get_document_requirements(engagement_id: str):
    """
    Get required documents for engagement.

    Returns checklist of required documents with status.
    """
    requirements = [
        {
            "id": str(uuid4()),
            "category": "financial_statements",
            "title": "Financial Statements",
            "description": "Balance sheet, income statement, and cash flow statement",
            "required": True,
            "status": "uploaded",
            "uploadedDocuments": 1,
        },
        {
            "id": str(uuid4()),
            "category": "bank_statements",
            "title": "Bank Statements",
            "description": "Monthly bank statements for all accounts (last 12 months)",
            "required": True,
            "status": "uploaded",
            "uploadedDocuments": 12,
        },
        {
            "id": str(uuid4()),
            "category": "tax_documents",
            "title": "Tax Documents",
            "description": "Previous year tax returns and supporting schedules",
            "required": True,
            "status": "pending",
            "uploadedDocuments": 0,
        },
        {
            "id": str(uuid4()),
            "category": "payroll",
            "title": "Payroll Records",
            "description": "Payroll registers and quarterly 941 filings",
            "required": True,
            "status": "pending",
            "uploadedDocuments": 0,
        },
    ]

    return requirements


# ============================================================================
# PROGRESS & DASHBOARD ENDPOINTS
# ============================================================================


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(engagementId: Optional[str] = None):
    """
    Get dashboard statistics.

    Returns key metrics for client dashboard.
    """
    return DashboardStatsResponse(
        documentsUploaded=18,
        documentsRequired=25,
        integrationsConnected=2,
        integrationsAvailable=3,
        overallProgress=72,
        nextDeadline={
            "date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "description": "Complete all document uploads",
        },
    )


@router.get("/engagements/{engagement_id}/progress", response_model=ProgressResponse)
async def get_engagement_progress(engagement_id: str):
    """
    Get detailed engagement progress.

    Returns progress breakdown by category.
    """
    return ProgressResponse(
        overall=72,
        categories=[
            {
                "category": "documents",
                "label": "Documents",
                "progress": 72,
                "status": "in_progress",
                "items": [
                    {"name": "Financial Statements", "completed": True},
                    {"name": "Bank Statements", "completed": True},
                    {"name": "Tax Documents", "completed": False},
                    {"name": "Payroll Records", "completed": False},
                ],
            },
            {
                "category": "integrations",
                "label": "Integrations",
                "progress": 67,
                "status": "in_progress",
                "items": [
                    {"name": "Accounting Software", "completed": True},
                    {"name": "Payroll System", "completed": True},
                    {"name": "Bank Accounts", "completed": False},
                ],
            },
            {
                "category": "questionnaire",
                "label": "Questionnaire",
                "progress": 75,
                "status": "in_progress",
                "items": [
                    {"name": "Company Information", "completed": True},
                    {"name": "Financial Details", "completed": True},
                    {"name": "Risk Assessment", "completed": False},
                ],
            },
        ],
        lastUpdated=datetime.utcnow().isoformat(),
    )


# ============================================================================
# AI ASSISTANT ENDPOINTS
# ============================================================================


@router.get("/ai/chat/messages")
async def get_chat_messages(engagementId: Optional[str] = None):
    """
    Get chat message history.

    Returns previous conversations with AI assistant.
    """
    messages = [
        ChatMessageResponse(
            id=str(uuid4()),
            role="assistant",
            content="Hi! I'm here to help you with your audit engagement. What can I assist you with today?",
            timestamp=(datetime.utcnow() - timedelta(hours=2)).isoformat(),
            attachments=None,
        ),
        ChatMessageResponse(
            id=str(uuid4()),
            role="user",
            content="What documents do I still need to upload?",
            timestamp=(datetime.utcnow() - timedelta(hours=2)).isoformat(),
            attachments=None,
        ),
        ChatMessageResponse(
            id=str(uuid4()),
            role="assistant",
            content="You still need to upload:\n1. Tax documents (2023 returns)\n2. Payroll records (last 12 months)\n\nWould you like me to guide you through uploading these?",
            timestamp=(datetime.utcnow() - timedelta(hours=2)).isoformat(),
            attachments=[
                {"type": "checklist", "data": {"items": ["Tax documents", "Payroll records"]}}
            ],
        ),
    ]

    return messages


@router.post("/ai/chat/send", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest):
    """
    Send message to AI assistant.

    Returns AI-generated response.
    """
    # In production:
    # 1. Store user message
    # 2. Build context (engagement data, documents, progress)
    # 3. Call LLM service
    # 4. Parse response
    # 5. Store assistant message
    # 6. Return response

    # Mock AI response
    ai_responses = {
        "help": "I can help you with:\n• Uploading documents\n• Connecting integrations\n• Understanding requirements\n• Tracking your progress",
        "documents": "Based on your engagement, you still need to upload tax documents and payroll records. Would you like me to guide you?",
        "integration": "To connect QuickBooks, go to the Integrations page and click 'Connect' on the QuickBooks card. You'll need your Intuit account credentials.",
    }

    # Simple keyword matching for demo
    response_content = ai_responses.get(
        "help",
        "I understand. Let me help you with that. Could you provide more details about what you need?",
    )

    return ChatMessageResponse(
        id=str(uuid4()),
        role="assistant",
        content=response_content,
        timestamp=datetime.utcnow().isoformat(),
        attachments=None,
    )


@router.get("/ai/suggestions")
async def get_ai_suggestions(engagementId: Optional[str] = None):
    """
    Get AI-powered suggestions.

    Returns smart suggestions based on engagement status.
    """
    suggestions = [
        {
            "id": str(uuid4()),
            "type": "document",
            "title": "Upload missing tax documents",
            "description": "Your 2023 tax returns are still required",
            "priority": "high",
        },
        {
            "id": str(uuid4()),
            "type": "integration",
            "title": "Connect your payroll system",
            "description": "Connecting Gusto will automatically import payroll data",
            "priority": "medium",
        },
        {
            "id": str(uuid4()),
            "type": "action",
            "title": "Complete risk assessment questionnaire",
            "description": "Only 2 questions remaining",
            "priority": "low",
        },
    ]

    return suggestions


# ============================================================================
# ACTIVITY & NOTIFICATIONS
# ============================================================================


@router.get("/activity")
async def get_activity_feed(engagementId: Optional[str] = None):
    """
    Get activity feed.

    Returns recent activities and updates.
    """
    activities = [
        {
            "id": str(uuid4()),
            "type": "document_uploaded",
            "title": "Document uploaded",
            "description": "Bank_Statement_Dec_2024.pdf",
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "icon": "Upload",
            "color": "green",
        },
        {
            "id": str(uuid4()),
            "type": "integration_synced",
            "title": "QuickBooks synced",
            "description": "156 transactions imported",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "icon": "RefreshCw",
            "color": "blue",
        },
        {
            "id": str(uuid4()),
            "type": "auditor_comment",
            "title": "Auditor commented",
            "description": "Please upload Q4 payroll summaries",
            "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "icon": "MessageSquare",
            "color": "purple",
        },
    ]

    return {"activities": activities}


@router.get("/notifications")
async def get_notifications():
    """
    Get user notifications.

    Returns unread and recent notifications.
    """
    notifications = [
        {
            "id": str(uuid4()),
            "type": "info",
            "title": "New document required",
            "message": "Your auditor has requested additional documentation",
            "timestamp": datetime.utcnow().isoformat(),
            "read": False,
            "action": {"label": "View Details", "url": "/documents"},
        },
        {
            "id": str(uuid4()),
            "type": "success",
            "title": "Integration connected",
            "message": "QuickBooks Online successfully connected",
            "timestamp": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            "read": True,
        },
    ]

    return notifications
