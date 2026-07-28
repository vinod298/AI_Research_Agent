from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    text: Optional[str] = Field(default=None, description="Text to classify")
    document_id: Optional[str] = Field(default=None, description="Or document ID to classify existing document content")


class CategoryScore(BaseModel):
    category: str
    confidence: float


class ClassifyResponse(BaseModel):
    predicted_category: str
    confidence: float
    all_scores: List[CategoryScore]
    latency_ms: float
