

# Stripe Integration Guide

## 🎯 Overview

Complete Stripe payment integration with automatic feature activation and late payment suspension.

---

## ✨ Key Features

### 1. Automatic Feature Activation
When a customer purchases an add-on or upgrades their plan, features are **automatically activated** upon successful payment:

- **Extra Users**: Immediately increases `max_users` limit
- **Extra Engagements**: Immediately increases `max_engagements` limit
- **Extra Storage**: Immediately increases `max_storage_gb` limit
- **Plan Upgrades**: Immediately updates subscription tier and limits

**How it works:**
1. Customer clicks "Purchase" in admin portal
2. Payment processed through Stripe
3. Webhook receives `invoice.payment_succeeded` event
4. Backend automatically activates the feature
5. Customer can use new features immediately

### 2. Automatic Suspension for Late Payments

Customers are **automatically suspended** if invoices are 15+ days overdue:

**Timeline:**
- **Day 0**: Invoice due date
- **Day 1-14**: Invoice overdue, customer still has access
- **Day 15**: **AUTOMATIC SUSPENSION** - customer access turned off
- Customer must pay invoice to restore access
- Upon payment, access automatically restored

**Daily Cron Job:**
```bash
# Run this daily at midnight
0 0 * * * curl -X POST https://api.aura-audit.com/api/stripe/admin/check-overdue
```

The cron job:
1. Checks all active customers
2. Finds invoices 15+ days overdue
3. Suspends customer access
4. Sends notification to customer and admin
5. Logs suspension in audit trail

---

## 💳 Subscription Plans

### Trial Plan (Free)
- $0/month
- 2 users, 5 engagements, 10 GB
- 30-day trial
- No payment required

### Starter Plan
- $299/month
- 5 users, 25 engagements, 100 GB
- Stripe Price ID: `price_starter_monthly`

### Professional Plan ⭐
- $799/month
- 20 users, 100 engagements, 500 GB
- Stripe Price ID: `price_professional_monthly`

### Enterprise Plan
- $1,999/month
- 100 users, 500 engagements, 2 TB
- Stripe Price ID: `price_enterprise_monthly`

### Custom Plan
- Contact sales
- Custom pricing and limits

---

## 🛒 Add-On Purchases

### Available Add-Ons:

**1. Extra Users (10 pack)**
- Price: $100 one-time
- Adds 10 users to account permanently
- Stripe Price ID: `price_extra_users_10`
- Auto-activates on payment

**2. Extra Engagements (25 pack)**
- Price: $150 one-time
- Adds 25 to monthly engagement limit permanently
- Stripe Price ID: `price_extra_engagements_25`
- Auto-activates on payment

**3. Extra Storage (100 GB)**
- Price: $50 one-time
- Adds 100 GB to storage limit permanently
- Stripe Price ID: `price_extra_storage_100gb`
- Auto-activates on payment

**Purchase Flow:**
```
1. Admin clicks "Purchase Add-on"
2. Selects add-on type and quantity
3. Stripe creates invoice
4. Payment processed
5. Webhook receives payment_succeeded
6. Backend increases limits automatically
7. Customer can use extra capacity immediately
```

---

## 🔄 Webhook Events

### Configured Webhooks:

**1. invoice.payment_succeeded**
- **Trigger**: Payment successful
- **Action**:
  - Reactivate customer if suspended
  - Activate purchased add-ons
  - Update subscription status

**2. invoice.payment_failed**
- **Trigger**: Payment failed
- **Action**:
  - Send notification to customer
  - Send alert to admin
  - Start retry attempts

**3. customer.subscription.updated**
- **Trigger**: Subscription changed
- **Action**:
  - Update subscription tier
  - Update limits to match new plan

**4. customer.subscription.deleted**
- **Trigger**: Subscription cancelled
- **Action**:
  - Suspend customer access
  - Update status to "cancelled"

### Webhook Setup:

1. Go to Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Enter URL: `https://api.aura-audit.com/api/stripe/webhook`
4. Select events:
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `invoice.payment_action_required`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy webhook secret
6. Add to environment: `STRIPE_WEBHOOK_SECRET=whsec_...`

---

## 📋 Setup Instructions

### 1. Create Stripe Products

In Stripe Dashboard → Products, create:

**Starter Plan:**
- Name: "Starter Plan"
- Pricing: $299/month recurring
- Copy Price ID → `price_starter_monthly`

**Professional Plan:**
- Name: "Professional Plan"
- Pricing: $799/month recurring
- Copy Price ID → `price_professional_monthly`

