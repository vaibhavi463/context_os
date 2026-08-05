from typing import Generic, TypeVar, Type, Any, Sequence
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, id: uuid.UUID | str) -> ModelType | None:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs: Any) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, id: uuid.UUID | str, **kwargs: Any) -> ModelType | None:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, id: uuid.UUID | str) -> bool:
        if isinstance(id, str):
            id = uuid.UUID(id)
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
