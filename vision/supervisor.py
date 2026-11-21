"""Vision process entry point: reads every configured camera and publishes its newest frame for the live view."""
import logging
import time

import cv2

from shared.bus import publish_frame
from shared.config import settings
from vision.worker.capture import CameraStream

log = logging.getLogger("supervisor")


def main() -> None:
    streams = [CameraStream(camera_id, url) for camera_id, url in settings.cameras.items()]
    for stream in streams:
        stream.start()
    log.info("Publishing %d camera(s) at %.0f fps", len(streams), settings.stream_fps)

    encode_params = [cv2.IMWRITE_JPEG_QUALITY, settings.stream_jpeg_quality]
    interval = 1.0 / settings.stream_fps
    while True:
        started = time.monotonic()
        for stream in streams:
            frame = stream.latest()
            if frame is None or not stream.connected:
                continue
            ok, jpeg = cv2.imencode(".jpg", frame, encode_params)
            if ok:
                publish_frame(stream.camera_id, jpeg.tobytes())
        time.sleep(max(0.0, interval - (time.monotonic() - started)))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
