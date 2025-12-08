"""
QRE (Qualified Research Expense) Engine

Computes wages, supplies, and contract research expenses
with evidence-based qualification and allocation.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID
from datetime import date, datetime
from enum import Enum

from .rules_engine import RulesEngine

logger = logging.getLogger(__name__)


class QREClassification(str, Enum):
    """QRE classification categories."""
    WAGES = "wages"
    SUPPLIES = "supplies"
    CONTRACT_RESEARCH = "contract_research"
    BASIC_RESEARCH = "basic_research"
    ENERGY_RESEARCH = "energy_research"


@dataclass
class WageAllocation:
    """Wage allocation result for an employee."""
    employee_id: UUID
    employee_name: str
    total_wages: Decimal
    qualified_percentage: Decimal
    qualified_wages: Decimal
    project_allocations: Dict[UUID, Decimal]  # project_id -> amount
    source: str  # timesheet, estimate, interview
    confidence: float
    evidence_ids: List[UUID]
    notes: str


@dataclass
class SupplyExpense:
    """Supply expense QRE record."""
    id: UUID
    description: str
    vendor: str
    gl_account: str
    gross_amount: Decimal
    qualified_percentage: Decimal
    qualified_amount: Decimal
    project_id: Optional[UUID]
    evidence_id: Optional[UUID]
    classification_reason: str
    confidence: float


@dataclass
class ContractResearchExpense:
    """Contract research expense QRE record."""
    id: UUID
    contractor_name: str
    contractor_ein: Optional[str]
    contract_description: str
    gross_amount: Decimal
    applicable_percentage: Decimal  # 65% or 75%
    qualified_amount: Decimal
    is_qualified_research_org: bool
    project_id: Optional[UUID]
    evidence_ids: List[UUID]
    notes: str


@dataclass
class QRESummary:
    """Summary of all QREs for a study."""
    study_id: UUID
    tax_year: int

    # Category totals
    total_wages: Decimal
    total_supplies: Decimal
    total_contract_research: Decimal
    total_basic_research: Decimal
    total_energy_research: Decimal
    total_qre: Decimal

    # Breakdown
    wage_allocations: List[WageAllocation]
    supply_expenses: List[SupplyExpense]
    contract_expenses: List[ContractResearchExpense]

    # State allocations
    state_allocations: Dict[str, Dict[str, Decimal]]

    # Confidence and audit
    overall_confidence: float
    evidence_coverage: float  # % of QRE backed by evidence
    risk_flags: List[Dict[str, Any]]

    # Audit trail
    calculation_timestamp: datetime
    rules_version: str


class QREEngine:
    """
    Engine for calculating Qualified Research Expenses.

    Handles:
    - Wage QRE calculation with time allocation
    - Supply expense qualification
    - Contract research expense calculation (65%/75%)
    - State-specific QRE allocations
    """

    def __init__(self, rules_engine: Optional[RulesEngine] = None):
        self.rules_engine = rules_engine or RulesEngine()
        self.qre_rules = self.rules_engine.get_qre_rules()

    def calculate_study_qres(
        self,
        study_id: UUID,
        tax_year: int,
        employees: List[Dict[str, Any]],
        projects: List[Dict[str, Any]],
        expenses: List[Dict[str, Any]],
        time_allocations: List[Dict[str, Any]],
        contracts: List[Dict[str, Any]],
        states: Optional[List[str]] = None
    ) -> QRESummary:
        """
        Calculate all QREs for a study.

        Args:
            study_id: Study identifier
            tax_year: Tax year
            employees: Employee data with wages
            projects: Qualified projects
            expenses: Expense data (supplies)
            time_allocations: Time tracking/allocation data
            contracts: Contract research agreements
            states: States for allocation

        Returns:
            Complete QRE summary
        """
        logger.info(f"Calculating QREs for study {study_id}, tax year {tax_year}")

        # Calculate wages
        wage_allocations = self._calculate_wage_qres(
            employees, projects, time_allocations
        )

        # Calculate supplies
        supply_expenses = self._calculate_supply_qres(
            expenses, projects
        )

        # Calculate contract research
        contract_expenses = self._calculate_contract_qres(
            contracts, projects
        )

        # Calculate totals
        total_wages = sum(w.qualified_wages for w in wage_allocations)
        total_supplies = sum(s.qualified_amount for s in supply_expenses)
        total_contract = sum(c.qualified_amount for c in contract_expenses)
        total_qre = total_wages + total_supplies + total_contract

        # Calculate state allocations
        state_allocations = {}
        if states:
            state_allocations = self._calculate_state_allocations(
                states,
                wage_allocations,
                supply_expenses,
                contract_expenses
            )

        # Calculate confidence metrics
        overall_confidence = self._calculate_overall_confidence(
            wage_allocations,
            supply_expenses,
            contract_expenses
        )

        evidence_coverage = self._calculate_evidence_coverage(
            wage_allocations,
            supply_expenses,
            contract_expenses
        )

        # Generate risk flags
        risk_flags = self._generate_qre_risk_flags(
            wage_allocations,
            supply_expenses,
            contract_expenses,
            total_qre
        )

        return QRESummary(
            study_id=study_id,
            tax_year=tax_year,
            total_wages=total_wages,
            total_supplies=total_supplies,
            total_contract_research=total_contract,
            total_basic_research=Decimal("0"),  # Calculated separately if applicable
            total_energy_research=Decimal("0"),
            total_qre=total_qre,
            wage_allocations=wage_allocations,
            supply_expenses=supply_expenses,
            contract_expenses=contract_expenses,
            state_allocations=state_allocations,
            overall_confidence=overall_confidence,
            evidence_coverage=evidence_coverage,
            risk_flags=risk_flags,
            calculation_timestamp=datetime.utcnow(),
            rules_version=self.rules_engine.version
        )

    def _calculate_wage_qres(
        self,
        employees: List[Dict[str, Any]],
        projects: List[Dict[str, Any]],
        time_allocations: List[Dict[str, Any]]
    ) -> List[WageAllocation]:
        """
        Calculate wage QREs for all employees.

        Only W-2 wages qualify (IRC §41(b)(2)(A)).
        Stock-based compensation generally excluded.
        """
        wage_allocations = []
        qualified_project_ids = {p["id"] for p in projects if p.get("qualified", True)}

        for employee in employees:
            employee_id = employee.get("id")
            employee_name = employee.get("name", "Unknown")

            # Get W-2 wages (exclude stock compensation)
            w2_wages = Decimal(str(employee.get("w2_wages", 0)))
            stock_comp = Decimal(str(employee.get("stock_compensation", 0)))
            total_wages = Decimal(str(employee.get("total_wages", 0)))

            # Qualified wages = W-2 wages (excluding stock comp if included)
            base_qualified_wages = w2_wages

            # Get time allocation for this employee
            employee_allocations = [
                ta for ta in time_allocations
                if ta.get("employee_id") == employee_id
            ]

            # Calculate qualified percentage
            if employee_allocations:
                # Sum time on qualified projects
                total_time = sum(
                    ta.get("hours", 0) or ta.get("percentage", 0)
                    for ta in employee_allocations
                )
                qualified_time = sum(
                    ta.get("hours", 0) or ta.get("percentage", 0)
                    for ta in employee_allocations
                    if ta.get("project_id") in qualified_project_ids
                )

                if total_time > 0:
                    qualified_percentage = Decimal(str(qualified_time / total_time * 100))
                else:
                    qualified_percentage = Decimal(str(employee.get("qualified_time_percentage", 0)))
                source = "timesheet"
            else:
                # Use estimated percentage
                qualified_percentage = Decimal(str(employee.get("qualified_time_percentage", 0)))
                source = employee.get("qualified_time_source", "estimate")

            # Calculate qualified wages
            # IRS Rule: If employee spends 80%+ of time on qualified R&D, 100% of wages are QRE
            # This is known as the "substantially all" rule per IRC §41(b)(2)(B)
            if qualified_percentage >= Decimal("80"):
                qualified_wages = base_qualified_wages
                source = source + " (80%+ rule applied)"
            else:
                qualified_wages = (base_qualified_wages * qualified_percentage / 100).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

            # Project-level allocation
            project_allocations = {}
            if employee_allocations and qualified_time > 0:
                for ta in employee_allocations:
                    project_id = ta.get("project_id")
                    if project_id in qualified_project_ids:
                        allocation_pct = ta.get("hours", 0) or ta.get("percentage", 0)
                        project_amount = (qualified_wages * Decimal(str(allocation_pct / qualified_time))).quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                        project_allocations[project_id] = project_amount

            # Determine confidence
            confidence = self._calculate_wage_confidence(
                source,
                len(employee_allocations),
                employee.get("has_timesheets", False)
            )

            wage_allocations.append(WageAllocation(
                employee_id=employee_id,
                employee_name=employee_name,
                total_wages=base_qualified_wages,
                qualified_percentage=qualified_percentage,
                qualified_wages=qualified_wages,
                project_allocations=project_allocations,
                source=source,
                confidence=confidence,
                evidence_ids=employee.get("evidence_ids", []),
                notes=self._generate_wage_notes(employee, source, qualified_percentage)
            ))

        return wage_allocations

    def _calculate_supply_qres(
        self,
        expenses: List[Dict[str, Any]],
        projects: List[Dict[str, Any]]
    ) -> List[SupplyExpense]:
        """
        Calculate supply QREs.

        Supplies must be:
        - Tangible property (not land or depreciable property)
        - Used in conduct of qualified research
        - Consumed in research activities
        """
        supply_expenses = []
        qualified_project_ids = {p["id"] for p in projects if p.get("qualified", True)}

        # GL accounts typically associated with supplies
        supply_gl_patterns = [
            "6", "7",  # Cost of goods, operating expenses
            "supplies", "materials", "consumables"
        ]

        # Excluded categories
        excluded_categories = [
            "capital", "equipment", "depreciation", "land", "building",
            "overhead", "administrative", "rent", "utilities"
        ]

        for expense in expenses:
            expense_id = expense.get("id")
            description = expense.get("description", "").lower()
            gl_account = expense.get("gl_account", "")
            gross_amount = Decimal(str(expense.get("amount", 0)))

            # Check if this is a supply expense
            is_supply = self._is_supply_expense(
                description,
                gl_account,
                expense.get("category", "")
            )

            if not is_supply:
                continue

            # Check for exclusions
            is_excluded = any(excl in description for excl in excluded_categories)
            if is_excluded:
                continue

            # Check project association
            project_id = expense.get("project_id")
            if project_id and project_id not in qualified_project_ids:
                continue

            # Calculate qualified percentage
            qualified_percentage = Decimal(str(expense.get("qualified_percentage", 100)))

            # Calculate qualified amount
            qualified_amount = (gross_amount * qualified_percentage / 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            # Determine confidence
            confidence = self._calculate_supply_confidence(
                expense.get("has_documentation", False),
                project_id is not None,
                expense.get("ai_classification_confidence", 0.5)
            )

            supply_expenses.append(SupplyExpense(
                id=expense_id,
                description=expense.get("description", ""),
                vendor=expense.get("vendor", ""),
                gl_account=gl_account,
                gross_amount=gross_amount,
                qualified_percentage=qualified_percentage,
                qualified_amount=qualified_amount,
                project_id=project_id,
                evidence_id=expense.get("evidence_id"),
                classification_reason=self._generate_supply_classification_reason(expense),
                confidence=confidence
            ))

        return supply_expenses

    def _calculate_contract_qres(
        self,
        contracts: List[Dict[str, Any]],
        projects: List[Dict[str, Any]]
    ) -> List[ContractResearchExpense]:
        """
        Calculate contract research QREs.

        - 65% of amounts paid for qualified research (standard)
        - 75% if paid to qualified research organization
        - Research must be performed in US
        """
        contract_expenses = []
        qualified_project_ids = {p["id"] for p in projects if p.get("qualified", True)}

        for contract in contracts:
            contract_id = contract.get("id")
            contractor_name = contract.get("contractor_name", "")
            gross_amount = Decimal(str(contract.get("amount", 0)))

            # Check project association
            project_id = contract.get("project_id")
            if project_id and project_id not in qualified_project_ids:
                continue

            # Check if performed in US
            if contract.get("performed_outside_us", False):
                continue

            # Determine applicable percentage (65% or 75%)
            is_qualified_org = contract.get("is_qualified_research_org", False)
            applicable_percentage = Decimal(
                str(self.rules_engine.get_contract_research_percentage(is_qualified_org))
            )

            # Calculate qualified amount
            qualified_amount = (gross_amount * applicable_percentage).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            contract_expenses.append(ContractResearchExpense(
                id=contract_id,
                contractor_name=contractor_name,
                contractor_ein=contract.get("contractor_ein"),
                contract_description=contract.get("description", ""),
                gross_amount=gross_amount,
                applicable_percentage=applicable_percentage,
                qualified_amount=qualified_amount,
                is_qualified_research_org=is_qualified_org,
                project_id=project_id,
                evidence_ids=contract.get("evidence_ids", []),
                notes=f"Contract research at {applicable_percentage * 100}% rate"
            ))

        return contract_expenses

    def _calculate_state_allocations(
        self,
        states: List[str],
        wage_allocations: List[WageAllocation],
        supply_expenses: List[SupplyExpense],
        contract_expenses: List[ContractResearchExpense]
    ) -> Dict[str, Dict[str, Decimal]]:
        """Calculate QRE allocations by state."""
        allocations = {}

        for state_code in states:
            state_rules = self.rules_engine.get_state_rules(state_code)
            if not state_rules or not state_rules.has_rd_credit:
                continue

            # For simplicity, allocate based on presence
            # In production, this would use actual state-specific allocation factors
            state_wages = sum(w.qualified_wages for w in wage_allocations)
            state_supplies = sum(s.qualified_amount for s in supply_expenses)
            state_contract = sum(c.qualified_amount for c in contract_expenses)

            allocations[state_code] = {
                "wages": state_wages,
                "supplies": state_supplies,
                "contract_research": state_contract,
                "total": state_wages + state_supplies + state_contract
            }

        return allocations

    def _is_supply_expense(
        self,
        description: str,
        gl_account: str,
        category: str
    ) -> bool:
        """Determine if an expense qualifies as a supply."""
        supply_indicators = [
            "material", "supply", "supplies", "consumable", "component",
            "raw material", "prototype material", "test material",
            "chemical", "reagent", "sample", "specimen"
        ]

        description_lower = description.lower()
        category_lower = category.lower()

        # Check description
        if any(ind in description_lower for ind in supply_indicators):
            return True

        # Check category
        if any(ind in category_lower for ind in supply_indicators):
            return True

        # Check GL account patterns (typically 6xxx-7xxx range)
        if gl_account and gl_account[0] in ["6", "7"]:
            # Further validation would be needed based on chart of accounts
            return True

        return False

    def _calculate_wage_confidence(
        self,
        source: str,
        allocation_count: int,
        has_timesheets: bool
    ) -> float:
        """Calculate confidence score for wage allocation."""
        base_confidence = {
            "timesheet": 0.90,
            "estimate": 0.60,
            "interview": 0.70,
            "ai_inference": 0.50
        }

        confidence = base_confidence.get(source, 0.50)

        if has_timesheets:
            confidence = min(confidence + 0.10, 0.95)

        if allocation_count > 3:
            confidence = min(confidence + 0.05, 0.95)

        return confidence

    def _calculate_supply_confidence(
        self,
        has_documentation: bool,
        has_project: bool,
        ai_confidence: float
    ) -> float:
        """Calculate confidence score for supply classification."""
        confidence = 0.50

        if has_documentation:
            confidence += 0.25

        if has_project:
            confidence += 0.15

        confidence = max(confidence, ai_confidence)

        return min(confidence, 0.95)

    def _generate_wage_notes(
        self,
        employee: Dict[str, Any],
        source: str,
        qualified_percentage: Decimal
    ) -> str:
        """Generate notes for wage allocation."""
        notes = []

        notes.append(f"Time allocation source: {source}")

        if qualified_percentage > 80:
            notes.append("High R&D time allocation - verify with additional documentation")

        if source == "estimate":
            notes.append("Based on estimate - consider gathering timesheet data")

        title = employee.get("title", "")
        if title:
            notes.append(f"Role: {title}")

        return "; ".join(notes)

    def _generate_supply_classification_reason(
        self,
        expense: Dict[str, Any]
    ) -> str:
        """Generate classification reason for supply expense."""
        reasons = []

        if expense.get("category"):
            reasons.append(f"Category: {expense['category']}")

        if expense.get("gl_account"):
            reasons.append(f"GL Account: {expense['gl_account']}")

        if expense.get("project_id"):
            reasons.append("Associated with qualified project")

        return "; ".join(reasons) if reasons else "General supply expense"

    def _calculate_overall_confidence(
        self,
        wage_allocations: List[WageAllocation],
        supply_expenses: List[SupplyExpense],
        contract_expenses: List[ContractResearchExpense]
    ) -> float:
        """Calculate overall confidence for all QREs."""
        all_confidences = []

        for w in wage_allocations:
            weight = float(w.qualified_wages)
            all_confidences.append((w.confidence, weight))

        for s in supply_expenses:
            weight = float(s.qualified_amount)
            all_confidences.append((s.confidence, weight))

        for c in contract_expenses:
            weight = float(c.qualified_amount)
            all_confidences.append((0.85, weight))  # Contract research typically well-documented

        if not all_confidences:
            return 0.0

        total_weight = sum(w for _, w in all_confidences)
        if total_weight == 0:
            return 0.0

        weighted_confidence = sum(c * w for c, w in all_confidences) / total_weight

        return weighted_confidence

    def _calculate_evidence_coverage(
        self,
        wage_allocations: List[WageAllocation],
        supply_expenses: List[SupplyExpense],
        contract_expenses: List[ContractResearchExpense]
    ) -> float:
        """Calculate percentage of QREs backed by evidence."""
        total_qre = Decimal("0")
        evidenced_qre = Decimal("0")

        for w in wage_allocations:
            total_qre += w.qualified_wages
            if w.evidence_ids or w.source == "timesheet":
                evidenced_qre += w.qualified_wages

        for s in supply_expenses:
            total_qre += s.qualified_amount
            if s.evidence_id:
                evidenced_qre += s.qualified_amount

        for c in contract_expenses:
            total_qre += c.qualified_amount
            if c.evidence_ids:
                evidenced_qre += c.qualified_amount

        if total_qre == 0:
            return 0.0

        return float(evidenced_qre / total_qre)

    def _generate_qre_risk_flags(
        self,
        wage_allocations: List[WageAllocation],
        supply_expenses: List[SupplyExpense],
        contract_expenses: List[ContractResearchExpense],
        total_qre: Decimal
    ) -> List[Dict[str, Any]]:
        """Generate risk flags for QRE calculation."""
        risk_flags = []

        # Check for high wage percentages
        high_wage_employees = [
            w for w in wage_allocations
            if w.qualified_percentage > 80
        ]
        if high_wage_employees:
            risk_flags.append({
                "type": "high_wage_percentage",
                "severity": "medium",
                "description": f"{len(high_wage_employees)} employees with >80% R&D time allocation",
                "affected_ids": [w.employee_id for w in high_wage_employees]
            })

        # Check for low confidence allocations
        low_confidence_wages = [
            w for w in wage_allocations
            if w.confidence < 0.6
        ]
        if low_confidence_wages:
            risk_flags.append({
                "type": "low_confidence_wages",
                "severity": "medium",
                "description": f"{len(low_confidence_wages)} employees with low confidence wage allocation",
                "affected_ids": [w.employee_id for w in low_confidence_wages]
            })

        # Check for estimate-based allocations
        estimate_based = [
            w for w in wage_allocations
            if w.source == "estimate"
        ]
        if len(estimate_based) > len(wage_allocations) / 2:
            risk_flags.append({
                "type": "estimate_heavy",
                "severity": "medium",
                "description": "Majority of wage allocations based on estimates rather than timesheets"
            })

        # Check supply expense concentration
        if supply_expenses:
            total_supply = sum(s.qualified_amount for s in supply_expenses)
            if total_qre > 0 and total_supply / total_qre > Decimal("0.3"):
                risk_flags.append({
                    "type": "high_supply_ratio",
                    "severity": "low",
                    "description": f"Supply expenses are {total_supply/total_qre*100:.1f}% of total QRE"
                })

        # Check for missing evidence
        no_evidence_count = sum(
            1 for w in wage_allocations
            if not w.evidence_ids and w.source != "timesheet"
        )
        if no_evidence_count > 0:
            risk_flags.append({
                "type": "missing_evidence",
                "severity": "medium",
                "description": f"{no_evidence_count} wage allocations without supporting evidence"
            })

        return risk_flags

    def generate_employee_narrative(
        self,
        employee: Dict[str, Any],
        allocation: WageAllocation,
        projects: List[Dict[str, Any]]
    ) -> str:
        """
        Generate R&D-relevant narrative for an employee.

        Narratives must:
        - Be conservative
        - Be evidence-cited
        - Never invent numbers
        - Focus on R&D relevance
        """
        name = employee.get("name", "Employee")
        title = employee.get("title", "")
        department = employee.get("department", "")

        narrative_parts = []

        # Introduction
        intro = f"{name}"
        if title:
            intro += f", {title}"
        if department:
            intro += f" in the {department} department"
        intro += ","
        narrative_parts.append(intro)

        # R&D involvement
        if allocation.qualified_percentage > 0:
            narrative_parts.append(
                f"devoted approximately {allocation.qualified_percentage:.0f}% of their time "
                f"to qualified research activities during the tax year."
            )

        # Project involvement
        if allocation.project_allocations:
            project_names = []
            for project_id in allocation.project_allocations.keys():
                project = next((p for p in projects if p.get("id") == project_id), None)
                if project:
                    project_names.append(project.get("name", "research project"))

            if project_names:
                if len(project_names) == 1:
                    narrative_parts.append(
                        f"Their work primarily supported the {project_names[0]} project."
                    )
                else:
                    narrative_parts.append(
                        f"Their work supported multiple research projects including: {', '.join(project_names[:3])}."
                    )

        # Role description
        role_category = employee.get("role_category", "")
        if role_category:
            role_descriptions = {
                "engineer": "performing engineering analysis, design, and development activities",
                "scientist": "conducting scientific research and experimentation",
                "developer": "developing and testing software solutions",
                "technician": "providing technical support for research activities",
                "supervisor": "directly supervising qualified research personnel",
                "support": "providing direct support to research activities"
            }
            role_desc = role_descriptions.get(role_category.lower(), "contributing to research activities")
            narrative_parts.append(f"Responsibilities included {role_desc}.")

        # Source citation
        source_descriptions = {
            "timesheet": "time records",
            "estimate": "management estimates",
            "interview": "employee interview",
            "ai_inference": "activity analysis"
        }
        source_desc = source_descriptions.get(allocation.source, "available records")
        narrative_parts.append(f"Qualified time allocation based on {source_desc}.")

        return " ".join(narrative_parts)

    def generate_qre_schedule(
        self,
        summary: QRESummary,
        include_detail: bool = True
    ) -> Dict[str, Any]:
        """Generate QRE schedule for study documentation."""
        schedule = {
            "study_id": str(summary.study_id),
            "tax_year": summary.tax_year,
            "summary": {
                "total_wages": str(summary.total_wages),
                "total_supplies": str(summary.total_supplies),
                "total_contract_research": str(summary.total_contract_research),
                "total_basic_research": str(summary.total_basic_research),
                "total_qre": str(summary.total_qre)
            },
            "calculation_date": summary.calculation_timestamp.isoformat(),
            "rules_version": summary.rules_version,
            "confidence_score": summary.overall_confidence,
            "evidence_coverage": summary.evidence_coverage
        }

        if include_detail:
            schedule["wages_detail"] = [
                {
                    "employee_id": str(w.employee_id),
                    "employee_name": w.employee_name,
                    "total_wages": str(w.total_wages),
                    "qualified_percentage": str(w.qualified_percentage),
                    "qualified_wages": str(w.qualified_wages),
                    "source": w.source,
                    "confidence": w.confidence
                }
                for w in summary.wage_allocations
            ]

            schedule["supplies_detail"] = [
                {
                    "description": s.description,
                    "vendor": s.vendor,
                    "gl_account": s.gl_account,
                    "gross_amount": str(s.gross_amount),
                    "qualified_amount": str(s.qualified_amount),
                    "confidence": s.confidence
                }
                for s in summary.supply_expenses
            ]

            schedule["contract_detail"] = [
                {
                    "contractor": c.contractor_name,
                    "description": c.contract_description,
                    "gross_amount": str(c.gross_amount),
                    "applicable_percentage": str(c.applicable_percentage),
                    "qualified_amount": str(c.qualified_amount),
                    "is_qualified_org": c.is_qualified_research_org
                }
                for c in summary.contract_expenses
            ]

        if summary.state_allocations:
            schedule["state_allocations"] = {
                state: {k: str(v) for k, v in allocs.items()}
                for state, allocs in summary.state_allocations.items()
            }

        if summary.risk_flags:
            schedule["risk_flags"] = summary.risk_flags

        return schedule
