"""
Aura Audit AI - Disclosures Service
AI-powered disclosure note drafting with RAG, citations, and confidence scores
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, confloat

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura Audit AI - Disclosures Service",
    description="AI-powered disclosure drafting with citations and confidence scores",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# Pydantic Models (Schema-Constrained)
# ========================================

class Citation(BaseModel):
    """Source citation for disclosure content"""
    source_type: str
    source_reference: str
    section: Optional[str] = None
    excerpt: Optional[str] = None


class NoteItem(BaseModel):
    """Individual disclosure note item"""
    label: str
    text: str
    citations: List[Citation] = Field(default_factory=list)
    confidence: confloat(ge=0.0, le=1.0)
    contradictions: List[dict] = Field(default_factory=list)


class NoteDraft(BaseModel):
    """Complete disclosure note draft"""
    section: str
    title: str
    items: List[NoteItem]
    overall_confidence: confloat(ge=0.0, le=1.0)
    model_version: str
    prompt_version: str
    temperature: float


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "disclosures", "version": "1.0.0"}


@app.post("/disclosures/draft")
async def draft_disclosure(engagement_id: UUID, section: str):
    """Generate AI-powered disclosure with citations"""
    # Mock response for demonstration
    return {
        "note_draft": NoteDraft(
            section=section,
            title="Revenue Recognition",
            items=[
                NoteItem(
                    label="Revenue Recognition Policy",
                    text="The Company recognizes revenue when control transfers.",
                    citations=[
                        Citation(source_type="us-gaap", source_reference="ASC 606")
                    ],
                    confidence=0.92,
                    contradictions=[]
                )
            ],
            overall_confidence=0.90,
            model_version="gpt-4-turbo",
            prompt_version="v1.0",
            temperature=0.1
        )
    }
