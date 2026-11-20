"""Business logic for events."""
from typing import Annotated

from fastapi import Depends

from backend.core.dependencies import DbSession
from backend.modules.events.models import EventRecord
from backend.modules.events.repository import EventRepository
from backend.modules.events.schemas import EventOut
from shared.schemas import Event, EventType


# Stores events from the vision bus and serves them to the API
class EventService:
    def __init__(self, repo: EventRepository) -> None:
        self.repo = repo

    async def record(self, event: Event) -> None:
        await self.repo.add(EventRecord(**event.model_dump()))

    async def list_events(
        self, camera_id: str | None, type: EventType | None, limit: int
    ) -> list[EventOut]:
        return [EventOut.model_validate(e) for e in await self.repo.list(camera_id, type, limit)]


def get_event_service(db: DbSession) -> EventService:
    return EventService(EventRepository(db))


EventServiceDep = Annotated[EventService, Depends(get_event_service)]
