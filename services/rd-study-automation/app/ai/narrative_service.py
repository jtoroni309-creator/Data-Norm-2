"""
AI Narrative Generation Service

Generates audit-defensible narratives for R&D tax credit studies.
All narratives are evidence-cited and conservative.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class GeneratedNarrative:
    """Generated narrative with metadata."""
    narrative_type: str
    entity_id: Optional[UUID]
    title: str
    content: str
    content_html: str
    evidence_citations: List[Dict[str, Any]]
    confidence: float
    model_used: str
    prompt_version: str
    generated_at: datetime


class NarrativeService:
    """
    AI-powered narrative generation service.

    Generates:
    - Executive summaries
    - Project qualification narratives
    - Employee role narratives
    - QRE schedule narratives
    - 4-part test analysis narratives

    All narratives are:
    - Evidence-cited
    - Conservative (no aggressive language)
    - Factual (never invent numbers or details)
    - Audit-defensible
    """

    PROMPT_VERSION = "v2024.1"

    def __init__(self, openai_client=None, config: Optional[Dict] = None):
        self.openai_client = openai_client
        self.config = config or {}
        self.model = self.config.get("model", "gpt-4-turbo-preview")

    async def generate_executive_summary(
        self,
        study_data: Dict[str, Any],
        projects: List[Dict[str, Any]],
        qre_summary: Dict[str, Any],
        calculation_result: Dict[str, Any]
    ) -> GeneratedNarrative:
        """
        Generate executive summary for R&D study.

        Summary includes:
        - Overview of the study and taxpayer
        - Qualified research activities identified
        - QRE summary by category
        - Credit amounts (Federal and state)
        - Key assumptions and limitations
        """
        prompt = self._build_executive_summary_prompt(
            study_data, projects, qre_summary, calculation_result
        )

        content = await self._generate_with_guardrails(prompt)

        return GeneratedNarrative(
            narrative_type="executive_summary",
            entity_id=None,
            title="Executive Summary",
            content=content,
            content_html=self._convert_to_html(content),
            evidence_citations=[],
            confidence=0.90,
            model_used=self.model,
            prompt_version=self.PROMPT_VERSION,
            generated_at=datetime.utcnow()
        )

    async def generate_project_narrative(
        self,
        project: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        qualification_result: Dict[str, Any]
    ) -> GeneratedNarrative:
        """
        Generate qualification narrative for a project.

        Narrative addresses:
        - Project overview and business component
        - Analysis of each 4-part test element
        - Evidence supporting qualification
        - Technical uncertainties addressed
        - Process of experimentation used
        """
        prompt = self._build_project_narrative_prompt(
            project, evidence, qualification_result
        )

        content = await self._generate_with_guardrails(prompt)

        # Extract evidence citations
        citations = self._extract_citations(content, evidence)

        return GeneratedNarrative(
            narrative_type="project",
            entity_id=project.get("id"),
            title=f"Project: {project.get('name', 'Unknown')}",
            content=content,
            content_html=self._convert_to_html(content),
            evidence_citations=citations,
            confidence=qualification_result.get("overall_confidence", 0.75),
            model_used=self.model,
            prompt_version=self.PROMPT_VERSION,
            generated_at=datetime.utcnow()
        )

    async def generate_employee_narrative(
        self,
        employee: Dict[str, Any],
        time_allocations: List[Dict[str, Any]],
        projects: List[Dict[str, Any]]
    ) -> GeneratedNarrative:
        """
        Generate R&D-relevant role narrative for an employee.

        Narrative describes:
        - Employee's role and responsibilities
        - Involvement in qualified research activities
        - Time allocation methodology
        - Evidence supporting qualified time percentage
        """
        prompt = self._build_employee_narrative_prompt(
            employee, time_allocations, projects
        )

        content = await self._generate_with_guardrails(prompt)

        return GeneratedNarrative(
            narrative_type="employee",
            entity_id=employee.get("id"),
            title=f"Employee: {employee.get('name', 'Unknown')}",
            content=content,
            content_html=self._convert_to_html(content),
            evidence_citations=[],
            confidence=0.80,
            model_used=self.model,
            prompt_version=self.PROMPT_VERSION,
            generated_at=datetime.utcnow()
        )

    async def generate_four_part_test_narrative(
        self,
        project: Dict[str, Any],
        test_results: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> GeneratedNarrative:
        """
        Generate detailed 4-part test analysis narrative.

        Provides detailed analysis of:
        - Permitted Purpose (IRC §41(d)(1)(B)(i))
        - Technological in Nature (IRC §41(d)(1)(B)(ii))
        - Elimination of Uncertainty (IRC §41(d)(1)(B)(iii))
        - Process of Experimentation (IRC §41(d)(1)(B)(iv))
        """
        prompt = self._build_four_part_test_prompt(
            project, test_results, evidence
        )

        content = await self._generate_with_guardrails(prompt)
        citations = self._extract_citations(content, evidence)

        return GeneratedNarrative(
            narrative_type="four_part_test",
            entity_id=project.get("id"),
            title=f"4-Part Test Analysis: {project.get('name', 'Unknown')}",
            content=content,
            content_html=self._convert_to_html(content),
            evidence_citations=citations,
            confidence=test_results.get("overall_confidence", 0.75),
            model_used=self.model,
            prompt_version=self.PROMPT_VERSION,
            generated_at=datetime.utcnow()
        )

    async def generate_qre_narrative(
        self,
        qre_summary: Dict[str, Any],
        study_data: Dict[str, Any]
    ) -> GeneratedNarrative:
        """
        Generate QRE schedule narrative.

        Describes:
        - Overview of QRE methodology
        - Wage QRE allocation approach
        - Supply expense qualification
        - Contract research treatment
        """
        prompt = self._build_qre_narrative_prompt(qre_summary, study_data)

        content = await self._generate_with_guardrails(prompt)

        return GeneratedNarrative(
            narrative_type="qre_schedule",
            entity_id=None,
            title="Qualified Research Expenses Summary",
            content=content,
            content_html=self._convert_to_html(content),
            evidence_citations=[],
            confidence=0.85,
            model_used=self.model,
            prompt_version=self.PROMPT_VERSION,
            generated_at=datetime.utcnow()
        )

    def _build_executive_summary_prompt(
        self,
        study_data: Dict,
        projects: List[Dict],
        qre_summary: Dict,
        calculation_result: Dict
    ) -> str:
        """Build prompt for executive summary generation."""
        project_names = [p.get("name", "Unknown") for p in projects[:10]]

        return f"""You are a tax professional writing an executive summary for an R&D tax credit study.
