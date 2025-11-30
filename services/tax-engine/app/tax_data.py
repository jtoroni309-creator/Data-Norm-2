"""
Tax Data - Brackets, Rules, Thresholds, and Limits

All configurable tax data for 2023-2025 tax years.
This data should be loaded into the database for production use.
NO HARDCODED VALUES in calculators - all rules loaded from here.
"""
from decimal import Decimal
from typing import Dict, List, Any


# ========================================
# Federal Tax Brackets 2024
# ========================================

TAX_BRACKETS_2024 = {
    # Ordinary Income Brackets
    "ordinary_single": [
        {"min": 0, "max": 11600, "rate": 0.10},
        {"min": 11600, "max": 47150, "rate": 0.12},
        {"min": 47150, "max": 100525, "rate": 0.22},
        {"min": 100525, "max": 191950, "rate": 0.24},
        {"min": 191950, "max": 243725, "rate": 0.32},
        {"min": 243725, "max": 609350, "rate": 0.35},
        {"min": 609350, "max": None, "rate": 0.37},
    ],
    "ordinary_married_filing_jointly": [
        {"min": 0, "max": 23200, "rate": 0.10},
        {"min": 23200, "max": 94300, "rate": 0.12},
        {"min": 94300, "max": 201050, "rate": 0.22},
        {"min": 201050, "max": 383900, "rate": 0.24},
        {"min": 383900, "max": 487450, "rate": 0.32},
        {"min": 487450, "max": 731200, "rate": 0.35},
        {"min": 731200, "max": None, "rate": 0.37},
    ],
    "ordinary_married_filing_separately": [
        {"min": 0, "max": 11600, "rate": 0.10},
        {"min": 11600, "max": 47150, "rate": 0.12},
        {"min": 47150, "max": 100525, "rate": 0.22},
        {"min": 100525, "max": 191950, "rate": 0.24},
        {"min": 191950, "max": 243725, "rate": 0.32},
        {"min": 243725, "max": 365600, "rate": 0.35},
        {"min": 365600, "max": None, "rate": 0.37},
    ],
    "ordinary_head_of_household": [
        {"min": 0, "max": 16550, "rate": 0.10},
        {"min": 16550, "max": 63100, "rate": 0.12},
        {"min": 63100, "max": 100500, "rate": 0.22},
        {"min": 100500, "max": 191950, "rate": 0.24},
        {"min": 191950, "max": 243700, "rate": 0.32},
        {"min": 243700, "max": 609350, "rate": 0.35},
        {"min": 609350, "max": None, "rate": 0.37},
    ],

    # Capital Gains Brackets 2024
    "capital_gains_single": [
        {"min": 0, "max": 47025, "rate": 0.00},
        {"min": 47025, "max": 518900, "rate": 0.15},
        {"min": 518900, "max": None, "rate": 0.20},
    ],
    "capital_gains_married_filing_jointly": [
        {"min": 0, "max": 94050, "rate": 0.00},
        {"min": 94050, "max": 583750, "rate": 0.15},
        {"min": 583750, "max": None, "rate": 0.20},
    ],
    "capital_gains_married_filing_separately": [
        {"min": 0, "max": 47025, "rate": 0.00},
        {"min": 47025, "max": 291850, "rate": 0.15},
        {"min": 291850, "max": None, "rate": 0.20},
    ],
    "capital_gains_head_of_household": [
        {"min": 0, "max": 63000, "rate": 0.00},
        {"min": 63000, "max": 551350, "rate": 0.15},
        {"min": 551350, "max": None, "rate": 0.20},
    ],

    # Trust/Estate Brackets 2024 (compressed)
    "trust_estate": [
        {"min": 0, "max": 3100, "rate": 0.10},
        {"min": 3100, "max": 11150, "rate": 0.24},
        {"min": 11150, "max": 15200, "rate": 0.35},
        {"min": 15200, "max": None, "rate": 0.37},
    ],

    # Trust/Estate Capital Gains 2024
    "trust_capital_gains": [
        {"min": 0, "max": 3150, "rate": 0.00},
        {"min": 3150, "max": 15450, "rate": 0.15},
        {"min": 15450, "max": None, "rate": 0.20},
    ],
}


