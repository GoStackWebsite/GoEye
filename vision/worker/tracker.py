"""Multi-object tracking (e.g. ByteTrack via supervision or ultralytics)."""


# Assigns stable track IDs to detections across frames
class Tracker:
    def update(self, detections):
        # TODO: implement
        raise NotImplementedError
