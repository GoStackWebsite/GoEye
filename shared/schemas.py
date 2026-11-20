"""The contract between vision and backend. Change carefully."""
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


# Who a tracked person is
class PersonRole(StrEnum):
    STAFF = "staff"
    CUSTOMER = "customer"
    UNKNOWN = "unknown"


# Bounding box in pixel coordinates
class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


# One tracked person in one frame
class TrackUpdate(BaseModel):
    camera_id: str
    track_id: int
    ts: datetime
    bbox: BBox
    confidence: float
    role: PersonRole = PersonRole.UNKNOWN
    zone_ids: list[str] = Field(default_factory=list)


# Kinds of behavior the analyzers can report
class EventType(StrEnum):
    IDLE = "idle"
    WORKING = "working"
    THEFT_RISK = "theft_risk"
    DWELL = "dwell"
    QUEUE = "queue"


# A behavior detected by an analyzer
class Event(BaseModel):
    camera_id: str
    type: EventType
    ts: datetime
    track_ids: list[int] = Field(default_factory=list)
    zone_id: str | None = None
    score: float | None = None
    data: dict[str, Any] = Field(default_factory=dict)
