"""Counts people crossing count lines and records their time in zones, from each person's foot point.

The count-line rules are ported from camera_tool (app/analytics.py _observe_line / _update_line).
"""
import math
from dataclasses import dataclass, field
from datetime import datetime

from shared.schemas import Event, EventType, TrackUpdate
from vision.analyzers.base import Analyzer
from vision.zones import CameraZones, CountLine

LINE_MARGIN = 0.015            # feet closer to a line than this (fraction of the frame height) are "on the line"
LINE_MIN_FRAMES = 2            # frames a person must stay on the new side before the crossing counts
LINE_COOLDOWN_SECONDS = 1.5    # minimum gap between two crossings of the same line by the same person
SEGMENT_SLACK = 0.1            # a crossing counts this far past either end of the drawn line (fraction of its length)
ZONE_MIN_FRAMES = 2            # frames a person must be in (or out of) a zone before it counts, so an edge does not flicker


# What is known about one person and one count line
@dataclass(slots=True)
class LineState:
    side: int = 0                                   # last clear side: +1, -1, or 0 before the first clear view
    side_point: tuple[float, float] | None = None   # where they stood when that side was seen
    pending_side: int = 0                           # opposite side seen while a crossing is being confirmed
    pending_frames: int = 0
    pending_point: tuple[float, float] | None = None  # where they stood on that opposite side
    pending_at: float = 0.0
    last_cross: float = float("-inf")


# What is known about one person and one zone
@dataclass(slots=True)
class ZoneState:
    inside: bool = False
    entered: float = 0.0
    pending_frames: int = 0  # frames seen on the other side of the zone edge


# Everything remembered about one tracked person
@dataclass(slots=True)
class PersonState:
    lines: dict[int, LineState] = field(default_factory=dict)
    zones: dict[int, ZoneState] = field(default_factory=dict)


# Running totals of one count line since the vision service started
@dataclass(slots=True)
class LineCount:
    entered: int = 0
    left: int = 0


def signed_distance(line: CountLine, x: float, y: float) -> float:
    """Distance in pixels from a point to the line through a and b; the sign says which side it is on."""
    (ax, ay), (bx, by) = line.a, line.b
    dx, dy = bx - ax, by - ay
    return (dx * (y - ay) - dy * (x - ax)) / (math.hypot(dx, dy) or 1e-9)


def crosses_within_segment(line: CountLine, start: tuple[float, float], end: tuple[float, float]) -> bool:
    """Does the path from start to end cut the line between its two drawn points (with a little slack)?"""
    (ax, ay), (bx, by) = line.a, line.b
    dx, dy = bx - ax, by - ay
    d0, d1 = signed_distance(line, *start), signed_distance(line, *end)
    t = d0 / (d0 - d1) if d0 != d1 else 0.0
    qx, qy = start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1])
    along = ((qx - ax) * dx + (qy - ay) * dy) / ((dx * dx + dy * dy) or 1e-12)
    return -SEGMENT_SLACK <= along <= 1 + SEGMENT_SLACK


