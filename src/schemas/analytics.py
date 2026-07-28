from typing import Dict, List, Optional
from pydantic import BaseModel


class SystemMetrics(BaseModel):
    total_documents: int
    total_chunks: int
    total_pages_processed: int
    total_chat_sessions: int
    total_queries_executed: int
    total_users: int


class CategoryDistribution(BaseModel):
    category: str
    count: int


class LatencyStats(BaseModel):
    avg_search_latency_ms: float
    avg_rag_latency_ms: float
    avg_classification_latency_ms: float


class AnalyticsOverview(BaseModel):
    metrics: SystemMetrics
    category_distribution: List[CategoryDistribution]
    latency: LatencyStats
    recent_events_count: int
