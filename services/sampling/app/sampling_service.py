"""
Statistical Sampling Service

Implements audit sampling methods per PCAOB AS 2315 and AICPA AU-C 530.

Provides:
- Monetary Unit Sampling (MUS/PPS - Probability Proportional to Size)
- Classical Variables Sampling (Mean-per-unit, Ratio, Difference estimation)
- Attribute Sampling for control testing
- Sample size determination based on risk parameters
- Sample evaluation and projection of errors
"""

import logging
import math
import random
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class SamplingMethod(str, Enum):
    """Statistical sampling methods"""
    MUS = "mus"  # Monetary Unit Sampling (Probability Proportional to Size)
    MEAN_PER_UNIT = "mean_per_unit"  # Classical variables sampling
    RATIO_ESTIMATION = "ratio"  # Ratio estimation
    DIFFERENCE_ESTIMATION = "difference"  # Difference estimation
    ATTRIBUTE = "attribute"  # Attribute sampling for controls


class RiskLevel(str, Enum):
    """Audit risk levels"""
    LOW = "low"  # 5% risk
    MODERATE = "moderate"  # 10% risk
    HIGH = "high"  # 20% risk


class MonetaryUnitSampling:
    """
    Monetary Unit Sampling (MUS) / Probability Proportional to Size (PPS).

    Used for substantive testing when:
    - Population is large
    - Low error rate expected
    - Overstatement is primary concern
    - Zero or negative balances are rare

    Advantages:
    - Automatically stratifies (larger items more likely selected)
    - Efficient for testing overstatement
    - Does not require normal distribution assumption

    Formula:
    Sample Size (n) = (RF × BV) / TM
    Where:
    - RF = Reliability Factor (based on risk of incorrect acceptance)
    - BV = Book Value (population value)
    - TM = Tolerable Misstatement
    """

    # Reliability factors for zero errors (from statistical tables)
    RELIABILITY_FACTORS = {
        RiskLevel.LOW: 3.00,    # 5% risk of incorrect acceptance
        RiskLevel.MODERATE: 2.31,  # 10% risk
        RiskLevel.HIGH: 1.61,   # 20% risk
    }

    @classmethod
    def calculate_sample_size(
        cls,
        population_value: Decimal,
        tolerable_misstatement: Decimal,
        expected_misstatement: Decimal,
        risk_level: RiskLevel = RiskLevel.MODERATE,
    ) -> Dict:
        """
        Calculate required sample size for MUS.

        Args:
            population_value: Total population book value
            tolerable_misstatement: Maximum acceptable misstatement (usually performance materiality)
            expected_misstatement: Anticipated misstatement based on prior experience
            risk_level: Risk of incorrect acceptance

        Returns:
            Dictionary with sample_size, sampling_interval, and other parameters
        """
        rf = Decimal(str(cls.RELIABILITY_FACTORS[risk_level]))

        # Adjust reliability factor for expected misstatement
        if expected_misstatement > 0:
            expected_tainting = expected_misstatement / population_value
            # Use expansion factor (simplified - full calculation more complex)
            expansion_factor = Decimal("1.3")  # Conservative adjustment
            rf = rf * expansion_factor

        # Calculate sample size
        sample_size_exact = (rf * population_value) / tolerable_misstatement

        # Round up to ensure adequate coverage
        sample_size = int(math.ceil(float(sample_size_exact)))

        # Ensure minimum sample size
        sample_size = max(sample_size, 30)  # Professional judgment minimum

        # Calculate sampling interval
        sampling_interval = population_value / Decimal(sample_size)

        return {
            "sample_size": sample_size,
            "sampling_interval": round(sampling_interval, 2),
            "reliability_factor": float(rf),
            "population_value": float(population_value),
            "tolerable_misstatement": float(tolerable_misstatement),
            "expected_misstatement": float(expected_misstatement),
            "risk_level": risk_level.value,
            "method": "mus",
        }

    @classmethod
    def select_sample(
        cls,
        population: List[Dict],  # List of {"id": ..., "amount": ...}
        sample_size: int,
        sampling_interval: Decimal,
    ) -> List[Dict]:
        """
        Select sample items using systematic selection with random start.

        Args:
            population: List of population items with 'id' and 'amount'
            sample_size: Number of items to select
            sampling_interval: Monetary interval between selections

        Returns:
            List of selected sample items
        """
        # Sort population by ID for systematic selection
        sorted_pop = sorted(population, key=lambda x: x["id"])

        # Calculate cumulative amounts
        cumulative_amounts = []
        cumulative = Decimal("0")
        for item in sorted_pop:
            cumulative += Decimal(str(item["amount"]))
            cumulative_amounts.append(cumulative)

        # Random start between 0 and sampling interval
        random_start = Decimal(str(random.uniform(0, float(sampling_interval))))

        # Select sample items
        selected_items = []
        current_selection_point = random_start

        for _ in range(sample_size):
            # Find item containing this selection point
            for i, cum_amount in enumerate(cumulative_amounts):
                if cum_amount >= current_selection_point:
                    if sorted_pop[i] not in selected_items:
                        selected_items.append(sorted_pop[i])
                    break

            # Move to next selection point
            current_selection_point += sampling_interval

            # Stop if we've exceeded population
            if current_selection_point > cumulative_amounts[-1]:
                break

        return selected_items

    @classmethod
    def evaluate_sample(
        cls,
        sample_results: List[Dict],  # [{"book_value": ..., "audit_value": ...}]
        population_value: Decimal,
        tolerable_misstatement: Decimal,
        risk_level: RiskLevel = RiskLevel.MODERATE,
    ) -> Dict:
        """
        Evaluate MUS sample results and project errors to population.

        Args:
            sample_results: List of sample items with book and audit values
            population_value: Total population book value
            tolerable_misstatement: Maximum acceptable misstatement
            risk_level: Risk of incorrect acceptance

        Returns:
            Dictionary with projected misstatement, conclusion, and details
        """
        rf = Decimal(str(cls.RELIABILITY_FACTORS[risk_level]))

        # Calculate taintings for each misstatement
        taintings = []
        total_misstatement = Decimal("0")

        for item in sample_results:
            book_value = Decimal(str(item["book_value"]))
            audit_value = Decimal(str(item["audit_value"]))
            misstatement = book_value - audit_value

            if misstatement != 0 and book_value != 0:
                tainting = misstatement / book_value
                taintings.append({
                    "misstatement": float(misstatement),
                    "tainting": float(tainting),
                    "book_value": float(book_value),
                })
                total_misstatement += misstatement

        # Project errors to population
        # Simplified projection (full MUS projection more complex with layering)
        if len(taintings) == 0:
            # No errors found - basic projection
            projected_misstatement = (rf * population_value) / Decimal(len(sample_results))
        else:
            # Errors found - sum of taintings method
            total_tainting = sum(Decimal(str(t["tainting"])) for t in taintings)
            projected_misstatement = total_tainting * population_value

        # Upper misstatement limit (UML) - includes allowance for sampling risk
        uml = projected_misstatement * Decimal("1.3")  # Add precision allowance

        # Determine conclusion
        conclusion = "ACCEPT" if uml < tolerable_misstatement else "REJECT"

        return {
            "projected_misstatement": round(float(projected_misstatement), 2),
            "upper_misstatement_limit": round(float(uml), 2),
            "tolerable_misstatement": float(tolerable_misstatement),
            "actual_misstatements_found": len(taintings),
            "total_known_misstatement": round(float(total_misstatement), 2),
            "misstatement_details": taintings,
            "conclusion": conclusion,
            "conclusion_rationale": (
                f"UML ({round(float(uml), 2)}) is {'less than' if conclusion == 'ACCEPT' else 'greater than'} "
                f"tolerable misstatement ({float(tolerable_misstatement)})"
            ),
        }


