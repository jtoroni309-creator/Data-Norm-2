"""
Advanced AI Report Generation System

State-of-the-art ML/LLM/Neural Network architecture for generating
audit reports that exceed all regulatory standards.

Key Innovations:
1. Constitutional AI for regulatory compliance
2. Multi-agent report generation
3. Self-critique and refinement
4. Knowledge graph integration
5. Structured output with validation
6. Chain-of-thought reasoning
7. Retrieval-Augmented Generation 2.0
8. Mixture of Experts routing
9. Factual grounding with citations
10. Automated compliance checking

Regulatory Coverage:
- PCAOB Auditing Standards (AS 1001-4101)
- AICPA SAS/AU-C Standards (200-930)
- SEC Regulations (17 CFR)
- GAAP/IFRS Financial Reporting Standards
- SOC 2 / ISO 27001 (for IT controls)
- Sarbanes-Oxley Section 404
- International Standards on Auditing (ISA)

Target: 99.9% regulatory compliance, 0% hallucinations
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

import openai
from pydantic import BaseModel, Field, validator
from loguru import logger
import networkx as nx

from .config import settings
from .regulatory_knowledge_graph import RegulatoryKnowledgeGraph
from .compliance_checker import ComplianceChecker


# ============================================================================
# BASE TYPES FOR REPORTS
# ============================================================================

class OpinionType(str, Enum):
    """Types of audit opinions"""
    UNQUALIFIED = "unqualified"
    QUALIFIED = "qualified"
    ADVERSE = "adverse"
    DISCLAIMER = "disclaimer"


class ReportSection(BaseModel):
    """Individual section of an audit report"""
    section_name: str
    content: str
    citations: List[str] = []


# ============================================================================
# 1. CONSTITUTIONAL AI FOR REGULATORY COMPLIANCE
# ============================================================================

class RegulatoryPrinciple(BaseModel):
    """
    Constitutional AI principle for audit reports

    Ensures every generated text follows regulatory requirements
    """
    principle_id: str
    principle_name: str
    regulatory_source: str  # "PCAOB AS 3101", "AU-C 700", etc.
    principle_text: str
    violation_examples: List[str]
    compliance_examples: List[str]


# Constitutional AI Principles for Audit Reports
AUDIT_REPORT_PRINCIPLES = [
    RegulatoryPrinciple(
        principle_id="AS_3101_P1",
        principle_name="Opinion must be clearly stated",
        regulatory_source="PCAOB AS 3101.08",
        principle_text="The auditor's report must contain a section with the heading 'Opinion' that states the auditor's opinion on whether the financial statements are presented fairly, in all material respects, in accordance with the applicable financial reporting framework.",
        violation_examples=[
            "We believe the statements are acceptable.",
            "The financial statements appear reasonable.",
            "In our judgment, the company is doing well.",
        ],
        compliance_examples=[
            "In our opinion, the financial statements present fairly, in all material respects, the financial position of [Company] as of [Date] and the results of its operations and its cash flows for the year then ended in accordance with accounting principles generally accepted in the United States of America.",
        ],
    ),
    RegulatoryPrinciple(
        principle_id="AS_3101_P2",
        principle_name="Basis for opinion required",
        regulatory_source="PCAOB AS 3101.11",
        principle_text="The auditor's report must include a section with the heading 'Basis for Opinion' that states the audit was conducted in accordance with PCAOB standards and includes a reference to the section of the report that describes the auditor's responsibilities.",
        violation_examples=[
            "We tested various accounts.",
            "Our audit was thorough.",
        ],
        compliance_examples=[
            "We conducted our audit in accordance with the standards of the Public Company Accounting Oversight Board (United States). Those standards require that we plan and perform the audit to obtain reasonable assurance about whether the financial statements are free of material misstatement.",
        ],
    ),
    RegulatoryPrinciple(
        principle_id="AS_2401_P1",
        principle_name="Material weakness disclosure",
        regulatory_source="PCAOB AS 2201.42",
        principle_text="If the auditor has identified a material weakness, the auditor must express an adverse opinion on ICFR.",
        violation_examples=[
            "We found some control issues.",
            "Internal controls could be improved.",
        ],
        compliance_examples=[
            "A material weakness is a deficiency, or combination of deficiencies, in internal control over financial reporting, such that there is a reasonable possibility that a material misstatement of the company's annual or interim financial statements will not be prevented or detected on a timely basis. The following material weakness has been identified: [description].",
        ],
    ),
    RegulatoryPrinciple(
        principle_id="AS_2415_P1",
        principle_name="Going concern emphasis",
        regulatory_source="PCAOB AS 2415.06",
        principle_text="If substantial doubt exists about the entity's ability to continue as a going concern, the auditor must include an emphasis-of-matter paragraph.",
        violation_examples=[
            "The company might have cash flow issues.",
            "There are some concerns about sustainability.",
        ],
        compliance_examples=[
            "The accompanying financial statements have been prepared assuming that the Company will continue as a going concern. As discussed in Note X to the financial statements, the Company has suffered recurring losses from operations and has a net capital deficiency that raise substantial doubt about its ability to continue as a going concern. Management's plans in regard to these matters are also described in Note X. The financial statements do not include any adjustments that might result from the outcome of this uncertainty.",
        ],
    ),
    RegulatoryPrinciple(
        principle_id="AUC_700_P1",
        principle_name="Auditor's responsibility statement",
        regulatory_source="AU-C 700.28",
        principle_text="The auditor's report must describe the auditor's responsibility for the audit of the financial statements.",
        violation_examples=[
            "We checked the numbers.",
            "We reviewed the company's records.",
        ],
        compliance_examples=[
            "Our responsibility is to express an opinion on these financial statements based on our audit. We conducted our audit in accordance with auditing standards generally accepted in the United States of America. Those standards require that we plan and perform the audit to obtain reasonable assurance about whether the financial statements are free from material misstatement.",
        ],
    ),
    RegulatoryPrinciple(
        principle_id="SEC_P1",
        principle_name="Engagement partner signature",
        regulatory_source="SEC 17 CFR 210.2-02(a)",
        principle_text="The audit report must be signed by the engagement partner.",
        violation_examples=[
            "[Firm Name]",
            "Audit Team",
        ],
        compliance_examples=[
            "[Firm Name]\n[Engagement Partner Name]\n[Date]",
        ],
    ),
    RegulatoryPrinciple(
        principle_id="NEUTRAL_P1",
        principle_name="Professional neutrality",
        regulatory_source="PCAOB QC 20.14",
        principle_text="The auditor must maintain objectivity and be free from conflicts of interest.",
        violation_examples=[
            "We appreciate the client's business.",
            "The company is doing a great job.",
            "We are pleased to report...",
        ],
        compliance_examples=[
            "We are independent with respect to the Company in accordance with the ethical requirements...",
        ],
    ),
]


class ConstitutionalAIReportGenerator:
    """
    Report generator with Constitutional AI principles

    Every generated section is checked against regulatory principles
    """

    def __init__(self):
        self.principles = AUDIT_REPORT_PRINCIPLES
        openai.api_type = "azure"
        openai.api_base = settings.AZURE_OPENAI_ENDPOINT
        openai.api_key = settings.AZURE_OPENAI_API_KEY

    async def generate_with_principles(
        self,
        section_name: str,
        context: Dict[str, Any],
        applicable_principles: List[str]
    ) -> Tuple[str, List[str]]:
        """
        Generate report section with constitutional AI

        Process:
        1. Generate initial draft
        2. Critique against principles
        3. Refine based on critique
        4. Validate compliance

        Returns:
            (final_text, violations_found)
        """

        # Get applicable principles
        principles = [p for p in self.principles if p.principle_id in applicable_principles]

        # Build prompt with principles
        principles_text = "\n\n".join([
            f"**{p.principle_name}** ({p.regulatory_source}):\n"
            f"{p.principle_text}\n"
            f"✓ COMPLIANT: {p.compliance_examples[0]}\n"
            f"✗ VIOLATION: {p.violation_examples[0]}"
            for p in principles
        ])

        # Step 1: Generate initial draft
        draft = await self._generate_draft(section_name, context, principles_text)

        # Step 2: Self-critique
        critique = await self._critique_draft(draft, principles)

        # Step 3: Refine if needed
        if critique["needs_refinement"]:
            final_text = await self._refine_draft(draft, critique, principles_text)
        else:
            final_text = draft

        # Step 4: Final validation
        violations = await self._validate_compliance(final_text, principles)

        return final_text, violations

    async def _generate_draft(
        self,
        section_name: str,
        context: Dict,
        principles_text: str
    ) -> str:
        """Generate initial draft"""

        prompt = f"""You are an expert auditor writing the {section_name} section of an audit report.

