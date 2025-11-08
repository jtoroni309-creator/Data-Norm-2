# Multi-Level Admin System Guide

## Overview

The Data-Norm-2 platform implements a comprehensive multi-tenant RBAC (Role-Based Access Control) system with three distinct portal levels:

1. **Platform Admin Portal** - Super administrators manage the entire platform
2. **CPA Firm Portal** - CPA firms manage their employees, clients, and firm settings
3. **Client Portal** - Clients manage their users and participate in engagements

---

## Architecture

### Multi-Tenancy Hierarchy

```
Platform
  └── CPA Firms (Tenants)
        ├── Employees (Firm Users)
        │     ├── Partner (Approval Level 100)
        │     ├── Manager (Approval Level 75)
        │     ├── Senior (Approval Level 50)
        │     └── Staff (Approval Level 25)
        │
        └── Clients
              ├── Client Admin
              ├── Finance Manager
              └── Viewers
```

### Data Isolation

- **Row-Level Security (RLS)**: PostgreSQL policies ensure firms only see their data
- **Tenant Scoping**: All queries automatically filtered by `current_firm_id`
- **Audit Logging**: Complete trail of all actions across all portals

---

## 1. Platform Admin Portal

### Purpose
Super administrators manage the entire platform, CPA firms, subscriptions, and system settings.

### Access Level
- **Platform Administrators** only
- Highest privilege level in the system

### Capabilities

#### 1.1 Firm Management

**Create CPA Firm:**
```python
from services.admin.app.firm_management_service import FirmManagementService

firm_service = FirmManagementService(db)

# Create new firm with 30-day trial
firm = await firm_service.create_firm(
    firm_name="Smith & Partners CPA",
    primary_contact_email="admin@smithcpa.com",
    primary_contact_name="John Smith",
    legal_name="Smith & Partners CPA, LLP",
    start_trial=True
)

print(f"Created firm {firm.id}")
print(f"Trial ends: {firm.trial_end_date}")
```

**Upgrade Subscription:**
```python
from services.admin.app.firm_management_service import FirmSubscriptionTier

# Upgrade from trial to professional
await firm_service.upgrade_subscription(
    firm_id=firm.id,
    new_tier=FirmSubscriptionTier.PROFESSIONAL,
    user_id=admin_user_id
)

# New limits: 50 clients, 25 users
```

**Suspend Firm:**
```python
# Suspend for non-payment
await firm_service.suspend_firm(
    firm_id=firm.id,
    reason="Payment past due 30 days",
    user_id=admin_user_id
)
```

#### 1.2 Subscription Tiers

| Tier | Max Clients | Max Users | Price/Month | Features |
|------|------------|-----------|-------------|----------|
| **Trial** | 2 | 3 | Free | 30-day trial, all features |
| **Starter** | 10 | 5 | $99 | All features |
| **Professional** | 50 | 25 | $299 | All features + priority support |
| **Enterprise** | Unlimited | Unlimited | $999 | All features + dedicated account manager |

#### 1.3 Monitoring

**Get Platform Metrics:**
```python
# Query all firms
query = text("""
    SELECT
        subscription_tier,
        subscription_status,
        COUNT(*) as firm_count,
        SUM(total_clients) as total_clients,
        SUM(total_users) as total_users
    FROM atlas.firm_dashboard_metrics
    GROUP BY subscription_tier, subscription_status
""")

result = await db.execute(query)
metrics = result.fetchall()
```

**Check Trial Expirations:**
```python
# Get firms with trials expiring soon
trial_status = await firm_service.check_trial_expiration(firm_id)

if trial_status['days_remaining'] <= 7:
    print(f"Trial expires in {trial_status['days_remaining']} days")
    # Send reminder email
```

---

## 2. CPA Firm Portal

### Purpose
CPA firm administrators and partners manage their firm, employees, clients, and engagements.

### Roles

| Role | Approval Level | Permissions |
|------|---------------|-------------|
| **Firm Admin** | 90 | Full firm settings, user management, billing |
| **Partner** | 100 | All engagement permissions, final approvals, issue reports |
| **Manager** | 75 | Manage engagements, supervise staff, review workpapers |
| **Senior** | 50 | Perform reviews, complex procedures |
| **Staff** | 25 | Fieldwork, basic testing |

### 2.1 Firm Settings

