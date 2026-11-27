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
    # person detector; ultralytics downloads it into models_dir on first start. The large model: on the office cameras
    # nano and medium both took a chair back and a hanging decoration for people, large found the same people without
    # them (2026-11-27)
    yolo_model: str = "yolo26l.pt"
    # lowest detection score handed to the tracker, equal to its track_low_thresh: low-score boxes only keep people it
    # already follows (a seated person dipping below 0.45 flickered in and out); a new person still needs new_track_thresh
    detect_conf: float = 0.1
    detect_imgsz: int = 640           # inference size (multiple of 32)
    analysis_fps: float = 5.0         # frames per second per camera run through detection (CPU-bound)
    staff_model: str = "staff_cls.pt"  # staff-uniform classifier in models_dir (trained in camera_tool, copied here)
    staff_threshold: float = 0.5      # a person is staff when the classifier's staff probability is at least this


settings = Settings()