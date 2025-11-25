"""
Tests for the Rules Engine

Covers:
- Federal 4-part test criteria
- State rules overlays
- Rules versioning
- IRC Section 41 compliance
"""

import pytest
from decimal import Decimal
from datetime import date

from app.engines.rules_engine import (
    RulesEngine,
    FederalRules,
    StateRules,
    FEDERAL_RULES_2024,
    STATE_RULES_2024,
)


class TestFederalRules:
    """Test federal R&D tax credit rules."""

    @pytest.fixture
    def rules_engine(self):
        return RulesEngine()

    def test_four_part_test_criteria_present(self, rules_engine):
        """Verify all 4-part test elements are defined."""
        rules = rules_engine.get_federal_rules()
        assert "permitted_purpose" in rules.four_part_test
        assert "technological_nature" in rules.four_part_test
        assert "elimination_of_uncertainty" in rules.four_part_test
        assert "process_of_experimentation" in rules.four_part_test

    def test_regular_credit_rate(self, rules_engine):
        """IRC §41(a)(1) - Regular credit rate is 20%."""
        rules = rules_engine.get_federal_rules()
        assert rules.regular_credit_rate == Decimal("0.20")

    def test_asc_rate(self, rules_engine):
        """IRC §41(c)(4) - ASC rate is 14%."""
        rules = rules_engine.get_federal_rules()
        assert rules.asc_rate == Decimal("0.14")

    def test_contract_research_rates(self, rules_engine):
        """IRC §41(b)(3) - Contract research rates."""
        rules = rules_engine.get_federal_rules()
        # Non-qualified small business: 65%
        assert rules.contract_research_rate == Decimal("0.65")
        # Qualified small business: 75%
        assert rules.contract_research_qualified_rate == Decimal("0.75")

    def test_basic_research_rate(self, rules_engine):
        """IRC §41(a)(2) - Basic research rate is 20%."""
        rules = rules_engine.get_federal_rules()
        assert rules.basic_research_rate == Decimal("0.20")

    def test_section_280c_rate(self, rules_engine):
        """Section 280C election - Corporate tax rate adjustment."""
        rules = rules_engine.get_federal_rules()
        # Current corporate tax rate is 21%
        assert rules.section_280c_rate == Decimal("0.21")

    def test_startup_qsb_rules(self, rules_engine):
        """IRC §41(h) - Qualified small business provisions."""
        rules = rules_engine.get_federal_rules()
        assert rules.qsb_gross_receipts_limit == Decimal("5000000")
        assert rules.qsb_payroll_offset_limit == Decimal("250000")

    def test_fixed_base_percentage_cap(self, rules_engine):
        """IRC §41(c)(3)(B) - Fixed base percentage capped at 16%."""
        rules = rules_engine.get_federal_rules()
        assert rules.max_fixed_base_percentage == Decimal("0.16")

    def test_startup_fixed_base_phase_in(self, rules_engine):
        """IRC §41(c)(3)(B)(ii) - Startup company phase-in percentages."""
        rules = rules_engine.get_federal_rules()
        phase_in = rules.startup_fixed_base_percentages
        assert phase_in["year_1"] == Decimal("0.03")
        assert phase_in["year_2"] == Decimal("0.03")
        assert phase_in["year_3"] == Decimal("0.03")
        assert phase_in["year_4"] == Decimal("0.03")
        assert phase_in["year_5"] == Decimal("0.03")
        # Years 6-10 transition to computed ratio


class TestStateRules:
    """Test state R&D tax credit rules."""

    @pytest.fixture
    def rules_engine(self):
        return RulesEngine()

    def test_california_rules(self, rules_engine):
        """California R&D credit rules."""
        rules = rules_engine.get_state_rules("CA")
        assert rules.credit_rate == Decimal("0.24")
        assert rules.carryforward_years == 0  # Indefinite
        assert rules.has_rd_credit is True

    def test_texas_rules(self, rules_engine):
        """Texas franchise tax R&D credit."""
        rules = rules_engine.get_state_rules("TX")
        assert rules.credit_type == "franchise_tax"
        assert rules.credit_rate == Decimal("0.05")

    def test_new_york_rules(self, rules_engine):
        """New York R&D credit rules."""
        rules = rules_engine.get_state_rules("NY")
        assert rules.credit_rate == Decimal("0.09")
        assert rules.cap == Decimal("10000000")

    def test_massachusetts_rules(self, rules_engine):
        """Massachusetts R&D credit."""
        rules = rules_engine.get_state_rules("MA")
        assert rules.credit_rate == Decimal("0.10")
        # MA follows federal 4-part test
        assert rules.follows_federal_qualification is True

    def test_state_without_credit(self, rules_engine):
        """States without R&D credit programs."""
        rules = rules_engine.get_state_rules("WY")  # Wyoming has no state income tax
        assert rules.has_rd_credit is False

    def test_all_states_defined(self, rules_engine):
        """Verify all major states have rules defined."""
        major_states = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
        for state in major_states:
            rules = rules_engine.get_state_rules(state)
            assert rules is not None


