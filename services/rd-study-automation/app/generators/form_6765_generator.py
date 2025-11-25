"""
Form 6765 Generator

Generates IRS Form 6765 (Credit for Increasing Research Activities).
"""

import io
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

logger = logging.getLogger(__name__)


class Form6765Generator:
    """
    Generates IRS Form 6765 data and draft forms.

    Form 6765 includes:
    - Section A: Regular Credit
    - Section B: Alternative Simplified Credit
    - Section C: Current Year Credit
    - Section D: Qualified Research Expenses
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.tax_year = self.config.get("tax_year", 2024)

    def generate_form_data(
        self,
        study_data: Dict[str, Any],
        qre_summary: Dict[str, Any],
        calculation_result: Dict[str, Any],
        selected_method: str = "asc"
    ) -> Dict[str, Any]:
        """
        Generate Form 6765 line data.

        Returns dictionary with all form lines populated.
        """
        form_data = {
            "form_number": "6765",
            "form_title": "Credit for Increasing Research Activities",
            "tax_year": study_data.get("tax_year", self.tax_year),
            "entity_info": {
                "name": study_data.get("entity_name", ""),
                "ein": study_data.get("ein", ""),
                "tax_year_beginning": str(study_data.get("fiscal_year_start", "")),
                "tax_year_ending": str(study_data.get("fiscal_year_end", ""))
            },
            "section_a": self._generate_section_a(qre_summary, calculation_result),
            "section_b": self._generate_section_b(qre_summary, calculation_result),
            "section_c": self._generate_section_c(calculation_result, selected_method),
            "section_d": self._generate_section_d(qre_summary),
            "election_made": {
                "regular_credit": selected_method == "regular",
                "asc": selected_method == "asc",
                "280c_election": True
            },
            "supporting_schedules": self._generate_supporting_schedules(
                qre_summary, calculation_result
            )
        }

        return form_data

    def _generate_section_a(
        self,
        qre_summary: Dict,
        calculation_result: Dict
    ) -> Dict[str, Any]:
        """Generate Section A - Regular Credit."""
        regular = calculation_result.get("federal_regular", {})

        return {
            "title": "Section A—Regular Credit",
            "lines": {
                "1": {
                    "description": "Certain amounts paid or incurred to energy consortia",
                    "value": Decimal("0"),
                    "source": "Schedule - Energy research payments"
                },
                "2": {
                    "description": "Basic research payments to qualified organizations",
                    "value": qre_summary.get("total_basic_research", Decimal("0")),
                    "source": "QRE Schedule - Basic Research"
                },
                "3": {
                    "description": "Qualified organization base period amount",
                    "value": Decimal("0"),
                    "source": "Calculated from prior years"
                },
                "4": {
                    "description": "Subtract line 3 from line 2",
                    "value": qre_summary.get("total_basic_research", Decimal("0")),
                    "formula": "Line 2 - Line 3"
                },
                "5": {
                    "description": "Wages for qualified services",
                    "value": qre_summary.get("total_wages", Decimal("0")),
                    "source": "QRE Schedule - Wages"
                },
                "6": {
                    "description": "Cost of supplies",
                    "value": qre_summary.get("total_supplies", Decimal("0")),
                    "source": "QRE Schedule - Supplies"
                },
                "7": {
                    "description": "Rental or lease costs of computers",
                    "value": Decimal("0"),
                    "source": "Not applicable"
                },
                "8": {
                    "description": "Enter the applicable percentage of contract research expenses",
                    "value": qre_summary.get("total_contract_research", Decimal("0")),
                    "source": "QRE Schedule - Contract Research (65%/75%)"
                },
                "9": {
                    "description": "Total qualified research expenses",
                    "value": qre_summary.get("total_qre", Decimal("0")),
                    "formula": "Sum of Lines 1-8"
                },
                "10": {
                    "description": "Enter fixed-base percentage (not more than 16%)",
                    "value": regular.get("fixed_base_percentage", Decimal("0.03")),
                    "format": "percentage",
                    "source": "Base period calculation"
                },
                "11": {
                    "description": "Enter average annual gross receipts for the 4 tax years",
                    "value": regular.get("avg_gross_receipts", Decimal("0")),
                    "source": "Gross receipts schedule"
                },
                "12": {
                    "description": "Multiply line 10 by line 11",
                    "value": regular.get("calculated_base", Decimal("0")),
                    "formula": "Line 10 × Line 11"
                },
                "13": {
                    "description": "Subtract line 12 from line 9. If zero or less, enter -0-",
                    "value": regular.get("excess_qre", Decimal("0")),
                    "formula": "MAX(Line 9 - Line 12, 0)"
                },
                "14": {
                    "description": "Multiply line 13 by 20% (0.20)",
                    "value": regular.get("tentative_credit", Decimal("0")),
                    "formula": "Line 13 × 0.20"
                },
                # Lines 15-23 for startup companies (typically not applicable)
                "24": {
                    "description": "Add lines 1, 4, and 14. Also include amounts from lines 15-23 if applicable",
                    "value": regular.get("tentative_credit", Decimal("0")),
                    "formula": "Line 1 + Line 4 + Line 14"
                }
            }
        }

    def _generate_section_b(
        self,
        qre_summary: Dict,
        calculation_result: Dict
    ) -> Dict[str, Any]:
        """Generate Section B - Alternative Simplified Credit."""
        asc = calculation_result.get("federal_asc", {})

        return {
            "title": "Section B—Alternative Simplified Credit",
            "lines": {
                "25": {
                    "description": "Certain amounts paid or incurred to energy consortia",
                    "value": Decimal("0")
                },
                "26": {
                    "description": "Basic research payments to qualified organizations",
                    "value": qre_summary.get("total_basic_research", Decimal("0"))
                },
                "27": {
                    "description": "Qualified organization base period amount",
                    "value": Decimal("0")
                },
                "28": {
                    "description": "Subtract line 27 from line 26",
                    "value": qre_summary.get("total_basic_research", Decimal("0")),
                    "formula": "Line 26 - Line 27"
                },
                "29": {
                    "description": "Add lines 25 and 28",
                    "value": qre_summary.get("total_basic_research", Decimal("0")),
                    "formula": "Line 25 + Line 28"
                },
                "30": {
                    "description": "Multiply line 29 by 20% (0.20)",
                    "value": qre_summary.get("total_basic_research", Decimal("0")) * Decimal("0.20"),
                    "formula": "Line 29 × 0.20"
                },
                "31": {
                    "description": "Wages for qualified services",
                    "value": qre_summary.get("total_wages", Decimal("0"))
                },
                "32": {
                    "description": "Cost of supplies",
                    "value": qre_summary.get("total_supplies", Decimal("0"))
                },
                "33": {
                    "description": "Rental or lease costs of computers",
                    "value": Decimal("0")
                },
                "34": {
                    "description": "Enter the applicable percentage of contract research expenses",
                    "value": qre_summary.get("total_contract_research", Decimal("0"))
                },
                "35": {
                    "description": "Total qualified research expenses",
                    "value": qre_summary.get("total_qre", Decimal("0")),
                    "formula": "Sum of Lines 31-34"
                },
                "36": {
                    "description": "Enter your total QREs for the 3 tax years prior to the current year",
                    "value": asc.get("total_prior_3_years", Decimal("0")),
                    "note": "Enter amount from prior year studies"
                },
                "37": {
                    "description": "Divide line 36 by 3.0",
                    "value": asc.get("avg_prior_qre", Decimal("0")),
                    "formula": "Line 36 ÷ 3"
                },
                "38": {
                    "description": "Multiply line 37 by 50% (0.50)",
                    "value": asc.get("base_amount", Decimal("0")),
                    "formula": "Line 37 × 0.50"
                },
                "39": {
                    "description": "Subtract line 38 from line 35. If zero or less, enter -0-",
                    "value": asc.get("excess_qre", Decimal("0")),
                    "formula": "MAX(Line 35 - Line 38, 0)"
                },
                "40": {
                    "description": "Multiply line 39 by 14% (0.14)",
                    "value": asc.get("calculated_credit", Decimal("0")),
                    "formula": "Line 39 × 0.14"
                },
                "41": {
                    "description": "Add lines 30 and 40",
                    "value": asc.get("tentative_credit", Decimal("0")),
                    "formula": "Line 30 + Line 40"
                }
            }
        }

    def _generate_section_c(
        self,
        calculation_result: Dict,
        selected_method: str
    ) -> Dict[str, Any]:
        """Generate Section C - Current Year Credit."""
        regular = calculation_result.get("federal_regular", {})
        asc = calculation_result.get("federal_asc", {})

        if selected_method == "regular":
            line_42_value = regular.get("tentative_credit", Decimal("0"))
            line_42_source = "From Section A, line 24"
        else:
            line_42_value = asc.get("tentative_credit", Decimal("0"))
            line_42_source = "From Section B, line 41"

        section_280c = calculation_result.get("section_280c_reduction", Decimal("0"))

        return {
            "title": "Section C—Current Year Credit",
            "lines": {
                "42": {
                    "description": "Enter the amount from Section A, line 24, or Section B, line 41",
                    "value": line_42_value,
                    "source": line_42_source
                },
                "43": {
                    "description": "Are you electing the reduced credit under section 280C?",
                    "value": "Yes",
                    "type": "checkbox"
                },
                "44": {
                    "description": "Multiply line 42 by the corporate tax rate",
                    "value": section_280c,
                    "formula": "Line 42 × 0.21 (if 280C elected)"
                },
                "45": {
                    "description": "Subtract line 44 from line 42",
                    "value": calculation_result.get("federal_credit", Decimal("0")),
                    "formula": "Line 42 - Line 44"
                },
                "46": {
                    "description": "Research credit from partnerships, S corporations, estates, and trusts",
                    "value": Decimal("0")
                },
                "47": {
                    "description": "Add lines 45 and 46",
                    "value": calculation_result.get("federal_credit", Decimal("0")),
                    "formula": "Line 45 + Line 46"
                },
                "48": {
                    "description": "Amount allocated to beneficiaries of estates or trusts",
                    "value": Decimal("0")
                },
                "49": {
                    "description": "Estates and trusts: subtract line 48 from line 47",
                    "value": calculation_result.get("federal_credit", Decimal("0")),
                    "formula": "Line 47 - Line 48"
                }
            }
        }

    def _generate_section_d(self, qre_summary: Dict) -> Dict[str, Any]:
        """Generate Section D - Qualified Research Expenses."""
        return {
            "title": "Section D—Qualified Research Expenses",
            "note": "Complete this section if you are claiming the credit for increasing research activities",
            "summary": {
                "total_wages": qre_summary.get("total_wages", Decimal("0")),
                "total_supplies": qre_summary.get("total_supplies", Decimal("0")),
                "total_contract": qre_summary.get("total_contract_research", Decimal("0")),
                "total_qre": qre_summary.get("total_qre", Decimal("0"))
            }
        }

    def _generate_supporting_schedules(
        self,
        qre_summary: Dict,
        calculation_result: Dict
    ) -> List[Dict[str, Any]]:
        """Generate supporting schedules."""
        return [
            {
                "schedule": "QRE Summary",
                "columns": ["Category", "Amount"],
                "data": [
                    ["Wage QRE", qre_summary.get("total_wages", Decimal("0"))],
                    ["Supply QRE", qre_summary.get("total_supplies", Decimal("0"))],
                    ["Contract Research QRE", qre_summary.get("total_contract_research", Decimal("0"))],
                    ["Basic Research QRE", qre_summary.get("total_basic_research", Decimal("0"))],
                    ["Total QRE", qre_summary.get("total_qre", Decimal("0"))]
                ]
            },
            {
                "schedule": "Gross Receipts",
                "columns": ["Year", "Gross Receipts"],
                "data": calculation_result.get("gross_receipts_schedule", [])
            },
            {
                "schedule": "Base Period QRE",
                "columns": ["Year", "QRE"],
                "data": calculation_result.get("base_period_schedule", [])
            }
        ]

    def generate_tax_preparer_summary(
        self,
        study_data: Dict[str, Any],
        qre_summary: Dict[str, Any],
        calculation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate summary for tax preparer.

        Shows Form 6765 line values with sources.
        """
        selected_method = calculation_result.get("selected_method", "asc")

        return {
            "study_id": str(study_data.get("id", "")),
            "tax_year": study_data.get("tax_year"),
            "entity_name": study_data.get("entity_name"),
            "entity_type": study_data.get("entity_type"),
            "ein": study_data.get("ein"),

            "federal_method": selected_method,
            "federal_credit": calculation_result.get("federal_credit", Decimal("0")),

            "form_6765_key_lines": {
                "line_9_total_qre": qre_summary.get("total_qre", Decimal("0")),
                "line_24_regular_credit": calculation_result.get("federal_regular", {}).get("tentative_credit", Decimal("0")),
                "line_41_asc_credit": calculation_result.get("federal_asc", {}).get("tentative_credit", Decimal("0")),
                "line_45_final_credit": calculation_result.get("federal_credit", Decimal("0"))
            },

            "qre_breakdown": {
                "wages": qre_summary.get("total_wages", Decimal("0")),
                "supplies": qre_summary.get("total_supplies", Decimal("0")),
                "contract_research": qre_summary.get("total_contract_research", Decimal("0")),
                "basic_research": qre_summary.get("total_basic_research", Decimal("0"))
            },

            "state_credits": {
                state: str(result.get("final_credit", Decimal("0")))
                for state, result in calculation_result.get("state_results", {}).items()
            },

            "total_credits": calculation_result.get("total_credits", Decimal("0")),

            "key_assumptions": study_data.get("assumptions", []),
            "limitations": study_data.get("limitations", []),

            "effective_credit_rate": (
                calculation_result.get("federal_credit", Decimal("0")) /
                qre_summary.get("total_qre", Decimal("1"))
            ) if qre_summary.get("total_qre") else Decimal("0"),

            "preparer_notes": [
                f"Credit calculated using {selected_method.upper()} method",
                "Section 280C(c) election made - reduced credit claimed",
                f"Study covers tax year ending {study_data.get('fiscal_year_end', 'N/A')}"
            ]
        }

    def generate_draft_form(
        self,
        form_data: Dict[str, Any]
    ) -> bytes:
        """
        Generate draft PDF of Form 6765.

        In production, this would populate an actual IRS form template.
        """
        # Placeholder - returns JSON structure
        # In production, use pdfrw or PyPDF2 to fill IRS Form 6765 template

        import json
        return json.dumps(form_data, indent=2, default=str).encode("utf-8")
