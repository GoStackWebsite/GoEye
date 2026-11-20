"""Backend settings: shared settings plus backend-only values."""
from pydantic import Field

from shared.config import Settings


# Settings used only by the backend (auth, CORS) on top of the shared ones
class BackendSettings(Settings):
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 12
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])


settings = BackendSettings()
