"""
Tests for the QRE Calculation Engine

Covers:
- Wage QRE calculations
- Supply QRE calculations
- Contract research QRE calculations
- Employee allocation validation
- Evidence strength scoring
"""

import pytest
from decimal import Decimal
from datetime import date

from app.engines.qre_engine import QREEngine
from app.engines.rules_engine import RulesEngine


class TestWageQRE:
    """Test wage QRE calculations."""

    @pytest.fixture
    def qre_engine(self):
        rules = RulesEngine()
        return QREEngine(rules)

    def test_basic_wage_qre(self, qre_engine):
        """Basic wage QRE calculation."""
        employee = {
            "id": "emp_1",
            "name": "Jane Engineer",
            "title": "Software Engineer",
            "department": "Engineering",
            "total_compensation": Decimal("150000"),
            "rd_allocation_percent": Decimal("80"),
            "projects": [
                {"project_id": "p1", "allocation_percent": Decimal("60")},
                {"project_id": "p2", "allocation_percent": Decimal("20")},
            ],
        }

        qualified_projects = {"p1": True, "p2": True}

        result = qre_engine.calculate_employee_qre(employee, qualified_projects)

        # Total R&D wages = $150K × 80% = $120,000
        assert result["total_rd_wages"] == Decimal("120000")
        # Project p1 = $150K × 60% = $90,000
        assert result["project_allocation"]["p1"] == Decimal("90000")
        # Project p2 = $150K × 20% = $30,000
        assert result["project_allocation"]["p2"] == Decimal("30000")

    def test_wage_qre_unqualified_project(self, qre_engine):
        """Wages on unqualified projects excluded."""
        employee = {
            "id": "emp_1",
            "name": "Jane Engineer",
            "title": "Software Engineer",
            "total_compensation": Decimal("100000"),
            "rd_allocation_percent": Decimal("100"),
            "projects": [
                {"project_id": "p1", "allocation_percent": Decimal("50")},
                {"project_id": "p2", "allocation_percent": Decimal("50")},
            ],
        }

        # Only p1 qualifies
        qualified_projects = {"p1": True, "p2": False}

        result = qre_engine.calculate_employee_qre(employee, qualified_projects)

        # Only p1 wages qualify
        assert result["qualified_wages"] == Decimal("50000")
        # p2 excluded
        assert result["excluded_wages"] == Decimal("50000")

    def test_wage_qre_supervising_role(self, qre_engine):
        """
        Supervisors qualify for time directly supervising R&D.

        IRC §41(b)(2)(B)(i) - Direct supervision counts.
        """
        employee = {
            "id": "emp_2",
            "name": "Tech Lead",
            "title": "Engineering Manager",
            "role_type": "supervisor",
            "total_compensation": Decimal("200000"),
            "rd_allocation_percent": Decimal("50"),  # 50% supervising R&D
            "projects": [
                {"project_id": "p1", "allocation_percent": Decimal("50")},
            ],
        }

        qualified_projects = {"p1": True}

        result = qre_engine.calculate_employee_qre(employee, qualified_projects)

        # Supervision time qualifies
        assert result["qualified_wages"] == Decimal("100000")
        assert result["activity_type"] == "supervising"

    def test_wage_qre_support_role_80_percent_rule(self, qre_engine):
        """
        Support activities require 80% threshold.

        IRC §41(b)(2)(B)(ii) - Support must be substantially all (80%+)
        for direct support.
        """
        employee = {
            "id": "emp_3",
            "name": "Lab Tech",
            "title": "Laboratory Technician",
            "role_type": "support",
            "total_compensation": Decimal("60000"),
            "rd_allocation_percent": Decimal("70"),  # Below 80%
            "projects": [
                {"project_id": "p1", "allocation_percent": Decimal("70")},
            ],
        }

        qualified_projects = {"p1": True}

        result = qre_engine.calculate_employee_qre(employee, qualified_projects)

        # Below 80% threshold - may not fully qualify
        # Engine should flag this
        assert any(f["type"] == "support_below_threshold" for f in result.get("risk_flags", []))

    def test_wage_qre_administrative_exclusion(self, qre_engine):
        """
        Administrative activities don't qualify.

        HR, finance, general management activities excluded.
        """
        employee = {
            "id": "emp_4",
            "name": "Office Manager",
            "title": "Administrative Assistant",
            "role_type": "administrative",
            "total_compensation": Decimal("50000"),
            "rd_allocation_percent": Decimal("30"),  # Claims 30% R&D
            "projects": [
                {"project_id": "p1", "allocation_percent": Decimal("30")},
            ],
        }

        qualified_projects = {"p1": True}

        result = qre_engine.calculate_employee_qre(employee, qualified_projects)

        # Administrative roles typically don't qualify
        assert result["qualified_wages"] == Decimal("0")
        assert any(f["type"] == "administrative_exclusion" for f in result.get("risk_flags", []))


