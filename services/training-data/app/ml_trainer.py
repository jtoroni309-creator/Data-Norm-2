"""
ML Training Module for CPA-Level Audit AI

Trains transformer models on SEC financial data to develop:
- Financial statement comprehension
- Audit reasoning capabilities
- Anomaly detection
- Financial analysis
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
from sentence_transformers import SentenceTransformer
import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class FinancialDataset(Dataset):
    """
    PyTorch Dataset for SEC financial filings
    """

    def __init__(self, data: List[Dict], tokenizer, max_length: int = 512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # Combine filing text for training
        text = f"Company: {item.get('company_name', 'Unknown')}\n"
        text += f"Form: {item.get('form', 'Unknown')}\n"
        text += f"Filing Date: {item.get('filing_date', 'Unknown')}\n"
        text += f"Content: {item.get('content', '')}"

        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': encoding['input_ids'].squeeze()  # For language modeling
        }


class FinancialMLTrainer:
    """
    Main ML training orchestrator for financial audit AI
    """

    def __init__(
        self,
        model_name: str = "bert-base-uncased",
        output_dir: str = "/app/models",
        use_gpu: bool = True
    ):
        """
        Initialize the ML trainer

        Args:
            model_name: Base model to fine-tune
            output_dir: Directory to save trained models
            use_gpu: Whether to use GPU acceleration
        """
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Check GPU availability
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        if self.device == "cuda":
            logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            logger.info("Training on CPU")

        self.tokenizer = None
        self.model = None

    async def load_training_data(
        self,
        db: AsyncSession,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Load SEC filing data from database for training

        Args:
            db: Database session
            limit: Optional limit on number of filings

        Returns:
            List of filing records
        """
        logger.info("Loading training data from database...")

        query = """
            SELECT
                cik,
                company_name,
                form,
                filing_date,
                accession_number
            FROM atlas.filings
            ORDER BY filing_date DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        result = await db.execute(text(query))
        filings = result.fetchall()

        # Convert to list of dicts
        data = []
        for filing in filings:
            data.append({
                'cik': filing[0],
                'company_name': filing[1],
                'form': filing[2],
                'filing_date': filing[3],
                'accession_number': filing[4],
                'content': f"SEC Filing {filing[2]} for {filing[1]}"  # Simplified for now
            })

        logger.info(f"Loaded {len(data)} filings for training")
        return data

    def prepare_model(self, task: str = "language_modeling"):
        """
        Initialize model and tokenizer

        Args:
            task: Type of task (language_modeling, classification, etc.)
        """
        logger.info(f"Preparing model: {self.model_name}")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        if task == "language_modeling":
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
        elif task == "classification":
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=2  # Binary classification for anomaly detection
            )

        self.model.to(self.device)
        logger.info(f"Model loaded on {self.device}")

    async def train(
        self,
        training_data: List[Dict],
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-5,
        save_steps: int = 100,
        eval_steps: int = 100
    ) -> Dict[str, Any]:
        """
        Train the model on financial data

        Args:
            training_data: List of training examples
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            save_steps: Steps between model saves
            eval_steps: Steps between evaluations

        Returns:
            Training metrics and results
        """
        logger.info(f"Starting training with {len(training_data)} examples...")

        if not self.model or not self.tokenizer:
            raise ValueError("Model not prepared. Call prepare_model() first.")

        # Create dataset
        dataset = FinancialDataset(training_data, self.tokenizer)

        # Split into train/val
        train_size = int(0.9 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )

        logger.info(f"Train size: {train_size}, Val size: {val_size}")

        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir / "checkpoints"),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=0.01,
            logging_dir=str(self.output_dir / "logs"),
            logging_steps=10,
            save_steps=save_steps,
            eval_steps=eval_steps,
            eval_strategy="steps",  # Updated from evaluation_strategy for newer transformers
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            fp16=self.device == "cuda",  # Mixed precision on GPU
            gradient_accumulation_steps=2,  # Effective batch size = 8
            warmup_steps=100,
            report_to="none"  # Disable wandb/tensorboard for now
        )

        # Data collator
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)

        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator
        )

        # Train
        logger.info("Beginning training...")
        train_result = trainer.train()

        # Save final model
        final_model_path = self.output_dir / "final_model"
        trainer.save_model(str(final_model_path))
        self.tokenizer.save_pretrained(str(final_model_path))

        logger.info(f"Training complete! Model saved to {final_model_path}")

        # Return metrics
        return {
            "train_loss": train_result.training_loss,
            "train_runtime": train_result.metrics.get("train_runtime", 0),
            "train_samples_per_second": train_result.metrics.get("train_samples_per_second", 0),
            "eval_loss": trainer.evaluate().get("eval_loss", 0),
            "model_path": str(final_model_path),
            "training_data_size": len(training_data),
            "completed_at": datetime.utcnow().isoformat()
        }

    async def train_embeddings(
        self,
        training_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Train sentence embeddings for financial document retrieval

        Args:
            training_data: List of training examples

        Returns:
            Training metrics
        """
        logger.info("Training sentence embeddings...")

        # Use pre-trained sentence transformer
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Prepare texts
        texts = [
            f"{d['company_name']} {d['form']} {d['content']}"
            for d in training_data
        ]

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings = model.encode(texts, show_progress_bar=True)

        # Save embeddings
        embeddings_path = self.output_dir / "embeddings"
        embeddings_path.mkdir(exist_ok=True)

        import numpy as np
        np.save(str(embeddings_path / "financial_embeddings.npy"), embeddings)

        logger.info(f"Embeddings saved to {embeddings_path}")

        return {
            "num_documents": len(texts),
            "embedding_dim": embeddings.shape[1],
            "embeddings_path": str(embeddings_path),
            "completed_at": datetime.utcnow().isoformat()
        }


