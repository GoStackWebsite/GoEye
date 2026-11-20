from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


# A camera feed the vision workers read from
class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    source: Mapped[str] = mapped_column(String(512))  # RTSP URL, file path or webcam index
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