**Update Firm Profile:**
```python
from services.admin.app.firm_management_service import FirmManagementService

firm_service = FirmManagementService(db)

# Update firm details
await firm_service.update_firm(
    firm_id=firm_id,
    updates={
        "address_line1": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "default_engagement_partner": "John Smith, CPA",
        "require_two_factor_auth": True,
        "session_timeout_minutes": 30
    },
    updated_by_user_id=admin_user_id
)
```

**Update Branding:**
```python
# Customize firm branding
await firm_service.update_branding(
    firm_id=firm_id,
    logo_url="https://cdn.example.com/smithcpa_logo.png",
    primary_color="#003366",  # Navy blue
    secondary_color="#FFD700", # Gold
    user_id=admin_user_id
)
```

### 2.2 Employee Management

**Add Employee:**
```python
from services.admin.app.user_management_service import UserManagementService

user_service = UserManagementService(db)

# Create senior accountant
user = await user_service.create_user(
    email="jane.doe@smithcpa.com",
    first_name="Jane",
    last_name="Doe",
    cpa_firm_id=firm_id,
    role_ids=[senior_role_id],  # Senior Accountant role
    send_invitation=True,
    created_by_user_id=admin_user_id
)

print(f"Created user {user['email']}")
print(f"Temporary password: {user['temporary_password']}")
```

**Assign Additional Roles:**
```python
# Promote to manager
await user_service.assign_role(
    user_id=user_id,
    role_id=manager_role_id,
    granted_by=partner_user_id
)
```

**List Employees:**
```python
# Get all firm users
employees = await user_service.list_firm_users(
    firm_id=firm_id,
    include_inactive=False
)

for emp in employees:
    print(f"{emp['first_name']} {emp['last_name']} - {emp['roles']}")
```

### 2.3 Client Management

**Add Client:**
```python
from services.admin.app.client_management_service import ClientManagementService

client_service = ClientManagementService(db)

# Create new client
client = await client_service.create_client(
    cpa_firm_id=firm_id,
    client_name="ABC Corporation",
    primary_contact_email="cfo@abccorp.com",
    primary_contact_name="Mary Johnson",
    entity_type="c_corporation",
    fiscal_year_end="12-31",
    enable_portal=True,
    created_by_user_id=admin_user_id
)

print(f"Created client {client['client_id']}")
```

**Configure Client Portal:**
```python
# Enable/disable portal features for client
await client_service.configure_portal_features(
    client_id=client_id,
    allow_document_upload=True,
    allow_confirmation_response=True,
    allow_data_export=False,  # Disable data export
    allow_report_download=True,
    allow_messaging=True,
    allow_financial_view=True,
    configured_by_user_id=admin_user_id
)
```

**Enable Portal with Custom Domain:**
```python
# Enable portal with custom branding
await client_service.enable_portal(
    client_id=client_id,
    custom_domain="portal.abccorp.com",
    logo_url="https://abccorp.com/logo.png",
    enabled_by_user_id=admin_user_id
)
```

**Disable Portal:**
```python
# Temporarily disable client portal
await client_service.disable_portal(
    client_id=client_id,
    disabled_by_user_id=admin_user_id
)
```

**List Clients:**
```python
# Get all firm clients
clients = await client_service.list_firm_clients(
    firm_id=firm_id,
    include_inactive=False
)

for client in clients:
    print(f"{client['client_name']}: {client['engagement_count']} engagements, "
          f"{client['user_count']} users, Portal: {client['portal_enabled']}")
```

### 2.4 Permissions Management

**Check User Permission:**
```python
# Check if user can create engagements
has_permission = await user_service.check_permission(
    user_id=user_id,
    permission_name="engagement.create",
    client_id=client_id
)

if has_permission:
    # Allow action
    pass
```

**Get User Permissions:**
```python
# Get all permissions for user
permissions = await user_service.get_user_permissions(
    user_id=user_id,
    client_id=client_id
)

print(f"User has {len(permissions)} permissions:")
for perm in permissions:
    print(f"  - {perm}")
```

**Available Permissions:**

**Engagement:**
- `engagement.create` - Create new engagements
- `engagement.read` - View engagements
- `engagement.update` - Update engagement details
- `engagement.delete` - Delete engagements
- `engagement.approve` - Approve engagements

**Workpaper:**
- `workpaper.create` - Create workpapers
- `workpaper.read` - View workpapers
- `workpaper.update` - Edit workpapers
- `workpaper.review` - Review and approve workpapers

**Client:**
- `client.create` - Add new clients
- `client.read` - View client information
- `client.update` - Update client details
- `client.delete` - Delete clients
- `client.configure_portal` - Configure client portal settings

