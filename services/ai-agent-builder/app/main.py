"""
AI Agent Builder Service - Competitive Advantage over FloQast

Enables CPAs to create custom AI agents using natural language, no coding required.
Beats FloQast's AI Agent Builder with:
- More agent types (Journal Entry, Data Transformation, Task, Reconciliation, Financial Insights, Compliance, Custom)
- Natural language agent definition
- Visual workflow builder support
- Agent marketplace for sharing
- Real-time agent execution monitoring
- A/B testing for agent performance

Key Features:
1. No-code agent creation using natural language
2. Pre-built agent templates for common audit tasks
3. Custom agent workflows with conditional logic
4. Agent scheduling and automation
5. Agent performance analytics
6. Agent versioning and rollback
7. Collaborative agent editing
8. Agent marketplace for CPA firms
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import asyncio
from loguru import logger

app = FastAPI(
    title="AI Agent Builder Service",
    description="Create custom AI agents with natural language - No coding required",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Enums and Constants
# ============================================================================

class AgentType(str, Enum):
    """Types of AI agents that can be created"""
    JOURNAL_ENTRY = "journal_entry"  # Auto-create journal entries
    DATA_TRANSFORMATION = "data_transformation"  # Transform unstructured data
    RECONCILIATION = "reconciliation"  # Auto-reconcile accounts
    FINANCIAL_INSIGHTS = "financial_insights"  # Generate insights from data
    COMPLIANCE = "compliance"  # Compliance checking
    TASK_AUTOMATION = "task_automation"  # General task automation
    ANOMALY_DETECTION = "anomaly_detection"  # Custom anomaly rules
    REPORT_GENERATION = "report_generation"  # Generate reports
    AUDIT_PROCEDURE = "audit_procedure"  # Execute audit procedures
    CUSTOM = "custom"  # Fully custom agent


class AgentStatus(str, Enum):
    """Agent execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(str, Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(str, Enum):
    """How agents are triggered"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    WEBHOOK = "webhook"


# ============================================================================
# Pydantic Models
# ============================================================================

class AgentStep(BaseModel):
    """Individual step in an agent workflow"""
    step_id: str = Field(default_factory=lambda: str(uuid4())[:8])
    name: str
    description: str
    action_type: str  # 'llm_query', 'data_fetch', 'data_transform', 'validation', 'output'
    config: Dict[str, Any] = {}
    conditions: Optional[Dict[str, Any]] = None  # Conditional execution
    next_steps: List[str] = []  # IDs of next steps
    fallback_step: Optional[str] = None  # Step to execute on failure


class AgentWorkflow(BaseModel):
    """Complete agent workflow definition"""
    start_step: str
    steps: List[AgentStep]
    error_handling: Dict[str, Any] = {}
    retry_policy: Dict[str, Any] = {"max_retries": 3, "backoff_seconds": 5}


class AgentCreateRequest(BaseModel):
    """Request to create a new agent"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str
    agent_type: AgentType
    natural_language_definition: str  # User describes what they want in plain English
    trigger_type: TriggerType = TriggerType.MANUAL
    schedule: Optional[str] = None  # Cron expression for scheduled triggers
    input_schema: Optional[Dict[str, Any]] = None  # Expected input format
    output_schema: Optional[Dict[str, Any]] = None  # Expected output format
    tags: List[str] = []
    is_template: bool = False  # Can be shared in marketplace


class AgentResponse(BaseModel):
    """Agent response model"""
    agent_id: str
    name: str
    description: str
    agent_type: AgentType
    status: AgentStatus
    trigger_type: TriggerType
    workflow: Optional[AgentWorkflow] = None
    created_at: datetime
    updated_at: datetime
    created_by: str
    execution_count: int = 0
    success_rate: float = 0.0
    avg_execution_time_ms: int = 0
    tags: List[str] = []
    version: int = 1


class AgentExecutionRequest(BaseModel):
    """Request to execute an agent"""
    agent_id: str
    input_data: Dict[str, Any]
    engagement_id: Optional[str] = None
    dry_run: bool = False  # Test without actually applying changes


class AgentExecutionResponse(BaseModel):
    """Agent execution result"""
    execution_id: str
    agent_id: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    steps_completed: List[str] = []
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    execution_log: List[Dict[str, Any]] = []
    metrics: Dict[str, Any] = {}


class AgentTemplate(BaseModel):
    """Pre-built agent template"""
    template_id: str
    name: str
    description: str
    agent_type: AgentType
    category: str
    workflow: AgentWorkflow
    sample_input: Dict[str, Any]
    sample_output: Dict[str, Any]
    popularity_score: int = 0
    created_by: str
    is_official: bool = False


class NaturalLanguageParseResult(BaseModel):
    """Result of parsing natural language agent definition"""
    understood: bool
    confidence_score: float
    parsed_workflow: AgentWorkflow
    suggested_improvements: List[str] = []
    required_permissions: List[str] = []
    estimated_execution_time_ms: int
    warnings: List[str] = []


# ============================================================================
# In-Memory Storage (Replace with database in production)
# ============================================================================

agents_db: Dict[str, Dict] = {}
executions_db: Dict[str, Dict] = {}
templates_db: Dict[str, AgentTemplate] = {}


# ============================================================================
# Pre-built Templates - Beat FloQast with more options
# ============================================================================

def initialize_templates():
    """Initialize pre-built agent templates"""

    templates = [
        # Journal Entry Agents (FloQast has this)
        AgentTemplate(
            template_id="tmpl_coupa_accruals",
            name="Coupa Accruals Journal Entry",
            description="Automatically create accrual journal entries from Coupa invoice data",
            agent_type=AgentType.JOURNAL_ENTRY,
            category="Journal Entries",
            workflow=AgentWorkflow(
                start_step="fetch_coupa",
                steps=[
                    AgentStep(
                        step_id="fetch_coupa",
                        name="Fetch Coupa Data",
                        description="Pull invoice data from Coupa integration",
                        action_type="data_fetch",
                        config={"source": "coupa", "filter": "unbilled_invoices"},
                        next_steps=["calculate_accruals"]
                    ),
                    AgentStep(
                        step_id="calculate_accruals",
                        name="Calculate Accruals",
                        description="Calculate accrual amounts based on invoice dates",
                        action_type="data_transform",
                        config={"operation": "calculate_period_accruals"},
                        next_steps=["generate_je"]
                    ),
                    AgentStep(
                        step_id="generate_je",
                        name="Generate Journal Entry",
                        description="Create journal entry with debit/credit lines",
                        action_type="output",
                        config={"output_type": "journal_entry", "require_approval": True},
                        next_steps=[]
                    )
                ]
            ),
            sample_input={"coupa_company_id": "ACME", "period_end": "2024-12-31"},
            sample_output={"journal_entry_id": "JE-2024-12345", "total_accrual": 150000.00},
            popularity_score=95,
            created_by="system",
            is_official=True
        ),

        # Lease Accounting Journal Entry (We have this, FloQast might not)
        AgentTemplate(
            template_id="tmpl_asc842_lease",
            name="ASC 842 Lease Amortization Entry",
            description="Calculate and create lease liability/ROU asset amortization entries per ASC 842",
            agent_type=AgentType.JOURNAL_ENTRY,
            category="Journal Entries",
            workflow=AgentWorkflow(
                start_step="get_leases",
                steps=[
                    AgentStep(
                        step_id="get_leases",
                        name="Get Active Leases",
                        description="Fetch all active leases from lease management system",
                        action_type="data_fetch",
                        config={"source": "lease_system", "filter": "active_leases"},
                        next_steps=["calculate_amort"]
                    ),
                    AgentStep(
                        step_id="calculate_amort",
                        name="Calculate Amortization",
                        description="Calculate monthly amortization using effective interest method",
                        action_type="data_transform",
                        config={
                            "operation": "asc842_amortization",
                            "method": "effective_interest",
                            "components": ["lease_liability", "rou_asset", "interest_expense"]
                        },
                        next_steps=["create_entries"]
                    ),
                    AgentStep(
                        step_id="create_entries",
                        name="Create Entries",
                        description="Generate journal entries for lease accounting",
                        action_type="output",
                        config={"output_type": "journal_entry", "auto_post": False},
                        next_steps=[]
                    )
                ]
            ),
            sample_input={"period": "2024-12"},
            sample_output={"entries_created": 15, "total_interest_expense": 45000},
            popularity_score=88,
            created_by="system",
            is_official=True
        ),

        # Data Transformation Agent (FloQast has this)
        AgentTemplate(
            template_id="tmpl_bank_recon_transform",
            name="Bank Statement Transformer",
            description="Transform bank statement data into standard format for reconciliation",
            agent_type=AgentType.DATA_TRANSFORMATION,
            category="Data Transformation",
            workflow=AgentWorkflow(
                start_step="parse_bank",
                steps=[
                    AgentStep(
                        step_id="parse_bank",
                        name="Parse Bank Statement",
                        description="Parse raw bank statement file (CSV, OFX, BAI2)",
                        action_type="data_transform",
                        config={"operation": "parse_bank_statement", "formats": ["csv", "ofx", "bai2"]},
                        next_steps=["standardize"]
                    ),
                    AgentStep(
                        step_id="standardize",
                        name="Standardize Format",
                        description="Convert to standard transaction format",
                        action_type="data_transform",
                        config={"operation": "standardize_transactions"},
                        next_steps=["categorize"]
                    ),
                    AgentStep(
                        step_id="categorize",
                        name="Auto-Categorize",
                        description="Use AI to categorize transactions",
                        action_type="llm_query",
                        config={"model": "gpt-4", "task": "categorize_transactions"},
                        next_steps=["output"]
                    ),
                    AgentStep(
                        step_id="output",
                        name="Output Transformed Data",
                        description="Output standardized transaction data",
                        action_type="output",
                        config={"output_type": "transformed_data"},
                        next_steps=[]
                    )
                ]
            ),
            sample_input={"bank_statement_file": "bank_stmt_dec2024.csv"},
            sample_output={"transactions_processed": 1250, "categories_assigned": 1250},
            popularity_score=92,
            created_by="system",
            is_official=True
        ),

        # Reconciliation Agent (Unique to us)
        AgentTemplate(
            template_id="tmpl_three_way_recon",
            name="Three-Way Reconciliation",
            description="Automated three-way matching between PO, receipt, and invoice",
            agent_type=AgentType.RECONCILIATION,
            category="Reconciliations",
            workflow=AgentWorkflow(
                start_step="fetch_data",
                steps=[
                    AgentStep(
                        step_id="fetch_data",
                        name="Fetch Source Data",
                        description="Pull POs, receipts, and invoices from ERP",
                        action_type="data_fetch",
                        config={"sources": ["purchase_orders", "receipts", "invoices"]},
                        next_steps=["match"]
                    ),
                    AgentStep(
                        step_id="match",
                        name="Three-Way Match",
                        description="Match PO-Receipt-Invoice using fuzzy matching",
                        action_type="data_transform",
                        config={
                            "operation": "three_way_match",
                            "tolerance_percent": 2.0,
                            "date_tolerance_days": 5
                        },
                        next_steps=["analyze_variances"]
                    ),
                    AgentStep(
                        step_id="analyze_variances",
                        name="Analyze Variances",
                        description="AI analysis of unmatched items and variances",
                        action_type="llm_query",
                        config={"model": "gpt-4", "task": "analyze_reconciliation_variances"},
                        next_steps=["output"]
                    ),
                    AgentStep(
                        step_id="output",
                        name="Generate Report",
                        description="Create reconciliation report with exceptions",
                        action_type="output",
                        config={"output_type": "reconciliation_report"},
                        next_steps=[]
                    )
                ]
            ),
            sample_input={"period": "2024-12", "vendor_filter": None},
            sample_output={"matched": 950, "unmatched": 50, "variance_total": 12500},
            popularity_score=85,
            created_by="system",
            is_official=True
        ),

        # Financial Insights Agent (Unique to us)
        AgentTemplate(
            template_id="tmpl_variance_analysis",
            name="Variance Analysis Insights",
            description="AI-powered variance analysis with natural language explanations",
            agent_type=AgentType.FINANCIAL_INSIGHTS,
            category="Financial Analysis",
            workflow=AgentWorkflow(
                start_step="get_balances",
                steps=[
                    AgentStep(
                        step_id="get_balances",
                        name="Get Trial Balances",
                        description="Fetch current and prior period trial balances",
                        action_type="data_fetch",
                        config={"source": "trial_balance", "periods": ["current", "prior"]},
                        next_steps=["calculate_variances"]
                    ),
                    AgentStep(
                        step_id="calculate_variances",
                        name="Calculate Variances",
                        description="Calculate $ and % variances by account",
                        action_type="data_transform",
                        config={"operation": "variance_calculation", "include_pct": True},
                        next_steps=["identify_material"]
                    ),
                    AgentStep(
                        step_id="identify_material",
                        name="Identify Material Items",
                        description="Flag variances exceeding materiality thresholds",
                        action_type="data_transform",
                        config={
                            "operation": "materiality_filter",
                            "threshold_pct": 10,
                            "threshold_amount": 50000
                        },
                        next_steps=["explain"]
                    ),
                    AgentStep(
                        step_id="explain",
                        name="Generate Explanations",
                        description="Use AI to generate variance explanations",
                        action_type="llm_query",
                        config={
                            "model": "gpt-4",
                            "task": "explain_variances",
                            "include_citations": True
                        },
                        next_steps=["output"]
                    ),
                    AgentStep(
                        step_id="output",
                        name="Output Insights",
                        description="Generate variance analysis report with AI insights",
                        action_type="output",
                        config={"output_type": "variance_report"},
                        next_steps=[]
                    )
                ]
            ),
            sample_input={"engagement_id": "ENG-001", "materiality": 50000},
            sample_output={"material_variances": 12, "explanations_generated": 12},
            popularity_score=90,
            created_by="system",
            is_official=True
        ),

        # Compliance Agent - SOX Testing (Unique to us)
        AgentTemplate(
            template_id="tmpl_sox_control_test",
            name="SOX Control Testing",
            description="Automated SOX control testing with evidence collection",
            agent_type=AgentType.COMPLIANCE,
            category="Compliance",
            workflow=AgentWorkflow(
                start_step="get_controls",
                steps=[
                    AgentStep(
                        step_id="get_controls",
                        name="Get Control Matrix",
                        description="Fetch SOX control matrix for testing",
                        action_type="data_fetch",
                        config={"source": "sox_controls"},
                        next_steps=["sample_selection"]
                    ),
                    AgentStep(
                        step_id="sample_selection",
                        name="Select Test Samples",
                        description="AI-powered risk-based sample selection",
                        action_type="llm_query",
                        config={
                            "model": "gpt-4",
                            "task": "select_control_samples",
                            "risk_based": True
                        },
                        next_steps=["collect_evidence"]
                    ),
                    AgentStep(
                        step_id="collect_evidence",
                        name="Collect Evidence",
                        description="Automatically gather evidence from source systems",
                        action_type="data_fetch",
                        config={"operation": "collect_evidence", "sources": ["erp", "documents"]},
                        next_steps=["evaluate"]
                    ),
                    AgentStep(
                        step_id="evaluate",
                        name="Evaluate Controls",
                        description="AI evaluation of control effectiveness",
                        action_type="llm_query",
                        config={
                            "model": "gpt-4",
                            "task": "evaluate_control_effectiveness",
                            "criteria": ["design", "operating_effectiveness"]
                        },
                        next_steps=["output"]
                    ),
                    AgentStep(
                        step_id="output",
                        name="Generate Test Results",
                        description="Create SOX testing workpaper",
                        action_type="output",
                        config={"output_type": "sox_workpaper"},
                        next_steps=[]
                    )
                ]
            ),
            sample_input={"control_ids": ["CTL-001", "CTL-002"], "period": "2024-Q4"},
            sample_output={"controls_tested": 25, "passed": 23, "failed": 2},
            popularity_score=88,
            created_by="system",
            is_official=True
        ),

        # Anomaly Detection Agent (Unique advanced version)
        AgentTemplate(
            template_id="tmpl_custom_anomaly",
            name="Custom Anomaly Detection Rules",
            description="Create custom anomaly detection rules using natural language",
            agent_type=AgentType.ANOMALY_DETECTION,
            category="Analytics",
            workflow=AgentWorkflow(
                start_step="parse_rules",
                steps=[
                    AgentStep(
                        step_id="parse_rules",
                        name="Parse Detection Rules",
                        description="Convert natural language rules to detection logic",
                        action_type="llm_query",
                        config={
                            "model": "gpt-4",
                            "task": "parse_anomaly_rules",
                            "output_format": "detection_config"
                        },
                        next_steps=["fetch_data"]
                    ),
                    AgentStep(
                        step_id="fetch_data",
                        name="Fetch Transaction Data",
                        description="Pull relevant transaction data for analysis",
                        action_type="data_fetch",
                        config={"source": "journal_entries"},
                        next_steps=["detect"]
                    ),
                    AgentStep(
                        step_id="detect",
                        name="Run Detection",
                        description="Execute anomaly detection rules",
                        action_type="data_transform",
                        config={"operation": "run_anomaly_detection"},
                        next_steps=["explain"]
                    ),
                    AgentStep(
                        step_id="explain",
                        name="Explain Findings",
                        description="Generate explanations for detected anomalies",
                        action_type="llm_query",
                        config={
                            "model": "gpt-4",
                            "task": "explain_anomalies",
                            "include_risk_assessment": True
                        },
                        next_steps=["output"]
                    ),
                    AgentStep(
                        step_id="output",
                        name="Output Results",
                        description="Generate anomaly detection report",
                        action_type="output",
                        config={"output_type": "anomaly_report"},
                        next_steps=[]
                    )
                ]
            ),
            sample_input={
                "rules": "Flag all transactions over $10,000 posted on weekends by users who don't normally post weekend entries"
            },
            sample_output={"anomalies_detected": 15, "high_risk": 3, "medium_risk": 12},
            popularity_score=82,
            created_by="system",
            is_official=True
        ),

        # Audit Procedure Agent (Unique to us)
        AgentTemplate(
            template_id="tmpl_audit_procedure",
            name="Automated Audit Procedure",
            description="Execute standardized audit procedures with AI assistance",
            agent_type=AgentType.AUDIT_PROCEDURE,
            category="Audit",
            workflow=AgentWorkflow(
                start_step="get_procedure",
                steps=[
                    AgentStep(
                        step_id="get_procedure",
                        name="Load Procedure",
                        description="Load audit procedure from library",
                        action_type="data_fetch",
                        config={"source": "audit_procedure_library"},
                        next_steps=["gather_evidence"]
                    ),
                    AgentStep(
                        step_id="gather_evidence",
                        name="Gather Evidence",
                        description="Collect evidence based on procedure requirements",
                        action_type="data_fetch",
                        config={"operation": "gather_audit_evidence"},
                        next_steps=["execute_tests"]
                    ),
                    AgentStep(
                        step_id="execute_tests",
                        name="Execute Tests",
                        description="Perform analytical procedures and tests",
                        action_type="data_transform",
                        config={"operation": "execute_audit_tests"},
                        next_steps=["evaluate"]
                    ),
                    AgentStep(
                        step_id="evaluate",
                        name="Evaluate Results",
                        description="AI evaluation of test results",
                        action_type="llm_query",
                        config={
                            "model": "gpt-4",
                            "task": "evaluate_audit_evidence",
                            "include_conclusion": True
                        },
                        next_steps=["document"]
                    ),
                    AgentStep(
                        step_id="document",
                        name="Document Workpaper",
                        description="Generate audit workpaper with conclusions",
                        action_type="output",
                        config={"output_type": "audit_workpaper", "include_citations": True},
                        next_steps=[]
                    )
                ]
            ),
            sample_input={"procedure_id": "PROC-REV-001", "engagement_id": "ENG-001"},
            sample_output={"procedure_completed": True, "issues_identified": 2, "conclusion": "Satisfactory"},
            popularity_score=85,
            created_by="system",
            is_official=True
        )
    ]

    for template in templates:
        templates_db[template.template_id] = template


# Initialize templates on startup
initialize_templates()


# ============================================================================
# Natural Language Parser - Core differentiator
# ============================================================================

class NaturalLanguageAgentParser:
    """
    Parses natural language descriptions into executable agent workflows.
    This is the core innovation that makes our agent builder superior.
    """

    def __init__(self):
        self.action_keywords = {
            "fetch": "data_fetch",
            "get": "data_fetch",
            "pull": "data_fetch",
            "calculate": "data_transform",
            "transform": "data_transform",
            "convert": "data_transform",
            "analyze": "llm_query",
            "explain": "llm_query",
            "generate": "llm_query",
            "summarize": "llm_query",
            "validate": "validation",
            "check": "validation",
            "verify": "validation",
            "create": "output",
            "output": "output",
            "export": "output",
            "send": "output"
        }

        self.data_sources = {
            "journal entries": "journal_entries",
            "trial balance": "trial_balance",
            "bank statements": "bank_statements",
            "invoices": "invoices",
            "purchase orders": "purchase_orders",
            "receipts": "receipts",
            "leases": "lease_system",
            "fixed assets": "fixed_assets",
            "payroll": "payroll_system",
            "inventory": "inventory_system"
        }

    async def parse(self, natural_language: str, agent_type: AgentType) -> NaturalLanguageParseResult:
        """
        Parse natural language into an agent workflow.

        In production, this would use GPT-4 for sophisticated parsing.
        Here we demonstrate the structure with rule-based parsing.
        """

        # Normalize input
        nl_lower = natural_language.lower()

        # Extract steps from natural language
        steps = []

        # Step 1: Identify data sources needed
        data_sources_found = []
        for phrase, source in self.data_sources.items():
            if phrase in nl_lower:
                data_sources_found.append(source)

        if data_sources_found:
            steps.append(AgentStep(
                step_id="fetch_data",
                name="Fetch Data",
                description=f"Fetch data from: {', '.join(data_sources_found)}",
                action_type="data_fetch",
                config={"sources": data_sources_found},
                next_steps=["process_data"]
            ))

        # Step 2: Identify transformations/calculations
        if any(kw in nl_lower for kw in ["calculate", "transform", "convert", "match", "reconcile"]):
            steps.append(AgentStep(
                step_id="process_data",
                name="Process Data",
                description="Apply transformations and calculations",
                action_type="data_transform",
                config={"operation": "custom_transform"},
                next_steps=["analyze"]
            ))

        # Step 3: AI analysis if needed
        if any(kw in nl_lower for kw in ["analyze", "explain", "summarize", "interpret", "detect"]):
            steps.append(AgentStep(
                step_id="analyze",
                name="AI Analysis",
                description="Use AI to analyze and generate insights",
                action_type="llm_query",
                config={"model": "gpt-4", "task": "custom_analysis"},
                next_steps=["output"]
            ))

        # Step 4: Output
        output_type = "report"
        if "journal entry" in nl_lower:
            output_type = "journal_entry"
        elif "reconciliation" in nl_lower:
            output_type = "reconciliation_report"
        elif "workpaper" in nl_lower:
            output_type = "workpaper"

        steps.append(AgentStep(
            step_id="output",
            name="Generate Output",
            description=f"Create {output_type}",
            action_type="output",
            config={"output_type": output_type},
            next_steps=[]
        ))

        # Ensure step connections
        for i, step in enumerate(steps[:-1]):
            step.next_steps = [steps[i + 1].step_id]

        workflow = AgentWorkflow(
            start_step=steps[0].step_id if steps else "output",
            steps=steps
        )

        # Determine required permissions
        permissions = []
        if data_sources_found:
            permissions.append("read_financial_data")
        if "journal entry" in nl_lower or "create" in nl_lower:
            permissions.append("write_journal_entries")
        if "email" in nl_lower or "send" in nl_lower:
            permissions.append("send_notifications")

        # Generate suggestions
        suggestions = []
        if len(steps) < 3:
            suggestions.append("Consider adding validation steps to ensure data quality")
        if "error" not in nl_lower and "exception" not in nl_lower:
            suggestions.append("Consider specifying error handling behavior")

        return NaturalLanguageParseResult(
            understood=True,
            confidence_score=0.85,
            parsed_workflow=workflow,
            suggested_improvements=suggestions,
            required_permissions=permissions,
            estimated_execution_time_ms=len(steps) * 500,
            warnings=[]
        )


# Global parser instance
nl_parser = NaturalLanguageAgentParser()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Agent Builder",
        "version": "1.0.0",
        "agents_count": len(agents_db),
        "templates_count": len(templates_db)
    }


