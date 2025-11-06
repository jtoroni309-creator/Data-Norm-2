"""
Contradiction Detection System for Audit AI

Detects logical inconsistencies and contradictions in AI-generated audit content
using multiple NLP techniques:

1. Semantic Similarity Analysis - Finds opposing statements
2. Negation Detection - Identifies conflicting assertions
3. Temporal Inconsistency - Detects timeline contradictions
4. Numerical Inconsistency - Finds conflicting figures
5. Cross-Document Verification - Checks consistency across workpapers

Goal: Ensure audit conclusions are internally consistent and free of contradictions
"""
import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


class ContradictionSeverity(str, Enum):
    """Severity levels for contradictions"""
    CRITICAL = "critical"      # Direct logical contradiction - must resolve
    HIGH = "high"             # Likely contradiction - review required
    MEDIUM = "medium"         # Possible contradiction - verify
    LOW = "low"              # Minor inconsistency - consider clarifying


@dataclass
class Contradiction:
    """Detected contradiction"""
    severity: ContradictionSeverity
    type: str  # semantic, negation, temporal, numerical, cross_document
    statement1: str
    statement2: str
    explanation: str
    confidence: float  # 0-1
    location1: Optional[Dict[str, Any]] = None  # document/section reference
    location2: Optional[Dict[str, Any]] = None


@dataclass
class ContradictionReport:
    """Comprehensive contradiction detection report"""
    has_contradictions: bool
    contradiction_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    contradictions: List[Contradiction]
    overall_consistency_score: float  # 0-1, higher is better
    recommendation: str