**Report:**
- `report.create` - Generate reports
- `report.read` - View reports
- `report.approve` - Approve reports
- `report.issue` - Issue final reports

### 2.5 Approval Workflows

**Create Approval Chain:**
```python
from services.admin.app.approval_workflow_service import ApprovalWorkflowService

approval_service = ApprovalWorkflowService(db)

# Create 3-level approval chain for reports
chain_id = await approval_service.create_approval_chain(
    firm_id=firm_id,
    chain_name="Standard Report Approval",
    resource_type="report",
    approval_levels=[
        {"level": 1, "role_id": str(senior_role_id), "required": True},
        {"level": 2, "role_id": str(manager_role_id), "required": True},
        {"level": 3, "role_id": str(partner_role_id), "required": True}
    ],
    created_by_user_id=admin_user_id
)
```

**Request Approval:**
```python
# Submit report for approval
request_id = await approval_service.request_approval(
    approval_chain_id=chain_id,
    resource_type="report",
    resource_id=report_id,
    requested_by_user_id=staff_user_id,
    request_description="Audit report for ABC Corp FY2024"
)
```

**Approve:**
```python
# Senior approves (Level 1)
result = await approval_service.approve(
    approval_request_id=request_id,
    approver_user_id=senior_user_id,
    notes="Reviewed workpapers, no issues found"
)

# Manager approves (Level 2)
result = await approval_service.approve(
    approval_request_id=request_id,
    approver_user_id=manager_user_id,
    notes="Engagement quality review complete"
)

# Partner final approval (Level 3)
result = await approval_service.approve(
    approval_request_id=request_id,
    approver_user_id=partner_user_id,
    notes="Approved for issuance"
)

if result['overall_status'] == 'approved':
    print("Report fully approved and ready for issuance")
```

**Reject:**
```python
# Manager rejects
await approval_service.reject(
    approval_request_id=request_id,
    rejector_user_id=manager_user_id,
    rejection_reason="Missing disclosure for lease commitments (ASC 842)"
)
```

**Delegate:**
```python
# Partner delegates to another partner
await approval_service.delegate(
    approval_request_id=request_id,
    delegator_user_id=partner_user_id,
    delegatee_user_id=other_partner_user_id,
    delegation_notes="Out of office, please review"
)
```

**Get Pending Approvals:**
```python
# Get items pending my approval
pending = await approval_service.get_pending_approvals(
    user_id=manager_user_id,
    resource_type="report"
)

print(f"You have {len(pending)} reports pending approval:")
for item in pending:
    print(f"  - {item['description']} (Level {item['approval_level']})")
```

### 2.6 Firm Dashboard

**Get Dashboard:**
```python
# Get comprehensive firm dashboard
dashboard = await firm_service.get_firm_dashboard(firm_id)

print(f"=== {dashboard['firm']['name']} ===")
print(f"Subscription: {dashboard['firm']['subscription_tier']}")
print(f"\nMetrics:")
print(f"  Clients: {dashboard['metrics']['total_clients']}")
print(f"  Users: {dashboard['metrics']['total_users']}")
print(f"  Active Engagements: {dashboard['metrics']['active_engagements']}")

print(f"\nLimits:")
print(f"  Clients: {dashboard['limits']['clients']['current']}/{dashboard['limits']['clients']['max']}")
print(f"  Users: {dashboard['limits']['users']['current']}/{dashboard['limits']['users']['max']}")

if dashboard['trial']['is_trial']:
    print(f"\nTrial expires in {dashboard['trial']['days_remaining']} days")
```

---

## 3. Client Portal

### Purpose
Clients manage their users, upload data, respond to confirmation requests, and participate in attestation engagements.

### Roles

| Role | Approval Level | Permissions |
|------|---------------|-------------|
| **Client Admin** | 100 | Manage client users, portal settings |
| **Finance Manager** | 75 | Upload data, respond to requests, approvals |
| **Viewer** | 0 | Read-only access |

### 3.1 Client User Management

**Add Client User:**
```python
# Client admin adds finance manager
user = await user_service.create_user(
    email="controller@abccorp.com",
    first_name="Alice",
    last_name="Williams",
    client_id=client_id,
    role_ids=[client_finance_role_id],
    send_invitation=True,
    created_by_user_id=client_admin_user_id
)
```