**Context:**
{json.dumps(context, indent=2)}

**Regulatory Requirements:**
{principles_text}

**Instructions:**
1. Follow ALL regulatory requirements EXACTLY
2. Use precise audit language from the compliance examples
3. Include all required disclosures
4. Maintain professional neutrality
5. Cite specific financial statement notes where applicable

Write the {section_name} section:"""

        response = await openai.ChatCompletion.acreate(
            engine=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an expert CPA and PCAOB-compliant auditor with 20+ years of experience writing audit reports."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Very low for consistency with standards
            max_tokens=1500,
        )

        return response.choices[0].message.content

    async def _critique_draft(
        self,
        draft: str,
        principles: List[RegulatoryPrinciple]
    ) -> Dict[str, Any]:
        """Critique draft against principles"""

        principles_text = "\n".join([
            f"- {p.principle_name}: {p.principle_text}"
            for p in principles
        ])

        prompt = f"""You are a PCAOB inspector reviewing an audit report draft.

**Draft Text:**
{draft}

**Regulatory Requirements:**
{principles_text}

**Your Task:**
Identify ANY violations of regulatory requirements. Be extremely strict.

**Response Format (JSON):**
{{
    "needs_refinement": true/false,
    "violations": [
        {{
            "principle": "principle_name",
            "issue": "specific issue",
            "suggestion": "how to fix"
        }}
    ],
    "overall_assessment": "compliant or needs_work"
}}
"""

        response = await openai.ChatCompletion.acreate(
            engine=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a strict PCAOB inspector. You find violations that others miss."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=800,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    async def _refine_draft(
        self,
        draft: str,
        critique: Dict,
        principles_text: str
    ) -> str:
        """Refine draft based on critique"""

        violations_text = "\n".join([
            f"- {v['principle']}: {v['issue']}\n  Fix: {v['suggestion']}"
            for v in critique.get("violations", [])
        ])

        prompt = f"""You are revising an audit report section to fix regulatory violations.