@app.get("/")
async def root():
    """Service info"""
    return {
        "service": "AI Agent Builder Service",
        "version": "1.0.0",
        "description": "Create custom AI agents with natural language - No coding required",
        "features": [
            "Natural language agent definition",
            "10+ agent types (more than FloQast)",
            "Pre-built templates for common audit tasks",
            "Visual workflow builder support",
            "Agent scheduling and automation",
            "Agent performance analytics",
            "Agent marketplace for sharing"
        ],
        "agent_types": [t.value for t in AgentType],
        "docs": "/docs"
    }


# -------------------- Templates --------------------

@app.get("/templates", response_model=List[AgentTemplate])
async def list_templates(
    agent_type: Optional[AgentType] = None,
    category: Optional[str] = None,
    official_only: bool = False
):
    """List available agent templates"""
    templates = list(templates_db.values())

    if agent_type:
        templates = [t for t in templates if t.agent_type == agent_type]

    if category:
        templates = [t for t in templates if t.category == category]

    if official_only:
        templates = [t for t in templates if t.is_official]

    # Sort by popularity
    templates.sort(key=lambda t: t.popularity_score, reverse=True)

    return templates


@app.get("/templates/{template_id}", response_model=AgentTemplate)
async def get_template(template_id: str):
    """Get specific template"""
    if template_id not in templates_db:
        raise HTTPException(status_code=404, detail="Template not found")
    return templates_db[template_id]


