"""
Admin Portal API Endpoints

FastAPI routes for platform administration including:
- Dashboard KPIs and analytics
- Customer (CPA firm) management
- Usage monitoring and billing
- Limit enforcement
- System monitoring
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .permission_service import PermissionService
from .permissions_models import (
    PermissionScope,
    Tenant,
    TenantStatus,
    User,
    UserRole,
)

router = APIRouter(prefix="/api/admin", tags=["Admin Portal"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class DashboardKPIsResponse(BaseModel):
    """Dashboard KPIs"""

    revenue: dict
    customers: dict
    usage: dict
    health: dict


class CustomerResponse(BaseModel):
    """Customer response"""

    id: str
    firmName: str
    firmEin: str
    status: str
    subscriptionTier: str
    billingEmail: str
    primaryContact: dict
    limits: dict
    usage: dict
    billing: dict
    createdAt: str
    lastActivityAt: str
    onboardingCompleted: bool


class CreateCustomerRequest(BaseModel):
    """Create customer request"""

    firmName: str
    firmEin: str
    billingEmail: EmailStr
    primaryContactName: str
    primaryContactEmail: EmailStr
    primaryContactPhone: str
    subscriptionTier: str
    addressLine1: str
    addressLine2: Optional[str]
    city: str
    state: str
    postalCode: str
    country: str = "USA"
    customLimits: Optional[dict]


class UpdateCustomerRequest(BaseModel):
    """Update customer request"""

    firmName: Optional[str]
    status: Optional[str]
    subscriptionTier: Optional[str]
    billingEmail: Optional[EmailStr]
    limits: Optional[dict]


class UsageAnalyticsResponse(BaseModel):
    """Usage analytics response"""

    customerId: str
    period: dict
    users: dict
    engagements: dict
    documents: dict
    integrations: dict
    api: dict


class SubscriptionPlanResponse(BaseModel):
    """Subscription plan response"""

    id: str
    name: str
    description: str
    monthlyPrice: float
    yearlyPrice: float
    limits: dict
    features: List[str]
    recommended: bool = False


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_subscription_plans() -> List[SubscriptionPlanResponse]:
    """Get all subscription plans"""
    return [
        SubscriptionPlanResponse(
            id="trial",
            name="Trial",
            description="30-day free trial with limited features",
            monthlyPrice=0,
            yearlyPrice=0,
            limits={"users": 2, "engagements": 5, "storageGB": 10, "clients": 10},
            features=[
                "Up to 2 users",
                "5 engagements per month",
                "10 GB storage",
                "Email support",
                "Basic integrations",
            ],
        ),
        SubscriptionPlanResponse(
            id="starter",
            name="Starter",
            description="Perfect for small CPA firms",
            monthlyPrice=299,
            yearlyPrice=3228,  # 10% discount
            limits={"users": 5, "engagements": 25, "storageGB": 100, "clients": 50},
            features=[
                "Up to 5 users",
                "25 engagements per month",
                "100 GB storage",
                "Priority email support",
                "All integrations",
                "AI-powered analysis",
                "Standard reports",
            ],
        ),
        SubscriptionPlanResponse(
            id="professional",
            name="Professional",
            description="For growing firms with multiple partners",
            monthlyPrice=799,
            yearlyPrice=8628,  # 10% discount
            limits={"users": 20, "engagements": 100, "storageGB": 500, "clients": 200},
            features=[
                "Up to 20 users",
                "100 engagements per month",
                "500 GB storage",
                "Phone & email support",
                "All integrations",
                "Advanced AI features",
                "Custom reports",
                "White-label reports",
                "API access",
            ],
            recommended=True,
        ),
        SubscriptionPlanResponse(
            id="enterprise",
            name="Enterprise",
            description="For large firms with complex needs",
            monthlyPrice=1999,
            yearlyPrice=21588,  # 10% discount
            limits={"users": 100, "engagements": 500, "storageGB": 2000, "clients": 1000},
            features=[
                "Up to 100 users",
                "500 engagements per month",
                "2 TB storage",
                "24/7 phone & email support",
                "Dedicated account manager",
                "All integrations",
                "Advanced AI features",
                "Custom reports",
                "White-label platform",
                "API access",
                "SSO/SAML",
                "Custom integrations",
                "SLA guarantee",
            ],
        ),
        SubscriptionPlanResponse(
            id="custom",
            name="Custom",
            description="Tailored solutions for your specific needs",
            monthlyPrice=0,  # Custom pricing
            yearlyPrice=0,
            limits={"users": 999, "engagements": 9999, "storageGB": 10000, "clients": 10000},
            features=[
                "Unlimited users",
                "Unlimited engagements",
                "Custom storage",
                "White-glove support",
                "Custom features",
                "On-premise deployment",
                "Custom SLA",
            ],
        ),
    ]


def calculate_customer_usage(customer_id: str) -> dict:
    """Calculate current usage for a customer"""
    # In production, query from database
    return {
        "currentUsers": 3,
        "currentEngagements": 12,
        "currentStorageGB": 45.2,
        "currentClients": 18,
    }


def calculate_billing_info(customer_id: str, subscription_tier: str) -> dict:
    """Calculate billing information"""
    plans = {plan.id: plan for plan in get_subscription_plans()}
    plan = plans.get(subscription_tier)

    if not plan:
        return {
            "monthlyRevenue": 0,
            "lastPaymentDate": None,
            "nextBillingDate": None,
            "paymentMethod": None,
            "billingStatus": "pending",
        }

    return {
        "monthlyRevenue": plan.monthlyPrice,
        "lastPaymentDate": (datetime.utcnow() - timedelta(days=15)).isoformat(),
        "nextBillingDate": (datetime.utcnow() + timedelta(days=15)).isoformat(),
        "paymentMethod": "Visa ****1234",
        "billingStatus": "current",
    }


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================


@router.get("/dashboard/kpis", response_model=DashboardKPIsResponse)
async def get_dashboard_kpis():
    """
    Get dashboard KPIs.

    Returns key performance indicators for platform overview.
    """
    # In production, calculate from database
    kpis = DashboardKPIsResponse(
        revenue={
            "mrr": 47850,  # Monthly Recurring Revenue
            "arr": 574200,  # Annual Recurring Revenue
            "growth": 12.5,  # 12.5% MoM growth
            "churn": 2.1,  # 2.1% churn rate
        },
        customers={
            "total": 48,
            "active": 42,
            "trial": 6,
            "churned": 3,
            "newThisMonth": 5,
        },
        usage={
            "totalUsers": 324,
            "totalEngagements": 1247,
            "totalStorageGB": 2847.5,
            "activeEngagements": 389,
        },
        health={
            "uptime": 99.98,
            "avgResponseTime": 145,  # ms
            "errorRate": 0.02,  # 0.02%
            "apiCalls24h": 458742,
        },
    )

    return kpis


@router.get("/dashboard/stats")
async def get_platform_stats(timeRange: str = Query("month", regex="^(day|week|month|year)$")):
    """
    Get platform statistics over time.

    Returns time-series data for charts.
    """
    # Generate mock time-series data
    if timeRange == "month":
        days = 30
    elif timeRange == "week":
        days = 7
    elif timeRange == "day":
        days = 1
    else:
        days = 365

    revenue_over_time = []
    customers_over_time = []
    base_revenue = 35000
    base_customers = 35

    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days - i - 1)).date().isoformat()
        revenue_over_time.append(
            {
                "date": date,
                "value": base_revenue + (i * 450) + (i % 5) * 200,
            }
        )
        customers_over_time.append(
            {
                "date": date,
                "active": base_customers + (i // 3),
                "trial": 4 + (i % 3),
                "churned": 2 + (i % 2),
            }
        )

    return {
        "timeRange": timeRange,
        "revenueOverTime": revenue_over_time,
        "customersOverTime": customers_over_time,
        "topCustomers": [
            {"customerId": str(uuid4()), "firmName": "Smith & Associates CPA", "revenue": 1999},
            {"customerId": str(uuid4()), "firmName": "Johnson Tax Services", "revenue": 1999},
            {"customerId": str(uuid4()), "firmName": "Williams Accounting", "revenue": 799},
            {"customerId": str(uuid4()), "firmName": "Brown Financial Group", "revenue": 799},
            {"customerId": str(uuid4()), "firmName": "Davis & Partners", "revenue": 299},
        ],
        "subscriptionDistribution": [
            {"tier": "trial", "count": 6, "revenue": 0},
            {"tier": "starter", "count": 15, "revenue": 4485},
            {"tier": "professional", "count": 22, "revenue": 17578},
            {"tier": "enterprise", "count": 5, "revenue": 9995},
        ],
    }


# ============================================================================
# CUSTOMER MANAGEMENT ENDPOINTS
# ============================================================================


@router.get("/customers", response_model=List[CustomerResponse])
async def list_customers(
    status: Optional[str] = None,
    subscriptionTier: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    pageSize: int = Query(25, ge=1, le=100),
):
    """
    List all customers (CPA firms).

    Supports filtering by status, subscription tier, and search.
    """
    # Mock customer data
    plans = {plan.id: plan for plan in get_subscription_plans()}

    customers = []
    for i in range(10):
        tier = ["starter", "professional", "enterprise", "trial"][i % 4]
        customer_id = str(uuid4())

        customer = CustomerResponse(
            id=customer_id,
            firmName=f"Customer Firm {i + 1}",
            firmEin=f"{10 + i}-{1234567 + i}",
            status=["active", "trial", "active", "suspended"][i % 4],
            subscriptionTier=tier,
            billingEmail=f"billing{i}@firm{i}.com",
            primaryContact={
                "name": f"John Doe {i}",
                "email": f"john{i}@firm{i}.com",
                "phone": f"555-010{i}",
            },
            limits=plans[tier].limits,
            usage=calculate_customer_usage(customer_id),
            billing=calculate_billing_info(customer_id, tier),
            createdAt=(datetime.utcnow() - timedelta(days=30 * i)).isoformat(),
            lastActivityAt=(datetime.utcnow() - timedelta(hours=i)).isoformat(),
            onboardingCompleted=i % 3 != 0,
        )
        customers.append(customer)

    # Apply filters
    if status:
        customers = [c for c in customers if c.status == status]
    if subscriptionTier:
        customers = [c for c in customers if c.subscriptionTier == subscriptionTier]
    if search:
        search_lower = search.lower()
        customers = [
            c
            for c in customers
            if search_lower in c.firmName.lower() or search_lower in c.billingEmail.lower()
        ]

    # Pagination
    start = (page - 1) * pageSize
    end = start + pageSize
    return customers[start:end]


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    """
    Get customer details.

    Returns detailed information about a specific customer.
    """
    # Mock customer
    tier = "professional"
    plans = {plan.id: plan for plan in get_subscription_plans()}

    customer = CustomerResponse(
        id=customer_id,
        firmName="Smith & Associates CPA",
        firmEin="12-3456789",
        status="active",
        subscriptionTier=tier,
        billingEmail="billing@smithcpa.com",
        primaryContact={
            "name": "Sarah Smith",
            "email": "sarah@smithcpa.com",
            "phone": "555-0100",
        },
        limits=plans[tier].limits,
        usage=calculate_customer_usage(customer_id),
        billing=calculate_billing_info(customer_id, tier),
        createdAt=(datetime.utcnow() - timedelta(days=90)).isoformat(),
        lastActivityAt=(datetime.utcnow() - timedelta(hours=2)).isoformat(),
        onboardingCompleted=True,
    )

    return customer


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(request: CreateCustomerRequest):
    """
    Create new customer (CPA firm).

    Sets up new tenant with subscription and limits.
    """
    # In production:
    # 1. Create tenant in database
    # 2. Send welcome email
    # 3. Create initial admin user invitation
    # 4. Set up billing subscription
    # 5. Initialize usage tracking

    customer_id = str(uuid4())
    plans = {plan.id: plan for plan in get_subscription_plans()}
    plan = plans.get(request.subscriptionTier)

    if not plan:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")

    # Use custom limits if provided, otherwise use plan defaults
    limits = request.customLimits if request.customLimits else plan.limits

    customer = CustomerResponse(
        id=customer_id,
        firmName=request.firmName,
        firmEin=request.firmEin,
        status="trial" if request.subscriptionTier == "trial" else "active",
        subscriptionTier=request.subscriptionTier,
        billingEmail=request.billingEmail,
        primaryContact={
            "name": request.primaryContactName,
            "email": request.primaryContactEmail,
            "phone": request.primaryContactPhone,
        },
        limits=limits,
        usage={"currentUsers": 0, "currentEngagements": 0, "currentStorageGB": 0, "currentClients": 0},
        billing=calculate_billing_info(customer_id, request.subscriptionTier),
        createdAt=datetime.utcnow().isoformat(),
        lastActivityAt=datetime.utcnow().isoformat(),
        onboardingCompleted=False,
    )

    return customer


@router.patch("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: str, request: UpdateCustomerRequest):
    """
    Update customer details.

    Allows updating subscription, status, limits, etc.
    """
    # In production:
    # 1. Update tenant in database
    # 2. If subscription changed, update billing
    # 3. If limits changed, validate current usage
    # 4. Send notification email

    # Get current customer
    current = await get_customer(customer_id)

    # Apply updates
    if request.firmName:
        current.firmName = request.firmName
    if request.status:
        current.status = request.status
    if request.subscriptionTier:
        current.subscriptionTier = request.subscriptionTier
        # Update billing
        current.billing = calculate_billing_info(customer_id, request.subscriptionTier)
    if request.billingEmail:
        current.billingEmail = request.billingEmail
    if request.limits:
        # Validate limits don't go below current usage
        for key, value in request.limits.items():
            limit_key = f"max{key.capitalize()}" if not key.startswith("max") else key
            usage_key = f"current{key.replace('max', '').capitalize()}" if key.startswith("max") else f"current{key.capitalize()}"

            if usage_key in current.usage:
                if value < current.usage[usage_key]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Cannot set {key} limit below current usage ({current.usage[usage_key]})",
                    )

        current.limits.update(request.limits)

    return current


@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str):
    """
    Delete customer.

    Soft-deletes customer and cancels subscription.
    """
    # In production:
    # 1. Soft delete tenant
    # 2. Cancel billing subscription
    # 3. Notify users
    # 4. Archive data

    return {"status": "deleted", "message": "Customer deleted successfully"}


# ============================================================================
# USAGE & ANALYTICS ENDPOINTS
# ============================================================================


@router.get("/customers/{customer_id}/usage", response_model=UsageAnalyticsResponse)
async def get_customer_usage(
    customer_id: str,
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
):
    """
    Get detailed usage analytics for a customer.

    Returns usage breakdown for billing and monitoring.
    """
    start = startDate or (datetime.utcnow() - timedelta(days=30)).isoformat()
    end = endDate or datetime.utcnow().isoformat()

    usage = UsageAnalyticsResponse(
        customerId=customer_id,
        period={"start": start, "end": end},
        users={
            "activeUsers": 12,
            "logins": 347,
            "avgSessionDuration": 42,
            "byRole": {"firmAdmin": 2, "firmUser": 8, "client": 15},
        },
        engagements={
            "created": 8,
            "completed": 5,
            "inProgress": 3,
            "byType": {"audit": 3, "review": 4, "compilation": 1},
        },
        documents={
            "uploaded": 247,
            "totalSizeGB": 12.4,
            "aiExtractions": 189,
        },
        integrations={
            "connected": 3,
            "syncs": 94,
            "dataPointsSynced": 15847,
        },
        api={
            "totalCalls": 8475,
            "avgResponseTime": 127,
            "errors": 12,
        },
    )

    return usage


@router.get("/customers/{customer_id}/limits")
async def check_customer_limits(customer_id: str):
    """
    Check customer limit status.

    Returns whether customer is approaching or exceeding limits.
    """
    customer = await get_customer(customer_id)

    limit_checks = []

    for limit_type in ["Users", "Engagements", "StorageGB", "Clients"]:
        current_key = f"current{limit_type}"
        limit_key = f"max{limit_type}"

        current = customer.usage.get(current_key, 0)
        limit = customer.limits.get(limit_key, 0)

        percentage = (current / limit * 100) if limit > 0 else 0
        exceeded = current >= limit

        limit_checks.append(
            {
                "limitType": limit_type.lower(),
                "current": current,
                "limit": limit,
                "percentage": round(percentage, 1),
                "exceeded": exceeded,
                "canAdd": not exceeded,
            }
        )

    return {"customerId": customer_id, "limits": limit_checks}


# ============================================================================
# BILLING ENDPOINTS
# ============================================================================


@router.get("/billing/invoices")
async def list_invoices(
    customerId: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    pageSize: int = Query(25, ge=1, le=100),
):
    """
    List invoices.

    Supports filtering by customer and status.
    """
    # Mock invoices
    invoices = []
    for i in range(20):
        invoice = {
            "id": str(uuid4()),
            "customerId": str(uuid4()),
            "invoiceNumber": f"INV-{2024}-{1000 + i}",
            "amount": 799 if i % 2 == 0 else 1999,
            "status": ["paid", "pending", "paid", "overdue"][i % 4],
            "dueDate": (datetime.utcnow() + timedelta(days=15 - i)).isoformat(),
            "paidDate": (datetime.utcnow() - timedelta(days=i)).isoformat() if i % 4 == 0 else None,
        }
        invoices.append(invoice)

    # Apply filters
    if customerId:
        invoices = [inv for inv in invoices if inv["customerId"] == customerId]
    if status:
        invoices = [inv for inv in invoices if inv["status"] == status]

    # Pagination
    start = (page - 1) * pageSize
    end = start + pageSize
    return invoices[start:end]


@router.get("/subscription-plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans_endpoint():
    """
    Get all subscription plans.

    Returns available subscription tiers with pricing and limits.
    """
    return get_subscription_plans()


# ============================================================================
# SYSTEM MONITORING ENDPOINTS
# ============================================================================


@router.get("/system/alerts")
async def get_system_alerts():
    """
    Get system alerts.

    Returns alerts requiring admin attention.
    """
    alerts = [
        {
            "id": str(uuid4()),
            "severity": "warning",
            "category": "usage",
            "title": "Customer approaching limit",
            "message": "Smith & Associates CPA is at 90% of user limit",
            "customerId": str(uuid4()),
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "acknowledged": False,
            "actionRequired": True,
            "actionUrl": "/admin/customers/123",
        },
        {
            "id": str(uuid4()),
            "severity": "error",
            "category": "billing",
            "title": "Payment failed",
            "message": "Payment failed for Johnson Tax Services",
            "customerId": str(uuid4()),
            "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
            "acknowledged": False,
            "actionRequired": True,
            "actionUrl": "/admin/billing/invoices",
        },
        {
            "id": str(uuid4()),
            "severity": "info",
            "category": "system",
            "title": "New customer signup",
            "message": "Williams Accounting signed up for Professional plan",
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "acknowledged": True,
            "actionRequired": False,
        },
    ]

    return alerts


@router.get("/system/activity")
async def get_activity_log(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=200),
):
    """
    Get activity log.

    Returns recent admin and system activities.
    """
    activities = []
    categories = ["customer", "user", "billing", "system", "security"]
    actions = [
        "Customer created",
        "Customer updated",
        "Subscription changed",
        "Limits updated",
        "User invited",
        "Payment received",
        "Invoice generated",
        "Alert triggered",
    ]

    for i in range(100):
        activity = {
            "id": str(uuid4()),
            "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
            "customerId": str(uuid4()) if i % 3 == 0 else None,
            "userId": str(uuid4()) if i % 2 == 0 else None,
            "action": actions[i % len(actions)],
            "category": categories[i % len(categories)],
            "description": f"Action performed: {actions[i % len(actions)]}",
            "ipAddress": f"192.168.{i % 255}.{(i * 7) % 255}",
        }
        activities.append(activity)

    # Apply filter
    if category:
        activities = [a for a in activities if a["category"] == category]

    # Pagination
    start = (page - 1) * pageSize
    end = start + pageSize
    return activities[start:end]


@router.post("/export")
async def export_data(exportType: str, format: str = "csv"):
    """
    Export data.

    Generates export file for customers, invoices, usage, etc.
    """
    # In production:
    # 1. Generate export file in background
    # 2. Store in S3
    # 3. Send download link via email
    # 4. Return job ID for polling

    export_id = str(uuid4())

    return {
        "exportId": export_id,
        "type": exportType,
        "format": format,
        "status": "processing",
        "estimatedTime": "2-3 minutes",
        "downloadUrl": None,  # Will be available when complete
    }


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================


class UserListResponse(BaseModel):
    """User list item response"""
    id: str
    email: str
    firstName: Optional[str]
    lastName: Optional[str]
    role: str
    tenantId: Optional[str]
    tenantName: Optional[str]
    isActive: bool
    emailVerified: bool
    lastLoginAt: Optional[str]
    createdAt: str


class CreateUserRequest(BaseModel):
    """Create user request"""
    email: EmailStr
    firstName: str
    lastName: str
    role: str  # platform_admin, firm_admin, firm_user
    tenantId: Optional[str]  # Required for non-platform-admin roles
    password: Optional[str]  # If not provided, will send invitation
    cpaLicenseNumber: Optional[str]
    cpaLicenseState: Optional[str]
    professionalTitle: Optional[str]
    sendInvitation: bool = True


class UpdateUserRequest(BaseModel):
    """Update user request"""
    firstName: Optional[str]
    lastName: Optional[str]
    role: Optional[str]
    tenantId: Optional[str]
    isActive: Optional[bool]
    cpaLicenseNumber: Optional[str]
    cpaLicenseState: Optional[str]
    professionalTitle: Optional[str]


class UserDetailResponse(BaseModel):
    """Detailed user response"""
    id: str
    email: str
    firstName: Optional[str]
    lastName: Optional[str]
    phone: Optional[str]
    role: str
    tenantId: Optional[str]
    tenantName: Optional[str]
    isActive: bool
    emailVerified: bool
    emailVerifiedAt: Optional[str]
    twoFactorEnabled: bool
    lastLoginAt: Optional[str]
    lastLoginIp: Optional[str]
    failedLoginAttempts: int
    cpaLicenseNumber: Optional[str]
    cpaLicenseState: Optional[str]
    professionalTitle: Optional[str]
    createdAt: str
    updatedAt: Optional[str]
    createdBy: Optional[str]


@router.get("/tenants", response_model=List[dict])
async def list_tenants(
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
):
    """
    List all CPA firms (tenants).

    Returns paginated list of tenants for firm selection in user creation.
    """
    # Mock data for now - in production, query from database
    tenants = [
        {
            "id": str(uuid4()),
            "firmName": "Anderson & Partners CPA",
            "firmEin": "12-3456789",
            "status": "active",
            "subscriptionTier": "professional",
            "userCount": 8,
            "maxUsers": 20,
            "createdAt": "2024-01-15T10:00:00Z",
        },
        {
            "id": str(uuid4()),
            "firmName": "Smith Accounting Group",
            "firmEin": "98-7654321",
            "status": "active",
            "subscriptionTier": "starter",
            "userCount": 3,
            "maxUsers": 5,
            "createdAt": "2024-02-20T10:00:00Z",
        },
        {
            "id": str(uuid4()),
            "firmName": "Jones & Associates",
            "firmEin": "45-6789012",
            "status": "trial",
            "subscriptionTier": "trial",
            "userCount": 1,
            "maxUsers": 2,
            "createdAt": "2024-11-01T10:00:00Z",
        },
    ]

    # Filter by status
    if status:
        tenants = [t for t in tenants if t["status"] == status]

    # Search by name
    if search:
        tenants = [t for t in tenants if search.lower() in t["firmName"].lower()]

    # Pagination
    start = (page - 1) * pageSize
    end = start + pageSize

    return tenants[start:end]


@router.get("/users", response_model=List[UserListResponse])
async def list_users(
    tenantId: Optional[str] = None,
    role: Optional[str] = None,
    isActive: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
):
    """
    List all users across all tenants or filter by tenant.

    Platform admins can view all users.
    Allows filtering by tenant, role, active status, and search.
    """
    # Mock data for now - in production, query from database
    users = [
        UserListResponse(
            id=str(uuid4()),
            email="john.admin@auraaudit.ai",
            firstName="John",
            lastName="Admin",
            role="platform_admin",
            tenantId=None,
            tenantName=None,
            isActive=True,
            emailVerified=True,
            lastLoginAt="2024-11-12T08:30:00Z",
            createdAt="2024-01-01T00:00:00Z",
        ),
        UserListResponse(
            id=str(uuid4()),
            email="sarah.partner@andersoncp a.com",
            firstName="Sarah",
            lastName="Anderson",
            role="firm_admin",
            tenantId=str(uuid4()),
            tenantName="Anderson & Partners CPA",
            isActive=True,
            emailVerified=True,
            lastLoginAt="2024-11-12T09:15:00Z",
            createdAt="2024-01-15T10:00:00Z",
        ),
        UserListResponse(
            id=str(uuid4()),
            email="mike.manager@andersoncpa.com",
            firstName="Mike",
            lastName="Johnson",
            role="firm_user",
            tenantId=str(uuid4()),
            tenantName="Anderson & Partners CPA",
            isActive=True,
            emailVerified=True,
            lastLoginAt="2024-11-11T16:45:00Z",
            createdAt="2024-02-01T10:00:00Z",
        ),
    ]

    # Filter by tenant
    if tenantId:
        users = [u for u in users if u.tenantId == tenantId]

    # Filter by role
    if role:
        users = [u for u in users if u.role == role]

    # Filter by active status
    if isActive is not None:
        users = [u for u in users if u.isActive == isActive]

    # Search by name or email
    if search:
        search_lower = search.lower()
        users = [
            u for u in users
            if (u.email and search_lower in u.email.lower())
            or (u.firstName and search_lower in u.firstName.lower())
            or (u.lastName and search_lower in u.lastName.lower())
        ]

    # Pagination
    start = (page - 1) * pageSize
    end = start + pageSize

    return users[start:end]


@router.post("/users", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user and assign to a CPA firm.

    Platform admins can create users for any tenant.
    If password is not provided, sends an invitation email.
    """
    # Validate role and tenant assignment
    if request.role != "platform_admin" and not request.tenantId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenantId is required for non-platform-admin roles"
        )

    if request.role == "platform_admin" and request.tenantId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform admins cannot be assigned to a tenant"
        )

    # In production: Use PermissionService.create_user()
    # For now, return mock response
    user_id = str(uuid4())

    # Send invitation if requested
    if request.sendInvitation and not request.password:
        # In production: Send invitation email via PermissionService.invite_user()
        pass

    return UserDetailResponse(
        id=user_id,
        email=request.email,
        firstName=request.firstName,
        lastName=request.lastName,
        phone=None,
        role=request.role,
        tenantId=request.tenantId,
        tenantName="Anderson & Partners CPA" if request.tenantId else None,
        isActive=True,
        emailVerified=False,
        emailVerifiedAt=None,
        twoFactorEnabled=False,
        lastLoginAt=None,
        lastLoginIp=None,
        failedLoginAttempts=0,
        cpaLicenseNumber=request.cpaLicenseNumber,
        cpaLicenseState=request.cpaLicenseState,
        professionalTitle=request.professionalTitle,
        createdAt=datetime.utcnow().isoformat() + "Z",
        updatedAt=None,
        createdBy=None,
    )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(user_id: str):
    """
    Get detailed user information.

    Returns comprehensive user details including permissions and activity.
    """
    # Mock response - in production, query from database
    return UserDetailResponse(
        id=user_id,
        email="sarah.partner@andersoncpa.com",
        firstName="Sarah",
        lastName="Anderson",
        phone="+1-555-0123",
        role="firm_admin",
        tenantId=str(uuid4()),
        tenantName="Anderson & Partners CPA",
        isActive=True,
        emailVerified=True,
        emailVerifiedAt="2024-01-15T12:00:00Z",
        twoFactorEnabled=True,
        lastLoginAt="2024-11-12T09:15:00Z",
        lastLoginIp="192.168.1.100",
        failedLoginAttempts=0,
        cpaLicenseNumber="CPA-123456",
        cpaLicenseState="California",
        professionalTitle="Partner, CPA",
        createdAt="2024-01-15T10:00:00Z",
        updatedAt="2024-11-01T10:00:00Z",
        createdBy=str(uuid4()),
    )


