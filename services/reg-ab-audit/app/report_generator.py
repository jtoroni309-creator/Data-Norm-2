"""
AI-Powered Audit Report Generator

Generates comprehensive Regulation A/B audit reports with AI-powered analysis and summary.
"""

import hashlib
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import CMBSDeal, ComplianceCheck, RegABWorkpaper

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates comprehensive audit reports using AI analysis of all engagement data.
    """

    def __init__(self, ai_engine):
        """
        Initialize report generator.

        Args:
            ai_engine: AIComplianceEngine instance
        """
        self.ai_engine = ai_engine

    async def generate_report(
        self,
        engagement: Any,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Generate comprehensive audit report for an engagement.

        Args:
            engagement: RegABAuditEngagement model instance
            db: Database session

        Returns:
            Report data dictionary
        """
        logger.info(f"Generating audit report for engagement {engagement.id}")

        # Gather all data
        deals = await self._get_deals(engagement.id, db)
        compliance_checks = await self._get_compliance_checks(engagement.id, db)
        workpapers = await self._get_workpapers(engagement.id, db)

        # Generate report content using AI
        prompt = self._build_report_prompt(
            engagement=engagement,
            deals=deals,
            compliance_checks=compliance_checks,
            workpapers=workpapers
        )

        response = await self.ai_engine._call_openai_api(
            prompt=prompt,
            check_code="REPORT_GENERATION"
        )

        content_data = json.loads(response)

        # Calculate statistics
        stats = self._calculate_statistics(
            deals=deals,
            compliance_checks=compliance_checks,
            workpapers=workpapers
        )

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            engagement=engagement,
            stats=stats,
            content_data=content_data
        )

        # Build report data
        report = {
            "audit_engagement_id": engagement.id,
            "report_type": "Regulation AB Compilation Report",
            "report_period_start": engagement.audit_period_start,
            "report_period_end": engagement.audit_period_end,
            "version": 1,
            "executive_summary": executive_summary,
            "findings_summary": content_data.get("findings_summary", {}),
            "content": content_data,
            "content_html": self._render_report_html(
                engagement=engagement,
                content=content_data,
                stats=stats,
                executive_summary=executive_summary
            ),
            "total_deals_audited": stats["total_deals"],
            "total_compliance_checks": stats["total_compliance_checks"],
            "passed_checks": stats["passed_checks"],
            "failed_checks": stats["failed_checks"],
            "total_workpapers": stats["total_workpapers"],
            "ai_generated": True,
            "ai_model_version": self.ai_engine.model_version,
            "ai_generation_timestamp": datetime.utcnow(),
            "ai_confidence_score": Decimal(str(content_data.get("confidence", 0.9))),
            "draft": True,
            "generated_at": datetime.utcnow(),
            "content_hash": hashlib.sha256(
                json.dumps(content_data, sort_keys=True).encode()
            ).hexdigest(),
        }

        return report

    async def _get_deals(self, engagement_id: UUID, db: AsyncSession) -> List[Any]:
        """Get all deals for engagement."""
        result = await db.execute(
            select(CMBSDeal).where(
                CMBSDeal.audit_engagement_id == engagement_id
            )
        )
        return result.scalars().all()

    async def _get_compliance_checks(self, engagement_id: UUID, db: AsyncSession) -> List[Any]:
        """Get all compliance checks for engagement."""
        result = await db.execute(
            select(ComplianceCheck).where(
                ComplianceCheck.audit_engagement_id == engagement_id
            )
        )
        return result.scalars().all()

    async def _get_workpapers(self, engagement_id: UUID, db: AsyncSession) -> List[Any]:
        """Get all workpapers for engagement."""
        result = await db.execute(
            select(RegABWorkpaper).where(
                RegABWorkpaper.audit_engagement_id == engagement_id
            )
        )
        return result.scalars().all()

    def _calculate_statistics(
        self,
        deals: List[Any],
        compliance_checks: List[Any],
        workpapers: List[Any]
    ) -> Dict[str, Any]:
        """Calculate report statistics."""
        return {
            "total_deals": len(deals),
            "total_compliance_checks": len(compliance_checks),
            "passed_checks": sum(1 for c in compliance_checks if c.passed),
            "failed_checks": sum(1 for c in compliance_checks if not c.passed),
            "total_workpapers": len(workpapers),
            "approved_workpapers": sum(1 for w in workpapers if w.status == "approved"),
            "compliance_pass_rate": (
                (sum(1 for c in compliance_checks if c.passed) / len(compliance_checks) * 100)
                if compliance_checks else 0
            ),
            "total_balance": sum(float(d.current_balance or 0) for d in deals),
            "avg_dscr": (
                sum(float(d.dscr or 0) for d in deals if d.dscr) / sum(1 for d in deals if d.dscr)
                if any(d.dscr for d in deals) else 0
            ),
            "avg_ltv": (
                sum(float(d.ltv or 0) for d in deals if d.ltv) / sum(1 for d in deals if d.ltv)
                if any(d.ltv for d in deals) else 0
            ),
        }

    def _build_report_prompt(
        self,
        engagement: Any,
        deals: List[Any],
        compliance_checks: List[Any],
        workpapers: List[Any]
    ) -> str:
        """Build prompt for report generation."""
        stats = self._calculate_statistics(deals, compliance_checks, workpapers)

        # Summarize deals
        deals_summary = [
            {
                "deal_name": d.deal_name,
                "balance": float(d.current_balance or 0),
                "dscr": float(d.dscr) if d.dscr else None,
                "ltv": float(d.ltv) if d.ltv else None,
                "property_type": d.property_type,
            }
            for d in deals[:10]  # Limit to top 10
        ]

        # Summarize compliance issues
        failed_checks = [
            {
                "rule": c.check_name,
                "standard": str(c.standard),
                "findings": c.findings[:200] if c.findings else ""
            }
            for c in compliance_checks if not c.passed
        ][:10]  # Top 10 failures

        prompt = f"""You are an expert auditor preparing a comprehensive Regulation A/B audit report for CMBS loans.

Engagement Information:
- Audit Name: {engagement.audit_name}
- Period: {engagement.audit_period_start} to {engagement.audit_period_end}
- Total CMBS Deals: {stats['total_deals']}
- Total Balance: ${stats['total_balance']:,.2f}

Performance Metrics:
- Compliance Pass Rate: {stats['compliance_pass_rate']:.1f}%
- Average DSCR: {stats['avg_dscr']:.2f}
- Average LTV: {stats['avg_ltv']:.1f}%

Deals Summary:
{json.dumps(deals_summary, indent=2)}

Compliance Issues:
{json.dumps(failed_checks, indent=2)}

Task:
Prepare a comprehensive Regulation A/B audit report. Include:

1. Scope and Methodology - Describe audit scope, standards applied, and procedures
2. Portfolio Overview - Summary of CMBS deals audited
3. Compliance Assessment - Overall compliance status with PCAOB, GAAP, GAAS, SEC, AICPA
4. Key Findings - Significant findings and observations organized by:
   - Critical Issues
   - Material Findings
   - Minor Observations
5. Risk Assessment - Overall risk profile of the portfolio
6. Recommendations - Specific recommendations for remediation
7. Conclusion - Overall audit conclusion and opinion

For each finding, include:
- Severity (critical/high/medium/low)
- Affected deals (if applicable)
- Regulatory reference
- Impact assessment
- Recommended actions

Respond in JSON format:
{{
    "confidence": 0.95,
    "scope_and_methodology": "...",
    "portfolio_overview": {{
        "summary": "...",
        "key_metrics": {{}},
        "deal_breakdown": []
    }},
    "compliance_assessment": {{
        "overall_status": "Compliant|Non-Compliant|Qualified",
        "pcaob_compliance": "...",
        "gaap_compliance": "...",
        "gaas_compliance": "...",
        "sec_compliance": "...",
        "aicpa_compliance": "..."
    }},
    "key_findings": [
        {{
            "title": "...",
            "severity": "critical|high|medium|low",
            "description": "...",
            "affected_deals": [...],
            "regulatory_reference": "...",
            "impact": "...",
            "recommendations": [...]
        }}
    ],
    "risk_assessment": {{
        "overall_risk_level": "low|medium|high|critical",
        "risk_factors": [...],
        "mitigation_strategies": [...]
    }},
    "recommendations": [
        {{
            "priority": "immediate|high|medium|low",
            "recommendation": "...",
            "rationale": "...",
            "expected_outcome": "..."
        }}
    ],
    "conclusion": "...",
    "opinion": "Unqualified|Qualified|Adverse|Disclaimer",
    "findings_summary": {{
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }}
}}

Be thorough, professional, and objective. This report will be reviewed and signed by a licensed CPA.
"""

        return prompt

    def _generate_executive_summary(
        self,
        engagement: Any,
        stats: Dict[str, Any],
        content_data: Dict[str, Any]
    ) -> str:
        """Generate executive summary section."""
        opinion = content_data.get("opinion", "Unqualified")
        compliance_status = content_data.get("compliance_assessment", {}).get("overall_status", "Unknown")

        summary = f"""
EXECUTIVE SUMMARY

Engagement: {engagement.audit_name}
Period: {engagement.audit_period_start.strftime('%B %d, %Y')} to {engagement.audit_period_end.strftime('%B %d, %Y')}

We have completed our Regulation A/B audit of {stats['total_deals']} CMBS deals with an aggregate
balance of ${stats['total_balance']:,.2f}. Our audit was conducted in accordance with PCAOB standards,
GAAP, GAAS, SEC Regulation AB, and AICPA attestation standards.

OVERALL CONCLUSION: {opinion} Opinion

COMPLIANCE STATUS: {compliance_status}

KEY STATISTICS:
- Total CMBS Deals Audited: {stats['total_deals']}
- Compliance Checks Performed: {stats['total_compliance_checks']}
- Compliance Pass Rate: {stats['compliance_pass_rate']:.1f}%
- Workpapers Generated: {stats['total_workpapers']}
- Average DSCR: {stats['avg_dscr']:.2f}
- Average LTV: {stats['avg_ltv']:.1f}%

FINDINGS SUMMARY:
- Critical Issues: {content_data.get('findings_summary', {}).get('critical', 0)}
- High Priority: {content_data.get('findings_summary', {}).get('high', 0)}
- Medium Priority: {content_data.get('findings_summary', {}).get('medium', 0)}
- Low Priority: {content_data.get('findings_summary', {}).get('low', 0)}

{content_data.get('conclusion', '')}
"""

        return summary.strip()

    def _render_report_html(
        self,
        engagement: Any,
        content: Dict[str, Any],
        stats: Dict[str, Any],
        executive_summary: str
    ) -> str:
        """Render report as HTML."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Regulation A/B Audit Report - {engagement.audit_name}</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; text-align: center; font-size: 24pt; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 30px; }}
        h3 {{ color: #555; margin-top: 20px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .executive-summary {{ background: #f8f9fa; padding: 20px; border-left: 5px solid #3498db; margin: 20px 0; }}
        .finding {{ background: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 15px 0; }}
        .finding.critical {{ border-left: 5px solid #e74c3c; }}
        .finding.high {{ border-left: 5px solid #f39c12; }}
        .finding.medium {{ border-left: 5px solid #3498db; }}
        .finding.low {{ border-left: 5px solid #2ecc71; }}
        .severity-badge {{ display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }}
        .severity-critical {{ background: #e74c3c; }}
        .severity-high {{ background: #f39c12; }}
        .severity-medium {{ background: #3498db; }}
        .severity-low {{ background: #2ecc71; }}
        .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ color: #7f8c8d; font-size: 0.9em; }}
        .recommendation {{ background: #e8f8f5; border-left: 4px solid #27ae60; padding: 15px; margin: 10px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #34495e; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        .page-break {{ page-break-after: always; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Regulation A/B Audit Report</h1>
        <h2>{engagement.audit_name}</h2>
        <p><strong>Audit Period:</strong> {engagement.audit_period_start.strftime('%B %d, %Y')} to {engagement.audit_period_end.strftime('%B %d, %Y')}</p>
        <p><strong>Report Date:</strong> {datetime.utcnow().strftime('%B %d, %Y')}</p>
    </div>

    <div class="executive-summary">
        <h2>Executive Summary</h2>
        <pre style="white-space: pre-wrap; font-family: inherit;">{executive_summary}</pre>
    </div>

    <div class="page-break"></div>

    <h2>Key Metrics</h2>
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value">{stats['total_deals']}</div>
            <div class="metric-label">CMBS Deals Audited</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{stats['compliance_pass_rate']:.1f}%</div>
            <div class="metric-label">Compliance Pass Rate</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${stats['total_balance']:,.0f}</div>
            <div class="metric-label">Total Balance</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{stats['avg_dscr']:.2f}</div>
            <div class="metric-label">Average DSCR</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{stats['avg_ltv']:.1f}%</div>
            <div class="metric-label">Average LTV</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{stats['total_compliance_checks']}</div>
            <div class="metric-label">Compliance Checks</div>
        </div>
    </div>

    <h2>Scope and Methodology</h2>
    <p>{content.get('scope_and_methodology', 'N/A')}</p>

    <div class="page-break"></div>

    <h2>Compliance Assessment</h2>
    <h3>Overall Status: {content.get('compliance_assessment', {}).get('overall_status', 'Unknown')}</h3>
    <ul>
        <li><strong>PCAOB:</strong> {content.get('compliance_assessment', {}).get('pcaob_compliance', 'N/A')}</li>
        <li><strong>GAAP:</strong> {content.get('compliance_assessment', {}).get('gaap_compliance', 'N/A')}</li>
        <li><strong>GAAS:</strong> {content.get('compliance_assessment', {}).get('gaas_compliance', 'N/A')}</li>
        <li><strong>SEC:</strong> {content.get('compliance_assessment', {}).get('sec_compliance', 'N/A')}</li>
        <li><strong>AICPA:</strong> {content.get('compliance_assessment', {}).get('aicpa_compliance', 'N/A')}</li>
    </ul>

    <h2>Key Findings</h2>
    {''.join(
        f'<div class="finding {f.get("severity", "low")}">'
        f'<h3><span class="severity-badge severity-{f.get("severity", "low")}">{f.get("severity", "LOW").upper()}</span> {f.get("title", "Finding")}</h3>'
        f'<p><strong>Description:</strong> {f.get("description", "")}</p>'
        f'<p><strong>Regulatory Reference:</strong> {f.get("regulatory_reference", "N/A")}</p>'
        f'<p><strong>Impact:</strong> {f.get("impact", "N/A")}</p>'
        f'<p><strong>Recommendations:</strong></p>'
        f'<ul>{"".join(f"<li>{r}</li>" for r in f.get("recommendations", []))}</ul>'
        f'</div>'
        for f in content.get('key_findings', [])
    )}

    <div class="page-break"></div>

    <h2>Risk Assessment</h2>
    <p><strong>Overall Risk Level:</strong> {content.get('risk_assessment', {}).get('overall_risk_level', 'Unknown').upper()}</p>
    <h3>Risk Factors:</h3>
    <ul>
    {''.join(f'<li>{r}</li>' for r in content.get('risk_assessment', {}).get('risk_factors', []))}
    </ul>

    <h2>Recommendations</h2>
    {''.join(
        f'<div class="recommendation">'
        f'<h3>{r.get("priority", "MEDIUM").upper()} PRIORITY: {r.get("recommendation", "")}</h3>'
        f'<p><strong>Rationale:</strong> {r.get("rationale", "")}</p>'
        f'<p><strong>Expected Outcome:</strong> {r.get("expected_outcome", "")}</p>'
        f'</div>'
        for r in content.get('recommendations', [])
    )}

    <h2>Conclusion</h2>
    <p>{content.get('conclusion', 'N/A')}</p>

    <div class="footer">
        <p>This report was generated using AI-powered audit analysis.</p>
        <p>CPA review and sign-off required before finalization.</p>
        <p><strong>Report Version:</strong> 1 (Draft)</p>
    </div>
</body>
</html>
"""
        return html
