"""
Aura Audit AI - Training Data Service

ML model training data management:
- Training dataset curation
- Data labeling and annotation
- Model performance tracking
- Feature engineering
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura Audit AI - Training Data Service",
    description="ML training data management and curation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# Schemas
# ========================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


# ========================================
# Mock Authentication
# ========================================

async def get_current_user_id() -> UUID:
    """Mock function to get current user ID"""
    return UUID("00000000-0000-0000-0000-000000000001")


# ========================================
# Health & Status
# ========================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="training-data",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aura Audit AI - Training Data Service",
        "version": "1.0.0",
        "features": [
            "Training dataset curation",
            "Data labeling and annotation",
            "Model performance tracking",
            "Feature engineering"
        ],
        "docs": "/docs"
    }


# ========================================
# Training Data Endpoints
# ========================================

@app.get("/datasets")
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """List available training datasets"""
    logger.info("Listing training datasets")

    return {
        "datasets": [],
        "total": 0,
        "skip": skip,
        "limit": limit
    }


@app.post("/datasets")
async def create_dataset(
    name: str,
    description: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Create new training dataset"""
    logger.info(f"Creating dataset: {name}")

    return {
        "dataset_id": "placeholder",
        "name": name,
        "description": description,
        "status": "created"
    }


@app.post("/datasets/{dataset_id}/labels")
async def add_labels(
    dataset_id: str,
    labels: List[dict],
    db: AsyncSession = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Add labeled data to dataset"""
    logger.info(f"Adding {len(labels)} labels to dataset {dataset_id}")

    return {
        "dataset_id": dataset_id,
        "labels_added": len(labels),
        "status": "success"
    }


# ========================================
# ML Training Endpoints
# ========================================

class TrainingRequest(BaseModel):
    """Training configuration"""
    model_name: str = "bert-base-uncased"
    epochs: int = 3
    batch_size: int = 4
    data_limit: Optional[int] = None


class TrainingResponse(BaseModel):
    """Training result"""
    status: str
    message: str
    results: Optional[dict] = None


@app.post("/training/start", response_model=TrainingResponse)
async def start_training(
    request: TrainingRequest,
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Start ML training pipeline

    This will:
    1. Load SEC filing data from database
    2. Fine-tune a transformer model on financial data
    3. Train document embeddings
    4. Save trained models
    """
    logger.info(f"Starting training with config: {request}")

    try:
        from .ml_trainer import start_training_pipeline

        # Start training (this is async but runs in background)
        results = await start_training_pipeline(
            model_name=request.model_name,
            epochs=request.epochs,
            batch_size=request.batch_size,
            data_limit=request.data_limit
        )

        if results["status"] == "success":
            return TrainingResponse(
                status="success",
                message="Training completed successfully",
                results=results
            )
        else:
            return TrainingResponse(
                status="failed",
                message=f"Training failed: {results.get('error', 'Unknown error')}",
                results=results
            )

    except Exception as e:
        logger.error(f"Training request failed: {e}", exc_info=True)
        return TrainingResponse(
            status="error",
            message=f"Failed to start training: {str(e)}"
        )


@app.get("/training/status")
async def training_status(
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Check training status and GPU availability"""
    import torch

    gpu_available = torch.cuda.is_available()
    gpu_info = {}

    if gpu_available:
        gpu_info = {
            "device_name": torch.cuda.get_device_name(0),
            "device_count": torch.cuda.device_count(),
            "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
            "memory_allocated_gb": torch.cuda.memory_allocated(0) / 1e9,
            "memory_cached_gb": torch.cuda.memory_reserved(0) / 1e9
        }

    return {
        "status": "ready",
        "gpu_available": gpu_available,
        "gpu_info": gpu_info if gpu_available else None,
        "models_directory": "/app/models"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
