"""
Jira API Endpoints

FastAPI routes for Jira integration including:
- Customer bug reporting
- Feature requests
- Support tickets
- Issue management
- Claude Code automated bug analysis
- Webhook handling
"""

import os
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, UploadFile, File, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .jira_service import JiraService
from .permission_service import PermissionService
from .permissions_models import User, UserRole

router = APIRouter(prefix="/api/jira", tags=["Jira"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class BugReportRequest(BaseModel):
    """Customer bug report request"""

    summary: str
    description: str
    reporter_email: EmailStr
    customer_id: str
    priority: str = "Medium"
    environment: Optional[str] = None
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    screenshot_url: Optional[str] = None


class FeatureRequestRequest(BaseModel):
    """Feature request submission"""

    summary: str
    description: str
    requester_email: EmailStr
    customer_id: str
    priority: str = "Medium"
    business_value: Optional[str] = None
    use_case: Optional[str] = None


class SupportTicketRequest(BaseModel):
    """General support ticket"""

    summary: str
    description: str
    requester_email: EmailStr
    customer_id: str
    priority: str = "Medium"
    category: Optional[str] = None  # e.g., "technical", "billing", "training"


class AnalyzeBugRequest(BaseModel):
    """Request to analyze bug with Claude Code"""

    issue_key: str
    codebase_path: str = "/home/user/Data-Norm-2"
    auto_fix: bool = False
    create_pr: bool = False


class UpdateIssueRequest(BaseModel):
    """Update issue status or details"""

    status: Optional[str] = None
    assignee_email: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List[str]] = None


class AddCommentRequest(BaseModel):
    """Add comment to issue"""

    comment: str
    internal: bool = False


class IssueResponse(BaseModel):
    """Jira issue response"""

    key: str
    summary: str
    status: str
    priority: str
    created: str
    updated: str
    reporter: str
    assignee: Optional[str]
    description: str
    labels: List[str]
    url: str


class BugAnalysisResponse(BaseModel):
    """Claude Code bug analysis response"""

    issue_key: str
    analysis: str
    suggested_files: List[str]
    fix_approach: str
    pr_url: Optional[str] = None


# ============================================================================
# CUSTOMER-FACING ENDPOINTS
# ============================================================================


@router.post("/bug-report", response_model=IssueResponse)
async def submit_bug_report(
    request: BugReportRequest, session: AsyncSession = Depends(get_db)
):
    """
    Submit a bug report from a customer.

    This endpoint is called from the client portal when customers
    encounter bugs or issues with the platform.
    """
    # Create Jira service
    jira_service = JiraService()

    # Create bug report in Jira
    try:
        issue = jira_service.create_bug_report(
            summary=request.summary,
            description=request.description,
            reporter_email=request.reporter_email,
            customer_id=request.customer_id,
            priority=request.priority,
            environment=request.environment,
            steps_to_reproduce=request.steps_to_reproduce,
            expected_behavior=request.expected_behavior,
            actual_behavior=request.actual_behavior,
            screenshot_url=request.screenshot_url,
        )

        # Automatically trigger Claude analysis for high priority bugs
        if request.priority in ["High", "Critical"]:
            try:
                await jira_service.analyze_bug_with_claude(
                    issue_key=issue["key"], codebase_path="/home/user/Data-Norm-2"
                )
            except Exception as e:
                # Don't fail the bug report if analysis fails
                print(f"Failed to auto-analyze bug {issue['key']}: {e}")

        return IssueResponse(
            key=issue["key"],
            summary=issue["fields"]["summary"],
            status=issue["fields"]["status"]["name"],
            priority=issue["fields"]["priority"]["name"],
            created=issue["fields"]["created"],
            updated=issue["fields"]["updated"],
            reporter=issue["fields"]["reporter"]["emailAddress"],
            assignee=issue["fields"].get("assignee", {}).get("emailAddress") if issue["fields"].get("assignee") else None,
            description=issue["fields"]["description"],
            labels=issue["fields"]["labels"],
            url=f"{jira_service.jira_url}/browse/{issue['key']}",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bug report: {str(e)}")


@router.post("/feature-request", response_model=IssueResponse)
async def submit_feature_request(
    request: FeatureRequestRequest, session: AsyncSession = Depends(get_db)
):
    """
    Submit a feature request from a customer.

    Customers can suggest new features or enhancements to the platform.
    """
    # Create Jira service
    jira_service = JiraService()

    # Create feature request in Jira
    try:
        issue = jira_service.create_feature_request(
            summary=request.summary,
            description=request.description,
            requester_email=request.requester_email,
            customer_id=request.customer_id,
            priority=request.priority,
            business_value=request.business_value,
            use_case=request.use_case,
        )

        return IssueResponse(
            key=issue["key"],
            summary=issue["fields"]["summary"],
            status=issue["fields"]["status"]["name"],
            priority=issue["fields"]["priority"]["name"],
            created=issue["fields"]["created"],
            updated=issue["fields"]["updated"],
            reporter=issue["fields"]["reporter"]["emailAddress"],
            assignee=issue["fields"].get("assignee", {}).get("emailAddress") if issue["fields"].get("assignee") else None,
            description=issue["fields"]["description"],
            labels=issue["fields"]["labels"],
            url=f"{jira_service.jira_url}/browse/{issue['key']}",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create feature request: {str(e)}")


@router.post("/support-ticket", response_model=IssueResponse)
async def submit_support_ticket(
    request: SupportTicketRequest, session: AsyncSession = Depends(get_db)
):
    """
    Submit a general support ticket.

    For customer support issues like billing questions, training requests, etc.
    """
    # Create Jira service
    jira_service = JiraService()

    # Create support ticket in Jira
    try:
        issue = jira_service.create_support_ticket(
            summary=request.summary,
            description=request.description,
            requester_email=request.requester_email,
            customer_id=request.customer_id,
            priority=request.priority,
            category=request.category,
        )

        return IssueResponse(
            key=issue["key"],
            summary=issue["fields"]["summary"],
            status=issue["fields"]["status"]["name"],
            priority=issue["fields"]["priority"]["name"],
            created=issue["fields"]["created"],
            updated=issue["fields"]["updated"],
            reporter=issue["fields"]["reporter"]["emailAddress"],
            assignee=issue["fields"].get("assignee", {}).get("emailAddress") if issue["fields"].get("assignee") else None,
            description=issue["fields"]["description"],
            labels=issue["fields"]["labels"],
            url=f"{jira_service.jira_url}/browse/{issue['key']}",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create support ticket: {str(e)}")


@router.get("/my-tickets", response_model=List[IssueResponse])
async def get_my_tickets(
    email: EmailStr, customer_id: str, session: AsyncSession = Depends(get_db)
):
    """
    Get all tickets submitted by a customer user.

    Returns bugs, features, and support tickets from this customer.
    """
    # Create Jira service
    jira_service = JiraService()

    # Search for customer's tickets
    try:
        jql = f'reporter = "{email}" AND labels = "customer-{customer_id}" ORDER BY created DESC'
        issues = jira_service.search_issues(jql=jql, max_results=100)

        return [
            IssueResponse(
                key=issue["key"],
                summary=issue["fields"]["summary"],
                status=issue["fields"]["status"]["name"],
                priority=issue["fields"]["priority"]["name"],
                created=issue["fields"]["created"],
                updated=issue["fields"]["updated"],
                reporter=issue["fields"]["reporter"]["emailAddress"],
                assignee=issue["fields"].get("assignee", {}).get("emailAddress") if issue["fields"].get("assignee") else None,
                description=issue["fields"]["description"],
                labels=issue["fields"]["labels"],
                url=f"{jira_service.jira_url}/browse/{issue['key']}",
            )
            for issue in issues
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tickets: {str(e)}")


@router.get("/ticket/{issue_key}", response_model=IssueResponse)
async def get_ticket_details(issue_key: str, session: AsyncSession = Depends(get_db)):
    """
    Get details for a specific ticket.

    Customers can view their submitted tickets and track progress.
    """
    # Create Jira service
    jira_service = JiraService()

    # Get issue details
    try:
        issue = jira_service.get_issue(issue_key)

        return IssueResponse(
            key=issue["key"],
            summary=issue["fields"]["summary"],
            status=issue["fields"]["status"]["name"],
            priority=issue["fields"]["priority"]["name"],
            created=issue["fields"]["created"],
            updated=issue["fields"]["updated"],
            reporter=issue["fields"]["reporter"]["emailAddress"],
            assignee=issue["fields"].get("assignee", {}).get("emailAddress") if issue["fields"].get("assignee") else None,
            description=issue["fields"]["description"],
            labels=issue["fields"]["labels"],
            url=f"{jira_service.jira_url}/browse/{issue['key']}",
        )

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Ticket not found: {str(e)}")


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================


@router.get("/admin/issues", response_model=List[IssueResponse])
async def search_issues(
    jql: Optional[str] = None,
    issue_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    customer_id: Optional[str] = None,
    max_results: int = 50,
    session: AsyncSession = Depends(get_db),
):
    """
    Search and filter Jira issues for admin dashboard.

    Supports filtering by type, status, priority, and customer.
    """
    # Create Jira service
    jira_service = JiraService()

    # Build JQL query
    try:
        if not jql:
            filters = []
            if issue_type:
                filters.append(f'issuetype = "{issue_type}"')
            if status:
                filters.append(f'status = "{status}"')
            if priority:
                filters.append(f'priority = "{priority}"')
            if customer_id:
                filters.append(f'labels = "customer-{customer_id}"')

            jql = " AND ".join(filters) if filters else "project = AURA"
            jql += " ORDER BY created DESC"

        issues = jira_service.search_issues(jql=jql, max_results=max_results)

        return [
            IssueResponse(
                key=issue["key"],
                summary=issue["fields"]["summary"],
                status=issue["fields"]["status"]["name"],
                priority=issue["fields"]["priority"]["name"],
                created=issue["fields"]["created"],
                updated=issue["fields"]["updated"],
                reporter=issue["fields"]["reporter"]["emailAddress"],
                assignee=issue["fields"].get("assignee", {}).get("emailAddress") if issue["fields"].get("assignee") else None,
                description=issue["fields"]["description"],
                labels=issue["fields"]["labels"],
                url=f"{jira_service.jira_url}/browse/{issue['key']}",
            )
            for issue in issues
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search issues: {str(e)}")


@router.patch("/admin/issues/{issue_key}")
async def update_issue(
    issue_key: str, request: UpdateIssueRequest, session: AsyncSession = Depends(get_db)
):
    """
    Update issue status, assignee, or other fields.

    Admin users can manage tickets from the dashboard.
    """
    # Create Jira service
    jira_service = JiraService()

    try:
        # Update status if provided
        if request.status:
            jira_service.update_issue_status(issue_key, request.status)

        # Update other fields
        update_data = {}
        if request.assignee_email:
            update_data["assignee"] = {"emailAddress": request.assignee_email}
        if request.priority:
            update_data["priority"] = {"name": request.priority}
        if request.labels:
            update_data["labels"] = request.labels

        if update_data:
            jira_service.update_issue(issue_key, update_data)

        # Get updated issue
        issue = jira_service.get_issue(issue_key)

        return IssueResponse(
            key=issue["key"],
            summary=issue["fields"]["summary"],
            status=issue["fields"]["status"]["name"],
            priority=issue["fields"]["priority"]["name"],
            created=issue["fields"]["created"],
            updated=issue["fields"]["updated"],
            reporter=issue["fields"]["reporter"]["emailAddress"],
            assignee=issue["fields"].get("assignee", {}).get("emailAddress") if issue["fields"].get("assignee") else None,
            description=issue["fields"]["description"],
            labels=issue["fields"]["labels"],
            url=f"{jira_service.jira_url}/browse/{issue['key']}",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update issue: {str(e)}")


@router.post("/admin/issues/{issue_key}/comment")
async def add_comment_to_issue(
    issue_key: str, request: AddCommentRequest, session: AsyncSession = Depends(get_db)
):
    """
    Add a comment to an issue.

    Supports both public comments (visible to customer) and internal notes.
    """
    # Create Jira service
    jira_service = JiraService()

    try:
        comment_id = jira_service.add_comment(
            issue_key=issue_key, comment=request.comment, internal=request.internal
        )

        return {"comment_id": comment_id, "issue_key": issue_key, "internal": request.internal}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add comment: {str(e)}")


# ============================================================================
# CLAUDE CODE INTEGRATION ENDPOINTS
# ============================================================================


@router.post("/admin/analyze-bug", response_model=BugAnalysisResponse)
async def analyze_bug_with_claude(
    request: AnalyzeBugRequest, session: AsyncSession = Depends(get_db)
):
    """
    Analyze a bug using Claude Code AI.

    Provides automated analysis of the bug including:
    - Understanding of the issue
    - Root cause analysis
    - Files to examine
    - Suggested fix approach
    - Optionally generates and applies the fix
    """
    # Create Jira service
    jira_service = JiraService()

    try:
        if request.auto_fix:
            # Full automated workflow: analyze, fix, and create PR
            result = await jira_service.auto_analyze_and_fix_bug(
                issue_key=request.issue_key,
                codebase_path=request.codebase_path,
                create_pr=request.create_pr,
            )

            return BugAnalysisResponse(
                issue_key=request.issue_key,
                analysis=result["analysis"],
                suggested_files=result["files_to_examine"],
                fix_approach=result["fix_approach"],
                pr_url=result.get("pr_url"),
            )
        else:
            # Just analyze the bug
            analysis = await jira_service.analyze_bug_with_claude(
                issue_key=request.issue_key, codebase_path=request.codebase_path
            )

            return BugAnalysisResponse(
                issue_key=request.issue_key,
                analysis=analysis.get("understanding", ""),
                suggested_files=analysis.get("files_to_examine", []),
                fix_approach=analysis.get("fix_approach", ""),
                pr_url=None,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze bug: {str(e)}")


@router.post("/admin/generate-fix/{issue_key}")
async def generate_fix(
    issue_key: str,
    codebase_path: str = "/home/user/Data-Norm-2",
    create_pr: bool = False,
    session: AsyncSession = Depends(get_db),
):
    """
    Generate a fix for a bug using Claude Code.

    Optionally creates a pull request with the fix.
    """
    # Create Jira service
    jira_service = JiraService()

    try:
        # First get the issue to understand what files to read
        issue = jira_service.get_issue(issue_key)

        # Read relevant files (this would be smarter in production)
        # For now, we'll let Claude analyze and tell us what files to read
        result = await jira_service.auto_analyze_and_fix_bug(
            issue_key=issue_key, codebase_path=codebase_path, create_pr=create_pr
        )

        return {
            "issue_key": issue_key,
            "fix_generated": True,
            "files_modified": result.get("files_modified", []),
            "pr_url": result.get("pr_url"),
            "fix_summary": result.get("fix_explanation", ""),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate fix: {str(e)}")


# ============================================================================
# WEBHOOK ENDPOINT
# ============================================================================


@router.post("/webhook")
async def jira_webhook(request: Request, session: AsyncSession = Depends(get_db)):
    """
    Handle Jira webhook events.

    This endpoint receives events from Jira including:
    - issue_created
    - issue_updated
    - comment_created

    IMPORTANT: This endpoint must be publicly accessible and
    configured in your Jira settings under System > Webhooks.
    """
    # Get webhook payload
    payload = await request.json()

    # Create Jira service
    jira_service = JiraService()

    # Handle webhook event
    try:
        webhook_event = payload.get("webhookEvent")
        issue_key = payload.get("issue", {}).get("key")

        # Log the event
        print(f"Received Jira webhook: {webhook_event} for issue {issue_key}")

        # Handle specific events
        if webhook_event == "jira:issue_created":
            issue_type = payload.get("issue", {}).get("fields", {}).get("issuetype", {}).get("name")
            priority = payload.get("issue", {}).get("fields", {}).get("priority", {}).get("name")

            # Auto-analyze high priority bugs
            if issue_type == "Bug" and priority in ["High", "Critical"]:
                try:
                    await jira_service.analyze_bug_with_claude(
                        issue_key=issue_key, codebase_path="/home/user/Data-Norm-2"
                    )
                except Exception as e:
                    print(f"Failed to auto-analyze {issue_key}: {e}")

        elif webhook_event == "jira:issue_updated":
            # Could trigger re-analysis if issue details changed
            pass

        elif webhook_event == "comment_created":
            # Could trigger notifications or other actions
            pass

        return {"status": "success", "event": webhook_event, "issue_key": issue_key}

    except Exception as e:
        # Log error but return success to avoid Jira retries
        print(f"Error handling Jira webhook: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================


@router.get("/admin/stats")
async def get_jira_stats(session: AsyncSession = Depends(get_db)):
    """
    Get Jira statistics for admin dashboard.

    Returns counts of issues by type, status, priority, etc.
    """
    # Create Jira service
    jira_service = JiraService()

    try:
        # Get various issue counts
        stats = {
            "total_issues": len(jira_service.search_issues("project = AURA", max_results=1000)),
            "open_bugs": len(
                jira_service.search_issues(
                    'project = AURA AND issuetype = "Bug" AND status != "Done"', max_results=1000
                )
            ),
            "open_features": len(
                jira_service.search_issues(
                    'project = AURA AND issuetype = "Feature" AND status != "Done"',
                    max_results=1000,
                )
            ),
            "open_support": len(
                jira_service.search_issues(
                    'project = AURA AND issuetype = "Support" AND status != "Done"',
                    max_results=1000,
                )
            ),
            "high_priority": len(
                jira_service.search_issues(
                    'project = AURA AND priority = "High" AND status != "Done"', max_results=1000
                )
            ),
            "critical_priority": len(
                jira_service.search_issues(
                    'project = AURA AND priority = "Critical" AND status != "Done"',
                    max_results=1000,
                )
            ),
        }

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