class TestSupplyQRE:
    """Test supply QRE calculations."""

    @pytest.fixture
    def qre_engine(self):
        rules = RulesEngine()
        return QREEngine(rules)

    def test_basic_supply_qre(self, qre_engine):
        """Basic supply QRE calculation."""
        supplies = [
            {
                "id": "sup_1",
                "description": "Electronic components",
                "amount": Decimal("50000"),
                "project_id": "p1",
                "consumed_in_research": True,
            },
            {
                "id": "sup_2",
                "description": "Testing materials",
                "amount": Decimal("25000"),
                "project_id": "p1",
                "consumed_in_research": True,
            },
        ]

        qualified_projects = {"p1": True}

        result = qre_engine.calculate_supply_qre(supplies, qualified_projects)

        # Total = $50K + $25K = $75,000
        assert result["total_supply_qre"] == Decimal("75000")

    def test_supply_qre_land_excluded(self, qre_engine):
        """Land and improvements excluded from supply QRE."""
        supplies = [
            {
                "id": "sup_1",
                "description": "Laboratory supplies",
                "amount": Decimal("30000"),
                "project_id": "p1",
                "supply_type": "consumable",
            },
            {
                "id": "sup_2",
                "description": "Land for test facility",
                "amount": Decimal("500000"),
                "project_id": "p1",
                "supply_type": "land",
            },
        ]

        qualified_projects = {"p1": True}

        result = qre_engine.calculate_supply_qre(supplies, qualified_projects)

        # Land excluded
        assert result["total_supply_qre"] == Decimal("30000")
        assert result["excluded_items"][0]["reason"] == "land_excluded"

    def test_supply_qre_depreciable_excluded(self, qre_engine):
        """Depreciable property excluded from supply QRE."""
        supplies = [
            {
                "id": "sup_1",
                "description": "Raw materials",
                "amount": Decimal("20000"),
                "project_id": "p1",
                "supply_type": "consumable",
            },
            {
                "id": "sup_2",
                "description": "Testing equipment",
                "amount": Decimal("100000"),
                "project_id": "p1",
                "supply_type": "equipment",
                "is_depreciable": True,
            },
        ]

        qualified_projects = {"p1": True}

        result = qre_engine.calculate_supply_qre(supplies, qualified_projects)

        # Equipment excluded
        assert result["total_supply_qre"] == Decimal("20000")

    def test_supply_qre_allocation_to_projects(self, qre_engine):
        """Supplies allocated across multiple projects."""
        supplies = [
            {
                "id": "sup_1",
                "description": "Shared materials",
                "amount": Decimal("100000"),
                "project_allocations": [
                    {"project_id": "p1", "percent": Decimal("60")},
                    {"project_id": "p2", "percent": Decimal("40")},
                ],
            },
        ]

        qualified_projects = {"p1": True, "p2": False}

        result = qre_engine.calculate_supply_qre(supplies, qualified_projects)

        # Only p1 allocation qualifies (60% of $100K = $60K)
        assert result["total_supply_qre"] == Decimal("60000")


