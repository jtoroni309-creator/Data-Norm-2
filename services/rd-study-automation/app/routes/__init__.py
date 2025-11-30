"""
R&D Study Automation Routes Package
"""

from .outputs import router as outputs_router
from .ai_processing import router as ai_router

__all__ = ["outputs_router", "ai_router"]