**Enterprise Plan:**
- Name: "Enterprise Plan"
- Pricing: $1,999/month recurring
- Copy Price ID → `price_enterprise_monthly`

**Extra Users (10 pack):**
- Name: "10 Additional Users"
- Pricing: $100 one-time
- Copy Price ID → `price_extra_users_10`

**Extra Engagements (25 pack):**
- Name: "25 Additional Engagements"
- Pricing: $150 one-time
- Copy Price ID → `price_extra_engagements_25`

**Extra Storage (100 GB):**
- Name: "100 GB Additional Storage"
- Pricing: $50 one-time
- Copy Price ID → `price_extra_storage_100gb`

### 2. Update Price IDs

In `stripe_service.py`, update:

```python
SUBSCRIPTION_PRICES = {
    "starter": "price_1234567890",  # Your actual price ID
    "professional": "price_0987654321",
    "enterprise": "price_1122334455",
}

ADDON_PRICES = {
    "extra_users_10": {
        "price_id": "price_2233445566",
        "name": "10 Additional Users",
        "amount": 100,
    },
    # ... etc
}
```

### 3. Set Environment Variables

```bash
# Stripe API Keys
STRIPE_SECRET_KEY=sk_live_...  # Production secret key
STRIPE_PUBLISHABLE_KEY=pk_live_...  # Production publishable key

# Webhook Secret
STRIPE_WEBHOOK_SECRET=whsec_...  # From webhook endpoint
```

### 4. Configure Webhook Endpoint

Set up webhook as described above in "Webhook Setup" section.

### 5. Set Up Daily Cron Job

Add to crontab:
```bash
# Check for overdue invoices daily at midnight
0 0 * * * curl -X POST https://api.aura-audit.com/api/stripe/admin/check-overdue
```

Or use a service like:
- **AWS CloudWatch Events** (trigger Lambda)
- **Google Cloud Scheduler** (trigger Cloud Function)
- **Heroku Scheduler** (run task)

---

## 🎨 UI Components

### Purchase Add-On Modal

```
┌────────────────────────────────────────────────────────────┐
│ Purchase Add-On                                 [✕] Close   │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Select Add-On                                               │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ (•) 10 Additional Users               $100         │    │
│  │     Add 10 more users to your account              │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ ( ) 25 Additional Engagements         $150         │    │
│  │     Increase monthly engagement limit by 25        │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ ( ) 100 GB Additional Storage         $50          │    │
│  │     Add 100 GB to your storage capacity            │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Quantity: [1 ▼]                                            │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Order Summary                                       │    │
│  │                                                      │    │
│  │ Item:      10 Additional Users                      │    │
│  │ Quantity:  1                                        │    │
│  │ Price:     $100.00                                  │    │
│  │                                                      │    │
│  │ Total:     $100.00                                  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Payment Method                                              │
│  Visa ****1234 (expires 12/2025)              [Change]     │
│                                                              │
│  💡 Features will be activated immediately upon payment      │
│                                                              │
│                                [Cancel]   [Purchase $100]   │
└────────────────────────────────────────────────────────────┘
```

### Payment Failed Alert

```
┌────────────────────────────────────────────────────────────┐
│ ❌ Payment Failed - Smith & Associates CPA                  │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Invoice: INV-2024-1045                                     │
│  Amount: $799.00                                             │
│  Reason: Insufficient funds                                 │
│  Failed: 2 hours ago                                        │
│                                                              │
│  ⚠️ Customer still has access (grace period)                │
│  ⏰ Access will be suspended in 13 days if unpaid           │
│                                                              │
│  Actions:                                                    │
│  [Retry Payment] [Update Payment Method] [Contact Customer] │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### Suspended Customer Alert

```
┌────────────────────────────────────────────────────────────┐
│ 🔴 Customer Suspended - Johnson Tax Services                │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Status: SUSPENDED                                           │
│  Reason: Payment overdue                                     │
│  Suspended: January 20, 2025                                │
│  Days Overdue: 17 days                                      │
│                                                              │
│  Outstanding Invoice:                                        │
│  Invoice: INV-2024-1042                                     │
│  Amount: $1,999.00                                           │
│  Due Date: January 3, 2025                                  │
│                                                              │
│  ⛔ Customer access is currently disabled                    │
│  ✅ Access will restore automatically upon payment           │
│                                                              │
│  Actions:                                                    │
│  [Send Payment Reminder] [Manual Activation] [View Details] │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### Add-On Activated Notification