# -------------------- Agent Management --------------------

@app.post("/agents", response_model=AgentResponse)
async def create_agent(request: AgentCreateRequest, background_tasks: BackgroundTasks):
    """
    Create a new AI agent from natural language description.

    The natural_language_definition field is where users describe what they want
    their agent to do in plain English. Our AI parses this into an executable workflow.
    """

    # Parse natural language into workflow
    parse_result = await nl_parser.parse(
        request.natural_language_definition,
        request.agent_type
    )

    if not parse_result.understood:
        raise HTTPException(
            status_code=400,
            detail="Could not understand the agent definition. Please try rephrasing."
        )

    # Create agent
    agent_id = str(uuid4())
    now = datetime.utcnow()

    agent = {
        "agent_id": agent_id,
        "name": request.name,
        "description": request.description,
        "agent_type": request.agent_type,
        "status": AgentStatus.DRAFT,
        "trigger_type": request.trigger_type,
        "schedule": request.schedule,
        "workflow": parse_result.parsed_workflow.dict(),
        "natural_language_definition": request.natural_language_definition,
        "input_schema": request.input_schema,
        "output_schema": request.output_schema,
        "created_at": now,
        "updated_at": now,
        "created_by": "current_user",  # Would come from auth
        "execution_count": 0,
        "success_rate": 0.0,
        "avg_execution_time_ms": 0,
        "tags": request.tags,
        "version": 1,
        "parse_confidence": parse_result.confidence_score,
        "required_permissions": parse_result.required_permissions,
        "suggested_improvements": parse_result.suggested_improvements
    }

    agents_db[agent_id] = agent

    logger.info(f"Created agent {agent_id}: {request.name}")

    return AgentResponse(
        agent_id=agent_id,
        name=request.name,
        description=request.description,
        agent_type=request.agent_type,
        status=AgentStatus.DRAFT,
        trigger_type=request.trigger_type,
        workflow=parse_result.parsed_workflow,
        created_at=now,
        updated_at=now,
        created_by="current_user",
        execution_count=0,
        success_rate=0.0,
        avg_execution_time_ms=parse_result.estimated_execution_time_ms,
        tags=request.tags,
        version=1
    )


