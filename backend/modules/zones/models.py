from typing import Any

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


# A zone or count line drawn on a camera in the dashboard
class ZoneRecord(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    camera_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(64))
    kind: Mapped[str] = mapped_column(String(16))
    points: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    in_side: Mapped[int] = mapped_column(Integer, default=1)
