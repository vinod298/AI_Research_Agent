from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    document_title: str
    filename: str
    page_number: int
    chunk_id: str
    relevance_score: float
    snippet: str


class SearchQuery(BaseModel):
    query: str = Field(..., min_length=2, description="Search question or query phrase")
    top_k: int = Field(default=5, ge=1, le=20)
    search_type: str = Field(default="hybrid", description="semantic, keyword, or hybrid")
    document_ids: Optional[List[str]] = Field(default=None, description="Optional filter by document IDs")
    category_filter: Optional[str] = Field(default=None, description="Optional filter by TF category")


class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    filename: str
    page_number: int
    content: str
    score: float
    search_mode: str
    metadata: Dict[str, Any] = {}


class SearchResponse(BaseModel):
    query: str
    search_type: str
    total_results: int
    results: List[SearchResultItem]
    latency_ms: float
