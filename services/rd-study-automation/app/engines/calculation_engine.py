"""
Deterministic Calculation Engine for R&D Tax Credits

Computes Federal Regular Credit, Alternative Simplified Credit (ASC),
and state credits with full audit trail and step-by-step documentation.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from uuid import UUID
from datetime import date, datetime
from enum import Enum

from .rules_engine import RulesEngine, StateRules

logger = logging.getLogger(__name__)


class CalculationMethod(str, Enum):
    """Credit calculation method."""
    REGULAR = "regular"
    ASC = "asc"


@dataclass
class CalculationStep:
    """
    Individual calculation step for audit trail.

    Each step is deterministic and reproducible.
    """
    step_number: int
    description: str
    formula: str
    inputs: Dict[str, Any]
    result: Decimal
    irc_reference: str
    notes: Optional[str] = None


@dataclass
class BasePeriodData:
    """Base period data for Regular credit calculation."""
    years: Dict[int, Dict[str, Decimal]]  # {year: {qre, gross_receipts}}
    fixed_base_percentage: Decimal
    average_annual_gross_receipts: Decimal
    is_startup: bool = False
    startup_years: int = 0


@dataclass
class FederalCreditResult:
    """Result of Federal R&D credit calculation."""
    method: CalculationMethod
    tax_year: int

    # QRE Inputs
    qre_wages: Decimal
    qre_supplies: Decimal
    qre_contract: Decimal
    qre_basic_research: Decimal
    total_qre: Decimal

    # Base calculation (Regular method)
    base_period_data: Optional[BasePeriodData]
    base_amount: Decimal

    # Credit calculation
    credit_rate: Decimal
    excess_qre: Decimal
    tentative_credit: Decimal

    # Adjustments
    section_280c_election: bool
    section_280c_reduction: Decimal
    controlled_group_allocation: Decimal  # Percentage
    allocated_credit: Decimal

    # Final credit
    final_credit: Decimal

    # Qualified Small Business provisions
    is_qsb: bool
    payroll_tax_offset_eligible: Decimal
    payroll_tax_offset_claimed: Decimal

    # Calculation steps for audit trail
    steps: List[CalculationStep]

    # Metadata
    rules_version: str
    calculated_at: datetime


@dataclass
class StateCreditResult:
    """Result of state R&D credit calculation."""
    state_code: str
    state_name: str
    tax_year: int

    # State QRE
    state_qre: Decimal
    state_qre_breakdown: Dict[str, Decimal]

    # Base calculation
    base_method: str
    state_base_amount: Decimal

    # Credit calculation
    credit_rate: Decimal
    credit_type: str
    excess_qre: Decimal
    tentative_credit: Decimal

    # State-specific adjustments
    state_adjustments: Dict[str, Decimal]
    credit_cap: Optional[Decimal]
    credit_after_cap: Decimal

    # Final credit
    final_credit: Decimal

    # Carryforward
    carryforward_years: int
    prior_carryforward: Decimal
    current_year_used: Decimal
    carryforward_generated: Decimal

    # Calculation steps
    steps: List[CalculationStep]

    # Metadata
    rules_version: str
    state_form: str
    calculated_at: datetime


@dataclass
class CreditComparison:
    """Comparison of Regular vs ASC methods."""
    regular_credit: Decimal
    asc_credit: Decimal
    difference: Decimal
    recommended_method: CalculationMethod
    recommendation_reason: str
    factors_considered: List[str]


@dataclass
class FullCalculationResult:
    """Complete calculation result for a study."""
    study_id: UUID
    tax_year: int
    entity_name: str

    # Federal calculations
    federal_regular: Optional[FederalCreditResult]
    federal_asc: Optional[FederalCreditResult]
    federal_comparison: Optional[CreditComparison]
    selected_federal_method: CalculationMethod
    federal_credit: Decimal

    # State calculations
    state_results: Dict[str, StateCreditResult]
    total_state_credits: Decimal

    # Combined totals
    total_credits: Decimal

    # CPA selection
    cpa_method_override: Optional[CalculationMethod]
    cpa_override_reason: Optional[str]

    # Metadata
    rules_version: str
    calculated_at: datetime
    calculated_by: Optional[UUID]


class CalculationEngine:
    """
    Deterministic calculation engine for R&D tax credits.

    All calculations are:
    - Reproducible with same inputs
    - Fully documented with step-by-step audit trail
    - Based on IRC Section 41 and state statutes
    """

    def __init__(self, rules_engine: Optional[RulesEngine] = None):
        self.rules_engine = rules_engine or RulesEngine()
        self.federal_rules = self.rules_engine.get_federal_rules()

    def calculate_full_credit(
        self,
        study_id: UUID,
        tax_year: int,
        entity_name: str,
        qre_data: Dict[str, Decimal],
        base_period_data: Optional[Dict[int, Dict[str, Decimal]]] = None,
        gross_receipts: Optional[Decimal] = None,
        is_controlled_group: bool = False,
        controlled_group_allocation: Decimal = Decimal("100"),
        is_short_year: bool = False,
        short_year_days: int = 365,
        section_280c_election: bool = True,
        states: Optional[List[str]] = None,
        state_qre_allocations: Optional[Dict[str, Dict[str, Decimal]]] = None,
        cpa_method_override: Optional[CalculationMethod] = None
    ) -> FullCalculationResult:
        """
        Calculate complete R&D credit for a study.

        Args:
            study_id: Study identifier
            tax_year: Tax year
            entity_name: Entity name
            qre_data: QRE amounts by category
            base_period_data: Historical QRE and gross receipts
            gross_receipts: Current year gross receipts
            is_controlled_group: Whether part of controlled group
            controlled_group_allocation: % allocated to this entity
            is_short_year: Whether this is a short tax year
            short_year_days: Days in short year
            section_280c_election: Whether to make 280C(c) election
            states: States to calculate credits for
            state_qre_allocations: State-specific QRE allocations
            cpa_method_override: CPA override of method selection

        Returns:
            Complete calculation result
        """
        logger.info(f"Calculating credits for study {study_id}, tax year {tax_year}")

        # Calculate Federal Regular Credit
        federal_regular = self.calculate_regular_credit(
            tax_year=tax_year,
            qre_data=qre_data,
            base_period_data=base_period_data,
            gross_receipts=gross_receipts,
            controlled_group_allocation=controlled_group_allocation,
            is_short_year=is_short_year,
            short_year_days=short_year_days,
            section_280c_election=section_280c_election
        )

        # Calculate Federal ASC
        federal_asc = self.calculate_asc_credit(
            tax_year=tax_year,
            qre_data=qre_data,
            base_period_data=base_period_data,
            controlled_group_allocation=controlled_group_allocation,
            is_short_year=is_short_year,
            short_year_days=short_year_days,
            section_280c_election=section_280c_election
        )

        # Compare methods
        federal_comparison = self._compare_methods(federal_regular, federal_asc)

        # Determine selected method
        if cpa_method_override:
            selected_method = cpa_method_override
        else:
            selected_method = federal_comparison.recommended_method

        federal_credit = (
            federal_regular.final_credit if selected_method == CalculationMethod.REGULAR
            else federal_asc.final_credit
        )

        # Calculate state credits
        state_results = {}
        total_state_credits = Decimal("0")

        if states:
            for state_code in states:
                state_qre = (
                    state_qre_allocations.get(state_code, {})
                    if state_qre_allocations else qre_data
                )
                state_result = self.calculate_state_credit(
                    state_code=state_code,
                    tax_year=tax_year,
                    qre_data=state_qre,
                    federal_qre=qre_data.get("total", Decimal("0")),
                    federal_base_amount=(
                        federal_regular.base_amount if selected_method == CalculationMethod.REGULAR
                        else Decimal("0")
                    )
                )
                if state_result:
                    state_results[state_code] = state_result
                    total_state_credits += state_result.final_credit

        total_credits = federal_credit + total_state_credits

        return FullCalculationResult(
            study_id=study_id,
            tax_year=tax_year,
            entity_name=entity_name,
            federal_regular=federal_regular,
            federal_asc=federal_asc,
            federal_comparison=federal_comparison,
            selected_federal_method=selected_method,
            federal_credit=federal_credit,
            state_results=state_results,
            total_state_credits=total_state_credits,
            total_credits=total_credits,
            cpa_method_override=cpa_method_override,
            cpa_override_reason=None,
            rules_version=self.rules_engine.version,
            calculated_at=datetime.utcnow(),
            calculated_by=None
        )

    def calculate_regular_credit(
        self,
        tax_year: int,
        qre_data: Dict[str, Decimal],
        base_period_data: Optional[Dict[int, Dict[str, Decimal]]] = None,
        gross_receipts: Optional[Decimal] = None,
        controlled_group_allocation: Decimal = Decimal("100"),
        is_short_year: bool = False,
        short_year_days: int = 365,
        section_280c_election: bool = True
    ) -> FederalCreditResult:
        """
        Calculate Federal Regular R&D Credit (IRC §41(a)(1)).

        Formula: 20% × (Current QRE - Base Amount)
        """
        steps = []
        step_num = 0

        # Step 1: Calculate Total QRE
        step_num += 1
        qre_wages = qre_data.get("wages", Decimal("0"))
        qre_supplies = qre_data.get("supplies", Decimal("0"))
        qre_contract = qre_data.get("contract_research", Decimal("0"))
        qre_basic = qre_data.get("basic_research", Decimal("0"))
        total_qre = qre_wages + qre_supplies + qre_contract + qre_basic

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate Total QRE",
            formula="Wages + Supplies + Contract Research + Basic Research",
            inputs={
                "wages": str(qre_wages),
                "supplies": str(qre_supplies),
                "contract_research": str(qre_contract),
                "basic_research": str(qre_basic)
            },
            result=total_qre,
            irc_reference="IRC §41(b)"
        ))

        # Step 2: Calculate Fixed-Base Percentage
        step_num += 1
        fixed_base_percentage = self._calculate_fixed_base_percentage(
            base_period_data, tax_year
        )

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate Fixed-Base Percentage",
            formula="Aggregate QRE for base period ÷ Aggregate Gross Receipts for base period",
            inputs={
                "base_period_data": base_period_data or "Not provided",
                "result_capped": "Maximum 16%"
            },
            result=fixed_base_percentage,
            irc_reference="IRC §41(c)(3)"
        ))

        # Step 3: Calculate Average Annual Gross Receipts (4 prior years)
        step_num += 1
        avg_gross_receipts = self._calculate_average_gross_receipts(
            base_period_data, tax_year, gross_receipts
        )

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate Average Annual Gross Receipts",
            formula="Sum of 4 prior years gross receipts ÷ 4",
            inputs={
                "gross_receipts_used": str(avg_gross_receipts)
            },
            result=avg_gross_receipts,
            irc_reference="IRC §41(c)(1)(B)"
        ))

        # Step 4: Calculate Base Amount
        step_num += 1
        base_amount_calc = (fixed_base_percentage * avg_gross_receipts).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Apply minimum base amount (50% of current QRE)
        min_base = (total_qre * Decimal("0.50")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        base_amount = max(base_amount_calc, min_base)

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate Base Amount",
            formula="MAX(Fixed-Base % × Avg Gross Receipts, 50% of Current QRE)",
            inputs={
                "fixed_base_percentage": str(fixed_base_percentage),
                "avg_gross_receipts": str(avg_gross_receipts),
                "calculated_base": str(base_amount_calc),
                "minimum_base": str(min_base)
            },
            result=base_amount,
            irc_reference="IRC §41(c)(1)",
            notes="Base amount cannot be less than 50% of current year QRE"
        ))

        # Step 5: Calculate Excess QRE
        step_num += 1
        excess_qre = max(total_qre - base_amount, Decimal("0"))

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate Excess QRE",
            formula="MAX(Total QRE - Base Amount, 0)",
            inputs={
                "total_qre": str(total_qre),
                "base_amount": str(base_amount)
            },
            result=excess_qre,
            irc_reference="IRC §41(a)(1)"
        ))

        # Step 6: Calculate Tentative Credit
        step_num += 1
        credit_rate = Decimal(str(self.federal_rules.REGULAR_CREDIT_RATE))
        tentative_credit = (excess_qre * credit_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate Tentative Credit",
            formula="Excess QRE × 20%",
            inputs={
                "excess_qre": str(excess_qre),
                "credit_rate": str(credit_rate)
            },
            result=tentative_credit,
            irc_reference="IRC §41(a)(1)"
        ))

        # Step 7: Apply Section 280C Reduction (if elected)
        step_num += 1
        if section_280c_election:
            # Reduced credit = Credit × (1 - 21%)
            reduction_rate = Decimal(str(self.federal_rules.SECTION_280C_REDUCTION_RATE))
            section_280c_reduction = (tentative_credit * reduction_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            credit_after_280c = tentative_credit - section_280c_reduction
        else:
            section_280c_reduction = Decimal("0")
            credit_after_280c = tentative_credit

        steps.append(CalculationStep(
            step_number=step_num,
            description="Apply Section 280C(c) Election",
            formula="Tentative Credit × (1 - Corporate Tax Rate)" if section_280c_election else "No election",
            inputs={
                "tentative_credit": str(tentative_credit),
                "election_made": section_280c_election,
                "reduction_rate": str(self.federal_rules.SECTION_280C_REDUCTION_RATE) if section_280c_election else "N/A"
            },
            result=credit_after_280c,
            irc_reference="IRC §280C(c)",
            notes="Election reduces credit but allows full QRE deduction"
        ))

        # Step 8: Apply Controlled Group Allocation
        step_num += 1
        allocation_pct = controlled_group_allocation / Decimal("100")
        allocated_credit = (credit_after_280c * allocation_pct).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        steps.append(CalculationStep(
            step_number=step_num,
            description="Apply Controlled Group Allocation",
            formula="Credit after 280C × Allocation %",
            inputs={
                "credit_after_280c": str(credit_after_280c),
                "allocation_percentage": str(controlled_group_allocation)
            },
            result=allocated_credit,
            irc_reference="IRC §41(f)(1)"
        ))

        # Step 9: Short Year Adjustment (if applicable)
        step_num += 1
        if is_short_year and short_year_days < 365:
            short_year_factor = Decimal(str(short_year_days)) / Decimal("365")
            final_credit = (allocated_credit * short_year_factor).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            short_year_note = f"Adjusted for {short_year_days} day tax year"
        else:
            final_credit = allocated_credit
            short_year_note = "Full year - no adjustment"

        steps.append(CalculationStep(
            step_number=step_num,
            description="Short Year Adjustment",
            formula="Allocated Credit × (Days in Year / 365)" if is_short_year else "No adjustment",
            inputs={
                "allocated_credit": str(allocated_credit),
                "days_in_year": short_year_days,
                "is_short_year": is_short_year
            },
            result=final_credit,
            irc_reference="IRC §41(h)",
            notes=short_year_note
        ))

        # Build base period data object
        bp_data = None
        if base_period_data:
            bp_data = BasePeriodData(
                years=base_period_data,
                fixed_base_percentage=fixed_base_percentage,
                average_annual_gross_receipts=avg_gross_receipts
            )

        return FederalCreditResult(
            method=CalculationMethod.REGULAR,
            tax_year=tax_year,
            qre_wages=qre_wages,
            qre_supplies=qre_supplies,
            qre_contract=qre_contract,
            qre_basic_research=qre_basic,
            total_qre=total_qre,
            base_period_data=bp_data,
            base_amount=base_amount,
            credit_rate=credit_rate,
            excess_qre=excess_qre,
            tentative_credit=tentative_credit,
            section_280c_election=section_280c_election,
            section_280c_reduction=section_280c_reduction,
            controlled_group_allocation=controlled_group_allocation,
            allocated_credit=allocated_credit,
            final_credit=final_credit,
            is_qsb=False,
            payroll_tax_offset_eligible=Decimal("0"),
            payroll_tax_offset_claimed=Decimal("0"),
            steps=steps,
            rules_version=self.rules_engine.version,
            calculated_at=datetime.utcnow()
        )

    def calculate_asc_credit(
        self,
        tax_year: int,
        qre_data: Dict[str, Decimal],
        base_period_data: Optional[Dict[int, Dict[str, Decimal]]] = None,
        controlled_group_allocation: Decimal = Decimal("100"),
        is_short_year: bool = False,
        short_year_days: int = 365,
        section_280c_election: bool = True
    ) -> FederalCreditResult:
        """
        Calculate Federal Alternative Simplified Credit (IRC §41(c)(4)).

        Formula: 14% × (Current QRE - 50% of Average QRE for 3 prior years)
        """
        steps = []
        step_num = 0

        # Step 1: Calculate Total QRE
        step_num += 1
        qre_wages = qre_data.get("wages", Decimal("0"))
        qre_supplies = qre_data.get("supplies", Decimal("0"))
        qre_contract = qre_data.get("contract_research", Decimal("0"))
        qre_basic = qre_data.get("basic_research", Decimal("0"))
        total_qre = qre_wages + qre_supplies + qre_contract + qre_basic

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate Total QRE",
            formula="Wages + Supplies + Contract Research + Basic Research",
            inputs={
                "wages": str(qre_wages),
                "supplies": str(qre_supplies),
                "contract_research": str(qre_contract),
                "basic_research": str(qre_basic)
            },
            result=total_qre,
            irc_reference="IRC §41(b)"
        ))

        # Step 2: Calculate Average QRE for 3 Prior Years
        step_num += 1
        prior_years_qre = self._get_prior_years_qre(base_period_data, tax_year, years=3)
        avg_prior_qre = (
            sum(prior_years_qre.values()) / Decimal("3")
            if prior_years_qre else Decimal("0")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate Average QRE for 3 Prior Years",
            formula="(QRE Year-1 + QRE Year-2 + QRE Year-3) ÷ 3",
            inputs={
                "prior_years": {str(y): str(q) for y, q in prior_years_qre.items()}
            },
            result=avg_prior_qre,
            irc_reference="IRC §41(c)(4)(A)(ii)"
        ))

        # Step 3: Calculate Base Amount (50% of average)
        step_num += 1
        base_amount = (avg_prior_qre * Decimal("0.50")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate ASC Base Amount",
            formula="50% × Average Prior Year QRE",
            inputs={
                "avg_prior_qre": str(avg_prior_qre)
            },
            result=base_amount,
            irc_reference="IRC §41(c)(4)(A)(i)"
        ))

        # Step 4: Calculate Excess QRE
        step_num += 1
        excess_qre = max(total_qre - base_amount, Decimal("0"))

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate Excess QRE",
            formula="MAX(Total QRE - Base Amount, 0)",
            inputs={
                "total_qre": str(total_qre),
                "base_amount": str(base_amount)
            },
            result=excess_qre,
            irc_reference="IRC §41(c)(4)(A)"
        ))

        # Step 5: Calculate Tentative Credit
        step_num += 1
        credit_rate = Decimal(str(self.federal_rules.ASC_CREDIT_RATE))
        tentative_credit = (excess_qre * credit_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Special case: If no QRE in any of 3 prior years, use 6% rate
        if avg_prior_qre == 0:
            credit_rate = Decimal("0.06")
            tentative_credit = (total_qre * credit_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate Tentative Credit",
            formula="Excess QRE × 14%" if avg_prior_qre > 0 else "Total QRE × 6%",
            inputs={
                "excess_qre": str(excess_qre) if avg_prior_qre > 0 else str(total_qre),
                "credit_rate": str(credit_rate)
            },
            result=tentative_credit,
            irc_reference="IRC §41(c)(4)(B)",
            notes="6% rate applies if no QRE in any of 3 prior years"
        ))

        # Step 6: Apply Section 280C Reduction
        step_num += 1
        if section_280c_election:
            reduction_rate = Decimal(str(self.federal_rules.SECTION_280C_REDUCTION_RATE))
            section_280c_reduction = (tentative_credit * reduction_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            credit_after_280c = tentative_credit - section_280c_reduction
        else:
            section_280c_reduction = Decimal("0")
            credit_after_280c = tentative_credit

        steps.append(CalculationStep(
            step_number=step_num,
            description="Apply Section 280C(c) Election",
            formula="Tentative Credit × (1 - Corporate Tax Rate)" if section_280c_election else "No election",
            inputs={
                "tentative_credit": str(tentative_credit),
                "election_made": section_280c_election
            },
            result=credit_after_280c,
            irc_reference="IRC §280C(c)"
        ))

        # Step 7: Apply Controlled Group Allocation
        step_num += 1
        allocation_pct = controlled_group_allocation / Decimal("100")
        allocated_credit = (credit_after_280c * allocation_pct).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        steps.append(CalculationStep(
            step_number=step_num,
            description="Apply Controlled Group Allocation",
            formula="Credit after 280C × Allocation %",
            inputs={
                "credit_after_280c": str(credit_after_280c),
                "allocation_percentage": str(controlled_group_allocation)
            },
            result=allocated_credit,
            irc_reference="IRC §41(f)(1)"
        ))

        # Step 8: Short Year Adjustment
        step_num += 1
        if is_short_year and short_year_days < 365:
            short_year_factor = Decimal(str(short_year_days)) / Decimal("365")
            final_credit = (allocated_credit * short_year_factor).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            final_credit = allocated_credit

        steps.append(CalculationStep(
            step_number=step_num,
            description="Short Year Adjustment",
            formula="Allocated Credit × (Days in Year / 365)" if is_short_year else "No adjustment",
            inputs={
                "allocated_credit": str(allocated_credit),
                "days_in_year": short_year_days
            },
            result=final_credit,
            irc_reference="IRC §41(h)"
        ))

        return FederalCreditResult(
            method=CalculationMethod.ASC,
            tax_year=tax_year,
            qre_wages=qre_wages,
            qre_supplies=qre_supplies,
            qre_contract=qre_contract,
            qre_basic_research=qre_basic,
            total_qre=total_qre,
            base_period_data=None,
            base_amount=base_amount,
            credit_rate=credit_rate,
            excess_qre=excess_qre,
            tentative_credit=tentative_credit,
            section_280c_election=section_280c_election,
            section_280c_reduction=section_280c_reduction,
            controlled_group_allocation=controlled_group_allocation,
            allocated_credit=allocated_credit,
            final_credit=final_credit,
            is_qsb=False,
            payroll_tax_offset_eligible=Decimal("0"),
            payroll_tax_offset_claimed=Decimal("0"),
            steps=steps,
            rules_version=self.rules_engine.version,
            calculated_at=datetime.utcnow()
        )

    def calculate_state_credit(
        self,
        state_code: str,
        tax_year: int,
        qre_data: Dict[str, Decimal],
        federal_qre: Decimal,
        federal_base_amount: Decimal = Decimal("0")
    ) -> Optional[StateCreditResult]:
        """
        Calculate state R&D credit based on state-specific rules.
        """
        state_rules = self.rules_engine.get_state_rules(state_code)

        if not state_rules or not state_rules.has_rd_credit:
            return None

        steps = []
        step_num = 0

        # Calculate state QRE
        step_num += 1
        state_qre_total = sum(qre_data.values())

        steps.append(CalculationStep(
            step_number=step_num,
            description=f"Calculate {state_code} QRE",
            formula="Sum of state-allocated QRE",
            inputs={"qre_breakdown": {k: str(v) for k, v in qre_data.items()}},
            result=state_qre_total,
            irc_reference=state_rules.statute_citation
        ))

        # Calculate base amount based on state method
        step_num += 1
        if state_rules.base_method == "federal":
            state_base = federal_base_amount
            base_description = "Use Federal base amount"
        elif state_rules.base_method == "non_incremental":
            state_base = Decimal("0")
            base_description = "Non-incremental credit (no base)"
        elif state_rules.base_method == "pa_specific":
            # PA uses: Greater of (50% of current QRE) or (average of prior 4 years QRE)
            # Since we don't have prior year data readily available, use 50% minimum base
            minimum_base = (state_qre_total * Decimal("0.50")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            # TODO: When prior year data is available, calculate avg and use greater of
            state_base = minimum_base
            base_description = "PA base: Greater of 50% current QRE or avg prior 4 years (using 50% minimum)"
        else:
            # State-specific calculation
            state_base = (state_qre_total * Decimal(str(state_rules.base_percentage))).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            base_description = f"State-specific base ({state_rules.base_percentage}%)"

        steps.append(CalculationStep(
            step_number=step_num,
            description=f"Calculate {state_code} Base Amount",
            formula=base_description,
            inputs={"base_method": state_rules.base_method},
            result=state_base,
            irc_reference=state_rules.statute_citation
        ))

        # Calculate excess QRE
        step_num += 1
        excess_qre = max(state_qre_total - state_base, Decimal("0"))

        steps.append(CalculationStep(
            step_number=step_num,
            description="Calculate State Excess QRE",
            formula="MAX(State QRE - State Base, 0)",
            inputs={
                "state_qre": str(state_qre_total),
                "state_base": str(state_base)
            },
            result=excess_qre,
            irc_reference=state_rules.statute_citation
        ))

        # Calculate tentative credit
        step_num += 1
        credit_rate = Decimal(str(state_rules.credit_rate))

        if state_rules.credit_type == "non_incremental":
            tentative_credit = (state_qre_total * credit_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            tentative_credit = (excess_qre * credit_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        steps.append(CalculationStep(
            step_number=step_num,
            description=f"Calculate {state_code} Tentative Credit",
            formula=f"QRE × {credit_rate * 100}%",
            inputs={
                "qre_base": str(state_qre_total if state_rules.credit_type == "non_incremental" else excess_qre),
                "credit_rate": str(credit_rate)
            },
            result=tentative_credit,
            irc_reference=state_rules.statute_citation
        ))

        # Apply cap if applicable
        step_num += 1
        credit_after_cap = tentative_credit
        if state_rules.credit_cap:
            credit_after_cap = min(tentative_credit, state_rules.credit_cap)

        steps.append(CalculationStep(
            step_number=step_num,
            description="Apply Credit Cap",
            formula="MIN(Tentative Credit, Cap)" if state_rules.credit_cap else "No cap",
            inputs={
                "tentative_credit": str(tentative_credit),
                "cap": str(state_rules.credit_cap) if state_rules.credit_cap else "None"
            },
            result=credit_after_cap,
            irc_reference=state_rules.statute_citation
        ))

        # Apply PA program proration if applicable
        final_credit = credit_after_cap
        state_adjustments = {}
        if state_rules.base_method == "pa_specific" and state_rules.qre_modifications:
            proration_rate = state_rules.qre_modifications.get("program_proration_rate", 1.0)
            if proration_rate and proration_rate < 1.0:
                step_num += 1
                prorated_credit = (credit_after_cap * Decimal(str(proration_rate))).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                steps.append(CalculationStep(
                    step_number=step_num,
                    description="Apply PA Program Proration",
                    formula=f"Credit × {proration_rate * 100:.1f}% (program cap proration)",
                    inputs={
                        "credit_before_proration": str(credit_after_cap),
                        "proration_rate": str(proration_rate),
                        "program_cap": str(state_rules.qre_modifications.get("program_cap", "60000000")),
                        "note": "PA program cap of $60M is prorated among all applicants"
                    },
                    result=prorated_credit,
                    irc_reference=state_rules.statute_citation,
                    notes="Estimated based on historical proration rate; actual award determined by PA DOR"
                ))
                final_credit = prorated_credit
                state_adjustments["program_proration"] = {
                    "rate": proration_rate,
                    "tentative_credit": str(credit_after_cap),
                    "prorated_credit": str(prorated_credit)
                }

        return StateCreditResult(
            state_code=state_code,
            state_name=state_rules.state_name,
            tax_year=tax_year,
            state_qre=state_qre_total,
            state_qre_breakdown={k: v for k, v in qre_data.items()},
            base_method=state_rules.base_method,
            state_base_amount=state_base,
            credit_rate=credit_rate,
            credit_type=state_rules.credit_type,
            excess_qre=excess_qre,
            tentative_credit=tentative_credit,
            state_adjustments=state_adjustments,
            credit_cap=state_rules.credit_cap,
            credit_after_cap=credit_after_cap,
            final_credit=final_credit,
            carryforward_years=state_rules.carryforward_years,
            prior_carryforward=Decimal("0"),
            current_year_used=Decimal("0"),
            carryforward_generated=Decimal("0"),
            steps=steps,
            rules_version=self.rules_engine.version,
            state_form=state_rules.state_form_number,
            calculated_at=datetime.utcnow()
        )

    def _calculate_fixed_base_percentage(
        self,
        base_period_data: Optional[Dict[int, Dict[str, Decimal]]],
        tax_year: int
    ) -> Decimal:
        """Calculate fixed-base percentage for Regular credit."""
        if not base_period_data:
            # Use minimum floor
            return Decimal(str(self.federal_rules.MIN_BASE_AMOUNT_PERCENTAGE))

        # Calculate from base period (1984-1988 for established taxpayers)
        total_qre = Decimal("0")
        total_gross_receipts = Decimal("0")

        for year, data in base_period_data.items():
            total_qre += Decimal(str(data.get("qre", 0)))
            total_gross_receipts += Decimal(str(data.get("gross_receipts", 0)))

        if total_gross_receipts == 0:
            return Decimal(str(self.federal_rules.MIN_BASE_AMOUNT_PERCENTAGE))

        fixed_base = (total_qre / total_gross_receipts).quantize(
            Decimal("0.0001"), rounding=ROUND_DOWN
        )

        # Cap at 16%
        fixed_base = min(fixed_base, Decimal("0.16"))

        # Floor at 3%
        fixed_base = max(fixed_base, Decimal(str(self.federal_rules.MIN_BASE_AMOUNT_PERCENTAGE)))

        return fixed_base

    def _calculate_average_gross_receipts(
        self,
        base_period_data: Optional[Dict[int, Dict[str, Decimal]]],
        tax_year: int,
        current_gross_receipts: Optional[Decimal]
    ) -> Decimal:
        """Calculate average annual gross receipts for 4 prior years."""
        if not base_period_data and not current_gross_receipts:
            return Decimal("0")

        prior_years = [tax_year - i for i in range(1, 5)]
        total_receipts = Decimal("0")
        count = 0

        if base_period_data:
            for year in prior_years:
                if year in base_period_data:
                    total_receipts += Decimal(str(base_period_data[year].get("gross_receipts", 0)))
                    count += 1

        if count == 0:
            return current_gross_receipts or Decimal("0")

        return (total_receipts / Decimal(str(count))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def _get_prior_years_qre(
        self,
        base_period_data: Optional[Dict[int, Dict[str, Decimal]]],
        tax_year: int,
        years: int = 3
    ) -> Dict[int, Decimal]:
        """Get QRE for prior years."""
        result = {}

        if not base_period_data:
            return result

        for i in range(1, years + 1):
            prior_year = tax_year - i
            if prior_year in base_period_data:
                result[prior_year] = Decimal(str(base_period_data[prior_year].get("qre", 0)))
            else:
                result[prior_year] = Decimal("0")

        return result

    def _compare_methods(
        self,
        regular: FederalCreditResult,
        asc: FederalCreditResult
    ) -> CreditComparison:
        """Compare Regular and ASC methods to recommend optimal choice."""
        difference = regular.final_credit - asc.final_credit

        factors = []

        # Compare credits
        if regular.final_credit > asc.final_credit:
            recommended = CalculationMethod.REGULAR
            factors.append(f"Regular credit (${regular.final_credit:,.2f}) exceeds ASC (${asc.final_credit:,.2f})")
        elif asc.final_credit > regular.final_credit:
            recommended = CalculationMethod.ASC
            factors.append(f"ASC (${asc.final_credit:,.2f}) exceeds Regular credit (${regular.final_credit:,.2f})")
        else:
            # Equal - prefer ASC for simplicity
            recommended = CalculationMethod.ASC
            factors.append("Credits are equal - ASC preferred for simplicity")

        # Consider base period data availability
        if regular.base_period_data is None:
            factors.append("Limited base period data may favor ASC election")
            if abs(difference) < regular.final_credit * Decimal("0.10"):
                recommended = CalculationMethod.ASC

        # Consider consistency
        factors.append("ASC election is irrevocable once made")

        reason = f"{'Regular' if recommended == CalculationMethod.REGULAR else 'ASC'} method recommended. " + \
                 "; ".join(factors[:2])

        return CreditComparison(
            regular_credit=regular.final_credit,
            asc_credit=asc.final_credit,
            difference=difference,
            recommended_method=recommended,
            recommendation_reason=reason,
            factors_considered=factors
        )

    def generate_calculation_summary(
        self,
        result: FullCalculationResult
    ) -> Dict[str, Any]:
        """Generate summary for tax preparer."""
        return {
            "study_id": str(result.study_id),
            "tax_year": result.tax_year,
            "entity_name": result.entity_name,
            "federal_credit": {
                "method": result.selected_federal_method.value,
                "credit_amount": str(result.federal_credit),
                "total_qre": str(result.federal_regular.total_qre if result.federal_regular else Decimal("0")),
                "regular_credit": str(result.federal_regular.final_credit if result.federal_regular else Decimal("0")),
                "asc_credit": str(result.federal_asc.final_credit if result.federal_asc else Decimal("0"))
            },
            "state_credits": {
                state: str(credit.final_credit)
                for state, credit in result.state_results.items()
            },
            "total_state_credits": str(result.total_state_credits),
            "total_credits": str(result.total_credits),
            "calculation_date": result.calculated_at.isoformat(),
            "rules_version": result.rules_version
        }
