"""Shared FastAPI dependencies."""
from typing import Annotated

import jwt
from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.core.exceptions import UnauthorizedError
from backend.core.security import decode_access_token

DbSession = Annotated[AsyncSession, Depends(get_session)]

_bearer = HTTPBearer(auto_error=False)


def _user_id_from_token(token: str | None) -> str:
    if not token:
        raise UnauthorizedError("Missing bearer token")
    try:
        return decode_access_token(token)
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid or expired token")


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str:
    return _user_id_from_token(credentials.credentials if credentials else None)


def get_current_user_id_from_query(token: Annotated[str | None, Query()] = None) -> str:
    """For endpoints opened by <img>/<video> tags, which cannot send an Authorization header."""
    return _user_id_from_token(token)


CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentUserIdFromQuery = Annotated[str, Depends(get_current_user_id_from_query)]