Write a professional, audit-defensible executive summary.

IMPORTANT GUIDELINES:
- Be factual and conservative
- Never invent numbers or details
- Use passive voice where appropriate
- Cite IRC Section 41 when referencing tax law
- Do not use aggressive language or overstate claims

STUDY INFORMATION:
- Entity Name: {study_data.get('entity_name', 'N/A')}
- Tax Year: {study_data.get('tax_year', 'N/A')}
- Entity Type: {study_data.get('entity_type', 'N/A')}
- Study Type: R&D Tax Credit Study under IRC Section 41

QUALIFIED PROJECTS IDENTIFIED:
{', '.join(project_names)}

QRE SUMMARY:
- Total QRE Wages: ${qre_summary.get('total_wages', 0):,.2f}
- Total QRE Supplies: ${qre_summary.get('total_supplies', 0):,.2f}
- Total QRE Contract Research: ${qre_summary.get('total_contract_research', 0):,.2f}
- Total QRE: ${qre_summary.get('total_qre', 0):,.2f}

CREDIT CALCULATION:
- Federal Credit Method: {calculation_result.get('selected_method', 'N/A')}
- Federal Credit: ${calculation_result.get('federal_credit', 0):,.2f}
- Total State Credits: ${calculation_result.get('total_state_credits', 0):,.2f}
- Total Credits: ${calculation_result.get('total_credits', 0):,.2f}

Write the executive summary with these sections:
1. Overview (2-3 sentences about the study)
2. Research Activities Summary (brief description of qualifying activities)
3. QRE Analysis (summary of qualified expenses)
4. Credit Calculation Summary (federal and state credits)
5. Assumptions and Limitations (standard disclosures)

