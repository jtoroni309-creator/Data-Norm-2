"""
Qualification Engine for R&D Tax Credits

Evaluates projects against Federal 4-part test and state overlays
using AI for analysis combined with deterministic rule application.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from enum import Enum

from .rules_engine import RulesEngine, FederalRules, StateRules, RuleResult

logger = logging.getLogger(__name__)


class EvidenceStrength(str, Enum):
    """Strength of evidence supporting qualification."""
    STRONG = "strong"  # Direct documentation, clear support
    MODERATE = "moderate"  # Indirect evidence, reasonable inference
    WEAK = "weak"  # Limited evidence, requires additional support
    INSUFFICIENT = "insufficient"  # Not enough to support qualification


@dataclass
class FourPartTestScore:
    """Score for one element of the 4-part test."""
    element: str
    score: float  # 0-100
    confidence: float  # 0-1
    evidence_strength: EvidenceStrength
    evidence_items: List[Dict[str, Any]]
    analysis: str
    citations: List[str]
    risk_factors: List[str]
    improvement_suggestions: List[str]


@dataclass
class ProjectQualificationResult:
    """Complete qualification result for a project."""
    project_id: UUID
    project_name: str

    # 4-part test results
    permitted_purpose: FourPartTestScore
    technological_nature: FourPartTestScore
    elimination_of_uncertainty: FourPartTestScore
    process_of_experimentation: FourPartTestScore

    # Overall qualification
    overall_score: float
    overall_confidence: float
    qualification_status: str  # qualified, partially_qualified, not_qualified, needs_review
    qualification_narrative: str

    # Evidence summary
    total_evidence_items: int
    strong_evidence_count: int
    evidence_gaps: List[str]

    # State qualifications
    state_qualifications: Dict[str, Dict[str, Any]]

    # Risk assessment
    risk_flags: List[Dict[str, Any]]
    audit_risk_score: float  # 0-100, higher = more risk

    # AI analysis
    ai_analysis_summary: str
    ai_suggested_evidence: List[str]

    # Rules reference
    rules_version: str
    evaluated_at: datetime


class QualificationEngine:
    """
    Engine for evaluating R&D project qualification.

    Combines AI analysis with deterministic rule application
    to evaluate the Federal 4-part test and state overlays.
    """

    def __init__(self, rules_engine: Optional[RulesEngine] = None):
        self.rules_engine = rules_engine or RulesEngine()
        self.four_part_test = self.rules_engine.get_four_part_test_criteria()
        self.excluded_activities = self.rules_engine.get_excluded_activities()

    async def evaluate_project(
        self,
        project_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        employee_data: Optional[List[Dict[str, Any]]] = None,
        document_data: Optional[List[Dict[str, Any]]] = None,
        interview_data: Optional[List[Dict[str, Any]]] = None,
        ai_analysis: Optional[Dict[str, Any]] = None,
        states: Optional[List[str]] = None
    ) -> ProjectQualificationResult:
        """
        Evaluate a project against the Federal 4-part test.

        Args:
            project_data: Project information
            evidence_items: List of evidence items
            employee_data: Employee information
            document_data: Supporting documents
            interview_data: Interview transcripts/summaries
            ai_analysis: Pre-computed AI analysis
            states: States to evaluate for state credits

        Returns:
            Complete qualification result
        """
        logger.info(f"Evaluating project: {project_data.get('name')}")

        # First check for excluded activities
        exclusion_check = self._check_exclusions(project_data)
        if exclusion_check["is_excluded"]:
            return self._create_excluded_result(
                project_data,
                exclusion_check
            )

        # Evaluate each element of the 4-part test
        permitted_purpose = await self._evaluate_permitted_purpose(
            project_data, evidence_items, ai_analysis
        )
        technological_nature = await self._evaluate_technological_nature(
            project_data, evidence_items, ai_analysis
        )
        elimination_of_uncertainty = await self._evaluate_uncertainty(
            project_data, evidence_items, ai_analysis
        )
        process_of_experimentation = await self._evaluate_experimentation(
            project_data, evidence_items, ai_analysis
        )

        # Calculate overall score
        scores = [
            permitted_purpose.score,
            technological_nature.score,
            elimination_of_uncertainty.score,
            process_of_experimentation.score
        ]

        # All 4 parts must be met - use minimum as gate, weighted average for score
        min_score = min(scores)
        overall_score = sum(scores) / 4  # Equal weighting

        # Determine qualification status
        qualification_status = self._determine_qualification_status(
            min_score,
            overall_score,
            [
                permitted_purpose.evidence_strength,
                technological_nature.evidence_strength,
                elimination_of_uncertainty.evidence_strength,
                process_of_experimentation.evidence_strength
            ]
        )

        # Calculate confidence
        confidences = [
            permitted_purpose.confidence,
            technological_nature.confidence,
            elimination_of_uncertainty.confidence,
            process_of_experimentation.confidence
        ]
        overall_confidence = sum(confidences) / 4

        # Evaluate state qualifications
        state_qualifications = {}
        if states:
            for state_code in states:
                state_qualifications[state_code] = await self._evaluate_state_qualification(
                    project_data,
                    evidence_items,
                    state_code,
                    overall_score
                )

        # Generate qualification narrative
        qualification_narrative = self._generate_qualification_narrative(
            project_data,
            permitted_purpose,
            technological_nature,
            elimination_of_uncertainty,
            process_of_experimentation,
            qualification_status
        )

        # Identify evidence gaps
        evidence_gaps = self._identify_evidence_gaps(
            permitted_purpose,
            technological_nature,
            elimination_of_uncertainty,
            process_of_experimentation
        )

        # Generate risk flags
        risk_flags = self._generate_risk_flags(
            project_data,
            permitted_purpose,
            technological_nature,
            elimination_of_uncertainty,
            process_of_experimentation,
            evidence_gaps
        )

        # Calculate audit risk score
        audit_risk_score = self._calculate_audit_risk(
            overall_score,
            overall_confidence,
            evidence_gaps,
            risk_flags
        )

        return ProjectQualificationResult(
            project_id=project_data.get("id"),
            project_name=project_data.get("name", "Unknown Project"),
            permitted_purpose=permitted_purpose,
            technological_nature=technological_nature,
            elimination_of_uncertainty=elimination_of_uncertainty,
            process_of_experimentation=process_of_experimentation,
            overall_score=overall_score,
            overall_confidence=overall_confidence,
            qualification_status=qualification_status,
            qualification_narrative=qualification_narrative,
            total_evidence_items=len(evidence_items),
            strong_evidence_count=sum(
                1 for e in evidence_items
                if e.get("strength") == "strong"
            ),
            evidence_gaps=evidence_gaps,
            state_qualifications=state_qualifications,
            risk_flags=risk_flags,
            audit_risk_score=audit_risk_score,
            ai_analysis_summary=ai_analysis.get("summary", "") if ai_analysis else "",
            ai_suggested_evidence=self._suggest_additional_evidence(evidence_gaps),
            rules_version=self.rules_engine.version,
            evaluated_at=datetime.utcnow()
        )

    def _check_exclusions(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if project falls under any exclusion."""
        activity_factors = {
            "performed_outside_us": project_data.get("performed_outside_us", False),
            "is_funded_research": project_data.get("is_funded_research", False),
            "after_commercial_production": project_data.get("after_commercial_production", False),
            "is_adaptation": project_data.get("is_adaptation", False),
            "is_quality_control": project_data.get("is_quality_control", False),
            "is_reverse_engineering": project_data.get("is_reverse_engineering", False),
        }

        is_excluded, applicable_exclusions, explanation = self.rules_engine.evaluate_excluded_activity(
            project_data.get("description", ""),
            activity_factors
        )

        return {
            "is_excluded": is_excluded,
            "exclusions": applicable_exclusions,
            "explanation": explanation
        }

    async def _evaluate_permitted_purpose(
        self,
        project_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        ai_analysis: Optional[Dict[str, Any]]
    ) -> FourPartTestScore:
        """
        Evaluate IRC §41(d)(1)(B)(i) - Permitted Purpose

        Research must be undertaken to discover information to develop:
        - New or improved function
        - Performance
        - Reliability
        - Quality
        """
        criteria = self.four_part_test["permitted_purpose"]

        # Filter relevant evidence
        relevant_evidence = [
            e for e in evidence_items
            if e.get("relevant_to_permitted_purpose", False)
        ]

        # Analyze project for permitted purpose indicators
        indicators = {
            "new_product_development": self._check_indicator(
                project_data,
                ["new product", "new feature", "novel", "innovative", "develop"],
                evidence_items
            ),
            "improvement": self._check_indicator(
                project_data,
                ["improve", "enhance", "optimize", "better", "increase"],
                evidence_items
            ),
            "functionality": self._check_indicator(
                project_data,
                ["function", "capability", "feature", "ability"],
                evidence_items
            ),
            "performance": self._check_indicator(
                project_data,
                ["performance", "speed", "efficiency", "throughput", "faster"],
                evidence_items
            ),
            "reliability": self._check_indicator(
                project_data,
                ["reliability", "stable", "robust", "fault-tolerant", "uptime"],
                evidence_items
            ),
            "quality": self._check_indicator(
                project_data,
                ["quality", "accuracy", "precision", "defect", "error rate"],
                evidence_items
            )
        }

        # Calculate score based on indicators and evidence
        positive_indicators = sum(1 for v in indicators.values() if v["found"])
        max_indicators = len(indicators)

        base_score = (positive_indicators / max_indicators) * 70  # Up to 70 from indicators

        # Add evidence bonus
        evidence_bonus = min(len(relevant_evidence) * 5, 30)  # Up to 30 from evidence

        score = min(base_score + evidence_bonus, 100)

        # Determine evidence strength
        evidence_strength = self._determine_evidence_strength(
            len(relevant_evidence),
            indicators
        )

        # Get AI analysis if available
        ai_permitted_purpose = ai_analysis.get("permitted_purpose", {}) if ai_analysis else {}

        # Generate analysis narrative
        analysis = self._generate_element_analysis(
            "Permitted Purpose",
            indicators,
            relevant_evidence,
            ai_permitted_purpose
        )

        # Identify risk factors
        risk_factors = []
        if not indicators["new_product_development"]["found"] and not indicators["improvement"]["found"]:
            risk_factors.append("No clear evidence of new development or improvement")
        if len(relevant_evidence) < 2:
            risk_factors.append("Limited supporting evidence")

        # Suggest improvements
        improvement_suggestions = []
        if not indicators["functionality"]["found"]:
            improvement_suggestions.append("Document specific functionality improvements")
        if len(relevant_evidence) < 3:
            improvement_suggestions.append("Gather additional supporting documentation")

        return FourPartTestScore(
            element="permitted_purpose",
            score=score,
            confidence=self._calculate_element_confidence(evidence_strength, len(relevant_evidence)),
            evidence_strength=evidence_strength,
            evidence_items=[{
                "id": e.get("id"),
                "title": e.get("title"),
                "relevance_score": e.get("ai_relevance_score", 0.5)
            } for e in relevant_evidence],
            analysis=analysis,
            citations=[criteria["irc_citation"]],
            risk_factors=risk_factors,
            improvement_suggestions=improvement_suggestions
        )

    async def _evaluate_technological_nature(
        self,
        project_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        ai_analysis: Optional[Dict[str, Any]]
    ) -> FourPartTestScore:
        """
        Evaluate IRC §41(d)(1)(B)(ii) - Technological in Nature

        Research must rely on principles of physical or biological sciences,
        engineering, or computer science.
        """
        criteria = self.four_part_test["technological_nature"]

        relevant_evidence = [
            e for e in evidence_items
            if e.get("relevant_to_technological_nature", False)
        ]

        # Analyze for technological indicators
        indicators = {
            "engineering": self._check_indicator(
                project_data,
                ["engineer", "design", "architecture", "system", "mechanical", "electrical", "civil"],
                evidence_items
            ),
            "computer_science": self._check_indicator(
                project_data,
                ["software", "algorithm", "code", "programming", "database", "machine learning", "AI"],
                evidence_items
            ),
            "physical_science": self._check_indicator(
                project_data,
                ["physics", "chemistry", "materials", "thermodynamics", "mechanics"],
                evidence_items
            ),
            "biological_science": self._check_indicator(
                project_data,
                ["biology", "biochemistry", "genomics", "pharmaceutical", "medical device"],
                evidence_items
            ),
            "mathematics": self._check_indicator(
                project_data,
                ["mathematical", "statistical", "modeling", "simulation", "calculation"],
                evidence_items
            )
        }

        positive_indicators = sum(1 for v in indicators.values() if v["found"])
        base_score = min(positive_indicators * 20, 70)
        evidence_bonus = min(len(relevant_evidence) * 5, 30)
        score = min(base_score + evidence_bonus, 100)

        evidence_strength = self._determine_evidence_strength(
            len(relevant_evidence),
            indicators
        )

        ai_tech_nature = ai_analysis.get("technological_nature", {}) if ai_analysis else {}

        analysis = self._generate_element_analysis(
            "Technological Nature",
            indicators,
            relevant_evidence,
            ai_tech_nature
        )

        risk_factors = []
        if positive_indicators == 0:
            risk_factors.append("No clear technological basis identified")
        if not any([indicators["engineering"]["found"], indicators["computer_science"]["found"]]):
            risk_factors.append("Limited hard science foundation")

        improvement_suggestions = []
        if not indicators["computer_science"]["found"] and "software" in project_data.get("description", "").lower():
            improvement_suggestions.append("Document specific computer science principles applied")

        return FourPartTestScore(
            element="technological_nature",
            score=score,
            confidence=self._calculate_element_confidence(evidence_strength, len(relevant_evidence)),
            evidence_strength=evidence_strength,
            evidence_items=[{
                "id": e.get("id"),
                "title": e.get("title"),
                "relevance_score": e.get("ai_relevance_score", 0.5)
            } for e in relevant_evidence],
            analysis=analysis,
            citations=[criteria["irc_citation"]],
            risk_factors=risk_factors,
            improvement_suggestions=improvement_suggestions
        )

    async def _evaluate_uncertainty(
        self,
        project_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        ai_analysis: Optional[Dict[str, Any]]
    ) -> FourPartTestScore:
        """
        Evaluate IRC §41(d)(1)(B)(iii) - Elimination of Uncertainty

        Research must be undertaken to eliminate uncertainty concerning:
        - Capability
        - Method
        - Appropriate design
        """
        criteria = self.four_part_test["elimination_of_uncertainty"]

        relevant_evidence = [
            e for e in evidence_items
            if e.get("relevant_to_uncertainty", False)
        ]

        indicators = {
            "capability_uncertainty": self._check_indicator(
                project_data,
                ["uncertain", "unknown", "whether possible", "feasibility", "can we", "if possible"],
                evidence_items
            ),
            "method_uncertainty": self._check_indicator(
                project_data,
                ["how to", "method", "approach", "technique", "best way", "optimal"],
                evidence_items
            ),
            "design_uncertainty": self._check_indicator(
                project_data,
                ["design", "architecture", "configuration", "structure", "layout"],
                evidence_items
            ),
            "technical_challenges": self._check_indicator(
                project_data,
                ["challenge", "problem", "issue", "difficulty", "obstacle", "limitation"],
                evidence_items
            ),
            "failed_attempts": self._check_indicator(
                project_data,
                ["failed", "didn't work", "unsuccessful", "abandoned", "revised"],
                evidence_items
            )
        }

        positive_indicators = sum(1 for v in indicators.values() if v["found"])
        base_score = (positive_indicators / len(indicators)) * 70
        evidence_bonus = min(len(relevant_evidence) * 5, 30)
        score = min(base_score + evidence_bonus, 100)

        evidence_strength = self._determine_evidence_strength(
            len(relevant_evidence),
            indicators
        )

        ai_uncertainty = ai_analysis.get("elimination_of_uncertainty", {}) if ai_analysis else {}

        analysis = self._generate_element_analysis(
            "Elimination of Uncertainty",
            indicators,
            relevant_evidence,
            ai_uncertainty
        )

        risk_factors = []
        if not indicators["capability_uncertainty"]["found"] and not indicators["method_uncertainty"]["found"]:
            risk_factors.append("No clear uncertainty documented at project start")
        if not indicators["technical_challenges"]["found"]:
            risk_factors.append("Technical challenges not well documented")

        improvement_suggestions = []
        improvement_suggestions.append("Document uncertainties that existed at project inception")
        if not indicators["failed_attempts"]["found"]:
            improvement_suggestions.append("Document any failed approaches or iterations")

        return FourPartTestScore(
            element="elimination_of_uncertainty",
            score=score,
            confidence=self._calculate_element_confidence(evidence_strength, len(relevant_evidence)),
            evidence_strength=evidence_strength,
            evidence_items=[{
                "id": e.get("id"),
                "title": e.get("title"),
                "relevance_score": e.get("ai_relevance_score", 0.5)
            } for e in relevant_evidence],
            analysis=analysis,
            citations=[criteria["irc_citation"]],
            risk_factors=risk_factors,
            improvement_suggestions=improvement_suggestions
        )

    async def _evaluate_experimentation(
        self,
        project_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        ai_analysis: Optional[Dict[str, Any]]
    ) -> FourPartTestScore:
        """
        Evaluate IRC §41(d)(1)(B)(iv) - Process of Experimentation

        Research must involve systematic evaluation of one or more alternatives.
        """
        criteria = self.four_part_test["process_of_experimentation"]

        relevant_evidence = [
            e for e in evidence_items
            if e.get("relevant_to_experimentation", False)
        ]

        indicators = {
            "systematic_process": self._check_indicator(
                project_data,
                ["systematic", "methodical", "structured", "process", "framework"],
                evidence_items
            ),
            "alternatives_evaluation": self._check_indicator(
                project_data,
                ["alternative", "option", "evaluate", "compare", "assess", "analyze"],
                evidence_items
            ),
            "testing": self._check_indicator(
                project_data,
                ["test", "trial", "experiment", "validation", "verification", "QA"],
                evidence_items
            ),
            "prototyping": self._check_indicator(
                project_data,
                ["prototype", "POC", "proof of concept", "MVP", "pilot"],
                evidence_items
            ),
            "modeling_simulation": self._check_indicator(
                project_data,
                ["model", "simulation", "emulation", "virtual", "digital twin"],
                evidence_items
            ),
            "iteration": self._check_indicator(
                project_data,
                ["iteration", "version", "revision", "refine", "iterate", "sprint"],
                evidence_items
            )
        }

        positive_indicators = sum(1 for v in indicators.values() if v["found"])
        base_score = (positive_indicators / len(indicators)) * 70
        evidence_bonus = min(len(relevant_evidence) * 5, 30)
        score = min(base_score + evidence_bonus, 100)

        evidence_strength = self._determine_evidence_strength(
            len(relevant_evidence),
            indicators
        )

        ai_experimentation = ai_analysis.get("process_of_experimentation", {}) if ai_analysis else {}

        analysis = self._generate_element_analysis(
            "Process of Experimentation",
            indicators,
            relevant_evidence,
            ai_experimentation
        )

        risk_factors = []
        if not indicators["systematic_process"]["found"]:
            risk_factors.append("No documented systematic approach")
        if not indicators["alternatives_evaluation"]["found"]:
            risk_factors.append("Evaluation of alternatives not documented")
        if not indicators["testing"]["found"] and not indicators["modeling_simulation"]["found"]:
            risk_factors.append("No testing or modeling documentation")

        improvement_suggestions = []
        if not indicators["alternatives_evaluation"]["found"]:
            improvement_suggestions.append("Document alternatives considered and evaluation criteria")
        if not indicators["testing"]["found"]:
            improvement_suggestions.append("Include test plans and results")

        return FourPartTestScore(
            element="process_of_experimentation",
            score=score,
            confidence=self._calculate_element_confidence(evidence_strength, len(relevant_evidence)),
            evidence_strength=evidence_strength,
            evidence_items=[{
                "id": e.get("id"),
                "title": e.get("title"),
                "relevance_score": e.get("ai_relevance_score", 0.5)
            } for e in relevant_evidence],
            analysis=analysis,
            citations=[criteria["irc_citation"]],
            risk_factors=risk_factors,
            improvement_suggestions=improvement_suggestions
        )

    async def _evaluate_state_qualification(
        self,
        project_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        state_code: str,
        federal_score: float
    ) -> Dict[str, Any]:
        """Evaluate project against state-specific rules."""
        state_rules = self.rules_engine.get_state_rules(state_code)

        if not state_rules or not state_rules.has_rd_credit:
            return {
                "qualified": False,
                "reason": f"{state_code} does not have an R&D credit",
                "notes": None
            }

        # Most states piggyback on Federal qualification
        if state_rules.base_method == "federal":
            qualified = federal_score >= 70
            return {
                "qualified": qualified,
                "reason": "Based on Federal 4-part test qualification",
                "federal_score": federal_score,
                "state_specific_notes": None
            }

        # Handle state-specific modifications
        state_qualified = federal_score >= 70
        notes = []

        if state_rules.qre_modifications.get("wages_in_state"):
            notes.append(f"Wages must be for work performed in {state_code}")

        if state_rules.qre_modifications.get("contract_research_in_state"):
            notes.append(f"Contract research must be performed in {state_code}")

        return {
            "qualified": state_qualified,
            "reason": "Based on Federal qualification with state modifications",
            "federal_score": federal_score,
            "state_specific_notes": notes if notes else None
        }

    def _check_indicator(
        self,
        project_data: Dict[str, Any],
        keywords: List[str],
        evidence_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check if indicator keywords are present in project data or evidence."""
        description = project_data.get("description", "").lower()
        name = project_data.get("name", "").lower()

        # Check project data
        found_in_project = any(kw.lower() in description or kw.lower() in name for kw in keywords)

        # Check evidence
        found_in_evidence = []
        for evidence in evidence_items:
            evidence_text = (
                evidence.get("title", "") + " " +
                evidence.get("description", "") + " " +
                evidence.get("source_excerpt", "")
            ).lower()
            if any(kw.lower() in evidence_text for kw in keywords):
                found_in_evidence.append(evidence.get("id"))

        return {
            "found": found_in_project or len(found_in_evidence) > 0,
            "in_project": found_in_project,
            "evidence_ids": found_in_evidence,
            "keywords_matched": [kw for kw in keywords if kw.lower() in description]
        }

    def _determine_evidence_strength(
        self,
        evidence_count: int,
        indicators: Dict[str, Dict[str, Any]]
    ) -> EvidenceStrength:
        """Determine overall evidence strength."""
        positive_indicators = sum(1 for v in indicators.values() if v["found"])
        evidence_backed = sum(1 for v in indicators.values() if len(v.get("evidence_ids", [])) > 0)

        if evidence_count >= 5 and evidence_backed >= 3:
            return EvidenceStrength.STRONG
        elif evidence_count >= 3 and evidence_backed >= 2:
            return EvidenceStrength.MODERATE
        elif evidence_count >= 1 or positive_indicators >= 2:
            return EvidenceStrength.WEAK
        else:
            return EvidenceStrength.INSUFFICIENT

    def _calculate_element_confidence(
        self,
        evidence_strength: EvidenceStrength,
        evidence_count: int
    ) -> float:
        """Calculate confidence score for an element."""
        base_confidence = {
            EvidenceStrength.STRONG: 0.90,
            EvidenceStrength.MODERATE: 0.75,
            EvidenceStrength.WEAK: 0.55,
            EvidenceStrength.INSUFFICIENT: 0.30
        }

        confidence = base_confidence.get(evidence_strength, 0.5)

        # Adjust based on evidence count
        if evidence_count > 5:
            confidence = min(confidence + 0.05, 0.95)
        elif evidence_count == 0:
            confidence = max(confidence - 0.15, 0.20)

        return confidence

    def _determine_qualification_status(
        self,
        min_score: float,
        overall_score: float,
        evidence_strengths: List[EvidenceStrength]
    ) -> str:
        """Determine qualification status based on scores and evidence."""
        weak_elements = sum(
            1 for s in evidence_strengths
            if s in [EvidenceStrength.WEAK, EvidenceStrength.INSUFFICIENT]
        )

        if min_score >= 70 and overall_score >= 75:
            if weak_elements == 0:
                return "qualified"
            elif weak_elements <= 1:
                return "qualified"  # Still qualified but note weakness
            else:
                return "needs_review"
        elif min_score >= 50 and overall_score >= 60:
            return "partially_qualified"
        elif min_score >= 40:
            return "needs_review"
        else:
            return "not_qualified"

    def _generate_element_analysis(
        self,
        element_name: str,
        indicators: Dict[str, Dict[str, Any]],
        evidence: List[Dict[str, Any]],
        ai_analysis: Dict[str, Any]
    ) -> str:
        """Generate analysis narrative for an element."""
        found_indicators = [k for k, v in indicators.items() if v["found"]]
        missing_indicators = [k for k, v in indicators.items() if not v["found"]]

        analysis_parts = []

        if found_indicators:
            analysis_parts.append(
                f"The project demonstrates {element_name} through: {', '.join(found_indicators)}."
            )

        if evidence:
            analysis_parts.append(
                f"Supported by {len(evidence)} evidence item(s)."
            )

        if missing_indicators:
            analysis_parts.append(
                f"Areas needing additional support: {', '.join(missing_indicators[:3])}."
            )

        if ai_analysis.get("summary"):
            analysis_parts.append(f"AI Analysis: {ai_analysis['summary']}")

        return " ".join(analysis_parts)

    def _generate_qualification_narrative(
        self,
        project_data: Dict[str, Any],
        permitted_purpose: FourPartTestScore,
        technological_nature: FourPartTestScore,
        elimination_of_uncertainty: FourPartTestScore,
        process_of_experimentation: FourPartTestScore,
        qualification_status: str
    ) -> str:
        """Generate comprehensive qualification narrative."""
        project_name = project_data.get("name", "The project")

        narrative_parts = [
            f"## Qualification Analysis for {project_name}\n",
            f"### Overall Status: {qualification_status.upper()}\n"
        ]

        # Permitted Purpose
        narrative_parts.append(f"\n**Permitted Purpose (Score: {permitted_purpose.score:.0f}/100)**\n")
        narrative_parts.append(permitted_purpose.analysis)

        # Technological Nature
        narrative_parts.append(f"\n**Technological in Nature (Score: {technological_nature.score:.0f}/100)**\n")
        narrative_parts.append(technological_nature.analysis)

        # Uncertainty
        narrative_parts.append(f"\n**Elimination of Uncertainty (Score: {elimination_of_uncertainty.score:.0f}/100)**\n")
        narrative_parts.append(elimination_of_uncertainty.analysis)

        # Experimentation
        narrative_parts.append(f"\n**Process of Experimentation (Score: {process_of_experimentation.score:.0f}/100)**\n")
        narrative_parts.append(process_of_experimentation.analysis)

        return "\n".join(narrative_parts)

    def _identify_evidence_gaps(
        self,
        permitted_purpose: FourPartTestScore,
        technological_nature: FourPartTestScore,
        elimination_of_uncertainty: FourPartTestScore,
        process_of_experimentation: FourPartTestScore
    ) -> List[str]:
        """Identify gaps in evidence."""
        gaps = []

        elements = [
            ("Permitted Purpose", permitted_purpose),
            ("Technological Nature", technological_nature),
            ("Elimination of Uncertainty", elimination_of_uncertainty),
            ("Process of Experimentation", process_of_experimentation)
        ]

        for name, element in elements:
            if element.evidence_strength in [EvidenceStrength.WEAK, EvidenceStrength.INSUFFICIENT]:
                gaps.append(f"{name}: {element.evidence_strength.value} evidence")
            if len(element.evidence_items) < 2:
                gaps.append(f"{name}: Limited supporting documentation")

        return gaps

    def _generate_risk_flags(
        self,
        project_data: Dict[str, Any],
        permitted_purpose: FourPartTestScore,
        technological_nature: FourPartTestScore,
        elimination_of_uncertainty: FourPartTestScore,
        process_of_experimentation: FourPartTestScore,
        evidence_gaps: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate risk flags for review."""
        risk_flags = []

        # Low score flags
        for name, element in [
            ("permitted_purpose", permitted_purpose),
            ("technological_nature", technological_nature),
            ("elimination_of_uncertainty", elimination_of_uncertainty),
            ("process_of_experimentation", process_of_experimentation)
        ]:
            if element.score < 50:
                risk_flags.append({
                    "type": "low_score",
                    "element": name,
                    "score": element.score,
                    "severity": "high" if element.score < 30 else "medium",
                    "description": f"{name.replace('_', ' ').title()} score is below threshold"
                })

            if element.evidence_strength == EvidenceStrength.INSUFFICIENT:
                risk_flags.append({
                    "type": "insufficient_evidence",
                    "element": name,
                    "severity": "high",
                    "description": f"Insufficient evidence for {name.replace('_', ' ')}"
                })

        # Add risk factors from each element
        for element in [permitted_purpose, technological_nature, elimination_of_uncertainty, process_of_experimentation]:
            for risk in element.risk_factors:
                risk_flags.append({
                    "type": "element_risk",
                    "element": element.element,
                    "severity": "medium",
                    "description": risk
                })

        return risk_flags

    def _calculate_audit_risk(
        self,
        overall_score: float,
        overall_confidence: float,
        evidence_gaps: List[str],
        risk_flags: List[Dict[str, Any]]
    ) -> float:
        """Calculate audit risk score (0-100, higher = more risk)."""
        base_risk = 100 - overall_score  # Lower score = higher risk

        # Adjust for confidence
        confidence_penalty = (1 - overall_confidence) * 20

        # Adjust for evidence gaps
        gap_penalty = len(evidence_gaps) * 5

        # Adjust for risk flags
        high_risk_count = sum(1 for f in risk_flags if f.get("severity") == "high")
        medium_risk_count = sum(1 for f in risk_flags if f.get("severity") == "medium")
        flag_penalty = (high_risk_count * 10) + (medium_risk_count * 5)

        audit_risk = base_risk + confidence_penalty + gap_penalty + flag_penalty

        return min(max(audit_risk, 0), 100)

    def _suggest_additional_evidence(self, evidence_gaps: List[str]) -> List[str]:
        """Suggest additional evidence to strengthen qualification."""
        suggestions = []

        evidence_suggestions = {
            "Permitted Purpose": [
                "Product requirements documents",
                "Design specifications",
                "Project proposals with objectives"
            ],
            "Technological Nature": [
                "Technical documentation",
                "Engineering calculations",
                "Algorithm documentation"
            ],
            "Elimination of Uncertainty": [
                "Feasibility studies",
                "Problem statements",
                "Technical challenge documentation"
            ],
            "Process of Experimentation": [
                "Test plans and results",
                "Prototype documentation",
                "Alternative analysis documents"
            ]
        }

        for gap in evidence_gaps:
            for element, element_suggestions in evidence_suggestions.items():
                if element in gap:
                    suggestions.extend(element_suggestions)

        return list(set(suggestions))[:10]  # Return unique suggestions, max 10

    def _create_excluded_result(
        self,
        project_data: Dict[str, Any],
        exclusion_check: Dict[str, Any]
    ) -> ProjectQualificationResult:
        """Create result for excluded project."""
        empty_score = FourPartTestScore(
            element="excluded",
            score=0,
            confidence=1.0,
            evidence_strength=EvidenceStrength.STRONG,
            evidence_items=[],
            analysis=f"Project excluded: {exclusion_check['explanation']}",
            citations=["IRC §41(d)(4)"],
            risk_factors=[],
            improvement_suggestions=[]
        )

        return ProjectQualificationResult(
            project_id=project_data.get("id"),
            project_name=project_data.get("name", "Unknown Project"),
            permitted_purpose=empty_score,
            technological_nature=empty_score,
            elimination_of_uncertainty=empty_score,
            process_of_experimentation=empty_score,
            overall_score=0,
            overall_confidence=1.0,
            qualification_status="not_qualified",
            qualification_narrative=f"Project is excluded from R&D credit qualification: {exclusion_check['explanation']}",
            total_evidence_items=0,
            strong_evidence_count=0,
            evidence_gaps=[],
            state_qualifications={},
            risk_flags=[{
                "type": "excluded_activity",
                "severity": "high",
                "description": exclusion_check["explanation"],
                "exclusions": exclusion_check["exclusions"]
            }],
            audit_risk_score=0,
            ai_analysis_summary="",
            ai_suggested_evidence=[],
            rules_version=self.rules_engine.version,
            evaluated_at=datetime.utcnow()
        )
