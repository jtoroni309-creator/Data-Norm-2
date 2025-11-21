"""
Smart Statistical Sampling Service
====================================
COMPETITIVE DIFFERENTIATOR #7: AI-optimized adaptive sampling

Uses statistical methods + AI to determine optimal sample sizes and selections

Key Features:
- Multiple sampling methods (random, stratified, systematic, cluster, judgmental)
- AI-optimized sample size recommendations
- Adaptive sampling (adjusts based on error rates)
- Risk-based sample selection
- Statistical confidence calculations
- CPA approval workflow
"""

import logging
import math
import random
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime
from enum import Enum

import numpy as np
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings

logger = logging.getLogger(__name__)


class SamplingMethod(str, Enum):
    """Sampling methods"""
    RANDOM = "RANDOM"
    STRATIFIED = "STRATIFIED"
    SYSTEMATIC = "SYSTEMATIC"
    CLUSTER = "CLUSTER"
    JUDGMENTAL = "JUDGMENTAL"
    AI_OPTIMIZED = "AI_OPTIMIZED"


class SmartSamplingService:
    """
    Intelligent statistical sampling with AI optimization
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.enabled = settings.ENABLE_AI_PLANNING and settings.OPENAI_API_KEY is not None

    def calculate_sample_size(
        self,
        population_size: int,
        confidence_level: float = 95.0,
        tolerable_error_rate: float = 5.0,
        expected_error_rate: float = 2.0,
        method: SamplingMethod = SamplingMethod.RANDOM
    ) -> Dict[str, Any]:
        """
        Calculate required sample size using statistical formulas

        Args:
            population_size: Total population size
            confidence_level: Confidence level (90%, 95%, 99%)
            tolerable_error_rate: Maximum acceptable error rate (%)
            expected_error_rate: Expected error rate based on prior knowledge (%)
            method: Sampling method

        Returns:
            Sample size calculation with statistical metrics
        """
        logger.info(f"Calculating sample size for population={population_size}, method={method}")

        # Convert percentages to decimals
        confidence = confidence_level / 100.0
        tolerable_error = tolerable_error_rate / 100.0
        expected_error = expected_error_rate / 100.0

        # Z-score based on confidence level
        z_scores = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }
        z = z_scores.get(confidence, 1.96)

        # Attribute sampling formula (for proportion/error rate testing)
        # n = (Z^2 * p * (1-p)) / E^2
        # Where p = expected error rate, E = tolerable error rate

        p = expected_error
        e = tolerable_error

        # Calculate sample size (infinite population formula)
        n_infinite = (z ** 2 * p * (1 - p)) / (e ** 2)

        # Finite population correction
        # n_adjusted = n / (1 + (n-1)/N)
        if population_size > 0:
            n_adjusted = n_infinite / (1 + (n_infinite - 1) / population_size)
        else:
            n_adjusted = n_infinite

        # Round up
        sample_size = math.ceil(n_adjusted)

        # Minimum sample size (audit best practice)
        min_sample = max(25, sample_size)

        # Maximum sample size (practical limit)
        max_sample = min(min_sample, population_size) if population_size > 0 else min_sample

        # Calculate sampling risk
        # Risk of incorrect acceptance = alpha (1 - confidence)
        # Risk of incorrect rejection = beta (typically 5-10%)
        risk_of_incorrect_acceptance = 1 - confidence
        risk_of_incorrect_rejection = 0.10  # 10% beta risk

        # Calculate precision
        # Precision = z * sqrt(p*(1-p)/n)
        if max_sample > 0:
            precision = z * math.sqrt(p * (1 - p) / max_sample)
        else:
            precision = 0

        result = {
            "population_size": population_size,
            "confidence_level": confidence_level,
            "tolerable_error_rate": tolerable_error_rate,
            "expected_error_rate": expected_error_rate,
            "sampling_method": method.value,
            "calculated_sample_size": int(n_infinite),
            "adjusted_sample_size": int(n_adjusted),
            "recommended_sample_size": max_sample,
            "minimum_sample_size": 25,
            "sampling_percentage": round((max_sample / population_size * 100), 2) if population_size > 0 else 0,
            "statistical_metrics": {
                "z_score": z,
                "precision": round(precision, 4),
                "risk_of_incorrect_acceptance": round(risk_of_incorrect_acceptance, 4),
                "risk_of_incorrect_rejection": round(risk_of_incorrect_rejection, 4)
            },
            "calculated_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Recommended sample size: {max_sample} ({result['sampling_percentage']:.1f}% of population)")
        return result

    async def ai_optimize_sample_size(
        self,
        db: AsyncSession,
        population_size: int,
        control_info: Dict[str, Any],
        historical_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use AI to optimize sample size based on risk factors

        Args:
            db: Database session
            population_size: Population size
            control_info: Information about the control being tested
            historical_data: Historical test results for this control

        Returns:
            AI-optimized sample size recommendation
        """
        if not self.enabled:
            # Fallback to statistical calculation
            return self.calculate_sample_size(population_size)

        logger.info(f"AI optimizing sample size for control: {control_info.get('control_name')}")

        try:
            prompt = f"""
Recommend optimal sample size for audit testing:

Population Size: {population_size}
Control Information: {control_info}
Historical Data: {historical_data or "No historical data"}

Consider:
1. Control criticality and risk level
2. Historical error rates (if available)
3. Technology complexity
4. Prior audit findings
5. Cost-benefit trade-off

Recommend:
- Optimal sample size
- Rationale for size
- Risk factors considered
- Confidence level to use
- Tolerable error rate

Return as JSON with keys: recommended_sample_size, confidence_level, tolerable_error_rate, expected_error_rate, rationale, risk_factors
"""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an audit sampling expert. Recommend statistically sound sample sizes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            import json
            ai_recommendation = json.loads(response.choices[0].message.content)

            # Calculate with AI-recommended parameters
            statistical_calc = self.calculate_sample_size(
                population_size=population_size,
                confidence_level=ai_recommendation.get("confidence_level", 95.0),
                tolerable_error_rate=ai_recommendation.get("tolerable_error_rate", 5.0),
                expected_error_rate=ai_recommendation.get("expected_error_rate", 2.0),
                method=SamplingMethod.AI_OPTIMIZED
            )

            # Merge AI recommendation with statistical calculation
            statistical_calc["ai_recommended_size"] = ai_recommendation.get("recommended_sample_size")
            statistical_calc["ai_rationale"] = ai_recommendation.get("rationale")
            statistical_calc["ai_risk_factors"] = ai_recommendation.get("risk_factors", [])

            logger.info(f"AI recommended: {ai_recommendation.get('recommended_sample_size')} samples")
            return statistical_calc

        except Exception as e:
            logger.error(f"AI optimization failed: {e}")
            return self.calculate_sample_size(population_size)

    def select_random_sample(
        self,
        population: List[Any],
        sample_size: int,
        seed: Optional[int] = None
    ) -> List[Any]:
        """
        Simple random sampling

        Args:
            population: List of all items
            sample_size: Number of items to select
            seed: Random seed for reproducibility

        Returns:
            Random sample
        """
        if seed:
            random.seed(seed)

        if sample_size >= len(population):
            return population

        return random.sample(population, sample_size)

    def select_systematic_sample(
        self,
        population: List[Any],
        sample_size: int
    ) -> List[Any]:
        """
        Systematic sampling (every Nth item)

        Args:
            population: Sorted list of items
            sample_size: Number of items to select

        Returns:
            Systematic sample
        """
        if sample_size >= len(population):
            return population

        # Calculate sampling interval
        interval = len(population) // sample_size

        # Random start point
        start = random.randint(0, interval - 1)

        # Select every Nth item
        sample = []
        for i in range(sample_size):
            index = (start + i * interval) % len(population)
            sample.append(population[index])

        return sample

    def select_stratified_sample(
        self,
        population: List[Dict[str, Any]],
        sample_size: int,
        stratify_by: str
    ) -> List[Dict[str, Any]]:
        """
        Stratified sampling (proportional representation from strata)

        Args:
            population: List of items with stratification field
            sample_size: Total sample size
            stratify_by: Field name to stratify by

        Returns:
            Stratified sample
        """
        # Group by strata
        strata = {}
        for item in population:
            stratum_value = item.get(stratify_by, "UNKNOWN")
            if stratum_value not in strata:
                strata[stratum_value] = []
            strata[stratum_value].append(item)

        # Calculate proportional sample sizes
        sample = []
        for stratum_name, stratum_items in strata.items():
            stratum_proportion = len(stratum_items) / len(population)
            stratum_sample_size = max(1, int(sample_size * stratum_proportion))

            stratum_sample = self.select_random_sample(stratum_items, stratum_sample_size)
            sample.extend(stratum_sample)

        return sample[:sample_size]  # Trim to exact size

    async def adaptive_sampling_adjustment(
        self,
        initial_sample_size: int,
        errors_found: int,
        tests_completed: int,
        tolerable_error_rate: float = 5.0
    ) -> Dict[str, Any]:
        """
        Adaptively adjust sample size based on errors found

        If error rate is higher than expected, increase sample size

        Args:
            initial_sample_size: Original planned sample size
            errors_found: Number of errors found so far
            tests_completed: Number of tests completed so far
            tolerable_error_rate: Maximum acceptable error rate (%)

        Returns:
            Adjustment recommendation
        """
        logger.info(f"Evaluating adaptive sampling: {errors_found} errors in {tests_completed} tests")

        if tests_completed == 0:
            return {
                "adjustment_needed": False,
                "reason": "No tests completed yet"
            }

        # Calculate current error rate
        current_error_rate = (errors_found / tests_completed) * 100

        tolerable_error = tolerable_error_rate

        # Determine if adjustment needed
        if current_error_rate > tolerable_error:
            # Error rate exceeds tolerance - need more samples

            # Calculate additional samples needed
            # Use sequential sampling formula
            additional_samples = math.ceil(initial_sample_size * 0.50)  # Increase by 50%

            adjustment = {
                "adjustment_needed": True,
                "adjustment_trigger": "HIGH_ERROR_RATE",
                "current_error_rate": round(current_error_rate, 2),
                "tolerable_error_rate": tolerable_error,
                "original_sample_size": initial_sample_size,
                "additional_samples_needed": additional_samples,
                "new_total_sample_size": initial_sample_size + additional_samples,
                "rationale": f"Error rate ({current_error_rate:.1f}%) exceeds tolerance ({tolerable_error}%). Expanding sample to improve statistical confidence.",
                "requires_cpa_approval": True,
                "calculated_at": datetime.utcnow().isoformat()
            }

            logger.warning(f"Sample expansion recommended: {additional_samples} additional samples")
            return adjustment

        elif current_error_rate < tolerable_error / 2 and tests_completed >= initial_sample_size:
            # Error rate significantly below expectations - can potentially reduce future samples
            # (But don't reduce current sample - audit conservatism)

            adjustment = {
                "adjustment_needed": False,
                "observation": "LOW_ERROR_RATE",
                "current_error_rate": round(current_error_rate, 2),
                "tolerable_error_rate": tolerable_error,
                "note": "Error rate lower than expected. No adjustment needed, but future samples for this control could potentially be reduced.",
                "calculated_at": datetime.utcnow().isoformat()
            }

            logger.info("Error rate below expectations - no adjustment needed")
            return adjustment

        else:
            # Error rate within acceptable range
            adjustment = {
                "adjustment_needed": False,
                "observation": "WITHIN_TOLERANCE",
                "current_error_rate": round(current_error_rate, 2),
                "tolerable_error_rate": tolerable_error,
                "note": "Error rate within acceptable range. Continue with original sample plan.",
                "calculated_at": datetime.utcnow().isoformat()
            }

            logger.info("Sample size appropriate - no adjustment needed")
            return adjustment

    async def risk_based_sample_selection(
        self,
        db: AsyncSession,
        population: List[Dict[str, Any]],
        sample_size: int,
        risk_field: str = "risk_score"
    ) -> List[Dict[str, Any]]:
        """
        Risk-based sampling - prioritize high-risk items

        Args:
            db: Database session
            population: List of items with risk scores
            sample_size: Number to select
            risk_field: Field containing risk score

        Returns:
            Risk-weighted sample
        """
        logger.info(f"Performing risk-based sampling on {len(population)} items")

        if sample_size >= len(population):
            return population

        # Sort by risk (highest first)
        sorted_pop = sorted(
            population,
            key=lambda x: x.get(risk_field, 0),
            reverse=True
        )

        # Hybrid approach: Select top 30% by risk, then random from remaining
        high_risk_count = math.ceil(sample_size * 0.30)
        random_count = sample_size - high_risk_count

        # Select high-risk items
        high_risk_sample = sorted_pop[:high_risk_count]

        # Random from remaining
        remaining = sorted_pop[high_risk_count:]
        if random_count > 0 and remaining:
            random_sample = self.select_random_sample(remaining, min(random_count, len(remaining)))
        else:
            random_sample = []

        combined_sample = high_risk_sample + random_sample

        logger.info(f"Selected {len(high_risk_sample)} high-risk + {len(random_sample)} random items")
        return combined_sample

    def calculate_sampling_results(
        self,
        sample_size: int,
        errors_found: int,
        confidence_level: float = 95.0
    ) -> Dict[str, Any]:
        """
        Calculate statistical results after sampling

        Args:
            sample_size: Total samples tested
            errors_found: Number of errors found
            confidence_level: Confidence level (%)

        Returns:
            Statistical analysis of results
        """
        logger.info(f"Calculating sampling results: {errors_found} errors in {sample_size} tests")

        if sample_size == 0:
            return {"error": "No samples tested"}

        # Observed error rate
        error_rate = (errors_found / sample_size) * 100

        # Calculate upper confidence limit (UCL) for error rate
        # Using Wilson score interval
        confidence = confidence_level / 100.0
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z = z_scores.get(confidence, 1.96)

        p = errors_found / sample_size
        n = sample_size

        # Wilson score interval
        denominator = 1 + (z ** 2) / n
        center = (p + (z ** 2) / (2 * n)) / denominator
        margin = (z / denominator) * math.sqrt((p * (1 - p) / n) + (z ** 2) / (4 * n ** 2))

        ucl = (center + margin) * 100
        lcl = max(0, (center - margin) * 100)

        # Determine conclusion
        if errors_found == 0:
            conclusion = "PASS - No errors found in sample"
        elif error_rate < 5.0:
            conclusion = "PASS - Error rate within acceptable limits"
        elif error_rate < 10.0:
            conclusion = "QUALIFIED - Error rate elevated, requires review"
        else:
            conclusion = "FAIL - Error rate exceeds acceptable limits"

        results = {
            "sample_size": sample_size,
            "errors_found": errors_found,
            "error_rate": round(error_rate, 2),
            "confidence_level": confidence_level,
            "upper_confidence_limit": round(ucl, 2),
            "lower_confidence_limit": round(lcl, 2),
            "confidence_interval": f"{round(lcl, 2)}% - {round(ucl, 2)}%",
            "precision": round((ucl - lcl) / 2, 2),
            "conclusion": conclusion,
            "calculated_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Results: {error_rate:.1f}% error rate, UCL: {ucl:.1f}%, Conclusion: {conclusion}")
        return results


# Global instance
smart_sampling_service = SmartSamplingService()
