"""DB access for events."""
from sqlalchemy import select

from backend.core.repository import BaseRepository
from backend.modules.events.models import EventRecord
from shared.schemas import EventType


# Handles DB access for events
class EventRepository(BaseRepository[EventRecord]):
    async def list(
        self, camera_id: str | None, type: EventType | None, limit: int
    ) -> list[EventRecord]:
        stmt = select(EventRecord).order_by(EventRecord.ts.desc()).limit(limit)
        if camera_id:
            stmt = stmt.where(EventRecord.camera_id == camera_id)
        if type:
            stmt = stmt.where(EventRecord.type == type)
        return list((await self.session.scalars(stmt)).all())
