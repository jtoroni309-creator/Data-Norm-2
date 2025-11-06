"""
Data Anonymization Service

Removes all identifying information from financial statements before AI training.

Privacy Guarantees:
- No company identifiers sent to AI
- No personal information exposed
- Consistent tokenization for relationships
- Reversible only by authorized users
- Full audit trail
"""

from .anonymization_service import (
    DataAnonymizationService,
    CompanyNameDetector,
    PIIType,
    AnonymizationLevel,
    AnonymizationError,
    DeAnonymizationError,
)

__all__ = [
    "DataAnonymizationService",
    "CompanyNameDetector",
    "PIIType",
    "AnonymizationLevel",
    "AnonymizationError",
    "DeAnonymizationError",
]

__version__ = "1.0.0"