**List Client Users:**
```python
# Get all users for this client
client_users = await user_service.list_client_users(
    client_id=client_id,
    include_inactive=False
)

for user in client_users:
    print(f"{user['first_name']} {user['last_name']} - {user['roles']}")
```

### 3.2 Portal Features (Configurable by CPA Firm)

The CPA firm controls which features are available in the client portal:

#### Feature Flags

```python
# Get portal configuration
config = await client_service.get_portal_configuration(client_id)

print(f"Portal enabled: {config['portal_enabled']}")
print("\nFeatures:")
print(f"  Document Upload: {config['features']['document_upload']}")
print(f"  Confirmation Response: {config['features']['confirmation_response']}")
print(f"  Data Export: {config['features']['data_export']}")
print(f"  Report Download: {config['features']['report_download']}")
print(f"  Messaging: {config['features']['messaging']}")
print(f"  Financial View: {config['features']['financial_view']}")
```

#### Conditional UI Elements

In the client portal UI, features are conditionally shown:

```typescript
// Frontend example
if (portalConfig.features.document_upload) {
    // Show "Upload Documents" button
}

if (portalConfig.features.confirmation_response) {
    // Show pending confirmations
}

if (portalConfig.features.financial_view) {
    // Show trial balance, financial statements
}
```

### 3.3 Client Dashboard

**Get Dashboard:**
```python
# Get client dashboard
dashboard = await client_service.get_client_dashboard(client_id)

print(f"=== {dashboard['client']['name']} ===")
print(f"CPA Firm: {dashboard['cpa_firm']['name']}")
print(f"Contact: {dashboard['cpa_firm']['contact_name']} ({dashboard['cpa_firm']['contact_email']})")

print(f"\nEngagements:")
for eng in dashboard['engagements']:
    print(f"  - {eng['engagement_type'].upper()} FY{eng['fiscal_year_end']}: {eng['status']}")

print(f"\nPending Items: {len(dashboard['pending_items'])}")
for item in dashboard['pending_items']:
    if item['type'] == 'confirmation':
        print(f"  - Confirmation: {item['entity_name']} (${item['amount']:,.2f})")
    else:
        print(f"  - {item['type']}")
```

### 3.4 Client Portal Actions

#### Upload Trial Balance
```python
# Upload trial balance (if feature enabled)
if portalConfig.features.document_upload:
    # Permission: data.upload_trial_balance
    await upload_trial_balance(
        client_id=client_id,
        fiscal_year_end=date(2024, 12, 31),
        file_path="trial_balance_2024.xlsx",
        uploaded_by=client_user_id
    )
```

#### Respond to Confirmation
```python
# Respond to A/R confirmation (if feature enabled)
if portalConfig.features.confirmation_response:
    # Permission: confirmation.respond
    await confirmation_service.record_confirmation_response(
        confirmation_id=confirmation_id,
        confirmed_amount=125000.00,
        received_date=date.today(),
        response_notes="Balance confirmed as of 12/31/2024"
    )
```

#### Download Report
```python
# Download final audit report (if feature enabled)
if portalConfig.features.report_download:
    # Permission: report.read
    report_url = await get_report_download_url(
        engagement_id=engagement_id,
        report_id=report_id
    )
```

#### Send Message to CPA Firm
```python
# Send message (if feature enabled)
if portalConfig.features.messaging:
    await send_message(
        from_user_id=client_user_id,
        to_firm_id=cpa_firm_id,
        engagement_id=engagement_id,
        subject="Question about inventory observation",
        message="Can we schedule the inventory count for January 5th?"
    )
```

---

## 4. Security & Compliance

### 4.1 Row-Level Security (RLS)

PostgreSQL RLS policies ensure data isolation:

```sql
-- Engagements: Users only see their firm's client engagements
CREATE POLICY engagement_firm_isolation ON engagements
    USING (
        client_id IN (
            SELECT c.id FROM clients c
            WHERE c.cpa_firm_id = current_setting('app.current_firm_id')::UUID
        )
    );

-- Clients: Users only see their firm's clients
CREATE POLICY client_firm_isolation ON clients
    USING (cpa_firm_id = current_setting('app.current_firm_id')::UUID);
```

### 4.2 Audit Logging

All actions are logged:

```python
# Audit log automatically created for all actions
await _audit_log(
    user_id=user_id,
    cpa_firm_id=firm_id,
    client_id=client_id,
    action="engagement.approve",
    resource_type="engagement",
    resource_id=engagement_id,
    description="Approved engagement for issuance",
    changes={"status": {"old": "draft", "new": "approved"}},
    ip_address=request.client.host,
    user_agent=request.headers.get("User-Agent")
)
```

