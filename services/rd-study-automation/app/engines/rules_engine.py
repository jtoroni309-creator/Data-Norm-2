"""
Versioned Rules Engine for R&D Tax Credits

Implements Federal IRC Section 41 rules and state-specific overlays
with full version control and audit trail.
"""

import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import date
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RuleType(str, Enum):
    """Types of rules in the engine."""
    QUALIFICATION = "qualification"
    QRE_CLASSIFICATION = "qre_classification"
    CALCULATION = "calculation"
    DOCUMENTATION = "documentation"
    STATE_OVERLAY = "state_overlay"


@dataclass
class RuleResult:
    """Result of a rule evaluation."""
    rule_id: str
    rule_version: str
    passed: bool
    score: float  # 0-100
    confidence: float  # 0-1
    evidence_required: List[str]
    evidence_found: List[str]
    explanation: str
    citations: List[str]
    warnings: List[str] = field(default_factory=list)


@dataclass
class FederalRules:
    """
    Federal R&D Credit Rules (IRC Section 41)

    Implements the Federal 4-part test and QRE rules.
    """
    version: str = "2024.1"
    effective_date: date = field(default_factory=lambda: date(2024, 1, 1))

    # Credit rates
    REGULAR_CREDIT_RATE: float = 0.20  # 20%
    ASC_CREDIT_RATE: float = 0.14  # 14%

    # Base period
    DEFAULT_BASE_PERIOD_YEARS: int = 4
    MIN_BASE_AMOUNT_PERCENTAGE: float = 0.03  # 3% floor

    # Contract research percentages
    CONTRACT_RESEARCH_STANDARD_PERCENTAGE: float = 0.65  # 65%
    CONTRACT_RESEARCH_QUALIFIED_ORG_PERCENTAGE: float = 0.75  # 75%

    # Section 280C
    SECTION_280C_REDUCTION_RATE: float = 0.21  # Corporate tax rate

    # Qualified Small Business (payroll tax offset)
    QSB_GROSS_RECEIPTS_LIMIT: Decimal = Decimal("5000000")
    QSB_PAYROLL_TAX_OFFSET_LIMIT: Decimal = Decimal("500000")

    # 4-Part Test Criteria
    FOUR_PART_TEST = {
        "permitted_purpose": {
            "description": "New or improved function, performance, reliability, or quality",
            "irc_citation": "IRC §41(d)(1)(B)(i)",
            "criteria": [
                "Developing new products or processes",
                "Improving existing products or processes",
                "Enhancing functionality, performance, reliability, or quality",
                "NOT: Style, taste, cosmetic, or seasonal design changes",
                "NOT: Adaptation of existing business component to customer requirements",
                "NOT: Reverse engineering",
                "NOT: Funded research"
            ],
            "evidence_types": [
                "Product specifications",
                "Design documents",
                "Engineering notes",
                "Project proposals",
                "Technical requirements"
            ]
        },
        "technological_nature": {
            "description": "Relies on principles of physical or biological sciences, engineering, or computer science",
            "irc_citation": "IRC §41(d)(1)(B)(ii)",
            "criteria": [
                "Based on hard sciences (physics, chemistry, biology)",
                "Engineering principles",
                "Computer science principles",
                "Mathematical modeling and simulation",
                "NOT: Social sciences, economics, or humanities"
            ],
            "evidence_types": [
                "Technical documentation",
                "Engineering calculations",
                "Scientific analysis",
                "Algorithm documentation",
                "Test protocols"
            ]
        },
        "elimination_of_uncertainty": {
            "description": "Uncertainty regarding capability, method, or design",
            "irc_citation": "IRC §41(d)(1)(B)(iii)",
            "criteria": [
                "Uncertainty about capability to achieve result",
                "Uncertainty about method or methodology",
                "Uncertainty about design or appropriate design",
                "Uncertainty must exist at START of research",
                "NOT: Uncertainty about cost, time, or market acceptance"
            ],
            "evidence_types": [
                "Problem statements",
                "Feasibility studies",
                "Risk assessments",
                "Technical challenges documentation",
                "Failed approach documentation"
            ]
        },
        "process_of_experimentation": {
            "description": "Systematic evaluation of alternatives through modeling, simulation, or testing",
            "irc_citation": "IRC §41(d)(1)(B)(iv)",
            "criteria": [
                "Systematic process to evaluate alternatives",
                "Modeling and simulation",
                "Systematic trial and error",
                "Testing and prototyping",
                "Hypothesis formulation and testing",
                "NOT: Simply choosing among known alternatives",
                "NOT: Trial without systematic evaluation"
            ],
            "evidence_types": [
                "Test plans and results",
                "Prototype documentation",
                "Simulation results",
                "Alternative analysis",
                "Iteration documentation"
            ]
        }
    }

    # Excluded activities (IRC §41(d)(4))
    EXCLUDED_ACTIVITIES = [
        {
            "code": "FOREIGN",
            "description": "Research conducted outside the United States",
            "irc_citation": "IRC §41(d)(4)(F)"
        },
        {
            "code": "SOCIAL_SCIENCE",
            "description": "Research in the social sciences, arts, or humanities",
            "irc_citation": "IRC §41(d)(4)(G)"
        },
        {
            "code": "FUNDED",
            "description": "Funded research where payment does not depend on success",
            "irc_citation": "IRC §41(d)(4)(H)"
        },
        {
            "code": "AFTER_PRODUCTION",
            "description": "Research after commercial production begins",
            "irc_citation": "IRC §41(d)(4)(A)"
        },
        {
            "code": "ADAPTATION",
            "description": "Adaptation of existing business component for specific customer",
            "irc_citation": "IRC §41(d)(4)(B)"
        },
        {
            "code": "DUPLICATION",
            "description": "Duplication of existing business component from physical examination",
            "irc_citation": "IRC §41(d)(4)(C)"
        },
        {
            "code": "SURVEYS",
            "description": "Surveys, studies, etc.",
            "irc_citation": "IRC §41(d)(4)(D)"
        },
        {
            "code": "COMPUTER_SOFTWARE_INTERNAL",
            "description": "Internal use software (with exceptions)",
            "irc_citation": "IRC §41(d)(4)(E)"
        },
        {
            "code": "MANAGEMENT_STUDIES",
            "description": "Efficiency surveys, management function, market research",
            "irc_citation": "IRC §41(d)(4)(D)"
        },
        {
            "code": "QUALITY_CONTROL",
            "description": "Routine quality control testing",
            "irc_citation": "Treasury Reg. §1.41-4(c)(6)"
        },
        {
            "code": "REVERSE_ENGINEERING",
            "description": "Reverse engineering of publicly available products",
            "irc_citation": "IRC §41(d)(4)(C)"
        }
    ]

    # QRE Rules
    QRE_RULES = {
        "wages": {
            "description": "Wages for qualified services",
            "irc_citation": "IRC §41(b)(2)",
            "qualified_services": [
                "Engaging in qualified research",
                "Engaging in direct supervision of qualified research",
                "Engaging in direct support of qualified research"
            ],
            "exclusions": [
                "Fringe benefits (generally)",
                "Stock-based compensation",
                "Wages for non-qualified activities"
            ],
            "documentation_required": [
                "W-2 wages",
                "Time tracking records",
                "Project assignments",
                "Employee role documentation"
            ]
        },
        "supplies": {
            "description": "Supplies used in conduct of qualified research",
            "irc_citation": "IRC §41(b)(2)(C)",
            "qualified_supplies": [
                "Tangible property other than land or depreciable property",
                "Used in the conduct of qualified research",
                "Consumed in research activities"
            ],
            "exclusions": [
                "Capital equipment (depreciable property)",
                "Land and buildings",
                "General overhead supplies"
            ],
            "documentation_required": [
                "Purchase invoices",
                "GL account detail",
                "Project allocation"
            ]
        },
        "contract_research": {
            "description": "Contract research expenses",
            "irc_citation": "IRC §41(b)(3)",
            "requirements": [
                "65% of amounts paid for qualified research",
                "75% if paid to qualified research consortium or energy research consortium",
                "Must be performed in United States"
            ],
            "exclusions": [
                "Amounts for non-qualified activities",
                "Foreign research"
            ],
            "documentation_required": [
                "Contracts with research providers",
                "Invoices",
                "Scope of work documentation",
                "Research results"
            ]
        },
        "basic_research": {
            "description": "Basic research payments to qualified organizations",
            "irc_citation": "IRC §41(e)",
            "qualified_organizations": [
                "Educational institutions",
                "Scientific research organizations",
                "Grants for basic research"
            ],
            "documentation_required": [
                "Grant agreements",
                "Payment records",
                "Organization qualification"
            ]
        }
    }

    def get_rules_hash(self) -> str:
        """Generate hash of rules for version tracking."""
        rules_str = json.dumps({
            "version": self.version,
            "four_part_test": self.FOUR_PART_TEST,
            "excluded_activities": self.EXCLUDED_ACTIVITIES,
            "qre_rules": self.QRE_RULES,
            "rates": {
                "regular": self.REGULAR_CREDIT_RATE,
                "asc": self.ASC_CREDIT_RATE
            }
        }, sort_keys=True)
        return hashlib.sha256(rules_str.encode()).hexdigest()[:16]


