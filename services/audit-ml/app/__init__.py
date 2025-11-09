"""
Audit ML Service - 99% CPA-Level Accuracy

High-performance machine learning service for audit procedures.
"""

from .audit_model_trainer import CPAAuditModelTrainer, audit_model_trainer
from .pcaob_compliance_model import PCAOBComplianceScorer, pcaob_compliance_scorer
from .training_pipeline import AuditTrainingPipeline

__version__ = "1.0.0"
__all__ = [
    'CPAAuditModelTrainer',
    'audit_model_trainer',
    'PCAOBComplianceScorer',
    'pcaob_compliance_scorer',
    'AuditTrainingPipeline'
]
