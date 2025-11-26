"""
SEC EDGAR Scraper Module

Provides data acquisition from SEC EDGAR for audit ML training.
"""

from .edgar_scraper import EDGARScraper, Filing, FinancialStatement, AuditOpinion, DisclosureNote

__all__ = [
    "EDGARScraper",
    "Filing",
    "FinancialStatement",
    "AuditOpinion",
    "DisclosureNote",
]
