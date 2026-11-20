"""Common DB operations shared by every module repository."""
from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


# Generic repository: get-by-id and add; module repositories extend it with their own queries
class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: Any) -> ModelT | None:
        return await self.session.get(self.model, id)

    async def add(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        await self.session.commit()
        return obj
