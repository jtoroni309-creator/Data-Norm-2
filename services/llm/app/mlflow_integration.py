"""
MLflow Integration for Audit AI Model Management

Provides comprehensive model lifecycle management:
- Experiment tracking for RAG configurations
- Model versioning and registry
- Performance metrics logging
- A/B testing support
- Model comparison and selection
- Deployment management

Goal: Track and optimize AI models to continuously improve audit quality
"""
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.models import infer_signature
import numpy as np

from .config import settings

logger = logging.getLogger(__name__)


class MLflowManager:
    """
    MLflow integration for audit AI model management

    Tracks:
    - RAG configuration experiments
    - Model performance metrics
    - Confidence scoring accuracy
    - Contradiction detection effectiveness
    - End-to-end audit quality metrics
    """

    def __init__(self):
        """Initialize MLflow connection"""
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        self.client = MlflowClient()
        self.experiment_name = "audit-ai-rag-system"

        # Create or get experiment
        try:
            self.experiment_id = mlflow.create_experiment(
                self.experiment_name,
                tags={
                    "project": "aura-audit-ai",
                    "team": "ml-engineering",
                    "purpose": "audit automation"
                }
            )
            logger.info(f"Created new experiment: {self.experiment_name}")
        except Exception:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            self.experiment_id = experiment.experiment_id
            logger.info(f"Using existing experiment: {self.experiment_name}")

    def start_run(
        self,
        run_name: str,
        tags: Optional[Dict[str, str]] = None
    ) -> mlflow.ActiveRun:
        """
        Start a new MLflow run

        Args:
            run_name: Name for this run
            tags: Optional tags for the run

        Returns:
            Active MLflow run
        """
        default_tags = {
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat()
        }

        if tags:
            default_tags.update(tags)

        run = mlflow.start_run(
            experiment_id=self.experiment_id,
            run_name=run_name,
            tags=default_tags
        )

        logger.info(f"Started MLflow run: {run_name} (id: {run.info.run_id})")
        return run

    def log_rag_configuration(
        self,
        embedding_model: str,
        llm_model: str,
        chunk_size: int,
        chunk_overlap: int,
        top_k: int,
        similarity_threshold: float,
        temperature: float,
        max_tokens: int,
        additional_params: Optional[Dict[str, Any]] = None
    ):
        """
        Log RAG system configuration parameters

        Args:
            embedding_model: Name of embedding model
            llm_model: Name of LLM (e.g., gpt-4-turbo)
            chunk_size: Text chunk size
            chunk_overlap: Overlap between chunks
            top_k: Number of chunks to retrieve
            similarity_threshold: Minimum similarity for retrieval
            temperature: LLM temperature
            max_tokens: Maximum tokens to generate
            additional_params: Any additional parameters
        """
        params = {
            "embedding_model": embedding_model,
            "llm_model": llm_model,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if additional_params:
            params.update(additional_params)

        mlflow.log_params(params)
        logger.debug(f"Logged RAG configuration: {len(params)} parameters")

    def log_query_metrics(
        self,
        query_id: UUID,
        retrieval_time_ms: int,
        generation_time_ms: int,
        total_time_ms: int,
        tokens_used: int,
        chunks_retrieved: int,
        avg_similarity_score: float,
        confidence_score: float,
        contradiction_count: int,
        user_feedback_score: Optional[float] = None
    ):
        """
        Log metrics for a single query execution

        Args:
            query_id: Unique query identifier
            retrieval_time_ms: Time spent on retrieval (ms)
            generation_time_ms: Time spent on generation (ms)
            total_time_ms: Total processing time (ms)
            tokens_used: Total tokens consumed
            chunks_retrieved: Number of chunks retrieved
            avg_similarity_score: Average similarity score of retrieved chunks
            confidence_score: Overall confidence score
            contradiction_count: Number of contradictions detected
            user_feedback_score: Optional user rating (0-5)
        """
        metrics = {
            f"query.{query_id}.retrieval_time_ms": retrieval_time_ms,
            f"query.{query_id}.generation_time_ms": generation_time_ms,
            f"query.{query_id}.total_time_ms": total_time_ms,
            f"query.{query_id}.tokens_used": tokens_used,
            f"query.{query_id}.chunks_retrieved": chunks_retrieved,
            f"query.{query_id}.avg_similarity": avg_similarity_score,
            f"query.{query_id}.confidence_score": confidence_score,
            f"query.{query_id}.contradiction_count": contradiction_count,
        }

        if user_feedback_score is not None:
            metrics[f"query.{query_id}.user_feedback"] = user_feedback_score

        mlflow.log_metrics(metrics)

    def log_aggregate_metrics(
        self,
        total_queries: int,
        avg_retrieval_time_ms: float,
        avg_generation_time_ms: float,
        avg_total_time_ms: float,
        avg_tokens_per_query: float,
        avg_confidence_score: float,
        high_confidence_rate: float,
        contradiction_rate: float,
        avg_user_rating: Optional[float] = None,
        p95_latency_ms: Optional[float] = None,
        p99_latency_ms: Optional[float] = None
    ):
        """
        Log aggregate metrics for a batch of queries

        Args:
            total_queries: Total number of queries processed
            avg_retrieval_time_ms: Average retrieval time
            avg_generation_time_ms: Average generation time
            avg_total_time_ms: Average total time
            avg_tokens_per_query: Average tokens consumed per query
            avg_confidence_score: Average confidence score
            high_confidence_rate: % of queries with high/very high confidence
            contradiction_rate: % of queries with contradictions
            avg_user_rating: Average user rating if available
            p95_latency_ms: 95th percentile latency
            p99_latency_ms: 99th percentile latency
        """
        metrics = {
            "aggregate.total_queries": total_queries,
            "aggregate.avg_retrieval_time_ms": avg_retrieval_time_ms,
            "aggregate.avg_generation_time_ms": avg_generation_time_ms,
            "aggregate.avg_total_time_ms": avg_total_time_ms,
            "aggregate.avg_tokens_per_query": avg_tokens_per_query,
            "aggregate.avg_confidence_score": avg_confidence_score,
            "aggregate.high_confidence_rate": high_confidence_rate,
            "aggregate.contradiction_rate": contradiction_rate,
        }

        if avg_user_rating is not None:
            metrics["aggregate.avg_user_rating"] = avg_user_rating

        if p95_latency_ms is not None:
            metrics["aggregate.p95_latency_ms"] = p95_latency_ms

        if p99_latency_ms is not None:
            metrics["aggregate.p99_latency_ms"] = p99_latency_ms

        mlflow.log_metrics(metrics)
        logger.info(f"Logged aggregate metrics for {total_queries} queries")

    def log_audit_quality_metrics(
        self,
        engagement_id: UUID,
        findings_accuracy_rate: float,
        false_positive_rate: float,
        false_negative_rate: float,
        citation_accuracy_rate: float,
        workpaper_quality_score: float,
        compliance_check_pass_rate: float,
        partner_approval_rate: float,
        time_savings_vs_manual_hours: float
    ):
        """
        Log audit-specific quality metrics

        These metrics measure how well the AI performs actual audit tasks
        compared to a seasoned CPA.

        Args:
            engagement_id: Engagement being audited
            findings_accuracy_rate: % of AI findings that are correct
            false_positive_rate: % of findings that are false alarms
            false_negative_rate: % of issues missed by AI
            citation_accuracy_rate: % of citations that are correct
            workpaper_quality_score: Quality score from CPA review (0-1)
            compliance_check_pass_rate: % of AI outputs passing compliance checks
            partner_approval_rate: % approved by partner without changes
            time_savings_vs_manual_hours: Hours saved compared to manual process
        """
        metrics = {
            f"engagement.{engagement_id}.findings_accuracy": findings_accuracy_rate,
            f"engagement.{engagement_id}.false_positive_rate": false_positive_rate,
            f"engagement.{engagement_id}.false_negative_rate": false_negative_rate,
            f"engagement.{engagement_id}.citation_accuracy": citation_accuracy_rate,
            f"engagement.{engagement_id}.workpaper_quality": workpaper_quality_score,
            f"engagement.{engagement_id}.compliance_pass_rate": compliance_check_pass_rate,
            f"engagement.{engagement_id}.partner_approval_rate": partner_approval_rate,
            f"engagement.{engagement_id}.time_savings_hours": time_savings_vs_manual_hours,
        }

        mlflow.log_metrics(metrics)
        logger.info(f"Logged audit quality metrics for engagement {engagement_id}")

    def log_model_artifact(
        self,
        artifact_path: str,
        local_path: str,
        artifact_type: str = "model"
    ):
        """
        Log a model artifact (weights, configs, etc.)

        Args:
            artifact_path: Path within MLflow artifact store
            local_path: Local file/directory path
            artifact_type: Type of artifact
        """
        mlflow.log_artifact(local_path, artifact_path)
        logger.info(f"Logged {artifact_type} artifact: {artifact_path}")

    def register_model(
        self,
        model_name: str,
        model_uri: str,
        description: str,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Register a model in MLflow Model Registry

        Args:
            model_name: Name for the model
            model_uri: URI of the model (e.g., runs:/<run_id>/model)
            description: Model description
            tags: Optional tags

        Returns:
            Model version string
        """
        try:
            # Register model
            model_version = mlflow.register_model(
                model_uri=model_uri,
                name=model_name,
                tags=tags
            )

            # Update description
            self.client.update_model_version(
                name=model_name,
                version=model_version.version,
                description=description
            )

            logger.info(
                f"Registered model '{model_name}' version {model_version.version}"
            )

            return model_version.version

        except Exception as e:
            logger.error(f"Error registering model: {e}")
            raise

    def transition_model_stage(
        self,
        model_name: str,
        version: str,
        stage: str,  # "Staging", "Production", "Archived"
        archive_existing: bool = True
    ):
        """
        Transition a model version to a new stage

        Args:
            model_name: Model name
            version: Model version
            stage: Target stage (Staging/Production/Archived)
            archive_existing: Whether to archive existing models in target stage
        """
        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage,
                archive_existing_versions=archive_existing
            )

            logger.info(
                f"Transitioned model '{model_name}' version {version} to {stage}"
            )

        except Exception as e:
            logger.error(f"Error transitioning model stage: {e}")
            raise

    def compare_runs(
        self,
        run_ids: List[str],
        metric_names: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare metrics across multiple runs

        Args:
            run_ids: List of run IDs to compare
            metric_names: List of metric names to compare

        Returns:
            Dictionary of run_id -> {metric_name: value}
        """
        comparison = {}

        for run_id in run_ids:
            run = self.client.get_run(run_id)
            metrics = {}

            for metric_name in metric_names:
                if metric_name in run.data.metrics:
                    metrics[metric_name] = run.data.metrics[metric_name]

            comparison[run_id] = metrics

        logger.info(f"Compared {len(run_ids)} runs across {len(metric_names)} metrics")
        return comparison

    def get_best_run(
        self,
        metric_name: str,
        maximize: bool = True,
        filter_string: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find the best run based on a metric

        Args:
            metric_name: Metric to optimize
            maximize: Whether to maximize (True) or minimize (False)
            filter_string: Optional filter (e.g., "params.temperature < 0.5")

        Returns:
            Best run info or None
        """
        order_by = [f"metrics.{metric_name} {'DESC' if maximize else 'ASC'}"]

        runs = self.client.search_runs(
            experiment_ids=[self.experiment_id],
            filter_string=filter_string,
            order_by=order_by,
            max_results=1
        )

        if runs:
            best_run = runs[0]
            logger.info(
                f"Best run for {metric_name}: {best_run.info.run_id} "
                f"(value: {best_run.data.metrics.get(metric_name)})"
            )
            return {
                "run_id": best_run.info.run_id,
                "run_name": best_run.info.run_name,
                "metric_value": best_run.data.metrics.get(metric_name),
                "params": best_run.data.params,
                "tags": best_run.data.tags
            }

        return None

    def log_feature_importance(
        self,
        feature_names: List[str],
        importance_scores: List[float]
    ):
        """
        Log feature importance for interpretability

        Args:
            feature_names: List of feature names
            importance_scores: Corresponding importance scores
        """
        # Log as individual metrics
        for name, score in zip(feature_names, importance_scores):
            mlflow.log_metric(f"feature_importance.{name}", score)

        # Also log as artifact (JSON)
        importance_dict = dict(zip(feature_names, importance_scores))
        mlflow.log_dict(importance_dict, "feature_importance.json")

        logger.info(f"Logged importance for {len(feature_names)} features")

    def log_confusion_matrix(
        self,
        true_labels: List[str],
        predicted_labels: List[str],
        label_names: List[str]
    ):
        """
        Log confusion matrix for classification tasks

        Args:
            true_labels: Ground truth labels
            predicted_labels: Predicted labels
            label_names: Names of labels
        """
        from sklearn.metrics import confusion_matrix, classification_report
        import matplotlib.pyplot as plt
        import seaborn as sns

        # Compute confusion matrix
        cm = confusion_matrix(true_labels, predicted_labels, labels=label_names)

        # Plot
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=label_names,
            yticklabels=label_names,
            ax=ax
        )
        ax.set_xlabel('Predicted')
        ax.set_ylabel('True')
        ax.set_title('Confusion Matrix')

        # Log as artifact
        mlflow.log_figure(fig, "confusion_matrix.png")

        # Log classification report
        report = classification_report(true_labels, predicted_labels, output_dict=True)
        mlflow.log_dict(report, "classification_report.json")

        logger.info("Logged confusion matrix and classification report")

    def log_cpa_comparison_metrics(
        self,
        task_name: str,
        ai_accuracy: float,
        cpa_accuracy: float,
        ai_time_minutes: float,
        cpa_time_minutes: float,
        ai_cost_dollars: float,
        cpa_cost_dollars: float,
        quality_score_ai: float,
        quality_score_cpa: float
    ):
        """
        Log direct comparison between AI and CPA performance

        This is the ultimate metric: Can AI match or exceed a seasoned CPA?

        Args:
            task_name: Name of audit task
            ai_accuracy: AI accuracy rate (0-1)
            cpa_accuracy: CPA accuracy rate (0-1)
            ai_time_minutes: Time taken by AI
            cpa_time_minutes: Time taken by CPA
            ai_cost_dollars: Cost of AI execution
            cpa_cost_dollars: Cost of CPA time
            quality_score_ai: Quality score for AI output (0-1)
            quality_score_cpa: Quality score for CPA output (0-1)
        """
        metrics = {
            f"comparison.{task_name}.ai_accuracy": ai_accuracy,
            f"comparison.{task_name}.cpa_accuracy": cpa_accuracy,
            f"comparison.{task_name}.accuracy_ratio": ai_accuracy / cpa_accuracy if cpa_accuracy > 0 else 0,
            f"comparison.{task_name}.ai_time_minutes": ai_time_minutes,
            f"comparison.{task_name}.cpa_time_minutes": cpa_time_minutes,
            f"comparison.{task_name}.time_savings_pct": (cpa_time_minutes - ai_time_minutes) / cpa_time_minutes * 100 if cpa_time_minutes > 0 else 0,
            f"comparison.{task_name}.ai_cost_dollars": ai_cost_dollars,
            f"comparison.{task_name}.cpa_cost_dollars": cpa_cost_dollars,
            f"comparison.{task_name}.cost_savings_pct": (cpa_cost_dollars - ai_cost_dollars) / cpa_cost_dollars * 100 if cpa_cost_dollars > 0 else 0,
            f"comparison.{task_name}.ai_quality_score": quality_score_ai,
            f"comparison.{task_name}.cpa_quality_score": quality_score_cpa,
            f"comparison.{task_name}.quality_ratio": quality_score_ai / quality_score_cpa if quality_score_cpa > 0 else 0,
        }

        mlflow.log_metrics(metrics)

        # Log summary
        summary = {
            "task": task_name,
            "ai_exceeds_cpa_accuracy": ai_accuracy > cpa_accuracy,
            "ai_faster_than_cpa": ai_time_minutes < cpa_time_minutes,
            "ai_cheaper_than_cpa": ai_cost_dollars < cpa_cost_dollars,
            "ai_higher_quality": quality_score_ai > quality_score_cpa,
            "overall_ai_superior": (
                ai_accuracy >= cpa_accuracy and
                quality_score_ai >= quality_score_cpa
            )
        }

        mlflow.log_dict(summary, f"cpa_comparison_{task_name}.json")

        logger.info(
            f"CPA Comparison ({task_name}): "
            f"Accuracy {ai_accuracy:.1%} vs {cpa_accuracy:.1%}, "
            f"Quality {quality_score_ai:.1%} vs {quality_score_cpa:.1%}"
        )


# Global MLflow manager instance
mlflow_manager = MLflowManager()