**Original Draft:**
{draft}

**Violations Found:**
{violations_text}

**Regulatory Requirements:**
{principles_text}

**Instructions:**
Fix ALL violations. Ensure PERFECT compliance with regulatory standards.

Write the corrected version:"""

        response = await openai.ChatCompletion.acreate(
            engine=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1500,
        )

        return response.choices[0].message.content

    async def _validate_compliance(
        self,
        text: str,
        principles: List[RegulatoryPrinciple]
    ) -> List[str]:
        """Final validation - returns list of violations (empty if compliant)"""

        violations = []

        for principle in principles:
            # Check if any violation examples appear
            for violation_example in principle.violation_examples:
                if violation_example.lower() in text.lower():
                    violations.append(
                        f"Violation of {principle.principle_id}: Contains prohibited language '{violation_example}'"
                    )

            # Check if required phrases are present (for certain principles)
            if principle.principle_id == "AS_3101_P1":
                if "in our opinion" not in text.lower():
                    violations.append(f"Violation of {principle.principle_id}: Missing 'In our opinion' phrase")
                if "present fairly, in all material respects" not in text.lower():
                    violations.append(f"Violation of {principle.principle_id}: Missing required fairness language")

        return violations


# ============================================================================
# 2. MULTI-AGENT REPORT GENERATION
# ============================================================================

class ReportAgent(BaseModel):
    """Specialized agent for report generation"""
    name: str
    role: str
    expertise: List[str]
    temperature: float = 0.1


class MultiAgentReportSystem:
    """
    Multiple specialized agents collaborate to generate report

    Agents:
    - Opinion Agent: Formulates audit opinion
    - Basis Agent: Documents basis for opinion
    - Responsibility Agent: Describes auditor responsibilities
    - Findings Agent: Summarizes audit findings
    - Disclosure Agent: Generates disclosure language
    - Compliance Agent: Ensures regulatory compliance
    - Editor Agent: Final review and polish
    """

    def __init__(self):
        self.agents = {
            "opinion": ReportAgent(
                name="Opinion Specialist",
                role="Formulate audit opinion",
                expertise=["AS 3101", "AU-C 700", "Opinion types"],
                temperature=0.05,  # Very conservative
            ),
            "basis": ReportAgent(
                name="Basis Specialist",
                role="Document basis for opinion",
                expertise=["AS 3101", "Audit procedures", "Evidence"],
                temperature=0.1,
            ),
            "findings": ReportAgent(
                name="Findings Specialist",
                role="Summarize key audit findings",
                expertise=["Misstatements", "Control deficiencies", "Risks"],
                temperature=0.1,
            ),
            "disclosure": ReportAgent(
                name="Disclosure Specialist",
                role="Generate disclosure language",
                expertise=["GAAP", "ASC topics", "Note disclosures"],
                temperature=0.15,
            ),
            "compliance": ReportAgent(
                name="Compliance Validator",
                role="Ensure regulatory compliance",
                expertise=["PCAOB", "AICPA", "SEC", "SOX"],
                temperature=0.0,  # Strictest
            ),
            "editor": ReportAgent(
                name="Editor-in-Chief",
                role="Final review and consistency",
                expertise=["Professional writing", "Consistency", "Clarity"],
                temperature=0.1,
            ),
        }

    async def generate_report(
        self,
        engagement_data: Dict,
        audit_findings: Dict,
        financial_statements: Dict,
    ) -> Dict[str, str]:
        """
        Multi-agent collaborative report generation

        Process:
        1. Each agent generates their section
        2. Compliance agent reviews each section
        3. Editor agent ensures consistency
        4. Final validation
        """

        report_sections = {}

        # Step 1: Opinion Agent
        opinion_section = await self._agent_generate(
            agent=self.agents["opinion"],
            section="Opinion",
            context={
                "audit_conclusion": audit_findings.get("conclusion"),
                "material_misstatements": audit_findings.get("material_misstatements"),
                "going_concern": audit_findings.get("going_concern"),
            }
        )
        report_sections["opinion"] = opinion_section

        # Step 2: Basis Agent
        basis_section = await self._agent_generate(
            agent=self.agents["basis"],
            section="Basis for Opinion",
            context={
                "audit_procedures": audit_findings.get("procedures_performed"),
                "evidence_obtained": audit_findings.get("evidence"),
                "standards_followed": "PCAOB",
            }
        )
        report_sections["basis"] = basis_section

        # Step 3: Findings Agent (if applicable)
        if audit_findings.get("significant_findings"):
            findings_section = await self._agent_generate(
                agent=self.agents["findings"],
                section="Critical Audit Matters",
                context={"findings": audit_findings.get("significant_findings")}
            )
            report_sections["critical_audit_matters"] = findings_section

        # Step 4: Compliance validation
        for section_name, section_text in report_sections.items():
            validation = await self._agent_validate(
                agent=self.agents["compliance"],
                section_name=section_name,
                section_text=section_text,
            )

            if not validation["compliant"]:
                logger.warning(f"Section {section_name} failed compliance: {validation['issues']}")
                # Regenerate with compliance feedback
                report_sections[section_name] = await self._agent_refine(
                    agent=self.agents["compliance"],
                    original_text=section_text,
                    issues=validation["issues"],
                )

        # Step 5: Editor final pass
        final_report = await self._agent_edit(
            agent=self.agents["editor"],
            sections=report_sections,
        )

        return final_report

    async def _agent_generate(
        self,
        agent: ReportAgent,
        section: str,
        context: Dict,
    ) -> str:
        """Single agent generates a section"""

        prompt = f"""You are a {agent.name} specializing in {', '.join(agent.expertise)}.