```
┌────────────────────────────────────────────────────────────┐
│ ✅ Add-On Activated Successfully                            │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Customer: Smith & Associates CPA                           │
│  Add-On: 10 Additional Users                                │
│  Payment: $100.00 (Paid)                                    │
│                                                              │
│  ✓ Limits Updated:                                          │
│    Users: 20 → 30                                           │
│                                                              │
│  Customer can now add 10 more users immediately!            │
│                                                              │
│                                            [View Customer]  │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Flows

### Flow 1: New Customer Subscription

```
┌──────────────────────────────────────────────────────────┐
│ 1. Admin Creates Customer                                 │
│    - Selects "Professional" plan                          │
│    - Enters payment method                                │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ 2. Stripe Creates Subscription                            │
│    - Creates customer in Stripe                           │
│    - Attaches payment method                              │
│    - Creates subscription ($799/mo)                       │
│    - Charges first payment                                │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Webhook: invoice.payment_succeeded                     │
│    - Customer status → ACTIVE                             │
│    - Sets limits: 20 users, 100 engagements, 500 GB      │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ 4. Customer Can Start Using Platform                      │
│    - Full access to Professional features                 │
│    - Can add up to 20 users                               │
│    - Can create up to 100 engagements                     │
└──────────────────────────────────────────────────────────┘
```

### Flow 2: Purchase Add-On (Extra Users)

```
┌──────────────────────────────────────────────────────────┐
│ 1. Customer Approaching User Limit                        │
│    - Current: 18/20 users                                 │
│    - Wants to add 5 more users                            │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ 2. Admin Purchases "10 Additional Users"                  │
│    - Clicks "Purchase Add-on"                             │
│    - Selects "10 Additional Users" ($100)                 │
│    - Confirms purchase                                     │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Stripe Processes Payment                               │
│    - Creates invoice for $100                             │
│    - Charges payment method                               │
│    - Invoice status → PAID                                │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ 4. Webhook: invoice.payment_succeeded                     │
│    - Detects add-on purchase in metadata                  │
│    - Increases max_users: 20 → 30                         │
│    - Stores purchase in tenant.settings                   │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ 5. Customer Can Add Users Immediately                     │
│    - Limit increased from 20 to 30                        │
│    - Can now add 12 more users (18/30)                    │
│    - No waiting, instant activation                       │
└──────────────────────────────────────────────────────────┘
```

### Flow 3: Late Payment Suspension

```
┌──────────────────────────────────────────────────────────┐
│ Day 0: Invoice Due                                        │
│    - Invoice INV-2024-1045 ($799) due                     │
│    - Payment method charged                               │
│    - Payment FAILED (insufficient funds)                  │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Webhook: invoice.payment_failed                           │
│    - Sends notification to customer                       │
│    - Sends alert to admin                                 │
│    - Customer still has access (grace period)             │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Day 1-14: Grace Period                                    │
│    - Customer continues to have access                    │
│    - Stripe retries payment (smart retries)               │
│    - Reminder emails sent                                 │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Day 15: Daily Cron Job Runs                               │
│    - check_overdue_invoices() executes                    │
│    - Finds invoice 15 days overdue                        │
│    - SUSPENDS customer automatically                      │
│    - Sets status → SUSPENDED                              │
│    - Stores suspension details in settings                │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Customer Access Disabled                                  │
│    - Cannot log in                                        │
│    - Users see "Account Suspended" message                │
│    - Admin notified of suspension                         │
│    - Customer receives suspension notice                  │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Customer Pays Invoice                                     │
│    - Updates payment method                               │
│    - Pays outstanding invoice                             │
│    - Payment successful                                    │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Webhook: invoice.payment_succeeded                        │
│    - Detects customer was suspended                       │
│    - Reactivates automatically                            │
│    - Sets status → ACTIVE                                 │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│ Access Restored                                           │
│    - Customer can log in immediately                      │
│    - All features restored                                │
│    - Users notified of restoration                        │
└──────────────────────────────────────────────────────────┘
```

---

## 🔧 API Endpoints

### Subscription Management

**Create Subscription:**
```http
POST /api/stripe/subscriptions/create
Content-Type: application/json

{
  "customerId": "uuid",
  "subscriptionTier": "professional",
  "paymentMethodId": "pm_1234567890"
}
```

**Change Subscription:**
```http
POST /api/stripe/subscriptions/change
Content-Type: application/json

