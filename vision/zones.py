"""One camera's zones and count lines in pixel coordinates, kept in step with what is drawn in the dashboard."""
from dataclasses import dataclass

import numpy as np
from shapely.geometry import Point, Polygon

from shared.bus import load_zones
from shared.schemas import ZoneKind, ZoneShape

ZONE_REFRESH_SECONDS = 2.0  # how often the saved shapes are read again, so a change shows without a restart


# A count line across an entrance: a crossing towards the in_side is IN, the other way is OUT
@dataclass(frozen=True, slots=True)
class CountLine:
    id: int
    name: str
    a: tuple[float, float]
    b: tuple[float, float]
    in_side: int


# An area of floor; a person is in it when their foot point is inside the polygon
@dataclass(frozen=True, slots=True)
class FloorZone:
    id: int
    name: str
    polygon: Polygon
    outline: np.ndarray  # the corners as integer pixels, for drawing

    def contains(self, x: float, y: float) -> bool:
        return self.polygon.contains(Point(x, y))


# Loads a camera's shapes from the bus and scales them to its frame size; version changes whenever they do
class CameraZones:
    def __init__(self, camera_id: str) -> None:
        self.camera_id = camera_id
        self.lines: list[CountLine] = []
        self.zones: list[FloorZone] = []
        self.version = 0
        self.frame_height = 0
        self._shapes: list[ZoneShape] = []
        self._size = (0, 0)
        self._loaded_at = float("-inf")

    def refresh(self, width: int, height: int, now: float) -> None:
        """Read the saved shapes again if they are due, and rebuild when they or the frame size changed."""
        if now - self._loaded_at < ZONE_REFRESH_SECONDS:
            return
        self._loaded_at = now
        shapes = load_zones(self.camera_id)
        if shapes == self._shapes and (width, height) == self._size:
            return
        self._shapes, self._size, self.frame_height = shapes, (width, height), height
        self.lines, self.zones = [], []
        for shape in shapes:
            pixels = [(p.x * width, p.y * height) for p in shape.points]
            if shape.kind is ZoneKind.LINE:
                self.lines.append(CountLine(shape.id, shape.name, pixels[0], pixels[1], shape.in_side))
            else:
                self.zones.append(FloorZone(shape.id, shape.name, Polygon(pixels), np.array(pixels, np.int32)))
        self.version += 1
