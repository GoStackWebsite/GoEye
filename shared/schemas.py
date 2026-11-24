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


# What a shape drawn on a camera is used for
class ZoneKind(StrEnum):
    ZONE = "zone"  # an area of floor (polygon)
    LINE = "line"  # a count line across an entrance (two points)


# A point in a camera frame as fractions of its width and height, so shapes survive a change of resolution
class Point(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)


# A zone or count line drawn on one camera, as the backend hands it to vision
class ZoneShape(BaseModel):
    id: int
    name: str
    kind: ZoneKind
    points: list[Point]
    in_side: int = 1  # count lines only: the side that is IN, as the sign of the cross product from point 1 to point 2


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
    LINE_IN = "line_in"
    LINE_OUT = "line_out"
    ZONE_ENTER = "zone_enter"
    ZONE_EXIT = "zone_exit"


# A behavior detected by an analyzer
class Event(BaseModel):
    camera_id: str
    type: EventType
    ts: datetime
    track_ids: list[int] = Field(default_factory=list)
    zone_id: str | None = None
    score: float | None = None
    data: dict[str, Any] = Field(default_factory=dict)