Keep the summary to approximately 400-600 words."""

    def _build_project_narrative_prompt(
        self,
        project: Dict,
        evidence: List[Dict],
        qualification_result: Dict
    ) -> str:
        """Build prompt for project narrative generation."""
        evidence_summaries = [
            f"- {e.get('title', 'Evidence')}: {e.get('description', '')[:100]}..."
            for e in evidence[:5]
        ]

        return f"""You are a tax professional writing a project qualification narrative for an R&D tax credit study.

IMPORTANT GUIDELINES:
- Be factual and cite evidence
- Use IRC Section 41 terminology
- Be conservative, not aggressive
- Focus on the 4-part test elements
- Never invent details not supported by evidence

PROJECT INFORMATION:
- Name: {project.get('name', 'N/A')}
- Description: {project.get('description', 'N/A')}
- Department: {project.get('department', 'N/A')}
- Business Component: {project.get('business_component', 'N/A')}

QUALIFICATION SCORES:
- Permitted Purpose: {qualification_result.get('permitted_purpose', {}).get('score', 0)}/100
- Technological Nature: {qualification_result.get('technological_nature', {}).get('score', 0)}/100
- Elimination of Uncertainty: {qualification_result.get('elimination_of_uncertainty', {}).get('score', 0)}/100
- Process of Experimentation: {qualification_result.get('process_of_experimentation', {}).get('score', 0)}/100
- Overall Qualification: {qualification_result.get('qualification_status', 'N/A')}

SUPPORTING EVIDENCE:
{chr(10).join(evidence_summaries) if evidence_summaries else 'Limited evidence available'}

Write a project qualification narrative with these sections:
1. Project Overview (what the project aims to achieve)
2. Permitted Purpose Analysis (new/improved function, performance, reliability, quality)
3. Technological Nature Analysis (reliance on hard sciences)
4. Uncertainty Analysis (technical uncertainties at project inception)
5. Experimentation Analysis (systematic evaluation of alternatives)
6. Qualification Conclusion

Reference evidence where available. Keep to approximately 300-500 words."""

    def _build_employee_narrative_prompt(
        self,
        employee: Dict,
        time_allocations: List[Dict],
        projects: List[Dict]
    ) -> str:
        """Build prompt for employee narrative generation."""
        project_names = [p.get("name", "Unknown") for p in projects[:5]]

        return f"""You are a tax professional writing an employee role narrative for an R&D tax credit study.

IMPORTANT GUIDELINES:
- Describe role in terms of R&D activities
- Be factual about time allocation methodology
- Do not overstate involvement
- Use professional, audit-defensible language

EMPLOYEE INFORMATION:
- Name: {employee.get('name', 'N/A')}
- Title: {employee.get('title', 'N/A')}
- Department: {employee.get('department', 'N/A')}
- Role Category: {employee.get('role_category', 'N/A')}

TIME ALLOCATION:
- Qualified Time Percentage: {employee.get('qualified_time_percentage', 0)}%
- Allocation Source: {employee.get('qualified_time_source', 'estimate')}

PROJECTS SUPPORTED:
{', '.join(project_names) if project_names else 'Various R&D projects'}

Write a brief employee narrative (150-250 words) describing:
1. The employee's role and primary responsibilities
2. How their work supports qualified research activities
3. The basis for the qualified time allocation
4. Any direct supervision or support activities"""

    def _build_four_part_test_prompt(
        self,
        project: Dict,
        test_results: Dict,
        evidence: List[Dict]
    ) -> str:
        """Build prompt for 4-part test narrative."""
        return f"""You are a tax professional writing a detailed 4-part test analysis for an R&D project.

IRC SECTION 41 4-PART TEST REQUIREMENTS:
1. Permitted Purpose (§41(d)(1)(B)(i)): Research must be undertaken to discover information intended to be useful in developing new or improved function, performance, reliability, or quality.

2. Technological in Nature (§41(d)(1)(B)(ii)): Research must rely on principles of physical or biological sciences, engineering, or computer science.

3. Elimination of Uncertainty (§41(d)(1)(B)(iii)): Research must be undertaken to eliminate uncertainty concerning capability, method, or appropriate design.

4. Process of Experimentation (§41(d)(1)(B)(iv)): Research must involve a process of experimentation for a qualified purpose through modeling, simulation, systematic trial and error, or other methods.