async def start_training_pipeline(
    model_name: str = "bert-base-uncased",
    epochs: int = 3,
    batch_size: int = 4,
    data_limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Main entry point for starting ML training

    Args:
        model_name: Base model to use
        epochs: Number of training epochs
        batch_size: Training batch size
        data_limit: Optional limit on training data

    Returns:
        Training results
    """
    logger.info("=" * 80)
    logger.info("Starting CPA-Level Audit AI Training Pipeline")
    logger.info("=" * 80)

    try:
        # Initialize trainer
        trainer = FinancialMLTrainer(
            model_name=model_name,
            use_gpu=True
        )

        # Load training data
        async with AsyncSessionLocal() as db:
            training_data = await trainer.load_training_data(db, limit=data_limit)

        if len(training_data) == 0:
            raise ValueError("No training data found in database")

        # Prepare model
        trainer.prepare_model(task="language_modeling")

        # Train main model
        logger.info("\n" + "=" * 80)
        logger.info("Phase 1: Training Financial Language Model")
        logger.info("=" * 80)
        train_results = await trainer.train(
            training_data=training_data,
            epochs=epochs,
            batch_size=batch_size
        )

        # Train embeddings
        logger.info("\n" + "=" * 80)
        logger.info("Phase 2: Training Document Embeddings")
        logger.info("=" * 80)
        embedding_results = await trainer.train_embeddings(training_data)

        # Combine results
        results = {
            "status": "success",
            "model_training": train_results,
            "embedding_training": embedding_results,
            "total_training_examples": len(training_data),
            "pipeline_completed_at": datetime.utcnow().isoformat()
        }

        logger.info("\n" + "=" * 80)
        logger.info("Training Pipeline Complete!")
        logger.info("=" * 80)
        logger.info(f"Model saved: {train_results['model_path']}")
        logger.info(f"Embeddings saved: {embedding_results['embeddings_path']}")
        logger.info(f"Train loss: {train_results['train_loss']:.4f}")
        logger.info(f"Eval loss: {train_results['eval_loss']:.4f}")
        logger.info("=" * 80)

        return results

    except Exception as e:
        logger.error(f"Training pipeline failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    # Run training when executed directly
    results = asyncio.run(start_training_pipeline(
        epochs=3,
        batch_size=4
    ))

    print("\n" + "=" * 80)
    print("TRAINING RESULTS")
    print("=" * 80)
    print(f"Status: {results['status']}")
    if results['status'] == 'success':
        print(f"Training examples: {results['total_training_examples']}")
        print(f"Model path: {results['model_training']['model_path']}")
        print(f"Train loss: {results['model_training']['train_loss']:.4f}")
        print(f"Eval loss: {results['model_training']['eval_loss']:.4f}")
    else:
        print(f"Error: {results.get('error', 'Unknown')}")
    print("=" * 80)
