"""Background process: reads events from the Redis bus and stores them via EventService."""
import asyncio

from backend.core.config import settings
from backend.core.database import SessionLocal, create_tables
from backend.modules.events.repository import EventRepository
from backend.modules.events.service import EventService
from shared.bus import subscribe
from shared.schemas import Event


async def main() -> None:
    await create_tables()
    # subscribe() blocks while waiting; fine here because this process does nothing else.
    for event in subscribe(settings.event_stream, Event, group="event_writer", consumer="writer-1"):
        async with SessionLocal() as session:
            await EventService(EventRepository(session)).record(event)


if __name__ == "__main__":
    asyncio.run(main())