class TestRulesVersioning:
    """Test rules versioning and tax year applicability."""

    @pytest.fixture
    def rules_engine(self):
        return RulesEngine()

    def test_default_version(self, rules_engine):
        """Default rules version is current year."""
        assert rules_engine.version == "2024.1"

    def test_load_specific_version(self):
        """Load specific rules version."""
        engine = RulesEngine(version="2024.1")
        assert engine.version == "2024.1"

    def test_rules_effective_dates(self, rules_engine):
        """Rules have effective date ranges."""
        rules = rules_engine.get_federal_rules()
        assert rules.effective_from is not None
        assert isinstance(rules.effective_from, date)

    def test_retroactive_rule_lookup(self, rules_engine):
        """Look up rules for prior tax years."""
        # Should be able to get 2023 rules for 2023 studies
        rules = rules_engine.get_federal_rules(tax_year=2023)
        assert rules is not None


class TestIRCComplianceTests:
    """
    Compliance tests against IRC Section 41 requirements.

    These tests verify the rules engine correctly implements
    IRS regulations and can withstand audit scrutiny.
    """

    @pytest.fixture
    def rules_engine(self):
        return RulesEngine()

    def test_irc_41_b_2_wages_definition(self, rules_engine):
        """
        IRC §41(b)(2) - Wages include only amounts paid for qualified services.
        """
        rules = rules_engine.get_federal_rules()
        wage_rules = rules.qre_definitions["wages"]

        # Must be for qualified services (engaging in, supervising, supporting)
        assert "qualified_services" in wage_rules
        assert "engaging_in" in wage_rules["qualified_services"]
        assert "supervising" in wage_rules["qualified_services"]
        assert "supporting" in wage_rules["qualified_services"]

    def test_irc_41_b_2_a_supply_definition(self, rules_engine):
        """
        IRC §41(b)(2)(A) - Supplies must be consumed in qualified research.
        """
        rules = rules_engine.get_federal_rules()
        supply_rules = rules.qre_definitions["supplies"]

        # Must be tangible property consumed in research
        assert supply_rules["must_be_consumed"] is True
        assert supply_rules["tangible_property"] is True
        # Cannot be land, depreciable property
        assert "land" in supply_rules["exclusions"]
        assert "depreciable_property" in supply_rules["exclusions"]

    def test_irc_41_b_3_contract_research(self, rules_engine):
        """
        IRC §41(b)(3) - Contract research limitations.
        """
        rules = rules_engine.get_federal_rules()
        contract_rules = rules.qre_definitions["contract_research"]

        # 65% for regular contract research
        assert contract_rules["standard_rate"] == Decimal("0.65")
        # 75% for qualified research consortia
        assert contract_rules["consortia_rate"] == Decimal("0.75")
        # Cannot be for rights to research results
        assert "rights_retained" in contract_rules["requirements"]

    def test_irc_41_d_1_qualified_research_elements(self, rules_engine):
        """
        IRC §41(d)(1) - All 4 elements required for qualification.
        """
        rules = rules_engine.get_federal_rules()
        four_part = rules.four_part_test

        # All four elements must be satisfied
        assert len(four_part) == 4
        for element in four_part.values():
            assert element["required"] is True

    def test_irc_41_d_4_excluded_research(self, rules_engine):
        """
        IRC §41(d)(4) - Research excluded from credit.
        """
        rules = rules_engine.get_federal_rules()
        exclusions = rules.excluded_research

        required_exclusions = [
            "research_after_commercial_production",
            "adaptation_of_existing_products",
            "foreign_research",
            "social_sciences",
            "funded_research",
            "surveys_studies_routine_testing",
            "computer_software_for_internal_use"
        ]

        for exclusion in required_exclusions:
            assert exclusion in exclusions

    def test_irc_41_c_4_asc_computation(self, rules_engine):
        """
        IRC §41(c)(4) - ASC computation requirements.
        """
        rules = rules_engine.get_federal_rules()
        asc_rules = rules.asc_computation

        # ASC = 14% * (current QRE - 50% * average prior 3 years)
        assert asc_rules["credit_rate"] == Decimal("0.14")
        assert asc_rules["base_multiplier"] == Decimal("0.50")
        assert asc_rules["lookback_years"] == 3

        # Minimum 6% if no prior history
        assert asc_rules["minimum_rate_no_history"] == Decimal("0.06")

    def test_irc_280c_election(self, rules_engine):
        """
        Section 280C - Election to reduce credit.
        """
        rules = rules_engine.get_federal_rules()

        # Can elect reduced credit to avoid deduction reduction
        assert rules.section_280c_available is True
        # Reduction rate equals corporate tax rate
        assert rules.section_280c_rate == Decimal("0.21")