class TestContractResearchQRE:
    """Test contract research QRE calculations."""

    @pytest.fixture
    def qre_engine(self):
        rules = RulesEngine()
        return QREEngine(rules)

    def test_basic_contract_qre_65_percent(self, qre_engine):
        """Standard contract research at 65%."""
        contracts = [
            {
                "id": "con_1",
                "vendor": "Research Corp",
                "description": "Third-party development",
                "amount": Decimal("200000"),
                "project_id": "p1",
                "is_qualified_research_consortia": False,
            },
        ]

        qualified_projects = {"p1": True}

        result = qre_engine.calculate_contract_qre(contracts, qualified_projects)

        # 65% of $200K = $130,000
        assert result["total_contract_qre"] == Decimal("130000")
        assert result["contracts"][0]["applied_rate"] == Decimal("0.65")

    def test_contract_qre_consortia_75_percent(self, qre_engine):
        """Qualified research consortia at 75%."""
        contracts = [
            {
                "id": "con_1",
                "vendor": "University Research Lab",
                "description": "Basic research agreement",
                "amount": Decimal("100000"),
                "project_id": "p1",
                "is_qualified_research_consortia": True,
            },
        ]

        qualified_projects = {"p1": True}

        result = qre_engine.calculate_contract_qre(contracts, qualified_projects)

        # 75% of $100K = $75,000
        assert result["total_contract_qre"] == Decimal("75000")
        assert result["contracts"][0]["applied_rate"] == Decimal("0.75")

    def test_contract_qre_rights_retained_excluded(self, qre_engine):
        """Contract where third party retains rights excluded."""
        contracts = [
            {
                "id": "con_1",
                "vendor": "External Lab",
                "description": "Joint development",
                "amount": Decimal("150000"),
                "project_id": "p1",
                "third_party_retains_rights": True,  # Disqualifying
            },
        ]

        qualified_projects = {"p1": True}

        result = qre_engine.calculate_contract_qre(contracts, qualified_projects)

        # Excluded due to rights retention
        assert result["total_contract_qre"] == Decimal("0")
        assert result["contracts"][0]["excluded_reason"] == "third_party_rights"

    def test_contract_qre_prepaid_expenses(self, qre_engine):
        """Prepaid contract research handled correctly."""
        contracts = [
            {
                "id": "con_1",
                "vendor": "Dev Partner",
                "description": "Phase 1 development",
                "amount": Decimal("300000"),
                "project_id": "p1",
                "payment_date": date(2024, 12, 15),
                "service_period_end": date(2025, 6, 30),  # Extends to next year
            },
        ]

        qualified_projects = {"p1": True}

        result = qre_engine.calculate_contract_qre(contracts, qualified_projects, tax_year=2024)

        # Should only count portion for current tax year
        assert result["contracts"][0].get("prepaid_adjustment") is not None


