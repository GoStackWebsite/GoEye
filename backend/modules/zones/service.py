"""Business logic for zones and count lines: saving them and handing each camera's current set to vision."""
import asyncio
from datetime import datetime
from typing import Annotated

from fastapi import Depends

from backend.core.dependencies import DbSession
from backend.core.exceptions import NotFoundError
from backend.modules.cameras.repository import CameraRepository
from backend.modules.events.repository import EventRepository
from backend.modules.zones.models import ZoneRecord
from backend.modules.zones.repository import ZoneRepository
from backend.modules.zones.schemas import (
    LineCountOut,
    ZoneIn,
    ZoneOccupancyOut,
    ZoneOut,
)
from shared.bus import load_occupancy, publish_zones
from shared.schemas import EventType, ZoneKind


# Saves the zones and count lines drawn in the dashboard and keeps vision's copy in step with them
class ZoneService:
    def __init__(self, repo: ZoneRepository, cameras: CameraRepository, events: EventRepository) -> None:
        self.repo = repo
        self.cameras = cameras
        self.events = events

    async def list_zones(self, camera_id: str) -> list[ZoneOut]:
        self._ensure_camera(camera_id)
        return [ZoneOut.model_validate(z) for z in await self.repo.list_by_camera(camera_id)]

    async def create(self, camera_id: str, data: ZoneIn) -> ZoneOut:
        self._ensure_camera(camera_id)
        zone = await self.repo.add(ZoneRecord(camera_id=camera_id, **data.model_dump()))
        await self._publish(camera_id)
        return ZoneOut.model_validate(zone)

    async def update(self, zone_id: int, data: ZoneIn) -> ZoneOut:
        zone = await self._get(zone_id)
        for field, value in data.model_dump().items():
            setattr(zone, field, value)
        await self.repo.add(zone)
        await self._publish(zone.camera_id)
        return ZoneOut.model_validate(zone)

    async def delete(self, zone_id: int) -> None:
        zone = await self._get(zone_id)
        camera_id = zone.camera_id
        await self.repo.delete(zone)
        await self._publish(camera_id)

    async def line_counts(self, since: datetime | None) -> list[LineCountOut]:
        """IN and OUT totals of every count line, including lines nobody has crossed yet."""
        totals = await self.events.count_by_zone([EventType.LINE_IN, EventType.LINE_OUT], since)
        return [
            LineCountOut(
                id=line.id,
                camera_id=line.camera_id,
                name=line.name,
                entered=totals.get((line.id, EventType.LINE_IN), 0),
                left=totals.get((line.id, EventType.LINE_OUT), 0),
            )
            for line in await self.repo.list_by_kind(ZoneKind.LINE)
        ]

    async def occupancy(self) -> list[ZoneOccupancyOut]:
        """People in every zone right now, as vision last reported them."""
        zones = await self.repo.list_by_kind(ZoneKind.ZONE)
        reported = {}
        for camera_id in {zone.camera_id for zone in zones}:
            reported[camera_id] = await asyncio.to_thread(load_occupancy, camera_id)  # the Redis client is blocking
        return [
            ZoneOccupancyOut(
                id=zone.id,
                camera_id=zone.camera_id,
                name=zone.name,
                people=None if reported[zone.camera_id] is None else reported[zone.camera_id].get(zone.id, 0),
            )
            for zone in zones
        ]

    async def publish_all(self) -> None:
        """Hand every camera's saved set to vision; run at startup, because Redis does not keep it across a restart."""
        for camera_id in self.cameras.ids():
            await self._publish(camera_id)

    async def _publish(self, camera_id: str) -> None:
        zones = [ZoneOut.model_validate(z) for z in await self.repo.list_by_camera(camera_id)]
        await asyncio.to_thread(publish_zones, camera_id, zones)  # the Redis client is blocking

    async def _get(self, zone_id: int) -> ZoneRecord:
        zone = await self.repo.get(zone_id)
        if zone is None:
            raise NotFoundError(f"Zone {zone_id} does not exist")
        return zone

    def _ensure_camera(self, camera_id: str) -> None:
        if not self.cameras.exists(camera_id):
            raise NotFoundError(f"Camera '{camera_id}' is not configured")


def get_zone_service(db: DbSession) -> ZoneService:
    return ZoneService(ZoneRepository(db), CameraRepository(), EventRepository(db))


ZoneServiceDep = Annotated[ZoneService, Depends(get_zone_service)]