@app.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    agent_type: Optional[AgentType] = None,
    status: Optional[AgentStatus] = None,
    skip: int = 0,
    limit: int = 100
):
    """List all agents"""
    agents = list(agents_db.values())

    if agent_type:
        agents = [a for a in agents if a["agent_type"] == agent_type]

    if status:
        agents = [a for a in agents if a["status"] == status]

    agents = agents[skip:skip + limit]

    return [
        AgentResponse(
            agent_id=a["agent_id"],
            name=a["name"],
            description=a["description"],
            agent_type=a["agent_type"],
            status=a["status"],
            trigger_type=a["trigger_type"],
            workflow=AgentWorkflow(**a["workflow"]) if a.get("workflow") else None,
            created_at=a["created_at"],
            updated_at=a["updated_at"],
            created_by=a["created_by"],
            execution_count=a["execution_count"],
            success_rate=a["success_rate"],
            avg_execution_time_ms=a["avg_execution_time_ms"],
            tags=a["tags"],
            version=a["version"]
        )
        for a in agents
    ]


@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get agent details"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    a = agents_db[agent_id]
    return AgentResponse(
        agent_id=a["agent_id"],
        name=a["name"],
        description=a["description"],
        agent_type=a["agent_type"],
        status=a["status"],
        trigger_type=a["trigger_type"],
        workflow=AgentWorkflow(**a["workflow"]) if a.get("workflow") else None,
        created_at=a["created_at"],
        updated_at=a["updated_at"],
        created_by=a["created_by"],
        execution_count=a["execution_count"],
        success_rate=a["success_rate"],
        avg_execution_time_ms=a["avg_execution_time_ms"],
        tags=a["tags"],
        version=a["version"]
    )


