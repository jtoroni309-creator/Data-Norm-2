"""
AI Audit Program Generator
============================
COMPETITIVE DIFFERENTIATOR #3: Dynamic AI-generated audit programs

vs. ALL Competitors: Static templates vs. intelligent, tech-stack-aware programs

Key Features:
- Auto-discovery of client tech stack
- Risk-based scoping and sample size recommendations
- Custom audit procedures generated for each technology
- Continuous program optimization based on results
"""

import logging
import json
from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .config import settings
from .models import SOCEngagement, ControlObjective

logger = logging.getLogger(__name__)


class AIAuditProgramGenerator:
    """
    Generates custom audit programs using AI based on client's technology stack
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.enabled = settings.ENABLE_AI_PLANNING and settings.OPENAI_API_KEY is not None

    async def discover_tech_stack(
        self,
        db: AsyncSession,
        engagement_id: UUID,
        discovery_method: str = "CLIENT_PROVIDED"
    ) -> List[Dict[str, Any]]:
        """
        Discover client's technology stack

        Methods:
        - CLIENT_PROVIDED: Client fills out tech inventory form
        - NETWORK_SCAN: Scan client network (requires VPN access)
        - API_INTEGRATION: Auto-discover via SSO, HRIS, cloud provider APIs

        Returns:
            List of technologies discovered
        """
        logger.info(f"Discovering tech stack for engagement {engagement_id} via {discovery_method}")

        # Mock tech stack discovery
        discovered_tech = [
            {
                "tech_name": "AWS",
                "tech_vendor": "Amazon Web Services",
                "tech_category": "CLOUD_PROVIDER",
                "criticality": "CRITICAL",
                "user_count": 50,
                "data_classification": ["PII", "CONFIDENTIAL"],
                "supports_sso": True,
                "supports_mfa": True,
                "supports_audit_logs": True
            },
            {
                "tech_name": "Okta",
                "tech_vendor": "Okta",
                "tech_category": "IDENTITY_PROVIDER",
                "criticality": "CRITICAL",
                "user_count": 150,
                "supports_sso": True,
                "supports_mfa": True,
                "supports_audit_logs": True
            },
            {
                "tech_name": "GitHub",
                "tech_vendor": "GitHub",
                "tech_category": "CODE_REPOSITORY",
                "criticality": "HIGH",
                "user_count": 30,
                "supports_audit_logs": True
            },
            {
                "tech_name": "Datadog",
                "tech_vendor": "Datadog",
                "tech_category": "MONITORING",
                "criticality": "HIGH",
                "supports_audit_logs": True
            }
        ]

        # TODO: Save to tech_stack_inventory table

        logger.info(f"Discovered {len(discovered_tech)} technologies")
        return discovered_tech

    async def generate_audit_program(
        self,
        db: AsyncSession,
        engagement_id: UUID,
        control_objective_id: UUID,
        tech_stack: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate custom audit program using AI

        Analyzes tech stack and creates tailored audit procedures

        Args:
            db: Database session
            engagement_id: SOC engagement
            control_objective_id: Which control objective (e.g., CC6.1 Logical Access)
            tech_stack: List of client technologies

        Returns:
            AI-generated audit program with procedures
        """
        if not self.enabled:
            logger.warning("AI audit program generation disabled - using template")
            return self._get_template_program()

        # Fetch control objective
        result = await db.execute(
            select(ControlObjective).where(ControlObjective.id == control_objective_id)
        )
        control_obj = result.scalar_one_or_none()
        if not control_obj:
            raise ValueError(f"Control objective {control_objective_id} not found")

        logger.info(f"Generating AI audit program for {control_obj.objective_code}")

        # Build AI prompt
        prompt = self._build_program_generation_prompt(control_obj, tech_stack)

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert SOC 2 auditor creating custom audit programs. "
                            "Generate detailed, technology-specific audit procedures based on the "
                            "client's tech stack. Include specific steps, evidence requirements, "
                            "sample sizes, and risk factors."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )

            program_data = json.loads(response.choices[0].message.content)

            # Enhance with our risk-based scoping
            program = {
                "id": str(UUID("12345678-1234-5678-1234-567812345678")),
                "engagement_id": str(engagement_id),
                "control_objective_id": str(control_objective_id),
                "program_name": program_data.get("program_name"),
                "program_description": program_data.get("description"),
                "generated_by_ai": True,
                "ai_model": settings.OPENAI_MODEL,
                "generation_timestamp": datetime.utcnow().isoformat(),
                "tech_stack_summary": {
                    "total_technologies": len(tech_stack),
                    "critical_systems": [t["tech_name"] for t in tech_stack if t.get("criticality") == "CRITICAL"],
                    "high_risk_systems": [t["tech_name"] for t in tech_stack if t.get("criticality") == "HIGH"]
                },
                "risk_level": self._assess_risk_level(control_obj, tech_stack),
                "risk_factors": program_data.get("risk_factors", []),
                "recommended_sample_size": program_data.get("recommended_sample_size", 25),
                "recommended_test_frequency": program_data.get("test_frequency", "QUARTERLY"),
                "procedures": program_data.get("procedures", []),
                "expected_evidence": program_data.get("expected_evidence", []),
                "cpa_approved": False,
                "version": 1
            }

            logger.info(f"AI audit program generated: {program['program_name']}")
            return program

        except Exception as e:
            logger.error(f"AI audit program generation failed: {e}")
            return self._get_template_program()

    async def optimize_program_from_results(
        self,
        db: AsyncSession,
        program_id: UUID,
        test_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimize audit program based on actual test results

        Uses AI to analyze what worked/didn't work and suggest improvements

        Args:
            program_id: Audit program to optimize
            test_results: Historical test results

        Returns:
            Optimized program (new version)
        """
        if not self.enabled:
            return {}

        logger.info(f"Optimizing audit program {program_id} based on {len(test_results)} test results")

        # Analyze results
        analysis = {
            "total_tests": len(test_results),
            "passed": sum(1 for r in test_results if r.get("passed")),
            "failed": sum(1 for r in test_results if not r.get("passed")),
            "common_failures": self._identify_common_failures(test_results)
        }

        prompt = f"""
Based on these audit test results, suggest improvements to the audit program:

Test Results Summary: {analysis}

Suggest:
1. Which procedures should be enhanced or added
2. Changes to sample sizes
3. New evidence types to collect
4. Frequency adjustments
5. Technology-specific improvements

Return as JSON with keys: suggestions, enhanced_procedures, adjusted_sample_size
"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert auditor optimizing audit programs based on results."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            optimizations = json.loads(response.choices[0].message.content)
            logger.info("Audit program optimizations generated")

            return {
                "program_id": str(program_id),
                "optimizations": optimizations,
                "requires_cpa_review": True,
                "version": 2
            }

        except Exception as e:
            logger.error(f"Program optimization failed: {e}")
            return {}

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _build_program_generation_prompt(
        self,
        control_obj: ControlObjective,
        tech_stack: List[Dict[str, Any]]
    ) -> str:
        """Build AI prompt for program generation"""
        return f"""
Generate a custom audit program for this SOC 2 control objective:

Control: {control_obj.objective_code} - {control_obj.objective_name}
Description: {control_obj.objective_description}
TSC Category: {control_obj.tsc_category}

Client Technology Stack:
{json.dumps(tech_stack, indent=2)}

Create a detailed audit program with:
1. Program name and description
2. Risk assessment (consider tech complexity, criticality, data sensitivity)
3. Specific audit procedures (step-by-step) tailored to each technology
4. Evidence requirements (exactly what to collect from each system)
5. Recommended sample size (statistical, based on risk)
6. Test frequency (MONTHLY, QUARTERLY, ANNUALLY)
7. Expected outcomes

For each technology, include:
- How to access audit data (APIs, exports, screenshots)
- What configurations to verify
- Specific settings to check
- Red flags to watch for

Return as JSON with keys: program_name, description, risk_factors, procedures (array), expected_evidence (array), recommended_sample_size, test_frequency
"""

    def _assess_risk_level(
        self,
        control_obj: ControlObjective,
        tech_stack: List[Dict[str, Any]]
    ) -> str:
        """
        Assess risk level based on control and tech stack
        """
        # Count critical systems
        critical_count = sum(1 for t in tech_stack if t.get("criticality") == "CRITICAL")

        # High-risk control categories
        high_risk_controls = ["CC6.1", "CC6.2", "CC6.6", "CC7.2"]

        if control_obj.objective_code in high_risk_controls and critical_count >= 3:
            return "CRITICAL"
        elif control_obj.objective_code in high_risk_controls or critical_count >= 2:
            return "HIGH"
        elif critical_count >= 1:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_template_program(self) -> Dict[str, Any]:
        """Fallback template program when AI is disabled"""
        return {
            "program_name": "Standard Access Control Testing",
            "program_description": "Template-based audit program",
            "generated_by_ai": False,
            "procedures": [
                {
                    "step": 1,
                    "description": "Obtain user access listing",
                    "evidence": "User list export"
                },
                {
                    "step": 2,
                    "description": "Verify MFA enforcement",
                    "evidence": "MFA status report"
                }
            ]
        }

    def _identify_common_failures(
        self,
        test_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify common failure patterns"""
        # Simple analysis for now
        failures = [r for r in test_results if not r.get("passed")]

        # Group by failure reason
        failure_reasons = {}
        for f in failures:
            reason = f.get("failure_reason", "Unknown")
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        return [
            {"reason": reason, "count": count}
            for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)
        ]


# Global instance
ai_program_generator = AIAuditProgramGenerator()
