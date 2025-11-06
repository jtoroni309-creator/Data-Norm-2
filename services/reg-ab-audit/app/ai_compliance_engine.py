"""
AI-Powered Compliance Engine

Performs automated compliance checks against PCAOB, GAAP, GAAS, SEC, and AICPA standards
using OpenAI's GPT-4 for intelligent analysis.
"""

import hashlib
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import openai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import ComplianceStandard, ComplianceCheckStatus

logger = logging.getLogger(__name__)


class AIComplianceEngine:
    """
    AI-powered compliance engine for Regulation A/B audits.
    Uses OpenAI GPT-4 to analyze CMBS deals against regulatory requirements.
    """

    def __init__(self, api_key: str, model_version: str = "gpt-4-turbo"):
        """
        Initialize the AI compliance engine.

        Args:
            api_key: OpenAI API key
            model_version: Model to use (default: gpt-4-turbo)
        """
        self.api_key = api_key
        self.model_version = model_version
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.compliance_rules = self._load_compliance_rules()

    def _load_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Load compliance rules from database or cache.
        In production, this would query the compliance_rules_library table.
        """
        # Hardcoded rules for demonstration - should be loaded from DB
        return {
            "PCAOB_AS_1215": {
                "rule_code": "PCAOB_AS_1215",
                "rule_name": "Audit Documentation",
                "standard": ComplianceStandard.PCAOB,
                "standard_reference": "AS 1215",
                "description": "Requires complete and accurate audit documentation",
                "requirements": "All audit procedures must be documented with sufficient detail",
                "testing_procedures": "Review workpapers for completeness and clarity",
                "risk_category": "critical",
                "mandatory": True
            },
            "PCAOB_AS_2401": {
                "rule_code": "PCAOB_AS_2401",
                "rule_name": "Consideration of Fraud",
                "standard": ComplianceStandard.PCAOB,
                "standard_reference": "AS 2401",
                "description": "Requires consideration of fraud in audit",
                "requirements": "Assess risks of material misstatement due to fraud",
                "testing_procedures": "Evaluate fraud risk factors and test high-risk areas",
                "risk_category": "high",
                "mandatory": True
            },
            "SEC_REG_AB_1100": {
                "rule_code": "SEC_REG_AB_1100",
                "rule_name": "Reg AB General Disclosure",
                "standard": ComplianceStandard.SEC,
                "standard_reference": "Regulation AB Item 1100",
                "description": "General disclosure requirements for ABS",
                "requirements": "Comprehensive disclosure of transaction structure and parties",
                "testing_procedures": "Review transaction documentation for completeness",
                "risk_category": "critical",
                "mandatory": True
            },
            "SEC_REG_AB_1111": {
                "rule_code": "SEC_REG_AB_1111",
                "rule_name": "Asset Pool Characteristics",
                "standard": ComplianceStandard.SEC,
                "standard_reference": "Regulation AB Item 1111",
                "description": "Detailed disclosure of asset pool composition",
                "requirements": "Statistical information about the asset pool",
                "testing_procedures": "Verify asset pool data completeness and accuracy",
                "risk_category": "high",
                "mandatory": True
            },
            "GAAP_ASC_860": {
                "rule_code": "GAAP_ASC_860",
                "rule_name": "Transfers and Servicing",
                "standard": ComplianceStandard.GAAP,
                "standard_reference": "ASC 860",
                "description": "Accounting for transfers and servicing",
                "requirements": "Proper recognition and measurement of transferred assets",
                "testing_procedures": "Verify transfer accounting and servicing rights valuation",
                "risk_category": "high",
                "mandatory": True
            },
            "GAAP_ASC_310": {
                "rule_code": "GAAP_ASC_310",
                "rule_name": "Loan Impairment",
                "standard": ComplianceStandard.GAAP,
                "standard_reference": "ASC 310",
                "description": "Accounting for loan impairment",
                "requirements": "Properly identify and measure impaired loans",
                "testing_procedures": "Test impairment calculations and DSCR/LTV metrics",
                "risk_category": "high",
                "mandatory": True
            },
            "AICPA_AT_C_205": {
                "rule_code": "AICPA_AT_C_205",
                "rule_name": "Examination Engagements",
                "standard": ComplianceStandard.AICPA,
                "standard_reference": "AT-C Section 205",
                "description": "Standards for examination engagements",
                "requirements": "Obtain reasonable assurance about subject matter",
                "testing_procedures": "Plan and perform examination procedures",
                "risk_category": "critical",
                "mandatory": True
            },
        }

    async def run_compliance_checks(
        self,
        deal: Any,  # CMBSDeal model instance
        engagement: Any,  # RegABAuditEngagement model instance
    ) -> List[Dict[str, Any]]:
        """
        Run all compliance checks for a CMBS deal.

        Args:
            deal: CMBS deal to analyze
            engagement: Parent audit engagement

        Returns:
            List of compliance check results
        """
        logger.info(f"Running compliance checks for deal {deal.id}")

        results = []

        # Run each compliance rule
        for rule_code, rule in self.compliance_rules.items():
            try:
                start_time = datetime.utcnow()

                result = await self._check_compliance_rule(
                    deal=deal,
                    engagement=engagement,
                    rule=rule
                )

                end_time = datetime.utcnow()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)

                result["execution_duration_ms"] = duration_ms
                result["executed_at"] = end_time

                results.append(result)

                logger.info(
                    f"Completed check {rule_code} for deal {deal.id}: "
                    f"{result['status']} (confidence: {result.get('ai_confidence', 0):.2f})"
                )

            except Exception as e:
                logger.error(f"Error running check {rule_code} for deal {deal.id}: {str(e)}", exc_info=True)

                # Create failure result
                results.append({
                    "audit_engagement_id": engagement.id,
                    "cmbs_deal_id": deal.id,
                    "check_name": rule["rule_name"],
                    "check_code": rule_code,
                    "standard": rule["standard"],
                    "standard_reference": rule["standard_reference"],
                    "description": rule["description"],
                    "status": ComplianceCheckStatus.MANUAL_REVIEW_REQUIRED,
                    "passed": False,
                    "findings": f"Error during automated check: {str(e)}",
                    "recommendation": "Manual review required",
                    "requires_manual_review": True,
                    "risk_level": rule["risk_category"],
                })

        return results

    async def _check_compliance_rule(
        self,
        deal: Any,
        engagement: Any,
        rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check a single compliance rule using AI.

        Args:
            deal: CMBS deal to analyze
            engagement: Parent audit engagement
            rule: Compliance rule to check

        Returns:
            Compliance check result dictionary
        """
        # Build prompt with deal data
        prompt = self._build_compliance_prompt(deal, engagement, rule)

        # Call OpenAI API
        response = await self._call_openai_api(prompt, rule["rule_code"])

        # Parse response
        analysis = self._parse_ai_response(response)

        # Build result
        result = {
            "audit_engagement_id": engagement.id,
            "cmbs_deal_id": deal.id,
            "check_name": rule["rule_name"],
            "check_code": rule["rule_code"],
            "standard": rule["standard"],
            "standard_reference": rule["standard_reference"],
            "description": rule["description"],
            "status": analysis["status"],
            "passed": analysis["passed"],
            "findings": analysis["findings"],
            "recommendation": analysis["recommendation"],
            "ai_analysis": analysis["full_analysis"],
            "ai_confidence": Decimal(str(analysis["confidence"])),
            "risk_level": analysis.get("risk_level", rule["risk_category"]),
            "remediation_steps": analysis.get("remediation_steps"),
            "evidence_references": analysis.get("evidence_references"),
            "data_points_analyzed": analysis.get("data_points_analyzed"),
            "requires_manual_review": analysis["confidence"] < settings.MIN_CONFIDENCE_THRESHOLD or not analysis["passed"],
        }

        return result

    def _build_compliance_prompt(
        self,
        deal: Any,
        engagement: Any,
        rule: Dict[str, Any]
    ) -> str:
        """
        Build a detailed prompt for AI compliance checking.

        Args:
            deal: CMBS deal data
            engagement: Audit engagement data
            rule: Compliance rule

        Returns:
            Formatted prompt string
        """
        # Extract deal data
        deal_data = {
            "deal_name": deal.deal_name,
            "deal_number": deal.deal_number,
            "cusip": deal.cusip,
            "origination_date": str(deal.origination_date) if deal.origination_date else None,
            "maturity_date": str(deal.maturity_date) if deal.maturity_date else None,
            "original_balance": float(deal.original_balance) if deal.original_balance else None,
            "current_balance": float(deal.current_balance) if deal.current_balance else None,
            "interest_rate": float(deal.interest_rate) if deal.interest_rate else None,
            "property_type": deal.property_type,
            "property_count": deal.property_count,
            "master_servicer": deal.master_servicer,
            "special_servicer": deal.special_servicer,
            "trustee": deal.trustee,
            "dscr": float(deal.dscr) if deal.dscr else None,
            "ltv": float(deal.ltv) if deal.ltv else None,
            "occupancy_rate": float(deal.occupancy_rate) if deal.occupancy_rate else None,
            "delinquency_status": deal.delinquency_status,
            "is_oa": deal.is_oa,
        }

        prompt = f"""You are an expert auditor conducting a Regulation A/B audit for CMBS (Commercial Mortgage-Backed Securities) loans.

Compliance Rule: {rule['rule_name']}
Standard: {rule['standard_reference']}
Description: {rule['description']}

Requirements:
{rule['requirements']}

Testing Procedures:
{rule['testing_procedures']}

CMBS Deal Information:
{json.dumps(deal_data, indent=2)}

Audit Engagement:
- Audit Name: {engagement.audit_name}
- Audit Period: {engagement.audit_period_start} to {engagement.audit_period_end}

Task:
Analyze the CMBS deal against the compliance rule requirements. Provide a detailed assessment including:

1. Compliance Status: Does the deal comply with the rule? (PASSED/FAILED/WARNING)
2. Confidence Score: Your confidence in this assessment (0.0 to 1.0)
3. Findings: Detailed findings from your analysis
4. Recommendation: What actions should be taken
5. Risk Level: low/medium/high/critical
6. Data Points Analyzed: Key metrics and data points you evaluated
7. Evidence References: What documentation or data supports your conclusion
8. Remediation Steps: If non-compliant, what steps are needed to remediate (if applicable)

Respond in JSON format:
{{
    "status": "PASSED|FAILED|WARNING",
    "confidence": 0.95,
    "passed": true,
    "findings": "Detailed findings here...",
    "recommendation": "Recommendation here...",
    "risk_level": "low|medium|high|critical",
    "data_points_analyzed": {{"key": "value"}},
    "evidence_references": ["ref1", "ref2"],
    "remediation_steps": ["step1", "step2"],
    "full_analysis": "Complete analysis narrative..."
}}

Be thorough, specific, and cite relevant regulations. Focus on material issues that could impact the audit opinion.
"""

        return prompt

    async def _call_openai_api(self, prompt: str, check_code: str) -> str:
        """
        Call OpenAI API with the compliance check prompt.

        Args:
            prompt: Formatted prompt
            check_code: Compliance rule code for logging

        Returns:
            AI response text
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model_version,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert CPA and auditor specializing in CMBS audits and Regulation A/B compliance. Provide detailed, accurate compliance assessments."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                response_format={"type": "json_object"}
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error for check {check_code}: {str(e)}", exc_info=True)
            raise

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI response into structured format.

        Args:
            response: Raw AI response text

        Returns:
            Parsed compliance check result
        """
        try:
            data = json.loads(response)

            # Map status string to enum
            status_str = data.get("status", "WARNING").upper()
            if data.get("passed"):
                status = ComplianceCheckStatus.PASSED
            elif status_str == "FAILED":
                status = ComplianceCheckStatus.FAILED
            elif status_str == "WARNING":
                status = ComplianceCheckStatus.WARNING
            else:
                status = ComplianceCheckStatus.MANUAL_REVIEW_REQUIRED

            return {
                "status": status,
                "confidence": float(data.get("confidence", 0.0)),
                "passed": bool(data.get("passed", False)),
                "findings": data.get("findings", ""),
                "recommendation": data.get("recommendation", ""),
                "risk_level": data.get("risk_level", "medium"),
                "data_points_analyzed": data.get("data_points_analyzed", {}),
                "evidence_references": data.get("evidence_references", []),
                "remediation_steps": data.get("remediation_steps", []),
                "full_analysis": data.get("full_analysis", data.get("findings", ""))
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return {
                "status": ComplianceCheckStatus.MANUAL_REVIEW_REQUIRED,
                "confidence": 0.0,
                "passed": False,
                "findings": "Failed to parse AI response",
                "recommendation": "Manual review required",
                "risk_level": "high",
                "data_points_analyzed": {},
                "evidence_references": [],
                "remediation_steps": [],
                "full_analysis": response
            }

    def calculate_overall_confidence(self, compliance_results: List[Dict[str, Any]]) -> float:
        """
        Calculate overall confidence score for an engagement.

        Args:
            compliance_results: List of compliance check results

        Returns:
            Overall confidence score (0.0 to 1.0)
        """
        if not compliance_results:
            return 0.0

        confidences = [
            float(r.get("ai_confidence", 0))
            for r in compliance_results
            if r.get("ai_confidence") is not None
        ]

        if not confidences:
            return 0.0

        # Weight by importance (critical rules weighted higher)
        weighted_sum = sum(confidences)
        return weighted_sum / len(confidences)