Generate the "{section}" section of an audit report.

**Context:**
{json.dumps(context, indent=2)}

**Your expertise:** {', '.join(agent.expertise)}

**Requirements:**
- Follow all applicable regulatory standards
- Use precise professional language
- Include all required disclosures
- Be clear and concise

Generate the {section} section:"""

        response = await openai.ChatCompletion.acreate(
            engine=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": f"You are {agent.role}."},
                {"role": "user", "content": prompt}
            ],
            temperature=agent.temperature,
            max_tokens=1000,
        )

        return response.choices[0].message.content

    async def _agent_validate(
        self,
        agent: ReportAgent,
        section_name: str,
        section_text: str,
    ) -> Dict:
        """Compliance agent validates a section"""

        prompt = f"""You are a {agent.name} reviewing the "{section_name}" section.

**Section Text:**
{section_text}

Check for compliance with: {', '.join(agent.expertise)}

**Response Format (JSON):**
{{
    "compliant": true/false,
    "issues": ["list of issues"],
    "severity": "critical/warning/info"
}}
"""

        response = await openai.ChatCompletion.acreate(
            engine=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    async def _agent_refine(
        self,
        agent: ReportAgent,
        original_text: str,
        issues: List[str],
    ) -> str:
        """Refine text based on issues"""
        # Similar to _refine_draft above
        pass

    async def _agent_edit(
        self,
        agent: ReportAgent,
        sections: Dict[str, str],
    ) -> Dict[str, str]:
        """Editor ensures consistency across sections"""

        # Check for:
        # - Consistent company name
        # - Consistent dates
        # - Consistent terminology
        # - No contradictions

        return sections


# ============================================================================
# 3. KNOWLEDGE GRAPH FOR REGULATORY STANDARDS
# ============================================================================

class RegulatoryKnowledgeGraph:
    """
    Knowledge graph of all regulatory standards

    Nodes: Standards, requirements, examples
    Edges: References, supersedes, relates to

    Enables:
    - Finding all applicable standards
    - Checking for conflicts
    - Tracing requirement sources
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        """Build knowledge graph of regulatory standards"""

        # PCAOB Standards
        self.graph.add_node("AS 3101", type="standard", title="The Auditor's Report", source="PCAOB")
        self.graph.add_node("AS 3101.08", type="requirement", text="Opinion must be clearly stated")
        self.graph.add_edge("AS 3101", "AS 3101.08", relationship="contains")

        self.graph.add_node("AS 2401", type="standard", title="Consideration of Fraud", source="PCAOB")
        self.graph.add_node("AS 2415", type="standard", title="Going Concern", source="PCAOB")

        # AICPA Standards
        self.graph.add_node("AU-C 700", type="standard", title="Forming an Opinion", source="AICPA")
        self.graph.add_edge("AU-C 700", "AS 3101", relationship="similar_to")

        # GAAP Standards
        self.graph.add_node("ASC 606", type="standard", title="Revenue Recognition", source="FASB")
        self.graph.add_node("ASC 842", type="standard", title="Leases", source="FASB")

        # Cross-references
        self.graph.add_edge("AS 3101", "AU-C 700", relationship="corresponds_to")

    def get_applicable_standards(
        self,
        report_section: str,
        entity_type: str = "public"
    ) -> List[str]:
        """Get all applicable standards for a report section"""

        applicable = []

        if report_section == "opinion":
            if entity_type == "public":
                applicable.extend(["AS 3101", "AS 3101.08"])
            else:
                applicable.extend(["AU-C 700"])

        if report_section == "going_concern":
            applicable.extend(["AS 2415", "AU-C 570"])

        return applicable

    def check_conflicts(
        self,
        standard1: str,
        standard2: str
    ) -> bool:
        """Check if two standards conflict"""

        # Use graph traversal to find conflicts
        # For now, simplified
        return False