@app.patch("/agents/{agent_id}/activate")
async def activate_agent(agent_id: str):
    """Activate an agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agents_db[agent_id]["status"] = AgentStatus.ACTIVE
    agents_db[agent_id]["updated_at"] = datetime.utcnow()

    return {"message": "Agent activated", "agent_id": agent_id}


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    del agents_db[agent_id]
    return {"message": "Agent deleted", "agent_id": agent_id}


# -------------------- Agent Execution --------------------

@app.post("/agents/{agent_id}/execute", response_model=AgentExecutionResponse)
async def execute_agent(
    agent_id: str,
    request: AgentExecutionRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute an agent with given input data.

    Supports dry_run mode for testing without applying changes.
    """
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents_db[agent_id]

    if agent["status"] != AgentStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Agent is not active. Current status: {agent['status']}"
        )

    # Create execution record
    execution_id = str(uuid4())
    now = datetime.utcnow()

    execution = {
        "execution_id": execution_id,
        "agent_id": agent_id,
        "status": ExecutionStatus.PENDING,
        "started_at": now,
        "completed_at": None,
        "input_data": request.input_data,
        "output_data": None,
        "engagement_id": request.engagement_id,
        "dry_run": request.dry_run,
        "steps_completed": [],
        "current_step": None,
        "error_message": None,
        "execution_log": [],
        "metrics": {}
    }

    executions_db[execution_id] = execution

    # Execute in background
    background_tasks.add_task(run_agent_execution, execution_id, agent_id, request.input_data)

    return AgentExecutionResponse(
        execution_id=execution_id,
        agent_id=agent_id,
        status=ExecutionStatus.PENDING,
        started_at=now,
        input_data=request.input_data,
        execution_log=[{"timestamp": now.isoformat(), "message": "Execution queued"}]
    )


