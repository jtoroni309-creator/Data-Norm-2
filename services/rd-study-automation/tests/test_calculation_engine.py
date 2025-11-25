"""
Tests for the Calculation Engine

Covers:
- Federal Regular Credit calculation
- Alternative Simplified Credit (ASC) calculation
- State credit calculations
- Golden-file deterministic calculation verification
- Audit trail generation
"""

import pytest
from decimal import Decimal
from datetime import date
import json
import os

from app.engines.calculation_engine import CreditCalculationEngine
from app.engines.rules_engine import RulesEngine


class TestFederalRegularCredit:
    """Test Federal Regular Credit calculations per IRC §41(a)(1)."""

    @pytest.fixture
    def calc_engine(self):
        rules = RulesEngine()
        return CreditCalculationEngine(rules)

    def test_basic_regular_credit_calculation(self, calc_engine):
        """
        Basic regular credit calculation.

        Credit = 20% × (Current QRE - Base Amount)
        """
        qre_summary = {
            "total_qre": Decimal("1000000"),
            "total_wages": Decimal("700000"),
            "total_supplies": Decimal("200000"),
            "total_contract_research": Decimal("100000"),
        }

        historical_data = {
            "fixed_base_percentage": Decimal("0.03"),  # 3%
            "avg_gross_receipts_4_years": Decimal("10000000"),
        }

        result = calc_engine.calculate_federal_regular(qre_summary, historical_data)

        # Base amount = 3% × $10M = $300,000
        assert result["base_amount"] == Decimal("300000")
        # Excess QRE = $1M - $300K = $700,000
        assert result["excess_qre"] == Decimal("700000")
        # Credit = 20% × $700K = $140,000
        assert result["tentative_credit"] == Decimal("140000")

    def test_fixed_base_percentage_cap(self, calc_engine):
        """Fixed base percentage capped at 16%."""
        qre_summary = {"total_qre": Decimal("1000000")}

        historical_data = {
            "fixed_base_percentage": Decimal("0.25"),  # 25% - exceeds cap
            "avg_gross_receipts_4_years": Decimal("5000000"),
        }

        result = calc_engine.calculate_federal_regular(qre_summary, historical_data)

        # Should use 16% cap, not 25%
        # Base = 16% × $5M = $800,000
        assert result["fixed_base_percentage_used"] == Decimal("0.16")
        assert result["base_amount"] == Decimal("800000")

    def test_minimum_base_50_percent_current_qre(self, calc_engine):
        """
        Base amount cannot be less than 50% of current QRE.

        This prevents excessive credits when base is artificially low.
        """
        qre_summary = {"total_qre": Decimal("1000000")}

        historical_data = {
            "fixed_base_percentage": Decimal("0.01"),  # 1% - very low
            "avg_gross_receipts_4_years": Decimal("1000000"),
        }

        result = calc_engine.calculate_federal_regular(qre_summary, historical_data)

        # Calculated base = 1% × $1M = $10,000
        # Minimum base = 50% × $1M QRE = $500,000
        # Should use minimum
        assert result["base_amount"] >= Decimal("500000")

    def test_startup_company_fixed_base(self, calc_engine):
        """
        Startup companies use prescribed base percentages.

        Years 1-5: 3%
        Years 6-10: Transition to computed percentage
        """
        qre_summary = {"total_qre": Decimal("500000")}

        # First year taxpayer
        historical_data = {
            "is_startup": True,
            "tax_year_number": 1,
            "avg_gross_receipts_4_years": Decimal("2000000"),
        }

        result = calc_engine.calculate_federal_regular(qre_summary, historical_data)

        # Year 1 uses 3%
        assert result["fixed_base_percentage_used"] == Decimal("0.03")
        # Base = 3% × $2M = $60,000
        assert result["base_amount"] == Decimal("60000")

    def test_no_credit_when_qre_below_base(self, calc_engine):
        """No credit when current QRE is below base amount."""
        qre_summary = {"total_qre": Decimal("100000")}

        historical_data = {
            "fixed_base_percentage": Decimal("0.10"),
            "avg_gross_receipts_4_years": Decimal("5000000"),
        }

        result = calc_engine.calculate_federal_regular(qre_summary, historical_data)

        # Base = 10% × $5M = $500,000
        # QRE = $100,000 < Base, so no credit
        assert result["excess_qre"] == Decimal("0")
        assert result["tentative_credit"] == Decimal("0")


