"""Settings loaded from environment / .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


# Settings used by both vision and backend
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+asyncpg://goeye:goeye@localhost:5432/goeye"

    track_stream: str = "tracks"
    event_stream: str = "events"

    yolo_model: str = "yolov8n.pt"


settings = Settings()
