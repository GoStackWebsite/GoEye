"""Flags theft-risk behavior near shelves and exits."""
from shared.schemas import Event, TrackUpdate
from vision.analyzers.base import Analyzer


# Flags theft-risk behavior near shelves and exits
class TheftRiskAnalyzer(Analyzer):
    name = "theft_risk"

    def on_track_update(self, update: TrackUpdate) -> list[Event]:
        # TODO: implement
        return []
