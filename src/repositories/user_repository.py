from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User, APIKey
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        stmt = select(User).where((User.email == identifier) | (User.username == identifier))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()


class APIKeyRepository(BaseRepository[APIKey]):
    def __init__(self, session: AsyncSession):
        super().__init__(APIKey, session)

    async def get_by_key_hash(self, key_hash: str) -> Optional[APIKey]:
        stmt = select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active == True)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
