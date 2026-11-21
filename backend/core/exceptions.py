"""Application errors and the handlers that turn every error into an ApiResponse."""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.core.responses import fail


# Base error raised by services; carries the HTTP status and a user-facing message
class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


# Raised when a requested resource does not exist
class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


# Raised when credentials or a token are missing or invalid
class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED


def _error_response(status_code: int, message: str, data: object = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=fail(message, data).model_dump())


async def _app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return _error_response(exc.status_code, exc.message)


async def _http_error_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    return _error_response(exc.status_code, str(exc.detail))


async def _validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{"field": ".".join(map(str, e["loc"])), "error": e["msg"]} for e in exc.errors()]
    return _error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, "Validation failed", errors)


async def _unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception(exc)
    return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(StarletteHTTPException, _http_error_handler)
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(Exception, _unhandled_error_handler)