# ========================================
# Federal Tax Brackets 2023 (for prior year)
# ========================================

TAX_BRACKETS_2023 = {
    "ordinary_single": [
        {"min": 0, "max": 11000, "rate": 0.10},
        {"min": 11000, "max": 44725, "rate": 0.12},
        {"min": 44725, "max": 95375, "rate": 0.22},
        {"min": 95375, "max": 182100, "rate": 0.24},
        {"min": 182100, "max": 231250, "rate": 0.32},
        {"min": 231250, "max": 578125, "rate": 0.35},
        {"min": 578125, "max": None, "rate": 0.37},
    ],
    "ordinary_married_filing_jointly": [
        {"min": 0, "max": 22000, "rate": 0.10},
        {"min": 22000, "max": 89450, "rate": 0.12},
        {"min": 89450, "max": 190750, "rate": 0.22},
        {"min": 190750, "max": 364200, "rate": 0.24},
        {"min": 364200, "max": 462500, "rate": 0.32},
        {"min": 462500, "max": 693750, "rate": 0.35},
        {"min": 693750, "max": None, "rate": 0.37},
    ],
    # ... similar for other filing statuses
}


# ========================================
# Standard Deductions
# ========================================

STANDARD_DEDUCTIONS = {
    2024: {
        "single": Decimal("14600"),
        "married_filing_jointly": Decimal("29200"),
        "married_filing_separately": Decimal("14600"),
        "head_of_household": Decimal("21900"),
        "qualifying_surviving_spouse": Decimal("29200"),
        # Additional for age 65+ or blind
        "additional_single": Decimal("1950"),
        "additional_married": Decimal("1550"),
    },
    2023: {
        "single": Decimal("13850"),
        "married_filing_jointly": Decimal("27700"),
        "married_filing_separately": Decimal("13850"),
        "head_of_household": Decimal("20800"),
        "qualifying_surviving_spouse": Decimal("27700"),
        "additional_single": Decimal("1850"),
        "additional_married": Decimal("1500"),
    },
    2025: {
        # Projected 2025 (will be updated when IRS releases)
        "single": Decimal("15000"),
        "married_filing_jointly": Decimal("30000"),
        "married_filing_separately": Decimal("15000"),
        "head_of_household": Decimal("22500"),
        "qualifying_surviving_spouse": Decimal("30000"),
        "additional_single": Decimal("2000"),
        "additional_married": Decimal("1600"),
    },
}


# ========================================
# Social Security and Medicare
# ========================================

SOCIAL_SECURITY_LIMITS = {
    2024: {
        "wage_base": Decimal("168600"),
        "ss_rate_employee": Decimal("0.062"),
        "ss_rate_employer": Decimal("0.062"),
        "ss_rate_self_employed": Decimal("0.124"),
        "medicare_rate_employee": Decimal("0.0145"),
        "medicare_rate_employer": Decimal("0.0145"),
        "medicare_rate_self_employed": Decimal("0.029"),
        "additional_medicare_threshold_single": Decimal("200000"),
        "additional_medicare_threshold_mfj": Decimal("250000"),
        "additional_medicare_threshold_mfs": Decimal("125000"),
        "additional_medicare_rate": Decimal("0.009"),
    },
    2023: {
        "wage_base": Decimal("160200"),
        "ss_rate_employee": Decimal("0.062"),
        "medicare_rate_employee": Decimal("0.0145"),
        # ... similar
    },
    2025: {
        "wage_base": Decimal("176100"),  # Projected
        "ss_rate_employee": Decimal("0.062"),
        "medicare_rate_employee": Decimal("0.0145"),
        # ... similar
    },
}


# ========================================
# Alternative Minimum Tax (AMT)
# ========================================

