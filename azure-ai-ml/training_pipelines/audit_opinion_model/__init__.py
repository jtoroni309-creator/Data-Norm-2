"""
Audit Opinion Model Training Pipeline

Trains CPA-level AI models for audit opinion generation.
"""

from .train_audit_opinion_model import (
    AuditOpinionTrainer,
    AuditOpinionDataset,
    AuditOpinionClassifier,
    AuditOpinionTrainingSample,
)

__all__ = [
    "AuditOpinionTrainer",
    "AuditOpinionDataset",
    "AuditOpinionClassifier",
    "AuditOpinionTrainingSample",
]