Query audit log:

```python
# Get audit trail for engagement
query = text("""
    SELECT
        u.email,
        al.action,
        al.description,
        al.created_at,
        al.ip_address
    FROM atlas.audit_log al
    LEFT JOIN atlas.users u ON u.id = al.user_id
    WHERE al.resource_type = 'engagement'
    AND al.resource_id = :engagement_id
    ORDER BY al.created_at DESC
""")

result = await db.execute(query, {"engagement_id": engagement_id})
```

### 4.3 Session Management

Configurable session settings per firm:

```python
# Firm settings
{
    "session_timeout_minutes": 30,  # Auto-logout after 30 minutes
    "require_two_factor_auth": True,  # Require 2FA for all users
    "password_expiry_days": 90  # Force password change every 90 days
}
```

---

## 5. API Integration

### 5.1 Setting Current Firm Context

For multi-tenant queries, set the current firm context:

```python
# Set firm context for RLS policies
await db.execute(text("SET app.current_firm_id = :firm_id"), {"firm_id": firm_id})

# Set client context for client users
await db.execute(text("SET app.current_client_id = :client_id"), {"client_id": client_id})

# Now all queries automatically filtered by RLS policies
```

### 5.2 Permission Middleware

Check permissions before actions:

```python
from fastapi import HTTPException

async def require_permission(
    user_id: UUID,
    permission: str,
    client_id: Optional[UUID] = None
):
    """Middleware to check user permissions"""
    has_permission = await user_service.check_permission(
        user_id=user_id,
        permission_name=permission,
        client_id=client_id
    )

    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {permission}"
        )

# Usage in endpoint
@app.post("/api/engagements")
async def create_engagement(
    engagement_data: EngagementCreate,
    current_user: User = Depends(get_current_user)
):
    # Check permission
    await require_permission(
        user_id=current_user.id,
        permission="engagement.create",
        client_id=engagement_data.client_id
    )

    # Create engagement
    # ...
```

---

## 6. Common Workflows

### 6.1 Onboarding New CPA Firm

```python
# 1. Platform admin creates firm
firm = await firm_service.create_firm(
    firm_name="New CPA Firm",
    primary_contact_email="admin@newcpa.com",
    start_trial=True
)

# 2. Create firm admin user
admin_user = await user_service.create_user(
    email="admin@newcpa.com",
    first_name="Admin",
    last_name="User",
    cpa_firm_id=firm.id,
    role_ids=[firm_admin_role_id]
)

# 3. Firm admin adds employees
employees = [
    {"email": "partner@newcpa.com", "role": "firm_partner"},
    {"email": "manager@newcpa.com", "role": "firm_manager"},
    {"email": "staff@newcpa.com", "role": "firm_staff"}
]

for emp in employees:
    await user_service.create_user(
        email=emp["email"],
        cpa_firm_id=firm.id,
        role_ids=[get_role_id(emp["role"])]
    )

# 4. Firm admin adds first client
client = await client_service.create_client(
    cpa_firm_id=firm.id,
    client_name="First Client",
    primary_contact_email="cfo@firstclient.com",
    enable_portal=True
)

# 5. Configure client portal
await client_service.configure_portal_features(
    client_id=client.id,
    allow_document_upload=True,
    allow_confirmation_response=True,
    allow_report_download=True
)
```

### 6.2 Client Onboarding

```python
# 1. Firm admin creates client
client = await client_service.create_client(
    cpa_firm_id=firm_id,
    client_name="ABC Corporation",
    primary_contact_email="cfo@abccorp.com",
    enable_portal=True
)

# 2. Create client admin user
client_admin = await user_service.create_user(
    email="cfo@abccorp.com",
    first_name="Mary",
    last_name="Johnson",
    client_id=client.id,
    role_ids=[client_admin_role_id]
)

# 3. Client admin adds team members
await user_service.create_user(
    email="controller@abccorp.com",
    client_id=client.id,
    role_ids=[client_finance_role_id],
    created_by_user_id=client_admin.id
)

# 4. Create engagement
from services.engagement.app.engagement_workflow_service import EngagementWorkflowService

workflow_service = EngagementWorkflowService(db)

engagement, summary = await workflow_service.create_engagement_with_workflow(
    client_name=client.name,
    engagement_type="audit",
    fiscal_year_end=date(2024, 12, 31),
    engagement_partner="John Smith, CPA",
    user_id=firm_admin_user_id
)
```

