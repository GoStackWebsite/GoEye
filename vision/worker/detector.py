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
DUPLICATE_INSIDE = 0.85     # a box this much inside a bigger one...
DUPLICATE_SAME_TOP = 0.15   # ...whose top is this close to the bigger one's (fraction of its height) is the same person


# One tracked person box in pixel coordinates
@dataclass(slots=True)
class Detection:
    track_id: int
    x1: int
    y1: int
    x2: int
    y2: int
    conf: float


def drop_duplicates(detections: list[Detection]) -> list[Detection]:
    """Remove a second box on the same person: YOLO26 has no duplicate suppression, and a seated person can get both a
    whole-body box and an upper-body box starting at the same head. The whole-body box is kept, because counting uses
    the feet. A different person behind someone has their head higher up, so they are not removed."""
    def area(d: Detection) -> int:
        return max(0, d.x2 - d.x1) * max(0, d.y2 - d.y1)

    kept = []
    for small in detections:
        duplicate = False
        for big in detections:
            if big is small or area(big) <= area(small) or area(small) == 0:
                continue
            overlap = max(0, min(small.x2, big.x2) - max(small.x1, big.x1)) * max(0, min(small.y2, big.y2) - max(small.y1, big.y1))
            if overlap / area(small) >= DUPLICATE_INSIDE and abs(small.y1 - big.y1) <= DUPLICATE_SAME_TOP * (big.y2 - big.y1):
                duplicate = True
                break
        if not duplicate:
            kept.append(small)
    return kept


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
        return drop_duplicates([
            Detection(int(i), int(b[0]), int(b[1]), int(b[2]), int(b[3]), float(c))
            for b, i, c in zip(xyxy, ids, confs)
        ])
