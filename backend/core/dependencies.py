"""Shared FastAPI dependencies."""
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.core.exceptions import UnauthorizedError
from backend.core.security import decode_access_token

DbSession = Annotated[AsyncSession, Depends(get_session)]

_bearer = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str:
    if credentials is None:
        raise UnauthorizedError("Missing bearer token")
    try:
        return decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid or expired token")


CurrentUserId = Annotated[str, Depends(get_current_user_id)]