AMT_LIMITS = {
    2024: {
        "exemption_single": Decimal("85700"),
        "exemption_mfj": Decimal("133300"),
        "exemption_mfs": Decimal("66650"),
        "phase_out_single": Decimal("609350"),
        "phase_out_mfj": Decimal("1218700"),
        "phase_out_mfs": Decimal("609350"),
        "rate_breakpoint_single": Decimal("220700"),
        "rate_breakpoint_mfj": Decimal("220700"),
        "rate_26_pct": Decimal("0.26"),
        "rate_28_pct": Decimal("0.28"),
    },
    2023: {
        "exemption_single": Decimal("81300"),
        "exemption_mfj": Decimal("126500"),
        "exemption_mfs": Decimal("63250"),
        "phase_out_single": Decimal("578150"),
        "phase_out_mfj": Decimal("1156300"),
        "phase_out_mfs": Decimal("578150"),
        # ...
    },
}


# ========================================
# Net Investment Income Tax (NIIT)
# ========================================

NIIT_THRESHOLDS = {
    2024: {
        "single": Decimal("200000"),
        "married_filing_jointly": Decimal("250000"),
        "married_filing_separately": Decimal("125000"),
        "head_of_household": Decimal("200000"),
        "rate": Decimal("0.038"),
    },
}


# ========================================
# Child Tax Credit
# ========================================

CHILD_TAX_CREDIT = {
    2024: {
        "credit_per_child": Decimal("2000"),
        "credit_per_other_dependent": Decimal("500"),
        "refundable_max": Decimal("1700"),  # Additional child tax credit
        "phase_out_single": Decimal("200000"),
        "phase_out_mfj": Decimal("400000"),
        "phase_out_rate": Decimal("50"),  # $50 per $1,000 over threshold
        "earned_income_threshold": Decimal("2500"),  # For refundable portion
    },
    2023: {
        "credit_per_child": Decimal("2000"),
        "credit_per_other_dependent": Decimal("500"),
        "refundable_max": Decimal("1600"),
        "phase_out_single": Decimal("200000"),
        "phase_out_mfj": Decimal("400000"),
        # ...
    },
}


# ========================================
# Earned Income Credit (EIC)
# ========================================

EIC_PARAMETERS = {
    2024: {
        "investment_income_limit": Decimal("11600"),
        # Credit amounts and phase-out thresholds by number of children
        "no_children": {
            "max_credit": Decimal("632"),
            "earned_income_max": Decimal("7840"),
            "phase_out_start_single": Decimal("10330"),
            "phase_out_start_mfj": Decimal("17250"),
            "phase_out_complete_single": Decimal("18591"),
            "phase_out_complete_mfj": Decimal("25511"),
            "age_min": 25,
            "age_max": 64,
        },
        "one_child": {
            "max_credit": Decimal("4213"),
            "earned_income_max": Decimal("12390"),
            "phase_out_start_single": Decimal("22720"),
            "phase_out_start_mfj": Decimal("29640"),
            "phase_out_complete_single": Decimal("49084"),
            "phase_out_complete_mfj": Decimal("56004"),
        },
        "two_children": {
            "max_credit": Decimal("6960"),
            "earned_income_max": Decimal("17400"),
            "phase_out_start_single": Decimal("22720"),
            "phase_out_start_mfj": Decimal("29640"),
            "phase_out_complete_single": Decimal("55768"),
            "phase_out_complete_mfj": Decimal("62688"),
        },
        "three_or_more_children": {
            "max_credit": Decimal("7830"),
            "earned_income_max": Decimal("17400"),
            "phase_out_start_single": Decimal("22720"),
            "phase_out_start_mfj": Decimal("29640"),
            "phase_out_complete_single": Decimal("59899"),
            "phase_out_complete_mfj": Decimal("66819"),
        },
    },
}


# ========================================
# Education Credits
# ========================================

EDUCATION_CREDITS = {
    2024: {
        "american_opportunity": {
            "max_credit": Decimal("2500"),
            "expenses_100_pct": Decimal("2000"),  # 100% of first $2,000
            "expenses_25_pct": Decimal("2000"),   # 25% of next $2,000
            "refundable_pct": Decimal("0.40"),    # 40% refundable
            "phase_out_start_single": Decimal("80000"),
            "phase_out_start_mfj": Decimal("160000"),
            "phase_out_range": Decimal("10000"),
            "max_years": 4,
        },
        "lifetime_learning": {
            "max_credit": Decimal("2000"),
            "credit_rate": Decimal("0.20"),  # 20% of first $10,000
            "phase_out_start_single": Decimal("80000"),
            "phase_out_start_mfj": Decimal("160000"),
            "phase_out_range": Decimal("10000"),
        },
    },
}


