from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.chat import ChatSession, ChatMessage
from src.repositories.chat_repository import ChatRepository


class ConversationMemoryManager:
    """Manages chat session history, conversation buffer, and windowing."""

    def __init__(self, session: AsyncSession):
        self.repository = ChatRepository(session)

    async def get_or_create_session(
        self,
        session_id: Optional[str],
        user_id: str,
        llm_provider: str = "mock"
    ) -> ChatSession:
        if session_id:
            chat_session = await self.repository.get_with_messages(session_id)
            if chat_session:
                return chat_session

        # Create new session
        new_session = ChatSession(
            title="AI Research Session",
            user_id=user_id,
            llm_provider=llm_provider
        )
        return await self.repository.create(new_session)

    async def save_interaction(
        self,
        session_id: str,
        question: str,
        answer: str,
        citations: List[Dict] = None,
        latency_ms: float = 0.0
    ) -> None:
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=question
        )
        await self.repository.add_message(user_msg)

        assistant_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=answer,
            citations=citations or [],
            latency_ms=latency_ms
        )
        await self.repository.add_message(assistant_msg)

    async def get_recent_history(
        self,
        session_id: str,
        window_size: int = 6
    ) -> List[Dict[str, str]]:
        chat_session = await self.repository.get_with_messages(session_id)
        if not chat_session or not chat_session.messages:
            return []

        recent_messages = chat_session.messages[-window_size:]
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]
