"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.database import SessionLocal, create_tables, engine
from backend.core.exceptions import register_exception_handlers
from backend.core.responses import ApiResponse, ok
from backend.core.security import RedactTokenFilter
from backend.modules.auth.router import router as auth_router
from backend.modules.cameras.repository import CameraRepository
from backend.modules.cameras.router import router as cameras_router
from backend.modules.events.repository import EventRepository
from backend.modules.events.router import router as events_router
from backend.modules.zones.repository import ZoneRepository
from backend.modules.zones.router import router as zones_router
from backend.modules.zones.service import ZoneService

logging.getLogger("uvicorn.access").addFilter(RedactTokenFilter())

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    async with SessionLocal() as session:
        await ZoneService(ZoneRepository(session), CameraRepository(), EventRepository(session)).publish_all()
    yield
    await engine.dispose()


app = FastAPI(title="goeye", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(cameras_router)
app.include_router(events_router)
app.include_router(zones_router)


@app.get("/health", tags=["health"], response_model=ApiResponse[None])
def health():
    return ok(message="ok")
