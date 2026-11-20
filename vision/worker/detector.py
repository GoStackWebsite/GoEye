"""YOLOv8 wrapper (swappable). Keep the interface stable so models can change."""
from typing import Protocol

import numpy as np


# Interface any detector must implement, so models can be swapped
class Detector(Protocol):
    def detect(self, frame: np.ndarray): ...


# Person detector backed by Ultralytics YOLO
class YoloDetector:
    def __init__(self, model_path: str) -> None:
        from ultralytics import YOLO

        self.model = YOLO(model_path)

    def detect(self, frame: np.ndarray):
        return self.model(frame, classes=[0], verbose=False)[0]  # class 0 = person