@router.patch("/users/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update user information.

    Platform admins can update any user.
    Can update role, tenant assignment, and user details.
    """
    # In production: Query user from database and update
    # Validate role changes and tenant reassignments
    # Use PermissionService for role/tenant changes

    # Mock response
    return UserDetailResponse(
        id=user_id,
        email="sarah.partner@andersoncpa.com",
        firstName=request.firstName or "Sarah",
        lastName=request.lastName or "Anderson",
        phone="+1-555-0123",
        role=request.role or "firm_admin",
        tenantId=request.tenantId or str(uuid4()),
        tenantName="Anderson & Partners CPA",
        isActive=request.isActive if request.isActive is not None else True,
        emailVerified=True,
        emailVerifiedAt="2024-01-15T12:00:00Z",
        twoFactorEnabled=True,
        lastLoginAt="2024-11-12T09:15:00Z",
        lastLoginIp="192.168.1.100",
        failedLoginAttempts=0,
        cpaLicenseNumber=request.cpaLicenseNumber or "CPA-123456",
        cpaLicenseState=request.cpaLicenseState or "California",
        professionalTitle=request.professionalTitle or "Partner, CPA",
        createdAt="2024-01-15T10:00:00Z",
        updatedAt=datetime.utcnow().isoformat() + "Z",
        createdBy=str(uuid4()),
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate a user (soft delete).

    Sets is_active to False instead of hard deleting.
    User can be reactivated later if needed.
    """
    # In production: Update user.is_active = False
    # Use PermissionService with audit logging
    return None
