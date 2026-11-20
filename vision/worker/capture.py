"""Frame capture from a webcam index, RTSP URL or video file."""
from collections.abc import Iterator

import cv2
import numpy as np


def frames(source: str | int) -> Iterator[np.ndarray]:
    cap = cv2.VideoCapture(source)
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            yield frame
    finally:
        cap.release()
