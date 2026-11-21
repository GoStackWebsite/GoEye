"""Background process: reads events from the Redis bus and stores them via EventService.

The backend creates the tables at startup, so this process starts only once the backend is healthy.
"""
import asyncio

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.modules.events.repository import EventRepository
from backend.modules.events.service import EventService
from shared.bus import subscribe
from shared.schemas import Event

CONSUMER_GROUP = "event_writer"  # Redis remembers per group which events were already stored
CONSUMER_NAME = "writer-1"


async def main() -> None:
    # subscribe() blocks while waiting; fine here because this process does nothing else.
    for event in subscribe(settings.event_stream, Event, group=CONSUMER_GROUP, consumer=CONSUMER_NAME):
        async with SessionLocal() as session:
            await EventService(EventRepository(session)).record(event)


if __name__ == "__main__":
    asyncio.run(main())
