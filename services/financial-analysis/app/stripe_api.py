"""
Stripe API Endpoints

FastAPI routes for Stripe payment processing including:
- Subscription management
- Add-on purchases
- Payment methods
- Webhook handling
"""

import os
from typing import List, Optional

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_async_session
from .permission_service import PermissionService
from .permissions_models import Tenant, User
from .stripe_service import StripeService

router = APIRouter(prefix="/api/stripe", tags=["Stripe"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class CreateSubscriptionRequest(BaseModel):
    """Create subscription request"""

    customerId: str
    subscriptionTier: str
    paymentMethodId: str


class ChangeSubscriptionRequest(BaseModel):
    """Change subscription request"""

    customerId: str
    newSubscriptionTier: str


class PurchaseAddonRequest(BaseModel):
    """Purchase add-on request"""

    customerId: str
    addonType: str
    quantity: int = 1


class AddPaymentMethodRequest(BaseModel):
    """Add payment method request"""

    customerId: str
    paymentMethodId: str


class SubscriptionResponse(BaseModel):
    """Subscription response"""

    subscriptionId: str
    status: str
    clientSecret: Optional[str] = None


class AddonResponse(BaseModel):
    """Add-on purchase response"""

    invoiceId: str
    status: str
    amount: float
    addonType: str
    quantity: int


class PaymentMethodResponse(BaseModel):
    """Payment method response"""

    id: str
    type: str
    card: Optional[dict]


# ============================================================================
# SUBSCRIPTION ENDPOINTS
# ============================================================================


@router.post("/subscriptions/create", response_model=SubscriptionResponse)
async def create_subscription(
    request: CreateSubscriptionRequest, session: AsyncSession = Depends(get_async_session)
):
    """
    Create a Stripe subscription for a customer.

    This is called when a new customer signs up or upgrades from trial.
    """
    # Get tenant
    tenant = await session.get(Tenant, request.customerId)
    if not tenant:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create Stripe service
    stripe_service = StripeService(session)

    # Create subscription
    try:
        subscription = await stripe_service.create_subscription(
            tenant=tenant,
            subscription_tier=request.subscriptionTier,
            billing_email=tenant.primary_contact_email or tenant.firm_name,
            payment_method_id=request.paymentMethodId,
        )

        return SubscriptionResponse(
            subscriptionId=subscription["subscription_id"],
            status=subscription["status"],
            clientSecret=subscription.get("client_secret"),
        )

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscriptions/change", response_model=SubscriptionResponse)
async def change_subscription(
    request: ChangeSubscriptionRequest, session: AsyncSession = Depends(get_async_session)
):
    """
    Change subscription tier (upgrade/downgrade).

    Automatically prorates the change.
    """
    # Get tenant
    tenant = await session.get(Tenant, request.customerId)
    if not tenant:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create Stripe service
    stripe_service = StripeService(session)

    # Change subscription
    try:
        subscription = await stripe_service.change_subscription(
            tenant=tenant, new_subscription_tier=request.newSubscriptionTier
        )

        return SubscriptionResponse(
            subscriptionId=subscription["subscription_id"], status=subscription["status"]
        )

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscriptions/cancel")
async def cancel_subscription(
    customerId: str, immediate: bool = False, session: AsyncSession = Depends(get_async_session)
):
    """
    Cancel subscription.

    Args:
        customerId: Customer ID
        immediate: If True, cancel now; if False, cancel at period end
    """
    # Get tenant
    tenant = await session.get(Tenant, customerId)
    if not tenant:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create Stripe service
    stripe_service = StripeService(session)

    # Cancel subscription
    try:
        result = await stripe_service.cancel_subscription(tenant=tenant, immediate=immediate)
        return result

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# ADD-ON PURCHASE ENDPOINTS
# ============================================================================


@router.post("/addons/purchase", response_model=AddonResponse)
async def purchase_addon(
    request: PurchaseAddonRequest, session: AsyncSession = Depends(get_async_session)
):
    """
    Purchase an add-on (extra users, engagements, storage).

    The add-on is automatically activated upon successful payment.
    """
    # Get tenant
    tenant = await session.get(Tenant, request.customerId)
    if not tenant:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create Stripe service
    stripe_service = StripeService(session)

    # Purchase add-on
    try:
        result = await stripe_service.purchase_addon(
            tenant=tenant, addon_type=request.addonType, quantity=request.quantity
        )

        return AddonResponse(
            invoiceId=result["invoice_id"],
            status=result["status"],
            amount=result["amount"],
            addonType=result["addon_type"],
            quantity=result["quantity"],
        )

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/addons/available")
async def get_available_addons():
    """
    Get available add-ons for purchase.

    Returns pricing and details for all add-ons.
    """
    return {
        "addons": [
            {
                "id": "extra_users_10",
                "name": "10 Additional Users",
                "description": "Add 10 more users to your account",
                "price": 100,
                "type": "users",
            },
            {
                "id": "extra_engagements_25",
                "name": "25 Additional Engagements",
                "description": "Increase your monthly engagement limit by 25",
                "price": 150,
                "type": "engagements",
            },
            {
                "id": "extra_storage_100gb",
                "name": "100 GB Additional Storage",
                "description": "Add 100 GB to your storage limit",
                "price": 50,
                "type": "storage",
            },
        ]
    }


# ============================================================================
# PAYMENT METHOD ENDPOINTS
# ============================================================================


@router.post("/payment-methods/add", response_model=PaymentMethodResponse)
async def add_payment_method(
    request: AddPaymentMethodRequest, session: AsyncSession = Depends(get_async_session)
):
    """
    Add a payment method to customer.

    Sets it as the default payment method.
    """
    # Get tenant
    tenant = await session.get(Tenant, request.customerId)
    if not tenant:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create Stripe service
    stripe_service = StripeService(session)

    # Add payment method
    try:
        payment_method = await stripe_service.add_payment_method(
            tenant=tenant, payment_method_id=request.paymentMethodId
        )

        return PaymentMethodResponse(
            id=payment_method["id"], type=payment_method["type"], card=payment_method.get("card")
        )

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payment-methods/{customer_id}", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    customer_id: str, session: AsyncSession = Depends(get_async_session)
):
    """
    Get all payment methods for customer.
    """
    # Get tenant
    tenant = await session.get(Tenant, customer_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create Stripe service
    stripe_service = StripeService(session)

    # Get payment methods
    payment_methods = await stripe_service.get_payment_methods(tenant=tenant)

    return [
        PaymentMethodResponse(id=pm["id"], type=pm["type"], card=pm.get("card"))
        for pm in payment_methods
    ]


# ============================================================================
# INVOICE ENDPOINTS
# ============================================================================


@router.get("/invoices/{customer_id}")
async def get_invoices(customer_id: str, session: AsyncSession = Depends(get_async_session)):
    """
    Get invoices for customer.
    """
    # Get tenant
    tenant = await session.get(Tenant, customer_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create Stripe service
    stripe_service = StripeService(session)

    # Get invoices
    invoices = await stripe_service.get_invoices(tenant=tenant)

    return {"invoices": invoices}


# ============================================================================
# WEBHOOK ENDPOINT
# ============================================================================


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Handle Stripe webhook events.

    This endpoint receives events from Stripe including:
    - invoice.payment_succeeded
    - invoice.payment_failed
    - customer.subscription.updated
    - customer.subscription.deleted

    IMPORTANT: This endpoint must be publicly accessible and
    configured in your Stripe Dashboard under Webhooks.
    """
    # Get webhook secret from environment
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")

    # Get raw body
    payload = await request.body()

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, webhook_secret)
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Create Stripe service
    stripe_service = StripeService(session)

    # Handle event
    try:
        await stripe_service.handle_webhook_event(event)
        return {"status": "success"}
    except Exception as e:
        # Log error but return success to Stripe to avoid retries
        print(f"Error handling webhook: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================


@router.post("/admin/check-overdue")
async def check_overdue_invoices(session: AsyncSession = Depends(get_async_session)):
    """
    Check for overdue invoices and suspend customers.

    This endpoint should be called daily via cron job.
    Suspends customers with invoices 15+ days overdue.
    """
    # Create Stripe service
    stripe_service = StripeService(session)

    # Check overdue invoices
    suspended = await stripe_service.check_overdue_invoices()

    return {
        "suspended_count": len(suspended),
        "suspended_tenants": suspended,
    }


@router.get("/admin/subscription-stats")
async def get_subscription_stats(session: AsyncSession = Depends(get_async_session)):
    """
    Get subscription statistics for admin dashboard.
    """
    # This would query the database for subscription stats
    # For now, return mock data
    return {
        "total_subscriptions": 48,
        "active": 42,
        "trialing": 6,
        "past_due": 2,
        "canceled": 3,
        "mrr": 47850,
        "churn_rate": 2.1,
    }
