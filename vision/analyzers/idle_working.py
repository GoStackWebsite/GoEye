"""Detects staff idle vs working."""
from shared.schemas import Event, TrackUpdate
from vision.analyzers.base import Analyzer


# Detects whether staff are idle or working
class IdleWorkingAnalyzer(Analyzer):
    name = "idle_working"

    def on_track_update(self, update: TrackUpdate) -> list[Event]:
        # TODO: implement
        return []