class TestAdversarialAuditScenarios:
    """
    Adversarial test cases that simulate IRS audit challenges.

    These tests ensure the system handles edge cases and
    potential audit challenges appropriately.
    """

    @pytest.fixture
    def rules_engine(self):
        return RulesEngine()

    def test_audit_challenge_generic_description(self, rules_engine):
        """
        Audit scenario: Project description is too generic.

        IRS commonly challenges vague descriptions like
        "software development" or "product improvement".
        """
        from app.engines.qualification_engine import QualificationEngine

        qual_engine = QualificationEngine(rules_engine)

        # Generic description should flag for review
        project = {
            "name": "Software Development",
            "description": "We developed software to improve our products.",
            "activities": []
        }

        result = qual_engine.evaluate_project(project)

        # Should have risk flag for generic description
        assert any(f["type"] == "generic_description" for f in result.get("risk_flags", []))
        # Should NOT auto-qualify
        assert result["auto_approved"] is False

    def test_audit_challenge_missing_uncertainty(self, rules_engine):
        """
        Audit scenario: No documented uncertainty.

        IRS requires specific technological uncertainty,
        not business uncertainty.
        """
        from app.engines.qualification_engine import QualificationEngine

        qual_engine = QualificationEngine(rules_engine)

        project = {
            "name": "Database Migration",
            "description": "Migrated database from Oracle to PostgreSQL.",
            "technological_uncertainty": None,
            "activities": [
                {"description": "Installed PostgreSQL"},
                {"description": "Wrote migration scripts"},
                {"description": "Tested data integrity"}
            ]
        }

        result = qual_engine.evaluate_project(project)

        # Elimination of uncertainty should score low
        assert result["four_part_test"]["elimination_of_uncertainty"]["score"] < 0.5
        # Should flag missing evidence
        assert any(f["type"] == "missing_evidence" for f in result.get("risk_flags", []))

    def test_audit_challenge_routine_development(self, rules_engine):
        """
        Audit scenario: Activities appear routine.

        Routine data collection, quality control, and
        testing typically don't qualify.
        """
        from app.engines.qualification_engine import QualificationEngine

        qual_engine = QualificationEngine(rules_engine)

        project = {
            "name": "Quality Improvement",
            "description": "Improved manufacturing quality.",
            "activities": [
                {"description": "Updated quality control procedures"},
                {"description": "Collected defect data"},
                {"description": "Trained staff on new procedures"}
            ]
        }

        result = qual_engine.evaluate_project(project)

        # Process of experimentation should score low
        assert result["four_part_test"]["process_of_experimentation"]["score"] < 0.5

    def test_audit_challenge_high_allocation(self, rules_engine):
        """
        Audit scenario: Suspiciously high R&D allocation.

        100% allocation for non-research roles raises red flags.
        """
        from app.engines.qre_engine import QREEngine

        qre_engine = QREEngine(rules_engine)

        employee = {
            "name": "John Smith",
            "title": "Marketing Manager",
            "department": "Marketing",
            "total_compensation": 150000,
            "rd_allocation_percent": 100,
            "projects": [{"project_id": "p1", "allocation_percent": 100}]
        }

        result = qre_engine.calculate_employee_qre(employee, {})

        # Should flag unusual allocation
        assert any(f["type"] == "high_allocation" for f in result.get("risk_flags", []))

    def test_audit_challenge_internal_use_software(self, rules_engine):
        """
        Audit scenario: Internal use software.

        IRC §41(d)(4)(E) requires high threshold of innovation
        for internal use software.
        """
        from app.engines.qualification_engine import QualificationEngine

        qual_engine = QualificationEngine(rules_engine)

        project = {
            "name": "HR System Enhancement",
            "description": "Added new features to internal HR system.",
            "is_internal_use_software": True,
            "activities": []
        }

        result = qual_engine.evaluate_project(project)

        # Should apply higher qualification threshold
        assert result.get("internal_use_software_flag") is True
        # Should require innovation, significant economic risk, unique capability

    def test_audit_challenge_funded_research(self, rules_engine):
        """
        Audit scenario: Potentially funded research.

        Research funded by contract or grant doesn't qualify.
        """
        from app.engines.qualification_engine import QualificationEngine

        qual_engine = QualificationEngine(rules_engine)

        project = {
            "name": "Government Contract Project",
            "description": "Developed system under government contract.",
            "funding_source": "government_contract",
            "activities": []
        }

        result = qual_engine.evaluate_project(project)

        # Should flag funded research exclusion
        assert result["qualification_status"] == "not_qualified"
        assert "funded_research" in result.get("exclusion_reason", "")

    def test_audit_challenge_no_documentation(self, rules_engine):
        """
        Audit scenario: Inadequate contemporaneous documentation.

        IRS requires documentation created during research,
        not reconstructed later.
        """
        from app.engines.qualification_engine import QualificationEngine

        qual_engine = QualificationEngine(rules_engine)

        project = {
            "name": "Legacy Project",
            "description": "Research conducted in tax year.",
            "evidence_items": [],
            "documentation_type": "reconstructed",
            "activities": []
        }

        result = qual_engine.evaluate_project(project)

        # Should have weak evidence rating
        assert result["evidence_strength"] in ["weak", "insufficient"]
        # Should flag documentation issue
        assert any(f["type"] == "missing_evidence" for f in result.get("risk_flags", []))
