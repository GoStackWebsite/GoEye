"""Per-camera people state on top of the tracker's boxes: foot-point history and when a person is gone.

Ported from camera_tool (app/analytics.py Track / update).
"""
from collections import deque
from dataclasses import dataclass, field

from vision.worker.detector import Detection

LOST_TIMEOUT = 1.5       # seconds without a detection before a person is considered gone
HISTORY_LENGTH = 150     # foot points kept per person


# One person on one camera: latest box, and where their feet have been (normalised 0-1 frame coordinates)
@dataclass
class Track:
    id: int
    first_seen: float
    last_seen: float
    bbox: tuple[int, int, int, int]
    conf: float
    history: deque = field(default_factory=lambda: deque(maxlen=HISTORY_LENGTH))  # (time, foot x, foot y)

    @property
    def foot(self) -> tuple[float, float]:
        return (self.history[-1][1], self.history[-1][2]) if self.history else (0.0, 0.0)

    def dwell(self, now: float) -> float:
        return now - self.first_seen


# Keeps one camera's live people up to date from each frame's detections
class PeopleTracker:
    def __init__(self) -> None:
        self.tracks: dict[int, Track] = {}

    def update(self, detections: list[Detection], width: int, height: int, now: float) -> list[Track]:
        """Apply one frame's detections; returns the people currently in view."""
        for d in detections:
            bbox = (d.x1, d.y1, d.x2, d.y2)
            t = self.tracks.get(d.track_id)
            if t is None:
                t = self.tracks[d.track_id] = Track(d.track_id, now, now, bbox, d.conf)
            t.last_seen, t.bbox, t.conf = now, bbox, d.conf
            # the foot point (bottom centre of the box) is where the person stands on the floor
            t.history.append((now, (d.x1 + d.x2) / 2 / width, d.y2 / height))
        for track_id in [tid for tid, t in self.tracks.items() if now - t.last_seen > LOST_TIMEOUT]:
            del self.tracks[track_id]
        return list(self.tracks.values())