class TestAlternativeSimplifiedCredit:
    """Test ASC calculations per IRC §41(c)(4)."""

    @pytest.fixture
    def calc_engine(self):
        rules = RulesEngine()
        return CreditCalculationEngine(rules)

    def test_basic_asc_calculation(self, calc_engine):
        """
        Basic ASC calculation.

        Credit = 14% × (Current QRE - 50% × Average Prior 3 Years QRE)
        """
        qre_summary = {"total_qre": Decimal("1000000")}

        historical_data = {
            "prior_year_1_qre": Decimal("800000"),
            "prior_year_2_qre": Decimal("700000"),
            "prior_year_3_qre": Decimal("600000"),
        }

        result = calc_engine.calculate_federal_asc(qre_summary, historical_data)

        # Avg prior 3 years = ($800K + $700K + $600K) / 3 = $700,000
        assert result["avg_prior_qre"] == Decimal("700000")
        # Base = 50% × $700K = $350,000
        assert result["base_amount"] == Decimal("350000")
        # Excess = $1M - $350K = $650,000
        assert result["excess_qre"] == Decimal("650000")
        # Credit = 14% × $650K = $91,000
        assert result["tentative_credit"] == Decimal("91000")

    def test_asc_no_prior_history(self, calc_engine):
        """
        ASC with no prior QRE history.

        Uses 6% rate instead of 14% when no prior history.
        """
        qre_summary = {"total_qre": Decimal("500000")}

        historical_data = {
            "prior_year_1_qre": Decimal("0"),
            "prior_year_2_qre": Decimal("0"),
            "prior_year_3_qre": Decimal("0"),
        }

        result = calc_engine.calculate_federal_asc(qre_summary, historical_data)

        # No prior history = 6% of current QRE
        # Credit = 6% × $500K = $30,000
        assert result["tentative_credit"] == Decimal("30000")
        assert result["applied_rate"] == Decimal("0.06")

    def test_asc_partial_prior_history(self, calc_engine):
        """ASC with partial prior history (less than 3 years)."""
        qre_summary = {"total_qre": Decimal("600000")}

        historical_data = {
            "prior_year_1_qre": Decimal("400000"),
            "prior_year_2_qre": Decimal("0"),  # No QRE in year 2
            "prior_year_3_qre": Decimal("0"),  # No QRE in year 3
        }

        result = calc_engine.calculate_federal_asc(qre_summary, historical_data)

        # Only 1 year of prior QRE
        # Should still calculate average using available data
        assert result["avg_prior_qre"] >= Decimal("0")


class TestSection280CElection:
    """Test Section 280C reduced credit election."""

    @pytest.fixture
    def calc_engine(self):
        rules = RulesEngine()
        return CreditCalculationEngine(rules)

    def test_280c_reduction(self, calc_engine):
        """
        280C election reduces credit but avoids deduction adjustment.

        Reduced credit = Tentative credit × (1 - corporate tax rate)
        """
        qre_summary = {"total_qre": Decimal("1000000")}
        historical_data = {"prior_year_1_qre": Decimal("500000"),
                          "prior_year_2_qre": Decimal("500000"),
                          "prior_year_3_qre": Decimal("500000")}

        result = calc_engine.calculate_federal_asc(qre_summary, historical_data, section_280c=True)

        # Tentative credit before 280C
        tentative = result["tentative_credit"]
        # 280C reduction = tentative × 21%
        reduction = tentative * Decimal("0.21")
        # Final credit
        final = tentative - reduction

        assert result["section_280c_reduction"] == reduction
        assert result["final_credit"] == final

    def test_without_280c_election(self, calc_engine):
        """Without 280C election, full credit but must adjust deductions."""
        qre_summary = {"total_qre": Decimal("1000000")}
        historical_data = {"prior_year_1_qre": Decimal("500000"),
                          "prior_year_2_qre": Decimal("500000"),
                          "prior_year_3_qre": Decimal("500000")}

        result = calc_engine.calculate_federal_asc(qre_summary, historical_data, section_280c=False)

        # No reduction
        assert result["section_280c_reduction"] == Decimal("0")
        assert result["final_credit"] == result["tentative_credit"]
        # Should note deduction adjustment required
        assert result["requires_deduction_adjustment"] is True


