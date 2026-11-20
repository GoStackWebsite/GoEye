"""HTTP endpoints for cameras."""
from fastapi import APIRouter, status

from backend.core.dependencies import CurrentUserId
from backend.core.responses import ApiResponse, ok
from backend.modules.cameras.schemas import CameraCreate, CameraOut
from backend.modules.cameras.service import CameraServiceDep

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_model=ApiResponse[list[CameraOut]])
async def list_cameras(service: CameraServiceDep, _user: CurrentUserId):
    return ok(await service.list_cameras())


@router.post("", response_model=ApiResponse[CameraOut], status_code=status.HTTP_201_CREATED)
async def create_camera(data: CameraCreate, service: CameraServiceDep, _user: CurrentUserId):
    return ok(await service.create_camera(data), "Camera created")
