"""Common DB operations shared by every module repository."""
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


# Generic repository holding the session and the add operation; module repositories add their own queries
class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        await self.session.commit()
        return obj
