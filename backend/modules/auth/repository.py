"""DB access for users."""
from sqlalchemy import select

from backend.core.repository import BaseRepository
from backend.modules.auth.models import User


# Handles DB access for users
class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))
