from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.document import Document, DocumentChunk
from src.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)

    async def get_with_chunks(self, document_id: str) -> Optional[Document]:
        stmt = select(Document).options(selectinload(Document.chunks)).where(Document.id == document_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        stmt = select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def total_pages_processed(self) -> int:
        stmt = select(func.sum(Document.page_count))
        res = await self.session.execute(stmt)
        return res.scalar() or 0

    async def get_category_distribution(self) -> List[dict]:
        stmt = select(Document.predicted_category, func.count(Document.id)).group_by(Document.predicted_category)
        res = await self.session.execute(stmt)
        return [{"category": row[0] or "Unclassified", "count": row[1]} for row in res.all()]


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    def __init__(self, session: AsyncSession):
        super().__init__(DocumentChunk, session)

    async def get_by_document(self, document_id: str) -> List[DocumentChunk]:
        stmt = select(DocumentChunk).options(selectinload(DocumentChunk.document)).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_all_with_document(self, limit: int = 1000) -> List[DocumentChunk]:
        stmt = select(DocumentChunk).options(selectinload(DocumentChunk.document)).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def delete_by_document(self, document_id: str) -> int:
        chunks = await self.get_by_document(document_id)
        for chunk in chunks:
            await self.session.delete(chunk)
        return len(chunks)
