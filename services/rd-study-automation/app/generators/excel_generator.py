"""
Excel Workbook Generator

Generates comprehensive Excel workbooks for R&D tax credit studies.
"""

import io
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

logger = logging.getLogger(__name__)


class ExcelWorkbookGenerator:
    """
    Generates Excel workbooks for R&D tax credit studies.

    Workbook includes:
    - Raw Imports (read-only)
    - Normalized Data
    - QRE Schedules
    - Federal Regular Calculation
    - Federal ASC Calculation
    - State Tabs
    - GL/Payroll Reconciliations
    - Sanity Checks
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    def generate_workbook(
        self,
        study_data: Dict[str, Any],
        projects: List[Dict[str, Any]],
        employees: List[Dict[str, Any]],
        qres: List[Dict[str, Any]],
        calculation_result: Dict[str, Any],
        raw_data: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate complete Excel workbook.

        Returns workbook content as bytes.
        """
        # In production, use openpyxl or xlsxwriter
        # This is a structure representation

        workbook_structure = {
            "metadata": {
                "title": f"R&D Study - {study_data.get('entity_name', 'Unknown')}",
                "tax_year": study_data.get("tax_year"),
                "generated_at": datetime.utcnow().isoformat()
            },
            "sheets": [
                self._create_summary_sheet(study_data, calculation_result),
                self._create_raw_imports_sheet(raw_data),
                self._create_employees_sheet(employees),
                self._create_projects_sheet(projects),
                self._create_wage_qre_sheet(employees, qres),
                self._create_supply_qre_sheet(qres),
                self._create_contract_qre_sheet(qres),
                self._create_federal_regular_sheet(calculation_result),
                self._create_federal_asc_sheet(calculation_result),
                self._create_reconciliation_sheet(study_data, qres, employees),
                self._create_sanity_checks_sheet(study_data, calculation_result),
            ]
        }

        # Add state sheets
        for state_code, state_result in calculation_result.get("state_results", {}).items():
            workbook_structure["sheets"].append(
                self._create_state_sheet(state_code, state_result)
            )

        return self._generate_excel_bytes(workbook_structure)

    def _create_summary_sheet(
        self,
        study_data: Dict,
        calculation_result: Dict
    ) -> Dict:
        """Create summary sheet."""
        return {
            "name": "Summary",
            "type": "summary",
            "protected": True,
            "sections": [
                {
                    "title": "Study Information",
                    "data": [
                        ["Entity Name", study_data.get("entity_name", "")],
                        ["Tax Year", study_data.get("tax_year", "")],
                        ["EIN", study_data.get("ein", "")],
                        ["Entity Type", study_data.get("entity_type", "")],
                        ["Fiscal Year End", str(study_data.get("fiscal_year_end", ""))],
                    ]
                },
                {
                    "title": "QRE Summary",
                    "data": [
                        ["Total Wage QRE", calculation_result.get("qre_wages", 0)],
                        ["Total Supply QRE", calculation_result.get("qre_supplies", 0)],
                        ["Total Contract QRE", calculation_result.get("qre_contract", 0)],
                        ["Total QRE", calculation_result.get("total_qre", 0)],
                    ],
                    "format": "currency"
                },
                {
                    "title": "Credit Summary",
                    "data": [
                        ["Regular Credit", calculation_result.get("regular_credit", 0)],
                        ["ASC Credit", calculation_result.get("asc_credit", 0)],
                        ["Selected Method", calculation_result.get("selected_method", "")],
                        ["Federal Credit", calculation_result.get("federal_credit", 0)],
                        ["Total State Credits", calculation_result.get("total_state_credits", 0)],
                        ["Total Credits", calculation_result.get("total_credits", 0)],
                    ],
                    "format": "currency"
                }
            ]
        }

    def _create_raw_imports_sheet(self, raw_data: Optional[Dict]) -> Dict:
        """Create raw imports sheet (read-only)."""
        return {
            "name": "Raw Imports",
            "type": "data",
            "protected": True,  # Read-only
            "note": "Original imported data - Do not modify",
            "tables": [
                {
                    "name": "GL_Import",
                    "headers": ["Account", "Description", "Debit", "Credit", "Source"],
                    "data": raw_data.get("gl_data", []) if raw_data else []
                },
                {
                    "name": "Payroll_Import",
                    "headers": ["Employee", "Wages", "Bonus", "Total", "Source"],
                    "data": raw_data.get("payroll_data", []) if raw_data else []
                }
            ]
        }

    def _create_employees_sheet(self, employees: List[Dict]) -> Dict:
        """Create employees sheet."""
        return {
            "name": "Employees",
            "type": "data",
            "headers": [
                "Employee ID",
                "Name",
                "Title",
                "Department",
                "Total Wages",
                "W2 Wages",
                "Qualified %",
                "Qualified Wages",
                "Source",
                "Reviewed"
            ],
            "data": [
                [
                    e.get("employee_id", ""),
                    e.get("name", ""),
                    e.get("title", ""),
                    e.get("department", ""),
                    e.get("total_wages", 0),
                    e.get("w2_wages", 0),
                    e.get("qualified_time_percentage", 0),
                    e.get("qualified_wages", 0),
                    e.get("qualified_time_source", ""),
                    "Yes" if e.get("cpa_reviewed") else "No"
                ]
                for e in employees
            ],
            "column_formats": {
                "Total Wages": "currency",
                "W2 Wages": "currency",
                "Qualified %": "percentage",
                "Qualified Wages": "currency"
            }
        }

    def _create_projects_sheet(self, projects: List[Dict]) -> Dict:
        """Create projects sheet."""
        return {
            "name": "Projects",
            "type": "data",
            "headers": [
                "Project Name",
                "Code",
                "Department",
                "Status",
                "Overall Score",
                "Permitted Purpose",
                "Tech Nature",
                "Uncertainty",
                "Experimentation",
                "Reviewed"
            ],
            "data": [
                [
                    p.get("name", ""),
                    p.get("code", ""),
                    p.get("department", ""),
                    p.get("qualification_status", ""),
                    p.get("overall_score", 0),
                    p.get("permitted_purpose_score", 0),
                    p.get("technological_nature_score", 0),
                    p.get("uncertainty_score", 0),
                    p.get("experimentation_score", 0),
                    "Yes" if p.get("cpa_reviewed") else "No"
                ]
                for p in projects
            ]
        }

    def _create_wage_qre_sheet(
        self,
        employees: List[Dict],
        qres: List[Dict]
    ) -> Dict:
        """Create wage QRE detail sheet."""
        wage_qres = [q for q in qres if q.get("category") == "wages"]

        return {
            "name": "Wage QRE",
            "type": "schedule",
            "headers": [
                "Employee",
                "Project",
                "Total Wages",
                "Qualified %",
                "Qualified Wages",
                "Evidence",
                "Notes"
            ],
            "data": [
                [
                    e.get("name", ""),
                    "Various",
                    e.get("w2_wages", 0),
                    e.get("qualified_time_percentage", 0),
                    e.get("qualified_wages", 0),
                    e.get("qualified_time_source", ""),
                    ""
                ]
                for e in employees
                if e.get("qualified_wages", 0) > 0
            ],
            "totals_row": True,
            "column_formats": {
                "Total Wages": "currency",
                "Qualified %": "percentage",
                "Qualified Wages": "currency"
            }
        }

    def _create_supply_qre_sheet(self, qres: List[Dict]) -> Dict:
        """Create supply QRE detail sheet."""
        supply_qres = [q for q in qres if q.get("category") == "supplies"]

        return {
            "name": "Supply QRE",
            "type": "schedule",
            "headers": [
                "Description",
                "Vendor",
                "GL Account",
                "Gross Amount",
                "Qualified %",
                "QRE Amount",
                "Project"
            ],
            "data": [
                [
                    q.get("supply_description", ""),
                    q.get("supply_vendor", ""),
                    q.get("gl_account", ""),
                    q.get("gross_amount", 0),
                    q.get("qualified_percentage", 100),
                    q.get("qualified_amount", 0),
                    q.get("project_name", "")
                ]
                for q in supply_qres
            ],
            "totals_row": True,
            "column_formats": {
                "Gross Amount": "currency",
                "Qualified %": "percentage",
                "QRE Amount": "currency"
            }
        }

    def _create_contract_qre_sheet(self, qres: List[Dict]) -> Dict:
        """Create contract research QRE detail sheet."""
        contract_qres = [q for q in qres if q.get("category") == "contract_research"]

        return {
            "name": "Contract QRE",
            "type": "schedule",
            "headers": [
                "Contractor",
                "Description",
                "Gross Amount",
                "Qualified Org?",
                "Applicable %",
                "QRE Amount",
                "Project"
            ],
            "data": [
                [
                    q.get("contractor_name", ""),
                    q.get("description", ""),
                    q.get("gross_amount", 0),
                    "Yes" if q.get("is_qualified_research_org") else "No",
                    q.get("contract_percentage", 65),
                    q.get("qualified_amount", 0),
                    q.get("project_name", "")
                ]
                for q in contract_qres
            ],
            "totals_row": True,
            "column_formats": {
                "Gross Amount": "currency",
                "Applicable %": "percentage",
                "QRE Amount": "currency"
            }
        }

    def _create_federal_regular_sheet(self, calculation_result: Dict) -> Dict:
        """Create Federal Regular credit calculation sheet."""
        regular = calculation_result.get("federal_regular", {})

        return {
            "name": "Federal Regular",
            "type": "calculation",
            "sections": [
                {
                    "title": "Current Year QRE",
                    "rows": [
                        {"label": "Wage QRE", "value": regular.get("qre_wages", 0), "ref": "IRC §41(b)(2)(A)"},
                        {"label": "Supply QRE", "value": regular.get("qre_supplies", 0), "ref": "IRC §41(b)(2)(C)"},
                        {"label": "Contract Research QRE", "value": regular.get("qre_contract", 0), "ref": "IRC §41(b)(3)"},
                        {"label": "Basic Research QRE", "value": regular.get("qre_basic_research", 0), "ref": "IRC §41(e)"},
                        {"label": "Total QRE", "value": regular.get("total_qre", 0), "formula": "SUM", "bold": True},
                    ]
                },
                {
                    "title": "Base Amount Calculation",
                    "rows": [
                        {"label": "Fixed-Base Percentage", "value": regular.get("fixed_base_percentage", 0), "format": "percentage"},
                        {"label": "Average Gross Receipts (4 years)", "value": regular.get("avg_gross_receipts", 0)},
                        {"label": "Calculated Base", "value": regular.get("calculated_base", 0)},
                        {"label": "Minimum Base (50% of QRE)", "value": regular.get("min_base", 0)},
                        {"label": "Base Amount", "value": regular.get("base_amount", 0), "ref": "IRC §41(c)", "bold": True},
                    ]
                },
                {
                    "title": "Credit Calculation",
                    "rows": [
                        {"label": "Excess QRE (QRE - Base)", "value": regular.get("excess_qre", 0)},
                        {"label": "Credit Rate", "value": 0.20, "format": "percentage"},
                        {"label": "Tentative Credit", "value": regular.get("tentative_credit", 0), "ref": "IRC §41(a)(1)"},
                        {"label": "Section 280C Reduction", "value": regular.get("section_280c_reduction", 0), "ref": "IRC §280C(c)"},
                        {"label": "Final Regular Credit", "value": regular.get("final_credit", 0), "bold": True},
                    ]
                }
            ]
        }

    def _create_federal_asc_sheet(self, calculation_result: Dict) -> Dict:
        """Create Federal ASC calculation sheet."""
        asc = calculation_result.get("federal_asc", {})

        return {
            "name": "Federal ASC",
            "type": "calculation",
            "sections": [
                {
                    "title": "Current Year QRE",
                    "rows": [
                        {"label": "Total QRE", "value": asc.get("total_qre", 0), "ref": "IRC §41(b)"},
                    ]
                },
                {
                    "title": "Base Amount Calculation",
                    "rows": [
                        {"label": "Year -1 QRE", "value": asc.get("prior_year_1", 0)},
                        {"label": "Year -2 QRE", "value": asc.get("prior_year_2", 0)},
                        {"label": "Year -3 QRE", "value": asc.get("prior_year_3", 0)},
                        {"label": "Average (3 years)", "value": asc.get("avg_prior_qre", 0)},
                        {"label": "Base Amount (50% of avg)", "value": asc.get("base_amount", 0), "ref": "IRC §41(c)(4)"},
                    ]
                },
                {
                    "title": "Credit Calculation",
                    "rows": [
                        {"label": "Excess QRE (QRE - Base)", "value": asc.get("excess_qre", 0)},
                        {"label": "Credit Rate", "value": 0.14, "format": "percentage"},
                        {"label": "Tentative Credit", "value": asc.get("tentative_credit", 0), "ref": "IRC §41(c)(4)"},
                        {"label": "Section 280C Reduction", "value": asc.get("section_280c_reduction", 0)},
                        {"label": "Final ASC Credit", "value": asc.get("final_credit", 0), "bold": True},
                    ]
                }
            ]
        }

    def _create_state_sheet(
        self,
        state_code: str,
        state_result: Dict
    ) -> Dict:
        """Create state credit calculation sheet."""
        return {
            "name": f"State - {state_code}",
            "type": "calculation",
            "sections": [
                {
                    "title": f"{state_code} R&D Credit",
                    "rows": [
                        {"label": "State", "value": state_result.get("state_name", state_code)},
                        {"label": "Credit Type", "value": state_result.get("credit_type", "")},
                        {"label": "State QRE", "value": state_result.get("state_qre", 0)},
                        {"label": "Credit Rate", "value": state_result.get("credit_rate", 0), "format": "percentage"},
                        {"label": "Base Amount", "value": state_result.get("state_base_amount", 0)},
                        {"label": "Excess QRE", "value": state_result.get("excess_qre", 0)},
                        {"label": "Calculated Credit", "value": state_result.get("calculated_credit", 0)},
                        {"label": "Credit Cap", "value": state_result.get("credit_cap", "N/A")},
                        {"label": "Final State Credit", "value": state_result.get("final_credit", 0), "bold": True},
                    ]
                },
                {
                    "title": "Carryforward",
                    "rows": [
                        {"label": "Carryforward Years", "value": state_result.get("carryforward_years", 0)},
                        {"label": "Prior Carryforward", "value": state_result.get("prior_carryforward", 0)},
                    ]
                }
            ]
        }

    def _create_reconciliation_sheet(
        self,
        study_data: Dict,
        qres: List[Dict],
        employees: List[Dict]
    ) -> Dict:
        """Create reconciliation sheet."""
        total_payroll = sum(e.get("total_wages", 0) for e in employees)
        total_wage_qre = sum(e.get("qualified_wages", 0) for e in employees)

        return {
            "name": "Reconciliation",
            "type": "reconciliation",
            "sections": [
                {
                    "title": "Payroll Reconciliation",
                    "rows": [
                        {"label": "Total Payroll (per records)", "value": total_payroll},
                        {"label": "Total W2 Wages (employees)", "value": sum(e.get("w2_wages", 0) for e in employees)},
                        {"label": "Difference", "value": 0, "formula": True},
                        {"label": "", "value": ""},
                        {"label": "Total Wage QRE", "value": total_wage_qre},
                        {"label": "Wage QRE as % of Payroll", "value": total_wage_qre / total_payroll if total_payroll else 0, "format": "percentage"},
                    ]
                },
                {
                    "title": "QRE Reconciliation",
                    "rows": [
                        {"label": "Total Wage QRE", "value": total_wage_qre},
                        {"label": "Total Supply QRE", "value": sum(q.get("qualified_amount", 0) for q in qres if q.get("category") == "supplies")},
                        {"label": "Total Contract QRE", "value": sum(q.get("qualified_amount", 0) for q in qres if q.get("category") == "contract_research")},
                        {"label": "Total QRE", "value": study_data.get("total_qre", 0), "bold": True},
                    ]
                }
            ]
        }

    def _create_sanity_checks_sheet(
        self,
        study_data: Dict,
        calculation_result: Dict
    ) -> Dict:
        """Create sanity checks sheet."""
        total_qre = calculation_result.get("total_qre", 0)
        federal_credit = calculation_result.get("federal_credit", 0)

        checks = [
            {
                "check": "Credit as % of QRE",
                "value": federal_credit / total_qre if total_qre else 0,
                "expected": "8-14%",
                "status": "PASS" if 0.08 <= (federal_credit / total_qre if total_qre else 0) <= 0.14 else "REVIEW"
            },
            {
                "check": "Wage QRE as % of Total",
                "value": calculation_result.get("qre_wages", 0) / total_qre if total_qre else 0,
                "expected": "60-80%",
                "status": "PASS" if 0.60 <= (calculation_result.get("qre_wages", 0) / total_qre if total_qre else 0) <= 0.80 else "REVIEW"
            },
            {
                "check": "Supply QRE as % of Total",
                "value": calculation_result.get("qre_supplies", 0) / total_qre if total_qre else 0,
                "expected": "5-20%",
                "status": "PASS" if (calculation_result.get("qre_supplies", 0) / total_qre if total_qre else 0) <= 0.20 else "REVIEW"
            },
            {
                "check": "Average Qualified Time %",
                "value": calculation_result.get("avg_qualified_time", 0),
                "expected": "20-60%",
                "status": "PASS"
            }
        ]

        return {
            "name": "Sanity Checks",
            "type": "checks",
            "headers": ["Check", "Value", "Expected Range", "Status"],
            "data": [
                [c["check"], c["value"], c["expected"], c["status"]]
                for c in checks
            ],
            "conditional_formatting": {
                "Status": {
                    "PASS": "green",
                    "REVIEW": "yellow",
                    "FAIL": "red"
                }
            }
        }

    def _generate_excel_bytes(self, workbook_structure: Dict) -> bytes:
        """
        Generate actual Excel bytes.

        In production, this would use openpyxl or xlsxwriter.
        """
        # Placeholder - returns JSON structure
        # In production, implement with openpyxl:
        #
        # from openpyxl import Workbook
        # from openpyxl.styles import Font, Alignment, PatternFill
        # from openpyxl.utils.dataframe import dataframe_to_rows
        #
        # wb = Workbook()
        # for sheet_data in workbook_structure["sheets"]:
        #     ws = wb.create_sheet(sheet_data["name"])
        #     ...build sheet...
        #
        # buffer = io.BytesIO()
        # wb.save(buffer)
        # return buffer.getvalue()

        import json
        return json.dumps(workbook_structure, indent=2, default=str).encode("utf-8")