class TestStateCredits:
    """Test state R&D credit calculations."""

    @pytest.fixture
    def calc_engine(self):
        rules = RulesEngine()
        return CreditCalculationEngine(rules)

    def test_california_credit(self, calc_engine):
        """California credit at 24% of excess QRE."""
        qre_summary = {"total_qre": Decimal("1000000")}
        state_allocation = {"CA": Decimal("0.60")}  # 60% California

        historical_data = {
            "prior_year_1_qre": Decimal("500000"),
            "prior_year_2_qre": Decimal("500000"),
            "prior_year_3_qre": Decimal("500000"),
        }

        result = calc_engine.calculate_state_credits(
            qre_summary, historical_data, state_allocation
        )

        assert "CA" in result
        # CA QRE = 60% × $1M = $600,000
        assert result["CA"]["allocated_qre"] == Decimal("600000")
        # CA credit rate = 24%
        assert result["CA"]["credit_rate"] == Decimal("0.24")

    def test_texas_franchise_tax_credit(self, calc_engine):
        """Texas credit against franchise tax."""
        qre_summary = {"total_qre": Decimal("500000")}
        state_allocation = {"TX": Decimal("1.00")}

        result = calc_engine.calculate_state_credits(
            qre_summary, {}, state_allocation
        )

        assert "TX" in result
        assert result["TX"]["credit_type"] == "franchise_tax"
        assert result["TX"]["credit_rate"] == Decimal("0.05")

    def test_multi_state_allocation(self, calc_engine):
        """Credits allocated across multiple states."""
        qre_summary = {"total_qre": Decimal("1000000")}
        state_allocation = {
            "CA": Decimal("0.40"),
            "TX": Decimal("0.30"),
            "NY": Decimal("0.30"),
        }

        result = calc_engine.calculate_state_credits(
            qre_summary, {}, state_allocation
        )

        # Should have calculations for all states
        assert len(result) == 3
        # Allocations should be correct
        assert result["CA"]["allocated_qre"] == Decimal("400000")
        assert result["TX"]["allocated_qre"] == Decimal("300000")
        assert result["NY"]["allocated_qre"] == Decimal("300000")

    def test_state_credit_cap(self, calc_engine):
        """New York credit capped at $10M."""
        qre_summary = {"total_qre": Decimal("200000000")}  # Large company
        state_allocation = {"NY": Decimal("1.00")}

        result = calc_engine.calculate_state_credits(
            qre_summary, {}, state_allocation
        )

        # Credit should not exceed $10M cap
        assert result["NY"]["final_credit"] <= Decimal("10000000")