class TestTotalQRESummary:
    """Test total QRE summary calculations."""

    @pytest.fixture
    def qre_engine(self):
        rules = RulesEngine()
        return QREEngine(rules)

    def test_total_qre_summary(self, qre_engine):
        """Calculate total QRE from all categories."""
        wage_result = {"qualified_wages": Decimal("500000")}
        supply_result = {"total_supply_qre": Decimal("100000")}
        contract_result = {"total_contract_qre": Decimal("65000")}

        total = qre_engine.calculate_total_qre(wage_result, supply_result, contract_result)

        assert total["total_qre"] == Decimal("665000")
        assert total["breakdown"]["wages"] == Decimal("500000")
        assert total["breakdown"]["supplies"] == Decimal("100000")
        assert total["breakdown"]["contract_research"] == Decimal("65000")

    def test_qre_by_project(self, qre_engine):
        """QRE breakdown by project."""
        employees = [
            {
                "id": "e1",
                "total_compensation": Decimal("100000"),
                "rd_allocation_percent": Decimal("100"),
                "projects": [
                    {"project_id": "p1", "allocation_percent": Decimal("60")},
                    {"project_id": "p2", "allocation_percent": Decimal("40")},
                ],
            },
        ]

        supplies = [
            {"id": "s1", "amount": Decimal("20000"), "project_id": "p1"},
        ]

        contracts = [
            {"id": "c1", "amount": Decimal("50000"), "project_id": "p2"},
        ]

        qualified_projects = {"p1": True, "p2": True}

        result = qre_engine.calculate_qre_by_project(
            employees, supplies, contracts, qualified_projects
        )

        # Project 1: $60K wages + $20K supplies = $80K
        assert result["p1"]["total_qre"] == Decimal("80000")
        # Project 2: $40K wages + $32.5K contracts (65%) = $72.5K
        assert result["p2"]["total_qre"] == Decimal("72500")


class TestEvidenceStrength:
    """Test evidence strength evaluation."""

    @pytest.fixture
    def qre_engine(self):
        rules = RulesEngine()
        return QREEngine(rules)

    def test_strong_evidence(self, qre_engine):
        """Employee with strong evidence documentation."""
        employee = {
            "id": "emp_1",
            "name": "Engineer",
            "evidence_items": [
                {"type": "timesheet", "contemporaneous": True},
                {"type": "project_log", "contemporaneous": True},
                {"type": "interview", "contemporaneous": False},
                {"type": "email_trail", "contemporaneous": True},
            ],
        }

        strength = qre_engine.evaluate_evidence_strength(employee)

        assert strength == "strong"

    def test_moderate_evidence(self, qre_engine):
        """Employee with moderate evidence."""
        employee = {
            "id": "emp_1",
            "name": "Engineer",
            "evidence_items": [
                {"type": "interview", "contemporaneous": False},
                {"type": "project_summary", "contemporaneous": False},
            ],
        }

        strength = qre_engine.evaluate_evidence_strength(employee)

        assert strength == "moderate"

    def test_weak_evidence(self, qre_engine):
        """Employee with weak/reconstructed evidence."""
        employee = {
            "id": "emp_1",
            "name": "Engineer",
            "evidence_items": [
                {"type": "estimate", "contemporaneous": False},
            ],
        }

        strength = qre_engine.evaluate_evidence_strength(employee)

        assert strength == "weak"


class TestStateQREAllocation:
    """Test QRE allocation to states."""

    @pytest.fixture
    def qre_engine(self):
        rules = RulesEngine()
        return QREEngine(rules)

    def test_state_allocation_by_employee_location(self, qre_engine):
        """Allocate QRE based on employee work location."""
        employees = [
            {
                "id": "e1",
                "work_state": "CA",
                "qualified_wages": Decimal("100000"),
            },
            {
                "id": "e2",
                "work_state": "TX",
                "qualified_wages": Decimal("80000"),
            },
            {
                "id": "e3",
                "work_state": "CA",
                "qualified_wages": Decimal("50000"),
            },
        ]

        result = qre_engine.allocate_qre_by_state(employees)

        # CA: $100K + $50K = $150K
        assert result["CA"] == Decimal("150000")
        # TX: $80K
        assert result["TX"] == Decimal("80000")

    def test_remote_employee_allocation(self, qre_engine):
        """Handle remote employees working in multiple states."""
        employees = [
            {
                "id": "e1",
                "work_locations": [
                    {"state": "CA", "percent": Decimal("60")},
                    {"state": "OR", "percent": Decimal("40")},
                ],
                "qualified_wages": Decimal("100000"),
            },
        ]

        result = qre_engine.allocate_qre_by_state(employees)

        # CA: 60% of $100K = $60K
        assert result["CA"] == Decimal("60000")
        # OR: 40% of $100K = $40K
        assert result["OR"] == Decimal("40000")
