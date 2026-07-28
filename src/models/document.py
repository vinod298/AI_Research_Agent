from typing import List, Optional
from sqlalchemy import Float, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="application/pdf", nullable=False)
    
    # Metadata & Status
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False) # pending, processing, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # TensorFlow Category & Metadata JSON
    predicted_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    doc_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    
    # Relationships
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="documents")
    chunks: Mapped[List["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(BaseModel):
    __tablename__ = "document_chunks"

    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vector_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    chunk_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
