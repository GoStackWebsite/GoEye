"""Redis Streams publish/subscribe helpers."""
from collections.abc import Iterator
from typing import TypeVar

import redis
from pydantic import BaseModel

from shared.config import settings

M = TypeVar("M", bound=BaseModel)

_client: redis.Redis | None = None


def get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def publish(stream: str, message: BaseModel, maxlen: int = 10_000) -> str:
    """Append a Pydantic message to a stream."""
    return get_client().xadd(
        stream, {"json": message.model_dump_json()}, maxlen=maxlen, approximate=True
    )


def subscribe(
    stream: str, model: type[M], group: str, consumer: str, block_ms: int = 5000
) -> Iterator[M]:
    """Yield validated messages from a stream via a consumer group."""
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
