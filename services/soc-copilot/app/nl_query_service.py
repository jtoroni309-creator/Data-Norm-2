"""
Natural Language Query Service
================================
COMPETITIVE DIFFERENTIATOR #8: ChatGPT-like interface for audit analytics

Uses GPT-4 to convert natural language questions into SQL queries

Key Features:
- Natural language to SQL conversion
- Intent recognition and validation
- Safe SQL execution (read-only)
- Result summarization
- Query templates for common questions
"""

import logging
import json
import re
from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .config import settings

logger = logging.getLogger(__name__)


class NaturalLanguageQueryService:
    """
    Convert natural language questions into SQL queries and execute them
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.enabled = settings.ENABLE_AI_PLANNING and settings.OPENAI_API_KEY is not None

        # Database schema for AI context
        self.schema_description = """
Database Schema (PostgreSQL):

Core Tables:
- soc_copilot.soc_engagements: SOC engagements (id, client_name, engagement_type, report_type, status, review_period_start, review_period_end)
- soc_copilot.control_objectives: Control objectives (id, objective_code, objective_name, tsc_category, tsc_criteria)
- soc_copilot.controls: Controls (id, control_id, control_name, control_type, control_frequency)
- soc_copilot.test_plans: Test plans (id, engagement_id, control_id, test_type, sample_size, status)
- soc_copilot.test_results: Test results (id, test_plan_id, test_status, passed, test_date, tester_notes)
- soc_copilot.deviations: Deviations (id, test_result_id, severity, root_cause, remediation_status, remediation_due_date)
- soc_copilot.evidence: Evidence (id, engagement_id, evidence_type, file_name, collected_at)

Enums:
- engagement_status: DRAFT, PLANNING, FIELDWORK, REPORTING, REVIEW, SIGNED, DELIVERED
- test_status: NOT_STARTED, IN_PROGRESS, COMPLETED, BLOCKED
- deviation_severity: LOW, MEDIUM, HIGH, CRITICAL

