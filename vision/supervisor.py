"""Vision process entry point: one worker per camera reads frames, detects and tracks people, and publishes the
annotated frame for the live view. If a worker fails the process exits, and Docker restarts it."""
import logging
import threading
import time

import cv2
import numpy as np

from shared.bus import publish_frame
from shared.config import settings
from vision.worker.capture import CameraStream
from vision.worker.detector import PersonDetector
from vision.worker.tracker import PeopleTracker, Track

log = logging.getLogger("supervisor")

BOX_COLOUR = (0, 200, 255)  # BGR
LABEL_FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_tracks(frame: np.ndarray, tracks: list[Track]) -> None:
    for t in tracks:
        x1, y1, x2, y2 = t.bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOUR, 2)
        cv2.putText(frame, f"#{t.id}", (x1, max(14, y1 - 6)), LABEL_FONT, 0.5, BOX_COLOUR, 1, cv2.LINE_AA)


def run_camera(stream: CameraStream, detector: PersonDetector) -> None:
    """Detect and track people on one camera at analysis_fps, forever."""
    people = PeopleTracker()
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, settings.stream_jpeg_quality]
    interval = 1.0 / settings.analysis_fps
    log.info("Camera %s: analysing at %.0f fps", stream.camera_id, settings.analysis_fps)
    last_frame = None
    while True:
        started = time.monotonic()
        frame = stream.latest()
        if frame is not None and frame is not last_frame and stream.connected:
            last_frame = frame
            height, width = frame.shape[:2]
            tracks = people.update(detector.track(frame), width, height, time.time())
            annotated = frame.copy()
            draw_tracks(annotated, tracks)
            ok, jpeg = cv2.imencode(".jpg", annotated, encode_params)
            if ok:
                publish_frame(stream.camera_id, jpeg.tobytes())
        time.sleep(max(0.0, interval - (time.monotonic() - started)))


def main() -> None:
    failed = threading.Event()

    def guarded(stream: CameraStream, detector: PersonDetector) -> None:
        try:
            run_camera(stream, detector)
        except Exception:
            log.exception("Camera %s worker failed", stream.camera_id)
            failed.set()

    # detectors are created one after another: the first one downloads the model file, the rest reuse it
    workers = [(CameraStream(camera_id, url), PersonDetector()) for camera_id, url in settings.cameras.items()]
    for stream, detector in workers:
        stream.start()
        threading.Thread(target=guarded, args=(stream, detector), name=f"worker-{stream.camera_id}", daemon=True).start()
    failed.wait()
    raise SystemExit(1)  # Docker restarts the vision container


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
