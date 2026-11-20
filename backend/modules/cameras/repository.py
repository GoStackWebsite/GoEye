"""DB access for cameras."""
from sqlalchemy import select

from backend.core.repository import BaseRepository
from backend.modules.cameras.models import Camera


# Handles DB access for cameras
class CameraRepository(BaseRepository[Camera]):
    model = Camera

    async def list(self) -> list[Camera]:
        return list((await self.session.scalars(select(Camera).order_by(Camera.id))).all())
