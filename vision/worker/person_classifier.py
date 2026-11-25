"""Classifies a tracked person as staff vs customer from their clothing.

The model is a YOLO11n classification network trained in camera_tool (tools/staff_train.py) on upper-body crops
with the head pixelated, so live crops are made exactly the same way. One instance per camera: the ultralytics
predictor is not thread-safe.
"""
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from shared.config import settings
from shared.schemas import PersonRole

STAFF_CLASS = "staff"        # class name in the trained model
CROP_BOTTOM = 0.62           # of the person box: head to hips, the crop the model was trained on
CROP_SIDE_PAD = 0.08         # of the box width, added on each side
MIN_BOX_HEIGHT, MIN_BOX_WIDTH = 24, 12
MIN_CROP_HEIGHT = 16
HEAD_BAND = 0.39             # of the crop height: the head, pixelated so the model judges clothing, never the face
HEAD_LEFT, HEAD_RIGHT = 0.17, 0.83
MIN_HEAD_HEIGHT, MIN_HEAD_WIDTH = 8, 4
PIXEL_BLOCKS = 6             # the head band is reduced to about this many blocks across its longer side
DEFAULT_IMGSZ = 128          # used when the model file does not record the size it was trained at


def upper_body(frame: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray | None:
    """The head-to-hips crop of one person, or None when the box is too small to judge."""
    x1, y1, x2, y2 = bbox
    height, width = y2 - y1, x2 - x1
    if height < MIN_BOX_HEIGHT or width < MIN_BOX_WIDTH:
        return None
    pad = int(width * CROP_SIDE_PAD)
    x1, x2 = max(0, x1 - pad), min(frame.shape[1], x2 + pad)
    y2 = min(frame.shape[0], int(y1 + height * CROP_BOTTOM))
    crop = frame[max(0, y1):y2, x1:x2]
    return crop if crop.shape[0] >= MIN_CROP_HEIGHT and crop.shape[1] >= MIN_BOX_WIDTH else None


def mask_head(crop: np.ndarray) -> np.ndarray:
    """Pixelate the head band of an upper-body crop."""
    height, width = crop.shape[:2]
    y2 = max(MIN_HEAD_HEIGHT, int(height * HEAD_BAND))
    x1, x2 = int(width * HEAD_LEFT), int(width * HEAD_RIGHT)
    if x2 - x1 < MIN_HEAD_WIDTH or y2 >= height:
        return crop
    out = crop.copy()
    head = out[:y2, x1:x2]
    block = max(3, max(head.shape[:2]) // PIXEL_BLOCKS)
    small = cv2.resize(head, (max(1, head.shape[1] // block), max(1, head.shape[0] // block)), interpolation=cv2.INTER_LINEAR)
    out[:y2, x1:x2] = cv2.resize(small, (head.shape[1], head.shape[0]), interpolation=cv2.INTER_NEAREST)
    return out


# Decides whether a tracked person is staff or a customer with the learned staff-uniform model
class PersonClassifier:
    def __init__(self) -> None:
        path = Path(settings.models_dir) / settings.staff_model
        if not path.exists():
            raise FileNotFoundError(f"Staff model {path} not found: copy staff_cls.pt from camera_tool's models folder")
        self.model = YOLO(str(path), task="classify")
        self.imgsz = int(self.model.overrides.get("imgsz") or DEFAULT_IMGSZ)
        staff = [i for i, name in self.model.names.items() if str(name).lower() == STAFF_CLASS]
        if not staff:
            raise ValueError(f"Staff model {path} has no '{STAFF_CLASS}' class: {self.model.names}")
        self.staff_index = staff[0]

    def classify(self, frame: np.ndarray, bbox: tuple[int, int, int, int]) -> PersonRole:
        """Staff or customer for the person in bbox; UNKNOWN when the box is too small to judge."""
        crop = upper_body(frame, bbox)
        if crop is None:
            return PersonRole.UNKNOWN
        probs = self.model.predict(mask_head(crop), imgsz=self.imgsz, verbose=False)[0].probs
        staff_prob = float(probs.data[self.staff_index])
        return PersonRole.STAFF if staff_prob >= settings.staff_threshold else PersonRole.CUSTOMER
