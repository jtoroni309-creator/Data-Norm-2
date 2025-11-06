"""
Confidence Scoring System for AI Audit Outputs

Evaluates the reliability and confidence level of AI-generated audit content
using multiple scoring mechanisms:

1. Citation Quality Score - Based on relevance and authority of sources
2. Semantic Consistency Score - Internal consistency check
3. Statistical Confidence - Based on retrieval similarity scores
4. Expert Validation Score - Historical accuracy tracking
5. Uncertainty Detection - Identifies hedging language and ambiguity

Goal: Ensure AI outputs meet or exceed seasoned CPA judgment quality
"""
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy import stats

from .schemas import Citation

logger = logging.getLogger(__name__)


class ConfidenceLevel(str, Enum):
    """Confidence levels for AI outputs"""
    VERY_HIGH = "very_high"  # 90-100% - Ready for partner review
    HIGH = "high"            # 75-89% - Senior/Manager review recommended
    MEDIUM = "medium"        # 60-74% - Requires significant review
    LOW = "low"              # 40-59% - Extensive revision needed
    VERY_LOW = "very_low"    # 0-39% - Regenerate or manual creation


@dataclass
class ConfidenceScores:
    """Detailed confidence scores breakdown"""
    overall_score: float  # 0-1
    confidence_level: ConfidenceLevel

    # Component scores
    citation_quality_score: float
    semantic_consistency_score: float
    statistical_confidence_score: float
    expert_validation_score: Optional[float]

    # Risk indicators
    uncertainty_indicators: List[str]
    contradiction_flags: List[str]
    missing_citations_count: int

    # Explanation
    explanation: str
    recommendations: List[str]


