from typing import Optional
from sqlalchemy import Float, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import BaseModel


class AnalyticsEvent(BaseModel):
    __tablename__ = "analytics_events"

    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # document_upload, search, chat_query, classification, compare, summarize
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status_code: Mapped[int] = mapped_column(default=200, nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)


class ProcessingLog(BaseModel):
    __tablename__ = "processing_logs"

    document_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    step: Mapped[str] = mapped_column(String(100), nullable=False) # extract, chunk, embed, vector_index, classify
    status: Mapped[str] = mapped_column(String(50), nullable=False) # success, failed, warning
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
