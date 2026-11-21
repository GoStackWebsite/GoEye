"""Redis helpers: Streams for messages, and the latest JPEG frame per camera for the live view."""
from collections.abc import Iterator
from typing import TypeVar

import redis
from pydantic import BaseModel

from shared.config import settings

M = TypeVar("M", bound=BaseModel)

FRAME_KEY = "frame:{camera_id}"

_text_client: redis.Redis | None = None
_binary_client: redis.Redis | None = None


def get_client() -> redis.Redis:
    """Client for JSON messages (responses decoded to str)."""
    global _text_client
    if _text_client is None:
        _text_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    return _text_client


def _get_binary_client() -> redis.Redis:
    """Client for raw bytes such as JPEG frames (responses left as bytes)."""
    global _binary_client
    if _binary_client is None:
        _binary_client = redis.Redis.from_url(settings.redis_url)
    return _binary_client


def publish(stream: str, message: BaseModel, maxlen: int = 10_000) -> str:
    """Append a Pydantic message to a stream."""
    return get_client().xadd(
        stream, {"json": message.model_dump_json()}, maxlen=maxlen, approximate=True
    )


def subscribe(
    stream: str, model: type[M], group: str, consumer: str, block_ms: int = 2000
) -> Iterator[M]:
    """Yield validated messages from a stream via a consumer group.

    block_ms must stay below redis-py's default 5 s socket timeout, or an idle wait raises TimeoutError.
    """
    client = get_client()
    try:
        client.xgroup_create(stream, group, id="0", mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
    while True:
        resp = client.xreadgroup(group, consumer, {stream: ">"}, count=100, block=block_ms)
        for _stream, entries in resp or []:
            for msg_id, fields in entries:
                yield model.model_validate_json(fields["json"])
                client.xack(stream, group, msg_id)


def publish_frame(camera_id: str, jpeg: bytes) -> None:
    """Store a camera's newest frame; it expires so a stalled camera shows as offline."""
    key = FRAME_KEY.format(camera_id=camera_id)
    _get_binary_client().set(key, jpeg, px=int(settings.frame_ttl_seconds * 1000))


def latest_frame(camera_id: str) -> bytes | None:
    return _get_binary_client().get(FRAME_KEY.format(camera_id=camera_id))