@dataclass
class StateRules:
    """
    State R&D Credit Rules

    State-specific overlays for R&D tax credits.
    Each state may have different:
    - Credit rates
    - QRE definitions
    - Base period calculations
    - Carryforward/carryback rules
    - Caps and limitations
    """
    version: str = "2024.1"
    state_code: str = ""
    state_name: str = ""
    effective_date: date = field(default_factory=lambda: date(2024, 1, 1))

    # Credit availability
    has_rd_credit: bool = True
    credit_type: str = "incremental"  # incremental, non-incremental, hybrid

    # Rates
    credit_rate: float = 0.0
    alternative_rate: float = 0.0
    small_business_rate: float = 0.0

    # Base calculation
    base_method: str = "federal"  # federal, fixed_percentage, state_specific
    base_percentage: float = 0.0

    # QRE modifications
    qre_modifications: Dict[str, Any] = field(default_factory=dict)
    additional_qre_categories: List[str] = field(default_factory=list)
    excluded_qre_categories: List[str] = field(default_factory=list)

    # Limitations
    credit_cap: Optional[Decimal] = None
    credit_cap_percentage: Optional[float] = None  # % of tax liability

    # Carryforward/Carryback
    carryforward_years: int = 0
    carryback_years: int = 0

    # Refundability
    is_refundable: bool = False
    refundable_percentage: float = 0.0

    # Small business provisions
    small_business_threshold: Optional[Decimal] = None
    small_business_credit_cap: Optional[Decimal] = None

    # Documentation requirements
    additional_documentation: List[str] = field(default_factory=list)
    state_form_number: str = ""

    # Citation
    statute_citation: str = ""
    regulation_citation: str = ""