class TestGoldenFileCalculations:
    """
    Golden-file tests for calculation verification.

    These tests use pre-computed expected results to ensure
    calculation determinism and accuracy.
    """

    @pytest.fixture
    def calc_engine(self):
        rules = RulesEngine()
        return CreditCalculationEngine(rules)

    # Golden file test cases
    GOLDEN_FILES = [
        {
            "name": "software_company_asc",
            "inputs": {
                "qre_summary": {
                    "total_qre": Decimal("2500000"),
                    "total_wages": Decimal("2000000"),
                    "total_supplies": Decimal("300000"),
                    "total_contract_research": Decimal("200000"),
                },
                "historical_data": {
                    "prior_year_1_qre": Decimal("2000000"),
                    "prior_year_2_qre": Decimal("1800000"),
                    "prior_year_3_qre": Decimal("1500000"),
                },
                "method": "asc",
                "section_280c": True,
            },
            "expected": {
                "avg_prior_qre": Decimal("1766666.67"),
                "base_amount": Decimal("883333.33"),
                "excess_qre": Decimal("1616666.67"),
                "tentative_credit": Decimal("226333.33"),
                "section_280c_reduction": Decimal("47530.00"),
                "final_credit": Decimal("178803.33"),
            },
        },
        {
            "name": "manufacturer_regular",
            "inputs": {
                "qre_summary": {
                    "total_qre": Decimal("5000000"),
                    "total_wages": Decimal("3500000"),
                    "total_supplies": Decimal("1000000"),
                    "total_contract_research": Decimal("500000"),
                },
                "historical_data": {
                    "fixed_base_percentage": Decimal("0.08"),
                    "avg_gross_receipts_4_years": Decimal("25000000"),
                },
                "method": "regular",
                "section_280c": True,
            },
            "expected": {
                "base_amount": Decimal("2000000"),
                "excess_qre": Decimal("3000000"),
                "tentative_credit": Decimal("600000"),
                "section_280c_reduction": Decimal("126000"),
                "final_credit": Decimal("474000"),
            },
        },
        {
            "name": "startup_year_2",
            "inputs": {
                "qre_summary": {
                    "total_qre": Decimal("750000"),
                },
                "historical_data": {
                    "is_startup": True,
                    "tax_year_number": 2,
                    "avg_gross_receipts_4_years": Decimal("3000000"),
                },
                "method": "regular",
                "section_280c": True,
            },
            "expected": {
                "fixed_base_percentage_used": Decimal("0.03"),
                "base_amount": Decimal("90000"),
                "excess_qre": Decimal("660000"),
                "tentative_credit": Decimal("132000"),
                "section_280c_reduction": Decimal("27720"),
                "final_credit": Decimal("104280"),
            },
        },
    ]

    @pytest.mark.parametrize("golden_case", GOLDEN_FILES, ids=lambda x: x["name"])
    def test_golden_file_calculation(self, calc_engine, golden_case):
        """Verify calculations match pre-computed golden files."""
        inputs = golden_case["inputs"]
        expected = golden_case["expected"]

        if inputs["method"] == "asc":
            result = calc_engine.calculate_federal_asc(
                inputs["qre_summary"],
                inputs["historical_data"],
                section_280c=inputs["section_280c"],
            )
        else:
            result = calc_engine.calculate_federal_regular(
                inputs["qre_summary"],
                inputs["historical_data"],
                section_280c=inputs["section_280c"],
            )

        # Compare key values with tolerance for rounding
        for key, expected_value in expected.items():
            if key in result:
                actual = result[key]
                # Allow 0.01% tolerance for rounding differences
                tolerance = abs(expected_value) * Decimal("0.0001")
                assert abs(actual - expected_value) <= tolerance, \
                    f"Mismatch in {golden_case['name']}.{key}: expected {expected_value}, got {actual}"