class ClassicalVariablesSampling:
    """
    Classical Variables Sampling using normal distribution theory.

    Methods:
    - Mean-per-unit estimation
    - Ratio estimation
    - Difference estimation

    Used when:
    - Population values not highly skewed
    - Errors expected in both directions (over/understatement)
    - Reliable estimate of population standard deviation available
    """

    @staticmethod
    def calculate_sample_size_mean_per_unit(
        population_size: int,
        population_std_dev: Decimal,
        tolerable_misstatement: Decimal,
        risk_level: RiskLevel = RiskLevel.MODERATE,
    ) -> int:
        """
        Calculate sample size for mean-per-unit estimation.

        Formula:
        n = (N × σ × Z_alpha / TM)^2

        Where:
        - N = Population size
        - σ = Population standard deviation
        - Z_alpha = Z-score for confidence level
        - TM = Tolerable misstatement
        """
        # Z-scores for confidence levels
        z_scores = {
            RiskLevel.LOW: 1.96,   # 95% confidence (5% risk)
            RiskLevel.MODERATE: 1.645,  # 90% confidence (10% risk)
            RiskLevel.HIGH: 1.28,   # 80% confidence (20% risk)
        }
        z = Decimal(str(z_scores[risk_level]))

        # Calculate sample size
        numerator = Decimal(population_size) * population_std_dev * z
        denominator = tolerable_misstatement

        sample_size_exact = (numerator / denominator) ** 2

        # Apply finite population correction
        sample_size = int(math.ceil(
            float(sample_size_exact) /
            (1 + float(sample_size_exact) / population_size)
        ))

        # Ensure minimum sample size
        sample_size = max(sample_size, 30)

        return sample_size

    @staticmethod
    def evaluate_mean_per_unit(
        sample_values: List[Decimal],
        population_size: int,
        tolerable_misstatement: Decimal,
        risk_level: RiskLevel = RiskLevel.MODERATE,
    ) -> Dict:
        """
        Evaluate sample using mean-per-unit estimation.

        Projects sample mean to population and calculates precision.
        """
        z_scores = {
            RiskLevel.LOW: 1.96,
            RiskLevel.MODERATE: 1.645,
            RiskLevel.HIGH: 1.28,
        }
        z = Decimal(str(z_scores[risk_level]))

        # Calculate sample statistics
        sample_mean = sum(sample_values) / Decimal(len(sample_values))
        sample_std_dev = Decimal(str(np.std([float(v) for v in sample_values], ddof=1)))

        # Project to population
        projected_value = sample_mean * Decimal(population_size)

        # Calculate precision (allowance for sampling risk)
        n = Decimal(len(sample_values))
        N = Decimal(population_size)
        precision = z * sample_std_dev * (N / n**Decimal("0.5")) * ((N - n) / N)**Decimal("0.5")

        # Precision interval
        lower_limit = projected_value - precision
        upper_limit = projected_value + precision

        return {
            "projected_value": round(float(projected_value), 2),
            "precision": round(float(precision), 2),
            "confidence_interval": {
                "lower": round(float(lower_limit), 2),
                "upper": round(float(upper_limit), 2),
            },
            "sample_mean": round(float(sample_mean), 2),
            "sample_std_dev": round(float(sample_std_dev), 2),
            "sample_size": len(sample_values),
        }


