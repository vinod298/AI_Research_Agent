from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.chat import ChatSession, ChatMessage
from src.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatSession]):
    def __init__(self, session: AsyncSession):
        super().__init__(ChatSession, session)

    async def get_with_messages(self, session_id: str) -> Optional[ChatSession]:
        stmt = select(ChatSession).options(selectinload(ChatSession.messages)).where(ChatSession.id == session_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_user_sessions(self, user_id: str, limit: int = 50) -> List[ChatSession]:
        stmt = select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_message(self, message: ChatMessage) -> ChatMessage:
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message
