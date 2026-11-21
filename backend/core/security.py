"""Password hashing, JWT helpers, and keeping tokens out of the logs."""
import logging
import re
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from backend.core.config import settings

_hasher = PasswordHash.recommended()

_TOKEN_IN_URL = re.compile(r"([?&]token=)[^&\s]+")
_URL_ARG_INDEX = 2  # uvicorn access log args: (client, method, path with query, http version, status)


# Masks ?token= in uvicorn access-log lines: the live stream URL carries a login token that must not be logged
class RedactTokenFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, tuple) and len(record.args) > _URL_ARG_INDEX:
            args = list(record.args)
            args[_URL_ARG_INDEX] = _TOKEN_IN_URL.sub(r"\1<redacted>", str(args[_URL_ARG_INDEX]))
            record.args = tuple(args)
        return True


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
