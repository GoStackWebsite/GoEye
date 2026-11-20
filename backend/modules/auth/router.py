"""HTTP endpoints for authentication."""
from fastapi import APIRouter

from backend.core.responses import ApiResponse, ok
from backend.modules.auth.schemas import LoginIn, TokenOut
from backend.modules.auth.service import AuthServiceDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ApiResponse[TokenOut])
async def login(data: LoginIn, service: AuthServiceDep):
    return ok(await service.login(data), "Login successful")