class ContradictionDetector:
    """
    Multi-method contradiction detection system

    Uses NLP and rule-based techniques to identify logical inconsistencies
    that would be caught by an experienced CPA reviewer.
    """

    def __init__(self, embedding_model: Optional[SentenceTransformer] = None):
        """
        Initialize contradiction detector

        Args:
            embedding_model: Pre-loaded sentence transformer model
        """
        self.model = embedding_model
        self.semantic_threshold = 0.8  # High similarity with opposing semantics

        # Negation words that flip meaning
        self.negation_words = {
            "not", "no", "never", "none", "neither", "nor", "cannot", "can't",
            "don't", "doesn't", "didn't", "won't", "wouldn't", "couldn't",
            "shouldn't", "hasn't", "haven't", "hadn't", "isn't", "aren't",
            "wasn't", "weren't", "without", "lacking", "absence", "fail", "failed"
        }

        # Opposing term pairs that indicate contradiction
        self.opposing_pairs = [
            ("increase", "decrease"),
            ("gain", "loss"),
            ("profit", "loss"),
            ("asset", "liability"),
            ("credit", "debit"),
            ("overstated", "understated"),
            ("compliant", "non-compliant"),
            ("compliant", "violation"),
            ("adequate", "inadequate"),
            ("sufficient", "insufficient"),
            ("reliable", "unreliable"),
            ("accurate", "inaccurate"),
            ("material", "immaterial"),
            ("significant", "insignificant"),
            ("present", "absent"),
            ("exists", "does not exist"),
            ("confirm", "deny"),
            ("support", "contradict"),
        ]

    def _load_model(self):
        """Lazy load sentence transformer model"""
        if self.model is None:
            logger.info("Loading sentence transformer model for contradiction detection")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Model loaded successfully")

    def detect_semantic_contradictions(
        self,
        statements: List[str]
    ) -> List[Contradiction]:
        """
        Detect semantic contradictions using embedding similarity

        Finds statements that are semantically similar but have opposing meanings
        (high cosine similarity with negation/opposition markers).

        Args:
            statements: List of statement strings to analyze

        Returns:
            List of detected contradictions
        """
        if len(statements) < 2:
            return []

        self._load_model()

        contradictions = []

        # Generate embeddings
        embeddings = self.model.encode(statements, convert_to_numpy=True)

        # Compute pairwise similarities
        for i in range(len(statements)):
            for j in range(i + 1, len(statements)):
                stmt1 = statements[i]
                stmt2 = statements[j]

                # Calculate cosine similarity
                similarity = util.pytorch_cos_sim(embeddings[i], embeddings[j]).item()

                # High similarity suggests related topics
                if similarity > self.semantic_threshold:
                    # Check for opposing terms or negation
                    has_negation = self._check_negation_pattern(stmt1, stmt2)
                    has_opposing = self._check_opposing_terms(stmt1, stmt2)

                    if has_negation or has_opposing:
                        # Determine severity
                        if has_negation and has_opposing:
                            severity = ContradictionSeverity.CRITICAL
                            confidence = 0.95
                        elif has_negation:
                            severity = ContradictionSeverity.HIGH
                            confidence = 0.85
                        else:
                            severity = ContradictionSeverity.MEDIUM
                            confidence = 0.70

                        explanation = self._generate_semantic_explanation(
                            stmt1, stmt2, similarity, has_negation, has_opposing
                        )

                        contradictions.append(Contradiction(
                            severity=severity,
                            type="semantic",
                            statement1=stmt1,
                            statement2=stmt2,
                            explanation=explanation,
                            confidence=confidence
                        ))

        logger.info(f"Detected {len(contradictions)} semantic contradictions")
        return contradictions

    def _check_negation_pattern(self, stmt1: str, stmt2: str) -> bool:
        """Check if one statement negates the other"""
        stmt1_lower = stmt1.lower()
        stmt2_lower = stmt2.lower()

        # Check if one has negation and the other doesn't
        neg_count1 = sum(1 for neg in self.negation_words if f" {neg} " in f" {stmt1_lower} ")
        neg_count2 = sum(1 for neg in self.negation_words if f" {neg} " in f" {stmt2_lower} ")

        # XOR: one has negation, the other doesn't
        return (neg_count1 > 0) != (neg_count2 > 0)

    def _check_opposing_terms(self, stmt1: str, stmt2: str) -> bool:
        """Check if statements contain opposing term pairs"""
        stmt1_lower = stmt1.lower()
        stmt2_lower = stmt2.lower()

        for term1, term2 in self.opposing_pairs:
            # Check if one statement has term1 and the other has term2
            if (term1 in stmt1_lower and term2 in stmt2_lower) or \
               (term2 in stmt1_lower and term1 in stmt2_lower):
                return True

        return False

    def _generate_semantic_explanation(
        self,
        stmt1: str,
        stmt2: str,
        similarity: float,
        has_negation: bool,
        has_opposing: bool
    ) -> str:
        """Generate explanation for semantic contradiction"""
        explanation = f"Statements are semantically similar ({similarity:.2f}) but express opposing meanings. "

        if has_negation:
            explanation += "One statement negates what the other asserts. "
        if has_opposing:
            explanation += "Statements contain opposing terms (e.g., increase/decrease, adequate/inadequate). "

        explanation += "Review for logical consistency."
        return explanation

    def detect_numerical_contradictions(
        self,
        text: str
    ) -> List[Contradiction]:
        """
        Detect numerical inconsistencies

        Finds cases where the same metric is given different values,
        or where calculations don't add up.

        Args:
            text: Text to analyze

        Returns:
            List of numerical contradictions
        """
        contradictions = []

        # Extract numerical statements
        # Pattern: "X is $Y" or "X equals $Y" or "X of $Y"
        number_pattern = r'(\w+(?:\s+\w+){0,3})\s+(?:is|equals?|of|totals?|amounts? to)\s+\$?([\d,]+(?:\.\d{2})?)'
        matches = re.findall(number_pattern, text, re.IGNORECASE)

        # Group by metric name (rough matching)
        metric_values = {}
        for metric, value in matches:
            metric_clean = metric.strip().lower()
            value_clean = value.replace(',', '')

            try:
                value_num = float(value_clean)

                if metric_clean in metric_values:
                    # Check if different value for same metric
                    prev_value = metric_values[metric_clean]
                    if abs(value_num - prev_value) > 0.01:  # Allow for rounding
                        severity = ContradictionSeverity.CRITICAL
                        confidence = 0.90

                        contradictions.append(Contradiction(
                            severity=severity,
                            type="numerical",
                            statement1=f"{metric} is ${prev_value:,.2f}",
                            statement2=f"{metric} is ${value_num:,.2f}",
                            explanation=(
                                f"Same metric '{metric}' given two different values. "
                                f"Verify which is correct or if they refer to different periods."
                            ),
                            confidence=confidence
                        ))
                else:
                    metric_values[metric_clean] = value_num

            except ValueError:
                continue

        logger.info(f"Detected {len(contradictions)} numerical contradictions")
        return contradictions

    def detect_temporal_contradictions(
        self,
        text: str
    ) -> List[Contradiction]:
        """
        Detect temporal/timeline contradictions

        Finds inconsistencies in dates, sequences, or time-based statements.

        Args:
            text: Text to analyze

        Returns:
            List of temporal contradictions
        """
        contradictions = []

        # Extract temporal statements
        temporal_patterns = [
            r'(?:before|prior to|preceding)\s+([A-Za-z]+ \d{1,2},? \d{4})',
            r'(?:after|following|subsequent to)\s+([A-Za-z]+ \d{1,2},? \d{4})',
            r'(?:on|dated)\s+([A-Za-z]+ \d{1,2},? \d{4})',
            r'(?:in|during)\s+(?:fiscal year|FY|year)\s+(\d{4})',
        ]

        temporal_statements = []
        for pattern in temporal_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end]
                temporal_statements.append((match.group(0), context))

        # Check for contradictory temporal logic
        # E.g., "before March 2024" followed by "after March 2024" for same event
        for i in range(len(temporal_statements)):
            for j in range(i + 1, len(temporal_statements)):
                stmt1, context1 = temporal_statements[i]
                stmt2, context2 = temporal_statements[j]

                # Check if contexts are about same subject (simple word overlap check)
                words1 = set(re.findall(r'\w+', context1.lower()))
                words2 = set(re.findall(r'\w+', context2.lower()))
                overlap = len(words1 & words2) / len(words1 | words2) if words1 | words2 else 0

                if overlap > 0.3:  # Similar context
                    # Check for opposing temporal indicators
                    has_before = any(w in stmt1.lower() for w in ['before', 'prior', 'preceding'])
                    has_after = any(w in stmt2.lower() for w in ['after', 'following', 'subsequent'])

                    if has_before and has_after:
                        contradictions.append(Contradiction(
                            severity=ContradictionSeverity.HIGH,
                            type="temporal",
                            statement1=context1,
                            statement2=context2,
                            explanation=(
                                "Temporal contradiction detected: statements indicate conflicting "
                                "time sequences for the same event or subject."
                            ),
                            confidence=0.75
                        ))

        logger.info(f"Detected {len(contradictions)} temporal contradictions")
        return contradictions

    def detect_cross_document_contradictions(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Contradiction]:
        """
        Detect contradictions across multiple documents/workpapers

        Checks for inconsistent conclusions or findings across related
        audit workpapers.

        Args:
            documents: List of document dictionaries with 'content', 'title', 'id'

        Returns:
            List of cross-document contradictions
        """
        if len(documents) < 2:
            return []

        self._load_model()

        contradictions = []

        # Extract key conclusions from each document
        conclusions = []
        for doc in documents:
            content = doc.get('content', '')

            # Find conclusion sections (common audit workpaper structure)
            conclusion_patterns = [
                r'(?:Conclusion|Summary|Finding|Opinion|Assessment):\s*(.+?)(?:\n\n|$)',
                r'(?:We (?:conclude|find|determined) that)\s+(.+?)(?:\.|$)',
                r'(?:Based on (?:our|the) (?:review|analysis|procedures))[,:]?\s+(.+?)(?:\.|$)'
            ]

            for pattern in conclusion_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    conclusion_text = match.strip()
                    if len(conclusion_text) > 20:  # Substantial conclusion
                        conclusions.append({
                            'text': conclusion_text[:500],  # First 500 chars
                            'document_id': doc.get('id'),
                            'document_title': doc.get('title', 'Unknown')
                        })

        # Compare conclusions pairwise
        if len(conclusions) >= 2:
            texts = [c['text'] for c in conclusions]
            embeddings = self.model.encode(texts, convert_to_numpy=True)

            for i in range(len(conclusions)):
                for j in range(i + 1, len(conclusions)):
                    similarity = util.pytorch_cos_sim(embeddings[i], embeddings[j]).item()

                    # High similarity with opposing conclusions
                    if similarity > 0.7:
                        text1 = conclusions[i]['text']
                        text2 = conclusions[j]['text']

                        if self._check_negation_pattern(text1, text2) or \
                           self._check_opposing_terms(text1, text2):

                            contradictions.append(Contradiction(
                                severity=ContradictionSeverity.CRITICAL,
                                type="cross_document",
                                statement1=text1,
                                statement2=text2,
                                explanation=(
                                    f"Contradictory conclusions found between "
                                    f"'{conclusions[i]['document_title']}' and "
                                    f"'{conclusions[j]['document_title']}'. "
                                    f"Verify consistency across workpapers."
                                ),
                                confidence=0.85,
                                location1={'document_id': conclusions[i]['document_id'],
                                         'title': conclusions[i]['document_title']},
                                location2={'document_id': conclusions[j]['document_id'],
                                         'title': conclusions[j]['document_title']}
                            ))

        logger.info(f"Detected {len(contradictions)} cross-document contradictions")
        return contradictions

    def analyze_text(
        self,
        text: str,
        check_semantic: bool = True,
        check_numerical: bool = True,
        check_temporal: bool = True
    ) -> ContradictionReport:
        """
        Comprehensive contradiction analysis of text

        Args:
            text: Text to analyze
            check_semantic: Enable semantic contradiction detection
            check_numerical: Enable numerical contradiction detection
            check_temporal: Enable temporal contradiction detection

        Returns:
            ContradictionReport with all detected contradictions
        """
        logger.info("Starting comprehensive contradiction analysis")

        all_contradictions = []

        # 1. Semantic contradictions
        if check_semantic:
            # Split into substantial sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

            if len(sentences) >= 2:
                semantic = self.detect_semantic_contradictions(sentences)
                all_contradictions.extend(semantic)

        # 2. Numerical contradictions
        if check_numerical:
            numerical = self.detect_numerical_contradictions(text)
            all_contradictions.extend(numerical)

        # 3. Temporal contradictions
        if check_temporal:
            temporal = self.detect_temporal_contradictions(text)
            all_contradictions.extend(temporal)

        # Count by severity
        critical = sum(1 for c in all_contradictions if c.severity == ContradictionSeverity.CRITICAL)
        high = sum(1 for c in all_contradictions if c.severity == ContradictionSeverity.HIGH)
        medium = sum(1 for c in all_contradictions if c.severity == ContradictionSeverity.MEDIUM)
        low = sum(1 for c in all_contradictions if c.severity == ContradictionSeverity.LOW)

        # Calculate consistency score
        # Start at 1.0, deduct based on contradictions
        consistency_score = 1.0
        consistency_score -= critical * 0.20
        consistency_score -= high * 0.10
        consistency_score -= medium * 0.05
        consistency_score -= low * 0.02
        consistency_score = max(0.0, consistency_score)

        # Generate recommendation
        recommendation = self._generate_recommendation(
            len(all_contradictions),
            critical,
            high,
            consistency_score
        )

        report = ContradictionReport(
            has_contradictions=len(all_contradictions) > 0,
            contradiction_count=len(all_contradictions),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            contradictions=all_contradictions,
            overall_consistency_score=round(consistency_score, 3),
            recommendation=recommendation
        )

        logger.info(
            f"Contradiction analysis complete: {len(all_contradictions)} found "
            f"(Critical: {critical}, High: {high}, Medium: {medium}, Low: {low})"
        )

        return report

    def _generate_recommendation(
        self,
        total_count: int,
        critical_count: int,
        high_count: int,
        consistency_score: float
    ) -> str:
        """Generate recommendation based on findings"""
        if critical_count > 0:
            return (
                f"⚠️ CRITICAL: {critical_count} critical contradiction(s) detected. "
                "Do NOT finalize until resolved. Manual CPA review required immediately."
            )
        elif high_count > 0:
            return (
                f"⚠️ WARNING: {high_count} high-severity contradiction(s) found. "
                "Resolve before proceeding to finalization."
            )
        elif total_count > 0:
            return (
                f"ℹ️ REVIEW: {total_count} potential inconsistency(ies) detected. "
                "Review and clarify before partner sign-off."
            )
        else:
            return (
                f"✓ PASS: No contradictions detected. "
                f"Content is logically consistent (score: {consistency_score:.1%})."
            )


# Global contradiction detector instance
contradiction_detector = ContradictionDetector()