{
  "customerId": "uuid",
  "newSubscriptionTier": "enterprise"
}
```

**Cancel Subscription:**
```http
POST /api/stripe/subscriptions/cancel?customerId=uuid&immediate=false
```

### Add-On Purchases

**Get Available Add-Ons:**
```http
GET /api/stripe/addons/available
```

**Purchase Add-On:**
```http
POST /api/stripe/addons/purchase
Content-Type: application/json

{
  "customerId": "uuid",
  "addonType": "extra_users_10",
  "quantity": 1
}
```

### Payment Methods

**Add Payment Method:**
```http
POST /api/stripe/payment-methods/add
Content-Type: application/json

{
  "customerId": "uuid",
  "paymentMethodId": "pm_1234567890"
}
```

**Get Payment Methods:**
```http
GET /api/stripe/payment-methods/{customerId}
```

### Invoices

**Get Invoices:**
```http
GET /api/stripe/invoices/{customerId}
```

### Webhooks

**Webhook Endpoint:**
```http
POST /api/stripe/webhook
Stripe-Signature: t=...,v1=...

{
  "type": "invoice.payment_succeeded",
  "data": { ... }
}
```

### Admin Endpoints

**Check Overdue Invoices:**
```http
POST /api/stripe/admin/check-overdue
```

**Get Subscription Stats:**
```http
GET /api/stripe/admin/subscription-stats
```

---

## 🔒 Security Best Practices

1. **Webhook Signature Verification**
   - Always verify Stripe webhook signatures
   - Use `Stripe-Signature` header
   - Prevents unauthorized webhook calls

2. **Environment Variables**
   - Never commit API keys to git
   - Use environment variables
   - Different keys for dev/staging/prod

3. **HTTPS Only**
   - Webhook endpoint must use HTTPS
   - Stripe requires secure connections

4. **Idempotency**
   - Webhooks may be sent multiple times
   - Handle duplicate events gracefully
   - Use idempotency keys for safety

5. **Error Handling**
   - Catch and log all Stripe errors
   - Return 200 OK to Stripe even on errors
   - Prevents infinite retries

---

## 📊 Monitoring & Alerts

### Metrics to Monitor:

1. **Subscription Health:**
   - Active subscriptions
   - Churn rate
   - MRR/ARR

2. **Payment Success Rate:**
   - Successful payments / total payments
   - Target: > 95%

3. **Suspension Rate:**
   - Suspended customers / total customers
   - Monitor for trends

4. **Add-On Revenue:**
   - Total add-on purchases
   - Most popular add-ons

### Alerts to Set Up:

1. **Payment Failure Spike**
   - Alert if > 10% of payments fail in 24h
   - May indicate Stripe issue

2. **Suspension Spike**
   - Alert if > 5 customers suspended in one day
   - May indicate billing issue

3. **Webhook Failure**
   - Alert if webhook endpoint returns errors
   - Critical for automation

4. **Overdue Invoice Count**
   - Daily report of invoices approaching 15 days
   - Proactive intervention opportunity

---

## 🧪 Testing

### Test Mode:

Use Stripe test cards in test mode:

**Successful Payment:**
```
Card: 4242 4242 4242 4242
Exp: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits
```

**Payment Decline:**
```
Card: 4000 0000 0000 0002
(Will decline)
```

**Requires Authentication:**
```
Card: 4000 0025 0000 3155
(Triggers 3D Secure)
```

### Test Webhooks:

Use Stripe CLI to test webhooks locally:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Listen for webhooks
stripe listen --forward-to localhost:8000/api/stripe/webhook

# Trigger test events
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
```

---

## 📚 Additional Resources

- **Stripe Documentation**: https://stripe.com/docs
- **Webhook Best Practices**: https://stripe.com/docs/webhooks/best-practices
- **Subscription Billing**: https://stripe.com/docs/billing/subscriptions/overview
- **Testing**: https://stripe.com/docs/testing

---

## ✅ Checklist

Before going live:

- [ ] Created all products in Stripe Dashboard
- [ ] Updated price IDs in `stripe_service.py`
- [ ] Set environment variables (API keys, webhook secret)
- [ ] Configured webhook endpoint in Stripe Dashboard
- [ ] Set up daily cron job for overdue checks
- [ ] Tested subscription creation
- [ ] Tested add-on purchases
- [ ] Tested webhook events
- [ ] Tested payment failure handling
- [ ] Tested suspension/reactivation
- [ ] Set up monitoring and alerts
- [ ] Documented runbook for common issues

---

**The Stripe integration is production-ready and fully automated!**

Customers can purchase add-ons and have features activate instantly. Late payments automatically suspend access after 15 days, and payment restores access immediately. Zero manual intervention required! 🚀
