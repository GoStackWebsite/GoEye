"""Settings loaded from environment / .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


# Settings used by both vision and backend; connection details and credentials must come from .env
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_url: str

    track_stream: str = "tracks"
    event_stream: str = "events"

    cameras: dict[str, str]  # camera id -> RTSP URL without credentials
    rtsp_user: str
    rtsp_password: str
    camera_timeout_seconds: float = 10.0
    camera_reconnect_seconds: float = 3.0

    stream_fps: float = 10.0          # live view frames per second sent to the dashboard
    stream_jpeg_quality: int = 80
    frame_ttl_seconds: float = 5.0    # a camera with no frame for this long shows as offline

    models_dir: str = "models"        # model files; the vision container mounts ./models here
    yolo_model: str = "yolo26n.pt"    # person detector; ultralytics downloads it into models_dir on first start
    detect_conf: float = 0.35         # minimum detection confidence
    detect_imgsz: int = 640           # inference size (multiple of 32)
    analysis_fps: float = 5.0         # frames per second per camera run through detection (CPU-bound)


settings = Settings()
