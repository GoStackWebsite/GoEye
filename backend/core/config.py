"""Backend settings: shared settings plus backend-only values."""
from pydantic import Field

from shared.config import Settings


# Settings used only by the backend (database, auth, CORS) on top of the shared ones; secrets must come from .env
class BackendSettings(Settings):
    database_url: str
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 12
    cors_origins: list[str]


settings = BackendSettings()
