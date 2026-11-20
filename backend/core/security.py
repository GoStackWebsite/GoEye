"""Password hashing and JWT helpers."""
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from backend.core.config import settings

_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _hasher.verify(password, password_hash)


def create_access_token(subject: str) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": subject, "exp": expires}, settings.jwt_secret, settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    """Return the token subject; raises jwt.InvalidTokenError if invalid."""
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return payload["sub"]
