"""
AI-Powered Workpaper Generator

Generates comprehensive audit workpapers for CMBS deals using AI analysis.
"""

import hashlib
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List
from uuid import uuid4

from .config import settings
from .models import WorkpaperStatus

logger = logging.getLogger(__name__)


class WorkpaperGenerator:
    """
    Generates structured audit workpapers using AI analysis.
    """

    def __init__(self, ai_engine):
        """
        Initialize workpaper generator.

        Args:
            ai_engine: AIComplianceEngine instance
        """
        self.ai_engine = ai_engine
        self.workpaper_templates = self._load_workpaper_templates()

    def _load_workpaper_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load workpaper templates."""
        return {
            "cash_flow_analysis": {
                "ref_prefix": "WP-CF",
                "title": "Cash Flow Analysis",
                "category": "Financial Analysis",
                "description": "Analysis of property cash flows and DSCR calculations"
            },
            "property_valuation": {
                "ref_prefix": "WP-PV",
                "title": "Property Valuation Review",
                "category": "Valuation",
                "description": "Review of property valuations and LTV calculations"
            },
            "servicer_assessment": {
                "ref_prefix": "WP-SA",
                "title": "Servicer Assessment",
                "category": "Third Party Services",
                "description": "Assessment of servicer qualifications and performance"
            },
            "compliance_summary": {
                "ref_prefix": "WP-CS",
                "title": "Compliance Summary",
                "category": "Compliance",
                "description": "Summary of compliance check results"
            },
            "risk_assessment": {
                "ref_prefix": "WP-RA",
                "title": "Risk Assessment",
                "category": "Risk Analysis",
                "description": "Assessment of deal-specific risks"
            },
            "disclosure_review": {
                "ref_prefix": "WP-DR",
                "title": "Disclosure Review",
                "category": "Reporting",
                "description": "Review of SEC Regulation AB disclosures"
            }
        }

    async def generate_workpapers(
        self,
        deal: Any,
        engagement: Any,
        compliance_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate all workpapers for a CMBS deal.

        Args:
            deal: CMBS deal model instance
            engagement: Audit engagement model instance
            compliance_results: Results from compliance checks

        Returns:
            List of workpaper data dictionaries
        """
        logger.info(f"Generating workpapers for deal {deal.id}")

        workpapers = []

        # Generate each type of workpaper
        for wp_type, template in self.workpaper_templates.items():
            try:
                workpaper = await self._generate_workpaper(
                    wp_type=wp_type,
                    template=template,
                    deal=deal,
                    engagement=engagement,
                    compliance_results=compliance_results
                )
                workpapers.append(workpaper)

            except Exception as e:
                logger.error(f"Error generating workpaper {wp_type} for deal {deal.id}: {str(e)}", exc_info=True)

        return workpapers

    async def _generate_workpaper(
        self,
        wp_type: str,
        template: Dict[str, Any],
        deal: Any,
        engagement: Any,
        compliance_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a single workpaper using AI.

        Args:
            wp_type: Workpaper type key
            template: Workpaper template
            deal: CMBS deal
            engagement: Audit engagement
            compliance_results: Compliance check results

        Returns:
            Workpaper data dictionary
        """
        # Build AI prompt
        prompt = self._build_workpaper_prompt(
            wp_type=wp_type,
            template=template,
            deal=deal,
            engagement=engagement,
            compliance_results=compliance_results
        )

        # Generate content using AI
        response = await self.ai_engine._call_openai_api(
            prompt=prompt,
            check_code=f"WORKPAPER_{wp_type}"
        )

        content_data = json.loads(response)

        # Generate workpaper reference
        workpaper_ref = f"{template['ref_prefix']}-{deal.deal_number}"

        # Calculate content hash
        content_hash = hashlib.sha256(
            json.dumps(content_data, sort_keys=True).encode()
        ).hexdigest()

        # Build workpaper data
        workpaper = {
            "audit_engagement_id": engagement.id,
            "cmbs_deal_id": deal.id,
            "workpaper_ref": workpaper_ref,
            "title": f"{template['title']} - {deal.deal_name}",
            "category": template["category"],
            "description": template["description"],
            "content": content_data,
            "content_html": self._render_html(content_data, template),
            "status": WorkpaperStatus.AI_GENERATED,
            "ai_generated": True,
            "ai_model_version": self.ai_engine.model_version,
            "ai_prompt_used": prompt[:500],  # Store truncated prompt
            "ai_generation_confidence": Decimal(str(content_data.get("confidence", 0.9))),
            "ai_generation_timestamp": datetime.utcnow(),
            "compliance_checks": [
                str(r.get("id")) for r in compliance_results
                if r.get("id")
            ],
            "content_hash": content_hash,
            "version": 1,
            "revision_count": 0,
            "locked": False
        }

        return workpaper

    def _build_workpaper_prompt(
        self,
        wp_type: str,
        template: Dict[str, Any],
        deal: Any,
        engagement: Any,
        compliance_results: List[Dict[str, Any]]
    ) -> str:
        """
        Build prompt for workpaper generation.

        Args:
            wp_type: Workpaper type
            template: Workpaper template
            deal: CMBS deal
            engagement: Audit engagement
            compliance_results: Compliance results

        Returns:
            Formatted prompt
        """
        # Build deal summary
        deal_summary = {
            "deal_name": deal.deal_name,
            "deal_number": deal.deal_number,
            "original_balance": float(deal.original_balance) if deal.original_balance else None,
            "current_balance": float(deal.current_balance) if deal.current_balance else None,
            "dscr": float(deal.dscr) if deal.dscr else None,
            "ltv": float(deal.ltv) if deal.ltv else None,
            "property_type": deal.property_type,
            "master_servicer": deal.master_servicer,
            "special_servicer": deal.special_servicer,
        }

        # Build compliance summary
        compliance_summary = {
            "total_checks": len(compliance_results),
            "passed": sum(1 for r in compliance_results if r.get("passed")),
            "failed": sum(1 for r in compliance_results if not r.get("passed")),
            "key_findings": [
                {
                    "rule": r.get("check_name"),
                    "status": str(r.get("status")),
                    "findings": r.get("findings", "")[:200]  # Truncate
                }
                for r in compliance_results[:5]  # Top 5
            ]
        }

        prompt = f"""You are an expert auditor preparing audit workpapers for a Regulation A/B CMBS audit.

Workpaper Type: {template['title']}
Category: {template['category']}
Description: {template['description']}

CMBS Deal Information:
{json.dumps(deal_summary, indent=2)}

Compliance Check Summary:
{json.dumps(compliance_summary, indent=2)}

Task:
Prepare a comprehensive audit workpaper for this CMBS deal. Include:

1. Executive Summary - Brief overview of scope and conclusions
2. Procedures Performed - Detailed audit procedures executed
3. Findings - Key findings and observations
4. Analysis - Detailed analysis of relevant metrics and data
5. Conclusion - Overall conclusion and any recommendations
6. References - References to source documents and compliance checks

For {wp_type} specifically:
"""

        # Add type-specific instructions
        if wp_type == "cash_flow_analysis":
            prompt += """
- Analyze the DSCR and trends
- Review cash flow adequacy
- Assess debt service coverage
- Identify any cash flow concerns
"""
        elif wp_type == "property_valuation":
            prompt += """
- Review LTV ratios and trends
- Assess property valuation methodology
- Evaluate collateral adequacy
- Identify valuation risks
"""
        elif wp_type == "servicer_assessment":
            prompt += """
- Evaluate servicer qualifications
- Review servicer performance history
- Assess servicer oversight
- Identify any servicer concerns
"""
        elif wp_type == "compliance_summary":
            prompt += """
- Summarize all compliance check results
- Highlight any compliance failures
- Assess overall compliance status
- Recommend remediation actions
"""
        elif wp_type == "risk_assessment":
            prompt += """
- Identify key risks for this deal
- Assess likelihood and impact
- Evaluate risk mitigation
- Provide risk recommendations
"""
        elif wp_type == "disclosure_review":
            prompt += """
- Review SEC Regulation AB disclosures
- Verify completeness and accuracy
- Identify any disclosure gaps
- Assess presentation and clarity
"""

        prompt += """

Respond in JSON format:
{
    "confidence": 0.95,
    "executive_summary": "...",
    "procedures_performed": ["procedure1", "procedure2", ...],
    "findings": [
        {
            "title": "Finding title",
            "description": "Detailed description",
            "severity": "low|medium|high",
            "recommendation": "..."
        }
    ],
    "analysis": {
        "metrics": {...},
        "trends": "...",
        "assessment": "..."
    },
    "conclusion": "...",
    "references": ["ref1", "ref2", ...],
    "reviewer_notes": "Notes for CPA reviewer..."
}

Be thorough, specific, and professional. This workpaper will be reviewed by a licensed CPA.
"""

        return prompt

    def _render_html(self, content: Dict[str, Any], template: Dict[str, Any]) -> str:
        """
        Render workpaper content as HTML.

        Args:
            content: Workpaper content data
            template: Workpaper template

        Returns:
            HTML string
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{template['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        .section {{ margin: 20px 0; }}
        .finding {{ background: #f8f9fa; border-left: 4px solid #3498db; padding: 10px; margin: 10px 0; }}
        .finding.high {{ border-left-color: #e74c3c; }}
        .finding.medium {{ border-left-color: #f39c12; }}
        .finding.low {{ border-left-color: #2ecc71; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-label {{ font-weight: bold; color: #7f8c8d; }}
        .metric-value {{ font-size: 1.2em; color: #2c3e50; }}
        ul {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <h1>{template['title']}</h1>
    <p><strong>Category:</strong> {template['category']}</p>
    <p><strong>Description:</strong> {template['description']}</p>

    <div class="section">
        <h2>Executive Summary</h2>
        <p>{content.get('executive_summary', 'N/A')}</p>
    </div>

    <div class="section">
        <h2>Procedures Performed</h2>
        <ul>
        {''.join(f'<li>{p}</li>' for p in content.get('procedures_performed', []))}
        </ul>
    </div>

    <div class="section">
        <h2>Findings</h2>
        {''.join(
            f'<div class="finding {f.get("severity", "low")}">'
            f'<h3>{f.get("title", "Finding")}</h3>'
            f'<p>{f.get("description", "")}</p>'
            f'<p><strong>Recommendation:</strong> {f.get("recommendation", "None")}</p>'
            f'</div>'
            for f in content.get('findings', [])
        )}
    </div>

    <div class="section">
        <h2>Analysis</h2>
        <div class="metrics">
        {''.join(
            f'<div class="metric">'
            f'<div class="metric-label">{k}:</div>'
            f'<div class="metric-value">{v}</div>'
            f'</div>'
            for k, v in content.get('analysis', {}).get('metrics', {}).items()
        )}
        </div>
        <p><strong>Assessment:</strong> {content.get('analysis', {}).get('assessment', 'N/A')}</p>
    </div>

    <div class="section">
        <h2>Conclusion</h2>
        <p>{content.get('conclusion', 'N/A')}</p>
    </div>

    <div class="section">
        <h2>References</h2>
        <ul>
        {''.join(f'<li>{r}</li>' for r in content.get('references', []))}
        </ul>
    </div>

    <div class="section">
        <h2>Reviewer Notes</h2>
        <p><em>{content.get('reviewer_notes', 'No notes')}</em></p>
    </div>
</body>
</html>
"""
        return html
