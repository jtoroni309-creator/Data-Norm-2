"""
R&D Study Automation Engines

Core calculation and rules engines for R&D tax credit studies.
"""

from .rules_engine import RulesEngine, FederalRules, StateRules
from .qualification_engine import QualificationEngine
from .qre_engine import QREEngine
from .calculation_engine import CalculationEngine

__all__ = [
    "RulesEngine",
    "FederalRules",
    "StateRules",
    "QualificationEngine",
    "QREEngine",
    "CalculationEngine",
]
