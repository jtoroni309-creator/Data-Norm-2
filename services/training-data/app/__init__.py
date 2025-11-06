"""
Training Data Management Service

Manages financial statement data for AI model training with full anonymization.

Features:
- Automated anonymization before training
- Data quality assessment
- Training dataset preparation
- Model lineage tracking
- Complete audit trail
"""

from .training_data_service import (
    TrainingDataService,
    FinancialStatementValidator,
    DataSource,
    DataQuality,
    TrainingDataStatus,
    StatementType,
    TrainingDataError,
)

__all__ = [
    "TrainingDataService",
    "FinancialStatementValidator",
    "DataSource",
    "DataQuality",
    "TrainingDataStatus",
    "StatementType",
    "TrainingDataError",
]

__version__ = "1.0.0"