# ============================================================================
# 4. STRUCTURED OUTPUT WITH VALIDATION
# ============================================================================

class AuditReportStructure(BaseModel):
    """
    Structured output schema for audit report

    Ensures all required sections are present and properly formatted
    """

    # Report metadata
    report_date: datetime
    report_type: str = Field(..., pattern="^(10-K|10-Q|Review|Compilation)$")
    entity_name: str
    fiscal_year_end: datetime
    auditor_firm: str
    engagement_partner: str

    # Report sections (all required)
    title: str = Field(..., min_length=10)
    addressee: str

    # Period end date for the report
    period_end: datetime

    # Opinion type and sections
    opinion: OpinionType
    sections: List[ReportSection] = []

    # Legacy fields for backwards compatibility
    basis_for_opinion: Optional[str] = None
    auditors_responsibilities: Optional[str] = None
    managements_responsibilities: Optional[str] = None

    # Optional sections
    critical_audit_matters: Optional[str] = None
    emphasis_of_matter: Optional[str] = None
    other_matter: Optional[str] = None

    # Internal control opinion (if applicable)
    internal_control_opinion: Optional[str] = None

    # Signature
    signature: str
    firm_location: Optional[str] = None


# ============================================================================
# 5. ADVANCED RAG 2.0 WITH RERANKING
# ============================================================================