# ========================================
# Retirement Contribution Limits
# ========================================

RETIREMENT_LIMITS = {
    2024: {
        "401k_limit": Decimal("23000"),
        "401k_catch_up": Decimal("7500"),
        "ira_limit": Decimal("7000"),
        "ira_catch_up": Decimal("1000"),
        "simple_limit": Decimal("16000"),
        "simple_catch_up": Decimal("3500"),
        "sep_limit_pct": Decimal("0.25"),
        "sep_max": Decimal("69000"),
        "defined_benefit_max": Decimal("275000"),
        "hsa_individual": Decimal("4150"),
        "hsa_family": Decimal("8300"),
        "hsa_catch_up": Decimal("1000"),
        "catch_up_age": 50,
    },
    2023: {
        "401k_limit": Decimal("22500"),
        "401k_catch_up": Decimal("7500"),
        "ira_limit": Decimal("6500"),
        "ira_catch_up": Decimal("1000"),
        # ...
    },
}


# ========================================
# QBI Deduction (§199A)
# ========================================

QBI_LIMITS = {
    2024: {
        "deduction_rate": Decimal("0.20"),
        "threshold_single": Decimal("191950"),
        "threshold_mfj": Decimal("383900"),
        "phase_out_range_single": Decimal("50000"),
        "phase_out_range_mfj": Decimal("100000"),
        "w2_wage_limit_pct": Decimal("0.50"),  # 50% of W-2 wages
        "wage_ubia_limit": Decimal("0.25"),    # 25% wages + 2.5% UBIA
        "ubia_pct": Decimal("0.025"),
    },
}


# ========================================
# SALT Cap
# ========================================

SALT_LIMITS = {
    2024: {"cap": Decimal("10000")},
    2023: {"cap": Decimal("10000")},
    2025: {"cap": Decimal("10000")},  # Scheduled to expire after 2025
}


# ========================================
# Foreign Earned Income Exclusion
# ========================================

FOREIGN_INCOME = {
    2024: {
        "exclusion": Decimal("126500"),
        "housing_base": Decimal("19448"),  # 16% of exclusion
        "housing_max_default": Decimal("37960"),  # 30% of exclusion
    },
    2023: {
        "exclusion": Decimal("120000"),
        # ...
    },
}


# ========================================
# Gift and Estate Tax
# ========================================

GIFT_ESTATE = {
    2024: {
        "annual_exclusion": Decimal("18000"),
        "annual_exclusion_spouse": Decimal("185000"),  # Non-citizen spouse
        "lifetime_exemption": Decimal("13610000"),
        "top_rate": Decimal("0.40"),
    },
    2023: {
        "annual_exclusion": Decimal("17000"),
        "lifetime_exemption": Decimal("12920000"),
        # ...
    },
}


# ========================================
# Corporate Tax
# ========================================

CORPORATE_TAX = {
    2024: {
        "flat_rate": Decimal("0.21"),
        "accumulated_earnings_rate": Decimal("0.20"),
        "personal_holding_company_rate": Decimal("0.20"),
    },
}


# ========================================
# State Tax Data (Sample - would be comprehensive in production)
# ========================================

