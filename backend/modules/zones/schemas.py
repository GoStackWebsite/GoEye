from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from shared.schemas import Point, ZoneKind, ZoneShape

LINE_POINTS = 2
MIN_ZONE_POINTS = 3
MAX_ZONE_POINTS = 32
MAX_NAME_LENGTH = 64  # the width of the name column


# A zone or count line as the dashboard sends it when creating or changing one
class ZoneIn(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_NAME_LENGTH)]
    kind: ZoneKind
    points: list[Point] = Field(max_length=MAX_ZONE_POINTS)
    in_side: Literal[1, -1] = 1

    @model_validator(mode="after")
    def check_point_count(self) -> "ZoneIn":
        if self.kind is ZoneKind.LINE and len(self.points) != LINE_POINTS:
            raise ValueError(f"A count line needs exactly {LINE_POINTS} points")
        if self.kind is ZoneKind.ZONE and len(self.points) < MIN_ZONE_POINTS:
            raise ValueError(f"A zone needs at least {MIN_ZONE_POINTS} points")
        return self


# A zone or count line as returned by the API
class ZoneOut(ZoneShape):
    model_config = ConfigDict(from_attributes=True)

    camera_id: str


# IN and OUT totals of one count line
class LineCountOut(BaseModel):
    id: int
    camera_id: str
    name: str
    entered: int
    left: int


# How many people are in one zone right now
class ZoneOccupancyOut(BaseModel):
    id: int
    camera_id: str
    name: str
    people: int | None  # None while the camera is not being analysed
