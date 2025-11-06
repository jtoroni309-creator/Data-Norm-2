# Jira Integration with Claude Code AI

## Overview

The Aura Audit AI platform includes a powerful Jira integration that enables:

1. **Customer Bug Reporting** - Customers can report bugs directly from the client portal
2. **Feature Requests** - Customers can suggest new features and improvements
3. **Support Tickets** - General customer support and help requests
4. **AI-Powered Bug Analysis** - Claude Code automatically analyzes bugs and suggests fixes
5. **Automated Bug Fixing** - Claude Code can generate fixes and create pull requests
6. **Admin Dashboard** - Comprehensive ticket management interface

## Features

### Customer-Facing Features

- **🐛 Bug Reporting**
  - Detailed bug report forms with priority levels
  - Steps to reproduce, expected vs actual behavior
  - Environment information capture
  - Screenshot upload support
  - Automatic ticket tracking

- **💡 Feature Requests**
  - Business value assessment
  - Use case documentation
  - Priority voting
  - Status tracking

- **❓ Support Tickets**
  - Multiple support categories (technical, billing, training, etc.)
  - Priority levels
  - Real-time status updates
  - Response tracking

- **📊 My Tickets Dashboard**
  - View all submitted tickets
  - Filter by status and type
  - Search functionality
  - Direct link to Jira

### Admin Features

- **📈 Statistics Dashboard**
  - Total issues count
  - Open bugs, features, and support tickets
  - High and critical priority counts
  - Real-time metrics

- **🎯 Advanced Filtering**
  - Filter by issue type (Bug, Feature, Support)
  - Filter by status (Open, In Progress, Resolved, Closed)
  - Filter by priority (Low, Medium, High, Critical)
  - Filter by customer
  - Full-text search

- **✏️ Ticket Management**
  - Update ticket status
  - Assign tickets to team members
  - Add public and internal comments
  - View full ticket history

- **🤖 Claude Code AI Integration**
  - **Analyze Bug**: AI analyzes the bug and provides:
    - Root cause analysis
    - Files that need to be examined
    - Suggested fix approach
    - Potential side effects

  - **Auto-Fix**: Fully automated bug fixing:
    - Analyzes the bug
    - Reads relevant code files
    - Generates the fix
    - Creates a pull request
    - Updates Jira with results

## Architecture

```
┌─────────────────┐
│  Client Portal  │
│   Bug Report    │
└────────┬────────┘
         │
         v
┌─────────────────┐      ┌──────────────┐
│   FastAPI       │─────>│  Jira API    │
│   jira_api.py   │      │  REST v3     │
└────────┬────────┘      └──────────────┘
         │
         v
┌─────────────────┐      ┌──────────────┐
│  jira_service   │─────>│ Claude Code  │
│  AI Integration │      │ Anthropic AI │
└─────────────────┘      └──────────────┘
         │
         v
┌─────────────────┐
│   GitHub API    │
│  Pull Requests  │
└─────────────────┘
```

## Setup

### 1. Jira Configuration

#### Create Jira Project

1. Go to your Jira instance
2. Create a new project (e.g., "AURA")
3. Configure issue types:
   - Bug
   - Feature
   - Support