class TestAuditTrail:
    """Test audit trail generation for calculations."""

    @pytest.fixture
    def calc_engine(self):
        rules = RulesEngine()
        return CreditCalculationEngine(rules)

    def test_calculation_steps_recorded(self, calc_engine):
        """All calculation steps are recorded with citations."""
        qre_summary = {"total_qre": Decimal("1000000")}
        historical_data = {
            "prior_year_1_qre": Decimal("800000"),
            "prior_year_2_qre": Decimal("700000"),
            "prior_year_3_qre": Decimal("600000"),
        }

        result = calc_engine.calculate_federal_asc(qre_summary, historical_data)

        # Should have audit trail
        assert "audit_trail" in result
        audit_trail = result["audit_trail"]

        # Each step should have required fields
        for step in audit_trail:
            assert "step_number" in step
            assert "description" in step
            assert "formula" in step
            assert "inputs" in step
            assert "result" in step
            assert "irc_citation" in step

    def test_irc_citations_present(self, calc_engine):
        """Calculations reference appropriate IRC sections."""
        qre_summary = {"total_qre": Decimal("1000000")}
        historical_data = {"prior_year_1_qre": Decimal("800000"),
                          "prior_year_2_qre": Decimal("700000"),
                          "prior_year_3_qre": Decimal("600000")}

        result = calc_engine.calculate_federal_asc(qre_summary, historical_data)

        audit_trail = result.get("audit_trail", [])

        # Should cite IRC §41(c)(4) for ASC
        citations = [step.get("irc_citation", "") for step in audit_trail]
        assert any("41(c)(4)" in c for c in citations)

    def test_calculation_reproducibility(self, calc_engine):
        """Same inputs produce identical results."""
        qre_summary = {"total_qre": Decimal("1000000")}
        historical_data = {"prior_year_1_qre": Decimal("800000"),
                          "prior_year_2_qre": Decimal("700000"),
                          "prior_year_3_qre": Decimal("600000")}

        result1 = calc_engine.calculate_federal_asc(qre_summary, historical_data)
        result2 = calc_engine.calculate_federal_asc(qre_summary, historical_data)

        # Results should be identical
        assert result1["final_credit"] == result2["final_credit"]
        assert result1["tentative_credit"] == result2["tentative_credit"]


class TestControlledGroupAllocation:
    """Test controlled group credit allocation."""

    @pytest.fixture
    def calc_engine(self):
        rules = RulesEngine()
        return CreditCalculationEngine(rules)

    def test_controlled_group_allocation(self, calc_engine):
        """Credits allocated among controlled group members."""
        group_members = [
            {"entity_id": "parent", "qre": Decimal("2000000")},
            {"entity_id": "sub_1", "qre": Decimal("1500000")},
            {"entity_id": "sub_2", "qre": Decimal("500000")},
        ]

        total_credit = Decimal("400000")

        result = calc_engine.allocate_controlled_group(group_members, total_credit)

        # Total QRE = $4M
        # Parent gets 50%, Sub1 gets 37.5%, Sub2 gets 12.5%
        assert result["parent"]["allocated_credit"] == Decimal("200000")
        assert result["sub_1"]["allocated_credit"] == Decimal("150000")
        assert result["sub_2"]["allocated_credit"] == Decimal("50000")

        # Total allocated should equal total credit
        total_allocated = sum(m["allocated_credit"] for m in result.values())
        assert total_allocated == total_credit


class TestQSBPayrollOffset:
    """Test qualified small business payroll tax offset."""

    @pytest.fixture
    def calc_engine(self):
        rules = RulesEngine()
        return CreditCalculationEngine(rules)

    def test_qsb_payroll_offset_eligible(self, calc_engine):
        """
        QSB with gross receipts < $5M can elect payroll offset.

        Up to $250,000 against payroll tax.
        """
        company_data = {
            "gross_receipts": Decimal("3000000"),  # Under $5M
            "years_with_gross_receipts": 4,  # Less than 5 years
        }

        credit_amount = Decimal("300000")

        result = calc_engine.calculate_qsb_offset(company_data, credit_amount)

        # Eligible for payroll offset
        assert result["payroll_offset_eligible"] is True
        # Offset limited to $250K
        assert result["payroll_offset_amount"] == Decimal("250000")
        # Remaining credit against income tax
        assert result["income_tax_credit"] == Decimal("50000")

    def test_qsb_not_eligible_high_receipts(self, calc_engine):
        """Company with > $5M gross receipts not eligible."""
        company_data = {
            "gross_receipts": Decimal("10000000"),
            "years_with_gross_receipts": 3,
        }

        result = calc_engine.calculate_qsb_offset(company_data, Decimal("100000"))

        assert result["payroll_offset_eligible"] is False
