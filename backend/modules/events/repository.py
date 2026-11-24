"""DB access for events."""
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select

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

    async def count_by_zone(self, types: Sequence[EventType], since: datetime | None) -> dict[tuple[int, str], int]:
        """Number of events per (zone id, event type), counted from since onwards (all time when it is None)."""
        zone = EventRecord.data["id"].as_integer()
        stmt = select(zone, EventRecord.type, func.count()).where(EventRecord.type.in_(types)).group_by(zone, EventRecord.type)
        if since:
            stmt = stmt.where(EventRecord.ts >= since)
        return {(zone_id, type): n for zone_id, type, n in (await self.session.execute(stmt)).all()}