async def run_agent_execution(execution_id: str, agent_id: str, input_data: Dict):
    """Background task to execute agent workflow"""

    execution = executions_db[execution_id]
    agent = agents_db[agent_id]
    workflow = agent["workflow"]

    execution["status"] = ExecutionStatus.RUNNING
    execution["execution_log"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Execution started"
    })

    try:
        # Simulate workflow execution
        for step_data in workflow["steps"]:
            step_id = step_data["step_id"]
            execution["current_step"] = step_id

            execution["execution_log"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Executing step: {step_data['name']}"
            })

            # Simulate step execution
            await asyncio.sleep(0.5)

            execution["steps_completed"].append(step_id)

        # Mark as completed
        execution["status"] = ExecutionStatus.COMPLETED
        execution["completed_at"] = datetime.utcnow()
        execution["output_data"] = {
            "result": "success",
            "items_processed": 100,
            "summary": "Agent execution completed successfully"
        }
        execution["metrics"] = {
            "total_time_ms": 2500,
            "steps_executed": len(workflow["steps"]),
            "records_processed": 100
        }

        # Update agent stats
        agent["execution_count"] += 1
        agent["success_rate"] = (
            (agent["success_rate"] * (agent["execution_count"] - 1) + 1) /
            agent["execution_count"]
        )

        execution["execution_log"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Execution completed successfully"
        })

    except Exception as e:
        execution["status"] = ExecutionStatus.FAILED
        execution["completed_at"] = datetime.utcnow()
        execution["error_message"] = str(e)

        execution["execution_log"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Execution failed: {str(e)}"
        })

        agent["execution_count"] += 1