class AttributeSampling:
    """
    Attribute Sampling for testing controls.

    Used for testing frequency of control deviations.

    Steps:
    1. Determine tolerable deviation rate
    2. Assess expected deviation rate
    3. Calculate sample size
    4. Evaluate sample and determine upper deviation limit
    """

    # Sample size tables (simplified - full tables in AU-C 530)
    SAMPLE_SIZE_TABLE = {
        # (expected_rate, tolerable_rate, risk_level) → sample_size
        (0.00, 0.05, RiskLevel.LOW): 93,
        (0.00, 0.05, RiskLevel.MODERATE): 77,
        (0.00, 0.10, RiskLevel.LOW): 46,
        (0.00, 0.10, RiskLevel.MODERATE): 38,
        (0.01, 0.05, RiskLevel.LOW): 156,
        (0.01, 0.05, RiskLevel.MODERATE): 129,
        (0.02, 0.06, RiskLevel.LOW): 127,
        (0.02, 0.06, RiskLevel.MODERATE): 105,
    }

    @classmethod
    def calculate_sample_size(
        cls,
        population_size: int,
        tolerable_deviation_rate: Decimal,
        expected_deviation_rate: Decimal = Decimal("0.0"),
        risk_level: RiskLevel = RiskLevel.MODERATE,
    ) -> int:
        """
        Calculate sample size for attribute sampling.

        Uses statistical tables or formulas based on binomial distribution.

        Args:
            population_size: Number of items in population
            tolerable_deviation_rate: Maximum acceptable deviation rate (e.g., 0.05 for 5%)
            expected_deviation_rate: Anticipated deviation rate
            risk_level: Risk of over-reliance on controls

        Returns:
            Required sample size
        """
        # Try to find in lookup table
        tdr = float(tolerable_deviation_rate)
        edr = float(expected_deviation_rate)

        # Round to nearest table values
        table_key = (
            round(edr, 2),
            round(tdr, 2) if tdr <= 0.10 else 0.10,
            risk_level
        )

        if table_key in cls.SAMPLE_SIZE_TABLE:
            sample_size = cls.SAMPLE_SIZE_TABLE[table_key]
        else:
            # Use approximation formula
            z_scores = {RiskLevel.LOW: 1.96, RiskLevel.MODERATE: 1.645, RiskLevel.HIGH: 1.28}
            z = z_scores[risk_level]

            # Binomial approximation
            p = float(tolerable_deviation_rate)
            sample_size = int(math.ceil(
                (z ** 2 * p * (1 - p)) / ((float(tolerable_deviation_rate) - float(expected_deviation_rate)) ** 2)
            ))

        # Apply finite population correction for small populations
        if population_size < 10000:
            sample_size = int(math.ceil(
                sample_size / (1 + sample_size / population_size)
            ))

        # Ensure reasonable bounds
        sample_size = max(25, min(sample_size, population_size))

        return sample_size

    @classmethod
    def evaluate_sample(
        cls,
        sample_size: int,
        deviations_found: int,
        tolerable_deviation_rate: Decimal,
        risk_level: RiskLevel = RiskLevel.MODERATE,
    ) -> Dict:
        """
        Evaluate attribute sample and determine if controls can be relied upon.

        Calculates upper deviation limit and compares to tolerable rate.

        Args:
            sample_size: Number of items tested
            deviations_found: Number of control deviations found
            tolerable_deviation_rate: Maximum acceptable deviation rate
            risk_level: Risk of over-reliance

        Returns:
            Dictionary with evaluation results and conclusion
        """
        # Calculate sample deviation rate
        sample_deviation_rate = Decimal(deviations_found) / Decimal(sample_size)

        # Calculate upper deviation limit using statistical tables
        # Simplified - full calculation uses binomial distribution
        z_scores = {RiskLevel.LOW: 1.96, RiskLevel.MODERATE: 1.645, RiskLevel.HIGH: 1.28}
        z = Decimal(str(z_scores[risk_level]))

        # Approximate upper limit using normal approximation
        p = float(sample_deviation_rate)
        n = sample_size
        standard_error = Decimal(str(math.sqrt(p * (1 - p) / n)))
        upper_deviation_limit = sample_deviation_rate + (z * standard_error)

        # Ensure upper limit doesn't exceed 1.0
        upper_deviation_limit = min(upper_deviation_limit, Decimal("1.0"))

        # Determine conclusion
        conclusion = "RELY" if upper_deviation_limit < tolerable_deviation_rate else "DO_NOT_RELY"

        return {
            "sample_size": sample_size,
            "deviations_found": deviations_found,
            "sample_deviation_rate": round(float(sample_deviation_rate), 4),
            "upper_deviation_limit": round(float(upper_deviation_limit), 4),
            "tolerable_deviation_rate": float(tolerable_deviation_rate),
            "conclusion": conclusion,
            "conclusion_rationale": (
                f"Upper deviation limit ({round(float(upper_deviation_limit), 4)}) is "
                f"{'less than' if conclusion == 'RELY' else 'greater than'} "
                f"tolerable rate ({float(tolerable_deviation_rate)}). "
                f"Controls {'can' if conclusion == 'RELY' else 'cannot'} be relied upon."
            ),
        }