### 6.3 Approval Workflow

```python
# 1. Staff completes workpaper
await binder_service.mark_workpaper_complete(
    node_id=workpaper_node_id,
    user_id=staff_user_id
)

# 2. System automatically requests approval
request_id = await approval_service.request_approval(
    approval_chain_id=default_chain_id,
    resource_type="workpaper",
    resource_id=workpaper_node_id,
    requested_by_user_id=staff_user_id
)

# 3. Senior reviews and approves
await approval_service.approve(
    approval_request_id=request_id,
    approver_user_id=senior_user_id,
    notes="Reviewed, no exceptions"
)

# 4. Manager reviews and approves
await approval_service.approve(
    approval_request_id=request_id,
    approver_user_id=manager_user_id,
    notes="EQR complete"
)

# 5. Workpaper marked as reviewed
await binder_service.mark_workpaper_reviewed(
    node_id=workpaper_node_id,
    user_id=manager_user_id
)
```

---

## 7. Database Schema Summary

### Core Tables

- `cpa_firms` - CPA firms (top-level tenants)
- `clients` - Clients belonging to firms
- `users` - All platform users
- `roles` - System and custom roles
- `permissions` - Granular permissions
- `user_roles` - User-role assignments
- `role_permissions` - Role-permission mappings
- `approval_chains` - Configurable approval workflows
- `approval_requests` - Approval requests
- `approval_actions` - Individual approval actions
- `audit_log` - Complete audit trail

### Views

- `user_permissions_view` - Flattened user permissions
- `firm_dashboard_metrics` - Firm dashboard data
- `client_portal_access` - Client portal configuration

---

## 8. Best Practices

### For Platform Admins:
1. Monitor trial expirations and send reminders
2. Review subscription limits before firms hit caps
3. Audit suspicious activity via audit_log
4. Provide upgrade paths for growing firms

### For CPA Firms:
1. Use approval chains for all critical actions
2. Regularly review user permissions
3. Configure client portal features based on engagement needs
4. Leverage firm dashboard for resource planning
5. Maintain proper segregation of duties

### For Clients:
1. Designate clear admin vs. finance roles
2. Respond promptly to confirmation requests
3. Use portal messaging for audit questions
4. Keep user list updated (deactivate terminated employees)

---

## 9. Troubleshooting

### Issue: User Cannot See Client Data

**Diagnosis:**
```python
# Check user's firm association
user = await db.get(User, user_id)
print(f"User firm: {user.cpa_firm_id}")

# Check client's firm association
client = await db.get(Client, client_id)
print(f"Client firm: {client.cpa_firm_id}")

# Check if RLS context is set
result = await db.execute(text("SHOW app.current_firm_id"))
print(f"Current firm context: {result.scalar()}")
```

**Solution:** Ensure RLS context is set correctly and user belongs to same firm as client.

### Issue: Permission Denied

**Diagnosis:**
```python
# Check user's roles
roles = await user_service.get_user_roles(user_id)
print(f"User roles: {roles}")

# Check user's permissions
permissions = await user_service.get_user_permissions(user_id)
print(f"User permissions: {permissions}")

# Check required permission
has_perm = await user_service.check_permission(
    user_id=user_id,
    permission_name="engagement.create"
)
print(f"Has permission: {has_perm}")
```

**Solution:** Assign appropriate role or grant specific permission.

### Issue: Approval Stuck

**Diagnosis:**
```python
# Get approval history
history = await approval_service.get_approval_history(
    resource_type="report",
    resource_id=report_id
)

for entry in history:
    print(f"Level {entry['approval_level']}: {entry['action']} by {entry['approver_name']}")
```

**Solution:** Identify missing approval level and notify appropriate approver or delegate.

---

## 10. Summary

The multi-level admin system provides:

✅ **Complete Multi-Tenancy** - Firms are fully isolated with RLS
✅ **Flexible RBAC** - Granular permissions with role-based access
✅ **Approval Workflows** - Configurable multi-level approvals
✅ **Client Portal Control** - Feature flags for client access
✅ **Comprehensive Auditing** - Full trail of all actions
✅ **Subscription Management** - Tiered pricing with limits
✅ **User Management** - Both firm and client user administration

The platform now has **enterprise-grade multi-tenant capabilities** that match or exceed commercial audit software platforms.
