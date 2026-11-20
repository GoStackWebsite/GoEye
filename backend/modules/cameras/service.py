"""Business logic for cameras."""
from typing import Annotated

from fastapi import Depends

from backend.core.dependencies import DbSession
from backend.core.exceptions import ConflictError
from backend.modules.cameras.models import Camera
from backend.modules.cameras.repository import CameraRepository
from backend.modules.cameras.schemas import CameraCreate, CameraOut


# Lists and registers cameras
class CameraService:
    def __init__(self, repo: CameraRepository) -> None:
        self.repo = repo

    async def list_cameras(self) -> list[CameraOut]:
        return [CameraOut.model_validate(c) for c in await self.repo.list()]

    async def create_camera(self, data: CameraCreate) -> CameraOut:
        if await self.repo.get(data.id):
            raise ConflictError(f"Camera '{data.id}' already exists")
        return CameraOut.model_validate(await self.repo.add(Camera(**data.model_dump())))


def get_camera_service(db: DbSession) -> CameraService:
    return CameraService(CameraRepository(db))


CameraServiceDep = Annotated[CameraService, Depends(get_camera_service)]