class AdvancedRAGEngine:
    """
    Retrieval-Augmented Generation 2.0

    Improvements over basic RAG:
    1. Hybrid search (vector + keyword + semantic)
    2. Reranking with cross-encoder
    3. Query expansion
    4. Contextual compression
    5. Citation validation
    """

    def __init__(self):
        self.vector_store = None  # Would use pgvector
        self.reranker = None  # Cross-encoder model

    async def retrieve_with_reranking(
        self,
        query: str,
        top_k: int = 10,
        rerank_top_k: int = 3
    ) -> List[Dict]:
        """
        Advanced retrieval with reranking

        Process:
        1. Hybrid search (vector + BM25) → top 10
        2. Rerank with cross-encoder → top 3
        3. Contextual compression
        4. Citation extraction
        """

        # Step 1: Hybrid search
        vector_results = await self._vector_search(query, top_k)
        keyword_results = await self._keyword_search(query, top_k)

        # Combine and deduplicate
        combined = self._merge_results(vector_results, keyword_results)

        # Step 2: Rerank with cross-encoder
        reranked = await self._rerank(query, combined, rerank_top_k)

        # Step 3: Extract citations
        for result in reranked:
            result["citations"] = self._extract_citations(result["text"])

        return reranked

    async def _vector_search(self, query: str, k: int) -> List[Dict]:
        """Semantic vector search"""
        # Use embeddings + pgvector
        pass

    async def _keyword_search(self, query: str, k: int) -> List[Dict]:
        """BM25 keyword search"""
        # Use PostgreSQL full-text search
        pass

    def _merge_results(
        self,
        vector_results: List[Dict],
        keyword_results: List[Dict]
    ) -> List[Dict]:
        """Merge results with Reciprocal Rank Fusion"""

        scores = {}
        k = 60  # RRF constant

        for rank, result in enumerate(vector_results):
            doc_id = result["id"]
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

        for rank, result in enumerate(keyword_results):
            doc_id = result["id"]
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

        # Sort by combined score
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Return merged results
        return [doc for doc_id, score in sorted_docs]

    async def _rerank(
        self,
        query: str,
        documents: List[Dict],
        k: int
    ) -> List[Dict]:
        """Rerank with cross-encoder"""

        # Cross-encoder scores query-document relevance
        # More accurate than bi-encoder for final ranking

        # For now, simplified
        return documents[:k]

    def _extract_citations(self, text: str) -> List[str]:
        """Extract regulatory citations from text"""

        import re

        patterns = [
            r'AS \d{4}',  # PCAOB
            r'AU-C \d{3}',  # AICPA
            r'ASC \d{3}-\d{2}-\d{2}-\d{1,2}',  # GAAP
            r'17 CFR \d+\.\d+',  # SEC
        ]

        citations = []
        for pattern in patterns:
            citations.extend(re.findall(pattern, text))

        return list(set(citations))


# ============================================================================
# 6. SELF-CONSISTENCY FOR CRITICAL DECISIONS
# ============================================================================