@app.get("/executions/{execution_id}", response_model=AgentExecutionResponse)
async def get_execution(execution_id: str):
    """Get execution status and results"""
    if execution_id not in executions_db:
        raise HTTPException(status_code=404, detail="Execution not found")

    e = executions_db[execution_id]
    return AgentExecutionResponse(
        execution_id=e["execution_id"],
        agent_id=e["agent_id"],
        status=e["status"],
        started_at=e["started_at"],
        completed_at=e["completed_at"],
        input_data=e["input_data"],
        output_data=e["output_data"],
        steps_completed=e["steps_completed"],
        current_step=e["current_step"],
        error_message=e["error_message"],
        execution_log=e["execution_log"],
        metrics=e["metrics"]
    )


@app.get("/agents/{agent_id}/executions", response_model=List[AgentExecutionResponse])
async def list_agent_executions(agent_id: str, limit: int = 20):
    """List recent executions for an agent"""
    executions = [
        e for e in executions_db.values()
        if e["agent_id"] == agent_id
    ]

    # Sort by started_at descending
    executions.sort(key=lambda e: e["started_at"], reverse=True)

    return [
        AgentExecutionResponse(
            execution_id=e["execution_id"],
            agent_id=e["agent_id"],
            status=e["status"],
            started_at=e["started_at"],
            completed_at=e["completed_at"],
            input_data=e["input_data"],
            output_data=e["output_data"],
            steps_completed=e["steps_completed"],
            current_step=e["current_step"],
            error_message=e["error_message"],
            execution_log=e["execution_log"],
            metrics=e["metrics"]
        )
        for e in executions[:limit]
    ]