STATE_TAX_DATA = {
    "CA": {
        "name": "California",
        "has_income_tax": True,
        "brackets_single_2024": [
            {"min": 0, "max": 10412, "rate": 0.01},
            {"min": 10412, "max": 24684, "rate": 0.02},
            {"min": 24684, "max": 38959, "rate": 0.04},
            {"min": 38959, "max": 54081, "rate": 0.06},
            {"min": 54081, "max": 68350, "rate": 0.08},
            {"min": 68350, "max": 349137, "rate": 0.093},
            {"min": 349137, "max": 418961, "rate": 0.103},
            {"min": 418961, "max": 698271, "rate": 0.113},
            {"min": 698271, "max": None, "rate": 0.123},
        ],
        "standard_deduction_single": Decimal("5363"),
        "standard_deduction_mfj": Decimal("10726"),
        "exemption_credit": Decimal("144"),
    },
    "NY": {
        "name": "New York",
        "has_income_tax": True,
        "brackets_single_2024": [
            {"min": 0, "max": 8500, "rate": 0.04},
            {"min": 8500, "max": 11700, "rate": 0.045},
            {"min": 11700, "max": 13900, "rate": 0.0525},
            {"min": 13900, "max": 80650, "rate": 0.0585},
            {"min": 80650, "max": 215400, "rate": 0.0625},
            {"min": 215400, "max": 1077550, "rate": 0.0685},
            {"min": 1077550, "max": 5000000, "rate": 0.0965},
            {"min": 5000000, "max": 25000000, "rate": 0.103},
            {"min": 25000000, "max": None, "rate": 0.109},
        ],
        "standard_deduction_single": Decimal("8000"),
        "standard_deduction_mfj": Decimal("16050"),
    },
    "TX": {
        "name": "Texas",
        "has_income_tax": False,
    },
    "FL": {
        "name": "Florida",
        "has_income_tax": False,
    },
    "WA": {
        "name": "Washington",
        "has_income_tax": False,
        "has_capital_gains_tax": True,
        "capital_gains_rate": Decimal("0.07"),
        "capital_gains_threshold": Decimal("262000"),
    },
    # ... Would include all 50 states + DC
}


# ========================================
# Local Tax Data (Sample)
# ========================================

LOCAL_TAX_DATA = {
    "NYC": {
        "name": "New York City",
        "state": "NY",
        "type": "city",
        "brackets_2024": [
            {"min": 0, "max": 12000, "rate": 0.03078},
            {"min": 12000, "max": 25000, "rate": 0.03762},
            {"min": 25000, "max": 50000, "rate": 0.03819},
            {"min": 50000, "max": None, "rate": 0.03876},
        ],
    },
    "PHILLY": {
        "name": "Philadelphia",
        "state": "PA",
        "type": "city",
        "wage_tax_resident": Decimal("0.0384"),
        "wage_tax_nonresident": Decimal("0.0359"),
    },
    # ... Would include major cities with local taxes
}


# ========================================
# Validation Rules Database
# ========================================

VALIDATION_RULES = {
    "1040": [
        {
            "rule_id": "1040-001",
            "description": "SSN must be 9 digits",
            "field": "taxpayer_ssn",
            "type": "format",
            "pattern": r"^\d{9}$",
            "severity": "error",
            "irs_code": "FW2-052",
        },
        {
            "rule_id": "1040-002",
            "description": "Filing status required",
            "field": "filing_status",
            "type": "required",
            "severity": "error",
        },
        {
            "rule_id": "1040-003",
            "description": "MFS filers cannot claim EIC",
            "type": "conditional",
            "condition": "filing_status == 'married_filing_separately' and eic > 0",
            "severity": "error",
            "irs_code": "IND-516",
        },
        {
            "rule_id": "1040-004",
            "description": "Total income should not be negative unless specific conditions",
            "field": "total_income",
            "type": "range",
            "min": 0,
            "severity": "warning",
        },
        {
            "rule_id": "1040-005",
            "description": "Withholding cannot exceed wages",
            "type": "comparison",
            "condition": "withholding <= wages",
            "severity": "error",
        },
        # ... hundreds more validation rules
    ],
    "1120": [
        {
            "rule_id": "1120-001",
            "description": "EIN must be 9 digits",
            "field": "ein",
            "type": "format",
            "pattern": r"^\d{9}$",
            "severity": "error",
        },
        # ...
    ],
}


# ========================================
# E-File Business Rules
# ========================================