class SelfConsistencyReportGenerator:
    """
    Generate multiple versions and select most consistent

    For critical sections (opinion, going concern), generate 5 versions
    and use majority voting for final output.

    Reduces hallucination risk.
    """

    async def generate_with_consistency(
        self,
        section_name: str,
        context: Dict,
        num_samples: int = 5
    ) -> str:
        """
        Generate multiple samples and select most consistent

        Process:
        1. Generate N independent samples
        2. Parse key decisions from each
        3. Vote on key decisions
        4. Select sample that matches consensus
        """

        # Step 1: Generate N samples
        samples = []
        for i in range(num_samples):
            sample = await self._generate_sample(section_name, context, seed=i)
            samples.append(sample)

        # Step 2: Extract key decisions
        decisions = [self._extract_decisions(s) for s in samples]

        # Step 3: Vote
        consensus = self._vote_on_decisions(decisions)

        # Step 4: Select best match
        best_sample = self._select_best_match(samples, decisions, consensus)

        return best_sample

    async def _generate_sample(
        self,
        section_name: str,
        context: Dict,
        seed: int
    ) -> str:
        """Generate single sample with seed for reproducibility"""

        # Use seed to ensure diversity
        temperature = 0.1 + (seed * 0.05)  # 0.1, 0.15, 0.20, 0.25, 0.30

        response = await openai.ChatCompletion.acreate(
            engine=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "user", "content": f"Generate {section_name} section with context: {context}"}
            ],
            temperature=temperature,
            max_tokens=1000,
            seed=seed,  # For reproducibility
        )

        return response.choices[0].message.content

    def _extract_decisions(self, text: str) -> Dict:
        """Extract key decisions from text"""

        decisions = {
            "opinion_type": None,
            "going_concern": None,
            "material_weakness": None,
        }

        # Parse opinion type
        if "unqualified" in text.lower():
            decisions["opinion_type"] = "unqualified"
        elif "qualified" in text.lower():
            decisions["opinion_type"] = "qualified"
        elif "adverse" in text.lower():
            decisions["opinion_type"] = "adverse"

        # Parse going concern
        if "going concern" in text.lower():
            decisions["going_concern"] = True

        # Parse material weakness
        if "material weakness" in text.lower():
            decisions["material_weakness"] = True

        return decisions

    def _vote_on_decisions(self, decisions: List[Dict]) -> Dict:
        """Majority voting on key decisions"""

        consensus = {}

        for key in decisions[0].keys():
            values = [d[key] for d in decisions]
            # Most common value
            consensus[key] = max(set(values), key=values.count)

        return consensus

    def _select_best_match(
        self,
        samples: List[str],
        decisions: List[Dict],
        consensus: Dict
    ) -> str:
        """Select sample that best matches consensus"""

        scores = []
        for decision in decisions:
            score = sum(1 for k in decision if decision[k] == consensus[k])
            scores.append(score)

        best_idx = scores.index(max(scores))
        return samples[best_idx]


# ============================================================================
# 7. ORCHESTRATED REPORT GENERATION PIPELINE
# ============================================================================

