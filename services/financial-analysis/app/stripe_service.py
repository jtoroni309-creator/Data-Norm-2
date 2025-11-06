"""
Stripe Integration Service

Handles all Stripe payment processing including:
- Subscription management
- One-time payments for add-ons
- Webhook event processing
- Automatic feature activation
- Automatic suspension for late payments
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .permissions_models import Tenant, TenantStatus

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")


class StripeService:
    """Service for Stripe payment processing"""

    # Stripe Price IDs (set these in your Stripe dashboard)
    SUBSCRIPTION_PRICES = {
        "trial": None,  # No charge for trial
        "starter": "price_starter_monthly",  # Replace with actual Stripe price ID
        "professional": "price_professional_monthly",
        "enterprise": "price_enterprise_monthly",
        "custom": None,  # Custom pricing handled separately
    }

    # Add-on prices
    ADDON_PRICES = {
        "extra_users_10": {
            "price_id": "price_extra_users_10",
            "name": "10 Additional Users",
            "amount": 100,  # $100
        },
        "extra_engagements_25": {
            "price_id": "price_extra_engagements_25",
            "name": "25 Additional Engagements",
            "amount": 150,  # $150
        },
        "extra_storage_100gb": {
            "price_id": "price_extra_storage_100gb",
            "name": "100 GB Additional Storage",
            "amount": 50,  # $50
        },
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========================================================================
    # CUSTOMER MANAGEMENT
    # ========================================================================

    async def create_stripe_customer(
        self, tenant: Tenant, billing_email: str, payment_method_id: Optional[str] = None
    ) -> str:
        """
        Create a Stripe customer for a tenant.

        Args:
            tenant: Tenant object
            billing_email: Billing email address
            payment_method_id: Optional payment method ID

        Returns:
            Stripe customer ID
        """
        # Create Stripe customer
        customer = stripe.Customer.create(
            email=billing_email,
            name=tenant.firm_name,
            metadata={
                "tenant_id": str(tenant.id),
                "firm_ein": tenant.firm_ein or "",
            },
            payment_method=payment_method_id,
            invoice_settings={
                "default_payment_method": payment_method_id,
            }
            if payment_method_id
            else None,
        )

        # Store Stripe customer ID in tenant settings
        if not tenant.settings:
            tenant.settings = {}
        tenant.settings["stripe_customer_id"] = customer.id

        await self.session.commit()

        return customer.id

    async def get_or_create_stripe_customer(self, tenant: Tenant, billing_email: str) -> str:
        """
        Get existing Stripe customer or create new one.

        Args:
            tenant: Tenant object
            billing_email: Billing email address

        Returns:
            Stripe customer ID
        """
        # Check if customer already exists
        if tenant.settings and "stripe_customer_id" in tenant.settings:
            return tenant.settings["stripe_customer_id"]

        # Create new customer
        return await self.create_stripe_customer(tenant, billing_email)

    # ========================================================================
    # SUBSCRIPTION MANAGEMENT
    # ========================================================================

    async def create_subscription(
        self,
        tenant: Tenant,
        subscription_tier: str,
        billing_email: str,
        payment_method_id: str,
    ) -> Dict[str, Any]:
        """
        Create a Stripe subscription for a tenant.

        Args:
            tenant: Tenant object
            subscription_tier: Subscription tier (starter, professional, enterprise)
            billing_email: Billing email
            payment_method_id: Stripe payment method ID

        Returns:
            Subscription details
        """
        # Get or create Stripe customer
        customer_id = await self.get_or_create_stripe_customer(tenant, billing_email)

        # Attach payment method to customer
        stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

        # Set as default payment method
        stripe.Customer.modify(
            customer_id,
            invoice_settings={"default_payment_method": payment_method_id},
        )

        # Get price ID for subscription tier
        price_id = self.SUBSCRIPTION_PRICES.get(subscription_tier)
        if not price_id:
            raise ValueError(f"Invalid subscription tier: {subscription_tier}")

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            metadata={
                "tenant_id": str(tenant.id),
                "subscription_tier": subscription_tier,
            },
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
        )

        # Store subscription ID in tenant settings
        if not tenant.settings:
            tenant.settings = {}
        tenant.settings["stripe_subscription_id"] = subscription.id

        # Update tenant status
        tenant.status = TenantStatus.ACTIVE
        tenant.subscription_tier = subscription_tier

        await self.session.commit()

        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret,
            "status": subscription.status,
        }

    async def change_subscription(
        self, tenant: Tenant, new_subscription_tier: str
    ) -> Dict[str, Any]:
        """
        Change subscription tier (upgrade/downgrade).

        Args:
            tenant: Tenant object
            new_subscription_tier: New subscription tier

        Returns:
            Updated subscription details
        """
        # Get Stripe subscription ID
        if not tenant.settings or "stripe_subscription_id" not in tenant.settings:
            raise ValueError("No active subscription found")

        subscription_id = tenant.settings["stripe_subscription_id"]

        # Get current subscription
        subscription = stripe.Subscription.retrieve(subscription_id)

        # Get new price ID
        new_price_id = self.SUBSCRIPTION_PRICES.get(new_subscription_tier)
        if not new_price_id:
            raise ValueError(f"Invalid subscription tier: {new_subscription_tier}")

        # Update subscription
        updated_subscription = stripe.Subscription.modify(
            subscription_id,
            items=[
                {
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price_id,
                }
            ],
            proration_behavior="create_prorations",  # Prorate the change
            metadata={"subscription_tier": new_subscription_tier},
        )

        # Update tenant
        tenant.subscription_tier = new_subscription_tier
        await self.session.commit()

        return {
            "subscription_id": updated_subscription.id,
            "status": updated_subscription.status,
            "tier": new_subscription_tier,
        }

    async def cancel_subscription(self, tenant: Tenant, immediate: bool = False) -> Dict[str, Any]:
        """
        Cancel subscription.

        Args:
            tenant: Tenant object
            immediate: If True, cancel immediately; if False, cancel at period end

        Returns:
            Cancellation details
        """
        # Get Stripe subscription ID
        if not tenant.settings or "stripe_subscription_id" not in tenant.settings:
            raise ValueError("No active subscription found")

        subscription_id = tenant.settings["stripe_subscription_id"]

        # Cancel subscription
        if immediate:
            subscription = stripe.Subscription.delete(subscription_id)
            tenant.status = TenantStatus.CANCELLED
        else:
            subscription = stripe.Subscription.modify(
                subscription_id, cancel_at_period_end=True
            )

        await self.session.commit()

        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "cancel_at": subscription.cancel_at,
        }

    # ========================================================================
    # ADD-ON PURCHASES
    # ========================================================================

    async def purchase_addon(
        self, tenant: Tenant, addon_type: str, quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Purchase an add-on (extra users, engagements, storage).

        Automatically activates the add-on upon successful payment.

        Args:
            tenant: Tenant object
            addon_type: Type of add-on (extra_users_10, extra_engagements_25, etc.)
            quantity: Quantity to purchase

        Returns:
            Payment details
        """
        # Get Stripe customer ID
        if not tenant.settings or "stripe_customer_id" not in tenant.settings:
            raise ValueError("No Stripe customer found")

        customer_id = tenant.settings["stripe_customer_id"]

        # Get add-on details
        addon = self.ADDON_PRICES.get(addon_type)
        if not addon:
            raise ValueError(f"Invalid add-on type: {addon_type}")

        # Create invoice item
        invoice_item = stripe.InvoiceItem.create(
            customer=customer_id,
            price=addon["price_id"],
            quantity=quantity,
            metadata={
                "tenant_id": str(tenant.id),
                "addon_type": addon_type,
                "quantity": quantity,
            },
        )

        # Create and finalize invoice
        invoice = stripe.Invoice.create(
            customer=customer_id,
            auto_advance=True,  # Auto-finalize invoice
            metadata={
                "tenant_id": str(tenant.id),
                "addon_type": addon_type,
            },
        )

        # Finalize and pay invoice
        finalized_invoice = stripe.Invoice.finalize_invoice(invoice.id)

        # Try to pay invoice
        paid_invoice = stripe.Invoice.pay(finalized_invoice.id)

        # If payment successful, activate add-on
        if paid_invoice.status == "paid":
            await self._activate_addon(tenant, addon_type, quantity)

        return {
            "invoice_id": paid_invoice.id,
            "status": paid_invoice.status,
            "amount": paid_invoice.amount_due / 100,  # Convert from cents
            "addon_type": addon_type,
            "quantity": quantity,
        }

    async def _activate_addon(self, tenant: Tenant, addon_type: str, quantity: int) -> None:
        """
        Activate purchased add-on by increasing limits.

        Args:
            tenant: Tenant object
            addon_type: Type of add-on
            quantity: Quantity purchased
        """
        # Increase limits based on add-on type
        if addon_type == "extra_users_10":
            tenant.max_users += 10 * quantity
        elif addon_type == "extra_engagements_25":
            tenant.max_engagements += 25 * quantity
        elif addon_type == "extra_storage_100gb":
            tenant.max_storage_gb += 100 * quantity

        # Store add-on purchase in settings
        if not tenant.settings:
            tenant.settings = {}
        if "addons_purchased" not in tenant.settings:
            tenant.settings["addons_purchased"] = []

        tenant.settings["addons_purchased"].append(
            {
                "type": addon_type,
                "quantity": quantity,
                "purchased_at": datetime.utcnow().isoformat(),
            }
        )

        await self.session.commit()

    # ========================================================================
    # WEBHOOK HANDLERS
    # ========================================================================

    async def handle_webhook_event(self, event: Dict[str, Any]) -> None:
        """
        Handle Stripe webhook events.

        Args:
            event: Stripe webhook event
        """
        event_type = event["type"]

        # Payment succeeded
        if event_type == "invoice.payment_succeeded":
            await self._handle_payment_succeeded(event["data"]["object"])

        # Payment failed
        elif event_type == "invoice.payment_failed":
            await self._handle_payment_failed(event["data"]["object"])

        # Invoice overdue (past_due)
        elif event_type == "invoice.payment_action_required":
            await self._handle_payment_action_required(event["data"]["object"])

        # Subscription updated
        elif event_type == "customer.subscription.updated":
            await self._handle_subscription_updated(event["data"]["object"])

        # Subscription deleted
        elif event_type == "customer.subscription.deleted":
            await self._handle_subscription_deleted(event["data"]["object"])

    async def _handle_payment_succeeded(self, invoice: Dict[str, Any]) -> None:
        """
        Handle successful payment.

        Activates features if customer was suspended.
        """
        # Get tenant from metadata
        tenant_id = invoice.get("metadata", {}).get("tenant_id")
        if not tenant_id:
            return

        # Get tenant
        result = await self.session.execute(select(Tenant).where(Tenant.id == UUID(tenant_id)))
        tenant = result.scalar_one_or_none()

        if not tenant:
            return

        # If customer was suspended, reactivate
        if tenant.status == TenantStatus.SUSPENDED:
            tenant.status = TenantStatus.ACTIVE

        # If this was an add-on purchase, activate it
        addon_type = invoice.get("metadata", {}).get("addon_type")
        if addon_type:
            quantity = int(invoice.get("metadata", {}).get("quantity", 1))
            await self._activate_addon(tenant, addon_type, quantity)

        await self.session.commit()

    async def _handle_payment_failed(self, invoice: Dict[str, Any]) -> None:
        """
        Handle failed payment.

        Sends notification but doesn't suspend immediately.
        """
        # Get tenant from metadata
        tenant_id = invoice.get("metadata", {}).get("tenant_id")
        if not tenant_id:
            return

        # TODO: Send notification email to customer and admin
        # This is handled in webhook but doesn't suspend yet
        print(f"Payment failed for tenant {tenant_id}, invoice {invoice['id']}")

    async def _handle_payment_action_required(self, invoice: Dict[str, Any]) -> None:
        """
        Handle payment that requires action (3D Secure, etc.).

        Sends notification to customer.
        """
        # Get tenant from metadata
        tenant_id = invoice.get("metadata", {}).get("tenant_id")
        if not tenant_id:
            return

        # TODO: Send notification email requesting payment action
        print(f"Payment action required for tenant {tenant_id}, invoice {invoice['id']}")

    async def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> None:
        """
        Handle subscription update.

        Updates tenant subscription tier if changed.
        """
        # Get tenant from metadata
        tenant_id = subscription.get("metadata", {}).get("tenant_id")
        if not tenant_id:
            return

        # Get tenant
        result = await self.session.execute(select(Tenant).where(Tenant.id == UUID(tenant_id)))
        tenant = result.scalar_one_or_none()

        if not tenant:
            return

        # Update subscription tier if changed
        new_tier = subscription.get("metadata", {}).get("subscription_tier")
        if new_tier and new_tier != tenant.subscription_tier:
            tenant.subscription_tier = new_tier
            await self.session.commit()

    async def _handle_subscription_deleted(self, subscription: Dict[str, Any]) -> None:
        """
        Handle subscription deletion.

        Suspends tenant access.
        """
        # Get tenant from metadata
        tenant_id = subscription.get("metadata", {}).get("tenant_id")
        if not tenant_id:
            return

        # Get tenant
        result = await self.session.execute(select(Tenant).where(Tenant.id == UUID(tenant_id)))
        tenant = result.scalar_one_or_none()

        if not tenant:
            return

        # Suspend tenant
        tenant.status = TenantStatus.CANCELLED

        await self.session.commit()

    # ========================================================================
    # LATE PAYMENT SUSPENSION
    # ========================================================================

    async def check_overdue_invoices(self) -> List[Dict[str, Any]]:
        """
        Check for invoices that are 15+ days overdue and suspend access.

        This should be run daily via cron job.

        Returns:
            List of suspended tenants
        """
        suspended_tenants = []

        # Get all active tenants
        result = await self.session.execute(
            select(Tenant).where(Tenant.status == TenantStatus.ACTIVE)
        )
        tenants = result.scalars().all()

        for tenant in tenants:
            # Get Stripe customer ID
            if not tenant.settings or "stripe_customer_id" not in tenant.settings:
                continue

            customer_id = tenant.settings["stripe_customer_id"]

            # Get overdue invoices
            invoices = stripe.Invoice.list(
                customer=customer_id, status="open", limit=100  # Open = unpaid
            )

            # Check each invoice
            for invoice in invoices.data:
                # Calculate days overdue
                due_date = datetime.fromtimestamp(invoice.due_date) if invoice.due_date else None
                if not due_date:
                    continue

                days_overdue = (datetime.utcnow() - due_date).days

                # If 15+ days overdue, suspend
                if days_overdue >= 15:
                    tenant.status = TenantStatus.SUSPENDED

                    # Store suspension info in settings
                    if not tenant.settings:
                        tenant.settings = {}
                    tenant.settings["suspended_at"] = datetime.utcnow().isoformat()
                    tenant.settings["suspension_reason"] = "payment_overdue"
                    tenant.settings["overdue_invoice_id"] = invoice.id
                    tenant.settings["days_overdue"] = days_overdue

                    suspended_tenants.append(
                        {
                            "tenant_id": str(tenant.id),
                            "firm_name": tenant.firm_name,
                            "invoice_id": invoice.id,
                            "amount_due": invoice.amount_due / 100,
                            "days_overdue": days_overdue,
                        }
                    )

                    break  # Only need to find one overdue invoice

        # Commit all suspensions
        await self.session.commit()

        return suspended_tenants

    # ========================================================================
    # PAYMENT METHODS
    # ========================================================================

    async def add_payment_method(
        self, tenant: Tenant, payment_method_id: str
    ) -> Dict[str, Any]:
        """
        Add a payment method to customer.

        Args:
            tenant: Tenant object
            payment_method_id: Stripe payment method ID

        Returns:
            Payment method details
        """
        # Get Stripe customer ID
        if not tenant.settings or "stripe_customer_id" not in tenant.settings:
            raise ValueError("No Stripe customer found")

        customer_id = tenant.settings["stripe_customer_id"]

        # Attach payment method
        payment_method = stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

        # Set as default
        stripe.Customer.modify(
            customer_id, invoice_settings={"default_payment_method": payment_method_id}
        )

        return {
            "id": payment_method.id,
            "type": payment_method.type,
            "card": {
                "brand": payment_method.card.brand,
                "last4": payment_method.card.last4,
                "exp_month": payment_method.card.exp_month,
                "exp_year": payment_method.card.exp_year,
            }
            if payment_method.type == "card"
            else None,
        }

    async def get_payment_methods(self, tenant: Tenant) -> List[Dict[str, Any]]:
        """
        Get all payment methods for customer.

        Args:
            tenant: Tenant object

        Returns:
            List of payment methods
        """
        # Get Stripe customer ID
        if not tenant.settings or "stripe_customer_id" not in tenant.settings:
            return []

        customer_id = tenant.settings["stripe_customer_id"]

        # Get payment methods
        payment_methods = stripe.PaymentMethod.list(customer=customer_id, type="card")

        return [
            {
                "id": pm.id,
                "type": pm.type,
                "card": {
                    "brand": pm.card.brand,
                    "last4": pm.card.last4,
                    "exp_month": pm.card.exp_month,
                    "exp_year": pm.card.exp_year,
                },
            }
            for pm in payment_methods.data
        ]

    # ========================================================================
    # INVOICE MANAGEMENT
    # ========================================================================

    async def get_invoices(self, tenant: Tenant, limit: int = 12) -> List[Dict[str, Any]]:
        """
        Get invoices for customer.

        Args:
            tenant: Tenant object
            limit: Number of invoices to retrieve

        Returns:
            List of invoices
        """
        # Get Stripe customer ID
        if not tenant.settings or "stripe_customer_id" not in tenant.settings:
            return []

        customer_id = tenant.settings["stripe_customer_id"]

        # Get invoices
        invoices = stripe.Invoice.list(customer=customer_id, limit=limit)

        return [
            {
                "id": inv.id,
                "number": inv.number,
                "amount_due": inv.amount_due / 100,
                "amount_paid": inv.amount_paid / 100,
                "status": inv.status,
                "due_date": datetime.fromtimestamp(inv.due_date).isoformat()
                if inv.due_date
                else None,
                "paid_at": datetime.fromtimestamp(inv.status_transitions.paid_at).isoformat()
                if inv.status_transitions.paid_at
                else None,
                "invoice_pdf": inv.invoice_pdf,
                "hosted_invoice_url": inv.hosted_invoice_url,
            }
            for inv in invoices.data
        ]