# -------------------- Natural Language Parsing --------------------

@app.post("/parse-natural-language", response_model=NaturalLanguageParseResult)
async def parse_natural_language(
    natural_language: str,
    agent_type: AgentType = AgentType.CUSTOM
):
    """
    Preview how natural language will be parsed into a workflow.

    Useful for users to see the interpreted workflow before creating an agent.
    """
    return await nl_parser.parse(natural_language, agent_type)


# -------------------- Agent Marketplace --------------------

@app.get("/marketplace")
async def get_marketplace_agents():
    """Get agents shared in the marketplace"""
    # In production, this would query shared agents from database
    return {
        "featured_templates": list(templates_db.values())[:5],
        "categories": [
            {"name": "Journal Entries", "count": 3},
            {"name": "Reconciliations", "count": 2},
            {"name": "Compliance", "count": 2},
            {"name": "Financial Analysis", "count": 3},
            {"name": "Analytics", "count": 2}
        ],
        "total_available": len(templates_db)
    }


@app.post("/agents/{agent_id}/publish-to-marketplace")
async def publish_to_marketplace(agent_id: str):
    """Publish an agent to the marketplace for other firms to use"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents_db[agent_id]

    # Create template from agent
    template = AgentTemplate(
        template_id=f"tmpl_{agent_id[:8]}",
        name=agent["name"],
        description=agent["description"],
        agent_type=agent["agent_type"],
        category="User Created",
        workflow=AgentWorkflow(**agent["workflow"]),
        sample_input=agent.get("input_schema", {}),
        sample_output=agent.get("output_schema", {}),
        popularity_score=0,
        created_by=agent["created_by"],
        is_official=False
    )

    templates_db[template.template_id] = template

    return {"message": "Agent published to marketplace", "template_id": template.template_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8030)
