"""
AI-Powered Disclosure Generation Service

Generates FASB-compliant financial statement disclosures using AI
and integrates with engagement workpapers and trial balance data.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import DisclosureRequirement, DisclosureChecklist, ASCTopic
from .config import settings

logger = logging.getLogger(__name__)


class AIDisclosureGenerator:
    """
    AI-powered disclosure generator using LLM service

    Generates FASB-compliant disclosures by:
    1. Analyzing engagement workpapers
    2. Reviewing trial balance and financial data
    3. Identifying applicable ASC topics
    4. Generating disclosure text following FASB Codification
    5. Cross-referencing to audit evidence
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_service_url = settings.LLM_SERVICE_URL or "http://llm.aura-audit-ai.svc.cluster.local:8000"

    async def generate_disclosure(
        self,
        engagement_id: str,
        asc_topic: str,
        requirement_id: str,
        financial_data: Dict[str, Any],
        workpaper_context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, str]:
        """
        Generate a single disclosure using AI

        Args:
            engagement_id: Engagement UUID
            asc_topic: ASC topic number (e.g., "606", "842")
            requirement_id: Specific disclosure requirement ID
            financial_data: Trial balance and financial statement data
            workpaper_context: Related workpaper content for context

        Returns:
            Dictionary with disclosure_text, references, and confidence
        """
        # Get requirement details
        requirement = await self._get_requirement(requirement_id)
        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")

        # Build comprehensive context
        context = await self._build_disclosure_context(
            engagement_id=engagement_id,
            requirement=requirement,
            financial_data=financial_data,
            workpaper_context=workpaper_context or []
        )

        # Generate disclosure using LLM
        disclosure = await self._call_llm_for_disclosure(
            asc_topic=asc_topic,
            requirement=requirement,
            context=context
        )

        return disclosure

    async def generate_all_disclosures(
        self,
        engagement_id: str,
        financial_data: Dict[str, Any],
        entity_type: str = "private"
    ) -> List[Dict[str, Any]]:
        """
        Generate all applicable disclosures for an engagement

        Args:
            engagement_id: Engagement UUID
            financial_data: Complete financial data
            entity_type: public, private, or nonprofit

        Returns:
            List of generated disclosures with metadata
        """
        # Get all applicable requirements for this engagement
        requirements = await self._get_applicable_requirements(
            engagement_id,
            entity_type
        )

        disclosures = []
        for req in requirements:
            try:
                # Get relevant workpapers for this topic
                workpapers = await self._get_related_workpapers(
                    engagement_id,
                    req.asc_topic_number
                )

                disclosure = await self.generate_disclosure(
                    engagement_id=engagement_id,
                    asc_topic=req.asc_topic_number,
                    requirement_id=str(req.id),
                    financial_data=financial_data,
                    workpaper_context=workpapers
                )

                disclosures.append({
                    "requirement_id": str(req.id),
                    "asc_topic": req.asc_topic_number,
                    "title": req.requirement_title,
                    "disclosure_text": disclosure["disclosure_text"],
                    "references": disclosure["references"],
                    "confidence": disclosure["confidence"]
                })

            except Exception as e:
                logger.error(f"Error generating disclosure for {req.requirement_title}: {e}")
                disclosures.append({
                    "requirement_id": str(req.id),
                    "asc_topic": req.asc_topic_number,
                    "title": req.requirement_title,
                    "error": str(e),
                    "disclosure_text": f"[Error generating disclosure: {str(e)}]"
                })

        return disclosures

    async def _get_requirement(self, requirement_id: str) -> Optional[DisclosureRequirement]:
        """Fetch disclosure requirement from database"""
        result = await self.db.execute(
            select(DisclosureRequirement).where(
                DisclosureRequirement.id == requirement_id
            )
        )
        return result.scalar_one_or_none()

    async def _get_applicable_requirements(
        self,
        engagement_id: str,
        entity_type: str
    ) -> List[DisclosureRequirement]:
        """Get all applicable disclosure requirements for engagement"""
        # Get checklist items marked as applicable
        result = await self.db.execute(
            select(DisclosureChecklist, DisclosureRequirement)
            .join(DisclosureRequirement)
            .where(
                DisclosureChecklist.engagement_id == engagement_id,
                DisclosureChecklist.is_applicable == True
            )
        )
        rows = result.all()
        return [row.DisclosureRequirement for row in rows]

    async def _get_related_workpapers(
        self,
        engagement_id: str,
        asc_topic: str
    ) -> List[Dict[str, Any]]:
        """Fetch workpapers related to this ASC topic"""
        # Map ASC topics to workpaper sections
        topic_to_section = {
            "210": ["C", "D", "F"],  # Balance Sheet - Cash, A/R, Inventory
            "310": ["D"],  # Receivables
            "330": ["F"],  # Inventory
            "360": ["G"],  # Property, Plant & Equipment
            "450": ["J"],  # Contingencies
            "470": ["I"],  # Debt
            "606": ["E"],  # Revenue
            "740": ["K"],  # Income Taxes
            "842": ["G"],  # Leases
        }

        sections = topic_to_section.get(asc_topic, [])
        # This would query workpapers - simplified for now
        return []

    async def _build_disclosure_context(
        self,
        engagement_id: str,
        requirement: DisclosureRequirement,
        financial_data: Dict[str, Any],
        workpaper_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build comprehensive context for AI disclosure generation"""
        context = {
            "requirement": {
                "title": requirement.requirement_title,
                "description": requirement.requirement_description,
                "level": requirement.requirement_level,
                "codification_reference": requirement.codification_reference
            },
            "financial_data": financial_data,
            "workpapers": workpaper_context,
            "entity_info": {
                # Would fetch from engagement
                "name": "Entity Name",
                "fiscal_year_end": "2024-12-31",
                "entity_type": "private"
            }
        }
        return context

    async def _call_llm_for_disclosure(
        self,
        asc_topic: str,
        requirement: DisclosureRequirement,
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Call LLM service to generate disclosure text"""

        prompt = self._build_disclosure_prompt(asc_topic, requirement, context)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.llm_service_url}/generate",
                    json={
                        "prompt": prompt,
                        "temperature": 0.1,  # Low temperature for factual accuracy
                        "max_tokens": 2000,
                        "system_message": "You are an expert in FASB Accounting Standards Codification and GAAP-compliant financial statement disclosures. Generate precise, professional disclosure language."
                    }
                )
                response.raise_for_status()
                result = response.json()

                return {
                    "disclosure_text": result.get("text", ""),
                    "references": self._extract_references(result.get("text", "")),
                    "confidence": result.get("confidence", 0.8)
                }

        except Exception as e:
            logger.error(f"Error calling LLM service: {e}")
            # Fallback to template-based disclosure
            return {
                "disclosure_text": self._generate_template_disclosure(asc_topic, requirement, context),
                "references": [requirement.codification_reference],
                "confidence": 0.5
            }

    def _build_disclosure_prompt(
        self,
        asc_topic: str,
        requirement: DisclosureRequirement,
        context: Dict[str, Any]
    ) -> str:
        """Build detailed prompt for LLM"""

        prompt = f"""Generate a FASB-compliant financial statement disclosure for the following requirement:

**ASC Topic**: {asc_topic} - {requirement.asc_topic_name}
**Requirement**: {requirement.requirement_title}
**Description**: {requirement.requirement_description}
**Codification Reference**: {requirement.codification_reference}

**Entity Information**:
- Entity: {context['entity_info']['name']}
- Fiscal Year End: {context['entity_info']['fiscal_year_end']}
- Entity Type: {context['entity_info']['entity_type']}

**Financial Data**:
```
{self._format_financial_data(context['financial_data'])}
```

**Requirements**:
1. Generate professional disclosure language suitable for financial statements
2. Follow FASB Codification guidance precisely
3. Include all required elements per ASC {asc_topic}
4. Use standard accounting terminology
5. Be concise but complete
6. Include quantitative information where applicable
7. Reference the ASC topic appropriately

**Generate the disclosure text below:**
"""
        return prompt

    def _format_financial_data(self, data: Dict[str, Any]) -> str:
        """Format financial data for prompt"""
        # Simplified formatting
        if not data:
            return "No financial data provided"

        formatted = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                formatted.append(f"{key}: ${value:,.2f}")
            else:
                formatted.append(f"{key}: {value}")
        return "\n".join(formatted)

    def _extract_references(self, text: str) -> List[str]:
        """Extract ASC references from generated text"""
        # Simple regex to find ASC references like "ASC 606-10-50-4"
        import re
        pattern = r'ASC\s+\d{3}-\d{2}-\d{2}-\d+'
        return re.findall(pattern, text)

    def _generate_template_disclosure(
        self,
        asc_topic: str,
        requirement: DisclosureRequirement,
        context: Dict[str, Any]
    ) -> str:
        """Generate template-based disclosure as fallback"""

        templates = {
            "606": """Note X - Revenue Recognition

The Company recognizes revenue in accordance with ASC 606, Revenue from Contracts with Customers. Revenue is recognized when control of the promised goods or services is transferred to customers, in an amount that reflects the consideration the Company expects to be entitled to in exchange for those goods or services.

[Additional disclosure details would be populated based on financial data]
""",
            "842": """Note X - Leases

The Company has adopted ASC 842, Leases, which requires lessees to recognize a right-of-use asset and lease liability for all leases with terms greater than 12 months.

[Additional disclosure details would be populated based on financial data]
""",
            "default": f"""Note X - {requirement.requirement_title}

{requirement.requirement_description}

[Disclosure details based on {requirement.codification_reference}]
"""
        }

        return templates.get(asc_topic, templates["default"])


class DisclosureQualityChecker:
    """Validates generated disclosures for completeness and compliance"""

    def __init__(self):
        self.required_elements = {
            "606": ["performance obligations", "timing of revenue recognition", "significant judgments"],
            "842": ["lease terms", "discount rate", "lease expense", "maturity analysis"],
            "740": ["current tax expense", "deferred tax assets", "uncertain tax positions"],
        }

    def check_disclosure_quality(
        self,
        asc_topic: str,
        disclosure_text: str
    ) -> Dict[str, Any]:
        """
        Check disclosure quality and completeness

        Returns:
            Quality score and missing elements
        """
        required = self.required_elements.get(asc_topic, [])
        missing = []

        disclosure_lower = disclosure_text.lower()
        for element in required:
            if element.lower() not in disclosure_lower:
                missing.append(element)

        quality_score = 1.0 - (len(missing) / len(required)) if required else 1.0

        return {
            "quality_score": quality_score,
            "missing_elements": missing,
            "is_complete": len(missing) == 0,
            "recommendations": [
                f"Consider adding disclosure about: {elem}" for elem in missing
            ]
        }