# =============================================================================
# STATE RULES DEFINITIONS
# =============================================================================

STATE_RULES_2024: Dict[str, StateRules] = {
    "CA": StateRules(
        version="2024.1",
        state_code="CA",
        state_name="California",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.24,  # 24%
        alternative_rate=0.15,  # 15% for basic research
        base_method="state_specific",
        carryforward_years=0,  # Indefinite
        carryback_years=0,
        is_refundable=False,
        statute_citation="Cal. Rev. & Tax Code §23609",
        state_form_number="FTB 3523",
        qre_modifications={
            "contract_research_in_state": True,  # Must be performed in CA
            "wages_in_state": True  # Must be for work performed in CA
        }
    ),
    "TX": StateRules(
        version="2024.1",
        state_code="TX",
        state_name="Texas",
        has_rd_credit=True,
        credit_type="franchise_tax",
        credit_rate=0.05,  # 5% of qualified research expenses
        base_method="non_incremental",
        credit_cap_percentage=0.50,  # 50% of franchise tax
        carryforward_years=20,
        is_refundable=False,
        statute_citation="Tex. Tax Code §171.651-.658",
        state_form_number="Form 05-178",
        qre_modifications={
            "wages_in_state": True
        }
    ),
    "NY": StateRules(
        version="2024.1",
        state_code="NY",
        state_name="New York",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.09,  # 9% (current year only)
        alternative_rate=0.03,  # 3% of Federal QRE
        base_method="federal",
        carryforward_years=15,
        is_refundable=True,
        refundable_percentage=0.50,  # 50% for qualified emerging tech companies
        small_business_threshold=Decimal("40000000"),
        statute_citation="NY Tax Law §210-B",
        state_form_number="CT-46"
    ),
    "MA": StateRules(
        version="2024.1",
        state_code="MA",
        state_name="Massachusetts",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.10,  # 10%
        base_method="federal",
        base_percentage=0.0,
        credit_cap=Decimal("25000000"),  # $25M cap
        carryforward_years=15,
        is_refundable=False,
        statute_citation="M.G.L. c. 63, §38M",
        state_form_number="Schedule RC"
    ),
    "NJ": StateRules(
        version="2024.1",
        state_code="NJ",
        state_name="New Jersey",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.10,  # 10%
        small_business_rate=0.15,  # 15% for small businesses
        base_method="federal",
        carryforward_years=7,
        is_refundable=False,
        small_business_threshold=Decimal("5000000"),
        statute_citation="N.J.S.A. 54:10A-5.24",
        state_form_number="Form 306"
    ),
    "PA": StateRules(
        version="2024.1",
        state_code="PA",
        state_name="Pennsylvania",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.10,  # 10%
        small_business_rate=0.20,  # 20% for small businesses
        base_method="federal",
        credit_cap=Decimal("55000000"),  # Program cap
        carryforward_years=15,
        is_refundable=False,
        small_business_threshold=Decimal("5000000"),
        statute_citation="72 P.S. §8904-A et seq.",
        state_form_number="REV-545"
    ),
    "GA": StateRules(
        version="2024.1",
        state_code="GA",
        state_name="Georgia",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.10,  # 10%
        base_method="federal",
        carryforward_years=10,
        is_refundable=False,
        statute_citation="O.C.G.A. §48-7-40.12",
        state_form_number="IT-RD"
    ),
    "AZ": StateRules(
        version="2024.1",
        state_code="AZ",
        state_name="Arizona",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.24,  # 24% first $2.5M
        alternative_rate=0.15,  # 15% over $2.5M
        base_method="state_specific",
        carryforward_years=15,
        is_refundable=True,
        refundable_percentage=0.75,  # Up to 75% for qualified taxpayers
        statute_citation="A.R.S. §43-1074.01",
        state_form_number="Form 308"
    ),
    "CT": StateRules(
        version="2024.1",
        state_code="CT",
        state_name="Connecticut",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.20,  # 20%
        base_method="federal",
        credit_cap_percentage=0.70,  # 70% of tax liability
        carryforward_years=15,
        is_refundable=False,
        statute_citation="Conn. Gen. Stat. §12-217n",
        state_form_number="CT-1120 RDC"
    ),
    "FL": StateRules(
        version="2024.1",
        state_code="FL",
        state_name="Florida",
        has_rd_credit=False,  # No state R&D credit
        credit_rate=0.0
    ),
    "IL": StateRules(
        version="2024.1",
        state_code="IL",
        state_name="Illinois",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.065,  # 6.5%
        base_method="federal",
        carryforward_years=5,
        is_refundable=False,
        statute_citation="35 ILCS 5/201(k)",
        state_form_number="Schedule 1299-D"
    ),
    "OH": StateRules(
        version="2024.1",
        state_code="OH",
        state_name="Ohio",
        has_rd_credit=True,
        credit_type="non_incremental",
        credit_rate=0.07,  # 7%
        base_method="non_incremental",
        credit_cap=Decimal("5000000"),
        carryforward_years=7,
        is_refundable=False,
        statute_citation="ORC §122.152",
        state_form_number="IT K-1"
    ),
    "WA": StateRules(
        version="2024.1",
        state_code="WA",
        state_name="Washington",
        has_rd_credit=True,
        credit_type="b_and_o_credit",  # Against B&O tax
        credit_rate=0.015,  # 1.5% of qualified R&D
        base_method="non_incremental",
        carryforward_years=5,
        is_refundable=False,
        statute_citation="RCW 82.04.4452",
        state_form_number="Schedule C"
    ),
    "MN": StateRules(
        version="2024.1",
        state_code="MN",
        state_name="Minnesota",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.10,  # 10% first $2M
        alternative_rate=0.04,  # 4% over $2M
        base_method="federal",
        carryforward_years=15,
        is_refundable=True,
        refundable_percentage=1.0,  # Fully refundable (with limits)
        statute_citation="Minn. Stat. §290.068",
        state_form_number="Schedule RD"
    ),
    "CO": StateRules(
        version="2024.1",
        state_code="CO",
        state_name="Colorado",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.03,  # 3%
        base_method="federal",
        carryforward_years=5,
        is_refundable=False,
        statute_citation="C.R.S. §39-22-104.7",
        state_form_number="DR 1366"
    ),
    "WI": StateRules(
        version="2024.1",
        state_code="WI",
        state_name="Wisconsin",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.05,  # 5% general
        small_business_rate=0.10,  # 10% for qualified expenses
        base_method="federal",
        carryforward_years=15,
        is_refundable=False,
        small_business_threshold=Decimal("5000000"),
        statute_citation="Wis. Stat. §71.07(4k)",
        state_form_number="Schedule R"
    ),
    "VA": StateRules(
        version="2024.1",
        state_code="VA",
        state_name="Virginia",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.15,  # 15%
        base_method="federal",
        credit_cap=Decimal("45000000"),  # Program cap
        carryforward_years=10,
        is_refundable=False,
        statute_citation="Va. Code Ann. §58.1-439.12:08",
        state_form_number="RDC"
    ),
    "UT": StateRules(
        version="2024.1",
        state_code="UT",
        state_name="Utah",
        has_rd_credit=True,
        credit_type="non_incremental",
        credit_rate=0.05,  # 5% nonrefundable + 5% refundable
        alternative_rate=0.05,  # Additional refundable portion
        base_method="non_incremental",
        carryforward_years=14,
        is_refundable=True,
        refundable_percentage=0.50,
        statute_citation="Utah Code Ann. §59-7-614.3",
        state_form_number="TC-20R"
    ),
    "NC": StateRules(
        version="2024.1",
        state_code="NC",
        state_name="North Carolina",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.0125,  # 1.25% of NC QRE
        base_method="state_specific",
        carryforward_years=15,
        is_refundable=False,
        statute_citation="N.C. Gen. Stat. §105-129.50",
        state_form_number="NC-478R"
    ),
    "MD": StateRules(
        version="2024.1",
        state_code="MD",
        state_name="Maryland",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.10,  # 10% basic
        small_business_rate=0.03,  # 3% + basic
        base_method="federal",
        carryforward_years=7,
        is_refundable=True,
        refundable_percentage=1.0,  # For small businesses
        small_business_threshold=Decimal("5000000"),
        statute_citation="Md. Tax-Gen. Code Ann. §10-721",
        state_form_number="Form 500CR"
    ),
    "SC": StateRules(
        version="2024.1",
        state_code="SC",
        state_name="South Carolina",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.05,  # 5%
        base_method="federal",
        carryforward_years=10,
        is_refundable=False,
        statute_citation="S.C. Code Ann. §12-6-3415",
        state_form_number="SC I-330"
    ),
    "IN": StateRules(
        version="2024.1",
        state_code="IN",
        state_name="Indiana",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.15,  # 15% for small business
        alternative_rate=0.10,  # 10% general
        base_method="federal",
        carryforward_years=10,
        is_refundable=False,
        small_business_threshold=Decimal("5000000"),
        statute_citation="IC 6-3.1-4-1 et seq.",
        state_form_number="Schedule IN-RDC"
    ),
    "OR": StateRules(
        version="2024.1",
        state_code="OR",
        state_name="Oregon",
        has_rd_credit=True,
        credit_type="incremental",
        credit_rate=0.05,  # 5%
        base_method="federal",
        carryforward_years=5,
        is_refundable=False,
        statute_citation="ORS 317.152-.154",
        state_form_number="OR-RD"
    ),
}