# Turns one camera's track updates into line_in / line_out and zone_enter / zone_exit events
class CrossingAnalyzer(Analyzer):
    name = "crossing"

    def __init__(self, camera_id: str, zones: CameraZones) -> None:
        super().__init__(camera_id)
        self.zones = zones
        self.counts: dict[int, LineCount] = {}
        self._people: dict[int, PersonState] = {}
        self._zones_version = zones.version

    def on_track_update(self, update: TrackUpdate) -> list[Event]:
        self._follow_zone_changes()
        person = self._people.setdefault(update.track_id, PersonState())
        foot = ((update.bbox.x1 + update.bbox.x2) / 2, update.bbox.y2)
        events = []
        for line in self.zones.lines:
            direction = self._update_line(person.lines.setdefault(line.id, LineState()), line, foot, update.ts.timestamp())
            if direction is not None:
                events.append(self._line_event(direction, line, update.track_id, update.ts))
        for zone in self.zones.zones:
            state = person.zones.setdefault(zone.id, ZoneState())
            if zone.contains(*foot) == state.inside:
                state.pending_frames = 0
                continue
            state.pending_frames += 1
            if state.pending_frames < ZONE_MIN_FRAMES:
                continue
            state.pending_frames = 0
            if state.inside:
                events.append(self._zone_exit(update.track_id, update.ts, zone.id, zone.name, state))
            else:
                state.inside, state.entered = True, update.ts.timestamp()
                events.append(self._event(EventType.ZONE_ENTER, update.track_id, update.ts, zone.name, {"id": zone.id}))
        return events

    def on_track_lost(self, track_id: int, ts: datetime) -> list[Event]:
        """A person is gone from view: settle a crossing they had just made and close the zones they were still in."""
        person = self._people.pop(track_id, None)
        if person is None:
            return []
        events = []
        # someone who steps over the line and straight through a door is seen on the new side only once:
        # their last sighting confirms the crossing, since they were never seen back on the old side
        for line in self.zones.lines:
            state = person.lines.get(line.id)
            if state is not None and state.pending_frames:
                direction = self._settle_crossing(state, line, state.pending_point, state.pending_at)
                if direction is not None:
                    events.append(self._line_event(direction, line, track_id, ts))
        names = {zone.id: zone.name for zone in self.zones.zones}
        events += [
            self._zone_exit(track_id, ts, zone_id, names[zone_id], state)
            for zone_id, state in person.zones.items()
            if state.inside and zone_id in names
        ]
        return events

    def occupancy(self) -> dict[int, int]:
        """How many people are in each zone right now (zone id -> people); empty zones are listed with 0."""
        people = {zone.id: 0 for zone in self.zones.zones}
        for person in self._people.values():
            for zone_id, state in person.zones.items():
                if state.inside and zone_id in people:
                    people[zone_id] += 1
        return people

    def _follow_zone_changes(self) -> None:
        """Shapes were redrawn: what was known about sides and zones no longer applies, and removed lines lose their totals."""
        if self._zones_version == self.zones.version:
            return
        self._zones_version = self.zones.version
        self._people.clear()
        line_ids = {line.id for line in self.zones.lines}
        self.counts = {line_id: count for line_id, count in self.counts.items() if line_id in line_ids}

    def _update_line(self, state: LineState, line: CountLine, foot: tuple[float, float], now: float) -> EventType | None:
        """Count a crossing only when the person clearly changes side, stays there for LINE_MIN_FRAMES frames,
        crossed within the drawn segment, and did not just cross. A person lost after fewer frames on the new side is
        settled in on_track_lost."""
        distance = signed_distance(line, *foot)
        if abs(distance) < LINE_MARGIN * self.zones.frame_height:
            return None
        side = 1 if distance > 0 else -1
        if state.side == 0 or side == state.side:
            state.side, state.side_point = side, foot
            state.pending_side = state.pending_frames = 0
            return None
        if state.pending_side != side:
            state.pending_side, state.pending_frames = side, 0
        state.pending_frames += 1
        state.pending_point, state.pending_at = foot, now
        if state.pending_frames < LINE_MIN_FRAMES:
            return None
        return self._settle_crossing(state, line, foot, now)

    @staticmethod
    def _settle_crossing(state: LineState, line: CountLine, foot: tuple[float, float], now: float) -> EventType | None:
        """The person is now on pending_side: count it if they crossed the drawn segment and did not just cross."""
        side = state.pending_side
        counted = (
            crosses_within_segment(line, state.side_point or foot, foot)
            and now - state.last_cross >= LINE_COOLDOWN_SECONDS
        )
        state.side, state.side_point = side, foot
        state.pending_side = state.pending_frames = 0
        if not counted:
            return None
        state.last_cross = now
        return EventType.LINE_IN if side == line.in_side else EventType.LINE_OUT

    def _line_event(self, direction: EventType, line: CountLine, track_id: int, ts: datetime) -> Event:
        count = self.counts.setdefault(line.id, LineCount())
        if direction is EventType.LINE_IN:
            count.entered += 1
        else:
            count.left += 1
        return self._event(direction, track_id, ts, line.name, {"id": line.id})

    def _zone_exit(self, track_id: int, ts: datetime, zone_id: int, zone_name: str, state: ZoneState) -> Event:
        state.inside = False
        dwell = round(ts.timestamp() - state.entered, 1)
        return self._event(EventType.ZONE_EXIT, track_id, ts, zone_name, {"id": zone_id, "dwell_seconds": dwell})

    def _event(self, type: EventType, track_id: int, ts: datetime, zone_name: str, data: dict) -> Event:
        return Event(camera_id=self.camera_id, type=type, ts=ts, track_ids=[track_id], zone_id=zone_name, data=data)
