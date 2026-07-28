from typing import Generic, List, Optional, Type, TypeVar
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id_val: str) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id_val)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, id_val: str, values: dict) -> Optional[ModelType]:
        stmt = update(self.model).where(self.model.id == id_val).values(**values).execution_options(synchronize_session="fetch")
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_by_id(id_val)

    async def delete(self, id_val: str) -> bool:
        stmt = delete(self.model).where(self.model.id == id_val)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def count(self) -> int:
        stmt = select(func.count(self.model.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0
