"""HTTP endpoints for zones and count lines."""
from datetime import datetime

from fastapi import APIRouter, status

from backend.core.dependencies import CurrentUserId
from backend.core.responses import ApiResponse, ok
from backend.modules.zones.schemas import (
    LineCountOut,
    ZoneIn,
    ZoneOccupancyOut,
    ZoneOut,
)
from backend.modules.zones.service import ZoneServiceDep

router = APIRouter(tags=["zones"])


@router.get("/cameras/{camera_id}/zones", response_model=ApiResponse[list[ZoneOut]])
async def list_zones(camera_id: str, service: ZoneServiceDep, _user: CurrentUserId):
    return ok(await service.list_zones(camera_id))


@router.post(
    "/cameras/{camera_id}/zones", response_model=ApiResponse[ZoneOut], status_code=status.HTTP_201_CREATED
)
async def create_zone(camera_id: str, data: ZoneIn, service: ZoneServiceDep, _user: CurrentUserId):
    return ok(await service.create(camera_id, data), "Saved")


@router.get("/zones/line-counts", response_model=ApiResponse[list[LineCountOut]])
async def line_counts(service: ZoneServiceDep, _user: CurrentUserId, since: datetime | None = None):
    return ok(await service.line_counts(since))


@router.get("/zones/occupancy", response_model=ApiResponse[list[ZoneOccupancyOut]])
async def zone_occupancy(service: ZoneServiceDep, _user: CurrentUserId):
    return ok(await service.occupancy())


@router.put("/zones/{zone_id}", response_model=ApiResponse[ZoneOut])
async def update_zone(zone_id: int, data: ZoneIn, service: ZoneServiceDep, _user: CurrentUserId):
    return ok(await service.update(zone_id, data), "Saved")


@router.delete("/zones/{zone_id}", response_model=ApiResponse[None])
async def delete_zone(zone_id: int, service: ZoneServiceDep, _user: CurrentUserId):
    await service.delete(zone_id)
    return ok(message="Deleted")
