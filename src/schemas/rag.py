from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from src.schemas.search import Citation


class ChatMessageSchema(BaseModel):
    id: Optional[str] = None
    role: str # user, assistant, system
    content: str
    citations: Optional[List[Citation]] = None
    latency_ms: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, description="User question for RAG")
    session_id: Optional[str] = Field(default=None, description="Existing session ID or auto-created if null")
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: Optional[List[str]] = Field(default=None, description="Filter response to specific document IDs")
    llm_provider: Optional[str] = Field(default=None, description="mock, openai, anthropic, gemini, ollama, deepseek, mistral")
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    citations: List[Citation]
    confidence_score: float
    retrieved_chunks_count: int
    llm_provider: str
    latency_ms: float


class CompareRequest(BaseModel):
    document_ids: List[str] = Field(..., min_items=2, description="List of document IDs to compare")
    aspects: Optional[List[str]] = Field(
        default=["Methodology", "Advantages", "Disadvantages", "Architecture", "Complexity", "Conclusion"],
        description="Aspects to evaluate across documents"
    )
    llm_provider: Optional[str] = Field(default=None)


class ComparisonMatrixItem(BaseModel):
    aspect: str
    document_summaries: Dict[str, str] # map doc_id or filename to aspect text


class CompareResponse(BaseModel):
    compared_documents: List[Dict[str, str]]
    comparison_table: List[ComparisonMatrixItem]
    narrative_analysis: str
    conclusion: str
    latency_ms: float


class SummarizeRequest(BaseModel):
    document_id: str = Field(..., description="Document ID to generate summary for")
    summary_type: str = Field(
        default="all",
        description="executive, technical, detailed, bullet, or all"
    )
    llm_provider: Optional[str] = Field(default=None)


class SummarizeResponse(BaseModel):
    document_id: str
    document_title: str
    executive_summary: Optional[str] = None
    technical_summary: Optional[str] = None
    detailed_summary: Optional[str] = None
    bullet_summary: Optional[List[str]] = None
    key_takeaways: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    future_work: Optional[List[str]] = None
    latency_ms: float
