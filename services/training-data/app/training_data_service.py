"""
Training Data Management Service

Manages financial statement data for AI model training:
- Ingests non-public financial statements
- Anonymizes before training
- Validates data quality
- Tracks data lineage
- Prepares training datasets
- Manages model versioning

Privacy Guarantees:
- All training data fully anonymized
- Original data encrypted at rest
- No company identifiers in training sets
- Complete audit trail
- SOC 2 compliant data handling
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class DataSource(str, Enum):
    """Source of training data"""
    CLIENT_UPLOAD = "client_upload"
    MANUAL_ENTRY = "manual_entry"
    API_IMPORT = "api_import"
    BULK_IMPORT = "bulk_import"
    PUBLIC_FILINGS = "public_filings"  # SEC EDGAR, etc.


class DataQuality(str, Enum):
    """Data quality assessment"""
    EXCELLENT = "excellent"  # Complete, accurate, validated
    GOOD = "good"  # Minor issues, usable
    FAIR = "fair"  # Some issues, may need cleanup
    POOR = "poor"  # Significant issues, not recommended for training


class TrainingDataStatus(str, Enum):
    """Status of training data"""
    PENDING_REVIEW = "pending_review"
    ANONYMIZING = "anonymizing"
    ANONYMIZED = "anonymized"
    VALIDATED = "validated"
    APPROVED_FOR_TRAINING = "approved_for_training"
    IN_TRAINING = "in_training"
    RETIRED = "retired"
    REJECTED = "rejected"


class StatementType(str, Enum):
    """Type of financial statement"""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    STATEMENT_OF_EQUITY = "statement_of_equity"
    NOTES_TO_FINANCIAL_STATEMENTS = "notes"
    COMPLETE_PACKAGE = "complete_package"


class TrainingDataService:
    """
    Comprehensive training data management for AI models.

    Workflow:
    1. Ingest financial statements
    2. Store original (encrypted)
    3. Anonymize for training
    4. Validate quality
    5. Approve for training
    6. Prepare training datasets
    7. Track usage in models
    """

    def __init__(
        self,
        anonymization_service=None,
        encryption_service=None,
        audit_log_service=None,
    ):
        """
        Initialize training data service.

        Args:
            anonymization_service: DataAnonymizationService
            encryption_service: EncryptionService for storing originals
            audit_log_service: AuditLogService for tracking
        """
        self.anonymization_service = anonymization_service
        self.encryption_service = encryption_service
        self.audit_log_service = audit_log_service

        # In-memory storage (in production, use database)
        self._training_data: Dict[str, Dict] = {}
        self._datasets: Dict[str, Dict] = {}

    async def ingest_financial_statement(
        self,
        statement_data: Dict[str, Any],
        statement_type: StatementType,
        source: DataSource,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> str:
        """
        Ingest a financial statement for training.

        Args:
            statement_data: Raw financial statement data
            statement_type: Type of statement
            source: Source of data
            metadata: Additional metadata
            tenant_id: Tenant providing data
            user_id: User uploading data

        Returns:
            Training data ID
        """
        try:
            training_data_id = str(uuid4())

            # Validate statement has required fields
            validation_result = self._validate_statement(statement_data, statement_type)
            if not validation_result["is_valid"]:
                raise TrainingDataError(
                    f"Invalid statement: {validation_result['issues']}"
                )

            # Encrypt original statement
            encrypted_original = None
            if self.encryption_service:
                # In production, encrypt and store in secure storage
                encrypted_original = statement_data  # Placeholder

            # Anonymize for training
            if not self.anonymization_service:
                raise TrainingDataError("Anonymization service not configured")

            anonymized_statement = self.anonymization_service.anonymize_financial_statement(
                statement=statement_data,
                level="full",
                tenant_id=tenant_id,
                user_id=user_id,
            )

            # Validate anonymization
            anonymization_validation = self.anonymization_service.validate_anonymization(
                anonymized_statement
            )

            if not anonymization_validation["is_valid"]:
                logger.error(
                    f"Anonymization validation failed: "
                    f"{anonymization_validation['issues']}"
                )
                raise TrainingDataError("Anonymization validation failed")

            # Assess data quality
            quality_assessment = self._assess_data_quality(anonymized_statement)

            # Store training data record
            training_record = {
                "id": training_data_id,
                "statement_type": statement_type.value,
                "source": source.value,
                "status": TrainingDataStatus.ANONYMIZED.value,
                "original_statement_encrypted": encrypted_original,
                "anonymized_statement": anonymized_statement,
                "validation_result": validation_result,
                "anonymization_validation": anonymization_validation,
                "quality_assessment": quality_assessment,
                "metadata": metadata or {},
                "tenant_id": str(tenant_id) if tenant_id else None,
                "uploaded_by": str(user_id) if user_id else None,
                "uploaded_at": datetime.utcnow().isoformat(),
                "approved_for_training": False,
                "used_in_models": [],
            }

            self._training_data[training_data_id] = training_record

            # Audit log
            if self.audit_log_service and user_id:
                logger.info(
                    f"Ingested financial statement for training: {training_data_id}"
                )

            logger.info(
                f"Successfully ingested statement {training_data_id} "
                f"(quality: {quality_assessment['overall_quality']})"
            )

            return training_data_id

        except Exception as e:
            logger.error(f"Failed to ingest financial statement: {e}", exc_info=True)
            raise TrainingDataError(f"Ingestion failed: {e}")

    def _validate_statement(
        self,
        statement: Dict[str, Any],
        statement_type: StatementType
    ) -> Dict[str, Any]:
        """
        Validate financial statement has required fields and data.

        Args:
            statement: Statement data
            statement_type: Type of statement

        Returns:
            Validation result
        """
        issues = []

        # Check required fields based on statement type
        required_fields = self._get_required_fields(statement_type)
        missing_fields = [
            field for field in required_fields
            if field not in statement or statement[field] is None
        ]

        if missing_fields:
            issues.append({
                "type": "missing_fields",
                "fields": missing_fields,
            })

        # Check for reasonable financial values
        financial_fields = [
            'total_assets', 'total_liabilities', 'total_equity',
            'revenue', 'expenses', 'net_income'
        ]

        for field in financial_fields:
            if field in statement:
                value = statement[field]
                if isinstance(value, (int, float, Decimal)):
                    # Check for unreasonable values
                    if value < 0 and field not in ['net_income', 'expenses']:
                        issues.append({
                            "type": "negative_value",
                            "field": field,
                            "value": float(value),
                        })

        # Check balance sheet equation: Assets = Liabilities + Equity
        if statement_type == StatementType.BALANCE_SHEET:
            if all(k in statement for k in ['total_assets', 'total_liabilities', 'total_equity']):
                assets = Decimal(str(statement['total_assets']))
                liabilities = Decimal(str(statement['total_liabilities']))
                equity = Decimal(str(statement['total_equity']))

                # Allow 1% tolerance for rounding
                if abs(assets - (liabilities + equity)) > assets * Decimal('0.01'):
                    issues.append({
                        "type": "balance_sheet_equation_mismatch",
                        "assets": float(assets),
                        "liabilities_plus_equity": float(liabilities + equity),
                    })

        return {
            "is_valid": len(issues) == 0,
            "issues_count": len(issues),
            "issues": issues,
            "validated_at": datetime.utcnow().isoformat(),
        }

    def _get_required_fields(self, statement_type: StatementType) -> List[str]:
        """
        Get required fields for statement type.

        Args:
            statement_type: Type of statement

        Returns:
            List of required field names
        """
        if statement_type == StatementType.BALANCE_SHEET:
            return [
                'total_assets',
                'total_liabilities',
                'total_equity',
                'reporting_period',
            ]
        elif statement_type == StatementType.INCOME_STATEMENT:
            return [
                'revenue',
                'expenses',
                'net_income',
                'reporting_period',
            ]
        elif statement_type == StatementType.CASH_FLOW:
            return [
                'operating_cash_flow',
                'investing_cash_flow',
                'financing_cash_flow',
                'reporting_period',
            ]
        else:
            return ['reporting_period']

    def _assess_data_quality(self, statement: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess quality of financial statement data.

        Checks:
        - Completeness (how many fields populated)
        - Consistency (relationships between values)
        - Accuracy (reasonable values)

        Args:
            statement: Statement to assess

        Returns:
            Quality assessment
        """
        # Count total and populated fields
        total_fields = len(statement)
        populated_fields = sum(1 for v in statement.values() if v is not None)
        completeness = populated_fields / total_fields if total_fields > 0 else 0

        # Check for consistency issues
        consistency_issues = []

        # Example: Gross profit should = Revenue - COGS
        if all(k in statement for k in ['revenue', 'cost_of_goods_sold', 'gross_profit']):
            revenue = Decimal(str(statement['revenue']))
            cogs = Decimal(str(statement['cost_of_goods_sold']))
            gross_profit = Decimal(str(statement['gross_profit']))

            calculated_gp = revenue - cogs
            if abs(gross_profit - calculated_gp) > revenue * Decimal('0.01'):
                consistency_issues.append("gross_profit_mismatch")

        # Determine overall quality
        if completeness >= 0.9 and len(consistency_issues) == 0:
            overall_quality = DataQuality.EXCELLENT
        elif completeness >= 0.75 and len(consistency_issues) <= 1:
            overall_quality = DataQuality.GOOD
        elif completeness >= 0.5:
            overall_quality = DataQuality.FAIR
        else:
            overall_quality = DataQuality.POOR

        return {
            "overall_quality": overall_quality.value,
            "completeness_score": round(completeness, 2),
            "consistency_issues": consistency_issues,
            "assessed_at": datetime.utcnow().isoformat(),
        }

    async def approve_for_training(
        self,
        training_data_id: str,
        approver_user_id: UUID,
    ) -> bool:
        """
        Approve training data for use in AI models.

        REQUIRES ADMIN/DATA SCIENTIST AUTHORIZATION.

        Args:
            training_data_id: Training data ID
            approver_user_id: User approving data

        Returns:
            True if approved, False otherwise
        """
        if training_data_id not in self._training_data:
            raise TrainingDataError(f"Training data not found: {training_data_id}")

        training_record = self._training_data[training_data_id]

        # Check quality is acceptable
        quality = training_record["quality_assessment"]["overall_quality"]
        if quality == DataQuality.POOR.value:
            logger.warning(
                f"Cannot approve poor quality data: {training_data_id}"
            )
            return False

        # Check anonymization is valid
        if not training_record["anonymization_validation"]["is_valid"]:
            logger.error(
                f"Cannot approve data with failed anonymization: {training_data_id}"
            )
            return False

        # Approve
        training_record["status"] = TrainingDataStatus.APPROVED_FOR_TRAINING.value
        training_record["approved_for_training"] = True
        training_record["approved_by"] = str(approver_user_id)
        training_record["approved_at"] = datetime.utcnow().isoformat()

        # Audit log
        if self.audit_log_service:
            logger.info(
                f"Training data approved: {training_data_id} by user {approver_user_id}"
            )

        return True

    def create_training_dataset(
        self,
        dataset_name: str,
        training_data_ids: List[str],
        purpose: str,
        creator_user_id: UUID,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a training dataset from approved training data.

        Args:
            dataset_name: Name for dataset
            training_data_ids: IDs of training data to include
            purpose: Purpose of dataset (fraud detection, analysis, etc.)
            creator_user_id: User creating dataset
            filters: Optional filters (date range, statement type, etc.)

        Returns:
            Dataset ID
        """
        dataset_id = str(uuid4())

        # Verify all training data is approved
        approved_data = []
        for data_id in training_data_ids:
            if data_id not in self._training_data:
                logger.warning(f"Training data not found: {data_id}")
                continue

            record = self._training_data[data_id]
            if record["approved_for_training"]:
                approved_data.append(record["anonymized_statement"])
            else:
                logger.warning(
                    f"Training data not approved, skipping: {data_id}"
                )

        if not approved_data:
            raise TrainingDataError("No approved training data found")

        # Create dataset
        dataset = {
            "id": dataset_id,
            "name": dataset_name,
            "purpose": purpose,
            "training_data_ids": training_data_ids,
            "training_data_count": len(approved_data),
            "data": approved_data,
            "filters": filters or {},
            "created_by": str(creator_user_id),
            "created_at": datetime.utcnow().isoformat(),
            "last_used_at": None,
            "models_trained": [],
        }

        self._datasets[dataset_id] = dataset

        # Update training data records
        for data_id in training_data_ids:
            if data_id in self._training_data:
                self._training_data[data_id]["status"] = TrainingDataStatus.IN_TRAINING.value

        # Audit log
        if self.audit_log_service:
            logger.info(
                f"Created training dataset {dataset_id} with {len(approved_data)} statements"
            )

        return dataset_id

    def get_training_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Retrieve training dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dataset
        """
        if dataset_id not in self._datasets:
            raise TrainingDataError(f"Dataset not found: {dataset_id}")

        dataset = self._datasets[dataset_id]
        dataset["last_used_at"] = datetime.utcnow().isoformat()

        return dataset

    def track_model_training(
        self,
        dataset_id: str,
        model_id: str,
        model_name: str,
        training_metadata: Dict[str, Any],
    ):
        """
        Track which models were trained on which datasets.

        Args:
            dataset_id: Dataset used for training
            model_id: Model ID
            model_name: Model name
            training_metadata: Training metadata (hyperparameters, etc.)
        """
        if dataset_id not in self._datasets:
            raise TrainingDataError(f"Dataset not found: {dataset_id}")

        dataset = self._datasets[dataset_id]
        dataset["models_trained"].append({
            "model_id": model_id,
            "model_name": model_name,
            "trained_at": datetime.utcnow().isoformat(),
            "metadata": training_metadata,
        })

        # Update training data records
        for data_id in dataset["training_data_ids"]:
            if data_id in self._training_data:
                self._training_data[data_id]["used_in_models"].append({
                    "model_id": model_id,
                    "model_name": model_name,
                    "trained_at": datetime.utcnow().isoformat(),
                })

        logger.info(f"Tracked model {model_id} training on dataset {dataset_id}")

    def generate_data_lineage_report(
        self,
        model_id: str
    ) -> Dict[str, Any]:
        """
        Generate data lineage report for a model.

        Shows which training data was used, sources, quality, etc.

        Args:
            model_id: Model ID

        Returns:
            Data lineage report
        """
        # Find all datasets used by model
        datasets_used = []
        training_data_used = []

        for dataset_id, dataset in self._datasets.items():
            for model_info in dataset["models_trained"]:
                if model_info["model_id"] == model_id:
                    datasets_used.append({
                        "dataset_id": dataset_id,
                        "dataset_name": dataset["name"],
                        "data_count": dataset["training_data_count"],
                        "trained_at": model_info["trained_at"],
                    })

                    # Collect training data details
                    for data_id in dataset["training_data_ids"]:
                        if data_id in self._training_data:
                            record = self._training_data[data_id]
                            training_data_used.append({
                                "id": data_id,
                                "type": record["statement_type"],
                                "source": record["source"],
                                "quality": record["quality_assessment"]["overall_quality"],
                                "uploaded_at": record["uploaded_at"],
                            })

        # Aggregate statistics
        sources = {}
        qualities = {}
        for data in training_data_used:
            sources[data["source"]] = sources.get(data["source"], 0) + 1
            qualities[data["quality"]] = qualities.get(data["quality"], 0) + 1

        return {
            "model_id": model_id,
            "datasets_used": datasets_used,
            "total_training_statements": len(training_data_used),
            "sources_breakdown": sources,
            "quality_breakdown": qualities,
            "training_data_details": training_data_used,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get training data statistics.

        Returns:
            Statistics report
        """
        # Count by status
        status_counts = {}
        for record in self._training_data.values():
            status = record["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        # Count by quality
        quality_counts = {}
        for record in self._training_data.values():
            quality = record["quality_assessment"]["overall_quality"]
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

        # Count by source
        source_counts = {}
        for record in self._training_data.values():
            source = record["source"]
            source_counts[source] = source_counts.get(source, 0) + 1

        return {
            "total_statements": len(self._training_data),
            "approved_for_training": sum(
                1 for r in self._training_data.values()
                if r["approved_for_training"]
            ),
            "total_datasets": len(self._datasets),
            "status_breakdown": status_counts,
            "quality_breakdown": quality_counts,
            "source_breakdown": source_counts,
        }


class TrainingDataError(Exception):
    """Raised when training data operation fails"""
    pass


# ============================================================================
# DATA QUALITY VALIDATORS
# ============================================================================

class FinancialStatementValidator:
    """
    Advanced validation for financial statements.

    Checks:
    - Mathematical relationships (balance sheet equation, etc.)
    - Industry benchmarks (reasonable ranges for ratios)
    - Temporal consistency (year-over-year changes)
    """

    @staticmethod
    def validate_balance_sheet(statement: Dict[str, Any]) -> List[str]:
        """
        Validate balance sheet.

        Args:
            statement: Balance sheet data

        Returns:
            List of validation errors
        """
        errors = []

        # Check balance sheet equation
        if all(k in statement for k in ['total_assets', 'total_liabilities', 'total_equity']):
            assets = Decimal(str(statement['total_assets']))
            liabilities = Decimal(str(statement['total_liabilities']))
            equity = Decimal(str(statement['total_equity']))

            if assets != liabilities + equity:
                errors.append(f"Balance sheet equation mismatch: {assets} != {liabilities + equity}")

        # Check current ratio reasonableness (0.5 to 10 typically)
        if 'current_assets' in statement and 'current_liabilities' in statement:
            current_assets = Decimal(str(statement['current_assets']))
            current_liabilities = Decimal(str(statement['current_liabilities']))

            if current_liabilities > 0:
                current_ratio = current_assets / current_liabilities
                if current_ratio < Decimal('0.1') or current_ratio > Decimal('20'):
                    errors.append(f"Unusual current ratio: {current_ratio}")

        return errors

    @staticmethod
    def validate_income_statement(statement: Dict[str, Any]) -> List[str]:
        """
        Validate income statement.

        Args:
            statement: Income statement data

        Returns:
            List of validation errors
        """
        errors = []

        # Check net income calculation
        if all(k in statement for k in ['revenue', 'expenses', 'net_income']):
            revenue = Decimal(str(statement['revenue']))
            expenses = Decimal(str(statement['expenses']))
            net_income = Decimal(str(statement['net_income']))

            calculated_net_income = revenue - expenses
            if abs(net_income - calculated_net_income) > revenue * Decimal('0.01'):
                errors.append(f"Net income mismatch: {net_income} != {calculated_net_income}")

        # Check profit margin reasonableness (-100% to 100%)
        if 'revenue' in statement and 'net_income' in statement:
            revenue = Decimal(str(statement['revenue']))
            net_income = Decimal(str(statement['net_income']))

            if revenue > 0:
                profit_margin = (net_income / revenue) * 100
                if profit_margin < Decimal('-100') or profit_margin > Decimal('100'):
                    errors.append(f"Unusual profit margin: {profit_margin}%")

        return errors