class SamplingService:
    """
    Main service for statistical sampling operations.

    Provides unified interface to all sampling methods.
    """

    def __init__(self):
        self.mus = MonetaryUnitSampling()
        self.classical = ClassicalVariablesSampling()
        self.attribute = AttributeSampling()

    def recommend_sampling_method(
        self,
        population_size: int,
        population_value: Decimal,
        test_objective: str,  # "overstatement", "understatement", "controls"
        expected_error_rate: Decimal = Decimal("0.0"),
    ) -> SamplingMethod:
        """
        Recommend appropriate sampling method based on circumstances.

        Decision factors:
        - Test objective (overstatement vs understatement)
        - Population characteristics
        - Expected error rate
        - Population size

        Returns:
            Recommended sampling method
        """
        if test_objective == "controls":
            return SamplingMethod.ATTRIBUTE

        # For substantive testing
        if expected_error_rate < Decimal("0.05") and test_objective == "overstatement":
            # Low expected errors and testing overstatement → MUS
            return SamplingMethod.MUS

        if population_size < 100:
            # Small population → examine all or use classical
            return SamplingMethod.MEAN_PER_UNIT

        # Default to classical variables sampling for understatement or higher error rates
        return SamplingMethod.MEAN_PER_UNIT

    def calculate_optimal_sample_size(
        self,
        method: SamplingMethod,
        **kwargs
    ) -> int:
        """
        Calculate sample size for given method and parameters.

        Delegates to appropriate sampling class.
        """
        if method == SamplingMethod.MUS:
            result = self.mus.calculate_sample_size(
                population_value=kwargs["population_value"],
                tolerable_misstatement=kwargs["tolerable_misstatement"],
                expected_misstatement=kwargs.get("expected_misstatement", Decimal("0")),
                risk_level=kwargs.get("risk_level", RiskLevel.MODERATE),
            )
            return result["sample_size"]

        elif method == SamplingMethod.MEAN_PER_UNIT:
            return self.classical.calculate_sample_size_mean_per_unit(
                population_size=kwargs["population_size"],
                population_std_dev=kwargs["population_std_dev"],
                tolerable_misstatement=kwargs["tolerable_misstatement"],
                risk_level=kwargs.get("risk_level", RiskLevel.MODERATE),
            )

        elif method == SamplingMethod.ATTRIBUTE:
            return self.attribute.calculate_sample_size(
                population_size=kwargs["population_size"],
                tolerable_deviation_rate=kwargs["tolerable_deviation_rate"],
                expected_deviation_rate=kwargs.get("expected_deviation_rate", Decimal("0.0")),
                risk_level=kwargs.get("risk_level", RiskLevel.MODERATE),
            )

        else:
            raise ValueError(f"Unsupported sampling method: {method}")