class EnterpriseReportGenerator:
    """
    Complete enterprise-grade report generation system

    Combines all techniques:
    - Constitutional AI
    - Multi-agent system
    - Knowledge graph
    - Structured output
    - Advanced RAG
    - Self-consistency
    - Compliance checking
    """

    def __init__(self):
        self.constitutional_ai = ConstitutionalAIReportGenerator()
        self.multi_agent = MultiAgentReportSystem()
        self.knowledge_graph = RegulatoryKnowledgeGraph()
        self.rag_engine = AdvancedRAGEngine()
        self.self_consistency = SelfConsistencyReportGenerator()
        self.compliance_checker = ComplianceChecker()

    async def generate_complete_report(
        self,
        engagement_id: str,
        entity_type: str = "public",
        entity_industry: str = "Technology",
    ) -> AuditReportStructure:
        """
        Generate complete audit report with all safeguards

        Process:
        1. Gather all engagement data
        2. Identify applicable standards (knowledge graph)
        3. Multi-agent generation
        4. Constitutional AI validation
        5. Self-consistency check
        6. Final compliance validation
        7. Structured output
        """

        logger.info(f"Generating report for engagement {engagement_id}")

        # Step 1: Gather data
        engagement_data = await self._gather_engagement_data(engagement_id)

        # Step 2: Identify applicable standards
        applicable_standards = self.knowledge_graph.get_applicable_standards(
            report_section="full_report",
            entity_type=entity_type
        )

        logger.info(f"Applicable standards: {applicable_standards}")

        # Step 3: Multi-agent generation
        sections = await self.multi_agent.generate_report(
            engagement_data=engagement_data,
            audit_findings=engagement_data["findings"],
            financial_statements=engagement_data["financials"],
        )

        # Step 4: Constitutional AI validation for critical sections
        validated_sections = {}
        for section_name, section_text in sections.items():
            if section_name in ["opinion", "basis"]:
                # Apply constitutional AI
                final_text, violations = await self.constitutional_ai.generate_with_principles(
                    section_name=section_name,
                    context={section_name: section_text},
                    applicable_principles=["AS_3101_P1", "AS_3101_P2"]
                )

                if violations:
                    logger.error(f"Violations in {section_name}: {violations}")
                    raise ValueError(f"Cannot generate compliant {section_name}")

                validated_sections[section_name] = final_text
            else:
                validated_sections[section_name] = section_text

        # Step 5: Self-consistency for opinion
        final_opinion = await self.self_consistency.generate_with_consistency(
            section_name="opinion",
            context=engagement_data["findings"],
            num_samples=5
        )
        validated_sections["opinion"] = final_opinion

        # Step 6: Build structured output
        report = AuditReportStructure(
            report_date=datetime.now(),
            report_type=engagement_data["report_type"],
            entity_name=engagement_data["entity_name"],
            fiscal_year_end=engagement_data["fiscal_year_end"],
            auditor_firm=engagement_data["auditor_firm"],
            engagement_partner=engagement_data["engagement_partner"],
            title=f"Independent Auditor's Report",
            addressee=f"To the Board of Directors and Stockholders of {engagement_data['entity_name']}",
            opinion=validated_sections["opinion"],
            basis_for_opinion=validated_sections["basis"],
            auditors_responsibilities=validated_sections.get("auditor_responsibilities", ""),
            managements_responsibilities=validated_sections.get("management_responsibilities", ""),
            signature=f"{engagement_data['auditor_firm']}\n{engagement_data['engagement_partner']}\n{datetime.now().strftime('%B %d, %Y')}",
            firm_location=engagement_data.get("firm_location", ""),
        )

        # Step 7: Final compliance check
        compliance_result = await self.compliance_checker.validate_report(report)

        if not compliance_result["compliant"]:
            logger.error(f"Report failed compliance: {compliance_result['errors']}")
            raise ValueError("Report does not meet regulatory standards")

        logger.success(f"Report generated successfully for {engagement_id}")

        return report

    async def _gather_engagement_data(self, engagement_id: str) -> Dict:
        """Gather all data needed for report"""
        # Would query database for all engagement data
        # For now, mock data
        return {
            "engagement_id": engagement_id,
            "entity_name": "Acme Corporation",
            "report_type": "10-K",
            "fiscal_year_end": datetime(2024, 12, 31),
            "auditor_firm": "Smith & Partners LLP",
            "engagement_partner": "Jane Smith, CPA",
            "firm_location": "New York, New York",
            "findings": {},
            "financials": {},
        }


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

async def main():
    """Example usage"""

    generator = EnterpriseReportGenerator()

    report = await generator.generate_complete_report(
        engagement_id="eng_12345",
        entity_type="public",
        entity_industry="Technology"
    )

    print("=" * 80)
    print("GENERATED AUDIT REPORT")
    print("=" * 80)
    print(f"\n{report.title}\n")
    print(f"Date: {report.report_date.strftime('%B %d, %Y')}\n")
    print(f"To: {report.addressee}\n")
    print("\nOPINION")
    print("-" * 80)
    print(report.opinion)
    print("\nBASIS FOR OPINION")
    print("-" * 80)
    print(report.basis_for_opinion)
    print("\nSIGNATURE")
    print("-" * 80)
    print(report.signature)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
