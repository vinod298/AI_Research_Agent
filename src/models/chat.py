from typing import List, Optional
from sqlalchemy import Float, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import BaseModel


class ChatSession(BaseModel):
    __tablename__ = "chat_sessions"

    title: Mapped[str] = mapped_column(String(255), default="New Research Session", nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    llm_provider: Mapped[str] = mapped_column(String(50), default="mock", nullable=False)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(BaseModel):
    __tablename__ = "chat_messages"

    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False) # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[Optional[dict]] = mapped_column(JSON, default=list, nullable=True) # JSON list of cited chunks
    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
