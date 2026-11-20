"""Business logic for authentication."""
from typing import Annotated

from fastapi import Depends

from backend.core.dependencies import DbSession
from backend.core.exceptions import UnauthorizedError
from backend.core.security import create_access_token, verify_password
from backend.modules.auth.repository import UserRepository
from backend.modules.auth.schemas import LoginIn, TokenOut


# Verifies credentials and issues access tokens
class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def login(self, data: LoginIn) -> TokenOut:
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")
        return TokenOut(access_token=create_access_token(str(user.id)))


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(UserRepository(db))


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