class ConfidenceScorer:
    """
    Multi-faceted confidence scoring system

    Emulates seasoned CPA judgment by:
    - Evaluating source quality and relevance
    - Checking for internal consistency
    - Detecting uncertainty and hedging
    - Identifying potential contradictions
    - Tracking historical accuracy
    """

    # Authoritative audit standards (highest weight)
    AUTHORITATIVE_SOURCES = {
        "PCAOB", "AICPA", "FASB", "SEC", "SOX", "GAAS", "GAAP",
        "ASC", "SAS", "SSAE", "SSARS", "AU-C"
    }

    # Uncertainty indicators (hedging language)
    UNCERTAINTY_PATTERNS = [
        r"\bmay\s+(?:indicate|suggest|imply)",
        r"\bcould\s+(?:be|indicate|suggest)",
        r"\bmight\s+(?:be|indicate|suggest)",
        r"\bpossibly\b",
        r"\bperhaps\b",
        r"\buncertain",
        r"\bunclear",
        r"\bdifficult to (?:determine|assess|evaluate)",
        r"\blimited (?:evidence|information)",
        r"\binsufficient (?:evidence|data)",
        r"\brequires? (?:further|additional) (?:investigation|review|analysis)",
    ]

    # Contradiction patterns
    CONTRADICTION_PATTERNS = [
        (r"\bhowever\b", r"\bcontradict"),
        (r"\bnevertheless\b", r"\bcontradict"),
        (r"\bon the other hand\b", r"\bconflict"),
        (r"\bbut\b", r"\binconsistent"),
        (r"\balthough\b", r"\boppos(?:e|ing)"),
    ]

    def __init__(self):
        self.compiled_uncertainty_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.UNCERTAINTY_PATTERNS
        ]

    def score_citation_quality(
        self,
        citations: List[Citation],
        response_text: str
    ) -> Tuple[float, List[str]]:
        """
        Score the quality and appropriateness of citations

        Factors:
        - Source authority (PCAOB/AICPA > industry guides > general sources)
        - Citation relevance (similarity scores)
        - Citation coverage (% of response backed by citations)
        - Standard specificity (AS 1215.06 > AS 1215 > "audit standards")

        Returns:
            Tuple of (score, issues_found)
        """
        if not citations:
            return 0.0, ["No citations provided"]

        issues = []
        scores = []

        # 1. Source Authority Score (0-1)
        authority_scores = []
        for citation in citations:
            authority = 0.5  # Default for general sources

            # Check if authoritative standard
            if citation.standard_code:
                for auth_source in self.AUTHORITATIVE_SOURCES:
                    if auth_source in citation.standard_code.upper():
                        authority = 1.0
                        break

            # Check document title for authority
            if citation.document_title:
                for auth_source in self.AUTHORITATIVE_SOURCES:
                    if auth_source in citation.document_title.upper():
                        authority = max(authority, 0.9)
                        break

            authority_scores.append(authority)

        avg_authority = np.mean(authority_scores)
        scores.append(avg_authority)

        if avg_authority < 0.7:
            issues.append("Citations lack authoritative sources (PCAOB/AICPA/FASB)")

        # 2. Similarity/Relevance Score (0-1)
        similarity_scores = [c.similarity_score for c in citations]
        avg_similarity = np.mean(similarity_scores)
        scores.append(avg_similarity)

        if avg_similarity < 0.7:
            issues.append(f"Low citation relevance (avg similarity: {avg_similarity:.2f})")

        # 3. Citation Coverage Score (0-1)
        # Count citation markers [1], [2], etc. in response
        citation_markers = re.findall(r'\[(\d+)\]', response_text)
        unique_citations_used = len(set(citation_markers))
        total_citations = len(citations)

        coverage = unique_citations_used / total_citations if total_citations > 0 else 0
        scores.append(coverage)

        if coverage < 0.5:
            issues.append(
                f"Low citation usage ({unique_citations_used}/{total_citations} citations used)"
            )

        # 4. Standard Specificity Score (0-1)
        specificity_scores = []
        for citation in citations:
            specificity = 0.5  # Default

            if citation.standard_code:
                # More specific citations are better (e.g., "AS 1215.06" > "AS 1215")
                if re.search(r'\.\d+', citation.standard_code):
                    specificity = 1.0  # Paragraph-level citation
                elif re.search(r'\d+', citation.standard_code):
                    specificity = 0.8  # Section-level citation

            specificity_scores.append(specificity)

        avg_specificity = np.mean(specificity_scores)
        scores.append(avg_specificity)

        if avg_specificity < 0.6:
            issues.append("Citations lack specificity (prefer paragraph-level references)")

        # Weighted average (authority and similarity are most important)
        weights = [0.35, 0.35, 0.15, 0.15]  # authority, similarity, coverage, specificity
        overall_score = np.average(scores, weights=weights)

        return float(overall_score), issues

    def score_semantic_consistency(self, response_text: str) -> Tuple[float, List[str]]:
        """
        Check for internal semantic consistency

        Detects:
        - Contradictory statements
        - Logical inconsistencies
        - Conflicting conclusions

        Returns:
            Tuple of (score, contradictions_found)
        """
        contradictions = []

        # Split into sentences
        sentences = re.split(r'[.!?]+', response_text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Check for contradiction patterns
        for pattern1, pattern2 in self.CONTRADICTION_PATTERNS:
            matches1 = [s for s in sentences if re.search(pattern1, s, re.IGNORECASE)]
            matches2 = [s for s in sentences if re.search(pattern2, s, re.IGNORECASE)]

            if matches1 and matches2:
                contradictions.append(
                    f"Potential contradiction detected ('{pattern1}' paired with '{pattern2}')"
                )

        # Check for negation pairs in same response
        negation_words = ["not", "no", "never", "none", "neither", "cannot", "don't", "doesn't"]
        positive_assertions = []
        negative_assertions = []

        for sentence in sentences:
            has_negation = any(re.search(rf'\b{neg}\b', sentence, re.IGNORECASE)
                             for neg in negation_words)
            if has_negation:
                negative_assertions.append(sentence)
            else:
                positive_assertions.append(sentence)

        # Score based on contradictions found
        # Start at 1.0, deduct for each issue
        score = 1.0
        score -= len(contradictions) * 0.15

        # Excessive negations could indicate uncertainty
        negation_ratio = len(negative_assertions) / len(sentences) if sentences else 0
        if negation_ratio > 0.3:
            contradictions.append(f"High negation rate ({negation_ratio:.1%}) may indicate uncertainty")
            score -= 0.1

        score = max(0.0, score)

        return float(score), contradictions

    def score_statistical_confidence(
        self,
        citations: List[Citation],
        top_k: int = 5
    ) -> Tuple[float, List[str]]:
        """
        Statistical confidence based on retrieval quality

        Factors:
        - Mean similarity score
        - Score variance (low variance = consistent retrieval)
        - Score distribution (confidence interval)

        Returns:
            Tuple of (score, issues)
        """
        if not citations:
            return 0.0, ["No citations for statistical analysis"]

        issues = []
        similarity_scores = [c.similarity_score for c in citations[:top_k]]

        # 1. Mean score (higher is better)
        mean_score = np.mean(similarity_scores)

        # 2. Variance (lower is better - indicates consistent retrieval)
        variance = np.var(similarity_scores)
        variance_score = np.exp(-variance * 5)  # Exponential decay

        # 3. Confidence interval (tighter CI = higher confidence)
        if len(similarity_scores) > 2:
            ci_95 = stats.t.interval(
                0.95,
                len(similarity_scores) - 1,
                loc=mean_score,
                scale=stats.sem(similarity_scores)
            )
            ci_width = ci_95[1] - ci_95[0]
            ci_score = np.exp(-ci_width * 5)
        else:
            ci_score = 0.5
            issues.append("Insufficient data for confidence interval")

        # 4. Top score dominance (if top-1 >> top-2, might be cherry-picking)
        if len(similarity_scores) >= 2:
            score_diff = similarity_scores[0] - similarity_scores[1]
            if score_diff > 0.3:
                issues.append(
                    f"Large gap between top citations ({score_diff:.2f}) - verify relevance"
                )

        # Combined score
        weights = [0.5, 0.25, 0.25]
        combined = np.average([mean_score, variance_score, ci_score], weights=weights)

        if mean_score < 0.7:
            issues.append(f"Low average citation relevance ({mean_score:.2f})")

        if variance > 0.1:
            issues.append(f"High variance in citation quality ({variance:.3f})")

        return float(combined), issues

    def detect_uncertainty(self, response_text: str) -> Tuple[float, List[str]]:
        """
        Detect uncertainty indicators and hedging language

        CPAs are trained to be confident and specific. Excessive hedging
        indicates lower confidence or insufficient evidence.

        Returns:
            Tuple of (certainty_score, indicators_found)
        """
        indicators_found = []

        # Search for uncertainty patterns
        for pattern in self.compiled_uncertainty_patterns:
            matches = pattern.findall(response_text)
            if matches:
                # Extract context around match
                for match in matches[:2]:  # Limit to first 2 examples
                    indicators_found.append(f"Uncertainty language: '{match}'")

        # Count qualifiers
        qualifiers = ["may", "might", "could", "possibly", "perhaps", "probably"]
        qualifier_count = sum(
            len(re.findall(rf'\b{q}\b', response_text, re.IGNORECASE))
            for q in qualifiers
        )

        # Penalize based on frequency
        words = response_text.split()
        qualifier_density = qualifier_count / len(words) if words else 0

        if qualifier_density > 0.03:  # More than 3% qualifiers
            indicators_found.append(
                f"High qualifier density ({qualifier_density:.1%}) suggests uncertainty"
            )

        # Calculate certainty score (1.0 = very certain, 0.0 = very uncertain)
        certainty_score = 1.0 - min(qualifier_density * 10, 1.0)
        certainty_score -= len(indicators_found) * 0.1
        certainty_score = max(0.0, certainty_score)

        return float(certainty_score), indicators_found

    def calculate_overall_confidence(
        self,
        citations: List[Citation],
        response_text: str,
        expert_validation_score: Optional[float] = None
    ) -> ConfidenceScores:
        """
        Calculate comprehensive confidence score

        Combines multiple scoring dimensions to produce overall confidence
        assessment that mimics seasoned CPA judgment.

        Args:
            citations: List of citations used
            response_text: Generated response text
            expert_validation_score: Optional historical accuracy score (0-1)

        Returns:
            ConfidenceScores object with detailed breakdown
        """
        logger.info("Calculating confidence scores for AI output")

        # 1. Citation Quality
        citation_score, citation_issues = self.score_citation_quality(citations, response_text)

        # 2. Semantic Consistency
        consistency_score, contradictions = self.score_semantic_consistency(response_text)

        # 3. Statistical Confidence
        statistical_score, stat_issues = self.score_statistical_confidence(citations)

        # 4. Uncertainty Detection
        certainty_score, uncertainty_indicators = self.detect_uncertainty(response_text)

        # 5. Missing Citations Check
        # Count assertions without citations
        assertions = re.split(r'[.!?]+', response_text)
        citation_markers = set(re.findall(r'\[(\d+)\]', response_text))
        assertion_count = len([a for a in assertions if len(a.split()) > 5])  # Substantial sentences
        citation_count = len(citation_markers)

        missing_citations_ratio = max(0, (assertion_count - citation_count) / assertion_count) if assertion_count > 0 else 0

        # Calculate weighted overall score
        component_scores = [
            citation_score,
            consistency_score,
            statistical_score,
            certainty_score
        ]

        weights = [0.30, 0.25, 0.25, 0.20]  # Citation quality is most important

        if expert_validation_score is not None:
            component_scores.append(expert_validation_score)
            weights = [0.25, 0.20, 0.20, 0.15, 0.20]  # Include expert validation

        overall_score = np.average(component_scores, weights=weights)

        # Apply penalties
        if missing_citations_ratio > 0.3:
            overall_score *= 0.9  # 10% penalty for too many unsupported assertions

        # Determine confidence level
        if overall_score >= 0.90:
            level = ConfidenceLevel.VERY_HIGH
        elif overall_score >= 0.75:
            level = ConfidenceLevel.HIGH
        elif overall_score >= 0.60:
            level = ConfidenceLevel.MEDIUM
        elif overall_score >= 0.40:
            level = ConfidenceLevel.LOW
        else:
            level = ConfidenceLevel.VERY_LOW

        # Build recommendations
        recommendations = self._generate_recommendations(
            level=level,
            citation_score=citation_score,
            consistency_score=consistency_score,
            certainty_score=certainty_score,
            missing_citations_ratio=missing_citations_ratio
        )

        # Build explanation
        explanation = self._generate_explanation(
            overall_score=overall_score,
            level=level,
            component_scores={
                "citation_quality": citation_score,
                "semantic_consistency": consistency_score,
                "statistical_confidence": statistical_score,
                "certainty": certainty_score
            }
        )

        return ConfidenceScores(
            overall_score=round(overall_score, 3),
            confidence_level=level,
            citation_quality_score=round(citation_score, 3),
            semantic_consistency_score=round(consistency_score, 3),
            statistical_confidence_score=round(statistical_score, 3),
            expert_validation_score=round(expert_validation_score, 3) if expert_validation_score else None,
            uncertainty_indicators=uncertainty_indicators,
            contradiction_flags=contradictions,
            missing_citations_count=int(assertion_count - citation_count) if assertion_count > citation_count else 0,
            explanation=explanation,
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        level: ConfidenceLevel,
        citation_score: float,
        consistency_score: float,
        certainty_score: float,
        missing_citations_ratio: float
    ) -> List[str]:
        """Generate actionable recommendations based on scores"""
        recommendations = []

        # Citation-based recommendations
        if citation_score < 0.7:
            recommendations.append(
                "Strengthen citations by adding authoritative sources (PCAOB, AICPA, FASB)"
            )
            recommendations.append(
                "Include paragraph-level standard references (e.g., AS 1215.06) for specificity"
            )

        # Consistency recommendations
        if consistency_score < 0.8:
            recommendations.append(
                "Review response for internal contradictions or conflicting statements"
            )
            recommendations.append(
                "Ensure conclusions align with evidence presented"
            )

        # Certainty recommendations
        if certainty_score < 0.7:
            recommendations.append(
                "Reduce hedging language - be more definitive where evidence supports"
            )
            recommendations.append(
                "If uncertain, explicitly state need for additional procedures"
            )

        # Citation coverage
        if missing_citations_ratio > 0.3:
            recommendations.append(
                f"Add citations to support unsupported assertions ({missing_citations_ratio:.0%} lack backing)"
            )

        # Level-specific recommendations
        if level in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]:
            recommendations.append(
                "⚠️ Consider regenerating with more specific query or additional context"
            )
            recommendations.append(
                "⚠️ Manual CPA review and editing strongly recommended"
            )
        elif level == ConfidenceLevel.MEDIUM:
            recommendations.append(
                "Manager or Senior-level review recommended before finalization"
            )
        elif level == ConfidenceLevel.HIGH:
            recommendations.append(
                "Partner review recommended - output meets quality standards"
            )
        else:  # VERY_HIGH
            recommendations.append(
                "Output ready for partner review - high confidence in quality"
            )

        return recommendations

    def _generate_explanation(
        self,
        overall_score: float,
        level: ConfidenceLevel,
        component_scores: Dict[str, float]
    ) -> str:
        """Generate human-readable explanation of confidence assessment"""

        level_descriptions = {
            ConfidenceLevel.VERY_HIGH: "Excellent quality - meets or exceeds seasoned CPA standards",
            ConfidenceLevel.HIGH: "Good quality - appropriate for audit use with senior review",
            ConfidenceLevel.MEDIUM: "Acceptable quality - requires significant professional review",
            ConfidenceLevel.LOW: "Below standard - extensive revision needed",
            ConfidenceLevel.VERY_LOW: "Poor quality - recommend manual creation by CPA"
        }

        explanation = f"Overall Confidence: {overall_score:.1%} ({level_descriptions[level]})\n\n"
        explanation += "Component Analysis:\n"

        for component, score in component_scores.items():
            component_name = component.replace('_', ' ').title()
            grade = self._score_to_grade(score)
            explanation += f"  • {component_name}: {score:.1%} ({grade})\n"

        return explanation

    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 0.90:
            return "A"
        elif score >= 0.80:
            return "B"
        elif score >= 0.70:
            return "C"
        elif score >= 0.60:
            return "D"
        else:
            return "F"


# Global confidence scorer instance
confidence_scorer = ConfidenceScorer()