Common Queries:
- Failed controls: SELECT * FROM controls WHERE id IN (SELECT control_id FROM test_results WHERE passed = false)
- High-risk deviations: SELECT * FROM deviations WHERE severity IN ('HIGH', 'CRITICAL')
- Testing progress: SELECT status, COUNT(*) FROM test_plans GROUP BY status
"""

        # Pre-built query templates
        self.query_templates = {
            "failed_controls": {
                "description": "List all controls that failed testing",
                "sql": """
                    SELECT DISTINCT c.control_id, c.control_name, c.control_type,
                           COUNT(tr.id) as failed_test_count
                    FROM soc_copilot.controls c
                    JOIN soc_copilot.test_plans tp ON c.id = tp.control_id
                    JOIN soc_copilot.test_results tr ON tp.id = tr.test_plan_id
                    WHERE tr.passed = false
                    GROUP BY c.id, c.control_id, c.control_name, c.control_type
                    ORDER BY failed_test_count DESC
                """,
                "example_question": "Show me all failed controls"
            },
            "high_risk_deviations": {
                "description": "List high and critical severity deviations",
                "sql": """
                    SELECT d.id, d.deviation_description, d.severity, d.root_cause,
                           d.remediation_status, d.remediation_due_date,
                           c.control_name
                    FROM soc_copilot.deviations d
                    JOIN soc_copilot.test_results tr ON d.test_result_id = tr.id
                    JOIN soc_copilot.test_plans tp ON tr.test_plan_id = tp.id
                    JOIN soc_copilot.controls c ON tp.control_id = c.id
                    WHERE d.severity IN ('HIGH', 'CRITICAL')
                    ORDER BY d.severity DESC, d.created_at DESC
                """,
                "example_question": "Show me all high-risk deviations"
            },
            "testing_progress": {
                "description": "Summary of testing completion",
                "sql": """
                    SELECT status, COUNT(*) as count,
                           ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
                    FROM soc_copilot.test_plans
                    GROUP BY status
                    ORDER BY count DESC
                """,
                "example_question": "What is the overall testing progress?"
            },
            "missing_evidence": {
                "description": "Identify missing or incomplete evidence",
                "sql": """
                    SELECT e.engagement_id, e.evidence_type, e.control_id,
                           c.control_name, e.status
                    FROM soc_copilot.evidence e
                    JOIN soc_copilot.controls c ON e.control_id = c.id
                    WHERE e.status IN ('PENDING', 'INCOMPLETE')
                    ORDER BY e.created_at ASC
                """,
                "example_question": "What evidence is missing or incomplete?"
            },
            "overdue_requests": {
                "description": "Evidence requests overdue from client",
                "sql": """
                    SELECT er.id, er.request_title, er.due_date, er.priority,
                           e.client_name,
                           DATE_PART('day', CURRENT_DATE - er.due_date) as days_overdue
                    FROM soc_copilot.evidence_requests er
                    JOIN soc_copilot.soc_engagements e ON er.engagement_id = e.id
                    WHERE er.status != 'COMPLETED'
                      AND er.due_date < CURRENT_DATE
                    ORDER BY days_overdue DESC
                """,
                "example_question": "Which evidence requests are overdue from the client?"
            },
            "security_controls_summary": {
                "description": "Summary of CC6 and CC7 security controls",
                "sql": """
                    SELECT co.objective_code, co.objective_name,
                           COUNT(DISTINCT c.id) as control_count,
                           COUNT(DISTINCT tp.id) as test_plan_count,
                           SUM(CASE WHEN tr.passed = true THEN 1 ELSE 0 END) as passed_tests,
                           SUM(CASE WHEN tr.passed = false THEN 1 ELSE 0 END) as failed_tests
                    FROM soc_copilot.control_objectives co
                    LEFT JOIN soc_copilot.controls c ON c.control_objective_id = co.id
                    LEFT JOIN soc_copilot.test_plans tp ON tp.control_id = c.id
                    LEFT JOIN soc_copilot.test_results tr ON tr.test_plan_id = tp.id
                    WHERE co.objective_code LIKE 'CC6.%' OR co.objective_code LIKE 'CC7.%'
                    GROUP BY co.id, co.objective_code, co.objective_name
                    ORDER BY co.objective_code
                """,
                "example_question": "Summarize all security controls (CC6 and CC7)"
            },
            "unresolved_deviations": {
                "description": "Deviations that haven't been remediated",
                "sql": """
                    SELECT d.id, d.deviation_description, d.severity,
                           d.remediation_status, d.remediation_due_date,
                           c.control_name,
                           DATE_PART('day', CURRENT_DATE - d.created_at) as days_open
                    FROM soc_copilot.deviations d
                    JOIN soc_copilot.test_results tr ON d.test_result_id = tr.id
                    JOIN soc_copilot.test_plans tp ON tr.test_plan_id = tp.id
                    JOIN soc_copilot.controls c ON tp.control_id = c.id
                    WHERE d.remediation_status != 'REMEDIATED'
                    ORDER BY d.severity DESC, days_open DESC
                """,
                "example_question": "Show me deviations that haven't been remediated"
            }
        }

    async def execute_nl_query(
        self,
        db: AsyncSession,
        user_query: str,
        engagement_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Execute natural language query

        Args:
            db: Database session
            user_query: Natural language question
            engagement_id: Optional filter by engagement
            user_id: User making the query

        Returns:
            Query results with AI summary
        """
        logger.info(f"Processing NL query: {user_query}")

        if not self.enabled:
            return self._handle_template_query(db, user_query, engagement_id)

        # Check if query matches a template
        template_match = self._match_query_template(user_query)
        if template_match:
            logger.info(f"Query matched template: {template_match}")
            return await self._execute_template_query(
                db, template_match, engagement_id, user_query, user_id
            )

        # Generate SQL using GPT-4
        sql_result = await self._generate_sql_from_nl(user_query, engagement_id)

        if sql_result.get("error"):
            return {
                "success": False,
                "error": sql_result["error"],
                "user_query": user_query
            }

        # Validate and sanitize SQL (security)
        if not self._is_safe_sql(sql_result["sql"]):
            return {
                "success": False,
                "error": "Query contains unsafe operations. Only SELECT queries are allowed.",
                "user_query": user_query
            }

        # Execute SQL
        try:
            result = await db.execute(text(sql_result["sql"]))
            rows = result.fetchall()
            columns = result.keys()

            # Convert to dict
            results = [dict(zip(columns, row)) for row in rows]

            # Generate AI summary
            summary = await self._generate_result_summary(user_query, results)

            response = {
                "success": True,
                "user_query": user_query,
                "interpreted_intent": sql_result.get("intent"),
                "sql_generated": sql_result["sql"],
                "results_count": len(results),
                "results": results[:100],  # Limit to 100 rows for display
                "summary": summary,
                "execution_time_ms": sql_result.get("processing_time_ms", 0)
            }

            # Log query for future training
            # TODO: Save to nl_query_history table

            return response

        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            return {
                "success": False,
                "error": f"Query execution failed: {str(e)}",
                "user_query": user_query,
                "sql_generated": sql_result["sql"]
            }

    async def get_query_suggestions(
        self,
        engagement_id: Optional[UUID] = None
    ) -> List[Dict[str, str]]:
        """
        Get suggested queries based on engagement context

        Returns:
            List of query suggestions
        """
        suggestions = []

        for template_name, template in self.query_templates.items():
            suggestions.append({
                "template_name": template_name,
                "description": template["description"],
                "example_question": template["example_question"]
            })

        return suggestions

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    async def _generate_sql_from_nl(
        self,
        user_query: str,
        engagement_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Use GPT-4 to convert natural language to SQL

        Args:
            user_query: Natural language question
            engagement_id: Optional engagement filter

        Returns:
            Generated SQL query with metadata
        """
        start_time = datetime.utcnow()

        try:
            prompt = f"""
Convert this natural language question into a SQL query.

Database Schema:
{self.schema_description}

User Question: {user_query}

{"Filter results to engagement_id = '" + str(engagement_id) + "'" if engagement_id else ""}

Requirements:
1. Use ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper JOIN syntax
3. Include appropriate WHERE clauses
4. Add ORDER BY for readability
5. Use table aliases for clarity
6. Schema is 'soc_copilot'

Return as JSON with keys:
- intent: Brief description of what the query does
- sql: The SQL query
- explanation: Human-readable explanation of the query logic
"""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a PostgreSQL expert. Convert natural language to SQL. Only generate safe SELECT queries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            result["processing_time_ms"] = int(processing_time)
            return result

        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return {
                "error": f"Failed to generate SQL: {str(e)}"
            }

    async def _generate_result_summary(
        self,
        user_query: str,
        results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate AI summary of query results

        Args:
            user_query: Original question
            results: Query results

        Returns:
            Natural language summary
        """
        if not self.enabled or not results:
            return f"Found {len(results)} results"

        try:
            # Limit data sent to GPT (cost optimization)
            sample_results = results[:10] if len(results) > 10 else results

            prompt = f"""
Summarize these query results in 2-3 sentences.

Original Question: {user_query}
Results: {json.dumps(sample_results, default=str)}
Total Results: {len(results)}

Provide a concise, actionable summary highlighting key findings.
"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an audit expert summarizing query results."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"Found {len(results)} results"

    def _match_query_template(self, user_query: str) -> Optional[str]:
        """
        Match user query to pre-built template

        Args:
            user_query: Natural language query

        Returns:
            Template name if matched, None otherwise
        """
        query_lower = user_query.lower()

        # Simple keyword matching (can be enhanced with ML)
        if any(word in query_lower for word in ["failed", "fail", "failing"]) and "control" in query_lower:
            return "failed_controls"

        if any(word in query_lower for word in ["high risk", "critical", "severe"]) and "deviation" in query_lower:
            return "high_risk_deviations"

        if any(word in query_lower for word in ["progress", "completion", "status"]) and "test" in query_lower:
            return "testing_progress"

        if any(word in query_lower for word in ["missing", "incomplete"]) and "evidence" in query_lower:
            return "missing_evidence"

        if "overdue" in query_lower:
            return "overdue_requests"

        if any(word in query_lower for word in ["cc6", "cc7", "security control"]):
            return "security_controls_summary"

        if any(word in query_lower for word in ["unresolved", "not remediated", "open"]) and "deviation" in query_lower:
            return "unresolved_deviations"

        return None

    async def _execute_template_query(
        self,
        db: AsyncSession,
        template_name: str,
        engagement_id: Optional[UUID],
        user_query: str,
        user_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Execute a pre-built template query"""

        template = self.query_templates[template_name]
        sql = template["sql"]

        # Add engagement filter if provided
        if engagement_id:
            # Simple approach: add WHERE clause if not exists
            if "WHERE" not in sql.upper():
                sql = sql.replace("FROM soc_copilot.soc_engagements", f"FROM soc_copilot.soc_engagements WHERE id = '{engagement_id}'")

        try:
            result = await db.execute(text(sql))
            rows = result.fetchall()
            columns = result.keys()

            results = [dict(zip(columns, row)) for row in rows]

            return {
                "success": True,
                "user_query": user_query,
                "template_used": template_name,
                "interpreted_intent": template["description"],
                "results_count": len(results),
                "results": results[:100],
                "summary": f"Found {len(results)} results for {template['description']}"
            }

        except Exception as e:
            logger.error(f"Template query execution failed: {e}")
            return {
                "success": False,
                "error": f"Query failed: {str(e)}",
                "template_used": template_name
            }

    def _is_safe_sql(self, sql: str) -> bool:
        """
        Validate SQL is safe (read-only SELECT)

        Args:
            sql: SQL query to validate

        Returns:
            True if safe, False otherwise
        """
        sql_upper = sql.upper().strip()

        # Must start with SELECT
        if not sql_upper.startswith("SELECT"):
            return False

        # Forbidden keywords
        forbidden = [
            "INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER",
            "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE", "CALL",
            "DECLARE", "CURSOR", "TRANSACTION", "COMMIT", "ROLLBACK"
        ]

        for keyword in forbidden:
            if keyword in sql_upper:
                return False

        # Check for SQL injection patterns
        injection_patterns = [
            r";\s*(DROP|DELETE|UPDATE|INSERT)",
            r"--",
            r"/\*",
            r"\*/",
            r"UNION\s+SELECT",
            r"OR\s+1\s*=\s*1",
            r"OR\s+TRUE"
        ]

        for pattern in injection_patterns:
            if re.search(pattern, sql_upper):
                return False

        return True

    def _handle_template_query(
        self,
        db: AsyncSession,
        user_query: str,
        engagement_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Fallback when AI is disabled - use templates only"""

        template_match = self._match_query_template(user_query)

        if template_match:
            # Would execute template, but async not available here
            return {
                "success": False,
                "error": "AI features disabled. Please enable OpenAI API key.",
                "suggestion": f"Your query matches template: {template_match}"
            }

        return {
            "success": False,
            "error": "AI features disabled and query doesn't match any template.",
            "available_templates": list(self.query_templates.keys())
        }


# Global instance
nl_query_service = NaturalLanguageQueryService()
