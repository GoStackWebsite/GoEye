"""Access to camera data: the configured cameras (.env) and their latest frames (Redis)."""
from backend.core.config import settings
from shared.bus import latest_frame


# Reads the camera list from settings and live frames from the bus
class CameraRepository:
    def ids(self) -> list[str]:
        return list(settings.cameras)

    def exists(self, camera_id: str) -> bool:
        return camera_id in settings.cameras

    def latest_frame(self, camera_id: str) -> bytes | None:
        return latest_frame(camera_id)
