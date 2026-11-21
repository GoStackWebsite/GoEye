"""Reads RTSP camera streams in the background, always exposing the newest frame and reconnecting on failure.

Run ``python -m vision.worker.capture`` to open a live preview window per configured camera (press q to quit).
"""
import logging
import os
import threading
import time
from urllib.parse import quote, urlsplit, urlunsplit

import cv2
import numpy as np

from shared.config import settings

log = logging.getLogger("capture")


def with_credentials(url: str, user: str, password: str) -> str:
    """Insert the login into an RTSP URL, URL-encoded so special characters in the password are safe."""
    parts = urlsplit(url)
    netloc = f"{quote(user, safe='')}:{quote(password, safe='')}@{parts.hostname}"
    if parts.port:
        netloc += f":{parts.port}"
    return urlunsplit(parts._replace(netloc=netloc))


# Background reader for one camera: keeps only the newest frame and reconnects when the stream fails or stalls
class CameraStream(threading.Thread):
    def __init__(self, camera_id: str, url: str) -> None:
        super().__init__(name=f"camera-{camera_id}", daemon=True)
        self.camera_id = camera_id
        self.url = url  # without credentials: safe to log
        self._source = with_credentials(url, settings.rtsp_user, settings.rtsp_password)
        self._lock = threading.Lock()
        self._frame: np.ndarray | None = None
        self._last_frame_at = 0.0
        self._stop_event = threading.Event()

    @property
    def connected(self) -> bool:
        return time.monotonic() - self._last_frame_at < settings.camera_timeout_seconds

    def latest(self) -> np.ndarray | None:
        with self._lock:
            return self._frame

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        # RTSP over TCP: UDP drops packets on busy networks and produces smeared frames
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        timeout_ms = int(settings.camera_timeout_seconds * 1000)
        while not self._stop_event.is_set():
            cap = cv2.VideoCapture(self._source, cv2.CAP_FFMPEG, [
                cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, timeout_ms,
                cv2.CAP_PROP_READ_TIMEOUT_MSEC, timeout_ms,
            ])
            if cap.isOpened():
                log.info("Connected to %s", self.url)
                self._read_until_failure(cap)
                log.warning("Lost %s, reconnecting", self.url)
            else:
                log.warning("Cannot open %s (check address, login and network), retrying", self.url)
            cap.release()
            self._stop_event.wait(settings.camera_reconnect_seconds)

    def _read_until_failure(self, cap: cv2.VideoCapture) -> None:
        while not self._stop_event.is_set():
            ok, frame = cap.read()
            if not ok:
                return
            with self._lock:
                self._frame = frame
                self._last_frame_at = time.monotonic()


def preview() -> None:
    """Show every configured camera in its own window until q is pressed."""
    streams = [CameraStream(camera_id, url) for camera_id, url in settings.cameras.items()]
    for stream in streams:
        stream.start()
    try:
        while cv2.waitKey(30) & 0xFF != ord("q"):
            for stream in streams:
                frame = stream.latest()
                if frame is not None:
                    cv2.namedWindow(stream.camera_id, cv2.WINDOW_NORMAL)
                    cv2.imshow(stream.camera_id, frame)
    finally:
        for stream in streams:
            stream.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    preview()
