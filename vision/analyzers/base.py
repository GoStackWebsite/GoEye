"""Analyzer interface. Every behavior analyzer implements this."""
from abc import ABC, abstractmethod

from shared.schemas import Event, TrackUpdate


# Base class for every behavior analyzer: track updates in, events out
class Analyzer(ABC):
    name: str = "base"

    def __init__(self, camera_id: str) -> None:
        self.camera_id = camera_id

    @abstractmethod
    def on_track_update(self, update: TrackUpdate) -> list[Event]:
        """Consume one track update; return zero or more events."""