EFILE_RULES = {
    "1040": {
        "mef_schema_version": "2024v1.0",
        "transmission_id_format": "YYYYMMDD-HHMMSS-NNNNNN",
        "max_attachment_size_mb": 25,
        "supported_states": ["AL", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "GA", "HI",
                            "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA",
                            "MI", "MN", "MS", "MO", "MT", "NE", "NJ", "NM", "NY", "NC",
                            "ND", "OH", "OK", "OR", "PA", "RI", "SC", "UT", "VT", "VA",
                            "WV", "WI"],
        "rejection_codes": {
            "IND-031": "Taxpayer SSN in the return must not be the same as a spouse SSN",
            "IND-516": "EIC is not allowed for MFS filers",
            "FW2-052": "Invalid SSN format",
            "R0000-905": "Business Rule validation error",
            # ... hundreds more
        },
    },
}


# ========================================
# Helper Functions
# ========================================

def get_tax_brackets(tax_year: int, bracket_type: str, filing_status: str) -> List[Dict]:
    """Get tax brackets for a specific year, type, and filing status"""
    if tax_year == 2024:
        brackets = TAX_BRACKETS_2024
    elif tax_year == 2023:
        brackets = TAX_BRACKETS_2023
    else:
        # Default to most recent year
        brackets = TAX_BRACKETS_2024

    key = f"{bracket_type}_{filing_status}"
    return brackets.get(key, [])


def get_standard_deduction(tax_year: int, filing_status: str,
                          age_65_plus: bool = False, blind: bool = False,
                          spouse_65_plus: bool = False, spouse_blind: bool = False) -> Decimal:
    """Calculate standard deduction including additional amounts"""
    deductions = STANDARD_DEDUCTIONS.get(tax_year, STANDARD_DEDUCTIONS[2024])
    base = deductions.get(filing_status, Decimal("0"))

    # Additional amounts for age 65+ or blind
    if filing_status in ["married_filing_jointly", "married_filing_separately",
                         "qualifying_surviving_spouse"]:
        additional = deductions.get("additional_married", Decimal("0"))
    else:
        additional = deductions.get("additional_single", Decimal("0"))

    total_additional = Decimal("0")
    if age_65_plus:
        total_additional += additional
    if blind:
        total_additional += additional
    if spouse_65_plus:
        total_additional += additional
    if spouse_blind:
        total_additional += additional

    return base + total_additional


def get_ss_wage_base(tax_year: int) -> Decimal:
    """Get Social Security wage base for a year"""
    limits = SOCIAL_SECURITY_LIMITS.get(tax_year, SOCIAL_SECURITY_LIMITS[2024])
    return limits.get("wage_base", Decimal("168600"))


def get_amt_exemption(tax_year: int, filing_status: str, amti: Decimal) -> Decimal:
    """Calculate AMT exemption with phase-out"""
    limits = AMT_LIMITS.get(tax_year, AMT_LIMITS[2024])

    if filing_status == "married_filing_jointly":
        exemption = limits["exemption_mfj"]
        phase_out = limits["phase_out_mfj"]
    elif filing_status == "married_filing_separately":
        exemption = limits["exemption_mfs"]
        phase_out = limits["phase_out_mfs"]
    else:
        exemption = limits["exemption_single"]
        phase_out = limits["phase_out_single"]

    # Phase-out at 25 cents per dollar over threshold
    if amti > phase_out:
        reduction = (amti - phase_out) * Decimal("0.25")
        exemption = max(Decimal("0"), exemption - reduction)

    return exemption


def get_niit_threshold(tax_year: int, filing_status: str) -> Decimal:
    """Get NIIT threshold for filing status"""
    thresholds = NIIT_THRESHOLDS.get(tax_year, NIIT_THRESHOLDS[2024])
    return thresholds.get(filing_status, Decimal("200000"))


def get_state_tax_info(state_code: str) -> Dict[str, Any]:
    """Get state tax information"""
    return STATE_TAX_DATA.get(state_code, {"has_income_tax": False})


def get_local_tax_info(locality_code: str) -> Dict[str, Any]:
    """Get local tax information"""
    return LOCAL_TAX_DATA.get(locality_code, {})


def get_validation_rules(form_type: str) -> List[Dict]:
    """Get validation rules for a form type"""
    return VALIDATION_RULES.get(form_type, [])


def get_efile_config(form_type: str) -> Dict[str, Any]:
    """Get e-file configuration for a form type"""
    return EFILE_RULES.get(form_type, {})
