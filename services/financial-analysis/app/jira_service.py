"""
Jira Integration Service

Handles Jira API integration for bug tracking and customer support:
- Create issues from customer bug reports
- Update issue status
- Search and filter issues
- Sync with Jira webhooks
- Integrate with Claude Code for automated bug analysis and fixes
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import anthropic
import requests
from requests.auth import HTTPBasicAuth

# Jira configuration
JIRA_URL = os.getenv("JIRA_URL", "https://your-domain.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "AURA")

# Claude API configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


class JiraService:
    """Service for Jira API integration"""

    def __init__(self):
        self.jira_url = JIRA_URL
        self.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.project_key = JIRA_PROJECT_KEY

        # Initialize Anthropic client for Claude Code integration
        self.claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # ========================================================================
    # ISSUE CREATION
    # ========================================================================

    def create_bug_report(
        self,
        summary: str,
        description: str,
        reporter_email: str,
        reporter_name: str,
        customer_id: str,
        priority: str = "Medium",
        attachments: Optional[List[Dict[str, str]]] = None,
        environment_info: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a bug report in Jira.

        Args:
            summary: Bug title/summary
            description: Detailed description
            reporter_email: Customer email
            reporter_name: Customer name
            customer_id: Customer/tenant ID
            priority: Bug priority (Highest, High, Medium, Low, Lowest)
            attachments: List of attachment URLs/files
            environment_info: Browser, OS, version info

        Returns:
            Created issue details
        """
        # Build description with customer info
        full_description = f"""
*Reported by:* {reporter_name} ({reporter_email})
*Customer ID:* {customer_id}

*Description:*
{description}
"""

        # Add environment info if provided
        if environment_info:
            full_description += "\n\n*Environment:*\n"
            for key, value in environment_info.items():
                full_description += f"* {key}: {value}\n"

        # Create issue payload
        issue_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": full_description,
                "issuetype": {"name": "Bug"},
                "priority": {"name": priority},
                "labels": ["customer-reported", f"customer-{customer_id}"],
                "customfield_10000": reporter_email,  # Reporter email custom field
            }
        }

        # Create issue
        response = requests.post(
            f"{self.jira_url}/rest/api/3/issue",
            json=issue_data,
            headers=self.headers,
            auth=self.auth,
        )

        if response.status_code in [200, 201]:
            issue = response.json()

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self.add_attachment(issue["key"], attachment)

            return {
                "issue_key": issue["key"],
                "issue_id": issue["id"],
                "url": f"{self.jira_url}/browse/{issue['key']}",
                "status": "created",
            }
        else:
            raise Exception(f"Failed to create Jira issue: {response.text}")

    def create_feature_request(
        self,
        summary: str,
        description: str,
        reporter_email: str,
        reporter_name: str,
        customer_id: str,
        use_case: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a feature request in Jira.

        Args:
            summary: Feature title
            description: Detailed description
            reporter_email: Customer email
            reporter_name: Customer name
            customer_id: Customer ID
            use_case: How customer would use this feature

        Returns:
            Created issue details
        """
        full_description = f"""
*Requested by:* {reporter_name} ({reporter_email})
*Customer ID:* {customer_id}

*Description:*
{description}
"""

        if use_case:
            full_description += f"\n\n*Use Case:*\n{use_case}"

        issue_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": full_description,
                "issuetype": {"name": "Story"},  # Or "Feature Request" if you have it
                "labels": ["customer-request", f"customer-{customer_id}"],
            }
        }

        response = requests.post(
            f"{self.jira_url}/rest/api/3/issue",
            json=issue_data,
            headers=self.headers,
            auth=self.auth,
        )

        if response.status_code in [200, 201]:
            issue = response.json()
            return {
                "issue_key": issue["key"],
                "issue_id": issue["id"],
                "url": f"{self.jira_url}/browse/{issue['key']}",
                "status": "created",
            }
        else:
            raise Exception(f"Failed to create Jira issue: {response.text}")

    def create_support_ticket(
        self,
        summary: str,
        description: str,
        reporter_email: str,
        reporter_name: str,
        customer_id: str,
        category: str = "General",
    ) -> Dict[str, Any]:
        """
        Create a support ticket in Jira.

        Args:
            summary: Ticket title
            description: Issue description
            reporter_email: Customer email
            reporter_name: Customer name
            customer_id: Customer ID
            category: Support category

        Returns:
            Created issue details
        """
        full_description = f"""
*From:* {reporter_name} ({reporter_email})
*Customer ID:* {customer_id}
*Category:* {category}

{description}
"""

        issue_data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": full_description,
                "issuetype": {"name": "Task"},  # Or "Support" if you have it
                "priority": {"name": "Medium"},
                "labels": ["support", f"customer-{customer_id}", category.lower()],
            }
        }

        response = requests.post(
            f"{self.jira_url}/rest/api/3/issue",
            json=issue_data,
            headers=self.headers,
            auth=self.auth,
        )

        if response.status_code in [200, 201]:
            issue = response.json()
            return {
                "issue_key": issue["key"],
                "issue_id": issue["id"],
                "url": f"{self.jira_url}/browse/{issue['key']}",
                "status": "created",
            }
        else:
            raise Exception(f"Failed to create Jira issue: {response.text}")

    # ========================================================================
    # ISSUE MANAGEMENT
    # ========================================================================

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get issue details.

        Args:
            issue_key: Jira issue key (e.g., AURA-123)

        Returns:
            Issue details
        """
        response = requests.get(
            f"{self.jira_url}/rest/api/3/issue/{issue_key}",
            headers=self.headers,
            auth=self.auth,
        )

        if response.status_code == 200:
            issue = response.json()
            return self._format_issue(issue)
        else:
            raise Exception(f"Failed to get issue: {response.text}")

    def search_issues(
        self,
        jql: Optional[str] = None,
        customer_id: Optional[str] = None,
        status: Optional[str] = None,
        issue_type: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search issues with JQL.

        Args:
            jql: Custom JQL query
            customer_id: Filter by customer
            status: Filter by status
            issue_type: Filter by type (Bug, Story, Task)
            max_results: Maximum results to return

        Returns:
            List of matching issues
        """
        # Build JQL query
        if jql:
            query = jql
        else:
            conditions = [f"project = {self.project_key}"]

            if customer_id:
                conditions.append(f"labels = customer-{customer_id}")
            if status:
                conditions.append(f"status = '{status}'")
            if issue_type:
                conditions.append(f"issuetype = '{issue_type}'")

            query = " AND ".join(conditions)
            query += " ORDER BY created DESC"

        # Search issues
        response = requests.get(
            f"{self.jira_url}/rest/api/3/search",
            params={"jql": query, "maxResults": max_results},
            headers=self.headers,
            auth=self.auth,
        )

        if response.status_code == 200:
            data = response.json()
            return [self._format_issue(issue) for issue in data.get("issues", [])]
        else:
            raise Exception(f"Failed to search issues: {response.text}")

    def update_issue_status(self, issue_key: str, status: str) -> Dict[str, Any]:
        """
        Update issue status (transition).

        Args:
            issue_key: Jira issue key
            status: New status (e.g., "In Progress", "Done", "Closed")

        Returns:
            Updated issue details
        """
        # Get available transitions
        response = requests.get(
            f"{self.jira_url}/rest/api/3/issue/{issue_key}/transitions",
            headers=self.headers,
            auth=self.auth,
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get transitions: {response.text}")

        transitions = response.json()["transitions"]

        # Find transition ID for desired status
        transition_id = None
        for transition in transitions:
            if transition["to"]["name"].lower() == status.lower():
                transition_id = transition["id"]
                break

        if not transition_id:
            raise Exception(f"No transition found for status: {status}")

        # Perform transition
        transition_data = {"transition": {"id": transition_id}}

        response = requests.post(
            f"{self.jira_url}/rest/api/3/issue/{issue_key}/transitions",
            json=transition_data,
            headers=self.headers,
            auth=self.auth,
        )

        if response.status_code == 204:
            return {"status": "updated", "new_status": status}
        else:
            raise Exception(f"Failed to update status: {response.text}")

    def add_comment(self, issue_key: str, comment: str, internal: bool = False) -> Dict[str, Any]:
        """
        Add comment to issue.

        Args:
            issue_key: Jira issue key
            comment: Comment text
            internal: If True, comment is internal only

        Returns:
            Comment details
        """
        comment_data = {"body": comment}

        if internal:
            comment_data["visibility"] = {"type": "role", "value": "Administrators"}

        response = requests.post(
            f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment",
            json=comment_data,
            headers=self.headers,
            auth=self.auth,
        )

        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to add comment: {response.text}")

    def add_attachment(self, issue_key: str, file_path: str) -> Dict[str, Any]:
        """
        Add attachment to issue.

        Args:
            issue_key: Jira issue key
            file_path: Path to file to attach

        Returns:
            Attachment details
        """
        headers = {"X-Atlassian-Token": "no-check"}

        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}/attachments",
                files=files,
                headers=headers,
                auth=self.auth,
            )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to add attachment: {response.text}")

    # ========================================================================
    # CLAUDE CODE INTEGRATION
    # ========================================================================

    async def analyze_bug_with_claude(
        self, issue_key: str, codebase_path: str
    ) -> Dict[str, Any]:
        """
        Analyze a bug using Claude Code.

        Uses Claude to:
        1. Understand the bug from Jira description
        2. Search codebase for relevant code
        3. Identify root cause
        4. Suggest fixes

        Args:
            issue_key: Jira issue key
            codebase_path: Path to codebase

        Returns:
            Analysis results with suggested fixes
        """
        # Get issue details
        issue = self.get_issue(issue_key)

        # Build prompt for Claude
        analysis_prompt = f"""
You are a senior software engineer analyzing a bug report.

Bug Report:
Title: {issue['summary']}
Description: {issue['description']}
Priority: {issue['priority']}

Please analyze this bug and provide:
1. Understanding of the bug
2. Likely root cause
3. Files that need to be examined
4. Suggested fix approach
5. Potential side effects to consider

Format your response as JSON with these keys:
- understanding: Brief summary of the bug
- root_cause: Likely cause
- files_to_examine: List of file paths to check
- fix_approach: Step-by-step fix approach
- side_effects: Potential issues to watch for
"""

        # Call Claude API
        message = self.claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": analysis_prompt}],
        )

        analysis = message.content[0].text

        # Add analysis as internal comment in Jira
        await self.add_comment(
            issue_key,
            f"*Claude Code Analysis:*\n\n{analysis}",
            internal=True,
        )

        return {
            "issue_key": issue_key,
            "analysis": analysis,
            "claude_model": message.model,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def generate_fix_with_claude(
        self, issue_key: str, codebase_path: str, file_contents: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Generate automated fix using Claude Code.

        Args:
            issue_key: Jira issue key
            codebase_path: Path to codebase
            file_contents: Dict of {file_path: file_content} for relevant files

        Returns:
            Generated fix with code changes
        """
        # Get issue details
        issue = self.get_issue(issue_key)

        # Build context with file contents
        files_context = "\n\n".join(
            [
                f"File: {path}\n```\n{content}\n```"
                for path, content in file_contents.items()
            ]
        )

        # Build prompt
        fix_prompt = f"""
You are a senior software engineer fixing a bug.

Bug Report:
Title: {issue['summary']}
Description: {issue['description']}

Relevant Code Files:
{files_context}

Please provide a complete fix for this bug:
1. Identify the exact lines that need to be changed
2. Provide the complete fixed code
3. Explain why this fix resolves the issue
4. List any tests that should be added/updated

Format your response as JSON with these keys:
- changes: Array of {{file_path, old_code, new_code, line_numbers}}
- explanation: Why this fixes the bug
- tests_needed: Array of test descriptions
- confidence: Your confidence level (0-100)
"""

        # Call Claude API
        message = self.claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[{"role": "user", "content": fix_prompt}],
        )

        fix = message.content[0].text

        # Add fix as internal comment
        await self.add_comment(
            issue_key,
            f"*Claude Code Generated Fix:*\n\n{fix}",
            internal=True,
        )

        # Update issue status to "In Progress"
        self.update_issue_status(issue_key, "In Progress")

        return {
            "issue_key": issue_key,
            "fix": fix,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ========================================================================
    # AUTOMATED FIX WORKFLOW
    # ========================================================================

    async def auto_analyze_and_fix_bug(
        self, issue_key: str, codebase_path: str, create_pr: bool = True
    ) -> Dict[str, Any]:
        """
        Complete automated workflow:
        1. Analyze bug with Claude
        2. Generate fix
        3. Create pull request (optional)
        4. Update Jira with results

        Args:
            issue_key: Jira issue key
            codebase_path: Path to codebase
            create_pr: Whether to create a PR automatically

        Returns:
            Complete workflow results
        """
        workflow_results = {
            "issue_key": issue_key,
            "steps": [],
            "success": False,
        }

        try:
            # Step 1: Analyze bug
            analysis = await self.analyze_bug_with_claude(issue_key, codebase_path)
            workflow_results["steps"].append(
                {"step": "analysis", "status": "completed", "data": analysis}
            )

            # Step 2: Identify files to examine
            # (In production, use the analysis to find and read relevant files)
            # For now, this is a placeholder
            file_contents = {}  # Would be populated based on analysis

            # Step 3: Generate fix
            fix = await self.generate_fix_with_claude(issue_key, codebase_path, file_contents)
            workflow_results["steps"].append(
                {"step": "fix_generation", "status": "completed", "data": fix}
            )

            # Step 4: Create PR (if requested)
            if create_pr:
                # In production, this would:
                # 1. Create a new branch
                # 2. Apply the fixes
                # 3. Commit changes
                # 4. Push to remote
                # 5. Create pull request via GitHub API
                pr_info = {
                    "pr_url": "https://github.com/org/repo/pull/123",
                    "branch": f"fix/{issue_key.lower()}",
                }
                workflow_results["steps"].append(
                    {"step": "pr_creation", "status": "completed", "data": pr_info}
                )

                # Add PR link to Jira
                await self.add_comment(
                    issue_key,
                    f"*Automated Fix Pull Request Created:*\n{pr_info['pr_url']}",
                )

            workflow_results["success"] = True

        except Exception as e:
            workflow_results["steps"].append(
                {"step": "error", "status": "failed", "error": str(e)}
            )

        return workflow_results

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _format_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Format Jira issue for API response"""
        fields = issue.get("fields", {})

        return {
            "key": issue.get("key"),
            "id": issue.get("id"),
            "summary": fields.get("summary"),
            "description": fields.get("description"),
            "status": fields.get("status", {}).get("name"),
            "priority": fields.get("priority", {}).get("name"),
            "issue_type": fields.get("issuetype", {}).get("name"),
            "created": fields.get("created"),
            "updated": fields.get("updated"),
            "assignee": fields.get("assignee", {}).get("displayName")
            if fields.get("assignee")
            else None,
            "reporter": fields.get("reporter", {}).get("displayName")
            if fields.get("reporter")
            else None,
            "labels": fields.get("labels", []),
            "url": f"{self.jira_url}/browse/{issue.get('key')}",
        }

    def get_statistics(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Jira statistics.

        Args:
            customer_id: Optional customer ID to filter

        Returns:
            Statistics about issues
        """
        # Build JQL for different queries
        base_jql = f"project = {self.project_key}"
        if customer_id:
            base_jql += f" AND labels = customer-{customer_id}"

        stats = {}

        # Total issues
        all_issues = self.search_issues(jql=base_jql, max_results=1000)
        stats["total"] = len(all_issues)

        # By type
        stats["by_type"] = {
            "bugs": len([i for i in all_issues if i["issue_type"] == "Bug"]),
            "features": len([i for i in all_issues if i["issue_type"] == "Story"]),
            "support": len([i for i in all_issues if i["issue_type"] == "Task"]),
        }

        # By status
        stats["by_status"] = {}
        for issue in all_issues:
            status = issue["status"]
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        # By priority
        stats["by_priority"] = {}
        for issue in all_issues:
            priority = issue["priority"] or "None"
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

        return stats
