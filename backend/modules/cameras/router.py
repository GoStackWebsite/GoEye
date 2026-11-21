"""HTTP endpoints for cameras."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.core.dependencies import CurrentUserId, CurrentUserIdFromQuery
from backend.core.responses import ApiResponse, ok
from backend.modules.cameras.schemas import CameraOut
from backend.modules.cameras.service import MJPEG_BOUNDARY, CameraServiceDep

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_model=ApiResponse[list[CameraOut]])
def list_cameras(service: CameraServiceDep, _user: CurrentUserId):
    return ok(service.list_cameras())


# <img> tags cannot send an Authorization header, so the live stream takes the token as ?token=
@router.get("/{camera_id}/stream")
def stream_camera(camera_id: str, service: CameraServiceDep, _user: CurrentUserIdFromQuery):
    service.ensure_exists(camera_id)
    return StreamingResponse(
        service.mjpeg(camera_id), media_type=f"multipart/x-mixed-replace; boundary={MJPEG_BOUNDARY}"
    )
