"""Vision process entry point: one worker per camera reads frames, detects and tracks people, counts them over the
drawn count lines and zones, and publishes the annotated frame for the live view. If a worker fails the process
exits, and Docker restarts it."""
import logging
import threading
import time
from datetime import UTC, datetime

import cv2
import numpy as np

from shared.bus import publish, publish_frame, publish_occupancy
from shared.config import settings
from shared.schemas import BBox, TrackUpdate
from vision.analyzers.crossing import CrossingAnalyzer, LineCount
from vision.worker.capture import CameraStream
from vision.worker.detector import PersonDetector
from vision.worker.tracker import PeopleTracker, Track
from vision.zones import CameraZones

log = logging.getLogger("supervisor")

BOX_COLOUR = (0, 200, 255)   # BGR
ZONE_COLOUR = (255, 170, 60)
LINE_COLOUR = (80, 220, 100)
LABEL_FONT = cv2.FONT_HERSHEY_SIMPLEX
LABEL_SCALE = 0.5
SIDE_LABEL_OFFSET = 22       # pixels from the middle of a count line to its IN and OUT labels


def draw_label(frame: np.ndarray, text: str, x: float, y: float, colour: tuple[int, int, int]) -> None:
    cv2.putText(frame, text, (int(x), int(y)), LABEL_FONT, LABEL_SCALE, colour, 1, cv2.LINE_AA)


def draw_shapes(frame: np.ndarray, zones: CameraZones, counts: dict[int, LineCount], people: dict[int, int]) -> None:
    """Draw each zone with the number of people in it, and each count line with its IN and OUT sides and totals."""
    for zone in zones.zones:
        cv2.polylines(frame, [zone.outline], True, ZONE_COLOUR, 2)
        # at the zone's highest corner, kept inside the picture
        x, y = min(zone.outline.tolist(), key=lambda corner: corner[1])
        label = f"{zone.name}: {people.get(zone.id, 0)} inside"
        text_width = cv2.getTextSize(label, LABEL_FONT, LABEL_SCALE, 1)[0][0]
        draw_label(frame, label, min(x + 4, frame.shape[1] - text_width - 4), max(y + 16, 16), ZONE_COLOUR)
    for line in zones.lines:
        (ax, ay), (bx, by) = line.a, line.b
        cv2.line(frame, (int(ax), int(ay)), (int(bx), int(by)), LINE_COLOUR, 2)
        count = counts.get(line.id, LineCount())
        totals = f"{line.name}  IN {count.entered}  OUT {count.left}"
        # above the top end of the line, but never off the top or right edge of the picture
        text_width = cv2.getTextSize(totals, LABEL_FONT, LABEL_SCALE, 1)[0][0]
        draw_label(frame, totals, min(min(ax, bx), frame.shape[1] - text_width - 4), max(min(ay, by) - 8, 16), LINE_COLOUR)
        # the IN side is where the cross product from a to b is positive (or negative when in_side is -1)
        dx, dy = bx - ax, by - ay
        length = float(np.hypot(dx, dy)) or 1.0
        nx, ny = -dy / length * line.in_side, dx / length * line.in_side
        mx, my = (ax + bx) / 2, (ay + by) / 2
        draw_label(frame, "IN", mx + nx * SIDE_LABEL_OFFSET, my + ny * SIDE_LABEL_OFFSET, LINE_COLOUR)
        draw_label(frame, "OUT", mx - nx * SIDE_LABEL_OFFSET, my - ny * SIDE_LABEL_OFFSET, LINE_COLOUR)


def draw_tracks(frame: np.ndarray, tracks: list[Track]) -> None:
    for t in tracks:
        x1, y1, x2, y2 = t.bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOUR, 2)
        cv2.putText(frame, f"#{t.id}", (x1, max(14, y1 - 6)), LABEL_FONT, LABEL_SCALE, BOX_COLOUR, 1, cv2.LINE_AA)


def run_camera(stream: CameraStream, detector: PersonDetector) -> None:
    """Detect, track and count people on one camera at analysis_fps, forever."""
    people = PeopleTracker()
    zones = CameraZones(stream.camera_id)
    crossing = CrossingAnalyzer(stream.camera_id, zones)
    in_view: set[int] = set()
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
            now = time.time()
            ts = datetime.fromtimestamp(now, UTC)
            zones.refresh(width, height, now)
            tracks = people.update(detector.track(frame), width, height, now)
            events = []
            for t in tracks:
                if t.last_seen == now:  # detected in this frame; a person kept for a moment after being lost has an old box
                    x1, y1, x2, y2 = t.bbox
                    update = TrackUpdate(camera_id=stream.camera_id, track_id=t.id, ts=ts,
                                         bbox=BBox(x1=x1, y1=y1, x2=x2, y2=y2), confidence=t.conf)
                    events += crossing.on_track_update(update)
            still_in_view = {t.id for t in tracks}
            for track_id in in_view - still_in_view:
                events += crossing.on_track_lost(track_id, ts)
            in_view = still_in_view
            for event in events:
                publish(settings.event_stream, event)
            people_in_zones = crossing.occupancy()
            publish_occupancy(stream.camera_id, people_in_zones)
            annotated = frame.copy()
            draw_shapes(annotated, zones, crossing.counts, people_in_zones)
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
