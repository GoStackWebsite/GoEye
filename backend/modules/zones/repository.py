"""DB access for zones and count lines."""
from sqlalchemy import select

from backend.core.repository import BaseRepository
from backend.modules.zones.models import ZoneRecord


# Handles DB access for zones and count lines
class ZoneRepository(BaseRepository[ZoneRecord]):
    async def list_by_camera(self, camera_id: str) -> list[ZoneRecord]:
        stmt = select(ZoneRecord).where(ZoneRecord.camera_id == camera_id).order_by(ZoneRecord.id)
        return list((await self.session.scalars(stmt)).all())

    async def list_by_kind(self, kind: str) -> list[ZoneRecord]:
        stmt = select(ZoneRecord).where(ZoneRecord.kind == kind).order_by(ZoneRecord.camera_id, ZoneRecord.id)
        return list((await self.session.scalars(stmt)).all())

    async def get(self, zone_id: int) -> ZoneRecord | None:
        return await self.session.get(ZoneRecord, zone_id)

    async def delete(self, zone: ZoneRecord) -> None:
        await self.session.delete(zone)
        await self.session.commit()
