"""Standard response envelope used by every endpoint, for success and failure."""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


# Envelope returned by every endpoint: {success, message, data}
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str | None = None
    data: T | None = None


def ok(data: T | None = None, message: str | None = None) -> ApiResponse[T]:
    return ApiResponse(success=True, message=message, data=data)


def fail(message: str, data: Any = None) -> ApiResponse[Any]:
    return ApiResponse(success=False, message=message, data=data)
