"""Measures dwell time and queue length."""
from shared.schemas import Event, TrackUpdate
from vision.analyzers.base import Analyzer


# Measures dwell time and queue length
class DwellQueueAnalyzer(Analyzer):
    name = "dwell_queue"

    def on_track_update(self, update: TrackUpdate) -> list[Event]:
        # TODO: implement
        return []
