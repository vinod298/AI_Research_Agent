from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    page_number: int
    content: str
    token_count: int
    vector_id: Optional[str] = None
    chunk_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: str
    title: str
    filename: str
    file_size_bytes: int
    mime_type: str
    page_count: int
    chunk_count: int
    processing_status: str
    error_message: Optional[str] = None
    predicted_category: Optional[str] = None
    category_confidence: Optional[float] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    chunks: List[ChunkResponse] = []


class ReprocessRequest(BaseModel):
    chunk_size: int = Field(default=1000, ge=100, le=4000)
    chunk_overlap: int = Field(default=150, ge=0, le=500)
    reclassify: bool = Field(default=True)
