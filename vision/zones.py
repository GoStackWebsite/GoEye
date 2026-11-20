"""Counter, shelf, entrance polygons per camera."""
from shapely.geometry import Point, Polygon

# camera_id -> zone_id -> polygon (pixel coordinates)
ZONES: dict[str, dict[str, Polygon]] = {}


def zones_for_point(camera_id: str, x: float, y: float) -> list[str]:
    p = Point(x, y)
    return [zid for zid, poly in ZONES.get(camera_id, {}).items() if poly.contains(p)]