PROJECT: {project.get('name', 'Unknown')}
DESCRIPTION: {project.get('description', 'N/A')}

TEST RESULTS:
{json.dumps(test_results, indent=2, default=str) if test_results else 'No results available'}

Write a detailed analysis (500-800 words) covering each element of the 4-part test.
For each element:
- State the requirement
- Describe how the project meets (or does not meet) the requirement
- Reference supporting evidence
- Cite the applicable IRC section"""

    def _build_qre_narrative_prompt(
        self,
        qre_summary: Dict,
        study_data: Dict
    ) -> str:
        """Build prompt for QRE narrative."""
        return f"""You are a tax professional writing a QRE methodology narrative for an R&D tax credit study.

QRE SUMMARY:
- Total Wages QRE: ${qre_summary.get('total_wages', 0):,.2f}
- Total Supplies QRE: ${qre_summary.get('total_supplies', 0):,.2f}
- Total Contract Research QRE: ${qre_summary.get('total_contract_research', 0):,.2f}
- Total QRE: ${qre_summary.get('total_qre', 0):,.2f}

STUDY DETAILS:
- Entity: {study_data.get('entity_name', 'N/A')}
- Tax Year: {study_data.get('tax_year', 'N/A')}

Write a QRE methodology narrative (300-400 words) covering:
1. Overview of QRE categories under IRC §41(b)
2. Wage QRE methodology (how qualified time was determined)
3. Supply QRE methodology (how supplies were identified and allocated)
4. Contract Research treatment (65%/75% limitations)
5. Quality assurance procedures applied"""

    async def _generate_with_guardrails(self, prompt: str) -> str:
        """Generate content with guardrails against fabrication."""
        system_prompt = """You are a conservative tax professional writing audit-defensible documentation.

CRITICAL RULES:
1. NEVER invent numbers, dates, or specific details not provided
2. NEVER use aggressive or promotional language
3. Use phrases like "based on available information" or "according to management" when appropriate
4. If information is missing, acknowledge the limitation
5. Always cite IRC sections correctly
6. Use professional, passive voice where appropriate
7. Do not overstate the strength of positions
8. Include appropriate caveats and limitations"""

        if not self.openai_client:
            return "Narrative generation requires AI service configuration."

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=2000
            )

            content = response.choices[0].message.content

            # Post-processing guardrails
            content = self._apply_guardrails(content)

            return content

        except Exception as e:
            logger.error(f"Narrative generation failed: {e}")
            return "Narrative generation encountered an error. Please review manually."

    def _apply_guardrails(self, content: str) -> str:
        """Apply post-generation guardrails."""
        # Remove any aggressive language
        aggressive_phrases = [
            "clearly qualifies",
            "without doubt",
            "absolutely",
            "guaranteed",
            "certainly",
            "undeniably",
            "unquestionably"
        ]

        for phrase in aggressive_phrases:
            content = content.replace(phrase, "appears to qualify" if "qualifies" in phrase else "")

        # Ensure proper disclaimers are present
        if "limitation" not in content.lower() and len(content) > 500:
            content += "\n\nThis analysis is based on information provided and is subject to review and adjustment."

        return content.strip()

    def _extract_citations(
        self,
        content: str,
        evidence: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Extract evidence citations from narrative content."""
        citations = []

        for i, e in enumerate(evidence):
            title = e.get("title", "")
            if title and title.lower() in content.lower():
                citations.append({
                    "citation_id": f"E{i+1}",
                    "evidence_id": e.get("id"),
                    "title": title,
                    "source_type": e.get("evidence_type", "document")
                })

        return citations

    def _convert_to_html(self, content: str) -> str:
        """Convert markdown content to HTML."""
        # Simple markdown to HTML conversion
        html = content

        # Headers
        html = html.replace("### ", "<h3>").replace("\n", "</h3>\n", 1)
        html = html.replace("## ", "<h2>").replace("\n", "</h2>\n", 1)
        html = html.replace("# ", "<h1>").replace("\n", "</h1>\n", 1)

        # Bold
        import re
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # Paragraphs
        html = "<p>" + html.replace("\n\n", "</p><p>") + "</p>"

        return html


# Import json for the 4-part test prompt
import json
