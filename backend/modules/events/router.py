"""HTTP endpoints for events."""
from fastapi import APIRouter, Query

from backend.core.dependencies import CurrentUserId
from backend.core.responses import ApiResponse, ok
from backend.modules.events.schemas import EventOut
from backend.modules.events.service import EventServiceDep
from shared.schemas import EventType

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=ApiResponse[list[EventOut]])
async def list_events(
    service: EventServiceDep,
    _user: CurrentUserId,
    camera_id: str | None = None,
    type: EventType | None = None,
    limit: int = Query(100, ge=1, le=1000),
):
    return ok(await service.list_events(camera_id, type, limit))
