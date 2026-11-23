"""YOLO person detection with ByteTrack tracking (ultralytics).

One instance per camera: the tracker keeps state between frames, and the ultralytics predictor is not thread-safe.
"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from ultralytics import YOLO

from shared.config import settings

PERSON_CLASS_ID = 0  # "person" in the COCO classes YOLO models are trained on
TRACKER_CONFIG = Path(__file__).with_name("tracker.yaml")  # ByteTrack tuned for fixed store cameras (from camera_tool)


# One tracked person box in pixel coordinates
@dataclass(slots=True)
class Detection:
    track_id: int
    x1: int
    y1: int
    x2: int
    y2: int
    conf: float


# Runs YOLO person detection plus ByteTrack on one camera's frames
class PersonDetector:
    def __init__(self) -> None:
        self.model = YOLO(str(Path(settings.models_dir) / settings.yolo_model))
        # the first prediction loads the weights; doing it now keeps the first live frame from stalling
        warmup = np.zeros((settings.detect_imgsz, settings.detect_imgsz, 3), np.uint8)
        self.model.predict(warmup, imgsz=settings.detect_imgsz, verbose=False)

    def track(self, frame: np.ndarray) -> list[Detection]:
        result = self.model.track(
            frame,
            persist=True,
            classes=[PERSON_CLASS_ID],
            conf=settings.detect_conf,
            imgsz=settings.detect_imgsz,
            tracker=str(TRACKER_CONFIG),
            verbose=False,
        )[0]
        boxes = result.boxes
        if boxes is None or boxes.id is None:
            return []
        xyxy = boxes.xyxy.cpu().numpy().astype(int)
        ids = boxes.id.cpu().numpy().astype(int)
        confs = boxes.conf.cpu().numpy()
        return [
            Detection(int(i), int(b[0]), int(b[1]), int(b[2]), int(b[3]), float(c))
            for b, i, c in zip(xyxy, ids, confs)
        ]
