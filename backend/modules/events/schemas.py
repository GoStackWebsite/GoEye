from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from shared.schemas import EventType


# Event as returned by the API
class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    camera_id: str
    type: EventType
    ts: datetime
    track_ids: list[int]
    zone_id: str | None
    score: float | None
    data: dict[str, Any]