class RulesEngine:
    """
    Main Rules Engine for R&D Tax Credit Studies

    Provides versioned rules for:
    - Federal 4-part test evaluation
    - QRE classification
    - Credit calculations
    - State-specific overlays
    """

    def __init__(self, version: str = "2024.1"):
        self.version = version
        self.federal_rules = FederalRules(version=version)
        self.state_rules = STATE_RULES_2024.copy()
        self._load_custom_rules()

    def _load_custom_rules(self):
        """Load any custom/updated rules from database or config."""
        # In production, this would load from database
        pass

    def get_federal_rules(self) -> FederalRules:
        """Get current Federal rules."""
        return self.federal_rules

    def get_state_rules(self, state_code: str) -> Optional[StateRules]:
        """Get rules for a specific state."""
        return self.state_rules.get(state_code.upper())

    def get_available_states(self) -> List[str]:
        """Get list of states with R&D credits."""
        return [
            code for code, rules in self.state_rules.items()
            if rules.has_rd_credit
        ]

    def get_four_part_test_criteria(self) -> Dict[str, Any]:
        """Get Federal 4-part test criteria."""
        return self.federal_rules.FOUR_PART_TEST

    def get_excluded_activities(self) -> List[Dict[str, str]]:
        """Get list of excluded activities."""
        return self.federal_rules.EXCLUDED_ACTIVITIES

    def get_qre_rules(self) -> Dict[str, Any]:
        """Get QRE classification rules."""
        return self.federal_rules.QRE_RULES

    def evaluate_excluded_activity(
        self,
        activity_description: str,
        activity_factors: Dict[str, Any]
    ) -> Tuple[bool, List[str], str]:
        """
        Evaluate if an activity is excluded from R&D credit.

        Returns:
            Tuple of (is_excluded, applicable_exclusions, explanation)
        """
        applicable_exclusions = []
        explanations = []

        for exclusion in self.federal_rules.EXCLUDED_ACTIVITIES:
            # Check each exclusion criterion
            exclusion_code = exclusion["code"]

            if exclusion_code == "FOREIGN" and activity_factors.get("performed_outside_us"):
                applicable_exclusions.append(exclusion_code)
                explanations.append(f"Activity performed outside US ({exclusion['irc_citation']})")

            elif exclusion_code == "FUNDED" and activity_factors.get("is_funded_research"):
                applicable_exclusions.append(exclusion_code)
                explanations.append(f"Funded research ({exclusion['irc_citation']})")

            elif exclusion_code == "AFTER_PRODUCTION" and activity_factors.get("after_commercial_production"):
                applicable_exclusions.append(exclusion_code)
                explanations.append(f"Research after commercial production ({exclusion['irc_citation']})")

            elif exclusion_code == "ADAPTATION" and activity_factors.get("is_adaptation"):
                applicable_exclusions.append(exclusion_code)
                explanations.append(f"Adaptation to customer requirements ({exclusion['irc_citation']})")

            elif exclusion_code == "QUALITY_CONTROL" and activity_factors.get("is_quality_control"):
                applicable_exclusions.append(exclusion_code)
                explanations.append(f"Routine quality control ({exclusion['irc_citation']})")

        is_excluded = len(applicable_exclusions) > 0
        explanation = "; ".join(explanations) if explanations else "No exclusions apply"

        return is_excluded, applicable_exclusions, explanation

    def get_contract_research_percentage(
        self,
        is_qualified_org: bool,
        state_code: Optional[str] = None
    ) -> float:
        """Get applicable contract research percentage."""
        if is_qualified_org:
            return self.federal_rules.CONTRACT_RESEARCH_QUALIFIED_ORG_PERCENTAGE
        return self.federal_rules.CONTRACT_RESEARCH_STANDARD_PERCENTAGE

    def get_credit_rate(
        self,
        method: str,
        state_code: Optional[str] = None,
        is_small_business: bool = False,
        qre_amount: Optional[Decimal] = None
    ) -> float:
        """
        Get applicable credit rate.

        Args:
            method: 'regular', 'asc', or state code
            state_code: State code for state credit
            is_small_business: Whether entity qualifies as small business
            qre_amount: Total QRE (for tiered rates)
        """
        if state_code:
            state_rules = self.get_state_rules(state_code)
            if not state_rules or not state_rules.has_rd_credit:
                return 0.0

            if is_small_business and state_rules.small_business_rate > 0:
                return state_rules.small_business_rate
            return state_rules.credit_rate

        if method.lower() == "asc":
            return self.federal_rules.ASC_CREDIT_RATE
        return self.federal_rules.REGULAR_CREDIT_RATE

    def validate_rules_version(self, tax_year: int) -> Tuple[bool, str]:
        """
        Validate that rules version is appropriate for tax year.

        Returns:
            Tuple of (is_valid, message)
        """
        rules_year = int(self.version.split(".")[0])

        if rules_year < tax_year:
            return False, f"Rules version {self.version} may not reflect {tax_year} tax year changes"

        return True, f"Rules version {self.version} is valid for tax year {tax_year}"

    def get_rules_citation(
        self,
        rule_type: str,
        state_code: Optional[str] = None
    ) -> str:
        """Get citation for a specific rule."""
        if state_code:
            state_rules = self.get_state_rules(state_code)
            if state_rules:
                return f"{state_rules.statute_citation}; {state_rules.regulation_citation}"
            return ""

        citations = {
            "four_part_test": "IRC §41(d)(1)(B); Treasury Reg. §1.41-4",
            "qre_wages": "IRC §41(b)(2)(A); Treasury Reg. §1.41-2(d)",
            "qre_supplies": "IRC §41(b)(2)(C); Treasury Reg. §1.41-2(b)",
            "qre_contract": "IRC §41(b)(3); Treasury Reg. §1.41-2(e)",
            "regular_credit": "IRC §41(a)(1), (c); Treasury Reg. §1.41-3",
            "asc": "IRC §41(c)(4); Treasury Reg. §1.41-8",
            "excluded_activities": "IRC §41(d)(4); Treasury Reg. §1.41-4(c)"
        }
        return citations.get(rule_type, "IRC §41")

    def export_rules_config(self) -> Dict[str, Any]:
        """Export current rules configuration for audit trail."""
        return {
            "version": self.version,
            "federal_rules_hash": self.federal_rules.get_rules_hash(),
            "federal_rules": {
                "rates": {
                    "regular": self.federal_rules.REGULAR_CREDIT_RATE,
                    "asc": self.federal_rules.ASC_CREDIT_RATE
                },
                "base_period_years": self.federal_rules.DEFAULT_BASE_PERIOD_YEARS,
                "min_base_percentage": self.federal_rules.MIN_BASE_AMOUNT_PERCENTAGE,
                "contract_percentages": {
                    "standard": self.federal_rules.CONTRACT_RESEARCH_STANDARD_PERCENTAGE,
                    "qualified_org": self.federal_rules.CONTRACT_RESEARCH_QUALIFIED_ORG_PERCENTAGE
                }
            },
            "state_rules": {
                code: {
                    "has_credit": rules.has_rd_credit,
                    "credit_rate": rules.credit_rate,
                    "credit_type": rules.credit_type,
                    "carryforward_years": rules.carryforward_years
                }
                for code, rules in self.state_rules.items()
            }
        }
