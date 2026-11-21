"""Business logic for cameras: listing with online status and the MJPEG live stream."""
import time
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends

from backend.core.config import settings
from backend.core.exceptions import NotFoundError
from backend.modules.cameras.repository import CameraRepository
from backend.modules.cameras.schemas import CameraOut

MJPEG_BOUNDARY = "frame"


# Lists cameras and turns their latest frames into a browser-viewable MJPEG stream
class CameraService:
    def __init__(self, repo: CameraRepository) -> None:
        self.repo = repo

    def list_cameras(self) -> list[CameraOut]:
        return [CameraOut(id=cid, online=self.repo.latest_frame(cid) is not None) for cid in self.repo.ids()]

    def ensure_exists(self, camera_id: str) -> None:
        if not self.repo.exists(camera_id):
            raise NotFoundError(f"Camera '{camera_id}' is not configured")

    def mjpeg(self, camera_id: str) -> Iterator[bytes]:
        """Yield each new frame as one MJPEG part; runs until the client disconnects."""
        interval = 1.0 / settings.stream_fps
        last: bytes | None = None
        while True:
            frame = self.repo.latest_frame(camera_id)
            if frame is not None and frame != last:
                last = frame
                yield (f"--{MJPEG_BOUNDARY}\r\nContent-Type: image/jpeg\r\n"
                       f"Content-Length: {len(frame)}\r\n\r\n").encode() + frame + b"\r\n"
            time.sleep(interval)


def get_camera_service() -> CameraService:
    return CameraService(CameraRepository())


CameraServiceDep = Annotated[CameraService, Depends(get_camera_service)]