#### Create API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name: "Aura Audit AI Integration"
4. Copy the token (you won't see it again!)

#### Configure Webhook

1. Go to Jira Settings > System > Webhooks
2. Create a new webhook:
   - **Name**: Aura Platform Webhook
   - **Status**: Enabled
   - **URL**: `https://your-domain.com/api/jira/webhook`
   - **Events**:
     - Issue: created, updated
     - Comment: created
3. Save the webhook

### 2. Environment Variables

Add these to your `.env` file:

```bash
# Jira Configuration
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_jira_api_token_here
JIRA_PROJECT_KEY=AURA

# Claude Code Configuration (already set up)
ANTHROPIC_API_KEY=your_anthropic_api_key

# GitHub Configuration (for PR creation)
GITHUB_TOKEN=your_github_token
GITHUB_REPO_OWNER=your-org
GITHUB_REPO_NAME=Data-Norm-2
```

### 3. Install Dependencies

The required dependencies are already included:

```bash
# In services/financial-analysis/requirements.txt
anthropic>=0.21.0
requests>=2.31.0
```

### 4. Run the Service

```bash
cd services/financial-analysis
python -m uvicorn app.main:app --reload
```

## API Endpoints

### Customer Endpoints

#### Submit Bug Report
```http
POST /api/jira/bug-report
Content-Type: application/json
Authorization: Bearer <token>

{
  "summary": "Unable to connect QuickBooks integration",
  "description": "Detailed description of the bug",
  "reporter_email": "user@client.com",
  "customer_id": "uuid",
  "priority": "High",
  "environment": "Chrome 120, MacOS",
  "steps_to_reproduce": "1. Click Connect QuickBooks\n2. Enter credentials\n3. Error appears",
  "expected_behavior": "Should connect successfully",
  "actual_behavior": "Shows 'Connection failed' error"
}
```

**Response:**
```json
{
  "key": "AURA-123",
  "summary": "Unable to connect QuickBooks integration",
  "status": "Open",
  "priority": "High",
  "created": "2025-11-06T10:30:00Z",
  "url": "https://your-company.atlassian.net/browse/AURA-123"
}
```

#### Submit Feature Request
```http
POST /api/jira/feature-request
Content-Type: application/json
Authorization: Bearer <token>

{
  "summary": "Add Excel export for audit reports",
  "description": "Would like to export reports to Excel format",
  "requester_email": "user@client.com",
  "customer_id": "uuid",
  "priority": "Medium",
  "business_value": "Would save 2 hours per report",
  "use_case": "Our management prefers Excel for analysis"
}
```

#### Submit Support Ticket
```http
POST /api/jira/support-ticket
Content-Type: application/json
Authorization: Bearer <token>

{
  "summary": "Question about billing",
  "description": "Need clarification on invoice charges",
  "requester_email": "user@client.com",
  "customer_id": "uuid",
  "priority": "Medium",
  "category": "billing"
}
```

#### Get My Tickets
```http
GET /api/jira/my-tickets?email=user@client.com&customer_id=uuid
Authorization: Bearer <token>
```

#### Get Ticket Details
```http
GET /api/jira/ticket/AURA-123
Authorization: Bearer <token>
```

### Admin Endpoints

#### Search Issues
```http
GET /api/jira/admin/issues?issue_type=Bug&status=Open&priority=High&max_results=50
Authorization: Bearer <admin_token>
```

#### Update Issue
```http
PATCH /api/jira/admin/issues/AURA-123
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "status": "In Progress",
  "assignee_email": "developer@company.com",
  "priority": "Critical"
}
```

#### Add Comment
```http
POST /api/jira/admin/issues/AURA-123/comment
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "comment": "Looking into this issue now",
  "internal": false
}
```

#### Analyze Bug with Claude Code
```http
POST /api/jira/admin/analyze-bug
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "issue_key": "AURA-123",
  "codebase_path": "/home/user/Data-Norm-2",
  "auto_fix": false,
  "create_pr": false
}
```

**Response:**
```json
{
  "issue_key": "AURA-123",
  "analysis": "The bug appears to be in the OAuth callback handler...",
  "suggested_files": [
    "services/financial-analysis/app/integration_service.py",
    "client-portal/src/services/integration.service.ts"
  ],
  "fix_approach": "Update the OAuth state validation logic..."
}
```

#### Generate Fix and Create PR
```http
POST /api/jira/admin/analyze-bug
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "issue_key": "AURA-123",
  "codebase_path": "/home/user/Data-Norm-2",
  "auto_fix": true,
  "create_pr": true
}
```

**Response:**
```json
{
  "issue_key": "AURA-123",
  "analysis": "Root cause identified in OAuth callback...",
  "suggested_files": ["..."],
  "fix_approach": "Update validation logic...",
  "pr_url": "https://github.com/your-org/Data-Norm-2/pull/456"
}
```

#### Get Statistics
```http
GET /api/jira/admin/stats
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "total_issues": 142,
  "open_bugs": 8,
  "open_features": 15,
  "open_support": 5,
  "high_priority": 3,
  "critical_priority": 1
}
```

## Claude Code AI Integration

### How It Works

1. **Bug Analysis**
   - Customer submits bug report via client portal
   - If priority is High or Critical, Claude Code automatically analyzes it
   - Claude reads the bug description and examines relevant code
   - Provides detailed analysis with root cause and fix suggestions
   - Analysis is added as internal Jira comment

2. **Automated Fix Generation**
   - Admin clicks "Auto-Fix" button in dashboard
   - Claude Code analyzes the bug
   - Identifies files that need changes
   - Generates the complete fix with code changes
   - Runs tests to verify the fix
   - Creates a pull request with the fix
   - Updates Jira with PR link

3. **Manual Review**
   - Admin reviews Claude's analysis
   - Admin reviews the pull request
   - Admin can request changes or merge
   - Jira ticket is automatically updated

### Example Claude Code Analysis

```
Bug Report: Unable to connect QuickBooks integration
Priority: High

Claude Code Analysis:
====================

Understanding:
The bug appears to be in the OAuth callback handler for QuickBooks.
The state parameter validation is failing, causing the connection to be rejected.

Root Cause:
In services/financial-analysis/app/integration_service.py:342, the OAuth state
is being compared before URL decoding, causing legitimate states to fail validation.

Files to Examine:
1. services/financial-analysis/app/integration_service.py (OAuth callback handler)
2. client-portal/src/services/integration.service.ts (OAuth initiator)
3. services/financial-analysis/app/oauth_service.py (State management)

Suggested Fix Approach:
1. Update integration_service.py line 342 to URL decode the state before comparison
2. Add unit test for URL-encoded states
3. Add logging to help debug future OAuth issues

Potential Side Effects:
- None expected - this is a bug fix for existing functionality
- All other OAuth flows should work the same way

Estimated Effort: 1 hour
Risk Level: Low
```

### Example Pull Request Created by Claude

```
Title: Fix QuickBooks OAuth state validation (AURA-123)

Description:
Fixes bug where QuickBooks OAuth connection fails due to state validation error.

Changes:
- Updated state comparison to URL decode before validation
- Added unit test for URL-encoded states
- Added debug logging for OAuth state mismatches

Root Cause:
The OAuth state parameter was being compared before URL decoding, causing
legitimate connection attempts to fail validation.

Testing:
- Added test_oauth_state_url_encoded() in test_integration_service.py
- Manually tested QuickBooks connection flow
- All existing OAuth tests pass

Resolves: AURA-123
```

## Webhook Events

The platform automatically handles these Jira webhook events:

### issue_created
- Triggered when a new issue is created
- If issue is High/Critical priority Bug, triggers automatic Claude analysis

### issue_updated
- Triggered when issue is updated
- Can trigger re-analysis if needed

### comment_created
- Triggered when comment is added
- Can trigger notifications to customers

## Customer UI

### Bug Reporting Flow

1. Customer clicks "Support Center" in client portal
2. Selects "Bug Report" ticket type
3. Fills out bug report form:
   - Summary (required)
   - Priority level
   - Detailed description (required)
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Screenshot upload
4. Submits ticket
5. Receives confirmation with ticket number (e.g., AURA-123)
6. Can track ticket status in "My Tickets" tab

### My Tickets Dashboard

- View all submitted tickets
- Filter by status (Open, In Progress, Resolved, Closed)
- Search tickets by title or description
- See current status and priority
- Click to view full details
- Link to view in Jira

## Admin UI

### Ticket Management Dashboard

1. **Statistics Overview**
   - 6 key metrics displayed at top
   - Total issues, open bugs, features, support tickets
   - High and critical priority counts
   - Updates in real-time

2. **Advanced Filtering**
   - Filter by issue type, status, priority
   - Filter by customer ID
   - Full-text search across all tickets
   - Combine multiple filters

3. **Ticket List**
   - Displays all matching tickets
   - Shows key information:
     - Ticket number and summary
     - Status and priority badges
     - Reporter and assignee
     - Creation and update dates
     - Customer-reported indicator

4. **Quick Actions**
   - **Analyze with AI**: Triggers Claude Code bug analysis
   - **Auto-Fix**: Generates fix and creates PR
   - **Manage**: Opens full ticket management modal
   - **View in Jira**: Opens ticket in Jira

5. **Ticket Management Modal**
   - Update ticket status
   - Assign to team members
   - Add public/internal comments
   - View full description and metadata

6. **Bug Analysis Modal**
   - Shows Claude Code AI analysis
   - Lists files to examine
   - Displays fix approach
   - Links to created pull request

## Best Practices

### For Customers

1. **Writing Good Bug Reports**
   - Use clear, descriptive titles
   - Include steps to reproduce
   - Specify expected vs actual behavior
   - Provide environment details (browser, OS)
   - Attach screenshots when helpful
   - Set appropriate priority

2. **Feature Requests**
   - Explain the business value
   - Describe your use case
   - Be specific about what you want
   - Set realistic priority

3. **Support Tickets**
   - Choose the correct category
   - Provide context and details
   - Include relevant account information

### For Admins

1. **Ticket Management**
   - Respond to tickets promptly
   - Update status regularly
   - Use internal comments for team communication
   - Keep customers informed with public comments

2. **Using Claude Code**
   - Use "Analyze with AI" for complex bugs
   - Review AI analysis before taking action
   - Use "Auto-Fix" for straightforward bugs
   - Always review generated pull requests
   - Run tests before merging

3. **Prioritization**
   - Critical: System down, data loss risk
   - High: Major functionality broken, many users affected
   - Medium: Important feature affected, workaround exists
   - Low: Minor issue, cosmetic problems

## Automation

### Automatic Analysis

High and Critical priority bugs are automatically analyzed by Claude Code:

1. Customer submits High/Critical bug
2. Jira ticket is created
3. Webhook triggers automatic analysis
4. Claude Code analyzes the bug
5. Analysis is added as internal comment
6. Admin is notified

### Scheduled Tasks

Set up these cron jobs for optimal performance:

```bash
# Check for stale tickets (daily at 9 AM)
0 9 * * * curl -X POST https://your-domain.com/api/jira/admin/check-stale-tickets

# Generate weekly reports (Monday at 8 AM)
0 8 * * 1 curl -X POST https://your-domain.com/api/jira/admin/weekly-report

# Sync ticket statistics (every hour)
0 * * * * curl -X POST https://your-domain.com/api/jira/admin/sync-stats
```

## Security

### Authentication

- All customer endpoints require valid JWT token
- Admin endpoints require admin-level JWT token
- Jira webhook validates signature

### Authorization

- Customers can only view their own tickets
- Admins can view all tickets
- Internal comments are hidden from customers
- Sensitive information is filtered from responses

### Rate Limiting

- Customer endpoints: 60 requests/minute per user
- Admin endpoints: 300 requests/minute per admin
- Webhook endpoint: 100 requests/minute

## Monitoring

### Key Metrics to Track

1. **Response Time**
   - Time from ticket creation to first response
   - Target: < 4 hours for Critical/High
   - Target: < 24 hours for Medium/Low

2. **Resolution Time**
   - Time from ticket creation to resolution
   - Target: < 24 hours for Critical
   - Target: < 72 hours for High
   - Target: < 1 week for Medium/Low

3. **Customer Satisfaction**
   - Track satisfaction ratings on closed tickets
   - Target: > 90% satisfied

4. **Claude Code Success Rate**
   - Percentage of AI-generated fixes that work
   - Track PRs created vs merged
   - Target: > 80% success rate

## Troubleshooting

### Issue: Bug reports not creating Jira tickets

**Possible causes:**
1. Jira API credentials incorrect
2. Jira project doesn't exist
3. Network connectivity issues

**Solution:**
```bash
# Test Jira connection
python -c "from app.jira_service import JiraService; js = JiraService(); print(js.test_connection())"
```

### Issue: Claude Code analysis failing

**Possible causes:**
1. Anthropic API key invalid
2. Rate limit exceeded
3. Codebase path incorrect

**Solution:**
```bash
# Test Claude API
python -c "from anthropic import Anthropic; c = Anthropic(); print(c.messages.create(model='claude-sonnet-4-20250514', max_tokens=10, messages=[{'role':'user','content':'test'}]))"
```

### Issue: Webhooks not triggering

**Possible causes:**
1. Webhook URL not publicly accessible
2. Webhook disabled in Jira
3. SSL certificate issues

**Solution:**
1. Check webhook configuration in Jira
2. Test webhook endpoint manually
3. Check webhook logs in Jira

## Support

For issues with the Jira integration:

1. Check the logs: `services/financial-analysis/logs/jira.log`
2. Verify environment variables are set correctly
3. Test Jira API connection
4. Check Claude Code API status
5. Review webhook configuration

## Future Enhancements

Planned improvements:

1. **Advanced Analytics**
   - Sentiment analysis on bug reports
   - Trend analysis for common issues
   - Predictive analytics for bug severity

2. **Enhanced AI Features**
   - Automatic duplicate detection
   - Smart assignment based on expertise
   - Auto-categorization of tickets

3. **Integration Improvements**
   - Slack notifications
   - Email notifications
   - Mobile app support

4. **Self-Service**
   - AI-powered chatbot for common issues
   - Knowledge base article suggestions
   - Community forum integration

## Conclusion

The Jira integration with Claude Code AI provides a powerful, automated customer support and bug tracking system. By combining traditional ticket management with AI-powered bug analysis and automated fixing, it significantly reduces response and resolution times while improving customer satisfaction.

Key benefits:
- ✅ Customers can easily report issues
- ✅ Automatic AI analysis of bugs
- ✅ Automated fix generation with PRs
- ✅ Comprehensive admin dashboard
- ✅ Real-time statistics and tracking
- ✅ Seamless Jira integration
