from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


# A behavior event detected by the vision analyzers
class EventRecord(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    camera_id: Mapped[str] = mapped_column(String(64), index=True)
    type: Mapped[str] = mapped_column(String(32), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    track_ids: Mapped[list[int]] = mapped_column(JSON, default=list)
    zone_id: Mapped[str | None] = mapped_column(String(64))
    score: Mapped[float | None] = mapped_column(Float)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
